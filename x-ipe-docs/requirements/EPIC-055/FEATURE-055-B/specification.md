# Feature Specification: Task CRUD Scripts

> Feature ID: FEATURE-055-B
> Version: v1.0
> Status: Refined
> Last Updated: 04-03-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-03-2026 | Initial specification |

## Linked Mockups

N/A — This feature provides CLI scripts with no UI component.

## Overview

FEATURE-055-B provides four standalone CLI Python scripts for managing task data as JSON files:

- **`task_create.py`** — Create a new task in the daily file and register in the index
- **`task_update.py`** — Update an existing task's fields (partial merge)
- **`task_query.py`** — Query tasks with filtering, search, pagination, or direct ID lookup
- **`task_archive.py`** — Archive a daily file and remove its entries from the index

Tasks are stored in daily JSON files (`tasks-YYYY-MM-DD.json`) under `x-ipe-docs/planning/tasks/`. A central index (`tasks-index.json`) maps each `task_id` to its daily file, status, and last-updated timestamp for O(1) lookups.

All scripts import `_board_lib.py` (FEATURE-055-A) for atomic JSON I/O, file locking, schema validation, structured output, and path resolution. They follow the established argparse CLI pattern from the `x-ipe-tool-x-ipe-app-interactor/scripts/` reference.

The primary consumers are AI agent skill scripts (`x-ipe+all+task-board-management`) that invoke these scripts via `python3 task_create.py --task '{...}'` to manage task board data.

## User Stories

- As an **AI agent skill**, I want to create tasks via a CLI command, so that task board data is stored as structured JSON with schema validation and atomic writes.
- As an **AI agent skill**, I want to update task fields via a CLI command, so that only the changed fields are modified while preserving existing data.
- As an **AI agent skill**, I want to query tasks with filters and pagination, so that I can retrieve relevant subsets of task data efficiently.
- As an **AI agent skill**, I want to look up a single task by ID in O(1) time, so that I can quickly access task details without scanning all files.
- As an **AI agent skill**, I want to archive old daily task files, so that the active index stays small and query performance remains fast.

## Acceptance Criteria

### AC-055B-01: Task Creation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055B-01a | GIVEN valid task JSON WHEN `task_create.py --task '{json}'` is called THEN a task entry is added to `tasks-YYYY-MM-DD.json` (today's date) AND `tasks-index.json` is updated with the task_id mapping | Unit |
| AC-055B-01b | GIVEN the `tasks/` directory does not exist WHEN `task_create.py` is called THEN the directory is created AND `tasks-index.json` is initialized with INDEX_SCHEMA_V1 structure AND the task is created successfully | Unit |
| AC-055B-01c | GIVEN task JSON with a task_id that already exists in the index WHEN `task_create.py` is called THEN the script exits with code 1 AND outputs `{"success": false, "error": "DUPLICATE_TASK_ID", "message": "..."}` to stderr | Unit |
| AC-055B-01d | GIVEN task JSON missing a required field per TASK_SCHEMA_V1 WHEN `task_create.py` is called THEN the script exits with code 1 AND outputs a schema validation error to stderr AND no file is modified | Unit |
| AC-055B-01e | GIVEN task JSON with an unknown field not in TASK_SCHEMA_V1 WHEN `task_create.py` is called THEN the script exits with code 1 AND outputs `"Unknown field"` error to stderr (strict mode) | Unit |
| AC-055B-01f | GIVEN valid task JSON WHEN `task_create.py` is called THEN `created_at` and `last_updated` fields are auto-set to the current ISO 8601 UTC timestamp regardless of any values provided by the caller | Unit |
| AC-055B-01g | GIVEN the daily file `tasks-YYYY-MM-DD.json` does not yet exist WHEN `task_create.py` is called THEN the daily file is created with the task as the first entry in a `{"_version": "1.0", "tasks": [...]}` structure | Unit |
| AC-055B-01h | GIVEN the daily file already exists with other tasks WHEN `task_create.py` is called THEN the new task is appended to the `tasks` array AND existing tasks are preserved | Unit |

