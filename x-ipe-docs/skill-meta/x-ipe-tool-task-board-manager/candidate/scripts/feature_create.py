#!/usr/bin/env python3
"""Create a feature in the feature board.

Usage: python3 feature_create.py --feature '{"feature_id": "FEATURE-055-A", ...}'
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _board_lib import (
    EXIT_VALIDATION_ERROR,
    FEATURE_SCHEMA_V1,
    atomic_read_json,
    atomic_write_json,
    exit_with_error,
    output_result,
    resolve_data_path,
    validate_schema,
    with_file_lock,
)

VALID_FEATURE_STATUSES = {
    "Planned", "Refined", "Designed", "Implemented",
    "Tested", "Completed", "Retired",
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a feature in the feature board")
    parser.add_argument("--feature", required=True, help="Feature data as JSON string")
    parser.add_argument("--lock-timeout", type=int, default=10, help="Lock timeout seconds")
    return parser.parse_args(argv)


def _validate_status(status: str) -> None:
    """Validate status against allowed enum; exit on invalid."""
    if status not in VALID_FEATURE_STATUSES:
        exit_with_error(
            EXIT_VALIDATION_ERROR, "INVALID_STATUS",
            f"Invalid status '{status}'. Must be one of: {sorted(VALID_FEATURE_STATUSES)}",
        )


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    try:
        feature = json.loads(args.feature)
    except json.JSONDecodeError as e:
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_JSON", str(e))

    if not isinstance(feature, dict):
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_FEATURE", "Feature must be a JSON object")

    # Strip system-managed fields — caller cannot override
    feature.pop("created_at", None)
    feature.pop("last_updated", None)

    now = datetime.now(timezone.utc).isoformat()
    feature["created_at"] = now
    feature["last_updated"] = now

    validation = validate_schema(feature, FEATURE_SCHEMA_V1)
    if not validation["success"]:
        exit_with_error(EXIT_VALIDATION_ERROR, "SCHEMA_VALIDATION_FAILED", validation["error"])

    _validate_status(feature["status"])

    features_dir = resolve_data_path("features")
    features_dir.mkdir(parents=True, exist_ok=True)
    features_path = features_dir / "features.json"
    feature_id = feature["feature_id"]

    with with_file_lock(features_dir / "features.json.lock", timeout=args.lock_timeout):
        if features_path.exists():
            result = atomic_read_json(features_path)
            store = result["data"] if result["success"] else {"_version": "1.0", "features": []}
        else:
            store = {"_version": "1.0", "features": []}

        # Duplicate check under lock
        for f in store.get("features", []):
            if f.get("feature_id") == feature_id:
                exit_with_error(
                    EXIT_VALIDATION_ERROR, "DUPLICATE_ERROR",
                    f"Feature {feature_id} already exists",
                )

        store["features"].append(feature)
        atomic_write_json(features_path, store)

    output_result({"success": True, "data": {"feature_id": feature_id}})


if __name__ == "__main__":
    main()
