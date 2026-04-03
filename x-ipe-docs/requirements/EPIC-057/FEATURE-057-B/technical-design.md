# Technical Design: Feature Board Web Page

> Feature ID: FEATURE-057-B
> Version: v1.0
> Last Updated: 04-03-2026

## Part 1: Design Overview

### Architecture

Same pattern as FEATURE-057-A. Vanilla JS IIFE fetches data from existing API and renders DOM.

```
Browser:
  feature-board.html (extends base.html)
  feature-board.js   (fetchSummary → renderEpics → on expand: fetchFeatures → renderTable)
  feature-board.css  (epic accordion, progress bars, status badges)
      │ fetch()
      ▼
Flask:
  feature_board_page_routes.py   GET /feature-board → render_template
  feature_board_routes.py        GET /api/features/list, /get/<id>, /epic-summary (existing)
```

### File Map

| File | Action | Purpose |
|------|--------|---------|
| `src/x_ipe/routes/feature_board_page_routes.py` | Create | GET /feature-board route |
| `src/x_ipe/templates/feature-board.html` | Create | Jinja template |
| `src/x_ipe/static/css/feature-board.css` | Create | Page styles |
| `src/x_ipe/static/js/features/feature-board.js` | Create | Fetch, render, accordion, filter |
| `src/x_ipe/app.py` | Modify | Register blueprint |
| `src/x_ipe/templates/index.html` | Modify | Add "Features" nav link |
| `tests/test_feature_board_page.py` | Create | Route + template tests |

### Data Flow

1. Page load → `fetchSummary()` calls `/api/features/epic-summary`
2. Renders collapsed epic accordion with counts + progress bars
3. User clicks epic header → `fetchEpicFeatures(epicId)` calls `/api/features/list?epic_id=X&page_size=200`
4. Renders feature table inside that epic's body
5. Status filter / search → re-fetches summary + clears cached features

### Key Functions

| Function | Purpose |
|----------|---------|
| `fetchSummary()` | GET /api/features/epic-summary, render accordion headers |
| `fetchEpicFeatures(epicId)` | GET /api/features/list?epic_id=X, render feature table |
| `renderEpics(summaries)` | Build accordion HTML with progress bars |
| `renderFeatureTable(epicId, features)` | Build table rows inside epic body |
| `toggleEpic(epicId)` | Expand/collapse, lazy-load features on first expand |
| `renderProgressBar(summary)` | Stacked bar from status counts |
| `toggleDetail(featureId)` | Inline expand feature detail |
| `sortByStatusPriority(features)` | Sort by status order then feature_id |
