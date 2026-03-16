# Technical Design: Enhanced Deliverable Viewer

> Feature ID: FEATURE-038-C | Version: v1.1 | Last Updated: 03-16-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.1 | 03-16-2026 | CR-001: Add .docx/.msg server-side conversion to HTML for inline preview |
| v1.0 | 02-20-2026 | Initial design: folder-type deliverables with file-tree and inline preview |

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating large projects.
> **📌 AI Coders:** Focus on this section for implementation context.

### Key Components Implemented

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| `_renderFolderDeliverable()` | Render file-tree for folder deliverables | workflow-stage.js | #deliverables #filetree #frontend |
| `_renderFilePreview()` | Inline file preview pane | workflow-stage.js | #deliverables #preview #markdown |
| `GET /api/workflow/{name}/deliverables/tree` | Folder contents endpoint | Backend API | #api #deliverables #backend |
| `_convert_docx()` (CR-001) | Convert .docx to HTML via mammoth | ideas_routes.py helper | #conversion #docx #mammoth #preview |
| `_convert_msg()` (CR-001) | Convert .msg to structured HTML via extract-msg | ideas_routes.py helper | #conversion #msg #email #preview |
| `_sanitize_converted_html()` (CR-001) | Strip scripts/iframes/event handlers from converted HTML | ideas_routes.py helper | #security #sanitization #beautifulsoup |
| `get_idea_file()` modified (CR-001) | Add conversion branch before UTF-8 fallback | ideas_routes.py route | #api #preview #conversion |
| `showPreview()` modified (CR-001) | Detect `X-Converted` header → render as sandboxed HTML | deliverable-viewer.js | #frontend #preview #iframe |

### Dependencies

| Dependency | Source | Design Link | Usage Description |
|------------|--------|-------------|-------------------|
| `_renderDeliverables()` | FEATURE-036-E | `src/x_ipe/static/js/features/workflow-stage.js` | Existing deliverable grid being extended |
| `GET /api/ideas/file` | FEATURE-037-B | `src/x_ipe/routes/ideas_routes.py` | File content retrieval for preview |
| `marked.js` | Foundation | `src/x_ipe/static/3rdparty/js/marked.min.js` | Markdown rendering for .md files |
| `GET /api/workflow/{name}/deliverables` | FEATURE-036-E | `src/x_ipe/routes/workflow_routes.py` | Existing deliverables API |
| `beautifulsoup4` (CR-001) | pyproject.toml | N/A (existing dep) | HTML sanitization of converted output |
| `mammoth` (CR-001) | PyPI (new) | N/A | .docx → HTML conversion |
| `extract-msg` (CR-001) | PyPI (new) | N/A | .msg email metadata + body extraction |

### Major Flow

1. Deliverables grid renders → for each deliverable, check if path ends with `/`
2. If folder-type → render card with expand toggle (▸) instead of standard file card
3. User clicks expand → fetch folder contents via API → build nested `<ul>` tree
4. User clicks file in tree → fetch file content via `GET /api/ideas/file` → render preview
5. Markdown files rendered via `marked.parse()`, text files shown as `<pre>`
6. **(CR-001)** `.docx`/`.msg` files → backend converts to HTML → returns with `X-Converted: true` header → frontend renders in sandboxed `<iframe>`
7. **(CR-001)** On conversion error or oversized file → backend returns 413/415 → frontend shows appropriate message

### Usage Example

```javascript
// In _renderDeliverables():
if (item.path.endsWith('/')) {
  card = this._renderFolderDeliverable(item, wfName);
} else {
  card = this._renderFileDeliverable(item); // existing
}

// Folder tree expansion:
async _expandFolderTree(card, folderPath, wfName) {
  const resp = await fetch(`/api/workflow/${wfName}/deliverables/tree?path=${encodeURIComponent(folderPath)}`);
  const entries = await resp.json();
  const tree = this._buildTreeDOM(entries);
  card.appendChild(tree);
}
```

