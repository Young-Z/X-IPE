# Feature Specification: KB Reference Picker

> Feature ID: FEATURE-049-G  
> Version: v4.0  
> Status: Refined  
> Last Updated: 03-13-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 07-19-2025 | Initial specification (retroactive from implementation) |
| v2.0 | 03-11-2026 | Template alignment — GWT format for ACs, Test Type Legend |
| v3.0 | 03-13-2026 | CR-003: 8-point UIUX redesign — folder navigation, light theme, standard modal, breadcrumb, tag layout, full paths |
| v4.0 | 03-13-2026 | CR-004: KB Reference integration in Workplace compose — button, picker invocation, .knowledge-reference.yaml, count label |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| KB Interface v1 (Scene 3 — Reference Picker) | HTML | [x-ipe-docs/requirements/EPIC-049/mockups/kb-interface-v1.html](x-ipe-docs/requirements/EPIC-049/mockups/kb-interface-v1.html) | Original reference picker — dark theme, checkbox folders | outdated | 03-11-2026 |

> **Path Convention:** Use full project-root-relative paths for mockup links (e.g., `x-ipe-docs/requirements/EPIC-XXX/mockups/file.html`).
> This enables the link preview feature (IDEA-033) — clicking opens an in-app DeliverableViewer modal.
> Do NOT use relative paths like `../mockups/` or `../../mockups/`.
>
> **Note:** UI/UX requirements and acceptance criteria below are derived from CR-003 feedback.
> The v1 mockup (Scene 3) is marked "outdated" — used as directional reference only.
>
> **Conflict Resolution:** If specification and mockup diverge, compare Linked Date vs spec Last Updated.
> If the mockup is newer and not stale → mockup takes precedence (update spec to match).
> If the spec is newer → spec takes precedence (mockup may need refresh).

## Overview

The KB Reference Picker is a cross-workflow modal that enables users to browse, search, and select Knowledge Base articles and folders for referencing within any workflow phase (ideation, design, implementation, etc.). It provides a two-panel layout with a folder tree on the left and a content panel on the right.

The left panel displays a hierarchical folder tree rooted at the KB root (`x-ipe-docs/knowledge-base/`), showing only folders. Clicking a folder navigates into it — the right panel updates to show the selected folder's sub-folders and files. Folders are not directly selectable in the tree; instead, a checkbox in the breadcrumb navigation bar at the top of the right panel allows the user to select the current folder. Files are selectable via individual checkboxes in the right panel.

The modal uses a light color scheme (no dark theme), standard modal dimensions, scrollable content panels, and separates lifecycle and domain tags onto distinct lines. Selected reference paths use the full project path format (`x-ipe-docs/knowledge-base/...`). The component is implemented as a standalone ES class (`KBReferencePicker`) with no external framework dependencies, loading data from parallel API endpoints and providing graceful degradation when APIs are unavailable.

## User Stories

**US-049-G-01: Browse KB from any workflow phase**  
As a user working in any workflow phase, I want to open a Reference Picker modal so that I can browse the Knowledge Base without leaving my current context.

**US-049-G-02: Navigate folder structure**  
As a user exploring the KB, I want to click folders in the tree to navigate into them and see their contents in the right panel, so that I can drill down to the content I need.

**US-049-G-03: Search KB articles**  
As a user looking for specific content, I want to search within the Reference Picker by filename and tags so that I can quickly find relevant KB articles.

**US-049-G-04: Filter by tag categories**  
As a user organizing references, I want to filter KB articles by lifecycle and domain tags (displayed on separate lines) so that I can narrow results to a specific category.

**US-049-G-05: Select files and folders**  
As a user building a reference set, I want to select files via checkboxes in the right panel and optionally select the current folder via a breadcrumb checkbox, so that I can batch-reference related content.

**US-049-G-06: Copy reference paths**  
As a user who needs references outside the workflow, I want to copy selected full paths (`x-ipe-docs/knowledge-base/...`) to my clipboard so that I can paste them elsewhere with correct project-relative references.

