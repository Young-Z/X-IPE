# Requirement Details - Part 25

> Continued from: [requirement-details-part-24.md](x-ipe-docs/requirements/requirement-details-part-24.md)
> Created: 04-15-2026

---

## EPIC-059: Rebuild Knowledge Skills — Systematic Knowledge Architecture

> Version: 1.0
> Source Idea: [IDEA-041 — CR-Rebuild Knowledge Skills](x-ipe-docs/ideas/041.%20CR-Rebuild%20Knowledge%20Skills/idea-summary-v1.md)
> Retires: EPIC-049, EPIC-050, EPIC-051, EPIC-053, EPIC-054, EPIC-058
> CR Impact: EPIC-047 (dao → assistant type rename)
> Dependencies: EPIC-044 (Skill Creator), EPIC-041 (Custom Instructions), EPIC-043 (Feature Board), EPIC-046 (Web App Architecture)

### Project Overview

A comprehensive restructuring of all knowledge-related skills in X-IPE, introducing two new skill namespaces (`x-ipe-knowledge-*` and `x-ipe-assistant-*`) that replace the current scattered knowledge tooling with a systematic, pipeline-oriented architecture. The design follows an ETL-inspired pattern: **extract** → **construct** → **keep** → **present**, with **mimic** running in parallel for dynamic knowledge. All coordinated by a Knowledge Librarian assistant using a 格物致知 (investigate things to extend knowledge) methodology with iterative replanning support.

The restructuring introduces:
- **13 new knowledge skills** across 7 sub-categories (extractor, constructor, mimic, keeper, present, ontology-builder, ontology-synthesizer)
- **2 assistant skills** (user-representative-Engineer, knowledge-librarian-DAO)
- **3-layer ontology model** (Schema / Instances / Vocabulary) replacing flat JSONL
- **Tulving 4-tier memory model** (working / episodic / semantic / procedural) replacing scattered storage
- **格物致知 workflow** — constructor-driven paradigm with rubric + critique loop
- **Deprecation of ~11 old skills** with alias/redirect migration

### User Request

Rebuild all knowledge-related skills into a coherent, pipeline-oriented architecture under new `x-ipe-knowledge-*` and `x-ipe-assistant-*` namespaces. Introduce a Knowledge Librarian (DAO) as the central coordinator using the 格物致知 workflow, a 3-layer ontology model (Schema/Instances/Vocabulary) with formal JSON Schemas, and Tulving's 4-tier memory model. Deprecate and remove all superseded skills.

### Clarifications

| Question | Answer |
|----------|--------|
| Epic structure? | One EPIC-059 with features per build layer (FEATURE-059-A through FEATURE-059-F) |
| Scope? | All 6 build layers in full detail within one document |
| Where is deprecation tracked? | In Layer 5 feature only (FEATURE-059-F) |
| Formal data model schemas? | Yes — formal JSON Schema definitions required for all ontology models (class registry, instances, vocabulary, relations) |
| Skill backbone for knowledge skills? | Operations + Steps pattern (stateless services called by DAO). NOT the phase backbone (博学之→笃行之) used by task-based skills |
| Write discipline? | Only `keeper-memory` writes to persistent folders; all other skills write exclusively to `.working/` |
| Rev-eng tools? | All 8 `x-ipe-tool-rev-eng-*` skills stay as-is — `constructor-app-reverse-engineering` depends on them |
| Content migration? | Existing knowledge content stays in old location; no automatic migration of content |
| Iterative replanning? | Yes, with max 3 iterations guard to prevent infinite loops |

### High-Level Requirements

> **Note:** Features are broken down per build layer. See Feature List below for tracking.

### Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-059-A | EPIC-059 | Knowledge & Assistant Skill Type Infrastructure | v1.0 | Add "knowledge" (Operations+Steps) and "assistant" templates to skill-creator, update custom instructions auto-discovery, document all 4 skill types | None |

---

### Feature Details

### FEATURE-059-A: Knowledge & Assistant Skill Type Infrastructure

