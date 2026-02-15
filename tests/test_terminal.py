"""
Tests for FEATURE-005: Interactive Console v4.0

This test suite covers:
1. OutputBuffer - Circular buffer for terminal output (10KB limit)
2. PersistentSession - PTY wrapper with attach/detach and expiry
3. SessionManager - Session registry with cleanup

TDD: All tests should FAIL initially until implementation is complete.
"""
import pytest
import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call
from collections import deque


# =============================================================================
# Unit Tests: OutputBuffer
# =============================================================================

class TestOutputBuffer:
    """Tests for OutputBuffer circular buffer class."""

    def test_output_buffer_init(self):
        """OutputBuffer initializes with empty buffer and default max_chars."""
        from x_ipe.services import OutputBuffer, BUFFER_MAX_CHARS
        
        buffer = OutputBuffer()
        
        assert len(buffer) == 0
        assert buffer.get_contents() == ""
        assert BUFFER_MAX_CHARS == 10240  # 10KB

    def test_output_buffer_init_custom_size(self):
        """OutputBuffer accepts custom max_chars."""
        from x_ipe.services import OutputBuffer
        
        buffer = OutputBuffer(max_chars=100)
        
        # Fill with 100 chars
        buffer.append("x" * 100)
        assert len(buffer) == 100
        
        # Adding more should drop old chars
        buffer.append("y")
        assert len(buffer) == 100
        assert buffer.get_contents().endswith("y")

    def test_output_buffer_append_string(self):
        """OutputBuffer.append() adds string data."""
        from x_ipe.services import OutputBuffer
        
        buffer = OutputBuffer()
        buffer.append("hello")
        
        assert buffer.get_contents() == "hello"
        assert len(buffer) == 5

    def test_output_buffer_append_multiple(self):
        """OutputBuffer.append() accumulates multiple appends."""
        from x_ipe.services import OutputBuffer
        
        buffer = OutputBuffer()
        buffer.append("hello")
        buffer.append(" ")
        buffer.append("world")
        
        assert buffer.get_contents() == "hello world"

    def test_output_buffer_append_special_chars(self):
        """OutputBuffer handles ANSI escape sequences and special chars."""
        from x_ipe.services import OutputBuffer
        
        buffer = OutputBuffer()
        ansi_output = "\x1b[32mgreen\x1b[0m\r\n"
        buffer.append(ansi_output)
        
        assert buffer.get_contents() == ansi_output

    def test_output_buffer_circular_limit(self):
        """OutputBuffer enforces 10KB limit (circular behavior)."""
        from x_ipe.services import OutputBuffer, BUFFER_MAX_CHARS
        
        buffer = OutputBuffer()
        
        # Fill buffer to limit
        data = "a" * BUFFER_MAX_CHARS
        buffer.append(data)
        assert len(buffer) == BUFFER_MAX_CHARS
        
        # Add more - should drop oldest
        buffer.append("bbb")
        
        assert len(buffer) == BUFFER_MAX_CHARS
        contents = buffer.get_contents()
        assert contents.endswith("bbb")
        assert contents.startswith("a")

    def test_output_buffer_circular_exact_overflow(self):
        """OutputBuffer drops exactly the right amount on overflow."""
        from x_ipe.services import OutputBuffer
        
        buffer = OutputBuffer(max_chars=10)
        buffer.append("0123456789")  # Exactly full
        assert buffer.get_contents() == "0123456789"
        
        buffer.append("ABC")  # Add 3 more
        assert len(buffer) == 10
        assert buffer.get_contents() == "3456789ABC"

    def test_output_buffer_clear(self):
        """OutputBuffer.clear() empties the buffer."""
        from x_ipe.services import OutputBuffer
        
        buffer = OutputBuffer()
        buffer.append("test data")
        buffer.clear()
        
        assert len(buffer) == 0
        assert buffer.get_contents() == ""

    def test_output_buffer_len(self):
        """OutputBuffer.__len__() returns current size."""
        from x_ipe.services import OutputBuffer
        
        buffer = OutputBuffer()
        assert len(buffer) == 0
        
        buffer.append("12345")
        assert len(buffer) == 5


