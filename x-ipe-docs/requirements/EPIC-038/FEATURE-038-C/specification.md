# Feature Specification: Enhanced Deliverable Viewer

> Feature ID: FEATURE-038-C
> Version: v1.3
> Status: Refined
> Last Updated: 03-26-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-20-2026 | Initial specification — folder-type deliverables with file-tree and inline preview |
| v1.1 | 03-16-2026 | [CR-001](CR-001.md): Add .docx and .msg file content preview via server-side conversion (mammoth + extract-msg). Updates AC-038-C.15, BR-038-C.3, Out-of-Scope. |
| v1.2 | 03-26-2026 | [CR-002](CR-002.md): Add download icon, preview/raw toggle, and smart default mode (raw for `*/src/*` files) to deliverable preview modal header. Updates Out-of-Scope, adds US-038-C.4/5, AC-038-C.06, FR-038-C.9/10/11, BR-038-C.6/7. |
| v1.3 | 03-26-2026 | Refinement of CR-002: Expand AC-038-C.06 (7→10 ACs) with toggle visibility rules (hidden for non-text files), per-file mode reset, download for all file types. Add UI/UX components and user flow for toolbar. Add CR-002 edge cases. Update FR-038-C.10 with visibility logic. |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Refine Idea Modal | HTML | [refine-idea-modal-v1.html](x-ipe-docs/requirements/EPIC-038/mockups/refine-idea-modal-v1.html) | Scene 4: deliverable viewer with file-tree and inline preview | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".

## Overview

This feature extends the deliverables section (FEATURE-036-E) to support **folder-type deliverables**. Currently, each deliverable card shows a single file with icon, name, and path. When an action produces a folder of output files (e.g., `refined-idea/`), there is no way to browse or preview the contents.

This feature adds:
1. **Folder detection** — deliverable paths ending with `/` are treated as folder-type
2. **File-tree rendering** — folder deliverables expand into a nested file listing with folder/file icons
3. **Inline preview** — clicking a file opens a preview pane below the tree: markdown rendered via `marked.js`, text/code shown as monospace preformatted text
4. **Convertible binary preview (CR-001)** — `.docx` and `.msg` files are converted server-side to HTML and rendered in the preview pane, instead of showing "Binary file — cannot preview"

This is a **CR on FEATURE-036-E** (Deliverables, Polling & Lifecycle).

**Target Users:**
- Workflow users who want to browse multi-file action outputs without leaving the workflow view

## User Stories

- **US-038-C.1:** As a workflow user, I want to see the contents of a folder deliverable as a file tree, so that I can understand what files the action produced.
- **US-038-C.2:** As a workflow user, I want to click a file in the tree to preview its content inline, so that I can quickly review outputs without opening external tools.
- **US-038-C.3 (CR-001):** As a workflow user, I want to preview .docx and .msg files in the deliverable viewer, so that I can read uploaded business documents without downloading them.
- **US-038-C.4 (CR-002):** As a workflow user, I want to download a file directly from the preview modal, so that I can save it locally without closing the modal and navigating elsewhere.
- **US-038-C.5 (CR-002):** As a workflow user, I want to toggle between rendered preview and raw text view in the preview modal, so that I can see either the formatted output or the unprocessed source content.

## Acceptance Criteria

### AC-038-C.01: Folder Detection

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-038-C.01a | GIVEN a deliverable item from the workflow API WHEN the path ends with `/` THEN it is rendered as a folder-type card with expand toggle | Unit |
| AC-038-C.01b | GIVEN a deliverable item with a path NOT ending in `/` WHEN the deliverables section renders THEN it uses the existing card layout (no regression) | Unit |

### AC-038-C.02: File-Tree Rendering

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-038-C.02a | GIVEN a folder-type deliverable card WHEN user clicks expand toggle THEN a nested file-tree listing is shown below the card | UI |
| AC-038-C.02b | GIVEN a file-tree listing WHEN it renders THEN directories show 📁 icons AND files show 📄 icons | UI |
| AC-038-C.02c | GIVEN a nested directory in the tree WHEN user clicks a folder node THEN it toggles collapse/expand of that subtree | UI |
| AC-038-C.02d | GIVEN a folder-type deliverable WHEN the tree first expands THEN folder contents are fetched lazily from the API | Integration |
| AC-038-C.02e | GIVEN a folder-type deliverable WHEN it renders THEN the visual layout matches mockup Scene 4 for tree structure | UI |

