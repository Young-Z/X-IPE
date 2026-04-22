# Feature Specification: Layer 3 — Integration Skills (Ontology Synthesizer + Presenters)

> Feature ID: FEATURE-059-D  
> Version: v1.0  
> Status: Refined  
> Last Updated: 04-16-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-16-2026 | Initial specification |

## Linked Mockups

N/A — Knowledge skills are non-visual (SKILL.md + scripts/ + references/).

## Overview

FEATURE-059-D delivers three integration-layer knowledge skills that sit on top of the Layer 2 domain skills (FEATURE-059-C). While Layer 2 skills build ontology entities in isolation (per-domain), Layer 3 skills integrate *across* domains — discovering relationships between graphs, normalizing vocabulary, and linking nodes to form a unified knowledge graph. They also provide the output layer, delivering knowledge to humans and to the frontend graph visualization.

The three skills are:

1. **`x-ipe-knowledge-ontology-synthesizer`** — Cross-graph integration engine. Discovers related ontology graphs, normalizes inconsistent vocabulary into canonical terms, and links nodes across domains. Operates at two tiers: class-level relationships first, then instance-level relationships (constrained by class relationships). Vocabulary translation is embedded within instance-level linking. Populates `synthesize_id` and `synthesize_message` fields on entities created by `ontology-builder` (059-C). Maintains `_relations.NNN.jsonl` with chunked storage and `synthesis_version` audit trail.

2. **`x-ipe-knowledge-present-to-user`** — Knowledge output formatter. Renders constructed knowledge as a structured summary for human consumption. The default output is a structured summary (YAML/JSON); other formats are supported only when explicitly requested by the caller.

3. **`x-ipe-knowledge-present-to-knowledge-graph`** — Frontend graph connector. Pushes ontology graph data to the X-IPE web application via the Socket.IO callback pattern (existing `ui-callback.py` approach from `x-ipe-tool-ontology`). Resolves the server port dynamically from `.x-ipe.yaml` → `server.port` with layered fallback.

Each skill follows the `x-ipe-knowledge` template (FEATURE-059-A) and is created via `x-ipe-meta-skill-creator`. All three include `scripts/` folders. The synthesizer additionally includes `references/` with examples of cross-graph linking scenarios.

## User Stories

1. **As** the Knowledge Librarian assistant, **I want** a synthesizer that discovers overlapping concepts across separate ontology graphs, **so that** I can build a unified knowledge graph that connects related domains.

2. **As** the Knowledge Librarian assistant, **I want** the synthesizer to normalize inconsistent vocabulary (e.g., "JS" vs "JavaScript") into canonical terms, **so that** search and linking operate on consistent terminology.

3. **As** the Knowledge Librarian assistant, **I want** node linking to enforce a hierarchy — class-level relationships first, then instance-level within class constraints, **so that** cross-domain relationships are structurally sound and not arbitrary.

4. **As** the ontology-synthesizer, **I want** to record a `synthesize_id` timestamp and `synthesize_message` on every entity I process, **so that** downstream consumers know when and why each entity was last synthesized.

5. **As** the Knowledge Librarian assistant, **I want** to present knowledge to the user as a structured summary, **so that** gathered knowledge is consumable without requiring the user to navigate raw files.

6. **As** the Knowledge Librarian assistant, **I want** to push ontology graph data to the X-IPE web app's graph viewer, **so that** the user can visually explore the knowledge graph in the browser.

7. **As** a developer, **I want** the graph connector to read the server port from `.x-ipe.yaml` rather than hardcoding it, **so that** it works in any deployment configuration.

8. **As** the system, **I want** relation storage to use chunked JSONL files (max 5000 records per chunk), **so that** the ontology scales without loading excessively large files.

## Acceptance Criteria