**US-049-G-07: Insert references into workflow**  
As a user working within a workflow, I want to insert selected references directly into the current action context so that the workflow can access those KB articles.

**US-049-G-08: Attach KB references from compose pane** *(CR-004)*  
As an idea author composing an idea, I want to click a "KB Reference" button on the compose action bar so that I can open the KB Reference Picker and select knowledge articles to attach to my idea.

**US-049-G-09: Persist knowledge references** *(CR-004)*  
As an idea author, I want my selected KB references to be saved as a `.knowledge-reference.yaml` file in the idea folder when I submit the idea, so that the references are permanently linked to the idea.

**US-049-G-10: View attached references** *(CR-004)*  
As an idea author, I want to see a reference count label after attaching KB references, and click it to see a popup listing all attached files with type icons (folder/file), so that I can verify what I've attached before submitting.

## Acceptance Criteria

### AC-049-G-01: Modal Lifecycle

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-01a | GIVEN KBReferencePicker is instantiated WHEN `open()` is called THEN modal overlay (`.kb-ref-overlay`) is appended to body with light-themed styling, left folder-tree panel (`.kb-ref-tree-panel`), AND right content panel (`.kb-ref-list-panel`) | UI |
| AC-049-G-01b | GIVEN reference picker modal is open WHEN user clicks ✕ close button or overlay backdrop THEN modal plays fade-out animation, overlay is removed from DOM, AND body scroll is restored | UI |
| AC-049-G-01c | GIVEN reference picker is used WHEN modal opens THEN `document.body.style.overflow` is set to `'hidden'` AND WHEN modal closes THEN overflow is restored to `''` | Unit |

### AC-049-G-02: Modal Layout & Theme

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-02a | GIVEN modal is open WHEN rendered THEN modal uses standard dimensions (90vw × 90vh, matching other modals) AND is centered on screen | UI |
| AC-049-G-02b | GIVEN modal content exceeds panel height WHEN content overflows THEN both tree panel and content panel scroll independently | UI |
| AC-049-G-02c | GIVEN modal is rendered WHEN user views the picker THEN the modal uses a light color scheme (white/light background, dark text) with no dark theme | UI |

### AC-049-G-03: Folder Tree Navigation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-03a | GIVEN modal is open WHEN tree panel renders THEN it shows the KB root folder at the top with sub-folders displayed as an expandable tree hierarchy (folders only, no files in tree) | UI |
| AC-049-G-03b | GIVEN folder tree is rendered WHEN user clicks a folder name THEN the right panel updates to show sub-folders and files within the selected folder AND the folder is visually highlighted as active | UI |
| AC-049-G-03c | GIVEN folder tree is rendered THEN folders do NOT have checkboxes — folders in the tree are navigation-only | UI |

### AC-049-G-04: Breadcrumb Navigation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-04a | GIVEN user has navigated into a folder WHEN right panel renders THEN a breadcrumb navigation bar appears at the top of the right panel showing the path from KB root to current folder | UI |
| AC-049-G-04b | GIVEN breadcrumb is displayed WHEN user clicks a breadcrumb segment THEN the right panel navigates to that folder's contents AND the tree highlights the corresponding folder | UI |
| AC-049-G-04c | GIVEN breadcrumb is displayed THEN a checkbox appears on the far right of the breadcrumb bar allowing the user to select the current folder for referencing | UI |
| AC-049-G-04d | GIVEN breadcrumb folder checkbox is checked WHEN selection is inspected THEN the current folder's full path (e.g., `x-ipe-docs/knowledge-base/guides`) is in the selected set | Unit |

### AC-049-G-05: Search

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-05a | GIVEN reference picker modal is open WHEN user types in search input AND 300ms debounce elapses THEN fetch request to `/api/kb/search?q={query}` fires | Unit |
| AC-049-G-05b | GIVEN a search request has been sent WHEN API response is received THEN file list panel re-renders with search results | UI |

