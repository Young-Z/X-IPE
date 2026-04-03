# Requirement Details - Part 23

> Continued from: [requirement-details-part-22.md](x-ipe-docs/requirements/requirement-details-part-22.md)
> Created: 04-03-2026

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-055-A | EPIC-055 | Board Shared Library | v1.0 | Atomic JSON I/O, file locking, schema validation, path resolution utilities shared across board managers. | None |
| FEATURE-055-B | EPIC-055 | Task CRUD Scripts | v1.0 | CLI scripts for task create, update, query, archive with daily file and index management. | FEATURE-055-A |
| FEATURE-055-C | EPIC-055 | Task Board API | v1.0 | Flask GET endpoints for tasks with time range, status, search, and pagination filtering. | FEATURE-055-B |
| FEATURE-056-A | EPIC-056 | Feature CRUD Scripts | v1.0 | CLI scripts for feature create, update, query with Epic grouping and computed status. | FEATURE-055-A |
| FEATURE-056-B | EPIC-056 | Feature Board API | v1.0 | Flask GET endpoints for features with Epic grouping, status filter, and search. | FEATURE-056-A |
| FEATURE-057-A | EPIC-057 | Task Board Web Page | v1.0 | View-only HTML/JS page with time range toggle, status filter, search, pagination. | FEATURE-055-C |
| FEATURE-057-B | EPIC-057 | Feature Board Web Page | v1.0 | View-only HTML/JS page with Epic accordion grouping, status badges, progress bars. | FEATURE-056-B |
| FEATURE-057-C | EPIC-057 | Data Migration | v1.0 | Migrate task-board.md and features.md to JSON via CRUD scripts with validation. | FEATURE-055-B, FEATURE-056-A |
| FEATURE-057-D | EPIC-057 | Skill Updates | v1.0 | Update ~34 referencing skills to use new JSON-based board manager scripts. | FEATURE-057-C |
| FEATURE-057-E | EPIC-057 | Cleanup & Scaffold Update | v1.0 | Remove deprecated markdown files and skills, update scaffold to init JSON. | FEATURE-057-D |

---

## Linked Mockups

| Mockup Function Name | Epic | Mockup List |
|---------------------|------|-------------|
| Task Board Page | EPIC-055 | [task-board-v1.html](x-ipe-docs/requirements/EPIC-055/mockups/task-board-v1.html) |
| Feature Board Page | EPIC-056 | [feature-board-v1.html](x-ipe-docs/requirements/EPIC-056/mockups/feature-board-v1.html) |

---

## Feature Details

## EPIC-055: Task Board Manager

### Project Overview

Replace the current markdown-based `task-board.md` with a JSON data layer managed by a dedicated skill (`x-ipe-tool-task-board-manager`). Provide CRUD operations via standalone Python scripts and a read-only Flask API endpoint (`GET /api/tasks`) for the web UI.

### User Request

Separate data and UI concerns for the task board. AI agents should manage task data programmatically via scripts (not by editing markdown tables). Humans should browse tasks via a filtered, searchable, paginated web page.

### Clarifications

| Question | Answer |
|----------|--------|
| JSON granularity for tasks? | Daily files: `tasks-YYYY-MM-DD.json` (ISO 8601) |
| Task deletion approach? | No deletion — archive daily files by renaming to `tasks-YYYY-MM-DD.archived.json`; UI/API skips archived files |
| Change history on update? | No history — overwrite in place (KISS) |
| Task file on update? | Task stays in creation-date file (never moves between daily files) |
| API schema vs file schema? | Same single schema — no computed fields in API |
| Migration approach? | AI agent migrates existing markdown → JSON, then remove old .md |
| Skill update scope? | Update all ~34 referencing skills in one go (clean break) — handled in EPIC-057 |
| Filter basis? | Last updated date (most useful for "recently active" work) |
| Pagination default? | 50 tasks per page, configurable via `?page_size=` |
| Schema validation? | Strict — reject writes if schema doesn't match (fail fast) |
| Web UI scope? | View-only — agents manage, humans browse |
| Workflow awareness? | Workflow-agnostic — standalone CRUD, no workflow integration |

