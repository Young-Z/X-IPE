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
| FEATURE-023-A | Application Action Tracing - Core | v1.0 | Decorator-based tracing framework for Python & TypeScript with log storage | None |
| FEATURE-023-B | Tracing Dashboard UI | v1.0 | Web UI for viewing and managing trace sessions | FEATURE-023-A |
| FEATURE-023-C | Trace Viewer & DAG Visualization | v1.0 | DAG-based call graph visualization with drill-down | FEATURE-023-B |
| FEATURE-023-D | Tracing Skill Integration | v1.0 | Auto-instrumentation skill for adding tracing to code | FEATURE-023-A |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| voice-input-console | FEATURE-021 | [mockup.html](../ideas/Console%20Voice%20Input%20-%2001242026%20000728/mockup.html) |
| uiux-feedback-view | FEATURE-022 | [uiux-feedback-v1.html](../ideas/005.%20Feature-UIUX%20Feedback/mockups/uiux-feedback-v1.html) |
| tracing-dashboard | FEATURE-023-B/C | [tracing-dashboard-v4.html](../ideas/007.%20Feature-Application%20Action%20Tracing/mockups/tracing-dashboard-v4.html) |

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
| FEATURE-023-A | None | Core infrastructure feature |
| FEATURE-023-B | FEATURE-023-A | Needs tracing API endpoints |
| FEATURE-023-C | FEATURE-023-B | Extends dashboard with visualization |
| FEATURE-023-D | FEATURE-023-A | Uses tracing decorators |

---

### FEATURE-023-A: Application Action Tracing - Core

**Version:** v1.0  
**Brief Description:** Decorator-based tracing framework for Python and TypeScript that automatically logs function calls, parameters, return values, and execution times with structured log files.

**Source:** [Idea Summary v1 - Application Action Tracing](../ideas/007.%20Feature-Application%20Action%20Tracing/idea-summary-v1.md)  
**Mockup:** [Tracing Dashboard v4](../ideas/007.%20Feature-Application%20Action%20Tracing/mockups/tracing-dashboard-v4.html)

#### Problem Statement

As applications grow in complexity, understanding execution flow becomes challenging:
- Debugging requires manually adding log statements
- No standardized way to trace function calls across the codebase
- Errors lack context about what led to the failure
- Code reviews cannot easily verify logging coverage
- Different developers implement logging inconsistently

#### Scope Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Phase Priority | Phase 1 (Core) first | Backend before UI |
| Language Support | Python + TypeScript together | Both from start |
| Log Storage | Configurable via tools.json | Flexibility |
| Trace Retention | Keep files, cleanup on reboot based on config (default 24h) | Balance storage vs utility |
| Error Logs | Same file with error markers | Simpler implementation |
| Sensitive Data | Built-in redaction patterns | Security by default |
| Decorator Config | level + redact fields | Basic but sufficient |
| Trace ID Format | UUID | Guaranteed unique |

#### Acceptance Criteria

**1. Python Tracing Decorator**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-1.1 | System MUST provide `@x_ipe_tracing` decorator in `x_ipe.tracing` module | Must |
| AC-1.2 | Decorator MUST accept `level` parameter with values: "INFO", "DEBUG", "SKIP" | Must |
| AC-1.3 | Decorator MUST accept optional `redact` parameter as list of field names to redact | Must |
| AC-1.4 | Decorator MUST log function entry with: function name, parameters (redacted as needed) | Must |
| AC-1.5 | Decorator MUST log function exit with: return value (redacted as needed), execution time in ms | Must |
| AC-1.6 | Decorator MUST log exceptions with: exception type, message, stack trace | Must |
| AC-1.7 | Decorator MUST work with sync and async functions | Must |
| AC-1.8 | Decorator SHOULD NOT significantly impact performance (<5ms overhead per call) | Should |

