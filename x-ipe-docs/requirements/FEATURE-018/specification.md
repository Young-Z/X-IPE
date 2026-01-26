# Feature Specification: X-IPE CLI Tool

> Feature ID: FEATURE-018  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-25-2026

## Overview

The X-IPE CLI Tool transforms X-IPE from a cloned repository into a pip-installable PyPI package with a command-line interface. This enables developers to use X-IPE on any project without copying files, managing subfolders, or manually creating configuration.

The CLI provides commands for project initialization (`x-ipe init`), running the web server (`x-ipe serve`), upgrading skills (`x-ipe upgrade`), and checking project status (`x-ipe status`, `x-ipe info`). Skills, templates, and static files are bundled within the package and accessed via Python's `importlib.resources`.

This is the foundation feature that enables FEATURE-019 (Simplified Project Setup) and FEATURE-020 (Skills Discovery & Override).

## User Stories

- As a **developer**, I want to **install X-IPE via pip**, so that **I can use it on any project without cloning repositories**.
- As a **developer**, I want to **run `x-ipe init` in my project**, so that **the necessary folder structure is created automatically**.
- As a **developer**, I want to **run `x-ipe serve` to start the web UI**, so that **I can manage ideas, requirements, and planning**.
- As a **developer**, I want to **run `x-ipe upgrade` when a new version is released**, so that **I get the latest skills and features**.
- As a **developer**, I want to **run `x-ipe status` to check my project's X-IPE state**, so that **I know if initialization is needed or if the server is running**.
- As a **developer**, I want to **run `x-ipe info` for detailed diagnostics**, so that **I can troubleshoot issues or report bugs**.

## Acceptance Criteria

### 1. Package Distribution
- [ ] AC-1.1: X-IPE published to PyPI as `x-ipe` package
- [ ] AC-1.2: Installable via `pip install x-ipe`
- [ ] AC-1.3: Package includes all skills as package data under `x_ipe/skills/`
- [ ] AC-1.4: Package includes static files (CSS, JS, templates) under `x_ipe/static/` and `x_ipe/templates/`
- [ ] AC-1.5: Package includes `.github/` templates for copilot instructions
- [ ] AC-1.6: Version follows semantic versioning (e.g., 1.0.0)
- [ ] AC-1.7: Package has minimal dependencies (Flask, Flask-SocketIO, click, PyYAML)

### 2. CLI Entry Point
- [ ] AC-2.1: `x-ipe` command available after installation
- [ ] AC-2.2: Running `x-ipe` without arguments shows help text
- [ ] AC-2.3: `x-ipe --version` shows package version
- [ ] AC-2.4: `x-ipe --help` shows all available commands with descriptions
- [ ] AC-2.5: Uses `click` library for CLI parsing

### 3. Init Command
- [ ] AC-3.1: `x-ipe init` creates project structure in current directory
- [ ] AC-3.2: Creates `x-ipe-docs/` folder with subfolders (ideas, planning, requirements, themes)
- [ ] AC-3.3: Creates `.x-ipe/` hidden folder for runtime data
- [ ] AC-3.4: Creates/merges `.github/skills/` with skills from package
- [ ] AC-3.5: Creates `.github/copilot-instructions.md` from package template
- [ ] AC-3.6: Creates `.x-ipe.yaml` config file with sensible defaults
- [ ] AC-3.7: Auto-detects git repository (checks for `.git/` folder)
- [ ] AC-3.8: If git detected, creates/updates `.gitignore` with X-IPE patterns
- [ ] AC-3.9: Adds `.x-ipe/` and `.x-ipe.yaml` to `.gitignore`
- [ ] AC-3.10: Non-destructive: skips existing files/folders with warning message
- [ ] AC-3.11: Shows summary of created/skipped items on completion
- [ ] AC-3.12: `--force` flag to overwrite existing files
- [ ] AC-3.13: `--dry-run` flag to preview changes without writing

### 4. Serve Command
- [ ] AC-4.1: `x-ipe serve` starts web server in current directory
- [ ] AC-4.2: Default port is 5000
- [ ] AC-4.3: `--port` flag to specify custom port (e.g., `x-ipe serve --port 8080`)
- [ ] AC-4.4: `--open` flag to auto-open browser after server starts
- [ ] AC-4.5: `--host` flag to specify bind address (default: 127.0.0.1)
- [ ] AC-4.6: Server discovers and uses `.x-ipe.yaml` if present
- [ ] AC-4.7: Falls back to sensible defaults without config file
- [ ] AC-4.8: `--debug` flag enables Flask debug mode with hot reload
- [ ] AC-4.9: Ctrl+C gracefully stops the server
- [ ] AC-4.10: Shows server URL on startup

### 5. Upgrade Command
- [ ] AC-5.1: `x-ipe upgrade` updates skills from package to local `.github/skills/`
- [ ] AC-5.2: Detects locally modified skills via hash comparison
- [ ] AC-5.3: Lists modified skills and prompts for confirmation before overwriting
- [ ] AC-5.4: `--force` flag to overwrite without confirmation
- [ ] AC-5.5: Creates backup of modified skills in `.x-ipe/backups/skills-{timestamp}/`
- [ ] AC-5.6: Updates `.github/copilot-instructions.md` from package
- [ ] AC-5.7: Shows summary of updated/skipped/backed-up items
- [ ] AC-5.8: `--dry-run` flag to preview changes

