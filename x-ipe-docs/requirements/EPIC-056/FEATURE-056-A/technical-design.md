# Technical Design: FEATURE-056-A — Feature CRUD Scripts

> **Feature ID:** FEATURE-056-A
> **Epic:** EPIC-056 (Feature Board Manager)
> **Version:** v1.0
> **Created:** 04-03-2026
> **Last Updated:** 04-03-2026

## Design Change Log

| Date | Change | Reason |
|------|--------|--------|
| 04-03-2026 | Initial design | FEATURE-056-A created |

---

# Part 1 — Design Summary

## Overview

Three CLI scripts (`feature_create.py`, `feature_update.py`, `feature_query.py`) operating on a single `features.json` file. All scripts use `_board_lib.py` for atomic I/O, file locking, and schema validation. Mirrors FEATURE-055-B (Task CRUD) patterns but simplified: single file (no daily files, no index, no archive).

## Architecture

```
.github/skills/x-ipe-tool-task-board-manager/scripts/
├── _board_lib.py          # Shared library (existing, FEATURE-055-A)
├── feature_create.py      # NEW — Create feature
├── feature_update.py      # NEW — Update feature
└── feature_query.py       # NEW — Query features (list/single/epic-summary)
```

## Data Model

### features.json

```json
{
  "_version": "1.0",
  "features": [
    {
      "feature_id": "FEATURE-055-A",
      "epic_id": "EPIC-055",
      "title": "Board Shared Library",
      "version": "v1.0",
      "status": "Completed",
      "description": "Shared library for board operations",
      "dependencies": ["FEATURE-054-A"],
      "specification_link": "x-ipe-docs/requirements/EPIC-055/FEATURE-055-A/specification.md",
      "created_at": "2026-04-03T10:00:00Z",
      "last_updated": "2026-04-03T12:00:00Z"
    }
  ]
}
```

### Valid Status Enum

```python
VALID_FEATURE_STATUSES = {"Planned", "Refined", "Designed", "Implemented", "Tested", "Completed", "Retired"}
```

### Immutable Fields

```python
IMMUTABLE_FIELDS = {"feature_id", "epic_id", "created_at"}
```

## Class Diagram

```
┌─────────────────────────────────────────┐
│           _board_lib (existing)         │
├─────────────────────────────────────────┤
│ + atomic_read_json(path) → dict         │
│ + atomic_write_json(path, data) → None  │
│ + with_file_lock(path, timeout) → ctx   │
│ + validate_schema(data, schema) → dict  │
│ + resolve_data_path("features") → Path  │
│ + output_result(result) → None          │
│ + exit_with_error(code, err, msg)       │
│ + FEATURE_SCHEMA_V1                     │
├─────────────────────────────────────────┤
│               ▲ ▲ ▲                     │
│     ┌─────────┼─┼─┼───────────┐        │
│     │         │ │ │           │        │
│  feature_  feature_  feature_          │
│  create    update    query             │
└─────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────────┐
│   feature_create.py  │  │   feature_update.py  │  │   feature_query.py       │
├──────────────────────┤  ├──────────────────────┤  ├──────────────────────────┤
│ + main(argv)         │  │ + main(argv)         │  │ + main(argv)             │
│ - _parse_args(argv)  │  │ - _parse_args(argv)  │  │ - _parse_args(argv)      │
│ - _validate_status() │  │ - _validate_updates()│  │ - _query_single(id, ...) │
│                      │  │                      │  │ - _query_list(feats, ..) │
│                      │  │                      │  │ - _epic_summary(feats, ..)│
│                      │  │                      │  │ - _matches_filters(..)   │
│                      │  │                      │  │ - _paginate(items, ..)   │
└──────────────────────┘  └──────────────────────┘  └──────────────────────────┘
```

## Sequence Diagram — Create Flow

```
User ──▶ feature_create.py
         │  _parse_args(argv)
         │  json.loads(--feature)
         │  validate_schema(data, FEATURE_SCHEMA_V1)
         │  _validate_status(data["status"])
         │  set created_at, last_updated
         │
         │  with_file_lock(features.json.lock):
         │    atomic_read_json(features.json) or init empty
         │    check duplicate feature_id
         │    append feature to array
         │    atomic_write_json(features.json, data)
         │
         │  output_result({"success": true, "data": {"feature_id": "..."}})
         ▼  exit(0)
```