### High-Level Requirements

1. **JSON Data Layer** — Daily task files (`tasks-YYYY-MM-DD.json`) in `x-ipe-docs/planning/tasks/` with a `tasks-index.json` for O(1) lookups by task ID
2. **CRUD Scripts** — `task_create.py`, `task_update.py`, `task_query.py`, `task_archive.py` in skill folder `.github/skills/x-ipe-tool-task-board-manager/scripts/`
3. **Shared Library** — `_board_lib.py` with atomic JSON I/O (`tempfile → fsync → os.replace`), file locking (`fcntl.flock`), schema validation
4. **Task Index** — `tasks-index.json` maps `task_id → {file, status, last_updated}` for fast lookups without scanning all daily files
5. **Task Archiving** — Rename daily file to `tasks-YYYY-MM-DD.archived.json`; index entries updated; API/UI ignores archived files
6. **Schema Validation** — Strict validation on every write; reject non-conforming data with exit code 1
7. **Concurrency Safety** — Lock-per-daily-file via `fcntl.flock` with configurable timeout (default 10s)
8. **Flask API** — `GET /api/tasks` with query params: `range` (1w/1m/all), `status`, `search`, `page`, `page_size`; `GET /api/tasks/<task_id>` for single task
9. **Structured Output** — All scripts output `{"success": true/false, "data": {...}, "error": "..."}` with exit codes 0/1/2/3

### Task JSON Schema

```json
{
  "task_id": "TASK-1052",
  "task_type": "Ideation",
  "description": "Refine idea 039...",
  "role": "Drift 🌊",
  "status": "in_progress",
  "created_at": "2026-04-03T03:10:00Z",
  "last_updated": "2026-04-03T03:45:00Z",
  "output_links": [],
  "next_task": "x-ipe-task-based-requirement-gathering"
}
```

### Index JSON Schema

```json
{
  "version": "1.0",
  "entries": {
    "TASK-1052": {
      "file": "tasks-2026-04-03.json",
      "status": "in_progress",
      "last_updated": "2026-04-03T03:45:00Z"
    }
  }
}
```

### Constraints

- Python stdlib only (zero external deps)
- All scripts standalone CLI via argparse
- Exit codes: 0=success, 1=validation error, 2=not found, 3=lock timeout
- JSON files with `indent=2` for git-friendly diffs
- ISO 8601 dates for sortable filenames and timestamps
- Tasks never move between daily files (stay in creation-date file)
- No write operations via web UI or API

### Open Questions

- None (all resolved during ideation and requirement gathering)

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| Task Board Page | [task-board-v1.html](x-ipe-docs/requirements/EPIC-055/mockups/task-board-v1.html) |

### Related Features

- **FEATURE-035-B** (EPIC-035): [RETIRED by EPIC-055] — Feature Board Epic Tracking (markdown approach superseded by JSON)
- **EPIC-036**: Engineering Workflow View — adjacent concern, no integration required (workflow-agnostic)
- **EPIC-052**: Replace MCP Server with Scripts — architectural alignment (same atomic I/O patterns)

### Feasibility Notes

| Risk | Severity | Mitigation |
|------|----------|------------|
| Concurrency: multiple agents writing daily files | MEDIUM | Lock-per-daily-file with `fcntl.flock` (proven pattern) |
| Index performance at 10,000+ entries | LOW | JSON index stays in memory during query; lazy-load daily files |
| Daily file proliferation over months | LOW | Archive old files; index provides fast lookup regardless |

---

## EPIC-056: Feature Board Manager

### Project Overview

Replace the current markdown-based `features.md` with a JSON data layer managed by a dedicated skill (`x-ipe-tool-feature-board-manager`). Provide CRUD operations via standalone Python scripts and a read-only Flask API endpoint (`GET /api/features`) for the web UI.

### User Request

Separate data and UI concerns for the feature board. AI agents should manage feature data programmatically via scripts. Humans should browse features grouped by Epic via a filtered, searchable web page.

### Clarifications

