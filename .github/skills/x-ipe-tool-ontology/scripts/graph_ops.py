#!/usr/bin/env python3
"""
Graph Operations: build named graph files from master entity store,
detect clusters via Union-Find, prune stale references.

Master store: _entities.jsonl (single source of truth)
Named graphs: {cluster-root-label}.jsonl (derived views)

Usage:
    python3 graph_ops.py build --scope PATH --output PATH [--entities PATH]
    python3 graph_ops.py prune --entities PATH
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from ontology import (
    append_op,
    load_graph,
    validate_graph,
)


def _slugify(text: str) -> str:
    """Convert label to safe filename slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "unnamed"


class UnionFind:
    """Union-Find / Disjoint Set for cluster detection."""

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}
        self._rank: dict[str, int] = {}

    def find(self, x: str) -> str:
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])  # path compression
        return self._parent[x]

    def union(self, x: str, y: str) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        # Union by rank
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1


def detect_clusters(
    entities: dict, relations: list
) -> dict[str, list[str]]:
    """Detect connected components using Union-Find.

    Returns dict mapping root_entity_id -> [member_entity_ids].
    Root = entity with highest degree (most edges) in the cluster.
    """
    uf = UnionFind()

    # Initialize all entities
    for eid in entities:
        uf.find(eid)

    # Union connected entities
    for rel in relations:
        if rel["from"] in entities and rel["to"] in entities:
            uf.union(rel["from"], rel["to"])

    # Group by root
    groups: dict[str, list[str]] = {}
    for eid in entities:
        root = uf.find(eid)
        groups.setdefault(root, []).append(eid)

    # Re-key by highest-degree entity in each cluster
    degree: dict[str, int] = {eid: 0 for eid in entities}
    for rel in relations:
        if rel["from"] in degree:
            degree[rel["from"]] += 1
        if rel["to"] in degree:
            degree[rel["to"]] += 1

    result: dict[str, list[str]] = {}
    for _, members in groups.items():
        hub = max(members, key=lambda m: degree.get(m, 0))
        result[hub] = members

    return result


def prune_stale(entities_path: str) -> dict:
    """Check source_files of each entity; remove entities whose files are all gone.

    For entities with some existing files, update source_files to only existing ones.
    Returns summary of pruned/updated entities.
    """
    entities, relations = load_graph(entities_path)
    pruned = []
    updated = []

    from datetime import datetime, timezone

    for eid, entity in list(entities.items()):
        source_files = entity.get("properties", {}).get("source_files", [])
        if not source_files:
            continue

        existing = [f for f in source_files if Path(f).exists()]

        if len(existing) == 0:
            # All source files gone — delete entity
            ts = datetime.now(timezone.utc).isoformat()
            append_op(entities_path, {"op": "delete", "id": eid, "timestamp": ts})
            pruned.append(eid)
        elif len(existing) < len(source_files):
            # Some files gone — update source_files
            ts = datetime.now(timezone.utc).isoformat()
            append_op(
                entities_path,
                {
                    "op": "update",
                    "id": eid,
                    "properties": {"source_files": existing},
                    "timestamp": ts,
                },
            )
            updated.append(eid)

    return {"pruned": pruned, "updated": updated}


