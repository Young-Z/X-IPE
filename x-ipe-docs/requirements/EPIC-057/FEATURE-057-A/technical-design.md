# Technical Design: Task Board Web Page

> Feature ID: FEATURE-057-A
> Version: v1.0
> Status: Designed
> Last Updated: 04-03-2026

## Part 1: Design Overview

### Summary

FEATURE-057-A adds a view-only Task Board web page at `/task-board` consuming the existing `/api/tasks/list` and `/api/tasks/get/<task_id>` endpoints. The page extends `base.html`, uses vanilla JS for data fetching and DOM manipulation, and follows the Slate/Emerald design system with DM Sans/DM Mono fonts.

### Architecture

```
┌──────────────────────────────────────────────────────┐
│ Browser                                               │
│  ┌─────────────────┐  ┌──────────────────────────┐   │
│  │ task-board.html  │  │ task-board.js            │   │
│  │ (extends base)   │  │  - fetchTasks()          │   │
│  │                  │  │  - renderTable()          │   │
│  │  {% block body %}│  │  - renderStats()          │   │
│  │  stat cards      │  │  - renderPagination()     │   │
│  │  filter bar      │  │  - toggleDetail()         │   │
│  │  table container │  │  - debounce(search, 300)  │   │
│  │  pagination      │  │                           │   │
│  └─────────────────┘  └──────────────────────────┘   │
│  ┌─────────────────┐                                  │
│  │ task-board.css   │                                  │
│  │  CSS vars, grid  │                                  │
│  └─────────────────┘                                  │
└──────────────────────────────────────────────────────┘
          │  fetch()
          ▼
┌──────────────────────────────────────────────────────┐
│ Flask Server                                          │
│  ┌──────────────────────────┐                        │
│  │ task_board_page_routes.py │                        │
│  │  GET /task-board          │─→ render_template()   │
│  └──────────────────────────┘                        │
│  ┌──────────────────────────┐                        │
│  │ task_board_routes.py      │ (existing, FEAT-055-C)│
│  │  GET /api/tasks/list      │─→ TaskBoardService    │
│  │  GET /api/tasks/get/<id>  │                        │
│  └──────────────────────────┘                        │
└──────────────────────────────────────────────────────┘
```

### File Map

| File | Action | Purpose |
|------|--------|---------|
| `src/x_ipe/templates/task-board.html` | Create | Jinja template extending base.html |
| `src/x_ipe/static/css/task-board.css` | Create | Page-specific styles, CSS custom properties |
| `src/x_ipe/static/js/features/task-board.js` | Create | Vanilla JS: fetch, render, filter, paginate |
| `src/x_ipe/routes/task_board_page_routes.py` | Create | Flask blueprint with GET /task-board route |
| `src/x_ipe/app.py` | Modify | Register task_board_page_bp blueprint |
| `src/x_ipe/templates/index.html` | Modify | Add "Task Board" nav link to menu-actions |
| `tests/test_task_board_page.py` | Create | Route + template rendering tests |

### AC Coverage

| AC Group | ACs | Covered By |
|----------|-----|------------|
| AC-057-A-01: Routing & Nav | 01a–01c | task_board_page_routes.py, base.html nav, test_task_board_page.py |
| AC-057-A-02: Data Loading & Range | 02a–02f | task-board.js fetchTasks(), setRange() |
| AC-057-A-03: Status Filter | 03a–03c | task-board.js onStatusChange() |
| AC-057-A-04: Search | 04a–04c | task-board.js onSearch() with debounce |
| AC-057-A-05: Table Display | 05a–05h | task-board.js renderTable(), task-board.css badges |
| AC-057-A-06: Stat Cards | 06a–06c | task-board.js renderStats() |
| AC-057-A-07: Pagination | 07a–07d | task-board.js renderPagination() |
| AC-057-A-08: Inline Detail | 08a–08c | task-board.js toggleDetail() |
| AC-057-A-09: Empty/Error | 09a–09c | task-board.js renderEmpty(), renderError() |
| AC-057-A-10: Mockup Compliance | 10a–10d | task-board.css, task-board.html structure |

---

## Part 2: Detailed Design

### 2.1 Flask Route — `task_board_page_routes.py`

```python
# src/x_ipe/routes/task_board_page_routes.py
from flask import Blueprint, render_template
from x_ipe.utils.tracing import x_ipe_tracing

task_board_page_bp = Blueprint('task_board_page', __name__)

@task_board_page_bp.route('/task-board')
@x_ipe_tracing()
def task_board():
    """Serve the Task Board web page."""
    return render_template('task-board.html')
```

**Registration in app.py:** Add import and `app.register_blueprint(task_board_page_bp)` in `_register_blueprints()`.

### 2.2 Template — `task-board.html`