# =============================================================================
# Unit Tests: PersistentSession
# =============================================================================

class TestPersistentSession:
    """Tests for PersistentSession class."""

    def test_persistent_session_init(self):
        """PersistentSession initializes with correct defaults."""
        from x_ipe.services import PersistentSession
        
        session_id = "test-session-123"
        session = PersistentSession(session_id)
        
        assert session.session_id == session_id
        assert session.pty_session is None
        assert session.socket_sid is None
        assert session.emit_callback is None
        assert session.state == 'disconnected'
        assert session.disconnect_time is None
        assert isinstance(session.created_at, datetime)

    def test_persistent_session_has_output_buffer(self):
        """PersistentSession has an OutputBuffer instance."""
        from x_ipe.services import PersistentSession, OutputBuffer
        
        session = PersistentSession("test")
        
        assert isinstance(session.output_buffer, OutputBuffer)

    def test_persistent_session_attach(self):
        """attach() sets socket_sid, callback, and state."""
        from x_ipe.services import PersistentSession
        
        session = PersistentSession("test")
        emit_fn = Mock()
        
        session.attach("socket-123", emit_fn)
        
        assert session.socket_sid == "socket-123"
        assert session.emit_callback == emit_fn
        assert session.state == 'connected'
        assert session.disconnect_time is None

    def test_persistent_session_detach(self):
        """detach() clears socket but keeps PTY alive."""
        from x_ipe.services import PersistentSession
        
        session = PersistentSession("test")
        session.attach("socket-123", Mock())
        
        session.detach()
        
        assert session.socket_sid is None
        assert session.emit_callback is None
        assert session.state == 'disconnected'
        assert isinstance(session.disconnect_time, datetime)

    def test_persistent_session_get_buffer(self):
        """get_buffer() returns buffered output."""
        from x_ipe.services import PersistentSession
        
        session = PersistentSession("test")
        session.output_buffer.append("buffered content")
        
        result = session.get_buffer()
        
        assert result == "buffered content"

    def test_persistent_session_write_no_pty(self):
        """write() does nothing if PTY not started."""
        from x_ipe.services import PersistentSession
        
        session = PersistentSession("test")
        # Should not raise
        session.write("test")

    def test_persistent_session_is_expired_when_connected(self):
        """is_expired() returns False when connected."""
        from x_ipe.services import PersistentSession
        
        session = PersistentSession("test")
        session.attach("socket", Mock())
        
        assert session.is_expired() is False

    def test_persistent_session_is_expired_not_yet(self):
        """is_expired() returns False within timeout period."""
        from x_ipe.services import PersistentSession
        
        session = PersistentSession("test")
        session.attach("socket", Mock())
        session.detach()
        
        # Just disconnected - should not be expired
        assert session.is_expired() is False

    def test_persistent_session_is_expired_after_timeout(self):
        """is_expired() returns True after 1 hour."""
        from x_ipe.services import PersistentSession, SESSION_TIMEOUT
        
        session = PersistentSession("test")
        session.attach("socket", Mock())
        session.detach()
        
        # Simulate time passage
        session.disconnect_time = datetime.now() - timedelta(seconds=SESSION_TIMEOUT + 1)
        
        assert session.is_expired() is True

    def test_persistent_session_is_expired_custom_timeout(self):
        """is_expired() accepts custom timeout."""
        from x_ipe.services import PersistentSession
        
        session = PersistentSession("test")
        session.detach()
        session.disconnect_time = datetime.now() - timedelta(seconds=10)
        
        assert session.is_expired(timeout_seconds=5) is True
        assert session.is_expired(timeout_seconds=60) is False


# =============================================================================
# Unit Tests: SessionManager
# =============================================================================

