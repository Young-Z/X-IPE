# Playground

Interactive playgrounds for human testing of implemented features.

## How to Run

| Playground | Command |
|------------|---------|
| Interactive Console (FEATURE-005) | `uv run python playground/playground_interactive_console.py` |
| Interactive Console (API Demo) | `uv run python playground/playground_interactive_console.py --demo` |
| Settings & Configuration (FEATURE-006) | `uv run python playground/playground_settings.py` |
| Settings & Configuration (Interactive) | `uv run python playground/playground_settings.py -i` |
| Project Folders (FEATURE-006 v2.0) | `uv run python playground/playground_project_folders.py --demo` |
| Project Folders (Interactive) | `uv run python playground/playground_project_folders.py` |

## Human Simulation Tests

These tests simulate human interaction scenarios to validate the user experience.

| Test | Command |
|------|---------|
| Interactive Console | `uv run python playground/tests/test_playground_interactive_console.py` |
| Settings & Configuration | `uv run python playground/tests/test_playground_settings.py` |
| Project Folders (v2.0) | `uv run python playground/tests/test_playground_project_folders.py` |

## Interactive Console (FEATURE-005)

The Interactive Console playground provides a PTY-based terminal for testing.

### Features
- Real-time shell output with ANSI colors
- Keyboard input handling
- Ctrl+C interrupt signal
- Terminal resize functionality

### Usage

**Interactive Mode:**
```bash
uv run python playground/playground_interactive_console.py
```
- Type commands and press Enter
- Use Ctrl+C to interrupt
- Type 'exit' or Ctrl+D to quit

**API Demo Mode:**
```bash
uv run python playground/playground_interactive_console.py --demo
```
- Non-interactive demonstration of TerminalService API
- Shows spawn, write, resize, and terminate operations

**Custom Directory:**
```bash
uv run python playground/playground_interactive_console.py --dir /path/to/project
```

## Settings & Configuration (FEATURE-006)

The Settings playground demonstrates the SettingsService with SQLite persistence.

### Features
- Get/set configuration values
- Path validation for project_root
- Reset to defaults
- Settings persistence across app restarts

### Usage

**Demo Mode (default):**
```bash
uv run python playground/playground_settings.py
```
- Runs through all settings operations
- Shows basic operations, path validation, reset, and persistence

**Interactive Mode:**
```bash
uv run python playground/playground_settings.py -i
```
- Commands: `get`, `get <key>`, `set <key> <value>`, `reset`, `quit`
- Type `help` for available commands

## Project Folders (FEATURE-006 v2.0)

The Project Folders playground demonstrates multi-project folder management.

### Features
- List all project folders
- Add/update/delete project folders
- Switch active project
- Validation error handling
- Persistence across sessions

### Usage

**Demo Mode:**
```bash
uv run python playground/playground_project_folders.py --demo
```
- Runs through all project folder operations
- Shows list, add, update, delete, switch, and validation demos

**Interactive Mode:**
```bash
uv run python playground/playground_project_folders.py
```
- Menu-driven interface for testing all operations
- Useful for manual exploration
