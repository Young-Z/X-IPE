"""
FEATURE-021: Console Voice Input (v2 - dashscope SDK)

VoiceSession: Individual voice recording session data
VoiceInputService: Backend service for Alibaba Cloud speech recognition
is_voice_command: Voice command pattern matching

Uses dashscope SDK for simpler API integration.
Supports both transcription-only and translation modes.
"""
import os
import uuid
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, Callable, Literal, Any

import dashscope
from dashscope.audio.asr import (
    TranslationRecognizerRealtime,
    TranslationRecognizerChat,
    TranslationRecognizerCallback,
    TranscriptionResult,
    TranslationResult,
)


# Constants
VOICE_MAX_DURATION = 30  # Maximum recording duration in seconds
VOICE_DEFAULT_MODEL = "gummy-realtime-v1"
VOICE_TRANSLATION_MODEL = "gummy-chat-v1"
VOICE_DEFAULT_TRANSLATION_TARGET = "en"

# Voice command patterns (case-insensitive)
VOICE_COMMANDS = {
    "close mic": "close_mic",
    "关闭麦克风": "close_mic",
}


def is_voice_command(text: Optional[str]) -> Optional[str]:
    """
    Check if transcribed text is a voice command.
    
    Args:
        text: Transcribed text to check
        
    Returns:
        Command name if matched, None otherwise
    """
    if not text:
        return None
    
    normalized = text.strip().lower()
    
    for pattern, command in VOICE_COMMANDS.items():
        if normalized == pattern.lower():
            return command
    
    return None


@dataclass
class VoiceSession:
    """
    Individual voice recording session.
    
    Tracks state and recognizer instance.
    """
    session_id: str
    socket_sid: str
    state: Literal["idle", "recording", "processing", "error"] = "idle"
    recognizer: Optional[Any] = None  # Can be TranslationRecognizerRealtime or TranslationRecognizerChat
    final_text: str = ""
    partial_text: str = ""
    translation_text: str = ""  # Translated text (when translation enabled)
    translation_enabled: bool = False
    translation_target: str = "en"
    created_at: datetime = field(default_factory=datetime.now)
    # Callback for sending events back to client
    on_partial: Optional[Callable[[str], None]] = None
    on_complete: Optional[Callable[[str], None]] = None
    on_error: Optional[Callable[[str], None]] = None