**Version:** v1.0
**Brief Description:** Update `x-ipe-meta-skill-creator` to support "knowledge" and "assistant" as new skill types, update custom instructions for auto-discovery, and create a skill type comparison reference document.

**Acceptance Criteria:**
- [ ] Knowledge skill template (`x-ipe-knowledge.md`) created in `.github/skills/x-ipe-meta-skill-creator/templates/` with Operations + Steps structure: each operation defines `name`, `description`, `input` (typed params), `output` (typed results), `steps[]`, `writes_to`, `constraints[]`
- [ ] Assistant skill template (`x-ipe-assistant.md`) created in `.github/skills/x-ipe-meta-skill-creator/templates/` with orchestration procedure structure (adapted from existing dao template)
- [ ] `x-ipe-meta-skill-creator` SKILL.md updated to recognize "knowledge" and "assistant" as valid skill types in its creation workflow
- [ ] Custom instructions updated: glob patterns include `x-ipe-knowledge-*` and `x-ipe-assistant-*` for auto-discovery in `available_skills` descriptions
- [ ] Skill type comparison reference document created at `.github/skills/x-ipe-meta-skill-creator/references/skill-type-comparison.md` covering all 4 types (task-based, tool, knowledge, assistant) with structure, invocation model, state model, and when-to-use guidance
- [ ] Smoke test: `x-ipe-meta-skill-creator` can create a new skill of type "knowledge" — produces valid SKILL.md with Operations + Steps sections
- [ ] Smoke test: `x-ipe-meta-skill-creator` can create a new skill of type "assistant" — produces valid SKILL.md with orchestration procedure

**Dependencies:**
- None — this is the foundation that all other EPIC-059 features depend on

**Technical Considerations:**
- Knowledge template uses Operations + Steps pattern (stateless services) — NOT the phase backbone (博学之→笃行之) used by task-based skills. Each operation has typed input/output contracts callable individually by the DAO orchestrator
- Assistant template reuses the existing dao SKILL.md template structure with namespace rename. The "dao" type is deprecated in favor of "assistant"
- Custom instructions update must not break existing skill auto-discovery for `x-ipe-task-based-*`, `x-ipe-tool-*`, and `x-ipe-dao-*` (backward compatible during transition)
- The skill type comparison doc serves as a design reference for contributors creating new skills — it should include the comparison table from the idea summary (Section 1c)

---

### Detailed Requirements (by Build Layer)

#### Layer 0 — Prerequisites

**Objective:** Update the skill creation infrastructure to support "knowledge" and "assistant" as new skill types before any new skill can be created.

1. **Knowledge skill type template**: Add a "knowledge" skill type to `x-ipe-meta-skill-creator` with the Operations + Steps structure. Each operation defines: `name`, `description`, `input` (typed params), `output` (typed results), `steps[]`, `writes_to`, `constraints[]`. Template location: `.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-knowledge.md`.

2. **Assistant skill type template**: Add an "assistant" skill type to `x-ipe-meta-skill-creator` with orchestration procedure structure (same DAO template format as existing dao type, renamed). Template location: `.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-assistant.md`.

3. **Custom instructions update**: Update custom instructions glob patterns to include `x-ipe-knowledge-*` and `x-ipe-assistant-*` for auto-discovery. Ensure skill matching logic recognizes the new skill types in available_skills descriptions.

4. **Skill type comparison documentation**: Document the 4 skill types (task-based, tool, knowledge, assistant) with their differences in structure, invocation model, state model, and when-to-use guidance. Include in skill-creator references.

**Acceptance Criteria:**
- `x-ipe-meta-skill-creator` can create skills of type "knowledge" with Operations + Steps structure
- `x-ipe-meta-skill-creator` can create skills of type "assistant" with orchestration procedure
- Custom instructions auto-discovery finds `x-ipe-knowledge-*` and `x-ipe-assistant-*` skills
- All 4 skill types documented with comparison table

---

#### FEATURE-059-B: Layer 1 — Core Skills (Keeper + Extractors)

