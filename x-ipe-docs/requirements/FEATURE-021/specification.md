# Feature Specification: Console Voice Input

> Feature ID: FEATURE-021  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-25-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 01-25-2026 | Initial specification - push-to-talk voice input for console | - |

---

## Overview

Console Voice Input brings hands-free terminal operation to X-IPE by adding a push-to-talk voice input feature to the Interactive Console. Users can hold a hotkey (`Ctrl+Shift+V`) to speak commands, which are transcribed using Alibaba Cloud's gummy-realtime-v1 speech recognition service and injected into the focused terminal pane.

This feature enhances accessibility and efficiency for developers who prefer voice interaction or have hands occupied (e.g., referencing documentation, holding a cup of coffee). The voice input does NOT auto-execute commands—users review the transcribed text and press Enter manually, ensuring safety and control.

**Key Capabilities:**
- **Push-to-Talk**: Hold hotkey to record, release to transcribe
- **Alibaba Cloud Integration**: Real-time speech recognition via WebSocket
- **Focused Terminal Targeting**: Transcribed text goes to the active terminal pane
- **Visual Feedback**: Waveform animation, transcription preview, recording indicators
- **Voice Command**: "close mic" disables the feature

---

## Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| voice-input-console | [voice-input-console.html](mockups/voice-input-console.html) |

---

## User Stories

- As a **developer**, I want to **speak commands instead of typing**, so that **I can interact with the terminal hands-free**.

- As a **developer**, I want to **see visual feedback when recording**, so that **I know the system is capturing my voice**.

- As a **developer**, I want to **review transcribed text before execution**, so that **I can correct any recognition errors**.

- As a **developer**, I want to **disable voice input with a voice command**, so that **I can quickly turn it off without using the mouse**.

- As a **developer**, I want to **the transcription to target the focused terminal**, so that **I can control which pane receives my input**.

---

## Acceptance Criteria

### Phase 1: UI Layout (P1)

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-1.1 | Connection status indicator MUST be moved from right side to left side of console header, beside "Console" text | Must | Yes |
| AC-1.2 | Mic toggle button MUST be added to the right side of console header, positioned left of "+" (Add Terminal) icon | Must | Yes |
| AC-1.3 | Voice animation indicator (waveform bars) MUST appear to the left of mic toggle when recording is active | Must | Yes |
| AC-1.4 | Existing "Add Terminal" (+) button MUST remain on right side, left of window controls (Zen, Collapse) | Must | Yes |
| AC-1.5 | Console header layout MUST match mockup: `[Console ●Connected] ... [🔊] [🎤] [+] [⛶] [▼]` | Must | Yes |

### Phase 2: Mic Toggle Behavior (P2)

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-2.1 | Mic toggle button MUST have two states: OFF (default, gray) and ON (enabled, cyan highlight) | Must | Yes |
| AC-2.2 | Clicking mic toggle MUST switch between OFF and ON states | Must | Yes |
| AC-2.3 | When mic is OFF, voice hotkey (`Ctrl+Shift+V`) MUST have no effect | Must | Yes |
| AC-2.4 | When mic is first enabled, browser MUST request microphone permission if not already granted | Must | Yes |
| AC-2.5 | If user denies mic permission, mic toggle MUST remain OFF with tooltip explaining the issue | Must | Yes |
| AC-2.6 | Mic state SHOULD persist in localStorage across page reloads | Should | Yes |

### Phase 3: Voice Input Recording (P3)

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-3.1 | Holding `Ctrl+Shift+V` (while mic ON) MUST start audio capture | Must | Yes |
| AC-3.2 | Audio MUST be captured using browser MediaRecorder API with PCM/WAV format at 16kHz sample rate | Must | Yes |
| AC-3.3 | Mic toggle button MUST change to "recording" style (orange highlight) during recording | Must | Yes |
| AC-3.4 | Voice animation indicator (5 waveform bars) MUST animate during recording | Must | Yes |
| AC-3.5 | Transcription preview bar MUST appear below console header during recording | Must | Yes |
| AC-3.6 | Transcription preview MUST show partial transcription text if available from streaming | Should | Yes |
| AC-3.7 | Transcription preview MUST show hotkey hint "Release to send" | Must | Yes |
| AC-3.8 | Releasing hotkey MUST stop audio capture and trigger transcription | Must | Yes |
| AC-3.9 | Recording MUST auto-stop after 30 seconds maximum | Must | Yes |