| Question | Answer |
|----------|--------|
| Feature file structure? | Single `features.json` file in `x-ipe-docs/planning/features/` |
| Feature deletion? | No deletion — features stay forever, use status lifecycle (Planned → Completed / Retired) |
| Feature archiving? | No archiving — all features always visible, filtered by status in UI |
| Schema validation? | Strict — reject writes if schema doesn't match (fail fast) |
| Concurrency? | Single lock for `features.json` (one file, one lock) |
| Epic grouping? | Features grouped by `epic_id` in both data schema and UI |
| Workflow integration? | Workflow-agnostic — standalone CRUD |

### High-Level Requirements

1. **JSON Data Layer** — Single `features.json` in `x-ipe-docs/planning/features/` with all features as an array
2. **CRUD Scripts** — `feature_create.py`, `feature_update.py`, `feature_query.py` in skill folder `.github/skills/x-ipe-tool-feature-board-manager/scripts/`
3. **Shared Library** — `_board_lib.py` with atomic JSON I/O, file locking, schema validation (shared with EPIC-055 or duplicated)
4. **Epic Grouping** — Features include `epic_id` field; API supports `?epic_id=EPIC-055` filter
5. **Status Lifecycle** — Planned → Refined → Designed → Implemented → Tested → Completed (also: Retired)
6. **Schema Validation** — Strict validation on every write
7. **Concurrency Safety** — Single file lock via `fcntl.flock` for `features.json`
8. **Flask API** — `GET /api/features` with query params: `epic_id`, `status`, `search`, `page`, `page_size`; `GET /api/features/<feature_id>` for single feature
9. **Computed Epic Status** — Epic status derived from constituent features (all completed → completed, any in_progress → in_progress)

### Feature JSON Schema

```json
{
  "epic_id": "EPIC-054",
  "feature_id": "FEATURE-054-A",
  "title": "Learn Panel UI",
  "version": "v0.6",
  "status": "Completed",
  "specification_link": "x-ipe-docs/requirements/EPIC-054/FEATURE-054-A/specification.md",
  "technical_design_link": "x-ipe-docs/requirements/EPIC-054/FEATURE-054-A/technical-design.md",
  "created_at": "2026-04-02T00:00:00Z",
  "last_updated": "2026-04-03T00:00:00Z"
}
```

### Constraints

- Python stdlib only (zero external deps)
- All scripts standalone CLI via argparse
- Exit codes: 0=success, 1=validation error, 2=not found, 3=lock timeout
- JSON files with `indent=2` for git-friendly diffs
- Features never deleted — status lifecycle only
- No write operations via web UI or API

### Open Questions

- None

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| Feature Board Page | [feature-board-v1.html](x-ipe-docs/requirements/EPIC-056/mockups/feature-board-v1.html) |

### Related Features

- **FEATURE-035-B** (EPIC-035): [RETIRED by EPIC-055/EPIC-056] — Feature Board Epic Tracking (markdown approach superseded)
- **FEATURE-035-C** (EPIC-035): [RETIRED by EPIC-057] — Feature Lifecycle Skill Updates (path-only updates superseded by full JSON migration)

### Feasibility Notes

| Risk | Severity | Mitigation |
|------|----------|------------|
| Single file lock contention | LOW | Feature updates are infrequent; lock timeout handles rare contention |
| features.json size at 200+ features | LOW | ~200 features × ~300 bytes = ~60KB — trivially small |

---

## EPIC-057: Board Web Pages & Migration

### Project Overview

Create view-only web pages for the Task Board and Feature Board that consume the JSON APIs from EPIC-055 and EPIC-056. Migrate existing data from `task-board.md` and `features.md` to JSON format. Update ~34 referencing skills to use the new board manager skills.

### User Request

Build web UI pages for humans to browse task and feature data with filtering, search, and pagination. Migrate all existing data from markdown to JSON. Update all skills that currently edit markdown boards to use the new JSON-based manager scripts.

### Clarifications

| Question | Answer |
|----------|--------|
| Web page scope? | Only Task Board and Feature Board pages (no sidebar changes) |
| Error handling in UI? | Inline "No tasks found" or "Error loading" messages — no dedicated error page |
| UI features? | Status color coding + clickable output links + search + pagination |
| Migration approach? | AI agent reads markdown, writes JSON via new scripts, validates completeness |
| Skill update strategy? | Update all ~34 referencing skills in one go (clean break) |
| Web framework? | Existing Flask app + Jinja templates + vanilla JS (consistent with codebase) |

