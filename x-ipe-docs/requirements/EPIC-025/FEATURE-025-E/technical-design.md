# Technical Design: KB Search & Preview

> Feature ID: FEATURE-025-E  
> Version: v1.0  
> Last Updated: 02-19-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-19-2026 | Initial technical design |

---

## Part 1 — Agent-Facing Summary

### Scope

| Dimension | Value |
|-----------|-------|
| Program Type | fullstack |
| Tech Stack | Python/Flask, JavaScript/Vanilla, CSS |
| Feature ID | FEATURE-025-E |
| Files to Create | `src/x_ipe/static/js/features/kb-search.js`, `src/x_ipe/static/css/kb-search.css` |
| Files to Modify | `kb_routes.py`, `kb_manager_service.py`, `knowledge-base.html`, `kb-core.js` |
| Dependencies | FEATURE-025-A (kbCore), FEATURE-025-C (search API), FEATURE-025-D (topics) |

### Key Decisions

1. **New JS module** (`kb-search.js`) for search modal + preview panel — keeps `kb-core.js` under 800 lines
2. **New CSS file** (`kb-search.css`) for search modal and preview panel styles
3. **Extend existing search API** (`GET /api/kb/search`) with `type` and `topic` query params + grouped response
4. **Preview panel** replaces existing `kbCore.showFilePreview()` placeholder with dedicated panel in HTML template
5. **Search modal** is a global overlay (like mockup) created by JS, triggered by Cmd+K
6. **Client-side sidebar search highlighting** via `<mark>` tag wrapping in tree items

### Architecture

```
┌──────────────────────────────────────────────┐
│ knowledge-base.html                          │
│  ┌──────┐ ┌─────────────┐ ┌──────────────┐  │
│  │sidebar│ │ content-body│ │ preview-panel│  │
│  │ #kb-  │ │  (landing/  │ │  (360px,     │  │
│  │ search│ │   topics)   │ │   hidden by  │  │
│  └──────┘ └─────────────┘ │   default)   │  │
│                            └──────────────┘  │
│  ┌──────────────────────────────────────┐    │
│  │ Search Modal (Cmd+K overlay)        │    │
│  │  - Input + ESC hint                 │    │
│  │  - Grouped results                  │    │
│  │  - Filter chips                     │    │
│  │  - Keyboard nav (↑↓ Enter)         │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

### Data Flow

```
Sidebar Search:  input → kbCore.searchTerm → filterTree() → highlight matches → re-render tree
Global Search:   Cmd+K → modal open → type query → debounce 300ms → GET /api/kb/search → render grouped results
Preview Panel:   click file → kbSearch.showPreview(file) → render panel → actions (Process/Open)
```

---

## Part 2 — Implementation Guide

### Step 1: Extend Search API (Backend)

**File: `src/x_ipe/routes/kb_routes.py`**

Modify `search_kb()` to:
- Accept optional `type` and `topic` query params
- Return grouped results: `{ query, results: { files: [...], topics: [...], summaries: [...] }, total }`

**File: `src/x_ipe/services/kb_manager_service.py`**

Modify `search()` to:
- Accept `file_type` and `topic` optional params
- Filter by type/topic if provided
- Add topic-name matching to results
- Add summary-file matching to results
- Group results by category before returning

```python
def search(self, query: str, file_type: str = None, topic: str = None) -> dict:
    # Search files (existing logic + type/topic filters)
    # Search topic names
    # Search summary files
    # Return grouped: { files: [...], topics: [...], summaries: [...] }
```

### Step 2: Create Search Modal (Frontend JS)

**New file: `src/x_ipe/static/js/features/kb-search.js`**

```javascript
const kbSearch = {
    modal: null,
    previewPanel: null,
    activeResultIndex: -1,
    results: [],
    debounceTimer: null,
    recentItems: [],  // in-memory, current session only
    
    // --- Search Modal ---
    init(),                    // bind Cmd+K, create modal DOM
    _createModalDOM(),         // lazy-create search modal HTML
    openModal(),               // show modal, focus input
    closeModal(),              // hide modal, clear results
    _onSearchInput(query),     // debounce 300ms → _fetchResults()
    _fetchResults(query),      // GET /api/kb/search?q=...&type=...&topic=...
    _renderResults(grouped),   // render sections: Recent, Files, Topics, Summaries
    _highlightMatch(text, q),  // wrap matched text in <span class="search-result-highlight">
    _navigateResults(dir),     // ↑/↓ keyboard nav, update activeResultIndex
    _selectResult(result),     // navigate to item: file→preview, topic→topics view
    
    // --- Filter Chips ---
    activeFilters: { types: [], topic: null },
    _renderFilterChips(),
    _toggleTypeFilter(type),
    _setTopicFilter(topic),
    
    // --- Preview Panel ---
    _createPreviewDOM(),       // lazy-create preview panel in kb-container
    showPreview(fileEntry),    // populate and show preview panel
    hidePreview(),             // hide preview panel
    _onProcess(filePath),      // POST /api/kb/process
    _onOpen(filePath),         // navigate to file in content viewer
    
    // --- Sidebar Search Enhancement ---
    enhanceSidebarSearch(),    // override kbCore tree rendering to add highlights
};
window.kbSearch = kbSearch;
```

**Key implementation details:**

1. **Modal DOM** — Created once on first `openModal()`, appended to `document.body`:
   ```html
   <div class="kb-search-modal" id="kb-search-modal">
     <div class="kb-search-modal-content">
       <div class="kb-search-modal-header">
         <i class="bi bi-search"></i>
         <input type="text" placeholder="Search knowledge base..." autofocus>
         <kbd>ESC</kbd>
       </div>
       <div class="kb-search-filter-bar">
         <!-- Filter chips: All | PDF | Markdown | Code | topic dropdown -->
       </div>
       <div class="kb-search-modal-body">
         <!-- Grouped results rendered here -->
       </div>
       <div class="kb-search-modal-footer">
         <span><kbd>↑</kbd> <kbd>↓</kbd> to navigate</span>
         <span><kbd>Enter</kbd> to select</span>
       </div>
     </div>
   </div>
   ```

2. **Keyboard handling:**
   - `document.addEventListener('keydown')` for Cmd+K (open), Esc (close)
   - Inside modal: ↑/↓ (navigate), Enter (select)
   - `e.preventDefault()` on Cmd+K to override browser default

3. **Debounce:** Use `clearTimeout`/`setTimeout` pattern (300ms)

4. **Result navigation:** `_selectResult()` dispatches to:
   - Files → `kbSearch.showPreview(file)` + highlight in tree
   - Topics → `kbTopics.loadTopic(topicName)` (if kbTopics available)
   - Summaries → `kbTopics.loadTopic(topicName)` with summary version

### Step 3: Create Preview Panel (Frontend JS + HTML)

**Preview panel** is injected into `kb-container` by `kb-search.js`:

```html
<aside class="kb-preview-panel" id="kb-preview-panel" style="display:none;">
  <div class="kb-preview-header">
    <h6>Preview</h6>
    <button class="btn-close btn-close-white" id="btn-close-preview"></button>
  </div>
  <div class="kb-preview-content">
    <div class="kb-preview-thumbnail">
      <i class="bi bi-file-pdf"></i>
    </div>
    <div class="kb-preview-info">
      <!-- Name, Type, Size, Added, Status rows -->
    </div>
    <div class="kb-preview-tags">
      <!-- AI-suggested tag badges -->
    </div>
  </div>
  <div class="kb-preview-actions">
    <button class="btn btn-primary btn-sm"><i class="bi bi-cpu"></i> Process</button>
    <button class="btn btn-outline-light btn-sm"><i class="bi bi-eye"></i> Open</button>
  </div>
