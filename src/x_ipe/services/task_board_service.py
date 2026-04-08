"""Task Board Service — read-only query layer over task JSON data.

Provides list_tasks (filtered, paginated) and get_task (by ID).
Reads daily JSON files written by task CRUD scripts (FEATURE-055-B).

Location: src/x_ipe/services/task_board_service.py
Consumer: task_board_routes.py (FEATURE-055-C)
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_VALID_RANGES = {"1w", "1m", "all"}
_SEARCH_FIELDS = ("task_id", "task_type", "description", "role")
_DATE_PATTERN = re.compile(r"^tasks-(\d{4}-\d{2}-\d{2})\.json$")

_TASK_STATUS_ALIASES: dict[str, str] = {
    "done": "completed",
    "complete": "completed",
}


class TaskBoardService:
    """Read-only service for querying task board data."""

    def __init__(self, project_root: str) -> None:
        self.tasks_dir = Path(project_root) / "x-ipe-docs" / "planning" / "tasks"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_tasks(
        self,
        range_str: str = "1w",
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Return filtered, sorted, paginated task list."""
        files = self._files_in_range(range_str)
        all_tasks = self._read_all_tasks(files)

        filtered = [t for t in all_tasks if self._matches_filters(t, status, search)]
        filtered.sort(key=lambda t: t.get("last_updated", ""), reverse=True)

        return {"success": True, "data": self._paginate(filtered, page, page_size)}

    def get_task(self, task_id: str) -> dict[str, Any]:
        """Look up a single task by ID via index, with fallback scan."""
        index_path = self.tasks_dir / "tasks-index.json"
        index_data = self._read_json(index_path)

        if index_data is not None:
            entries = index_data.get("entries", {})
            entry = entries.get(task_id)
            if entry:
                file_path = self.tasks_dir / entry["file"]
                tasks = self._read_json(file_path)
                if isinstance(tasks, list):
                    for task in tasks:
                        if task.get("task_id") == task_id:
                            return {"success": True, "data": task}

        # Fallback: scan daily files if index missing or stale
        for fp in sorted(self.tasks_dir.glob("tasks-*.json"), reverse=True):
            if fp.name.endswith(".archived.json") or not _DATE_PATTERN.match(fp.name):
                continue
            tasks = self._read_json(fp)
            if isinstance(tasks, list):
                for task in tasks:
                    if task.get("task_id") == task_id:
                        return {"success": True, "data": task}

        return {
            "success": False,
            "error": "NOT_FOUND",
            "message": f"Task '{task_id}' not found",
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _files_in_range(self, range_str: str) -> list[Path]:
        """Return daily JSON files within the requested date range."""
        if not self.tasks_dir.is_dir():
            return []

        today = datetime.now(timezone.utc).date()
        cutoff = None
        if range_str == "1w":
            cutoff = today - timedelta(days=7)
        elif range_str == "1m":
            cutoff = today - timedelta(days=30)

        result: list[Path] = []
        for fp in self.tasks_dir.iterdir():
            m = _DATE_PATTERN.match(fp.name)
            if not m:
                continue
            if cutoff is not None:
                try:
                    file_date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                except ValueError:
                    continue
                if file_date < cutoff:
                    continue
            result.append(fp)
        return result

    def _read_all_tasks(self, files: list[Path]) -> list[dict]:
        """Read and merge tasks from multiple daily files."""
        all_tasks: list[dict] = []
        for fp in files:
            data = self._read_json(fp)
            if isinstance(data, list):
                all_tasks.extend(data)
            elif isinstance(data, dict) and isinstance(data.get("tasks"), list):
                all_tasks.extend(data["tasks"])
            else:
                logger.warning("Skipping malformed task file: %s", fp.name)
        return all_tasks

    @staticmethod
    def _matches_filters(
        task: dict, status: str | None, search: str | None
    ) -> bool:
        """Return True if task passes status and search filters."""
        if status:
            norm_filter = _TASK_STATUS_ALIASES.get(status, status)
            norm_task = _TASK_STATUS_ALIASES.get(task.get("status", ""), task.get("status", ""))
            if norm_task != norm_filter:
                return False
        if search:
            searchable = " ".join(
                str(task.get(f, "")) for f in _SEARCH_FIELDS
            ).lower()
            if search.lower() not in searchable:
                return False
        return True

    @staticmethod
    def _paginate(tasks: list[dict], page: int, page_size: int) -> dict:
        """Slice task list and return with pagination metadata."""
        total = len(tasks)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        return {
            "tasks": tasks[start : start + page_size],
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            },
        }

    @staticmethod
    def _read_json(path: Path) -> Any | None:
        """Read and parse a JSON file, returning None on any error."""
        try:
            with open(path) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError, TypeError):
            return None
