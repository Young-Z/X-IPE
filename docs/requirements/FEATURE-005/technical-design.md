# Technical Design: Interactive Console

> Feature ID: FEATURE-005 | Version: v2.0 | Last Updated: 01-22-2026

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 01-18-2026 | Original design (WebSocket + PTY + VanillaTerminal) |
| v2.0 | 01-18-2026 | Polling-based HTTP REST (implemented, non-interactive) |
| v3.0 | 01-18-2026 | WebSocket + PTY + VanillaTerminal (current implementation) |
| **v4.0** | **01-22-2026** | **xterm.js + Session Persistence + Split Pane (this design)** |
| **v4.1** | **01-22-2026** | **Critical Fix: UTF-8 Incremental Decoder for multi-byte chars** |

---

## Critical Fix: UTF-8 Character Encoding (v4.1)

### Problem

When typing in the terminal, special characters (Unicode, emojis, Powerline symbols) displayed as "???" or diamond shapes. This occurred because multi-byte UTF-8 characters were being split across `os.read()` calls.

### Root Cause

```python
# BROKEN: Split multi-byte sequences cause corruption
data = os.read(self.fd, 4096)
self.output_callback(data.decode('utf-8', errors='replace'))  # ❌ "???" appears
```

When a 3-byte UTF-8 character (e.g., `→`) spans two read operations:
- Read 1: Gets bytes `[0xE2, 0x86]` (incomplete)
- Read 2: Gets byte `[0x92, ...]` (rest of char + more)
- Each decode produces replacement character `�` or `?`

### Solution

Use Python's **incremental UTF-8 decoder** which buffers incomplete sequences:

```python
# Location: src/services/terminal_service.py - PTYSession._read_loop()

import codecs

def _read_loop(self) -> None:
    """Background thread to read PTY output."""
    import select
    
    # Incremental decoder buffers incomplete multi-byte sequences
    decoder = codecs.getincrementaldecoder('utf-8')('replace')
    
    while self._running and self.fd is not None:
        try:
            r, _, _ = select.select([self.fd], [], [], 0.1)
            if self.fd in r:
                data = os.read(self.fd, 4096)
                if data:
                    # Decoder holds incomplete bytes until next read
                    text = decoder.decode(data)
                    if text:
                        self.output_callback(text)
                else:
                    self._running = False
                    break
        except (OSError, IOError):
            self._running = False
            break
    
    # Flush remaining bytes on exit
    try:
        final = decoder.decode(b'', final=True)
        if final:
            self.output_callback(final)
    except Exception:
        pass
```

### Key Points

| Aspect | Before | After |
|--------|--------|-------|
| Decoder | `data.decode('utf-8', errors='replace')` | `codecs.getincrementaldecoder('utf-8')` |
| Buffering | None - each read decoded independently | Incomplete sequences buffered across reads |
| Multi-byte chars | Corrupted to "???" | Rendered correctly |
| Performance | Same | Same (minimal overhead) |

### Files Changed

| File | Change |
|------|--------|
| `src/services/terminal_service.py` | `PTYSession._read_loop()` - use incremental decoder |

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating large projects.
> **📌 AI Coders:** Focus on this section for implementation context.

### Key Components

| Component | Responsibility | Location | Tags |
|-----------|----------------|----------|------|
| `SessionManager` | Manage persistent PTY sessions | `src/services/terminal_service.py` | #session #backend |
| `PersistentSession` | Wrap PTY with buffer + state | `src/services/terminal_service.py` | #session #pty |
| `OutputBuffer` | Circular buffer for reconnection | `src/services/terminal_service.py` | #buffer #replay |
| `Flask-SocketIO` | WebSocket server with session events | `src/app.py` | #websocket #api |
| `TerminalManager` | Frontend multi-terminal orchestrator | `index.html` | #frontend #manager |
| `xterm.js` | Full terminal emulator | CDN | #xterm #frontend |

### Scope & Boundaries

**In Scope (v4.0):**
- Replace VanillaTerminal with xterm.js 5.3.0
- Session persistence (1hr timeout, 10KB buffer)
- Auto-reconnection with session reattach
- Connection status indicator
- Multiple terminals (up to 2, split pane)
- Debounced resize with SIGWINCH

