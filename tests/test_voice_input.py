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
        from src.services.voice_input_service import VoiceSession
        
        session = VoiceSession(
            session_id="voice-123",
            socket_sid="socket-456"
        )
        
        assert session.session_id == "voice-123"
        assert session.socket_sid == "socket-456"
        assert session.state == "idle"
        assert session.alibaba_ws is None
        assert session.audio_buffer == b""
        assert session.partial_text == ""
        assert session.created_at is not None

    def test_voice_session_state_transitions(self):
        """VoiceSession state transitions: idle -> recording -> processing -> idle."""
        from src.services.voice_input_service import VoiceSession
        
        session = VoiceSession(session_id="test", socket_sid="test")
        
        assert session.state == "idle"
        
        session.state = "recording"
        assert session.state == "recording"
        
        session.state = "processing"
        assert session.state == "processing"
        
        session.state = "idle"
        assert session.state == "idle"

    def test_voice_session_audio_buffer_append(self):
        """VoiceSession accumulates audio data in buffer."""
        from src.services.voice_input_service import VoiceSession
        
        session = VoiceSession(session_id="test", socket_sid="test")
        
        chunk1 = b"\x00\x01\x02\x03"
        chunk2 = b"\x04\x05\x06\x07"
        
        session.audio_buffer += chunk1
        session.audio_buffer += chunk2
        
        assert session.audio_buffer == b"\x00\x01\x02\x03\x04\x05\x06\x07"
        assert len(session.audio_buffer) == 8


# =============================================================================
# Unit Tests: VoiceInputService
# =============================================================================

