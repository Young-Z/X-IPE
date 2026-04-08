#!/usr/bin/env python3
"""
KB Ontology Engine: entity CRUD, relations, JSONL event sourcing, validation.

Purpose-built for knowledge base context. Inspired by ontology-1.0.4 design
but with KB-specific rules (fixed KnowledgeNode type, hardcoded validation).

Usage:
    python3 ontology.py create --type KnowledgeNode --props '{"label":"JWT Auth"}' --graph path.jsonl
    python3 ontology.py get --id know_abc123 --graph path.jsonl
    python3 ontology.py update --id know_abc123 --props '{"weight":8}' --graph path.jsonl
    python3 ontology.py delete --id know_abc123 --graph path.jsonl
    python3 ontology.py list [--type KnowledgeNode] --graph path.jsonl
    python3 ontology.py query --type KnowledgeNode --where '{"node_type":"concept"}' --graph path.jsonl
    python3 ontology.py relate --from id1 --rel depends_on --to id2 --graph path.jsonl
    python3 ontology.py related --id id1 [--rel type] [--dir outgoing] --graph path.jsonl
    python3 ontology.py find-path --from id1 --to id2 --graph path.jsonl
    python3 ontology.py validate --graph path.jsonl
    python3 ontology.py load --graph path.jsonl
    python3 ontology.py retag --scope /path/to/kb --ontology-dir /path/.ontology --intake-status /path/.intake-status.json
"""

import argparse
import fcntl
import json
import sys
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_NODE_TYPES = {"concept", "entity", "document"}
ALLOWED_RELATIONS = {
    "related_to",
    "depends_on",
    "is_type_of",
    "part_of",
    "described_by",
}
ACYCLIC_RELATIONS = {"depends_on"}
REQUIRED_PROPERTIES = {"label", "node_type", "source_files"}
WEIGHT_MIN = 1
WEIGHT_MAX = 10
WEIGHT_DEFAULT = 5
ID_PREFIX = "know"


def resolve_safe_path(
    user_path: str,
    *,
    root: str | None = None,
    must_exist: bool = False,
    label: str = "path",
) -> Path:
    """Resolve user path within root and reject traversal outside it."""
    if not user_path or not user_path.strip():
        raise ValueError(f"Invalid {label}: empty path")

    safe_root = Path(root).resolve() if root else Path.cwd().resolve()
    candidate = Path(user_path).expanduser()
    if not candidate.is_absolute():
        candidate = safe_root / candidate

    resolved = candidate.resolve(strict=False)

    try:
        resolved.relative_to(safe_root)
    except ValueError:
        raise ValueError(
            f"Invalid {label}: must stay within root '{safe_root}'"
        )

    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"Invalid {label}: not found '{resolved}'")

    return resolved


def generate_id(prefix: str = ID_PREFIX) -> str:
    """Generate a unique entity ID: know_{uuid_hex[:8]}."""
    suffix = uuid.uuid4().hex[:8]
    return f"{prefix}_{suffix}"