## Sequence Diagram — Query Flow

```
User ──▶ feature_query.py
         │  _parse_args(argv)
         │
         ├─ IF --feature-id:
         │    _query_single(feature_id, features_path)
         │      atomic_read_json → scan array → found or NOT_FOUND
         │
         ├─ ELIF --epic-summary:
         │    _epic_summary(features, epic_id_filter)
         │      group by epic_id → count statuses → return summaries
         │
         └─ ELSE (list mode):
              _query_list(features, filters)
                _matches_filters → sort → _paginate → return
```

## AC Coverage

| AC ID | Mapped Component | Function |
|-------|-----------------|----------|
| AC-056A-01a | feature_create.py | main() |
| AC-056A-01b | feature_create.py | main() — auto-set timestamps |
| AC-056A-01c | feature_create.py | main() → validate_schema |
| AC-056A-01d | feature_create.py | main() → validate_schema (strict) |
| AC-056A-01e | feature_create.py | _validate_status() |
| AC-056A-02a | feature_create.py | main() — init empty file |
| AC-056A-02b | feature_create.py | main() — append |
| AC-056A-02c | feature_create.py | main() — duplicate check |
| AC-056A-02d | feature_create.py | main() — with_file_lock |
| AC-056A-03a | feature_update.py | main() |
| AC-056A-03b | feature_update.py | main() — auto-set last_updated |
| AC-056A-03c | feature_update.py | _validate_updates() — immutable check |
| AC-056A-03d | feature_update.py | _validate_updates() — unknown fields |
| AC-056A-03e | feature_update.py | main() — NOT_FOUND |
| AC-056A-04a | feature_update.py | _validate_updates() — status enum |
| AC-056A-04b | feature_update.py | _validate_updates() — invalid status |
| AC-056A-05a | feature_query.py | _query_list() — no filters |
| AC-056A-05b | feature_query.py | _matches_filters() — epic_id |
| AC-056A-05c | feature_query.py | _matches_filters() — status |
| AC-056A-05d | feature_query.py | _matches_filters() — search |
| AC-056A-05e | feature_query.py | _paginate() |
| AC-056A-05f | feature_query.py | _matches_filters() — AND logic |
| AC-056A-05g | feature_query.py | _query_list() — no file |
| AC-056A-06a | feature_query.py | _query_single() |
| AC-056A-06b | feature_query.py | _query_single() — NOT_FOUND |
| AC-056A-06c | feature_query.py | main() — single mode precedence |
| AC-056A-07a | feature_query.py | _epic_summary() |
| AC-056A-07b | feature_query.py | _epic_summary() — epic_id filter |
| AC-056A-07c | feature_query.py | _epic_summary() — all completed |
| AC-056A-07d | feature_query.py | _epic_summary() — empty |
| AC-056A-08a | all scripts | with_file_lock usage |
| AC-056A-08b | all scripts | LockTimeout handling |
| AC-056A-08c | all scripts | --lock-timeout arg |
| AC-056A-08d | all scripts | output_result / exit_with_error |
| AC-056A-08e | all scripts | argparse --help |

**Coverage: 35/35 ACs mapped**

---

# Part 2 — Implementation Guide

## File: feature_create.py

**Location:** `.github/skills/x-ipe-tool-task-board-manager/scripts/feature_create.py`

### Function: main(argv=None)

| Aspect | Detail |
|--------|--------|
| Signature | `def main(argv: list[str] \| None = None) -> None` |
| Purpose | Parse args, validate, lock, append feature to features.json |
| Algorithm | 1. Parse args (--feature JSON, --lock-timeout) 2. json.loads the feature string 3. validate_schema against FEATURE_SCHEMA_V1 4. _validate_status 5. Auto-set created_at + last_updated to ISO 8601 UTC 6. Lock features.json.lock 7. Read features.json (or init `{"_version":"1.0","features":[]}`) 8. Check duplicate feature_id 9. Append + atomic_write_json 10. output_result |
| Error Cases | VALIDATION_ERROR (exit 1), DUPLICATE_ERROR (exit 1), LOCK_TIMEOUT (exit 3) |

### Function: _parse_args(argv)

| Aspect | Detail |
|--------|--------|
| Signature | `def _parse_args(argv: list[str] \| None) -> argparse.Namespace` |
| Args | `--feature` (required, JSON string), `--lock-timeout` (int, default 10) |

