# Requirement Details - Part 7

> Continuation of requirement documentation.
> See [requirement-details-index.md](requirement-details-index.md) for full index.

---

## FEATURE-029: Console Session Explorer

> Source: IDEA-021 (CR to FEATURE-005 Interactive Console)
> Status: Proposed
> Priority: High
> Mockup: [console-explorer-v1.html](../ideas/017.%20CR-Console%20Window%20Explorer/mockups/console-explorer-v1.html)

### Overview

Replace the current 2-pane split-terminal layout in the console window with a **Session Explorer** — a collapsible, resizable right-side panel that lists up to 10 independent terminal sessions. Only the selected session is visible in the main console area; all other sessions continue running in the background. Sessions can be created, renamed, deleted, and previewed via hover.

### User Request

The user wants to:
1. Click "+" to create terminal sessions (up to 10)
2. Show only the selected session in the console window; non-selected sessions run in background
3. Click a session in the session explorer to switch sessions
4. Edit session names via an edit icon on each session bar
5. Hover on a session bar for 0.5s to see a live preview modal of the console content

### Clarifications

| Question | Answer |
|----------|--------|
| Explorer panel position? | Right side, collapsible with toggle button, resizable via drag handle |
| Default session on load? | Auto-create 1 default session ("Session 1") |
| Session deletion behavior? | No confirmation dialog; if last session deleted, auto-create new one |
| Session bar icons? | Rename and delete only (no copy/duplicate) |
| Default session naming? | Sequential: "Session 1", "Session 2", ... |
| Preview modal content? | Live mini-terminal view (read-only, auto-updating) |
| Preview modal size? | Configurable in .x-ipe.yaml (default: 50% width × 60% height of console area) |
| Feature tracking? | New standalone FEATURE-029 (not sub-feature of FEATURE-005) |

### High-Level Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-029.1 | Session Explorer panel on right side of console window with session list | P0 |
| FR-029.2 | "+" button to create new terminal sessions (max 10 concurrent) | P0 |
| FR-029.3 | Single-session view — only selected session visible, others run in background | P0 |
| FR-029.4 | Click session bar to switch active session | P0 |
| FR-029.5 | Inline session rename via edit icon on each session bar | P1 |
| FR-029.6 | Session delete via delete icon — no confirmation, auto-create if last deleted | P1 |
| FR-029.7 | Hover preview — 0.5s delay shows live mini-terminal modal (read-only) | P1 |
| FR-029.8 | Collapsible explorer panel via toggle button in console header | P1 |
| FR-029.9 | Resizable explorer panel via drag handle | P2 |
| FR-029.10 | Auto-create 1 default session ("Session 1") on console load | P0 |
| FR-029.11 | Sequential default naming: "Session 1", "Session 2", ... | P1 |
| FR-029.12 | Session limit toast notification when 10/10 reached | P2 |
| FR-029.13 | Preview modal size configurable in .x-ipe.yaml (console.preview_size_percent) | P2 |

#### Acceptance Criteria

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-029.1 | Session Explorer panel renders on right side of console with session list | P0 |
| AC-029.2 | Clicking "+" creates a new PTY session with default name "Session N" | P0 |
| AC-029.3 | Maximum 10 sessions enforced; "+" shows toast at limit | P0 |
| AC-029.4 | Only the selected session's terminal is visible in console area | P0 |
| AC-029.5 | All non-selected sessions continue running with PTY processes alive | P0 |
| AC-029.6 | Clicking a session bar switches the active terminal view | P0 |
| AC-029.7 | Session switching preserves terminal output (no content loss) | P0 |
| AC-029.8 | Clicking rename icon enables inline text editing of session name | P1 |
| AC-029.9 | Pressing Enter or clicking away confirms the rename | P1 |
| AC-029.10 | Pressing Escape cancels the rename | P1 |
| AC-029.11 | Clicking delete icon immediately terminates PTY and removes session | P1 |
| AC-029.12 | Deleting last session auto-creates a new "Session 1" | P1 |
| AC-029.13 | Hovering a non-active session bar for 0.5s shows live preview modal | P1 |
| AC-029.14 | Preview modal displays read-only, auto-updating terminal output | P1 |
| AC-029.15 | Preview hover zone includes both session bar and modal (connected area) | P1 |
| AC-029.16 | Clicking inside preview switches to that session | P1 |
| AC-029.17 | Moving cursor outside both bar and modal dismisses preview | P1 |
| AC-029.18 | Toggle button in console header collapses/expands explorer panel | P1 |
| AC-029.19 | When collapsed, explorer is fully hidden and terminal takes full width | P1 |
| AC-029.20 | Drag handle resizes explorer panel width (range: 160–360px) | P2 |
| AC-029.21 | Explorer panel width persists in localStorage | P2 |
| AC-029.22 | Explorer collapsed/expanded state persists in localStorage | P2 |
| AC-029.23 | Session names map to session UUIDs and persist across page reloads | P2 |
| AC-029.24 | PTY creation failure shows error toast without affecting existing sessions | P2 |
| AC-029.25 | Console loads with explorer expanded and 1 auto-created session | P0 |
| AC-029.26 | All existing console functionality (WebSocket reconnection, buffer replay) preserved | P0 |
| AC-029.27 | Active session highlighted with visual indicator (green accent bar) | P1 |
| AC-029.28 | Session status dot shows green for active, dim for background | P2 |
| AC-029.29 | 100ms grace period on hover jitter between session bar and preview modal | P2 |
| AC-029.30 | Preview modal size defaults to 50% width × 60% height, configurable via .x-ipe.yaml | P2 |
| AC-029.31 | No side-by-side split-pane layout — single session view only | P0 |
| AC-029.32 | Explorer panel starts at 220px default width | P2 |

