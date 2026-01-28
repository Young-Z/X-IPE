/**
 * FEATURE-021: Console Voice Input
 * 
 * VoiceInputManager - Handles push-to-talk voice input for terminal
 * Uses MediaRecorder API for audio capture and Socket.IO for communication
 * 
 * Hotkey: Ctrl+Shift+V (hold to record, release to transcribe)
 * Prerequisite: Mic toggle must be ON before hotkey works
 */

class VoiceInputManager {
    constructor(socket) {
        this.socket = socket;
        
        // State
        this.micEnabled = false;
        this.isRecording = false;
        this.isProcessing = false;
        this.permissionState = 'prompt';
        this.partialText = '';
        this.error = null;
        
        // Audio
        this.mediaStream = null;
        this.audioContext = null;
        this.scriptProcessor = null;
        this.sessionId = null;
        
        // Timing
        this.recordingStartTime = null;
        this.maxDuration = 30000; // 30 seconds max
        this.autoStopTimeout = null;
        this.debounceTimeout = null;
        this.debounceDelay = 200; // 200ms debounce for hotkey
        
        // UI Elements
        this.micToggle = document.getElementById('mic-toggle');
        this.voiceIndicator = document.getElementById('voice-indicator');
        this.transcriptionPreview = document.getElementById('transcription-preview');
        this.transcriptionText = document.getElementById('transcription-text');
        
        // Initialize
        this.bindEvents();
        this.loadState();
    }
    
