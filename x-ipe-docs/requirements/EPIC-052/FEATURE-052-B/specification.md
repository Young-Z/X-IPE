# Feature Specification: KB Index Scripts

> Feature ID: FEATURE-052-B
> Version: v1.0
> Status: Refined
> Last Updated: 03-30-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-30-2026 | Initial specification |

## Linked Mockups

N/A — CLI scripts with no UI.

## Overview

Replace the three Knowledge Base (KB) index MCP tools (`get_kb_index`, `set_kb_index_entry`, `remove_kb_index_entry`) with standalone Python scripts that directly read/write `.kb-index.json` files. These scripts eliminate the MCP protocol overhead (Agent → MCP stdio → FastMCP → HTTP POST → Flask → Service → JSON) for simple CRUD metadata operations.

Each script is a CLI tool invoked as `python3 script.py <args>` that reuses `_lib.py` from FEATURE-052-A for atomic I/O, file locking, project root discovery, and structured output. The scripts maintain full behavioral compatibility with the existing MCP tools — same input parameters, same output structure, same error handling.

The KB index is a per-folder metadata registry (`.kb-index.json`) that tracks title, description, tags, author, type, and other metadata for files and subfolders in the knowledge base. It supports both the canonical format (`{"version": "1.0", "entries": {...}}`) and a legacy flat format (auto-wrapped on read).

## User Stories

1. **As an AI agent**, I want to read KB index entries via a CLI script, so that I can discover knowledge base contents without depending on the MCP server or Flask backend.

2. **As an AI agent**, I want to create/update KB index entries via a CLI script, so that I can register new files in the knowledge base directly from any skill.

3. **As an AI agent**, I want to remove KB index entries via a CLI script, so that I can clean up metadata for deleted files without the MCP server.

4. **As a skill author**, I want the KB scripts to use the same output format as the MCP tools, so that migrating skills requires minimal changes.

## Acceptance Criteria

### AC-052-B-01: kb_get_index.py — Read Index

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-B-01a | GIVEN a folder with a valid `.kb-index.json` in canonical format WHEN `kb_get_index.py --folder {relative_path}` is invoked THEN the output is `{"success": true, "folder": "{relative_path}", "index": {"version": "1.0", "entries": {...}}}` | Unit |
| AC-052-B-01b | GIVEN `--folder` is omitted or empty WHEN the script runs THEN it reads the KB root folder's `.kb-index.json` | Unit |
| AC-052-B-01c | GIVEN a folder with no `.kb-index.json` file WHEN the script runs THEN the output is `{"success": true, "folder": "...", "index": {"version": "1.0", "entries": {}}}` | Unit |
| AC-052-B-01d | GIVEN a `.kb-index.json` in legacy flat format (no "entries" wrapper) WHEN the script reads it THEN it auto-wraps into canonical format: top-level dict keys (excluding "version") become entries | Unit |
| AC-052-B-01e | GIVEN a `.kb-index.json` with corrupted/invalid JSON WHEN the script reads it THEN it returns `{"success": true, "folder": "...", "index": {"version": "1.0", "entries": {}}}` AND logs a warning to stderr | Unit |
| AC-052-B-01f | GIVEN the folder path does not exist under the KB root WHEN the script runs THEN it exits with code 2 AND outputs `{"success": false, "error": "FOLDER_NOT_FOUND"}` | Unit |
| AC-052-B-01g | GIVEN `--format text` WHEN the script outputs results THEN a human-readable summary of entries is printed | Unit |

### AC-052-B-02: kb_set_entry.py — Create/Update Entry

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-B-02a | GIVEN a valid name and entry dict WHEN `kb_set_entry.py --folder {path} --name {name} --entry '{json}'` is invoked THEN the entry is written to `.kb-index.json` AND output is `{"success": true, "folder": "...", "name": "...", "entry": {...}}` | Integration |
| AC-052-B-02b | GIVEN an entry already exists for the name WHEN the script runs with new entry data THEN the existing entry is replaced (full overwrite, not merge) | Unit |
| AC-052-B-02c | GIVEN no `.kb-index.json` exists in the folder WHEN the script runs THEN a new `.kb-index.json` is created with `{"version": "1.0", "entries": {name: entry}}` | Unit |
| AC-052-B-02d | GIVEN the `.kb-index.json` is in legacy flat format WHEN the script runs THEN it reads the flat format, converts to canonical, adds/updates the entry, and writes canonical format | Unit |
| AC-052-B-02e | GIVEN `--name` is a folder name ending with "/" WHEN the script runs THEN the entry is stored with the trailing slash key (e.g., `"guides/": {...}`) | Unit |
| AC-052-B-02f | GIVEN `--entry` is not valid JSON WHEN the script runs THEN it exits with code 1 AND outputs `{"success": false, "error": "INVALID_ENTRY_JSON"}` | Unit |
| AC-052-B-02g | GIVEN `--name` is empty or whitespace-only WHEN the script runs THEN it exits with code 1 AND outputs `{"success": false, "error": "INVALID_NAME"}` | Unit |
| AC-052-B-02h | GIVEN the write is interrupted mid-operation WHEN the script resumes THEN the original `.kb-index.json` is unchanged (atomic write via _lib.py) | Unit |
| AC-052-B-02i | GIVEN `--format text` WHEN the script outputs results THEN a human-readable confirmation is printed | Unit |

