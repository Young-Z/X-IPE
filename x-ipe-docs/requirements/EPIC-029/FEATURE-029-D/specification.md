# Feature Specification: Explorer UI Controls

> Feature ID: FEATURE-029-D
> Version: v1.1
> Status: Refined
> Last Updated: 03-16-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.1 | 03-16-2026 | CR-001: Added border toggle ACs (AC-19–AC-25) in GWT format, updated AC-9, added FR-8/FR-9, edge cases 7-9 | [CR-001](./CR-001.md) |
| v1.0 | 02-12-2026 | Initial specification | - |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Console Explorer v1 | HTML | [console-explorer-v1.html](x-ipe-docs/requirements/EPIC-029/mockups/console-explorer-v1.html) | Full explorer with resize handle, toggle, collapsed scenario | superseded by v2 |
| Console Explorer v2 | HTML | [console-explorer-v2.html](x-ipe-docs/requirements/EPIC-029/FEATURE-029-D/mockups/console-explorer-v2.html) | Border toggle: chevron on resize handle, visible handle when collapsed, click-to-toggle interaction | current (03-16-2026) |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".

## Overview

FEATURE-029-D adds interactive UI controls to the Console Session Explorer panel introduced in FEATURE-029-A. It provides a drag handle between the terminal content area and the explorer panel for resizing the panel width within a 160–360px range, and persists both the panel width and collapsed/expanded state in localStorage so the user's preference survives page reloads. Additionally, session name-to-UUID mappings are persisted so renamed sessions retain their identity across reloads.

The toggle button (already implemented in TASK-322) and collapsed state CSS (already implemented) are prerequisites. This feature focuses on the drag-to-resize interaction, localStorage persistence, and session identity persistence.

## User Stories

1. **US-1:** As a developer, I want to drag the explorer panel border to resize it, so that I can allocate more or less screen space to the session list.
2. **US-2:** As a developer, I want my explorer panel width to persist across page reloads, so that I don't have to resize it every time.
3. **US-3:** As a developer, I want my explorer collapsed/expanded preference to persist, so the panel stays in my preferred state.
4. **US-4:** As a developer, I want my session names to persist across page reloads, so I don't lose renamed sessions.
5. **US-5:** As a developer, I want to click the border between the terminal and explorer to toggle the panel, so I can quickly expand or collapse it without finding the header button. *(Added by CR-001)*

## Acceptance Criteria

### Toggle & Collapse (partially implemented)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-1 | GIVEN user is viewing the terminal panel WHEN user clicks the toggle button in the terminal header THEN the explorer panel collapses or expands with a CSS transition | UI |
| AC-2 | GIVEN user has collapsed the explorer panel WHEN the collapse transition completes THEN explorer width is 0, visibility is hidden, AND terminal content takes full width | UI |

### Drag-to-Resize

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-3 | GIVEN terminal panel is open with explorer expanded WHEN user views the area between terminal content and explorer panel THEN a vertical drag handle (5px wide) is visible | UI |
| AC-4 | GIVEN explorer panel is expanded AND user is dragging the resize handle WHEN user drags left THEN explorer width increases AND WHEN user drags right THEN explorer width decreases | UI |
| AC-5 | GIVEN user is dragging the resize handle WHEN explorer width would exceed 360px or fall below 160px THEN the width is clamped to the range 160–360px | Unit |
| AC-6 | GIVEN explorer panel is expanded WHEN user hovers over the drag handle THEN cursor changes to `col-resize` | UI |
| AC-7 | GIVEN explorer panel is expanded WHEN user hovers over the drag handle THEN handle highlights with a subtle accent color | UI |
| AC-8 | GIVEN user has been dragging the resize handle WHEN user releases the mouse (mouseup) THEN terminal content re-fits via xterm FitAddon | Integration |
| AC-9 | GIVEN explorer panel is collapsed WHEN user views the resize handle area THEN the handle remains visible as a thin clickable strip (5px wide) with a chevron indicator (`›`) pointing toward the collapsed panel AND drag-to-resize is disabled (mousemove during drag has no effect). *[Updated by CR-001: was "hidden when collapsed"]* | UI |

### Persistence

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-10 | GIVEN user has finished resizing the explorer panel WHEN mouseup fires after drag THEN the new width is saved to `localStorage` key `console_explorer_width` | Unit |
| AC-11 | GIVEN user toggles the explorer panel (collapse or expand) WHEN the toggle action completes THEN the collapsed/expanded state is saved to `localStorage` key `console_explorer_collapsed` | Unit |
| AC-12 | GIVEN `localStorage` contains a value for `console_explorer_width` WHEN the page loads THEN the explorer width is restored from that value (default 220px if absent) | Unit |
| AC-13 | GIVEN `localStorage` contains a value for `console_explorer_collapsed` WHEN the page loads THEN the explorer collapsed state is restored (default expanded if absent) | Unit |
| AC-14 | GIVEN no `localStorage` value exists for `console_explorer_width` WHEN the page loads THEN the explorer panel starts at 220px default width | Unit |