### AC-038-C.03: Inline Preview (Text)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-038-C.03a | GIVEN a file-tree WHEN user clicks a file entry THEN an inline preview pane appears below the tree | UI |
| AC-038-C.03b | GIVEN a `.md` file is clicked WHEN preview loads THEN the markdown content is rendered as HTML via `marked.parse()` | Unit |
| AC-038-C.03c | GIVEN a text/code file is clicked WHEN preview loads THEN the content is shown as monospace preformatted text | UI |
| AC-038-C.03d | GIVEN a preview pane is open WHEN the file name is displayed THEN it appears as a header above the content | UI |
| AC-038-C.03e | GIVEN a preview pane is open WHEN user clicks a different file THEN the previous preview is replaced with the new file content | UI |

### AC-038-C.04: Convertible Binary Preview (CR-001)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-038-C.04a | GIVEN a `.docx` file in the file-tree or deliverable list WHEN user clicks to preview THEN the backend converts it to HTML via mammoth AND the preview pane renders the converted HTML | Integration |
| AC-038-C.04b | GIVEN a `.msg` file in the file-tree or deliverable list WHEN user clicks to preview THEN the backend extracts email metadata (From, To, CC, Date, Subject) and body AND the preview pane renders them as structured HTML | Integration |
| AC-038-C.04c | GIVEN a `.docx` file with headings, lists, tables, and bold/italic text WHEN converted and previewed THEN all formatting elements are preserved in the HTML output | Unit |
| AC-038-C.04d | GIVEN a `.msg` file with email body WHEN converted and previewed THEN the preview shows From, To, CC, Date, Subject fields as labeled headers AND the email body below | Unit |
| AC-038-C.04e | GIVEN a corrupted or password-protected `.docx` or `.msg` file WHEN conversion is attempted THEN the preview shows "Preview unavailable for this file" gracefully (no crash, no stack trace) | Unit |
| AC-038-C.04f | GIVEN a `.docx` or `.msg` file larger than 10MB WHEN user clicks to preview THEN the preview shows "File too large to preview (max 10MB)" without attempting conversion | Unit |
| AC-038-C.04g | GIVEN any converted HTML from mammoth or extract-msg WHEN rendered in the preview pane THEN script tags, iframes, and event handlers are stripped (sanitized via BeautifulSoup) | Unit |
| AC-038-C.04h | GIVEN a binary file that is NOT .docx or .msg (e.g., .png, .zip, .exe) WHEN user clicks to preview THEN the preview shows "Binary file — cannot preview" (unchanged behavior) | Unit |

### AC-038-C.05: Security & Performance

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-038-C.05a | GIVEN a file-tree or preview request WHEN the path contains traversal sequences (`../`) THEN the request is rejected AND an error is shown | API |
| AC-038-C.05b | GIVEN a folder with up to 50 files WHEN the tree renders THEN it completes within 500ms | Unit |
| AC-038-C.05c | GIVEN a `.docx` or `.msg` file up to 10MB WHEN conversion runs THEN it completes within 3 seconds | Unit |

### AC-038-C.06: Preview Header Toolbar (CR-002)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-038-C.06a | GIVEN the deliverable preview modal is open for a text-renderable file (markdown, code, html) WHEN the header renders THEN it displays: filename (left), and a toolbar group (right) containing download icon, preview/raw toggle icon, and close button | UI |
| AC-038-C.06b | GIVEN the preview modal is open for a non-text file (image, PDF, binary, .docx, .msg) WHEN the header renders THEN it displays: filename (left), and a toolbar group (right) containing download icon and close button only (no toggle icon) | UI |
| AC-038-C.06c | GIVEN the preview modal is showing any file WHEN user clicks the download icon THEN the browser downloads the file using the original filename | Unit |
| AC-038-C.06d | GIVEN the preview is in preview mode WHEN user clicks the toggle icon THEN the content re-renders as raw plain text in `<pre>` (no markdown rendering, no syntax highlighting) AND the toggle icon updates to indicate raw mode is active | UI |
| AC-038-C.06e | GIVEN the preview is in raw mode WHEN user clicks the toggle icon THEN the content re-renders in preview mode (markdown rendered as HTML, code syntax-highlighted) AND the toggle icon updates to indicate preview mode is active | UI |
| AC-038-C.06f | GIVEN a file path containing `/src/` as a path segment WHEN the preview modal opens THEN the default mode is raw AND the toggle icon indicates raw mode | Unit |
| AC-038-C.06g | GIVEN a file path NOT containing `/src/` as a path segment WHEN the preview modal opens THEN the default mode is preview AND the toggle icon indicates preview mode | Unit |
| AC-038-C.06h | GIVEN the preview modal with toggle icon WHEN the user toggles between modes THEN the FilePreviewRenderer re-renders without re-fetching the file content from the API | Unit |
| AC-038-C.06i | GIVEN the user has toggled to raw mode on file A WHEN the user selects a different file B THEN file B opens in its own default mode (smart defaults applied independently) AND the toggle state from file A is NOT carried over | Unit |
| AC-038-C.06j | GIVEN a file under `/src/` path (e.g., `src/x_ipe/app.py`) WHEN the file type is non-text (e.g., `src/images/logo.png`) THEN the `/src/` smart default is ignored AND the toggle icon is hidden (non-text rules take precedence) | Unit |

