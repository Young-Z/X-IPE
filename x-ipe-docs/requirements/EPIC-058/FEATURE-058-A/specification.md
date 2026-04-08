# Feature Specification: Ontology Tool Skill (x-ipe-tool-ontology)

> Feature ID: FEATURE-058-A  
> Version: v1.0  
> Status: Refined  
> Last Updated: 04-08-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-08-2026 | Initial specification — merged from original FEATURE-058-A/B/C |

## Linked Mockups

*No mockups linked — FEATURE-058-A is a backend tool skill. The Graph Viewer mockup applies to FEATURE-058-E/F.*

## Overview

This feature creates `x-ipe-tool-ontology`, a new tool-type skill that extends the proven ontology-1.0.4 data engine (581-line Python module) with KB-specific intelligence. The skill provides three operations: **(A) Knowledge Tagging** — AI-driven content analysis following the 格物→致知 methodology (study broadly, then derive understanding), with dynamic dimension discovery and normalization; **(B) Graph Creation** — collects tagged entities, builds knowledge graphs, detects disconnected clusters, and auto-splits into per-cluster JSONL files; **(C) Knowledge Search** — text matching combined with BFS graph traversal supporting multi-graph cross-search.

**Why:** The current 2-dimensional tagging (lifecycle × domain) loses all semantic richness. A document about "JWT authentication patterns for Python Flask APIs" gets tagged merely as `active` + `backend`. No inter-document relationships are captured. This skill enables multi-dimensional, AI-driven knowledge tagging with graph-based relationship discovery.

**Who:** AI agents operating within X-IPE skills (primary consumer — the KB Librarian calls this tool during `.intake/` processing). Developers interact with the knowledge graph indirectly through the Graph Viewer UI (FEATURE-058-E/F).

## User Stories

- As an **AI Librarian agent**, I want to tag knowledge base files with multi-dimensional metadata, so that knowledge can be categorized beyond the basic 2D (lifecycle × domain) system.
- As an **AI Librarian agent**, I want relationships between knowledge pieces (e.g., "auth-guide depends_on oauth2-spec") to be captured as typed edges, so that graph-based discovery is possible.
- As an **AI Librarian agent**, I want to create knowledge graphs from tagged entities and have disconnected clusters auto-split into separate files, so that each graph represents a coherent knowledge domain.
- As an **AI agent performing research**, I want to search knowledge graphs using text matching and BFS traversal, so that I can discover related knowledge beyond simple keyword search.
- As an **AI agent**, I want to search across multiple graph files simultaneously, so that I can find knowledge spanning different domains.
- As a **knowledge author**, I want the tagging system to dynamically discover relevant dimensions for my content (not limited to a predefined set), so that diverse knowledge types are accurately categorized.

## Acceptance Criteria

### AC-058A-01: Skill Structure & Engine Integration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-01a | GIVEN the X-IPE project WHEN the skill folder is inspected THEN `.github/skills/x-ipe-tool-ontology/SKILL.md` exists with valid skill metadata | Unit |
| AC-058A-01b | GIVEN the ontology tool is loaded WHEN it initializes THEN it successfully provides a standalone `ontology.py` engine (design-referenced from ontology-1.0.4) as a module | Unit |
| AC-058A-01c | GIVEN the ontology tool is loaded WHEN it initializes THEN it has access to all engine functions: `create_entity`, `get_entity`, `update_entity`, `delete_entity`, `list_entities`, `query_entities`, `get_related`, `find_path`, `create_relation`, `validate_graph`, `load_graph`, `append_op`, `merge_schema`, `generate_id`, `resolve_safe_path` | Unit |

### AC-058A-02: Operation A — 格物 Phase (Study Content)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-02a | GIVEN a single markdown file WHEN the tag operation is invoked THEN the 格物 phase reads the full file content and analyzes its domain, concepts, and relationships | Unit |
| AC-058A-02b | GIVEN a folder with multiple files WHEN the tag operation is invoked with folder path THEN the 格物 phase analyzes all files recursively | Unit |
| AC-058A-02c | GIVEN content about an unfamiliar topic AND `x-ipe-tool-web-search` is available WHEN the 格物 phase runs THEN it calls web search for additional context | Integration |
| AC-058A-02d | GIVEN content about an unfamiliar topic AND `x-ipe-tool-web-search` is NOT available WHEN the 格物 phase runs THEN it degrades gracefully and continues without web research | Unit |
| AC-058A-02e | GIVEN a folder where all files share the same topic WHEN the tag operation is invoked THEN a single folder-level KnowledgeNode is created (not per-file) | Unit |
| AC-058A-02f | GIVEN a folder where files cover distinct topics WHEN the tag operation is invoked THEN individual file-level KnowledgeNodes are created for each file | Unit |