**2. TypeScript Tracing Decorator**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-2.1 | System MUST provide `@xIpeTracing` decorator in `@x-ipe/tracing` package | Must |
| AC-2.2 | Decorator MUST accept `level` option with values: "INFO", "DEBUG", "SKIP" | Must |
| AC-2.3 | Decorator MUST accept optional `redact` option as array of field names | Must |
| AC-2.4 | Decorator MUST log function entry with: function name, parameters (redacted) | Must |
| AC-2.5 | Decorator MUST log function exit with: return value (redacted), execution time | Must |
| AC-2.6 | Decorator MUST log exceptions with: error type, message, stack trace | Must |
| AC-2.7 | Decorator MUST work with sync and async methods | Must |
| AC-2.8 | Decorator MUST work with class methods and standalone functions | Must |

**3. Trace Context Management**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-3.1 | System MUST generate unique UUID trace ID for each root request | Must |
| AC-3.2 | System MUST propagate trace ID to all nested function calls within same request | Must |
| AC-3.3 | System MUST track parent-child relationships between function calls | Must |
| AC-3.4 | System MUST maintain call depth/nesting level for each function | Must |
| AC-3.5 | System MUST use in-memory buffer during request execution | Must |
| AC-3.6 | System MUST flush buffer to file on request completion | Must |

**4. Log Format & Storage**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-4.1 | Log file MUST be named: `{timestamp}-{root-api-name}-{trace-id}.log` | Must |
| AC-4.2 | Log file path MUST be configurable via `tools.json` field `tracing_log_path` | Must |
| AC-4.3 | Default log path MUST be `instance/traces/` | Must |
| AC-4.4 | Log format MUST include: `[TRACE-START]`, `[TRACE-END]`, `[INFO]`, `[DEBUG]`, `[ERROR]` markers | Must |
| AC-4.5 | Each log entry MUST include: timestamp, trace ID, function name, direction (→/←), data | Must |
| AC-4.6 | Error entries MUST be marked with `[ERROR]` in same file (not separate file) | Must |
| AC-4.7 | Log files older than retention period MUST be deleted on backend startup | Must |
| AC-4.8 | Retention period MUST be configurable via `tools.json` field `tracing_retention_hours` (default: 24) | Must |

**5. Sensitive Data Redaction**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-5.1 | System MUST auto-redact fields containing "password" (case-insensitive) | Must |
| AC-5.2 | System MUST auto-redact fields containing "secret" (case-insensitive) | Must |
| AC-5.3 | System MUST auto-redact fields containing "token" (case-insensitive) | Must |
| AC-5.4 | System MUST auto-redact fields containing "api_key" or "apiKey" | Must |
| AC-5.5 | System MUST redact values matching credit card pattern (16 digits) | Must |
| AC-5.6 | System MUST redact values matching JWT pattern (eyJ...) | Must |
| AC-5.7 | Redacted values MUST be replaced with `[REDACTED]` | Must |
| AC-5.8 | Custom redact fields from decorator MUST be honored in addition to built-in patterns | Must |

**6. Tracing Configuration (tools.json)**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-6.1 | `tools.json` MUST support `tracing_enabled` field (boolean, default: false) | Must |
| AC-6.2 | `tools.json` MUST support `tracing_stop_at` field (ISO timestamp or null) | Must |
| AC-6.3 | `tools.json` MUST support `tracing_log_path` field (string, default: "instance/traces/") | Must |
| AC-6.4 | `tools.json` MUST support `tracing_retention_hours` field (number, default: 24) | Must |
| AC-6.5 | `tools.json` MUST support `tracing_ignored_apis` field (array of API path patterns) | Should |
| AC-6.6 | Backend MUST check `tracing_stop_at` on each request; if now > stop_at, disable tracing | Must |
| AC-6.7 | Backend MUST cleanup old logs on startup based on `tracing_retention_hours` | Must |

**7. API Endpoints**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-7.1 | `GET /api/tracing/status` MUST return current tracing state (enabled, stop_at, retention) | Must |
| AC-7.2 | `POST /api/tracing/start` MUST accept `duration_minutes` (3, 15, or 30) and set `tracing_stop_at` | Must |
| AC-7.3 | `POST /api/tracing/stop` MUST set `tracing_stop_at` to null and disable tracing | Must |
| AC-7.4 | `GET /api/tracing/logs` MUST return list of trace log files with metadata | Should |
| AC-7.5 | `GET /api/tracing/logs/{trace_id}` MUST return parsed trace data for visualization | Should |
| AC-7.6 | `DELETE /api/tracing/logs` MUST delete all trace logs | Should |