def load_graph(path: str) -> tuple[dict, list]:
    """Load entities and relations from JSONL, replaying events to current state.

    Skips corrupted/partial lines with a warning to stderr.

    Returns:
        (entities_dict, relations_list) where entities_dict maps id -> entity.
    """
    entities: dict[str, dict] = {}
    relations: list[dict] = []

    graph_path = Path(path)
    if not graph_path.exists():
        return entities, relations

    with open(graph_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(
                    f"Warning: skipping corrupted line {line_num} in {path}",
                    file=sys.stderr,
                )
                continue

            op = record.get("op")
            if op == "create":
                entity = record["entity"]
                entities[entity["id"]] = entity
            elif op == "update":
                eid = record["id"]
                if eid in entities:
                    entities[eid]["properties"].update(
                        record.get("properties", {})
                    )
                    entities[eid]["updated"] = record.get("timestamp")
            elif op == "delete":
                entities.pop(record["id"], None)
            elif op == "relate":
                relations.append(
                    {
                        "from": record["from"],
                        "rel": record["rel"],
                        "to": record["to"],
                        "properties": record.get("properties", {}),
                    }
                )
            elif op == "unrelate":
                relations = [
                    r
                    for r in relations
                    if not (
                        r["from"] == record["from"]
                        and r["rel"] == record["rel"]
                        and r["to"] == record["to"]
                    )
                ]

    return entities, relations


def append_op(path: str, record: dict) -> None:
    """Append a JSON event line to the graph file (creates parent dirs).

    Uses fcntl.flock for write safety.
    """
    graph_path = Path(path)
    graph_path.parent.mkdir(parents=True, exist_ok=True)

    with open(graph_path, "a") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _validate_node_properties(properties: dict) -> list[str]:
    """Validate KnowledgeNode properties. Returns list of errors."""
    errors = []
    for prop in REQUIRED_PROPERTIES:
        if prop not in properties:
            errors.append(f"Missing required property: '{prop}'")

    node_type = properties.get("node_type")
    if node_type and node_type not in ALLOWED_NODE_TYPES:
        errors.append(
            f"Invalid node_type '{node_type}': must be one of {sorted(ALLOWED_NODE_TYPES)}"
        )

    source_files = properties.get("source_files")
    if source_files is not None and not isinstance(source_files, list):
        errors.append("'source_files' must be a list of strings")

    weight = properties.get("weight")
    if weight is not None:
        if not isinstance(weight, (int, float)) or weight < WEIGHT_MIN or weight > WEIGHT_MAX:
            errors.append(
                f"'weight' must be between {WEIGHT_MIN} and {WEIGHT_MAX}"
            )

    return errors


def create_entity(
    type_name: str,
    properties: dict,
    graph_path: str,
    entity_id: str | None = None,
) -> dict:
    """Create a new KnowledgeNode entity with validation.

    Args:
        type_name: Entity type (must be "KnowledgeNode").
        properties: Entity properties (label, node_type, source_files, etc.).
        graph_path: Path to the JSONL graph file.
        entity_id: Optional custom ID; auto-generated if None.

    Returns:
        The created entity dict.

    Raises:
        ValueError: If validation fails.
    """
    errors = _validate_node_properties(properties)
    if errors:
        raise ValueError(f"Validation errors: {'; '.join(errors)}")

    if "weight" not in properties:
        properties["weight"] = WEIGHT_DEFAULT

    eid = entity_id or generate_id(ID_PREFIX)
    timestamp = datetime.now(timezone.utc).isoformat()

    entity = {
        "id": eid,
        "type": type_name,
        "properties": properties,
        "created": timestamp,
        "updated": timestamp,
    }

    record = {"op": "create", "entity": entity, "timestamp": timestamp}
    append_op(graph_path, record)
    return entity


def get_entity(entity_id: str, graph_path: str) -> dict | None:
    """Fetch entity by ID. Returns None if not found."""
    entities, _ = load_graph(graph_path)
    return entities.get(entity_id)


def update_entity(
    entity_id: str, properties: dict, graph_path: str
) -> dict | None:
    """Merge new properties into existing entity.

    Returns updated entity or None if not found.
    """
    entities, _ = load_graph(graph_path)
    if entity_id not in entities:
        return None

    # Validate updated fields
    if "node_type" in properties and properties["node_type"] not in ALLOWED_NODE_TYPES:
        raise ValueError(
            f"Invalid node_type '{properties['node_type']}': must be one of {sorted(ALLOWED_NODE_TYPES)}"
        )
    if "weight" in properties:
        w = properties["weight"]
        if not isinstance(w, (int, float)) or w < WEIGHT_MIN or w > WEIGHT_MAX:
            raise ValueError(f"'weight' must be between {WEIGHT_MIN} and {WEIGHT_MAX}")

    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "op": "update",
        "id": entity_id,
        "properties": properties,
        "timestamp": timestamp,
    }
    append_op(graph_path, record)

    entities[entity_id]["properties"].update(properties)
    entities[entity_id]["updated"] = timestamp
    return entities[entity_id]


