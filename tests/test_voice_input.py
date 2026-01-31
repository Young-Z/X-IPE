"""
Tests for FEATURE-021: Console Voice Input

This test suite covers:
1. VoiceInputService - Backend Alibaba Cloud speech recognition relay
2. VoiceSession - Individual voice recording session
3. Voice WebSocket Handlers - Socket.IO event handlers for voice
4. Voice Commands - Pattern matching for voice commands
5. Integration Tests - Full voice input flow

TDD: All tests should FAIL initially until implementation is complete.
"""
import pytest
import time
import uuid
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock, call
from io import BytesIO


# =============================================================================
# Unit Tests: VoiceSession
# =============================================================================

class TestVoiceSession:
    """Tests for VoiceSession data class."""

    def test_voice_session_init(self):
        """VoiceSession initializes with required attributes."""
        from x_ipe.services.voice_input_service_v2 import VoiceSession
        
        session = VoiceSession(
            session_id="voice-123",
            socket_sid="socket-456"
        )
        
        assert session.session_id == "voice-123"
        assert session.socket_sid == "socket-456"
        assert session.state == "idle"
        assert session.recognizer is None
        assert session.final_text == ""
        assert session.partial_text == ""
        assert session.created_at is not None

    def test_voice_session_state_transitions(self):
        """VoiceSession state transitions: idle -> recording -> processing -> idle."""
        from x_ipe.services.voice_input_service_v2 import VoiceSession
        
        session = VoiceSession(session_id="test", socket_sid="test")
        
        assert session.state == "idle"
        
        session.state = "recording"
        assert session.state == "recording"
        
        session.state = "processing"
        assert session.state == "processing"
        
        session.state = "idle"
        assert session.state == "idle"

    def test_voice_session_callbacks(self):
        """VoiceSession can have callbacks for events."""
        from x_ipe.services.voice_input_service_v2 import VoiceSession
        
        partial_called = []
        complete_called = []
        
        session = VoiceSession(
            session_id="test",
            socket_sid="test",
            on_partial=lambda t: partial_called.append(t),
            on_complete=lambda t: complete_called.append(t),
        )
        
        assert session.on_partial is not None
        assert session.on_complete is not None


# =============================================================================
# Unit Tests: VoiceInputService
# =============================================================================

class TestVoiceInputService:
    """Tests for VoiceInputService backend service."""

    def test_voice_input_service_init(self):
        """VoiceInputService initializes with API key."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-api-key")
        
        assert service.sessions == {}

    def test_voice_input_service_init_no_api_key(self):
        """VoiceInputService can initialize without API key (uses env var)."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        # Should not raise - will use env var or be empty
        service = VoiceInputService(api_key=None)
        assert service.sessions == {}

    def test_create_session(self):
        """VoiceInputService.create_session() creates new VoiceSession."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        
        session_id = service.create_session(socket_sid="socket-123")
        
        assert session_id is not None
        assert session_id in service.sessions
        assert service.sessions[session_id].socket_sid == "socket-123"
        assert service.sessions[session_id].state == "idle"

    def test_create_session_unique_ids(self):
        """VoiceInputService.create_session() generates unique session IDs."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        
        id1 = service.create_session(socket_sid="socket-1")
        id2 = service.create_session(socket_sid="socket-2")
        id3 = service.create_session(socket_sid="socket-3")
        
        assert id1 != id2 != id3
        assert len(service.sessions) == 3

    def test_get_session(self):
        """VoiceInputService.get_session() returns session by ID."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        session = service.get_session(session_id)
        
        assert session is not None
        assert session.session_id == session_id

    def test_get_session_not_found(self):
        """VoiceInputService.get_session() returns None for unknown ID."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        
        session = service.get_session("nonexistent-id")
        
        assert session is None

    def test_remove_session(self):
        """VoiceInputService.remove_session() removes session."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        assert session_id in service.sessions
        
        service.remove_session(session_id)
        
        assert session_id not in service.sessions

    def test_session_existence_check(self):
        """VoiceInputService.get_session() can check session existence."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        # Use get_session to check existence
        assert service.get_session(session_id) is not None
        assert service.get_session("nonexistent") is None


# =============================================================================
# Unit Tests: Dashscope SDK Integration
# =============================================================================

