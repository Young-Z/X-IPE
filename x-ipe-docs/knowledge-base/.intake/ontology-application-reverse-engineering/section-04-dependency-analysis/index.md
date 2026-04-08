# Section 04 — Dependency Analysis

## External Dependencies

| Package | Import Location | Purpose | Required |
|---------|----------------|---------|----------|
| PyYAML (`yaml`) | `ontology.py:388, 399, 572` | Schema file I/O (YAML format) | Only for schema operations |

PyYAML is imported lazily (inside functions `load_schema()`, `write_schema()`, and `schema-append` command) — the tool works for entity/relation operations without PyYAML installed.

## Standard Library Dependencies

| Module | Import Line | Functions Used |
|--------|-------------|---------------|
| `argparse` | line 16 | `ArgumentParser`, `add_subparsers` |
| `json` | line 17 | `loads`, `dumps`, `load` |
| `uuid` | line 18 | `uuid4()` |
| `datetime` | line 19 | `datetime.now(timezone.utc).isoformat()`, `datetime.fromisoformat()` |
| `pathlib` | line 20 | `Path`, `resolve()`, `exists()`, `parent`, `mkdir()`, `relative_to()` |

## Internal Module Dependencies

The skill is a **single-module** design — all logic lives in `scripts/ontology.py`. There are no internal module imports.

## Call Graph (Simplified)

```
main()
├── create  → create_entity() → append_op()
├── get     → get_entity() → load_graph()
├── query   → query_entities() → load_graph()
├── list    → list_entities() → load_graph()
├── update  → update_entity() → load_graph() + append_op()
├── delete  → delete_entity() → load_graph() + append_op()
├── relate  → create_relation() → append_op()
├── related → get_related() → load_graph()
├── validate → validate_graph() → load_graph() + load_schema()
└── schema-append → append_schema() → load_schema() + merge_schema() + write_schema()
```

## Dependency Characteristics

| Characteristic | Value |
|---------------|-------|
| Total external deps | 1 (PyYAML, optional) |
| Stdlib deps | 5 |
| Internal module deps | 0 |
| Coupling level | Very low — self-contained single file |
| Portability | High — runs on any Python 3.10+ with optional PyYAML |

## Skill-Level Dependencies (from SKILL.md)

The ontology skill declares **Skill Contracts** — other skills can declare ontology reads/writes:

```yaml
ontology:
  reads: [Task, Project, Person]
  writes: [Task, Action]
  preconditions:
    - "Task.assignee must exist"
  postconditions:
    - "Created Task has status=open"
```

This establishes a loosely-coupled integration pattern where consuming skills declare their data dependencies declaratively.