### 6. Status Command
- [ ] AC-6.1: `x-ipe status` shows project X-IPE status
- [ ] AC-6.2: Shows "Initialized" or "Not initialized" state
- [ ] AC-6.3: Shows skills count (package skills vs local overrides)
- [ ] AC-6.4: Shows if `.x-ipe.yaml` config exists
- [ ] AC-6.5: Shows if X-IPE server is currently running (checks port)
- [ ] AC-6.6: Exit code 0 if initialized, 1 if not

### 7. Info Command
- [ ] AC-7.1: `x-ipe info` shows detailed diagnostics
- [ ] AC-7.2: Shows X-IPE package version
- [ ] AC-7.3: Shows Python version and interpreter path
- [ ] AC-7.4: Shows config file path and parsed contents (if exists)
- [ ] AC-7.5: Shows paths: skills, docs, .x-ipe folder, static files
- [ ] AC-7.6: Shows package installation path
- [ ] AC-7.7: `--json` flag outputs machine-readable JSON

## Functional Requirements

### FR-1: Package Structure

**Description:** Define the Python package structure for PyPI distribution

**Details:**
- Input: Current X-IPE repository structure
- Process: Reorganize into pip-installable package
- Output: Package with following structure:

```
x-ipe/
├── pyproject.toml          # Package configuration
├── README.md               # PyPI description
├── LICENSE                 # MIT license
└── src/
    └── x_ipe/
        ├── __init__.py     # Package version
        ├── __main__.py     # Entry point for python -m x_ipe
        ├── cli.py          # Click CLI commands
        ├── app.py          # Flask app factory
        ├── config.py       # Configuration handling
        ├── services/       # Business logic
        ├── templates/      # Jinja2 templates
        ├── static/         # CSS, JS, images
        ├── skills/         # Bundled skills (package data)
        └── scaffolds/      # Init templates (.github/, x-ipe-docs/)
```

### FR-2: CLI Command Router

**Description:** Route CLI commands to appropriate handlers

**Details:**
- Input: Command line arguments
- Process: Parse with Click, dispatch to handler
- Output: Command execution result

```python
# Entry point in pyproject.toml
[project.scripts]
x-ipe = "x_ipe.cli:main"

# cli.py structure
@click.group()
@click.version_option()
def main():
    """X-IPE: Intelligent Project Environment"""
    pass

@main.command()
def init(): ...

@main.command()
def serve(): ...

@main.command()
def upgrade(): ...

@main.command()
def status(): ...

@main.command()
def info(): ...
```

### FR-3: Package Data Access

**Description:** Access bundled skills and templates from installed package

**Details:**
- Input: Resource path (e.g., "skills/task-type-bug-fix")
- Process: Use `importlib.resources` for package data access
- Output: File content or path to extracted resource

```python
from importlib import resources

def get_skill_path(skill_name: str) -> Path:
    """Get path to bundled skill."""
    with resources.as_file(resources.files("x_ipe.skills") / skill_name) as path:
        return path

def get_scaffold_path(name: str) -> Path:
    """Get path to scaffold template."""
    with resources.as_file(resources.files("x_ipe.scaffolds") / name) as path:
        return path
```

### FR-4: Init Command Handler

**Description:** Initialize X-IPE project structure

**Details:**
- Input: Current directory, flags (--force, --dry-run)
- Process:
  1. Check if already initialized (warn if so)
  2. Create `x-ipe-docs/` folder structure
  3. Create `.x-ipe/` runtime folder
  4. Copy skills to `.github/skills/`
  5. Copy copilot instructions to `.github/`
  6. Create `.x-ipe.yaml` with defaults
  7. Update `.gitignore` if git repo detected
- Output: Summary of created/skipped items

### FR-5: Serve Command Handler

**Description:** Start X-IPE web server

**Details:**
- Input: Flags (--port, --host, --open, --debug)
- Process:
  1. Load config from `.x-ipe.yaml` (or defaults)
  2. Create Flask app with config
  3. Start server with SocketIO
  4. Optionally open browser
- Output: Running web server

### FR-6: Upgrade Command Handler

**Description:** Sync skills from package to local project

**Details:**
- Input: Flags (--force, --dry-run)
- Process:
  1. Load skill hashes from `.x-ipe/skill-hashes.json`
  2. Compare local skills with package skills
  3. Identify modified/new/deleted skills
  4. Prompt for confirmation (unless --force)
  5. Backup modified skills
  6. Copy package skills to local
  7. Update hash file
- Output: Summary of changes

### FR-7: Status Command Handler

**Description:** Show project X-IPE status

**Details:**
- Input: Current directory
- Process:
  1. Check for `.x-ipe/` folder
  2. Check for `.x-ipe.yaml`
  3. Count skills (package vs local)
  4. Check if server running (port check)