### AC-059D-01: Synthesizer — discover_related Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059D-01a | GIVEN a `source_graph` path and `search_scope` WHEN `discover_related` is invoked THEN it returns `related_graphs[]` listing other graphs that share overlapping entities or vocabulary with the source | Unit |
| AC-059D-01b | GIVEN two ontology graphs with at least one shared class label WHEN `discover_related` is invoked THEN `overlap_candidates[]` includes entries with the shared class IDs from both graphs | Unit |
| AC-059D-01c | GIVEN two ontology graphs with zero overlapping concepts WHEN `discover_related` is invoked THEN `related_graphs[]` is empty AND `overlap_candidates[]` is empty | Unit |
| AC-059D-01d | GIVEN `discover_related` output WHEN examining `overlap_candidates[]` entries THEN each entry contains `source_id`, `target_id`, `graph_source`, `graph_target`, and `confidence_score` fields | Unit |
| AC-059D-01e | GIVEN the ontology-builder registers new entities WHEN the synthesizer auto-trigger is enabled THEN `discover_related` runs automatically after the builder completes | Integration |
| AC-059D-01f | GIVEN `discover_related` is invoked on-demand (explicit call) WHEN the same graphs were already analyzed THEN it re-analyzes from scratch (no stale cache) | Unit |

### AC-059D-02: Synthesizer — wash_terms Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059D-02a | GIVEN `graphs[]` and `overlap_candidates[]` from discover_related WHEN `wash_terms` is invoked THEN it returns a `canonical_vocabulary` mapping inconsistent labels to a single canonical form | Unit |
| AC-059D-02b | GIVEN terms "JS", "JavaScript", and "javascript" across multiple graphs WHEN `wash_terms` is invoked THEN all three map to one canonical term (e.g., "JavaScript") in `normalization_map` | Unit |
| AC-059D-02c | GIVEN terms with no synonyms or aliases WHEN `wash_terms` is invoked THEN they pass through unchanged in `canonical_vocabulary` | Unit |
| AC-059D-02d | GIVEN `wash_terms` output WHEN examining `normalization_map` THEN each entry contains `original_term`, `canonical_term`, `source_graph`, and `confidence` fields | Unit |
| AC-059D-02e | GIVEN vocabulary with broader/narrower hierarchy (SKOS-like) WHEN `wash_terms` normalizes terms THEN hierarchical relationships are preserved in the canonical vocabulary | Unit |

### AC-059D-03: Synthesizer — link_nodes Operation (Class-Level)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059D-03a | GIVEN `graphs[]`, `normalization_map`, and `canonical_vocabulary` from wash_terms WHEN `link_nodes` is invoked at class-level THEN it creates cross-domain relationships between overlapping classes and returns `linked_graph` | Unit |
| AC-059D-03b | GIVEN two graphs with classes "WebFramework" and "web-framework" WHEN terms are normalized AND `link_nodes` is invoked THEN a `related_to` relationship is created between the two classes | Unit |
| AC-059D-03c | GIVEN `link_nodes` creates class-level relationships WHEN examining the output `cross_references[]` THEN each entry contains `from_id`, `to_id`, `relation_type`, `source_graph`, `target_graph`, and `synthesis_version` | Unit |
| AC-059D-03d | GIVEN `link_nodes` runs for class-level linking WHEN it encounters an already-linked pair with the same relation THEN it skips the duplicate AND logs the skip reason | Unit |

### AC-059D-04: Synthesizer — link_nodes Operation (Instance-Level)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059D-04a | GIVEN class-level relationships exist between two domains WHEN `link_nodes` is invoked at instance-level THEN it creates instance relationships only between instances whose classes are already linked | Unit |
| AC-059D-04b | GIVEN no class-level relationship between domain A and domain B WHEN `link_nodes` is invoked for instances from those domains THEN no instance-level cross-references are created | Unit |
| AC-059D-04c | GIVEN instance linking is invoked WHEN vocabulary translation is needed (e.g., instance labels differ but map to same canonical term) THEN the vocabulary normalization_map is applied to resolve matches | Unit |
| AC-059D-04d | GIVEN instance-level linking creates relationships WHEN examining the written `_relations.NNN.jsonl` THEN each record includes `from_id`, `to_id`, `relation_type`, `synthesis_version`, `synthesized_with`, and `ts` fields | Unit |