### Phase 4: Speech Recognition & Injection (P4)

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-4.1 | Audio MUST be sent to backend server via WebSocket for relay to Alibaba Cloud | Must | Yes |
| AC-4.2 | Backend MUST use Alibaba Cloud gummy-realtime-v1 API for transcription | Must | Yes |
| AC-4.3 | API connection MUST use WebSocket with Bearer token authentication | Must | Yes |
| AC-4.4 | Transcribed text MUST be injected into the focused terminal pane's input line | Must | Yes |
| AC-4.5 | If no terminal pane is focused, transcription MUST target the last active pane | Must | Yes |
| AC-4.6 | Transcription MUST NOT auto-execute (user presses Enter manually) | Must | Yes |
| AC-4.7 | Text injection MUST simulate keyboard input to terminal (xterm.js writeData) | Must | Yes |
| AC-4.8 | Transcription latency MUST be under 2 seconds after hotkey release | Should | Yes |

### Phase 5: Voice Commands (P5)

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-5.1 | Voice command "close mic" (case-insensitive) MUST disable mic toggle (turn OFF) | Must | Yes |
| AC-5.2 | Voice command "关闭麦克风" (Chinese equivalent) SHOULD also disable mic toggle | Should | Yes |
| AC-5.3 | When voice command is recognized, transcribed text MUST NOT be injected into terminal | Must | Yes |
| AC-5.4 | Visual feedback MUST indicate voice command was executed (brief toast/notification) | Should | Yes |

### Phase 6: Error Handling (P6)

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-6.1 | If speech recognition fails, error message MUST appear in transcription preview area | Must | Yes |
| AC-6.2 | Network disconnection during capture MUST show error and reset recording state | Must | Yes |
| AC-6.3 | If Alibaba Cloud API is unavailable, mic toggle SHOULD be disabled with tooltip | Should | Yes |
| AC-6.4 | Empty/silent audio (no speech detected) MUST reset state silently without error | Must | Yes |
| AC-6.5 | Multiple rapid hotkey presses MUST be debounced (ignore until operation completes) | Must | Yes |
| AC-6.6 | Browser without MediaRecorder support MUST show error, mic toggle disabled | Must | Yes |

---

## Functional Requirements

### FR-1: Console Header UI Modification

**Description:** Modify console header layout to accommodate voice input controls

**Details:**
- Input: Current console header with connection status on right
- Process: Relocate connection status to left, add mic toggle and voice indicator on right
- Output: Updated header matching mockup layout

**Components:**
- Connection status badge (moved to left)
- Voice animation indicator (5 bars, animated during recording)
- Mic toggle button (with 3 states: off, on, recording)

### FR-2: Microphone Permission Management

**Description:** Handle browser microphone permission lifecycle

**Details:**
- Input: User clicks mic toggle to enable
- Process: Check permission state, request if needed, handle grant/deny
- Output: Mic enabled (permission granted) or error shown (permission denied)

**Permission States:**
- `prompt`: Show permission dialog
- `granted`: Enable mic functionality
- `denied`: Show error tooltip, keep mic OFF

### FR-3: Push-to-Talk Audio Capture

**Description:** Capture audio while hotkey is held

**Details:**
- Input: User holds `Ctrl+Shift+V` with mic enabled
- Process: Start MediaRecorder, stream audio chunks via WebSocket
- Output: Audio data sent to server

**Audio Configuration:**
- Format: PCM (audio/wav preferred, audio/webm fallback)
- Sample Rate: 16kHz
- Channels: Mono (1 channel)
- Chunk Size: 100ms intervals

### FR-4: Alibaba Cloud Speech Recognition Integration

**Description:** Backend service to relay audio to Alibaba Cloud gummy-realtime-v1

**Details:**
- Input: Audio stream from frontend WebSocket
- Process: Connect to Alibaba API, send `run-task`, stream audio, receive transcription
- Output: Transcribed text returned to frontend

**API Workflow:**
1. Open WebSocket to `wss://dashscope.aliyuncs.com/api-ws/v1/inference`
2. Send `run-task` with model `gummy-realtime-v1`
3. On `task-started`, stream audio chunks (100ms each)
4. Receive `result-generated` events with partial/final text
5. Send `finish-task` on recording end
6. Return final transcription to frontend

### FR-5: Terminal Text Injection

**Description:** Inject transcribed text into focused terminal

**Details:**
- Input: Transcribed text from speech recognition
- Process: Identify focused terminal pane, simulate keyboard input
- Output: Text appears in terminal input line

**Rules:**
- Target: Currently focused terminal pane (indicated by cyan border)
- Fallback: Last active terminal if none focused
- Method: xterm.js `write()` or `paste()` API
- Safety: No auto-execute, user presses Enter