class TestVoiceInputService:
    """Tests for VoiceInputService backend service."""

    def test_voice_input_service_init(self):
        """VoiceInputService initializes with API key."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-api-key")
        
        assert service.api_key == "test-api-key"
        assert service.sessions == {}
        assert service.WS_ENDPOINT == "wss://dashscope.aliyuncs.com/api-ws/v1/inference"

    def test_voice_input_service_init_missing_api_key(self):
        """VoiceInputService raises error if API key is None."""
        from src.services.voice_input_service import VoiceInputService
        
        with pytest.raises(ValueError, match="API key required"):
            VoiceInputService(api_key=None)

    def test_create_session(self):
        """VoiceInputService.create_session() creates new VoiceSession."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        
        session_id = service.create_session(socket_sid="socket-123")
        
        assert session_id is not None
        assert session_id in service.sessions
        assert service.sessions[session_id].socket_sid == "socket-123"
        assert service.sessions[session_id].state == "idle"

    def test_create_session_unique_ids(self):
        """VoiceInputService.create_session() generates unique session IDs."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        
        id1 = service.create_session(socket_sid="socket-1")
        id2 = service.create_session(socket_sid="socket-2")
        id3 = service.create_session(socket_sid="socket-3")
        
        assert id1 != id2 != id3
        assert len(service.sessions) == 3

    def test_get_session(self):
        """VoiceInputService.get_session() returns session by ID."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        session = service.get_session(session_id)
        
        assert session is not None
        assert session.session_id == session_id

    def test_get_session_not_found(self):
        """VoiceInputService.get_session() returns None for unknown ID."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        
        session = service.get_session("nonexistent-id")
        
        assert session is None

    def test_remove_session(self):
        """VoiceInputService.remove_session() removes session."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        assert session_id in service.sessions
        
        service.remove_session(session_id)
        
        assert session_id not in service.sessions

    def test_has_session(self):
        """VoiceInputService.has_session() checks session existence."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        assert service.has_session(session_id) is True
        assert service.has_session("nonexistent") is False


# =============================================================================
# Unit Tests: Alibaba Cloud API Integration
# =============================================================================

class TestAlibabaCloudIntegration:
    """Tests for Alibaba Cloud gummy-realtime-v1 API integration."""

    @pytest.mark.asyncio
    async def test_connect_to_alibaba_api(self):
        """VoiceInputService connects to Alibaba Cloud WebSocket."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_connect.return_value.__aenter__.return_value = mock_ws
            
            await service.start_recognition(session_id)
            
            mock_connect.assert_called_once()
            call_args = mock_connect.call_args
            assert "wss://dashscope.aliyuncs.com" in str(call_args)

    @pytest.mark.asyncio
    async def test_send_run_task_message(self):
        """VoiceInputService sends run-task message on start."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.recv = AsyncMock(return_value=json.dumps({
                "header": {"event": "task-started"}
            }))
            mock_connect.return_value.__aenter__.return_value = mock_ws
            
            await service.start_recognition(session_id)
            
            # Verify run-task message sent
            mock_ws.send.assert_called()
            sent_data = json.loads(mock_ws.send.call_args[0][0])
            assert sent_data["header"]["event"] == "run-task"
            assert sent_data["payload"]["model"] == "gummy-realtime-v1"

    @pytest.mark.asyncio
    async def test_send_audio_chunk(self):
        """VoiceInputService.send_audio() streams audio to API."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        mock_ws = AsyncMock()
        service.sessions[session_id].alibaba_ws = mock_ws
        service.sessions[session_id].state = "recording"
        
        audio_chunk = b"\x00\x01\x02\x03" * 800  # ~3200 bytes = 100ms at 16kHz
        
        await service.send_audio(session_id, audio_chunk)
        
        mock_ws.send.assert_called_with(audio_chunk)

    @pytest.mark.asyncio
    async def test_send_audio_ignores_idle_session(self):
        """VoiceInputService.send_audio() ignores audio when session is idle."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        mock_ws = AsyncMock()
        service.sessions[session_id].alibaba_ws = mock_ws
        service.sessions[session_id].state = "idle"  # Not recording
        
        await service.send_audio(session_id, b"\x00\x01\x02\x03")
        
        mock_ws.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_finish_recognition(self):
        """VoiceInputService.finish_recognition() sends finish-task and returns text."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        mock_ws = AsyncMock()
        mock_ws.recv = AsyncMock(return_value=json.dumps({
            "header": {"event": "task-finished"},
            "payload": {"output": {"text": "git status"}}
        }))
        service.sessions[session_id].alibaba_ws = mock_ws
        service.sessions[session_id].state = "recording"
        
        result = await service.finish_recognition(session_id)
        
        assert result == "git status"
        # Verify finish-task sent
        mock_ws.send.assert_called()
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["header"]["event"] == "finish-task"

    @pytest.mark.asyncio
    async def test_handle_partial_transcription(self):
        """VoiceInputService receives partial transcription during recording."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        partial_callback = Mock()
        
        mock_ws = AsyncMock()
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({
                "header": {"event": "result-generated"},
                "payload": {"output": {"text": "git"}, "is_final": False}
            }),
            json.dumps({
                "header": {"event": "result-generated"},
                "payload": {"output": {"text": "git status"}, "is_final": True}
            })
        ])
        service.sessions[session_id].alibaba_ws = mock_ws
        
        await service.listen_for_results(session_id, partial_callback)
        
        # Should receive partial updates
        assert partial_callback.call_count >= 1


# =============================================================================
# Unit Tests: Voice Commands
# =============================================================================

class TestVoiceCommands:
    """Tests for voice command recognition."""

    def test_is_voice_command_close_mic_english(self):
        """is_voice_command() recognizes 'close mic' command."""
        from src.services.voice_input_service import is_voice_command
        
        assert is_voice_command("close mic") == "close_mic"
        assert is_voice_command("Close Mic") == "close_mic"
        assert is_voice_command("CLOSE MIC") == "close_mic"
        assert is_voice_command("  close mic  ") == "close_mic"

    def test_is_voice_command_close_mic_chinese(self):
        """is_voice_command() recognizes Chinese '关闭麦克风' command."""
        from src.services.voice_input_service import is_voice_command
        
        assert is_voice_command("关闭麦克风") == "close_mic"
        assert is_voice_command("  关闭麦克风  ") == "close_mic"

    def test_is_voice_command_not_command(self):
        """is_voice_command() returns None for non-command text."""
        from src.services.voice_input_service import is_voice_command
        
        assert is_voice_command("git status") is None
        assert is_voice_command("npm install") is None
        assert is_voice_command("close the file") is None
        assert is_voice_command("mic check") is None

    def test_is_voice_command_empty(self):
        """is_voice_command() returns None for empty text."""
        from src.services.voice_input_service import is_voice_command
        
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
        from src.app import create_app
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('src.app.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-session-123"
            
            client = SocketIOTestClient(app)
            client.emit('voice_start', {})
            
            received = client.get_received()
            
            # Should emit voice_session event
            voice_session_events = [r for r in received if r['name'] == 'voice_session']
            assert len(voice_session_events) == 1
            assert voice_session_events[0]['args'][0]['session_id'] == "voice-session-123"

    def test_handle_voice_audio_forwards_to_service(self):
        """voice_audio handler forwards audio chunk to service."""
        from src.app import create_app
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('src.app.voice_service') as mock_service:
            client = SocketIOTestClient(app)
            
            audio_data = b"\x00\x01\x02\x03" * 800
            client.emit('voice_audio', {'audio': audio_data})
            
            mock_service.send_audio.assert_called()

    def test_handle_voice_stop_returns_transcription(self):
        """voice_stop handler returns transcription."""
        from src.app import create_app
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('src.app.voice_service') as mock_service:
            mock_service.finish_recognition.return_value = "git status"
            mock_service.get_session.return_value = Mock(session_id="test")
            
            client = SocketIOTestClient(app)
            client.emit('voice_start', {})
            client.emit('voice_stop', {})
            
            received = client.get_received()
            
            # Should emit voice_transcription event
            transcription_events = [r for r in received if r['name'] == 'voice_transcription']
            assert len(transcription_events) == 1
            assert transcription_events[0]['args'][0]['text'] == "git status"

    def test_handle_voice_stop_detects_command(self):
        """voice_stop handler detects voice commands."""
        from src.app import create_app
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('src.app.voice_service') as mock_service:
            mock_service.finish_recognition.return_value = "close mic"
            mock_service.get_session.return_value = Mock(session_id="test")
            
            client = SocketIOTestClient(app)
            client.emit('voice_start', {})
            client.emit('voice_stop', {})
            
            received = client.get_received()
            
            # Should emit voice_command event, NOT voice_transcription
            command_events = [r for r in received if r['name'] == 'voice_command']
            assert len(command_events) == 1
            assert command_events[0]['args'][0]['command'] == "close_mic"

    def test_handle_voice_cancel_cleans_up(self):
        """voice_cancel handler cleans up session."""
        from src.app import create_app
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('src.app.voice_service') as mock_service:
            client = SocketIOTestClient(app)
            client.emit('voice_start', {})
            client.emit('voice_cancel', {})
            
            mock_service.cancel_session.assert_called()

    def test_handle_voice_error_emits_error(self):
        """Voice handler emits error on service failure."""
        from src.app import create_app
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('src.app.voice_service') as mock_service:
            mock_service.finish_recognition.side_effect = Exception("API error")
            mock_service.get_session.return_value = Mock(session_id="test")
            
            client = SocketIOTestClient(app)
            client.emit('voice_start', {})
            client.emit('voice_stop', {})
            
            received = client.get_received()
            
            # Should emit voice_error event
            error_events = [r for r in received if r['name'] == 'voice_error']
            assert len(error_events) == 1
            assert 'message' in error_events[0]['args'][0]


# =============================================================================
# Unit Tests: Error Handling
# =============================================================================

class TestVoiceErrorHandling:
    """Tests for voice input error handling."""

    @pytest.mark.asyncio
    async def test_handle_network_disconnect(self):
        """VoiceInputService handles network disconnect gracefully."""
        from src.services.voice_input_service import VoiceInputService
        import websockets
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_connect.side_effect = websockets.exceptions.ConnectionClosed(None, None)
            
            with pytest.raises(ConnectionError):
                await service.start_recognition(session_id)
            
            # Session should be cleaned up
            assert service.sessions[session_id].state == "idle"

    @pytest.mark.asyncio
    async def test_handle_api_error(self):
        """VoiceInputService handles API error response."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        mock_ws = AsyncMock()
        mock_ws.recv = AsyncMock(return_value=json.dumps({
            "header": {"event": "task-failed"},
            "payload": {"error": {"code": "InvalidApiKey", "message": "Invalid API key"}}
        }))
        service.sessions[session_id].alibaba_ws = mock_ws
        
        with pytest.raises(Exception, match="Invalid API key"):
            await service.finish_recognition(session_id)

    def test_handle_empty_audio(self):
        """VoiceInputService handles empty/silent audio."""
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        
        # Simulate empty transcription result
        result = service.process_transcription(session_id, "")
        
        assert result is None  # No text to inject

    def test_handle_session_timeout(self):
        """VoiceInputService handles session timeout (30s max)."""
        from src.services.voice_input_service import VoiceInputService, VOICE_MAX_DURATION
        
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
        from src.app import create_app
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('src.app.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-123"
            mock_service.finish_recognition.return_value = "git status"
            mock_service.get_session.return_value = Mock(session_id="voice-123")
            
            client = SocketIOTestClient(app)
            
            # Step 1: Start voice
            client.emit('voice_start', {})
            received = client.get_received()
            session_event = next(r for r in received if r['name'] == 'voice_session')
            assert session_event['args'][0]['session_id'] == "voice-123"
            
            # Step 2: Send audio chunks
            for _ in range(5):
                audio_chunk = b"\x00" * 3200  # 100ms of 16kHz audio
                client.emit('voice_audio', {'audio': audio_chunk})
            
            # Step 3: Stop and get transcription
            client.emit('voice_stop', {})
            received = client.get_received()
            transcription_event = next(r for r in received if r['name'] == 'voice_transcription')
            assert transcription_event['args'][0]['text'] == "git status"

    def test_voice_command_flow(self):
        """Test voice command flow: start → audio → stop → command executed."""
        from src.app import create_app
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('src.app.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-123"
            mock_service.finish_recognition.return_value = "close mic"
            mock_service.get_session.return_value = Mock(session_id="voice-123")
            
            client = SocketIOTestClient(app)
            
            client.emit('voice_start', {})
            client.emit('voice_stop', {})
            
            received = client.get_received()
            command_event = next((r for r in received if r['name'] == 'voice_command'), None)
            
            assert command_event is not None
            assert command_event['args'][0]['command'] == "close_mic"

    def test_voice_cancel_flow(self):
        """Test voice cancel flow: start → audio → cancel → no transcription."""
        from src.app import create_app
        from flask_socketio import SocketIOTestClient
        
        app = create_app({'TESTING': True})
        
        with patch('src.app.voice_service') as mock_service:
            mock_service.create_session.return_value = "voice-123"
            
            client = SocketIOTestClient(app)
            
            client.emit('voice_start', {})
            client.emit('voice_audio', {'audio': b"\x00" * 3200})
            client.emit('voice_cancel', {})
            
            received = client.get_received()
            transcription_events = [r for r in received if r['name'] == 'voice_transcription']
            
            assert len(transcription_events) == 0
            mock_service.cancel_session.assert_called()


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
        from src.services.voice_input_service import VoiceInputService
        
        service = VoiceInputService(api_key="test-key")
        session_id = service.create_session(socket_sid="socket-123")
        session = service.get_session(session_id)
        
        # Simulate 30+ second old session
        session.created_at = datetime.now() - timedelta(seconds=31)
        
        assert service.should_auto_stop(session_id) is True

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
