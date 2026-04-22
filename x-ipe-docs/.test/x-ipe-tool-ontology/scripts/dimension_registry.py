#!/usr/bin/env python3
"""
Dimension Registry: alias resolution, registration, listing, rebuild.

Runtime store: x-ipe-docs/knowledge-base/.ontology/.dimension-registry.json

Usage:
    python3 dimension_registry.py resolve --name NAME --registry PATH
    python3 dimension_registry.py register --dimension JSON --registry PATH
    python3 dimension_registry.py list --registry PATH
    python3 dimension_registry.py rebuild --entities PATH --registry PATH
"""

import argparse
import fcntl
import json
import sys
from pathlib import Path

from ontology import load_graph, merge_schema


def _load_registry(registry_path: str) -> dict:
    """Load dimension registry from JSON. Returns empty structure if missing."""
    p = Path(registry_path)
    if not p.exists():
        return {"version": "1.0", "dimensions": {}}
    with open(p, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            data = json.load(f)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data


def _save_registry(registry_path: str, data: dict) -> None:
    """Write dimension registry atomically with file lock."""
    p = Path(registry_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def resolve(name: str, registry_path: str) -> dict:
    """Resolve a dimension name or alias to its canonical entry.

    Returns:
        {"canonical": "technology", "dimension": {...}} or
        {"canonical": None, "candidates": []} if not found.
    """
    registry = _load_registry(registry_path)
    dimensions = registry.get("dimensions", {})

    # Exact canonical match
    if name in dimensions:
        return {"canonical": name, "dimension": dimensions[name]}

    # Alias search
    name_lower = name.lower()
    for canonical, dim_data in dimensions.items():
        aliases = dim_data.get("aliases", [])
        if name_lower in [a.lower() for a in aliases]:
            return {"canonical": canonical, "dimension": dim_data}

    return {"canonical": None, "candidates": list(dimensions.keys())}


def register(dimension_json: dict, registry_path: str) -> dict:
    """Register or update a dimension in the registry.

    dimension_json format:
        {"name": "technology", "type": "multi-value",
         "examples": [...], "aliases": [...]}
    """
    name = dimension_json.get("name")
    if not name:
        raise ValueError("Dimension must have a 'name' field")

    registry = _load_registry(registry_path)
    dimensions = registry.get("dimensions", {})

    entry = {
        "type": dimension_json.get("type", "multi-value"),
        "examples": dimension_json.get("examples", []),
        "aliases": dimension_json.get("aliases", []),
    }

    if name in dimensions:
        # Merge with existing
        dimensions[name] = merge_schema(dimensions[name], entry)
    else:
        dimensions[name] = entry

    registry["dimensions"] = dimensions
    _save_registry(registry_path, registry)

    return {"registered": name, "dimension": dimensions[name]}


def list_dimensions(registry_path: str) -> dict:
    """List all registered dimensions."""
    registry = _load_registry(registry_path)
    return registry


def rebuild(entities_path: str, registry_path: str) -> dict:
    """Rebuild registry from all entities' dimensions in _entities.jsonl.

    Scans every entity's dimensions object, collects unique dimension
    names and their observed values, and reconstructs the registry.
    """
    entities, _ = load_graph(entities_path)
    discovered: dict[str, dict] = {}

    for entity in entities.values():
        props = entity.get("properties", {})
        dims = props.get("dimensions", {})
        if not isinstance(dims, dict):
            continue
        for dim_name, dim_values in dims.items():
            if dim_name not in discovered:
                discovered[dim_name] = {
                    "type": "multi-value",
                    "examples": [],
                    "aliases": [],
                }
            # Collect examples from values
            if isinstance(dim_values, list):
                for v in dim_values:
                    if v not in discovered[dim_name]["examples"]:
                        discovered[dim_name]["examples"].append(v)
            elif isinstance(dim_values, str):
                if dim_values not in discovered[dim_name]["examples"]:
                    discovered[dim_name]["examples"].append(dim_values)
                discovered[dim_name]["type"] = "single-value"

    registry = {"version": "1.0", "dimensions": discovered}
    _save_registry(registry_path, registry)

    return {
        "rebuilt": True,
        "dimension_count": len(discovered),
        "dimensions": list(discovered.keys()),
    }


def _output_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _error_exit(message: str) -> None:
    print(json.dumps({"error": message}, ensure_ascii=False))
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dimension Registry")
    sub = parser.add_subparsers(dest="command", required=True)

    p_resolve = sub.add_parser("resolve", help="Resolve dimension name/alias")
    p_resolve.add_argument("--name", required=True)
    p_resolve.add_argument("--registry", required=True)

    p_register = sub.add_parser("register", help="Register a dimension")
    p_register.add_argument("--dimension", required=True, help="JSON dimension")
    p_register.add_argument("--registry", required=True)

    p_list = sub.add_parser("list", help="List dimensions")
    p_list.add_argument("--registry", required=True)

    p_rebuild = sub.add_parser("rebuild", help="Rebuild from entities")
    p_rebuild.add_argument("--entities", required=True)
    p_rebuild.add_argument("--registry", required=True)

    args = parser.parse_args()

    try:
        if args.command == "resolve":
            result = resolve(args.name, args.registry)
            _output_json(result)
        elif args.command == "register":
            dim = json.loads(args.dimension)
            result = register(dim, args.registry)
            _output_json(result)
        elif args.command == "list":
            result = list_dimensions(args.registry)
            _output_json(result)
        elif args.command == "rebuild":
            result = rebuild(args.entities, args.registry)
            _output_json(result)
    except (ValueError, json.JSONDecodeError) as e:
        _error_exit(str(e))


if __name__ == "__main__":
    main()
