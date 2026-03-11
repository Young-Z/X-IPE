# Feature Specification: KB Reference Picker

> Feature ID: FEATURE-049-G  
> Version: v1.0  
> Status: Refined  
> Last Updated: 07-19-2025

## Version History
| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 07-19-2025 | Initial specification (retroactive from implementation) |

## Linked Mockups
- `x-ipe-docs/ideas/wf-007-knowledge-base-implementation/mockups/kb-interface-v1.html` — Scene 3 (Reference Picker). **Outdated**: directional reference only; the implementation evolved beyond the original mockup in layout details and interaction patterns.

## Overview

The KB Reference Picker is a cross-workflow modal that enables users to browse, search, and select Knowledge Base articles and folders for referencing within any workflow phase (ideation, design, implementation, etc.). It provides a two-panel layout with a folder tree on the left and a file list on the right, reusing the EPIC-039 Folder Browser Modal shell pattern at 80vw width.

The modal supports multi-select via checkboxes for both individual files and entire folders, real-time search with debounced API calls, and 2D tag filtering using lifecycle (amber) and domain (blue) filter chips. Selected references can be copied to clipboard or inserted directly into the current workflow action context via callback and custom DOM event.

The component is implemented as a standalone ES class (`KBReferencePicker`) with no external framework dependencies, loading data from three parallel API endpoints (`/api/kb/tree`, `/api/kb/config`, `/api/kb/files`) and providing graceful degradation when APIs are unavailable.

## User Stories

**US-049-G-01: Browse KB from any workflow phase**  
As a user working in any workflow phase, I want to open a Reference Picker modal so that I can browse the Knowledge Base without leaving my current context.

**US-049-G-02: Search KB articles**  
As a user looking for specific content, I want to search within the Reference Picker by filename and tags so that I can quickly find relevant KB articles.

**US-049-G-03: Filter by tag categories**  
As a user organizing references, I want to filter KB articles by lifecycle and domain tags so that I can narrow results to a specific category.

**US-049-G-04: Select multiple references**  
As a user building a reference set, I want to multi-select files and folders via checkboxes so that I can batch-reference related content.

**US-049-G-05: Copy reference paths**  
As a user who needs references outside the workflow, I want to copy selected paths to my clipboard so that I can paste them elsewhere.

**US-049-G-06: Insert references into workflow**  
As a user working within a workflow, I want to insert selected references directly into the current action context so that the workflow can access those KB articles.

## Acceptance Criteria

### AC-049-G-01: Modal opens with two-panel layout
- **Given** a KBReferencePicker instance is created
- **When** the `open()` method is called
- **Then** a modal overlay (`.kb-ref-overlay`) is appended to the document body with a left folder-tree panel (`.kb-ref-tree-panel`) and a right file-list panel (`.kb-ref-list-panel`)

### AC-049-G-02: Modal closes via close button and backdrop
- **Given** the Reference Picker modal is open
- **When** the user clicks the ✕ close button OR clicks the overlay backdrop (outside the modal)
- **Then** the modal plays a 300ms fade-out animation, the overlay is removed from the DOM, and body scroll is restored

### AC-049-G-03: Debounced search triggers API call
- **Given** the Reference Picker modal is open with a search input
- **When** the user types into the search input and 300ms elapses without further input
- **Then** a fetch request is made to `/api/kb/search?q={query}` and the file list panel re-renders with the results

### AC-049-G-04: Tag filter chips render and toggle
- **Given** the KB config returns lifecycle and domain tag arrays
- **When** the modal renders
- **Then** lifecycle tags appear as amber-styled chips (`kb-ref-chip-lifecycle`) and domain tags appear as blue-styled chips (`kb-ref-chip-domain`), and clicking a chip toggles its `active` class and filters the file list to show only files matching any active tag

### AC-049-G-05: Multi-select via checkboxes for files and folders
- **Given** the Reference Picker modal displays files and folders with checkboxes
- **When** the user checks a file or folder checkbox
- **Then** the item's path is added to the selected set, and unchecking removes it from the set

### AC-049-G-06: Selected count display updates
- **Given** the Reference Picker modal is open with a footer showing "0 selected"
- **When** the user checks or unchecks file/folder checkboxes
- **Then** the count label updates to reflect the current number of selected items (e.g., "3 selected")

### AC-049-G-07: Copy button copies paths to clipboard
- **Given** one or more files/folders are selected
- **When** the user clicks the "📋 Copy" button
- **Then** the selected paths are joined with newlines and written to the clipboard via `navigator.clipboard.writeText`, with a fallback to `document.execCommand('copy')` if the Clipboard API is unavailable