### AC-055B-02: Task Update

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055B-02a | GIVEN a valid task_id and update JSON WHEN `task_update.py --task-id TASK-XXX --updates '{json}'` is called THEN only the specified fields are updated (partial merge) AND unspecified fields remain unchanged | Unit |
| AC-055B-02b | GIVEN a task_id that does not exist in the index WHEN `task_update.py` is called THEN the script exits with code 2 AND outputs `{"success": false, "error": "TASK_NOT_FOUND", "message": "..."}` to stderr | Unit |
| AC-055B-02c | GIVEN an update that would set a field to the wrong type per TASK_SCHEMA_V1 WHEN `task_update.py` is called THEN the script exits with code 1 AND outputs a schema validation error AND no file is modified | Unit |
| AC-055B-02d | GIVEN a valid update WHEN `task_update.py` is called THEN `last_updated` is auto-set to the current ISO 8601 UTC timestamp AND the index entry's `last_updated` and `status` are also updated | Unit |
| AC-055B-02e | GIVEN an update that attempts to change `task_id` or `created_at` WHEN `task_update.py` is called THEN the script exits with code 1 AND outputs an error indicating these fields are immutable | Unit |
| AC-055B-02f | GIVEN an update with unknown fields not in TASK_SCHEMA_V1 WHEN `task_update.py` is called THEN the script exits with code 1 AND outputs `"Unknown field"` error (strict mode) | Unit |

### AC-055B-03: Task Query — Filtered List

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055B-03a | GIVEN tasks exist across multiple daily files WHEN `task_query.py --range 1w` is called THEN only tasks from daily files within the last 7 days are returned AND results are ordered by `last_updated` descending | Unit |
| AC-055B-03b | GIVEN tasks exist WHEN `task_query.py --range 1m` is called THEN only tasks from daily files within the last 30 days are returned | Unit |
| AC-055B-03c | GIVEN tasks exist WHEN `task_query.py --range all` is called THEN all non-archived tasks are returned | Unit |
| AC-055B-03d | GIVEN tasks exist WHEN `task_query.py --status "done"` is called THEN only tasks with `status == "done"` are returned | Unit |
| AC-055B-03e | GIVEN tasks exist WHEN `task_query.py --search "keyword"` is called THEN tasks matching "keyword" in `task_id`, `task_type`, `description`, or `role` (case-insensitive) are returned | Unit |
| AC-055B-03f | GIVEN more tasks than page_size WHEN `task_query.py --page 2 --page-size 10` is called THEN results contain at most 10 tasks from the second page AND response includes `{"total": N, "page": 2, "page_size": 10, "total_pages": M}` | Unit |
| AC-055B-03g | GIVEN no tasks match the filters WHEN `task_query.py` is called THEN the output is `{"success": true, "data": {"tasks": [], "total": 0, "page": 1, "page_size": 50, "total_pages": 1}}` (not an error) | Unit |
| AC-055B-03h | GIVEN `--range` is not specified WHEN `task_query.py` is called THEN the default range is `1w` (last 7 days) AND default page is 1 AND default page_size is 50 | Unit |

### AC-055B-04: Task Query — Single Task by ID

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055B-04a | GIVEN a task_id that exists in the index WHEN `task_query.py --task-id TASK-XXX` is called THEN the index is used for O(1) file lookup AND the full task data is returned from the daily file | Unit |
| AC-055B-04b | GIVEN a task_id that does not exist in the index WHEN `task_query.py --task-id TASK-XXX` is called THEN the script exits with code 2 AND outputs `TASK_NOT_FOUND` error | Unit |
| AC-055B-04c | GIVEN a task_id lookup WHEN `task_query.py --task-id TASK-XXX` is called THEN the output format is `{"success": true, "data": {"task": {...}}}` (single task, not array) | Unit |

### AC-055B-05: Task Archival

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055B-05a | GIVEN a daily file `tasks-2026-04-01.json` exists WHEN `task_archive.py --date 2026-04-01` is called THEN the file is renamed to `tasks-2026-04-01.archived.json` AND all task_ids from that file are removed from `tasks-index.json` | Unit |
| AC-055B-05b | GIVEN no daily file exists for the specified date WHEN `task_archive.py --date 2026-04-01` is called THEN the script exits with code 2 AND outputs `FILE_NOT_FOUND` error | Unit |
| AC-055B-05c | GIVEN a daily file has already been archived (`*.archived.json` exists) WHEN `task_archive.py` is called for the same date THEN the script exits with code 1 AND outputs `ALREADY_ARCHIVED` error | Unit |
| AC-055B-05d | GIVEN a daily file is archived WHEN `task_query.py --range all` is later called THEN the archived tasks do NOT appear in results | Integration |

### AC-055B-06: Index Management

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055B-06a | GIVEN a task is created WHEN the create operation succeeds THEN `tasks-index.json` contains an entry `{task_id: {file: "tasks-YYYY-MM-DD.json", status: "...", last_updated: "..."}}` | Unit |
| AC-055B-06b | GIVEN a task is updated WHEN the update operation succeeds THEN the index entry's `status` and `last_updated` fields are synchronized with the task's new values | Unit |
| AC-055B-06c | GIVEN the index file does not exist WHEN any script is called THEN the index is auto-created with `{"_version": "1.0", "version": "1.0", "entries": {}}` | Unit |
| AC-055B-06d | GIVEN concurrent create operations target the same daily file WHEN both acquire locks THEN file locking serializes the writes AND both tasks are correctly stored AND the index is consistent | Integration |

