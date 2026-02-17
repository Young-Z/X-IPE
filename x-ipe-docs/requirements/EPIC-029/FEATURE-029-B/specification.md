# Feature Specification: Session Actions

> Feature ID: FEATURE-029-B
> Version: v1.0
> Status: Refined
> Last Updated: 02-12-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-12-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Console Explorer v1 | HTML | [mockups/console-explorer-v1.html](mockups/console-explorer-v1.html) | Scenarios: Rename Session, Delete, 5 Sessions with action icons | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".

## Overview

FEATURE-029-B adds **Session Actions** to the Session Explorer panel — inline rename and delete operations for each session bar. This builds on FEATURE-029-A's core explorer by giving users the ability to customize session names and remove sessions they no longer need.

The feature addresses the need for session identity management. Developers running multiple processes (server, tests, logs) benefit from meaningful session names ("API Server", "Jest Tests") rather than generic "Session N" labels. Delete allows cleanup of finished processes without reloading the page.

The primary users are **developers** using the X-IPE console for multi-session workflows.

## User Stories

1. As a **developer**, I want to **rename a session by clicking an edit icon**, so that **I can label sessions with meaningful names like "API Server" or "Tests"**.

2. As a **developer**, I want to **delete a session by clicking a delete icon**, so that **I can clean up finished processes and free resources**.

3. As a **developer**, I want **the last session to be auto-recreated when deleted**, so that **the console always has at least one active session**.

4. As a **developer**, I want to **see a visual indicator for the active session**, so that **I can quickly identify which session I'm working in**.

## Acceptance Criteria

### AC-029-B.1: Rename Icon and Inline Editing
- [ ] Each session bar displays a rename icon (pencil/edit) on hover or always visible
- [ ] Clicking the rename icon converts the session name into an editable text input
- [ ] The text input is pre-filled with the current session name and auto-focused
- [ ] The text input width matches the available name area in the session bar
- [ ] UI layout MUST match the approved mockup (console-explorer-v1.html) for rename interaction

### AC-029-B.2: Rename Confirmation
- [ ] Pressing Enter confirms the rename and updates the session name
- [ ] Clicking outside the text input (blur) confirms the rename
- [ ] The renamed value is persisted in localStorage (`terminal_session_names`)
- [ ] Empty name input reverts to the previous name (no blank names allowed)
- [ ] Rename does not affect the PTY process or Socket.IO connection

### AC-029-B.3: Rename Cancel
- [ ] Pressing Escape cancels the rename and restores the original name
- [ ] The session bar returns to its normal (non-editing) state

### AC-029-B.4: Delete Icon and Session Removal
- [ ] Each session bar displays a delete icon (trash) on hover or always visible
- [ ] Clicking the delete icon immediately terminates the PTY session
- [ ] The Socket.IO connection for that session is closed
- [ ] The session bar is removed from the explorer list
- [ ] The xterm.js terminal instance is disposed
- [ ] No confirmation dialog is shown (per user decision in ideation)
- [ ] Interactive elements shown in mockup (console-explorer-v1.html) MUST be present and functional

### AC-029-B.5: Delete Last Session Auto-Recreate
- [ ] If the deleted session was the only session, a new "Session 1" is auto-created
- [ ] The auto-created session becomes the active session
- [ ] The explorer shows the new session with active indicator

### AC-029-B.6: Delete Active Session Handling
- [ ] If the deleted session was the active session, the next available session becomes active
- [ ] If no "next" session exists (was last in list), the previous session becomes active
- [ ] Terminal view switches to the new active session seamlessly

### AC-029-B.7: Session Limit Toast
- [ ] When session limit (10) is reached and user tries to create, a toast notification appears
- [ ] Toast message: "Maximum 10 sessions reached"
- [ ] Toast auto-dismisses after 2.5 seconds
- [ ] Toast does not block user interaction

