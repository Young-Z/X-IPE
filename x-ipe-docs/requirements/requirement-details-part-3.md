# Requirement Details - Part 3

> Continued from: [requirement-details-part-2.md](requirement-details-part-2.md)  
> Created: 01-25-2026

---

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-021 | Console Voice Input | v1.0 | Push-to-talk voice input for terminal with Alibaba Cloud speech recognition | FEATURE-005 |
| FEATURE-022-A | Browser Simulator & Proxy | v1.0 | Localhost proxy backend and browser simulator UI for viewing local web pages | FEATURE-008 |
| FEATURE-022-B | Element Inspector | v1.0 | Hover highlighting and multi-select element inspection within browser simulator | FEATURE-022-A |
| FEATURE-022-C | Feedback Capture & Panel | v1.0 | Right-click context menu and feedback entry panel with screenshot capture | FEATURE-022-B |
| FEATURE-022-D | Feedback Storage & Submission | v1.0 | Save feedback to structured folders and generate terminal command for agent | FEATURE-022-C |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| voice-input-console | FEATURE-021 | [mockup.html](../ideas/Console%20Voice%20Input%20-%2001242026%20000728/mockup.html) |
| uiux-feedback-view | FEATURE-022 | [uiux-feedback-v1.html](../ideas/005.%20Feature-UIUX%20Feedback/mockups/uiux-feedback-v1.html) |

---

## Feature Details (Continued)

### FEATURE-021: Console Voice Input

**Version:** v1.0  
**Brief Description:** Push-to-talk voice input feature for the Console that captures audio, sends it to Alibaba Cloud's real-time speech recognition service (gummy-realtime-v1), and injects transcribed text into the focused terminal pane.

**Source:** [Idea Summary v1 - Voice Input for Console](../ideas/Console%20Voice%20Input%20-%2001242026%20000728/idea-summary-v1.md)  
**Mockup:** [Voice Input Console Mockup](../ideas/Console%20Voice%20Input%20-%2001242026%20000728/mockup.html)  
**Design Reference:** [Current Console Design](../ideas/Console%20Voice%20Input%20-%2001242026%20000728/current%20design%20reference.png)

#### Problem Statement

Users currently interact with the X-IPE Console through keyboard input only. This limits accessibility and efficiency, especially when hands are occupied or for users who prefer voice interaction. Adding voice-to-text input would enable hands-free terminal operation.

#### Acceptance Criteria

**1. UI Layout Changes**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-1.1 | Connection status indicator MUST be moved from right side to left side, beside "Console" text | Must |
| AC-1.2 | Mic toggle button MUST be added to the right side of console header, left of "+" (Add Terminal) icon | Must |
| AC-1.3 | Voice animation indicator MUST appear to the left of mic toggle when voice is active | Must |
| AC-1.4 | Existing "Add Terminal" (+) button MUST remain on right side, left of window controls | Must |

**2. Mic Toggle Behavior**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-2.1 | Mic toggle button MUST have two states: OFF (default) and ON (enabled) | Must |
| AC-2.2 | Clicking mic toggle MUST switch between OFF and ON states | Must |
| AC-2.3 | When mic is OFF, button MUST show default/inactive styling | Must |
| AC-2.4 | When mic is ON, button MUST show active styling (cyan highlight as per mockup) | Must |
| AC-2.5 | Voice input hotkey MUST only work when mic toggle is ON | Must |

**3. Voice Input Activation**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-3.1 | Voice input MUST use push-to-talk activation (hold hotkey to speak) | Must |
| AC-3.2 | Default hotkey MUST be `Ctrl+Shift+V` | Must |
| AC-3.3 | Hotkey SHOULD be configurable in Settings (future enhancement) | Should |
| AC-3.4 | Pressing hotkey while mic is OFF MUST have no effect | Must |
| AC-3.5 | Releasing hotkey MUST stop audio capture and trigger transcription | Must |

