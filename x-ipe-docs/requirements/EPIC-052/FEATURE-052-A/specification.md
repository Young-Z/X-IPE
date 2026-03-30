# Feature Specification: Shared Utility & Workflow Scripts

> Feature ID: FEATURE-052-A
> Version: v1.0
> Status: Refined
> Last Updated: 03-30-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-30-2026 | Initial specification |

## Linked Mockups

N/A — backend/skill infrastructure feature, no UI.

## Overview

FEATURE-052-A delivers the foundational shared utility module (`_lib.py`) and the two highest-usage workflow scripts (`workflow_update_action.py` and `workflow_get_state.py`) for the new `x-ipe-tool-x-ipe-app-interactor` skill. This is the MVP of EPIC-052, covering 14 of 15 consuming skills that currently depend on the `x-ipe-app-and-agent-interaction` MCP server.

The shared utility module provides crash-safe atomic JSON I/O, exclusive file locking, project root discovery, and structured output formatting — all using only Python standard library modules. The workflow scripts replicate the full business logic of the existing MCP tools, including status validation, deliverable format transformation, schema versioning, stage gating re-evaluation, and feature breakdown population.

The primary consumers are AI agents executing X-IPE skills. Each script is invoked via `python3 <script>.py` with argparse-style flags and produces structured JSON output on stdout.

## User Stories

1. As an **AI agent executing a task-based skill**, I want to update a workflow action status via a standalone script, so that I do not need a running MCP server to track workflow progress.

2. As an **AI agent executing a task-based skill**, I want to read the full workflow state via a standalone script, so that I can check current stage, completed actions, and next suggested actions without a server dependency.

3. As a **skill developer creating new tool scripts**, I want a shared utility module with atomic I/O and file locking primitives, so that I can build reliable scripts without reimplementing crash-safe patterns.

4. As an **AI agent**, I want scripts to produce structured JSON output with consistent exit codes, so that I can reliably parse results and detect errors programmatically.

## Acceptance Criteria

### AC-052-A-01: Shared Utility — Atomic JSON I/O

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-01a | GIVEN a valid dict and a target file path WHEN `atomic_write_json(path, data)` is called THEN the file contains the JSON representation of the dict with `indent=2` and `ensure_ascii=False` | Unit |
| AC-052-A-01b | GIVEN `atomic_write_json` is called WHEN the write completes THEN the implementation uses `tempfile.mkstemp()` in the target directory, writes to the temp file, calls `os.fsync()`, and finishes with `os.replace()` to atomically swap | Unit |
| AC-052-A-01c | GIVEN `atomic_write_json` is called WHEN an exception occurs during write THEN the temp file is cleaned up (deleted) AND the original target file is unchanged | Unit |
| AC-052-A-01d | GIVEN a valid JSON file at path WHEN `atomic_read_json(path)` is called THEN the parsed dict is returned | Unit |
| AC-052-A-01e | GIVEN a file path that does not exist WHEN `atomic_read_json(path)` is called THEN a dict `{"success": false, "error": "FILE_NOT_FOUND", "message": "..."}` is returned | Unit |
| AC-052-A-01f | GIVEN a file with invalid JSON content WHEN `atomic_read_json(path)` is called THEN a dict `{"success": false, "error": "JSON_PARSE_ERROR", "message": "..."}` is returned | Unit |

### AC-052-A-02: Shared Utility — File Locking

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-02a | GIVEN a workflow JSON file WHEN `with_file_lock(lock_path, timeout=10)` is called AND no other process holds the lock THEN the lock is acquired via `fcntl.flock(LOCK_EX)` on a `.lock` file AND the caller's code block executes | Unit |
| AC-052-A-02b | GIVEN a lock is held by another process WHEN `with_file_lock(lock_path, timeout=10)` is called AND the timeout expires THEN the script exits with code 3 AND an error message is printed to stdout in JSON format | Integration |
| AC-052-A-02c | GIVEN a lock is acquired WHEN the caller's code block completes (success or exception) THEN the lock is released via `fcntl.flock(LOCK_UN)` AND the file descriptor is closed | Unit |
| AC-052-A-02d | GIVEN the `--lock-timeout` flag is provided WHEN the script runs THEN the custom timeout value (in seconds) is used instead of the default 10s | Unit |