### AC-049-G-08: Copy feedback animation
- **Given** the user clicks the Copy button and clipboard write succeeds
- **When** the copy operation completes
- **Then** the button text changes to "✅ Copied!" for 1500ms before reverting to "📋 Copy"

### AC-049-G-09: Insert button invokes callback and dispatches event
- **Given** one or more files/folders are selected and an `onInsert` callback is provided
- **When** the user clicks the "Insert" button
- **Then** the `onInsert` callback is called with an array of selected paths, a `kb:references-inserted` CustomEvent is dispatched on `document` with the paths in `detail`, and the modal closes

### AC-049-G-10: Parallel API loading on open
- **Given** a KBReferencePicker instance
- **When** `open()` is called
- **Then** three API requests (`/api/kb/tree`, `/api/kb/config`, `/api/kb/files`) are fired in parallel via `Promise.all` before the modal renders

### AC-049-G-11: HTML escaping prevents XSS
- **Given** a file name or tag text contains HTML special characters (e.g., `<script>`)
- **When** the file list or filter chips are rendered
- **Then** the content is escaped via DOM-based text content assignment, preventing script injection

### AC-049-G-12: Graceful degradation on API failure
- **Given** one or more of the KB API endpoints fail or are unavailable
- **When** `open()` is called
- **Then** the modal still opens without crashing, showing empty tree ("No folders") and/or empty file list ("No files found") placeholders as appropriate

### AC-049-G-13: Body scroll locked during modal
- **Given** the page has scrollable content
- **When** the Reference Picker modal opens
- **Then** `document.body.style.overflow` is set to `'hidden'`, and when the modal closes it is restored to `''`

## Functional Requirements

### FR-049-G-01: Modal instantiation
The `KBReferencePicker` class accepts an options object with an optional `onInsert` callback. The constructor initializes empty state for tree, files, config, selected set, search query, and active tag filters.

### FR-049-G-02: Data loading
On `open()`, the picker loads data from three endpoints in parallel:
- `/api/kb/tree` → populates the folder tree
- `/api/kb/config` → populates lifecycle and domain tag arrays
- `/api/kb/files` → populates the file list (or `/api/kb/search?q=...` when a search query is active)

### FR-049-G-03: Modal layout
The modal uses an 80vw-wide container with max-width 900px, consisting of: header (title + close button), toolbar (search input), filter chips row, two-panel body (240px tree panel + flex file list panel), and footer (selected count + action buttons).

### FR-049-G-04: Folder tree rendering
The left panel renders a recursive folder tree from the tree API response. Each folder node displays a checkbox (data-type="folder"), a 📁 icon, and the folder name. Nested children are indented via `.kb-ref-tree-children`.

### FR-049-G-05: File list rendering
The right panel renders file items, each with a checkbox (data-type="file"), the file title (from frontmatter or filename), and tag pills showing lifecycle (amber) and domain (blue) tags.

### FR-049-G-06: Search functionality
The search input triggers a debounced (300ms) re-fetch from the search API endpoint. Results replace the current file list. The debounce timer is cleared on modal close to prevent stale updates.

### FR-049-G-07: Tag filtering
Clicking a filter chip toggles it active/inactive. When any chips are active, the file list is filtered client-side to show only files whose frontmatter tags include at least one active filter tag (OR logic across active filters).

### FR-049-G-08: Selection management
Checkbox changes add/remove paths from a `Set`. The footer count label updates on every change. Both files and folders can be selected simultaneously.

### FR-049-G-09: Copy action
The Copy button joins all selected paths with newline characters and writes to clipboard. Primary method is `navigator.clipboard.writeText`; fallback creates a temporary textarea for `document.execCommand('copy')`.

### FR-049-G-10: Insert action
The Insert button invokes the `onInsert` callback (if provided) with the selected paths array, dispatches a `kb:references-inserted` CustomEvent on `document`, and closes the modal.

### FR-049-G-11: Modal lifecycle
Opening: overlay appended → `active` class added via `requestAnimationFrame` for CSS transition. Closing: `active` class removed → overlay removed after 300ms animation timeout. Body scroll is locked on open and restored on close.

## Non-Functional Requirements

### NFR-049-G-01: Performance
- API requests fire in parallel, not sequentially
- Search uses 300ms debounce to avoid excessive API calls
- DOM updates for file list filtering happen client-side without re-fetching

### NFR-049-G-02: Security
- All user-generated content (file names, tag text) is HTML-escaped before insertion into the DOM
- Attribute values are escaped via a dedicated `_escapeAttr` method

### NFR-049-G-03: Accessibility
- Checkboxes are wrapped in `<label>` elements for click-target expansion
- Close button uses semantic button element
- Modal overlay uses z-index 1051 to layer above other UI

