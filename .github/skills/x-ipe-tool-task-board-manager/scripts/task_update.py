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
    atomic_read_json,
    atomic_write_json,
    exit_with_error,
    output_result,
    resolve_data_path,
    with_file_lock,
)

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

    # Validate field types against schema
    field_defs = {k: v for k, v in TASK_SCHEMA_V1.items() if not k.startswith("_")}
    for key, value in updates.items():
        if key not in field_defs:
            exit_with_error(EXIT_VALIDATION_ERROR, "UNKNOWN_FIELD", f"Unknown field: {key}")
        expected = field_defs[key]["type"]
        if not isinstance(value, expected):
            exit_with_error(EXIT_VALIDATION_ERROR, "TYPE_ERROR",
                            f"Field '{key}' expected {expected.__name__}, got {type(value).__name__}")

    tasks_dir = resolve_data_path("tasks")
    index_path = tasks_dir / "tasks-index.json"

    # Read index to find task file
    idx_result = atomic_read_json(index_path)
    if not idx_result["success"]:
        exit_with_error(EXIT_FILE_NOT_FOUND, "INDEX_NOT_FOUND",
                        "Task index not found — no tasks created yet")

    index_data = idx_result["data"]
    entries = index_data.get("entries", {})
    if args.task_id not in entries:
        exit_with_error(EXIT_FILE_NOT_FOUND, "TASK_NOT_FOUND",
                        f"Task {args.task_id} not found in index")

    daily_name = entries[args.task_id]["file"]
    daily_path = tasks_dir / daily_name
    now = datetime.now(timezone.utc).isoformat()

    # Lock daily → lock index (nested) → merge → write both
    with with_file_lock(tasks_dir / f"{daily_name}.lock", timeout=args.lock_timeout):
        result = atomic_read_json(daily_path)
        if not result["success"]:
            exit_with_error(EXIT_FILE_NOT_FOUND, "DAILY_FILE_NOT_FOUND",
                            f"Daily file {daily_name} not found")

        daily_data = result["data"]
        task_idx = None
        for i, t in enumerate(daily_data.get("tasks", [])):
            if t.get("task_id") == args.task_id:
                task_idx = i
                break

        if task_idx is None:
            exit_with_error(EXIT_FILE_NOT_FOUND, "TASK_NOT_IN_FILE",
                            f"Task {args.task_id} not found in {daily_name}")

        # Merge updates + auto-set last_updated
        task = daily_data["tasks"][task_idx]
        task.update(updates)
        task["last_updated"] = now

        with with_file_lock(tasks_dir / "tasks-index.json.lock", timeout=args.lock_timeout):
            atomic_write_json(daily_path, daily_data)

            idx_result = atomic_read_json(index_path)
            index_data = idx_result["data"] if idx_result["success"] else index_data
            index_data["entries"][args.task_id]["status"] = task["status"]
            index_data["entries"][args.task_id]["last_updated"] = now
            atomic_write_json(index_path, index_data)

    updated_fields = list(updates.keys()) + ["last_updated"]
    output_result({"success": True, "data": {"task_id": args.task_id, "updated_fields": updated_fields}})


if __name__ == "__main__":
    main()