#### Non-Functional Requirements

| NFR ID | Description |
|--------|-------------|
| NFR-029.1 | Non-visible xterm.js instances stay mounted in DOM (CSS hide/show) to avoid re-render cost |
| NFR-029.2 | One Socket.IO connection per session (existing 1:1 pattern, no multiplexing) |
| NFR-029.3 | Max 100KB buffer memory (10 sessions × 10KB OutputBuffer each) |
| NFR-029.4 | Preview reads from OutputBuffer replay + live output stream (no backend changes for preview) |
| NFR-029.5 | All new code follows existing terminal.js and terminal_service.py patterns |

### Constraints

- **Breaking Change:** Replaces the split-pane layout entirely (FEATURE-005 Phase 3 split functionality deprecated)
- **Backend Minimal:** Backend `SessionManager` already supports N sessions; primary changes are frontend
- **xterm.js Limitation:** `Terminal.open()` is one-time — use CSS `display: none/block` instead of detach/reattach
- **OS Limits:** PTY creation can fail at scale; must handle gracefully
- **Config:** New `.x-ipe.yaml` section `console.preview_size_percent` (range: 20–80, default: 50)

### Out of Scope (v1)

- Keyboard shortcuts for session navigation (Ctrl+Tab, etc.)
- Drag-to-reorder sessions in the explorer
- Session grouping or tagging
- Split-pane view within a single session
- Session sharing or duplication

### Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-005 | Modifies (CR) | Replaces split-pane layout, raises session limit from 2 to 10. CR impact marker added to Part 1. |
| FEATURE-021 | Impacts | Console Voice Input references "focused terminal pane" — needs spec refactoring to "active session". CR impact marker added to Part 3. |
| terminal.js | File | Major refactor of TerminalManager class |
| terminal_service.py | File | Minor: raise MAX_TERMINALS constant |
| terminal_handlers.py | File | Minor: support preview_attach event |
| terminal.css | File | New styles for session explorer, preview modal |

### Related Features (Conflict Review)

| Feature | Decision | Rationale |
|---------|----------|-----------|
| FEATURE-005 (Interactive Console) | CR on FEATURE-005 | Same responsibility (terminal session mgmt), same UI area, same backend. FEATURE-029 extends and replaces split-pane model. |
| FEATURE-021 (Console Voice Input) | Mark for spec refactoring | Independent capability (speech API), but references "terminal pane" model that FEATURE-029 replaces. Needs terminology + UI placement updates. |

### Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-029-A | Session Explorer Core | v1.0 | Explorer panel UI, session create/switch, single-session view, auto-default session | FEATURE-005 |
| FEATURE-029-B | Session Actions | v1.0 | Inline rename, delete with auto-recreate, sequential naming, limit toast, visual indicators | FEATURE-029-A |
| FEATURE-029-C | Session Hover Preview | v1.0 | Live mini-terminal preview modal on hover with grace period, configurable size | FEATURE-029-A |
| FEATURE-029-D | Explorer UI Controls | v1.0 | Collapse/expand toggle, drag-to-resize, width/state persistence in localStorage | FEATURE-029-A |

### Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| Console Explorer — all scenarios | FEATURE-029-A to D | [console-explorer-v1.html](FEATURE-029-A/mockups/console-explorer-v1.html) |

---

## Feature Details

### FEATURE-029-A: Session Explorer Core

**Version:** v1.0
**Brief Description:** MVP — Session Explorer panel on right side of console with session list, create/switch sessions (up to 10), single-session view where only active session is visible.

