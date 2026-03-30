"""Shared KB index utilities for x-ipe-tool-x-ipe-app-interactor scripts.

Provides read_kb_index with format detection (canonical vs legacy flat).
Zero external dependencies — Python stdlib + _lib only.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Resolve _lib from same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import atomic_read_json  # noqa: E402

KB_INDEX_FILE = ".kb-index.json"
KB_INDEX_VERSION = "1.0"


def read_kb_index(folder_path: Path) -> dict:
    """Read .kb-index.json with format detection.

    Returns canonical format: {"version": "1.0", "entries": {...}}
    Handles: missing file, corrupted JSON, legacy flat format.
    """
    index_path = folder_path / KB_INDEX_FILE
    if not index_path.exists():
        return {"version": KB_INDEX_VERSION, "entries": {}}

    data = atomic_read_json(index_path)

    # atomic_read_json returns error dict on parse/read failure
    if data.get("success") is False:
        print(f"WARNING: {data.get('message', 'corrupted index')}", file=sys.stderr)
        return {"version": KB_INDEX_VERSION, "entries": {}}

    if not isinstance(data, dict):
        return {"version": KB_INDEX_VERSION, "entries": {}}

    # Canonical format: has "entries" key
    if "entries" in data:
        return data

    # Legacy flat format: all keys except "version" are entries
    entries = {k: v for k, v in data.items() if k != "version" and isinstance(v, dict)}
    return {"version": data.get("version", KB_INDEX_VERSION), "entries": entries}
