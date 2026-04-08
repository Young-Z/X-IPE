# Requirement Details - Part 24

> Continued from: [requirement-details-part-23.md](x-ipe-docs/requirements/requirement-details-part-23.md)
> Created: 04-08-2026

---

## EPIC-058: Feature-Ontology for Knowledgebase

> Version: 1.0
> Source Idea: [IDEA-040 — Feature-Ontology for Knowledgebase](x-ipe-docs/ideas/40.%20Feature-Ontology%20For%20Knowledgebase/refined-idea/idea-summary-v2.md)
> Depends On: ontology-1.0.4 data engine ([Research-Ontology](x-ipe-docs/ideas/103.%20Research-Ontology/ontology-1.0.4/))
> Related Epics: EPIC-049 (KB Management — CR for librarian ontology integration), EPIC-050 (Knowledge Extraction — CR for intake contract), EPIC-023 (Tracing — CR to standardize graph library)

### Project Overview

Replace the basic 2-dimensional knowledge tagging system (lifecycle × domain) in X-IPE's knowledge base with an **ontology-based, multi-dimensional knowledge graph system** built on top of the proven **ontology-1.0.4** data engine. This introduces a new `x-ipe-tool-ontology` skill for deep content analysis (格物→致知), dynamic dimension discovery, knowledge graph construction with auto-split clustering, and graph-based semantic search — backed by an interactive Cytoscape.js graph viewer in the KB UI.

**Why this matters:** The current 2D tagging (lifecycle + domain) loses all semantic richness. A document about "JWT authentication patterns for Python Flask APIs" gets tagged merely as `active` + `backend`. No relationships between knowledge pieces are captured, and search is limited to flat text matching.

### User Request

Build a 4-component ontology system for the knowledge base:
1. **Ontology Tool** — AI-driven tagging skill extending ontology-1.0.4 with knowledge tagging, graph creation, and search
2. **Updated KB Librarian** — Integrate ontology tool into the `.intake/` processing pipeline
3. **Ontology Graph Viewer** — Interactive Cytoscape.js-based UI for exploring knowledge graphs
4. **Data Layer** — KnowledgeNode entity model, JSONL event sourcing, dimension registry

### Clarifications

| Question | Answer |
|----------|--------|
| Tagging granularity? | File → multiple nodes if content covers distinct topics; folder → one node if single-topic folder |
| UI integration? | New "knowledge graph" icon beside KB icon, opens separate graph viewer (like workflow mode) |
| Re-tagging support? | No re-tagging from UI; only tag during `.intake/` processing by AI Librarian; graph auto-updated after tagging |
| Graph editing? | Read-only viewer only (browse, search, explore — no add/remove from UI) |
| Storage location? | `knowledge-base/.ontology/` (inside KB folder) |
| Search scope? | All three types are MVP: text search, graph BFS traversal, AI Agent terminal search |
| Multi-KB cross-graph search? | Supported — search can span across multiple graph files simultaneously |

### High-Level Requirements

1. **Ontology Tool Skill (`x-ipe-tool-ontology`):** Create a new tool-type skill wrapping and extending ontology-1.0.4's engine (581-line Python module). The skill provides three operations: (A) Knowledge Tagging — AI-driven content analysis (格物→致知) with dynamic dimension discovery and normalization, (B) Graph Creation — collect tagged entities, build graph, detect disconnected clusters, auto-split into per-cluster JSONL files, (C) Knowledge Search — text matching + BFS traversal via `find_path()` and `get_related()` with configurable depth.

2. **KnowledgeNode Entity Model:** Extend ontology-1.0.4's typed entity system with a `KnowledgeNode` type (label, type, description, dimensions, source_files, weight) and `KnowledgeDimension` type. Add 5 typed relations: `related_to`, `depends_on` (acyclic), `is_type_of`, `part_of`, `described_by`.

3. **Dynamic Dimension Discovery:** During the 致知 (Generate Tags) phase, the AI determines relevant tagging dimensions per knowledge piece — no predefined dimension set. New dimensions are appended to the YAML schema via `merge_schema()` deep merge. A `.dimension-registry.json` maps aliases to canonical names (e.g., "target-audience" → "audience") to prevent concept drift.

4. **JSONL Event-Sourced Storage:** All mutations stored as append-only JSONL event logs in `knowledge-base/.ontology/{root-node-name}.jsonl`. Provides full audit trail, crash recovery, and incremental update support. Root node naming uses highest-degree node in each cluster.

5. **Auto-Split Graph Clustering:** During graph creation, detect disconnected subgraphs and split into separate `.jsonl` files automatically. Validate referenced file paths still exist — prune stale references. Validate graph integrity via `validate_graph()` with KB-specific schema constraints.