### NFR-049-G-04: Browser compatibility
- Clipboard API with `execCommand` fallback for older browsers
- CSS custom properties with fallback values for all color/background declarations
- No external framework dependencies (vanilla JS + DOM API)

## UI/UX Requirements

### Layout
- Modal width: 80vw, max-width 900px, max-height 85vh
- Two-panel body: left tree panel 240px fixed, right list panel flex
- Dark theme with CSS custom property support (falls back to hardcoded dark values)
- 12px border-radius on modal, 6px on inputs and buttons

### Visual feedback
- Overlay backdrop: rgba(0,0,0,0.6) with 4px backdrop blur
- Modal entrance: scale(0.95→1) + opacity(0→1) over 300ms
- Chip toggle: background/border color shift on active state
- File items: subtle hover highlight (rgba white 4%)
- Copy confirmation: "📋 Copy" → "✅ Copied!" for 1500ms

### Tag chip styling
- Lifecycle chips: amber palette (border rgba(245,158,11,0.25), text #fbbf24)
- Domain chips: blue palette (border rgba(59,130,246,0.25), text #60a5fa)
- Active state intensifies background gradient/opacity

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-049-A (KB Storage & Config) | Data | Provides `/api/kb/tree`, `/api/kb/config`, `/api/kb/files` endpoints |
| FEATURE-049-C (KB Search & Tags) | Data | Provides `/api/kb/search` endpoint and tag taxonomy |
| EPIC-039 Folder Browser Modal | Pattern | Reuses the 80vw two-panel modal shell pattern (not a code import) |

## Business Rules

### BR-049-G-01: Reference format
Selected paths are project-root-relative strings (e.g., `knowledge-base/research/competitor-analysis.md`). No transformation or wrapping is applied by the picker — consumers decide how to use the paths.

### BR-049-G-02: Insert closes modal
Clicking "Insert" always closes the modal after dispatching the callback and event. This ensures the user returns to their workflow context.

### BR-049-G-03: Tag filter OR logic
When multiple tag filter chips are active, files matching ANY active tag are shown (inclusive OR), not requiring all tags (AND). This broadens results for discovery.

### BR-049-G-04: Cross-workflow availability
The Reference Picker is not bound to a specific workflow phase. Any UI surface that instantiates `KBReferencePicker` and calls `open()` can launch it.

## Edge Cases & Constraints

### EC-049-G-01: All APIs fail
If all three API endpoints fail on `open()`, the modal still renders with "No folders" in the tree panel and "No files found" in the file list. The user can close normally.

### EC-049-G-02: Empty KB
When the Knowledge Base has no content, the picker shows empty-state placeholders. Copy and Insert buttons remain functional but operate on an empty selection.

### EC-049-G-03: Clipboard API unavailable
In environments where `navigator.clipboard.writeText` is not available (e.g., non-HTTPS contexts), the fallback creates a temporary textarea, selects its content, and uses `document.execCommand('copy')`.

### EC-049-G-04: XSS in file/folder names
Malicious content in file names or tag values is neutralized by DOM-based escaping (`_escapeHtml` via textContent, `_escapeAttr` via character replacement) before rendering.

### EC-049-G-05: Rapid search typing
The 300ms debounce timer is reset on each keystroke, preventing redundant API calls during fast typing. The timer is cleared on modal close to prevent stale callbacks.

### EC-049-G-06: Double open
If `open()` is called while a modal is already displayed, a second overlay will be appended. Consumers should guard against this by tracking modal state.

## Out of Scope

- **File content preview**: The right panel shows a file list with metadata, not a rendered preview of file content (markdown rendering, image display, PDF placeholder mentioned in requirements are deferred)
- **Drag-and-drop reordering**: Selected references cannot be reordered within the picker
- **Persistence of selections**: Selections are not saved between modal open/close cycles
- **Folder expand/collapse toggle**: The tree renders all folders expanded; there is no collapse/expand toggle interaction
- **Keyboard navigation**: No keyboard shortcuts (Tab, Enter, Escape) beyond native browser behavior
- **Right panel file preview pane**: A dedicated preview pane for selected file content is not implemented

## Technical Considerations

- The picker should remain framework-agnostic (vanilla JS) to be embeddable in any UI context
- API endpoint paths are centralized as static frozen properties for maintainability
- The clipboard fallback mechanism covers non-secure-context environments
- The `kb:references-inserted` CustomEvent on `document` enables loose coupling — any listener can react to insertions without direct reference to the picker instance
- Animation timing constants (debounce, animation, copy feedback) are exposed as static class properties for testability and tuning
- Tag filtering operates client-side on the already-loaded file set; server-side tag filtering is delegated to the search endpoint