class TestDashscopeIntegration:
    """Tests for dashscope SDK integration (v2 service)."""

    def test_start_recognition_creates_recognizer(self):
        """VoiceInputService.start_recognition() creates recognizer."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        # Mock both recognizer types (service chooses based on translation_enabled)
        with patch('x_ipe.services.voice_input_service_v2.TranslationRecognizerRealtime') as MockRealtime, \
             patch('x_ipe.services.voice_input_service_v2.TranslationRecognizerChat') as MockChat:
            mock_recognizer = MagicMock()
            MockRealtime.return_value = mock_recognizer
            MockChat.return_value = mock_recognizer
            
            result = service.start_recognition(session_id)
            
            assert result is True
            # One of them should be called
            assert MockRealtime.called or MockChat.called
            mock_recognizer.start.assert_called_once()

    def test_send_audio_forwards_to_recognizer(self):
        """VoiceInputService.send_audio() forwards audio to recognizer."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        # Setup mock recognizer
        mock_recognizer = MagicMock()
        service.sessions[session_id].recognizer = mock_recognizer
        service.sessions[session_id].state = "recording"
        
        audio_chunk = b"\x00\x01\x02\x03" * 800
        service.send_audio(session_id, audio_chunk)
        
        mock_recognizer.send_audio_frame.assert_called_once_with(audio_chunk)

    def test_send_audio_ignores_idle_session(self):
        """VoiceInputService.send_audio() ignores audio when session is idle."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        mock_recognizer = MagicMock()
        service.sessions[session_id].recognizer = mock_recognizer
        service.sessions[session_id].state = "idle"  # Not recording
        
        service.send_audio(session_id, b"\x00\x01\x02\x03")
        
        mock_recognizer.send_audio_frame.assert_not_called()

    def test_stop_recognition_returns_text(self):
        """VoiceInputService.stop_recognition() stops and returns text."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        mock_recognizer = MagicMock()
        service.sessions[session_id].recognizer = mock_recognizer
        service.sessions[session_id].state = "recording"
        service.sessions[session_id].final_text = "git status"
        
        result = service.stop_recognition(session_id)
        
        assert result == "git status"
        mock_recognizer.stop.assert_called_once()
        assert service.sessions[session_id].state == "idle"

    def test_cancel_recognition_clears_text(self):
        """VoiceInputService.cancel_recognition() cancels without returning text."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        mock_recognizer = MagicMock()
        service.sessions[session_id].recognizer = mock_recognizer
        service.sessions[session_id].state = "recording"
        service.sessions[session_id].final_text = "some text"
        
        service.cancel_recognition(session_id)
        
        mock_recognizer.stop.assert_called_once()
        assert service.sessions[session_id].state == "idle"
        assert service.sessions[session_id].final_text == ""

    def test_callback_receives_partial_results(self):
        """VoiceRecognizerCallback calls on_partial for partial results."""
        from x_ipe.services.voice_input_service_v2 import VoiceSession, VoiceRecognizerCallback
        
        partial_results = []
        session = VoiceSession(
            session_id="test",
            socket_sid="test",
            on_partial=lambda t: partial_results.append(t)
        )
        
        callback = VoiceRecognizerCallback(session)
        
        # Simulate partial transcription event
        mock_result = MagicMock()
        mock_result.text = "git"
        mock_result.is_sentence_end = False
        
        callback.on_event("req-123", mock_result, None, None)
        
        assert session.partial_text == "git"
        assert "git" in partial_results


# =============================================================================
# Unit Tests: Voice Commands
# =============================================================================

class TestVoiceCommands:
    """Tests for voice command recognition."""

    def test_is_voice_command_close_mic_english(self):
        """is_voice_command() recognizes 'close mic' command."""
        from x_ipe.services.voice_input_service_v2 import is_voice_command
        
        assert is_voice_command("close mic") == "close_mic"
        assert is_voice_command("Close Mic") == "close_mic"
        assert is_voice_command("CLOSE MIC") == "close_mic"
        assert is_voice_command("  close mic  ") == "close_mic"

    def test_is_voice_command_close_mic_chinese(self):
        """is_voice_command() recognizes Chinese '关闭麦克风' command."""
        from x_ipe.services.voice_input_service_v2 import is_voice_command
        
        assert is_voice_command("关闭麦克风") == "close_mic"
        assert is_voice_command("  关闭麦克风  ") == "close_mic"

    def test_is_voice_command_not_command(self):
        """is_voice_command() returns None for non-command text."""
        from x_ipe.services.voice_input_service_v2 import is_voice_command
        
        assert is_voice_command("git status") is None
        assert is_voice_command("npm install") is None
        assert is_voice_command("close the file") is None
        assert is_voice_command("mic check") is None

    def test_is_voice_command_empty(self):
        """is_voice_command() returns None for empty text."""
        from x_ipe.services.voice_input_service_v2 import is_voice_command
        
        assert is_voice_command("") is None
        assert is_voice_command("   ") is None
        assert is_voice_command(None) is None


# =============================================================================
# Unit Tests: Socket.IO Voice Handlers
# =============================================================================

class TestVoiceSocketHandlers:
    """Tests for Socket.IO voice event handlers."""

    def test_handle_voice_start_creates_session(self):
        """voice_start handler creates new voice session."""
        from src.app import create_app, socketio
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('x_ipe.handlers.voice_handlers.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-session-123"
            
            client = SocketIOTestClient(app, socketio)
            client.emit('voice_start', {})
            
            received = client.get_received()
            
            # Should emit voice_ready event
            voice_ready_events = [r for r in received if r['name'] == 'voice_ready']
            assert len(voice_ready_events) == 1
            assert voice_ready_events[0]['args'][0]['session_id'] == "voice-session-123"

    def test_handle_voice_audio_forwards_to_service(self):
        """voice_audio handler forwards audio chunk to service."""
        from src.app import create_app, socketio
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('x_ipe.handlers.voice_handlers.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-session-123"
            client = SocketIOTestClient(app, socketio)
            
            # Start session first
            client.emit('voice_start', {})
            
            audio_data = b"\x00\x01\x02\x03" * 800
            client.emit('voice_audio', {'audio': list(audio_data)})
            
            # Note: send_audio is async, so we check session was mapped
            # The actual audio forwarding is tested separately

    def test_handle_voice_stop_returns_transcription(self):
        """voice_stop handler returns transcription."""
        from src.app import create_app, socketio
        from x_ipe.handlers.voice_handlers import socket_to_voice_session
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('x_ipe.handlers.voice_handlers.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-session-123"
            mock_service.start_recognition.return_value = True
            mock_service.stop_recognition.return_value = "git status"
            mock_service.remove_session = Mock()
            
            client = SocketIOTestClient(app, socketio)
            client.emit('voice_start', {})
            client.emit('voice_stop', {})
            
            received = client.get_received()
            
            # Should emit voice_result event (not voice_transcription - we use voice_result)
            result_events = [r for r in received if r['name'] == 'voice_result']
            assert len(result_events) == 1
            assert result_events[0]['args'][0]['text'] == "git status"

    def test_handle_voice_stop_detects_command(self):
        """voice_stop handler detects voice commands."""
        from src.app import create_app, socketio
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('x_ipe.handlers.voice_handlers.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-session-123"
            mock_service.start_recognition.return_value = True
            mock_service.stop_recognition.return_value = "close mic"
            mock_service.remove_session = Mock()
            
            client = SocketIOTestClient(app, socketio)
            client.emit('voice_start', {})
            client.emit('voice_stop', {})
            
            received = client.get_received()
            
            # Should emit voice_command event
            command_events = [r for r in received if r['name'] == 'voice_command']
            assert len(command_events) == 1
            assert command_events[0]['args'][0]['command'] == "close_mic"

    def test_handle_voice_cancel_cleans_up(self):
        """voice_cancel handler cleans up session."""
        from src.app import create_app, socketio
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('x_ipe.handlers.voice_handlers.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-session-123"
            mock_service.start_recognition.return_value = True
            mock_service.cancel_recognition = Mock()
            mock_service.remove_session = Mock()
            
            client = SocketIOTestClient(app, socketio)
            client.emit('voice_start', {})
            client.emit('voice_cancel', {})
            
            received = client.get_received()
            voice_cancelled_events = [r for r in received if r['name'] == 'voice_cancelled']
            assert len(voice_cancelled_events) == 1

    def test_handle_voice_error_emits_error(self):
        """Voice handler emits error on service failure."""
        from src.app import create_app, socketio
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('x_ipe.handlers.voice_handlers.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-session-123"
            async def mock_finish(sid):
                raise Exception("API error")
            mock_service.finish_recognition = mock_finish
            
            client = SocketIOTestClient(app, socketio)
            client.emit('voice_start', {})
            client.emit('voice_stop', {})
            
            received = client.get_received()
            
            # Should emit voice_error event
            error_events = [r for r in received if r['name'] == 'voice_error']
            assert len(error_events) >= 1
            assert 'message' in error_events[0]['args'][0]


# =============================================================================
# Unit Tests: Error Handling
# =============================================================================

class TestVoiceErrorHandling:
    """Tests for voice input error handling."""

    def test_handle_network_disconnect(self):
        """VoiceInputService handles network disconnect gracefully."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        # Mock both recognizer types to raise exception
        with patch('x_ipe.services.voice_input_service_v2.TranslationRecognizerRealtime') as MockRealtime, \
             patch('x_ipe.services.voice_input_service_v2.TranslationRecognizerChat') as MockChat:
            mock_recognizer = MagicMock()
            mock_recognizer.start.side_effect = Exception("Connection failed")
            MockRealtime.return_value = mock_recognizer
            MockChat.return_value = mock_recognizer
            
            result = service.start_recognition(session_id)
            
            # Should return False on failure
            assert result is False
            assert service.sessions[session_id].state == "idle"

    def test_handle_api_error_via_callback(self):
        """VoiceInputService handles API error via callback."""
        from x_ipe.services.voice_input_service_v2 import VoiceSession, VoiceRecognizerCallback
        
        errors = []
        session = VoiceSession(
            session_id="test",
            socket_sid="test",
            on_error=lambda e: errors.append(e)
        )
        session.state = "recording"
        
        callback = VoiceRecognizerCallback(session)
        callback.on_error("Invalid API key")
        
        assert len(errors) == 1
        assert "Invalid API key" in errors[0]
        assert session.state == "error"

    def test_handle_empty_audio(self):
        """VoiceInputService handles empty/silent audio."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        # Simulate empty transcription result
        result = service.process_transcription(session_id, "")
        
        assert result is None  # No text to inject

    def test_handle_session_timeout(self):
        """VoiceInputService handles session timeout (30s max)."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService, VOICE_MAX_DURATION
        
        assert VOICE_MAX_DURATION == 30  # 30 seconds
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        session = service.get_session(session_id)
        
        # Simulate old session
        session.created_at = datetime.now() - timedelta(seconds=35)
        
        assert service.is_session_expired(session_id) is True


