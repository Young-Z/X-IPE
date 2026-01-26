# Feature Specification: Live Refresh

> Feature ID: FEATURE-004  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-19-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 01-19-2026 | Initial specification | - |

## Overview

The Live Refresh feature provides automatic content updates when the currently viewed file changes on disk. As AI agents modify documentation or code files, the browser automatically refreshes the content without requiring manual page reloads, ensuring human reviewers always see the latest version.

This feature leverages the existing file system monitoring infrastructure (watchdog library and WebSocket connection) established in FEATURE-001, extending it to emit content-specific change notifications. When a file being viewed is modified externally, the frontend receives a targeted notification and re-fetches the file content seamlessly.

The experience is designed to be non-intrusive: content updates smoothly, a subtle visual indicator confirms the refresh, and the user's scroll position is preserved when possible. Edge cases like file deletion or permission errors are handled gracefully with appropriate user feedback.

## User Stories

- As a **human reviewer**, I want to **see file content update automatically when AI agents modify it**, so that **I always view the latest version without manual refresh**.

- As a **human reviewer**, I want to **receive a visual indication when content is refreshed**, so that **I know the file has been updated**.

- As a **human reviewer**, I want to **preserve my scroll position after a refresh**, so that **I don't lose my place in long documents**.

- As a **human reviewer**, I want to **be notified if a file I'm viewing is deleted**, so that **I can navigate to another file**.

- As a **developer**, I want to **see code changes reflected immediately**, so that **I can verify AI-generated code in real-time**.

## Acceptance Criteria

- [ ] AC-1: Content viewer automatically refreshes when the currently viewed file is modified on disk
- [ ] AC-2: Refresh occurs within 2 seconds of file modification (including debounce)
- [ ] AC-3: A subtle visual indicator (e.g., fade animation, toast notification) confirms content was refreshed
- [ ] AC-4: User's scroll position is preserved after refresh (when content length allows)
- [ ] AC-5: If the currently viewed file is deleted, display a "File not found" message with navigation prompt
- [ ] AC-6: Rapid successive file changes are debounced (only last state is rendered)
- [ ] AC-7: Live refresh can be toggled on/off via UI control (default: on)
- [ ] AC-8: Refresh does not interrupt user if they are actively scrolling (brief delay)
- [ ] AC-9: Works for all supported file types (Markdown, code files, JSON, YAML, etc.)
- [ ] AC-10: WebSocket reconnection automatically restores live refresh capability
- [ ] AC-11: No full page reload required - only content area updates

## Functional Requirements

### FR-1: Content Change Detection

**Description:** Detect when the currently viewed file is modified on disk

**Details:**
- Input: File system modification events from watchdog (already monitored)
- Process: Compare modified file path against currently viewed file path
- Output: Emit `content_changed` WebSocket event if paths match

**WebSocket Event:**
```json
{
  "type": "content_changed",
  "path": "x-ipe-docs/planning/task-board.md",
  "action": "modified"
}
```

### FR-2: Content Re-fetch on Change

**Description:** Frontend automatically re-fetches file content when change is detected

**Details:**
- Input: `content_changed` WebSocket event with matching path
- Process: Call existing `/api/content/<path>` endpoint
- Output: Update rendered content in viewer area

**Sequence:**
1. WebSocket receives `content_changed` event
2. Compare event path to currently displayed file path
3. If match, fetch new content via existing API
4. Re-render content (Markdown → HTML, syntax highlighting, etc.)
5. Display refresh indicator

### FR-3: Visual Refresh Indicator

**Description:** Show subtle visual feedback when content is refreshed

**Details:**
- Input: Content refresh triggered
- Process: Display transient indicator
- Output: User sees confirmation that content was updated

**UI Options (pick one or combine):**
- Brief highlight/pulse animation on content area
- Small toast notification "Content updated" (auto-dismiss 2s)
- Subtle border flash or fade effect

### FR-4: Scroll Position Preservation

**Description:** Maintain user's scroll position after content refresh

**Details:**
- Input: Current scroll position before refresh
- Process: Store scroll position, re-render, restore position
- Output: User remains at same reading position

**Edge Cases:**
- If content shortened and scroll position invalid → scroll to bottom
- If content significantly changed → optionally scroll to top with indicator

### FR-5: File Deletion Handling

**Description:** Handle case when currently viewed file is deleted

**Details:**
- Input: `content_changed` event with `action: "deleted"`
- Process: Check if deleted file matches current view
- Output: Display "File not found" message with navigation options

