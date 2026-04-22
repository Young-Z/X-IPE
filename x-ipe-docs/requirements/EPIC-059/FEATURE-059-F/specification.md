# FEATURE-059-F: Layer 5 — Integration, Migration & Deprecation

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-04-20 | Drift | Initial specification |

## Linked Mockups

_No mockups linked for this feature._

## Overview

FEATURE-059-F is the final layer of EPIC-059 (Knowledge Pipeline Refactoring). It completes the migration by:

1. **Removing the deprecated `x-ipe-assistant-user-representative-Engineer` skill** and updating all references across the codebase to point to its replacement `x-ipe-assistant-user-representative-Engineer` (created in 059-E).
2. **Updating the web app ontology graph viewer** to adopt the new knowledge structure from 059-C/D — removing the per-graph sidebar (graph list + select-all), keeping the legend, and integrating cross-graph `_relations.NNN.jsonl` support from the ontology-synthesizer.

This feature was deferred from earlier layers:
- 059-A (spec line 221): "Migration of existing `x-ipe-dao-*` skills to `x-ipe-assistant-*` namespace — Layer 5"
- 059-B/C (spec lines 215-216): "Web app UI changes — deferred to FEATURE-059-F"
- 059-E (spec line 268): "Deprecation of old `x-ipe-assistant-user-representative-Engineer` — tracked in FEATURE-059-F"

### Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-059-E | Internal | `x-ipe-assistant-user-representative-Engineer` must exist (replacement for old DAO skill) |
| FEATURE-059-D | Internal | `_relations.NNN.jsonl` cross-graph format defined by ontology-synthesizer |
| FEATURE-059-C | Internal | Ontology-builder JSONL event format (`_entities.jsonl`, `synthesize_id`/`synthesize_message`) |
| FEATURE-058-E/F | Internal | Existing ontology graph viewer (routes, service, JS components) being modified |

---

## User Stories

### US-F1: Skill Reference Migration
**As** an X-IPE developer or skill author, **I want** all skill references to use the new `x-ipe-assistant-user-representative-Engineer` name, **so that** the codebase is consistent and the old deprecated name no longer appears.

### US-F2: Instruction Template Update
**As** the X-IPE system, **I want** copilot-instructions and resource templates to reference the new assistant skill names, **so that** AI agents invoke the correct (non-deprecated) skills.

### US-F3: Streamlined Graph Viewer
**As** a knowledge graph user, **I want** the graph viewer to show graphs without a per-graph selection sidebar, **so that** I get more canvas space and don't need to manage ontology internals.

### US-F4: Cross-Graph Relation Visualization
**As** a knowledge graph user, **I want** the graph viewer to display cross-graph relationships from `_relations.NNN.jsonl`, **so that** I can see how entities in different knowledge domains connect.

---

## Acceptance Criteria

### Group 01: Old DAO Skill Removal

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-059F-01a | GIVEN the old `x-ipe-assistant-user-representative-Engineer` skill folder exists WHEN the migration is applied THEN the folder `.github/skills/x-ipe-assistant-user-representative-Engineer/` is completely removed from the repository | Unit |
| AC-059F-01b | GIVEN the old folder contained `SKILL.md`, `references/` (5 files), and `templates/` (1 file) WHEN the removal is applied THEN none of those files exist under `.github/skills/x-ipe-assistant-user-representative-Engineer/` | Unit |
| AC-059F-01c | GIVEN the old skill also had `x-ipe-docs/skill-meta/x-ipe-assistant-user-representative-Engineer/` WHEN the migration is applied THEN that skill-meta folder is also removed | Unit |

### Group 02: Skill SKILL.md Reference Updates

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-059F-02a | GIVEN 24 skill SKILL.md files reference `x-ipe-assistant-user-representative-Engineer` WHEN the migration runs THEN every occurrence in `.github/skills/*/SKILL.md` is replaced with `x-ipe-assistant-user-representative-Engineer` | Unit |
| AC-059F-02b | GIVEN a skill SKILL.md has `x-ipe-assistant-user-representative-Engineer` in its interaction_mode guidance WHEN the reference is updated THEN the replacement preserves the surrounding sentence structure and formatting | Unit |
| AC-059F-02c | GIVEN all 24 skill files are updated WHEN searching `.github/skills/*/SKILL.md` for the old name THEN zero results are returned | Unit |

### Group 03: Copilot Instructions Update

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-059F-03a | GIVEN `.github/copilot-instructions.md` line 103 references `x-ipe-assistant-user-representative-Engineer` WHEN the migration runs THEN it is replaced with `x-ipe-assistant-user-representative-Engineer` | Unit |
| AC-059F-03b | GIVEN `src/x_ipe/resources/copilot-instructions-en-no-dao.md` references the old name WHEN the migration runs THEN the old name is replaced | Unit |
| AC-059F-03c | GIVEN `src/x_ipe/resources/copilot-instructions-zh.md` references the old name WHEN the migration runs THEN all occurrences are replaced with the new name | Unit |

