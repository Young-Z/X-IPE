# Requirement Details - Part 3

> Continued from: [requirement-details-part-2.md](requirement-details-part-2.md)  
> Created: 01-25-2026

---

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-021 | Console Voice Input | v1.0 | Push-to-talk voice input for terminal with Alibaba Cloud speech recognition | FEATURE-005 |
| FEATURE-022 | UI/UX Feedback System | v1.0 | Browser simulator with element inspector for capturing contextual UI/UX feedback | FEATURE-008 (Workplace) |

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

### FEATURE-022: UI/UX Feedback System

**Version:** v1.0  
**Brief Description:** An integrated UI/UX feedback tool within X-IPE Workplace that enables developers to browse web pages in a simulated browser environment, inspect HTML elements, and submit contextual feedback with screenshots—all without leaving the X-IPE interface.

**Source:** [Idea Summary v2 - UI/UX Feedback System](../ideas/005.%20Feature-UIUX%20Feedback/idea-summary-v2.md)  
**Mockup:** [UI/UX Feedback View Mockup](../ideas/005.%20Feature-UIUX%20Feedback/mockups/uiux-feedback-v1.html)

#### Problem Statement

Currently, providing UI/UX feedback requires:
- Switching between development environment and browser
- Taking manual screenshots
- Writing feedback in separate documents
- Losing context about which elements were being reviewed

This fragmented workflow slows down the feedback loop between design review and implementation.

#### Clarifications Summary

| Question | Answer |
|----------|--------|
| Device support? | Desktop only (mouse required for inspector) |
| Localhost proxy ports? | Allow any localhost port |
| Proxy security? | No auth needed - localhost targets only |
| Feedback storage location? | `x-ipe/uiux-feedback/` relative to configured project root |
| External URL support? | Localhost only for v1 (full DOM access) |
| Element selection after submit? | Clear selection (clean slate) |
| Terminal command execution? | Always wait for human to run command |

#### Acceptance Criteria

**1. Workplace Integration**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-1.1 | UI/UX Feedback view MUST be accessible from Workplace sub-menu | Must |
| AC-1.2 | View MUST use 3-column layout: sidebar, browser simulator, feedback panel | Must |
| AC-1.3 | View MUST integrate with existing Workplace navigation structure | Must |

**2. Browser Simulator**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-2.1 | Simulator MUST have URL bar with text input and "Go" button | Must |
| AC-2.2 | Simulator MUST support localhost URLs (127.0.0.1 and localhost) | Must |
| AC-2.3 | Simulator MUST allow any localhost port (e.g., :3000, :5173, :8080) | Must |
| AC-2.4 | Simulator viewport MUST be responsive to panel size | Must |
| AC-2.5 | Simulator MUST have Refresh button in toolbar | Must |
| AC-2.6 | External URLs (non-localhost) MUST be blocked with clear message | Must |
| AC-2.7 | Simulator MUST show loading indicator while page loads | Should |

**3. Localhost Proxy**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-3.1 | Backend MUST provide proxy route: `GET /api/proxy?url=<localhost-url>` | Must |
| AC-3.2 | Proxy MUST only accept 127.0.0.1 and localhost targets (security) | Must |
| AC-3.3 | Proxy MUST fetch HTML from target URL and return to frontend | Must |
| AC-3.4 | Proxy MUST inject inspector script into returned HTML | Must |
| AC-3.5 | Proxy MUST handle relative asset paths (CSS, JS, images) | Must |
| AC-3.6 | Proxy MUST NOT require authentication (localhost only) | Must |
| AC-3.7 | Proxy MUST return appropriate error for non-localhost URLs | Must |

**4. Element Inspector**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-4.1 | Inspector MUST be activated via "Inspect" toggle button in toolbar | Must |
| AC-4.2 | When active, hovering elements MUST show highlight border (blue/orange) | Must |
| AC-4.3 | Hovering MUST show tooltip with element tag (e.g., `<button.submit>`) | Must |
| AC-4.4 | Clicking element MUST select it (persistent highlight) | Must |
| AC-4.5 | Ctrl/Cmd + click MUST add element to selection (multi-select) | Must |
| AC-4.6 | Clicking elsewhere (non-element area) MUST clear selection | Must |
| AC-4.7 | Toolbar MUST show count of selected elements | Should |
| AC-4.8 | "Select All" button SHOULD select all visible elements | Could |

**5. Feedback Capture (Right-Click Menu)**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-5.1 | Right-click on selected element(s) MUST show context menu | Must |
| AC-5.2 | Menu MUST have "Provide Feedback" option (element info only) | Must |
| AC-5.3 | Menu MUST have "Provide Feedback with Screenshot" option | Must |
| AC-5.4 | Screenshot capture MUST crop to selected element(s) bounding box | Must |
| AC-5.5 | Screenshot capture SHOULD use html2canvas or equivalent library | Should |
| AC-5.6 | After capture, feedback entry MUST be created in feedback panel | Must |