- Output: Status summary

### FR-8: Info Command Handler

**Description:** Show detailed diagnostics

**Details:**
- Input: Flags (--json)
- Process:
  1. Gather version info
  2. Gather path info
  3. Parse config if exists
  4. Format output
- Output: Diagnostic information

## Non-Functional Requirements

### NFR-1: Performance

- CLI startup time: < 500ms
- Init command: < 5 seconds for typical project
- Serve command: Server ready within 2 seconds
- Upgrade command: < 10 seconds for full skill sync

### NFR-2: Compatibility

- Python version: 3.10+
- Operating systems: macOS, Linux, Windows
- Package managers: pip, uv, pipx
- Virtual environments: venv, conda, poetry

### NFR-3: Reliability

- Graceful error handling with clear messages
- No data loss: backup before overwrite
- Atomic operations where possible
- Recoverable state after interruption

### NFR-4: Usability

- Colored terminal output for clarity
- Progress indicators for long operations
- Clear error messages with suggested fixes
- Helpful `--help` text for all commands

## Dependencies

### Internal Dependencies

- None (this is the foundation feature)

### External Dependencies

| Dependency | Purpose | Version |
|------------|---------|---------|
| Flask | Web framework | ^3.0.0 |
| Flask-SocketIO | WebSocket support | ^5.3.0 |
| click | CLI framework | ^8.1.0 |
| PyYAML | Config parsing | ^6.0 |
| python-socketio | Socket.IO client | ^5.10.0 |
| watchdog | File watching | ^4.0.0 |

## Business Rules

### BR-1: Non-Destructive Init

**Rule:** `x-ipe init` must never overwrite existing files without `--force` flag

**Example:**
- User has existing `.github/skills/task-type-bug-fix/` → Skip with warning
- User runs `x-ipe init --force` → Overwrite with backup

### BR-2: Backup Before Overwrite

**Rule:** Any destructive operation must create a backup first

**Example:**
- `x-ipe upgrade --force` creates `.x-ipe/backups/skills-20260125-051600/`
- Backup includes all modified files before overwriting

### BR-3: Config Discovery

**Rule:** `.x-ipe.yaml` is optional; CLI works with sensible defaults

**Example:**
- No config: `x-ipe serve` uses port 5000, current directory
- With config: Uses paths defined in config

### BR-4: Git-Aware Initialization

**Rule:** Only modify `.gitignore` if `.git/` folder exists

**Example:**
- Git repo: Adds `.x-ipe/` and `.x-ipe.yaml` to `.gitignore`
- Not git repo: Skips `.gitignore` modification

## Edge Cases & Constraints

### Edge Case 1: Already Initialized Project

**Scenario:** User runs `x-ipe init` in already initialized project  
**Expected Behavior:** Show "Already initialized" message, list existing structure, suggest `--force` to reinitialize

### Edge Case 2: Port Already in Use

**Scenario:** User runs `x-ipe serve` but port 5000 is busy  
**Expected Behavior:** Show error "Port 5000 is in use", suggest `--port` flag

### Edge Case 3: No Write Permission

**Scenario:** User runs `x-ipe init` in directory without write permission  
**Expected Behavior:** Show clear error "Cannot create files: Permission denied"

### Edge Case 4: Interrupted Init

**Scenario:** User Ctrl+C during `x-ipe init`  
**Expected Behavior:** Leave partial state, next `x-ipe init` can continue from where it left off

### Edge Case 5: Corrupted Config File

**Scenario:** `.x-ipe.yaml` has invalid YAML syntax  
**Expected Behavior:** Show parse error with line number, suggest fix or delete

### Edge Case 6: Missing Python Dependencies

**Scenario:** Optional dependency not installed  
**Expected Behavior:** Show which dependency is missing, suggest `pip install x-ipe[all]`

### Edge Case 7: Old X-IPE Version

**Scenario:** User has old X-IPE, config schema has changed  
**Expected Behavior:** Migrate config to new schema, or show migration instructions

### Edge Case 8: Windows Path Issues

**Scenario:** User on Windows with paths containing backslashes  
**Expected Behavior:** Normalize paths, handle both forward and backslashes

## Out of Scope

- GUI installer (CLI only for v1.0)
- Plugin system for custom commands
- Remote project support (local only)
- Docker container packaging
- Cloud deployment integration
- Auto-update mechanism (use pip upgrade)
- Multi-project management (one project at a time)

## Technical Considerations

- Use `click` over `argparse` for better UX and subcommand support
- Use `importlib.resources` (Python 3.9+) for package data access
- Consider `rich` library for colored/formatted terminal output
- Use `pathlib.Path` consistently for cross-platform paths
- Store skill hashes in `.x-ipe/skill-hashes.json` for upgrade detection
- Use `socket.connect()` to check if port is in use

## Open Questions

- [x] Package name on PyPI? → `x-ipe`
- [x] Minimum Python version? → 3.10+
- [x] CLI framework? → click
- [ ] Include `rich` for terminal styling? → TBD during implementation
- [ ] Support `pipx` installation? → Should work out of box

---
