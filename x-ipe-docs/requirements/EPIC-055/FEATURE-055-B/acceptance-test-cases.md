# Acceptance Test Cases: FEATURE-055-B — Task CRUD Scripts

> Feature: FEATURE-055-B (Task CRUD Scripts)
> Test Date: 04-03-2026
> Tester: Drift 🌊 (automated)
> Test Type: Unit (CLI scripts)
> Tool: pytest (x-ipe-tool-implementation-python)

## Related Documents

- [Specification](x-ipe-docs/requirements/EPIC-055/FEATURE-055-B/specification.md)
- [Technical Design](x-ipe-docs/requirements/EPIC-055/FEATURE-055-B/technical-design.md)
- [Test File](tests/test_task_crud.py)

---

## Execution Summary

| Metric | Value |
|--------|-------|
| Total Test Cases | 42 |
| Passed | 42 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | **100%** |
| Coverage | 88% |
| Test Methods | 50 |

### Results by Type

| Test Type | Passed | Failed | Blocked | Total |
|-----------|--------|--------|---------|-------|
| Unit | 42 | 0 | 0 | 42 |

---

## Unit Tests

### Group 1: Create Task (8 ACs)

| TC | AC | Priority | Test Method | Status | Notes |
|----|-----|----------|-------------|--------|-------|
| TC-01 | AC-055B-01a | P0 | `TestTaskCreate::test_happy_path` | ✅ Pass | --task JSON parsed, task created in daily file |
| TC-02 | AC-055B-01b | P0 | `test_happy_path`, `test_rejects_invalid_json`, `test_rejects_missing_required`, `test_rejects_non_dict` | ✅ Pass | TASK_SCHEMA_V1 validation enforced |
| TC-03 | AC-055B-01c | P0 | `test_rejects_unknown_fields` | ✅ Pass | Strict schema rejects unknown fields |
| TC-04 | AC-055B-01d | P0 | `test_rejects_duplicate_id` | ✅ Pass | Duplicate task_id rejected with exit code 1 |
| TC-05 | AC-055B-01e | P0 | `test_happy_path`, `test_strips_caller_timestamps` | ✅ Pass | created_at/last_updated auto-set, caller values stripped |
| TC-06 | AC-055B-01f | P0 | `test_happy_path`, `test_appends_same_day` | ✅ Pass | Task appended to tasks-YYYY-MM-DD.json |
| TC-07 | AC-055B-01g | P0 | `test_happy_path` | ✅ Pass | Index entry created with file/status/last_updated |
| TC-08 | AC-055B-01h | P0 | `test_happy_path` | ✅ Pass | JSON success output on stdout |

### Group 2: Update Task (6 ACs)

| TC | AC | Priority | Test Method | Status | Notes |
|----|-----|----------|-------------|--------|-------|
| TC-09 | AC-055B-02a | P0 | `TestTaskUpdate::test_partial_merge` | ✅ Pass | --task-id + --updates JSON parsed |
| TC-10 | AC-055B-02b | P0 | `test_partial_merge` | ✅ Pass | Only provided fields merged, others unchanged |
| TC-11 | AC-055B-02c | P0 | `test_partial_merge` | ✅ Pass | last_updated auto-set to current UTC time |
| TC-12 | AC-055B-02d | P0 | `test_rejects_immutable_task_id`, `test_rejects_immutable_created_at` | ✅ Pass | task_id and created_at changes rejected |
| TC-13 | AC-055B-02e | P1 | `test_updates_index` | ✅ Pass | Index entry status+last_updated updated |
| TC-14 | AC-055B-02f | P0 | `test_partial_merge` | ✅ Pass | JSON success output with updated_fields list |

### Group 3: Query List (8 ACs)

| TC | AC | Priority | Test Method | Status | Notes |
|----|-----|----------|-------------|--------|-------|
| TC-15 | AC-055B-03a | P0 | `TestTaskQueryList::test_default_range`, `test_range_filters_old`, `test_range_all` | ✅ Pass | --range 1w/1m/all works; default 1w |
| TC-16 | AC-055B-03b | P1 | `test_status_filter` | ✅ Pass | --status filters correctly |
| TC-17 | AC-055B-03c | P1 | `test_search_filter`, `test_search_case_insensitive` | ✅ Pass | --search text filter, case-insensitive |
| TC-18 | AC-055B-03d | P1 | `test_pagination` | ✅ Pass | --page default 1 |
| TC-19 | AC-055B-03e | P1 | `test_pagination` | ✅ Pass | --page-size default 50 |
| TC-20 | AC-055B-03f | P0 | `test_sort_order` | ✅ Pass | Sorted by last_updated descending |
| TC-21 | AC-055B-03g | P0 | `test_skips_archived` | ✅ Pass | *.archived.json files excluded |
| TC-22 | AC-055B-03h | P0 | `test_pagination` | ✅ Pass | Returns tasks + pagination metadata |

