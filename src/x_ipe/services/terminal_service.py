"""
FEATURE-005: Interactive Console v4.0

OutputBuffer: Circular buffer for terminal output (10KB)
PersistentSession: PTY wrapper with session persistence
SessionManager: Session lifecycle management
PTYSession: PTY process wrapper
"""
import os
import threading
import uuid
from collections import deque
from datetime import datetime
from typing import Dict, Optional, Any, Callable


# Constants for session management
BUFFER_MAX_CHARS = 10240  # 10KB limit for output buffer
SESSION_TIMEOUT = 3600   # 1 hour in seconds
CLEANUP_INTERVAL = 300   # 5 minutes for cleanup task


class OutputBuffer:
    """
    Circular buffer for terminal output.
    Uses deque with maxlen for automatic circular behavior.
    Stores up to 10KB of output for replay on reconnection.
    """
    
    def __init__(self, max_chars: int = BUFFER_MAX_CHARS):
        self._buffer: deque = deque(maxlen=max_chars)
    
    def append(self, data: str) -> None:
        """Append data character by character to maintain limit."""
        for char in data:
            self._buffer.append(char)
    
    def get_contents(self) -> str:
        """Get all buffered content as string."""
        return ''.join(self._buffer)
    
    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer.clear()
    
    def __len__(self) -> int:
        return len(self._buffer)


class PersistentSession:
    """
    Terminal session that persists across WebSocket disconnections.
    
    Wraps PTYSession with:
    - Output buffer for replay on reconnection
    - State tracking (connected/disconnected)
    - Expiry tracking for 1-hour timeout
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.pty_session: Optional[Any] = None
        self.output_buffer = OutputBuffer()
        self.socket_sid: Optional[str] = None
        self.emit_callback: Optional[Callable[[str], None]] = None
        self.disconnect_time: Optional[datetime] = None
        self.state = 'disconnected'
        self.created_at = datetime.now()
        self._lock = threading.Lock()
    
    def start_pty(self, rows: int = 24, cols: int = 80) -> None:
        """Start the underlying PTY process."""
        def buffered_emit(data: str) -> None:
            # Always buffer output
            self.output_buffer.append(data)
            # Only emit if connected
            if self.emit_callback and self.state == 'connected':
                self.emit_callback(data)
        
        self.pty_session = PTYSession(self.session_id, buffered_emit)
        self.pty_session.start(rows, cols)
    
    def attach(self, socket_sid: str, emit_callback: Callable[[str], None]) -> None:
        """Attach a WebSocket connection to this session."""
        with self._lock:
            self.socket_sid = socket_sid
            self.emit_callback = emit_callback
            self.state = 'connected'
            self.disconnect_time = None
    
    def detach(self) -> None:
        """Detach WebSocket, keeping PTY alive for reconnection."""
        with self._lock:
            self.socket_sid = None
            self.emit_callback = None
            self.state = 'disconnected'
            self.disconnect_time = datetime.now()
    
    def get_buffer(self) -> str:
        """Get buffered output for replay."""
        return self.output_buffer.get_contents()
    
    def write(self, data: str) -> None:
        """Write input to PTY."""
        if self.pty_session:
            self.pty_session.write(data)
    
    def resize(self, rows: int, cols: int) -> None:
        """Resize the PTY."""
        if self.pty_session:
            self.pty_session._set_size(rows, cols)
    
    def is_expired(self, timeout_seconds: int = SESSION_TIMEOUT) -> bool:
        """Check if session has expired (1hr after disconnect)."""
        if self.state == 'connected':
            return False
        if self.disconnect_time is None:
            return False
        elapsed = datetime.now() - self.disconnect_time
        return elapsed.total_seconds() > timeout_seconds
    
    def close(self) -> None:
        """Close session and cleanup resources."""
        if self.pty_session:
            self.pty_session.close()
            self.pty_session = None
        self.output_buffer.clear()


class SessionManager:
    """
    Manages persistent terminal sessions.
    Singleton pattern - one instance per application.
    """
    
    def __init__(self):
        self.sessions: Dict[str, PersistentSession] = {}
        self._lock = threading.Lock()
        self._cleanup_timer: Optional[threading.Timer] = None
        self._running = False
    
    def create_session(self, emit_callback: Callable[[str], None],
                       rows: int = 24, cols: int = 80) -> str:
        """Create new persistent session, returns session_id."""
        session_id = str(uuid.uuid4())
        session = PersistentSession(session_id)
        session.start_pty(rows, cols)
        session.attach(session_id, emit_callback)
        
        with self._lock:
            self.sessions[session_id] = session
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[PersistentSession]:
        """Get session by ID."""
        with self._lock:
            return self.sessions.get(session_id)
    
    def has_session(self, session_id: str) -> bool:
        """Check if session exists."""
        with self._lock:
            return session_id in self.sessions
    
    def remove_session(self, session_id: str) -> None:
        """Remove and close a session."""
        with self._lock:
            session = self.sessions.pop(session_id, None)
        if session:
            session.close()
    
    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count removed."""
        expired_ids = []
        with self._lock:
            for session_id, session in self.sessions.items():
                if session.is_expired():
                    expired_ids.append(session_id)
        
        for session_id in expired_ids:
            self.remove_session(session_id)
        
        return len(expired_ids)
    
    def start_cleanup_task(self) -> None:
        """Start background cleanup task (every 5 minutes)."""
        self._running = True
        self._schedule_cleanup()
    
    def stop_cleanup_task(self) -> None:
        """Stop the cleanup task."""
        self._running = False
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
    
    def _schedule_cleanup(self) -> None:
        if not self._running:
            return
        self._cleanup_timer = threading.Timer(
            CLEANUP_INTERVAL, self._cleanup_and_reschedule
        )
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def _cleanup_and_reschedule(self) -> None:
        try:
            self.cleanup_expired()
        finally:
            self._schedule_cleanup()


