"""
Voice Input WebSocket Handlers

FEATURE-021: Console Voice Input

Provides WebSocket handlers for:
- Voice recording start/stop
- Audio streaming
- Transcription results
- Voice commands
"""
import os
from flask import request
from flask_socketio import emit

from x_ipe.services.voice_input_service_v2 import VoiceInputService, is_voice_command

# Global voice service instance
voice_service = None

# Mapping: socket_sid -> voice_session_id
socket_to_voice_session = {}


def register_voice_handlers(socketio):
    """Register WebSocket event handlers for voice input."""
    global voice_service
    
    # Initialize voice service with API key from environment
    api_key = os.environ.get('ALIBABA_SPEECH_API_KEY', '')
    if api_key:
        voice_service = VoiceInputService(api_key=api_key)
        print("[Voice] Voice service initialized with API key")
    else:
        print("[Voice] No ALIBABA_SPEECH_API_KEY found, voice input disabled")
    
    @socketio.on('voice_start')
    def handle_voice_start(data=None):
        """Handle voice recording start request."""
        global voice_service
        sid = request.sid
        
        print(f"[Voice] 🎬 voice_start received from {sid}")
        print(f"[Voice]    data: {data}")
        
        if not voice_service:
            print(f"[Voice] ❌ Voice service not configured!")
            emit('voice_error', {'message': 'Voice service not configured. Set ALIBABA_SPEECH_API_KEY in x-ipe-docs/config/.env'})
            return
        
        try:
            # Create voice session with callbacks for partial results
            def on_partial(text):
                print(f"[Voice] 📤 Emitting voice_partial: '{text}'")
                socketio.emit('voice_partial', {'text': text}, room=sid)
            
            session_id = voice_service.create_session(
                socket_sid=sid,
                on_partial=on_partial,
            )
            socket_to_voice_session[sid] = session_id
            
            # Start recognition
            print(f"[Voice]    Starting recognition...")
            if voice_service.start_recognition(session_id):
                print(f"[Voice] ✅ Emitting voice_ready for session {session_id}")
                emit('voice_ready', {'session_id': session_id})
            else:
                print(f"[Voice] ❌ Failed to start recognition")
                emit('voice_error', {'message': 'Failed to start recognition'})
                voice_service.remove_session(session_id)
                del socket_to_voice_session[sid]
        except Exception as e:
            print(f"[Voice] ❌ Exception in voice_start: {e}")
            import traceback
            traceback.print_exc()
            emit('voice_error', {'message': str(e)})
    
    @socketio.on('voice_audio')
    def handle_voice_audio(data):
        """Handle incoming audio chunk from client."""
        global voice_service
        sid = request.sid
        
        if not voice_service:
            return
        
        session_id = socket_to_voice_session.get(sid)
        if not session_id:
            print(f"[Voice] ⚠️ voice_audio received but no session for {sid}")
            return
        
        try:
            # Get audio data from message
            audio_chunk = data.get('audio', b'') if isinstance(data, dict) else data
            if isinstance(audio_chunk, list):
                audio_chunk = bytes(audio_chunk)
            
            # Forward to voice service (sync now with dashscope SDK)
            voice_service.send_audio(session_id, audio_chunk)
        except Exception as e:
            print(f"[Voice] ❌ Exception in voice_audio: {e}")
            emit('voice_error', {'message': f'Audio error: {e}'})
    
    @socketio.on('voice_stop')
    def handle_voice_stop(data=None):
        """Handle voice recording stop request - finalize and get transcription."""
        global voice_service
        sid = request.sid
        
        print(f"[Voice] 🛑 voice_stop received from {sid}")
        
        if not voice_service:
            print(f"[Voice] ❌ Voice service not available")
            emit('voice_error', {'message': 'Voice service not available'})
            return
        
        session_id = socket_to_voice_session.get(sid)
        if not session_id:
            print(f"[Voice] ❌ No active voice session for {sid}")
            emit('voice_error', {'message': 'No active voice session'})
            return
        
        try:
            print(f"[Voice]    Stopping recognition for session {session_id}...")
            # Stop recognition and get result (sync with dashscope SDK)
            result = voice_service.stop_recognition(session_id)
            
            print(f"[Voice]    Result: '{result}'")
            
            # Check if result is a voice command
            command = is_voice_command(result)
            
            if command:
                print(f"[Voice] 📤 Emitting voice_command: {command}")
                emit('voice_command', {'command': command, 'text': result})
            else:
                print(f"[Voice] 📤 Emitting voice_result: '{result}'")
                emit('voice_result', {'text': result})
            
            # Cleanup session
            voice_service.remove_session(session_id)
            if sid in socket_to_voice_session:
                del socket_to_voice_session[sid]
            
            print(f"[Voice] ✅ Session completed: {session_id}")
        except Exception as e:
            print(f"[Voice] ❌ Exception in voice_stop: {e}")
            import traceback
            traceback.print_exc()
            emit('voice_error', {'message': str(e)})
    
    @socketio.on('voice_cancel')
    def handle_voice_cancel(data=None):
        """Handle voice recording cancel request - abort without transcription."""
        global voice_service
        sid = request.sid
        
        print(f"[Voice] ⚠️ voice_cancel received from {sid}")
        
        session_id = socket_to_voice_session.get(sid)
        if not session_id:
            print(f"[Voice]    No session to cancel")
            return
        
        try:
            # Cancel recognition (sync with dashscope SDK)
            if voice_service:
                voice_service.cancel_recognition(session_id)
                voice_service.remove_session(session_id)
            
            if sid in socket_to_voice_session:
                del socket_to_voice_session[sid]
            
            emit('voice_cancelled', {})
            print(f"[Voice] ✅ Session cancelled: {session_id}")
        except Exception as e:
            print(f"[Voice] ❌ Exception in voice_cancel: {e}")
            emit('voice_error', {'message': f'Cancel error: {e}'})
