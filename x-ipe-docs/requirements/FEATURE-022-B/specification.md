# Feature Specification: Element Inspector

> Feature ID: FEATURE-022-B  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-28-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 01-28-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description |
|--------|------|------|-------------|
| UI/UX Feedback View | HTML | [uiux-feedback-v1.html](../../ideas/005.%20Feature-UIUX%20Feedback/mockups/uiux-feedback-v1.html) | Shows inspect highlight, tooltip, and toolbar |

> **Note:** UI/UX requirements below are derived from the mockup's inspect functionality section.

---

## Overview

The Element Inspector feature provides hover highlighting and multi-select element inspection within the Browser Simulator viewport. When inspect mode is active, users can hover over DOM elements to see a highlight border and element tag tooltip, then click to select elements for feedback. Multiple elements can be selected using Ctrl/Cmd+click.

**This feature builds on FEATURE-022-A (Browser Simulator & Proxy)** which provides the localhost page viewing capability. The Element Inspector adds the ability to identify and select specific UI elements within that page.

**Key Value Proposition:**
- Visually identify UI elements by hovering
- See element tag/class information via tooltip
- Select single or multiple elements for feedback
- Non-intrusive highlighting (CSS outline, not affecting layout)

---

## User Stories

- As a **developer**, I want to **hover over elements to see them highlighted**, so that **I can visually identify which element I'm targeting**.

- As a **developer**, I want to **see the element tag and class in a tooltip**, so that **I understand which DOM element I'm inspecting**.

- As a **developer**, I want to **click to select an element**, so that **I can provide feedback on that specific element**.

- As a **developer**, I want to **Ctrl+click to select multiple elements**, so that **I can provide feedback on a group of related elements**.

- As a **developer**, I want to **see how many elements I have selected**, so that **I know the scope of my current selection**.

- As a **developer**, I want to **click elsewhere to clear my selection**, so that **I can start fresh when needed**.

---

## Acceptance Criteria

### Inspect Toggle

- [ ] AC-1: Toolbar displays "Inspect" toggle button with crosshair icon
- [ ] AC-2: Clicking "Inspect" toggles inspect mode on/off
- [ ] AC-3: "Inspect" button shows active state (highlighted) when enabled
- [ ] AC-4: Inspect mode persists until manually toggled off
- [ ] AC-5: Inspect mode is disabled by default when page loads

### Hover Highlighting

- [ ] AC-6: When inspect mode is ON, hovering an element shows blue highlight border
- [ ] AC-7: Highlight uses CSS outline (not border) to avoid layout shifts
- [ ] AC-8: Highlight color is blue (`#3b82f6` / info color)
- [ ] AC-9: Highlight has semi-transparent background overlay (`rgba(59, 130, 246, 0.08)`)
- [ ] AC-10: Highlight disappears immediately when cursor leaves element
- [ ] AC-11: Hovering does NOT affect elements when inspect mode is OFF

### Element Tooltip

- [ ] AC-12: Tooltip appears above hovered element showing element tag
- [ ] AC-13: Tooltip format: `<tagname.classname>` (e.g., `<a.sim-btn>`, `<div.header>`)
- [ ] AC-14: Tooltip has blue background matching highlight color
- [ ] AC-15: Tooltip uses monospace font for tag name
- [ ] AC-16: Tooltip follows element position (anchored to top-left of highlight)
- [ ] AC-17: If element has no class, show only tag: `<button>`
- [ ] AC-18: If element has multiple classes, show first class only: `<div.container>`

### Element Selection

- [ ] AC-19: Single click on element selects it (persistent highlight)
- [ ] AC-20: Selected element highlight uses different color (orange `#f59e0b` / warning color)
- [ ] AC-21: Clicking same element again deselects it
- [ ] AC-22: Ctrl+click (Cmd+click on Mac) adds element to selection (multi-select)
- [ ] AC-23: Clicking without Ctrl/Cmd replaces selection with new element
- [ ] AC-24: Clicking on empty area (not an element) clears all selections

### Selection Info

- [ ] AC-25: Toolbar shows selected element count: "N elements selected"
- [ ] AC-26: Count updates immediately when selection changes
- [ ] AC-27: Count shows "0 elements selected" or is hidden when nothing selected
- [ ] AC-28: Count text styled distinctly from buttons (lighter color)

### Select All (Nice-to-Have)

- [ ] AC-29: "Select All" button selects all visible elements in viewport
- [ ] AC-30: Select All excludes body, html, head, script, style elements
- [ ] AC-31: Select All is disabled when inspect mode is OFF

---

## Functional Requirements

### FR-1: Inspector Script Injection

**Description:** Inject inspector JavaScript into proxied pages to enable element tracking.

**Details:**
- Input: Proxied HTML content from FEATURE-022-A
- Process: Append inspector script to page via proxy rewrite
- Output: Page with inspect functionality enabled