**UI:**
```
┌─────────────────────────────────────┐
│  📄 File Not Found                   │
│                                      │
│  The file you were viewing has been  │
│  deleted or moved.                   │
│                                      │
│  [Browse Files] [Go to Home]         │
└─────────────────────────────────────┘
```

### FR-6: Live Refresh Toggle

**Description:** Allow users to enable/disable automatic refresh

**Details:**
- Input: User clicks toggle control
- Process: Enable/disable content change listener
- Output: Toggle state persisted in localStorage

**UI:** Small toggle switch in content header area
- Icon: 🔄 or sync icon
- States: "Auto-refresh ON" / "Auto-refresh OFF"
- Default: ON

## Non-Functional Requirements

### NFR-1: Performance

- Content refresh completes within 500ms of receiving WebSocket event
- No visible flicker during content update
- Debounce rapid changes: 100-200ms delay before refresh
- Memory: No memory leaks from WebSocket listeners

### NFR-2: Reliability

- WebSocket disconnection does not crash application
- Auto-reconnect with exponential backoff (already implemented)
- Graceful degradation: if WebSocket unavailable, feature silently disabled

### NFR-3: User Experience

- Refresh is non-disruptive (no modal dialogs, no jarring transitions)
- Works seamlessly with Markdown rendering, code highlighting, Mermaid diagrams
- Accessible: screen readers announce "Content updated" when refresh occurs

## Dependencies

### Internal Dependencies

- **FEATURE-001: Project Navigation** - Provides WebSocket infrastructure and FileWatcher
- **FEATURE-002: Content Viewer** - Provides content rendering and `/api/content/<path>` endpoint

### External Dependencies

- **watchdog** - Already installed, file system monitoring
- **Flask-SocketIO** - Already installed, WebSocket support
- **Socket.IO client** - Already included in frontend

## Technical Considerations

### Backend Changes

1. **Extend FileWatcher** to emit `content_changed` events (not just `structure_changed`)
2. **Track "active viewers"** - map session IDs to currently viewed file paths
3. **Targeted emission** - only emit to sessions viewing the changed file (optimization)

### Frontend Changes

1. **Listen for `content_changed`** WebSocket events
2. **Track current file path** in JavaScript state
3. **Implement refresh logic** with scroll preservation
4. **Add toggle UI** for live refresh control
5. **Add visual indicator** component

### WebSocket Event Flow

```
File modified on disk
        ↓
   watchdog detects
        ↓
   FileWatcher._emit_event()
        ↓
   socketio.emit('content_changed', {path, action})
        ↓
   Frontend socket.on('content_changed')
        ↓
   Compare path to currentFilePath
        ↓
   If match: fetch('/api/content/' + path)
        ↓
   Re-render content
        ↓
   Show indicator, restore scroll
```

## Edge Cases & Constraints

### Edge Case 1: Rapid File Modifications

**Scenario:** AI agent saves file multiple times per second during generation  
**Expected Behavior:** Debounce changes, only refresh with final content after 100-200ms of inactivity

### Edge Case 2: Binary File Opened

**Scenario:** User somehow views a binary file that gets modified  
**Expected Behavior:** Skip refresh for unsupported file types, or refresh with "Cannot display binary file" message

### Edge Case 3: Network Latency

**Scenario:** High latency causes old content to arrive after newer content  
**Expected Behavior:** Include timestamp or version in requests, discard stale responses

### Edge Case 4: Large File Changes

**Scenario:** Very large file (>1MB) modified  
**Expected Behavior:** Show loading indicator during fetch, consider streaming for very large files

### Edge Case 5: User Editing (Future)

**Scenario:** User is editing file (FEATURE-003) while external change occurs  
**Expected Behavior:** Live refresh disabled during edit mode, or show conflict warning

## Out of Scope

- Diff view showing what changed (planned for FEATURE-007: Git Integration)
- Collaborative editing / conflict resolution
- Change history / undo external changes
- Notifications for files NOT currently being viewed
- Mobile push notifications
- Offline support / service worker caching

## Open Questions

- [x] Q1: Should refresh interrupt active scrolling? → No, brief delay if user scrolling
- [x] Q2: Toast notification or subtle animation? → Both options acceptable, toast preferred
- [x] Q3: Persist toggle state? → Yes, in localStorage
- [ ] Q4: Rate limit for extremely rapid changes? → Debounce handles most cases

---

## Specification Quality Checklist

- [x] All acceptance criteria are testable
- [x] User stories provide clear value
- [x] Functional requirements are complete
- [x] Non-functional requirements defined
- [x] Dependencies clearly stated
- [x] Edge cases identified
- [x] Out of scope explicitly listed