**Objective:** Build the foundational skills that all other layers depend on — the write gatekeeper (keeper-memory) and the two data sources (extractor-web, extractor-memory).

##### B.1 — `x-ipe-knowledge-keeper-memory`

The unified write gatekeeper. All persistent storage writes go through this skill.

**Operations:**
| Operation | Input | Output | Writes To |
|-----------|-------|--------|-----------|
| `store` | `content`, `memory_type` (episodic\|semantic\|procedural), `metadata`, `tags[]` | `stored_path`, `memory_entry_id` | Target memory folder |
| `promote` | `working_path`, `memory_type`, `metadata` | `promoted_path` | Target memory folder |

**Self-bootstrap (`scripts/init_memory.py`):** Creates the memory folder structure on first use:
```
x-ipe-docs/memory/
├── .working/          # session-scoped, ephemeral
├── .ontology/         # system-managed ontology model
├── episodic/          # personal preferences, lessons learned
├── semantic/          # facts, findings, tagged concepts
└── procedural/        # behavior patterns, sequences, user manuals
```

**Acceptance Criteria:**
- `store` operation routes content to correct folder based on `memory_type`
- `promote` moves `.working/` artifacts to persistent storage
- Bootstrap script is idempotent (safe to call repeatedly)
- Memory folder structure created correctly on first operation

##### B.2 — `x-ipe-knowledge-extractor-web`

Extract raw knowledge from web sources via Chrome DevTools MCP.

**Operations:**
| Operation | Input | Output | Writes To |
|-----------|-------|--------|-----------|
| `extract_overview` | `target` (URL), `depth` (shallow\|medium) | `overview_content`, `source_map` | `.working/overview/` |
| `extract_details` | `target`, `scope` (full\|section\|specific), `format_hints` | `extracted_content`, `metadata` | `.working/extracted/` |

**Two-phase extraction pattern:** Constructor first requests `extract_overview` to understand the landscape, then requests `extract_details` for specific sections it needs. This avoids over-extraction.

**Acceptance Criteria:**
- Can navigate and extract from web pages via Chrome DevTools MCP
- Overview extraction produces source map of available content
- Detail extraction supports scoped extraction (full, section, specific)
- All output written to `.working/` only

##### B.3 — `x-ipe-knowledge-extractor-memory`

Search and retrieve existing knowledge from persistent memory storage. Replaces both `x-ipe-task-based-knowledge-referencer` and `x-ipe-tool-user-manual-referencer`.

**Operations:**
| Operation | Input | Output | Writes To |
|-----------|-------|--------|-----------|
| `extract_overview` | `target` (query/path), `depth` | `overview_content`, `source_map` | *(read-only)* |
| `extract_details` | `target`, `scope`, `format_hints` | `extracted_content`, `metadata` | *(read-only)* |

**Acceptance Criteria:**
- Can search across all memory tiers (episodic, semantic, procedural)
- Can query `.ontology/` for graph-based knowledge retrieval
- Read-only — does not write to any folder
- Supports knowledge_type filtering for callers that need specific memory tiers

---

#### FEATURE-059-C: Layer 2 — Domain Skills (Constructors, Mimic, Ontology Builder)

**Objective:** Build the domain-expert skills that synthesize raw inputs into structured knowledge representations.

##### C.1 — `x-ipe-knowledge-constructor-user-manual`

Synthesize extracted inputs into structured user manual documentation. Domain expert: knows what a user manual should look like.

**Operations:**
| Operation | Input | Output | Writes To |
|-----------|-------|--------|-----------|
| `provide_framework` | `request_context`, `output_format` | `framework_document`, `toc_structure` | `.working/framework/` |
| `design_rubric` | `framework`, `overview`, `user_request` | `rubric_metrics[]`, `acceptance_criteria[]` | `.working/rubric/` |
| `request_knowledge` | `framework`, `current_state`, `rubric` | `knowledge_requests[]` | `.working/plan/` |
| `fill_structure` | `framework`, `gathered_knowledge[]`, `rubric` | `completed_draft` | `.working/draft/` |

