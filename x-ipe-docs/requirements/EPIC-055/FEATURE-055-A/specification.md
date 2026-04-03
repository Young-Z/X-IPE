# Feature Specification: Board Shared Library

> Feature ID: FEATURE-055-A
> Version: v1.0
> Status: Refined
> Last Updated: 04-03-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-03-2026 | Initial specification |

## Linked Mockups

N/A — This feature is a backend Python library with no UI component.

## Overview

FEATURE-055-A provides a shared Python library (`_board_lib.py`) that serves as the foundation for all board manager operations in the X-IPE project. It encapsulates atomic JSON I/O, POSIX file locking, strict schema validation, path resolution, and structured output formatting into reusable utility functions.

The library is needed because both the Task Board Manager (EPIC-055) and Feature Board Manager (EPIC-056) require the same low-level file operations with identical safety guarantees — atomic writes that survive crashes, exclusive file locks that prevent concurrent corruption, and strict schema enforcement that catches invalid data early. Extracting these into a shared library avoids duplication and ensures consistent behavior.

The primary consumers are AI agent skill scripts (task CRUD, feature CRUD) that import `_board_lib.py` to perform safe, validated JSON file operations. The library lives in `.github/skills/x-ipe-tool-task-board-manager/scripts/_board_lib.py` and is imported by both task and feature board scripts.

## User Stories

- As a **skill script developer**, I want to read and write JSON files atomically, so that concurrent agent operations never corrupt board data.
- As a **skill script developer**, I want to validate data against a strict schema before writing, so that malformed data is rejected early with clear error messages.
- As a **skill script developer**, I want a file locking mechanism with configurable timeout, so that concurrent writes to the same file are serialized safely.
- As a **skill script developer**, I want versioned schema definitions for tasks and features, so that future schema changes can be managed without breaking existing data.
- As a **skill script developer**, I want consistent structured output formatting and exit codes, so that calling scripts can reliably parse results and handle errors.

## Acceptance Criteria

### AC-055A-01: Atomic JSON Read

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055A-01a | GIVEN a valid JSON file exists at a path WHEN `atomic_read_json(path)` is called THEN the file contents are returned as a parsed Python dict/list | Unit |
| AC-055A-01b | GIVEN the file at path does not exist WHEN `atomic_read_json(path)` is called THEN an error dict `{"success": false, "error": "..."}` is returned AND no exception is raised | Unit |
| AC-055A-01c | GIVEN the file contains invalid JSON WHEN `atomic_read_json(path)` is called THEN an error dict is returned with a descriptive message AND no exception is raised | Unit |
| AC-055A-01d | GIVEN an empty file exists at path WHEN `atomic_read_json(path)` is called THEN an error dict is returned indicating empty/invalid content | Unit |

### AC-055A-02: Atomic JSON Write

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055A-02a | GIVEN valid data and a target path WHEN `atomic_write_json(path, data)` is called THEN a temporary file is created in the same directory AND data is written with `indent=2` AND `fsync` is called AND `os.replace` atomically moves temp to target | Unit |
| AC-055A-02b | GIVEN the target directory does not exist WHEN `atomic_write_json(path, data)` is called THEN the parent directories are created AND the write succeeds | Unit |
| AC-055A-02c | GIVEN a write operation fails mid-way (simulated) WHEN the temporary file exists but `os.replace` has not been called THEN the original file remains unchanged AND the temp file is cleaned up | Unit |
| AC-055A-02d | GIVEN valid data WHEN `atomic_write_json(path, data)` is called THEN the output JSON uses `indent=2` formatting for git-friendly diffs | Unit |

### AC-055A-03: File Locking

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055A-03a | GIVEN no other process holds a lock on a file WHEN `with_file_lock(path)` is entered THEN an exclusive lock (`fcntl.LOCK_EX`) is acquired AND the context body executes AND the lock is released on exit | Unit |
| AC-055A-03b | GIVEN another process holds an exclusive lock WHEN `with_file_lock(path, timeout=2)` is called AND the lock is not released within 2 seconds THEN `exit_with_error` is called which prints a JSON error to stderr and calls `sys.exit(3)` | Integration |
| AC-055A-03c | GIVEN the default timeout is not overridden WHEN `with_file_lock(path)` is called THEN the timeout defaults to 10 seconds | Unit |
| AC-055A-03d | GIVEN a lock is held WHEN the context block raises an exception THEN the lock is released in the finally block AND the exception propagates | Unit |
| AC-055A-03e | GIVEN the lock file does not exist WHEN `with_file_lock(path)` is called THEN the lock file is created with `O_CREAT` flag AND the lock is acquired | Unit |