```python
# CR-001: Backend conversion in get_idea_file()
ext = target.suffix.lower()
if ext in CONVERTIBLE_EXTENSIONS:
    file_size = target.stat().st_size
    if file_size > MAX_CONVERSION_SIZE:
        return jsonify({'error': 'File too large to preview (max 10MB)'}), 413
    html = _convert_docx(target)  # or _convert_msg(target)
    html = _sanitize_converted_html(html)
    return html, 200, {'Content-Type': 'text/html; charset=utf-8', 'X-Converted': 'true'}
```

```javascript
// CR-001: Frontend X-Converted detection in showPreview()
if (resp.headers.get('X-Converted') === 'true') {
    const blob = new Blob([text], { type: 'text/html' });
    const iframe = document.createElement('iframe');
    iframe.src = URL.createObjectURL(blob);
    iframe.setAttribute('sandbox', 'allow-same-origin');
    content.appendChild(iframe);
    return;
}
```

---

## Part 2: Implementation Guide

> **Purpose:** Human-readable details for developers.

### Workflow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant WS as WorkflowStage
    participant DV as DeliverableViewer
    participant API as Backend API
    participant FS as FileSystem

    WS->>WS: _renderDeliverables()
    WS->>WS: Detect folder path (ends with /)
    WS->>WS: _renderFolderDeliverable() with expand toggle

    U->>WS: Click expand toggle
    WS->>API: GET /api/workflow/{name}/deliverables/tree?path=...
    API->>FS: List directory contents
    FS-->>API: File entries
    API-->>WS: [{name, type, path}]
    WS->>WS: Build <ul> tree DOM

    U->>DV: Click file in tree
    DV->>API: GET /api/ideas/file?path=...
    API->>FS: Read file content
    FS-->>API: File text
    API-->>DV: File content
    DV->>DV: _renderFilePreview() (marked.parse for .md, <pre> for others)
```

### CR-001: Conversion Flow Diagram

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant FE as deliverable-viewer.js
    participant BE as ideas_routes.py
    participant M as mammoth
    participant E as extract-msg
    participant BS as BeautifulSoup

    U->>FE: Click .docx/.msg file
    FE->>BE: GET /api/ideas/file?path=doc.docx
    BE->>BE: Check extension → convertible
    BE->>BE: Check file size ≤ 10MB

    alt .docx file
        BE->>M: mammoth.convert_to_html(file)
        M-->>BE: HTML result
    else .msg file
        BE->>E: extract_msg.openMsg(file)
        E-->>BE: Message object (from, to, subject, body)
        BE->>BE: Render to HTML template
    end

    BE->>BS: sanitize(html) — strip scripts, iframes, on* attrs
    BS-->>BE: Clean HTML
    BE-->>FE: 200 OK + text/html + X-Converted: true
    FE->>FE: Detect X-Converted header
    FE->>U: Render in sandboxed iframe (no scripts)
```

### CR-001: Error Flow

```mermaid
flowchart TD
    A[User clicks file] --> B{Extension?}
    B -->|.docx / .msg| C{Size ≤ 10MB?}
    B -->|other binary| H[415 → Binary file — cannot preview]
    B -->|text file| I[200 → existing text preview]
    C -->|No| D[413 → File too large to preview]
    C -->|Yes| E{Conversion succeeds?}
    E -->|Yes| F[200 + X-Converted: true → sandboxed iframe]
    E -->|No| G[415 → Preview unavailable for this file]
```

### CR-001: Module Diagram