class VoiceRecognizerCallback(TranslationRecognizerCallback):
    """Callback handler for dashscope recognizer events."""
    
    def __init__(self, session: VoiceSession):
        self.session = session
        self.audio_chunks_received = 0
        self.events_received = 0
    
    def on_open(self) -> None:
        """Called when connection is established."""
        print(f"[Voice] ✅ Recognizer OPENED for session {self.session.session_id}")
        print(f"[Voice]    Socket SID: {self.session.socket_sid}")
        print(f"[Voice]    Translation enabled: {self.session.translation_enabled}")
        if self.session.translation_enabled:
            print(f"[Voice]    Translation target: {self.session.translation_target}")
        self.session.state = "recording"
    
    def on_close(self) -> None:
        """Called when connection is closed."""
        print(f"[Voice] 🔴 Recognizer CLOSED for session {self.session.session_id}")
        print(f"[Voice]    Audio chunks received: {self.audio_chunks_received}")
        print(f"[Voice]    Events received: {self.events_received}")
        print(f"[Voice]    Final text: '{self.session.final_text}'")
        print(f"[Voice]    Partial text: '{self.session.partial_text}'")
        if self.session.translation_enabled:
            print(f"[Voice]    Translation text: '{self.session.translation_text}'")
        if self.session.state == "recording":
            self.session.state = "idle"
    
    def on_event(
        self,
        request_id,
        transcription_result: TranscriptionResult,
        translation_result: TranslationResult,
        usage,
    ) -> None:
        """Called when transcription/translation result is received."""
        self.events_received += 1
        print(f"[Voice] 📝 EVENT #{self.events_received} received (request_id: {request_id})")
        print(f"[Voice]    transcription_result: {transcription_result}")
        print(f"[Voice]    translation_result: {translation_result}")
        print(f"[Voice]    usage: {usage}")
        
        # Handle translation result (when translation is enabled)
        if translation_result is not None and self.session.translation_enabled:
            try:
                languages = translation_result.get_language_list()
                print(f"[Voice]    translation_languages: {languages}")
                
                target_lang = self.session.translation_target
                translation = translation_result.get_translation(target_lang)
                if translation:
                    translated_text = translation.text
                    print(f"[Voice]    translated to {target_lang}: '{translated_text}'")
                    self.session.translation_text = translated_text
            except Exception as e:
                print(f"[Voice]    ⚠️ Error getting translation: {e}")
        
        # Handle transcription result
        if transcription_result is not None:
            text = transcription_result.text
            sentence_id = getattr(transcription_result, 'sentence_id', None)
            is_final = getattr(transcription_result, 'is_sentence_end', False)
            
            print(f"[Voice]    text: '{text}'")
            print(f"[Voice]    sentence_id: {sentence_id}")
            print(f"[Voice]    is_sentence_end: {is_final}")
            
            if is_final:
                self.session.final_text = text
                print(f"[Voice] ✅ FINAL transcription: '{text}'")
                
                # Use translation if enabled, otherwise use transcription
                result_text = self.session.translation_text if self.session.translation_enabled and self.session.translation_text else text
                if self.session.on_complete:
                    self.session.on_complete(result_text)
            else:
                self.session.partial_text = text
                print(f"[Voice] 🔄 PARTIAL transcription: '{text}'")
                
                # For partial results, prefer translation if available
                result_text = self.session.translation_text if self.session.translation_enabled and self.session.translation_text else text
                if self.session.on_partial:
                    self.session.on_partial(result_text)
        else:
            print(f"[Voice]    ⚠️ transcription_result is None")
    
    def on_error(self, message: str) -> None:
        """Called when an error occurs."""
        print(f"[Voice] ❌ ERROR: {message}")
        print(f"[Voice]    Session: {self.session.session_id}")
        print(f"[Voice]    State before error: {self.session.state}")
        self.session.state = "error"
        if self.session.on_error:
            self.session.on_error(message)


