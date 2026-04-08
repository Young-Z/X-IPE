# Section 06 — Data Flow Analysis

## Primary Data Flows

### Flow 1: Entity Creation

```
User Input (CLI args)
  │
  ▼
main() → argparse parses --type, --props, --id
  │
  ▼
create_entity(type_name, properties, graph_path, entity_id?)
  │
  ├── generate_id(type_name) → "{prefix}_{uuid4_hex[:8]}"
  │
  ├── Build entity dict { id, type, properties, created, updated }
  │
  ├── Build record { op: "create", entity, timestamp }
  │
  └── append_op(graph_path, record) → JSON serialize → append to graph.jsonl
         │
         ▼
      graph.jsonl (new line appended)
```

### Flow 2: Entity Query

```
User Input (CLI args)
  │
  ▼
query_entities(type_name, where, graph_path)
  │
  ├── load_graph(graph_path) → replay all JSONL lines
  │     │
  │     ├── For each line: parse JSON record
  │     ├── op="create" → add to entities dict
  │     ├── op="update" → merge properties
  │     ├── op="delete" → remove from dict
  │     ├── op="relate" → add to relations list
  │     └── op="unrelate" → remove from relations list
  │
  │   Result: (entities: dict, relations: list)
  │
  ├── Filter entities by type match
  ├── Filter entities by where property match
  │
  └── Return matched entities as JSON
```

### Flow 3: Graph Validation

```
validate_graph(graph_path, schema_path)
  │
  ├── load_graph(graph_path) → (entities, relations)
  ├── load_schema(schema_path) → YAML → dict
  │
  ├── For each entity:
  │   ├── Check required properties against type schema
  │   ├── Check forbidden properties
  │   └── Check enum values
  │
  ├── For each relation type:
  │   ├── Check from/to entity type constraints
  │   ├── Check cardinality limits
  │   └── Check acyclicity (DFS)
  │
  ├── For each global constraint:
  │   └── Event end >= start check
  │
  └── Return error list (empty = valid)
```

### Flow 4: Schema Evolution

```
schema-append --data '{"types": {"NewType": {...}}}'
  │
  ▼
append_schema(schema_path, incoming)
  │
  ├── load_schema(schema_path) → existing YAML → dict
  │
  ├── merge_schema(base, incoming)
  │   ├── Dicts: deep merge recursively
  │   ├── Lists: append with dedup
  │   └── Scalars: overwrite
  │
  └── write_schema(schema_path, merged) → dict → YAML file
```

## Data Stores

| Store | Format | Access Pattern | Location |
|-------|--------|---------------|----------|
| Graph | JSONL | Append-only write; Full replay read | `memory/ontology/graph.jsonl` |
| Schema | YAML | Read/write (overwrite on merge) | `memory/ontology/schema.yaml` |

## Data Flow Characteristics

| Characteristic | Value |
|---------------|-------|
| Write pattern | Append-only (immutable history) |
| Read pattern | Full replay (reconstruct state) |
| Caching | None — every read replays full log |
| Consistency model | Single-writer assumed (no locks) |
| Data format | JSON (entities) + YAML (schema) |
| Serialization | `json.dumps` / `json.loads` for graph; `yaml.safe_load` / `yaml.safe_dump` for schema |
