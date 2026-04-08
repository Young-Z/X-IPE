# Section 03 — API Contracts

## CLI API (Command-Line Interface)

Entry point: `python3 scripts/ontology.py <command> [options]`

### Commands

| Command | Required Args | Optional Args | Output |
|---------|--------------|---------------|--------|
| `create` | `--type TYPE` | `--props JSON`, `--id ID`, `--graph PATH` | JSON entity object |
| `get` | `--id ID` | `--graph PATH` | JSON entity or "Entity not found" |
| `query` | — | `--type TYPE`, `--where JSON`, `--graph PATH` | JSON array of entities |
| `list` | — | `--type TYPE`, `--graph PATH` | JSON array of entities |
| `update` | `--id ID`, `--props JSON` | `--graph PATH` | JSON entity or "Entity not found" |
| `delete` | `--id ID` | `--graph PATH` | "Deleted: {id}" or "Entity not found" |
| `relate` | `--from ID`, `--rel TYPE`, `--to ID` | `--props JSON`, `--graph PATH` | JSON relation record |
| `related` | `--id ID` | `--rel TYPE`, `--dir {outgoing,incoming,both}`, `--graph PATH` | JSON array of related |
| `validate` | — | `--graph PATH`, `--schema PATH` | "Graph is valid." or error list |
| `schema-append` | `--data JSON` or `--file PATH` | `--schema PATH` | JSON merged schema |

### Default Paths

| Parameter | Default |
|-----------|---------|
| `--graph` | `memory/ontology/graph.jsonl` |
| `--schema` | `memory/ontology/schema.yaml` |

## Python Library API

Importable from: `from scripts.ontology import ...`

### Entity Operations

```python
create_entity(type_name: str, properties: dict, graph_path: str, entity_id: str = None) -> dict
get_entity(entity_id: str, graph_path: str) -> dict | None
query_entities(type_name: str, where: dict, graph_path: str) -> list
list_entities(type_name: str, graph_path: str) -> list
update_entity(entity_id: str, properties: dict, graph_path: str) -> dict | None
delete_entity(entity_id: str, graph_path: str) -> bool
```

### Relation Operations

```python
create_relation(from_id: str, rel_type: str, to_id: str, properties: dict, graph_path: str) -> dict
get_related(entity_id: str, rel_type: str, graph_path: str, direction: str = "outgoing") -> list
```

### Validation & Schema

```python
validate_graph(graph_path: str, schema_path: str) -> list[str]  # returns error messages
load_schema(schema_path: str) -> dict
write_schema(schema_path: str, schema: dict) -> None
merge_schema(base: dict, incoming: dict) -> dict
append_schema(schema_path: str, incoming: dict) -> dict
```

### Storage Primitives

```python
load_graph(path: str) -> tuple[dict, list]  # (entities_by_id, relations_list)
append_op(path: str, record: dict) -> None
generate_id(type_name: str) -> str  # "{prefix}_{uuid_hex[:8]}"
resolve_safe_path(user_path: str, *, root=None, must_exist=False, label="path") -> Path
```

## Data Contracts

### Entity Object

```json
{
  "id": "pers_a1b2c3d4",
  "type": "Person",
  "properties": { "name": "Alice", "email": "alice@example.com" },
  "created": "2026-01-01T00:00:00+00:00",
  "updated": "2026-01-01T00:00:00+00:00"
}
```

### JSONL Operation Record

```json
{"op": "create", "entity": {...}, "timestamp": "..."}
{"op": "update", "id": "...", "properties": {...}, "timestamp": "..."}
{"op": "delete", "id": "...", "timestamp": "..."}
{"op": "relate", "from": "...", "rel": "...", "to": "...", "properties": {}, "timestamp": "..."}
{"op": "unrelate", "from": "...", "rel": "...", "to": "..."}
```

### Related Entity Result

```json
{
  "relation": "has_task",
  "entity": { "id": "...", "type": "Task", "properties": {...} }
}
```

For bidirectional queries (`--dir both`), includes `"direction": "outgoing" | "incoming"`.