**4. Visual Feedback During Recording**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-4.1 | Voice animation indicator (waveform bars) MUST appear when recording starts | Must |
| AC-4.2 | Mic toggle button MUST change to "recording" style (orange highlight as per mockup) | Must |
| AC-4.3 | Transcription preview bar MUST appear below console header during recording | Must |
| AC-4.4 | Transcription preview MUST show real-time or partial transcription text if available | Should |
| AC-4.5 | Transcription preview MUST show "Release to send" hint | Must |

**5. Transcription & Text Injection**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-5.1 | Audio MUST be sent to Alibaba Cloud gummy-realtime-v1 API for transcription | Must |
| AC-5.2 | Transcribed text MUST be injected into the focused terminal pane's input line | Must |
| AC-5.3 | If no terminal pane is focused, transcription SHOULD target the last active pane | Should |
| AC-5.4 | Transcription MUST NOT auto-execute commands (user manually presses Enter) | Must |
| AC-5.5 | Complete phrases MUST be transcribed (not real-time streaming to terminal) | Must |

**6. Voice Commands**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-6.1 | Voice command "close mic" MUST disable mic toggle (turn OFF) | Must |
| AC-6.2 | Voice command recognition SHOULD be case-insensitive | Should |
| AC-6.3 | Additional voice commands MAY be added in future versions | Could |

**7. Error Handling**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-7.1 | If speech recognition fails, visual error feedback MUST be shown | Must |
| AC-7.2 | Error state SHOULD show brief message in transcription preview area | Should |
| AC-7.3 | Network disconnection during capture MUST be handled gracefully | Must |
| AC-7.4 | If API is unavailable, mic toggle SHOULD be disabled with tooltip explanation | Should |