**Acceptance Criteria:**
- [ ] AC-029.1: Session Explorer panel renders on right side of console with session list
- [ ] AC-029.2: Clicking "+" creates a new PTY session with default name "Session N"
- [ ] AC-029.3: Maximum 10 sessions enforced; "+" disabled at limit
- [ ] AC-029.4: Only the selected session's terminal is visible in console area
- [ ] AC-029.5: All non-selected sessions continue running with PTY processes alive
- [ ] AC-029.6: Clicking a session bar switches the active terminal view
- [ ] AC-029.7: Session switching preserves terminal output (no content loss)
- [ ] AC-029.25: Console loads with explorer expanded and 1 auto-created session
- [ ] AC-029.26: All existing console functionality (WebSocket reconnection, buffer replay) preserved
- [ ] AC-029.31: No side-by-side split-pane layout — single session view only

**Dependencies:**
- FEATURE-005: Extends existing console terminal infrastructure (CR — replaces split-pane model)

**Technical Considerations:**
- Non-visible xterm.js instances stay in DOM with CSS display:none/block (Terminal.open() is one-time)
- One Socket.IO connection per session (existing 1:1 pattern)
- Backend SessionManager already supports N sessions; raise MAX_TERMINALS to 10
- Must preserve WebSocket reconnection and buffer replay behavior

---

### FEATURE-029-B: Session Actions

**Version:** v1.0
**Brief Description:** Session bar actions: inline rename via edit icon, delete via delete icon with auto-recreate on last deletion, sequential naming, session limit toast, and visual status indicators.

**Acceptance Criteria:**
- [ ] AC-029.8: Clicking rename icon enables inline text editing of session name
- [ ] AC-029.9: Pressing Enter or clicking away confirms the rename
- [ ] AC-029.10: Pressing Escape cancels the rename
- [ ] AC-029.11: Clicking delete icon immediately terminates PTY and removes session
- [ ] AC-029.12: Deleting last session auto-creates a new "Session 1"
- [ ] AC-029.24: PTY creation failure shows error toast without affecting existing sessions
- [ ] AC-029.27: Active session highlighted with visual indicator (green accent bar)
- [ ] AC-029.28: Session status dot shows green for active, dim for background

**Dependencies:**
- FEATURE-029-A: Requires session explorer panel and session management core

**Technical Considerations:**
- Rename updates session name in frontend state and localStorage
- Delete must properly terminate PTY process and close Socket.IO connection
- Toast notification uses existing notification system

---

### FEATURE-029-C: Session Hover Preview

**Version:** v1.0
**Brief Description:** Hovering a non-active session bar for 0.5s shows a live read-only mini-terminal preview modal. Preview size configurable via .x-ipe.yaml.

**Acceptance Criteria:**
- [ ] AC-029.13: Hovering a non-active session bar for 0.5s shows live preview modal
- [ ] AC-029.14: Preview modal displays read-only, auto-updating terminal output
- [ ] AC-029.15: Preview hover zone includes both session bar and modal (connected area)
- [ ] AC-029.16: Clicking inside preview switches to that session
- [ ] AC-029.17: Moving cursor outside both bar and modal dismisses preview
- [ ] AC-029.29: 100ms grace period on hover jitter between session bar and preview modal
- [ ] AC-029.30: Preview modal size defaults to 50% width × 60% height, configurable via .x-ipe.yaml

**Dependencies:**
- FEATURE-029-A: Requires session explorer panel with session bars to hover over

**Technical Considerations:**
- Preview reads from OutputBuffer replay + live output stream (no backend changes for preview)
- Preview xterm.js instance is lightweight, read-only
- Hover zone = session bar + modal as connected area with 100ms grace period
- Config: .x-ipe.yaml → console.preview_size_percent (20-80, default 50)

---

### FEATURE-029-D: Explorer UI Controls

**Version:** v1.0
**Brief Description:** Explorer panel collapse/expand toggle button in console header, drag handle for resizing panel width (160-360px), and persistence of width/collapsed state in localStorage.

**Acceptance Criteria:**
- [ ] AC-029.18: Toggle button in console header collapses/expands explorer panel
- [ ] AC-029.19: When collapsed, explorer is fully hidden and terminal takes full width
- [ ] AC-029.20: Drag handle resizes explorer panel width (range: 160–360px)
- [ ] AC-029.21: Explorer panel width persists in localStorage
- [ ] AC-029.22: Explorer collapsed/expanded state persists in localStorage
- [ ] AC-029.23: Session names map to session UUIDs and persist across page reloads
- [ ] AC-029.32: Explorer panel starts at 220px default width

**Dependencies:**
- FEATURE-029-A: Requires explorer panel to collapse/resize

**Technical Considerations:**
- Collapse uses CSS width:0 + visibility:hidden with transition
- localStorage keys: console_explorer_width, console_explorer_collapsed
- Session UUID mapping stored in localStorage for reload persistence