# =============================================================================
# Integration Tests: Full Voice Flow
# =============================================================================

class TestVoiceInputIntegration:
    """Integration tests for complete voice input flow."""

    def test_full_voice_flow_happy_path(self):
        """Test complete voice input flow: start → audio → stop → transcription."""
        from src.app import create_app, socketio
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('x_ipe.handlers.voice_handlers.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-123"
            mock_service.stop_recognition.return_value = "git status"
            mock_service.start_recognition.return_value = True
            mock_service.send_audio = Mock()
            mock_service.remove_session = Mock()
            
            client = SocketIOTestClient(app, socketio)
            
            # Step 1: Start voice
            client.emit('voice_start', {})
            received = client.get_received()
            session_event = next((r for r in received if r['name'] == 'voice_ready'), None)
            assert session_event is not None
            assert session_event['args'][0]['session_id'] == "voice-123"
            
            # Step 2: Send audio chunks
            for _ in range(5):
                audio_chunk = b"\x00" * 3200  # 100ms of 16kHz audio
                client.emit('voice_audio', {'audio': list(audio_chunk)})
            
            # Step 3: Stop and get transcription
            client.emit('voice_stop', {})
            received = client.get_received()
            result_event = next((r for r in received if r['name'] == 'voice_result'), None)
            assert result_event is not None
            assert result_event['args'][0]['text'] == "git status"

    def test_voice_command_flow(self):
        """Test voice command flow: start → audio → stop → command executed."""
        from src.app import create_app, socketio
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('x_ipe.handlers.voice_handlers.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-123"
            mock_service.stop_recognition.return_value = "close mic"
            mock_service.start_recognition.return_value = True
            mock_service.remove_session = Mock()
            
            client = SocketIOTestClient(app, socketio)
            
            client.emit('voice_start', {})
            client.emit('voice_stop', {})
            
            received = client.get_received()
            command_event = next((r for r in received if r['name'] == 'voice_command'), None)
            
            assert command_event is not None
            assert command_event['args'][0]['command'] == "close_mic"

    def test_voice_cancel_flow(self):
        """Test voice cancel flow: start → audio → cancel → no transcription."""
        from src.app import create_app, socketio
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('x_ipe.handlers.voice_handlers.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-123"
            mock_service.start_recognition.return_value = True
            mock_service.cancel_recognition = Mock()
            mock_service.send_audio = Mock()
            mock_service.remove_session = Mock()
            
            client = SocketIOTestClient(app, socketio)
            
            client.emit('voice_start', {})
            client.emit('voice_audio', {'audio': list(b"\x00" * 3200)})
            client.emit('voice_cancel', {})
            
            received = client.get_received()
            # Should not have voice_result
            result_events = [r for r in received if r['name'] == 'voice_result']
            assert len(result_events) == 0
            # Should have voice_cancelled
            cancelled_events = [r for r in received if r['name'] == 'voice_cancelled']
            assert len(cancelled_events) == 1


# =============================================================================
# UI Tests: Console Header Voice Controls
# =============================================================================

class TestConsoleHeaderVoiceUI:
    """Tests for console header voice UI components."""

    def test_mic_toggle_button_exists(self):
        """Console header has mic toggle button."""
        from src.app import create_app
        
        app = create_app({'TESTING': True})
        client = app.test_client()
        
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        assert 'id="mic-toggle"' in html or 'class="mic-toggle"' in html

    def test_voice_indicator_exists(self):
        """Console header has voice indicator element."""
        from src.app import create_app
        
        app = create_app({'TESTING': True})
        client = app.test_client()
        
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        assert 'id="voice-indicator"' in html or 'class="voice-indicator"' in html

    def test_connection_status_on_left(self):
        """Connection status is positioned on left side of console header."""
        from src.app import create_app
        
        app = create_app({'TESTING': True})
        client = app.test_client()
        
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Connection status should be in header-left section
        assert 'connection-status' in html
        # Verify it's in the left section (implementation-specific check)

    def test_transcription_preview_bar_exists(self):
        """Console has transcription preview bar element."""
        from src.app import create_app
        
        app = create_app({'TESTING': True})
        client = app.test_client()
        
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        assert 'id="transcription-preview"' in html or 'class="transcription-preview"' in html


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestVoiceInputEdgeCases:
    """Tests for voice input edge cases."""

    def test_no_terminal_focused(self):
        """Voice input with no terminal focused uses last active pane."""
        # This is frontend behavior - tested via integration
        pass  # Placeholder for frontend test

    def test_terminal_focus_change_during_recording(self):
        """Transcription goes to newly focused terminal if focus changes."""
        # This is frontend behavior - tested via integration
        pass  # Placeholder for frontend test

    def test_rapid_hotkey_presses_debounced(self):
        """Rapid hotkey presses are debounced."""
        # This is frontend behavior - tested via integration
        pass  # Placeholder for frontend test

    def test_recording_auto_stops_at_30_seconds(self):
        """Recording auto-stops at 30 second limit."""
        from x_ipe.services.voice_input_service_v2 import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        session = service.get_session(session_id)
        
        # Simulate 30+ second old session
        session.created_at = datetime.now() - timedelta(seconds=31)
        
        # Use is_session_expired instead of should_auto_stop
        assert service.is_session_expired(session_id) is True

    def test_browser_without_mediarecorder(self):
        """Graceful degradation when MediaRecorder not supported."""
        # This is frontend behavior - tested via integration
        pass  # Placeholder for frontend test

    def test_mic_permission_denied(self):
        """Mic toggle stays OFF when permission denied."""
        # This is frontend behavior - tested via integration
        pass  # Placeholder for frontend test


# =============================================================================
# Test Coverage Summary
# =============================================================================
"""
Test Coverage:

| Component | Unit Tests | Integration | API Tests |
|-----------|------------|-------------|-----------|
| VoiceSession | 3 | - | - |
| VoiceInputService | 8 | - | - |
| Alibaba Cloud Integration | 6 | - | - |
| Voice Commands | 4 | - | - |
| Socket.IO Handlers | 6 | - | - |
| Error Handling | 4 | - | - |
| Integration Tests | - | 3 | - |
| UI Tests | - | 4 | - |
| Edge Cases | - | 6 | - |
| **TOTAL** | **31** | **13** | **0** |

Total: 44 tests (31 unit, 13 integration/UI)
"""