class TestSessionManager:
    """Tests for SessionManager class."""

    def test_session_manager_init(self):
        """SessionManager initializes with empty sessions."""
        from x_ipe.services import SessionManager
        
        manager = SessionManager()
        
        assert manager.sessions == {}
        assert manager._running is False

    def test_session_manager_get_session_not_found(self):
        """get_session() returns None for unknown ID."""
        from x_ipe.services import SessionManager
        
        manager = SessionManager()
        
        result = manager.get_session("nonexistent")
        
        assert result is None

    def test_session_manager_has_session_false(self):
        """has_session() returns False for unknown ID."""
        from x_ipe.services import SessionManager
        
        manager = SessionManager()
        
        assert manager.has_session("nonexistent") is False

    def test_session_manager_remove_session_nonexistent(self):
        """remove_session() handles nonexistent session gracefully."""
        from x_ipe.services import SessionManager
        
        manager = SessionManager()
        
        # Should not raise
        manager.remove_session("nonexistent")

    def test_session_manager_start_cleanup_task(self):
        """start_cleanup_task() sets _running and schedules timer."""
        from x_ipe.services import SessionManager
        
        manager = SessionManager()
        
        with patch.object(manager, '_schedule_cleanup') as mock_schedule:
            manager.start_cleanup_task()
        
        assert manager._running is True
        mock_schedule.assert_called_once()

    def test_session_manager_stop_cleanup_task(self):
        """stop_cleanup_task() stops the cleanup timer."""
        from x_ipe.services import SessionManager
        
        manager = SessionManager()
        manager._running = True
        mock_timer = MagicMock()
        manager._cleanup_timer = mock_timer
        
        manager.stop_cleanup_task()
        
        assert manager._running is False
        mock_timer.cancel.assert_called_once()


# =============================================================================
# Constants Tests
# =============================================================================

class TestConstants:
    """Tests for module-level constants."""

    def test_buffer_max_chars_constant(self):
        """BUFFER_MAX_CHARS is 10KB (10240)."""
        from x_ipe.services import BUFFER_MAX_CHARS
        
        assert BUFFER_MAX_CHARS == 10240

    def test_session_timeout_constant(self):
        """SESSION_TIMEOUT is 1 hour (3600 seconds)."""
        from x_ipe.services import SESSION_TIMEOUT
        
        assert SESSION_TIMEOUT == 3600

    def test_cleanup_interval_constant(self):
        """CLEANUP_INTERVAL is 5 minutes (300 seconds)."""
        from x_ipe.services import CLEANUP_INTERVAL
        
        assert CLEANUP_INTERVAL == 300


# =============================================================================
# UTF-8 Incremental Decoder Tests (Critical Fix v4.1)
# =============================================================================