**Migrates from:** `x-ipe-tool-knowledge-extraction-user-manual` (cherry-pick useful domain logic; discard direct-write-to-KB pattern and standalone orchestration).

##### C.2 — `x-ipe-knowledge-constructor-notes`

Same 4-operation pattern as user-manual constructor, specialized for notes (meeting notes, braindumps, research summaries).

**Migrates from:** `x-ipe-tool-knowledge-extraction-notes`

##### C.3 — `x-ipe-knowledge-constructor-app-reverse-engineering`

Same 4-operation pattern, specialized for app reverse-engineering reports. **Depends on** all 8 `x-ipe-tool-rev-eng-*` tool skills (stay as-is).

**Migrates from:** `x-ipe-tool-knowledge-extraction-application-reverse-engineering`

##### C.4 — `x-ipe-knowledge-mimic-web-behavior-tracker`

Track web interaction behavior across sessions, consolidate observations into static knowledge views.

**Operations:**
| Operation | Input | Output | Writes To |
|-----------|-------|--------|-----------|
| `start_tracking` | `target_app`, `session_config` | `tracking_session_id` | `.working/observations/` |
| `stop_tracking` | `tracking_session_id` | `observation_summary`, `raw_events[]` | `.working/observations/` |
| `get_observations` | `tracking_session_id`, `filter` | `observations[]` | *(read-only)* |

**Migrates from:** `x-ipe-tool-learning-behavior-tracker-for-web`

> **Note:** If no second mimic skill materializes within 2 releases, consider folding into extractor with `--track` mode.

##### C.5 — `x-ipe-knowledge-ontology-builder`

Discover and build ontology structure from constructed knowledge using iterative breadth-first strategy with sub-agents.

**Operations:**
| Operation | Input | Output | Writes To |
|-----------|-------|--------|-----------|
| `discover_nodes` | `source_content`, `depth_limit` | `node_tree[]`, `discovery_report` | `.working/ontology/` |
| `discover_properties` | `class_meta`, `source_content`, `web_search_template` | `proposed_properties[]`, `search_results` | `.working/ontology/` |
| `create_instances` | `class_registry`, `source_content`, `property_schema` | `instances[]` | `.working/ontology/instances/` |
| `critique_validate` | `class_registry`, `instances[]`, `vocabulary_index` | `critique_report`, `term_issues[]` | `.working/ontology/` |
| `register_vocabulary` | `new_terms[]`, `target_scheme` | `updated_vocabulary`, `added_terms[]` | `.working/ontology/vocabulary/` |

**5-step builder discovery process:**
1. **Discover nodes** — breadth-first scan, create class meta entries
2. **Discover properties** — (a) web search general attributes, (b) context-specific design, (c) propose schema
3. **Create instances** — fill data instances per class
4. **Critique & validate** — sub-agent reviews accuracy, term consistency, completeness
5. **Register vocabulary** — add new terms to vocabulary schemes

**Self-bootstrap (`scripts/init_ontology.py`):** Creates ontology structure:
```
x-ipe-docs/memory/.ontology/
├── schema/
│   └── class-registry.jsonl
├── instances/
│   ├── _index.json
│   └── (class folders created on demand)
└── vocabulary/
    ├── _index.json
    ├── technology.json
    ├── domain.json
    ├── abstraction.json
    ├── audience.json
    ├── lifecycle.json
    └── content-type.json
```

**Acceptance Criteria:**
- All 5 operations functional with typed input/output contracts
- Builder uses sub-agents for parallel property discovery across classes
- Web search template pattern works for discovering general attributes
- Bootstrap creates ontology schema and vocabulary seed files

---

#### FEATURE-059-D: Layer 3 — Integration Skills (Ontology Synthesizer + Presenters)

**Objective:** Build skills that integrate across knowledge domains and deliver output.

##### D.1 — `x-ipe-knowledge-ontology-synthesizer`

Cross-graph integration: discover related graphs → normalize vocabulary → link nodes across domains.