### High-Level Requirements

1. **Task Board Web Page** — HTML page fetching `GET /api/tasks` with:
   - Time range toggle: 1 week (default) / 1 month / All
   - Status filter dropdown: All / In Progress / Completed / Blocked / Pending
   - Free-text search across task ID, description, role
   - Status color coding (🟢 done, 🔵 in_progress, 🟡 pending, 🔴 blocked)
   - Clickable output links (open in preview modal)
   - Pagination at 50 items/page (configurable)
2. **Feature Board Web Page** — HTML page fetching `GET /api/features` with:
   - Epic grouping: collapsible accordion per EPIC
   - Status filter: All / Planned / Refined / Designed / Implemented / Tested / Completed
   - Search by feature ID, title, Epic ID
   - Clickable specification and design links
   - Status badges with color coding
   - Epic-level progress bar
3. **Data Migration** — Script or agent workflow that:
   - Reads all rows from current `task-board.md` markdown table
   - Writes each task to appropriate daily JSON file via `task_create.py`
   - Reads all rows from current `features.md` markdown table
   - Writes each feature to `features.json` via `feature_create.py`
   - Validates: JSON task count == markdown row count (100% coverage)
4. **Skill Updates (~34 skills)** — Update every skill that references `task-board.md`, `features.md`, or the current board management skills to use the new `x-ipe-tool-task-board-manager` and `x-ipe-tool-feature-board-manager` scripts
5. **Cleanup** — After migration validation:
   - Remove `task-board.md` and `features.md` from `x-ipe-docs/planning/`
   - Update scaffold templates in `src/x_ipe/core/scaffold.py` to initialize JSON structure
   - Remove deprecated board management skills (`x-ipe+all+task-board-management`, `x-ipe+feature+feature-board-management`)

### Constraints

- Web pages are view-only (no edit capability)
- Pages use existing Flask app architecture (Jinja templates + vanilla JS)
- Migration must achieve 100% data coverage (validated by count comparison)
- Skill updates must be validated individually (each skill tested after update)
- No sidebar/navigation changes (pages accessible via direct URL or existing file browser)

### Open Questions

- None

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| Task Board Page | [task-board-v1.html](x-ipe-docs/requirements/EPIC-057/mockups/task-board-v1.html) |
| Feature Board Page | [feature-board-v1.html](x-ipe-docs/requirements/EPIC-057/mockups/feature-board-v1.html) |

### Related Features

- **EPIC-055**: Task Board Manager — provides `/api/tasks` consumed by the Task Board page
- **EPIC-056**: Feature Board Manager — provides `/api/features` consumed by the Feature Board page
- **FEATURE-035-C** (EPIC-035): [RETIRED by EPIC-057] — Feature Lifecycle Skill Updates (10+ skills superseded by this broader 34-skill migration)
- **FEATURE-035-E** (EPIC-035): Retroactive Feature Migration — folder structure migration that should be coordinated with data migration
- **EPIC-052**: Replace MCP Server with Scripts — architectural alignment (same script-based approach)

### Feasibility Notes

| Risk | Severity | Mitigation |
|------|----------|------------|
| 34-skill update scope is large | HIGH | Batch by category; validate each skill with test run; rollback plan per skill |
| Migration data loss | MEDIUM | Post-migration validation script comparing row counts; manual spot-check |
| EPIC-035-E folder migration alignment | MEDIUM | Sequence: EPIC-055/056 first, then EPIC-057 migration, coordinate with EPIC-035-E |
| Removing deprecated skills breaks in-progress agents | LOW | Announce deprecation, complete all active tasks before removal |

### Cross-Epic Dependency Chain

```
EPIC-055 (Task Board Manager) ─┐
                                ├──► EPIC-057 (Web Pages + Migration)
EPIC-056 (Feature Board Manager)─┘
```

EPIC-057 depends on both EPIC-055 and EPIC-056 being completed first (APIs must exist before web pages can consume them, and scripts must exist before migration can run).

