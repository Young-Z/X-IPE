#!/usr/bin/env python3
"""Create a task in the task board.

Usage: python3 task_create.py --task '{"task_id": "TASK-001", ...}'
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _board_lib import (
    EXIT_VALIDATION_ERROR,
    TASK_SCHEMA_V1,
    atomic_read_json,
    atomic_write_json,
    exit_with_error,
    normalize_task_status,
    output_result,
    resolve_data_path,
    validate_schema,
    with_file_lock,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a task in the task board")
    parser.add_argument("--task", required=True, help="Task data as JSON string")
    parser.add_argument("--lock-timeout", type=int, default=10, help="Lock timeout seconds")
    return parser.parse_args(argv)


def _today_filename() -> str:
    """Return daily filename for today's UTC date."""
    return f"tasks-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"


def _read_index(tasks_dir: Path) -> dict:
    """Read index file, creating it with defaults if missing."""
    index_path = tasks_dir / "tasks-index.json"
    if not index_path.exists():
        initial: dict = {"_version": "1.0", "version": "1.0", "entries": {}}
        atomic_write_json(index_path, initial)
        return initial
    result = atomic_read_json(index_path)
    if result["success"]:
        return result["data"]
    initial = {"_version": "1.0", "version": "1.0", "entries": {}}
    atomic_write_json(index_path, initial)
    return initial


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    try:
        task = json.loads(args.task)
    except json.JSONDecodeError as e:
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_JSON", str(e))

    if not isinstance(task, dict):
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_TASK", "Task must be a JSON object")

    # Strip system-managed fields — caller cannot override
    task.pop("created_at", None)
    task.pop("last_updated", None)

    if "status" in task:
        task["status"] = normalize_task_status(task["status"])

    now = datetime.now(timezone.utc).isoformat()
    task["created_at"] = now
    task["last_updated"] = now

    validation = validate_schema(task, TASK_SCHEMA_V1)
    if not validation["success"]:
        exit_with_error(EXIT_VALIDATION_ERROR, "SCHEMA_VALIDATION_FAILED", validation["error"])

    # Bootstrap tasks directory
    tasks_dir = resolve_data_path("tasks")
    tasks_dir.mkdir(parents=True, exist_ok=True)

    task_id = task["task_id"]

    # Optimistic duplicate check
    index_data = _read_index(tasks_dir)
    if task_id in index_data.get("entries", {}):
        exit_with_error(EXIT_VALIDATION_ERROR, "DUPLICATE_TASK_ID", f"Task {task_id} already exists")

    daily_name = _today_filename()
    daily_path = tasks_dir / daily_name
    index_path = tasks_dir / "tasks-index.json"

    # Lock daily → lock index (nested) → write both atomically
    with with_file_lock(tasks_dir / f"{daily_name}.lock", timeout=args.lock_timeout):
        if daily_path.exists():
            result = atomic_read_json(daily_path)
            daily_data = result["data"] if result["success"] else {"_version": "1.0", "tasks": []}
        else:
            daily_data = {"_version": "1.0", "tasks": []}

        with with_file_lock(tasks_dir / "tasks-index.json.lock", timeout=args.lock_timeout):
            # Definitive duplicate check under lock
            index_data = _read_index(tasks_dir)
            if task_id in index_data.get("entries", {}):
                exit_with_error(EXIT_VALIDATION_ERROR, "DUPLICATE_TASK_ID", f"Task {task_id} already exists")

            daily_data["tasks"].append(task)
            atomic_write_json(daily_path, daily_data)

            index_data["entries"][task_id] = {
                "file": daily_name,
                "status": task["status"],
                "last_updated": now,
            }
            atomic_write_json(index_path, index_data)

    output_result({"success": True, "data": {"task_id": task_id, "file": daily_name}})


if __name__ == "__main__":
    main()
