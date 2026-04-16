#!/usr/bin/env python3
"""Bootstrap the memory folder structure under x-ipe-docs/memory/.

Idempotent — creates only missing directories and seed files.
Never overwrites existing content.

Usage:
    python3 init_memory.py [--memory-dir PATH]

Output:
    JSON to stdout: {"success": true, "created": [...], "skipped": [...]}
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MEMORY_TIERS = ["episodic", "semantic", "procedural"]

DIRECTORIES = [
    ".working/overview",
    ".working/extracted",
    ".ontology/schema",
    ".ontology/instances",
    ".ontology/vocabulary",
    *MEMORY_TIERS,
]

SEED_FILES: dict[str, str] = {
    ".ontology/schema/class-registry.jsonl": "",
    ".ontology/instances/_index.json": "{}",
    ".ontology/instances/_relations.001.jsonl": "",
    ".ontology/vocabulary/_index.json": "{}",
}


def bootstrap(memory_dir: Path) -> dict:
    """Create missing folders and seed files. Return result dict."""
    created: list[str] = []
    skipped: list[str] = []

    for rel_dir in DIRECTORIES:
        target = memory_dir / rel_dir
        if target.is_dir():
            skipped.append(str(rel_dir) + "/")
        else:
            target.mkdir(parents=True, exist_ok=True)
            created.append(str(rel_dir) + "/")

    for rel_path, content in SEED_FILES.items():
        target = memory_dir / rel_path
        if target.exists():
            skipped.append(str(rel_path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            created.append(str(rel_path))

    return {"success": True, "created": created, "skipped": skipped}


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap memory folder structure")
    parser.add_argument(
        "--memory-dir",
        default="x-ipe-docs/memory",
        help="Root directory for memory (default: x-ipe-docs/memory)",
    )
    args = parser.parse_args()

    memory_dir = Path(args.memory_dir)
    try:
        result = bootstrap(memory_dir)
        print(json.dumps(result, ensure_ascii=False))
    except OSError as exc:
        print(
            json.dumps({"success": False, "error": "BOOTSTRAP_FAILED", "message": str(exc)}),
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
