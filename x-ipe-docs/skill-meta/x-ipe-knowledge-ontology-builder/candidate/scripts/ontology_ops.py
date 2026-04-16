#!/usr/bin/env python3
"""Ontology JSONL operations: register_class, add_properties, create_instance,
add_vocabulary, validate_terms.

JSON to stdout on success; JSON to stderr + exit 1 on error.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CHUNK_LINE_LIMIT = 5000


# ── helpers ────────────────────────────────────────────────────────────────

def _exit_error(error: str, message: str) -> None:
    print(json.dumps({"success": False, "error": error, "message": message}), file=sys.stderr)
    sys.exit(1)


def _ok(data: dict) -> None:
    print(json.dumps({"success": True, **data}, ensure_ascii=False))


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slugify(label: str) -> str:
    """Convert label to kebab-case slug (handles CamelCase)."""
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", label)
    slug = re.sub(r"[^a-z0-9]+", "-", spaced.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug) or "unnamed"


def _ensure_dirs(ontology_dir: Path) -> None:
    for sub in ("schema", "instances", "vocabulary"):
        (ontology_dir / sub).mkdir(parents=True, exist_ok=True)


def _append_jsonl(path: Path, record: dict) -> None:
    """Append a JSON line with file locking."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with open(path) as f:
        return sum(1 for _ in f)


def _load_jsonl_ids(path: Path) -> set[str]:
    """Replay JSONL events and return set of live entity IDs."""
    ids: set[str] = set()
    if not path.exists():
        return ids
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            op, rid = rec.get("op"), rec.get("id", "")
            if op in ("create", "update"):
                ids.add(rid)
            elif op == "delete":
                ids.discard(rid)
    return ids


def determine_lifecycle(source_files: list[str]) -> str:
    """Ephemeral if any source path contains .working/, else Persistent."""
    for path in source_files:
        if ".working/" in path:
            return "Ephemeral"
    return "Persistent"


# ── commands ───────────────────────────────────────────────────────────────

def cmd_register_class(args: argparse.Namespace) -> None:
    ontology_dir = Path(args.ontology_dir)
    _ensure_dirs(ontology_dir)
    if not args.label or not args.label.strip():
        _exit_error("INPUT_VALIDATION_FAILED", "'label' is required")

    source_files = json.loads(args.source_files) if args.source_files else []
    class_id = _slugify(args.label)
    lifecycle = determine_lifecycle(source_files)

    weight = 5
    if args.weight:
        try:
            weight = max(1, min(10, int(args.weight)))
        except ValueError:
            weight = 5

    record = {
        "op": "create",
        "type": "KnowledgeNode",
        "id": class_id,
        "ts": _now_iso(),
        "props": {
            "label": args.label.strip(),
            "description": (args.description or "").strip(),
            "source_files": source_files,
            "weight": weight,
            "parent": args.parent if args.parent else None,
            "properties": [],
            "lifecycle": lifecycle,
            "synthesize_id": None,
            "synthesize_message": None,
        },
    }

    registry_path = ontology_dir / "schema" / "class-registry.jsonl"
    _append_jsonl(registry_path, record)
    _ok({"class_id": class_id, "lifecycle": lifecycle,
         "writes_to": str(registry_path)})


def cmd_add_properties(args: argparse.Namespace) -> None:
    ontology_dir = Path(args.ontology_dir)
    _ensure_dirs(ontology_dir)

    if not args.class_id or not args.class_id.strip():
        _exit_error("INPUT_VALIDATION_FAILED", "'class_id' is required")

    registry_path = ontology_dir / "schema" / "class-registry.jsonl"
    existing = _load_jsonl_ids(registry_path)
    if args.class_id not in existing:
        _exit_error("CLASS_NOT_FOUND", f"Class '{args.class_id}' not in registry")

    properties = json.loads(args.properties) if args.properties else []
    if not properties:
        _exit_error("INPUT_VALIDATION_FAILED", "'properties' must be a non-empty array")

    record = {
        "op": "update",
        "type": "KnowledgeNode",
        "id": args.class_id,
        "ts": _now_iso(),
        "props": {"properties": properties},
    }

    _append_jsonl(registry_path, record)
    _ok({"class_id": args.class_id, "properties_added": len(properties),
         "writes_to": str(registry_path)})