**Operations:**
| Operation | Input | Output | Writes To |
|-----------|-------|--------|-----------|
| `discover_related` | `source_graph`, `search_scope` | `related_graphs[]`, `overlap_candidates[]` | `.working/ontology/` |
| `wash_terms` | `graphs[]`, `overlap_candidates[]` | `canonical_vocabulary`, `normalization_map` | `.working/ontology/` |
| `link_nodes` | `graphs[]`, `normalization_map`, `canonical_vocabulary` | `linked_graph`, `cross_references[]` | `.working/ontology/` |

**Synthesis versioning:** Bumps `synthesis_version` in class meta and records `synthesized_with` audit trail when merging/linking.

**Self-bootstrap (`scripts/init_relations.py`):** Creates `_relations.001.jsonl` with chunked relation storage (max 5000 records/chunk, append to highest, auto-split).

##### D.2 — `x-ipe-knowledge-present-to-user`

Format and deliver knowledge output to the user.

**Operations:**
| Operation | Input | Output | Writes To |
|-----------|-------|--------|-----------|
| `render` | `content_path`, `target` (user), `format` | `rendered_output` | *(output only)* |

##### D.3 — `x-ipe-knowledge-present-to-knowledge-graph`

Generate ontology graph visualization for the frontend UI.

**Operations:**
| Operation | Input | Output | Writes To |
|-----------|-------|--------|-----------|
| `connector` | `content_path`, `graph_data`, `target`, `ui_callback_config` | `graph_visualization`, `callback_status` | *(output via UI callback)* |

**Acceptance Criteria:**
- Synthesizer can discover overlap between two ontology graphs
- Term washing normalizes inconsistent labels to canonical vocabulary
- Node linking establishes cross-domain relationships without false positives
- Relation chunking works correctly (auto-split at 5000 records)
- Present-to-user renders knowledge in markdown/structured formats
- Present-to-knowledge-graph triggers UI callback for graph rendering

---

#### FEATURE-059-E: Layer 4 — Orchestrator (Knowledge Librarian + User Representative Migration)

**Objective:** Build the Knowledge Librarian DAO and migrate the user-representative to the assistant namespace.

##### E.1 — `x-ipe-assistant-knowledge-librarian-DAO`

The central coordinator for all knowledge operations, using the 格物致知 (investigate things to extend knowledge) workflow.

**格物致知 Workflow:**

| Phase | Step | Actor | Action |
|-------|------|-------|--------|
| 格物 (Plan) | Input Init | DAO | Classify request → identify target constructor |
| 格物 | 1. Framework | DAO → Constructor | Constructor provides overall structure/outline |
| 格物 | 2. Overview | Constructor → DAO → Extractor | Constructor requests topic overview; DAO uses extractors |
| 格物 | 3. Rubric | Constructor | Design rubric metrics from framework + overview + user request |
| 格物 | 4. Plan | Constructor → DAO | Constructor tells DAO what knowledge it needs per section |
| 致知 (Execute) | 1. Execute | DAO → Extractors | Coordinate extractors to fulfill each knowledge request |
| 致知 | 2. Fill & Draft | Constructor | Fill structure with gathered knowledge |
| 致知 | 3. Critique | Sub-agent | Evaluate against rubric; loop back to 格物.4 if gaps (max 3 iterations) |
| 致知 | 4. Ontology | DAO → Builder + Synthesizer | Build ontology nodes → synthesize cross-graph → critique ontology |
| 致知 | 5. Store | DAO → Keeper-memory | Persist to appropriate memory tier |
| 致知 | 6. Respond | DAO → Present | Deliver output to user |

**Constructor-driven paradigm:** The constructor is the domain expert. It drives the process by providing the framework first, then iteratively requesting what knowledge it needs. The DAO coordinates fulfillment by dispatching extractors and sub-agents.

**Skill discovery:** Discovers available knowledge skills via `.github/skills/x-ipe-knowledge-*/` glob pattern at runtime.

**Direct invocation:** Knowledge skills CAN be invoked directly by other skills (e.g., code-implementation calling extractor-memory). The Librarian is the *preferred* entry point for complex multi-step tasks, not a mandatory gateway.

