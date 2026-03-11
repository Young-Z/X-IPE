# FEATURE-049-B: KB Sidebar & Navigation — Technical Design

## Part 1: Agent-Facing Summary

### Key Decision: Leverage Existing Sidebar Pipeline

The existing sidebar already handles folder tree rendering, expand/collapse, and file click navigation via `DEFAULT_SECTIONS` in `file_service.py` → `/api/project/structure` → `sidebar.js`. Rather than building a custom tree renderer, we INSERT the KB section into `DEFAULT_SECTIONS` and add minimal customizations.

### Components to Change

| # | Component | File | Change |
|---|-----------|------|--------|
| 1 | Section Config | `src/x_ipe/services/file_service.py` | Insert KB section between Planning and Requirements |
| 2 | Sidebar Renderer | `src/x_ipe/static/js/features/sidebar.js` | Add KB-specific rendering (Intake placeholder, empty state, drag-drop) |
| 3 | KB Sidebar CSS | `src/x_ipe/static/css/sidebar.css` | Add KB drag-drop styles (emerald dashed border) |
| 4 | KB Event Bridge | `src/x_ipe/static/js/features/sidebar.js` | Listen for `kb:changed` custom event to auto-refresh tree |

### Dependencies

- FEATURE-049-A: `GET /api/kb/tree`, `PUT /api/kb/files/move`, `PUT /api/kb/folders/move` (already implemented)
- Existing: `sidebar.js` render pipeline, `TreeDragManager`, `contentRenderer`, Bootstrap Collapse

### Architecture Decision: Simple > Custom

Using the existing pipeline means:
- ✅ Free: Section rendering, folder expand/collapse, chevron animation, file icons, file click → content load
- ✅ Free: Active state highlighting, breadcrumb update, change detection polling
- Add: Intake placeholder (5 lines HTML), drag-drop CSS (15 lines), `kb:changed` listener (10 lines)
- Add: Drop handler that calls KB move APIs instead of generic move

---

## Part 2: Implementation Guide

### Step 1: Add KB Section to DEFAULT_SECTIONS

In `file_service.py`, insert between Planning (`index 2`) and Requirements (`index 3`):

```python
{
    'id': 'knowledge-base',
    'label': 'Knowledge Base',
    'path': 'x-ipe-docs/knowledge-base',
    'icon': 'bi-book'
}
```

### Step 2: Customize sidebar.js for KB Section

In `renderSection()`, add KB-specific handling (similar to Workplace special case):

```javascript
if (section.id === 'knowledge-base') {
    // Render generic tree + append Intake placeholder + empty state
}
```

Key additions:
- After rendering children, append "📥 Intake" placeholder entry
- If no children and section doesn't exist, show "No articles yet" message
- Add `data-kb-folder="true"` attribute to KB folder items for drag-drop targeting

### Step 3: KB Drag-Drop in Sidebar

Add dragover/dragleave/drop event handlers specifically for KB folder items:
- On dragover: add `.kb-drag-over` class (emerald dashed border)
- On drop: call `PUT /api/kb/files/move` or `PUT /api/kb/folders/move`
- On dragleave: remove visual feedback
- Validate: prevent self-drop, prevent parent-into-child

### Step 4: Auto-Refresh on KB Changes

Listen for custom `kb:changed` event on `document`:
```javascript
document.addEventListener('kb:changed', () => {
    this.load(); // Re-fetch /api/project/structure
});
```

Dispatch `kb:changed` from KB route handlers (in fetch wrappers) after any write operation.

### Step 5: CSS for KB Drag-Drop

```css
.nav-item.kb-drag-over {
    border: 2px dashed #10b981 !important; /* emerald */
    background: rgba(16, 185, 129, 0.1) !important;
    border-radius: 6px;
}
```

### API Contracts Used

| Endpoint | Purpose | Already Exists |
|----------|---------|----------------|
| GET /api/project/structure | Sidebar tree (includes KB section) | ✅ Yes |
| GET /api/file/content?path= | File content on click | ✅ Yes |
| PUT /api/kb/files/move | Move file via drag-drop | ✅ FEATURE-049-A |
| PUT /api/kb/folders/move | Move folder via drag-drop | ✅ FEATURE-049-A |

### Test Strategy

Frontend tests (Vitest + jsdom):
- KB section appears in rendered sidebar HTML
- Intake placeholder present
- Empty state shown when no KB children
- Drag-drop CSS classes toggled correctly
- `kb:changed` event triggers re-render
- File click dispatches to content renderer

### Implementation Order

1. `file_service.py` — Add section config (1 min)
2. `sidebar.js` — Add KB rendering + Intake + empty state + drag-drop + auto-refresh (main work)
3. `sidebar.css` — Add KB drag-drop styles
4. Tests — Vitest test file for KB sidebar behavior