### FR-6: Voice Command Processing

**Description:** Recognize and execute voice commands

**Details:**
- Input: Transcribed text
- Process: Check against command patterns before terminal injection
- Output: Execute command action if matched, else inject text

**Commands (v1):**
| Voice Command | Action |
|---------------|--------|
| "close mic" | Disable mic toggle |
| "关闭麦克风" | Disable mic toggle |

### FR-7: Visual Feedback System

**Description:** Provide real-time visual feedback during voice operations

**Details:**
- Recording active: Orange mic button, animated waveform bars
- Mic enabled: Cyan mic button highlight
- Mic disabled: Gray mic button (default)
- Processing: "Processing..." in transcription preview
- Error: Red text in transcription preview, auto-dismiss after 3s

---

## Non-Functional Requirements

### NFR-1: Performance

| Metric | Target |
|--------|--------|
| Transcription latency | < 2 seconds after release |
| Audio streaming latency | < 100ms chunk delivery |
| UI responsiveness | < 50ms for state changes |

### NFR-2: Security

| Requirement | Implementation |
|-------------|----------------|
| API Key Protection | Store Alibaba Cloud API key server-side only |
| Audio Data | Not stored, processed in-memory only |
| WebSocket | Use WSS (encrypted) for all connections |

### NFR-3: Browser Compatibility

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | 90+ | Full |
| Firefox | 88+ | Full |
| Edge | 90+ | Full |
| Safari | 14.1+ | Partial (MediaRecorder limitations) |

### NFR-4: Accessibility

| Requirement | Implementation |
|-------------|----------------|
| Keyboard only | Hotkey-based activation, no mouse required |
| Screen reader | ARIA labels for mic toggle and status |
| Visual impairment | High contrast states, not color-only indicators |

---

## UI/UX Requirements

### Console Header Layout

```
┌─────────────────────────────────────────────────────────────┐
│  [≡] Console ●Connected                   [🔊] [🎤] [+] [⛶] [▼] │
└─────────────────────────────────────────────────────────────┘
     │         │                             │    │   │   │   │
     │         └─ Connection status (left)   │    │   │   │   └─ Collapse
     │                                       │    │   │   └─ Zen mode
     │                                       │    │   └─ Add terminal
     │                                       │    └─ Mic toggle
     └─ Console icon                         └─ Voice indicator (when recording)
```

### State Transitions

```
[Mic OFF] --click--> [Mic ON] --hold Ctrl+Shift+V--> [Recording]
    ^                    |                               |
    |                    |<--release hotkey--            |
    |                    |                               v
    └----"close mic"-----+<---------[Transcribing]-------┘
```

### UI Elements

| Element | States | Visual |
|---------|--------|--------|
| Mic Toggle | off, on, recording | Gray → Cyan → Orange |
| Voice Indicator | hidden, visible+animated | 5 bars, cyan glow |
| Transcription Preview | hidden, recording, processing, error | Slide-in bar below header |
| Connection Status | connected, disconnected | Green/Red dot with text |

### User Flows

**Flow 1: Normal Voice Input**
1. User clicks mic toggle → Mic enabled (cyan)
2. User focuses terminal pane → Pane highlighted
3. User holds `Ctrl+Shift+V` → Recording starts, waveform animates
4. User speaks "git status"
5. User releases hotkey → Recording stops
6. Transcription preview shows "Processing..."
7. Text "git status" appears in terminal input
8. User presses Enter to execute

**Flow 2: Voice Command**
1. User has mic enabled
2. User holds hotkey, says "close mic"
3. User releases hotkey
4. System recognizes command
5. Toast: "Mic disabled"
6. Mic toggle turns OFF

---

## Dependencies

### Internal Dependencies

| Feature | Dependency Type | Reason |
|---------|-----------------|--------|
| FEATURE-005: Interactive Console | Hard | Requires terminal panes, WebSocket infrastructure, xterm.js |

### External Dependencies

| Dependency | Purpose | Version |
|------------|---------|---------|
| Alibaba Cloud Model Studio | gummy-realtime-v1 speech recognition | API v1 |
| MediaRecorder API | Browser audio capture | Web standard |
| xterm.js | Terminal text injection | 5.x (existing) |
| Socket.IO | WebSocket communication | 4.x (existing) |

---

## Business Rules

### BR-1: No Auto-Execution

**Rule:** Transcribed text is NEVER auto-executed. User must press Enter.
**Rationale:** Prevents accidental destructive commands from recognition errors.

