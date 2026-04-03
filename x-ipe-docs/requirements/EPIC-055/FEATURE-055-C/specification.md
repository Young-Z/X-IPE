# Feature Specification: Task Board API

> Feature ID: FEATURE-055-C
> Version: v1.0
> Status: Refined
> Last Updated: 04-03-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-03-2026 | Initial specification |

## Linked Mockups

No mockups linked. This is a backend API feature with no direct UI.

## Overview

FEATURE-055-C provides a read-only Flask API for querying task data stored in the JSON data layer created by FEATURE-055-A and FEATURE-055-B. The API exposes two endpoints — list (with filtering, search, and pagination) and get-by-ID — consumed primarily by the Task Board Web Page (FEATURE-057-A).

The API follows existing codebase conventions: action-based route structure (`/api/tasks/list`, `/api/tasks/get/<id>`), a service-layer class (`TaskBoardService`) wrapping `_board_lib` functions via direct import, and the standard `{"success": true/false, ...}` response envelope used by all other blueprints.

## User Stories

1. **As the Task Board Web Page**, I want to fetch a paginated, filtered list of tasks via `GET /api/tasks/list`, so that I can render the task board with time range, status, search, and pagination controls.

2. **As the Task Board Web Page**, I want to fetch a single task by ID via `GET /api/tasks/get/<task_id>`, so that I can display task detail in a modal or expanded row.

3. **As a developer**, I want the API to follow existing Flask blueprint conventions, so that the codebase stays consistent and maintainable.

## Acceptance Criteria

### AC-055C-01: List Endpoint — Basic

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055C-01a | GIVEN the Flask app is running WHEN a GET request is sent to `/api/tasks/list` with no parameters THEN the response status is 200 AND body is JSON with `{"success": true, "data": {"tasks": [...], "pagination": {...}}}` | API |
| AC-055C-01b | GIVEN the Flask app is running WHEN a GET request is sent to `/api/tasks/list` with no parameters THEN pagination defaults are page=1, page_size=50, range=1w | API |
| AC-055C-01c | GIVEN tasks exist in the data layer WHEN a GET request is sent to `/api/tasks/list` THEN tasks are sorted by `last_updated` descending | API |
| AC-055C-01d | GIVEN tasks exist WHEN a GET request is sent to `/api/tasks/list` THEN each task in the `tasks` array contains all TASK_SCHEMA_V1 fields | API |

### AC-055C-02: List Endpoint — Filtering

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055C-02a | GIVEN tasks exist WHEN `?range=1w` is sent THEN only tasks from daily files within the last 7 days are returned | API |
| AC-055C-02b | GIVEN tasks exist WHEN `?range=1m` is sent THEN only tasks from daily files within the last 30 days are returned | API |
| AC-055C-02c | GIVEN tasks exist WHEN `?range=all` is sent THEN all non-archived tasks are returned | API |
| AC-055C-02d | GIVEN tasks exist WHEN `?status=in_progress` is sent THEN only tasks with status `in_progress` are returned | API |
| AC-055C-02e | GIVEN tasks exist WHEN `?search=keyword` is sent THEN only tasks matching the keyword (case-insensitive) in task_id, task_type, description, or role are returned | API |
| AC-055C-02f | GIVEN tasks exist WHEN `?status=in_progress&search=drift` is sent THEN filters are combined (AND logic) | API |

### AC-055C-03: List Endpoint — Pagination

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055C-03a | GIVEN 60 tasks exist WHEN `?page=1&page_size=50` is sent THEN 50 tasks are returned AND pagination shows `total: 60, page: 1, page_size: 50, total_pages: 2` | API |
| AC-055C-03b | GIVEN 60 tasks exist WHEN `?page=2&page_size=50` is sent THEN 10 tasks are returned AND pagination shows `page: 2` | API |
| AC-055C-03c | GIVEN 3 tasks exist WHEN `?page=1&page_size=50` is sent THEN 3 tasks are returned AND pagination shows `total_pages: 1` | API |
| AC-055C-03d | GIVEN tasks exist WHEN `?page=999` is sent (beyond range) THEN an empty tasks list is returned AND pagination metadata is still correct | API |