## Functional Requirements

**FR-038-C.1: Folder Detection in Deliverable Rendering**
- Input: Deliverable item from `/api/workflow/{name}/deliverables` response
- Process: Check if `item.path` ends with `/`. If yes, render as folder-type card with expand button.
- Output: Folder card with expand toggle, or standard file card

**FR-038-C.2: Folder Contents API**
- Input: Folder path relative to project root
- Process: Use existing `GET /api/ideas/folder-contents?path={folder_path}` or extend deliverables endpoint to support folder listing
- Output: JSON array of `{name, type: 'file'|'dir', path}` entries

**FR-038-C.3: File-Tree DOM Construction**
- Input: Folder contents array
- Process: Build nested `<ul>` structure with `<li>` for each entry. Directories get collapse/expand toggle. Files get click handler for preview.
- Output: DOM subtree appended below deliverable card

**FR-038-C.4: Inline Preview Loading**
- Input: File path from tree item click
- Process: Call `GET /api/ideas/file?path={file_path}`. Check response content type: if `text/html` with `X-Converted: true` header, render as HTML in sandboxed container. If plain text, render: markdown → `marked.parse()`, other text → `<pre>`. If 415 (unconvertible binary), show message.
- Output: Preview pane with rendered content

**FR-038-C.5: Path Scoping Validation**
- Input: Requested file/folder path
- Process: Validate that resolved path is a descendant of the deliverable's base folder. Reject path traversal attempts (`../`).
- Output: Valid path proceeds; invalid path shows error

**FR-038-C.6: .docx File Conversion (CR-001)**
- Input: File path with `.docx` extension
- Process: Read file as binary, pass to `mammoth.convert_to_html()`. Sanitize output HTML with BeautifulSoup (strip `<script>`, `<iframe>`, `on*` event attributes). Return as `text/html` with `X-Converted: true` header.
- Output: Clean HTML string representing the document content

**FR-038-C.7: .msg File Conversion (CR-001)**
- Input: File path with `.msg` extension
- Process: Open with `extract_msg.openMsg()`. Extract From, To, CC, Date, Subject, Body fields. Render into an HTML template with labeled sections. Sanitize body HTML. Return as `text/html` with `X-Converted: true` header.
- Output: Structured HTML with email metadata and body

**FR-038-C.8: Conversion Size Guard (CR-001)**
- Input: File path for .docx or .msg
- Process: Check file size before conversion. If > 10MB, return error response without attempting conversion.
- Output: 413 status with "File too large to preview" message, or proceed to conversion

**FR-038-C.9: Download from Preview Header (CR-002)**
- Input: File path of currently previewed file
- Process: Render a download `<a>` element in the preview header with `href` pointing to `GET /api/ideas/file?path={file}` and `download` attribute set to filename
- Output: Clicking the icon triggers native browser file download

**FR-038-C.10: Preview/Raw Toggle (CR-002)**
- Input: Toggle icon click event; file type classification from FilePreviewRenderer
- Process: Toggle is only rendered for text-renderable file types (markdown, code, html). For non-text types (image, pdf, binary, converted .docx/.msg), the toggle icon is omitted from the header. When visible and clicked, switch `FilePreviewRenderer` render mode between `auto` (type-detected preview) and `raw` (plain `<pre>` text). Re-render content without re-fetching from API. Toggle state resets to the smart default when a different file is opened.
- Output: Content area updates to show rendered or raw view; toggle icon updates to reflect current mode

**FR-038-C.11: Smart Default Mode (CR-002)**
- Input: File path opened in preview modal
- Process: Check if path contains `/src/` as a path segment (regex `/\/src\//`). If match → set initial render mode to `raw`. Otherwise → set to `auto` (preview).
- Output: Preview opens in the appropriate default mode based on file location

## Non-Functional Requirements