    /**
     * Bind DOM and Socket.IO events
     */
    bindEvents() {
        // Mic toggle button
        if (this.micToggle) {
            this.micToggle.addEventListener('click', (e) => {
                e.stopPropagation();  // Prevent header toggle
                this.toggleMic();
            });
        }
        
        // Hotkey: Ctrl+Shift+V
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));
        
        // Socket.IO events from server
        if (this.socket) {
            this.socket.on('voice_ready', (data) => this.onVoiceReady(data));
            this.socket.on('voice_partial', (data) => this.onVoicePartial(data));
            this.socket.on('voice_result', (data) => this.onVoiceResult(data));
            this.socket.on('voice_command', (data) => this.onVoiceCommand(data));
            this.socket.on('voice_error', (data) => this.onVoiceError(data));
            this.socket.on('voice_cancelled', () => this.onVoiceCancelled());
        }
    }
    
    /**
     * Load persisted state from localStorage
     */
    loadState() {
        const savedState = localStorage.getItem('voiceInput.micEnabled');
        if (savedState === 'true') {
            // Re-enable mic on reload (will prompt for permission)
            this.enableMic();
        }
    }
    
    /**
     * Save state to localStorage
     */
    saveState() {
        localStorage.setItem('voiceInput.micEnabled', this.micEnabled.toString());
    }
    
    /**
     * Toggle microphone on/off
     */
    async toggleMic() {
        if (this.micEnabled) {
            this.disableMic();
        } else {
            await this.enableMic();
        }
    }
    
    /**
     * Enable microphone - request permission and get audio stream
     */
    async enableMic() {
        try {
            // Check if MediaRecorder is available
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('MediaRecorder not supported in this browser');
            }
            
            // Request microphone permission
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            
            this.permissionState = 'granted';
            this.micEnabled = true;
            this.updateUI();
            this.saveState();
            
            console.log('[Voice] Microphone enabled');
        } catch (err) {
            console.error('[Voice] Failed to enable mic:', err);
            this.permissionState = err.name === 'NotAllowedError' ? 'denied' : 'prompt';
            this.error = err.message;
            this.updateUI();
        }
    }
    
    /**
     * Disable microphone - stop stream and release resources
     */
    disableMic() {
        if (this.isRecording) {
            this.stopRecording(true); // Cancel if recording
        }
        
        // Clean up ScriptProcessor
        if (this.scriptProcessor) {
            this.scriptProcessor.disconnect();
            this.scriptProcessor = null;
        }
        
        // Clean up AudioContext
        if (this.audioContext && this.audioContext.state !== 'closed') {
            this.audioContext.close().catch(() => {});
            this.audioContext = null;
        }
        
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }
        
        this.micEnabled = false;
        this.updateUI();
        this.saveState();
        
        console.log('[Voice] Microphone disabled');
    }
    
    /**
     * Handle keydown event for hotkey
     */
    handleKeyDown(e) {
        // Check for Ctrl+Shift+V
        if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'v') {
            e.preventDefault();
            
            // Debounce rapid presses
            if (this.debounceTimeout) return;
            
            this.debounceTimeout = setTimeout(() => {
                this.debounceTimeout = null;
            }, this.debounceDelay);
            
            // Only start if mic is enabled and not already recording
            if (this.micEnabled && !this.isRecording && !this.isProcessing) {
                this.startRecording();
            }
        }
    }
    
    /**
     * Handle keyup event for hotkey
     */
    handleKeyUp(e) {
        // Check for Ctrl+Shift+V release
        if (!e.key) return;
        if (e.key.toLowerCase() === 'v' || e.key === 'Control' || e.key === 'Shift') {
            if (this.isRecording) {
                // Check if the combination is still held
                if (!e.ctrlKey || !e.shiftKey) {
                    this.stopRecording(false);
                }
            }
        }
    }
    
    /**
     * Start recording audio
     */
    startRecording() {
        if (!this.mediaStream) {
            console.error('[Voice] No media stream available');
            return;
        }
        
        try {
            this.isRecording = true;
            this.partialText = '';
            this.recordingStartTime = Date.now();
            
            // Create AudioContext for PCM conversion
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 16000  // 16kHz for speech recognition
            });
            
            // Create source from media stream
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            
            // Create ScriptProcessor for raw PCM access
            // Buffer size 4096 at 16kHz = ~256ms chunks
            this.scriptProcessor = this.audioContext.createScriptProcessor(4096, 1, 1);
            
            this.scriptProcessor.onaudioprocess = (e) => {
                if (!this.isRecording) return;
                
                // Get raw PCM float data
                const inputData = e.inputBuffer.getChannelData(0);
                
                // Convert Float32 to Int16 PCM
                const pcmData = this.float32ToInt16(inputData);
                
                // Send to server
                this.sendAudioChunk(pcmData);
            };
            
            // Connect: source -> processor -> destination (required for processing)
            source.connect(this.scriptProcessor);
            this.scriptProcessor.connect(this.audioContext.destination);
            
            // Emit voice_start to server
            if (this.socket) {
                this.socket.emit('voice_start', {});
            }
            
            // Auto-stop after max duration
            this.autoStopTimeout = setTimeout(() => {
                if (this.isRecording) {
                    console.log('[Voice] Auto-stopping after max duration');
                    this.stopRecording(false);
                }
            }, this.maxDuration);
            
            this.updateUI();
            console.log('[Voice] Recording started (PCM 16kHz mono)');
        } catch (err) {
            console.error('[Voice] Failed to start recording:', err);
            this.isRecording = false;
            this.error = err.message;
            this.updateUI();
        }
    }
    
    /**
     * Convert Float32 audio samples to Int16 PCM
     */
    float32ToInt16(float32Array) {
        const int16Array = new Int16Array(float32Array.length);
        for (let i = 0; i < float32Array.length; i++) {
            // Clamp to [-1, 1] and convert to 16-bit signed int
            const s = Math.max(-1, Math.min(1, float32Array[i]));
            int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return int16Array.buffer;  // Return ArrayBuffer
    }
    
    /**
     * Stop recording and request transcription (or cancel)
     */
    stopRecording(cancel = false) {
        if (!this.isRecording) return;
        
        this.isRecording = false;
        
        // Clear auto-stop timeout
        if (this.autoStopTimeout) {
            clearTimeout(this.autoStopTimeout);
            this.autoStopTimeout = null;
        }
        
        // Stop ScriptProcessor
        if (this.scriptProcessor) {
            this.scriptProcessor.disconnect();
            this.scriptProcessor = null;
        }
        
        // Close AudioContext (will recreate on next recording)
        if (this.audioContext && this.audioContext.state !== 'closed') {
            this.audioContext.close().catch(() => {});
            this.audioContext = null;
        }
        
        // Emit stop or cancel to server
        if (this.socket) {
            if (cancel) {
                this.socket.emit('voice_cancel', {});
            } else {
                this.isProcessing = true;
                this.socket.emit('voice_stop', {});
            }
        }
        
        this.updateUI();
        console.log('[Voice] Recording stopped, cancel:', cancel);
    }
    
    /**
     * Send audio chunk to server (PCM ArrayBuffer)
     */
    sendAudioChunk(arrayBuffer) {
        if (!this.socket) return;
        
        try {
            // Convert ArrayBuffer to regular array for JSON serialization
            const audioData = new Uint8Array(arrayBuffer);
            
            this.socket.emit('voice_audio', {
                audio: Array.from(audioData)
            });
        } catch (err) {
            console.error('[Voice] Failed to send audio:', err);
        }
    }
    
    /**
     * Handle voice_ready event from server
     */
    onVoiceReady(data) {
        this.sessionId = data.session_id;
        console.log('[Voice] Session ready:', this.sessionId);
    }
    
    /**
     * Handle voice_partial event - update preview
     */
    onVoicePartial(data) {
        this.partialText = data.text;
        this.updateTranscriptionPreview(data.text);
    }
    
    /**
     * Handle voice_result event - inject into terminal
     */
    onVoiceResult(data) {
        this.isProcessing = false;
        this.updateUI();
        
        const text = data.text?.trim();
        if (text) {
            this.injectToTerminal(text);
            this.updateTranscriptionPreview('');
        }
        
        console.log('[Voice] Result:', text);
    }
    
    /**
     * Handle voice_command event
     */
    onVoiceCommand(data) {
        this.isProcessing = false;
        this.updateUI();
        
        console.log('[Voice] Command:', data.command);
        
        if (data.command === 'close_mic') {
            this.disableMic();
        }
    }
    
    /**
     * Handle voice_error event
     */
    onVoiceError(data) {
        this.isProcessing = false;
        this.error = data.message;
        this.updateUI();
        
        console.error('[Voice] Error:', data.message);
    }
    
    /**
     * Handle voice_cancelled event
     */
    onVoiceCancelled() {
        this.isProcessing = false;
        this.partialText = '';
        this.updateTranscriptionPreview('');
        this.updateUI();
        
        console.log('[Voice] Recording cancelled');
    }
    
    /**
     * Inject transcribed text into focused terminal
     */
    injectToTerminal(text) {
        console.log('[Voice] Injecting text to terminal:', text);
        
        // Get the focused terminal from TerminalManager
        if (window.terminalManager) {
            console.log('[Voice] terminalManager.activeIndex:', window.terminalManager.activeIndex);
            console.log('[Voice] paneManager.terminals:', window.terminalManager.paneManager?.terminals);
            
            const terminal = window.terminalManager.getFocusedTerminal();
            console.log('[Voice] Focused terminal object:', terminal);
            
            if (terminal) {
                console.log('[Voice] terminal.sessionId:', terminal.sessionId);
                console.log('[Voice] terminal.socket connected:', terminal.socket?.connected);
                
                if (terminal.sendInput) {
                    console.log('[Voice] Calling terminal.sendInput()...');
                    terminal.sendInput(text);
                    console.log('[Voice] sendInput() called successfully');
                } else {
                    console.warn('[Voice] No sendInput method on terminal');
                }
            } else {
                console.warn('[Voice] getFocusedTerminal() returned null');
            }
        } else {
            console.warn('[Voice] No terminalManager found on window');
        }
    }
    
    /**
     * Update transcription preview bar
     */
    updateTranscriptionPreview(text) {
        if (this.transcriptionText) {
            this.transcriptionText.textContent = text;
        }
        if (this.transcriptionPreview) {
            if (text) {
                this.transcriptionPreview.classList.add('visible');
            } else {
                this.transcriptionPreview.classList.remove('visible');
            }
        }
    }
    
    /**
     * Update UI based on current state
     */
    updateUI() {
        // Mic toggle button
        if (this.micToggle) {
            if (this.micEnabled) {
                this.micToggle.classList.add('enabled');
                this.micToggle.innerHTML = '<i class="bi bi-mic"></i>';
                this.micToggle.title = 'Microphone ON (Ctrl+Shift+V to record)';
            } else {
                this.micToggle.classList.remove('enabled');
                this.micToggle.innerHTML = '<i class="bi bi-mic-mute"></i>';
                this.micToggle.title = 'Click to enable microphone';
            }
            
            // Permission denied state
            if (this.permissionState === 'denied') {
                this.micToggle.classList.add('denied');
                this.micToggle.title = 'Microphone permission denied';
            } else {
                this.micToggle.classList.remove('denied');
            }
        }
        
        // Voice indicator
        if (this.voiceIndicator) {
            if (this.isRecording) {
                this.voiceIndicator.classList.add('recording');
            } else if (this.isProcessing) {
                this.voiceIndicator.classList.add('processing');
                this.voiceIndicator.classList.remove('recording');
            } else {
                this.voiceIndicator.classList.remove('recording', 'processing');
            }
        }
    }
}

// Export for use by other modules
window.VoiceInputManager = VoiceInputManager;
