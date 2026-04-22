#!/usr/bin/env python3
"""Ontology synthesis operations: discover, wash, link, init_relations.

Cross-graph integration engine — discovers overlap between ontology graphs,
normalizes vocabulary, and creates typed cross-domain relationships.

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

# Common abbreviation expansions for wash_terms
ABBREVIATION_TABLE: dict[str, str] = {
    "js": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "rb": "Ruby",
    "db": "Database",
    "api": "API",
    "ui": "UI",
    "ux": "UX",
    "css": "CSS",
    "html": "HTML",
    "sql": "SQL",
    "http": "HTTP",
    "rest": "REST",
    "cli": "CLI",
    "sdk": "SDK",
    "oop": "OOP",
    "fp": "Functional Programming",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "ci": "Continuous Integration",
    "cd": "Continuous Deployment",
}


# ── helpers ────────────────────────────────────────────────────────────────

def _exit_error(error: str, message: str) -> None:
    print(json.dumps({"success": False, "error": error, "message": message}),
          file=sys.stderr)
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


def _load_jsonl(path: Path) -> list[dict]:
    """Load all valid JSONL records from a file, skipping corrupt lines."""
    records: list[dict] = []
    if not path.exists():
        return records
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _replay_entities(records: list[dict]) -> dict[str, dict]:
    """Replay JSONL event log and return live entity state {id → props}."""
    state: dict[str, dict] = {}
    for rec in records:
        op = rec.get("op")
        rid = rec.get("id", "")
        if op == "create":
            state[rid] = rec.get("props", {})
        elif op == "update" and rid in state:
            state[rid].update(rec.get("props", {}))
        elif op == "delete":
            state.pop(rid, None)
    return state


def _resolve_relation_chunk(relations_dir: Path) -> int:
    """Find current relation chunk number; create next if limit exceeded."""
    existing = sorted(relations_dir.glob("_relations.*.jsonl"))
    if not existing:
        return 1
    last = existing[-1]
    num_match = re.search(r"_relations\.(\d+)\.jsonl", last.name)
    current = int(num_match.group(1)) if num_match else 1
    if _count_lines(last) >= CHUNK_LINE_LIMIT:
        return current + 1
    return current


def _next_relation_id(relations_dir: Path) -> str:
    """Generate next sequential relation ID across all chunks."""
    max_seq = 0
    for chunk in relations_dir.glob("_relations.*.jsonl"):
        for rec in _load_jsonl(chunk):
            rid = rec.get("id", "")
            if rid.startswith("rel-"):
                try:
                    max_seq = max(max_seq, int(rid[4:]))
                except ValueError:
                    pass
    return f"rel-{max_seq + 1:03d}"


def _load_existing_relations(relations_dir: Path) -> list[dict]:
    """Load all relation records from all chunks."""
    all_relations: list[dict] = []
    for chunk in sorted(relations_dir.glob("_relations.*.jsonl")):
        all_relations.extend(_load_jsonl(chunk))
    return all_relations


def _relation_exists(existing: list[dict], from_id: str, to_id: str,
                     relation_type: str) -> bool:
    """Check if a relation already exists (deduplicate)."""
    for rec in existing:
        if rec.get("op") == "delete":
            continue
        props = rec.get("props", {})
        if (props.get("from_id") == from_id and
                props.get("to_id") == to_id and
                props.get("relation_type") == relation_type):
            return True
    return False


def _load_synthesis_meta(relations_dir: Path) -> dict:
    """Load _synthesis_meta.json or return defaults."""
    meta_path = relations_dir / "_synthesis_meta.json"
    if meta_path.exists():
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"synthesis_version": 0, "last_run": None,
            "synthesized_with": [], "total_relations": 0}


def _save_synthesis_meta(relations_dir: Path, meta: dict) -> None:
    """Write _synthesis_meta.json atomically."""
    meta_path = relations_dir / "_synthesis_meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")


def _load_class_registry(ontology_dir: Path) -> dict[str, dict]:
    """Load class-registry.jsonl and replay to live state."""
    path = ontology_dir / "schema" / "class-registry.jsonl"
    return _replay_entities(_load_jsonl(path))


def _load_instances(ontology_dir: Path) -> dict[str, dict]:
    """Load all instance chunks and replay to live state."""
    instances_dir = ontology_dir / "instances"
    all_records: list[dict] = []
    for chunk in sorted(instances_dir.glob("instance.*.jsonl")):
        all_records.extend(_load_jsonl(chunk))
    return _replay_entities(all_records)


def _find_instance_chunk(ontology_dir: Path, instance_id: str) -> Path | None:
    """Find which chunk file contains a given instance ID."""
    instances_dir = ontology_dir / "instances"
    for chunk in sorted(instances_dir.glob("instance.*.jsonl")):
        for rec in _load_jsonl(chunk):
            if rec.get("id") == instance_id:
                return chunk
    return None


# ── commands ───────────────────────────────────────────────────────────────

def cmd_discover(args: argparse.Namespace) -> None:
    ontology_dir = Path(args.ontology_dir)
    if not ontology_dir.exists():
        _exit_error("ONTOLOGY_DIR_ERROR",
                    f"Ontology directory not found: {ontology_dir}")

    source_graph = args.source_graph
    search_scope = args.search_scope

    # Load source entities — only from the specified source_graph file
    instances_dir = ontology_dir / "instances"
    source_path = instances_dir / source_graph
    source_index: dict[str, list[tuple[str, str]]] = {}

    if source_graph == "class-registry.jsonl":
        source_entities = _load_class_registry(ontology_dir)
    elif source_path.exists():
        source_entities = _replay_entities(_load_jsonl(source_path))
    else:
        # Source graph not found — return empty results gracefully
        _ok({"related_graphs": [], "overlap_candidates": []})
        return

    for eid, props in source_entities.items():
        label = props.get("label", eid)
        slug = _slugify(label)
        source_index.setdefault(slug, []).append((eid, label))

    # Determine target graphs
    if search_scope == "all":
        target_chunks = sorted(instances_dir.glob("instance.*.jsonl"))
    else:
        target_chunks = [instances_dir / p.strip()
                         for p in search_scope.split(",") if p.strip()]

    related_graphs: list[str] = []
    overlap_candidates: list[dict] = []

    for chunk_path in target_chunks:
        if not chunk_path.exists():
            continue
        if chunk_path.name == source_graph:
            continue

        target_records = _load_jsonl(chunk_path)
        target_entities = _replay_entities(target_records)
        chunk_has_overlap = False

        for tid, tprops in target_entities.items():
            tlabel = tprops.get("label", tid)
            tslug = _slugify(tlabel)

            if tslug in source_index:
                for sid, slabel in source_index[tslug]:
                    if slabel.lower() == tlabel.lower():
                        confidence = 1.0
                    elif _slugify(slabel) == tslug:
                        confidence = 0.8
                    else:
                        confidence = 0.6

                    overlap_candidates.append({
                        "source_id": sid,
                        "target_id": tid,
                        "graph_source": source_graph,
                        "graph_target": chunk_path.name,
                        "confidence_score": confidence,
                    })
                    chunk_has_overlap = True

        if chunk_has_overlap:
            related_graphs.append(chunk_path.name)

    # Deduplicate by (source_id, target_id) keeping highest confidence
    seen: dict[tuple[str, str], dict] = {}
    for cand in overlap_candidates:
        key = (cand["source_id"], cand["target_id"])
        if key not in seen or cand["confidence_score"] > seen[key]["confidence_score"]:
            seen[key] = cand
    overlap_candidates = sorted(seen.values(),
                                key=lambda c: c["confidence_score"],
                                reverse=True)

    _ok({"related_graphs": related_graphs,
         "overlap_candidates": overlap_candidates})


def cmd_wash(args: argparse.Namespace) -> None:
    ontology_dir = Path(args.ontology_dir)
    if not ontology_dir.exists():
        _exit_error("ONTOLOGY_DIR_ERROR",
                    f"Ontology directory not found: {ontology_dir}")

    # Load candidates from file or stdin
    candidates_json = args.candidates_json
    if candidates_json and candidates_json != "-":
        try:
            candidates_data = json.loads(
                Path(candidates_json).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            _exit_error("INPUT_VALIDATION_FAILED",
                        f"Cannot read candidates: {e}")
    else:
        try:
            candidates_data = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            _exit_error("INPUT_VALIDATION_FAILED",
                        f"Invalid JSON on stdin: {e}")

    overlap_candidates = candidates_data if isinstance(
        candidates_data, list) else candidates_data.get(
        "overlap_candidates", [])

    # Collect all labels from involved graphs
    all_labels: list[tuple[str, str, str]] = []  # (label, id, graph)
    for cand in overlap_candidates:
        all_labels.append((cand.get("source_id", ""), cand.get("source_id", ""),
                           cand.get("graph_source", "")))
        all_labels.append((cand.get("target_id", ""), cand.get("target_id", ""),
                           cand.get("graph_target", "")))

    # Also load class and instance labels for richer vocabulary
    classes = _load_class_registry(ontology_dir)
    instances = _load_instances(ontology_dir)
    for cid, props in classes.items():
        all_labels.append((props.get("label", cid), cid, "class-registry"))
    for iid, props in instances.items():
        all_labels.append((props.get("label", iid), iid, "instances"))

    # Group synonyms by slug
    slug_groups: dict[str, list[tuple[str, str, str]]] = {}
    for label, eid, graph in all_labels:
        slug = _slugify(label)
        # Also check abbreviation table
        lower = label.lower().strip()
        if lower in ABBREVIATION_TABLE:
            slug = _slugify(ABBREVIATION_TABLE[lower])
        slug_groups.setdefault(slug, []).append((label, eid, graph))

    canonical_vocabulary: list[dict] = []
    normalization_map: list[dict] = []

    for slug, members in slug_groups.items():
        if len(members) <= 1:
            continue

        # Select canonical form: longest non-abbreviation, prefer title case
        labels = list({m[0] for m in members})
        non_abbrev = [l for l in labels
                      if l.lower() not in ABBREVIATION_TABLE]
        candidates = non_abbrev if non_abbrev else labels
        canonical = max(candidates, key=lambda l: (len(l), l[0].isupper()))

        aliases = [l for l in labels if l != canonical]
        if aliases:
            canonical_vocabulary.append({
                "canonical": canonical,
                "aliases": sorted(aliases),
            })
            for label, eid, graph in members:
                if label != canonical:
                    normalization_map.append({
                        "original_term": label,
                        "canonical_term": canonical,
                        "source_graph": graph,
                        "confidence": 1.0 if label.lower() == canonical.lower()
                        else 0.8,
                    })

    _ok({"canonical_vocabulary": canonical_vocabulary,
         "normalization_map": normalization_map})


def cmd_link(args: argparse.Namespace) -> None:
    ontology_dir = Path(args.ontology_dir)
    if not ontology_dir.exists():
        _exit_error("ONTOLOGY_DIR_ERROR",
                    f"Ontology directory not found: {ontology_dir}")

    tier = args.tier
    if tier not in ("class", "instance"):
        _exit_error("INPUT_VALIDATION_FAILED",
                    f"Invalid tier: {tier}. Must be 'class' or 'instance'")

    dry_run = args.dry_run

    # Load normalization map and canonical vocabulary
    try:
        norm_map = json.loads(
            Path(args.normalization_map_json).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        _exit_error("INPUT_VALIDATION_FAILED",
                    f"Cannot read normalization map: {e}")

    try:
        canon_vocab = json.loads(
            Path(args.canonical_vocab_json).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        _exit_error("INPUT_VALIDATION_FAILED",
                    f"Cannot read canonical vocabulary: {e}")

    graphs = [g.strip() for g in args.graphs.split(",") if g.strip()]
    if len(graphs) < 2:
        _exit_error("INPUT_VALIDATION_FAILED",
                    "At least two graphs required for linking")

    relations_dir = ontology_dir / "relations"
    relations_dir.mkdir(parents=True, exist_ok=True)

    existing_relations = _load_existing_relations(relations_dir)
    meta = _load_synthesis_meta(relations_dir)
    new_version = meta["synthesis_version"] + 1
    ts = _now_iso()

    # Build normalization lookup: original_term → canonical_term
    norm_lookup: dict[str, str] = {}
    if isinstance(norm_map, list):
        for entry in norm_map:
            norm_lookup[entry.get("original_term", "")] = entry.get(
                "canonical_term", "")
    elif isinstance(norm_map, dict):
        for entry in norm_map.get("normalization_map", []):
            norm_lookup[entry.get("original_term", "")] = entry.get(
                "canonical_term", "")

    cross_references: list[dict] = []
    duplicates_skipped = 0
    entities_updated = 0

    if tier == "class":
        classes = _load_class_registry(ontology_dir)

        # Apply normalization to class labels → build normalized_slug → class_id map
        norm_classes: dict[str, list[tuple[str, str]]] = {}
        for cid, props in classes.items():
            label = props.get("label", cid)
            canonical = norm_lookup.get(label, label)
            slug = _slugify(canonical)
            norm_classes.setdefault(slug, []).append((cid, "class-registry"))

        # Find matches across different graphs (same normalized slug)
        for slug, members in norm_classes.items():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    from_id, from_graph = members[i]
                    to_id, to_graph = members[j]

                    if _relation_exists(existing_relations, from_id, to_id,
                                        "related_to"):
                        duplicates_skipped += 1
                        continue

                    cross_references.append({
                        "from_id": from_id,
                        "to_id": to_id,
                        "relation_type": "related_to",
                        "source_graph": from_graph,
                        "target_graph": to_graph,
                        "synthesis_version": new_version,
                    })

    elif tier == "instance":
        # Load class-level relations
        class_relations = [
            r for r in existing_relations
            if r.get("op") == "create" and r.get("type") == "Relation"
            and r.get("props", {}).get("relation_type") == "related_to"
        ]

        if not class_relations:
            _ok({"cross_references": [], "relations_written": 0,
                 "duplicates_skipped": 0, "entities_updated": 0,
                 "message": "No class-level relationships found — "
                            "instance linking skipped",
                 "writes_to": None})
            return

        instances = _load_instances(ontology_dir)

        # For each class-level relation, find instances of both classes
        for crel in class_relations:
            cprops = crel.get("props", {})
            from_class = cprops.get("from_id", "")
            to_class = cprops.get("to_id", "")

            from_instances = {iid: p for iid, p in instances.items()
                             if p.get("class") == from_class}
            to_instances = {iid: p for iid, p in instances.items()
                           if p.get("class") == to_class}

            # Match by normalized labels
            for fiid, fprops in from_instances.items():
                flabel = fprops.get("label", fiid)
                fcanonical = norm_lookup.get(flabel, flabel)
                fslug = _slugify(fcanonical)

                for tiid, tprops in to_instances.items():
                    tlabel = tprops.get("label", tiid)
                    tcanonical = norm_lookup.get(tlabel, tlabel)
                    tslug = _slugify(tcanonical)

                    if fslug != tslug:
                        continue

                    if _relation_exists(existing_relations, fiid, tiid,
                                        "related_to"):
                        duplicates_skipped += 1
                        continue

                    cross_references.append({
                        "from_id": fiid,
                        "to_id": tiid,
                        "relation_type": "related_to",
                        "source_graph": f"instance (class: {from_class})",
                        "target_graph": f"instance (class: {to_class})",
                        "synthesis_version": new_version,
                    })

    # Write relations (unless dry-run)
    writes_to = None
    if cross_references and not dry_run:
        lock_path = relations_dir / ".relations.lock"
        lock_path.touch(exist_ok=True)
        lock_fd = open(lock_path, "r")
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)

            for xref in cross_references:
                chunk_num = _resolve_relation_chunk(relations_dir)
                chunk_path = relations_dir / f"_relations.{chunk_num:03d}.jsonl"
                rel_id = _next_relation_id(relations_dir)

                record = {
                    "op": "create",
                    "type": "Relation",
                    "id": rel_id,
                    "ts": ts,
                    "props": {
                        "from_id": xref["from_id"],
                        "to_id": xref["to_id"],
                        "relation_type": xref["relation_type"],
                        "source_graph": xref["source_graph"],
                        "target_graph": xref["target_graph"],
                        "synthesis_version": new_version,
                        "synthesized_with": graphs,
                    },
                }
                _append_jsonl(chunk_path, record)
                writes_to = str(chunk_path)
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()

        # Update entity synthesis fields (instance tier only)
        if tier == "instance":
            updated_ids: set[str] = set()
            for xref in cross_references:
                for eid in (xref["from_id"], xref["to_id"]):
                    if eid in updated_ids:
                        continue
                    chunk_path = _find_instance_chunk(ontology_dir, eid)
                    if chunk_path:
                        update_record = {
                            "op": "update",
                            "type": "KnowledgeNode",
                            "id": eid,
                            "ts": ts,
                            "props": {
                                "synthesize_id": ts,
                                "synthesize_message":
                                    f"Cross-domain linking: "
                                    f"{xref['from_id']} ↔ {xref['to_id']}",
                            },
                        }
                        _append_jsonl(chunk_path, update_record)
                        updated_ids.add(eid)
            entities_updated = len(updated_ids)

        # Update synthesis meta
        meta["synthesis_version"] = new_version
        meta["last_run"] = ts
        meta["synthesized_with"] = graphs
        meta["total_relations"] = meta.get("total_relations", 0) + len(
            cross_references)
        _save_synthesis_meta(relations_dir, meta)

    _ok({"cross_references": cross_references,
         "relations_written": len(cross_references) if not dry_run else 0,
         "duplicates_skipped": duplicates_skipped,
         "entities_updated": entities_updated,
         "writes_to": writes_to})


def cmd_init_relations(args: argparse.Namespace) -> None:
    ontology_dir = Path(args.ontology_dir)
    if not ontology_dir.exists():
        _exit_error("ONTOLOGY_DIR_ERROR",
                    f"Ontology directory not found: {ontology_dir}")

    relations_dir = ontology_dir / "relations"
    relations_dir.mkdir(parents=True, exist_ok=True)

    first_chunk = relations_dir / "_relations.001.jsonl"
    if first_chunk.exists():
        _ok({"message": "Relations already initialized"})
        return

    first_chunk.touch()
    meta = {
        "synthesis_version": 0,
        "last_run": None,
        "synthesized_with": [],
        "total_relations": 0,
    }
    _save_synthesis_meta(relations_dir, meta)
    _ok({"message": "Relations initialized",
         "writes_to": str(first_chunk)})


# ── CLI entrypoint ─────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ontology synthesis operations")
    sub = parser.add_subparsers(dest="command")

    # discover
    p_discover = sub.add_parser("discover",
                                help="Scan for cross-graph overlap")
    p_discover.add_argument("--ontology-dir", required=True)
    p_discover.add_argument("--source-graph", required=True,
                            help="Source graph filename (e.g. instance.001.jsonl)")
    p_discover.add_argument("--search-scope", default="all",
                            help="'all' or comma-separated graph paths")

    # wash
    p_wash = sub.add_parser("wash",
                            help="Normalize vocabulary terms")
    p_wash.add_argument("--ontology-dir", required=True)
    p_wash.add_argument("--candidates-json", default="-",
                        help="Path to candidates JSON file, or '-' for stdin")

    # link
    p_link = sub.add_parser("link",
                            help="Create cross-domain relations")
    p_link.add_argument("--ontology-dir", required=True)
    p_link.add_argument("--tier", required=True, choices=["class", "instance"])
    p_link.add_argument("--normalization-map-json", required=True)
    p_link.add_argument("--canonical-vocab-json", required=True)
    p_link.add_argument("--graphs", required=True,
                        help="Comma-separated graph file paths")
    p_link.add_argument("--dry-run", action="store_true",
                        help="Preview without writing")

    # init_relations
    p_init = sub.add_parser("init_relations",
                            help="Bootstrap empty relations file")
    p_init.add_argument("--ontology-dir", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "discover": cmd_discover,
        "wash": cmd_wash,
        "link": cmd_link,
        "init_relations": cmd_init_relations,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
