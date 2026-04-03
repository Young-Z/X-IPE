"""Board Shared Library — foundation for task and feature board managers.

Provides atomic JSON I/O, POSIX file locking, strict schema validation,
path resolution, and structured output formatting. Python stdlib only.

Location: .github/skills/x-ipe-tool-task-board-manager/scripts/_board_lib.py
Consumers: task CRUD scripts (EPIC-055), feature CRUD scripts (EPIC-056)
"""

from __future__ import annotations

import fcntl
import json
import os
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Exit code constants
# ---------------------------------------------------------------------------

EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_FILE_NOT_FOUND = 2
EXIT_LOCK_TIMEOUT = 3

# ---------------------------------------------------------------------------
# Schema definitions (versioned)
# ---------------------------------------------------------------------------

TASK_SCHEMA_V1: dict[str, Any] = {
    "_version": "1.0",
    "task_id":      {"type": str,  "required": True},
    "task_type":    {"type": str,  "required": True},
    "description":  {"type": str,  "required": True},
    "role":         {"type": str,  "required": True},
    "status":       {"type": str,  "required": True},
    "created_at":   {"type": str,  "required": True},
    "last_updated": {"type": str,  "required": True},
    "output_links": {"type": list, "required": True},
    "next_task":    {"type": str,  "required": True},
}

FEATURE_SCHEMA_V1: dict[str, Any] = {
    "_version": "1.0",
    "feature_id":         {"type": str,  "required": True},
    "epic_id":            {"type": str,  "required": True},
    "title":              {"type": str,  "required": True},
    "version":            {"type": str,  "required": True},
    "status":             {"type": str,  "required": True},
    "description":        {"type": str,  "required": False},
    "dependencies":       {"type": list, "required": True},
    "specification_link": {"type": str,  "required": False},
    "created_at":         {"type": str,  "required": True},
    "last_updated":       {"type": str,  "required": True},
}

INDEX_SCHEMA_V1: dict[str, Any] = {
    "_version": "1.0",
    "version": {"type": str,  "required": True},
    "entries": {"type": dict, "required": True},
}

# ---------------------------------------------------------------------------
# Project root detection
# ---------------------------------------------------------------------------

_PROJECT_ROOT_MARKER = "x-ipe-docs"


def _resolve_project_root() -> Path:
    """Walk up from CWD until a directory containing x-ipe-docs/ is found."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / _PROJECT_ROOT_MARKER).is_dir():
            return parent
    exit_with_error(
        EXIT_FILE_NOT_FOUND,
        "PROJECT_ROOT_NOT_FOUND",
        f"Could not find '{_PROJECT_ROOT_MARKER}/' in any parent of {current}",
    )
    return Path()  # unreachable, satisfies type checker


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_DATA_PATHS: dict[str, str] = {
    "tasks":    "x-ipe-docs/planning/tasks",
    "features": "x-ipe-docs/planning/features",
}


def resolve_data_path(data_type: str) -> Path:
    """Resolve absolute path to board data directory.

    Args:
        data_type: ``"tasks"`` or ``"features"``

    Returns:
        Absolute Path to the data directory.

    Raises:
        ValueError: If *data_type* is not recognised.
    """
    relative = _DATA_PATHS.get(data_type)
    if relative is None:
        raise ValueError(
            f"Unknown data_type '{data_type}'. "
            f"Expected one of: {', '.join(sorted(_DATA_PATHS))}"
        )
    return _resolve_project_root() / relative


# ---------------------------------------------------------------------------
# Structured output helpers
# ---------------------------------------------------------------------------

def output_result(result: dict[str, Any]) -> None:
    """Print structured JSON result to stdout."""
    print(json.dumps(result, ensure_ascii=False))


def exit_with_error(code: int, error: str, message: str) -> None:
    """Print structured JSON error to stderr and exit.

    Args:
        code: Exit code (one of ``EXIT_*`` constants).
        error: Machine-readable error code (e.g. ``"VALIDATION_ERROR"``).
        message: Human-readable description.
    """
    print(
        json.dumps({"success": False, "error": error, "message": message},
                    ensure_ascii=False),
        file=sys.stderr,
    )
    sys.exit(code)


# ---------------------------------------------------------------------------
# Atomic JSON I/O
# ---------------------------------------------------------------------------

def atomic_read_json(path: str | Path) -> dict[str, Any]:
    """Read and parse a JSON file safely.

    Returns a result dict — never raises exceptions to the caller.

    Returns:
        On success: ``{"success": True, "data": <parsed content>}``
        On failure: ``{"success": False, "error": "<CODE>", "message": "..."}``
    """
    path = Path(path)
    if not path.exists():
        return {
            "success": False,
            "error": "FILE_NOT_FOUND",
            "message": f"File not found: {path}",
        }
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "success": False,
            "error": "READ_ERROR",
            "message": f"Cannot read {path}: {exc}",
        }
    if not text.strip():
        return {
            "success": False,
            "error": "JSON_PARSE_ERROR",
            "message": f"File is empty: {path}",
        }
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return {
            "success": False,
            "error": "JSON_PARSE_ERROR",
            "message": f"Invalid JSON in {path}: {exc}",
        }
    return {"success": True, "data": data}


def atomic_write_json(path: str | Path, data: dict | list) -> None:
    """Write data to a JSON file atomically.

    Uses the ``tempfile → fsync → os.replace`` pattern so that concurrent
    readers always see either the old or the new content, never a partial
    write.  Creates parent directories if they do not exist.

    Raises:
        OSError: On unrecoverable I/O errors.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        # Clean up temp file on any error
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# File locking
# ---------------------------------------------------------------------------