```mermaid
classDiagram
    class ideas_routes {
        +get_idea_file() Flask route
        -_convert_docx(path) str
        -_convert_msg(path) str
        -_sanitize_converted_html(html) str
        -CONVERTIBLE_EXTENSIONS set
        -MAX_CONVERSION_SIZE int
    }

    class DeliverableViewer {
        +showPreview(filePath) void
    }

    class mammoth {
        +convert_to_html(file) Result
    }

    class extract_msg {
        +openMsg(path) Message
    }

    class BeautifulSoup {
        +find_all(tags) list
        +decompose() void
    }

    ideas_routes --> mammoth : .docx conversion
    ideas_routes --> extract_msg : .msg extraction
    ideas_routes --> BeautifulSoup : HTML sanitization
    DeliverableViewer --> ideas_routes : GET /api/ideas/file
```

### UI Component Structure (from Mockup Scene 4)

```
.deliverable-card.folder-type
├── .deliverable-card-header (click → toggle tree)
│   ├── .toggle-icon (▸/▾)
│   ├── 📁 icon
│   ├── .deliverable-name (folder name)
│   └── .deliverable-path (full path, monospace)
├── .deliverable-tree (hidden initially)
│   └── ul.file-tree
│       ├── li.tree-item.folder
│       │   ├── .toggle-icon + 📁 + name
│       │   └── ul.file-tree (nested, collapsed)
│       └── li.tree-item.file (click → preview)
│           └── 📄 + name
└── .deliverable-preview (hidden initially)
    ├── .preview-header (file name)
    └── .preview-content (rendered HTML or <pre>)
```

### Backend API

#### `GET /api/workflow/{name}/deliverables/tree`

```python
@workflow_bp.route('/api/workflow/<name>/deliverables/tree', methods=['GET'])
def get_deliverable_tree(name):
    """
    Query params: path (required) - Relative folder path from project root
    
    Response 200:
    [
      {"name": "idea-summary.md", "type": "file", "path": "x-ipe-docs/ideas/.../refined-idea/idea-summary.md"},
      {"name": "mockups", "type": "dir", "path": "x-ipe-docs/ideas/.../refined-idea/mockups/"}
    ]
    
    Security: Validate path is within project root (no traversal)
    Limit: Return max 50 entries per folder level
    """
```

### Implementation Steps

1. **Backend:** Add `GET /api/workflow/{name}/deliverables/tree` endpoint in `workflow_routes.py`
   - List directory contents (files + subdirs)
   - Validate path is within project root
   - Limit to 50 entries per level
   - Return `[{name, type, path}]` JSON

2. **Frontend — Folder Detection:**
   - In `_renderDeliverables()`, check `item.path.endsWith('/')` 
   - Route to `_renderFolderDeliverable()` for folder-type

3. **Frontend — File-Tree:**
   - `_renderFolderDeliverable(item, wfName)` creates card with expand toggle
   - On expand click: fetch tree → `_buildTreeDOM(entries)` → append
   - Nested folders collapse/expand on click

4. **Frontend — Preview:**
   - `_renderFilePreview(filePath, container)` fetches file content
   - `.md` files → `marked.parse(content)` → inject HTML
   - Other text files → `<pre>${escaped(content)}</pre>`
   - Binary files (415 response) → "Binary file" message

5. **CSS:** Add styles for `.folder-type`, `.file-tree`, `.deliverable-preview`, `.tree-item`

### CR-001: Modified API — `GET /api/ideas/file`

Existing behavior preserved. New conversion branch added for `.docx` and `.msg` extensions.

**New Response (200 — converted):**

| Header | Value |
|--------|-------|
| `Content-Type` | `text/html; charset=utf-8` |
| `X-Converted` | `true` |

Body: Sanitized HTML string (no wrapping JSON).

**New Response (413 — too large):**

```json
{"error": "File too large to preview (max 10MB)"}
```

**Complete status code mapping:**

| Status | Condition |
|--------|-----------|
| 200 | Text file (existing) or converted binary (new) |
| 400 | Missing `path` parameter |
| 403 | Path outside project root |
| 404 | File not found |
| 413 | Convertible file > 10MB (new) |
| 415 | Unconvertible binary OR conversion failure |

### CR-001: Constants