### Function: _validate_status(status)

| Aspect | Detail |
|--------|--------|
| Signature | `def _validate_status(status: str) -> None` |
| Purpose | Check status against VALID_FEATURE_STATUSES set; exit_with_error if invalid |

## File: feature_update.py

**Location:** `.github/skills/x-ipe-tool-task-board-manager/scripts/feature_update.py`

### Function: main(argv=None)

| Aspect | Detail |
|--------|--------|
| Signature | `def main(argv: list[str] \| None = None) -> None` |
| Algorithm | 1. Parse args (--feature-id, --updates JSON, --lock-timeout) 2. json.loads the updates 3. _validate_updates 4. Lock features.json.lock 5. Read features.json 6. Find feature by feature_id (or NOT_FOUND exit 2) 7. Merge updates (dict.update) 8. Auto-set last_updated 9. atomic_write_json 10. output_result |
| Error Cases | VALIDATION_ERROR (exit 1), NOT_FOUND (exit 2), LOCK_TIMEOUT (exit 3) |

### Function: _parse_args(argv)

| Aspect | Detail |
|--------|--------|
| Args | `--feature-id` (required), `--updates` (required, JSON string), `--lock-timeout` (int, default 10) |

### Function: _validate_updates(updates)

| Aspect | Detail |
|--------|--------|
| Signature | `def _validate_updates(updates: dict) -> None` |
| Purpose | 1. Reject immutable fields (feature_id, epic_id, created_at) 2. Reject unknown fields (not in FEATURE_SCHEMA_V1) 3. Validate status enum if "status" in updates |

## File: feature_query.py

**Location:** `.github/skills/x-ipe-tool-task-board-manager/scripts/feature_query.py`

### Function: main(argv=None)

| Aspect | Detail |
|--------|--------|
| Signature | `def main(argv: list[str] \| None = None) -> None` |
| Algorithm | 1. Parse args 2. Route: `--feature-id` → _query_single, `--epic-summary` → _epic_summary, else → _query_list |

### Function: _parse_args(argv)

| Aspect | Detail |
|--------|--------|
| Args | `--feature-id` (optional), `--epic-summary` (flag), `--epic-id` (optional filter), `--status` (optional), `--search` (optional), `--page` (int, default 1), `--page-size` (int, default 50), `--lock-timeout` (int, default 10) |

### Function: _query_single(feature_id, features_path)

| Aspect | Detail |
|--------|--------|
| Purpose | Read features.json, linear scan for feature_id. O(n) but fine for small set. |
| Output | output_result with feature data, or exit_with_error NOT_FOUND (exit 2) |

### Function: _query_list(features, epic_id, status, search, page, page_size)

| Aspect | Detail |
|--------|--------|
| Purpose | Filter → sort by last_updated desc → paginate → output |
| Algorithm | 1. Read features.json (empty list if missing) 2. Filter with _matches_filters 3. Sort by last_updated descending 4. _paginate 5. output_result |

### Function: _epic_summary(features, epic_id_filter)

| Aspect | Detail |
|--------|--------|
| Purpose | Group features by epic_id, count statuses per epic |
| Output | `[{"epic_id": "EPIC-055", "total": 3, "Planned": 0, "Completed": 3, ...}]` |
| Algorithm | 1. Read features.json 2. Group by epic_id 3. Optional epic_id filter 4. For each epic: count per-status 5. Return list |

### Function: _matches_filters(feature, epic_id, status, search)

| Aspect | Detail |
|--------|--------|
| Purpose | AND-combined filter: epic_id exact, status exact, search case-insensitive across feature_id, title, description, epic_id |

### Function: _paginate(items, page, page_size)

| Aspect | Detail |
|--------|--------|
| Purpose | Slice items and return with pagination metadata |
| Output | `{"items": [...], "page": N, "page_size": N, "total": N, "total_pages": N}` |

---

## Design Constraints

1. **Single file**: All features in one `features.json` — no daily files, no index
2. **No archive/delete**: Use `Retired` status for soft-delete
3. **Locking**: Single lock file `features.json.lock` for all write ops
4. **KISS**: Linear scan for lookups (features count is small, <100)
5. **Consistent patterns**: Same output format, exit codes, arg parsing as Task CRUD