```
{% extends "base.html" %}
{% block title %}Task Board{% endblock %}

{% block extra_css %}
<link href="/static/css/task-board.css" rel="stylesheet">
{% endblock %}

{% block body %}
<div class="tb-page">
  <!-- Stat Cards Row -->
  <div class="tb-stats" id="tb-stats">
    <!-- 5 stat cards rendered by JS -->
  </div>

  <!-- Filter Bar -->
  <div class="tb-filters">
    <div class="tb-search-wrap">
      <i class="bi bi-search"></i>
      <input id="tb-search" type="text" placeholder="Search tasks...">
    </div>
    <div class="tb-filter-divider"></div>
    <select id="tb-status-filter">
      <option value="">All Statuses</option>
      <option value="in_progress">In Progress</option>
      <option value="done">Done</option>
      <option value="completed">Completed</option>
      <option value="pending">Pending</option>
      <option value="blocked">Blocked</option>
      <option value="deferred">Deferred</option>
    </select>
    <div class="tb-filter-divider"></div>
    <div class="tb-range-group">
      <button class="tb-range-btn active" data-range="1w">1W</button>
      <button class="tb-range-btn" data-range="1m">1M</button>
      <button class="tb-range-btn" data-range="all">All</button>
    </div>
  </div>

  <!-- Error Banner (hidden by default) -->
  <div id="tb-error" class="tb-error" style="display:none;"></div>

  <!-- Table -->
  <div class="tb-table-wrap">
    <table class="tb-table" id="tb-table">
      <thead>
        <tr>
          <th>Task ID</th>
          <th>Type</th>
          <th>Description</th>
          <th>Role</th>
          <th>Status</th>
          <th>Updated</th>
          <th>Output</th>
          <th>Next</th>
        </tr>
      </thead>
      <tbody id="tb-body">
        <!-- Rendered by JS -->
      </tbody>
    </table>
  </div>

  <!-- Pagination -->
  <div class="tb-pagination" id="tb-pagination"></div>
</div>
{% endblock %}

{% block extra_js %}
<script src="/static/js/features/task-board.js"></script>
{% endblock %}
```

### 2.3 JavaScript — `task-board.js`

**Module structure (IIFE pattern):**

```javascript
(function() {
  'use strict';

  // --- State ---
  let state = {
    range: '1w',
    status: '',
    search: '',
    page: 1,
    pageSize: 50,
    tasks: [],
    pagination: null,
    expandedTaskId: null
  };

  // --- Constants ---
  const STATUS_COLORS = {
    done:        { color: '#22c55e', bg: '#f0fdf4' },
    completed:   { color: '#22c55e', bg: '#f0fdf4' },
    in_progress: { color: '#3b82f6', bg: '#eff6ff' },
    pending:     { color: '#f59e0b', bg: '#fffbeb' },
    blocked:     { color: '#ef4444', bg: '#fef2f2' },
    deferred:    { color: '#8b5cf6', bg: '#f5f3ff' }
  };

  const TYPE_COLORS = {
    'Ideation':         { bg: '#fef3c7', color: '#92400e' },
    'Bug Fix':          { bg: '#fce7f3', color: '#9d174d' },
    'Implementation':   { bg: '#dbeafe', color: '#1e40af' },
    'Refinement':       { bg: '#e0e7ff', color: '#3730a3' },
    'Feature Closing':  { bg: '#d1fae5', color: '#065f46' },
    'Acceptance Test':  { bg: '#fae8ff', color: '#86198f' },
    'Technical Design': { bg: '#f1f5f9', color: '#334155' },
    'Skill Creation':   { bg: '#ccfbf1', color: '#134e4a' },
    'Breakdown':        { bg: '#fed7aa', color: '#9a3412' }
  };

  const STAT_CARDS = [
    { key: 'total',       label: 'Total Tasks',  borderColor: '#475569' },
    { key: 'in_progress', label: 'In Progress',   borderColor: '#3b82f6' },
    { key: 'done',        label: 'Completed',     borderColor: '#22c55e' },
    { key: 'blocked',     label: 'Blocked',       borderColor: '#ef4444' },
    { key: 'pending',     label: 'Pending',       borderColor: '#f59e0b' }
  ];

  // --- API ---
  async function fetchTasks() {
    const params = new URLSearchParams({
      range: state.range,
      page: state.page,
      page_size: state.pageSize
    });
    if (state.status) params.set('status', state.status);
    if (state.search) params.set('search', state.search);

    try {
      hideError();
      const resp = await fetch(`/api/tasks/list?${params}`);
      const json = await resp.json();
      if (!json.success) throw new Error(json.message || 'API error');
      state.tasks = json.data.tasks;
      state.pagination = json.data.pagination;
      renderAll();
    } catch (err) {
      showError('Error loading tasks: ' + err.message);
    }
  }

  // --- Render functions ---
  function renderAll() {
    renderStats();
    renderTable();
    renderPagination();
  }

  function renderStats() { /* compute counts, build stat card HTML */ }
  function renderTable() { /* build <tr> rows, attach click handlers */ }
  function renderPagination() { /* build page buttons */ }
  function toggleDetail(taskId) { /* expand/collapse inline row */ }

  // --- Helpers ---
  function debounce(fn, ms) { /* standard debounce */ }
  function escapeHtml(str) { /* XSS prevention */ }
  function showError(msg) { /* show #tb-error */ }
  function hideError() { /* hide #tb-error */ }

  // --- Event binding ---
  document.addEventListener('DOMContentLoaded', () => {
    // Range buttons
    document.querySelectorAll('.tb-range-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelector('.tb-range-btn.active').classList.remove('active');
        btn.classList.add('active');
        state.range = btn.dataset.range;
        state.page = 1;
        fetchTasks();
      });
    });

    // Status filter
    document.getElementById('tb-status-filter').addEventListener('change', (e) => {
      state.status = e.target.value;
      state.page = 1;
      fetchTasks();
    });

    // Search with debounce
    const searchInput = document.getElementById('tb-search');
    searchInput.addEventListener('input', debounce(() => {
      state.search = searchInput.value.trim();
      state.page = 1;
      fetchTasks();
    }, 300));

    // Initial load
    fetchTasks();
  });
})();
```

