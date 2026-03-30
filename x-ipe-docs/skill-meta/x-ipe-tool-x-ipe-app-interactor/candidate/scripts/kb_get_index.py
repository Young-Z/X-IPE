#!/usr/bin/env python3
"""Read all entries from a folder's .kb-index.json metadata registry.

Usage:
    python3 kb_get_index.py --folder "guides" --format json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    exit_with_error,
    output_result,
    resolve_kb_root,
    resolve_project_root,
    EXIT_FILE_NOT_FOUND,
)
from _kb_lib import read_kb_index  # noqa: E402


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Read KB index entries")
    parser.add_argument("--folder", default="", help="Relative folder path within KB root")
    parser.add_argument("--format", dest="fmt", default="json", choices=["json", "text"])
    args = parser.parse_args(argv)

    root = resolve_project_root()
    kb_root = resolve_kb_root(root)
    folder_path = kb_root / args.folder if args.folder else kb_root

    if not folder_path.is_dir():
        exit_with_error(EXIT_FILE_NOT_FOUND, "FOLDER_NOT_FOUND",
                        f"Folder does not exist: {args.folder or '(KB root)'}")

    index = read_kb_index(folder_path)
    output_result({
        "success": True,
        "folder": args.folder,
        "index": index,
    }, fmt=args.fmt)


if __name__ == "__main__":
    main()
