# Technical Design: Breadcrumb Navigation & Visual Distinction

> Feature ID: FEATURE-043-B
> Epic ID: EPIC-043
> Version: v1.0
> Last Updated: 03-04-2026
> Specification: [specification.md](x-ipe-docs/requirements/EPIC-043/FEATURE-043-B/specification.md)

---

## Part 1: Agent Summary

### Technical Scope

- **Scope:** [Frontend]
- **Complexity:** Medium
- **Estimated changes:** 3 files modified, 0 new files

### Architecture Decision

Extend the existing `LinkPreviewManager` class (from FEATURE-043-A) with navigation stack management and breadcrumb rendering. Add CSS-only visual distinction for internal links. No new classes or modules needed — this is a pure extension of existing code.

**Key Design Decisions:**
1. **Navigation stack** is a simple array `_navStack` on the singleton instance. Max 5 entries.
2. **Breadcrumb bar** is a new DOM row inserted between the header and content area.
3. **Back button** is added to the modal header (left of title).
4. **Visual distinction** is pure CSS using `a[data-preview-path]` selector — no JS changes for styling.
5. **Tooltip** is added at render-time in `content-renderer.js` by adding `title="Open preview"` to the custom link renderer.

### Class Diagram (Changes Only)

```
LinkPreviewManager (extended)
├── _navStack: Array<{path: string, title: string}>  // NEW
├── _backBtn: HTMLElement                              // NEW
├── _breadcrumbBar: HTMLElement                        // NEW
├── _maxDepth: number (5)                              // NEW
│
├── _createModal()          // MODIFIED — add back button + breadcrumb bar
├── open(filePath)          // MODIFIED — push to stack before loading new file
├── _navigateFromModal(path) // NEW — called when link inside modal is clicked
├── _goBack()               // NEW — pop stack and navigate
├── _goToBreadcrumb(index)  // NEW — truncate stack and navigate
├── _updateBreadcrumb()     // NEW — re-render breadcrumb bar
├── close()                 // MODIFIED — clear stack on close
└── attachTo(container)     // MODIFIED — pass source context (external vs modal)
```

### Sequence Diagram: Nested Navigation

```
User clicks internal link in modal
  → attachTo handler fires with e.target inside .link-preview-content
  → _navigateFromModal(path) called instead of open(path)
  → push current {path, title} to _navStack
  → if _navStack.length >= _maxDepth: replace instead of push
  → call open(newPath) internally
  → open() renders new content
  → _updateBreadcrumb() re-renders breadcrumb bar
  → _backBtn visibility updated
```

---

## Part 2: Implementation Guide

### Step 1: Add Navigation Stack Fields (link-preview-manager.js)

Add to constructor:
```javascript
this._navStack = [];      // Array of {path, title}
this._maxDepth = 5;
this._backBtn = null;
this._breadcrumbBar = null;
this._currentPath = null;  // Track current file path
```

### Step 2: Modify _createModal() — Add Back Button & Breadcrumb

After the existing header creation, insert:

```javascript
// Back button (left of title)
this._backBtn = document.createElement('span');
this._backBtn.className = 'link-preview-back';
this._backBtn.innerHTML = '← Back';
this._backBtn.style.display = 'none';
this._backBtn.addEventListener('click', () => this._goBack());
header.insertBefore(this._backBtn, this._titleEl);

// Breadcrumb bar (new row between header and content)
this._breadcrumbBar = document.createElement('div');
this._breadcrumbBar.className = 'link-preview-breadcrumb';
this._breadcrumbBar.style.display = 'none';
modal.insertBefore(this._breadcrumbBar, this._contentArea);
```

### Step 3: Modify open() — Track Current Path

In the `open()` method, save the path being viewed:
```javascript
this._currentPath = cleanPath;
```
After showing content, call `this._updateBreadcrumb()`.

### Step 4: Add _navigateFromModal(path) — Stack Push + Navigate

```javascript
_navigateFromModal(path) {
    if (this._currentPath) {
        if (this._navStack.length >= this._maxDepth) {
            // At max depth — replace current, don't push
        } else {
            this._navStack.push({
                path: this._currentPath,
                title: this._currentPath.split('/').pop()
            });
        }
    }
    this.open(path);
}
```

### Step 5: Add _goBack() — Pop Stack

```javascript
_goBack() {
    if (this._navStack.length === 0) return;
    const prev = this._navStack.pop();
    this.open(prev.path);
}
```

### Step 6: Add _goToBreadcrumb(index) — Truncate Stack

```javascript
_goToBreadcrumb(index) {
    const entry = this._navStack[index];
    this._navStack = this._navStack.slice(0, index);
    this.open(entry.path);
}
```

### Step 7: Add _updateBreadcrumb() — Render Breadcrumb Bar

