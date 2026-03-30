---
skill: x-ipe-tool-x-ipe-app-interactor
---

# Skill Meta — x-ipe-tool-x-ipe-app-interactor

## IDENTITY

| Field | Value |
|-------|-------|
| skill_name | x-ipe-tool-x-ipe-app-interactor |
| skill_type | x-ipe-tool |
| version | 1.0.0 |
| status | production |
| created | 2026-03-30 |
| last_synced | 2026-03-30 |
| epic | EPIC-052 |
| features | FEATURE-052-A, FEATURE-052-B, FEATURE-052-C, FEATURE-052-D |

## PURPOSE

| Field | Value |
|-------|-------|
| summary | Standalone Python CLI scripts for X-IPE project state management — workflow actions, KB index metadata, and UIUX reference persistence. Zero external dependencies. Replaces the x-ipe-app-and-agent-interaction MCP server. |
| triggers | workflow update, kb index, uiux reference, project state, app interactor |
| not_for | MCP server operations (deprecated), direct Flask API calls |

## INTERFACE

### Operations

| Operation | Script | Purpose |
|-----------|--------|---------|
| workflow_update_action | `scripts/workflow_update_action.py` | Update workflow action status with deliverables |
| workflow_get_state | `scripts/workflow_get_state.py` | Read full workflow state |
| kb_get_index | `scripts/kb_get_index.py` | Read folder's .kb-index.json entries |
| kb_set_entry | `scripts/kb_set_entry.py` | Create/update KB index entry |
| kb_remove_entry | `scripts/kb_remove_entry.py` | Remove KB index entry |
| uiux_save_reference | `scripts/uiux_save_reference.py` | Persist UIUX reference data with multi-file generation |

### Shared Utilities

| Module | Purpose |
|--------|---------|
| `scripts/_lib.py` | Project root discovery, atomic writes, file locking, output formatting |
| `scripts/_kb_lib.py` | KB index reading with format detection (canonical/legacy) |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation error |
| 2 | File/folder not found |
| 3 | Lock timeout |

## DEPENDENCIES

| Type | Name | Relationship |
|------|------|-------------|
| replaces | x-ipe-app-and-agent-interaction MCP server | Full replacement — all 6 MCP tools now have script equivalents |
| consumed_by | 12 task-based skills | Workflow Mode header references script invocations |
| consumed_by | x-ipe-workflow-task-execution | Verification step references script |
| consumed_by | x-ipe-tool-kb-librarian | KB write operations |
| consumed_by | x-ipe-tool-uiux-reference | UIUX data persistence |

## ACCEPTANCE CRITERIA (MoSCoW)

### MUST

| ID | Criterion |
|----|-----------|
| M1 | All 6 scripts execute successfully with `python3` and zero external dependencies |
| M2 | Scripts discover project root by walking up from CWD looking for `x-ipe-docs/` |
| M3 | All write operations use atomic file writes (tempfile → fsync → rename) |
| M4 | KB write operations use `fcntl.flock` for concurrency safety |
| M5 | Output is structured JSON to stdout on success |
| M6 | Exit codes follow the 0/1/2/3 convention |
| M7 | SKILL.md documents all 6 operations with CLI args and examples |

### SHOULD

| ID | Criterion |
|----|-----------|
| S1 | Error messages include actionable guidance |
| S2 | Scripts support both `--format json` and `--format text` output |
| S3 | Lock timeout is configurable via `--lock-timeout` flag |

## TESTING

| Test Suite | Tests | Status |
|------------|-------|--------|
| tests/test_feature_052a.py | 57 (workflow scripts) | ✅ Passing |
| tests/test_feature_052b.py | 38 (KB index scripts) | ✅ Passing |
| tests/test_feature_052c.py | 47 (UIUX reference script) | ✅ Passing |

## CHANGE LOG

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-30 | Initial release — all 6 scripts, SKILL.md, full test coverage (142 tests) |