### AC-049-G-06: Tag Filtering

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-06a | GIVEN `/api/kb/config` returns tag data WHEN filter chips render THEN lifecycle tags render as amber-styled chips on one line AND domain tags render as blue-styled chips on a separate line below | UI |
| AC-049-G-06b | GIVEN filter chips are rendered WHEN user clicks a chip THEN chip's `active` class is toggled AND file list filters to show only files matching any active tag (OR logic) | UI |

### AC-049-G-07: Selection Management

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-07a | GIVEN a file checkbox in the right panel is unchecked WHEN user checks it THEN the file's full path (e.g., `x-ipe-docs/knowledge-base/guides/setup.md`) is added to the selected set | Unit |
| AC-049-G-07b | GIVEN a file checkbox is checked WHEN user unchecks it THEN its path is removed from the selected set | Unit |
| AC-049-G-07c | GIVEN reference picker modal is open WHEN any checkbox changes THEN footer count label updates to reflect current number of selected items (e.g., "3 selected") | UI |

### AC-049-G-08: Copy Action

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-08a | GIVEN one or more items are selected WHEN user clicks "Copy" button THEN selected full paths (e.g., `x-ipe-docs/knowledge-base/folder/file.md`) are joined with newlines AND written to clipboard via `navigator.clipboard.writeText` | Unit |
| AC-049-G-08b | GIVEN Clipboard API is unavailable WHEN user clicks "Copy" button THEN fallback to `document.execCommand('copy')` is used | Unit |
| AC-049-G-08c | GIVEN user clicks "Copy" button WHEN clipboard write succeeds THEN button shows "✅ Copied!" feedback for 1500ms AND then reverts to original label | UI |

### AC-049-G-09: Insert Action

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-09a | GIVEN one or more items are selected AND `onInsert` callback is configured WHEN user clicks "Insert" button THEN `onInsert` callback is called with array of selected full paths | Unit |
| AC-049-G-09b | GIVEN one or more items are selected WHEN user clicks "Insert" button THEN `kb:references-inserted` CustomEvent is dispatched on `document` with full paths in `detail` | Unit |
| AC-049-G-09c | GIVEN user clicks "Insert" button WHEN insert action completes THEN modal closes | UI |

### AC-049-G-10: Data Loading & Error Handling

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-10a | GIVEN KBReferencePicker is instantiated WHEN `open()` is called THEN three API requests (`/api/kb/tree`, `/api/kb/config`, `/api/kb/files`) fire in parallel via `Promise.all` | Integration |
| AC-049-G-10b | GIVEN one or more API endpoints fail WHEN `open()` is called THEN modal opens without crashing AND shows "No folders" and/or "No files found" placeholders | Integration |

### AC-049-G-11: Security

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-11a | GIVEN file names or tag text contain HTML special characters WHEN content is rendered in the modal THEN characters are escaped via DOM-based text content assignment, preventing script injection | Unit |

### AC-049-G-12: Compose Pane KB Reference Button *(CR-004)*

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-12a | GIVEN user is on the Workplace Ideation compose pane WHEN the compose pane renders THEN a "KB Reference" button appears on the left side of the `.workplace-compose-actions` bar, with the Submit Idea button on the right | UI |
| AC-049-G-12b | GIVEN the KB Reference button is visible WHEN user clicks it THEN the KB Reference Picker modal opens via `KBReferencePicker.open()` | UI |
| AC-049-G-12c | GIVEN KBReferencePicker is not available (class undefined) WHEN compose pane renders THEN the KB Reference button is hidden or disabled AND no error is thrown | Unit |
| AC-049-G-12d | GIVEN the KB Reference button is rendered THEN it uses `btn-outline-secondary` styling (secondary to the primary Submit button) AND displays a book/reference icon | UI |
| AC-049-G-12e | GIVEN the `.workplace-compose-actions` container has the KB Reference button and Submit button WHEN rendered THEN the container uses flexbox layout with `justify-content: space-between` so KB button is left-aligned and Submit is right-aligned | UI |

