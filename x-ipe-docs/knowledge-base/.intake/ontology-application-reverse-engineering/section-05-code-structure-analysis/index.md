# Section 05 — Code Structure Analysis

## Overview

The ontology skill is organized as a self-contained skill package following X-IPE skill conventions. It contains 5 meaningful files across 3 directories.

## Directory Tree

```
ontology-1.0.4/
├── SKILL.md              # Main skill specification (232 lines)
├── _meta.json            # Skill registry metadata (5 lines)
├── references/
│   ├── schema.md         # Full type definitions & constraints (323 lines)
│   └── queries.md        # Query patterns & traversal examples (212 lines)
└── scripts/
    └── ontology.py       # CLI + library implementation (581 lines)
```

## Module Inventory

| Module | File | Purpose | LOC |
|--------|------|---------|-----|
| Specification | `SKILL.md` | Defines triggers, core types, workflows, integration patterns, constraints | 232 |
| Type Schema | `references/schema.md` | Complete type definitions, relation types, global constraints in YAML | 323 |
| Query Reference | `references/queries.md` | CLI and Python query patterns, traversal examples, aggregation recipes | 212 |
| Implementation | `scripts/ontology.py` | Python CLI tool with entity CRUD, relation ops, validation, schema management | 581 |
| Metadata | `_meta.json` | Skill identity (ownerId, slug, version, publishedAt) | 5 |

## File Statistics

- **Total files:** 5 (excl. .DS_Store)
- **Total size:** ~40.5 KB
- **Primary language:** Python (1 file, 581 lines)
- **Documentation:** Markdown (3 files, ~767 lines)
- **Data:** JSON (1 file, 5 lines)

## Naming Conventions

- Skill root named by slug + version: `ontology-1.0.4/`
- References stored in `references/` subdirectory
- Scripts stored in `scripts/` subdirectory
- Entry point: `scripts/ontology.py` (used as both CLI and importable library)

## Entry Points

1. **CLI:** `python3 scripts/ontology.py <command>` — 9 subcommands
2. **Library:** `from scripts.ontology import load_graph, query_entities, get_related, create_entity`