##### E.2 — `x-ipe-assistant-user-representative-Engineer`

Migrate `x-ipe-dao-end-user-representative` to `x-ipe-assistant-user-representative-Engineer` (工程師). Same functionality, new namespace. The "dao" skill type becomes "assistant".

**Acceptance Criteria:**
- Librarian-DAO can route a request through full pipeline: classify → plan → extract → construct → critique → ontology → store → present
- Constructor-driven paradigm works: constructor defines framework → DAO fulfills knowledge requests
- Max 3 iteration guard prevents infinite loops in critique cycle
- Pure ontology operations (no constructor needed) handled correctly
- User-representative works identically under new namespace
- Auto-discovery via glob finds all knowledge skills

---

#### FEATURE-059-F: Layer 5 — Web App Updates, Migration & Deprecation

**Objective:** Rename UI labels, update data viewers, migrate old skills, and deprecate superseded skills.

##### F.1 — Web App Rename: "Knowledge Base" → "Memory"

| Area | Files Affected | Change |
|------|---------------|--------|
| Service layer | `kb_service.py`, `kb_routes.py` | Rename service/route references |
| Frontend JS | `kb-browse.js`, `kb-browse-modal.js`, `kb-reference-picker.js`, `kb-article-editor.js` | Update labels |
| Sidebar | `sidebar.js`, `sidebar.css` | Rename "Knowledge Base" → "Memory" |
| Templates | `index.html`, `content-renderer.js`, `instructions-template.md`, `instructions-template-no-dao.md` | Update references |
| Scaffold | `scaffold.py` | Reference `x-ipe-docs/memory/` instead of `knowledge-base/` |

##### F.2 — Ontology Graph Viewer Update

Update `ontology_graph_service.py`, `ontology_graph_routes.py`, `ontology-graph-viewer.js`, `ontology-graph-canvas.js`, `ontology-graph-socket.js` to point at new `.ontology/` structure (Schema/Instances/Vocabulary instead of flat JSONL).

##### F.3 — Present Connector Endpoint

Add UI callback endpoint in `ontology_graph_routes.py` for `present-to-knowledge-graph` connector operation to trigger interactive graph rendering in the frontend.

##### F.4 — Old Skill Deprecation & Removal

| Old Skill | Action | New Replacement |
|-----------|--------|-----------------|
| `x-ipe-tool-knowledge-extraction-user-manual` | Remove (one PR) | `x-ipe-knowledge-constructor-user-manual` |
| `x-ipe-tool-knowledge-extraction-notes` | Remove (one PR) | `x-ipe-knowledge-constructor-notes` |
| `x-ipe-tool-knowledge-extraction-application-reverse-engineering` | Remove (one PR) | `x-ipe-knowledge-constructor-app-reverse-engineering` |
| `x-ipe-task-based-application-knowledge-extractor` | Remove (one PR) | `x-ipe-knowledge-extractor-web` |
| `x-ipe-tool-learning-behavior-tracker-for-web` | Remove (one PR) | `x-ipe-knowledge-mimic-web-behavior-tracker` |
| `x-ipe-tool-kb-librarian` | Remove (one PR) | `x-ipe-knowledge-keeper-memory` (file-org logic) |
| `x-ipe-task-based-knowledge-referencer` | Remove (one PR) | `x-ipe-knowledge-extractor-memory` |
| `x-ipe-tool-user-manual-referencer` | Remove (one PR) | `x-ipe-knowledge-extractor-memory` |
| `x-ipe-tool-reference-ontology` | Remove (one PR) | `x-ipe-knowledge-ontology-builder` + `ontology-synthesizer` |
| `x-ipe-tool-ontology` | Remove (one PR) | `x-ipe-knowledge-ontology-builder` + `ontology-synthesizer` |
| `x-ipe-dao-end-user-representative` | Redirect → `x-ipe-assistant-user-representative-Engineer` | Same skill, new namespace |

