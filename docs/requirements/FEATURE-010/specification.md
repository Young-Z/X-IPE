# Feature Specification: Project Root Configuration

> Feature ID: FEATURE-010  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-23-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 01-23-2026 | Initial specification | - |

## Overview

This feature enables X-IPE to operate as a subfolder within a larger project by introducing a `.x-ipe.yaml` configuration file. When X-IPE runs inside a nested project structure (e.g., `project-root/x-ipe/`), the config file at the project root defines path mappings so the file tree shows the entire project, not just the X-IPE application folder.

The config discovery mechanism traverses from the current working directory up to parent directories, allowing flexible launch locations (`python x-ipe/main.py` from project root OR `python main.py` from the x-ipe folder). This is fully backward compatible—without a config file, X-IPE behaves exactly as before.

## User Stories

- As a **developer**, I want X-IPE to **discover the project root automatically**, so that **I can view my entire project structure, not just the X-IPE app folder**.
- As a **developer**, I want to **configure the terminal's working directory**, so that **my terminal starts in the project root where I run my commands**.
- As a **developer**, I want to **see the active configuration in Settings**, so that **I can verify X-IPE detected the correct paths**.
- As a **developer**, I want X-IPE to **work without a config file**, so that **existing projects continue to work without changes**.

## Acceptance Criteria

- [x] AC-1: X-IPE reads `.x-ipe.yaml` config file if present in cwd or parent directories
- [x] AC-2: Config discovery traverses from cwd up to 20 parent directories before giving up
- [x] AC-3: Config defines `paths.project_root` and `paths.x_ipe_app` (relative to config file location)
- [x] AC-4: Config defines `defaults.file_tree_scope` ("project_root" or "x_ipe_app")
- [x] AC-5: Config defines `defaults.terminal_cwd` for terminal working directory
- [x] AC-6: File tree defaults to `project_root` when `file_tree_scope: "project_root"`
- [x] AC-7: Works when launched from project root (`python x-ipe/main.py`) or x-ipe folder (`python main.py`)
- [x] AC-8: Invalid paths in config show warning toast and fall back to current working directory
- [x] AC-9: Existing multi-project folder behavior (FEATURE-006) remains unchanged
- [x] AC-10: Settings page shows read-only display of detected `.x-ipe.yaml` config values
- [x] AC-11: Without `.x-ipe.yaml`, X-IPE behaves exactly as before (backward compatible)

## Functional Requirements

### FR-1: Config File Discovery

**Description:** Locate `.x-ipe.yaml` starting from cwd and traversing parent directories.

**Details:**
- Input: Current working directory at application startup
- Process: 
  1. Check cwd for `.x-ipe.yaml`
  2. If not found, check parent directory
  3. Repeat up to 20 levels (safety limit)
  4. Stop at filesystem root
- Output: Config file path or None if not found

### FR-2: Config File Parsing

**Description:** Parse and validate `.x-ipe.yaml` content.

**Details:**
- Input: Path to config file
- Process:
  1. Read YAML content using PyYAML
  2. Validate required fields: `version`, `paths.project_root`, `paths.x_ipe_app`
  3. Resolve relative paths based on config file location
  4. Validate paths exist and are directories
- Output: ConfigData object with resolved absolute paths

**Config Schema:**
```yaml
# .x-ipe.yaml
version: 1
paths:
  project_root: "."          # Required: relative to this config file
  x_ipe_app: "./x-ipe"       # Required: path to X-IPE application
defaults:
  file_tree_scope: "project_root"  # Optional: "project_root" | "x_ipe_app", default: "project_root"
  terminal_cwd: "project_root"     # Optional: "project_root" | "x_ipe_app", default: "project_root"
```

### FR-3: Path Validation

**Description:** Ensure configured paths are valid and secure.

**Details:**
- Input: Resolved absolute paths from config
- Process:
  1. Check paths exist using `os.path.exists()`
  2. Check paths are directories using `os.path.isdir()`
  3. Validate paths don't escape project bounds (no `../../../` attacks)
  4. Verify x_ipe_app path contains expected X-IPE files (e.g., `main.py`)
- Output: Validation result with errors if invalid

### FR-4: File Tree Integration

**Description:** Apply config to file tree default scope.

**Details:**
- Input: ConfigData with `file_tree_scope` setting
- Process:
  1. If config exists and `file_tree_scope: "project_root"`, default to project root path
  2. If config exists and `file_tree_scope: "x_ipe_app"`, default to x_ipe_app path
  3. If no config, use current behavior (cwd)
- Output: Default path for file tree

### FR-5: Terminal Integration

**Description:** Apply config to terminal default working directory.

**Details:**
- Input: ConfigData with `terminal_cwd` setting
- Process:
  1. If config exists, set terminal cwd based on `terminal_cwd` value
  2. Map "project_root" → resolved project_root path
  3. Map "x_ipe_app" → resolved x_ipe_app path
  4. If no config, use current behavior (cwd)
