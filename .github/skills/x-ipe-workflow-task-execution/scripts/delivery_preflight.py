#!/usr/bin/env python3
"""Read-only delivery capability resolution and byte-drift audit.

Eligibility is not semantic matching, execution authority, or proof of policy
equivalence. This helper never edits configuration, skills, mirrors or boards.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_bytes(root: Path, relative: str) -> bytes:
    parts = relative.split("/")
    if not relative or Path(relative).is_absolute() or any(p in ("", ".", "..") for p in parts):
        raise ValueError(f"Unsafe project-relative path: {relative}")
    path = root
    for part in parts:
        path /= part
        if path.is_symlink():
            raise ValueError(f"Symlink input: {relative}")
    path.resolve(strict=True).relative_to(root)
    return path.read_bytes()


def eligible_tools(section: dict, discovered: list[str]) -> dict:
    """Preserve implementation-route discovery defaults; explicit flags opt in."""
    if not isinstance(section, dict):
        raise ValueError("Tool section must be an object")
    flags = {key: value for key, value in section.items() if not key.startswith("_")}
    if any(type(value) is not bool for value in flags.values()):
        raise ValueError("Tool flags must be literal JSON booleans")
    explicit = bool(flags)
    enabled = sorted(name for name in discovered if not explicit or flags.get(name) is True)
    return {
        "mode": "opt-in" if explicit else "discovery",
        "enabled": enabled,
        "disabled": sorted(set(discovered) - set(enabled)),
        "undiscovered": sorted(set(flags) - set(discovered)),
        "extra_instruction": section.get("_extra_instruction", ""),
    }


def capabilities(root: Path, stage: str, action: str) -> dict:
    config_path = "x-ipe-docs/config/tools.json"
    try:
        raw = file_bytes(root, config_path)
    except FileNotFoundError:
        # A missing file retains the documented implementation discovery default.
        raw = None
    config = {} if raw is None else json.loads(raw)
    section = config
    for key in ("stages", stage, action):
        if not isinstance(section, dict):
            raise ValueError(f"Configuration parent of {key} must be an object")
        section = section.get(key, {})
    catalog = {}
    for path in sorted((root / ".github/skills").glob("x-ipe-tool-implementation-*")):
        relative = f".github/skills/{path.name}/SKILL.md"
        catalog[path.name] = digest(file_bytes(root, relative))
    result = eligible_tools(section, list(catalog))
    result["config_revision"] = None if raw is None else digest(raw)
    result["catalog_revision"] = digest(json.dumps(catalog, sort_keys=True).encode())
    return result


def audit(root: Path, skills: list[str], mirrors: list[str]) -> dict:
    entries = {}
    for name in skills:
        relative = f".github/skills/{name}/SKILL.md"
        data = file_bytes(root, relative)
        copies = {}
        for mirror in mirrors:
            target = f"{mirror}/{name}/SKILL.md"
            try:
                other = file_bytes(root, target)
            except FileNotFoundError:
                copies[mirror] = {"state": "missing"}
            else:
                copies[mirror] = {
                    "state": "same" if data == other else "different",
                    "sha256": digest(other),
                }
        entries[name] = {
            "sha256": digest(data), "bytes": len(data),
            "lines": len(data.splitlines()), "mirrors": copies,
        }
    instructions = {}
    canonical = file_bytes(root, ".github/copilot-instructions.md")
    for name in ("AGENTS.md", "Agents.md", "CLAUDE.md"):
        try:
            data = file_bytes(root, name)
        except FileNotFoundError:
            instructions[name] = {"state": "missing"}
        else:
            instructions[name] = {
                "state": "same" if data == canonical else "different",
                "sha256": digest(data),
            }
    return {
        "skills": entries, "instructions": instructions,
        "instruction_sha256": digest(canonical),
        "entry_bytes": sum(item["bytes"] for item in entries.values()),
        "entry_lines": sum(item["lines"] for item in entries.values()),
        "limits": "Byte comparison only, not semantic policy equivalence, tokens or latency.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    operations = parser.add_subparsers(dest="operation", required=True)
    routing = operations.add_parser("capabilities")
    routing.add_argument("--stage", required=True)
    routing.add_argument("--action", required=True)
    drift = operations.add_parser("audit")
    drift.add_argument("--skill", action="append", required=True)
    drift.add_argument("--mirror", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        if args.project_root.is_symlink():
            raise ValueError("Project root cannot be a symlink")
        root = args.project_root.resolve(strict=True)
        result = (capabilities(root, args.stage, args.action)
                  if args.operation == "capabilities"
                  else audit(root, args.skill, args.mirror))
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