### AC-055A-04: Schema Validation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055A-04a | GIVEN data that conforms to a schema WHEN `validate_schema(data, schema)` is called THEN `{"success": true}` is returned | Unit |
| AC-055A-04b | GIVEN data missing a required field WHEN `validate_schema(data, schema)` is called THEN `{"success": false, "error": "Missing required field: X"}` is returned | Unit |
| AC-055A-04c | GIVEN data with a field value of wrong type WHEN `validate_schema(data, schema)` is called THEN `{"success": false, "error": "..."}` is returned indicating the type mismatch | Unit |
| AC-055A-04d | GIVEN data with an extra field not in the schema WHEN `validate_schema(data, schema)` is called THEN `{"success": false, "error": "Unknown field: X"}` is returned (strict mode) | Unit |
| AC-055A-04e | GIVEN data is not a dict WHEN `validate_schema(data, schema)` is called THEN `{"success": false, "error": "..."}` is returned indicating data must be a dict | Unit |

### AC-055A-05: Schema Definitions

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055A-05a | GIVEN the module is imported WHEN `TASK_SCHEMA_V1` is accessed THEN it returns a dict defining fields: `task_id`, `task_type`, `description`, `role`, `status`, `created_at`, `last_updated`, `output_links`, `next_task` with their expected types | Unit |
| AC-055A-05b | GIVEN the module is imported WHEN `FEATURE_SCHEMA_V1` is accessed THEN it returns a dict defining fields: `feature_id`, `epic_id`, `title`, `version`, `status`, `description`, `dependencies`, `specification_link`, `created_at`, `last_updated` with their expected types | Unit |
| AC-055A-05c | GIVEN any schema constant WHEN inspected THEN it contains a `_version` key with a string value (e.g., `"1.0"`) for migration support | Unit |
| AC-055A-05d | GIVEN the module is imported WHEN `INDEX_SCHEMA_V1` is accessed THEN it returns a dict defining the index file structure: `version`, `entries` (dict of `task_id → {file, status, last_updated}`) | Unit |

### AC-055A-06: Path Resolution

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055A-06a | GIVEN data_type is `"tasks"` WHEN `resolve_data_path("tasks")` is called THEN it returns the absolute path to `x-ipe-docs/planning/tasks/` relative to project root | Unit |
| AC-055A-06b | GIVEN data_type is `"features"` WHEN `resolve_data_path("features")` is called THEN it returns the absolute path to `x-ipe-docs/planning/features/` relative to project root | Unit |
| AC-055A-06c | GIVEN an unknown data_type WHEN `resolve_data_path("unknown")` is called THEN a `ValueError` is raised with a descriptive message | Unit |
| AC-055A-06d | GIVEN the project root is detected WHEN `resolve_data_path` computes paths THEN it walks up from CWD to find a directory containing `x-ipe-docs/` as the project root marker | Unit |

### AC-055A-07: Structured Output & Exit Codes

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055A-07a | GIVEN a successful result dict WHEN `output_result({"success": True, "data": {...}})` is called THEN the dict is printed to stdout as JSON | Unit |
| AC-055A-07b | GIVEN an error WHEN `exit_with_error(code, error, message)` is called THEN `{"success": false, "error": "<error>", "message": "<message>"}` is printed to stderr AND the process exits with the given code | Unit |
| AC-055A-07c | GIVEN the module is imported WHEN exit code constants are accessed THEN `EXIT_SUCCESS == 0`, `EXIT_VALIDATION_ERROR == 1`, `EXIT_FILE_NOT_FOUND == 2`, `EXIT_LOCK_TIMEOUT == 3` | Unit |
| AC-055A-07d | GIVEN any output helper is called WHEN the output is captured THEN it is valid JSON parseable by `json.loads()` | Unit |

### AC-055A-08: Stdlib-Only Constraint

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-055A-08a | GIVEN the `_board_lib.py` source file WHEN all import statements are analyzed THEN every import is from the Python standard library (no third-party packages) | Unit |
| AC-055A-08b | GIVEN the module WHEN loaded in a clean Python environment with no pip packages installed THEN the module imports successfully without `ImportError` | Integration |

## Functional Requirements

### FR-1: Atomic JSON Read

**Description:** Read and parse a JSON file safely, returning structured errors instead of raising exceptions.

**Details:**
- Input: File path (str or Path)
- Process: Read file contents, parse as JSON, return parsed data
- Output: Parsed dict/list on success, `{"success": false, "error": "..."}` on failure

### FR-2: Atomic JSON Write

**Description:** Write JSON data to a file atomically using the tempfile → fsync → os.replace pattern.

**Details:**
- Input: File path (str or Path), data (dict or list)
- Process: Create temp file in same dir → write with indent=2 → flush → fsync → os.replace → cleanup temp on error
- Output: Returns `None` on success; raises `OSError` on unrecoverable I/O failure

### FR-3: File Locking

**Description:** Provide a context manager for exclusive POSIX file locking with configurable timeout.

**Details:**
- Input: Lock file path, timeout in seconds (default 10)
- Process: Open/create lock file → attempt `fcntl.LOCK_EX | fcntl.LOCK_NB` → retry every 0.1s until timeout → unlock in finally
- Output: Lock acquired (context entered) or `SystemExit(3)` via `exit_with_error` on timeout

