# Feature Specification: Task Board Web Page

> Feature ID: FEATURE-057-A
> Version: v1.0
> Status: Refined
> Last Updated: 04-03-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-03-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| Task Board V1 | HTML | [x-ipe-docs/requirements/EPIC-057/FEATURE-057-A/mockups/task-board-v1.html](x-ipe-docs/requirements/EPIC-057/FEATURE-057-A/mockups/task-board-v1.html) | Full task board page with sidebar, stat cards, filters, table, pagination | current | 04-03-2026 |

## Overview

FEATURE-057-A delivers a view-only web page for browsing development tasks tracked by the X-IPE task board system. The page consumes the `/api/tasks/list` and `/api/tasks/get/<task_id>` REST endpoints (FEATURE-055-C) and presents tasks in a searchable, filterable table with time-range controls, status badges, and inline detail expansion.

The page extends `base.html` to inherit the existing app chrome (top menu bar, terminal panel) and is served at `/task-board`. It uses DM Sans / DM Mono fonts with the Slate/Emerald color palette consistent with the design system.

Target users are AI agents and human engineers who need a visual overview of task activity, status distribution, and output artifacts.

## User Stories

- **US-057-A-01:** As a developer, I want to view all recent tasks in a table so that I can track engineering activity at a glance.
- **US-057-A-02:** As a developer, I want to filter tasks by status so that I can focus on blocked or in-progress work.
- **US-057-A-03:** As a developer, I want to search tasks by ID, description, or role so that I can quickly find a specific task.
- **US-057-A-04:** As a developer, I want to toggle the time range (1W / 1M / All) so that I can control how much history is shown.
- **US-057-A-05:** As a developer, I want to see summary statistics (total, in-progress, done, blocked, pending) so that I can assess project health.
- **US-057-A-06:** As a developer, I want to expand a task row inline to see full details so that I can inspect outputs without leaving the page.

## Acceptance Criteria

### AC-057-A-01: Page Routing & Navigation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-A-01a | GIVEN the Flask app is running WHEN a user navigates to `/task-board` THEN the task board HTML page is returned with HTTP 200 | API |
| AC-057-A-01b | GIVEN the task board page is loaded WHEN the user inspects the page THEN it extends `base.html` and inherits the app menu bar and terminal panel | UI |
| AC-057-A-01c | GIVEN any page in the app WHEN the user looks at the navigation THEN a "Task Board" link is visible that navigates to `/task-board` | UI |

### AC-057-A-02: Data Loading & Time Range

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-A-02a | GIVEN the page loads WHEN DOMContentLoaded fires THEN the page calls `/api/tasks/list?range=1w&page=1&page_size=50` and displays results | UI |
| AC-057-A-02b | GIVEN the page is loaded WHEN the user clicks "1 Week" toggle THEN the page fetches tasks with `range=1w` | UI |
| AC-057-A-02c | GIVEN the page is loaded WHEN the user clicks "1 Month" toggle THEN the page fetches tasks with `range=1m` | UI |
| AC-057-A-02d | GIVEN the page is loaded WHEN the user clicks "All" toggle THEN the page fetches tasks with `range=all` | UI |
| AC-057-A-02e | GIVEN a time range toggle is clicked WHEN the fetch completes THEN only the clicked toggle has the active visual state | UI |
| AC-057-A-02f | GIVEN a time range toggle is clicked WHEN the fetch completes THEN the stat cards, table, and pagination all update to reflect the new data | UI |

### AC-057-A-03: Status Filter

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-A-03a | GIVEN the page is loaded WHEN the user selects "In Progress" from the status dropdown THEN the page fetches tasks with `status=in_progress` and displays only in-progress tasks | UI |
| AC-057-A-03b | GIVEN the page is loaded WHEN the user selects "All Statuses" THEN the page fetches tasks without a status filter | UI |
| AC-057-A-03c | GIVEN the status dropdown WHEN rendered THEN it contains options: All Statuses, In Progress, Completed, Pending, Blocked, Deferred, Done | UI |

### AC-057-A-04: Search

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-A-04a | GIVEN the page is loaded WHEN the user types "TASK-1054" in the search input THEN the page fetches tasks with `search=TASK-1054` and displays matching results | UI |
| AC-057-A-04b | GIVEN the search input has text WHEN the user clears the input THEN the page fetches tasks without a search filter | UI |
| AC-057-A-04c | GIVEN the user types in search WHEN fewer than 300ms have elapsed since the last keystroke THEN no API call is made (debounce) | Unit |

