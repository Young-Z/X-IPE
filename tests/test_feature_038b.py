"""
TDD Tests for FEATURE-038-B: Session Idle Detection
Tests: PersistentSession.is_idle(), SessionManager.find_idle_session(),
       SessionManager.claim_session_for_action(), strip_ansi()
"""
import pytest
import time
from unittest.mock import MagicMock, patch, PropertyMock


# ---------------------------------------------------------------------------
# Utility: strip_ansi
# ---------------------------------------------------------------------------

class TestStripAnsi:
    """Test ANSI escape sequence removal utility."""

    def test_strip_plain_text_unchanged(self):
        """Plain text without ANSI codes passes through unchanged."""
        from src.x_ipe.services.terminal_service import strip_ansi
        assert strip_ansi("hello world") == "hello world"

    def test_strip_color_codes(self):
        """Common color escape sequences are removed."""
        from src.x_ipe.services.terminal_service import strip_ansi
        colored = "\x1b[32muser@host\x1b[0m:\x1b[34m~/project\x1b[0m$ "
        assert strip_ansi(colored) == "user@host:~/project$ "

    def test_strip_bold_and_underline(self):
        """Bold and underline ANSI codes are removed."""
        from src.x_ipe.services.terminal_service import strip_ansi
        text = "\x1b[1mbold\x1b[0m \x1b[4munderline\x1b[0m"
        assert strip_ansi(text) == "bold underline"

    def test_strip_osc_sequences(self):
        """OSC (Operating System Command) sequences are removed."""
        from src.x_ipe.services.terminal_service import strip_ansi
        text = "\x1b]0;title\x07user@host$ "
        assert strip_ansi(text) == "user@host$ "

    def test_strip_empty_string(self):
        """Empty string returns empty."""
        from src.x_ipe.services.terminal_service import strip_ansi
        assert strip_ansi("") == ""

    def test_strip_multiple_codes_in_line(self):
        """Multiple ANSI codes in one line are all removed."""
        from src.x_ipe.services.terminal_service import strip_ansi
        text = "\x1b[1;32m$\x1b[0m \x1b[36m~\x1b[0m\x1b[33m%\x1b[0m "
        result = strip_ansi(text)
        assert "\x1b" not in result


# ---------------------------------------------------------------------------
# PersistentSession.is_idle()
# ---------------------------------------------------------------------------

class TestIsIdle:
    """Test PersistentSession.is_idle() method."""

    def _make_session(self, state='connected', buffer_content='', last_output_age=5.0):
        """Create a mock PersistentSession with controlled state."""
        from src.x_ipe.services.terminal_service import PersistentSession
        session = PersistentSession.__new__(PersistentSession)
        session.state = state
        session.output_buffer = MagicMock()
        session.output_buffer.get_contents.return_value = buffer_content
        session._last_output_time = time.time() - last_output_age
        return session

    def test_idle_at_dollar_prompt(self):
        """Session at '$ ' prompt with no recent output is idle."""
        session = self._make_session(buffer_content="user@host:~/project$ ", last_output_age=5.0)
        assert session.is_idle() is True

    def test_idle_at_percent_prompt(self):
        """Session at '% ' prompt is idle."""
        session = self._make_session(buffer_content="user@host% ", last_output_age=5.0)
        assert session.is_idle() is True

    def test_idle_at_hash_prompt(self):
        """Session at '# ' prompt (root) is idle."""
        session = self._make_session(buffer_content="root@host# ", last_output_age=5.0)
        assert session.is_idle() is True

    def test_idle_at_angle_prompt(self):
        """Session at '> ' prompt is idle."""
        session = self._make_session(buffer_content="PS C:\\> ", last_output_age=5.0)
        assert session.is_idle() is True

    def test_not_idle_when_disconnected(self):
        """Disconnected session is never idle."""
        session = self._make_session(state='disconnected', buffer_content="user@host$ ", last_output_age=5.0)
        assert session.is_idle() is False

    def test_not_idle_when_buffer_empty(self):
        """Session with empty buffer is not idle."""
        session = self._make_session(buffer_content="", last_output_age=5.0)
        assert session.is_idle() is False

    def test_not_idle_when_recent_output(self):
        """Session with recent output (within idle_timeout) is not idle."""
        session = self._make_session(buffer_content="user@host$ ", last_output_age=0.5)
        assert session.is_idle(idle_timeout=2.0) is False

    def test_not_idle_when_running_command(self):
        """Session showing command output (no prompt) is not idle."""
        session = self._make_session(buffer_content="Running tests...\n  PASS test_foo.py", last_output_age=5.0)
        assert session.is_idle() is False

    def test_not_idle_in_vim(self):
        """Session in vim is not idle (no shell prompt)."""
        session = self._make_session(buffer_content="~\n~\n~\n-- INSERT --", last_output_age=5.0)
        assert session.is_idle() is False

    def test_not_idle_in_less(self):
        """Session in less pager is not idle."""
        session = self._make_session(buffer_content="(END)", last_output_age=5.0)
        assert session.is_idle() is False

    def test_idle_with_ansi_colored_prompt(self):
        """Session with ANSI-colored prompt is correctly detected as idle."""
        colored_prompt = "\x1b[32muser@host\x1b[0m:\x1b[34m~/project\x1b[0m$ "
        session = self._make_session(buffer_content=colored_prompt, last_output_age=5.0)
        assert session.is_idle() is True

    def test_idle_multiline_buffer_checks_last_line(self):
        """Only the last non-empty line is checked for prompt."""
        content = "previous command output\nmore output\nuser@host$ "
        session = self._make_session(buffer_content=content, last_output_age=5.0)
        assert session.is_idle() is True

    def test_idle_with_custom_timeout(self):
        """Custom idle_timeout is respected."""
        session = self._make_session(buffer_content="user@host$ ", last_output_age=1.5)
        assert session.is_idle(idle_timeout=1.0) is True
        assert session.is_idle(idle_timeout=2.0) is False

    def test_idle_responds_within_100ms(self):
        """is_idle() should be fast (< 100ms)."""
        large_buffer = "line\n" * 1000 + "user@host$ "
        session = self._make_session(buffer_content=large_buffer, last_output_age=5.0)
        start = time.time()
        session.is_idle()
        elapsed = time.time() - start
        assert elapsed < 0.1