6. **Updated AI Librarian (`x-ipe-tool-kb-librarian`):** During `.intake/` processing, call ontology tool for multi-dimensional tagging (replaces basic 2D domain assignment). Lifecycle tags remain in `.kb-index.json` as operational metadata. After each tagging batch, always recreate affected graphs. Declare ontology skill contract (reads, writes, pre/postconditions).

7. **Ontology Graph Viewer (Frontend):** Split-panel layout: left = ontology graph file list with Select All, right = interactive Cytoscape.js visualization. Features: 3-option layout picker (fcose/dagre/concentric), radial context menus, navigator minimap, tippy tooltips, zoom controls, search bar, and AI Agent terminal integration.

8. **Text Search:** Wildcard text search under selected graph scope. Matching nodes highlighted on the graph with info panel display.

9. **BFS Graph Search:** Match query to KnowledgeNode entities via label/metadata text matching using `query_entities()`. BFS traversal from matched nodes via `find_path()` + `get_related()` with configurable depth. Return matched nodes + related subgraph.

10. **AI Agent Terminal Search:** "Search with AI Agent" button opens X-IPE terminal overlay, auto-types prompt template with selected graph scope, waits for user's natural language query.

11. **Multi-KB Cross-Graph Search:** Search can span across multiple graph files simultaneously. The search scope selector (expandable multi-select dropdown) allows selecting any combination of available graph files for unified search results.

12. **Cytoscape.js Plugin Stack:** Use 5 plugins — `cytoscape-fcose` (force-directed layout), `cytoscape-dagre` (hierarchical layout), `cytoscape-cxtmenu` (radial context menus), `cytoscape-navigator` (minimap), `tippy.js` (tooltips). All verified working via CDN.

### Constraints

- **Scale ceiling:** Designed for KBs up to ~200 files per collection. JSONL full-replay on read is the bottleneck. SQLite migration path documented in ontology-1.0.4 for future scale needs.
- **Graph recreation is full rebuild:** Disconnected cluster detection requires loading all entities. JSONL append-only storage makes incremental tagging efficient.
- **Dimension consistency:** The running dimension registry + `merge_schema()` deep merge is critical for preventing concept drift.
- **Read-only viewer:** No graph editing from UI — only browse, search, explore.
- **No re-tagging from UI:** Tagging only happens during `.intake/` processing.
- **Python 3.10+ required:** ontology.py engine dependency.
- **Web search dependency:** The 格物 phase may call `x-ipe-tool-web-search` (requires agent web capability).
- **AI Agent terminal integration:** Depends on X-IPE terminal being available and a CLI agent being active.
- **ontology-1.0.4 dependency:** The engine script must be vendored or imported as a module.

### Scope

**In Scope (MVP):**
- `x-ipe-tool-ontology` skill with 3 operations (tag, graph create, search)
- KnowledgeNode entity model extending ontology-1.0.4
- Dynamic dimension discovery with dimension registry normalization
- JSONL event-sourced storage in `knowledge-base/.ontology/`
- Auto-split disconnected clusters into separate graph files
- Update `x-ipe-tool-kb-librarian` to call ontology tool during intake
- Ontology Graph Viewer UI (Cytoscape.js + 5 plugins, 3 layouts)
- Text search + BFS graph search + AI Agent terminal search
- Multi-KB cross-graph search (span multiple graph files)
- Read-only graph viewer

**Out of Scope:**
- Graph editing (add/remove nodes from UI)
- Re-tagging from UI (only during intake processing)
- SQLite migration (documented as future path for >200 files)
- G6→Cytoscape.js migration for EPIC-023 (separate future CR)
- Real-time collaborative graph viewing

### Risks & Assumptions

| Risk | Severity | Mitigation |
|------|----------|------------|
| AI tagging quality inconsistency | Medium | Dimension registry + merge_schema normalization + alias mapping |
| JSONL replay performance at scale (>200 files) | Medium | Documented SQLite migration path from ontology-1.0.4 |
| Web search unavailability during 格物 phase | Low | Fallback: tag without web research, flag for human review |
| CDN availability for Cytoscape.js plugins | Low | Can bundle locally as fallback |
| Dimension drift across tagging sessions | Medium | `.dimension-registry.json` with alias canonicalization |

**Assumptions:**
- Python 3.10+ available in execution environment
- ontology.py (581 lines) can be imported as a module
- Cytoscape.js CDN URLs remain accessible
- KB sizes stay under ~200 files per collection for v1

### Related Features (Conflict Decisions)