**Key functions:**

| Function | Purpose | ACs |
|----------|---------|-----|
| `fetchTasks()` | GET /api/tasks/list with current state params | AC-02a–02f, 03a–03b, 04a–04b |
| `renderStats()` | Compute status counts from `state.tasks`, render 5 stat cards | AC-06a–06c |
| `renderTable()` | Build table rows with badges, attach row click for detail | AC-05a–05h |
| `renderPagination()` | Page numbers, prev/next, "Showing X–Y of Z" | AC-07a–07d |
| `toggleDetail(taskId)` | Insert/remove detail row below clicked task | AC-08a–08c |
| `debounce(fn, ms)` | Delay search API calls by 300ms | AC-04c |
| `showError(msg)` / `hideError()` | Error banner management | AC-09a–09c |
| `escapeHtml(str)` | Prevent XSS in user-generated content | EC-06 |

### 2.4 CSS — `task-board.css`

**Custom properties** (from mockup):
```css
.tb-page {
  --bg-page: #f8fafc;
  --bg-card: #ffffff;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --accent: #10b981;
  --radius: 10px;
  --radius-sm: 6px;
  --shadow-sm: 0 1px 2px rgb(0 0 0 / 0.04);
  --shadow-md: 0 4px 12px rgb(0 0 0 / 0.06);
  --font-body: 'DM Sans', system-ui, sans-serif;
  --font-mono: 'DM Mono', 'JetBrains Mono', monospace;
}
```

**Key CSS classes:**

| Class | Purpose |
|-------|---------|
| `.tb-page` | Root container with scoped custom properties |
| `.tb-stats` | 5-column CSS grid for stat cards |
| `.tb-stat-card` | Card with 3px top border, hover shadow |
| `.tb-filters` | Flex row: search + divider + dropdown + divider + range |
| `.tb-range-btn` / `.tb-range-btn.active` | Toggle button styling |
| `.tb-table` | Full-width table with sticky header |
| `.tb-table tr:hover` | Hover highlight |
| `.status-badge.{status}` | Color-coded pill badges |
| `.type-badge.{type}` | Task type color badges |
| `.tb-detail-row` | Expanded detail row with slide animation |
| `.tb-pagination` | Centered pagination controls |
| `.tb-error` | Red error banner |
| `.tb-empty` | Empty state with icon |

### 2.5 Navigation Link

In `src/x_ipe/templates/index.html`, add to `<div class="menu-actions">`:
```html
<a href="/task-board" class="menu-link" title="Task Board">
    <i class="bi bi-list-check"></i>
    <span>Tasks</span>
</a>
```

### 2.6 Test Strategy

**File:** `tests/test_task_board_page.py`

| Test | What | Type |
|------|------|------|
| `test_task_board_route_returns_200` | GET /task-board returns 200 | API |
| `test_task_board_route_returns_html` | Response content-type is text/html | API |
| `test_task_board_template_extends_base` | Template contains base.html markers | API |
| `test_task_board_has_table_container` | Response contains #tb-table element | API |
| `test_task_board_has_stat_cards` | Response contains #tb-stats element | API |
| `test_task_board_has_filters` | Response contains filter elements | API |
| `test_task_board_has_js_script` | Response includes task-board.js | API |
| `test_task_board_has_css_link` | Response includes task-board.css | API |

JS tests are out of scope for this feature (UI tests would require browser automation). The API-level tests verify the route and template rendering.