### Group 04: Resource Template Updates

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-059F-04a | GIVEN `src/x_ipe/resources/templates/instructions-template.md` has 6 references to `x-ipe-assistant-user-representative-Engineer` WHEN the migration runs THEN all 6 are replaced with `x-ipe-assistant-user-representative-Engineer` | Unit |
| AC-059F-04b | GIVEN `src/x_ipe/resources/templates/instructions-template-no-dao.md` references the old name WHEN the migration runs THEN all occurrences are replaced | Unit |

### Group 05: Graph Viewer Sidebar Removal

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-059F-05a | GIVEN the ontology graph viewer has an `.ogv-sidebar` containing graph list and select-all checkbox WHEN the viewer renders THEN the graph list section and select-all checkbox are removed from the sidebar | UI |
| AC-059F-05b | GIVEN the sidebar's "NODE TYPES" legend section WHEN the viewer renders THEN the legend remains visible and correctly positioned | UI |
| AC-059F-05c | GIVEN the graph-list sidebar is removed WHEN the graph canvas renders THEN the canvas occupies the full width previously shared with the sidebar | UI |
| AC-059F-05d | GIVEN the viewer previously loaded graphs via sidebar checkbox selection WHEN the sidebar is removed THEN the viewer auto-loads all available graphs on initialization | UI |

### Group 06: Graph Viewer Auto-Load Behavior

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-059F-06a | GIVEN the graph viewer opens WHEN the `/api/kb/ontology/graphs` endpoint returns a list of graphs THEN all graphs are automatically loaded and rendered on the canvas | Integration |
| AC-059F-06b | GIVEN all graphs are auto-loaded WHEN examining the canvas THEN nodes from all graphs are visible with correct node types and labels | UI |
| AC-059F-06c | GIVEN no graphs exist in `.ontology/` WHEN the viewer opens THEN an empty-state message is displayed (no errors) | UI |

### Group 07: Cross-Graph Relations Support (Backend)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-059F-07a | GIVEN `.ontology/relations/_relations.001.jsonl` exists with relation records WHEN `/api/kb/ontology/graph/<name>` is called THEN the response includes edges from `_relations.NNN.jsonl` that connect entities in the requested graph | API |
| AC-059F-07b | GIVEN multiple `_relations.NNN.jsonl` chunks exist (001, 002, etc.) WHEN the service loads relations THEN it reads ALL chunk files and merges them | Unit |
| AC-059F-07c | GIVEN a relation record in `_relations.NNN.jsonl` has `from_id`, `to_id`, `relation_type`, `synthesis_version` WHEN converted to Cytoscape edge format THEN `source` = `from_id`, `target` = `to_id`, `relation_type` and `label` = `relation_type` | Unit |
| AC-059F-07d | GIVEN cross-graph relations link entities from different graphs WHEN a combined view is rendered THEN edges crossing graph boundaries are included and visually distinguishable | UI |

### Group 08: Graph Service — Unified Graph Endpoint

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-059F-08a | GIVEN the viewer auto-loads all graphs WHEN a new API endpoint `/api/kb/ontology/graphs/all` is called THEN it returns merged Cytoscape elements (nodes + edges) from all graphs plus all `_relations.NNN.jsonl` files | API |
| AC-059F-08b | GIVEN entities have `synthesize_id` and `synthesize_message` fields (from 059-D synthesizer) WHEN converting to Cytoscape nodes THEN these fields are included in the node data for tooltip display | Unit |
| AC-059F-08c | GIVEN a graph has zero entities WHEN included in the merged response THEN no nodes are added (empty graphs are silently skipped) | Unit |

### Group 09: Search Behavior After Sidebar Removal

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-059F-09a | GIVEN the sidebar graph selector is removed WHEN the user performs a search via the topbar THEN the search scope defaults to all graphs | Integration |
| AC-059F-09b | GIVEN BFS search previously filtered by selected graphs WHEN the sidebar is removed THEN BFS search operates on all graphs by default | Integration |
| AC-059F-09c | GIVEN the scope pills bar exists in the topbar WHEN graphs are auto-loaded THEN scope pills still display per-graph pills for filtering the canvas view | UI |

### Group 10: No Regression — Existing Functionality

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-059F-10a | GIVEN the ontology graph viewer has a topbar with search, BFS, and AI Agent Console bridge WHEN 059-F changes are applied THEN topbar functionality remains intact | Integration |
| AC-059F-10b | GIVEN the detail panel shows node metadata on click WHEN 059-F changes are applied THEN the detail panel continues to work correctly, including new `synthesize_id`/`synthesize_message` fields | UI |
| AC-059F-10c | GIVEN the SocketIO `/ontology` namespace broadcasts AI agent search results WHEN 059-F changes are applied THEN the callback endpoint and real-time rendering continue to function | Integration |
| AC-059F-10d | GIVEN existing tests in `tests/` cover ontology graph routes and service WHEN 059-F changes are applied THEN all existing tests continue to pass (updated as needed) | Unit |

---

## Functional Requirements

### FR-1: DAO Skill Removal
Remove the entire `.github/skills/x-ipe-assistant-user-representative-Engineer/` directory and its corresponding `x-ipe-docs/skill-meta/x-ipe-assistant-user-representative-Engineer/` directory.

