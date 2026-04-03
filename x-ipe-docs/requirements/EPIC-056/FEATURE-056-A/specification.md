# Specification: FEATURE-056-A — Feature CRUD Scripts

> **Feature ID:** FEATURE-056-A
> **Epic:** EPIC-056 (Feature Board Manager)
> **Version:** v1.0
> **Status:** Refined
> **Created:** 04-03-2026
> **Last Updated:** 04-03-2026

## Overview

Standalone CLI scripts for creating, updating, and querying features in a single `features.json` file. Uses `_board_lib.py` for atomic I/O, schema validation, and file locking. Mirrors FEATURE-055-B (Task CRUD) patterns but adapted for the single-file feature store.

## Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-055-A | Feature | `_board_lib.py` — atomic I/O, locking, validation, FEATURE_SCHEMA_V1 |

## Linked Mockups

N/A — CLI scripts only, no UI.

## DAO Design Decisions

| # | Decision | Detail |
|---|----------|--------|
| 1 | Status enum | Validated: `Planned`, `Refined`, `Designed`, `Implemented`, `Tested`, `Completed`, `Retired` |
| 2 | Epic summary | Count-based: `{"total": N, "Planned": X, "Completed": Y, ...}` |
| 3 | feature_id | Caller-provided (not auto-generated) |
| 4 | Immutable fields | `feature_id`, `epic_id`, `created_at` |
| 5 | Pagination defaults | page=1, page_size=50 (same as tasks) |
| 6 | Dependency validation | Store as strings, no existence check (YAGNI) |
| 7 | Script count | 3 scripts: create, update, query. No archive (status lifecycle) |

---

## Acceptance Criteria

### Group 1: Feature Create — Basic (5 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056A-01a | GIVEN valid feature JSON with all required fields WHEN `feature_create.py --feature '{json}'` is run THEN the feature is appended to `features.json` and `{"success": true, "data": {"feature_id": "..."}}` is written to stdout | Unit |
| AC-056A-01b | GIVEN a new feature WHEN created THEN `created_at` and `last_updated` are auto-set to ISO 8601 UTC even if provided in input | Unit |
| AC-056A-01c | GIVEN feature JSON missing a required field (e.g. no `title`) WHEN create is run THEN exit code 1 with `{"success": false, "error": "VALIDATION_ERROR", "message": "..."}` to stderr | Unit |
| AC-056A-01d | GIVEN feature JSON with an unknown field WHEN create is run THEN exit code 1 with VALIDATION_ERROR (strict schema) | Unit |
| AC-056A-01e | GIVEN a feature with `status` not in the valid enum WHEN create is run THEN exit code 1 with VALIDATION_ERROR | Unit |

### Group 2: Feature Create — File Operations (4 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056A-02a | GIVEN `features.json` does not exist WHEN create is run THEN a new file is created with `{"_version": "1.0", "features": [feature]}` | Unit |
| AC-056A-02b | GIVEN `features.json` exists with features WHEN create is run THEN the new feature is appended to the array | Unit |
| AC-056A-02c | GIVEN a duplicate `feature_id` already exists WHEN create is run THEN exit code 1 with `DUPLICATE_ERROR` | Unit |
| AC-056A-02d | GIVEN concurrent create calls WHEN both run THEN file locking ensures no data loss (atomic write via `_board_lib`) | Integration |

### Group 3: Feature Update — Basic (5 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056A-03a | GIVEN existing feature WHEN `feature_update.py --feature-id FEATURE-XXX --updates '{json}'` is run THEN fields are merged and `{"success": true, "data": {"feature_id": "..."}}` is written to stdout | Unit |
| AC-056A-03b | GIVEN an update WHEN applied THEN `last_updated` is auto-set to current ISO 8601 UTC | Unit |
| AC-056A-03c | GIVEN an update containing immutable field (`feature_id`, `epic_id`, or `created_at`) WHEN update is run THEN exit code 1 with VALIDATION_ERROR | Unit |
| AC-056A-03d | GIVEN an update with unknown field WHEN update is run THEN exit code 1 with VALIDATION_ERROR | Unit |
| AC-056A-03e | GIVEN a feature_id that does not exist WHEN update is run THEN exit code 2 with `NOT_FOUND` error | Unit |