**Migration rules:**
- Each removal is one independently revertable PR
- Alias/redirect shim active during transition period
- Old skill invocations continue to work via redirect until removal
- `x-ipe-knowledge-keeper-staging` — folded into `keeper-memory` as `memory_type: working`

##### F.5 — Rename Blast-Radius Audit: "dao" → "assistant"

Audit all references to "dao" skill type across: custom instructions glob patterns, SKILL.md procedure steps, skill-creator templates, hardcoded skill names, `available_skills` descriptions. Update to "assistant" namespace.

**Acceptance Criteria:**
- "Knowledge Base" → "Memory" rename complete (grep returns zero hits outside migration notes)
- Ontology graph viewer reads from new `.ontology/` 3-layer structure
- Present connector UI callback endpoint functional
- All 11 old skills removed with redirect shims (one PR each)
- "dao" → "assistant" rename complete across all references
- All general-purpose-executor calls updated from user-manual-referencer to extractor-memory

---

### Formal Data Model Schemas

#### Ontology Class Registry Schema (`schema/class-registry.jsonl` — one JSON object per line)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OntologyClassEntry",
  "type": "object",
  "required": ["class", "meta", "properties"],
  "properties": {
    "class": { "type": "string", "description": "Class name (PascalCase)" },
    "meta": {
      "type": "object",
      "required": ["description", "source_files", "synthesis_version", "created", "updated"],
      "properties": {
        "parent": { "type": ["string", "null"], "description": "Parent class name or null for root" },
        "abstract": { "type": "boolean", "default": false },
        "description": { "type": "string" },
        "source_files": { "type": "array", "items": { "type": "string" } },
        "synthesis_version": { "type": "string", "pattern": "^\\d+\\.\\d+$" },
        "synthesized_with": { "type": "array", "items": { "type": "string" }, "default": [] },
        "created": { "type": "string", "format": "date-time" },
        "updated": { "type": "string", "format": "date-time" }
      }
    },
    "properties": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["kind", "range"],
        "properties": {
          "kind": { "type": "string", "enum": ["datatype", "object", "vocabulary"] },
          "range": { "type": "string", "description": "Data type, class name, or vocabulary:scheme reference" },
          "cardinality": { "type": "string", "enum": ["single", "multi"], "default": "single" },
          "required": { "type": "boolean", "default": false },
          "constraints": { "type": "object" }
        }
      }
    }
  }
}
```

#### Ontology Instance Schema (one JSON object per line in `instances/{root-class}/{class}.jsonl`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OntologyInstance",
  "type": "object",
  "required": ["id", "class", "label", "source_files", "created", "updated"],
  "properties": {
    "id": { "type": "string", "pattern": "^know_\\d+$" },
    "class": { "type": "string" },
    "label": { "type": "string" },
    "description": { "type": ["string", "null"] },
    "weight": { "type": "integer", "minimum": 1, "maximum": 10, "default": 5 },
    "source_files": { "type": "array", "items": { "type": "string" } },
    "created": { "type": "string", "format": "date-time" },
    "updated": { "type": "string", "format": "date-time" }
  },
  "additionalProperties": true
}
```