class LockTimeout(Exception):
    """Raised when a file lock cannot be acquired within the timeout."""


@contextmanager
def with_file_lock(
    lock_path: str | Path,
    timeout: int = 10,
    cleanup: bool = False,
):
    """Acquire an exclusive POSIX file lock with timeout.

    Args:
        lock_path: Path to lock file (e.g. ``data.json.lock``).
        timeout: Maximum seconds to wait (default 10).
        cleanup: If ``True``, remove the lock file after release.

    Yields:
        Control to the caller's ``with`` block once the lock is held.

    Raises:
        SystemExit(3): If the lock cannot be acquired within *timeout*.
    """
    lock_path = Path(lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    acquired = False
    try:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except BlockingIOError:
                time.sleep(0.1)
        if not acquired:
            os.close(fd)
            exit_with_error(
                EXIT_LOCK_TIMEOUT,
                "LOCK_TIMEOUT",
                f"Could not acquire lock on {lock_path} within {timeout}s",
            )
        yield
    finally:
        if acquired:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            if cleanup:
                try:
                    lock_path.unlink()
                except OSError:
                    pass


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def validate_schema(data: Any, schema: dict[str, Any]) -> dict[str, Any]:
    """Validate a dict against a schema definition.

    The schema maps field names to ``{"type": <type>, "required": <bool>}``.
    Keys starting with ``_`` (e.g. ``_version``) are metadata and are not
    treated as field definitions.

    Strict mode: rejects any field in *data* not defined in the schema.

    Returns:
        ``{"success": True}`` or ``{"success": False, "error": "..."}``
    """
    if not isinstance(data, dict):
        return {
            "success": False,
            "error": f"Expected dict, got {type(data).__name__}",
        }

    # Separate metadata keys from field definitions
    field_defs = {k: v for k, v in schema.items() if not k.startswith("_")}

    # Check required fields
    for field, spec in field_defs.items():
        if spec.get("required") and field not in data:
            return {
                "success": False,
                "error": f"Missing required field: {field}",
            }

    # Check types for present fields
    for field, value in data.items():
        if field in field_defs:
            expected_type = field_defs[field]["type"]
            if not isinstance(value, expected_type):
                return {
                    "success": False,
                    "error": (
                        f"Field '{field}' expected type "
                        f"{expected_type.__name__}, got {type(value).__name__}"
                    ),
                }

    # Strict mode: reject unknown fields
    known_fields = set(field_defs)
    unknown = set(data) - known_fields
    if unknown:
        return {
            "success": False,
            "error": f"Unknown field: {sorted(unknown)[0]}",
        }

    return {"success": True}
