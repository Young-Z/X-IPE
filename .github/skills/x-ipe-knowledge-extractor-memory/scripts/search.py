#!/usr/bin/env python3
"""
Search Engine for persistent memory ontology.

Migrated from x-ipe-tool-ontology/scripts/search.py.
Standalone — no dependency on ontology.py.

Usage:
    python3 search.py --query TEXT --memory-dir PATH \
        [--depth N] [--page-size N] [--page N] [--class-filter TYPE]
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Data Loading (standalone — replaces `from ontology import load_graph`)
# ---------------------------------------------------------------------------


def _load_entities(ontology_dir: Path) -> dict:
    """Load entities from instances/*.jsonl files (excluding _ prefix).

    Falls back to instances/_index.json if no non-prefixed JSONL files exist.
    """
    entities: dict = {}
    instances_dir = ontology_dir / "instances"
    if not instances_dir.exists():
        return entities

    # Primary: non-prefixed JSONL files
    jsonl_files = sorted(
        f for f in instances_dir.glob("*.jsonl") if not f.name.startswith("_")
    )
    if jsonl_files:
        for jf in jsonl_files:
            with open(jf, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        entity = record.get("entity", record)
                        eid = entity.get("id")
                        if eid:
                            entities[eid] = entity
                    except json.JSONDecodeError:
                        continue
        return entities

    # Fallback: _index.json
    index_path = instances_dir / "_index.json"
    if index_path.exists():
        try:
            with open(index_path, encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                for eid, entity in data.items():
                    if isinstance(entity, dict):
                        entity.setdefault("id", eid)
                        entities[eid] = entity
            elif isinstance(data, list):
                for entity in data:
                    eid = entity.get("id")
                    if eid:
                        entities[eid] = entity
        except (json.JSONDecodeError, OSError):
            pass

    return entities


def _load_relations(ontology_dir: Path) -> list:
    """Load relations from instances/_relations.*.jsonl in numeric order."""
    relations: list = []
    instances_dir = ontology_dir / "instances"
    if not instances_dir.exists():
        return relations

    def _sort_key(f: Path) -> int:
        m = re.search(r"(\d+)", f.stem.split(".")[-1])
        return int(m.group()) if m else 0

    rel_files = sorted(instances_dir.glob("_relations.*.jsonl"), key=_sort_key)

    for rf in rel_files:
        with open(rf, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    rel = record.get("relation", record)
                    if "from" in rel and "to" in rel:
                        relations.append(rel)
                except json.JSONDecodeError:
                    continue

    return relations


# ---------------------------------------------------------------------------
# Core Search Logic (preserved from x-ipe-tool-ontology/scripts/search.py)
# ---------------------------------------------------------------------------


def _text_match(entity: dict, query: str) -> list[str]:
    """Case-insensitive substring match on label, description, dimensions.

    Returns list of matched field names.
    """
    props = entity.get("properties", {})
    q = query.lower()
    matched: list[str] = []

    label = props.get("label", "")
    if isinstance(label, str) and q in label.lower():
        matched.append("label")

    desc = props.get("description", "")
    if isinstance(desc, str) and q in desc.lower():
        matched.append("description")

    dims = props.get("dimensions", {})
    if isinstance(dims, dict):
        for dim_name, dim_val in dims.items():
            if isinstance(dim_val, str) and q in dim_val.lower():
                matched.append(f"dimensions.{dim_name}")
            elif isinstance(dim_val, list):
                for v in dim_val:
                    if isinstance(v, str) and q in v.lower():
                        matched.append(f"dimensions.{dim_name}")
                        break

    return matched


def _bfs_subgraph(
    seed_ids: set[str],
    entities: dict,
    relations: list,
    depth: int,
) -> tuple[set[str], list[dict]]:
    """BFS traversal from seed entities up to *depth* hops.

    Returns (node_ids, edges) for the subgraph.
    """
    adj: dict[str, list[tuple[str, dict]]] = {}
    for rel in relations:
        adj.setdefault(rel["from"], []).append((rel["to"], rel))
        adj.setdefault(rel["to"], []).append((rel["from"], rel))

    visited: set[str] = set(seed_ids)
    frontier = set(seed_ids)
    collected_edges: list[dict] = []
    seen_edges: set[tuple[str, str, str]] = set()

    for _ in range(depth):
        next_frontier: set[str] = set()
        for node in frontier:
            for neighbor, rel in adj.get(node, []):
                edge_key = (rel["from"], rel["rel"], rel["to"])
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    collected_edges.append(
                        {"from": rel["from"], "rel": rel["rel"], "to": rel["to"]}
                    )
                if neighbor not in visited and neighbor in entities:
                    visited.add(neighbor)
                    next_frontier.add(neighbor)
        frontier = next_frontier
        if not frontier:
            break

    return visited, collected_edges


def _score_match(match_fields: list[str]) -> float:
    """Simple scoring: 1.0 for label, 0.5 for others. Sum capped at 1."""
    if not match_fields:
        return 0.0
    score = 0.0
    for field in match_fields:
        if field == "label":
            score += 1.0
        else:
            score += 0.5
    return min(score, 1.0)


# ---------------------------------------------------------------------------
# Main Search Function
# ---------------------------------------------------------------------------


def search(
    query: str,
    memory_dir: str,
    depth: int = 3,
    page_size: int = 20,
    page: int = 1,
    class_filter: str | None = None,
) -> dict:
    """Execute search across memory ontology.

    Args:
        query: Text to search for.
        memory_dir: Path to memory/ directory (contains .ontology/).
        depth: BFS traversal depth from matched nodes.
        page_size: Results per page.
        page: 1-based page number.
        class_filter: Optional entity class/type filter.

    Returns:
        Search result dict with matches, subgraph, pagination.
    """
    ont_path = Path(memory_dir) / ".ontology"

    entities = _load_entities(ont_path)
    relations = _load_relations(ont_path)

    # Filter by class if specified
    if class_filter:
        cf_lower = class_filter.lower()
        entities = {
            eid: e
            for eid, e in entities.items()
            if e.get("type", "").lower() == cf_lower
            or e.get("properties", {}).get("node_type", "").lower() == cf_lower
        }

    # Search entities
    all_matches: list[dict] = []
    for eid, entity in entities.items():
        match_fields = _text_match(entity, query)
        if match_fields:
            all_matches.append(
                {
                    "entity": entity,
                    "score": _score_match(match_fields),
                    "match_fields": match_fields,
                }
            )

    # Sort by score descending
    all_matches.sort(key=lambda m: m["score"], reverse=True)

    # Pagination
    total_count = len(all_matches)
    start = (page - 1) * page_size
    end = start + page_size
    page_matches = all_matches[start:end]

    # BFS subgraph from matched entities on current page
    seed_ids = {m["entity"]["id"] for m in page_matches}
    if seed_ids:
        subgraph_nodes, subgraph_edges = _bfs_subgraph(
            seed_ids, entities, relations, depth
        )
    else:
        subgraph_nodes, subgraph_edges = set(), []

    return {
        "query": query,
        "matches": page_matches,
        "subgraph": {
            "nodes": sorted(subgraph_nodes),
            "edges": subgraph_edges,
        },
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Memory Ontology Search")
    parser.add_argument("--query", required=True, help="Search text")
    parser.add_argument(
        "--memory-dir",
        required=True,
        help="Path to memory/ directory (contains .ontology/)",
    )
    parser.add_argument(
        "--depth", type=int, default=3, help="BFS depth (default: 3)"
    )
    parser.add_argument(
        "--page-size", type=int, default=20, help="Results per page (default: 20)"
    )
    parser.add_argument(
        "--page", type=int, default=1, help="Page number, 1-based (default: 1)"
    )
    parser.add_argument(
        "--class-filter",
        default=None,
        help="Filter entities by class/type",
    )

    args = parser.parse_args()

    try:
        result = search(
            query=args.query,
            memory_dir=args.memory_dir,
            depth=args.depth,
            page_size=args.page_size,
            page=args.page,
            class_filter=args.class_filter,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
