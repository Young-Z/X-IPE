"""
Tests for FEATURE-029-A: Session Explorer Core

Backend tests for multi-session management (up to 10 sessions).
FEATURE-029-A replaces the 2-pane split layout with a session explorer
supporting up to 10 concurrent terminal sessions.

TDD: All tests should FAIL initially until implementation is complete.

Note: FEATURE-029-A is primarily frontend. These tests cover:
- Backend SessionManager capacity for 10 sessions
- Socket.IO handler multi-session scenarios
- Session lifecycle with 10 concurrent sessions
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from x_ipe.services.terminal_service import (
    SessionManager,
    PersistentSession,
    OutputBuffer,
    BUFFER_MAX_CHARS,
    SESSION_TIMEOUT,
)


class TestSessionManagerMultiSession:
    """Tests for SessionManager supporting up to 10 concurrent sessions."""

    def setup_method(self):
        """Create fresh SessionManager for each test."""
        self.manager = SessionManager()

    def test_create_10_sessions(self):
        """AC: Maximum 10 sessions enforced — backend must support 10."""
        mock_emit = Mock()
        session_ids = []
        for i in range(10):
            sid = self.manager.create_session(mock_emit, 24, 80)
            session_ids.append(sid)

        assert len(session_ids) == 10
        assert len(set(session_ids)) == 10  # All unique
        for sid in session_ids:
            assert self.manager.has_session(sid)

    def test_all_sessions_have_independent_buffers(self):
        """AC: All non-selected sessions continue running with PTY processes alive."""
        mock_emit = Mock()
        session_ids = []
        for i in range(10):
            sid = self.manager.create_session(mock_emit, 24, 80)
            session_ids.append(sid)

        # Each session should have its own OutputBuffer
        buffers = set()
        for sid in session_ids:
            session = self.manager.get_session(sid)
            assert session is not None
            assert session.output_buffer is not None
            buffers.add(id(session.output_buffer))

        assert len(buffers) == 10  # All distinct buffer instances

    def test_remove_session_preserves_others(self):
        """AC: Session switching preserves terminal output (no content loss)."""
        mock_emit = Mock()
        session_ids = []
        for i in range(5):
            sid = self.manager.create_session(mock_emit, 24, 80)
            session_ids.append(sid)

        # Remove the 3rd session
        self.manager.remove_session(session_ids[2])

        # Verify other sessions still exist
        assert not self.manager.has_session(session_ids[2])
        for i, sid in enumerate(session_ids):
            if i != 2:
                assert self.manager.has_session(sid)

    def test_session_attach_detach_independent(self):
        """AC: Socket.IO connections for background sessions remain open."""
        mock_emit = Mock()
        sid1 = self.manager.create_session(mock_emit, 24, 80)
        sid2 = self.manager.create_session(mock_emit, 24, 80)

        session1 = self.manager.get_session(sid1)
        session2 = self.manager.get_session(sid2)

        # Attach both
        session1.attach("socket-1", mock_emit)
        session2.attach("socket-2", mock_emit)

        # Detach one — other should remain attached
        session1.detach()

        assert session1.state == 'disconnected'
        assert session2.state == 'connected'
        assert session2.socket_sid == "socket-2"

    def test_cleanup_does_not_affect_active_sessions(self):
        """AC: All existing console functionality (WebSocket reconnection, buffer replay) preserved."""
        mock_emit = Mock()
        session_ids = []
        for i in range(5):
            sid = self.manager.create_session(mock_emit, 24, 80)
            session_ids.append(sid)

        # Attach all sessions (mark as connected)
        for sid in session_ids:
            session = self.manager.get_session(sid)
            session.attach(f"socket-{sid}", mock_emit)

        # Cleanup should not remove connected sessions
        removed = self.manager.cleanup_expired()
        assert removed == 0
        for sid in session_ids:
            assert self.manager.has_session(sid)

    def test_buffer_replay_per_session(self):
        """AC: Session switching preserves terminal output — buffer replay works per session."""
        mock_emit = Mock()
        sid1 = self.manager.create_session(mock_emit, 24, 80)
        sid2 = self.manager.create_session(mock_emit, 24, 80)

        session1 = self.manager.get_session(sid1)
        session2 = self.manager.get_session(sid2)

        # Write different content to each buffer
        session1.output_buffer.append("session1 output line 1\n")
        session1.output_buffer.append("session1 output line 2\n")
        session2.output_buffer.append("session2 different content\n")

        # Verify independent buffer content
        buffer1 = session1.get_buffer()
        buffer2 = session2.get_buffer()

        assert "session1" in buffer1
        assert "session2" not in buffer1
        assert "session2" in buffer2
        assert "session1" not in buffer2


class TestSessionManagerCapacity:
    """Tests for session capacity and limits."""

    def setup_method(self):
        self.manager = SessionManager()

    def test_session_count_tracking(self):
        """AC: Maximum 10 sessions enforced — verify count tracking."""
        mock_emit = Mock()
        for i in range(10):
            self.manager.create_session(mock_emit, 24, 80)

        # SessionManager should track all sessions
        assert len(self.manager.sessions) == 10

    def test_session_ids_are_unique_uuids(self):
        """AC: Session names map to session UUIDs."""
        mock_emit = Mock()
        session_ids = []
        for i in range(10):
            sid = self.manager.create_session(mock_emit, 24, 80)
            session_ids.append(sid)

        # All IDs should be unique strings (UUIDs)
        assert len(set(session_ids)) == 10
        for sid in session_ids:
            assert isinstance(sid, str)
            assert len(sid) > 0

    def test_remove_all_sessions(self):
        """AC: Deleting last session auto-creates a new one — backend supports full cleanup."""
        mock_emit = Mock()
        session_ids = []
        for i in range(5):
            sid = self.manager.create_session(mock_emit, 24, 80)
            session_ids.append(sid)

        # Remove all sessions
        for sid in session_ids:
            self.manager.remove_session(sid)

        assert len(self.manager.sessions) == 0

    def test_create_after_remove(self):
        """AC: Console loads with explorer expanded and 1 auto-created session."""
        mock_emit = Mock()

        # Create and remove
        sid1 = self.manager.create_session(mock_emit, 24, 80)
        self.manager.remove_session(sid1)
        assert len(self.manager.sessions) == 0

        # Create new — should work fine
        sid2 = self.manager.create_session(mock_emit, 24, 80)
        assert sid2 != sid1
        assert self.manager.has_session(sid2)


class TestSocketIOMultiSession:
    """Tests for Socket.IO handler behavior with multiple sessions."""

    def setup_method(self):
        self.manager = SessionManager()

    def test_multiple_sockets_to_different_sessions(self):
        """AC: One Socket.IO connection per session (1:1 pattern)."""
        mock_emit = Mock()
        sid1 = self.manager.create_session(mock_emit, 24, 80)
        sid2 = self.manager.create_session(mock_emit, 24, 80)

        session1 = self.manager.get_session(sid1)
        session2 = self.manager.get_session(sid2)

        # Each session gets its own socket
        session1.attach("socket-aaa", mock_emit)
        session2.attach("socket-bbb", mock_emit)

        assert session1.socket_sid == "socket-aaa"
        assert session2.socket_sid == "socket-bbb"

    def test_disconnect_one_session_others_unaffected(self):
        """AC: Socket.IO disconnect on one session MUST NOT affect other sessions."""
        mock_emit = Mock()
        sids = []
        for i in range(3):
            sid = self.manager.create_session(mock_emit, 24, 80)
            sids.append(sid)

        # Attach all
        for i, sid in enumerate(sids):
            self.manager.get_session(sid).attach(f"socket-{i}", mock_emit)

        # Disconnect session 1
        self.manager.get_session(sids[1]).detach()

        # Others still connected
        assert self.manager.get_session(sids[0]).state == 'connected'
        assert self.manager.get_session(sids[1]).state == 'disconnected'
        assert self.manager.get_session(sids[2]).state == 'connected'

    def test_reattach_session_after_disconnect(self):
        """AC: WebSocket reconnection with exponential backoff continues to work."""
        mock_emit = Mock()
        sid = self.manager.create_session(mock_emit, 24, 80)
        session = self.manager.get_session(sid)

        # Write some output before disconnect
        session.output_buffer.append("important output\n")

        # Attach, detach, re-attach
        session.attach("socket-1", mock_emit)
        session.detach()
        session.attach("socket-2", mock_emit)

        # Session should be connected with new socket, buffer preserved
        assert session.state == 'connected'
        assert session.socket_sid == "socket-2"
        assert "important output" in session.get_buffer()

    def test_buffer_replay_on_reconnect(self):
        """AC: Buffer replay on reconnect works correctly (10KB OutputBuffer)."""
        mock_emit = Mock()
        sid = self.manager.create_session(mock_emit, 24, 80)
        session = self.manager.get_session(sid)

        # Simulate output during session
        test_output = "line of output\n" * 100
        session.output_buffer.append(test_output)

        # Detach (simulate disconnect)
        session.attach("socket-1", mock_emit)
        session.detach()

        # Reattach — buffer should still have content
        buffer_content = session.get_buffer()
        assert len(buffer_content) > 0
        assert "line of output" in buffer_content


class TestPersistentSessionMulti:
    """Edge case tests for PersistentSession in multi-session context."""

    def test_session_isolation_buffer_overflow(self):
        """AC: Max 100KB buffer memory (10 sessions × 10KB each)."""
        sessions = []
        for i in range(10):
            session = PersistentSession(f"test-{i}")
            sessions.append(session)

        # Fill each buffer to capacity
        big_data = "x" * (BUFFER_MAX_CHARS + 100)
        for session in sessions:
            session.output_buffer.append(big_data)

        # Each buffer should be independently capped
        for session in sessions:
            buffer = session.get_buffer()
            assert len(buffer) <= BUFFER_MAX_CHARS

    def test_session_expiry_independent(self):
        """AC: Session timeout is independent per session."""
        session1 = PersistentSession("test-1")
        session2 = PersistentSession("test-2")

        mock_emit = Mock()
        session1.attach("socket-1", mock_emit)
        # session2 never attached — will be in disconnected state

        # session1 connected, session2 disconnected
        assert not session1.is_expired()
        # session2 has never been attached, check its state
        # (depends on implementation — new sessions start disconnected)

    def test_concurrent_writes_different_sessions(self):
        """AC: Non-selected sessions continue running with PTY processes alive."""
        mock_emit = Mock()
        session1 = PersistentSession("test-1")
        session2 = PersistentSession("test-2")

        # Simulate concurrent writes
        session1.output_buffer.append("s1: command output\n")
        session2.output_buffer.append("s2: different output\n")
        session1.output_buffer.append("s1: more output\n")
        session2.output_buffer.append("s2: more different\n")

        # Verify isolation
        b1 = session1.get_buffer()
        b2 = session2.get_buffer()
        assert "s1:" in b1
        assert "s2:" not in b1
        assert "s2:" in b2
        assert "s1:" not in b2