**Out of Scope:**
- Terminal themes/customization
- SSH to remote servers
- Command autocomplete
- More than 2 terminals
- Cross-browser session sync

### Dependencies

| Dependency | Source | Version | Purpose |
|------------|--------|---------|---------|
| xterm | CDN | 5.3.0 | Terminal emulator |
| xterm-addon-fit | CDN | 0.8.0 | Auto-resize to container |
| Socket.IO Client | CDN | 4.7.x | WebSocket client |
| Flask-SocketIO | PyPI | 5.x | WebSocket server |
| eventlet | PyPI | 0.33+ | Async for Socket.IO |
| ptyprocess | PyPI | 0.7+ | PTY management |

### Major Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Browser                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  TerminalManager (Orchestrates multiple terminals)                       ││
│  │  ┌────────────────────┐  ┌────────────────────────────────────────────┐ ││
│  │  │ Terminal 1 (xterm) │  │ Terminal 2 (xterm) [optional]              │ ││
│  │  │ - Socket 1         │  │ - Socket 2                                 │ ││
│  │  │ - Session ID 1     │  │ - Session ID 2                             │ ││
│  │  └────────────────────┘  └────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                          │ WebSocket (Socket.IO)                             │
└──────────────────────────│──────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Flask + Flask-SocketIO                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  WebSocket Event Handlers                                                ││
│  │  - connect: Log new connection                                           ││
│  │  - attach: Create or reattach session                                    ││
│  │  - input: Forward keystrokes to PTY                                      ││
│  │  - resize: Update PTY dimensions                                         ││
│  │  - disconnect: Detach socket, keep session alive                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                          │                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  SessionManager (Singleton)                                              ││
│  │  - sessions: Dict[str, PersistentSession]                                ││
│  │  - create_session() → session_id                                         ││
│  │  - get_session(session_id) → PersistentSession                           ││
│  │  - cleanup_expired() runs every 5 minutes                                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                          │                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  PersistentSession                                                       ││
│  │  - pty_session: PTYSession (ptyprocess)                                  ││
│  │  - output_buffer: OutputBuffer (10KB circular)                           ││
│  │  - state: 'connected' | 'disconnected'                                   ││
│  │  - disconnect_time: datetime (for 1hr expiry)                            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 2: Detailed Design

### 2.1 Backend Components

#### 2.1.1 OutputBuffer Class

**Purpose:** Circular buffer for storing recent terminal output for replay on reconnection.

```python
# Location: src/services/terminal_service.py

from collections import deque

BUFFER_MAX_CHARS = 10240  # 10KB limit

class OutputBuffer:
    """
    Circular buffer for terminal output.
    Uses deque with maxlen for automatic circular behavior.
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
```

#### 2.1.2 PersistentSession Class

**Purpose:** Wraps PTYSession with persistence support including buffer and state tracking.

```python
# Location: src/services/terminal_service.py

import uuid
import threading
from datetime import datetime
from typing import Callable, Optional

SESSION_TIMEOUT = 3600  # 1 hour in seconds

class PersistentSession:
    """
    Terminal session that persists across WebSocket disconnections.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.pty_session: Optional[PTYSession] = None
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
```

#### 2.1.3 SessionManager Class

**Purpose:** Manages all persistent sessions with lifecycle and cleanup.

```python
# Location: src/services/terminal_service.py

CLEANUP_INTERVAL = 300  # 5 minutes

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

# Global singleton
session_manager = SessionManager()
```

#### 2.1.4 WebSocket Event Handlers

**Purpose:** Handle terminal WebSocket events with session management.