def cmd_create_instance(args: argparse.Namespace) -> None:
    ontology_dir = Path(args.ontology_dir)
    _ensure_dirs(ontology_dir)

    if not args.label or not args.label.strip():
        _exit_error("INPUT_VALIDATION_FAILED", "'label' is required")
    if not args.class_id or not args.class_id.strip():
        _exit_error("INPUT_VALIDATION_FAILED", "'class' is required")

    source_files = json.loads(args.source_files) if args.source_files else []
    extra_props = json.loads(args.properties) if args.properties else {}
    lifecycle = determine_lifecycle(source_files)

    instances_dir = ontology_dir / "instances"

    # Single critical section: ID generation + append + index update
    lock_path = instances_dir / ".instance.lock"
    lock_path.touch(exist_ok=True)
    lock_fd = open(lock_path, "r")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)

        chunk_num = _resolve_chunk(instances_dir)
        chunk_path = instances_dir / f"instance.{chunk_num:03d}.jsonl"
        instance_id = _next_instance_id(instances_dir)

        props = {
            "label": args.label.strip(),
            "class": args.class_id.strip(),
            "source_files": source_files,
            "lifecycle": lifecycle,
            "synthesize_id": None,
            "synthesize_message": None,
            **extra_props,
        }

        record = {
            "op": "create",
            "type": "KnowledgeNode",
            "id": instance_id,
            "ts": _now_iso(),
            "props": props,
        }

        _append_jsonl(chunk_path, record)
        _update_index(instances_dir, instance_id, chunk_num)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()

    _ok({"instance_id": instance_id, "chunk": f"instance.{chunk_num:03d}.jsonl",
         "lifecycle": lifecycle, "writes_to": str(chunk_path)})


def _resolve_chunk(instances_dir: Path) -> int:
    """Find current chunk number; create next if current exceeds limit."""
    existing = sorted(instances_dir.glob("instance.*.jsonl"))
    if not existing:
        return 1
    last = existing[-1]
    num_match = re.search(r"instance\.(\d+)\.jsonl", last.name)
    current = int(num_match.group(1)) if num_match else 1
    if _count_lines(last) >= CHUNK_LINE_LIMIT:
        return current + 1
    return current


def _next_instance_id(instances_dir: Path) -> str:
    """Generate next sequential instance ID across all chunks.
    
    NOTE: Must be called while holding the instance lock (see cmd_create_instance).
    """
    max_seq = 0
    for chunk in instances_dir.glob("instance.*.jsonl"):
        for line in open(chunk):
            try:
                rid = json.loads(line.strip()).get("id", "")
            except (json.JSONDecodeError, ValueError):
                continue
            if rid.startswith("inst-"):
                try:
                    max_seq = max(max_seq, int(rid[5:]))
                except ValueError:
                    pass
    return f"inst-{max_seq + 1:03d}"