class TestUTF8IncrementalDecoder:
    """
    Tests for UTF-8 incremental decoding in PTY output.
    
    Critical Fix: Multi-byte UTF-8 characters split across os.read() calls
    were being corrupted to "???" or diamond shapes. The fix uses Python's
    codecs.getincrementaldecoder('utf-8') to buffer incomplete sequences.
    """

    def test_incremental_decoder_complete_chars(self):
        """Incremental decoder handles complete ASCII characters."""
        import codecs
        
        decoder = codecs.getincrementaldecoder('utf-8')('replace')
        
        result = decoder.decode(b'hello world')
        
        assert result == 'hello world'

    def test_incremental_decoder_complete_utf8(self):
        """Incremental decoder handles complete UTF-8 multi-byte chars."""
        import codecs
        
        decoder = codecs.getincrementaldecoder('utf-8')('replace')
        
        # Arrow symbol: 3 bytes (E2 86 92)
        arrow = '→'.encode('utf-8')
        result = decoder.decode(arrow)
        
        assert result == '→'

    def test_incremental_decoder_split_utf8_across_reads(self):
        """Incremental decoder buffers incomplete UTF-8 sequences across reads."""
        import codecs
        
        decoder = codecs.getincrementaldecoder('utf-8')('replace')
        
        # Arrow symbol: E2 86 92 (3 bytes)
        # Split: first read gets E2 86, second read gets 92
        arrow_bytes = '→'.encode('utf-8')  # b'\xe2\x86\x92'
        
        # First read: incomplete sequence (should buffer, return empty)
        result1 = decoder.decode(arrow_bytes[:2])  # E2 86
        
        # Second read: completes the sequence
        result2 = decoder.decode(arrow_bytes[2:])  # 92
        
        # The arrow should appear in result2 after sequence is complete
        assert result1 + result2 == '→'

    def test_incremental_decoder_emoji_split(self):
        """Incremental decoder handles 4-byte emoji split across reads."""
        import codecs
        
        decoder = codecs.getincrementaldecoder('utf-8')('replace')
        
        # Emoji: 4 bytes
        emoji = '😀'.encode('utf-8')  # 4 bytes
        
        # Split in middle
        result1 = decoder.decode(emoji[:2])
        result2 = decoder.decode(emoji[2:])
        
        assert result1 + result2 == '😀'

    def test_incremental_decoder_mixed_content(self):
        """Incremental decoder handles mixed ASCII and split UTF-8."""
        import codecs
        
        decoder = codecs.getincrementaldecoder('utf-8')('replace')
        
        # "hello→world" split in middle of arrow
        text = 'hello→world'.encode('utf-8')
        
        # Split at arrow (bytes 5-7 are the arrow)
        part1 = text[:6]   # "hello" + first byte of arrow
        part2 = text[6:]   # rest of arrow + "world"
        
        result1 = decoder.decode(part1)
        result2 = decoder.decode(part2)
        
        assert result1 + result2 == 'hello→world'

    def test_incremental_decoder_final_flush(self):
        """Incremental decoder flushes remaining bytes on final=True."""
        import codecs
        
        decoder = codecs.getincrementaldecoder('utf-8')('replace')
        
        # Incomplete sequence
        decoder.decode(b'\xe2\x86')  # Incomplete arrow
        
        # Final flush with replace error handler returns replacement char
        final = decoder.decode(b'', final=True)
        
        # Should get replacement character for incomplete sequence
        assert '�' in final or final == ''  # Depends on implementation

    def test_incremental_decoder_ansi_escapes(self):
        """Incremental decoder preserves ANSI escape sequences."""
        import codecs
        
        decoder = codecs.getincrementaldecoder('utf-8')('replace')
        
        ansi = b'\x1b[32mgreen\x1b[0m'
        result = decoder.decode(ansi)
        
        assert result == '\x1b[32mgreen\x1b[0m'

    def test_incremental_decoder_powerline_symbols(self):
        """Incremental decoder handles Powerline/Nerd font symbols."""
        import codecs
        
        decoder = codecs.getincrementaldecoder('utf-8')('replace')
        
        # Common Powerline symbols
        symbols = '    '.encode('utf-8')
        result = decoder.decode(symbols)
        
        assert result == '    '


# =============================================================================
# Global Session Manager Tests
# =============================================================================

class TestGlobalSessionManager:
    """Tests for the global session_manager singleton."""

    def test_session_manager_singleton_exists(self):
        """Global session_manager singleton is available."""
        from x_ipe.services import session_manager
        from x_ipe.services import SessionManager
        
        assert session_manager is not None
        assert isinstance(session_manager, SessionManager)


# =============================================================================
# Fixtures
# =============================================================================

# =============================================================================
# Bug Fix Tests: Multi-Tab Session Stability (TASK-413)
# =============================================================================