def delete_entity(entity_id: str, graph_path: str) -> bool:
    """Soft-delete an entity (append delete event). Returns False if not found."""
    entities, _ = load_graph(graph_path)
    if entity_id not in entities:
        return False

    timestamp = datetime.now(timezone.utc).isoformat()
    record = {"op": "delete", "id": entity_id, "timestamp": timestamp}
    append_op(graph_path, record)
    return True


def list_entities(type_name: str | None, graph_path: str) -> list:
    """List all entities, optionally filtered by type."""
    entities, _ = load_graph(graph_path)
    if type_name:
        return [e for e in entities.values() if e["type"] == type_name]
    return list(entities.values())


def query_entities(
    type_name: str | None, where: dict, graph_path: str
) -> list:
    """Filter entities by type and property predicates.

    Supports nested key lookup for dimensions (e.g., "dimensions.topic").
    """
    entities, _ = load_graph(graph_path)
    results = []

    for entity in entities.values():
        if type_name and entity["type"] != type_name:
            continue

        match = True
        for key, value in where.items():
            # Support dotted key for nested properties
            parts = key.split(".")
            current = entity["properties"]
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    current = None
                    break

            if current != value:
                # Check if value is in a list
                if isinstance(current, list) and value in current:
                    continue
                match = False
                break

        if match:
            results.append(entity)

    return results


def _has_cycle(from_id: str, to_id: str, relations: list) -> bool:
    """Check if adding from_id->to_id creates a cycle via DFS."""
    # Build adjacency for existing depends_on
    adj: dict[str, list[str]] = {}
    for rel in relations:
        if rel["rel"] in ACYCLIC_RELATIONS:
            adj.setdefault(rel["from"], []).append(rel["to"])

    # Adding from_id -> to_id; check if to_id can reach from_id
    visited: set[str] = set()
    stack = [to_id]
    while stack:
        node = stack.pop()
        if node == from_id:
            return True
        if node in visited:
            continue
        visited.add(node)
        stack.extend(adj.get(node, []))
    return False


def create_relation(
    from_id: str,
    rel_type: str,
    to_id: str,
    properties: dict | None,
    graph_path: str,
) -> dict:
    """Create a typed relation between entities.

    Validates relation type and checks acyclicity for depends_on.

    Raises:
        ValueError: If relation type invalid or cycle detected.
    """
    if rel_type not in ALLOWED_RELATIONS:
        raise ValueError(
            f"Invalid relation type '{rel_type}': must be one of {sorted(ALLOWED_RELATIONS)}"
        )

    entities, relations = load_graph(graph_path)

    if from_id not in entities:
        raise ValueError(f"Source entity '{from_id}' not found")
    if to_id not in entities:
        raise ValueError(f"Target entity '{to_id}' not found")

    if rel_type in ACYCLIC_RELATIONS and _has_cycle(from_id, to_id, relations):
        raise ValueError(
            f"Cycle detected: adding {from_id} -[{rel_type}]-> {to_id} would create a cycle"
        )

    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "op": "relate",
        "from": from_id,
        "rel": rel_type,
        "to": to_id,
        "properties": properties or {},
        "timestamp": timestamp,
    }
    append_op(graph_path, record)
    return record


def get_related(
    entity_id: str,
    rel_type: str | None,
    graph_path: str,
    direction: str = "outgoing",
) -> list:
    """Get entities related to entity_id.

    Args:
        direction: "outgoing", "incoming", or "both".
    """
    entities, relations = load_graph(graph_path)
    results = []

    for rel in relations:
        if direction in ("outgoing", "both") and rel["from"] == entity_id:
            if not rel_type or rel["rel"] == rel_type:
                if rel["to"] in entities:
                    entry = {"relation": rel["rel"], "entity": entities[rel["to"]]}
                    if direction == "both":
                        entry["direction"] = "outgoing"
                    results.append(entry)
        if direction in ("incoming", "both") and rel["to"] == entity_id:
            if not rel_type or rel["rel"] == rel_type:
                if rel["from"] in entities:
                    entry = {"relation": rel["rel"], "entity": entities[rel["from"]]}
                    if direction == "both":
                        entry["direction"] = "incoming"
                    results.append(entry)

    return results


