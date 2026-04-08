---
name: x-ipe-tool-ontology
description: Manage knowledge base ontology — entity CRUD, dimension registry, graph clustering, and search. Use for tagging KB content, building ontology graphs, searching knowledge nodes. Triggers on requests like "create entity", "tag content", "build graph", "search ontology", "register dimension".
---

# KB Ontology Tool Skill

## Purpose

Provides the runtime engine for the Knowledge Base Ontology system. Manages KnowledgeNode entities, typed relations, dimension taxonomy, graph clustering, and search — all backed by append-only JSONL event sourcing.

## Data Storage

| Store | Location | Format |
|-------|----------|--------|
| Master entities | `x-ipe-docs/knowledge-base/.ontology/_entities.jsonl` | Append-only JSONL events |
| Named graphs | `x-ipe-docs/knowledge-base/.ontology/{cluster}.jsonl` | Derived views (auto-generated) |
| Dimension registry | `x-ipe-docs/knowledge-base/.ontology/.dimension-registry.json` | JSON taxonomy |

## Available Scripts

All scripts are in `.github/skills/x-ipe-tool-ontology/scripts/`.

### Entity Operations (`ontology.py`)

| Command | Purpose | Example |
|---------|---------|---------|
| `create` | Create KnowledgeNode | `python3 ontology.py create --type KnowledgeNode --props '{"label":"JWT Auth","node_type":"concept","source_files":["src/auth.py"]}' --graph PATH` |
| `get` | Get entity by ID | `python3 ontology.py get --id know_abc123 --graph PATH` |
| `update` | Update properties | `python3 ontology.py update --id know_abc123 --props '{"weight":8}' --graph PATH` |
| `delete` | Delete entity | `python3 ontology.py delete --id know_abc123 --graph PATH` |
| `list` | List entities | `python3 ontology.py list [--type KnowledgeNode] --graph PATH` |
| `query` | Filter by properties | `python3 ontology.py query --type KnowledgeNode --where '{"node_type":"concept"}' --graph PATH` |
| `relate` | Create relation | `python3 ontology.py relate --from ID1 --rel depends_on --to ID2 --graph PATH` |
| `related` | Get related entities | `python3 ontology.py related --id ID [--rel TYPE] [--dir outgoing] --graph PATH` |
| `find-path` | BFS shortest path | `python3 ontology.py find-path --from ID1 --to ID2 --graph PATH` |
| `validate` | Validate constraints | `python3 ontology.py validate --graph PATH` |
| `load` | Load full graph state | `python3 ontology.py load --graph PATH` |

### Dimension Registry (`dimension_registry.py`)

| Command | Purpose | Example |
|---------|---------|---------|
| `resolve` | Resolve name/alias | `python3 dimension_registry.py resolve --name tech --registry PATH` |
| `register` | Register dimension | `python3 dimension_registry.py register --dimension '{"name":"technology","type":"multi-value","examples":["Python"]}' --registry PATH` |
| `list` | List dimensions | `python3 dimension_registry.py list --registry PATH` |
| `rebuild` | Rebuild from entities | `python3 dimension_registry.py rebuild --entities PATH --registry PATH` |

### Graph Operations (`graph_ops.py`)

| Command | Purpose | Example |
|---------|---------|---------|
| `build` | Build named graphs | `python3 graph_ops.py build --scope PATH --output PATH [--entities PATH]` |
| `prune` | Remove stale refs | `python3 graph_ops.py prune --entities PATH` |

### Search (`search.py`)

| Arguments | Purpose | Example |
|-----------|---------|---------|
| `--query --scope --ontology-dir` | Search entities | `python3 search.py --query "auth" --scope all --ontology-dir PATH [--depth 3] [--page-size 20] [--page 1]` |

## Three Operations (AI Agent Workflow)

### Operation A: Tag (格物→致知)

AI agent reads KB content, discovers dimensions, resolves aliases via dimension registry, and creates entities/relations. The agent orchestrates this operation by:

1. Reading source content files
2. Analyzing content to identify knowledge concepts
3. Calling `dimension_registry.py resolve` for each discovered dimension
4. Calling `dimension_registry.py register` for new dimensions
5. Calling `ontology.py create` for each entity
6. Calling `ontology.py relate` for relationships between entities

### Operation B: Build Graph

Automated script that builds named graph files from the master entity store:

```bash
python3 graph_ops.py build \
    --scope x-ipe-docs/knowledge-base/ \
    --output x-ipe-docs/knowledge-base/.ontology/ \
    --entities x-ipe-docs/knowledge-base/.ontology/_entities.jsonl
```

### Operation C: Search

Automated script for searching across ontology graphs:

```bash
python3 search.py \
    --query "authentication" \
    --scope all \
    --ontology-dir x-ipe-docs/knowledge-base/.ontology/
```

## Entity Model

### KnowledgeNode Properties

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `label` | string | ✅ | Human-readable name |
| `node_type` | string | ✅ | `concept`, `entity`, or `document` |
| `description` | string | ❌ | Brief summary |
| `dimensions` | object | ❌ | Canonical dimension keys → values |
| `source_files` | string[] | ✅ | Project-root-relative paths |
| `weight` | number | ❌ | 1-10 (default: 5) |

### Relation Types

| Type | Acyclic | Description |
|------|---------|-------------|
| `related_to` | No | Bidirectional topical overlap |
| `depends_on` | **Yes** | Understanding dependency |
| `is_type_of` | No | Taxonomy/classification |
| `part_of` | No | Component composition |
| `described_by` | No | Explanatory relation |

### Entity ID Format

All IDs follow the pattern `know_{uuid_hex[:8]}` (e.g., `know_a1b2c3d4`).

## Output Format

All scripts output JSON to stdout. Errors output JSON `{"error": "message"}` with exit code 1.

## Dependencies

Python stdlib only — no external packages required.

## References

- [Dimension Guidelines](references/dimension-guidelines.md) — Naming guidance for AI agents when tagging content