### Session Identity Persistence

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-15 | GIVEN user has renamed a session WHEN the name is saved THEN session names are stored in `localStorage` key `console_session_names` as a JSON map of UUID → name | Unit |
| AC-16 | GIVEN `localStorage` contains saved session names WHEN the page loads THEN restored sessions use saved names instead of defaults | Integration |

### Mockup Compliance

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-17 | GIVEN terminal panel is rendered WHEN user views the resize handle THEN its visual styling matches the mockup (console-explorer-v2.html): 5px width, subtle border color, accent highlight on hover, chevron indicator | UI |
| AC-18 | GIVEN user triggers a collapse or expand WHEN the CSS transition runs THEN it matches the mockup: width→0 with 0.25s ease transition | UI |

### Border Toggle (added by CR-001)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-19 | GIVEN explorer panel is expanded AND user presses mousedown on resize handle AND releases mouseup without moving mouse more than 3px WHEN mouseup event fires THEN explorer panel collapses with CSS transition (same as header toggle) | UI |
| AC-20 | GIVEN explorer panel is collapsed WHEN user clicks the visible handle strip THEN explorer panel expands to its previously stored width from localStorage | UI |
| AC-21 | GIVEN explorer panel is expanded WHEN user clicks the resize handle without dragging (movement < 3px) THEN explorer panel collapses to width 0 with visibility hidden | UI |
| AC-22 | GIVEN explorer panel is expanded WHEN user views the resize handle THEN a `‹` chevron indicator is displayed on the handle AND GIVEN explorer panel is collapsed WHEN user views the handle strip THEN a `›` chevron indicator is displayed | UI |
| AC-23 | GIVEN user clicks the border toggle to expand or collapse WHEN the transition completes THEN the collapsed state is persisted to localStorage key `console_explorer_collapsed` identically to the header button toggle | Unit |
| AC-24 | GIVEN user presses mousedown on resize handle AND drags mouse more than 3px WHEN mouseup fires THEN the explorer is resized (not toggled) — existing drag behavior is preserved unchanged | UI |
| AC-25 | GIVEN explorer panel was collapsed AND page reloads WHEN terminal panel is opened THEN the resize handle shows as a thin visible strip with `›` chevron indicator (not hidden) | UI |

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
| FR-8 | **Border Toggle (CR-001):** On mousedown, record cursor start position. On mouseup, if total cursor movement < 3px, call `toggleExplorer()`. If movement ≥ 3px, treat as drag (existing behavior). When collapsed, the resize handle remains visible (not `display: none`) and shows a chevron indicator (`›`). When expanded, the chevron shows `‹`. Clicking the handle when collapsed expands; clicking when expanded collapses. |
| FR-9 | **Visible Handle When Collapsed (CR-001):** Instead of hiding the resize handle when explorer is collapsed, keep it visible as a thin 5px-wide strip. Disable drag-to-resize when collapsed — only click-to-expand is active. On expand, re-enable drag-to-resize. |

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

### Collapsed State (from mockup, updated by CR-001)
- Width transitions to 0 with `0.25s ease`
- `visibility: hidden` after transition (explorer panel only; resize handle stays visible)
- Border-left removed when collapsed
- Drag handle remains visible as a thin clickable strip with chevron indicator (`›`)
- Drag-to-resize disabled when collapsed; click-to-expand enabled

### User Flow: Resize
1. User hovers over drag handle → handle highlights
2. User mousedowns → drag begins, body cursor becomes `col-resize`, user-select disabled
3. User drags left/right → explorer width updates in real-time (clamped)
4. User mouseups → drag ends, width saved to localStorage, terminal re-fits

### User Flow: Toggle
1. User clicks toggle button → explorer collapses/expands with transition
2. State saved to localStorage
3. Terminal content re-fits after transition completes

### User Flow: Border Toggle (added by CR-001)
1. User clicks on the resize handle (without dragging) → explorer collapses/expands with transition
2. If collapsed: handle shows `›` chevron, clicking expands to previous width
3. If expanded: handle shows `‹` chevron, clicking collapses panel
4. State saved to localStorage (same as header toggle)
5. Terminal content re-fits after transition completes

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
| 7 | Click on handle during collapse/expand animation (CR-001) | Ignore click — do not toggle again until current transition completes (300ms guard) |
| 8 | Very fast mousedown→drag→mouseup under 3px (CR-001) | Treat as click (toggle), not drag — threshold is on total movement distance |
| 9 | Touch device tap on handle (CR-001) | Treat touch tap as click — toggle explorer (touchstart→touchend without touchmove) |

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