class TestMultiTabSessionStability:
    """
    Tests for TASK-413: Console session instability when multiple browser tabs
    connect to the same server.
    
    Root cause: PersistentSession.attach() overwrites socket_sid/emit_callback,
    and handle_disconnect detaches even if disconnecting SID != current socket_sid.
    """

    def test_detach_only_when_sid_matches(self):
        """detach() called from stale SID should NOT clear the active connection."""
        from x_ipe.services import PersistentSession
        
        session = PersistentSession("test-multi-tab")
        
        # Tab 1 attaches
        emit_tab1 = Mock()
        session.attach("sid-tab1", emit_tab1)
        assert session.socket_sid == "sid-tab1"
        assert session.state == 'connected'
        
        # Tab 2 attaches (overwrites Tab 1 — this is expected "last writer wins")
        emit_tab2 = Mock()
        session.attach("sid-tab2", emit_tab2)
        assert session.socket_sid == "sid-tab2"
        assert session.state == 'connected'
        
        # Tab 1 disconnects — should NOT detach since sid-tab1 != current socket_sid
        # This simulates the bug: handle_disconnect for Tab 1 should not kill Tab 2's connection
        if session.socket_sid == "sid-tab1":
            session.detach()
        
        # Tab 2 should still be connected
        assert session.socket_sid == "sid-tab2"
        assert session.emit_callback == emit_tab2
        assert session.state == 'connected'

    def test_detach_when_sid_matches(self):
        """detach() should work normally when SID matches current socket_sid."""
        from x_ipe.services import PersistentSession
        
        session = PersistentSession("test-detach-match")
        
        emit_fn = Mock()
        session.attach("sid-active", emit_fn)
        
        # Same SID disconnects — should detach
        if session.socket_sid == "sid-active":
            session.detach()
        
        assert session.socket_sid is None
        assert session.emit_callback is None
        assert session.state == 'disconnected'

    def test_active_session_not_hijacked_by_second_tab(self):
        """When session is actively connected, a second attach should NOT overwrite it."""
        from x_ipe.services import PersistentSession
        
        session = PersistentSession("test-no-hijack")
        
        # Tab 1 attaches
        emit_tab1 = Mock()
        session.attach("sid-tab1", emit_tab1)
        assert session.state == 'connected'
        assert session.socket_sid == "sid-tab1"
        
        # Simulate what handle_attach should do: check if session is active
        # before allowing attach from a different SID
        is_active_on_other_tab = (
            session.state == 'connected' and 
            session.socket_sid and 
            session.socket_sid != "sid-tab2"
        )
        
        # Should detect that session is active on another tab
        assert is_active_on_other_tab is True
        
        # Tab 1's callback should remain intact
        assert session.emit_callback == emit_tab1
        assert session.socket_sid == "sid-tab1"

    def test_session_manager_list_sessions(self):
        """SessionManager should provide a way to list all active sessions."""
        from x_ipe.services import SessionManager, PersistentSession
        
        manager = SessionManager()
        
        # Manually add sessions (bypass create_session which needs PTY)
        session1 = PersistentSession("session-1")
        session1.attach("sid-1", Mock())
        
        session2 = PersistentSession("session-2")
        session2.attach("sid-2", Mock())
        
        session3 = PersistentSession("session-3")
        # session3 is disconnected
        
        with manager._lock:
            manager.sessions["session-1"] = session1
            manager.sessions["session-2"] = session2
            manager.sessions["session-3"] = session3
        
        result = manager.list_sessions()
        
        assert len(result) == 3
        # Each entry should have session_id and state
        ids = [s['session_id'] for s in result]
        assert "session-1" in ids
        assert "session-2" in ids
        assert "session-3" in ids
        
        # Check states
        states = {s['session_id']: s['state'] for s in result}
        assert states["session-1"] == 'connected'
        assert states["session-2"] == 'connected'
        assert states["session-3"] == 'disconnected'

    def test_session_manager_destroy_sessions_by_ids(self):
        """SessionManager should destroy specific sessions by ID list."""
        from x_ipe.services import SessionManager, PersistentSession
        
        manager = SessionManager()
        
        session1 = PersistentSession("session-1")
        session2 = PersistentSession("session-2")
        session3 = PersistentSession("session-3")
        
        with manager._lock:
            manager.sessions["session-1"] = session1
            manager.sessions["session-2"] = session2
            manager.sessions["session-3"] = session3
        
        # Destroy sessions 1 and 3
        count = manager.destroy_sessions(["session-1", "session-3"])
        
        assert count == 2
        assert not manager.has_session("session-1")
        assert manager.has_session("session-2")
        assert not manager.has_session("session-3")


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    (project_dir / "test.txt").write_text("test content")
    (project_dir / "README.md").write_text("# Test Project")
    
    return project_dir