#### Ontology Relation Schema (one JSON object per line in `instances/_relations.NNN.jsonl`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OntologyRelation",
  "type": "object",
  "required": ["subject_id", "predicate", "object_id", "created"],
  "properties": {
    "subject_id": { "type": "string", "description": "Source entity ID" },
    "predicate": { "type": "string", "description": "Relation type (dependsOn, partOf, relatedTo, etc.)" },
    "object_id": { "type": "string", "description": "Target entity ID" },
    "weight": { "type": "number", "minimum": 0, "maximum": 1, "default": 1.0 },
    "source": { "type": "string", "description": "Which skill/operation created this relation" },
    "created": { "type": "string", "format": "date-time" }
  }
}
```

#### Vocabulary Scheme Schema (`vocabulary/{scheme}.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VocabularyScheme",
  "type": "object",
  "required": ["scheme", "version", "description", "concepts"],
  "properties": {
    "scheme": { "type": "string" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+$" },
    "description": { "type": "string" },
    "concepts": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["label"],
        "properties": {
          "label": { "type": "string" },
          "description": { "type": "string" },
          "broader": { "type": "string" },
          "narrower": { "type": "array", "items": { "type": "string" } },
          "related": { "type": "array", "items": { "type": "string" } }
        }
      }
    }
  }
}
```

---

### Constraints

- **Write discipline**: `keeper-memory` writes content files to persistent folders (`episodic/`, `semantic/`, `procedural/`). `ontology-builder` writes entities to `.ontology/`, `ontology-synthesizer` writes relationships. All extractors, constructors, and mimic skills write exclusively to `.working/`.
- **Backward compatibility**: During migration, both old and new skills coexist. Old skill invocations continue via alias/redirect until final removal. Each migration PR must be independently revertable.
- **Incremental migration**: Skills are migrated one at a time — each migration is its own PR.
- **Self-bootstrapping**: Each skill's `scripts/` folder includes idempotent initialization. No separate infrastructure setup phase.
- **Relation chunking**: `_relations.NNN.jsonl` files max at 5000 records per chunk. Append to highest-numbered chunk; auto-create new chunk when full.
- **Direct invocation allowed**: Knowledge skills can be invoked directly by other skills (e.g., code-implementation calling extractor-memory). The Librarian-DAO is preferred but not mandatory.
- **Rollback strategy**: If the Librarian-DAO misbehaves, agents fall back to direct skill invocation (pre-librarian behavior).
- **Rev-eng tools untouched**: All 8 `x-ipe-tool-rev-eng-*` skills remain as-is under their current namespace.

### Risks & Mitigations

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | Scope size (13 skills + web app + migration) | HIGH | Build-layer approach — each layer testable in isolation |
| 2 | Backward compatibility during old skill deprecation | MEDIUM | Alias/redirect shim + one PR per skill + independently revertable |
| 3 | Web app rename blast radius (~30+ files) | LOW | Mechanical rename — grep + replace with verification |
| 4 | Ontology data migration from flat JSONL to 3-layer model | MEDIUM | Migration script in ontology-builder bootstrap |
| 5 | Self-bootstrapping idempotency edge cases | LOW | Standard check-before-create pattern |
| 6 | Skill-creator complexity (2 new types) | LOW | Follows existing template patterns |

### Open Questions

- None — all questions resolved during ideation (see [idea-summary-v1.md](x-ipe-docs/ideas/041.%20CR-Rebuild%20Knowledge%20Skills/idea-summary-v1.md) Resolved Questions section)

### Related Features

| Related EPIC | Relationship |
|-------------|--------------|
| EPIC-049 (KB Management & AI Librarian) | **RETIRED** — superseded by keeper-memory + librarian-DAO |
| EPIC-050 (Knowledge Extraction Pipeline) | **RETIRED** — superseded by extractor + constructor skills |
| EPIC-051 (Knowledge Extraction Notes) | **RETIRED** — superseded by constructor-notes |
| EPIC-053 (Knowledge Extraction App Rev-Eng) | **RETIRED** — superseded by constructor-app-reverse-engineering |
| EPIC-054 (Learning Behavior Tracker) | **RETIRED** — superseded by mimic-web-behavior-tracker |
| EPIC-058 (Feature-Ontology for Knowledgebase) | **RETIRED** — superseded by ontology-builder + ontology-synthesizer |
| EPIC-047 (DAO End-User Human Proxy) | **CR** — "dao" type renamed to "assistant" |
| EPIC-044 (Skill Creator) | **Dependency** — must support knowledge + assistant types |
| EPIC-041 (Custom Instructions) | **Dependency** — must include new glob patterns |
| EPIC-043 (Feature Board) | **Dependency** — tracks feature progress |
| EPIC-046 (Web App Architecture) | **Dependency** — web app updates build on this |

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| *(none — architecture DSL in idea summary)* | [idea-summary-v1.md § Architecture](x-ipe-docs/ideas/041.%20CR-Rebuild%20Knowledge%20Skills/idea-summary-v1.md) |