</aside>
```

**Integration with kbCore:**
- Override `kbCore.showFilePreview()` to call `kbSearch.showPreview(file)` instead
- Preview panel is appended inside `.kb-container` as the last child (flex item)
- When visible, content area shrinks automatically (flex layout)

### Step 4: Sidebar Search Enhancement

**File: `src/x_ipe/static/js/features/kb-core.js`**

Modify the tree rendering to support highlighting:
- When `kbCore.searchTerm` is set, wrap matched portions in `<mark class="kb-search-highlight">` in rendered tree item HTML
- This is a small change to the existing `_renderTreeItem()` or equivalent rendering function

### Step 5: Create CSS Styles

**New file: `src/x_ipe/static/css/kb-search.css`**

Styles for:
1. **Search modal** — overlay, backdrop blur, centered content, animations
2. **Search results** — grouped sections, result items, highlight spans
3. **Filter chips** — horizontal strip, active/inactive states
4. **Preview panel** — 360px width, header, thumbnail, info rows, tags, actions
5. **Sidebar highlight** — `.kb-search-highlight` mark style

Key CSS patterns (from mockup):
```css
.kb-search-modal { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); }
.kb-search-modal-content { width: min(640px, 90vw); margin-top: 120px; }
.kb-preview-panel { width: 360px; border-left: 1px solid var(--border-color); }
```

### Step 6: Wire Up in Template

**File: `src/x_ipe/templates/knowledge-base.html`**

1. Add `<link>` for `kb-search.css`
2. Add `<script>` for `kb-search.js` (after kb-core.js)
3. In DOMContentLoaded init:
   ```javascript
   if (window.kbSearch) {
       window.kbSearch.init();
   }
   ```

### Implementation Order

| Order | Step | Scope | Depends On |
|-------|------|-------|------------|
| 1 | Step 1 | Backend | — |
| 2 | Step 5 | CSS | — |
| 3 | Step 2 | Frontend (search modal) | Step 1, Step 5 |
| 4 | Step 3 | Frontend (preview panel) | Step 5 |
| 5 | Step 4 | Frontend (sidebar highlight) | — |
| 6 | Step 6 | Template wiring | Steps 2-5 |

### File Impact Summary

| File | Action | Lines (est.) |
|------|--------|-------------|
| `src/x_ipe/static/js/features/kb-search.js` | Create | ~400 |
| `src/x_ipe/static/css/kb-search.css` | Create | ~250 |
| `src/x_ipe/services/kb_manager_service.py` | Modify | ~30 lines changed |
| `src/x_ipe/routes/kb_routes.py` | Modify | ~15 lines changed |
| `src/x_ipe/static/js/features/kb-core.js` | Modify | ~20 lines changed |
| `src/x_ipe/templates/knowledge-base.html` | Modify | ~5 lines added |

### Testing Strategy

| Layer | Framework | What to Test |
|-------|-----------|-------------|
| Backend (Python) | pytest | Search API with type/topic filters, grouped response format, edge cases |
| Frontend (JS) | Vitest + jsdom | kbSearch module: modal open/close, keyboard nav, debounce, preview show/hide, filter toggles, highlight logic |
| Acceptance | Chrome DevTools | End-to-end: Cmd+K search, preview panel, filter chips, sidebar highlight |

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Search API slow with large index | Client-side debounce (300ms), limit results to 50/category |
| Preview panel layout shift | Flex layout + transition for smooth appearance |
| Cmd+K conflicts with browser | `e.preventDefault()` + test across browsers |
| Modal accessibility | Focus trap, aria-labels, Esc to close |
