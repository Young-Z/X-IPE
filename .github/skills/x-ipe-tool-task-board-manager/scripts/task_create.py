#!/usr/bin/env python3
"""Create a task using --task JSON; omitted task_id allocates under index lock."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _board_lib import (
    EXIT_VALIDATION_ERROR, exit_with_error, output_result,
    resolve_data_path, with_file_lock,
)
from _task_store import allocate_id, commit_task, inventory, prepare_task, read_index


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a task in the task board")
    parser.add_argument("--task", required=True, help="Task JSON; task_id is optional")
    parser.add_argument("--lock-timeout", type=int, default=10, help="Lock timeout seconds")
    return parser.parse_args(argv)


def _today_filename() -> str:
    """Return daily filename for today's UTC date."""
    return f"tasks-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    try:
        payload = json.loads(args.task)
    except json.JSONDecodeError as exc:
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_JSON", str(exc))
    if not isinstance(payload, dict):
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_TASK", "Task must be a JSON object")
    task = prepare_task(payload, datetime.now(timezone.utc).isoformat(), allow_auto=True)
    tasks_dir = resolve_data_path("tasks")
    daily_name = _today_filename()

    # No index reads/writes before lock; keep existing daily → index order.
    with with_file_lock(tasks_dir / f"{daily_name}.lock", timeout=args.lock_timeout):
        with with_file_lock(tasks_dir / "tasks-index.json.lock", timeout=args.lock_timeout):
            index = read_index(tasks_dir)
            reserved, _ = inventory(tasks_dir, index)
            if "task_id" not in task:
                task["task_id"] = allocate_id(reserved)
            elif task["task_id"] in reserved:
                exit_with_error(EXIT_VALIDATION_ERROR, "DUPLICATE_TASK_ID",
                                f"Task {task['task_id']} already exists")
            commit_task(tasks_dir, daily_name, task, index)

    output_result({"success": True, "data": {"task_id": task["task_id"], "file": daily_name}})


if __name__ == "__main__":
    main()