```python
CONVERTIBLE_EXTENSIONS = {'.docx', '.msg'}
MAX_CONVERSION_SIZE = 10 * 1024 * 1024  # 10MB
```

### CR-001: .msg HTML Template

```html
<div class="msg-preview">
  <table class="msg-headers">
    <tr><td><strong>From:</strong></td><td>{sender}</td></tr>
    <tr><td><strong>To:</strong></td><td>{to}</td></tr>
    <tr><td><strong>CC:</strong></td><td>{cc}</td></tr>
    <tr><td><strong>Date:</strong></td><td>{date}</td></tr>
    <tr><td><strong>Subject:</strong></td><td>{subject}</td></tr>
  </table>
  <hr>
  <div class="msg-body">{body_html_or_pre_text}</div>
</div>
```

### CR-001: Implementation Steps

1. **Backend — Add dependencies:** Add `mammoth` and `extract-msg` to `pyproject.toml` dependencies. Run `uv sync`.

2. **Backend — Add helper functions to `ideas_routes.py`:**
   - `_convert_docx(file_path: Path) -> str` — opens file as binary, calls `mammoth.convert_to_html()`, returns `result.value`
   - `_convert_msg(file_path: Path) -> str` — opens with `extract_msg.openMsg()`, extracts metadata (sender, to, cc, date, subject), extracts body (prefer htmlBody, fallback to plain text in `<pre>`), renders into HTML template, closes message object
   - `_sanitize_converted_html(html: str) -> str` — parses with BeautifulSoup, removes `<script>`, `<iframe>`, `<object>`, `<embed>` tags, strips `on*` event attributes from all tags, returns cleaned string

3. **Backend — Modify `get_idea_file()` in `ideas_routes.py`:**
   - Add conversion branch AFTER the `send_file` check for images/PDFs but BEFORE the `try: read_text(encoding='utf-8')` block
   - Check `target.suffix.lower() in CONVERTIBLE_EXTENSIONS`
   - If yes: check file size against `MAX_CONVERSION_SIZE` → 413 if too large
   - Call `_convert_docx()` or `_convert_msg()` based on extension
   - Sanitize result with `_sanitize_converted_html()`
   - Return with `Content-Type: text/html; charset=utf-8` and `X-Converted: true` header
   - Wrap in try/except — any exception returns 415 with "Preview unavailable for this file"

4. **Frontend — Modify `showPreview()` in `deliverable-viewer.js`:**
   - After `const text = await resp.text();` and BEFORE the extension-based dispatch
   - Add: `if (resp.headers.get('X-Converted') === 'true') { ... }`
   - Inside: create Blob with type `text/html`, create iframe with `sandbox='allow-same-origin'` (NO `allow-scripts`), append to content container, return early
   - Also handle 413 status: show "File too large to preview" alongside existing 415 handler

5. **Tests — Backend unit tests:**
   - `_convert_docx()` with small valid .docx fixture
   - `_convert_msg()` with small valid .msg fixture
   - `_sanitize_converted_html()` strips scripts, iframes, on* attributes
   - Route test: .docx returns 200 with X-Converted header
   - Route test: oversized .docx returns 413
   - Route test: corrupted .docx returns 415

6. **Tests — Frontend unit tests:**
   - showPreview detects X-Converted header and renders iframe
   - showPreview handles 413 status with correct message
   - Existing 415 handling unchanged for non-convertible binary

### CR-001: Line Count Impact

| File | Current Lines | Added Lines | Total | Under 800? |
|------|--------------|-------------|-------|------------|
| `ideas_routes.py` | 695 | ~50 | ~745 | ✅ Yes |
| `deliverable-viewer.js` | 257 | ~15 | ~272 | ✅ Yes |

### CR-001: Security Considerations