- **NFR-038-C.1:** File-tree render must complete within 500ms for folders with up to 50 files
- **NFR-038-C.2:** File preview fetch and render must complete within 1s for text files up to 100KB
- **NFR-038-C.3:** No additional JS libraries — uses native DOM + existing `marked.js`
- **NFR-038-C.4 (CR-001):** .docx/.msg conversion must complete within 3s for files up to 10MB
- **NFR-038-C.5 (CR-001):** Converted HTML must be sanitized server-side (BeautifulSoup) — no script execution, no iframes, no event handlers in output

## UI/UX Requirements

### Components (from mockup Scene 4)

| Component | Description | Behavior |
|-----------|-------------|----------|
| Folder Card | Deliverable card with expand toggle (▸/▾) | Click header to expand/collapse tree |
| File-Tree | Nested `<ul>` with folder/file icons | Directories collapsible, files clickable |
| Preview Pane | Below tree, shows file content | Markdown rendered, text as preformatted |
| Preview Header | File name above content | Shows active file name |

### Components (CR-002: Preview Header Toolbar)

| Component | Description | Behavior |
|-----------|-------------|----------|
| Preview Header (updated) | Flex row: filename (left) + toolbar group (right) | Layout uses `display: flex; justify-content: space-between; align-items: center` |
| Download Icon | `<a>` element with download emoji/icon (⬇️) | Click triggers native browser file download. Visible for ALL file types. Styled as small button with hover background. |
| Preview/Raw Toggle | Icon button: `👁️` (preview mode) / `</>` (raw mode) | Click toggles render mode. Only visible for text-renderable files (markdown, code, html). Hidden for images, PDF, binary, .docx, .msg. Has `title` tooltip showing current mode name. |
| Close Button | Existing `✕` span | Click closes the modal (unchanged) |
| Toolbar Group | `<span>` wrapper for download + toggle + close | `display: flex; align-items: center; gap: 8px`. Groups right-aligned icons. |

### User Flow

```
1. User sees deliverable card for folder-type output (e.g., "refined-idea/")
2. User clicks expand toggle on the card
3. File-tree loads and shows folder contents
4. User clicks a .md file in the tree
5. Preview pane appears below tree with rendered markdown
6. User clicks a different file — preview updates
7. User clicks collapse toggle — tree and preview collapse
```

### User Flow (CR-002: Single-File Preview Modal)

```
1. User clicks a single-file deliverable card (e.g., "technical-design.md")
2. Modal opens with preview header: filename | [⬇️] [👁️] [✕]
3. File renders in default mode:
   - Files NOT under /src/ → preview mode (markdown rendered, code highlighted)
   - Files under /src/ → raw mode (plain text)
4. User clicks ⬇️ → file downloads via browser
5. User clicks 👁️↔</> → content toggles between preview and raw mode
6. User clicks a different file (if in folder browser context):
   - Toggle resets to the new file's smart default
   - Toggle visibility updates (hidden if new file is image/PDF/binary)
7. User clicks ✕ or backdrop or Escape → modal closes
```

## Dependencies

### Internal

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-036-E | CR target | Deliverables, Polling & Lifecycle — base card grid being extended |
| `GET /api/ideas/file` | Data source | File content retrieval for preview |
| `GET /api/ideas/folder-contents` | Data source | Folder listing for tree |
| `marked.js` | Rendering | Already loaded globally for markdown rendering |
| `FilePreviewRenderer` (CR-002) | Shared component | Needs `renderMode` extension for raw/auto toggle support. Shared by KB browse, folder browser, deliverable viewer. |

### External

- **mammoth (CR-001)** — Python library for .docx → HTML conversion
- **extract-msg (CR-001)** — Python library for .msg email extraction

## Business Rules

