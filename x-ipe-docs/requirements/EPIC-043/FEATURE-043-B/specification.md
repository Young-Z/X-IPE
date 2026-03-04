# Feature Specification: Breadcrumb Navigation & Visual Distinction

> Feature ID: FEATURE-043-B
> Epic ID: EPIC-043
> Version: v1.0
> Status: Refined
> Last Updated: 03-04-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-04-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| File Link Preview — Full Interactive | HTML | [mockups/file-link-preview-v1.html](x-ipe-docs/requirements/EPIC-043/FEATURE-043-B/mockups/file-link-preview-v1.html) | Scenarios ① (link distinction), ③ (breadcrumb nav) are primary references | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".

## Overview

FEATURE-043-B enhances the preview modal from FEATURE-043-A with two capabilities:

1. **Breadcrumb Navigation** — When a user clicks an internal link inside the preview modal, the modal navigates to the new file and maintains a breadcrumb trail. A "← Back" button and clickable breadcrumb entries let the user retrace their path. Navigation depth is capped at 5 levels.

2. **Visual Link Distinction** — Internal links (`x-ipe-docs/`, `.github/skills/`) receive visual styling to distinguish them from external links: a 📄 emoji prefix, dashed green underline, and "Open preview" tooltip on hover.

**Target users:** Developers following documentation chains across linked files, project managers reviewing cross-referenced specs.

## User Stories

1. **US-043-B.1:** As a developer viewing a file in the preview modal, I want to click an internal link within it and see the linked file replace the modal content, so I can follow documentation chains without opening multiple modals.

2. **US-043-B.2:** As a developer who has navigated 3 files deep in the preview modal, I want a "← Back" button and a breadcrumb trail, so I can return to any previously viewed file.

3. **US-043-B.3:** As a developer scanning a rendered markdown document, I want internal links to look visually different from external links, so I can tell at a glance which links will open a preview vs. navigate away.

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| FEATURE-043-A: Link Interception & Preview Modal | Hard | Closed |

## Functional Requirements

### FR-043-B.1: Breadcrumb Navigation Stack

The `LinkPreviewManager` maintains a navigation stack (array of `{path, title}` objects) tracking files opened within the same modal session.

- **FR-043-B.1.1:** When `open(path)` is called from a link click inside the modal, the current file is pushed onto the stack before loading the new file.
- **FR-043-B.1.2:** A "← Back" button in the modal header navigates to the previous file (pops the stack).
- **FR-043-B.1.3:** A breadcrumb bar below the header shows the full navigation path. Each entry (except the current file) is clickable.
- **FR-043-B.1.4:** Clicking a breadcrumb entry navigates to that file and truncates the stack at that position.
- **FR-043-B.1.5:** Stack depth is capped at 5 levels. At level 5, new internal links inside the modal are still clickable but replace the current entry (no push) and a tooltip warns "Maximum preview depth reached".
- **FR-043-B.1.6:** When the modal is closed (via close button, backdrop click, or Escape), the navigation stack is cleared.
- **FR-043-B.1.7:** The "← Back" button is hidden when the stack is empty (i.e., viewing the first file).

### FR-043-B.2: Visual Link Distinction

Internal links in rendered markdown receive visual styling to distinguish them from external links.

- **FR-043-B.2.1:** Links with `data-preview-path` attribute are styled with a dashed underline in Emerald-500 color (`#10b981`).
- **FR-043-B.2.2:** A 📄 emoji is prepended to the link text via CSS `::before` pseudo-element.
- **FR-043-B.2.3:** On hover, these links show `title="Open preview"` tooltip.
- **FR-043-B.2.4:** External links remain unstyled (no emoji, no dashed underline).
- **FR-043-B.2.5:** Links inside `<code>` or `<pre>` elements are excluded from visual distinction styling.

## Non-Functional Requirements

- **NFR-043-B.1:** Breadcrumb navigation must be smooth — no full-page reload, no modal flash.
- **NFR-043-B.2:** Visual distinction CSS must not conflict with existing `.markdown-body a` styles.
- **NFR-043-B.3:** Stack operations (push, pop, truncate) must be O(1) or O(n) where n ≤ 5.

## UI/UX Requirements

### Breadcrumb Bar (Mockup Scenario ③)

- Position: Below the modal header, above the content area
- Layout: Horizontal flex, left-aligned, with `›` separator between entries
- Current file: Bold, non-clickable
- Previous files: Regular weight, clickable, hover underline
- Back button: Left of breadcrumb bar, shows "←" arrow + "Back" text
- Overflow: Horizontal scroll with hidden scrollbar when breadcrumb is long
- On close: Breadcrumb and stack fully reset

### Visual Link Distinction (Mockup Scenario ①)

- 📄 emoji prefix: Via CSS `::before { content: '📄 '; font-size: 0.85em; }`
- Dashed underline: `border-bottom: 1px dashed rgba(16, 185, 129, 0.3)` on normal state
- Hover state: Underline opacity increases, `border-bottom: 1px dashed rgba(16, 185, 129, 0.6)`
- Color: Inherit from parent (no color override on the link text itself)
- Text decoration: `text-decoration: none` (replaced by border-bottom)

## Acceptance Criteria

### Breadcrumb Navigation

- **AC-043-B.1:** Clicking an internal link inside the preview modal replaces the modal content with the new file and adds a breadcrumb entry for the previous file.
- **AC-043-B.2:** The breadcrumb bar shows the full navigation path with `›` separators.
- **AC-043-B.3:** A "← Back" button appears when navigation stack has ≥ 1 entry, clicking it returns to the previous file.
- **AC-043-B.4:** Clicking a breadcrumb entry (not the current file) navigates to that file and truncates the stack.
- **AC-043-B.5:** Navigation depth is capped at 5 levels; at depth 5, new links replace current entry instead of pushing.
- **AC-043-B.6:** Closing the modal clears the navigation stack entirely.
- **AC-043-B.7:** The "← Back" button is hidden when viewing the first file (empty stack).

### Visual Link Distinction

- **AC-043-B.8:** Internal links (`data-preview-path`) display a 📄 emoji prefix.
- **AC-043-B.9:** Internal links have a dashed green underline (Emerald-500 based).
- **AC-043-B.10:** Hovering over an internal link shows "Open preview" tooltip.
- **AC-043-B.11:** External links (no `data-preview-path`) do NOT have the emoji, dashed underline, or tooltip.
- **AC-043-B.12:** Links inside `<code>` or `<pre>` blocks do NOT receive visual distinction styling.

### Non-Regression

- **AC-043-B.13:** FEATURE-043-A behavior is fully preserved: click opens modal, error states, loading spinner, close via button/Escape/backdrop.
- **AC-043-B.14:** Existing ContentRenderer, DeliverableViewer, and FolderBrowserModal functionality is unchanged.

## Technical Scope

- **Scope:** [Frontend]
- **Files to modify:**
  - `src/x_ipe/static/js/features/link-preview-manager.js` — add navigation stack, back button, breadcrumb rendering
  - `src/x_ipe/static/js/core/content-renderer.js` — add `title="Open preview"` to custom link renderer
  - `src/x_ipe/static/css/workflow.css` — add breadcrumb styles, visual distinction styles
- **No new files** expected (all changes extend existing FEATURE-043-A code)
- **No backend changes** needed