### BR-2: Focused Terminal Only

**Rule:** Voice input targets only the focused terminal pane.
**Rationale:** Predictable behavior, user controls destination.

### BR-3: Mic State Explicit

**Rule:** Voice hotkey only works when mic toggle is explicitly ON.
**Rationale:** Prevents accidental recordings, privacy protection.

### BR-4: Recording Time Limit

**Rule:** Maximum recording duration is 30 seconds.
**Rationale:** Prevents excessive API usage, encourages concise commands.

---

## Edge Cases & Constraints

### Edge Case 1: No Terminal Focused

**Scenario:** User records voice but no terminal pane is focused
**Expected Behavior:** Inject text into last active terminal pane

### Edge Case 2: Network Disconnection During Recording

**Scenario:** WebSocket disconnects while user is speaking
**Expected Behavior:** Show error "Network error - please try again", reset recording state, do not inject partial text

### Edge Case 3: Browser Denies Mic Permission

**Scenario:** User denies microphone permission prompt
**Expected Behavior:** Mic toggle remains OFF, tooltip shows "Microphone access denied. Click to learn more."

### Edge Case 4: Silent Audio

**Scenario:** User holds hotkey but doesn't speak
**Expected Behavior:** Reset state silently, no error shown, no text injected

### Edge Case 5: Very Long Recording

**Scenario:** User holds hotkey for over 30 seconds
**Expected Behavior:** Auto-stop at 30s, proceed with transcription of recorded portion

### Edge Case 6: Rapid Hotkey Presses

**Scenario:** User rapidly presses hotkey multiple times
**Expected Behavior:** Debounce, only first press triggers recording until operation completes

### Edge Case 7: Terminal Focus Changes During Recording

**Scenario:** User clicks different terminal pane while recording
**Expected Behavior:** Transcribed text goes to newly focused pane

### Edge Case 8: API Quota Exceeded

**Scenario:** Alibaba Cloud API returns quota error
**Expected Behavior:** Show "Service temporarily unavailable", disable mic toggle, retry after 1 minute

---

## Out of Scope

The following are explicitly **NOT** included in v1.0:

| Feature | Reason | Future Version |
|---------|--------|----------------|
| Voice commands for terminal control | Complexity, safety concerns | v2.0 |
| Multi-language simultaneous detection | API limitation | v2.0 |
| Voice feedback/text-to-speech | Different feature category | v2.0 |
| Voice-activated wake word | Always-listening privacy concerns | v2.0 |
| Configurable hotkey | Settings UI complexity | v1.1 |
| Real-time streaming to terminal | UX preference for complete phrases | v2.0 |
| Offline speech recognition | API dependency | v2.0 |

---

## Technical Considerations

### Audio Flow Architecture

```
Browser (MediaRecorder)
    │
    │ Audio chunks (100ms)
    ▼
Frontend WebSocket Client
    │
    │ Binary frames
    ▼
Backend WebSocket Server (Flask-SocketIO)
    │
    │ Audio stream
    ▼
Alibaba Cloud gummy-realtime-v1
    │
    │ Transcription events
    ▼
Backend → Frontend → Terminal
```

### API Integration Notes

- Endpoint: `wss://dashscope.aliyuncs.com/api-ws/v1/inference`
- Auth: `Authorization: Bearer <API_KEY>` header
- Model: `gummy-realtime-v1`
- Audio: PCM 16kHz mono, chunks ~100ms
- Language: Chinese (primary), English (secondary)

### Frontend Considerations

- Use `navigator.permissions.query({ name: 'microphone' })` for permission state
- MediaRecorder with `audio/webm;codecs=opus` or `audio/wav` fallback
- Debounce hotkey events to prevent double-triggers
- Clean up MediaRecorder on component unmount

### Backend Considerations

- Maintain WebSocket connection pool to Alibaba API
- Handle API reconnection on disconnect
- Log transcription requests for debugging (without audio data)
- Rate limit per-user to prevent abuse

---

## Open Questions

All questions resolved during ideation phase. No open questions for v1.0.

---

## Glossary

| Term | Definition |
|------|------------|
| PTT | Push-to-Talk - voice activation mode requiring continuous button press |
| gummy-realtime-v1 | Alibaba Cloud's real-time speech recognition model |
| WebSocket | Full-duplex communication protocol for streaming |
| xterm.js | Terminal emulator library used in FEATURE-005 |
| MediaRecorder | Browser API for recording audio/video |

---

*Specification complete. Ready for Technical Design phase.*
