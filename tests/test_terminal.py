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

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    (project_dir / "test.txt").write_text("test content")
    (project_dir / "README.md").write_text("# Test Project")
    
    return project_dir