**8. Technical Integration**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-8.1 | Audio capture MUST use browser's MediaRecorder API | Must |
| AC-8.2 | Audio MUST be streamed via WebSocket to backend server | Must |
| AC-8.3 | Backend MUST relay audio to Alibaba Cloud gummy-realtime-v1 API | Must |
| AC-8.4 | API documentation: [Real-time Speech Recognition](https://help.aliyun.com/zh/model-studio/real-time-speech-recognition) | Must |
| AC-8.5 | Audio flow: Browser → WebSocket → Server → Alibaba API → Server → Terminal | Must |

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | System SHALL provide a mic toggle button in console header | Must |
| FR-2 | System SHALL capture audio when hotkey is held and mic is enabled | Must |
| FR-3 | System SHALL transcribe audio using Alibaba Cloud speech recognition | Must |
| FR-4 | System SHALL inject transcribed text into focused terminal input | Must |
| FR-5 | System SHALL provide visual feedback during recording (animation, preview) | Must |
| FR-6 | System SHALL support "close mic" voice command | Must |
| FR-7 | System SHALL handle errors gracefully with user feedback | Must |

#### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Transcription latency | < 2 seconds after release |
| NFR-2 | Audio quality | 16kHz sample rate minimum |
| NFR-3 | Browser support | Chrome, Firefox, Edge (latest) |
| NFR-4 | Mic permission | Request only when toggle enabled |

#### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| EC-1 | User holds hotkey but mic is OFF | No action, no feedback |
| EC-2 | User switches terminal focus during recording | Continue recording, inject to newly focused pane |
| EC-3 | Network drops during recording | Show error, discard audio, reset state |
| EC-4 | Browser denies mic permission | Show error, disable mic toggle |
| EC-5 | Very long recording (>30 seconds) | Auto-stop and transcribe |
| EC-6 | Empty/silent audio | No text injected, reset state silently |
| EC-7 | Multiple hotkey presses in quick succession | Ignore until current operation completes |

#### Out of Scope (v1)

The following are explicitly out of scope for the initial version:

- Voice commands for terminal control (cd, ls, etc.)
- Multi-language simultaneous detection
- Voice feedback/text-to-speech
- Voice-activated wake word
- Configurable hotkey in Settings UI

#### Open Questions (Resolved)

| # | Question | Resolution |
|---|----------|------------|
| Q1 | Animation style for active recording? | Waveform bars (5 bars) as shown in mockup |
| Q2 | Language support? | Chinese primary, English secondary |
| Q3 | Error handling for network issues? | Show visual feedback, graceful degradation |
| Q4 | Hotkey configurable? | Not in v1, hardcoded to Ctrl+Shift+V |

---

## Dependencies

| Feature | Depends On | Reason |
|---------|------------|--------|
| FEATURE-021 | FEATURE-005 (Interactive Console) | Voice input requires existing console/terminal infrastructure |

---

### FEATURE-022-A: Browser Simulator & Proxy (MVP)

**Version:** v1.0  
**Brief Description:** Localhost proxy backend and browser simulator UI that enables viewing local web pages within X-IPE Workplace. This is the minimum runnable feature - users can load and view their localhost dev server.

**Source:** [Idea Summary v2 - UI/UX Feedback System](../ideas/005.%20Feature-UIUX%20Feedback/idea-summary-v2.md)  
**Mockup:** [UI/UX Feedback View Mockup](../ideas/005.%20Feature-UIUX%20Feedback/mockups/uiux-feedback-v1.html)

#### Acceptance Criteria

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-A.1 | UI/UX Feedback view accessible from Workplace sub-menu | Must |
| AC-A.2 | 3-column layout: sidebar, browser simulator, feedback panel (empty initially) | Must |
| AC-A.3 | Browser simulator with URL bar (text input + "Go" button) | Must |
| AC-A.4 | Backend proxy route: `GET /api/proxy?url=<localhost-url>` | Must |
| AC-A.5 | Proxy only accepts 127.0.0.1 and localhost targets | Must |
| AC-A.6 | Proxy fetches HTML and returns to frontend | Must |
| AC-A.7 | Proxy handles relative asset paths (CSS, JS, images) | Must |
| AC-A.8 | Simulator viewport responsive to panel size | Must |
| AC-A.9 | Refresh button in toolbar | Must |
| AC-A.10 | Loading indicator while page loads | Should |
| AC-A.11 | Block external URLs with clear error message | Must |
| AC-A.12 | Show "Connection refused" error when dev server not running | Must |

#### Dependencies

- **FEATURE-008 (Workplace):** Required for sub-menu integration

#### Technical Considerations

- Proxy must strip/modify CSP headers to allow inspection
- Consider URL rewriting for relative paths in proxied content
- Use iframe with srcdoc for rendering proxied HTML

---

### FEATURE-022-B: Element Inspector

**Version:** v1.0  
**Brief Description:** Hover highlighting and multi-select element inspection capability within the browser simulator, allowing users to identify and select UI elements for feedback.

#### Acceptance Criteria

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-B.1 | "Inspect" toggle button in toolbar | Must |
| AC-B.2 | Hovering elements shows highlight border (blue/orange) | Must |
| AC-B.3 | Tooltip shows element tag (e.g., `<button.submit>`) | Must |
| AC-B.4 | Click element to select (persistent highlight) | Must |
| AC-B.5 | Ctrl/Cmd + click for multi-select | Must |
| AC-B.6 | Click elsewhere clears selection | Must |
| AC-B.7 | Toolbar shows selected element count | Should |
| AC-B.8 | "Select All" button for visible elements | Could |

#### Dependencies

- **FEATURE-022-A:** Requires browser simulator to be loaded

#### Technical Considerations

- Inject inspector script via proxy
- Use CSS outline for non-intrusive highlighting
- Store selected elements as CSS selectors array

---

### FEATURE-022-C: Feedback Capture & Panel

**Version:** v1.0  
**Brief Description:** Right-click context menu for initiating feedback capture and a feedback entry panel showing pending feedback items with screenshot thumbnails.

#### Acceptance Criteria

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-C.1 | Right-click on selected element(s) shows context menu | Must |
| AC-C.2 | Menu option: "Provide Feedback" (element info only) | Must |
| AC-C.3 | Menu option: "Provide Feedback with Screenshot" | Must |
| AC-C.4 | Screenshot crops to selected element(s) bounding box | Must |
| AC-C.5 | Use html2canvas or equivalent for screenshot | Should |
| AC-C.6 | Feedback panel shows expandable entry list | Must |
| AC-C.7 | Entry name auto-generates: `Feedback-YYYYMMDD-HHMMSS` | Must |
| AC-C.8 | Entry displays: URL, selected elements list | Must |
| AC-C.9 | Entry displays screenshot thumbnail (if captured) | Must |
| AC-C.10 | Entry has text area for feedback description | Must |
| AC-C.11 | Entry has Delete button | Must |
| AC-C.12 | Entry has Submit button | Must |
| AC-C.13 | New entry auto-expands and receives focus | Must |
| AC-C.14 | Context menu disabled when no elements selected | Must |

#### Dependencies

- **FEATURE-022-B:** Requires element selection capability

#### Technical Considerations

- html2canvas may have cross-origin limitations
- Consider fallback to full-page screenshot if element capture fails
- Store feedback entries in memory until submitted

---

### FEATURE-022-D: Feedback Storage & Submission

**Version:** v1.0  
**Brief Description:** Backend API for saving feedback to structured folder format and frontend workflow for submission with terminal command generation.

#### Acceptance Criteria

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-D.1 | Backend route: `POST /api/uiux-feedback` | Must |
| AC-D.2 | Creates folder: `{project_root}/x-ipe/uiux-feedback/{entry-name}/` | Must |
| AC-D.3 | Saves `feedback.md` with structured content | Must |
| AC-D.4 | Saves `page-screenshot.png` if screenshot captured | Must |
| AC-D.5 | On success: toast notification "Saved" | Must |
| AC-D.6 | On success: entry status changes to "Reported" | Must |
| AC-D.7 | On success: terminal command typed (not executed) | Must |
| AC-D.8 | On failure: entry status "Failed" with error | Must |
| AC-D.9 | Clear element selection after successful submit | Must |
| AC-D.10 | Handle duplicate entry names (append suffix) | Must |
| AC-D.11 | Allow submit with empty feedback text | Must |
| AC-D.12 | Allow submit if screenshot capture failed | Must |

**Terminal Command Format:**
```
Get uiux feedback, please visit feedback folder x-ipe/uiux-feedback/Feedback-YYYYMMDD-HHMMSS to get details.
```

**Feedback.md Template:**
```markdown
# UI/UX Feedback

**ID:** Feedback-YYYYMMDD-HHMMSS
**URL:** http://localhost:3000/dashboard
**Date:** YYYY-MM-DD HH:MM:SS

## Selected Elements

- `<button.submit>` - Submit button in form
- `<div.form-group>` - Form container

## Feedback

{User's feedback text}

## Screenshot

![Screenshot](./page-screenshot.png)
```

#### Dependencies

- **FEATURE-022-C:** Requires feedback entries to submit

#### Technical Considerations

- Use configured project_root for storage path
- Terminal command injection via existing Console API
- Consider async file operations for large screenshots

---

## FEATURE-022 Summary

**UI/UX Feedback System** is broken down into 4 sequential features:

| Feature | Title | MVP? | Dependencies |
|---------|-------|------|--------------|
| FEATURE-022-A | Browser Simulator & Proxy | ✅ Yes | FEATURE-008 |
| FEATURE-022-B | Element Inspector | No | FEATURE-022-A |
| FEATURE-022-C | Feedback Capture & Panel | No | FEATURE-022-B |
| FEATURE-022-D | Feedback Storage & Submission | No | FEATURE-022-C |

**Total Acceptance Criteria:** 46 (across all sub-features)

---

## Dependencies (Part 3 Summary)

| Feature | Depends On | Reason |
|---------|------------|--------|
| FEATURE-021 | FEATURE-005 (Interactive Console) | Voice input requires existing console/terminal infrastructure |
| FEATURE-022-A | FEATURE-008 (Workplace) | Browser simulator is a Workplace sub-menu item |
| FEATURE-022-B | FEATURE-022-A | Inspector requires loaded browser simulator |
| FEATURE-022-C | FEATURE-022-B | Feedback capture requires element selection |
| FEATURE-022-D | FEATURE-022-C | Submission requires feedback entries |

---

*End of Part 3*