### AC-052-A-03: Shared Utility — Project Root Discovery

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-03a | GIVEN the CWD is inside a project that has an `x-ipe-docs/` directory WHEN `resolve_project_root()` is called THEN it returns the path of the directory containing `x-ipe-docs/` | Unit |
| AC-052-A-03b | GIVEN the CWD is deeply nested (e.g., `project/src/x_ipe/services/`) WHEN `resolve_project_root()` is called THEN it walks up parent directories until it finds the marker directory | Unit |
| AC-052-A-03c | GIVEN no parent directory contains `x-ipe-docs/` WHEN `resolve_project_root()` is called THEN the script exits with code 2 AND an error `{"success": false, "error": "PROJECT_ROOT_NOT_FOUND"}` is output | Unit |
| AC-052-A-03d | GIVEN `resolve_project_root()` succeeds WHEN `resolve_workflow_dir()` is called THEN it returns `{project_root}/x-ipe-docs/engineering-workflow/` | Unit |

### AC-052-A-04: Shared Utility — Output Formatting

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-04a | GIVEN a result dict WHEN `output_result(result, fmt="json")` is called THEN the dict is printed to stdout as compact JSON (no extra whitespace) with a trailing newline | Unit |
| AC-052-A-04b | GIVEN a result dict with `success: true` and `data` key WHEN `output_result(result, fmt="text")` is called THEN a human-readable summary is printed to stdout | Unit |
| AC-052-A-04c | GIVEN a result dict with `success: false` WHEN `output_result(result, fmt="text")` is called THEN the error code and message are printed to stdout | Unit |

### AC-052-A-05: Shared Utility — Exit Codes

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-05a | GIVEN a script completes successfully WHEN it exits THEN the exit code is 0 | Unit |
| AC-052-A-05b | GIVEN a validation error occurs (invalid status, unexpected deliverable tags) WHEN the script exits THEN the exit code is 1 AND structured error JSON is output | Unit |
| AC-052-A-05c | GIVEN a required file is not found (workflow state file, template file) WHEN the script exits THEN the exit code is 2 AND error JSON includes `"error": "FILE_NOT_FOUND"` | Unit |
| AC-052-A-05d | GIVEN a file lock cannot be acquired within the timeout WHEN the script exits THEN the exit code is 3 AND error JSON includes `"error": "LOCK_TIMEOUT"` | Unit |

### AC-052-A-06: workflow_update_action.py — CLI Interface

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-06a | GIVEN the script is invoked with `--workflow myflow --action compose_idea --status done` WHEN it runs THEN it updates the action status in the workflow state file AND outputs `{"success": true, "data": {"action_updated": "compose_idea", "new_status": "done", ...}}` | Integration |
| AC-052-A-06b | GIVEN `--status invalid_value` is provided WHEN the script runs THEN it exits with code 1 AND outputs `{"success": false, "error": "INVALID_STATUS", "message": "Status must be one of: pending, in_progress, done, skipped, failed"}` | Unit |
| AC-052-A-06c | GIVEN `--deliverables '{"raw-ideas": "path/to/file.md"}'` is provided WHEN the script runs THEN the deliverables are parsed as JSON dict and stored in the action | Integration |
| AC-052-A-06d | GIVEN `--deliverables '["path1.md", "path2.md"]'` (legacy list format) is provided WHEN the script runs THEN the list is converted to a keyed dict using template tag order from `workflow-template.json` | Integration |
| AC-052-A-06e | GIVEN `--context '{"raw-ideas": "path.md"}'` is provided WHEN the script runs THEN the context dict is stored on the action | Integration |
| AC-052-A-06f | GIVEN `--features '[{"id": "FEATURE-001-A", "name": "My Feature", "depends_on": []}]'` is provided with `--action feature_breakdown --status done` WHEN the script runs THEN per-feature structures are populated for implement/validation/feedback stages AND `next_actions_suggested` is set to features with no dependencies | Integration |
| AC-052-A-06g | GIVEN `--feature-id FEATURE-001-A` is provided WHEN the script runs THEN the action is updated within the per-feature lane for that feature | Integration |
| AC-052-A-06h | GIVEN `--format json` (default) WHEN the script outputs results THEN output is valid JSON on stdout | Unit |
| AC-052-A-06i | GIVEN `--format text` WHEN the script outputs results THEN output is human-readable text on stdout | Unit |