- Output: Terminal working directory path

### FR-6: Settings Page Display

**Description:** Show read-only config information on Settings page.

**Details:**
- Input: ConfigData from ConfigService
- Process:
  1. Add new section "Project Configuration" to Settings page
  2. Display detected config file path (or "No config file detected")
  3. Display resolved paths: project_root, x_ipe_app
  4. Display current defaults: file_tree_scope, terminal_cwd
- Output: Read-only config card on Settings page

## Non-Functional Requirements

### NFR-1: Performance

- Config discovery should complete in < 100ms (max 20 directory checks)
- Config parsing should complete in < 50ms
- No performance impact when config file doesn't exist

### NFR-2: Security

- Path traversal prevention: reject paths containing `..` that escape project root
- Validate all paths are within expected bounds before use
- Read-only access to config (no API to modify config file)

### NFR-3: Reliability

- Graceful fallback on any config error
- Clear error messages for debugging
- Never crash due to missing/invalid config

## UI/UX Requirements

### Settings Page: Project Configuration Section

**Location:** Below existing Settings sections

**UI Elements:**
- Card with header "Project Configuration"
- Read-only text fields showing:
  - Config File: `{path}` or "Not detected"
  - Project Root: `{resolved path}`
  - X-IPE App: `{resolved path}`  
  - File Tree Scope: `{value}`
  - Terminal CWD: `{value}`
- Info alert if no config detected: "No `.x-ipe.yaml` found. Using default paths."
- Warning alert if config has errors: "Config file found but has errors: {error message}"

## Dependencies

### Internal Dependencies

- **FEATURE-006:** Settings & Configuration - Settings page integration for displaying config values

### External Dependencies

- **PyYAML:** Python library for parsing YAML files (already in dependencies via uv)

## Business Rules

### BR-1: Config File Location Priority

**Rule:** Search for config in cwd first, then traverse parent directories.

**Example:**
- If cwd is `/project/x-ipe/`, check:
  1. `/project/x-ipe/.x-ipe.yaml`
  2. `/project/.x-ipe.yaml` ← Found here
  3. (Stop, don't check further)

### BR-2: Path Resolution

**Rule:** All paths in config are relative to the config file's directory, not cwd.

**Example:**
- Config at `/project/.x-ipe.yaml` with `paths.x_ipe_app: "./x-ipe"`
- Resolves to `/project/x-ipe/` regardless of where X-IPE was launched

### BR-3: Backward Compatibility

**Rule:** Without `.x-ipe.yaml`, X-IPE must behave exactly as in previous versions.

**Example:**
- No config file → file tree shows cwd
- No config file → terminal starts in cwd
- No config file → Settings shows "Not detected"

## Edge Cases & Constraints

### Edge Case 1: Config File at Root

**Scenario:** User places `.x-ipe.yaml` at filesystem root `/`  
**Expected Behavior:** Config is used normally (root is valid project root)

### Edge Case 2: Symlinked Directories

**Scenario:** `x_ipe_app` path is a symlink  
**Expected Behavior:** Follow symlink and validate target exists

### Edge Case 3: Path with Spaces

**Scenario:** Path contains spaces: `"/Users/name/My Projects/x-ipe"`  
**Expected Behavior:** Handle correctly, no escaping issues

### Edge Case 4: Missing Required Fields

**Scenario:** Config missing `paths.project_root`  
**Expected Behavior:** Show warning, fall back to cwd

### Edge Case 5: Config File Read Permission Denied

**Scenario:** `.x-ipe.yaml` exists but not readable  
**Expected Behavior:** Log warning, fall back to cwd

### Edge Case 6: Circular Parent Traversal

**Scenario:** Filesystem has unusual structure (e.g., bind mounts creating loops)  
**Expected Behavior:** Stop at 20 directory limit, fall back to cwd

### Edge Case 7: Project Root Outside X-IPE App

**Scenario:** Config sets `project_root: "../.."` (two levels up from x-ipe)  
**Expected Behavior:** Valid if path exists and doesn't escape 20-level limit

## Out of Scope

- Config file editing through the UI (read-only display only)
- Multiple config file support (only one `.x-ipe.yaml` per project)
- Environment variable expansion in config values
- Remote/URL-based config files
- Config file hot-reload (requires app restart)

## Technical Considerations

- New `ConfigService` class in `services.py`
- Config loaded once at application startup
- Store config data in app context for access by other services
- Add `/api/config` endpoint for frontend to fetch config state
- Integrate with `ProjectService` for file tree scope
- Integrate with `TerminalService` for terminal cwd
- Use `pathlib.Path` for cross-platform path handling

## Open Questions

- [x] Should config support environment variable expansion? **Decision: No (v1.0 keeps it simple)**
- [x] Should config hot-reload when file changes? **Decision: No (requires restart for simplicity)**
- [x] What happens if project_root doesn't contain .git? **Decision: Still valid, git is optional**

---