#### Data Models

**Trace Log Entry:**
```
[{marker}] {direction} {function}: {function_name} | {description} | {data_json} | {duration_ms}
```

**Example Log File:**
```
[TRACE-START] 550e8400-e29b-41d4-a716-446655440000 | POST /api/orders | 2026-02-01T03:10:00Z
  [INFO] → start_function: validate_order | {"order_id": "O001", "items": [...]}
  [DEBUG] → start_function: check_inventory | {"item_ids": ["I1"]}
  [DEBUG] ← return_function: check_inventory | {"available": true} | 12ms
  [INFO] ← return_function: validate_order | {"valid": true} | 45ms
  [ERROR] → start_function: process_payment | {"amount": 99.99}
  [ERROR] ← exception: process_payment | PaymentError: Card declined | 230ms
    at process_payment (payment.py:42)
    at handle_order (orders.py:15)
[TRACE-END] 550e8400-e29b-41d4-a716-446655440000 | 287ms | ERROR
```

**tools.json Schema Addition:**
```json
{
  "tracing_enabled": false,
  "tracing_stop_at": "2026-02-01T03:30:00.000Z",
  "tracing_log_path": "instance/traces/",
  "tracing_retention_hours": 24,
  "tracing_ignored_apis": ["/api/health", "/api/ping"]
}
```

#### Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NFR-1 | Decorator overhead per call | < 5ms |
| NFR-2 | Memory buffer size limit | 10MB per request |
| NFR-3 | Log file write latency | < 50ms |
| NFR-4 | Startup cleanup time | < 5s for 1000 files |

#### Out of Scope (Phase 1)

- UI dashboard (Phase 2)
- Skill integration (Phase 3)
- Distributed tracing across services
- Real-time log streaming
- Log aggregation/analytics

#### Feature Dependencies

| Feature | Depends On | Reason |
|---------|------------|--------|
| FEATURE-023-A | None | Core infrastructure feature |
| FEATURE-023-B | FEATURE-023-A | Needs tracing API to display |
| FEATURE-023-C | FEATURE-023-B | Extends dashboard with visualization |
| FEATURE-023-D | FEATURE-023-A | Uses tracing decorators |

---

### FEATURE-023-B: Tracing Dashboard UI

**Version:** v1.0  
**Brief Description:** Web-based dashboard for viewing tracing status, managing trace sessions (start/stop), browsing trace logs, and monitoring active traces.

**Dependencies:** FEATURE-023-A  
**Mockup:** [Tracing Dashboard v4](../ideas/007.%20Feature-Application%20Action%20Tracing/mockups/tracing-dashboard-v4.html)  
**Full Specification:** [specification.md](FEATURE-023-B/specification.md)

#### Acceptance Criteria Summary

| Category | Count | Key Requirements |
|----------|-------|------------------|
| 1. Workplace Integration | 4 AC | Sidebar access, main content display, X-IPE design system |
| 2. Header Controls | 7 AC | Title, Config button, Ignored APIs, duration buttons (3/15/30 min) |
| 3. Countdown Timer | 8 AC | MM:SS format, live updates, color coding, stop button |
| 4. Trace Session Persistence | 5 AC | Persist across refresh via tools.json, resume countdown |
| 5. Trace List Sidebar | 9 AC | File list, sorting, filtering, selection highlight |
| 6. Config Modal | 6 AC | Log path, retention settings, save/cancel |
| 7. Ignored APIs Modal | 6 AC | Add/remove patterns, wildcard support |
| 8. API Integration | 5 AC | GET /status, POST /start, POST /stop endpoints |

**Total Acceptance Criteria:** ~50

---

### FEATURE-023-C: Trace Viewer & DAG Visualization