### AC-049-G-13: Knowledge Reference Persistence *(CR-004)*

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-13a | GIVEN user has selected KB references via the picker WHEN the picker's Insert button is clicked THEN selected paths are stored in the compose pane's internal state (e.g., `this.kbReferences` array) | Unit |
| AC-049-G-13b | GIVEN user has KB references stored in state WHEN `submitComposedIdea()` is called THEN the KB references are included in the FormData as a JSON-encoded `kb_references` field | Unit |
| AC-049-G-13c | GIVEN the backend receives a request with `kb_references` field WHEN the idea folder is created THEN a `.knowledge-reference.yaml` file is written to the idea folder | API |
| AC-049-G-13d | GIVEN `.knowledge-reference.yaml` is written WHEN the file is read THEN it contains a `knowledge-reference` key with a list of full KB paths matching the selected references | Unit |
| AC-049-G-13e | GIVEN user submits an idea without selecting any KB references WHEN `submitComposedIdea()` is called THEN no `.knowledge-reference.yaml` file is created AND the submit flow works normally | Integration |
| AC-049-G-13f | GIVEN user opens the picker multiple times before submitting WHEN inserting new references each time THEN the stored references accumulate (new selections are appended, not replaced) | Unit |

### AC-049-G-14: Reference Count Label & Popup *(CR-004)*

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-----------|-----------|
| AC-049-G-14a | GIVEN no KB references have been inserted WHEN the compose pane renders THEN no reference count label is displayed | UI |
| AC-049-G-14b | GIVEN user inserts KB references via the picker WHEN the picker closes THEN a reference count label (e.g., "📚 3 references") appears near the KB Reference button | UI |
| AC-049-G-14c | GIVEN the reference count label is visible WHEN user clicks it THEN an inline popup (tooltip/popover) appears listing each referenced file/folder with a type icon (📁 for folder, 📄 for file) and the file/folder name | UI |
| AC-049-G-14d | GIVEN the reference popup is open WHEN user clicks outside the popup or clicks the count label again THEN the popup closes | UI |
| AC-049-G-14e | GIVEN the reference count label is showing WHEN user opens the picker and inserts additional references THEN the count label updates to reflect the new total | UI |
| AC-049-G-14f | GIVEN the reference popup is showing items WHEN user views the list THEN each item shows the filename (not full path) with a tooltip showing the full path on hover | UI |

> **Test Type Legend:**
> - **UI** — Browser/DOM interaction test (clicks, renders, layout)
> - **API** — HTTP request/response test (status codes, response body)
> - **Unit** — Isolated function/module test (parsing, calculations)
> - **Integration** — Multi-component interaction test (service + DB)

## Functional Requirements

### FR-049-G-01: Modal instantiation
The `KBReferencePicker` class accepts an options object with an optional `onInsert` callback. The constructor initializes empty state for tree, files, config, selected set, search query, active tag filters, and current folder path.

### FR-049-G-02: Data loading
On `open()`, the picker loads data from three endpoints in parallel:
- `/api/kb/tree` → populates the folder tree (hierarchical structure from KB root)
- `/api/kb/config` → populates lifecycle and domain tag arrays
- `/api/kb/files` → populates the file list (or `/api/kb/search?q=...` when a search query is active)

### FR-049-G-03: Modal layout
The modal uses standard dimensions (90vw × 90vh, matching other modals), consisting of: header (title + close button), toolbar (search input), filter chip area (lifecycle tags on first line, domain tags on second line), two-panel body (tree panel + scrollable content panel), and footer (selected count + action buttons). Light color scheme throughout.

### FR-049-G-04: Folder tree rendering
The left panel renders a hierarchical folder tree from the tree API response, rooted at the KB root folder. Each folder node displays a 📁 icon and the folder name — no checkboxes. Clicking a folder navigates into it (updates right panel). The tree visually highlights the currently active folder. Sub-folders are indented to show hierarchy. Reference the ideation sidebar tree pattern for visual style (folders only).