### AC-058A-03: Operation A — 致知 Phase (Discover Dimensions & Create Entities)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-03a | GIVEN the 格物 phase has completed content analysis WHEN the 致知 phase runs THEN it dynamically discovers tagging dimensions relevant to the content (no predefined set) | Unit |
| AC-058A-03b | GIVEN discovered dimensions WHEN a KnowledgeNode entity is created THEN `create_entity()` is called with type `KnowledgeNode` and properties: label, node_type, description, dimensions (object), source_files (string[]), weight (number) | Unit |
| AC-058A-03c | GIVEN the content is a specification document WHEN the AI classifies the node type THEN it assigns `type: "document"` | Unit |
| AC-058A-03d | GIVEN the content describes an abstract pattern or methodology WHEN the AI classifies the node type THEN it assigns `type: "concept"` | Unit |
| AC-058A-03e | GIVEN the content describes a concrete system, tool, or named thing WHEN the AI classifies the node type THEN it assigns `type: "entity"` | Unit |
| AC-058A-03f | GIVEN the content is foundational and widely referenced WHEN the AI assigns weight THEN it assigns a higher weight (e.g., 7-10) based on importance | Unit |
| AC-058A-03g | GIVEN the content is peripheral or narrowly scoped WHEN the AI assigns weight THEN it assigns a lower weight (e.g., 1-3) based on importance | Unit |
| AC-058A-03h | GIVEN a new entity is created WHEN the entity ID is generated THEN it follows the `know_{uuid_hex[:8]}` format | Unit |

### AC-058A-04: Operation A — Relation Creation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-04a | GIVEN two knowledge nodes with topical overlap WHEN relations are created THEN a `related_to` typed relation is created via `create_relation()` | Unit |
| AC-058A-04b | GIVEN a knowledge node that requires understanding of another WHEN relations are created THEN a `depends_on` typed relation is created (must be acyclic) | Unit |
| AC-058A-04c | GIVEN a knowledge node that is a specific instance of a category WHEN relations are created THEN an `is_type_of` typed relation is created | Unit |
| AC-058A-04d | GIVEN a knowledge node that is a component of a larger topic WHEN relations are created THEN a `part_of` typed relation is created | Unit |
| AC-058A-04e | GIVEN a knowledge node that provides explanatory content for another WHEN relations are created THEN a `described_by` typed relation is created | Unit |
| AC-058A-04f | GIVEN a `depends_on` relation being created WHEN the relation would create a cycle THEN the relation is rejected with an error | Unit |

### AC-058A-05: Operation A — Dimension Registry & Schema Evolution

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-05a | GIVEN a newly discovered dimension (e.g., "technology") WHEN it doesn't exist in the schema THEN it is appended via `merge_schema()` deep merge without overwriting existing dimensions | Unit |
| AC-058A-05b | GIVEN a dimension alias (e.g., "target-audience") WHEN it maps to a canonical name in `.dimension-registry.json` (e.g., "audience") THEN the canonical name is used in the entity | Unit |
| AC-058A-05c | GIVEN `.dimension-registry.json` does not exist WHEN the first tagging operation runs THEN the file is created with initial dimensions and empty aliases | Unit |
| AC-058A-05d | GIVEN a dimension of type `multi-value` (e.g., "topic") WHEN it is assigned to a KnowledgeNode THEN the value is stored as an array (e.g., `["authentication", "security"]`) | Unit |
| AC-058A-05e | GIVEN a dimension of type `single-value` (e.g., "abstraction") WHEN it is assigned to a KnowledgeNode THEN the value is stored as a single string (e.g., `"pattern"`) | Unit |
| AC-058A-05f | GIVEN the KnowledgeDimension schema WHEN a dimension is registered THEN it has properties: name (string), type (single-value/multi-value), examples (string[]?), aliases (string[]) | Unit |