### AC-029-B.8: Visual Status Indicators
- [ ] Active session bar has a green left accent border (#4ec9b0)
- [ ] Active session's status dot is green (#4ec9b0)
- [ ] Inactive session bars have dim/transparent border
- [ ] Inactive session's status dot is dim gray (#555)
- [ ] Visual styling (colors, spacing, typography) MUST be consistent with mockup (console-explorer-v1.html)

## Functional Requirements

### FR-029-B.1: Inline Rename

**Description:** Session bars support inline text editing for renaming.

**Details:**
- Input: User clicks rename icon on a session bar
- Process: Replace `.session-name` span with `<input type="text">`, pre-fill current name, focus input. Listen for Enter (confirm), Escape (cancel), blur (confirm). On confirm: update `session.name`, update bar display, save to localStorage. On cancel: restore original span.
- Output: Session name updated in UI and persisted

### FR-029-B.2: Session Deletion

**Description:** Session bars support one-click deletion with proper cleanup.

**Details:**
- Input: User clicks delete icon on a session bar
- Process: Call `TerminalManager.removeSession(key)` which handles: socket disconnect, terminal dispose, container removal, Map entry deletion, explorer bar removal, active session switch if needed, auto-recreate if last session.
- Output: Session fully removed, resources freed

### FR-029-B.3: Toast Notifications

**Description:** Toast messages for session limit and error conditions.

**Details:**
- Input: Session limit reached or PTY creation failure
- Process: Create toast element, show with slide-in animation, auto-dismiss after 2.5s
- Output: Non-blocking user feedback

### FR-029-B.4: Action Icons in Session Bar

**Description:** Each session bar shows rename and delete action buttons.

**Details:**
- Input: Session bar rendered in explorer
- Process: Append rename icon (pencil) and delete icon (trash) buttons to session bar. Icons use Bootstrap Icons classes. Icons positioned on right side of bar.
- Output: Clickable action icons per session bar

## Non-Functional Requirements

### NFR-029-B.1: Performance
- Rename operation MUST complete within 16ms (single frame — DOM swap only)
- Delete operation MUST complete within 100ms (includes socket disconnect + DOM removal)
- Toast show/hide MUST not cause layout shift on terminal area

### NFR-029-B.2: Accessibility
- Action icons MUST have `title` attributes for tooltip/screen reader support
- Text input for rename MUST be keyboard-navigable (Tab/Shift-Tab)
- Toast MUST have `role="alert"` for screen readers

### NFR-029-B.3: Resilience
- Deleting a session with a dead PTY MUST not throw errors
- Renaming during a Socket.IO reconnect MUST not affect connection
- Rapid successive deletes MUST not cause race conditions

## UI/UX Requirements

### Session Bar Layout (with actions)

```
┌────────────────────────────────────────┐
│ ● Session Name                    ✎ 🗑 │
└────────────────────────────────────────┘
```

### Session Bar During Rename

```
┌────────────────────────────────────────┐
│ ● [  editable text input         ]  🗑 │
└────────────────────────────────────────┘
```

### UI Elements

| Element | Type | Location | Behavior |
|---------|------|----------|----------|
| Rename Icon | `<button>` | Right side of session bar | Pencil icon (`bi-pencil`). Triggers inline rename. |
| Delete Icon | `<button>` | Right side of session bar, after rename | Trash icon (`bi-trash`). Deletes session immediately. |
| Rename Input | `<input type="text">` | Replaces session name span | Auto-focused, pre-filled. Enter/blur = confirm, Esc = cancel. |
| Toast | `<div>` | Bottom-center of console panel | Auto-dismiss after 2.5s. Slide-in animation. |

### User Flows

**Flow 1: Rename Session**
1. User sees session bar with ✎ icon
2. Clicks ✎ — name span becomes text input
3. Types new name, presses Enter
4. Name updates, input reverts to span, localStorage updated

**Flow 2: Delete Session**
1. User clicks 🗑 icon on session bar
2. PTY terminated, socket closed, terminal disposed
3. Session bar removed from explorer
4. If was active: next session activated
5. If was last: new "Session 1" auto-created

**Flow 3: Session Limit Toast**
1. User has 10 sessions, "+" is disabled
2. Toast "Maximum 10 sessions reached" shown on add attempt
3. Toast slides in, displays 2.5s, slides out

### Empty & Error States

| State | Behavior |
|-------|----------|
| Rename to empty string | Revert to previous name |
| Rename to very long name | Text truncated with ellipsis in bar |
| Delete session with active process | Process killed, session removed |
| Delete last session | Auto-create "Session 1" |
| PTY creation failure on auto-recreate | Error toast shown |

## Dependencies

### Internal Dependencies
- **FEATURE-029-A (Required):** Session Explorer Core — provides `TerminalManager.removeSession()`, `SessionExplorer.addSessionBar()/removeSessionBar()`, `sessions` Map, `_saveSessionNames()` method

### External Dependencies
- **Bootstrap Icons:** Already loaded — provides `bi-pencil`, `bi-trash` icon classes

### File Dependencies

| File | Change Type | Description |
|------|-------------|-------------|
| `src/x_ipe/static/js/terminal.js` | Modify | Add rename logic to SessionExplorer, add action icons to session bars, add toast |
| `src/x_ipe/static/css/terminal.css` | Add | Styles for action icons, rename input, toast notifications |

## Business Rules

### BR-1: No Empty Names
**Rule:** Session names must be non-empty after trim. Empty or whitespace-only renames revert to the previous name.

### BR-2: No Confirmation on Delete
**Rule:** Delete is immediate with no confirmation dialog (per user decision during ideation). The auto-recreate on last deletion provides a safety net.

### BR-3: Name Persistence
**Rule:** Renamed session names persist in `localStorage['terminal_session_names']` as a JSON object `{sessionId: name}`. Names survive page reload.

## Edge Cases & Constraints

### Edge Case 1: Double-Click Rename Icon
**Scenario:** User double-clicks the rename icon rapidly.
**Expected:** Only one rename input shown. Subsequent clicks ignored while editing.

### Edge Case 2: Rename While Switching Sessions
**Scenario:** User starts rename on Session 1, then clicks Session 2 bar.
**Expected:** Rename on Session 1 is confirmed (blur event), Session 2 becomes active.

### Edge Case 3: Delete During Rename
**Scenario:** User is renaming a session and clicks its delete icon.
**Expected:** Session is deleted. Rename is abandoned (no save).

### Edge Case 4: Rapid Delete of Multiple Sessions
**Scenario:** User clicks delete on 5 sessions quickly.
**Expected:** Each session removed sequentially. No race conditions. Active session switches correctly. If all deleted, auto-recreate fires once.

### Edge Case 5: Delete Session That Lost Connection
**Scenario:** Session's Socket.IO connection died, user clicks delete.
**Expected:** Session removed from UI. Socket disconnect call is a no-op. No errors thrown.

### Constraints
- `removeSession()` already handles socket disconnect, terminal dispose, container removal, auto-recreate — reuse this method
- Session name changes are frontend-only; backend PTY has no concept of session names
- Icons must not increase session bar height

## Out of Scope

- Drag-to-reorder sessions — future enhancement
- Right-click context menu — future enhancement
- Keyboard shortcut for delete (Ctrl+W) — future enhancement
- Session duplication/cloning — future enhancement
- Batch delete — future enhancement

## Technical Considerations

- The `SessionExplorer.addSessionBar()` method needs to include rename and delete action buttons
- Rename uses a simple DOM swap: replace `.session-name` span with `<input>`, then swap back on confirm/cancel
- The `TerminalManager.removeSession(key)` method already exists and handles all cleanup logic
- Toast notification can be a simple `<div>` appended to the terminal panel, positioned via CSS
- Action icons should prevent event propagation to avoid triggering session switch when clicking rename/delete
- The `_saveSessionNames()` method already exists in TerminalManager for localStorage persistence

## Open Questions

None — all design decisions resolved during ideation (IDEA-021).
