---
name: x-ipe-tool-x-ipe-app-interactor
description: Standalone Python scripts for project state management — workflow actions, KB index metadata, and UIUX reference persistence. Replaces the x-ipe-app-and-agent-interaction MCP server with direct file I/O. Zero external dependencies.
---

# Tool Skill: X-IPE App Interactor

## Purpose

Provide standalone CLI scripts that manage X-IPE project state by directly reading/writing JSON files — no MCP server or Flask backend required.

## Operations

### 1. workflow_update_action

Update the status of a workflow action with deliverables.

```bash
python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_update_action.py \
  --workflow "{workflow_name}" \
  --action "{action}" \
  --status "done" \
  --feature-id "{FEATURE-XXX}" \
  --deliverables '{"tag-name": "path/to/file"}' \
  --format json
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--workflow` | Yes | Workflow name |
| `--action` | Yes | Action identifier (e.g., implementation, acceptance_testing) |
| `--status` | Yes | New status: pending, in_progress, done, skipped, failed |
| `--feature-id` | No | Feature ID for per-feature actions |
| `--deliverables` | No | JSON dict of deliverable tag→path mappings |
| `--context` | No | JSON dict of action context selections |
| `--features` | No | JSON list of feature objects (for feature_breakdown) |
| `--format` | No | Output format: json (default) or text |

### 2. workflow_get_state

Get the full state of an engineering workflow.

```bash
python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_get_state.py \
  --workflow "{workflow_name}" \
  --format json
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--workflow` | Yes | Workflow name |
| `--format` | No | Output format: json (default) or text |

### 3. kb_get_index

Read all entries from a folder's `.kb-index.json`.

```bash
python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/kb_get_index.py \
  --folder "{relative_folder}" \
  --format json
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--folder` | No | Relative folder path within KB root (empty = KB root) |
| `--format` | No | Output format: json (default) or text |

### 4. kb_set_entry

Create or update a metadata entry in a folder's `.kb-index.json`.

```bash
python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/kb_set_entry.py \
  --name "{filename}" \
  --entry '{"title": "...", "description": "...", "tags": {...}}' \
  --folder "{relative_folder}" \
  --format json
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--name` | Yes | Filename or foldername/ to set entry for |
| `--entry` | Yes | JSON dict with metadata (title, description, tags, etc.) |
| `--folder` | No | Relative folder path within KB root (empty = KB root) |
| `--lock-timeout` | No | Lock timeout in seconds (default: 10) |
| `--format` | No | Output format: json (default) or text |

### 5. kb_remove_entry

Remove a metadata entry from a folder's `.kb-index.json`.

```bash
python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/kb_remove_entry.py \
  --name "{filename}" \
  --folder "{relative_folder}" \
  --format json
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--name` | Yes | Filename or foldername/ whose entry to remove |
| `--folder` | No | Relative folder path within KB root (empty = KB root) |
| `--lock-timeout` | No | Lock timeout in seconds (default: 10) |
| `--format` | No | Output format: json (default) or text |

### 6. uiux_save_reference

Save UIUX reference data to an idea folder with multi-file generation.

```bash
python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/uiux_save_reference.py \
  --data-file /tmp/uiux-data.json \
  --format json
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--data-file` | No* | Path to JSON file with UIUX reference data |
| `--data` | No* | Inline JSON string with UIUX reference data |
| `--format` | No | Output format: json (default) or text |

\* At least one of `--data-file` or `--data` required. `--data-file` takes precedence.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation error (missing args, invalid JSON, schema violation) |
| 2 | File/folder not found (workflow file, idea folder, KB folder) |
| 3 | Lock timeout (KB write operations only) |

## Shared Utilities

All scripts import from `_lib.py` which provides:
- `resolve_project_root()` — find project root from CWD
- `atomic_write_json(path, data)` — crash-safe JSON persistence
- `with_file_lock(lock_path, timeout)` — exclusive file locking
- `output_result(result, fmt)` — structured JSON/text output
- `exit_with_error(code, error, message)` — structured error exit

KB scripts additionally import from `_kb_lib.py` which provides:
- `read_kb_index(index_path)` — read with format detection (canonical/legacy)

## Dependencies

- Python 3.10+ (standard library only, zero external packages)
- Project must have `x-ipe-docs/` directory (for project root detection)