# ---------------------------------------------------------------------------
# SessionManager.find_idle_session()
# ---------------------------------------------------------------------------

class TestFindIdleSession:
    """Test SessionManager.find_idle_session() method."""

    def _make_manager_with_sessions(self, sessions_idle_states):
        """Create a SessionManager with mock sessions.
        sessions_idle_states: list of bools, each is the is_idle() return value
        """
        from src.x_ipe.services.terminal_service import SessionManager
        import threading
        manager = SessionManager.__new__(SessionManager)
        manager._lock = threading.Lock()
        manager.sessions = {}
        for i, is_idle in enumerate(sessions_idle_states):
            session = MagicMock()
            session.session_id = f"session-{i}"
            session.is_idle.return_value = is_idle
            manager.sessions[f"session-{i}"] = session
        return manager

    def test_find_returns_first_idle(self):
        """Returns the first idle session when multiple exist."""
        manager = self._make_manager_with_sessions([False, True, True])
        result = manager.find_idle_session()
        assert result is not None
        assert result.is_idle() is True

    def test_find_returns_none_when_all_busy(self):
        """Returns None when no session is idle."""
        manager = self._make_manager_with_sessions([False, False, False])
        result = manager.find_idle_session()
        assert result is None

    def test_find_returns_none_when_no_sessions(self):
        """Returns None when no sessions exist."""
        manager = self._make_manager_with_sessions([])
        result = manager.find_idle_session()
        assert result is None

    def test_find_single_idle_session(self):
        """Returns the only session if it's idle."""
        manager = self._make_manager_with_sessions([True])
        result = manager.find_idle_session()
        assert result is not None

    def test_find_is_thread_safe(self):
        """find_idle_session uses lock for thread safety."""
        manager = self._make_manager_with_sessions([True])
        # Should not deadlock when called
        result = manager.find_idle_session()
        assert result is not None


# ---------------------------------------------------------------------------
# SessionManager.claim_session_for_action()
# ---------------------------------------------------------------------------

class TestClaimSessionForAction:
    """Test SessionManager.claim_session_for_action() method."""

    def _make_manager_with_session(self, session_id='sess-1', state='connected'):
        """Create a SessionManager with one session."""
        from src.x_ipe.services.terminal_service import SessionManager
        import threading
        manager = SessionManager.__new__(SessionManager)
        manager._lock = threading.Lock()
        session = MagicMock()
        session.session_id = session_id
        session.state = state
        session.name = 'Session 1'
        manager.sessions = {session_id: session}
        return manager, session

    def test_claim_renames_session(self):
        """Claiming renames session to wf-{workflow}-{action}."""
        manager, session = self._make_manager_with_session()
        result = manager.claim_session_for_action('sess-1', 'hello', 'refine_idea')
        assert result is True
        assert session.name == 'wf-hello-refine_idea'

    def test_claim_nonexistent_session(self):
        """Claiming nonexistent session returns False."""
        manager, _ = self._make_manager_with_session()
        result = manager.claim_session_for_action('nonexistent', 'hello', 'refine_idea')
        assert result is False

    def test_claim_disconnected_session(self):
        """Claiming disconnected session returns False."""
        manager, session = self._make_manager_with_session(state='disconnected')
        result = manager.claim_session_for_action('sess-1', 'hello', 'refine_idea')
        assert result is False

    def test_claim_already_claimed_session(self):
        """Re-claiming an already-claimed session succeeds (idempotent)."""
        manager, session = self._make_manager_with_session()
        session.name = 'wf-hello-old_action'
        result = manager.claim_session_for_action('sess-1', 'hello', 'refine_idea')
        assert result is True
        assert session.name == 'wf-hello-refine_idea'