**Version:** v1.0  
**Brief Description:** Interactive DAG (Directed Acyclic Graph) visualization of traced function calls, showing call hierarchy, timing, and parameters with click-to-expand details.

**Dependencies:** FEATURE-023-B  
**Mockup:** [Tracing Dashboard v4](../ideas/007.%20Feature-Application%20Action%20Tracing/mockups/tracing-dashboard-v4.html)  
**Full Specification:** [specification.md](FEATURE-023-C/specification.md)

#### Acceptance Criteria Summary

| Category | Count | Key Requirements |
|----------|-------|------------------|
| 1. Trace Selection & Loading | 6 AC | Click to load, header with trace ID/status/stats |
| 2. DAG Graph Rendering | 6 AC | G6 library, dagre layout, auto-fit, empty state |
| 3. Trace Node Design | 8 AC | Function name, status dot, level badge, timing |
| 4. Edge Design | 5 AC | Polyline edges, arrows, gray color |
| 5. Node Detail Modal | 10 AC | Click-to-open, input/output JSON, error details |
| 6. Zoom/Pan Controls | 5 AC | Zoom buttons, drag pan, fit-to-view, wheel zoom |
| 7. Duration Toggle | 4 AC | Show/hide timing, persist preference |
| 8. Error Visualization | 5 AC | Red error nodes, stack trace display |
| 9. Log File Parsing | 7 AC | Parse TRACE-START/END, function calls, exceptions |
| 10. Performance | 4 AC | Handle 100+ nodes, lazy rendering, smooth zoom |

**Total Acceptance Criteria:** ~60

---

### FEATURE-023-D: Tracing Skill Integration

**Version:** v1.0  
**Brief Description:** AI skills for auto-instrumenting code with `@x_ipe_tracing` decorators and integrating tracing into existing X-IPE workflow skills.

**Dependencies:** FEATURE-023-A  
**Full Specification:** [specification.md](FEATURE-023-D/specification.md)

#### Acceptance Criteria Summary

| Category | Count | Key Requirements |
|----------|-------|------------------|
| 1. Skill Definition | 4 AC | SKILL.md at correct path, trigger patterns, procedure |
| 2. Code Analysis | 7 AC | Analyze files/modules, detect async, skip traced/private |
| 3. Level Assignment | 5 AC | INFO for public, DEBUG for utils, path-based rules |
| 4. Sensitive Param Detection | 5 AC | Detect password/token/secret/key, auto-redact |
| 5. Decorator Application | 5 AC | Correct syntax, add imports, preserve decorators |
| 6. Batch Operations | 4 AC | Multi-file, summary, exclusions, reporting |
| 7. Configuration Respect | 3 AC | Read tools.json, respect ignored APIs |
| 8. Skill Integration Updates | 25 AC | Update 5 existing skills with tracing checks |

**Skills Created:**
- `x-ipe-tool-tracing-instrumentation` - Add decorators to existing code
- `x-ipe-tool-tracing-creator` - Create tracing infrastructure for projects

**Skills Updated:**
- `x-ipe-task-based-code-implementation` - DoR/DoD tracing checks
- `x-ipe-task-based-test-generation` - Tracing test assertions
- `x-ipe-task-based-code-refactor` - Preserve tracing during refactor
- `x-ipe-task-based-refactoring-analysis` - Tracing as 5th quality dimension
- `x-ipe+feature+quality-board-management` - Tracing gap reporting

**Total Acceptance Criteria:** ~58

---

## FEATURE-023 Summary

**Application Action Tracing System** is broken down into 4 sequential features:

| Feature | Title | Status | Dependencies |
|---------|-------|--------|--------------|
| FEATURE-023-A | Application Action Tracing - Core | ✅ Completed | None |
| FEATURE-023-B | Tracing Dashboard UI | ✅ Completed | FEATURE-023-A |
| FEATURE-023-C | Trace Viewer & DAG Visualization | ✅ Completed | FEATURE-023-B |
| FEATURE-023-D | Tracing Skill Integration | ✅ Completed | FEATURE-023-A |

**Total Acceptance Criteria:** ~235 (across all sub-features)

---

*End of Part 3*