def build(
    scope_path: str,
    output_path: str,
    entities_path: str | None = None,
) -> dict:
    """Build named graph files from master entity store.

    Steps:
    1. Load _entities.jsonl
    2. Filter entities with source_files under scope_path
    3. Collect relations where both endpoints are in filtered set
    4. Prune stale references
    5. Detect clusters (Union-Find)
    6. Clean old named .jsonl files in output dir
    7. Save each cluster as {root-label-slugified}.jsonl
    8. Validate each output file
    9. Return summary
    """
    if entities_path is None:
        entities_path = str(Path(output_path) / "_entities.jsonl")

    # Step 1: Load
    entities, relations = load_graph(entities_path)

    if not entities:
        return {
            "clusters": 0,
            "entities_total": 0,
            "entities_in_scope": 0,
            "files": [],
        }

    # Step 2: Filter by scope
    scope = Path(scope_path).resolve()
    filtered_ids: set[str] = set()
    for eid, entity in entities.items():
        source_files = entity.get("properties", {}).get("source_files", [])
        for sf in source_files:
            try:
                sf_resolved = Path(sf).resolve()
                if str(sf_resolved).startswith(str(scope)):
                    filtered_ids.add(eid)
                    break
            except (OSError, ValueError):
                continue

    if not filtered_ids:
        return {
            "clusters": 0,
            "entities_total": len(entities),
            "entities_in_scope": 0,
            "files": [],
        }

    # Step 3: Filter relations
    filtered_entities = {eid: entities[eid] for eid in filtered_ids}
    filtered_relations = [
        r
        for r in relations
        if r["from"] in filtered_ids and r["to"] in filtered_ids
    ]

    # Step 4: Prune stale (operates on master file)
    prune_result = prune_stale(entities_path)

    # Reload after pruning to get updated state
    if prune_result["pruned"] or prune_result["updated"]:
        entities, relations = load_graph(entities_path)
        filtered_ids = {eid for eid in filtered_ids if eid in entities}
        filtered_entities = {eid: entities[eid] for eid in filtered_ids}
        filtered_relations = [
            r
            for r in relations
            if r["from"] in filtered_ids and r["to"] in filtered_ids
        ]

    # Step 5: Detect clusters
    clusters = detect_clusters(filtered_entities, filtered_relations)

    # Step 6: Clean old named .jsonl files (not _entities.jsonl, not .dimension-registry.json)
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    protected = {"_entities.jsonl", ".dimension-registry.json"}
    for f in output_dir.glob("*.jsonl"):
        if f.name not in protected:
            f.unlink()

    # Step 7: Save each cluster
    files_created = []
    for root_id, member_ids in clusters.items():
        root_label = filtered_entities[root_id]["properties"].get("label", root_id)
        slug = _slugify(root_label)
        filename = f"{slug}.jsonl"
        filepath = output_dir / filename

        # Write cluster entities and relations
        cluster_entities = {eid: filtered_entities[eid] for eid in member_ids}
        cluster_relations = [
            r
            for r in filtered_relations
            if r["from"] in cluster_entities and r["to"] in cluster_entities
        ]

        with open(filepath, "w") as f:
            for entity in cluster_entities.values():
                from datetime import datetime, timezone

                record = {
                    "op": "create",
                    "entity": entity,
                    "timestamp": entity.get("updated", datetime.now(timezone.utc).isoformat()),
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            for rel in cluster_relations:
                record = {
                    "op": "relate",
                    "from": rel["from"],
                    "rel": rel["rel"],
                    "to": rel["to"],
                    "properties": rel.get("properties", {}),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        files_created.append(
            {
                "file": filename,
                "root": root_id,
                "root_label": root_label,
                "entity_count": len(cluster_entities),
                "relation_count": len(cluster_relations),
            }
        )

    # Step 8: Validate
    validation_errors = []
    for fc in files_created:
        errs = validate_graph(str(output_dir / fc["file"]))
        if errs:
            validation_errors.extend(
                [f"{fc['file']}: {e}" for e in errs]
            )

    return {
        "clusters": len(clusters),
        "entities_total": len(entities),
        "entities_in_scope": len(filtered_ids),
        "files": files_created,
        "pruned": prune_result["pruned"],
        "updated_stale": prune_result["updated"],
        "validation_errors": validation_errors,
    }


def _output_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _error_exit(message: str) -> None:
    print(json.dumps({"error": message}, ensure_ascii=False))
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Graph Operations")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Build named graphs from master store")
    p_build.add_argument("--scope", required=True, help="Scope path for filtering")
    p_build.add_argument("--output", required=True, help="Output directory")
    p_build.add_argument("--entities", default=None, help="Master entities JSONL path")

    p_prune = sub.add_parser("prune", help="Prune stale entity references")
    p_prune.add_argument("--entities", required=True)

    args = parser.parse_args()

    try:
        if args.command == "build":
            result = build(args.scope, args.output, args.entities)
            _output_json(result)
        elif args.command == "prune":
            result = prune_stale(args.entities)
            _output_json(result)
    except (ValueError, OSError) as e:
        _error_exit(str(e))


if __name__ == "__main__":
    main()
