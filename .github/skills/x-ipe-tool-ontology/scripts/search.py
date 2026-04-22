#!/usr/bin/env python3
"""
Search Engine: text matching, BFS subgraph extraction, cross-graph pagination.

Usage:
    python3 search.py --query TEXT --scope all|FILE[,FILE,...] \
        [--depth N] [--page-size N] [--page N] --ontology-dir PATH
"""

import argparse
import json
import sys
from pathlib import Path

from ontology import load_graph


def _text_match(entity: dict, query: str) -> list[str]:
    """Case-insensitive substring match on label, description, dimensions.

    Returns list of matched field names.
    """
    props = entity.get("properties", {})
    q = query.lower()
    matched = []

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
    """BFS traversal from seed entities up to `depth` hops.

    Returns (node_ids, edges) for the subgraph.
    """
    # Build adjacency (undirected)
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
    """Simple scoring: 1.0 for label, 0.5 for others. Sum normalized to max 1."""
    if not match_fields:
        return 0.0
    score = 0.0
    for field in match_fields:
        if field == "label":
            score += 1.0
        else:
            score += 0.5
    return min(score, 1.0)


def _find_components(seed_ids: set[str], edges: list[dict]) -> list[set[str]]:
    """Find connected components among seed_ids using the given edges.

    Returns list of sets — each set is one connected component of seeds.
    """
    adj: dict[str, set[str]] = {}
    seed_set = set(seed_ids)
    for e in edges:
        src, tgt = e["from"], e["to"]
        if src in seed_set or tgt in seed_set:
            adj.setdefault(src, set()).add(tgt)
            adj.setdefault(tgt, set()).add(src)

    visited: set[str] = set()
    components: list[set[str]] = []

    for sid in seed_ids:
        if sid in visited:
            continue
        component: set[str] = set()
        queue = [sid]
        while queue:
            node = queue.pop()
            if node not in seed_set or node in visited:
                continue
            visited.add(node)
            component.add(node)
            for neighbor in adj.get(node, set()):
                if neighbor in seed_set and neighbor not in visited:
                    queue.append(neighbor)
        if component:
            components.append(component)

    return components


def _inject_search_hub(
    query: str,
    seed_ids: set[str],
    subgraph_nodes: set[str],
    subgraph_edges: list[dict],
) -> tuple[set[str], list[dict], list[dict]]:
    """Inject virtual hub node if direct matches form disconnected components.

    Returns (nodes, edges, virtual_nodes) — virtual_nodes is [] if no hub needed.
    """
    if len(seed_ids) < 2:
        return subgraph_nodes, subgraph_edges, []

    components = _find_components(seed_ids, subgraph_edges)
    if len(components) <= 1:
        return subgraph_nodes, subgraph_edges, []

    hub_id = f"__search_hub__{query}"
    virtual_nodes = [{"id": hub_id, "label": query, "node_type": "search_hub"}]

    hub_edges = [
        {"from": hub_id, "rel": "search_match", "to": sid}
        for sid in seed_ids
    ]

    return (
        subgraph_nodes | {hub_id},
        subgraph_edges + hub_edges,
        virtual_nodes,
    )


def search(
    query: str,
    scope: str,
    ontology_dir: str,
    depth: int = 3,
    page_size: int = 20,
    page: int = 1,
) -> dict:
    """Execute search across ontology graphs.

    Args:
        query: Text to search for.
        scope: "all" or comma-separated list of .jsonl filenames.
        ontology_dir: Path to .ontology/ directory.
        depth: BFS traversal depth from matched nodes.
        page_size: Results per page.
        page: 1-based page number.

    Returns:
        Search result dict with matches, subgraph, pagination.
    """
    ont_path = Path(ontology_dir)

    # Determine which graph files to search
    if scope == "all":
        graph_files = [
            f
            for f in ont_path.glob("*.jsonl")
            if f.name != "_entities.jsonl"
        ]
    else:
        graph_files = []
        for name in scope.split(","):
            name = name.strip()
            candidate = ont_path / name
            if not candidate.exists() and not name.endswith(".jsonl"):
                candidate = ont_path / f"{name}.jsonl"
            if candidate.exists():
                graph_files.append(candidate)

    # Search across all graph files
    all_matches: list[dict] = []
    all_entities: dict = {}
    all_relations: list = []

    for gf in graph_files:
        entities, relations = load_graph(str(gf))
        all_entities.update(entities)
        all_relations.extend(relations)

        for eid, entity in entities.items():
            match_fields = _text_match(entity, query)
            if match_fields:
                all_matches.append(
                    {
                        "entity": entity,
                        "score": _score_match(match_fields),
                        "provenance": gf.name,
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
            seed_ids, all_entities, all_relations, depth
        )
        # CR-002: inject virtual hub if matches are disconnected
        subgraph_nodes, subgraph_edges, virtual_nodes = _inject_search_hub(
            query, seed_ids, subgraph_nodes, subgraph_edges
        )
    else:
        subgraph_nodes, subgraph_edges, virtual_nodes = set(), [], []

    return {
        "query": query,
        "scope": scope,
        "matches": page_matches,
        "subgraph": {
            "nodes": sorted(subgraph_nodes),
            "edges": subgraph_edges,
            "virtual_nodes": virtual_nodes,
        },
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
    }


def _output_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _error_exit(message: str) -> None:
    print(json.dumps({"error": message}, ensure_ascii=False))
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ontology Search")
    parser.add_argument("--query", required=True, help="Search text")
    parser.add_argument(
        "--scope",
        required=True,
        help="'all' or comma-separated .jsonl filenames",
    )
    parser.add_argument("--ontology-dir", required=True, help="Path to .ontology/")
    parser.add_argument("--depth", type=int, default=3, help="BFS depth (default: 3)")
    parser.add_argument("--page-size", type=int, default=20, help="Results per page")
    parser.add_argument("--page", type=int, default=1, help="Page number (1-based)")

    args = parser.parse_args()

    try:
        result = search(
            query=args.query,
            scope=args.scope,
            ontology_dir=args.ontology_dir,
            depth=args.depth,
            page_size=args.page_size,
            page=args.page,
        )
        _output_json(result)
    except (ValueError, OSError) as e:
        _error_exit(str(e))


if __name__ == "__main__":
    main()
