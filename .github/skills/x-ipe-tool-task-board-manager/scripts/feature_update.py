#!/usr/bin/env python3
"""Update a feature in the feature board.

Usage: python3 feature_update.py --feature-id FEATURE-055-A --updates '{"status": "Completed"}'
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
    FEATURE_SCHEMA_V1,
    atomic_read_json,
    atomic_write_json,
    exit_with_error,
    output_result,
    resolve_data_path,
    with_file_lock,
)

VALID_FEATURE_STATUSES = {
    "Planned", "Refined", "Designed", "Implemented",
    "Tested", "Completed", "Retired",
}

_IMMUTABLE_FIELDS = {"feature_id", "epic_id", "created_at"}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update a feature in the feature board")
    parser.add_argument("--feature-id", required=True, help="Feature ID to update")
    parser.add_argument("--updates", required=True, help="Update fields as JSON string")
    parser.add_argument("--lock-timeout", type=int, default=10, help="Lock timeout seconds")
    return parser.parse_args(argv)


def _validate_updates(updates: dict) -> None:
    """Validate updates: reject immutable/unknown fields, check status enum."""
    field_defs = {k: v for k, v in FEATURE_SCHEMA_V1.items() if not k.startswith("_")}

    for field in _IMMUTABLE_FIELDS:
        if field in updates:
            exit_with_error(
                EXIT_VALIDATION_ERROR, "IMMUTABLE_FIELD",
                f"Cannot update immutable field: {field}",
            )

    for key, value in updates.items():
        if key not in field_defs:
            exit_with_error(EXIT_VALIDATION_ERROR, "UNKNOWN_FIELD", f"Unknown field: {key}")
        expected = field_defs[key]["type"]
        if not isinstance(value, expected):
            exit_with_error(
                EXIT_VALIDATION_ERROR, "TYPE_ERROR",
                f"Field '{key}' expected {expected.__name__}, got {type(value).__name__}",
            )

    if "status" in updates and updates["status"] not in VALID_FEATURE_STATUSES:
        exit_with_error(
            EXIT_VALIDATION_ERROR, "INVALID_STATUS",
            f"Invalid status '{updates['status']}'. Must be one of: {sorted(VALID_FEATURE_STATUSES)}",
        )


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

    _validate_updates(updates)

    features_dir = resolve_data_path("features")
    features_path = features_dir / "features.json"

    if not features_path.exists():
        exit_with_error(EXIT_FILE_NOT_FOUND, "FEATURES_NOT_FOUND", "features.json not found — no features created yet")

    now = datetime.now(timezone.utc).isoformat()

    with with_file_lock(features_dir / "features.json.lock", timeout=args.lock_timeout):
        result = atomic_read_json(features_path)
        if not result["success"]:
            exit_with_error(EXIT_FILE_NOT_FOUND, "READ_ERROR", "Failed to read features.json")

        store = result["data"]
        feature_idx = None
        for i, f in enumerate(store.get("features", [])):
            if f.get("feature_id") == args.feature_id:
                feature_idx = i
                break

        if feature_idx is None:
            exit_with_error(
                EXIT_FILE_NOT_FOUND, "NOT_FOUND",
                f"Feature {args.feature_id} not found",
            )

        store["features"][feature_idx].update(updates)
        store["features"][feature_idx]["last_updated"] = now
        atomic_write_json(features_path, store)

    updated_fields = list(updates.keys()) + ["last_updated"]
    output_result({"success": True, "data": {"feature_id": args.feature_id, "updated_fields": updated_fields}})


if __name__ == "__main__":
    main()