### AC-055B-07: CLI Interface & Output

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055B-07a | GIVEN any script is called with `--help` WHEN argparse processes it THEN a usage message is displayed with all supported arguments | Unit |
| AC-055B-07b | GIVEN any successful operation WHEN the script completes THEN stdout contains valid JSON matching `{"success": true, "data": {...}}` AND exit code is 0 | Unit |
| AC-055B-07c | GIVEN any failed operation WHEN the script exits THEN stderr contains valid JSON matching `{"success": false, "error": "...", "message": "..."}` AND exit code is 1, 2, or 3 | Unit |
| AC-055B-07d | GIVEN all scripts WHEN their `main()` function is examined THEN each accepts an optional `argv` parameter for testability (`def main(argv: list[str] | None = None)`) | Unit |
| AC-055B-07e | GIVEN any script WHEN it imports shared utilities THEN it imports from `_board_lib` only (no third-party packages beyond stdlib + _board_lib) | Unit |

### AC-055B-08: Atomicity & Locking

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055B-08a | GIVEN a create or update operation WHEN the daily file is written THEN `with_file_lock` is used on a `.lock` file adjacent to the daily file AND `atomic_write_json` is used for the write | Unit |
| AC-055B-08b | GIVEN a create, update, or archive operation WHEN the index is written THEN `with_file_lock` is used on `tasks-index.json.lock` AND `atomic_write_json` is used for the write | Unit |
| AC-055B-08c | GIVEN a lock cannot be acquired within the timeout WHEN any script is called THEN the script exits with code 3 AND outputs `LOCK_TIMEOUT` error | Unit |
| AC-055B-08d | GIVEN a create operation fails after writing the daily file but before updating the index WHEN the error is caught THEN the daily file change is NOT rolled back (eventual consistency) AND the error is reported | Unit |

## Functional Requirements

### FR-1: Task Creation

**Description:** Create a new task in the current day's JSON file and register it in the index.

**Details:**
- Input: `--task '{json}'` (JSON string matching TASK_SCHEMA_V1, excluding `created_at`/`last_updated`)
- Process: Validate schema → optimistic duplicate check in index → acquire daily file lock → **nested:** acquire index lock → definitive duplicate check → append task to daily file → update index → release index lock → release daily lock
- Output: `{"success": true, "data": {"task_id": "...", "file": "tasks-YYYY-MM-DD.json"}}`
- Daily file structure: `{"_version": "1.0", "tasks": [...]}`

### FR-2: Task Update

**Description:** Update specific fields of an existing task using partial merge.

**Details:**
- Input: `--task-id TASK-XXX --updates '{json}'` (JSON with fields to update)
- Process: Look up file in index → validate update fields against schema → acquire daily file lock → merge fields → update last_updated → **nested:** acquire index lock → write daily file → sync index status/last_updated → release index lock → release daily lock
- Output: `{"success": true, "data": {"task_id": "...", "updated_fields": [...]}}`
- Immutable fields: `task_id`, `created_at`

### FR-3: Task Query (Filtered List)

**Description:** Query tasks with optional time range, status, search, and pagination filters.

**Details:**
- Input: `--range 1w|1m|all --status X --search "text" --page N --page-size N`
- Process: Read index → filter by date range (derive file dates from filenames) → load matching daily files → apply status/search filters → paginate → return
- Output: `{"success": true, "data": {"tasks": [...], "total": N, "page": N, "page_size": N, "total_pages": N}}`
- Defaults: range=1w, page=1, page_size=50
- Search: case-insensitive substring match on task_id, task_type, description, role

### FR-4: Task Query (Single by ID)

**Description:** Look up a single task by ID using the index for O(1) file resolution.

**Details:**
- Input: `--task-id TASK-XXX`
- Process: Read index → find file for task_id → read daily file → find task in array → return
- Output: `{"success": true, "data": {"task": {...}}}`

### FR-5: Task Archival

**Description:** Archive a daily task file and remove its entries from the active index.

**Details:**
- Input: `--date YYYY-MM-DD`
- Process: Check daily file exists → check not already archived → acquire daily file lock → read tasks and collect task_ids → **nested:** acquire index lock → rename to `.archived.json` → remove all task_ids from index → write index → release locks
- Output: `{"success": true, "data": {"archived_file": "...", "tasks_removed": N, "task_ids": [...]}}`

### FR-6: Index Management

