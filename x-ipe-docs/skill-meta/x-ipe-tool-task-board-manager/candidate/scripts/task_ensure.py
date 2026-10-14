#!/usr/bin/env python3
"""Idempotent supplied-ID registration/resume; no implicit ownership transfer."""
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
from _task_store import commit_task, inventory, matching_existing, prepare_task, read_index
from task_create import _today_filename


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Ensure supplied task ID without duplicating or changing it")
    parser.add_argument("--task", required=True, help="Creation JSON with supplied task_id and exact context")
    parser.add_argument("--lock-timeout", type=int, default=10, help="Lock timeout seconds")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.task)
    except json.JSONDecodeError as exc:
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_JSON", str(exc))
    if not isinstance(payload, dict):
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_TASK", "Task must be a JSON object")
    task = prepare_task(payload, datetime.now(timezone.utc).isoformat(), allow_auto=False)
    if not task["role"].strip():
        exit_with_error(EXIT_VALIDATION_ERROR, "OWNERSHIP_REQUIRED", "Ensure requires a nonempty caller role")
    tasks_dir = resolve_data_path("tasks")
    daily_name = _today_filename()
    with with_file_lock(tasks_dir / f"{daily_name}.lock", timeout=args.lock_timeout):
        with with_file_lock(tasks_dir / "tasks-index.json.lock", timeout=args.lock_timeout):
            index = read_index(tasks_dir)
            _, records = inventory(tasks_dir, index)
            existing = matching_existing(task, index, records)
            if existing is not None:
                filename, current = existing
                result = {"task_id": current["task_id"], "file": filename,
                          "created": False, "task": current}
            else:
                commit_task(tasks_dir, daily_name, task, index)
                result = {"task_id": task["task_id"], "file": daily_name,
                          "created": True, "task": task}
    output_result({"success": True, "data": result})


if __name__ == "__main__":
    main()