### AC-058A-06: Operation A — Entity CRUD & Re-tagging

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-06a | GIVEN a file that has never been tagged WHEN the tag operation runs THEN a new KnowledgeNode entity is created via `create_entity()` | Unit |
| AC-058A-06b | GIVEN a file whose content has been updated AND an existing KnowledgeNode exists WHEN the tag operation runs THEN the entity is updated via `update_entity()` with new dimensions appended and description refreshed | Unit |
| AC-058A-06c | GIVEN a file that has been deleted from the KB WHEN the tag operation detects the missing file THEN the corresponding KnowledgeNode is deleted via `delete_entity()` | Unit |
| AC-058A-06d | GIVEN an entity being updated WHEN new dimensions are discovered THEN existing dimensions are preserved and new ones are merged (not replaced) | Unit |

### AC-058A-07: Operation A — Output Contract

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-07a | GIVEN a successful tagging operation WHEN the operation completes THEN it returns a structured result containing: list of created entity IDs, list of updated entity IDs, dimensions discovered (new and existing), and relations created | Unit |
| AC-058A-07b | GIVEN a tagging operation that processes 5 files WHEN it completes THEN the result includes per-file status (created/updated/skipped) with entity ID | Unit |
| AC-058A-07c | GIVEN a tagging operation that encounters an error on one file WHEN processing continues THEN the error is logged and other files continue processing AND the result includes the error details for the failed file | Unit |

### AC-058A-08: Operation B — Graph Creation & Collection

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-08a | GIVEN a folder path with tagged entities WHEN the graph creation operation is invoked THEN all `KnowledgeNode` entities under that path are collected via `load_graph()` with scope path filtering on `source_files` | Unit |
| AC-058A-08b | GIVEN collected entities and relations WHEN the graph is built THEN a graph-centric ontology structure is created with nodes and edges | Unit |
| AC-058A-08c | GIVEN a graph with all connected nodes WHEN graph creation completes THEN a single `.jsonl` file is saved to `x-ipe-docs/knowledge-base/.ontology/{root-node-name}.jsonl` | Unit |
| AC-058A-08d | GIVEN graph creation WHEN determining the root node name THEN the node with the highest degree (most connections) is used as the file name | Unit |

### AC-058A-09: Operation B — Cluster Detection & Auto-Split

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-09a | GIVEN a graph with two disconnected subgraphs WHEN cluster detection runs THEN two separate clusters are identified | Unit |
| AC-058A-09b | GIVEN two identified clusters WHEN auto-split executes THEN each cluster is saved as a separate `.jsonl` file named after its highest-degree node | Unit |
| AC-058A-09c | GIVEN a graph with all nodes connected WHEN cluster detection runs THEN a single cluster is identified (no split) | Unit |
| AC-058A-09d | GIVEN graph recreation WHEN the operation completes THEN it is a full rebuild (all entities loaded, not incremental) | Unit |

### AC-058A-10: Operation B — Stale Reference Pruning & Validation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-10a | GIVEN a KnowledgeNode with `source_files: ["path/to/deleted-file.md"]` WHEN graph recreation validates file paths THEN the stale reference is detected | Unit |
| AC-058A-10b | GIVEN a detected stale reference WHEN pruning executes THEN the entity is updated (remove stale path) or deleted (if no valid paths remain) via `update_entity()` / `delete_entity()` | Unit |
| AC-058A-10c | GIVEN the completed graph WHEN validation runs via `validate_graph()` THEN KB-specific schema constraints are checked (acyclicity on `depends_on`, valid entity types, required properties) | Unit |
| AC-058A-10d | GIVEN JSONL event log WHEN mutations are appended THEN the append-only format preserves full mutation history for audit trail and crash recovery | Unit |