### AC-059D-05: Synthesizer — Relation Storage and Chunking

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059D-05a | GIVEN `_relations.001.jsonl` has fewer than 5000 records WHEN a new relation is created THEN it is appended to `_relations.001.jsonl` | Unit |
| AC-059D-05b | GIVEN `_relations.001.jsonl` has exactly 5000 records WHEN a new relation is created THEN `_relations.002.jsonl` is created AND the new record is written there | Unit |
| AC-059D-05c | GIVEN multiple chunk files exist (001, 002, 003) WHEN a new relation is created THEN it is appended to the highest-numbered chunk file | Unit |
| AC-059D-05d | GIVEN no `_relations.*.jsonl` files exist WHEN `scripts/init_relations.py` is run THEN `_relations.001.jsonl` is created as an empty file | Unit |
| AC-059D-05e | GIVEN a relation is written WHEN examining the JSONL record THEN it uses the event-sourcing envelope format (`op`, `type`, `id`, `ts`, `props`) consistent with `_entities.jsonl` | Unit |

### AC-059D-06: Synthesizer — Synthesis Versioning and Entity Updates

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059D-06a | GIVEN the synthesizer processes entities in `_entities.jsonl` WHEN it completes a run THEN it writes an `update` event for each processed entity with `synthesize_id` set to the current ISO-8601 timestamp | Unit |
| AC-059D-06b | GIVEN the synthesizer processes entities WHEN it writes the update event THEN `synthesize_message` is set to a descriptive string explaining the synthesis purpose (e.g., "Cross-domain linking: Flask ↔ web-framework") | Unit |
| AC-059D-06c | GIVEN an entity with `synthesize_id: null` (never synthesized) WHEN the synthesizer runs THEN the entity is included in the processing batch | Unit |
| AC-059D-06d | GIVEN a synthesizer run completes WHEN examining the audit trail THEN a `synthesis_version` counter is bumped in the relation chunk metadata AND `synthesized_with` records the graphs involved | Unit |

### AC-059D-07: Synthesizer — Self-Bootstrap Script

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059D-07a | GIVEN the `.ontology/` folder exists but has no `_relations.*.jsonl` files WHEN `scripts/init_relations.py` is executed THEN `_relations.001.jsonl` is created | Unit |
| AC-059D-07b | GIVEN `_relations.001.jsonl` already exists WHEN `scripts/init_relations.py` is executed THEN it exits without modifying the file AND logs "Relations already initialized" | Unit |
| AC-059D-07c | GIVEN `scripts/init_relations.py` creates the file WHEN examining the file THEN it is a valid empty JSONL file (0 bytes or empty lines only) | Unit |

### AC-059D-08: Present-to-User — render Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059D-08a | GIVEN a `content_path` pointing to a knowledge file and `target` set to "user" WHEN `render` is invoked with no explicit `format` THEN the output is a structured summary (JSON object with `title`, `summary`, `sections[]`, `metadata`) | Unit |
| AC-059D-08b | GIVEN a `content_path` pointing to a knowledge file WHEN `render` is invoked with `format: "markdown"` THEN the output is a Markdown-formatted summary | Unit |
| AC-059D-08c | GIVEN a `content_path` that does not exist WHEN `render` is invoked THEN it returns an error with `CONTENT_NOT_FOUND` code | Unit |
| AC-059D-08d | GIVEN a `content_path` pointing to a file with `[INCOMPLETE: reason]` markers (from constructor fill_structure) WHEN `render` is invoked THEN incomplete sections are flagged in the output with a warning | Unit |
| AC-059D-08e | GIVEN a multi-section knowledge document WHEN `render` produces a structured summary THEN each section includes `heading`, `content`, and `completeness` (percentage based on filled vs. incomplete markers) | Unit |