### Group 4: Feature Update — Status Transitions (2 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056A-04a | GIVEN an update with `status` in the valid enum WHEN update is run THEN status is updated | Unit |
| AC-056A-04b | GIVEN an update with `status` not in the valid enum WHEN update is run THEN exit code 1 with VALIDATION_ERROR | Unit |

### Group 5: Feature Query — List Mode (7 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056A-05a | GIVEN features exist WHEN `feature_query.py` is run with no filters THEN all features are returned sorted by `last_updated` descending | Unit |
| AC-056A-05b | GIVEN features exist WHEN `--epic-id EPIC-XXX` is provided THEN only features in that epic are returned | Unit |
| AC-056A-05c | GIVEN features exist WHEN `--status Completed` is provided THEN only features with matching status are returned | Unit |
| AC-056A-05d | GIVEN features exist WHEN `--search "text"` is provided THEN features matching (case-insensitive) in `feature_id`, `title`, `description`, `epic_id` are returned | Unit |
| AC-056A-05e | GIVEN features exist WHEN `--page 2 --page-size 5` is provided THEN correct pagination slice with metadata (`page`, `page_size`, `total`, `total_pages`) is returned | Unit |
| AC-056A-05f | GIVEN multiple filters are provided WHEN query is run THEN filters are combined with AND logic | Unit |
| AC-056A-05g | GIVEN `features.json` does not exist WHEN query is run THEN empty list returned with `total=0, total_pages=1` | Unit |

### Group 6: Feature Query — Single Mode (3 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056A-06a | GIVEN an existing feature_id WHEN `feature_query.py --feature-id FEATURE-XXX` is run THEN that single feature is returned | Unit |
| AC-056A-06b | GIVEN a non-existent feature_id WHEN single query is run THEN exit code 2 with NOT_FOUND | Unit |
| AC-056A-06c | GIVEN `--feature-id` is combined with list filters WHEN query is run THEN single mode takes precedence (filters ignored) | Unit |

### Group 7: Feature Query — Epic Summary (4 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056A-07a | GIVEN features across multiple epics WHEN `feature_query.py --epic-summary` is run THEN per-epic summary is returned with `{"epic_id": "...", "total": N, "Planned": X, ...}` for each epic | Unit |
| AC-056A-07b | GIVEN `--epic-summary` and `--epic-id EPIC-XXX` WHEN query is run THEN only that epic's summary is returned | Unit |
| AC-056A-07c | GIVEN an epic with all features Completed WHEN epic summary is run THEN all counts reflect correctly | Unit |
| AC-056A-07d | GIVEN no features exist WHEN `--epic-summary` is run THEN empty list returned | Unit |

### Group 8: Shared Patterns (5 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056A-08a | GIVEN any script WHEN run THEN `_board_lib.with_file_lock` is used for all write operations on `features.json` | Unit |
| AC-056A-08b | GIVEN any script WHEN lock cannot be acquired within timeout THEN exit code 3 with `LOCK_TIMEOUT` error | Unit |
| AC-056A-08c | GIVEN any script WHEN `--lock-timeout N` is provided THEN custom timeout is used | Unit |
| AC-056A-08d | GIVEN any script WHEN run THEN output follows `{"success": true/false, ...}` JSON format to stdout/stderr | Unit |
| AC-056A-08e | GIVEN any script WHEN run with `--help` THEN usage information is printed | Unit |

---

## Summary

| Metric | Value |
|--------|-------|
| Total ACs | 35 |
| Groups | 8 |
| Scripts | 3 (feature_create.py, feature_update.py, feature_query.py) |
| Valid Statuses | 7 (Planned, Refined, Designed, Implemented, Tested, Completed, Retired) |
| Immutable Fields | 3 (feature_id, epic_id, created_at) |
| Exit Codes | 4 (0=success, 1=validation, 2=not found, 3=lock timeout) |
