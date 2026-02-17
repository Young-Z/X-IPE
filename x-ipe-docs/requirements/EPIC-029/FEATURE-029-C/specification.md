# FEATURE-029-C: Session Hover Preview — Specification

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-02-12 | Spark | Initial specification |

## Linked Mockups

| Mockup | Status | Path |
|--------|--------|------|
| Console Explorer v1 (Hover Preview scenario) | current | mockups/console-explorer-v1.html |

## Overview

When a user hovers over a non-active session bar in the Session Explorer for 0.5 seconds, a live read-only mini-terminal preview modal appears. This allows quick inspection of background session output without switching away from the current session. The preview shows the session's terminal buffer content and updates in real-time as new output arrives.

## User Stories

1. **As a developer**, I want to hover over a background session to see its output, so I can monitor long-running processes without switching sessions.
2. **As a developer**, I want to click the preview to switch to that session, so I can quickly jump to a session that needs attention.
3. **As a developer**, I want the preview to dismiss naturally when I move away, so it doesn't block my workflow.

## Acceptance Criteria

| ID | Criterion | Priority |
|----|-----------|----------|
| AC-C.1 | Hovering a non-active session bar for 500ms shows a live preview modal positioned to the left of the explorer panel | P0 |
| AC-C.2 | Preview modal displays a read-only xterm.js terminal showing the session's current buffer content | P0 |
| AC-C.3 | Preview terminal auto-updates with new output from the session's socket in real-time | P0 |
| AC-C.4 | Hover zone includes both session bar and preview modal as a connected area | P0 |
| AC-C.5 | Moving cursor outside both session bar and preview modal dismisses the preview | P0 |
| AC-C.6 | 100ms grace period on hover jitter between session bar and preview modal | P1 |
| AC-C.7 | Clicking inside the preview switches to that session and dismisses the preview | P1 |
| AC-C.8 | Preview modal size defaults to 50% width × 60% height of the terminal panel | P1 |
| AC-C.9 | Hovering over the active session bar does NOT show a preview | P1 |
| AC-C.10 | UI layout MUST match the approved mockup (console-explorer-v1.html) for hover preview scenario | P2 |

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-C.1 | Preview is triggered by a 500ms hover delay on non-active session bars only |
| FR-C.2 | Preview creates a lightweight read-only xterm.js Terminal instance |
| FR-C.3 | Preview terminal is populated by reading the source session's buffer via buffer.active.getLine() |
| FR-C.4 | Preview terminal receives live output by tapping into the source session's socket output event |
| FR-C.5 | Preview is dismissed when cursor leaves both session bar and preview modal for >100ms |
| FR-C.6 | Clicking the preview triggers session switch and dismisses preview |
| FR-C.7 | Only one preview can be visible at a time |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-C.1 | Preview terminal must not capture keyboard input (read-only, disableStdin: true) |
| NFR-C.2 | Preview must not cause additional socket connections or backend requests |
| NFR-C.3 | Preview creation and dismissal must be smooth (<50ms perceived latency) |
| NFR-C.4 | Preview terminal disposal must clean up DOM and xterm.js resources |

## UI/UX Requirements

- Preview modal appears to the left of the session explorer panel
- Dark background (#1e1e1e) matching terminal aesthetic
- Subtle border (accent color, e.g. #4ec9b0)
- Preview header shows session name
- Terminal content scrolled to bottom (shows latest output)
- Semi-transparent backdrop or shadow to visually separate from main terminal

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| FEATURE-029-A: Session Explorer Core | Internal | Implemented |
| FEATURE-029-B: Session Actions | Internal | Implemented |

## Business Rules

1. Preview MUST NOT interfere with the active session's terminal input
2. Preview MUST NOT create additional server-side sessions
3. If a previewed session is deleted while preview is visible, preview must dismiss

## Edge Cases

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Hover over active session | No preview shown |
| Hover session then delete it before preview appears | Preview cancelled, no error |
| Rapid hover across multiple sessions | Only last hovered session shows preview |
| Session receives large output burst during preview | Preview updates without blocking UI |
| Previewed session deleted while preview visible | Preview dismisses immediately |

## Out of Scope

- Configurable preview size via .x-ipe.yaml (deferred for v1.0)
- Preview for disconnected sessions
- Resizable preview modal
- Preview in zen mode (explorer hidden)

## Technical Considerations

- xterm.js Terminal with `{ disableStdin: true, scrollback: 500 }` for preview
- Read source buffer via `buffer.active.getLine(i).translateToString()`
- Tap source socket output event with secondary listener for live updates
- mouseenter/mouseleave with setTimeout/clearTimeout for hover delay and grace period
- Preview container is a single reusable DOM element repositioned per hover