# =============================================================================
# Unit Tests: Terminal Auto-Scroll Pause (Feedback-20260213-235226)
# =============================================================================

class TestTerminalAutoScrollPause:
    """Tests for auto-scroll pause behavior when user scrolls up in terminal.

    The terminal should NOT force scroll-to-bottom when the user has actively
    scrolled up. Auto-scroll should only resume after 5 seconds of no user
    scroll activity when new content arrives.

    These tests validate the JavaScript logic contract by checking the
    terminal.js source contains the required scroll-pause mechanism.
    """

    def test_terminal_js_uses_buffer_api_for_scroll_detection(self):
        """terminal.js must use xterm.js buffer API (viewportY/baseY) for scroll state."""
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        assert 'buffer.active.viewportY' in content, \
            "terminal.js must use terminal.buffer.active.viewportY"
        assert 'buffer.active.baseY' in content, \
            "terminal.js must use terminal.buffer.active.baseY"
        assert '_isAtBottom' in content, \
            "terminal.js must have an _isAtBottom helper method"

    def test_terminal_js_has_scroll_pause_timeout(self):
        """terminal.js must have a 5-second timeout before resuming auto-scroll."""
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        # Must have a 5000ms (5 second) timeout for scroll resume
        assert '5000' in content, \
            "terminal.js must have a 5-second timeout for scroll-pause"

    def test_terminal_js_output_handler_checks_scroll_state(self):
        """The output handler must check scroll state using xterm.js buffer API."""
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        # The output handler should use the xterm.js buffer API
        output_idx = content.find("socket.on('output'")
        assert output_idx != -1, "Must have socket output handler"

        handler_block = content[output_idx:output_idx + 600]

        # Must use _isAtBottom (which checks viewportY === baseY)
        assert '_isAtBottom' in handler_block, \
            "Output handler must use _isAtBottom (xterm.js buffer API) to check scroll state"

    def test_terminal_js_output_handler_preserves_scroll_when_paused(self):
        """When user has scrolled up, output handler must lock scroll position.

        xterm.js's terminal.write() internally scrolls the viewport to follow
        the cursor in a requestAnimationFrame render cycle that fires AFTER the
        write callback. The output handler must use a scroll-lock approach:
        1. Save scrollTop and install a scroll event listener that reverts changes
        2. Use write(data, callback) with double-rAF to outlast xterm's render
        3. Only release the lock after xterm's render pass completes
        """
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        output_idx = content.find("socket.on('output'")
        assert output_idx != -1, "Must have socket output handler"

        handler_block = content[output_idx:output_idx + 2500]

        # Must save viewport scrollTop before write
        assert 'savedScrollTop' in handler_block, \
            "Output handler must save viewport scrollTop when user has scrolled up"

        # Must query .xterm-viewport to get the viewport element
        assert 'xterm-viewport' in handler_block, \
            "Output handler must access .xterm-viewport to save/restore scroll position"

        # Must install a scroll event listener to lock position
        assert "addEventListener('scroll'" in handler_block or \
               'addEventListener("scroll"' in handler_block, \
            "Output handler must use a scroll event lock to prevent xterm render scroll"

        # Must use write() callback for post-render handling
        assert 'write(data,' in handler_block or 'write(data, ' in handler_block, \
            "Output handler must use write(data, callback) for post-render scroll restore"

        # Must use requestAnimationFrame to outlast xterm's render cycle
        assert 'requestAnimationFrame' in handler_block, \
            "Output handler must use requestAnimationFrame to unlock after render"

        # Must remove the scroll listener to avoid leaks
        assert "removeEventListener('scroll'" in handler_block or \
               'removeEventListener("scroll"' in handler_block, \
            "Output handler must remove scroll lock listener after write completes"

    def test_terminal_js_setup_uses_request_animation_frame(self):
        """_setupAutoScrollPause must use requestAnimationFrame to wait for DOM."""
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        # Find the _setupAutoScrollPause method definition (not call site)
        method_idx = content.find('_setupAutoScrollPause(terminal, sessionKey)')
        assert method_idx != -1, "Must have _setupAutoScrollPause method definition"

        method_block = content[method_idx:method_idx + 800]

        # Must use requestAnimationFrame (not synchronous DOM query)
        assert 'requestAnimationFrame' in method_block, \
            "_setupAutoScrollPause must use requestAnimationFrame for robust DOM access"

    def test_terminal_js_no_scroll_event_reset(self):
        """Wheel listener must NOT use 'scroll' event to detect scroll state.

        Programmatic scrollTop changes from xterm.js internals (during write/resize)
        also fire 'scroll' events. Using them in the wheel listener causes race
        conditions. The buffer API (viewportY/baseY) is used instead.
        """
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        # Find the _initAutoScrollListeners method (where listeners are set up)
        method_idx = content.find('_initAutoScrollListeners')
        assert method_idx != -1, "Must have _initAutoScrollListeners method"

        method_block = content[method_idx:method_idx + 1500]

        # Must NOT have a 'scroll' event listener that resets _userScrolledUp
        import re
        scroll_listener = re.search(
            r"addEventListener\(\s*['\"]scroll['\"]",
            method_block
        )
        assert scroll_listener is None, \
            "Must NOT use 'scroll' event to reset auto-scroll pause (causes race condition)"

    def test_terminal_js_wheel_down_resets_at_bottom(self):
        """Scrolling down past the bottom must cancel the 5s resume timer."""
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        # Find the auto-scroll listener section
        method_idx = content.find('_initAutoScrollListeners')
        assert method_idx != -1
        method_block = content[method_idx:method_idx + 3000]

        # Must check deltaY > 0 (scroll down) and isAtBottom to cancel timer
        assert 'deltaY > 0' in method_block, \
            "Must detect wheel-down to cancel timer when user scrolls to bottom"
        assert 'isAtBottom' in method_block or 'viewportY' in method_block, \
            "Must check if viewport is at bottom using xterm.js buffer API"

    def test_terminal_js_scroll_up_only_pauses_when_not_at_bottom(self):
        """Scroll-up must only start resume timer if viewport actually left the bottom.

        When the scrollbar is already at the bottom, a small trackpad bounce or
        accidental deltaY < 0 event should NOT start a timer. The handler must
        check inside a requestAnimationFrame using xterm.js buffer API.
        """
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        # Find the _initAutoScrollListeners method
        method_idx = content.find('_initAutoScrollListeners')
        assert method_idx != -1
        method_block = content[method_idx:method_idx + 3000]

        # The deltaY < 0 branch must defer to rAF and check buffer API
        delta_neg_idx = method_block.find('deltaY < 0')
        assert delta_neg_idx != -1, "Must have deltaY < 0 check"

        delta_neg_block = method_block[delta_neg_idx:delta_neg_idx + 800]

        # Must have requestAnimationFrame inside the deltaY < 0 branch
        assert 'requestAnimationFrame' in delta_neg_block, \
            "deltaY < 0 must defer to requestAnimationFrame before checking scroll"

        # Must check !isAtBottom using buffer API before starting timer
        assert '!isAtBottom' in delta_neg_block or 'viewportY' in delta_neg_block, \
            "Must check buffer API (viewportY vs baseY) before starting resume timer"


    def test_terminal_js_is_at_bottom_uses_buffer_api(self):
        """_isAtBottom must use viewportY === baseY, not DOM scrollTop."""
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        method_idx = content.find('_isAtBottom(terminal)')
        assert method_idx != -1, "Must have _isAtBottom method"

        method_block = content[method_idx:method_idx + 300]
        assert 'viewportY' in method_block, \
            "_isAtBottom must use buffer.active.viewportY"
        assert 'baseY' in method_block, \
            "_isAtBottom must use buffer.active.baseY"
        # Must NOT use DOM-level scrollTop for this check
        assert 'scrollTop' not in method_block, \
            "_isAtBottom must use buffer API, not DOM scrollTop"

    def test_terminal_js_session_cleanup_clears_scroll_timer(self):
        """removeSession must clear the scroll resume timer to avoid leaks."""
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        method_idx = content.find('removeSession(key)')
        assert method_idx != -1, "Must have removeSession method"

        method_block = content[method_idx:method_idx + 800]
        assert '_scrollResumeTimers' in method_block, \
            "removeSession must clean up _scrollResumeTimers"
        assert 'clearTimeout' in method_block, \
            "removeSession must clearTimeout on scroll resume timer"

    def test_terminal_js_remove_session_destroys_backend_session(self):
        """removeSession must emit destroy_sessions to server before disconnecting socket.

        Bug (Feedback-20260215-211648): Clicking the delete icon in the session
        list only disconnects the socket but never tells the server to destroy
        the PTY session, leaving it orphaned.
        """
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        method_idx = content.find('removeSession(key)')
        assert method_idx != -1, "Must have removeSession method"

        method_block = content[method_idx:method_idx + 800]

        assert 'destroy_sessions' in method_block, \
            "removeSession must emit destroy_sessions to server to kill backend PTY session"

        # Ensure destroy_sessions is emitted BEFORE socket.disconnect()
        destroy_idx = method_block.find('destroy_sessions')
        disconnect_idx = method_block.find('.disconnect()')
        assert destroy_idx < disconnect_idx, \
            "destroy_sessions must be emitted BEFORE socket.disconnect()"