### AC-058A-11: Operation C — Text & BFS Search

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-11a | GIVEN a search query "authentication" AND a loaded graph WHEN the search operation runs THEN entities with matching labels or metadata are returned via `query_entities()` | Unit |
| AC-058A-11b | GIVEN matched entities WHEN BFS traversal is requested with depth=2 THEN related nodes within 2 hops are returned via BFS subgraph traversal (`_bfs_subgraph()` in `search.py`) | Unit |
| AC-058A-11c | GIVEN no depth parameter specified WHEN BFS search runs THEN a default depth of 3 is used | Unit |
| AC-058A-11d | GIVEN matched nodes and traversed subgraph WHEN results are returned THEN full metadata is included: dimensions, descriptions, source_files, weight | Unit |

### AC-058A-12: Operation C — Multi-Graph Cross-Search

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-12a | GIVEN a search query AND scope="all" WHEN the search operation runs THEN all `.jsonl` graph files in `x-ipe-docs/knowledge-base/.ontology/` are searched simultaneously | Unit |
| AC-058A-12b | GIVEN a search query AND scope=["graph-a.jsonl", "graph-b.jsonl"] WHEN the search operation runs THEN only the specified graph files are searched | Unit |
| AC-058A-12c | GIVEN results from multiple graph files WHEN results are returned THEN each result includes the graph file provenance (which `.jsonl` file it came from) | Unit |
| AC-058A-12d | GIVEN a large result set from cross-graph search WHEN results are returned THEN pagination is supported with configurable page size | Unit |

### AC-058A-13: JSONL Event-Sourced Storage

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058A-13a | GIVEN a create/update/delete operation WHEN the mutation is persisted THEN it is appended as a JSONL event with `op`, entity/relation data, and ISO 8601 `timestamp` | Unit |
| AC-058A-13b | GIVEN an existing `.jsonl` file WHEN `load_graph()` replays events THEN the current state is correctly reconstructed from the event log | Unit |
| AC-058A-13c | GIVEN a crash during append WHEN the file is reloaded THEN partial writes are detected and skipped (valid lines are replayed) | Unit |

> **Test Type Legend:**
> - **Unit** — Isolated function/module test (parsing, calculations, entity operations)
> - **Integration** — Multi-component interaction test (skill + web search, skill + file system)

## Functional Requirements

### FR-1: Knowledge Tagging Operation

**Description:** Accept a file path or folder path and produce multi-dimensional KnowledgeNode entities with typed relations.

**Details:**
- Input: File path or folder path, optional existing graph context
- Process: 格物 (content analysis) → 致知 (dimension discovery + entity creation)
- Output: Structured result with entity IDs, dimensions, relations

### FR-2: Graph Creation Operation

**Description:** Collect all tagged entities under a folder, build a graph, detect clusters, auto-split, and persist as JSONL files.

**Details:**
- Input: Folder path (scope for entity collection)
- Process: Load entities → Build graph → Detect clusters → Split → Validate → Save
- Output: List of `.jsonl` graph files created in `x-ipe-docs/knowledge-base/.ontology/`

### FR-3: Knowledge Search Operation

**Description:** Search knowledge graphs by text matching and BFS traversal with configurable depth.

**Details:**
- Input: Query string, search scope (graph file(s) or "all"), optional depth parameter
- Process: Text match → BFS traverse → Aggregate results across graphs
- Output: Matched nodes + subgraph with full metadata and provenance

### FR-4: Dimension Registry Management

**Description:** Maintain a `.dimension-registry.json` file that normalizes dimension names and prevents concept drift.

**Details:**
- Input: Newly discovered dimensions from 致知 phase
- Process: Check aliases → Resolve canonical name → Append if new → Update examples
- Output: Updated registry file

## Non-Functional Requirements

### NFR-1: Performance

- Tagging a single file: < 30 seconds (excluding web search)
- Graph creation for 200-file collection: < 60 seconds
- JSONL replay for 200-file graph: < 5 seconds
- Search across 5 graphs (200 entities each): < 3 seconds

### NFR-2: Reliability

