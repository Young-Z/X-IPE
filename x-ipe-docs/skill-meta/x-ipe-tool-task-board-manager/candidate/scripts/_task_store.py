"""Task registration helpers; all inventory/write callers must hold index lock.

Writers acquire their daily lock BEFORE the index lock. Never take another daily
lock while holding index: it serializes cooperating commits across all dates.
Atomic replace is per file, not a crash-atomic daily/index transaction.
"""
from __future__ import annotations

import re
from pathlib import Path

from _board_lib import (
    EXIT_VALIDATION_ERROR, TASK_SCHEMA_V1, VALID_TASK_STATUSES,
    atomic_read_json, atomic_write_json, exit_with_error,
    normalize_task_status, validate_schema,
)

_DAILY_NAME = re.compile(r"^tasks-\d{4}-\d{2}-\d{2}(?:\.archived)?\.json$")
_NUMERIC_ID = re.compile(r"^TASK-([0-9]+)$")


def prepare_task(task: dict, now: str, *, allow_auto: bool) -> dict:
    """Validate a creation payload without changing the persisted schema."""
    task = dict(task)
    task.pop("created_at", None)
    task.pop("last_updated", None)
    automatic = "task_id" not in task and allow_auto
    if automatic:
        # Placeholder only for schema validation; allocated under index lock.
        task["task_id"] = "TASK-000"
    task["created_at"] = now
    task["last_updated"] = now
    validation = validate_schema(task, TASK_SCHEMA_V1)
    if not validation["success"]:
        exit_with_error(EXIT_VALIDATION_ERROR, "SCHEMA_VALIDATION_FAILED", validation["error"])
    if not task["task_id"].strip():
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_TASK_ID", "task_id must be nonempty")
    task["status"] = normalize_task_status(task["status"])
    if task["status"] not in VALID_TASK_STATUSES:
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_STATUS", "Unknown task status")
    if automatic:
        del task["task_id"]
    return task


def _read_store(path: Path):
    result = atomic_read_json(path)
    if not result["success"]:
        exit_with_error(EXIT_VALIDATION_ERROR, "BOARD_READ_ERROR", result["message"])
    return result["data"]


def read_index(tasks_dir: Path) -> dict:
    """Read without side effects; initialize missing index only on a commit."""
    path = tasks_dir / "tasks-index.json"
    if not path.exists():
        return {"_version": "1.0", "version": "1.0", "entries": {}}
    data = _read_store(path)
    if not isinstance(data, dict) or not isinstance(data.get("entries"), dict):
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_BOARD", "Invalid tasks index")
    return data


def index_file(entry) -> str:
    """Support historical string entries; never follow an escaping index path."""
    filename = entry.get("file") if isinstance(entry, dict) else entry
    if not isinstance(filename, str) or not _DAILY_NAME.fullmatch(filename):
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_BOARD", "Invalid index filename")
    return filename


def read_daily(path: Path):
    """Accept both existing API list files and CRUD object envelopes."""
    data = _read_store(path)
    tasks = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(tasks, list) or any(
        not isinstance(t, dict) or not isinstance(t.get("task_id"), str)
        for t in tasks
    ):
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_BOARD", f"Invalid task file: {path.name}")
    return data, tasks


def inventory(tasks_dir: Path, index: dict) -> tuple[set[str], dict[str, list[tuple[str, dict]]]]:
    """Reserve every indexed, archived and unindexed ID under the index lock."""
    reserved = set(index["entries"])
    records: dict[str, list[tuple[str, dict]]] = {}
    for path in sorted(tasks_dir.glob("tasks-*.json")):
        if not _DAILY_NAME.fullmatch(path.name):
            continue
        _, tasks = read_daily(path)
        for task in tasks:
            tid = task["task_id"]
            reserved.add(tid)
            records.setdefault(tid, []).append((path.name, task))
    return reserved, records


def allocate_id(reserved: set[str]) -> str:
    """Monotonic numeric allocation; explicit nonnumeric IDs remain compatible."""
    numbers = [int(m.group(1)) for tid in reserved if (m := _NUMERIC_ID.fullmatch(tid))]
    return f"TASK-{max(numbers, default=0) + 1:03d}"


def commit_task(tasks_dir: Path, daily_name: str, task: dict, index: dict) -> None:
    """Commit with BOTH daily and index locks already held."""
    path = tasks_dir / daily_name
    if path.exists():
        daily, tasks = read_daily(path)
    else:
        daily = {"_version": "1.0", "tasks": []}
        tasks = daily["tasks"]
    tasks.append(task)
    atomic_write_json(path, daily)
    index["entries"][task["task_id"]] = {
        "file": daily_name, "status": task["status"],
        "last_updated": task["last_updated"],
    }
    atomic_write_json(tasks_dir / "tasks-index.json", index)


def matching_existing(task: dict, index: dict, records: dict) -> tuple[str, dict] | None:
    """Fail closed on collisions, orphan records, archives and foreign context."""
    tid = task["task_id"]
    matches = records.get(tid, [])
    entry = index["entries"].get(tid)
    if not matches and tid not in index["entries"]:
        return None
    if len(matches) != 1:
        exit_with_error(EXIT_VALIDATION_ERROR, "INCONSISTENT_BOARD", f"Expected one record for {tid}")
    filename, existing = matches[0]
    if filename.endswith(".archived.json"):
        exit_with_error(EXIT_VALIDATION_ERROR, "TASK_ARCHIVED", f"Task {tid} is archived")
    entry_file = entry.get("file") if isinstance(entry, dict) else entry
    if entry_file != filename:
        exit_with_error(EXIT_VALIDATION_ERROR, "INCONSISTENT_BOARD", f"Index mismatch for {tid}")
    validation = validate_schema(existing, TASK_SCHEMA_V1)
    if not validation["success"]:
        exit_with_error(EXIT_VALIDATION_ERROR, "INCONSISTENT_BOARD", validation["error"])
    if isinstance(entry, dict):
        # Old filename-only entries remain supported; present commit metadata
        # must agree or this may be an interrupted daily/index update.
        for field in ("status", "last_updated"):
            if field in entry and entry[field] != existing[field]:
                exit_with_error(EXIT_VALIDATION_ERROR, "INCONSISTENT_BOARD",
                                f"Index {field} mismatch for {tid}")
    if existing["role"] != task["role"]:
        exit_with_error(EXIT_VALIDATION_ERROR, "OWNERSHIP_CONFLICT", f"Task {tid} has a different role")
    if any(existing[field] != task[field] for field in ("task_type", "description")):
        exit_with_error(EXIT_VALIDATION_ERROR, "CONTEXT_CONFLICT", f"Task {tid} has a different context")
    return filename, existing