### AC-059D-09: Present-to-Knowledge-Graph — connector Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059D-09a | GIVEN `content_path` and `graph_data` (nodes + edges) WHEN `connector` is invoked THEN it POSTs the graph data to the X-IPE web app's internal callback endpoint via HTTP | Integration |
| AC-059D-09b | GIVEN a `.x-ipe.yaml` file exists with `server.port: 6000` WHEN `connector` resolves the server port THEN it uses port 6000 (not the default 5858) | Unit |
| AC-059D-09c | GIVEN no `.x-ipe.yaml` file exists in the project root WHEN `connector` resolves the server port THEN it falls back to the defaults file (`src/x_ipe/defaults/.x-ipe.yaml`) and uses its `server.port` value | Unit |
| AC-059D-09d | GIVEN neither project `.x-ipe.yaml` nor defaults file specifies a port WHEN `connector` resolves the server port THEN it falls back to hardcoded default 5858 | Unit |
| AC-059D-09e | GIVEN `connector` sends graph data WHEN the X-IPE web app receives it THEN the data is broadcast to connected Socket.IO clients on the ontology graph channel | Integration |
| AC-059D-09f | GIVEN `connector` sends graph data WHEN the HTTP POST fails THEN it retries once (max 2 attempts, 1-second delay) AND logs the failure with timestamp | Unit |
| AC-059D-09g | GIVEN `connector` is invoked WHEN constructing the HTTP payload THEN it includes `results`, `subgraph` (nodes + edges), `query`, `scope`, and `request_id` fields (compatible with existing `ui-callback.py` format) | Unit |
| AC-059D-09h | GIVEN `connector` needs an auth token WHEN resolving it THEN it follows the existing resolution chain: CLI flag → `$X_IPE_INTERNAL_TOKEN` env var → `instance/.internal_token` file | Unit |

### AC-059D-10: Port Resolution Contract

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059D-10a | GIVEN a project with `.x-ipe.yaml` at project root WHEN the port resolution function reads the file THEN it extracts `server.port` as an integer | Unit |
| AC-059D-10b | GIVEN `.x-ipe.yaml` exists but has no `server.port` key WHEN the port resolution function runs THEN it falls back to `src/x_ipe/defaults/.x-ipe.yaml` → `server.port` | Unit |
| AC-059D-10c | GIVEN a port resolution function WHEN called from any script in any skill THEN it searches for `.x-ipe.yaml` starting from the current working directory upward to project root (git root) | Unit |
| AC-059D-10d | GIVEN the port resolution is used by `connector` operation WHEN reading `.x-ipe.yaml` THEN it uses the same YAML parser as the X-IPE application (PyYAML) | Unit |

## Functional Requirements

### FR-1: Cross-Graph Discovery

**Description:** The synthesizer must identify related ontology graphs by comparing entity labels, class hierarchies, and vocabulary terms across all graphs in `.ontology/`.

**Details:**
- Input: `source_graph` (path to a named graph JSONL) and `search_scope` (which other graphs to check — `"all"` or a list of paths)
- Process: Load source graph entities, scan target graphs for overlapping class labels or vocabulary terms, compute confidence scores for each overlap candidate
- Output: `related_graphs[]` (paths to related graphs), `overlap_candidates[]` (specific entity pairs with confidence scores)

### FR-2: Vocabulary Normalization

**Description:** The synthesizer must normalize inconsistent terminology across domains into a canonical vocabulary.

**Details:**
- Input: `graphs[]` (list of graph paths), `overlap_candidates[]` (from discover_related)
- Process: Extract all labels/terms, group synonyms (case-insensitive, alias matching, abbreviation expansion), select canonical form (most common or most descriptive), preserve SKOS hierarchy
- Output: `canonical_vocabulary` (list of canonical terms), `normalization_map` (original → canonical mappings)

### FR-3: Hierarchical Node Linking

**Description:** The synthesizer must create cross-domain relationships following a strict hierarchy: class-level first, then instance-level constrained by class relationships.