def find_path(from_id: str, to_id: str, graph_path: str) -> list[str]:
    """BFS shortest path between two entities. Returns list of IDs or empty."""
    entities, relations = load_graph(graph_path)

    if from_id not in entities or to_id not in entities:
        return []

    # Build undirected adjacency
    adj: dict[str, set[str]] = {}
    for rel in relations:
        adj.setdefault(rel["from"], set()).add(rel["to"])
        adj.setdefault(rel["to"], set()).add(rel["from"])

    if from_id == to_id:
        return [from_id]

    visited: set[str] = {from_id}
    queue: deque[list[str]] = deque([[from_id]])
    while queue:
        path = queue.popleft()
        node = path[-1]
        for neighbor in adj.get(node, set()):
            if neighbor == to_id:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return []


def validate_graph(graph_path: str) -> list[str]:
    """Validate KB-specific graph constraints. Returns list of error strings."""
    entities, relations = load_graph(graph_path)
    errors = []

    for eid, entity in entities.items():
        props = entity.get("properties", {})
        for req in REQUIRED_PROPERTIES:
            if req not in props:
                errors.append(f"{eid}: missing required property '{req}'")

        nt = props.get("node_type")
        if nt and nt not in ALLOWED_NODE_TYPES:
            errors.append(f"{eid}: invalid node_type '{nt}'")

        w = props.get("weight")
        if w is not None and (not isinstance(w, (int, float)) or w < WEIGHT_MIN or w > WEIGHT_MAX):
            errors.append(f"{eid}: weight must be {WEIGHT_MIN}-{WEIGHT_MAX}")

        sf = props.get("source_files")
        if sf is not None and not isinstance(sf, list):
            errors.append(f"{eid}: source_files must be a list")

    for rel in relations:
        if rel["rel"] not in ALLOWED_RELATIONS:
            errors.append(
                f"Invalid relation type '{rel['rel']}' ({rel['from']} -> {rel['to']})"
            )
        if rel["from"] not in entities:
            errors.append(f"Relation references missing entity: {rel['from']}")
        if rel["to"] not in entities:
            errors.append(f"Relation references missing entity: {rel['to']}")

    # Acyclicity on depends_on
    dep_adj: dict[str, list[str]] = {}
    for rel in relations:
        if rel["rel"] in ACYCLIC_RELATIONS:
            dep_adj.setdefault(rel["from"], []).append(rel["to"])

    visited: dict[str, bool] = {}

    def dfs(node: str, stack: set[str]) -> bool:
        visited[node] = True
        stack.add(node)
        for nxt in dep_adj.get(node, []):
            if nxt in stack:
                return True
            if not visited.get(nxt, False):
                if dfs(nxt, stack):
                    return True
        stack.discard(node)
        return False

    for node in dep_adj:
        if not visited.get(node, False):
            if dfs(node, set()):
                errors.append("Cyclic dependency detected in 'depends_on' relations")
                break

    return errors


def merge_schema(base: dict, incoming: dict) -> dict:
    """Deep-merge two dicts. Lists are concatenated with deduplication."""
    result = dict(base)
    for key, value in incoming.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_schema(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list):
                merged = list(result[key])
                for item in value:
                    if item not in merged:
                        merged.append(item)
                result[key] = merged
            else:
                result[key] = value
        else:
            result[key] = value
    return result