### FR-049-G-05: Right panel content rendering
The right panel displays the contents of the currently selected folder. It shows:
- A breadcrumb navigation bar at the top (KB root → ... → current folder) with a checkbox on the far right to select the current folder
- Sub-folders within the current folder (clickable to navigate deeper)
- Files with checkboxes, file title (from frontmatter or filename), and tag pills showing lifecycle (amber) and domain (blue) tags

### FR-049-G-06: Search functionality
The search input triggers a debounced (300ms) re-fetch from the search API endpoint. Results replace the current file list in the right panel. The debounce timer is cleared on modal close to prevent stale updates.

### FR-049-G-07: Tag filtering
Clicking a filter chip toggles it active/inactive. Lifecycle and domain tags are displayed on separate lines. When any chips are active, the file list is filtered client-side to show only files whose frontmatter tags include at least one active filter tag (OR logic across active filters).

### FR-049-G-08: Selection management
File checkbox changes add/remove full paths (`x-ipe-docs/knowledge-base/...`) from a `Set`. The breadcrumb folder checkbox adds/removes the current folder's full path. The footer count label updates on every change. Files are selected via right-panel checkboxes; folders are selected via the breadcrumb checkbox only.

### FR-049-G-09: Copy action
The Copy button joins all selected full paths with newline characters and writes to clipboard. Paths use the format `x-ipe-docs/knowledge-base/{path}`. Primary method is `navigator.clipboard.writeText`; fallback creates a temporary textarea for `document.execCommand('copy')`.

### FR-049-G-10: Insert action
The Insert button invokes the `onInsert` callback (if provided) with the selected full paths array, dispatches a `kb:references-inserted` CustomEvent on `document`, and closes the modal.

### FR-049-G-11: Modal lifecycle
Opening: overlay appended → `active` class added via `requestAnimationFrame` for CSS transition. Closing: `active` class removed → overlay removed after animation timeout. Body scroll is locked on open and restored on close.

### FR-049-G-12: Compose pane KB Reference button *(CR-004)*
The Workplace compose pane (`.workplace-compose-actions`) renders a "KB Reference" button on the left side, using `btn-outline-secondary` styling with a book/reference icon (e.g., `bi-journal-bookmark`). The action bar uses `display: flex; justify-content: space-between` to place the KB button left and Submit Idea right. When clicked, the button instantiates (or reuses) a `KBReferencePicker` with an `onInsert` callback that stores selected paths in the compose pane's state. The button is hidden if `KBReferencePicker` class is not available (graceful degradation).

### FR-049-G-13: Knowledge reference YAML persistence *(CR-004)*
When the user submits an idea via `submitComposedIdea()` and KB references exist in state, the references are included in the FormData as a JSON-encoded `kb_references` field. The backend extracts this field and writes a `.knowledge-reference.yaml` file to the newly created idea folder. The YAML format is:
```yaml
knowledge-reference:
  - x-ipe-docs/knowledge-base/path/to/file1.md
  - x-ipe-docs/knowledge-base/path/to/folder
```
If no KB references are selected, no YAML file is created. Multiple picker invocations accumulate references (append, not replace).

### FR-049-G-14: Reference count label and popup *(CR-004)*
After inserting KB references, a reference count label (e.g., "📚 3 references") appears near the KB Reference button. Clicking the label opens an inline popup (Bootstrap popover or custom tooltip) listing each referenced item with a type icon: 📁 for folders, 📄 for files. Each item shows the filename with a tooltip showing the full path on hover. The popup closes when clicking outside or clicking the label again. The count updates when additional references are inserted.

## Non-Functional Requirements

### NFR-049-G-01: Performance
- API requests fire in parallel, not sequentially
- Search uses 300ms debounce to avoid excessive API calls
- DOM updates for file list filtering happen client-side without re-fetching
- Folder navigation within already-loaded tree data is instant (no additional API calls)

### NFR-049-G-02: Security
- All user-generated content (file names, tag text, folder names) is HTML-escaped before insertion into the DOM
- Attribute values are escaped via a dedicated `_escapeAttr` method