**Details:**
- Input: `graphs[]`, `normalization_map`, `canonical_vocabulary`, `tier` (class | instance)
- Process:
  - **Class tier:** Match normalized class labels across graphs, create `related_to` relations between matching classes
  - **Instance tier:** For each class-level relationship, find instances belonging to linked classes, match instances by normalized labels/properties, create instance-level relations. Vocabulary translation is applied at this tier.
- Output: `linked_graph` (merged graph view), `cross_references[]` (list of new relations created)

### FR-4: Relation Persistence

**Description:** Relations are stored in chunked append-only JSONL files following the event-sourcing pattern.

**Details:**
- Input: Relation records from link_nodes
- Process: Append to highest-numbered `_relations.NNN.jsonl` chunk. Auto-split when chunk exceeds 5000 records.
- Output: Persisted relations in `.ontology/relations/` folder

### FR-5: Knowledge Rendering

**Description:** The presenter must format knowledge content into a structured summary for human consumption.

**Details:**
- Input: `content_path` (path to knowledge file), `target` (always "user"), `format` (optional — defaults to "structured")
- Process: Read content, parse sections, compute completeness per section, generate summary
- Output: `rendered_output` — structured JSON with title, summary, sections[], metadata. Markdown output available when `format: "markdown"` is specified.

### FR-6: Graph Visualization Connector

**Description:** The connector must push ontology graph data to the X-IPE web app's graph viewer via the existing Socket.IO callback mechanism.

**Details:**
- Input: `content_path`, `graph_data` ({nodes, edges}), `target` (graph UI), `ui_callback_config` (optional overrides)
- Process: Resolve server port from `.x-ipe.yaml` → defaults → hardcoded. Resolve auth token. POST graph payload to `/api/internal/ontology/callback`. Retry once on failure.
- Output: `graph_visualization` (confirmation), `callback_status` (success/failure with details)

## Non-Functional Requirements

### NFR-1: Performance

- Relation chunking prevents loading more than 5000 records per file read
- `discover_related` should complete within 30 seconds for up to 50 graphs with 1000 entities each
- `wash_terms` should process up to 10,000 terms within 10 seconds
- `connector` HTTP POST timeout: 10 seconds per attempt

### NFR-2: Data Integrity

- Relation records use event-sourcing (append-only JSONL) — no in-place mutation
- `synthesis_version` is monotonically increasing — never decremented
- Entity updates (`synthesize_id`, `synthesize_message`) use the same JSONL `update` event pattern as the builder

### NFR-3: Compatibility

- `connector` output format must be backward-compatible with existing `ui-callback.py` payload structure
- Port resolution must work with both project-level `.x-ipe.yaml` and the defaults file
- JSONL event envelope format must be identical to `_entities.jsonl` (same `op`, `type`, `id`, `ts`, `props` fields)

## UI/UX Requirements

N/A — These are non-visual knowledge skills. The `connector` operation integrates with the existing ontology graph viewer UI (FEATURE-058-F) without requiring UI changes.

## Dependencies

**Internal:**
- **FEATURE-059-A:** Knowledge skill template — provides the Operations + Steps structure that all three skills follow
- **FEATURE-059-B:** `keeper-memory` and `extractor-memory` — synthesizer reads entities created by builder which depend on keeper's storage
- **FEATURE-059-C:** `ontology-builder` — creates the entities and vocabulary that the synthesizer integrates. Defines `_entities.jsonl` format, `synthesize_id`/`synthesize_message` fields (set to null), and chunk management patterns. **Direct dependency — 059-C must be implemented before synthesizer can function.**
- **FEATURE-058-F (existing):** Ontology graph viewer UI and `ui-callback.py` — provides the Socket.IO callback endpoint that `connector` targets

**External:**
- PyYAML — for reading `.x-ipe.yaml` configuration files
- Web search capability — used by `wash_terms` for synonym/alias lookup when normalizing vocabulary

## Business Rules

**BR-1:** Cross-domain linking is hierarchical: class-level relationships must be established before instance-level relationships. An instance relationship cannot exist between two domains that lack a class-level relationship.