| Epic | Feature | Conflict Type | Decision | Details |
|------|---------|---------------|----------|---------|
| EPIC-049 | FEATURE-049-F | MAJOR — Librarian tagging workflow changes | CR on EPIC-049 | Extend AI Librarian to call ontology tool instead of basic 2D tagging |
| EPIC-050 | EPIC-050 (all features) | MAJOR — Depends on EPIC-049 intake contract | CR on EPIC-050 | Intake output format unchanged; librarian does more with it (ontology enrichment) |
| EPIC-023 | FEATURE-023-C | MINOR — G6 vs Cytoscape.js duplication | CR on EPIC-023 | Future CR to standardize on Cytoscape.js (migrate trace viewer from G6) |
| EPIC-025 | (Retired) | MINOR — Deferred Phase 2 knowledge graph | Acknowledge | EPIC-058 supersedes the deferred work |

### Open Questions

- Should the dimension registry support confidence scores for AI-generated dimensions?
- Should graph recreation be triggerable manually via the UI (e.g., "Rebuild Graph" button)?
- What is the maximum BFS depth for cross-graph search spanning multiple collections?

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|--------------------|
| FEATURE-058-A | EPIC-058 | Ontology Tool Skill (x-ipe-tool-ontology) | v1.0 | Complete ontology tool: (A) Knowledge Tagging — AI-driven 格物→致知, dimension discovery, entity CRUD; (B) Graph Creation — cluster detection, auto-split JSONL; (C) Knowledge Search — text + BFS traversal, multi-graph cross-search | None |
| ~~FEATURE-058-B~~ | ~~EPIC-058~~ | ~~Ontology Tool — Graph Creation & Auto-Split~~ | - | *Merged into FEATURE-058-A* | - |
| ~~FEATURE-058-C~~ | ~~EPIC-058~~ | ~~Ontology Tool — Knowledge Search~~ | - | *Merged into FEATURE-058-A* | - |
| FEATURE-058-D | EPIC-058 | KB Librarian Ontology Integration | v1.0 | Update x-ipe-tool-kb-librarian to call ontology tool during intake, skill contract declaration, graph recreation after tagging batch | FEATURE-058-A |
| FEATURE-058-E | EPIC-058 | Ontology Graph Viewer UI | v1.0 | Cytoscape.js graph viewer with 5 plugins, 3 layouts, context menus, minimap, tooltips, zoom controls, graph file sidebar with Select All | FEATURE-058-A |
| FEATURE-058-F | EPIC-058 | Graph Search & AI Agent Integration | v1.0 | Search bar with scope selector, wildcard text search, BFS graph search, AI Agent terminal overlay, multi-graph cross-search | FEATURE-058-A, FEATURE-058-E |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| Ontology Graph Viewer | FEATURE-058-E, FEATURE-058-F | [ontology-graph-viewer-v1.html](x-ipe-docs/requirements/EPIC-058/mockups/ontology-graph-viewer-v1.html) |

---

## Feature Details

### FEATURE-058-A: Ontology Tool Skill (x-ipe-tool-ontology)

**Version:** v1.0
**Brief Description:** Complete `x-ipe-tool-ontology` skill extending ontology-1.0.4 with three operations: (A) Knowledge Tagging — AI-driven content analysis (格物→致知), dynamic dimension discovery, entity CRUD, dimension registry normalization; (B) Graph Creation — collect entities, build graph, detect disconnected clusters, auto-split JSONL, stale reference pruning; (C) Knowledge Search — text matching + BFS traversal, multi-graph cross-search, configurable depth.

> **Merge Note:** This feature consolidates the original FEATURE-058-A (Tagging), FEATURE-058-B (Graph Creation), and FEATURE-058-C (Search) into a single feature, as all three are operations of the same `x-ipe-tool-ontology` skill module.

