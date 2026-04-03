---
name: x-ipe-tool-task-board-manager
description: Manage tasks and features on the JSON-based project boards. Use for creating, updating, querying, and archiving tasks and features. Triggers on requests like "create task", "update task status", "query tasks", "create feature", "update feature", "query features".
---

# Task & Feature Board Manager

## Purpose

Provides CRUD operations for the JSON-based task board and feature board. All project tracking data is stored as JSON files managed by Python scripts with atomic file operations and concurrency-safe locking.

## Data Storage

| Board | Location | Format |
|-------|----------|--------|
| Tasks | `x-ipe-docs/planning/tasks/` | Daily files `tasks-YYYY-MM-DD.json` + `tasks-index.json` |
| Features | `x-ipe-docs/planning/features/features.json` | Single file with all features |

## Available Scripts

All scripts are in `.github/skills/x-ipe-tool-task-board-manager/scripts/`.

### Task Operations

| Script | Purpose | Example |
|--------|---------|---------|
| `task_create.py` | Create a new task | `uv run python scripts/task_create.py --title "Fix bug" --description "..." --assignee "Drift"` |
| `task_update.py` | Update task fields | `uv run python scripts/task_update.py TASK-123 --status done` |
| `task_query.py` | Query/search tasks | `uv run python scripts/task_query.py --status in_progress` |
| `task_archive.py` | Archive a task | `uv run python scripts/task_archive.py TASK-123` |

### Feature Operations

| Script | Purpose | Example |
|--------|---------|---------|
| `feature_create.py` | Create a new feature | `uv run python scripts/feature_create.py --epic-id EPIC-055 --feature-id FEATURE-055-A --title "..." --status Planned` |
| `feature_update.py` | Update feature fields | `uv run python scripts/feature_update.py FEATURE-055-A --status Completed` |
| `feature_query.py` | Query/search features | `uv run python scripts/feature_query.py --epic-id EPIC-055` |

### Migration

| Script | Purpose | Example |
|--------|---------|---------|
| `migrate.py` | Migrate from markdown boards to JSON | `uv run python scripts/migrate.py --all --dry-run` |

## Shared Library

`_board_lib.py` provides the foundation:
- `resolve_data_path(board_type)` — Locates data directory
- `atomic_read_json(path)` / `atomic_write_json(path, data)` — Thread-safe I/O
- `with_file_lock(path)` — fcntl-based file locking
- `generate_task_id()` / `validate_task(data)` / `validate_feature(data)` — ID generation & schema validation

## Task Data Model

```yaml
task_id: "TASK-XXX"        # Auto-generated sequential ID
title: "Task title"
description: "Detailed description"
status: "pending | in_progress | done | blocked | cancelled"
assignee: "Agent nickname"
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
output_links: []            # Paths to artifacts produced
next_task: ""               # Follow-up task reference
_version: "1.0"
```

## Feature Data Model

```yaml
feature_id: "FEATURE-XXX-Y"
epic_id: "EPIC-XXX"
title: "Feature title"
status: "Planned | Refined | Designed | Implemented | Tested | Completed | Retired"
version: "1.0"
description: ""
dependencies: []
artifact_links: []
_version: "1.0"
```

## Usage Pattern (for other skills)

```
# Creating a task
Use x-ipe-tool-task-board-manager to create a task:
  uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/task_create.py \
    --title "TASK_TITLE" --description "TASK_DESC" --assignee "NICKNAME"

# Updating task status
Use x-ipe-tool-task-board-manager to update task:
  uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/task_update.py \
    TASK-XXX --status done

# Querying tasks
Use x-ipe-tool-task-board-manager to query tasks:
  uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/task_query.py \
    --status in_progress --assignee "NICKNAME"
```

## Concurrency

- All operations use `fcntl.flock` file locking
- Tasks: nested locks (daily file → index)
- Features: single lock on features.json
- NEVER make parallel write calls — they must be sequential

## Notes

- No deletion: tasks are archived via `*.archived.json`; features use Retired status
- Schema validation rejects unknown fields
- All scripts output JSON to stdout for programmatic consumption
