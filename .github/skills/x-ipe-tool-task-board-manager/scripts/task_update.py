#!/usr/bin/env python3
"""Update a task in the task board.

Usage: python3 task_update.py --task-id TASK-001 --updates '{"status": "done"}'
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _board_lib import (
    EXIT_FILE_NOT_FOUND,
    EXIT_VALIDATION_ERROR,
    TASK_SCHEMA_V1,
    VALID_TASK_STATUSES,
    atomic_read_json,
    atomic_write_json,
    exit_with_error,
    normalize_task_status,
    output_result,
    resolve_data_path,
    with_file_lock,
)
from _task_store import index_file, read_daily, read_index

_IMMUTABLE_FIELDS = {"task_id", "created_at"}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update a task in the task board")
    parser.add_argument("--task-id", required=True, help="Task ID to update")
    parser.add_argument("--updates", required=True, help="Update fields as JSON string")
    parser.add_argument("--lock-timeout", type=int, default=10, help="Lock timeout seconds")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    try:
        updates = json.loads(args.updates)
    except json.JSONDecodeError as e:
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_JSON", str(e))

    if not isinstance(updates, dict):
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_UPDATES", "Updates must be a JSON object")

    # Strip auto-managed field
    updates.pop("last_updated", None)

    if not updates:
        exit_with_error(EXIT_VALIDATION_ERROR, "EMPTY_UPDATES", "No update fields provided")

    # Reject immutable fields
    for field in _IMMUTABLE_FIELDS:
        if field in updates:
            exit_with_error(EXIT_VALIDATION_ERROR, "IMMUTABLE_FIELD",
                            f"Cannot update immutable field: {field}")

    # Validate field types against schema before normalizing status
    field_defs = {k: v for k, v in TASK_SCHEMA_V1.items() if not k.startswith("_")}
    for key, value in updates.items():
        if key not in field_defs:
            exit_with_error(EXIT_VALIDATION_ERROR, "UNKNOWN_FIELD", f"Unknown field: {key}")
        expected = field_defs[key]["type"]
        if not isinstance(value, expected):
            exit_with_error(EXIT_VALIDATION_ERROR, "TYPE_ERROR",
                            f"Field '{key}' expected {expected.__name__}, got {type(value).__name__}")

    if "status" in updates:
        updates["status"] = normalize_task_status(updates["status"])
        if updates["status"] not in VALID_TASK_STATUSES:
            exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_STATUS", "Unknown task status")

    tasks_dir = resolve_data_path("tasks")
    index_path = tasks_dir / "tasks-index.json"

    # Read index to find task file
    if not index_path.exists():
        exit_with_error(EXIT_FILE_NOT_FOUND, "INDEX_NOT_FOUND",
                        "Task index not found — no tasks created yet")

    index_data = read_index(tasks_dir)
    entries = index_data["entries"]
    if args.task_id not in entries:
        exit_with_error(EXIT_FILE_NOT_FOUND, "TASK_NOT_FOUND",
                        f"Task {args.task_id} not found in index")

    daily_name = index_file(entries[args.task_id])
    daily_path = tasks_dir / daily_name
    now = datetime.now(timezone.utc).isoformat()

    # Lock daily → lock index (nested) → merge → write both
    with with_file_lock(tasks_dir / f"{daily_name}.lock", timeout=args.lock_timeout):
        result = atomic_read_json(daily_path)
        if not result["success"]:
            exit_with_error(EXIT_FILE_NOT_FOUND, "DAILY_FILE_NOT_FOUND",
                            f"Daily file {daily_name} not found")

        daily_data, daily_tasks = read_daily(daily_path)
        task_idx = None
        for i, t in enumerate(daily_tasks):
            if t.get("task_id") == args.task_id:
                task_idx = i
                break

        if task_idx is None:
            exit_with_error(EXIT_FILE_NOT_FOUND, "TASK_NOT_IN_FILE",
                            f"Task {args.task_id} not found in {daily_name}")

        # Merge updates + auto-set last_updated
        task = daily_tasks[task_idx]
        task.update(updates)
        task["last_updated"] = now

        with with_file_lock(tasks_dir / "tasks-index.json.lock", timeout=args.lock_timeout):
            index_data = read_index(tasks_dir)
            entry = index_data["entries"].get(args.task_id)
            if entry is None or index_file(entry) != daily_name:
                exit_with_error(EXIT_VALIDATION_ERROR, "INCONSISTENT_BOARD", "Task index changed")
            index_data["entries"][args.task_id] = {
                "file": daily_name, "status": task["status"], "last_updated": now,
            }
            atomic_write_json(daily_path, daily_data)
            atomic_write_json(index_path, index_data)

    updated_fields = list(updates.keys()) + ["last_updated"]
    output_result({"success": True, "data": {"task_id": args.task_id, "updated_fields": updated_fields}})


if __name__ == "__main__":
    main()