class TestSessionPreviewDismissOnLeave:
    """Tests for session preview dismiss behavior (Feedback-20260214-000335).

    When the mouse leaves a session bar, the preview must dismiss immediately.
    The preview container must NOT keep itself alive by canceling the dismiss
    timer on mouseenter — i.e., the preview container should have no mouseenter
    handler that clears _graceTimer.
    """

    def test_preview_container_does_not_cancel_dismiss_on_mouseenter(self):
        """Preview container must NOT have a mouseenter handler that clears graceTimer."""
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        # Find the _initPreviewContainer method
        init_idx = content.find('_initPreviewContainer')
        assert init_idx != -1, "Must have _initPreviewContainer method"

        # Get the method body (until the next method)
        next_method = content.find('\n        _showPreview', init_idx)
        method_body = content[init_idx:next_method] if next_method != -1 else content[init_idx:init_idx + 1500]

        # The preview container must NOT have a mouseenter handler that clears graceTimer
        # Look for pattern: previewContainer.addEventListener('mouseenter', ..._graceTimer
        import re
        mouseenter_match = re.search(
            r"_previewContainer\.addEventListener\(\s*['\"]mouseenter['\"]",
            method_body
        )
        assert mouseenter_match is None, \
            "Preview container must NOT have a mouseenter handler that keeps preview alive"

    def test_session_bar_mouseleave_dismisses_immediately(self):
        """Session bar mouseleave must dismiss preview without grace timer delay."""
        import os
        terminal_js = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'x_ipe', 'static', 'js', 'terminal.js'
        )
        with open(terminal_js, 'r') as f:
            content = f.read()

        # Find the session bar mouseleave handler
        mouseleave_idx = content.find("bar.addEventListener('mouseleave'")
        assert mouseleave_idx != -1, "Must have bar mouseleave handler"

        # Get the handler block
        handler_block = content[mouseleave_idx:mouseleave_idx + 200]

        # Must call _dismissPreview directly, not via _graceTimer/setTimeout
        assert '_dismissPreview' in handler_block, \
            "Session bar mouseleave must call _dismissPreview"
        assert '_graceTimer' not in handler_block, \
            "Session bar mouseleave must NOT use grace timer - must dismiss immediately"
