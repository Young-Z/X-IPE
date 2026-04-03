#!/usr/bin/env python3
"""Migrate task-board.md and features.md to JSON format.

Usage:
    python migrate.py --tasks          # Migrate tasks only
    python migrate.py --features       # Migrate features only
    python migrate.py --all            # Migrate both
    python migrate.py --all --dry-run  # Validate without writing

Feature: FEATURE-057-C
Location: .github/skills/x-ipe-tool-task-board-manager/scripts/migrate.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import shared library
sys.path.insert(0, str(Path(__file__).parent))
from _board_lib import (  # noqa: E402
    atomic_read_json,
    atomic_write_json,
    resolve_data_path,
    with_file_lock,
)

# ── Constants ────────────────────────────────────────────────────────

EMOJI_RE = re.compile(
    r"[\U0001F300-\U0001FAFF\U00002702-\U000027B0\U0000FE00-\U0000FE0F"
    r"\U0000200D\U00002640\U00002642\U00002600-\U000026FF\U00002700-\U000027BF"
    r"\U0000231A-\U0000231B\U000023E9-\U000023F3\U000023F8-\U000023FA]+",
    flags=re.UNICODE,
)

STATUS_NORMALIZE: dict[str, str] = {
    "done": "done",
    "completed": "completed",
    "in_progress": "in_progress",
    "in progress": "in_progress",
    "pending": "pending",
    "blocked": "blocked",
    "deferred": "deferred",
    "cancelled": "cancelled",
    "no longer needed": "cancelled",
}

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")


# ── Markdown Parsing ─────────────────────────────────────────────────

def _strip_emoji(text: str) -> str:
    """Remove emoji characters and leading/trailing whitespace."""
    return EMOJI_RE.sub("", text).strip()


def _normalize_status(raw: str) -> str:
    """Normalize status string: strip emoji, lowercase, map to canonical."""
    cleaned = _strip_emoji(raw).lower().strip()
    return STATUS_NORMALIZE.get(cleaned, cleaned)


def _parse_output_links(raw: str) -> list[str]:
    """Extract link URLs from markdown link syntax. Returns list of paths."""
    raw = raw.strip()
    if raw in ("—", "-", "", "N/A"):
        return []
    matches = LINK_RE.findall(raw)
    if matches:
        return [url for _, url in matches]
    # Plain text links (comma or space separated)
    parts = [p.strip() for p in raw.replace(",", " ").split() if p.strip() and p.strip() != "—"]
    return parts


def _parse_spec_link(raw: str) -> str:
    """Extract specification link from markdown link syntax."""
    raw = raw.strip()
    if raw in ("—", "-", "", "N/A"):
        return ""
    match = LINK_RE.search(raw)
    return match.group(2) if match else raw


def _parse_date(raw: str) -> str:
    """Parse date string to ISO format. Handles MM-DD-YYYY and variations."""
    raw = raw.strip()
    if not raw or raw in ("—", "-"):
        return datetime.now(timezone.utc).isoformat()

    # Try MM-DD-YYYY HH:MM:SS
    for fmt in ("%m-%d-%Y %H:%M:%S", "%m-%d-%Y %H:%M", "%m-%d-%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    return datetime.now(timezone.utc).isoformat()


def _parse_table_row(line: str) -> list[str]:
    """Split a markdown table row into cells."""
    cells = line.split("|")
    # Trim leading/trailing empty cells from the split
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [c.strip() for c in cells]


def parse_tasks_md(md_path: Path) -> list[dict]:
    """Parse task-board.md into a list of task dicts."""
    content = md_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    tasks: list[dict] = []

    for line in lines:
        line = line.strip()
        # Skip headers, separators, non-data lines
        if not line.startswith("| TASK-"):
            continue

        cells = _parse_table_row(line)
        if len(cells) < 6:
            continue

        task_id = cells[0].strip()
        task_type = cells[1].strip()
        description = cells[2].strip()

        # Handle different column layouts (8 cols vs 6 cols)
        if len(cells) >= 8:
            role = cells[3].strip()
            status = _normalize_status(cells[4])
            last_updated = _parse_date(cells[5])
            output_links = _parse_output_links(cells[6])
            next_task = cells[7].strip() if cells[7].strip() not in ("—", "-", "") else ""
        elif len(cells) >= 6:
            # Cancelled section: Task ID | Task | Description | Reason | Last Updated | Output Links
            role = cells[3].strip()  # "Reason" field → store in role
            status = "cancelled"
            last_updated = _parse_date(cells[4])
            output_links = _parse_output_links(cells[5])
            next_task = ""
        else:
            continue

        tasks.append({
            "task_id": task_id,
            "task_type": task_type,
            "description": description,
            "role": role,
            "status": status,
            "created_at": last_updated,  # Use last_updated as proxy (no created_at in MD)
            "last_updated": last_updated,
            "output_links": output_links,
            "next_task": next_task,
        })

    return tasks


def parse_features_md(md_path: Path) -> list[dict]:
    """Parse features.md into a list of feature dicts."""
    content = md_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    features: list[dict] = []

    for line in lines:
        line = line.strip()
        if not line.startswith("| FEATURE-"):
            continue

        cells = _parse_table_row(line)
        if len(cells) < 8:
            continue

        # Feature ID | Epic ID | Feature Title | Version | Status | Specification Link | Created | Last Updated
        feature_id = cells[0].strip()
        epic_id = cells[1].strip()
        title = cells[2].strip()
        version = cells[3].strip()
        status = cells[4].strip()
        spec_link = _parse_spec_link(cells[5])
        created_at = _parse_date(cells[6])
        last_updated = _parse_date(cells[7])

        features.append({
            "feature_id": feature_id,
            "epic_id": epic_id,
            "title": title,
            "version": version,
            "status": status,
            "description": "",
            "dependencies": [],
            "specification_link": spec_link,
            "created_at": created_at,
            "last_updated": last_updated,
        })

    return features


# ── Migration Writers ────────────────────────────────────────────────

def _date_from_iso(iso_str: str) -> str:
    """Extract YYYY-MM-DD from an ISO datetime string."""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def write_tasks_json(tasks: list[dict], dry_run: bool = False) -> dict:
    """Write tasks to daily JSON files + index. Returns summary stats."""
    tasks_dir = resolve_data_path("tasks")
    stats = {"total": len(tasks), "files_written": 0, "skipped_duplicates": 0}

    if dry_run:
        # Group by date to show what would happen
        by_date: dict[str, int] = {}
        for t in tasks:
            date_key = _date_from_iso(t["last_updated"])
            by_date[date_key] = by_date.get(date_key, 0) + 1
        stats["daily_breakdown"] = by_date
        return stats

    tasks_dir.mkdir(parents=True, exist_ok=True)

    # Group tasks by date
    by_date_tasks: dict[str, list[dict]] = {}
    for t in tasks:
        date_key = _date_from_iso(t["last_updated"])
        by_date_tasks.setdefault(date_key, []).append(t)

    index_path = tasks_dir / "tasks-index.json"
    lock_path = tasks_dir / "tasks-index.json.lock"

    with with_file_lock(lock_path, timeout=30):
        # Read or create index
        if index_path.exists():
            result = atomic_read_json(index_path)
            index = result["data"] if result["success"] else {"_version": "1.0", "version": "1.0", "entries": {}}
        else:
            index = {"_version": "1.0", "version": "1.0", "entries": {}}

        for date_key, date_tasks in by_date_tasks.items():
            filename = f"tasks-{date_key}.json"
            filepath = tasks_dir / filename
            file_lock = tasks_dir / f"{filename}.lock"

            with with_file_lock(file_lock, timeout=30):
                # Read existing or create new
                if filepath.exists():
                    result = atomic_read_json(filepath)
                    existing = result["data"] if result["success"] else {"_version": "1.0", "tasks": []}
                else:
                    existing = {"_version": "1.0", "tasks": []}

                existing_ids = {t["task_id"] for t in existing["tasks"]}

                for task in date_tasks:
                    if task["task_id"] in existing_ids:
                        stats["skipped_duplicates"] += 1
                        continue
                    existing["tasks"].append(task)
                    index["entries"][task["task_id"]] = filename

                atomic_write_json(filepath, existing)
                stats["files_written"] += 1

        atomic_write_json(index_path, index)

    return stats


def write_features_json(features: list[dict], dry_run: bool = False) -> dict:
    """Write features to features.json. Returns summary stats."""
    features_dir = resolve_data_path("features")
    stats = {"total": len(features), "skipped_duplicates": 0}

    if dry_run:
        epics: dict[str, int] = {}
        for f in features:
            epics[f["epic_id"]] = epics.get(f["epic_id"], 0) + 1
        stats["epic_breakdown"] = epics
        return stats

    features_dir.mkdir(parents=True, exist_ok=True)
    features_path = features_dir / "features.json"
    lock_path = features_dir / "features.json.lock"

    with with_file_lock(lock_path, timeout=30):
        if features_path.exists():
            result = atomic_read_json(features_path)
            existing = result["data"] if result["success"] else {"_version": "1.0", "features": []}
        else:
            existing = {"_version": "1.0", "features": []}

        existing_ids = {f["feature_id"] for f in existing["features"]}

        for feature in features:
            if feature["feature_id"] in existing_ids:
                stats["skipped_duplicates"] += 1
                continue
            existing["features"].append(feature)

        atomic_write_json(features_path, existing)

    return stats


# ── Main ─────────────────────────────────────────────────────────────

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate task-board.md and features.md to JSON")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tasks", action="store_true", help="Migrate tasks only")
    group.add_argument("--features", action="store_true", help="Migrate features only")
    group.add_argument("--all", action="store_true", help="Migrate both tasks and features")
    parser.add_argument("--dry-run", action="store_true", help="Validate and show plan without writing")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    project_root = resolve_data_path("tasks").parent  # x-ipe-docs/planning/tasks → x-ipe-docs/planning

    results: dict = {}

    if args.tasks or args.all:
        task_md = project_root / "task-board.md"
        if not task_md.exists():
            print(f"ERROR: {task_md} not found", file=sys.stderr)
            sys.exit(1)

        tasks = parse_tasks_md(task_md)
        print(f"Parsed {len(tasks)} tasks from task-board.md")

        stats = write_tasks_json(tasks, dry_run=args.dry_run)
        results["tasks"] = stats

        if args.dry_run:
            print(f"  DRY RUN: Would write {len(tasks)} tasks across {len(stats.get('daily_breakdown', {}))} daily files")
        else:
            print(f"  Written: {stats['files_written']} files, {stats['skipped_duplicates']} duplicates skipped")

    if args.features or args.all:
        features_md = project_root / "features.md"
        if not features_md.exists():
            print(f"ERROR: {features_md} not found", file=sys.stderr)
            sys.exit(1)

        features = parse_features_md(features_md)
        print(f"Parsed {len(features)} features from features.md")

        stats = write_features_json(features, dry_run=args.dry_run)
        results["features"] = stats

        if args.dry_run:
            print(f"  DRY RUN: Would write {len(features)} features across {len(stats.get('epic_breakdown', {}))} epics")
        else:
            print(f"  Written: {stats['skipped_duplicates']} duplicates skipped")

    # Output machine-readable results
    print(json.dumps({"success": True, "results": results}, indent=2))


if __name__ == "__main__":
    main()