### AC-057-A-05: Task Table Display

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-A-05a | GIVEN tasks are loaded WHEN the table renders THEN each row shows: Task ID, Type badge, Description, Role, Status badge, Last Updated date, Output link, Next task | UI |
| AC-057-A-05b | GIVEN a task has status "done" WHEN rendered THEN the status badge is green (#22c55e) with text "Done" per mockup | UI |
| AC-057-A-05c | GIVEN a task has status "in_progress" WHEN rendered THEN the status badge is blue (#3b82f6) with a pulsing dot animation per mockup | UI |
| AC-057-A-05d | GIVEN a task has status "pending" WHEN rendered THEN the status badge is amber (#f59e0b) per mockup | UI |
| AC-057-A-05e | GIVEN a task has status "blocked" WHEN rendered THEN the status badge is red (#ef4444) per mockup | UI |
| AC-057-A-05f | GIVEN a task has status "deferred" WHEN rendered THEN the status badge is purple (#8b5cf6) per mockup | UI |
| AC-057-A-05g | GIVEN the table is rendered WHEN inspecting Task ID and date columns THEN they use monospace font (DM Mono) per mockup | UI |
| AC-057-A-05h | GIVEN a task has a `task_type` field WHEN rendered THEN the type column shows a color-coded badge matching the 9 type categories from the mockup | UI |

### AC-057-A-06: Stat Cards

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-A-06a | GIVEN tasks are loaded WHEN the page renders THEN 5 stat cards are displayed: Total Tasks, In Progress, Completed, Blocked, Pending | UI |
| AC-057-A-06b | GIVEN 48 total tasks with 3 in_progress, 41 done, 1 blocked, 3 pending WHEN stat cards render THEN each card shows the correct count computed client-side from the API response | UI |
| AC-057-A-06c | GIVEN stat cards are rendered WHEN inspecting their style THEN each has a 3px colored top border and monospace value display per mockup | UI |

### AC-057-A-07: Pagination

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-A-07a | GIVEN more than 50 tasks exist WHEN the page loads THEN pagination controls are displayed showing page numbers and prev/next arrows | UI |
| AC-057-A-07b | GIVEN the user is on page 1 WHEN the user clicks page 2 THEN the page fetches tasks with `page=2` and updates the table | UI |
| AC-057-A-07c | GIVEN the user is on page 1 WHEN the previous button is displayed THEN it is visually disabled | UI |
| AC-057-A-07d | GIVEN pagination is shown WHEN rendered THEN it displays "Showing X–Y of Z tasks" text | UI |

### AC-057-A-08: Inline Task Detail Expansion

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-A-08a | GIVEN a task row is displayed WHEN the user clicks the row THEN an expanded detail section appears below the row showing full description, output links, and metadata | UI |
| AC-057-A-08b | GIVEN a task row is expanded WHEN the user clicks it again THEN the detail section collapses | UI |
| AC-057-A-08c | GIVEN a task has output_links WHEN the detail section is expanded THEN each link is rendered as a clickable anchor opening in a new tab | UI |

### AC-057-A-09: Empty & Error States

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-A-09a | GIVEN the API returns an empty tasks array WHEN the table renders THEN an inline "No tasks found" message with an icon is displayed in the table area | UI |
| AC-057-A-09b | GIVEN the API call fails (network error or 500) WHEN the page tries to load tasks THEN an inline error banner "Error loading tasks" is displayed above the table | UI |
| AC-057-A-09c | GIVEN an error banner is shown WHEN the user changes any filter THEN the error banner is cleared and a new fetch is attempted | UI |

### AC-057-A-10: Mockup Visual Compliance

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-057-A-10a | GIVEN the page is loaded WHEN inspecting fonts THEN DM Sans is the body font and DM Mono is the monospace font per mockup | UI |
| AC-057-A-10b | GIVEN the page is loaded WHEN inspecting colors THEN the page uses Slate/Emerald palette: page bg #f8fafc, cards #ffffff, accent #10b981 per mockup | UI |
| AC-057-A-10c | GIVEN the page is loaded WHEN inspecting the filter bar THEN it contains search input, status dropdown, and time range toggles laid out horizontally per mockup | UI |
| AC-057-A-10d | GIVEN the page is loaded WHEN inspecting the table THEN it has a sticky header row per mockup | UI |

## Functional Requirements

- **FR-01:** The page shall be served by a new Flask route at `/task-board` using `render_template('task-board.html')`.
- **FR-02:** The template shall extend `base.html` using `{% extends "base.html" %}`.
- **FR-03:** On page load, JavaScript shall call `GET /api/tasks/list?range=1w&page=1&page_size=50`.
- **FR-04:** Time-range toggles shall pass `range` query parameter (`1w`, `1m`, `all`) to the API.
- **FR-05:** Status filter dropdown shall pass `status` query parameter to the API.
- **FR-06:** Search input shall pass `search` query parameter with 300ms debounce.
- **FR-07:** Stat cards shall compute counts client-side from the current API response.
- **FR-08:** Pagination controls shall pass `page` parameter; page_size fixed at 50.
- **FR-09:** Task row click shall toggle an inline expansion showing full task details.
- **FR-10:** Output links in expanded rows shall open in new browser tabs.

## Non-Functional Requirements

- **NFR-01:** Page initial render (before API call) shall complete in < 500ms.
- **NFR-02:** API fetch + table render shall complete in < 2s for up to 50 tasks.
- **NFR-03:** All interactive elements shall be keyboard-accessible (tab, enter, escape).
- **NFR-04:** Page shall work in Chrome, Firefox, Safari, Edge (latest versions).
- **NFR-05:** No external CDN dependencies — all assets served from `/static/`.

## UI/UX Requirements

Derived from mockup `task-board-v1.html`:

- **UIR-01:** Fonts: DM Sans (body, 300–700 weights), DM Mono (monospace, 400–500). Loaded from Google Fonts.
- **UIR-02:** Color palette: Slate/Emerald — page bg `#f8fafc`, cards `#ffffff`, sidebar uses app default, accent `#10b981`.
- **UIR-03:** Status badge colors: Done `#22c55e`, In Progress `#3b82f6`, Pending `#f59e0b`, Blocked `#ef4444`, Deferred `#8b5cf6`. Each with light background variant.
- **UIR-04:** 9 task type badges with distinct color pairs per mockup (Ideation, Bug Fix, Implementation, Refinement, Feature Closing, Acceptance Test, Technical Design, Skill Creation, Breakdown).
- **UIR-05:** 5 stat cards in horizontal grid with 3px colored top border, uppercase label, monospace large value.
- **UIR-06:** Table: sticky header, row hover effect, max-width 340px on description column, monospace for IDs and dates.
- **UIR-07:** Filter bar: search with icon prefix, status dropdown, divider, time range toggle group.
- **UIR-08:** Pagination: page numbers, prev/next arrows, "Showing X–Y of Z tasks" text.
- **UIR-09:** Animations: staggered fade-in on stat cards and table rows, pulsing dot on in-progress badges.
- **UIR-10:** Inline expansion row for task detail with smooth slide-down animation.

## Dependencies

### Internal
- **FEATURE-055-C** (Task Board API) — provides `/api/tasks/list` and `/api/tasks/get/<task_id>` endpoints. **Status: Completed**.
- **base.html** template — provides app chrome, CSS/JS stack, template blocks.

### External
- Google Fonts: DM Sans, DM Mono (loaded in base.html or page-specific CSS).

## Business Rules

- **BR-01:** The page is read-only. No task creation, editing, or deletion from this page.
- **BR-02:** Default time range is 1 week (most relevant recent activity).
- **BR-03:** Default sort is `last_updated` descending (API default).
- **BR-04:** Page size is fixed at 50 items per page.
- **BR-05:** Stat card counts are computed from the full filtered result set on the current page.

## Edge Cases

- **EC-01:** No tasks exist for the selected time range → show "No tasks found" inline message with suggestion to expand time range.
- **EC-02:** API is unreachable → show error banner, keep previous data if available, allow retry via filter change.
- **EC-03:** Task has empty `output_links` array → show "—" dash in output column.
- **EC-04:** Task has no `next_task` → show "—" dash in next column.
- **EC-05:** Very long description → truncate with ellipsis in table, show full text in expanded row.
- **EC-06:** Task ID or role contains special characters → escape for HTML rendering.

## Out of Scope

- Task creation, editing, deletion (read-only page)
- Custom date range picker (use 1W/1M/All toggles)
- Multi-select status filter
- Auto-refresh / real-time updates
- Kanban/board view (table view only)
- Export to CSV/PDF
- Sort column toggling (API default sort only)
- DeliverableViewer modal integration for output links

## Technical Considerations

- Page template: `src/x_ipe/templates/task-board.html` extending `base.html`
- Page CSS: `src/x_ipe/static/css/task-board.css` with custom properties from mockup
- Page JS: `src/x_ipe/static/js/task-board.js` with vanilla JS (no framework)
- Flask route: add to existing routes file or new `task_board_page_routes.py`
- Navigation link: add to base.html or sidebar template
