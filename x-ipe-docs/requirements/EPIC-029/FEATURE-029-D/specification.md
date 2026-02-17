# Feature Specification: Explorer UI Controls

> Feature ID: FEATURE-029-D
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
| Console Explorer | HTML | [mockups/console-explorer-v1.html](mockups/console-explorer-v1.html) | Full explorer with resize handle, toggle, collapsed scenario | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".

## Overview

FEATURE-029-D adds interactive UI controls to the Console Session Explorer panel introduced in FEATURE-029-A. It provides a drag handle between the terminal content area and the explorer panel for resizing the panel width within a 160–360px range, and persists both the panel width and collapsed/expanded state in localStorage so the user's preference survives page reloads. Additionally, session name-to-UUID mappings are persisted so renamed sessions retain their identity across reloads.

The toggle button (already implemented in TASK-322) and collapsed state CSS (already implemented) are prerequisites. This feature focuses on the drag-to-resize interaction, localStorage persistence, and session identity persistence.

## User Stories

1. **US-1:** As a developer, I want to drag the explorer panel border to resize it, so that I can allocate more or less screen space to the session list.
2. **US-2:** As a developer, I want my explorer panel width to persist across page reloads, so that I don't have to resize it every time.
3. **US-3:** As a developer, I want my explorer collapsed/expanded preference to persist, so the panel stays in my preferred state.
4. **US-4:** As a developer, I want my session names to persist across page reloads, so I don't lose renamed sessions.

## Acceptance Criteria

### Toggle & Collapse (partially implemented)

| AC ID | Criterion | Priority |
|-------|-----------|----------|
| AC-1 | Toggle button in terminal header collapses/expands explorer panel with CSS transition | P0 |
| AC-2 | When collapsed, explorer width is 0, visibility is hidden, and terminal content takes full width | P0 |

### Drag-to-Resize

| AC ID | Criterion | Priority |
|-------|-----------|----------|
| AC-3 | A vertical drag handle (5px wide) is visible between terminal content and explorer panel | P0 |
| AC-4 | Dragging the handle left increases explorer width; dragging right decreases it | P0 |
| AC-5 | Explorer width is clamped to the range 160–360px during drag | P0 |
| AC-6 | Drag handle shows `col-resize` cursor on hover | P1 |
| AC-7 | Drag handle highlights on hover (subtle accent color) | P1 |
| AC-8 | Terminal content re-fits (xterm FitAddon) after drag ends | P0 |
| AC-9 | Drag handle is hidden when explorer is collapsed | P1 |

### Persistence

| AC ID | Criterion | Priority |
|-------|-----------|----------|
| AC-10 | Explorer panel width is saved to `localStorage` key `console_explorer_width` after resize | P0 |
| AC-11 | Explorer collapsed/expanded state is saved to `localStorage` key `console_explorer_collapsed` after toggle | P0 |
| AC-12 | On page load, explorer width is restored from localStorage (default 220px if absent) | P0 |
| AC-13 | On page load, explorer collapsed state is restored from localStorage (default expanded if absent) | P0 |
| AC-14 | Explorer panel starts at 220px default width when no localStorage value exists | P0 |

### Session Identity Persistence

| AC ID | Criterion | Priority |
|-------|-----------|----------|
| AC-15 | Session names are stored in localStorage key `console_session_names` as a JSON map of UUID → name | P1 |
| AC-16 | On page load, if saved session names exist, restored sessions use saved names instead of defaults | P1 |

### Mockup Compliance

| AC ID | Criterion | Priority |
|-------|-----------|----------|
| AC-17 | Resize handle visual styling MUST match mockup (console-explorer-v1.html): 5px width, subtle border color, accent highlight on hover | P1 |
| AC-18 | Collapsed state transition MUST match mockup: width→0 with 0.25s ease transition | P1 |

## Functional Requirements

