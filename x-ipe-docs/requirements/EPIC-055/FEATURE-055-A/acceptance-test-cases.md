# Acceptance Test Cases

> Feature: FEATURE-055-A - Board Shared Library
> Generated: 04-03-2026
> Status: Executed

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-055-A |
| Feature Title | Board Shared Library |
| Total Test Cases | 32 |
| Priority | P0 (Critical): 8 · P1 (High): 18 · P2 (Medium): 6 |
| Target URL | N/A (Python library — no UI) |
| Test Tool | pytest (x-ipe-tool-implementation-python) |
| Test File | [tests/test_board_lib.py](tests/test_board_lib.py) |

---

## Prerequisites

- [x] Feature is implemented — `_board_lib.py` created
- [x] Test environment ready — `uv run pytest` available
- [x] Implementation tests passing — 47/47 pass, 93% coverage

---

## Unit Tests

### TC-001: Read valid JSON file

**Acceptance Criteria Reference:** AC-055A-01a
**Priority:** P0
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestAtomicReadJson::test_read_valid_json` | ✅ PASS |
| `TestAtomicReadJson::test_read_valid_list` | ✅ PASS |

**Expected Outcome:** `atomic_read_json` returns parsed dict/list from valid JSON files
**Status:** ✅ Pass

---

### TC-002: Read missing file returns error dict

**Acceptance Criteria Reference:** AC-055A-01b
**Priority:** P0
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestAtomicReadJson::test_read_missing_file` | ✅ PASS |

**Expected Outcome:** Returns `{"success": false, "error": "..."}` without raising exception
**Status:** ✅ Pass

---

### TC-003: Read invalid JSON returns error dict

**Acceptance Criteria Reference:** AC-055A-01c
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestAtomicReadJson::test_read_invalid_json` | ✅ PASS |

**Expected Outcome:** Returns error dict with descriptive message, no exception raised
**Status:** ✅ Pass

---

### TC-004: Read empty file returns error dict

**Acceptance Criteria Reference:** AC-055A-01d
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestAtomicReadJson::test_read_empty_file` | ✅ PASS |
| `TestAtomicReadJson::test_read_whitespace_only` | ✅ PASS |

**Expected Outcome:** Error dict returned for empty/whitespace-only files
**Status:** ✅ Pass

---

### TC-005: Read accepts string and Path arguments

**Acceptance Criteria Reference:** AC-055A-01a (path flexibility)
**Priority:** P2
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestAtomicReadJson::test_read_accepts_string_path` | ✅ PASS |

**Expected Outcome:** Both `str` and `Path` arguments work
**Status:** ✅ Pass

---

### TC-006: Atomic write creates file with indent=2

**Acceptance Criteria Reference:** AC-055A-02a, AC-055A-02d
**Priority:** P0
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestAtomicWriteJson::test_write_creates_file` | ✅ PASS |
| `TestAtomicWriteJson::test_write_indent_2` | ✅ PASS |
| `TestAtomicWriteJson::test_write_trailing_newline` | ✅ PASS |

**Expected Outcome:** File created via atomic temp→replace pattern, JSON formatted with indent=2
**Status:** ✅ Pass

---

### TC-007: Atomic write creates parent directories

**Acceptance Criteria Reference:** AC-055A-02b
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestAtomicWriteJson::test_write_creates_parent_dirs` | ✅ PASS |

**Expected Outcome:** Missing parent directories are created automatically
**Status:** ✅ Pass

---

### TC-008: Atomic write cleans up temp on failure

**Acceptance Criteria Reference:** AC-055A-02c
**Priority:** P0
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestAtomicWriteJson::test_write_temp_cleanup_on_error` | ✅ PASS |
| `TestAtomicWriteJson::test_write_overwrites_existing` | ✅ PASS |

**Expected Outcome:** Temp file cleaned up on error; original preserved; overwrite works correctly
**Status:** ✅ Pass

---

### TC-009: Write accepts string and Path arguments

**Acceptance Criteria Reference:** AC-055A-02a (path flexibility)
**Priority:** P2
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestAtomicWriteJson::test_write_accepts_string_path` | ✅ PASS |

**Expected Outcome:** Both `str` and `Path` arguments work for write
**Status:** ✅ Pass

---

### TC-010: File lock acquire and release

**Acceptance Criteria Reference:** AC-055A-03a
**Priority:** P0
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestFileLocking::test_lock_acquire_and_release` | ✅ PASS |