### FR-4: Schema Validation

**Description:** Validate a Python dict against a schema definition, strictly rejecting unknown fields, missing required fields, and type mismatches.

**Details:**
- Input: Data dict, schema dict
- Process: Check required fields present → check types → check no extra fields
- Output: `{"success": true}` or `{"success": false, "error": "..."}` with specific field name

### FR-5: Schema Definitions

**Description:** Provide versioned schema constants for task, feature, and index data structures.

**Details:**
- Input: N/A (module-level constants)
- Process: Define `TASK_SCHEMA_V1`, `FEATURE_SCHEMA_V1`, `INDEX_SCHEMA_V1` with field names, types, and `_version` key
- Output: Schema dicts accessible as module attributes

### FR-6: Path Resolution

**Description:** Resolve absolute paths to task and feature data directories from any working directory.

**Details:**
- Input: Data type string (`"tasks"` or `"features"`)
- Process: Detect project root → append data-type-specific relative path
- Output: Absolute `pathlib.Path` to the data directory

### FR-7: Structured Output

**Description:** Provide output helpers that print JSON to stdout/stderr with standardized exit codes.

**Details:**
- Input: Success flag, data dict or error message, exit code
- Process: Format as JSON, print to appropriate stream, exit with code
- Output: JSON string on stdout (success) or stderr (error)

## Non-Functional Requirements

### NFR-1: Performance

- File locking retry interval: 0.1 seconds (100ms polling)
- Atomic write overhead: one additional file descriptor and one `fsync` call per write
- Schema validation: O(n) where n = number of fields in schema

### NFR-2: Reliability

- Atomic writes must survive process crashes (no partial writes visible to readers)
- Lock timeout must prevent indefinite hangs
- Error handling must never raise unhandled exceptions to callers

### NFR-3: Portability

- `fcntl.flock` is POSIX-only (Linux, macOS) — acceptable for this project
- All imports from Python stdlib only

## UI/UX Requirements

N/A — This feature is a backend library with no user interface.

## Dependencies

### Internal Dependencies

- None (foundation feature — no dependencies on other features)

### External Dependencies

- **Python 3.10+:** Uses `pathlib.Path`, `fcntl`, `tempfile`, `json`, `os` from stdlib
- **POSIX OS:** `fcntl.flock` requires POSIX-compatible operating system (Linux, macOS)

## Business Rules

- **BR-1:** All JSON writes MUST be atomic — partial writes must never be visible to concurrent readers
- **BR-2:** Schema validation MUST be strict — unknown fields are rejected, not silently ignored
- **BR-3:** All schemas MUST include a `_version` key for future migration support
- **BR-4:** File locks MUST be released in all code paths (success, error, exception)
- **BR-5:** Structured output MUST be valid JSON parseable by any JSON parser

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| File locked by dead process (stale lock) | `fcntl.flock` automatically clears stale locks when the holding process exits — lock is acquired normally |
| Disk full during atomic write | Temp file write fails → original file preserved → error returned with descriptive message |
| JSON file with BOM (byte order mark) | `atomic_read_json` reads as UTF-8 — Python handles BOM transparently |
| Concurrent `atomic_write_json` to same file without lock | Caller responsibility to use `with_file_lock` — library does not auto-lock on write |
| Schema with nested objects | Schema validation checks top-level fields only for v1.0 — nested object validation is out of scope |
| Empty string as path | `atomic_read_json("")` returns `FILE_NOT_FOUND` error dict; `atomic_write_json` attempts to write relative to CWD (caller should validate) |
| Path with non-existent parent directories | `atomic_write_json` creates parent dirs; `atomic_read_json` returns error |

## Out of Scope

- CRUD operations for tasks or features (→ FEATURE-055-B, FEATURE-056-A)
- Index file management (→ FEATURE-055-B)
- API endpoints (→ FEATURE-055-C, FEATURE-056-B)
- Web UI (→ FEATURE-057-A, FEATURE-057-B)
- Nested object schema validation (v1.0 validates top-level fields only)
- Windows file locking (`msvcrt.locking`) — project is POSIX-only
- Schema migration utilities (schemas are versioned for future use, but migration logic is out of scope)
- Async/await support — all operations are synchronous

## Technical Considerations

- Follow the established pattern from `.github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/_lib.py` for project root detection and output formatting
- The library resides at `.github/skills/x-ipe-tool-task-board-manager/scripts/_board_lib.py`
- Feature board scripts (EPIC-056) import from this path — Python path manipulation may be needed
- Exit codes (0/1/2/3) must align with the project-wide convention established in the existing `_lib.py`
- Schema dicts should define field name → expected type mapping (e.g., `{"task_id": str, "output_links": list}`)
- `with_file_lock` should use `.lock` suffix files adjacent to the data file (e.g., `tasks-2026-04-03.json.lock`)

## Open Questions

None — all questions resolved during requirement gathering and refinement phases.