```javascript
_updateBreadcrumb() {
    if (!this._breadcrumbBar) return;
    if (this._navStack.length === 0) {
        this._breadcrumbBar.style.display = 'none';
        this._backBtn.style.display = 'none';
        return;
    }
    this._breadcrumbBar.style.display = 'flex';
    this._backBtn.style.display = '';

    let html = '';
    this._navStack.forEach((entry, i) => {
        html += `<span class="breadcrumb-entry" data-index="${i}">${this._escapeHtml(entry.title)}</span>`;
        html += '<span class="breadcrumb-sep">›</span>';
    });
    html += `<span class="breadcrumb-current">${this._escapeHtml(this._currentPath.split('/').pop())}</span>`;
    this._breadcrumbBar.innerHTML = html;

    // Click handlers for breadcrumb entries
    this._breadcrumbBar.querySelectorAll('.breadcrumb-entry').forEach(el => {
        el.addEventListener('click', () => {
            this._goToBreadcrumb(parseInt(el.dataset.index));
        });
    });
}
```

### Step 8: Modify close() — Clear Stack

Add to `close()`:
```javascript
this._navStack = [];
this._currentPath = null;
if (this._breadcrumbBar) this._breadcrumbBar.style.display = 'none';
if (this._backBtn) this._backBtn.style.display = 'none';
```

### Step 9: Modify attachTo Click Handler — Detect Modal Context

In the delegated click handler inside `attachTo()`, distinguish between:
- Link clicked in page content → call `open(path)` (first-level, resets stack)
- Link clicked inside modal content → call `_navigateFromModal(path)` (pushes stack)

```javascript
container.addEventListener('click', (e) => {
    const link = e.target.closest('a[data-preview-path]');
    if (!link) return;
    e.preventDefault();
    const path = link.getAttribute('data-preview-path');
    const instance = LinkPreviewManager.instance;
    // If click is inside the modal content area, use navigate (preserves stack)
    if (instance._isOpen && instance._contentArea && instance._contentArea.contains(link)) {
        instance._navigateFromModal(path);
    } else {
        // Reset stack for fresh open
        instance._navStack = [];
        instance.open(path);
    }
});
```

### Step 10: Add Visual Distinction CSS (workflow.css)

```css
/* Visual distinction for internal preview links */
.markdown-body a[data-preview-path] {
    text-decoration: none;
    border-bottom: 1px dashed rgba(16, 185, 129, 0.3);
}
.markdown-body a[data-preview-path]::before {
    content: '📄 ';
    font-size: 0.85em;
}
.markdown-body a[data-preview-path]:hover {
    border-bottom: 1px dashed rgba(16, 185, 129, 0.6);
}
/* Exclude links inside code blocks */
.markdown-body pre a[data-preview-path],
.markdown-body code a[data-preview-path] {
    border-bottom: none;
}
.markdown-body pre a[data-preview-path]::before,
.markdown-body code a[data-preview-path]::before {
    content: none;
}
```

### Step 11: Add Breadcrumb CSS (workflow.css)

```css
.link-preview-breadcrumb {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 20px;
    font-size: 0.8rem;
    color: #64748b;
    border-bottom: 1px solid #e2e8f0;
    overflow-x: auto;
    white-space: nowrap;
}
.link-preview-breadcrumb::-webkit-scrollbar { display: none; }
.breadcrumb-entry {
    cursor: pointer;
    color: #3b82f6;
}
.breadcrumb-entry:hover { text-decoration: underline; }
.breadcrumb-sep { opacity: 0.4; font-size: 10px; margin: 0 2px; }
.breadcrumb-current { font-weight: 600; color: #1e293b; }

.link-preview-back {
    cursor: pointer;
    color: #3b82f6;
    margin-right: 12px;
    font-size: 0.85rem;
    white-space: nowrap;
}
.link-preview-back:hover { text-decoration: underline; }
```

### Step 12: Add title attribute to content-renderer.js

Modify the custom `renderer.link()` in `initMarked()`:
```javascript
// Change: always add title="Open preview" for internal links (unless already has title)
const safeTitle = title
    ? ` title="${title.replace(/"/g, '&quot;')}"`
    : ' title="Open preview"';
```

### Files Changed Summary

| File | Change | Lines |
|------|--------|-------|
| `src/x_ipe/static/js/features/link-preview-manager.js` | Add nav stack, back/breadcrumb, modify open/close/attachTo | ~80 lines added |
| `src/x_ipe/static/js/core/content-renderer.js` | Add default `title="Open preview"` | ~2 lines changed |
| `src/x_ipe/static/css/workflow.css` | Visual distinction + breadcrumb CSS | ~40 lines added |

### Risk Assessment

| Risk | Mitigation |
|------|------------|
| Stack overflow from circular links | Max depth cap at 5 |
| DOM memory from breadcrumb re-renders | innerHTML replacement clears old DOM |
| CSS specificity conflict with existing link styles | Use `a[data-preview-path]` attribute selector which is more specific |
| Breaking FEATURE-043-A tests | All changes are additive; existing test paths remain valid |