---

## Feature Details

### FEATURE-055-A: Board Shared Library

**Version:** v1.0
**Brief Description:** Shared Python library providing atomic JSON I/O, file locking, schema validation, and path resolution utilities for both task and feature board managers.

**Acceptance Criteria:**
- [ ] `_board_lib.py` provides `atomic_read_json(path)` that reads and parses JSON files safely
- [ ] `_board_lib.py` provides `atomic_write_json(path, data)` using tempfile → fsync → os.replace pattern
- [ ] File locking via `fcntl.flock` with configurable timeout (default 10s); raises LockTimeout on failure
- [ ] `validate_schema(data, schema)` function validates JSON data against a Python dict schema; rejects non-conforming data
- [ ] Task schema and Feature schema defined as Python constants
- [ ] `resolve_data_path(data_type)` returns correct directory path for tasks or features
- [ ] All functions use stdlib only (no external dependencies)
- [ ] Structured error output: `{"success": false, "error": "description"}` on failure

**Dependencies:**
- None (foundation feature)

**Technical Considerations:**
- Follow existing pattern from `.github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/_lib.py`
- Exit codes: 0=success, 1=validation, 2=not found, 3=lock timeout
- Schema validation should be strict (reject unknown fields)
- File locking: `fcntl.LOCK_EX | fcntl.LOCK_NB` with retry loop

---

### FEATURE-055-B: Task CRUD Scripts

**Version:** v1.0
**Brief Description:** Standalone CLI scripts for creating, updating, querying, and archiving tasks, with daily file storage and index management.