### FR-2: Hover Detection

**Description:** Detect when cursor hovers over DOM elements and report to parent frame.

**Details:**
- Input: Mouse move events within iframe content
- Process: Identify deepest element under cursor, send postMessage to parent
- Output: Element info (tag, class, position) sent to parent frame

### FR-3: Highlight Rendering

**Description:** Render visual highlight overlay on hovered/selected elements.

**Details:**
- Input: Element position and dimensions from inspector script
- Process: Create/update overlay div positioned over element
- Output: Blue highlight for hover, orange for selected

### FR-4: Selection Management

**Description:** Track selected elements as CSS selector strings.

**Details:**
- Input: Click events with element info
- Process: Generate unique CSS selector for element, add/remove from selection array
- Output: Array of CSS selectors representing selected elements

### FR-5: Cross-Frame Communication

**Description:** Enable communication between parent page and iframe content.

**Details:**
- Input: postMessage events from iframe
- Process: Parse message type (hover, click, leave) and element data
- Output: Update UI state in parent frame

---

## Non-Functional Requirements

### NFR-1: Performance

- Hover detection latency: < 50ms
- Highlight render latency: < 16ms (one frame)
- No visible lag when moving cursor quickly

### NFR-2: Non-Intrusive

- Highlight MUST NOT cause layout reflow
- Highlight MUST NOT intercept click events intended for page
- Inspector script MUST NOT break page functionality

### NFR-3: Compatibility

- Works with any HTML page loaded via proxy
- Handles pages with shadow DOM (best effort)
- Handles dynamically loaded content

---

## UI/UX Requirements

### Toolbar Layout (from mockup)

```
[Refresh] | [Inspect ●] [Select All] | "2 elements selected"
```

- Inspect button: Active state with filled dot indicator
- Select All button: Standard button state
- Element count: Right-aligned, lighter text color

### Highlight Styling (from mockup)

```css
/* Hover highlight */
.inspect-highlight {
  border: 2px solid #3b82f6;          /* Blue border */
  background: rgba(59, 130, 246, 0.08); /* Light blue overlay */
  border-radius: 8px;
  pointer-events: none;
}

/* Selection highlight */
.inspect-selected {
  border: 2px solid #f59e0b;          /* Orange border */
  background: rgba(245, 158, 11, 0.08); /* Light orange overlay */
}
```

### Tooltip Styling (from mockup)

```css
.inspect-tag {
  background: #3b82f6;     /* Blue background */
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 500;
}
```

---

## Dependencies

### Internal Dependencies

- **FEATURE-022-A (Browser Simulator & Proxy):** Required - provides iframe with proxied content
- **Proxy HTML Rewriting:** Inspector script must be injected via proxy

### External Dependencies

- None (pure JavaScript implementation)

---

## Business Rules

### BR-1: Inspect Mode Required

**Rule:** Hover highlighting only works when inspect mode is toggled ON.

### BR-2: Single Selection Default

**Rule:** Clicking without modifier key replaces entire selection.

### BR-3: Multi-Select Modifier

**Rule:** Ctrl (Windows/Linux) or Cmd (Mac) enables multi-select mode.

### BR-4: Selection Persistence

**Rule:** Selected elements remain selected until explicitly deselected or cleared.

---

## Edge Cases & Constraints

### Edge Case 1: Element Removed from DOM

**Scenario:** User selects element, then page content changes (dynamic update)
**Expected Behavior:** Selection remains as CSS selector; highlight removed if element gone

### Edge Case 2: Overlapping Elements

**Scenario:** Multiple elements stacked at same position
**Expected Behavior:** Highlight deepest (most specific) element under cursor

### Edge Case 3: Fixed/Sticky Elements

**Scenario:** Hovering over position:fixed elements
**Expected Behavior:** Highlight follows element position correctly

### Edge Case 4: Scrollable Content

**Scenario:** User scrolls iframe content while hovering
**Expected Behavior:** Highlight updates position to follow element

### Edge Case 5: Iframe Navigation

**Scenario:** User loads new URL while elements are selected
**Expected Behavior:** Clear all selections when URL changes

---

## Out of Scope

- Element property inspection (computed styles, attributes) - future enhancement
- DOM tree view panel - future enhancement
- Element editing capabilities - not planned
- Cross-iframe element selection (nested iframes) - not supported

---

## Technical Considerations

- Use postMessage API for iframe ↔ parent communication
- Inject inspector script via proxy HTML rewriting (extend FEATURE-022-A)
- Use `element.getBoundingClientRect()` for position calculation
- Generate CSS selectors using tag, id, classes, nth-child as needed
- Consider using MutationObserver for dynamic content tracking

---

## Open Questions

- [x] Should tooltip show full class list or just first class? → First class only
- [x] What color for selected vs hovered? → Blue hover, orange selected (from mockup)
- [ ] Should Select All have a maximum element limit? → TBD during implementation

---