### AC-052-A-07: workflow_update_action.py — Deliverable Validation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-07a | GIVEN deliverables contain a tag not defined in workflow-template.json for the action WHEN the script runs THEN it exits with code 1 AND outputs an error identifying the unexpected tag | Unit |
| AC-052-A-07b | GIVEN deliverables are missing a required tag defined in template WHEN the script runs THEN a warning is included in the output but the operation proceeds | Unit |
| AC-052-A-07c | GIVEN a `$output-folder` tag has an array value WHEN the script runs THEN it exits with code 1 AND outputs an error that folder tags must be scalar strings | Unit |
| AC-052-A-07d | GIVEN a deliverable tag has an array value where all elements are non-empty strings WHEN the script runs THEN schema version is set to "4.0" AND the operation succeeds | Unit |
| AC-052-A-07e | GIVEN a deliverable tag has an array value with an empty string element WHEN the script runs THEN it exits with code 1 AND outputs an error about invalid array elements | Unit |

### AC-052-A-08: workflow_update_action.py — Schema Versioning

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-08a | GIVEN deliverables are a keyed dict with all scalar values WHEN the action is updated THEN `schema_version` is set to "3.0" (or kept if already higher) | Unit |
| AC-052-A-08b | GIVEN deliverables contain at least one array value WHEN the action is updated THEN `schema_version` is set to "4.0" (or kept if already higher) | Unit |
| AC-052-A-08c | GIVEN current `schema_version` is "4.0" AND new deliverables are scalar (3.0) WHEN the action is updated THEN `schema_version` remains "4.0" (upward-only) | Unit |

### AC-052-A-09: workflow_update_action.py — Stage Gating

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-09a | GIVEN an action status is set to "done" WHEN stage gating is re-evaluated THEN the response includes the current stage name and next suggested action | Integration |
| AC-052-A-09b | GIVEN keyed deliverables are provided AND no `--context` flag is given WHEN the action is updated THEN an empty context dict `{}` is initialized on the action if none exists | Unit |

### AC-052-A-10: workflow_get_state.py — CLI Interface

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-10a | GIVEN a valid workflow name WHEN `workflow_get_state.py --workflow myflow` is invoked THEN the full workflow state JSON is output to stdout | Integration |
| AC-052-A-10b | GIVEN a workflow name with no corresponding state file WHEN the script runs THEN it exits with code 2 AND outputs `{"success": false, "error": "FILE_NOT_FOUND"}` | Unit |
| AC-052-A-10c | GIVEN a workflow state file with corrupted JSON WHEN the script runs THEN it exits with code 1 AND outputs `{"success": false, "error": "JSON_PARSE_ERROR"}` | Unit |
| AC-052-A-10d | GIVEN `--format text` WHEN the script runs THEN it outputs a human-readable summary of the workflow state (current stage, action statuses) | Unit |

### AC-052-A-11: Zero Dependencies & Stdlib Only

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-11a | GIVEN the scripts and `_lib.py` WHEN their import statements are inspected THEN only Python standard library modules are used (json, os, sys, argparse, tempfile, fcntl, pathlib, time, contextlib, datetime) | Unit |
| AC-052-A-11b | GIVEN a clean Python 3.10+ environment with no pip packages installed WHEN the scripts are executed THEN they run without import errors | Integration |

