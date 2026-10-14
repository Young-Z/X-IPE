#!/usr/bin/env python3
"""Query features from the feature board.

Usage:
  List:    python3 feature_query.py --status Completed --epic-id EPIC-055
  Single:  python3 feature_query.py --feature-id FEATURE-055-A
  Summary: python3 feature_query.py --epic-summary
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
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
    parser = argparse.ArgumentParser(description="Query features from the feature board")
    parser.add_argument("--feature-id", help="Query single feature by ID")
    parser.add_argument("--epic-summary", action="store_true", help="Show per-epic status summary")
    parser.add_argument("--epic-id", help="Filter by epic ID")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--search", help="Text search across feature fields")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=50)
    parser.add_argument("--lock-timeout", type=int, default=10, help="Lock timeout seconds")
    return parser.parse_args(argv)


def _read_features(features_dir: Path) -> list[dict]:
    """Read all features from features.json. Returns empty list if missing."""
    features_path = features_dir / "features.json"
    if not features_path.exists():
        return []
    result = atomic_read_json(features_path)
    if not result["success"]:
        return []
    return result["data"].get("features", [])


def _matches_filters(
    feature: dict,
    epic_id: str | None,
    status: str | None,
    search: str | None,
) -> bool:
    """Check if feature matches optional filters (AND logic)."""
    if epic_id and feature.get("epic_id") != epic_id:
        return False
    if status and feature.get("status") != status:
        return False
    if search:
        search_lower = search.lower()
        searchable = " ".join(
            str(feature.get(f, "")) for f in ("feature_id", "title", "description", "epic_id")
        )
        if search_lower not in searchable.lower():
            return False
    return True


def _paginate(items: list, page: int, page_size: int) -> dict:
    """Slice items and compute pagination metadata."""
    total = len(items)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    return {
        "features": items[start : start + page_size],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def _query_single(features_dir: Path, feature_id: str) -> None:
    """Query a single feature by ID via linear scan."""
    features = _read_features(features_dir)
    for f in features:
        if f.get("feature_id") == feature_id:
            output_result({"success": True, "data": {"feature": f}})
            return
    exit_with_error(EXIT_FILE_NOT_FOUND, "NOT_FOUND", f"Feature {feature_id} not found")


def _query_list(features_dir: Path, args: argparse.Namespace) -> None:
    """Query features with filters, sorting, and pagination."""
    features = _read_features(features_dir)

    filtered = [
        f for f in features
        if _matches_filters(f, args.epic_id, args.status, args.search)
    ]

    filtered.sort(key=lambda f: f.get("last_updated", ""), reverse=True)
    output_result({"success": True, "data": _paginate(filtered, args.page, args.page_size)})


def _epic_summary(features_dir: Path, epic_id_filter: str | None) -> None:
    """Compute per-epic status summary counts."""
    features = _read_features(features_dir)

    groups: dict[str, list[dict]] = defaultdict(list)
    for f in features:
        groups[f.get("epic_id", "UNKNOWN")].append(f)

    if epic_id_filter:
        groups = {k: v for k, v in groups.items() if k == epic_id_filter}

    summaries = []
    for eid, feats in sorted(groups.items()):
        summary: dict = {"epic_id": eid, "total": len(feats)}
        status_counts: dict[str, int] = defaultdict(int)
        for f in feats:
            status_counts[f.get("status", "Unknown")] += 1
        summary.update(status_counts)
        summaries.append(summary)

    output_result({"success": True, "data": {"summaries": summaries}})


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    features_dir = resolve_data_path("features")

    if args.feature_id:
        _query_single(features_dir, args.feature_id)
    elif args.epic_summary:
        _epic_summary(features_dir, args.epic_id)
    else:
        _query_list(features_dir, args)


if __name__ == "__main__":
    main()