**Description:** The index file (`tasks-index.json`) provides O(1) task-to-file lookups.

**Details:**
- Structure: `{"_version": "1.0", "version": "1.0", "entries": {"TASK-XXX": {"file": "tasks-YYYY-MM-DD.json", "status": "...", "last_updated": "..."}, ...}}`
- Auto-created on first use if missing
- Updated atomically on every create, update, and archive operation
- Read (but not locked) during query operations

## Non-Functional Requirements

### NFR-1: Performance

- Single task lookup via index: O(1) file resolution + O(n) scan within daily file (n = tasks in that day, typically < 50)
- Filtered query: O(d) daily files loaded where d = files in range window
- Index size: O(T) where T = total active tasks; ~100KB for 1000 tasks

### NFR-2: Reliability

- All file writes use `atomic_write_json` (crash-safe)
- All mutations protected by `with_file_lock` (concurrent-safe)
- Eventual consistency: daily file and index may briefly disagree if a script crashes mid-operation, but no data is lost

### NFR-3: Portability

- POSIX-only (fcntl.flock) — acceptable for this project
- All imports from Python stdlib + `_board_lib.py` only

## UI/UX Requirements

N/A — CLI scripts with structured JSON output.

## Dependencies

### Internal Dependencies

- **FEATURE-055-A (Board Shared Library):** Imports `_board_lib.py` for atomic I/O, file locking, schema validation, path resolution, output helpers, exit codes, and schema constants

### External Dependencies

- **Python 3.10+:** Uses pathlib, datetime, argparse, json from stdlib
- **POSIX OS:** File locking via fcntl (Linux, macOS)

## Business Rules

- **BR-1:** Task ID is provided by the caller and must be unique within the index
- **BR-2:** Tasks are stored in daily files based on creation date and never move between files on update
- **BR-3:** `created_at` and `last_updated` are system-managed; callers cannot set or override them
- **BR-4:** Schema validation is strict (rejects unknown fields) on both create and update
- **BR-5:** Archived files are renamed (not deleted) and excluded from queries and index
- **BR-6:** The index is the authoritative source for task-to-file mapping; query operations use it for routing

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| First-ever task_create.py call (no tasks/ dir, no index) | Auto-creates directory and index file, then creates the task |
| Create two tasks on the same day | Both go into the same `tasks-YYYY-MM-DD.json` file; locking serializes the writes |
| Update a task whose daily file was corrupted (invalid JSON) | `atomic_read_json` returns error dict; script exits with code 2 and error message |
| Query with all filters producing zero results | Returns `{"tasks": [], "total": 0}` — not an error |
| Archive a date with no file | Exit code 2, FILE_NOT_FOUND error |
| Archive a date that's already archived | Exit code 1, ALREADY_ARCHIVED error |
| task_query.py with both --task-id and --range | --task-id takes precedence (single lookup mode); --range is ignored |
| --page exceeds total pages | Returns empty tasks array with correct pagination metadata |
| Concurrent creates to different daily files | Each acquires its own daily file lock; no contention. Index lock serializes index updates. |
| Task JSON with extra whitespace or formatting | argparse captures the raw string; json.loads handles it normally |

## Out of Scope

- Feature CRUD operations (→ FEATURE-056-A)
- Flask API endpoints (→ FEATURE-055-C)
- Web UI (→ FEATURE-057-A)
- Task deletion (tasks are archived, not deleted)
- Task history / audit log (overwrite in place per KISS decision)
- Custom date range queries (--from/--to) — only 1w/1m/all presets
- Text output format (--format text) — JSON only for v1.0
- Dry-run mode — YAGNI
- Cross-file task migration on update — tasks stay in creation-date file

## Technical Considerations

- Scripts live in `.github/skills/x-ipe-tool-task-board-manager/scripts/` alongside `_board_lib.py`
- Import pattern: `sys.path.insert(0, str(Path(__file__).resolve().parent))` then `from _board_lib import ...`
- Each script defines `def main(argv: list[str] | None = None)` for testability
- Argument parsing uses `argparse.ArgumentParser` (consistent with existing scripts)
- Daily file naming: `tasks-YYYY-MM-DD.json` (e.g., `tasks-2026-04-03.json`)
- Archived file naming: `tasks-YYYY-MM-DD.archived.json`
- Index file: `tasks-index.json` in the same `tasks/` directory
- Lock files: `tasks-YYYY-MM-DD.json.lock` for daily files, `tasks-index.json.lock` for index
- Date range computation: `1w` = 7 days back, `1m` = 30 days back, `all` = no date filter
- Sort order for query results: `last_updated` descending (most recent first)

## Open Questions

None — all questions resolved via DAO decisions (04-03-2026).