### AC-055C-04: Get Endpoint

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055C-04a | GIVEN a task with ID "TASK-100" exists WHEN a GET request is sent to `/api/tasks/get/TASK-100` THEN response status is 200 AND body is `{"success": true, "data": {task object}}` | API |
| AC-055C-04b | GIVEN no task with ID "TASK-999" exists WHEN a GET request is sent to `/api/tasks/get/TASK-999` THEN response status is 404 AND body is `{"success": false, "error": "NOT_FOUND", "message": "..."}` | API |
| AC-055C-04c | GIVEN a task exists WHEN it is fetched by ID THEN the response includes all TASK_SCHEMA_V1 fields | API |

### AC-055C-05: Error Handling

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055C-05a | GIVEN the Flask app is running WHEN `?range=invalid` is sent to `/api/tasks/list` THEN response status is 400 AND body is `{"success": false, "error": "VALIDATION_ERROR", "message": "..."}` | API |
| AC-055C-05b | GIVEN the Flask app is running WHEN `?page=abc` (non-integer) is sent THEN response status is 400 AND body contains a validation error | API |
| AC-055C-05c | GIVEN the Flask app is running WHEN `?page_size=0` is sent THEN response status is 400 AND body contains a validation error | API |
| AC-055C-05d | GIVEN an unexpected server error occurs WHEN any task endpoint is called THEN response status is 500 AND body is `{"success": false, "error": "INTERNAL_ERROR", "message": "..."}` | API |

### AC-055C-06: Blueprint & Registration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055C-06a | GIVEN the Flask app starts WHEN blueprints are registered THEN `task_board_bp` is registered with url_prefix (if any) AND `/api/tasks/list` and `/api/tasks/get/<task_id>` are accessible | Integration |
| AC-055C-06b | GIVEN the task board blueprint is loaded WHEN the module is inspected THEN it uses a `TaskBoardService` class that reads JSON directly (no subprocess, no `_board_lib` import) | Unit |
| AC-055C-06c | GIVEN the blueprint has an `after_request` hook WHEN any response is returned THEN `Cache-Control: no-store` header is present | API |

### AC-055C-07: Service Layer

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055C-07a | GIVEN `TaskBoardService` is instantiated with a project root WHEN `list_tasks(range, status, search, page, page_size)` is called THEN it returns `{"success": true, "data": {"tasks": [...], "pagination": {...}}}` | Unit |
| AC-055C-07b | GIVEN `TaskBoardService` is instantiated WHEN `get_task(task_id)` is called with a valid ID THEN it returns `{"success": true, "data": {task}}` | Unit |
| AC-055C-07c | GIVEN `TaskBoardService` is instantiated WHEN `get_task(task_id)` is called with an invalid ID THEN it returns `{"success": false, "error": "NOT_FOUND", "message": "..."}` | Unit |
| AC-055C-07d | GIVEN `TaskBoardService` reads daily files WHEN listing tasks THEN it skips `*.archived.json` and non-date filenames | Unit |
| AC-055C-07e | GIVEN `TaskBoardService` lists tasks WHEN no tasks directory exists THEN it returns an empty list with pagination metadata (total: 0, total_pages: 1) | Unit |

## Functional Requirements

**FR-1: Task List Endpoint**
- **Input:** GET `/api/tasks/list` with optional query parameters: `range` (1w|1m|all, default: 1w), `status` (string, optional), `search` (string, optional), `page` (int ≥ 1, default: 1), `page_size` (int ≥ 1, default: 50)
- **Process:** Validate parameters → instantiate TaskBoardService → call `list_tasks()` → service reads daily JSON files via `json.load` (with error handling), filters by date range (parsing dates from filenames), status, search (case-insensitive across task_id, task_type, description, role), sorts by last_updated desc, paginates
- **Output:** `{"success": true, "data": {"tasks": [...], "pagination": {"total": N, "page": P, "page_size": S, "total_pages": T}}}`