**Expected Outcome:** Exclusive lock acquired, context body executes, lock released on exit
**Status:** ✅ Pass

---

### TC-011: Lock timeout exits with code 3

**Acceptance Criteria Reference:** AC-055A-03b
**Priority:** P0
**Test Type:** integration
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestFileLocking::test_lock_timeout_exits` | ✅ PASS |

**Expected Outcome:** When lock held by another, timeout triggers exit code 3
**Status:** ✅ Pass

---

### TC-012: Lock default timeout is 10 seconds

**Acceptance Criteria Reference:** AC-055A-03c
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestFileLocking::test_lock_default_timeout` | ✅ PASS |

**Expected Outcome:** Default timeout is 10 seconds when not specified
**Status:** ✅ Pass

---

### TC-013: Lock released on exception

**Acceptance Criteria Reference:** AC-055A-03d
**Priority:** P0
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestFileLocking::test_lock_released_on_exception` | ✅ PASS |

**Expected Outcome:** Lock released in finally block, exception propagates
**Status:** ✅ Pass

---

### TC-014: Lock file created automatically

**Acceptance Criteria Reference:** AC-055A-03e
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestFileLocking::test_lock_file_created` | ✅ PASS |
| `TestFileLocking::test_lock_creates_parent_dirs` | ✅ PASS |
| `TestFileLocking::test_lock_cleanup_removes_file` | ✅ PASS |

**Expected Outcome:** Lock file created with O_CREAT, parent dirs created, cleanup removes file
**Status:** ✅ Pass

---

### TC-015: Schema validation passes for valid data

**Acceptance Criteria Reference:** AC-055A-04a
**Priority:** P0
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestSchemaValidation::test_valid_data` | ✅ PASS |
| `TestSchemaValidation::test_valid_data_optional_missing` | ✅ PASS |

**Expected Outcome:** `{"success": true}` returned for conforming data
**Status:** ✅ Pass

---

### TC-016: Schema validation rejects missing required field

**Acceptance Criteria Reference:** AC-055A-04b
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestSchemaValidation::test_missing_required_field` | ✅ PASS |

**Expected Outcome:** Error with "Missing required field: X" message
**Status:** ✅ Pass

---

### TC-017: Schema validation rejects wrong type

**Acceptance Criteria Reference:** AC-055A-04c
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestSchemaValidation::test_wrong_type` | ✅ PASS |

**Expected Outcome:** Error indicating type mismatch
**Status:** ✅ Pass

---

### TC-018: Schema validation rejects unknown fields (strict)

**Acceptance Criteria Reference:** AC-055A-04d
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestSchemaValidation::test_unknown_field_rejected` | ✅ PASS |
| `TestSchemaValidation::test_metadata_keys_ignored` | ✅ PASS |

**Expected Outcome:** Unknown fields rejected; `_`-prefixed metadata keys allowed
**Status:** ✅ Pass

---

### TC-019: Schema validation rejects non-dict input

**Acceptance Criteria Reference:** AC-055A-04e
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestSchemaValidation::test_non_dict_input` | ✅ PASS |

**Expected Outcome:** Error indicating data must be a dict
**Status:** ✅ Pass

---

### TC-020: TASK_SCHEMA_V1 definition

**Acceptance Criteria Reference:** AC-055A-05a
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestSchemaDefinitions::test_task_schema_fields` | ✅ PASS |
| `TestSchemaDefinitions::test_task_schema_types` | ✅ PASS |
| `TestSchemaDefinitions::test_task_schema_validates_sample` | ✅ PASS |

**Expected Outcome:** Schema has all 9 fields with correct types; sample data validates
**Status:** ✅ Pass

---

### TC-021: FEATURE_SCHEMA_V1 definition

**Acceptance Criteria Reference:** AC-055A-05b
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestSchemaDefinitions::test_feature_schema_fields` | ✅ PASS |
| `TestSchemaDefinitions::test_feature_schema_types` | ✅ PASS |

**Expected Outcome:** Schema has all 10 fields with correct types
**Status:** ✅ Pass

---

### TC-022: Schema version keys

**Acceptance Criteria Reference:** AC-055A-05c
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestSchemaDefinitions::test_schema_version_key` | ✅ PASS |