| FR ID | Requirement |
|-------|-------------|
| FR-1 | **Drag Handle:** A 5px-wide vertical handle element is rendered between `.terminal-content` and `.session-explorer` inside `.terminal-body`. It supports mousedown→mousemove→mouseup drag to resize the explorer. |
| FR-2 | **Width Clamping:** During drag, explorer width = `bodyRect.right - e.clientX`, clamped to `[160, 360]` px. |
| FR-3 | **Persistence – Width:** On mouseup after resize, save width to `localStorage.setItem('console_explorer_width', width)`. |
| FR-4 | **Persistence – Collapsed:** On toggle, save state to `localStorage.setItem('console_explorer_collapsed', collapsed)`. |
| FR-5 | **Restore on Load:** On `SessionExplorer` init, read localStorage values and apply width/collapsed state before first render. |
| FR-6 | **Session Name Persistence:** On rename, save `{uuid: name}` map to `localStorage.setItem('console_session_names', JSON.stringify(map))`. On load, restore names from map. |
| FR-7 | **Fit After Resize:** After drag ends, call `terminalManager.fitActive()` to re-fit the xterm terminal. |

## Non-Functional Requirements

| NFR ID | Requirement |
|--------|-------------|
| NFR-1 | Drag resize MUST feel smooth — no visible lag or jank (requestAnimationFrame or direct style update). |
| NFR-2 | localStorage operations MUST NOT block the UI thread (they are synchronous but fast). |
| NFR-3 | CSS transitions for collapse/expand MUST be 0.25s ease for smooth animation. |
| NFR-4 | All localStorage keys MUST be prefixed with `console_` namespace to avoid collisions. |

## UI/UX Requirements

### Resize Handle (from mockup)
- Width: 5px
- Background: subtle border color (`#21262d` in mockup, `#333` in current theme)
- Hover: accent dim highlight
- Pseudo-element: 2px × 24px centered indicator dot, visible on hover
- Cursor: `col-resize`

### Collapsed State (from mockup)
- Width transitions to 0 with `0.25s cubic-bezier(0.4, 0, 0.2, 1)`
- `visibility: hidden` after transition
- Border-left removed when collapsed
- Drag handle hidden when collapsed

### User Flow: Resize
1. User hovers over drag handle → handle highlights
2. User mousedowns → drag begins, body cursor becomes `col-resize`, user-select disabled
3. User drags left/right → explorer width updates in real-time (clamped)
4. User mouseups → drag ends, width saved to localStorage, terminal re-fits

### User Flow: Toggle
1. User clicks toggle button → explorer collapses/expands with transition
2. State saved to localStorage
3. Terminal content re-fits after transition completes

## Dependencies

### Internal
| Dependency | Type | Status |
|------------|------|--------|
| FEATURE-029-A | Session Explorer Core | ✅ Complete |
| TASK-322 | Toggle button + collapsed CSS | ✅ Complete |

### External
None.

## Business Rules

| BR ID | Rule |
|-------|------|
| BR-1 | Default explorer width is 220px. |
| BR-2 | Minimum explorer width is 160px; maximum is 360px. |
| BR-3 | When no localStorage values exist, explorer starts expanded at 220px. |
| BR-4 | Session names default to "Session N" (sequential) when no saved names exist. |

## Edge Cases & Constraints

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | localStorage is unavailable (private browsing) | Gracefully degrade — use defaults, no errors |
| 2 | Stored width outside valid range (e.g., manually edited) | Clamp to [160, 360] on load |
| 3 | Stored collapsed value is not a boolean | Default to expanded (false) |
| 4 | Browser window too narrow for explorer + terminal | Explorer still honors min-width; terminal compresses |
| 5 | Rapid toggle clicks during animation | Debounce or let CSS transition handle naturally |
| 6 | Session UUID in localStorage no longer exists on server | Ignore stale entries, use default name |

## Out of Scope

- Explorer panel resizable via keyboard (accessibility resize)
- Drag-to-reorder sessions within the explorer
- Multi-column explorer layout
- Server-side session name persistence (localStorage only)
- Explorer width responsive breakpoints

## Technical Considerations

- Drag handle should be a sibling element between `.terminal-content` and `.session-explorer` in the flex row
- Preview panel `right` offset needs to track explorer width dynamically during resize
- `fitActive()` should be called with a small delay after collapse transition to allow animation to complete
- Session UUID is the key used in `TerminalManager.sessions` Map

## Open Questions

None — all requirements are clear from the mockup and acceptance criteria.