### AC-052-A-12: Output Compatibility

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-A-12a | GIVEN `workflow_update_action.py` completes successfully WHEN the output JSON is compared to the current MCP tool response THEN the structure matches: `{"success": true, "data": {"action_updated": str, "new_status": str, "current_stage": str, "next_action": {"action": str or null, "stage": str or null, "feature_id": str or null, "reason": str}}}` | Unit |
| AC-052-A-12b | GIVEN `workflow_get_state.py` completes successfully WHEN the output JSON is compared to the current MCP tool response THEN the structure matches the full workflow state dict | Unit |
| AC-052-A-12c | GIVEN any script encounters an error WHEN the output JSON is inspected THEN the structure matches: `{"success": false, "error": str, "message": str}` | Unit |

## Functional Requirements

### FR-052-A.01: Shared Utility Module (_lib.py)

**Description:** A Python module providing reusable primitives for all EPIC-052 scripts.

**Details:**
- Input: File paths, JSON data, format strings
- Process: Atomic file operations, lock management, path resolution, output formatting
- Output: Read data, write confirmations, resolved paths, formatted output

**Functions:**
- `atomic_read_json(path: Path) -> dict` — Reads and parses JSON; returns error dict on failure
- `atomic_write_json(path: Path, data: dict) -> None` — Writes via tempfile+fsync+replace; raises on failure
- `with_file_lock(lock_path: Path, timeout: int = 10) -> ContextManager` — Acquires fcntl.flock(LOCK_EX); exits with code 3 on timeout
- `resolve_project_root() -> Path` — Walks up from CWD looking for `x-ipe-docs/` marker
- `resolve_workflow_dir() -> Path` — Returns `{project_root}/x-ipe-docs/engineering-workflow/`
- `resolve_kb_root() -> Path` — Returns `{project_root}/x-ipe-docs/knowledge-base/`
- `output_result(result: dict, fmt: str) -> None` — Prints to stdout in JSON or text format
- `exit_with_error(code: int, error: str, message: str) -> NoReturn` — Prints error JSON and exits

### FR-052-A.02: workflow_update_action.py

**Description:** CLI script to update workflow action status, replacing the MCP `update_workflow_action` tool.

**Details:**
- Input: `--workflow`, `--action`, `--status`, `--feature-id` (optional), `--deliverables` (JSON string, optional), `--context` (JSON string, optional), `--features` (JSON string, optional), `--format` (json|text), `--lock-timeout` (seconds)
- Process:
  1. Parse and validate arguments
  2. Resolve project root and workflow directory
  3. Read workflow-template.json for deliverable tag definitions
  4. Acquire exclusive file lock on workflow state file
  5. Read current workflow state
  6. Validate status enum
  7. Convert deliverable list to keyed dict if needed (using template tags)
  8. Validate deliverable tags against template (abort on unexpected tags)
  9. Determine schema version (3.0 for scalar dict, 4.0 for array values)
  10. Update action status, deliverables, context
  11. Handle feature_breakdown special case (populate per-feature structures)
  12. Re-evaluate stage gating
  13. Persist state atomically
  14. Release lock
  15. Output result
- Output: JSON `{"success": true, "data": {...}}` on stdout, exit 0

### FR-052-A.03: workflow_get_state.py

**Description:** CLI script to read full workflow state, replacing the MCP `get_workflow_state` tool.

**Details:**
- Input: `--workflow`, `--format` (json|text)
- Process:
  1. Resolve project root and workflow directory
  2. Read workflow state file
  3. Handle missing or corrupted files
- Output: Full workflow state JSON on stdout, exit 0

## Non-Functional Requirements

### NFR-052-A.01: Crash Safety

Atomic writes MUST use the tempfile→fsync→os.replace pattern. If the process is killed at any point during a write, the original file must remain intact.