```python
# Location: src/app.py

from src.services import session_manager

# Socket SID to Session ID mapping
socket_to_session: Dict[str, str] = {}

@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connection."""
    sid = request.sid
    print(f"[+] Client connected: {sid}")

@socketio.on('attach')
def handle_attach(data):
    """
    Handle session attachment.
    Creates new session or reconnects to existing one.
    """
    sid = request.sid
    requested_session_id = data.get('session_id') if data else None
    rows = data.get('rows', 24) if data else 24
    cols = data.get('cols', 80) if data else 80
    
    def emit_output(output_data: str):
        socketio.emit('output', output_data, room=sid)
    
    # Try to reconnect to existing session
    if requested_session_id and session_manager.has_session(requested_session_id):
        session = session_manager.get_session(requested_session_id)
        
        if session.is_expired():
            session_manager.remove_session(requested_session_id)
        else:
            # Reconnect to existing session
            session.attach(sid, emit_output)
            socket_to_session[sid] = requested_session_id
            
            # Replay buffered output
            buffer = session.get_buffer()
            if buffer:
                socketio.emit('output', buffer, room=sid)
            
            socketio.emit('reconnected', {'session_id': requested_session_id}, room=sid)
            return
    
    # Create new session
    session_id = session_manager.create_session(emit_output, rows, cols)
    session = session_manager.get_session(session_id)
    session.attach(sid, emit_output)
    socket_to_session[sid] = session_id
    
    socketio.emit('session_id', session_id, room=sid)
    socketio.emit('new_session', {'session_id': session_id}, room=sid)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection - keep session alive."""
    sid = request.sid
    session_id = socket_to_session.pop(sid, None)
    
    if session_id:
        session = session_manager.get_session(session_id)
        if session:
            session.detach()  # Keep PTY alive for reconnection

@socketio.on('input')
def handle_input(data):
    """Forward input to PTY."""
    sid = request.sid
    session_id = socket_to_session.get(sid)
    
    if session_id:
        session = session_manager.get_session(session_id)
        if session:
            session.write(data)

@socketio.on('resize')
def handle_resize(data):
    """Handle terminal resize."""
    sid = request.sid
    session_id = socket_to_session.get(sid)
    
    if session_id:
        session = session_manager.get_session(session_id)
        if session:
            rows = data.get('rows', 24)
            cols = data.get('cols', 80)
            session.resize(rows, cols)
```

### 2.2 Frontend Components

#### 2.2.1 CDN Dependencies

Add to `base.html` `<head>`:

```html
<!-- xterm.js from CDN -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css">
<script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js"></script>
<script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
```

#### 2.2.2 TerminalManager Class

**Purpose:** Orchestrate multiple terminal instances with session management.