**Acceptance Criteria:**
- [ ] `task_create.py --task '{json}'` creates a task in `tasks-YYYY-MM-DD.json` (today's file) and updates `tasks-index.json`
- [ ] `task_update.py --task-id TASK-XXX --updates '{json}'` updates task in its creation-date file and updates index
- [ ] `task_query.py --range 1w|1m|all --status X --search "text" --page N --page-size N` returns filtered tasks
- [ ] `task_query.py --task-id TASK-XXX` returns a single task by ID using index for O(1) lookup
- [ ] `task_archive.py --date YYYY-MM-DD` renames daily file to `*.archived.json` and removes entries from index
- [ ] All scripts output `{"success": true, "data": {...}}` on success
- [ ] Schema validation runs on every create/update; rejects invalid data with exit code 1
- [ ] Concurrent writes to same daily file are serialized via file locking
- [ ] `tasks-index.json` maps `task_id → {file, status, last_updated}` and is updated atomically on every write

**Dependencies:**
- FEATURE-055-A: Uses `_board_lib.py` for atomic I/O, locking, validation

**Technical Considerations:**
- Task stays in creation-date daily file (never moves on update)
- Index provides O(1) lookup without scanning all daily files
- `task_query.py` with range filter reads index first, then only loads relevant daily files
- Archived files (`*.archived.json`) are skipped by query

---

### FEATURE-055-C: Task Board API

**Version:** v1.0
**Brief Description:** Flask read-only API endpoints for querying tasks with time range, status, search, and pagination.

**Acceptance Criteria:**
- [ ] `GET /api/tasks` returns tasks filtered by `range` (1w default, 1m, all), `status`, `search`, `page`, `page_size` (50 default)
- [ ] `GET /api/tasks/<task_id>` returns a single task or 404
- [ ] Response schema matches JSON file schema (no computed fields)
- [ ] Response includes pagination metadata: `{"tasks": [...], "total": N, "page": N, "page_size": N, "total_pages": N}`
- [ ] Search matches against task_id, description, and role fields (case-insensitive)
- [ ] API reads `tasks-index.json` for efficient filtering before loading daily files
- [ ] Returns `{"tasks": [], "total": 0}` when no results match (not an error)

**Dependencies:**
- FEATURE-055-B: Uses task data files and index created by CRUD scripts

**Technical Considerations:**
- Follow existing Flask route pattern from `src/x_ipe/routes/`
- Register blueprint in main app
- No write endpoints (view-only)
- Consider caching index in memory for repeated requests within same page load

---

### FEATURE-056-A: Feature CRUD Scripts

**Version:** v1.0
**Brief Description:** Standalone CLI scripts for creating, updating, and querying features in `features.json` with Epic grouping and computed Epic status.

**Acceptance Criteria:**
- [ ] `feature_create.py --feature '{json}'` adds a feature to `features.json` and validates schema
- [ ] `feature_update.py --feature-id FEATURE-XXX-X --updates '{json}'` updates a feature in place
- [ ] `feature_query.py --epic-id EPIC-XXX --status X --search "text" --page N --page-size N` returns filtered features
- [ ] `feature_query.py --feature-id FEATURE-XXX-X` returns a single feature
- [ ] `feature_query.py --epic-summary` returns per-Epic computed status (all completed → completed, any in_progress → in_progress)
- [ ] All scripts output structured JSON with `{"success": true, "data": {...}}`
- [ ] Schema validation on every create/update; rejects invalid data with exit code 1
- [ ] Single file lock for `features.json` via `fcntl.flock`

**Dependencies:**
- FEATURE-055-A: Uses `_board_lib.py` for atomic I/O, locking, validation

**Technical Considerations:**
- Features stored as JSON array in single file (not daily files)
- No delete/archive — status lifecycle only (Planned → Completed/Retired)
- Epic status is computed at query time, not stored

---

### FEATURE-056-B: Feature Board API

**Version:** v1.0
**Brief Description:** Flask read-only API endpoints for querying features with Epic grouping, status filter, and search.

**Acceptance Criteria:**
- [ ] `GET /api/features` returns features with optional `epic_id`, `status`, `search`, `page`, `page_size` filters
- [ ] `GET /api/features/<feature_id>` returns a single feature or 404
- [ ] Default response groups features by `epic_id` with computed Epic status
- [ ] Response includes pagination metadata
- [ ] Search matches against feature_id, title, and epic_id (case-insensitive)
- [ ] Returns `{"features": [], "total": 0}` when no results match

**Dependencies:**
- FEATURE-056-A: Uses features.json data created by CRUD scripts

**Technical Considerations:**
- Follow same Flask blueprint pattern as FEATURE-055-C
- Epic grouping can be done in Python after loading features.json
- Consider flat vs grouped response modes (`?group_by=epic` parameter)

---

### FEATURE-057-A: Task Board Web Page

**Version:** v1.0
**Brief Description:** View-only web page displaying tasks from `/api/tasks` with time range toggle, status filter, search, pagination, and color-coded status badges.

**Acceptance Criteria:**
- [ ] HTML page served at a route accessible from the X-IPE web app
- [ ] Time range toggle: 1 week (default) / 1 month / All — fetches from `/api/tasks?range=X`
- [ ] Status filter dropdown: All / In Progress / Completed / Blocked / Pending / Deferred
- [ ] Free-text search bar filtering by task ID, description, role
- [ ] Status badges with color coding: 🟢 done, 🔵 in_progress, 🟡 pending, 🔴 blocked
- [ ] Clickable output links opening in preview modal
- [ ] Pagination controls with 50 items/page default
- [ ] Inline "No tasks found" message when filter returns empty results
- [ ] Inline "Error loading tasks" message on API failure

**Dependencies:**
- FEATURE-055-C: Consumes `/api/tasks` endpoint

**Technical Considerations:**
- Use Jinja template + vanilla JS (consistent with codebase)
- Apply theme-default design tokens (Slate/Emerald palette)
- Reference mockup: [task-board-v1.html](x-ipe-docs/requirements/EPIC-057/mockups/task-board-v1.html)

---

### FEATURE-057-B: Feature Board Web Page

**Version:** v1.0
**Brief Description:** View-only web page displaying features from `/api/features` with Epic accordion grouping, status badges, progress bars, and search.

**Acceptance Criteria:**
- [ ] HTML page served at a route accessible from the X-IPE web app
- [ ] Epic accordion grouping: collapsible sections per EPIC with per-Epic progress bar
- [ ] Status filter: All / Planned / Refined / Designed / Implemented / Tested / Completed
- [ ] Search bar filtering by feature ID, title, Epic ID
- [ ] Status badges with color coding per feature status
- [ ] Clickable specification and design links opening in preview modal
- [ ] Pagination controls
- [ ] Inline empty/error state messages

**Dependencies:**
- FEATURE-056-B: Consumes `/api/features` endpoint

**Technical Considerations:**
- Same Jinja + vanilla JS pattern as Task Board page
- Reference mockup: [feature-board-v1.html](x-ipe-docs/requirements/EPIC-057/mockups/feature-board-v1.html)

---

### FEATURE-057-C: Data Migration

**Version:** v1.0
**Brief Description:** Migrate existing task-board.md and features.md data to JSON format using CRUD scripts, with row-count validation.

**Acceptance Criteria:**
- [ ] AI agent reads all rows from `task-board.md` markdown table
- [ ] Each task row written to appropriate daily JSON file via `task_create.py`
- [ ] AI agent reads all rows from `features.md` markdown table
- [ ] Each feature row written to `features.json` via `feature_create.py`
- [ ] Post-migration validation: JSON task count == markdown task row count
- [ ] Post-migration validation: JSON feature count == markdown feature row count
- [ ] Every task ID from markdown exists in `tasks-index.json`
- [ ] Migration script/procedure is repeatable (can re-run safely)

**Dependencies:**
- FEATURE-055-B: Uses `task_create.py` for writing tasks
- FEATURE-056-A: Uses `feature_create.py` for writing features

**Technical Considerations:**
- Migration may be a script or an agent-driven procedure
- Handle markdown parsing edge cases (multi-line descriptions, special characters)
- Consider dry-run mode for validation before actual write

---

### FEATURE-057-D: Skill Updates

**Version:** v1.0
**Brief Description:** Update ~34 referencing skills to use new JSON-based board manager scripts instead of markdown editing.

**Acceptance Criteria:**
- [ ] All skills referencing `task-board.md` updated to call `x-ipe-tool-task-board-manager` scripts
- [ ] All skills referencing `features.md` updated to call `x-ipe-tool-feature-board-manager` scripts
- [ ] All skills referencing `x-ipe+all+task-board-management` updated to use new skill
- [ ] All skills referencing `x-ipe+feature+feature-board-management` updated to use new skill
- [ ] Each updated skill tested to verify correct behavior after change
- [ ] Git commit message format includes `[EPIC-057]` prefix for Epic reference

**Dependencies:**
- FEATURE-057-C: Migration must complete before skills can reference JSON data

**Technical Considerations:**
- Changes are to SKILL.md files (agent skills), not application code
- Batch by category: lifecycle skills, board management skills, workflow skills
- Consider creating a checklist of all 34 skills before starting

---

### FEATURE-057-E: Cleanup & Scaffold Update

**Version:** v1.0
**Brief Description:** Remove deprecated markdown board files and skills, update scaffold to initialize JSON data structure.

**Acceptance Criteria:**
- [ ] `x-ipe-docs/planning/task-board.md` removed from repository
- [ ] `x-ipe-docs/planning/features.md` removed from repository
- [ ] `src/x_ipe/core/scaffold.py` updated to create `x-ipe-docs/planning/tasks/` with empty `tasks-index.json`
- [ ] `src/x_ipe/core/scaffold.py` updated to create `x-ipe-docs/planning/features/` with empty `features.json`
- [ ] Deprecated skill `x-ipe+all+task-board-management` removed or archived
- [ ] Deprecated skill `x-ipe+feature+feature-board-management` removed or archived
- [ ] No remaining references to old markdown board files in any skill

**Dependencies:**
- FEATURE-057-D: All skills must be updated before removing old files

**Technical Considerations:**
- Verify no active in-progress tasks reference old board files before removal
- Git history preserves old files if rollback is needed

---

## Notes

- This document was created during Requirement Gathering (TASK-1057) and Feature Breakdown (TASK-1058)
- Individual feature specifications will be created during Feature Refinement
- Feature status tracked on the feature board (features.md) via feature-board-management skill
- Implementation order: EPIC-055 → EPIC-056 → EPIC-057 (sequential dependency chain)