### NFR-052-A.02: Concurrent Access Safety

All write operations MUST acquire an exclusive file lock (`fcntl.flock(LOCK_EX)`) before reading or modifying the workflow state file. Lock scope covers the entire read→modify→write cycle.

### NFR-052-A.03: Lock Timeout

Default lock timeout is 10 seconds. Configurable via `--lock-timeout` flag. Exit with code 3 if lock cannot be acquired within timeout.

### NFR-052-A.04: Platform Scope

`fcntl.flock` is Unix/macOS only. This is acceptable — X-IPE targets macOS and Linux.

### NFR-052-A.05: Python Version

Scripts MUST run on Python 3.10+ (minimum version supported by X-IPE).

## UI/UX Requirements

N/A — this is a CLI/script infrastructure feature with no user interface.

## Dependencies

### Internal Dependencies

- None (this is the foundation feature for EPIC-052)

### External Dependencies

- **Python 3.10+:** Runtime requirement
- **x-ipe-docs/config/workflow-template.json:** Read at runtime for deliverable tag definitions
- **x-ipe-docs/engineering-workflow/workflow-{name}.json:** Workflow state files (read/written by scripts)

## Business Rules

- **BR-052-A.01:** Status values are restricted to: `pending`, `in_progress`, `done`, `skipped`, `failed`. Any other value is rejected with exit code 1.
- **BR-052-A.02:** Schema version is upward-only: once upgraded to 3.0 or 4.0, it never downgrades.
- **BR-052-A.03:** `$output-folder` deliverable tags must be scalar strings, never arrays.
- **BR-052-A.04:** When `action=feature_breakdown`, `status=done`, and `--features` is provided, per-feature structures are populated for implement/validation/feedback stages.
- **BR-052-A.05:** When keyed deliverables are provided without `--context`, an empty context dict `{}` is initialized on the action if none exists.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Workflow state file does not exist | `workflow_update_action.py` exits with code 2; `workflow_get_state.py` exits with code 2 |
| Workflow state file contains invalid JSON | Exit with code 1 and `JSON_PARSE_ERROR` |
| `workflow-template.json` missing | Exit with code 2 and `FILE_NOT_FOUND` |
| Lock held by another process beyond timeout | Exit with code 3 and `LOCK_TIMEOUT` |
| Deliverables provided as empty dict `{}` | Accepted — no tag validation needed for empty dict |
| Deliverables provided as empty list `[]` | Converted to empty keyed dict `{}` (no template tags to match) |
| `--features` flag without `--action feature_breakdown` | Features parameter is ignored (only processed for feature_breakdown action) |
| `--feature-id` provided for a shared-stage action | Feature ID is ignored for shared-stage actions |
| Script called from outside any project directory | Exit with code 2 and `PROJECT_ROOT_NOT_FOUND` |
| Multiple concurrent script invocations | File lock ensures sequential access; second caller waits up to timeout |

## Out of Scope

- KB index scripts (FEATURE-052-B)
- UIUX reference script (FEATURE-052-C)
- Skill migration and MCP removal (FEATURE-052-D)
- Flask API route changes (routes remain for web UI)
- Windows/non-Unix platform support
- Schema migration from v1 to v2 format (handled by existing service)
- Performance optimization beyond basic I/O patterns

## Technical Considerations

- Scripts will live in `.github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/`
- The `_lib.py` module is imported by all other scripts in the same directory
- `workflow-template.json` is loaded on every invocation (no caching between runs)
- The feature breakdown `_populate_features()` logic requires knowledge of stage configuration (mandatory vs optional actions per stage) — this config should be derived from `workflow-template.json`
- File lock granularity is per-workflow (one `.lock` file per workflow state file)
- JSON output uses `ensure_ascii=False` to preserve Unicode characters (Chinese filenames, etc.)

## Open Questions

- None (all clarifications resolved during ideation, requirement gathering, and refinement phases)