```javascript
// Location: src/templates/index.html (script section)

/**
 * TerminalManager - Manages multiple xterm.js terminals
 */
class TerminalManager {
    constructor() {
        this.terminals = [];      // Terminal instances
        this.fitAddons = [];      // FitAddon instances
        this.sockets = [];        // Socket.IO connections
        this.sessionIds = [];     // Server session UUIDs
        this.activeIndex = -1;    // Currently focused pane
        this.maxTerminals = 2;
        
        this.container = document.getElementById('terminal-content');
        this.statusIndicator = document.getElementById('terminal-status-indicator');
        this.statusText = document.getElementById('terminal-status-text');
        
        this._initialize();
    }
    
    _initialize() {
        const storedIds = this._getStoredSessionIds();
        if (storedIds.length > 0) {
            storedIds.forEach(sessionId => this.addTerminal(sessionId));
        } else {
            this.addTerminal();
        }
    }
    
    addTerminal(existingSessionId = null) {
        if (this.terminals.length >= this.maxTerminals) {
            console.warn('[Terminal] Maximum terminals reached');
            return -1;
        }
        
        const index = this.terminals.length;
        
        // Create pane
        const pane = this._createPane(index);
        this.container.appendChild(pane);
        
        // Create xterm instance
        const terminal = new Terminal(this._getTerminalConfig());
        const fitAddon = new FitAddon.FitAddon();
        terminal.loadAddon(fitAddon);
        
        const contentDiv = pane.querySelector('.xterm-container');
        terminal.open(contentDiv);
        
        // Fit terminal
        requestAnimationFrame(() => {
            fitAddon.fit();
            terminal.refresh(0, terminal.rows - 1);
        });
        
        this.terminals.push(terminal);
        this.fitAddons.push(fitAddon);
        this.sessionIds.push(existingSessionId);
        
        // Create socket
        const socket = this._createSocket(index, existingSessionId);
        this.sockets.push(socket);
        
        // Handle input
        terminal.onData(data => {
            if (socket.connected) {
                socket.emit('input', data);
            }
        });
        
        this.setFocus(index);
        this._saveSessionIds();
        
        return index;
    }
    
    closeTerminal(index) {
        if (index < 0 || index >= this.terminals.length) return;
        
        // Cleanup
        this.sockets[index]?.disconnect();
        this.terminals[index]?.dispose();
        
        // Remove from arrays
        this.terminals.splice(index, 1);
        this.fitAddons.splice(index, 1);
        this.sockets.splice(index, 1);
        this.sessionIds.splice(index, 1);
        
        // Remove pane
        const pane = this.container.querySelector(`[data-pane-index="${index}"]`);
        pane?.remove();
        
        // Reindex
        this._reindexPanes();
        
        // Handle focus
        if (this.terminals.length > 0) {
            this.setFocus(Math.min(index, this.terminals.length - 1));
            setTimeout(() => this._resizeAll(), 50);
        } else {
            this.addTerminal();  // Always have at least one
        }
        
        this._saveSessionIds();
        this._updateStatus();
    }
    
    setFocus(index) {
        if (index < 0 || index >= this.terminals.length) return;
        
        this.container.querySelectorAll('.terminal-pane').forEach(p => {
            p.classList.remove('focused');
        });
        
        const pane = this.container.querySelector(`[data-pane-index="${index}"]`);
        pane?.classList.add('focused');
        
        this.activeIndex = index;
        this.terminals[index].focus();
    }
    
    _createPane(index) {
        const pane = document.createElement('div');
        pane.className = 'terminal-pane';
        pane.dataset.paneIndex = index;
        
        // Header
        const header = document.createElement('div');
        header.className = 'pane-header';
        header.innerHTML = `
            <span class="pane-title">Terminal ${index + 1}</span>
            <button class="close-pane-btn" title="Close">×</button>
        `;
        
        header.querySelector('.close-pane-btn').addEventListener('click', e => {
            e.stopPropagation();
            this.closeTerminal(parseInt(pane.dataset.paneIndex));
        });
        
        // Content
        const content = document.createElement('div');
        content.className = 'xterm-container';
        
        pane.appendChild(header);
        pane.appendChild(content);
        
        pane.addEventListener('click', () => {
            this.setFocus(parseInt(pane.dataset.paneIndex));
        });
        
        return pane;
    }
    
    _createSocket(index, existingSessionId) {
        const socket = io({
            transports: ['websocket'],
            reconnection: true,
            reconnectionAttempts: Infinity,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            timeout: 60000
        });
        
        socket.on('connect', () => {
            this._updateStatus();
            const dims = this.fitAddons[index]?.proposeDimensions();
            socket.emit('attach', {
                session_id: existingSessionId,
                rows: dims?.rows || 24,
                cols: dims?.cols || 80
            });
        });
        
        socket.on('session_id', sessionId => {
            this.sessionIds[index] = sessionId;
            this._saveSessionIds();
        });
        
        socket.on('new_session', data => {
            this.terminals[index].write('\x1b[32m[New session started]\x1b[0m\r\n');
            this.sessionIds[index] = data.session_id;
            this._saveSessionIds();
        });
        
        socket.on('reconnected', data => {
            this.terminals[index].write('\x1b[33m[Reconnected to session]\x1b[0m\r\n');
        });
        
        socket.on('output', data => {
            this.terminals[index].write(data);
        });
        
        socket.on('disconnect', reason => {
            this._updateStatus();
            if (reason !== 'io client disconnect') {
                this.terminals[index].write('\r\n\x1b[31m[Disconnected - reconnecting...]\x1b[0m\r\n');
            }
        });
        
        socket.io.on('reconnect', attempt => {
            this._updateStatus();
            const sessionId = this.sessionIds[index];
            const dims = this.fitAddons[index]?.proposeDimensions();
            socket.emit('attach', {
                session_id: sessionId,
                rows: dims?.rows || 24,
                cols: dims?.cols || 80
            });
        });
        
        return socket;
    }
    
    _getTerminalConfig() {
        return {
            cursorBlink: true,
            cursorStyle: 'block',
            fontSize: 14,
            fontFamily: 'Menlo, Monaco, "Courier New", monospace',
            scrollback: 1000,
            theme: {
                background: '#1e1e1e',
                foreground: '#d4d4d4',
                cursor: '#ffffff',
                selection: 'rgba(255, 255, 255, 0.3)',
                black: '#000000',
                red: '#cd3131',
                green: '#0dbc79',
                yellow: '#e5e510',
                blue: '#2472c8',
                magenta: '#bc3fbc',
                cyan: '#11a8cd',
                white: '#e5e5e5',
                brightBlack: '#666666',
                brightRed: '#f14c4c',
                brightGreen: '#23d18b',
                brightYellow: '#f5f543',
                brightBlue: '#3b8eea',
                brightMagenta: '#d670d6',
                brightCyan: '#29b8db',
                brightWhite: '#ffffff'
            }
        };
    }
    
    _updateStatus() {
        const connected = this.sockets.filter(s => s?.connected).length;
        const total = this.terminals.length;
        
        if (connected === total && total > 0) {
            this.statusIndicator.className = 'status-connected';
            this.statusText.textContent = total > 1 ? `Connected (${connected}/${total})` : 'Connected';
        } else if (connected > 0) {
            this.statusIndicator.className = 'status-connected';
            this.statusText.textContent = `Partial (${connected}/${total})`;
        } else {
            this.statusIndicator.className = 'status-disconnected';
            this.statusText.textContent = 'Disconnected';
        }
    }
    
    _resizeAll() {
        this.fitAddons.forEach((fitAddon, i) => {
            try {
                fitAddon.fit();
                this.terminals[i]?.refresh(0, this.terminals[i].rows - 1);
                const dims = fitAddon.proposeDimensions();
                if (dims && this.sockets[i]?.connected) {
                    this.sockets[i].emit('resize', { rows: dims.rows, cols: dims.cols });
                }
            } catch (e) {}
        });
    }
    
    _reindexPanes() {
        const panes = this.container.querySelectorAll('.terminal-pane');
        panes.forEach((pane, i) => {
            pane.dataset.paneIndex = i;
            pane.querySelector('.pane-title').textContent = `Terminal ${i + 1}`;
        });
    }
    
    _getStoredSessionIds() {
        try {
            const stored = localStorage.getItem('terminal_session_ids');
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            return [];
        }
    }
    
    _saveSessionIds() {
        try {
            const validIds = this.sessionIds.filter(id => id !== null);
            localStorage.setItem('terminal_session_ids', JSON.stringify(validIds));
        } catch (e) {}
    }
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
```

