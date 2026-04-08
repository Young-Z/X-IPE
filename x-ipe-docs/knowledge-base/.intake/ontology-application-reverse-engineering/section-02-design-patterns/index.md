# Section 02 — Design Patterns

## Identified Patterns

### 1. Event Sourcing (Storage Layer)

**Location:** `scripts/ontology.py:67-108` (load_graph), `scripts/ontology.py:111-117` (append_op)

Every mutation is recorded as a JSONL event with an `op` field:
- `create`, `update`, `delete` — entity operations
- `relate`, `unrelate` — relation operations

Current state is reconstructed by replaying all events sequentially. This provides:
- Full audit trail of all mutations
- Ability to reconstruct state at any point in time (with custom code)
- Simple crash recovery (append-only = no partial writes)

### 2. Repository Pattern (Data Access)

**Location:** `scripts/ontology.py:120-248`

Functions like `create_entity()`, `get_entity()`, `query_entities()`, `get_related()` serve as a repository layer, abstracting the JSONL storage behind a clean API. The graph path is passed as a parameter (dependency injection of storage location).

### 3. Strategy Pattern (Validation)

**Location:** `scripts/ontology.py:250-380`

The `validate_graph()` function applies multiple validation strategies:
- Property validation (required, forbidden, enum)
- Relation type-safety checks
- Cardinality enforcement
- Acyclicity detection (DFS)
- Global constraint evaluation (Event time ordering)

Each strategy is applied independently, collecting all errors rather than failing fast.

### 4. Command Pattern (CLI Dispatch)

**Location:** `scripts/ontology.py:423-576`

The argparse subcommand structure maps CLI commands to domain operations:
- `create` → `create_entity()`
- `get` → `get_entity()`
- `query` → `query_entities()`
- `relate` → `create_relation()`
- `validate` → `validate_graph()`
- `schema-append` → `append_schema()`

### 5. Deep Merge Pattern (Schema Composition)

**Location:** `scripts/ontology.py:403-420`

`merge_schema()` recursively merges schema fragments:
- Dicts are deep-merged
- Lists are appended (with deduplication)
- Scalars are overwritten

This supports the "append-only" schema evolution strategy — new types and constraints can be added incrementally without overwriting existing definitions.

### 6. Guard/Gatekeeper Pattern (Path Security)

**Location:** `scripts/ontology.py:26-57`

`resolve_safe_path()` acts as a security gate:
1. Resolves the path to absolute
2. Verifies it stays within workspace root via `relative_to()`
3. Optionally checks existence
4. Raises `SystemExit` on violation

## Anti-Patterns / Concerns

| Concern | Details |
|---------|---------|
| Full replay on every read | `load_graph()` replays the entire JSONL on each call — O(n) with log size |
| No caching | No in-memory graph cache between operations |
| No locking | No file locking for concurrent access |
| Lazy import | `import yaml` inside functions (acceptable for optional dependency) |
