# Refactoring Analysis — TASK-966

## Scope

- **Task ID:** `TASK-966`
- **Scope Level:** `custom`
- **Purpose:** Replace the internal file watching backend from `watchdog` to `watchfiles` while preserving `FileWatcher` behavior and public lifecycle APIs.

## Expanded Scope

- `src/x_ipe/services/file_service.py`
- `pyproject.toml`
- `uv.lock`
- `README.md`
- Validation references:
  - `tests/test_live_refresh.py`
  - `tests/test_navigation.py`

## Quality Evaluation

### Requirements / Feature Alignment

- No feature or requirement delta was required for the watcher contract itself.
- The refactor remains internal to the existing backend file-watching implementation.

### Technical Alignment

- Existing public API to preserve:
  - `FileWatcher.start()`
  - `FileWatcher.stop()`
  - `FileWatcher.is_running`
  - emitted `structure_changed` / `content_changed` socket events
- Risk discovered during analysis:
  - `watchfiles` batches and normalizes filesystem events differently from `watchdog`, especially on macOS where some writes appear as `added`.

### Test Alignment

- Relevant backend watcher coverage already exists in:
  - `tests/test_live_refresh.py`
  - `tests/test_navigation.py` (`-k filewatcher`)
- Baseline unrelated failure before refactor:
  - `tests/test_navigation.py::test_get_structure_returns_five_sections` expects 5 sections but current code returns 6.

### Tracing

- Existing tracing decorators on `FileWatcher` were preserved.

## Refactoring Suggestions

### Goals

1. Preserve external `FileWatcher` behavior while replacing only the watcher engine.
2. Normalize `watchfiles` batch semantics back to the prior action contract (`created`, `modified`, `deleted`).
3. Keep `.gitignore`-aware filtering and relative path emission unchanged.

### Principles

- **KISS:** Replace only the watcher backend, not the surrounding event pipeline.
- **YAGNI:** Avoid introducing new abstractions beyond the watch loop and normalization logic.
- **Backward Compatibility:** Preserve event names, public method names, and debounce behavior expectations.

### Constraints

- No frontend contract changes.
- No unrelated project-structure or sidebar behavior changes.
- Treat unrelated baseline failures separately from watcher refactor validation.