### NFR-049-G-03: Accessibility
- Checkboxes are wrapped in `<label>` elements for click-target expansion
- Close button uses semantic button element
- Breadcrumb navigation uses semantic list or nav element
- Modal overlay uses z-index 1051 to layer above other UI

### NFR-049-G-04: Browser compatibility
- Clipboard API with `execCommand` fallback for older browsers
- No external framework dependencies (vanilla JS + DOM API)

## UI/UX Requirements

### Layout
- Modal: standard dimensions (90vw × 90vh, matching other modals), centered
- Two-panel body: left tree panel (fixed width), right content panel (flex)
- **Light theme** — white/light backgrounds, dark text, no dark theme
- Rounded corners on modal, inputs, and buttons

### Breadcrumb bar
- Positioned at top of right panel
- Shows path: `KB Root > Folder > Sub-folder`
- Each segment is clickable (navigates to that folder)
- Far-right: checkbox to select current folder

### Tag chip layout
- **Lifecycle tags**: amber-styled chips, displayed on first line with `▸` prefix
- **Domain tags**: blue-styled chips, displayed on second line with `#` prefix
- Two tag types MUST be on separate lines

### Scrollable content
- Both tree panel and right panel scroll independently when content overflows
- Scroll behavior is smooth

### Visual feedback
- Overlay backdrop with subtle blur
- Modal entrance animation (fade + scale)
- Active folder highlighted in tree
- Chip toggle: background/border color shift on active state
- File items: subtle hover highlight
- Copy confirmation: "✅ Copied!" for 1500ms

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-049-A (KB Storage & Config) | Data | Provides `/api/kb/tree`, `/api/kb/config`, `/api/kb/files` endpoints |
| FEATURE-049-C (KB Search & Tags) | Data | Provides `/api/kb/search` endpoint and tag taxonomy |
| Workplace compose pane (workplace.js) | Integration | CR-004: Host for KB Reference button, count label, and reference state |
| Ideas upload API (/api/ideas/upload) | Integration | CR-004: Backend endpoint to receive `kb_references` field and write YAML file |

## Business Rules

### BR-049-G-01: Reference format
Selected paths use full project-relative format: `x-ipe-docs/knowledge-base/{path}` (e.g., `x-ipe-docs/knowledge-base/research/competitor-analysis.md`). This format enables cross-document linking throughout the project.

### BR-049-G-02: Insert closes modal
Clicking "Insert" always closes the modal after dispatching the callback and event. This ensures the user returns to their workflow context.

### BR-049-G-03: Tag filter OR logic
When multiple tag filter chips are active, files matching ANY active tag are shown (inclusive OR), not requiring all tags (AND). This broadens results for discovery.

### BR-049-G-04: Cross-workflow availability
The Reference Picker is not bound to a specific workflow phase. Any UI surface that instantiates `KBReferencePicker` and calls `open()` can launch it.

### BR-049-G-05: Folder navigation model
Folders are navigation targets, not selection targets in the tree. The only way to select a folder is via the breadcrumb checkbox in the right panel. This prevents confusion between navigating into a folder and selecting it.

### BR-049-G-06: Reference accumulation *(CR-004)*
Multiple invocations of the KB Reference Picker within the same compose session accumulate references. New selections are appended to the existing set, not replaced. This allows building a reference list incrementally.

### BR-049-G-07: YAML file conditional creation *(CR-004)*
The `.knowledge-reference.yaml` file is only created when at least one KB reference is selected. Ideas submitted without KB references do not include this file.

### BR-049-G-08: Idea folder context tracking *(CR-004)*
When the KB Reference button is clicked, the compose pane records its current idea-folder context (if editing an existing idea) or defers YAML writing until the folder is created (if composing a new idea). This ensures references are always written to the correct location.

## Edge Cases & Constraints

### EC-049-G-01: All APIs fail
If all three API endpoints fail on `open()`, the modal still renders with "No folders" in the tree panel and "No files found" in the right panel. The user can close normally.

