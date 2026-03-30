#!/usr/bin/env python3
"""Read full workflow state — replaces MCP get_workflow_state tool.

Usage:
    python3 workflow_get_state.py --workflow NAME [--format json|text]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (
    EXIT_FILE_NOT_FOUND,
    EXIT_VALIDATION_ERROR,
    atomic_read_json,
    exit_with_error,
    output_result,
    resolve_project_root,
    resolve_workflow_dir,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read full workflow state.",
    )
    parser.add_argument("--workflow", required=True, help="Workflow name")
    parser.add_argument(
        "--format", choices=["json", "text"], default="json", dest="fmt",
        help="Output format (default: json)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    root = resolve_project_root()
    wf_dir = resolve_workflow_dir(root)
    state_path = wf_dir / f"workflow-{args.workflow}.json"

    state = atomic_read_json(state_path)
    if state.get("success") is False:
        code = EXIT_FILE_NOT_FOUND if state["error"] == "FILE_NOT_FOUND" else EXIT_VALIDATION_ERROR
        exit_with_error(code, state["error"], state["message"])

    output_result(state, fmt=args.fmt)


if __name__ == "__main__":
    main()