def retag_files(
    scope: str,
    ontology_dir: str,
    intake_status_path: str,
) -> dict:
    """Re-tag files with status 'filed-untagged' by creating minimal entities.

    Reads .intake-status.json, finds untagged files under scope,
    creates a KnowledgeNode for each (or updates existing), and
    updates status to 'filed'.

    Returns summary: {"retagged": N, "failed": M, "files": [...]}.
    """
    status_path = Path(intake_status_path)
    if not status_path.exists():
        raise ValueError(f"Intake status file not found: {intake_status_path}")

    with open(status_path) as f:
        try:
            status_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in intake status: {e}") from e

    scope_resolved = str(Path(scope).resolve())
    entities_path = str(Path(ontology_dir) / "_entities.jsonl")

    # Filter to filed-untagged entries within scope
    untagged = {}
    for filename, entry in status_data.items():
        if entry.get("status") != "filed-untagged":
            continue
        dest = entry.get("destination", "")
        try:
            dest_resolved = str(Path(dest).resolve())
        except (OSError, ValueError):
            continue
        if dest_resolved.startswith(scope_resolved):
            untagged[filename] = entry

    if not untagged:
        return {"retagged": 0, "failed": 0, "files": []}

    files_result = []
    retagged = 0
    failed = 0

    for filename, entry in untagged.items():
        dest = entry["destination"]
        dest_path = Path(dest)

        if not dest_path.exists():
            files_result.append({
                "file": filename,
                "status": "failed",
                "error": f"File not found: {dest}",
            })
            failed += 1
            continue

        try:
            # Check if entity already exists for this file
            entities, _ = load_graph(entities_path)
            existing_id = None
            for eid, ent in entities.items():
                sf = ent.get("properties", {}).get("source_files", [])
                if dest in sf:
                    existing_id = eid
                    break

            if existing_id:
                # Update existing entity
                update_entity(
                    existing_id,
                    {"source_files": [dest]},
                    entities_path,
                )
                entity_id = existing_id
            else:
                # Create minimal entity — label derived from filename
                label = dest_path.stem.replace("-", " ").replace("_", " ").title()
                props = {
                    "label": label,
                    "node_type": "document",
                    "source_files": [dest],
                }
                entity = create_entity("KnowledgeNode", props, entities_path)
                entity_id = entity["id"]

            # Update status
            status_data[filename]["status"] = "filed"
            if "error" in status_data[filename]:
                del status_data[filename]["error"]

            files_result.append({
                "file": filename,
                "entity_id": entity_id,
                "status": "tagged",
            })
            retagged += 1
        except (ValueError, OSError) as e:
            files_result.append({
                "file": filename,
                "status": "failed",
                "error": str(e),
            })
            failed += 1

    # Write updated status atomically
    tmp_path = status_path.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)
    tmp_path.rename(status_path)

    return {"retagged": retagged, "failed": failed, "files": files_result}