### EC-049-G-02: Empty KB
When the Knowledge Base has no content, the picker shows empty-state placeholders. Copy and Insert buttons remain functional but operate on an empty selection.

### EC-049-G-03: Clipboard API unavailable
In environments where `navigator.clipboard.writeText` is not available (e.g., non-HTTPS contexts), the fallback creates a temporary textarea, selects its content, and uses `document.execCommand('copy')`.

### EC-049-G-04: XSS in file/folder names
Malicious content in file names or tag values is neutralized by DOM-based escaping (`_escapeHtml` via textContent, `_escapeAttr` via character replacement) before rendering.

### EC-049-G-05: Rapid search typing
The 300ms debounce timer is reset on each keystroke, preventing redundant API calls during fast typing. The timer is cleared on modal close to prevent stale callbacks.

### EC-049-G-06: Deep folder nesting
When navigating deeply nested folders, the breadcrumb may become long. The breadcrumb bar should truncate intermediate segments or wrap gracefully.

### EC-049-G-07: Root-level selection
At the KB root level, the breadcrumb folder checkbox allows selecting the root folder itself (`x-ipe-docs/knowledge-base/`).

### EC-049-G-08: Submit without content but with references *(CR-004)*
If a user selects KB references but writes no idea content, the existing content validation ("Please write something before submitting") still applies. The references are kept in state so the user can add content and submit without re-selecting.

### EC-049-G-09: KB Reference Picker unavailable *(CR-004)*
If the `KBReferencePicker` class is not loaded (e.g., JS file failed to load), the KB Reference button is hidden or disabled gracefully. The compose pane remains fully functional for idea submission without KB references.

### EC-049-G-10: Very long reference list *(CR-004)*
When a user selects many references (10+), the reference count popup should be scrollable to prevent it from overflowing the viewport.

## Out of Scope

- **File content preview**: The right panel shows a file list with metadata, not a rendered preview of file content
- **Drag-and-drop reordering**: Selected references cannot be reordered within the picker
- **Persistence of selections**: Selections are not saved between modal open/close cycles
- **Keyboard navigation**: No keyboard shortcuts (Tab, Enter, Escape) beyond native browser behavior
- **Right panel file preview pane**: A dedicated preview pane for selected file content is not implemented
- **Dark theme**: The picker uses light theme only (CR-003 requirement)
- **Compose Idea Modal integration**: CR-004 only covers the Workplace compose pane (`workplace.js`). The separate Compose Idea Modal (`compose-idea-modal.js`) is not affected.
- **Reference editing/removal**: Users cannot remove individual references from the count popup; they can only add more via the picker. Full reference management is a future enhancement.
- **Reference validation**: The system does not verify that referenced KB paths still exist at submit time. Path validation is a future enhancement.

## Technical Considerations

- The picker should remain framework-agnostic (vanilla JS) to be embeddable in any UI context
- API endpoint paths are centralized as static frozen properties for maintainability
- The clipboard fallback mechanism covers non-secure-context environments
- The `kb:references-inserted` CustomEvent on `document` enables loose coupling
- Animation timing constants (debounce, animation, copy feedback) are exposed as static class properties for testability
- Tag filtering operates client-side on the already-loaded file set; server-side tag filtering is delegated to the search endpoint
- Full path prefix (`x-ipe-docs/knowledge-base/`) is centralized as a constant for consistency
- Tree navigation state (current folder) is tracked internally; folder contents are derived from the already-loaded tree data without additional API calls
- CR-004: The compose pane integration reuses the existing `KBReferencePicker` class without modification — all new logic lives in `workplace.js`
- CR-004: The `.knowledge-reference.yaml` file uses a simple flat list format for easy parsing by downstream agents and tools
- CR-004: Reference state persists in the compose pane instance across picker open/close cycles, but is cleared on successful submit or page reload
- CR-004: The backend YAML writer should use the `yaml` library (Python) for proper YAML serialization

## Open Questions

_No open questions at this time._