**Expected Outcome:** All schemas contain `_version` key with string value
**Status:** ✅ Pass

---

### TC-023: INDEX_SCHEMA_V1 definition

**Acceptance Criteria Reference:** AC-055A-05d
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestSchemaDefinitions::test_index_schema_fields` | ✅ PASS |

**Expected Outcome:** Schema defines `version` and `entries` fields
**Status:** ✅ Pass

---

### TC-024: resolve_data_path("tasks")

**Acceptance Criteria Reference:** AC-055A-06a
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestPathResolution::test_tasks_path` | ✅ PASS |

**Expected Outcome:** Returns absolute path to `x-ipe-docs/planning/tasks/`
**Status:** ✅ Pass

---

### TC-025: resolve_data_path("features")

**Acceptance Criteria Reference:** AC-055A-06b
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestPathResolution::test_features_path` | ✅ PASS |

**Expected Outcome:** Returns absolute path to `x-ipe-docs/planning/features/`
**Status:** ✅ Pass

---

### TC-026: resolve_data_path rejects unknown type

**Acceptance Criteria Reference:** AC-055A-06c
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestPathResolution::test_unknown_type_raises` | ✅ PASS |

**Expected Outcome:** ValueError raised for unknown data_type
**Status:** ✅ Pass

---

### TC-027: Path resolution returns absolute path with project root

**Acceptance Criteria Reference:** AC-055A-06d
**Priority:** P2
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestPathResolution::test_returns_absolute_path` | ✅ PASS |
| `TestPathResolution::test_project_root_contains_marker` | ✅ PASS |

**Expected Outcome:** Returns absolute path; project root contains `x-ipe-docs/` marker
**Status:** ✅ Pass

---

### TC-028: output_result prints JSON to stdout

**Acceptance Criteria Reference:** AC-055A-07a, AC-055A-07d
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestStructuredOutput::test_output_result_stdout` | ✅ PASS |
| `TestStructuredOutput::test_output_result_valid_json` | ✅ PASS |

**Expected Outcome:** Valid JSON printed to stdout
**Status:** ✅ Pass

---

### TC-029: exit_with_error prints JSON to stderr and exits

**Acceptance Criteria Reference:** AC-055A-07b, AC-055A-07d
**Priority:** P1
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestStructuredOutput::test_exit_with_error_stderr` | ✅ PASS |
| `TestStructuredOutput::test_exit_with_error_json_output` | ✅ PASS |

**Expected Outcome:** Valid JSON to stderr + correct exit code
**Status:** ✅ Pass

---

### TC-030: Exit code constants

**Acceptance Criteria Reference:** AC-055A-07c
**Priority:** P2
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestStructuredOutput::test_exit_code_constants` | ✅ PASS |

**Expected Outcome:** EXIT_SUCCESS=0, EXIT_VALIDATION_ERROR=1, EXIT_FILE_NOT_FOUND=2, EXIT_LOCK_TIMEOUT=3
**Status:** ✅ Pass

---

### TC-031: Stdlib-only imports