def _output_json(data: object) -> None:
    """Print JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _error_exit(message: str) -> None:
    """Print error JSON and exit with code 1."""
    print(json.dumps({"error": message}, ensure_ascii=False))
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="KB Ontology Engine")
    sub = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = sub.add_parser("create", help="Create entity")
    p_create.add_argument("--type", required=True)
    p_create.add_argument("--props", required=True, help="JSON properties")
    p_create.add_argument("--graph", required=True)
    p_create.add_argument("--id", default=None, help="Optional entity ID")

    # get
    p_get = sub.add_parser("get", help="Get entity by ID")
    p_get.add_argument("--id", required=True)
    p_get.add_argument("--graph", required=True)

    # update
    p_update = sub.add_parser("update", help="Update entity")
    p_update.add_argument("--id", required=True)
    p_update.add_argument("--props", required=True, help="JSON properties to merge")
    p_update.add_argument("--graph", required=True)

    # delete
    p_delete = sub.add_parser("delete", help="Delete entity")
    p_delete.add_argument("--id", required=True)
    p_delete.add_argument("--graph", required=True)

    # list
    p_list = sub.add_parser("list", help="List entities")
    p_list.add_argument("--type", default=None)
    p_list.add_argument("--graph", required=True)

    # query
    p_query = sub.add_parser("query", help="Query entities")
    p_query.add_argument("--type", default=None)
    p_query.add_argument("--where", required=True, help="JSON filter")
    p_query.add_argument("--graph", required=True)

    # relate
    p_rel = sub.add_parser("relate", help="Create relation")
    p_rel.add_argument("--from", dest="from_id", required=True)
    p_rel.add_argument("--rel", required=True)
    p_rel.add_argument("--to", required=True)
    p_rel.add_argument("--props", default="{}", help="JSON properties")
    p_rel.add_argument("--graph", required=True)

    # related
    p_related = sub.add_parser("related", help="Get related entities")
    p_related.add_argument("--id", required=True)
    p_related.add_argument("--rel", default=None)
    p_related.add_argument("--dir", default="outgoing", choices=["outgoing", "incoming", "both"])
    p_related.add_argument("--graph", required=True)

    # find-path
    p_fp = sub.add_parser("find-path", help="BFS shortest path")
    p_fp.add_argument("--from", dest="from_id", required=True)
    p_fp.add_argument("--to", required=True)
    p_fp.add_argument("--graph", required=True)

    # validate
    p_val = sub.add_parser("validate", help="Validate graph")
    p_val.add_argument("--graph", required=True)

    # load
    p_load = sub.add_parser("load", help="Load and display graph state")
    p_load.add_argument("--graph", required=True)

    # retag
    p_retag = sub.add_parser("retag", help="Re-tag filed-untagged files")
    p_retag.add_argument("--scope", required=True, help="KB folder path to scan")
    p_retag.add_argument("--ontology-dir", required=True, help="Path to .ontology/ directory")
    p_retag.add_argument("--intake-status", required=True, help="Path to .intake-status.json")

    args = parser.parse_args()

    try:
        if args.command == "create":
            props = json.loads(args.props)
            entity = create_entity(args.type, props, args.graph, args.id)
            _output_json(entity)

        elif args.command == "get":
            entity = get_entity(args.id, args.graph)
            if entity is None:
                _error_exit(f"Entity '{args.id}' not found")
            _output_json(entity)

        elif args.command == "update":
            props = json.loads(args.props)
            entity = update_entity(args.id, props, args.graph)
            if entity is None:
                _error_exit(f"Entity '{args.id}' not found")
            _output_json(entity)

        elif args.command == "delete":
            ok = delete_entity(args.id, args.graph)
            if not ok:
                _error_exit(f"Entity '{args.id}' not found")
            _output_json({"deleted": args.id})

        elif args.command == "list":
            entities = list_entities(args.type, args.graph)
            _output_json(entities)

        elif args.command == "query":
            where = json.loads(args.where)
            entities = query_entities(args.type, where, args.graph)
            _output_json(entities)

        elif args.command == "relate":
            props = json.loads(args.props)
            rel = create_relation(args.from_id, args.rel, args.to, props, args.graph)
            _output_json(rel)

        elif args.command == "related":
            results = get_related(args.id, args.rel, args.graph, args.dir)
            _output_json(results)

        elif args.command == "find-path":
            path = find_path(args.from_id, args.to, args.graph)
            _output_json({"path": path, "length": len(path)})

        elif args.command == "validate":
            errors = validate_graph(args.graph)
            _output_json({"valid": len(errors) == 0, "errors": errors})

        elif args.command == "load":
            entities, relations = load_graph(args.graph)
            _output_json(
                {
                    "entities": list(entities.values()),
                    "relations": relations,
                    "entity_count": len(entities),
                    "relation_count": len(relations),
                }
            )

        elif args.command == "retag":
            result = retag_files(
                scope=args.scope,
                ontology_dir=args.ontology_dir,
                intake_status_path=args.intake_status,
            )
            _output_json(result)

    except (ValueError, json.JSONDecodeError) as e:
        _error_exit(str(e))


if __name__ == "__main__":
    main()
