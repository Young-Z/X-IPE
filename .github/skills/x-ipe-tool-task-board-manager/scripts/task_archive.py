#!/usr/bin/env python3
"""Archive a daily task file.

Usage: python3 task_archive.py --date 2026-03-01
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _board_lib import (
    EXIT_FILE_NOT_FOUND,
    EXIT_VALIDATION_ERROR,
    atomic_read_json,
    atomic_write_json,
    exit_with_error,
    output_result,
    resolve_data_path,
    with_file_lock,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive a daily task file")
    parser.add_argument("--date", required=True, help="Date to archive (YYYY-MM-DD)")
    parser.add_argument("--lock-timeout", type=int, default=10, help="Lock timeout seconds")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_DATE",
                        f"Invalid date format: {args.date}. Expected YYYY-MM-DD")

    tasks_dir = resolve_data_path("tasks")
    daily_name = f"tasks-{args.date}.json"
    daily_path = tasks_dir / daily_name
    archived_path = tasks_dir / f"tasks-{args.date}.archived.json"

    if not daily_path.exists():
        exit_with_error(EXIT_FILE_NOT_FOUND, "FILE_NOT_FOUND",
                        f"Daily file {daily_name} not found")

    if archived_path.exists():
        exit_with_error(EXIT_VALIDATION_ERROR, "ALREADY_ARCHIVED",
                        f"File {daily_name} is already archived")

    index_path = tasks_dir / "tasks-index.json"

    # Lock daily → lock index (nested) → rename + update index
    with with_file_lock(tasks_dir / f"{daily_name}.lock", timeout=args.lock_timeout):
        result = atomic_read_json(daily_path)
        if not result["success"]:
            exit_with_error(EXIT_FILE_NOT_FOUND, "READ_ERROR",
                            f"Cannot read {daily_name}")

        task_ids = [t["task_id"] for t in result["data"].get("tasks", []) if "task_id" in t]

        with with_file_lock(tasks_dir / "tasks-index.json.lock", timeout=args.lock_timeout):
            os.rename(daily_path, archived_path)

            removed_count = 0
            idx_result = atomic_read_json(index_path)
            if idx_result["success"]:
                index_data = idx_result["data"]
                entries = index_data.get("entries", {})
                for tid in task_ids:
                    if tid in entries:
                        del entries[tid]
                        removed_count += 1
                atomic_write_json(index_path, index_data)

    output_result({
        "success": True,
        "data": {
            "archived_file": f"tasks-{args.date}.archived.json",
            "tasks_removed": removed_count,
            "task_ids": task_ids,
        },
    })


if __name__ == "__main__":
    main()
