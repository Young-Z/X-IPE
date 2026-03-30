"""Shared utilities for x-ipe-tool-x-ipe-app-interactor scripts.

Provides atomic JSON I/O, file locking, project root discovery,
workflow template loading, and structured output formatting.
Zero external dependencies — Python stdlib only.
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

# Exit codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_FILE_NOT_FOUND = 2
EXIT_LOCK_TIMEOUT = 3

PROJECT_ROOT_MARKER = "x-ipe-docs"


def resolve_project_root() -> Path:
    """Walk up from CWD until a directory containing x-ipe-docs/ is found."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / PROJECT_ROOT_MARKER).is_dir():
            return parent
    exit_with_error(
        EXIT_FILE_NOT_FOUND,
        "PROJECT_ROOT_NOT_FOUND",
        f"No '{PROJECT_ROOT_MARKER}/' directory found in any parent of {current}",
    )


def resolve_workflow_dir(project_root: Path | None = None) -> Path:
    """Return {project_root}/x-ipe-docs/engineering-workflow/."""
    root = project_root or resolve_project_root()
    return root / "x-ipe-docs" / "engineering-workflow"


def resolve_kb_root(project_root: Path | None = None) -> Path:
    """Return {project_root}/x-ipe-docs/knowledge-base/."""
    root = project_root or resolve_project_root()
    return root / "x-ipe-docs" / "knowledge-base"


def load_workflow_template(project_root: Path) -> dict:
    """Load workflow-template.json from x-ipe-docs/config/.

    Returns empty dict if not found or unparseable.
    """
    config_path = project_root / "x-ipe-docs" / "config" / "workflow-template.json"
    if not config_path.exists():
        exit_with_error(
            EXIT_FILE_NOT_FOUND,
            "FILE_NOT_FOUND",
            f"Workflow template not found: {config_path}",
        )
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        exit_with_error(
            EXIT_VALIDATION_ERROR,
            "JSON_PARSE_ERROR",
            f"Invalid JSON in workflow template: {exc}",
        )


def get_template_tags(template: dict, action: str) -> list[str]:
    """Extract ordered deliverable tag names for an action from template.

    Parses '$output:raw-ideas' -> 'raw-ideas' and
    '$output-folder:ideas-folder' -> 'ideas-folder'.
    """
    for stage in template.get("stages", {}).values():
        if action in stage.get("actions", {}):
            deliverables = stage["actions"][action].get("deliverables", [])
            tags = []
            for tag_str in deliverables:
                if ":" in tag_str:
                    tags.append(tag_str.split(":", 1)[1])
            return tags
    return []


def get_folder_tags(template: dict, action: str) -> set[str]:
    """Return set of tag names that use $output-folder prefix."""
    for stage in template.get("stages", {}).values():
        if action in stage.get("actions", {}):
            deliverables = stage["actions"][action].get("deliverables", [])
            return {
                tag_str.split(":", 1)[1]
                for tag_str in deliverables
                if tag_str.startswith("$output-folder:")
            }
    return set()


def atomic_read_json(path: Path) -> dict:
    """Read and parse JSON file.

    Returns error dict on failure instead of raising.
    """
    if not path.exists():
        return {
            "success": False,
            "error": "FILE_NOT_FOUND",
            "message": f"File not found: {path}",
        }
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "success": False,
            "error": "JSON_PARSE_ERROR",
            "message": f"Invalid JSON in {path}: {exc}",
        }


def atomic_write_json(path: Path, data: dict) -> None:
    """Atomic write: tempfile in same dir -> fsync -> os.replace.

    If process is killed mid-write, original file stays intact.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, str(path))
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


@contextmanager
def with_file_lock(lock_path: Path, timeout: int = 10):
    """Acquire exclusive flock with timeout. Yields on success, exit(3) on timeout."""
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
                f"Could not acquire lock {lock_path} within {timeout}s",
            )
        yield
    finally:
        if acquired:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


def output_result(result: dict, fmt: str = "json") -> None:
    """Print result to stdout in json or text format."""
    if fmt == "json":
        print(json.dumps(result, ensure_ascii=False))
    else:
        if result.get("success") is False:
            print(f"ERROR [{result.get('error', 'UNKNOWN')}]: {result.get('message', '')}")
        elif "data" in result:
            for key, val in result["data"].items():
                print(f"{key}: {val}")
        else:
            for key, val in result.items():
                print(f"{key}: {val}")


def exit_with_error(code: int, error: str, message: str) -> None:
    """Print error JSON to stdout and sys.exit(code)."""
    print(json.dumps({"success": False, "error": error, "message": message}, ensure_ascii=False))
    sys.exit(code)
