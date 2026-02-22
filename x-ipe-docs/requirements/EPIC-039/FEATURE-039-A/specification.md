# Feature Specification: Folder Browser Modal (MVP)

> Feature ID: FEATURE-039-A
> Version: v1.0
> Status: Refined
> Last Updated: 02-22-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-22-2026 | Initial specification — folder card styling, inline tree removal, modal with tree+preview |

## Linked Mockups

N/A — text-based idea summary, no visual mockup.

## Overview

This feature is a **Change Request on FEATURE-038-C** (Enhanced Deliverable Viewer). It replaces the current inline folder tree expansion with a dedicated **Folder Browser Modal** — a two-panel file explorer (tree + preview) that opens when a user clicks a folder-type deliverable card.

Additionally, folder deliverable cards receive a visually distinct background color to differentiate them from file-type cards at a glance.

The modal follows the same UX pattern as the `LinkExistingPanel` in the compose-idea-modal (tree on left, preview on right), providing a proven, consistent user experience without editing capabilities.

**Target Users:** Workflow users reviewing multi-file deliverable outputs (refined ideas, mockups, specifications).

## User Stories

- **US-039-A.1:** As a workflow user, I want folder cards to look different from file cards, so I can quickly identify which deliverables are folders.
- **US-039-A.2:** As a workflow user, I want to click a folder card and see its contents in a full-screen modal, so I have enough space to browse and preview files.
- **US-039-A.3:** As a workflow user, I want to preview markdown files as rendered HTML in the modal, so I can read formatted content without external tools.
- **US-039-A.4:** As a workflow user, I want the folder tree to load with a spinner, so I know the system is working while files are being fetched.

## Acceptance Criteria

### Folder Card Styling

- [ ] AC-039-A.1: Folder-type deliverable cards have a distinct background color different from file-type cards
- [ ] AC-039-A.2: Background color uses CSS variable `--deliverable-folder-bg` for themability
- [ ] AC-039-A.3: Non-folder deliverable cards are not affected (no regression)

### Inline Tree Removal

- [ ] AC-039-A.4: `_expandFolderTree()` method removed from deliverable-viewer.js
- [ ] AC-039-A.5: Expand/collapse toggle button (▸/▾) removed from folder card rendering
- [ ] AC-039-A.6: `.deliverable-tree` container and all nested tree CSS removed from workflow.css
- [ ] AC-039-A.7: `.deliverable-preview-backdrop` (inline preview overlay) removed
- [ ] AC-039-A.8: No dead CSS or JS remains from the inline tree implementation

### Modal Structure

- [ ] AC-039-A.9: Clicking a folder card opens a modal dialog with backdrop overlay
- [ ] AC-039-A.10: Modal width is 80vw, centered horizontally and vertically
- [ ] AC-039-A.11: Modal has a header with folder name and close button (✕)
- [ ] AC-039-A.12: Modal body has two panels: tree (left, 30%) and preview (right, 70%)

### Tree Panel

- [ ] AC-039-A.13: Tree fetches folder structure from `GET /api/workflow/{wf}/deliverables/tree?path={folder}`
- [ ] AC-039-A.14: Tree renders recursive folder structure with 📁 for folders and 📄 for files
- [ ] AC-039-A.15: Clicking a folder node expands/collapses its children
- [ ] AC-039-A.16: Clicking a file node loads its content in the preview panel
- [ ] AC-039-A.17: Selected file is visually highlighted in the tree

### Preview Panel

- [ ] AC-039-A.18: Preview fetches file content from `GET /api/ideas/file?path={file}`
- [ ] AC-039-A.19: Markdown files (`.md`) rendered as HTML via `marked.parse()`
- [ ] AC-039-A.20: Text/code files shown as preformatted text in `<pre>` element
- [ ] AC-039-A.21: Preview header shows the current file name
- [ ] AC-039-A.22: Only one file previewed at a time — selecting another replaces it

### Modal Lifecycle

- [ ] AC-039-A.23: Loading spinner shown while tree API call is in-flight
- [ ] AC-039-A.24: Modal closes via close button click
- [ ] AC-039-A.25: Modal closes via Escape key press
- [ ] AC-039-A.26: Modal closes via backdrop click (outside modal content)
- [ ] AC-039-A.27: When modal is open, background content does not scroll

## Functional Requirements

**FR-039-A.1: Folder Card Styling**
- Input: Deliverable item with folder-type path
- Process: Apply CSS class `.folder-type` with `--deliverable-folder-bg` variable
- Output: Folder card with distinct background; click handler opens modal instead of inline expansion

**FR-039-A.2: Inline Tree Code Removal**
- Input: Existing deliverable-viewer.js and workflow.css
- Process: Remove `_expandFolderTree()`, expand toggle rendering, `.deliverable-tree` DOM construction, `.deliverable-preview-backdrop`, and all related event listeners
- Output: Clean code with no dead inline tree artifacts