- **BR-038-C.1:** Folder detection is based solely on trailing `/` in the path — no filesystem stat.
- **BR-038-C.2:** File-tree only shows the immediate folder and its descendants — no parent navigation.
- **BR-038-C.3:** Preview supports text-based files AND convertible binary formats (`.docx`, `.msg`). Unconvertible binary files show a placeholder message. (Updated by CR-001)
- **BR-038-C.4 (CR-001):** Conversion is server-side only — no client-side parsing libraries. The frontend receives ready-to-render HTML.
- **BR-038-C.5 (CR-001):** Only `.docx` and `.msg` are convertible formats. Other Office formats (`.doc`, `.xls`, `.pptx`) remain unconvertible and show the binary placeholder.
- **BR-038-C.6 (CR-002):** The smart default mode uses path-segment matching (`/src/` in path), not prefix matching. Paths like `src_backup/file.js` do NOT match.
- **BR-038-C.7 (CR-002):** Raw mode shows the unprocessed file content as plain text in `<pre>`. No markdown rendering, no syntax highlighting, no HTML iframe rendering.
- **BR-038-C.8 (CR-002):** Toggle visibility is determined by file type classification: text-renderable types (markdown, code, html) show the toggle; non-text types (image, pdf, binary, server-converted) hide it.
- **BR-038-C.9 (CR-002):** Toggle state does not persist across files. Each file opens in its own smart default mode.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty folder deliverable | Tree shows "No files" message |
| Folder with >50 files | Show first 50 with "N more files..." truncation message |
| Nested folders 3+ levels deep | Tree renders all levels (no depth limit) |
| File with no extension | Preview as plain text |
| Large text file (>100KB) | Show first 100KB with "File truncated" message |
| Folder path doesn't exist on disk | Card shows "⚠️ folder not found" (same as existing missing file pattern) |
| Path traversal attempt (`../../etc/passwd`) | Rejected by path scoping validation, shows error |
| Corrupted .docx file (CR-001) | Conversion fails gracefully — shows "Preview unavailable for this file" |
| Password-protected .docx (CR-001) | Conversion fails gracefully — shows "Preview unavailable for this file" |
| .msg with HTML body (CR-001) | HTML body sanitized and rendered; plain text body rendered in `<pre>` |
| .msg with no body (CR-001) | Shows metadata headers only (From, To, Subject, Date) with empty body |
| .docx/.msg > 10MB (CR-001) | Shows "File too large to preview (max 10MB)" without attempting conversion |
| Toggle on image/PDF file (CR-002) | Toggle icon hidden — only download and close buttons in header |
| Toggle on .docx/.msg file (CR-002) | Toggle icon hidden — converted content is always rendered as preview (server-side HTML) |
| File under /src/ that is an image (CR-002) | `/src/` smart default ignored — non-text rule takes precedence, toggle hidden |
| User rapidly toggles raw/preview (CR-002) | Debounce re-render — only process latest toggle state |
| File with unknown extension under /src/ (CR-002) | Treated as text (existing behavior), defaults to raw mode per smart default |
| Toggle then download (CR-002) | Download always serves the original file regardless of current toggle mode |

## Out of Scope

- **File editing** — preview is read-only
- **~~File download~~** — ~~no download button~~ (Moved in-scope by CR-002: download icon added to preview header)
- **Image/unconvertible binary preview** — only text-based and convertible formats (.docx, .msg) are supported (Updated by CR-001)
- **File search within tree** — browse only
- **Syntax highlighting** — plain preformatted text for code files
- **Other Office formats (CR-001)** — `.doc`, `.xls`, `.xlsx`, `.ppt`, `.pptx` remain unsupported
- **.msg attachments (CR-001)** — email attachments are not extracted or previewed
- **Raw mode for binary files (CR-002)** — raw toggle only applies to text-renderable files; binary files always show placeholder

## Technical Considerations

- Extend `_renderDeliverables()` in `workflow-stage.js` to detect folder-type and call new `_renderFolderDeliverable()` method
- File-tree CSS: simple nested `<ul>` with `padding-left` indentation, `cursor: pointer` on items
- Preview pane: `<div class="deliverable-preview">` with content area, positioned below tree
- Reuse `GET /api/ideas/folder-contents` for tree data — may need to pass full relative path (not just ideas folder)
- `marked.js` already loaded globally — no additional setup needed
- **(CR-001)** Backend conversion layer intercepts `.docx`/`.msg` extensions in `/api/ideas/file` before the UTF-8 decode attempt
- **(CR-001)** Converted HTML returned with `X-Converted: true` response header so frontend knows to render as HTML
- **(CR-001)** `beautifulsoup4` (already a dependency) used for HTML sanitization of converted output
- **(CR-001)** Frontend renders converted HTML in the existing HTML preview path (sandboxed container)
- **(CR-002)** Extend `FilePreviewRenderer` with `renderMode` option (`auto` | `raw`): `auto` = current behavior; `raw` = plain `<pre>` text
- **(CR-002)** Add `setRenderMode(mode)` method to FilePreviewRenderer for runtime toggle without re-fetch
- **(CR-002)** Download icon in preview header uses `<a download>` pattern from folder-browser-modal.js `_makePreviewHeader`
- **(CR-002)** Smart default detection: `filePath.match(/\/src\//)` — simple regex on path string
- **(CR-002)** Toggle icon states: preview mode = `👁️` (eye); raw mode = `</>` (code brackets)

## Open Questions

None.