### Group 4: Query by ID (3 ACs)

| TC | AC | Priority | Test Method | Status | Notes |
|----|-----|----------|-------------|--------|-------|
| TC-23 | AC-055B-04a | P0 | `TestTaskQueryById::test_found` | ✅ Pass | --task-id lookup via index |
| TC-24 | AC-055B-04b | P0 | `test_found` | ✅ Pass | Single task returned with all fields |
| TC-25 | AC-055B-04c | P0 | `test_not_found`, `test_no_tasks_dir` | ✅ Pass | Exit code 2 when not found |

### Group 5: Archive (4 ACs)

| TC | AC | Priority | Test Method | Status | Notes |
|----|-----|----------|-------------|--------|-------|
| TC-26 | AC-055B-05a | P0 | `TestTaskArchive::test_happy_path` | ✅ Pass | --date YYYY-MM-DD accepted |
| TC-27 | AC-055B-05b | P0 | `test_happy_path` | ✅ Pass | File renamed to *.archived.json |
| TC-28 | AC-055B-05c | P0 | `test_happy_path` | ✅ Pass | Entries removed from index |
| TC-29 | AC-055B-05d | P0 | `test_happy_path` | ✅ Pass | Output reports archived_file + tasks_removed count |

### Group 6: Index Management (4 ACs)

| TC | AC | Priority | Test Method | Status | Notes |
|----|-----|----------|-------------|--------|-------|
| TC-30 | AC-055B-06a | P0 | `TestIndexManagement::test_auto_create_on_first_task`, `TestTaskCreate::test_bootstraps_directory` | ✅ Pass | tasks/ dir + index auto-created |
| TC-31 | AC-055B-06b | P1 | `test_updates_index` | ✅ Pass | Index updated on every write operation |
| TC-32 | AC-055B-06c | P0 | `test_entry_structure` | ✅ Pass | Entry has exactly {file, status, last_updated} |
| TC-33 | AC-055B-06d | P0 | `test_archive_removes_entries` | ✅ Pass | Archive removes entries from index |

### Group 7: CLI Interface (5 ACs)

| TC | AC | Priority | Test Method | Status | Notes |
|----|-----|----------|-------------|--------|-------|
| TC-34 | AC-055B-07a | P0 | `TestCLI::test_main_callable_with_argv` | ✅ Pass | argparse with def main(argv) |
| TC-35 | AC-055B-07b | P0 | `test_json_stdout_success` | ✅ Pass | Valid JSON on stdout for success |
| TC-36 | AC-055B-07c | P0 | `test_json_stderr_error` | ✅ Pass | Valid JSON on stderr for errors |
| TC-37 | AC-055B-07d | P0 | `test_exit_code_0`, `test_exit_code_1_validation`, `test_exit_code_2_not_found` | ✅ Pass | Exit codes 0/1/2 verified |
| TC-38 | AC-055B-07e | P1 | `test_lock_timeout_arg` | ✅ Pass | --lock-timeout optional (default 10) |

### Group 8: Atomicity & Locking (4 ACs)

| TC | AC | Priority | Test Method | Status | Notes |
|----|-----|----------|-------------|--------|-------|
| TC-39 | AC-055B-08a | P0 | `TestAtomicity::test_create_uses_both_locks`, `test_update_uses_both_locks`, `test_archive_uses_both_locks` | ✅ Pass | File locking on all write operations |
| TC-40 | AC-055B-08b | P0 | `test_create_uses_both_locks`, `test_update_uses_both_locks`, `test_archive_uses_both_locks` | ✅ Pass | Daily file lock acquired before index lock |
| TC-41 | AC-055B-08c | P0 | `test_query_no_locks` | ✅ Pass | Query is read-only, no locks |
| TC-42 | AC-055B-08d | P1 | Covered by `_board_lib.with_file_lock` (tested in `test_board_lib.py`) | ✅ Pass | Lock timeout exits code 3 via _board_lib |

---

## Additional Edge Case Tests

| Test Method | Category | Status | Notes |
|-------------|----------|--------|-------|
| `test_rejects_non_dict` | Create validation | ✅ Pass | Non-object JSON rejected |
| `test_rejects_wrong_type` | Update validation | ✅ Pass | Type mismatch rejected |
| `test_strips_last_updated` | Update semantics | ✅ Pass | last_updated silently stripped |
| `test_empty_after_strip` | Update semantics | ✅ Pass | Only last_updated → empty → error |
| `test_empty_dir` | Query edge case | ✅ Pass | Empty dir returns empty list |
| `test_no_tasks_dir_returns_empty` | Query edge case | ✅ Pass | No dir → empty paginated result |
| `test_invalid_date_format` | Archive validation | ✅ Pass | Bad date format exits code 1 |
| `test_already_archived` | Archive validation | ✅ Pass | Already-archived exits code 1 |
