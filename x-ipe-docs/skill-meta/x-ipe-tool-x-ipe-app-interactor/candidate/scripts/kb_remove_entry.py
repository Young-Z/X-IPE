#!/usr/bin/env python3
"""Remove a metadata entry from a folder's .kb-index.json.

Usage:
    python3 kb_remove_entry.py --name "old-doc.md" --folder "guides"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    atomic_write_json,
    exit_with_error,
    output_result,
    resolve_kb_root,
    resolve_project_root,
    with_file_lock,
    EXIT_VALIDATION_ERROR,
)
from _kb_lib import KB_INDEX_FILE, read_kb_index  # noqa: E402


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Remove KB index entry")
    parser.add_argument("--name", required=True, help="Filename or foldername/")
    parser.add_argument("--folder", default="", help="Relative folder path within KB root")
    parser.add_argument("--format", dest="fmt", default="json", choices=["json", "text"])
    parser.add_argument("--lock-timeout", type=int, default=10, help="Lock timeout seconds")
    args = parser.parse_args(argv)

    # Validate name
    if not args.name or not args.name.strip():
        exit_with_error(EXIT_VALIDATION_ERROR, "INVALID_NAME",
                        "Entry name must not be empty or whitespace-only")

    root = resolve_project_root()
    kb_root = resolve_kb_root(root)
    folder_path = kb_root / args.folder if args.folder else kb_root

    index_path = folder_path / KB_INDEX_FILE

    # If no index file exists, nothing to remove
    if not index_path.exists():
        output_result({
            "success": True,
            "folder": args.folder,
            "name": args.name,
            "removed": False,
        }, fmt=args.fmt)
        return

    lock_path = folder_path / f"{KB_INDEX_FILE}.lock"

    with with_file_lock(lock_path, timeout=args.lock_timeout, cleanup=True):
        index = read_kb_index(folder_path)
        if args.name in index["entries"]:
            del index["entries"][args.name]
            atomic_write_json(index_path, index)
            removed = True
        else:
            removed = False

    output_result({
        "success": True,
        "folder": args.folder,
        "name": args.name,
        "removed": removed,
    }, fmt=args.fmt)


if __name__ == "__main__":
    main()