#### 2.2.3 HTML Structure Updates

```html
<!-- Terminal Panel (updated structure) -->
<div class="terminal-panel collapsed" id="terminal-panel">
    <div class="terminal-resize-handle" id="terminal-resize-handle"></div>
    <div class="terminal-header" id="terminal-header">
        <i class="bi bi-terminal"></i>
        <span class="terminal-title">Console</span>
        <div class="terminal-status">
            <span class="status-indicator" id="terminal-status-indicator"></span>
            <span class="status-text" id="terminal-status-text">Connecting...</span>
        </div>
        <div class="terminal-actions">
            <button id="add-terminal-btn" title="Add Terminal">+</button>
            <button id="terminal-toggle" title="Toggle terminal">
                <i class="bi bi-chevron-up"></i>
            </button>
        </div>
    </div>
    <div class="terminal-content" id="terminal-content">
        <!-- Panes inserted dynamically by TerminalManager -->
    </div>
</div>
```

#### 2.2.4 CSS Updates

```css
/* Terminal Panel Styles - add to base.html */

/* Status indicator */
.terminal-status {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-left: auto;
    margin-right: 10px;
    font-size: 12px;
    color: #888;
}

.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    transition: background-color 0.3s;
}

.status-indicator.status-connected {
    background-color: #4ec9b0;
    box-shadow: 0 0 4px #4ec9b0;
}

.status-indicator.status-disconnected {
    background-color: #f14c4c;
    box-shadow: 0 0 4px #f14c4c;
}

/* Split pane layout */
.terminal-content {
    display: flex;
    flex-direction: row;
    gap: 2px;
    height: 100%;
    overflow: hidden;
}

.terminal-pane {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 200px;
    border: 2px solid transparent;
    transition: border-color 0.2s;
}

.terminal-pane.focused {
    border-color: #007acc;
}

.pane-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2px 8px;
    background-color: #252526;
    height: 24px;
}

.pane-title {
    font-size: 11px;
    color: #888;
}

.terminal-pane.focused .pane-title {
    color: #ccc;
}

.close-pane-btn {
    width: 18px;
    height: 18px;
    border: none;
    border-radius: 3px;
    background: transparent;
    color: #888;
    cursor: pointer;
    font-size: 14px;
}

.close-pane-btn:hover {
    background-color: #c42b1c;
    color: #fff;
}

.xterm-container {
    flex: 1;
    padding: 4px;
    overflow: hidden;
}

/* Add terminal button */
#add-terminal-btn {
    width: 24px;
    height: 24px;
    border: none;
    background: transparent;
    color: #888;
    cursor: pointer;
    font-size: 16px;
}

#add-terminal-btn:hover:not(:disabled) {
    color: #fff;
}

#add-terminal-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}
```

