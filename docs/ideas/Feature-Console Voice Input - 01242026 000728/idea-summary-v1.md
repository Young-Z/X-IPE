# Idea Summary v1: Voice Input for Console

> **Status:** Draft  
> **Version:** 1.0  
> **Created:** 2026-01-24  
> **Refined by:** Bolt (TASK-106)

---

## 1. Problem Statement

Users currently interact with the X-IPE Console through keyboard input only. This limits accessibility and efficiency, especially when hands are occupied or for users who prefer voice interaction. Adding voice-to-text input would enable hands-free terminal operation.

---

## 2. Proposed Solution

Add a **push-to-talk voice input** feature to the Console that captures audio, sends it to Alibaba's real-time speech recognition service (gummy-realtime-v1), and injects the transcribed text into the focused terminal window.

---

## 3. Key Features

### 3.1 UI Changes

| Component | Current State | Proposed Change |
|-----------|--------------|-----------------|
| Connection Status | Right side of console bar | Move to **left side**, beside "Console" text |
| Voice Indicator | N/A | Add **right side**, left of mic toggle (visible when voice active) |
| Mic Toggle | N/A | Add **right side**, left of "+" icon |
| Add Terminal (+) | Right side of console bar | Keep on **right side**, left of window controls |

### 3.2 Voice Input Behavior

| Aspect | Decision |
|--------|----------|
| **Activation Mode** | Push-to-talk (hold hotkey to speak) |
| **Hotkey** | `Ctrl+Shift+V` (configurable) |
| **Target Terminal** | Focused terminal pane only |
| **Transcription Mode** | Complete phrases only (not real-time streaming) |
| **Auto-Execute** | No - user manually presses Enter to execute |
| **Voice Command** | "close mic" disables voice feature |

### 3.3 Technical Integration

- **Speech Recognition API:** Alibaba Cloud gummy-realtime-v1
- **Documentation:** [Real-time Speech Recognition](https://help.aliyun.com/zh/model-studio/real-time-speech-recognition?spm=a2c4g.11186623.help-menu-2400256.d_0_5_0.490c23f5SE6gyr&scm=20140722.H_2842554._.OR_help-T_cn~zh-V_1)
- **Audio Flow:** Browser → WebSocket → Server → Alibaba API → Server → Terminal

---

## 4. User Flow

```
1. User clicks mic toggle ON (mic icon appears active)
2. User focuses on a terminal pane
3. User holds Ctrl+Shift+V and speaks
4. Voice animation shows recording is active
5. User releases hotkey
6. Server transcribes audio via gummy-realtime-v1
7. Transcribed text appears in terminal input line
8. User reviews and presses Enter to execute
9. (Optional) User says "close mic" → mic toggle turns OFF
```

---

## 5. Visual Design Reference

Based on `current design reference.png`:

```
┌─────────────────────────────────────────────────────────────┐
│  Console ●Connected                   [🔊] [🎤] [+] [−] [□] │
│─────────────────────────────────────────────────────────────│
│  Terminal 1                    │  Terminal 2                │
│  $ _                           │  $ _                       │
│                                │                            │
└─────────────────────────────────────────────────────────────┘

LEFT side:
  Console    - Section title
  ●Connected - Connection status (moved from right)
  
RIGHT side (left to right):
  [🔊]       - Voice animation indicator (visible when active)
  [🎤]       - Mic toggle button
  [+]        - Add terminal button (existing)
  [−] [□]    - Minimize/maximize controls (existing)
```

---

## 6. Acceptance Criteria (Draft)

- [ ] AC-1: Connection status displays on left side beside "Console" text
- [ ] AC-2: Mic toggle button visible left of "+" icon
- [ ] AC-3: Voice animation indicator shows when voice is active
- [ ] AC-4: Holding Ctrl+Shift+V starts audio capture
- [ ] AC-5: Releasing hotkey stops capture and sends audio for transcription
- [ ] AC-6: Transcribed text appears in focused terminal's input
- [ ] AC-7: Voice command "close mic" disables mic toggle
- [ ] AC-8: Mic toggle OFF prevents voice input
- [ ] AC-9: Error state shows visual feedback when recognition fails

---

## 7. Open Questions

1. **Animation Style:** What visual indicator for active voice recording? (pulsing mic, waveform bars, glow effect)
2. **Language Support:** Should it support multiple languages or Chinese only?
3. **Error Handling:** How to handle network disconnection during voice capture?
4. **Settings:** Should hotkey be configurable in Settings page?

---

## 8. Out of Scope (v1)

- Voice commands for terminal control (cd, ls, etc.)
- Multi-language simultaneous detection
- Voice feedback/text-to-speech
- Voice-activated wake word

---

## 9. Next Steps

1. **Mockup:** Create visual mockup of console bar with voice controls
2. **Requirement Gathering:** Convert to formal requirements if approved
3. **Technical Spike:** Validate gummy-realtime-v1 API integration

---

*This idea summary is ready for human review. Approve to proceed to Idea Mockup phase.*