### FR-2: Reference Migration
Replace all occurrences of `x-ipe-assistant-user-representative-Engineer` with `x-ipe-assistant-user-representative-Engineer` in:
- All 24 skill SKILL.md files under `.github/skills/*/SKILL.md`
- `.github/copilot-instructions.md`
- `src/x_ipe/resources/copilot-instructions-en-no-dao.md`
- `src/x_ipe/resources/copilot-instructions-zh.md`
- `src/x_ipe/resources/templates/instructions-template.md`
- `src/x_ipe/resources/templates/instructions-template-no-dao.md`

### FR-3: Graph Viewer Sidebar Simplification
Remove the graph-list and select-all checkbox sections from the `.ogv-sidebar`. Retain the NODE TYPES legend. Reposition the legend (e.g., overlay on canvas or compact bottom bar).

### FR-4: Auto-Load All Graphs
On viewer initialization, automatically fetch all graphs from `/api/kb/ontology/graphs` and load them all without user selection.

### FR-5: Cross-Graph Relations
Extend `OntologyGraphService` to read `_relations.NNN.jsonl` files from `.ontology/relations/` and include those edges when serving graph data.

### FR-6: Unified Graph Endpoint
Add `/api/kb/ontology/graphs/all` endpoint that returns merged Cytoscape elements from all graphs plus all cross-graph relations.

### FR-7: Synthesizer Metadata in Nodes
Include `synthesize_id` and `synthesize_message` fields in Cytoscape node data when present on entities.

---

## Non-Functional Requirements

**NFR-1: No Dangling References** — After migration, `grep -r "x-ipe-assistant-user-representative-Engineer" .github/ src/` must return zero results (excluding git history).

**NFR-2: Graph Load Performance** — The unified `/api/kb/ontology/graphs/all` endpoint should respond within 5 seconds for up to 50 graphs with 1000 entities each.

**NFR-3: Backward Compatibility** — Individual graph endpoints (`/api/kb/ontology/graph/<name>`) continue to work as before, now additionally including cross-graph relations relevant to that graph.

**NFR-4: Legend Readability** — The repositioned NODE TYPES legend must remain legible and not obscure graph content.

---

## UI/UX Requirements

### Layout Changes
- **Before:** Sidebar (graph list + select-all + legend) | Canvas | Detail Panel
- **After:** Legend (compact overlay or bottom bar) | Full-width Canvas | Detail Panel

### Interaction Changes
- Graph selection replaced by auto-load-all
- Search defaults to all-graphs scope
- Scope pills remain for optional filtering
- Cross-graph edges visually distinguishable (e.g., dashed line, different color)

---

## Business Rules

**BR-1:** The old `x-ipe-assistant-user-representative-Engineer` skill folder must be fully removed, not just deprecated with a header. This was clarified by the user.

**BR-2:** The legend (NODE TYPES) must be preserved for user orientation.

**BR-3:** Cross-graph relation edges from `_relations.NNN.jsonl` follow the 059-D synthesizer format: `from_id`, `to_id`, `relation_type`, `synthesis_version`, `synthesized_with`, `ts`.

---

## Edge Cases

| Edge Case | Expected Behavior |
|-----------|-------------------|
| No `.ontology/` directory exists | Graph viewer shows empty state, no errors |
| `.ontology/relations/` directory doesn't exist | No cross-graph edges rendered; intra-graph edges still shown |
| `_relations.NNN.jsonl` contains malformed lines | Malformed lines are skipped (same pattern as `_parse_graph_jsonl`) |
| A relation references an entity ID not present in any loaded graph | Edge is included but may render as disconnected; no error |
| Old DAO skill name appears in user-created files outside `.github/` and `src/` | Out of scope — only `.github/` and `src/` paths are updated |

---

## Out of Scope

- **Knowledge content migration** — Knowledge-base directory is empty; no content to migrate
- **New knowledge pipeline features** — No new pipeline capabilities; this feature only integrates existing 059-C/D outputs into the viewer
- **Performance optimization of graph rendering** — Canvas rendering performance is not addressed (existing behavior)
- **User-created files** — Files outside `.github/` and `src/` that may reference the old DAO name are not updated

---

## Technical Considerations

_(Focus on WHAT, not HOW)_

- The reference migration touches ~24 skill files, 1 copilot-instructions file, and ~4 resource templates — all are text replacements.
- The graph service (`ontology_graph_service.py`) needs a method to read `_relations.NNN.jsonl` from `.ontology/relations/` and merge them into Cytoscape edge format.
- A new endpoint `/api/kb/ontology/graphs/all` aggregates all individual graphs plus cross-graph relations.
- The JS viewer (`ontology-graph-viewer.js`) sidebar HTML and related event handlers need partial removal, with layout CSS adjustments.
- The `_loadGraphIndex` and checkbox-toggling logic is replaced by auto-load-all behavior.
- Existing tests for the graph routes/service need updating to reflect the new endpoint and removed sidebar behavior.