def _update_index(instances_dir: Path, instance_id: str, chunk_num: int) -> None:
    """Update _index.json. Must be called while holding the instance lock."""
    index_path = instances_dir / "_index.json"
    index: dict = {}
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            index = {}
    chunks = index.setdefault("chunks", {})
    key = f"instance.{chunk_num:03d}.jsonl"
    chunks.setdefault(key, {"instance_count": 0})
    chunks[key]["instance_count"] = chunks[key].get("instance_count", 0) + 1
    index.update({"latest_instance_id": instance_id, "updated": _now_iso()})
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_add_vocabulary(args: argparse.Namespace) -> None:
    ontology_dir = Path(args.ontology_dir)
    _ensure_dirs(ontology_dir)

    if not args.scheme or not args.scheme.strip():
        _exit_error("INPUT_VALIDATION_FAILED", "'scheme' is required")
    if not args.label or not args.label.strip():
        _exit_error("INPUT_VALIDATION_FAILED", "'label' is required")

    scheme_path = ontology_dir / "vocabulary" / f"{args.scheme.strip()}.json"
    vocab: dict = {"scheme": args.scheme.strip(), "version": "1.0",
                   "description": "", "concepts": {}}
    if scheme_path.exists():
        try:
            vocab = json.loads(scheme_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    label = args.label.strip()
    if label in vocab.get("concepts", {}):
        _ok({"added": False, "reason": "term already exists", "label": label})
        return

    entry: dict = {"label": label}
    if args.broader:
        entry["broader"] = args.broader.strip()
        # Update parent's narrower list
        parent = vocab["concepts"].get(args.broader.strip(), {})
        narrower = parent.get("narrower", [])
        if label not in narrower:
            narrower.append(label)
            parent["narrower"] = narrower
            vocab["concepts"][args.broader.strip()] = parent

    if args.narrower:
        narrower_list = json.loads(args.narrower)
        entry["narrower"] = narrower_list
        # Update each child's broader reference
        for child_label in narrower_list:
            child = vocab["concepts"].get(child_label, {"label": child_label})
            child["broader"] = label
            vocab["concepts"][child_label] = child

    vocab["concepts"][label] = entry
    scheme_path.write_text(json.dumps(vocab, indent=2, ensure_ascii=False), encoding="utf-8")
    _update_vocab_index(ontology_dir)
    _ok({"added": True, "label": label, "scheme": args.scheme.strip(),
         "writes_to": str(scheme_path)})


def _update_vocab_index(ontology_dir: Path) -> None:
    vocab_dir = ontology_dir / "vocabulary"
    schemes = []
    for f in sorted(vocab_dir.glob("*.json")):
        if f.name.startswith("_"):
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            schemes.append({"scheme": data.get("scheme", f.stem), "file": f.name,
                            "concept_count": len(data.get("concepts", {}))})
        except (json.JSONDecodeError, OSError):
            continue
    (vocab_dir / "_index.json").write_text(
        json.dumps({"schemes": schemes, "updated": _now_iso()}, indent=2, ensure_ascii=False),
        encoding="utf-8")


def cmd_validate_terms(args: argparse.Namespace) -> None:
    ontology_dir = Path(args.ontology_dir)
    terms = json.loads(args.terms) if args.terms else []
    if not terms:
        _exit_error("INPUT_VALIDATION_FAILED", "'terms' must be a non-empty array")

    vocab_dir = ontology_dir / "vocabulary"
    all_terms: dict[str, set[str]] = {}
    if vocab_dir.is_dir():
        for f in vocab_dir.glob("*.json"):
            if f.name.startswith("_"):
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                all_terms[data.get("scheme", f.stem)] = set(data.get("concepts", {}).keys())
            except (json.JSONDecodeError, OSError):
                continue

    valid, invalid = [], []
    for t in terms:
        label = t.get("label", "") if isinstance(t, dict) else str(t)
        scheme = t.get("scheme", "") if isinstance(t, dict) else ""
        if scheme and scheme in all_terms:
            bucket = valid if label in all_terms[scheme] else invalid
            bucket.append({"label": label, "scheme": scheme, "status": "found" if bucket is valid else "not_found"})
        else:
            found_in = [s for s, c in all_terms.items() if label in c]
            (valid if found_in else invalid).append(
                {"label": label, "status": "found", "found_in": found_in} if found_in
                else {"label": label, "status": "not_found"})

    _ok({"valid": valid, "invalid": invalid, "total": len(terms),
         "valid_count": len(valid), "invalid_count": len(invalid)})


# ── CLI ────────────────────────────────────────────────────────────────────

def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--ontology-dir", required=True, help="Ontology root directory")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ontology JSONL operations")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("register_class")
    p.add_argument("--label", required=True); p.add_argument("--description", default="")
    p.add_argument("--source-files", default=None); p.add_argument("--weight", default=None)
    p.add_argument("--parent", default=None); _add_common(p)

    p = sub.add_parser("add_properties")
    p.add_argument("--class-id", required=True); p.add_argument("--properties", required=True)
    _add_common(p)

    p = sub.add_parser("create_instance")
    p.add_argument("--class-id", required=True); p.add_argument("--label", required=True)
    p.add_argument("--source-files", default=None); p.add_argument("--properties", default=None)
    _add_common(p)

    p = sub.add_parser("add_vocabulary")
    p.add_argument("--scheme", required=True); p.add_argument("--label", required=True)
    p.add_argument("--broader", default=None); p.add_argument("--narrower", default=None)
    _add_common(p)

    p = sub.add_parser("validate_terms")
    p.add_argument("--terms", required=True); _add_common(p)

    args = parser.parse_args()
    {"register_class": cmd_register_class, "add_properties": cmd_add_properties,
     "create_instance": cmd_create_instance, "add_vocabulary": cmd_add_vocabulary,
     "validate_terms": cmd_validate_terms}[args.command](args)


if __name__ == "__main__":
    main()
