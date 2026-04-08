# Section 01 — Architecture Recovery

## Architectural Style

**Graph-based knowledge store** with a single-file append-only event log and schema-validated typed entities.

The system follows an **Event Sourcing** pattern at the storage layer: every mutation (create, update, delete, relate, unrelate) is appended as a JSONL record. Current state is reconstructed by replaying the log.

## Layered Architecture

```
┌─────────────────────────────────────────┐
│            CLI Layer (argparse)          │  ← User-facing: 9 subcommands
├─────────────────────────────────────────┤
│          Domain Logic Layer             │  ← Entity CRUD, Relation ops,
│  create_entity, query_entities,         │     Query, Validation
│  get_related, validate_graph            │
├─────────────────────────────────────────┤
│         Storage Layer                   │  ← JSONL append-only log
│  load_graph, append_op                  │     YAML schema read/write
├─────────────────────────────────────────┤
│         Security Layer                  │  ← Path traversal prevention
│  resolve_safe_path                      │
└─────────────────────────────────────────┘
```

## Component Diagram

```
                    ┌──────────────┐
                    │  CLI (main)  │
                    └──────┬───────┘
                           │ dispatches
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
   ┌──────────────┐ ┌────────────┐ ┌──────────────┐
   │ Entity Ops   │ │ Relation   │ │ Validation   │
   │ create/get/  │ │ Ops        │ │ Engine       │
   │ query/list/  │ │ relate/    │ │ validate/    │
   │ update/delete│ │ get_related│ │ constraints  │
   └──────┬───────┘ └─────┬──────┘ └──────┬───────┘
          │                │               │
          ▼                ▼               ▼
   ┌─────────────────────────────────────────────┐
   │            Storage (append_op / load_graph)  │
   │  graph.jsonl          schema.yaml            │
   └─────────────────────────────────────────────┘
```

## Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage format | JSONL (append-only) | Preserves full mutation history; simple to implement |
| Schema format | YAML | Human-readable type definitions |
| ID generation | `{type_prefix}_{uuid4_hex[:8]}` | Readable + unique |
| Graph reconstruction | Full replay on every read | Simple but O(n) with log size |
| Validation | Schema-driven at graph level | Decoupled from entity creation |
| Path security | Whitelist root enforcement | Prevents directory traversal |

## Quality Attributes

| Attribute | Assessment |
|-----------|-----------|
| **Simplicity** | High — single file, no external deps beyond PyYAML |
| **Extensibility** | Medium — new entity types via schema; new ops require code changes |
| **Performance** | Low for large graphs — full replay on every operation |
| **Durability** | Append-only log preserves all history |
| **Consistency** | No concurrency control (single-user assumed) |
| **Security** | Path traversal prevention; forbidden properties on credentials |