**FR-039-A.3: Modal Initialization**
- Input: Folder path from deliverable card click
- Process: Create `FolderBrowserModal` instance, set folder path, show backdrop + modal container, trigger tree load
- Output: Modal visible with loading spinner

**FR-039-A.4: Folder Tree Loading**
- Input: Folder path
- Process: Fetch `GET /api/workflow/{wf}/deliverables/tree?path={folder}`, parse JSON response, build recursive tree DOM (nested `<ul>/<li>`)
- Output: Tree panel populated with folder structure

**FR-039-A.5: File Preview Loading**
- Input: File path from tree item click
- Process: Fetch `GET /api/ideas/file?path={file}`, detect file type by extension, render: `.md` → `marked.parse()`, text/code → `<pre>`
- Output: Preview panel shows file content

**FR-039-A.6: Modal Close**
- Input: Close button click, Escape key, or backdrop click
- Process: Remove modal from DOM, remove backdrop, restore background scroll
- Output: Modal dismissed

## Non-Functional Requirements

- **NFR-039-A.1:** Tree render completes within 500ms for folders with up to 50 files
- **NFR-039-A.2:** File preview fetch and render completes within 1s for files up to 100KB
- **NFR-039-A.3:** No additional JS libraries — uses native DOM + existing marked.js
- **NFR-039-A.4:** Modal CSS uses CSS variables for theme compatibility

## UI/UX Requirements

### Components

| Component | Description | Behavior |
|-----------|-------------|----------|
| Folder Card | Deliverable card with distinct bg, folder icon | Click → opens modal |
| Modal Backdrop | Semi-transparent overlay | Click → closes modal |
| Modal Container | 80vw centered dialog | Contains header + body |
| Modal Header | Folder name + close button (✕) | Close button dismisses modal |
| Tree Panel | Left 30%, recursive folder/file tree | Folders expand/collapse, files select |
| Preview Panel | Right 70%, file content display | Markdown rendered, text preformatted |
| Loading Spinner | Centered in modal body | Shown during tree API call |

### User Flow

```
1. User sees folder deliverable card (distinct background)
2. User clicks folder card
3. Modal opens with loading spinner
4. Tree loads and populates left panel
5. User clicks a .md file in tree → rendered markdown in right panel
6. User clicks a .txt file → preformatted text in right panel
7. User clicks Escape / close button / backdrop → modal closes
```

## Dependencies

### Internal

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-038-C | CR target | Enhanced Deliverable Viewer — inline tree being replaced |
| FEATURE-036-E | Foundation | Deliverables, Polling & Lifecycle — base card grid, folder detection |
| `GET /api/workflow/{wf}/deliverables/tree` | Data source | Folder structure API (already exists) |
| `GET /api/ideas/file` | Data source | File content API (already exists) |
| `marked.js` | Library | Already loaded globally for markdown rendering |

### External

None.

## Business Rules

- **BR-039-A.1:** Folder detection remains based on trailing `/` in path or no file extension (existing logic)
- **BR-039-A.2:** Tree shows only descendants of the deliverable folder — no parent navigation
- **BR-039-A.3:** Preview is read-only — no editing capabilities
- **BR-039-A.4:** Binary files show "Binary file — cannot preview" message (text-only preview in MVP)

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty folder | Tree panel shows "No files in this folder" message |
| API error on tree load | Modal shows error message with retry option |
| File not found (404) | Preview shows "File not found" message |
| Binary file selected | Preview shows "Binary file — cannot preview" placeholder |
| Very long file names | Truncated with ellipsis in tree; full name as title tooltip |
| Modal open + navigate away | Modal should close on SPA navigation |
| Multiple rapid file clicks | Debounce — only load the last clicked file |

## Out of Scope

- Search/filter bar (→ FEATURE-039-B)
- Breadcrumb navigation (→ FEATURE-039-B)
- Typed file icons beyond basic 📁/📄 (→ FEATURE-039-B)
- Image preview (→ FEATURE-039-B)
- File download (→ FEATURE-039-B)
- Keyboard tree navigation (→ FEATURE-039-B)
- ARIA roles/accessibility (→ FEATURE-039-B)
- File editing

## Technical Considerations

- New `FolderBrowserModal` class in `src/static/js/folder-browser-modal.js` (or extend `deliverable-viewer.js`)
- CSS in new file `src/static/css/folder-browser-modal.css` or added to `workflow.css`
- Follow `ComposeIdeaModal` / `LinkExistingPanel` pattern for modal structure and tree rendering
- Clean removal of `_expandFolderTree()` and related code — verify no other code paths reference removed methods
- Modal CSS: `position: fixed`, `z-index` above workflow content, `overflow: auto` for tree/preview panels

## Open Questions

None.