**Acceptance Criteria Reference:** AC-055A-08a
**Priority:** P0
**Test Type:** unit
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestStdlibConstraint::test_only_stdlib_imports` | ✅ PASS |

**Expected Outcome:** AST analysis confirms all imports are from Python stdlib
**Status:** ✅ Pass

---

### TC-032: Module loads without third-party dependencies

**Acceptance Criteria Reference:** AC-055A-08b
**Priority:** P2
**Test Type:** integration
**Assigned Tool:** pytest

| pytest Test | Result |
|-------------|--------|
| `TestStdlibConstraint::test_module_loads_without_third_party` | ✅ PASS |

**Expected Outcome:** Module imports successfully in clean environment
**Status:** ✅ Pass

---

## Test Execution Summary

| Test Case | Title | AC Reference | Priority | Status |
|-----------|-------|-------------|----------|--------|
| TC-001 | Read valid JSON file | AC-055A-01a | P0 | ✅ Pass |
| TC-002 | Read missing file returns error dict | AC-055A-01b | P0 | ✅ Pass |
| TC-003 | Read invalid JSON returns error dict | AC-055A-01c | P1 | ✅ Pass |
| TC-004 | Read empty file returns error dict | AC-055A-01d | P1 | ✅ Pass |
| TC-005 | Read accepts string and Path arguments | AC-055A-01a | P2 | ✅ Pass |
| TC-006 | Atomic write creates file with indent=2 | AC-055A-02a/d | P0 | ✅ Pass |
| TC-007 | Atomic write creates parent directories | AC-055A-02b | P1 | ✅ Pass |
| TC-008 | Atomic write cleans up temp on failure | AC-055A-02c | P0 | ✅ Pass |
| TC-009 | Write accepts string and Path arguments | AC-055A-02a | P2 | ✅ Pass |
| TC-010 | File lock acquire and release | AC-055A-03a | P0 | ✅ Pass |
| TC-011 | Lock timeout exits with code 3 | AC-055A-03b | P0 | ✅ Pass |
| TC-012 | Lock default timeout is 10 seconds | AC-055A-03c | P1 | ✅ Pass |
| TC-013 | Lock released on exception | AC-055A-03d | P0 | ✅ Pass |
| TC-014 | Lock file created automatically | AC-055A-03e | P1 | ✅ Pass |
| TC-015 | Schema validation passes for valid data | AC-055A-04a | P0 | ✅ Pass |
| TC-016 | Schema rejects missing required field | AC-055A-04b | P1 | ✅ Pass |
| TC-017 | Schema rejects wrong type | AC-055A-04c | P1 | ✅ Pass |
| TC-018 | Schema rejects unknown fields (strict) | AC-055A-04d | P1 | ✅ Pass |
| TC-019 | Schema rejects non-dict input | AC-055A-04e | P1 | ✅ Pass |
| TC-020 | TASK_SCHEMA_V1 definition | AC-055A-05a | P1 | ✅ Pass |
| TC-021 | FEATURE_SCHEMA_V1 definition | AC-055A-05b | P1 | ✅ Pass |
| TC-022 | Schema version keys | AC-055A-05c | P1 | ✅ Pass |
| TC-023 | INDEX_SCHEMA_V1 definition | AC-055A-05d | P1 | ✅ Pass |
| TC-024 | resolve_data_path("tasks") | AC-055A-06a | P1 | ✅ Pass |
| TC-025 | resolve_data_path("features") | AC-055A-06b | P1 | ✅ Pass |
| TC-026 | resolve_data_path rejects unknown type | AC-055A-06c | P1 | ✅ Pass |
| TC-027 | Path resolution returns absolute path | AC-055A-06d | P2 | ✅ Pass |
| TC-028 | output_result prints JSON to stdout | AC-055A-07a/d | P1 | ✅ Pass |
| TC-029 | exit_with_error prints JSON to stderr | AC-055A-07b/d | P1 | ✅ Pass |
| TC-030 | Exit code constants | AC-055A-07c | P2 | ✅ Pass |
| TC-031 | Stdlib-only imports | AC-055A-08a | P0 | ✅ Pass |
| TC-032 | Module loads without third-party deps | AC-055A-08b | P2 | ✅ Pass |

---

## Execution Results

**Execution Date:** 04-03-2026
**Executed By:** Drift 🌊
**Environment:** Local development (macOS, Python 3.12.9)

| Metric | Value |
|--------|-------|
| Total Tests | 32 |
| Passed | 32 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

### Results by Type

| Test Type | Passed | Failed | Blocked | Total |
|-----------|--------|--------|---------|-------|
| unit | 30 | 0 | 0 | 30 |
| integration | 2 | 0 | 0 | 2 |

### pytest Execution Detail

- **Command:** `uv run pytest tests/test_board_lib.py -v`
- **Result:** 47 passed in 1.10s (47 pytest tests map to 32 acceptance TCs — some ACs verified by multiple sub-tests)
- **Coverage:** 93% of `_board_lib.py` (113 statements, 8 missed — edge-case error paths)

### Failed Tests

None — all 32 test cases passed.

---

## Notes

- This feature is a Python library with no UI or API components — all testing is via pytest
- 47 pytest test methods map to 32 acceptance test cases (some ACs require multiple assertions)
- Coverage of 93% exceeds the 80% target; uncovered lines are defensive error paths (project root not found, OS errors)
- All 8 AC groups (AC-055A-01 through AC-055A-08) are fully covered
