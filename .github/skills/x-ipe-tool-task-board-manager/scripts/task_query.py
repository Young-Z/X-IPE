#!/usr/bin/env python3
"""Query tasks from the task board.

Usage:
  Single: python3 task_query.py --task-id TASK-001
  List:   python3 task_query.py --range 1w --status done --page 1
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _board_lib import (
    EXIT_FILE_NOT_FOUND,
    atomic_read_json,
    exit_with_error,
    output_result,
    resolve_data_path,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query tasks from the task board")
    parser.add_argument("--task-id", help="Query single task by ID")
    parser.add_argument("--range", dest="range_str", default="1w", choices=["1w", "1m", "all"])
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--search", help="Text search across task fields")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=50)
    return parser.parse_args(argv)


def _files_in_range(tasks_dir: Path, range_str: str) -> list[Path]:
    """List non-archived daily files within date range, sorted by date desc."""
    today = datetime.now(timezone.utc).date()
    cutoffs = {"1w": today - timedelta(days=7), "1m": today - timedelta(days=30), "all": None}
    cutoff = cutoffs.get(range_str)

    result = []
    for f in sorted(tasks_dir.glob("tasks-*.json"), reverse=True):
        if f.name.endswith(".archived.json"):
            continue
        date_str = f.stem.replace("tasks-", "")
        try:
            file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if cutoff is None or file_date >= cutoff:
            result.append(f)
    return result


def _matches_filters(task: dict, status: str | None, search: str | None) -> bool:
    """Check if task matches optional status and search filters."""
    if status and task.get("status") != status:
        return False
    if search:
        search_lower = search.lower()
        searchable = " ".join(
            str(task.get(f, "")) for f in ("task_id", "task_type", "description", "role")
        )
        if search_lower not in searchable.lower():
            return False
    return True


def _paginate(tasks: list, page: int, page_size: int) -> dict:
    """Slice tasks and compute pagination metadata."""
    total = len(tasks)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    return {
        "tasks": tasks[start : start + page_size],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def _query_single(tasks_dir: Path, task_id: str) -> None:
    """Query a single task by ID via index lookup."""
    result = atomic_read_json(tasks_dir / "tasks-index.json")
    if not result["success"]:
        exit_with_error(EXIT_FILE_NOT_FOUND, "INDEX_NOT_FOUND", "Task index not found")

    entries = result["data"].get("entries", {})
    if task_id not in entries:
        exit_with_error(EXIT_FILE_NOT_FOUND, "TASK_NOT_FOUND", f"Task {task_id} not found")

    daily_name = entries[task_id]["file"]
    daily_result = atomic_read_json(tasks_dir / daily_name)
    if not daily_result["success"]:
        exit_with_error(EXIT_FILE_NOT_FOUND, "DAILY_FILE_NOT_FOUND", f"File {daily_name} not found")

    for task in daily_result["data"].get("tasks", []):
        if task.get("task_id") == task_id:
            output_result({"success": True, "data": {"task": task}})
            return

    exit_with_error(EXIT_FILE_NOT_FOUND, "TASK_NOT_IN_FILE",
                    f"Task {task_id} not found in {daily_name}")


def _query_list(tasks_dir: Path, args: argparse.Namespace) -> None:
    """Query tasks with filters, sorting, and pagination."""
    files = _files_in_range(tasks_dir, args.range_str)

    all_tasks: list[dict] = []
    for f in files:
        result = atomic_read_json(f)
        if result["success"]:
            for task in result["data"].get("tasks", []):
                if _matches_filters(task, args.status, args.search):
                    all_tasks.append(task)

    all_tasks.sort(key=lambda t: t.get("last_updated", ""), reverse=True)
    output_result({"success": True, "data": _paginate(all_tasks, args.page, args.page_size)})


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    tasks_dir = resolve_data_path("tasks")

    if not tasks_dir.exists():
        if args.task_id:
            exit_with_error(EXIT_FILE_NOT_FOUND, "NO_TASKS_DIR", "No tasks directory found")
        output_result({"success": True, "data": _paginate([], args.page, args.page_size)})
        return

    if args.task_id:
        _query_single(tasks_dir, args.task_id)
    else:
        _query_list(tasks_dir, args)


if __name__ == "__main__":
    main()