**6. Feedback Entry Panel**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-6.1 | Panel MUST show list of feedback entries (expandable/collapsible) | Must |
| AC-6.2 | Entry name MUST auto-generate with timestamp: `Feedback-YYYYMMDD-HHMMSS` | Must |
| AC-6.3 | Entry MUST display: URL, selected elements list | Must |
| AC-6.4 | Entry MUST display screenshot thumbnail (if captured) | Must |
| AC-6.5 | Entry MUST have text area for feedback description | Must |
| AC-6.6 | Entry MUST have Delete button to remove entry | Must |
| AC-6.7 | Entry MUST have Submit button | Must |
| AC-6.8 | Newly created entry MUST auto-expand and receive focus | Must |

**7. Feedback Storage**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-7.1 | Feedback MUST be saved to: `{project_root}/x-ipe/uiux-feedback/{entry-name}/` | Must |
| AC-7.2 | Folder MUST contain `feedback.md` with structured content | Must |
| AC-7.3 | Folder MUST contain `page-screenshot.png` if screenshot captured | Must |
| AC-7.4 | `feedback.md` MUST include: ID, URL, date, elements, feedback text | Must |
| AC-7.5 | `feedback.md` MUST include relative link to screenshot if exists | Must |

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

**8. Submission Workflow**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-8.1 | Submit MUST call backend: `POST /api/uiux-feedback` | Must |
| AC-8.2 | Backend MUST create folder structure and save files | Must |
| AC-8.3 | On success, toast notification MUST show "Saved" | Must |
| AC-8.4 | On success, entry status MUST change to "Reported" | Must |
| AC-8.5 | On success, terminal command MUST be typed (not executed) | Must |
| AC-8.6 | On failure, entry status MUST change to "Failed" with error | Must |
| AC-8.7 | Selected elements MUST be cleared after successful submit | Must |

**Terminal Command (typed but NOT executed):**
```
Get uiux feedback, please visit feedback folder x-ipe/uiux-feedback/Feedback-YYYYMMDD-HHMMSS to get details.
```

**9. Error Handling**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-9.1 | Invalid URL format MUST show error in URL bar | Must |
| AC-9.2 | Non-localhost URL MUST show "Only localhost URLs supported" message | Must |
| AC-9.3 | Connection refused (dev server not running) MUST show clear error | Must |
| AC-9.4 | Screenshot capture failure MUST allow submit without screenshot | Must |
| AC-9.5 | Save failure MUST show error toast with reason | Must |

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | System SHALL provide browser simulator in Workplace sub-menu | Must |
| FR-2 | System SHALL proxy localhost URLs for full DOM access | Must |
| FR-3 | System SHALL provide element inspector with hover highlighting | Must |
| FR-4 | System SHALL support multi-select elements via Ctrl/Cmd+click | Must |
| FR-5 | System SHALL capture element screenshots on demand | Must |
| FR-6 | System SHALL save feedback to structured folder format | Must |
| FR-7 | System SHALL generate terminal command for agent processing | Must |
| FR-8 | System SHALL NOT auto-execute terminal commands | Must |

#### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Page load time (via proxy) | < 3 seconds for typical localhost page |
| NFR-2 | Screenshot capture time | < 2 seconds |
| NFR-3 | Inspector responsiveness | < 100ms highlight on hover |
| NFR-4 | Device support | Desktop only (mouse required) |
| NFR-5 | Browser support | Chrome, Firefox, Edge (latest) |

#### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| EC-1 | Dev server not running | Show "Connection refused" error, suggest starting server |
| EC-2 | Page has iframes | Inspector works on main document only (v1) |
| EC-3 | Page has shadow DOM | Best effort - may not inspect shadow roots |
| EC-4 | Very large page (many elements) | Performance may degrade - no specific handling v1 |
| EC-5 | Page uses CSP headers | Proxy strips restrictive CSP for inspection |
| EC-6 | No elements selected, right-click | Context menu disabled or hidden |
| EC-7 | Submit with empty feedback text | Allow submit (screenshot may be sufficient) |
| EC-8 | Duplicate entry names (same second) | Append suffix: `Feedback-YYYYMMDD-HHMMSS-2` |

#### Out of Scope (v1)

The following are explicitly out of scope for the initial version:

- Responsive/mobile view simulation
- Video recording of interactions
- Collaborative feedback (multiple users)
- Feedback status tracking (open/resolved)
- Integration with issue trackers (GitHub, Jira)
- Annotation drawing tools on screenshots
- External URL viewing (iframe mode)
- Tablet/touch device support

#### Dependencies

| Feature | Depends On | Reason |
|---------|------------|--------|
| FEATURE-022 | FEATURE-008 (Workplace) | UI/UX Feedback is a Workplace sub-menu item |

---

## Dependencies (Part 3 Summary)

| Feature | Depends On | Reason |
|---------|------------|--------|
| FEATURE-021 | FEATURE-005 (Interactive Console) | Voice input requires existing console/terminal infrastructure |
| FEATURE-022 | FEATURE-008 (Workplace) | UI/UX Feedback is a Workplace sub-menu item |

---

*End of Part 3*