### AC-052-B-03: kb_remove_entry.py — Remove Entry

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-B-03a | GIVEN an entry exists for the name WHEN `kb_remove_entry.py --folder {path} --name {name}` is invoked THEN the entry is removed from `.kb-index.json` AND output is `{"success": true, "folder": "...", "name": "...", "removed": true}` | Integration |
| AC-052-B-03b | GIVEN no entry exists for the name WHEN the script runs THEN the output is `{"success": true, "folder": "...", "name": "...", "removed": false}` AND the file is NOT modified | Unit |
| AC-052-B-03c | GIVEN the `.kb-index.json` does not exist WHEN the script runs THEN the output is `{"success": true, "folder": "...", "name": "...", "removed": false}` AND no file is created | Unit |
| AC-052-B-03d | GIVEN `--name` is empty or whitespace-only WHEN the script runs THEN it exits with code 1 AND outputs `{"success": false, "error": "INVALID_NAME"}` | Unit |
| AC-052-B-03e | GIVEN `--format text` WHEN the script outputs results THEN a human-readable confirmation is printed | Unit |

### AC-052-B-04: File Locking

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-B-04a | GIVEN `kb_set_entry.py` is invoked WHEN it writes to `.kb-index.json` THEN it acquires an exclusive file lock on a `.kb-index.json.lock` file in the same folder before reading and releases after writing | Unit |
| AC-052-B-04b | GIVEN `kb_remove_entry.py` is invoked WHEN it modifies `.kb-index.json` THEN it acquires the same exclusive lock pattern as set_entry | Unit |
| AC-052-B-04c | GIVEN `kb_get_index.py` is invoked (read-only) WHEN it reads `.kb-index.json` THEN it does NOT acquire a file lock | Unit |
| AC-052-B-04d | GIVEN a lock is held by another process WHEN a write script tries to acquire THEN it retries until `--lock-timeout` (default 10s) expires, then exits with code 3 | Unit |

### AC-052-B-05: Shared Utilities Reuse

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-B-05a | GIVEN the KB scripts import from `_lib.py` WHEN their imports are inspected THEN they use `resolve_project_root`, `resolve_kb_root`, `atomic_read_json`, `atomic_write_json`, `with_file_lock`, `output_result`, `exit_with_error` from `_lib` | Unit |
| AC-052-B-05b | GIVEN the KB scripts WHEN their import statements are inspected THEN only Python standard library modules and `_lib` are used (zero external dependencies) | Unit |

### AC-052-B-06: Output Compatibility

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-B-06a | GIVEN `kb_get_index.py` returns successfully WHEN the output JSON is compared to the MCP tool response THEN the structure matches: `{"success": true, "folder": str, "index": {"version": str, "entries": dict}}` | Unit |
| AC-052-B-06b | GIVEN `kb_set_entry.py` returns successfully WHEN the output JSON is compared to the MCP tool response THEN the structure matches: `{"success": true, "folder": str, "name": str, "entry": dict}` | Unit |
| AC-052-B-06c | GIVEN `kb_remove_entry.py` returns successfully WHEN the output JSON is compared to the MCP tool response THEN the structure matches: `{"success": true, "folder": str, "name": str, "removed": bool}` | Unit |
| AC-052-B-06d | GIVEN any KB script encounters an error WHEN the output JSON is inspected THEN the structure matches: `{"success": false, "error": str, "message": str}` | Unit |

### AC-052-B-07: Exit Codes

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052-B-07a | GIVEN any KB script completes successfully WHEN it exits THEN the exit code is 0 | Unit |
| AC-052-B-07b | GIVEN a validation error occurs (invalid JSON, empty name) WHEN the script exits THEN the exit code is 1 | Unit |
| AC-052-B-07c | GIVEN a required folder does not exist WHEN the script exits THEN the exit code is 2 | Unit |
| AC-052-B-07d | GIVEN a file lock cannot be acquired within the timeout WHEN the script exits THEN the exit code is 3 | Unit |