- Crash recovery via JSONL event replay (no data loss on partial writes)
- Graceful degradation when web search unavailable
- File-level error isolation (one file failure doesn't block batch)

### NFR-3: Scalability

- Designed for KBs up to ~200 files per collection (v1 ceiling)
- SQLite migration path documented in ontology-1.0.4 for future scale needs
- Append-only JSONL enables efficient incremental tagging

## Dependencies

### Internal Dependencies

- **ontology-1.0.4 engine (design reference):** The `ontology.py` script from ontology-1.0.4 was used as a design blueprint. The implementation is a standalone purpose-built module (~695 lines) providing entity CRUD, relation management, schema validation, BFS traversal, JSONL event sourcing, and graph validation
- **x-ipe-tool-web-search:** Optional — used during 格物 phase for unfamiliar content research

### External Dependencies

- **Python 3.10+:** Required for ontology.py engine compatibility
- **Python stdlib only:** No external packages required (PyYAML dependency from ontology-1.0.4 was dropped in favor of JSON-only approach)

## Business Rules

- **BR-1:** All entity mutations must be recorded as JSONL events — no direct file overwrites
- **BR-2:** Dimension aliases must be resolved to canonical names before entity storage
- **BR-3:** `depends_on` relations must be acyclic — reject cycles with error
- **BR-4:** Entity IDs must follow `know_{uuid_hex[:8]}` format for consistency with ontology-1.0.4
- **BR-5:** Folder-level tagging creates one node when all files share the same topic; file-level tagging when content is diverse
- **BR-6:** Graph recreation is always a full rebuild (not incremental) to enable accurate cluster detection
- **BR-7:** Root node naming uses the highest-degree node in each cluster

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty folder (no files to tag) | Return empty result with zero entities created |
| File with no discernible topic | Create KnowledgeNode with minimal dimensions (type=document, basic label from filename) |
| Duplicate tagging of same file | Update existing entity — merge new dimensions, refresh description |
| File deleted between tagging and graph creation | Prune stale reference; delete entity if no valid source_files remain |
| `.dimension-registry.json` corrupted | Recreate from existing entities' dimensions with warning |
| All nodes in graph are disconnected (no edges) | Each node becomes its own single-node cluster/file |
| Circular `depends_on` detected | Reject the relation with error; all other relations in the batch proceed |
| Cross-graph search with no matching results | Return empty result set with zero matches |
| JSONL file with partial/corrupted last line | Skip corrupted line during replay; log warning |

## Out of Scope

- Graph Viewer UI rendering (FEATURE-058-E)
- Search bar UI and AI Agent terminal (FEATURE-058-F)
- KB Librarian integration and intake pipeline changes (FEATURE-058-D)
- Graph editing from UI (not in any feature)
- Re-tagging from UI (only via skill invocation)
- SQLite migration (documented path, not v1 scope)
- Real-time collaborative graph operations
- Confidence scores on AI-generated dimensions (open question — deferred)

## Technical Considerations

- **Skill architecture:** Agent-driven with Python scripts for data ops. The AI agent handles content analysis (格物→致知), while Python scripts in `.github/skills/x-ipe-tool-ontology/scripts/` handle deterministic operations (entity CRUD, graph creation, cluster detection, BFS search, JSONL storage).
- **Engine strategy:** Create our own `ontology.py` in `.github/skills/x-ipe-tool-ontology/scripts/`, purpose-built for KB context. Reference ontology-1.0.4 as a design blueprint — do NOT copy or import the original.
- **JSONL storage location:** Single `x-ipe-docs/knowledge-base/.ontology/` folder for all KB content. Cross-graph search scans across multiple `.jsonl` files within this single folder.
- **Dimension registry location:** `x-ipe-docs/knowledge-base/.ontology/.dimension-registry.json`
- **Thread safety:** Dimension registry updates must handle concurrent access (file locking or similar mechanism)
- **Event log format:** Each line is a valid JSON object with `op` (create/update/delete/relate), entity/relation data, and ISO 8601 timestamp
- **BFS default depth:** 3 hops (configurable via depth parameter)
- **Performance ceiling:** ~200 files per collection; beyond this, consider SQLite migration per ontology-1.0.4 documentation
- **Operation preconditions:** Guard each operation with clear error messages (e.g., "No entities found — run tagging first" for graph creation on empty scope)
- **Delivery:** All 3 operations delivered atomically as one feature

## Open Questions

1. Should the dimension registry support confidence scores for AI-generated dimensions? (Deferred from requirement gathering)
2. What is the maximum BFS depth for cross-graph search spanning multiple collections?
3. Should graph files be versioned (e.g., keep previous generation for diff/rollback)?