1. **Path traversal** — already handled by existing `resolve()` + `startswith()` check
2. **HTML sanitization** — BeautifulSoup removes `<script>`, `<iframe>`, `<object>`, `<embed>` tags and all `on*` event attributes
3. **Frontend sandbox** — converted HTML in `<iframe sandbox="allow-same-origin">` without `allow-scripts` (stricter than regular .html preview)
4. **No code execution** — mammoth and extract-msg are read-only parsers; no macro execution
5. **Size guard** — 10MB limit prevents memory exhaustion

### CR-001: Modified Files

- `pyproject.toml` — Add mammoth, extract-msg dependencies
- `src/x_ipe/routes/ideas_routes.py` — Add `_convert_docx()`, `_convert_msg()`, `_sanitize_converted_html()`, modify `get_idea_file()`
- `src/x_ipe/static/js/features/deliverable-viewer.js` — Add X-Converted detection + 413 handling in `showPreview()`

### File Tree CSS

```css
.file-tree {
  list-style: none;
  padding-left: 1.2rem;
  margin: 0;
}

.tree-item {
  padding: 2px 0;
  cursor: pointer;
  white-space: nowrap;
}

.tree-item.file:hover {
  background: var(--bg-hover);
  border-radius: 3px;
}

.deliverable-preview {
  border-top: 1px solid var(--border-color);
  padding: 0.75rem;
  max-height: 400px;
  overflow-y: auto;
}

.preview-header {
  font-weight: 600;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
}
```

### Modified Files

- `src/x_ipe/static/js/features/workflow-stage.js` — Add `_renderFolderDeliverable()`, `_buildTreeDOM()`, `_renderFilePreview()`
- `src/x_ipe/routes/workflow_routes.py` — Add deliverable tree endpoint
- `src/x_ipe/static/css/workflow-stage.css` — Add file-tree and preview styles

### Edge Cases & Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty folder | Show "No files" message in tree |
| >50 files in folder | Show first 50 + "N more files..." |
| Nested 3+ levels | All levels render (no limit) |
| File with no extension | Preview as plain text |
| Large file >100KB | Show first 100KB + "File truncated" |
| Folder doesn't exist | Show "⚠️ folder not found" |
| Path traversal attempt | Rejected by backend, show error |
| Binary file clicked | Show "Binary file" placeholder |
| Valid .docx (CR-001) | 200 + HTML + X-Converted → sandboxed iframe |
| Valid .msg (CR-001) | 200 + HTML email layout → sandboxed iframe |
| Corrupted .docx (CR-001) | 415 → "Preview unavailable for this file" (backend JSON); frontend shows generic "Binary file — cannot preview" for all 415s (see note below) |
| Password-protected .docx (CR-001) | 415 → "Preview unavailable for this file" (backend JSON); frontend shows generic "Binary file — cannot preview" for all 415s |
| .docx > 10MB (CR-001) | 413 → "File too large to preview (max 10MB)" |
| .msg with no body (CR-001) | Shows metadata headers with empty body |
| .msg with HTML body (CR-001) | Sanitized HTML body rendered |
| .msg with plain text body (CR-001) | Body in `<pre>` tag |
| mammoth import fails (CR-001) | 415 → "Preview unavailable for this file" |

> **Note (AC-038-C.04e vs actual):** The backend returns distinct error messages for conversion failures ("Preview unavailable for this file") vs unconvertible binaries ("Binary file — cannot read as text"), both as 415. However, the frontend does not parse the JSON body — it uses a single hardcoded message ("Binary file — cannot preview") for all 415 responses. AC-038-C.04e specifies the former message should surface to the user. This is a known simplification in the current frontend implementation.

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 03-16-2026 | Technical Design | CR-001: Added .docx/.msg conversion. Backend: 3 helper functions + conversion branch in get_idea_file(). Frontend: X-Converted header detection + sandboxed iframe. New deps: mammoth, extract-msg. |
| 02-20-2026 | Initial Design | Backend: folder listing endpoint. Frontend: folder detection in deliverables grid, file-tree DOM builder, inline preview with marked.js for markdown. |