**Acceptance Criteria (Operation A — Knowledge Tagging):**
- [ ] `x-ipe-tool-ontology` skill created at `.github/skills/x-ipe-tool-ontology/SKILL.md`
- [ ] Skill wraps ontology-1.0.4 engine (imports `ontology.py` as module)
- [ ] Operation A — Knowledge Tagging with two phases: 格物 (study content) → 致知 (discover dimensions)
- [ ] 格物 phase reads file content and understands domain/concepts/relationships
- [ ] 格物 phase calls `x-ipe-tool-web-search` for unfamiliar content (when available)
- [ ] 致知 phase dynamically discovers tagging dimensions based on content analysis (no predefined set)
- [ ] Each tagged file becomes a `KnowledgeNode` entity via `create_entity()`
- [ ] Relationships between knowledge pieces stored as typed relations via `create_relation()`
- [ ] Five relation types supported: `related_to`, `depends_on` (acyclic), `is_type_of`, `part_of`, `described_by`
- [ ] New dimensions appended to YAML schema via `merge_schema()` deep merge (never overwrites)
- [ ] `.dimension-registry.json` maps aliases to canonical dimension names
- [ ] Smart tagging granularity: folder-level tagging if all files share same topic; file-level tagging if content is diverse
- [ ] KnowledgeNode entity schema: label, type (concept/entity/document), description, dimensions (object), source_files (string[]), weight (number)
- [ ] KnowledgeDimension schema: name, type (single-value/multi-value), examples
- [ ] Entity IDs use `know_{uuid_hex[:8]}` format (following ontology-1.0.4 convention)
- [ ] Full CRUD support: create new entities, update existing (append dimensions, update description), delete stale entities
- [ ] AI determines node type (concept/entity/document) based on content analysis
- [ ] AI assigns weight based on content importance/centrality
- [ ] Returns structured result: created/updated entity IDs, dimensions discovered, relations created

**Acceptance Criteria (Operation B — Graph Creation & Auto-Split):**
- [ ] Operation B — Graph Creation collects all `KnowledgeNode` entities under a caller-specified folder path (recursive)
- [ ] Uses `load_graph()` + `query_entities()` to gather entities
- [ ] Builds graph-centric ontology from collected entities and relations
- [ ] Auto-detects disconnected subgraphs (clusters) using graph traversal
- [ ] Splits disconnected clusters into separate `.jsonl` files
- [ ] Graph files saved to `knowledge-base/.ontology/{root-node-name}.jsonl`
- [ ] Root node naming: highest-degree node (most connections) in each cluster
- [ ] Validates referenced file paths still exist during recreation
- [ ] Prunes stale file references via `update_entity()` / `delete_entity()`
- [ ] Validates graph integrity via `validate_graph()` with KB-specific schema constraints
- [ ] Graph recreation is a full rebuild (required for cluster detection)
- [ ] JSONL append-only event log format preserves full mutation history

**Acceptance Criteria (Operation C — Knowledge Search):**
- [ ] Operation C — Knowledge Search matches query to `KnowledgeNode` entities via label/metadata text matching
- [ ] Uses `query_entities()` for initial entity matching
- [ ] BFS traversal from matched nodes via `find_path()` + `get_related()` with configurable depth
- [ ] Returns matched nodes + related subgraph with full metadata (dimensions, descriptions, source_files)
- [ ] Multi-graph cross-search: search can span across multiple `.jsonl` graph files simultaneously
- [ ] Search scope parameter accepts single graph file, list of files, or "all" for cross-graph search
- [ ] Results include graph file provenance (which graph each result came from)
- [ ] Search results support pagination for large result sets

**Dependencies:** None (first feature to build)

**Technical Considerations:**
- Python 3.10+ required for ontology.py
- ontology.py (581 lines) must be vendored or importable
- Web search is optional — degrade gracefully if unavailable
- Dimension registry must be thread-safe for concurrent tagging scenarios
- Full rebuild on each graph creation — JSONL makes incremental tagging efficient but cluster detection needs all entities
- ~200 files/collection ceiling for v1 (JSONL replay performance)
- Disconnected cluster detection can use BFS/DFS from each unvisited node
- Cross-graph search loads multiple JSONL files — performance consideration for many large graphs
- BFS depth should have a sensible default (e.g., depth=3) with configurable override

---

> **FEATURE-058-B** and **FEATURE-058-C** have been merged into FEATURE-058-A above. See merge note.

---

### FEATURE-058-D: KB Librarian Ontology Integration

**Version:** v1.0
**Brief Description:** Update `x-ipe-tool-kb-librarian` to call ontology tool for multi-dimensional tagging during intake, replacing basic 2D domain assignment. Trigger graph recreation after tagging batches.

**Acceptance Criteria:**
- [ ] AI Librarian calls `x-ipe-tool-ontology` tag operation during `.intake/` processing
- [ ] Replaces basic 2D domain assignment with ontology multi-dimensional tagging
- [ ] Lifecycle tags remain in `.kb-index.json` (not moved to ontology)
- [ ] Domain classification migrates into ontology as one dynamically discovered dimension
- [ ] After tagging batch completes, triggers ontology graph recreation for affected KB folders
- [ ] Supports both file-level and folder-level recursive tagging
- [ ] Declares ontology skill contract in librarian SKILL.md:
  ```yaml
  ontology:
    reads: [KnowledgeNode]
    writes: [KnowledgeNode]
    preconditions:
      - "Files exist in intake or KB folder"
    postconditions:
      - "All processed files have KnowledgeNode entities with dimensions"
  ```