**FR-2: Task Get Endpoint**
- **Input:** GET `/api/tasks/get/<task_id>`
- **Process:** Instantiate TaskBoardService → call `get_task(task_id)` → service reads index via `json.load` to locate file → reads daily file → finds task by ID; falls back to scanning daily files if index is missing or stale
- **Output (found):** `{"success": true, "data": {task object}}`
- **Output (not found):** `{"success": false, "error": "NOT_FOUND", "message": "Task '{task_id}' not found"}` with HTTP 404

**FR-3: Parameter Validation**
- **Input:** Query parameters from GET requests
- **Process:** Validate `range` ∈ {1w, 1m, all}, `page` is int ≥ 1, `page_size` is int ≥ 1
- **Output (invalid):** `{"success": false, "error": "VALIDATION_ERROR", "message": "..."}` with HTTP 400

**FR-4: Blueprint Registration**
- **Input:** Flask app startup
- **Process:** Register `task_board_bp` blueprint in `_register_blueprints()` in `app.py`
- **Output:** Routes `/api/tasks/list` and `/api/tasks/get/<task_id>` are accessible

## Non-Functional Requirements

- **NFR-1: Response Time** — List endpoint should respond within 500ms for up to 1000 tasks
- **NFR-2: No Write Operations** — API is strictly read-only; no locks needed
- **NFR-3: Cache Prevention** — All responses include `Cache-Control: no-store` header
- **NFR-4: Error Isolation** — Blueprint-level error handler catches unhandled exceptions and returns structured JSON (never raw HTML error pages)

## UI/UX Requirements

N/A — This is a backend API feature with no direct UI.

## Dependencies

### Internal
- **FEATURE-055-B** (Task CRUD Scripts) — data format and index structure this API reads
- **Flask app** (src/x_ipe/app.py) — Blueprint registration in _register_blueprints()
- **x_ipe_tracing** — `@x_ipe_tracing()` decorator for route instrumentation

### External
- Flask (already in project dependencies)

## Business Rules

- **BR-1:** The API is read-only. All write operations go through CRUD scripts (FEATURE-055-B).
- **BR-2:** Archived tasks (*.archived.json) are excluded from all query results.
- **BR-3:** Search is case-insensitive and matches across task_id, task_type, description, and role fields.
- **BR-4:** Default time range is 1 week (1w) to keep responses focused on recent activity.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| No tasks directory exists | Return empty list with `total: 0, total_pages: 1` |
| No tasks match filters | Return empty list with correct pagination metadata |
| Page number exceeds total pages | Return empty tasks list, pagination still shows correct total |
| task_id contains URL-special characters | Flask URL routing handles encoding; service searches by exact match |
| Daily file is malformed JSON | Skip the file, log warning, continue with remaining files |
| Index file missing | Rebuild by scanning daily files (graceful degradation for get-by-id) |

## Out of Scope

- Write/mutation endpoints (POST, PUT, DELETE) — handled by CRUD scripts
- Authentication/authorization — internal tool
- CORS headers — same-origin serving
- Stats/aggregation endpoint — frontend computes from list data
- WebSocket/real-time updates
- Rate limiting

## Technical Considerations

- Service class should reuse the same query logic as `task_query.py` (date range parsing from filenames, filter matching, pagination) — extract shared functions or reimplement in service
- Blueprint file: `src/x_ipe/routes/task_board_routes.py`
- Service file: `src/x_ipe/services/task_board_service.py`
- Follow existing pattern: `_get_service()` helper returns `TaskBoardService(project_root)`
- No locks needed — read-only operations (same as task_query.py approach)

## Open Questions

None — all design decisions resolved via DAO.