**BR-2:** Vocabulary translation is part of instance-level linking, not a separate linking tier. When matching instances, the `normalization_map` from `wash_terms` is applied to resolve label differences.

**BR-3:** The synthesizer's `discover_related` operation is auto-triggered after the ontology-builder registers new entities (default behavior). It is also callable on-demand as a standalone operation.

**BR-4:** `synthesis_version` is bumped on every synthesizer run. The `synthesized_with` field records which graphs were involved in that run, forming an audit trail.

**BR-5:** `present-to-user` defaults to structured summary (JSON) output. Markdown and other formats are only used when the caller explicitly specifies `format`.

**BR-6:** `present-to-knowledge-graph` must resolve the server port dynamically: `.x-ipe.yaml` (project root) → defaults file → hardcoded 5858. It must never assume a fixed port.

**BR-7:** The connector's HTTP payload format must be compatible with the existing `ui-callback.py` contract: `results`, `subgraph`, `query`, `scope`, `request_id`.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| `discover_related` finds no overlap between any graphs | Returns empty `related_graphs[]` and `overlap_candidates[]`, logs "No cross-domain overlap found" |
| `wash_terms` receives terms in different character cases only (e.g., "flask", "Flask", "FLASK") | Normalizes to the most common form; if equal frequency, uses title case |
| `link_nodes` at instance-level with no class-level relationships | Returns empty `cross_references[]`, logs "No class-level relationships found — instance linking skipped" |
| `_relations.NNN.jsonl` chunk file is corrupted (invalid JSON lines) | Skip corrupted lines, log warnings, continue appending to a new chunk |
| `connector` cannot reach the X-IPE server after 2 attempts | Returns `callback_status: "failed"` with error details, does NOT throw |
| `.x-ipe.yaml` has non-integer `server.port` value | Falls back to defaults file, logs a warning |
| `render` receives a path to an empty file | Returns structured summary with `title: "Empty"`, `sections: []`, `completeness: 0` |
| `discover_related` is auto-triggered but the builder hasn't written any entities yet | Returns empty results gracefully (no error) |
| `link_nodes` encounters a duplicate relation (same from/to/type) | Skips the duplicate, logs "Relation already exists", does not write |
| Auth token not found by any resolution method | `connector` exits with error `AUTH_TOKEN_NOT_FOUND` and non-zero exit code |

## Out of Scope

- **Knowledge Librarian assistant** (`x-ipe-assistant-knowledge-librarian-DAO`) — deferred to FEATURE-059-E
- **Frontend UI changes** for the ontology graph viewer — the existing FEATURE-058-F UI is used as-is
- **Migration of existing knowledge-base content** to the new ontology structure — deferred to FEATURE-059-F
- **Modifications to `x-ipe-tool-ontology`** — remains deprecated; this feature builds new skills, not migrating the old tool
- **Graph clustering or dimension registry updates** — the synthesizer creates relations, not clusters
- **Real-time streaming** of synthesis progress to the UI — only the final graph push via connector

## Technical Considerations

- Each skill lives in `.github/skills/x-ipe-knowledge-{sub-category}-{name}/` directory
- Synthesizer: SKILL.md + `scripts/` (synthesis engine, relation storage, init_relations.py) + `references/` (cross-linking examples)
- Present-to-user: SKILL.md + `scripts/` (render engine)
- Present-to-knowledge-graph: SKILL.md + `scripts/` (connector, port resolution)
- All skills created via `x-ipe-meta-skill-creator` (candidate/ → validate → merge workflow)
- Port resolution utility should be reusable — consider a shared helper in `scripts/` that other skills can import
- The `_relations.NNN.jsonl` format must mirror `_entities.NNN.jsonl` event-sourcing envelope for consistency
- `discover_related` auto-trigger mechanism needs a well-defined hook point — the ontology-builder's write operations should emit a signal or the synthesizer should poll for new entities
- The `connector` script should be modeled after the existing `ui-callback.py` in `x-ipe-tool-ontology` to maintain backward compatibility

## Open Questions

None — all questions resolved during refinement.