class PTYSession:
    """
    PTY session using native pty.fork() approach.
    
    Based on working sample-root implementation.
    Manages a single pseudo-terminal process with:
    - Background reader thread for output
    - Write method for input
    - Resize support
    """
    
    def __init__(self, session_id: str, output_callback: Callable[[str], None]):
        self.session_id = session_id
        self.output_callback = output_callback
        self.fd: Optional[int] = None
        self.pid: Optional[int] = None
        self._running = False
        self._reader_thread: Optional[threading.Thread] = None
        self.rows = 24
        self.cols = 80
    
    def start(self, rows: int = 24, cols: int = 80) -> None:
        """Spawn PTY with shell and start output reader."""
        import pty
        import select
        
        self.rows = rows
        self.cols = cols
        
        # Fork a new process with a PTY
        pid, fd = pty.fork()
        
        if pid == 0:
            # Child process - execute shell
            env = os.environ.copy()
            env['TERM'] = 'xterm-256color'
            env['LC_ALL'] = 'en_US.UTF-8'
            env['LANG'] = 'en_US.UTF-8'
            
            # Try to find shell
            shell = os.environ.get('SHELL', '/bin/zsh')
            if not os.path.exists(shell):
                shell = '/bin/zsh'
            if not os.path.exists(shell):
                shell = '/bin/bash'
            
            os.execvpe(shell, [shell], env)
        else:
            # Parent process
            self.fd = fd
            self.pid = pid
            self._running = True
            
            # Set terminal size
            self._set_size(rows, cols)
            
            # Start background thread to read output
            self._reader_thread = threading.Thread(
                target=self._read_loop,
                daemon=True
            )
            self._reader_thread.start()
    
    def _read_loop(self) -> None:
        """Background thread to read PTY output."""
        import select
        import codecs
        
        # Use incremental decoder to properly handle multi-byte UTF-8 sequences
        # that may be split across read() calls
        decoder = codecs.getincrementaldecoder('utf-8')('replace')
        
        while self._running and self.fd is not None:
            try:
                # Use select to wait for data with timeout
                r, _, _ = select.select([self.fd], [], [], 0.1)
                if self.fd in r:
                    data = os.read(self.fd, 4096)
                    if data:
                        # Use incremental decoder - it buffers incomplete sequences
                        text = decoder.decode(data)
                        if text:
                            # Emit output to client
                            self.output_callback(text)
                    else:
                        # EOF - process exited
                        self._running = False
                        break
            except (OSError, IOError):
                # FD closed or error
                self._running = False
                break
        
        # Flush any remaining bytes in the decoder
        try:
            final = decoder.decode(b'', final=True)
            if final:
                self.output_callback(final)
        except Exception:
            pass
    
    def write(self, data: str) -> None:
        """Write input to PTY."""
        if self.fd is not None:
            os.write(self.fd, data.encode('utf-8'))
    
    def _set_size(self, rows: int, cols: int) -> None:
        """Set the terminal size using ioctl."""
        if self.fd is not None:
            import fcntl
            import struct
            import termios
            
            # Ensure rows and cols are integers with defaults (may come as None or strings)
            self.rows = int(rows) if rows is not None else 24
            self.cols = int(cols) if cols is not None else 80
            winsize = struct.pack('HHHH', self.rows, self.cols, 0, 0)
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)
    
    def close(self) -> None:
        """Terminate PTY session and cleanup."""
        import signal
        
        self._running = False
        
        # Close file descriptor
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = None
        
        # Kill child process
        if self.pid is not None:
            try:
                os.kill(self.pid, signal.SIGTERM)
                os.waitpid(self.pid, os.WNOHANG)
            except (OSError, ChildProcessError):
                pass
            self.pid = None
    
    def isalive(self) -> bool:
        """Check if the PTY process is still running."""
        return self._running and self.fd is not None


# Global singleton
session_manager = SessionManager()