---

## Part 3: Implementation Plan

### Phase 1: Core Upgrade (P1)

| Step | Task | Files | Est. |
|------|------|-------|------|
| 1.1 | Add xterm.js CDN links | `base.html` | 5m |
| 1.2 | Implement OutputBuffer class | `services/terminal_service.py` | 15m |
| 1.3 | Implement PersistentSession class | `services/terminal_service.py` | 30m |
| 1.4 | Implement SessionManager class | `services/terminal_service.py` | 30m |
| 1.5 | Update WebSocket handlers | `app.py` | 30m |
| 1.6 | Replace VanillaTerminal with xterm.js | `index.html` | 45m |
| 1.7 | Add localStorage session persistence | `index.html` | 15m |
| 1.8 | Test session persistence flow | - | 30m |

### Phase 2: UX Polish (P2)

| Step | Task | Files | Est. |
|------|------|-------|------|
| 2.1 | Add connection status indicator | `index.html`, `base.html` | 20m |
| 2.2 | Implement debounced resize | `index.html` | 15m |
| 2.3 | Panel height persistence | `index.html` | 10m |
| 2.4 | Reconnection messages | `index.html` | 10m |

### Phase 3: Advanced (P3)

| Step | Task | Files | Est. |
|------|------|-------|------|
| 3.1 | Implement TerminalManager class | `index.html` | 45m |
| 3.2 | Add split-pane CSS | `base.html` | 20m |
| 3.3 | Add terminal button functionality | `index.html` | 15m |
| 3.4 | Focus management | `index.html` | 15m |
| 3.5 | Multi-session localStorage | `index.html` | 10m |

---

## Part 4: Test Strategy

### Unit Tests

| Test | Description |
|------|-------------|
| `test_output_buffer_append` | Verify buffer appends data |
| `test_output_buffer_circular` | Verify 10KB limit enforced |
| `test_persistent_session_attach_detach` | Verify state transitions |
| `test_persistent_session_expiry` | Verify 1hr timeout |
| `test_session_manager_create` | Verify session creation |
| `test_session_manager_cleanup` | Verify expired session removal |

### Integration Tests

| Test | Description |
|------|-------------|
| `test_websocket_attach_new_session` | New session created on attach |
| `test_websocket_reconnect_existing` | Reconnect replays buffer |
| `test_websocket_session_expired` | Expired session creates new |
| `test_websocket_input_output` | Keystroke roundtrip works |
| `test_websocket_resize` | Resize signal sent to PTY |

### E2E Tests (Manual)

| Test | Description |
|------|-------------|
| Reconnection | Disconnect WiFi, reconnect, verify session preserved |
| Split pane | Add second terminal, verify both work |
| Buffer replay | Disconnect, run command on server, reconnect, verify output |

---

## Part 5: Migration Checklist

- [ ] Remove VanillaTerminal class from `index.html`
- [ ] Remove AnsiParser class from `index.html`
- [ ] Add xterm.js CDN links to `base.html`
- [ ] Add OutputBuffer, PersistentSession, SessionManager to `services/terminal_service.py`
- [ ] Update WebSocket handlers in `app.py`
- [ ] Replace terminal initialization in `index.html`
- [ ] Add connection status UI
- [ ] Add split-pane CSS
- [ ] Update tests for new architecture
- [ ] Start cleanup task in `app.py` main block