> **Test Type Legend:**
> - **Unit** — Isolated function/module test (parsing, file I/O, validation)
> - **Integration** — Multi-component interaction test (script end-to-end with temp filesystem)

## Functional Requirements

**FR-052-B.01: KB Root Resolution**
Scripts resolve the knowledge base root via `resolve_kb_root()` from `_lib.py`, which returns `{project_root}/x-ipe-docs/knowledge-base/`. The `--folder` argument is a relative path appended to this root.

**FR-052-B.02: Index Read with Format Detection**
`kb_get_index.py` reads `.kb-index.json` and detects the format:
- **Canonical:** `{"version": "1.0", "entries": {...}}` — returned as-is
- **Legacy flat:** `{"file.md": {...}, ...}` — auto-wrapped into canonical format (all top-level dict keys except "version" become entries)

**FR-052-B.03: Atomic Index Write**
`kb_set_entry.py` and `kb_remove_entry.py` use the read-modify-write pattern with file locking:
1. Acquire exclusive lock on `.kb-index.json.lock`
2. Read current index (or create empty canonical structure)
3. Modify entries
4. Write atomically via `atomic_write_json()`
5. Release lock

## Non-Functional Requirements

**NFR-052-B.01: Zero External Dependencies**
All scripts use only Python standard library modules plus `_lib.py` from FEATURE-052-A.

**NFR-052-B.02: Crash Safety**
Write operations use `atomic_write_json()` (tempfile → fsync → os.replace) so that a crash never corrupts `.kb-index.json`.

**NFR-052-B.03: Backward Compatibility**
Scripts read both canonical and legacy flat `.kb-index.json` formats. Writes always produce canonical format.

**NFR-052-B.04: Output Compatibility**
Script JSON output structures match the existing MCP tool responses so that consuming skills require minimal migration changes.

## UI/UX Requirements

N/A — CLI scripts with no user interface.

## Dependencies

### Internal
- **FEATURE-052-A** (Closed): Provides `_lib.py` shared utilities in `.github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/`
- **KB Service** (`src/x_ipe/services/kb_service.py`): Reference implementation for business logic — scripts replicate its behavior

### External
- Python 3.10+ standard library

## Business Rules

**BR-052-B.01:** The `.kb-index.json` version is always `"1.0"` for KB indices — unlike workflow state files, there is no schema version evolution.

**BR-052-B.02:** Entry names for folders MUST end with `/` (e.g., `"guides/"`). Entry names for files do not have trailing slashes.

**BR-052-B.03:** Removing an entry that does not exist is a no-op — it succeeds with `"removed": false`, and the file is NOT written.

**BR-052-B.04:** The actual files/folders in the knowledge base are NOT affected by these scripts — they only manage the metadata index.

**BR-052-B.05:** Reading a corrupted `.kb-index.json` returns empty entries (graceful degradation) rather than failing.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| `.kb-index.json` missing | get: return empty entries; set: create new file; remove: return removed=false |
| `.kb-index.json` corrupted JSON | get: return empty entries + warn stderr; set: overwrite with new canonical structure; remove: return removed=false |
| Legacy flat format `.kb-index.json` | Auto-wrap into canonical format on read; write always produces canonical |
| `--folder` points to non-existent directory | Exit code 2, FOLDER_NOT_FOUND error |
| `--name` is empty/whitespace | Exit code 1, INVALID_NAME error |
| `--entry` is not valid JSON | Exit code 1, INVALID_ENTRY_JSON error |
| Concurrent write access | File lock prevents corruption; second process waits or times out |
| Entry name contains special characters | Stored as-is in JSON (unicode safe via ensure_ascii=False) |
| Very large `.kb-index.json` (1000+ entries) | Handled normally — full file read/write per operation |

## Out of Scope

- File content indexing or search (just metadata registry)
- Directory creation or file management (metadata only)
- KB intake pipeline processing (separate EPIC-049 concern)
- Migration of consuming skills (FEATURE-052-D)
- Performance optimization for very large indices (YAGNI)

## Technical Considerations

- Scripts location: `.github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/`
- Lock file convention: `.kb-index.json.lock` in the same directory as `.kb-index.json`
- The `_lib.py` `atomic_read_json()` returns error dicts for missing/corrupted files, but KB scripts need graceful degradation (empty entries) — scripts should handle the error dict and convert to empty index
- `kb_get_index.py` is read-only and does NOT need file locking
- `kb_set_entry.py` and `kb_remove_entry.py` MUST lock before read-modify-write

## Open Questions

None — all design decisions resolved via FEATURE-052-A patterns and existing service implementation.
