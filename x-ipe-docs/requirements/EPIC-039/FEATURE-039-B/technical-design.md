# Technical Design: FEATURE-039-B — Enhanced Modal Features

> Feature ID: FEATURE-039-B
> Version: v1.0
> Last Updated: 03-04-2026

## Part 1: Agent-Facing Summary

### Component Table

| # | Component | File | Change | Tag |
|---|-----------|------|--------|-----|
| C1 | Modal JS | `src/x_ipe/static/js/features/folder-browser-modal.js` | Modify | `frontend` |
| C2 | Modal CSS | `src/x_ipe/static/css/features/folder-browser-modal.css` | Modify | `frontend` |
| C3 | Tests | `tests/frontend-js/folder-browser-modal.test.js` | Create/Modify | `test` |

All changes are frontend-only (vanilla JS + CSS). No backend changes needed.

## Part 2: Implementation Guide

### C1: folder-browser-modal.js Changes

**1. ICON_MAP constant** — Add after BINARY_EXTENSIONS:
```javascript
static FILE_ICONS = {
    md: '📝',
    png: '🖼️', jpg: '🖼️', jpeg: '🖼️', gif: '🖼️', svg: '🖼️', webp: '🖼️',
    js: '💻', py: '💻', ts: '💻', css: '💻', html: '💻', htm: '💻',
    json: '💻', yaml: '💻', yml: '💻', sh: '💻',
};
static IMAGE_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']);
static MAX_TEXT_SIZE = 1_048_576; // 1MB
```

**2. _createDOM()** — Add ARIA, breadcrumb, search:
- Modal: `role="dialog"`, `aria-modal="true"`, `aria-labelledby="folder-browser-title"`
- Title: add `id="folder-browser-title"`
- After header: add breadcrumb div `.folder-browser-breadcrumb`
- Tree panel: add search input at top, `tabindex="0"`
- Preview panel: `tabindex="0"`
- Tree root `<ul>`: `role="tree"`

**3. _getFileIcon(name)** — New method:
```javascript
_getFileIcon(name) {
    const ext = name.split('.').pop()?.toLowerCase();
    return FolderBrowserModal.FILE_ICONS[ext] || '📄';
}
```

**4. _buildSimpleTree()** — Use typed icons, add `role="treeitem"`:
- Replace `📄` with `this._getFileIcon(e.name)`
- Add `li.setAttribute('role', 'treeitem')`

**5. _wireTreeHandlers()** — Add ARIA to dynamically loaded trees:
- Set `role="tree"` on root `<ul>` if not set
- Set `role="treeitem"` on each `<li>`

**6. _updateBreadcrumb(folderPath)** — New method:
- Parse path into segments
- If >5 segments: show first + "…" + last 3
- Render clickable spans
- Click handler calls `_loadTree(pathUpToSegment)` + `_updateBreadcrumb()`

**7. _setupSearch()** — New method:
- Debounced input handler (200ms)
- Walk tree DOM: hide non-matching `.tree-item`, show matching + ancestors
- Empty query: show all
- No matches: show "No matching files" message

**8. _selectFile()** — Enhance:
- Image detection: if IMAGE_EXTENSIONS, render `<img>` instead of text fetch
- Download button in preview header
- Large file check: if content.length > MAX_TEXT_SIZE, show truncation message

**9. _renderBinaryMessage()** — Enhance:
- Show file name, extension, file type info
- Add functional download button

**10. _renderPreview()** — Add download button to header

**11. _setupKeyboard()** — New method:
- Tree panel keydown: ArrowUp/Down navigates items, Enter selects
- Track focused index within `.tree-item` elements

**12. Empty folder text** — Change to "This folder is empty"

### C2: folder-browser-modal.css Changes

Add styles for: search input, breadcrumb, download button, image preview, keyboard focus indicators.

### Implementation Order

1. ARIA roles + empty folder text (minimal, non-breaking)
2. Typed file icons
3. Download button
4. Image preview
5. Large file handling + binary enhancement
6. Breadcrumb navigation
7. Search/filter
8. Keyboard navigation
9. CSS additions
10. Tests