- [ ] Existing librarian functionality preserved: file moving, frontmatter generation, intake status tracking

**Dependencies:** FEATURE-058-A (ontology tagging operation)

**Technical Considerations:**
- This is a CR on EPIC-049 FEATURE-049-F — existing tests must continue to pass
- Librarian skill file: `.github/skills/x-ipe-tool-kb-librarian/SKILL.md`
- Graceful degradation if ontology tool fails (fall back to basic tagging with error log)

---

### FEATURE-058-E: Ontology Graph Viewer UI

**Version:** v1.0
**Brief Description:** Interactive frontend for exploring knowledge graphs using Cytoscape.js with 5 plugins, 3 layout options, context menus, minimap, tooltips, and a graph file sidebar with Select All.

**Acceptance Criteria:**
- [ ] New "knowledge graph" icon beside KB icon in main navigation
- [ ] Opens separate Ontology Graph Viewer view (like workflow mode — not a modal)
- [ ] Split-panel layout: left sidebar = graph file list, right = graph canvas
- [ ] Left sidebar lists all `.jsonl` graph files from `knowledge-base/.ontology/`
- [ ] Select All checkbox to toggle all graph files for viewing
- [ ] Per-file checkboxes to add/remove individual graphs from visualization scope
- [ ] Cytoscape.js renders graph nodes and edges on the canvas
- [ ] Node types visually distinguished by color: concept (emerald), document (blue), entity (amber), dimension (violet)
- [ ] Circle node shape for all types (consistent styling)
- [ ] 3-option layout picker (floating panel, top-left):
  - Force-Directed (fcose, default): cluster-aware, quality tuning, idealEdgeLength function
  - Hierarchical (dagre): top-to-bottom DAG layout
  - Radial (concentric): weight-based concentric rings
- [ ] Radial context menus on nodes: Details, Expand, Pin/Unpin
- [ ] Radial context menus on canvas: Fit, Reset, Force/Hierarchy/Radial layout shortcuts
- [ ] Navigator minimap (bottom-left corner) shows pan/zoom overview
- [ ] Tippy.js tooltips on node hover showing type, weight, and description
- [ ] Zoom controls (bottom-right): zoom in, zoom out, fit-to-view buttons
- [ ] Keyboard shortcuts: `/` to focus search, `Esc` to close panels
- [ ] Node click opens right slide-out detail panel with full metadata

**Dependencies:** FEATURE-058-A (ontology tool provides graph files to display)

**Technical Considerations:**
- Cytoscape.js CDN: `unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js`
- Plugin CDNs verified: fcose@2.2.0, dagre@2.5.0, cxtmenu@3.5.0, navigator@2.0.2, tippy.js@6.3.7
- dagre requires `dagre@0.8.5` as dependency
- navigator v2.0.4 returns 404 — must use v2.0.2
- fcose unified config: quality='default', randomize=true, animationDuration=800, nodeRepulsion=5500, gravity=0.25
- Mockup reference: [ontology-graph-viewer-v1.html](x-ipe-docs/requirements/EPIC-058/mockups/ontology-graph-viewer-v1.html)

---

### FEATURE-058-F: Graph Search & AI Agent Integration

**Version:** v1.0
**Brief Description:** Search bar area with scope selector, wildcard text search, BFS graph search integration, AI Agent terminal overlay, and multi-graph cross-search support.

**Acceptance Criteria:**
- [ ] Search bar area above the graph canvas with 3 components:
  - (a) Search scope selector — expandable multi-select dropdown of graph files
  - (b) Wildcard text search bar under selected graph scope
  - (c) "Search with AI Agent" button
- [ ] Text search highlights matching nodes on the graph
- [ ] Non-matching nodes dimmed/faded during active search
- [ ] Search results displayed in info panel with node details
- [ ] BFS graph search invokes `x-ipe-tool-ontology` search operation
- [ ] Configurable search depth for BFS traversal
- [ ] Multi-graph search: scope selector allows selecting multiple graph files for unified search
- [ ] "Search with AI Agent" button opens X-IPE terminal overlay
- [ ] Terminal auto-types prompt template with selected graph scope
- [ ] Terminal waits for user's natural language query input
- [ ] Clear search button resets graph to normal view (all nodes visible)
- [ ] Search results include graph file provenance label

**Dependencies:** FEATURE-058-A (search backend), FEATURE-058-E (graph viewer UI)

**Technical Considerations:**
- AI Agent terminal depends on X-IPE terminal being available and CLI agent active
- Cross-graph search UX: results from different graphs should be visually distinguishable
- Consider debouncing text search input for performance