class VoiceInputService:
    """
    Backend service for Alibaba Cloud speech recognition.
    
    Uses dashscope SDK for real-time transcription.
    Supports optional translation mode.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize VoiceInputService.
        
        Args:
            api_key: Alibaba Cloud API key (uses env var if not provided)
            model: Speech recognition model (uses env var or default if not provided)
        """
        # Set API key - SDK will use DASHSCOPE_API_KEY env var if not set
        if api_key:
            dashscope.api_key = api_key
            print(f"[Voice] API key set from parameter (length: {len(api_key)})")
        elif os.environ.get('ALIBABA_SPEECH_API_KEY'):
            dashscope.api_key = os.environ.get('ALIBABA_SPEECH_API_KEY')
            print(f"[Voice] API key set from ALIBABA_SPEECH_API_KEY env var")
        else:
            print(f"[Voice] ⚠️ No API key provided!")
        
        # Check translation settings from environment
        translation_env = os.environ.get('VOICE_TRANSLATION', 'false').lower()
        self.translation_enabled = translation_env in ('true', '1', 'yes')
        self.translation_target = os.environ.get('VOICE_TRANSLATION_TARGET', VOICE_DEFAULT_TRANSLATION_TARGET)
        
        # Set model - use translation model if translation is enabled
        if self.translation_enabled:
            self.model = model or os.environ.get('ALIBABA_SPEECH_MODEL') or VOICE_TRANSLATION_MODEL
        else:
            self.model = model or os.environ.get('ALIBABA_SPEECH_MODEL') or VOICE_DEFAULT_MODEL
        
        print(f"[Voice] Using model: {self.model}")
        print(f"[Voice] Translation enabled: {self.translation_enabled}")
        if self.translation_enabled:
            print(f"[Voice] Translation target: {self.translation_target}")
        
        self.sessions: Dict[str, VoiceSession] = {}
        print(f"[Voice] VoiceInputService initialized")
    
    def create_session(
        self, 
        socket_sid: str,
        on_partial: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> str:
        """
        Create a new voice session.
        
        Args:
            socket_sid: Socket.IO session ID
            on_partial: Callback for partial transcription
            on_complete: Callback for final transcription
            on_error: Callback for errors
            
        Returns:
            New session ID
        """
        session_id = f"voice-{uuid.uuid4().hex[:8]}"
        
        session = VoiceSession(
            session_id=session_id,
            socket_sid=socket_sid,
            translation_enabled=self.translation_enabled,
            translation_target=self.translation_target,
            on_partial=on_partial,
            on_complete=on_complete,
            on_error=on_error,
        )
        
        self.sessions[session_id] = session
        print(f"[Voice] 📦 Session created: {session_id} for socket {socket_sid}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[VoiceSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def start_recognition(self, session_id: str) -> bool:
        """
        Start speech recognition for a session.
        
        Args:
            session_id: Voice session ID
            
        Returns:
            True if started successfully
        """
        session = self.get_session(session_id)
        if not session:
            print(f"[Voice] ❌ start_recognition: session {session_id} not found")
            return False
        
        print(f"[Voice] 🎤 Starting recognition for {session_id}...")
        print(f"[Voice]    Model: {self.model}")
        print(f"[Voice]    Format: pcm, Sample rate: 16000")
        print(f"[Voice]    Translation: {session.translation_enabled}")
        if session.translation_enabled:
            print(f"[Voice]    Translation target: {session.translation_target}")
        
        try:
            callback = VoiceRecognizerCallback(session)
            
            if session.translation_enabled:
                # Use TranslationRecognizerChat for translation mode
                recognizer = TranslationRecognizerChat(
                    model=self.model,
                    format="pcm",
                    sample_rate=16000,
                    transcription_enabled=True,
                    translation_enabled=True,
                    translation_target_languages=[session.translation_target],
                    callback=callback,
                )
                print(f"[Voice]    Using TranslationRecognizerChat")
            else:
                # Use TranslationRecognizerRealtime for transcription-only mode
                recognizer = TranslationRecognizerRealtime(
                    model=self.model,
                    format="pcm",
                    sample_rate=16000,
                    transcription_enabled=True,
                    translation_enabled=False,
                    callback=callback,
                )
                print(f"[Voice]    Using TranslationRecognizerRealtime")
            
            session.recognizer = recognizer
            session._callback = callback  # Keep reference for logging
            session.state = "recording"
            
            # Start in background thread
            print(f"[Voice]    Calling recognizer.start()...")
            recognizer.start()
            
            print(f"[Voice] ✅ Recognition started for {session_id}")
            return True
            
        except Exception as e:
            print(f"[Voice] ❌ Failed to start recognition: {e}")
            import traceback
            traceback.print_exc()
            session.state = "idle"
            if session.on_error:
                session.on_error(str(e))
            return False
    
    def send_audio(self, session_id: str, audio_data: bytes) -> None:
        """
        Send audio data to recognizer.
        
        Args:
            session_id: Voice session ID
            audio_data: PCM audio bytes (16kHz, mono)
        """
        session = self.get_session(session_id)
        if not session:
            print(f"[Voice] ⚠️ send_audio: session {session_id} not found")
            return
        
        if session.state != "recording":
            print(f"[Voice] ⚠️ send_audio: session state is {session.state}, not recording")
            return
        
        if session.recognizer:
            try:
                # Track audio chunks in callback
                if hasattr(session, '_callback'):
                    session._callback.audio_chunks_received += 1
                    if session._callback.audio_chunks_received % 10 == 1:  # Log every 10th chunk
                        print(f"[Voice] 🔊 Audio chunk #{session._callback.audio_chunks_received}, size: {len(audio_data)} bytes")
                
                session.recognizer.send_audio_frame(audio_data)
            except Exception as e:
                print(f"[Voice] ❌ Error sending audio: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[Voice] ⚠️ send_audio: no recognizer for session {session_id}")
    
    def stop_recognition(self, session_id: str) -> str:
        """
        Stop recognition and get final result.
        
        Args:
            session_id: Voice session ID
            
        Returns:
            Final transcription text
        """
        session = self.get_session(session_id)
        if not session:
            print(f"[Voice] ❌ stop_recognition: session {session_id} not found")
            return ""
        
        print(f"[Voice] 🛑 Stopping recognition for {session_id}...")
        print(f"[Voice]    Current state: {session.state}")
        print(f"[Voice]    Final text so far: '{session.final_text}'")
        print(f"[Voice]    Partial text so far: '{session.partial_text}'")
        
        session.state = "processing"
        
        if session.recognizer:
            try:
                print(f"[Voice]    Calling recognizer.stop()...")
                session.recognizer.stop()
                print(f"[Voice]    Recognizer stopped")
            except Exception as e:
                print(f"[Voice] ❌ Error stopping recognition: {e}")
                import traceback
                traceback.print_exc()
        
        session.state = "idle"
        
        # Return the accumulated text (prefer translation if enabled)
        if session.translation_enabled and session.translation_text:
            result = session.translation_text
            print(f"[Voice] ✅ Recognition stopped, translation result: '{result}'")
        else:
            result = session.final_text or session.partial_text
            print(f"[Voice] ✅ Recognition stopped, transcription result: '{result}'")
        return result
    
    def cancel_recognition(self, session_id: str) -> None:
        """
        Cancel recognition without getting result.
        
        Args:
            session_id: Voice session ID
        """
        session = self.get_session(session_id)
        if not session:
            print(f"[Voice] ❌ cancel_recognition: session {session_id} not found")
            return
        
        print(f"[Voice] ⚠️ Cancelling recognition for {session_id}...")
        
        if session.recognizer:
            try:
                session.recognizer.stop()
            except Exception:
                pass
        
        session.state = "idle"
        session.final_text = ""
        session.partial_text = ""
        session.translation_text = ""
    
    def remove_session(self, session_id: str) -> None:
        """
        Remove a session.
        
        Args:
            session_id: Voice session ID
        """
        session = self.sessions.pop(session_id, None)
        if session and session.recognizer:
            try:
                session.recognizer.stop()
            except Exception:
                pass
    
    def is_session_expired(self, session_id: str) -> bool:
        """
        Check if session has exceeded max duration.
        
        Args:
            session_id: Voice session ID
            
        Returns:
            True if expired
        """
        session = self.get_session(session_id)
        if not session:
            return True
        
        elapsed = (datetime.now() - session.created_at).total_seconds()
        return elapsed > VOICE_MAX_DURATION
    
    def process_transcription(self, session_id: str, text: str) -> Optional[str]:
        """
        Process transcription result.
        
        Args:
            session_id: Voice session ID
            text: Transcription text
            
        Returns:
            Text if valid, None if empty
        """
        if not text or not text.strip():
            return None
        return text.strip()


# For backward compatibility - async wrappers
async def async_start_recognition(service: VoiceInputService, session_id: str) -> bool:
    """Async wrapper for start_recognition."""
    return service.start_recognition(session_id)


async def async_send_audio(service: VoiceInputService, session_id: str, audio_data: bytes) -> None:
    """Async wrapper for send_audio."""
    service.send_audio(session_id, audio_data)


async def async_finish_recognition(service: VoiceInputService, session_id: str) -> str:
    """Async wrapper for stop_recognition."""
    return service.stop_recognition(session_id)


async def async_cancel_recognition(service: VoiceInputService, session_id: str) -> None:
    """Async wrapper for cancel_recognition."""
    service.cancel_recognition(session_id)
