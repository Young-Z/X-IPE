#!/usr/bin/env python3
"""Memory entry CRUD: create, read, update, delete, list, promote.

JSON to stdout on success; JSON to stderr + exit 1 on error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from init_memory import MEMORY_TIERS, bootstrap

TYPE_PREFIX = {"episodic": "epi", "semantic": "sem", "procedural": "proc"}
FRONTMATTER_SEP = "---"


def _exit_error(error: str, message: str) -> None:
    print(json.dumps({"success": False, "error": error, "message": message}), file=sys.stderr)
    sys.exit(1)


def _ok(data: dict) -> None:
    print(json.dumps({"success": True, **data}, ensure_ascii=False))


def _slugify(title: str, max_len: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)[:max_len].rstrip("-")


def _ensure_dirs(memory_dir: Path) -> None:
    if not (memory_dir / "episodic").is_dir():
        bootstrap(memory_dir)

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _next_sequence(memory_dir: Path, memory_type: str, prefix: str, date_str: str) -> str:
    """Find next available 3-digit sequence for given prefix+date."""
    tier_dir = memory_dir / memory_type
    if not tier_dir.is_dir():
        return "001"
    pattern = f"{prefix}-{date_str}-"
    max_seq = 0
    for md_file in tier_dir.glob("*.md"):
        fm = _read_frontmatter(md_file)
        entry_id = fm.get("memory_entry_id", "")
        if entry_id.startswith(pattern):
            try:
                seq = int(entry_id[len(pattern):])
                max_seq = max(max_seq, seq)
            except ValueError:
                pass
    return f"{max_seq + 1:03d}"


def _read_frontmatter(filepath: Path) -> dict:
    """Parse YAML-like frontmatter from a markdown file."""
    text = filepath.read_text(encoding="utf-8")
    if not text.startswith(FRONTMATTER_SEP):
        return {}
    parts = text.split(FRONTMATTER_SEP, 2)
    if len(parts) < 3:
        return {}
    result: dict = {}
    current_key, indent_lines = "", []
    def _flush():
        nonlocal current_key, indent_lines
        if current_key and indent_lines:
            sub = {}
            for l in indent_lines:
                k, _, v = l.strip().partition(":")
                sub[k.strip()] = v.strip().strip('"').strip("'")
            result[current_key] = sub
        current_key, indent_lines = "", []
    for line in parts[1].strip().splitlines():
        if line.startswith("  ") and current_key:
            indent_lines.append(line); continue
        _flush()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not value:
            current_key = key; continue
        if value.startswith("[") and value.endswith("]"):
            result[key] = [i.strip().strip('"').strip("'") for i in value[1:-1].split(",") if i.strip()]
        elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            result[key] = value[1:-1]
        else:
            result[key] = value
    _flush()
    return result


def _read_body(filepath: Path) -> str:
    text = filepath.read_text(encoding="utf-8")
    if not text.startswith(FRONTMATTER_SEP):
        return text
    parts = text.split(FRONTMATTER_SEP, 2)
    return parts[2].lstrip("\n") if len(parts) >= 3 else ""

def _build_frontmatter(entry_id: str, title: str, memory_type: str,
                        tags: list, metadata: dict, created: str, updated: str) -> str:
    lines = [FRONTMATTER_SEP, f"memory_entry_id: {entry_id}", f'title: "{title}"',
             f"memory_type: {memory_type}", f"tags: {json.dumps(tags, ensure_ascii=False)}"]
    if metadata:
        lines.append("metadata:")
        lines.extend(f'  {k}: "{v}"' for k, v in metadata.items())
    lines += [f'created: "{created}"', f'updated: "{updated}"', FRONTMATTER_SEP]
    return "\n".join(lines) + "\n"

def _resolve_slug(memory_dir: Path, memory_type: str, slug: str) -> Path:
    tier_dir = memory_dir / memory_type
    candidate = tier_dir / f"{slug}.md"
    if not candidate.exists():
        return candidate
    counter = 2
    while (tier_dir / f"{slug}-{counter}.md").exists():
        counter += 1
    return tier_dir / f"{slug}-{counter}.md"


def _find_by_id(memory_dir: Path, entry_id: str) -> Path | None:
    for tier in MEMORY_TIERS:
        tier_dir = memory_dir / tier
        if not tier_dir.is_dir():
            continue
        for md_file in tier_dir.glob("*.md"):
            if _read_frontmatter(md_file).get("memory_entry_id") == entry_id:
                return md_file
    return None


def _validate_type(memory_type: str) -> None:
    if memory_type not in MEMORY_TIERS:
        _exit_error("INVALID_MEMORY_TYPE",
                     f"'{memory_type}' is not valid. Must be one of: {', '.join(MEMORY_TIERS)}")

def _resolve_file(memory_dir: Path, args) -> Path:
    if getattr(args, "path", None):
        fp = Path(args.path)
        return fp if fp.is_absolute() else memory_dir / args.path
    if getattr(args, "id", None):
        fp = _find_by_id(memory_dir, args.id)
        if fp is None:
            _exit_error("NOT_FOUND", f"No entry found with id '{args.id}'")
        return fp
    _exit_error("INPUT_VALIDATION_FAILED", "Either --id or --path is required")


def cmd_create(args: argparse.Namespace) -> None:
    memory_dir = Path(args.memory_dir)
    _ensure_dirs(memory_dir)
    _validate_type(args.type)

    if not args.title or not args.title.strip():
        _exit_error("INPUT_VALIDATION_FAILED", "'title' is required and must be non-empty")

    if args.content_file:
        cp = Path(args.content_file)
        if not cp.exists():
            _exit_error("PATH_NOT_FOUND", f"Content file not found: {cp}")
        content = cp.read_text(encoding="utf-8")
    elif args.content:
        content = args.content
    else:
        _exit_error("INPUT_VALIDATION_FAILED", "'content' is required for create operation")
    if not content.strip():
        _exit_error("INPUT_VALIDATION_FAILED", "'content' must be non-empty")

    tags = json.loads(args.tags) if args.tags else []
    metadata = json.loads(args.metadata) if args.metadata else {}
    prefix = TYPE_PREFIX[args.type]
    date_str = _today()
    entry_id = f"{prefix}-{date_str}-{_next_sequence(memory_dir, args.type, prefix, date_str)}"
    filepath = _resolve_slug(memory_dir, args.type, _slugify(args.title))

    now = _now_iso()
    fm = _build_frontmatter(entry_id, args.title, args.type, tags, metadata, now, now)
    filepath.write_text(fm + "\n" + content, encoding="utf-8")
    _ok({"stored_path": str(filepath), "memory_entry_id": entry_id,
         "writes_to": f"{memory_dir / args.type}/"})


def cmd_read(args: argparse.Namespace) -> None:
    memory_dir = Path(args.memory_dir)
    filepath = _resolve_file(memory_dir, args)
    if not filepath.exists():
        _exit_error("PATH_NOT_FOUND", f"File not found: {filepath}")
    _ok({"path": str(filepath), "frontmatter": _read_frontmatter(filepath),
         "content": _read_body(filepath)})


def cmd_update(args: argparse.Namespace) -> None:
    memory_dir = Path(args.memory_dir)
    filepath = _find_by_id(memory_dir, args.id)
    if filepath is None:
        _exit_error("NOT_FOUND", f"No entry found with id '{args.id}'")
    fm, body = _read_frontmatter(filepath), _read_body(filepath)
    if args.content_file:
        cp = Path(args.content_file)
        if not cp.exists():
            _exit_error("PATH_NOT_FOUND", f"Content file not found: {cp}")
        body = cp.read_text(encoding="utf-8")
    if args.metadata:
        existing = fm.get("metadata", {})
        fm["metadata"] = {**(existing if isinstance(existing, dict) else {}), **json.loads(args.metadata)}
    updated = _now_iso()
    tags = fm.get("tags", [])
    metadata = fm.get("metadata", {})
    new_fm = _build_frontmatter(
        fm.get("memory_entry_id", args.id), fm.get("title", ""), fm.get("memory_type", ""),
        tags if isinstance(tags, list) else [],
        metadata if isinstance(metadata, dict) else {},
        fm.get("created", updated), updated)
    filepath.write_text(new_fm + "\n" + body, encoding="utf-8")
    _ok({"path": str(filepath), "updated": updated})


def cmd_delete(args: argparse.Namespace) -> None:
    memory_dir = Path(args.memory_dir)
    filepath = _resolve_file(memory_dir, args)
    if not filepath.exists():
        _exit_error("PATH_NOT_FOUND", f"File not found: {filepath}")
    filepath.unlink()
    _ok({"deleted": str(filepath)})


def cmd_list(args: argparse.Namespace) -> None:
    memory_dir = Path(args.memory_dir)
    _validate_type(args.type)
    tier_dir = memory_dir / args.type
    if not tier_dir.is_dir():
        _ok({"entries": [], "count": 0}); return
    filter_tags = {t.strip() for t in args.tags.split(",")} if args.tags else set()
    entries = []
    for md_file in sorted(tier_dir.glob("*.md")):
        fm = _read_frontmatter(md_file)
        if filter_tags and not filter_tags.intersection(set(fm.get("tags", []))):
            continue
        entries.append({"path": str(md_file), "memory_entry_id": fm.get("memory_entry_id", ""),
                        "title": fm.get("title", ""), "tags": fm.get("tags", []),
                        "created": fm.get("created", ""), "updated": fm.get("updated", "")})
    _ok({"entries": entries, "count": len(entries)})


def cmd_promote(args: argparse.Namespace) -> None:
    memory_dir = Path(args.memory_dir)
    _ensure_dirs(memory_dir)
    _validate_type(args.type)

    working_dir = memory_dir / ".working"
    source = working_dir / args.path
    if not source.exists():
        _exit_error("PATH_NOT_FOUND", f"'{source}' does not exist")
    if not str(source.resolve()).startswith(str(working_dir.resolve())):
        _exit_error("INVALID_PATH", "Path must be within .working/ directory")
    if not args.title or not args.title.strip():
        _exit_error("INPUT_VALIDATION_FAILED", "'title' is required and must be non-empty")

    metadata = json.loads(args.metadata) if args.metadata else {}
    dest = _resolve_slug(memory_dir, args.type, _slugify(args.title))
    existing_fm = _read_frontmatter(source)
    body = _read_body(source) if existing_fm else source.read_text(encoding="utf-8")

    prefix = TYPE_PREFIX[args.type]
    date_str = _today()
    entry_id = f"{prefix}-{date_str}-{_next_sequence(memory_dir, args.type, prefix, date_str)}"
    old_meta = existing_fm.get("metadata", {})
    merged_meta = {**(old_meta if isinstance(old_meta, dict) else {}), **metadata}
    tags = existing_fm.get("tags", [])

    now = _now_iso()
    fm = _build_frontmatter(entry_id, args.title, args.type,
                             tags if isinstance(tags, list) else [],
                             merged_meta, existing_fm.get("created", now), now)
    dest.write_text(fm + "\n" + body, encoding="utf-8")
    source.unlink()
    _ok({"promoted_path": str(dest), "memory_entry_id": entry_id,
         "writes_to": f"{memory_dir / args.type}/"})


def _add_common(p):
    p.add_argument("--memory-dir", required=True, help="Memory root directory")

def main() -> None:
    parser = argparse.ArgumentParser(description="Memory entry CRUD operations")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("create")
    p.add_argument("--type", required=True); p.add_argument("--title", required=True)
    p.add_argument("--tags", default=None); p.add_argument("--metadata", default=None)
    p.add_argument("--content-file", default=None); p.add_argument("--content", default=None)
    _add_common(p)

    p = sub.add_parser("read")
    p.add_argument("--id", default=None); p.add_argument("--path", default=None)
    _add_common(p)

    p = sub.add_parser("update")
    p.add_argument("--id", required=True)
    p.add_argument("--content-file", default=None); p.add_argument("--metadata", default=None)
    _add_common(p)

    p = sub.add_parser("delete")
    p.add_argument("--id", default=None); p.add_argument("--path", default=None)
    _add_common(p)

    p = sub.add_parser("list")
    p.add_argument("--type", required=True); p.add_argument("--tags", default=None)
    _add_common(p)

    p = sub.add_parser("promote")
    p.add_argument("--path", required=True); p.add_argument("--type", required=True)
    p.add_argument("--title", required=True); p.add_argument("--metadata", default=None)
    _add_common(p)

    args = parser.parse_args()
    dispatch = {
        "create": cmd_create,
        "read": cmd_read,
        "update": cmd_update,
        "delete": cmd_delete,
        "list": cmd_list,
        "promote": cmd_promote,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
