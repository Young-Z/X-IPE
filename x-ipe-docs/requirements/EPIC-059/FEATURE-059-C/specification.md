# Feature Specification: Layer 2 — Domain Skills (Constructors + Mimic + Ontology-Builder)

> Feature ID: FEATURE-059-C  
> Version: v1.0  
> Status: Refined  
> Last Updated: 07-16-2025

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 07-16-2025 | Initial specification |
| v1.1 | 07-16-2025 | Redesign ontology-builder: collapse 5 operations into single `build_ontology` with iterative 6-step loop |

## Linked Mockups

N/A — Knowledge skills are non-visual (SKILL.md + templates/ + references/ + scripts/).

## Overview

FEATURE-059-C delivers five domain-level knowledge skills that sit on top of the Layer 1 core skills (FEATURE-059-B). These skills provide the intelligence layer — they know *what* knowledge to gather, *how* to structure it, and *how* to build the ontology graph from it.

The five skills are:

1. **`x-ipe-knowledge-constructor-user-manual`** — Domain expert for user manual construction. Provides framework, rubric, knowledge requests, and structure filling for user manual artifacts. Absorbs `x-ipe-tool-knowledge-extraction-user-manual`.
2. **`x-ipe-knowledge-constructor-notes`** — Domain expert for knowledge notes construction. Same 4-operation interface adapted for general knowledge notes. Absorbs `x-ipe-tool-knowledge-extraction-notes`.
3. **`x-ipe-knowledge-constructor-app-reverse-engineering`** — Domain expert for application reverse engineering. Same 4-operation interface with reverse engineering domain templates. Absorbs `x-ipe-tool-knowledge-extraction-application-reverse-engineering`. Delegates section extraction to existing `x-ipe-tool-rev-eng-*` sub-skills.
4. **`x-ipe-knowledge-mimic-web-behavior-tracker`** — Observes and records user behavior on websites via Chrome DevTools MCP. Migrates design from `x-ipe-tool-learning-behavior-tracker-for-web` into the new knowledge skill structure.
5. **`x-ipe-knowledge-ontology-builder`** — Discovers classes, properties, and instances from constructed knowledge and registers them in `.ontology/`. Writes directly to `.ontology/` with `Ephemeral` lifecycle flag for entities linked to `.working/` content.

Each skill follows the `x-ipe-knowledge` template (FEATURE-059-A) and is created via `x-ipe-meta-skill-creator`. Constructors ship with SKILL.md + `templates/` + `references/`. Mimic and ontology-builder additionally include `scripts/`.

Additionally, this feature deprecates 4 old tool skills by adding deprecation headers pointing to their replacements.

## User Stories

1. **As** the Knowledge Librarian assistant, **I want** domain-specific constructors that know the structure of user manuals, notes, and reverse engineering reports, **so that** I can orchestrate knowledge gathering by asking the constructor what knowledge is needed next.

2. **As** a constructor skill, **I want** to provide a framework and rubric for my domain, **so that** the gathered knowledge can be evaluated against measurable criteria before being finalized.

3. **As** the Knowledge Librarian assistant, **I want** a mimic skill that observes user behavior on websites via Chrome DevTools, **so that** I can capture interaction patterns as training data for AI agents.

4. **As** the Knowledge Librarian assistant, **I want** an ontology-builder that builds an ontology graph from source knowledge through iterative discovery, **so that** the ontology graph stays current as new knowledge is added to memory.

5. **As** a developer, **I want** old extraction tool skills deprecated with clear migration pointers, **so that** I know which new knowledge skill replaces each old tool.

6. **As** the ontology-builder, **I want** to mark entities as `Ephemeral` when they reference `.working/` content, **so that** downstream consumers know the entity may become orphaned if the working content is removed.

## Acceptance Criteria

### AC-059C-01: Constructor — provide_framework Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-01a | GIVEN a `request_context` describing a user manual project WHEN `provide_framework` is invoked on `constructor-user-manual` THEN a `framework_document` is returned containing domain-appropriate sections (Overview, Getting Started, Features, API Reference, Troubleshooting, FAQ) AND a `toc_structure` with section stubs | Unit |
| AC-059C-01b | GIVEN a `request_context` describing a notes project WHEN `provide_framework` is invoked on `constructor-notes` THEN a `framework_document` is returned with notes-appropriate sections AND the structure adapts to the `output_format` parameter | Unit |
| AC-059C-01c | GIVEN a `request_context` describing a reverse engineering project WHEN `provide_framework` is invoked on `constructor-app-reverse-engineering` THEN a `framework_document` references the 8 `x-ipe-tool-rev-eng-*` section sub-skills AND the `toc_structure` maps sections to sub-skill responsibilities | Unit |
| AC-059C-01d | GIVEN any constructor's `provide_framework` operation WHEN it completes THEN output is written to `.working/framework/` only (no persistent writes) AND the output includes `writes_to: .working/framework/` in its contract | Unit |

### AC-059C-02: Constructor — design_rubric Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-02a | GIVEN a `framework` and `overview` WHEN `design_rubric` is invoked THEN `rubric_metrics[]` is returned with measurable criteria per framework section (e.g., "Getting Started has ≥3 steps with code examples") | Unit |
| AC-059C-02b | GIVEN a `user_request` that emphasizes specific sections WHEN `design_rubric` is invoked THEN criteria weights reflect the user's priorities (high-weight for emphasized sections) | Unit |
| AC-059C-02c | GIVEN any constructor's `design_rubric` operation WHEN it completes THEN output is written to `.working/rubric/` only | Unit |

### AC-059C-03: Constructor — request_knowledge Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-03a | GIVEN a `framework`, `current_state` (partially filled), and `rubric` WHEN `request_knowledge` is invoked THEN `knowledge_requests[]` is returned with specific extraction requests per gap (e.g., "I need the list of CLI commands with their flags") | Unit |
| AC-059C-03b | GIVEN `knowledge_requests[]` output WHEN each request is inspected THEN it includes `target_section`, `what_needed`, and `suggested_extractor` (one of: extractor-web, extractor-memory) | Unit |
| AC-059C-03c | GIVEN all framework sections are already filled in `current_state` WHEN `request_knowledge` is invoked THEN an empty `knowledge_requests[]` is returned indicating no gaps remain | Unit |
| AC-059C-03d | GIVEN any constructor's `request_knowledge` operation WHEN it completes THEN output is written to `.working/plan/` only | Unit |

### AC-059C-04: Constructor — fill_structure Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-04a | GIVEN a `framework`, `gathered_knowledge[]`, and `rubric` WHEN `fill_structure` is invoked THEN a `completed_draft` is returned mapping gathered knowledge to framework sections | Unit |
| AC-059C-04b | GIVEN `gathered_knowledge[]` that does not fully satisfy the rubric WHEN `fill_structure` is invoked THEN the draft marks incomplete sections with `[INCOMPLETE: reason]` indicators | Unit |
| AC-059C-04c | GIVEN any constructor's `fill_structure` operation WHEN it completes THEN output is written to `.working/draft/` only (not persistent memory — keeper-memory handles promotion) | Unit |

### AC-059C-05: Constructor — Template and Reference Artifacts

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-05a | GIVEN `constructor-user-manual` WHEN its `templates/` folder is inspected THEN it contains domain-specific templates adapted from `x-ipe-tool-knowledge-extraction-user-manual/templates/` (playbook, collection template, app-type mixins) | Unit |
| AC-059C-05b | GIVEN `constructor-notes` WHEN its `templates/` folder is inspected THEN it contains notes-specific templates adapted from `x-ipe-tool-knowledge-extraction-notes/templates/` | Unit |
| AC-059C-05c | GIVEN `constructor-app-reverse-engineering` WHEN its `templates/` folder is inspected THEN it contains RE-specific templates adapted from `x-ipe-tool-knowledge-extraction-application-reverse-engineering/templates/` AND cross-references the 8 `x-ipe-tool-rev-eng-*` sub-skills | Unit |
| AC-059C-05d | GIVEN any constructor skill WHEN its `references/` folder is inspected THEN `examples.md` exists with at least one worked example per operation | Unit |

### AC-059C-06: Mimic — start_tracking Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-06a | GIVEN a `target_app` URL and `session_config` WHEN `start_tracking` is invoked THEN Chrome DevTools MCP is used to navigate to the URL AND the tracker IIFE is injected AND a `tracking_session_id` is returned AND session data is written to `x-ipe-docs/.mimicked/` | Integration |
| AC-059C-06b | GIVEN tracking is already active for a URL WHEN `start_tracking` is invoked again on the same URL THEN the IIFE guard prevents double injection AND the existing session ID is returned | Integration |
| AC-059C-06c | GIVEN `session_config` with `pii_whitelist` WHEN `start_tracking` is invoked THEN PII masking is configured with the whitelist AND password fields remain masked regardless | Integration |

### AC-059C-07: Mimic — stop_tracking Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-07a | GIVEN an active tracking session WHEN `stop_tracking` is invoked THEN events are collected from the circular buffer AND an `observation_summary` with flow narrative, key paths, and pain points is generated AND `raw_events[]` are returned | Integration |
| AC-059C-07b | GIVEN `stop_tracking` completes WHEN output is checked THEN all data is written to `x-ipe-docs/.mimicked/` (not `.working/` or persistent memory) | Unit |
| AC-059C-07c | GIVEN a non-existent `tracking_session_id` WHEN `stop_tracking` is invoked THEN an error is returned with SESSION_NOT_FOUND | Unit |

### AC-059C-08: Mimic — get_observations Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-08a | GIVEN an active or completed tracking session WHEN `get_observations` is invoked with a `filter` THEN matching `observations[]` are returned filtered by criteria | Unit |
| AC-059C-08b | GIVEN `get_observations` is invoked WHEN it completes THEN no files are written (read-only operation) | Unit |

### AC-059C-09: Ontology-Builder — build_ontology Content Learning (Step 1–2)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-09a | GIVEN `source_content` paths from semantic or procedural memory WHEN `build_ontology` is invoked THEN the builder reads all source files and produces a content overview summarizing key domains, entities, and relationships | Unit |
| AC-059C-09b | GIVEN the content overview WHEN the builder proposes an initial ontology graph THEN the proposal includes class candidates, instance candidates, and vocabulary term candidates — all derived from the source content | Unit |
| AC-059C-09c | GIVEN `depth_limit` is set to 1 WHEN `build_ontology` is invoked THEN only a single-pass flat scan is performed (no iterative drill-down) | Unit |

### AC-059C-10: Ontology-Builder — Critique Sub-Agent (Step 3)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-10a | GIVEN a proposed ontology graph WHEN the critique step runs THEN a sub-agent evaluates existing `.ontology/` for reuse opportunities AND returns constructive feedback categorized as {reuse[], modify[], create_new[], skip[]} | Integration |
| AC-059C-10b | GIVEN critique feedback WHEN the builder proceeds to implement THEN all reuse suggestions are incorporated before creating new entries (no duplicate classes or terms) | Unit |

### AC-059C-11: Ontology-Builder — Iterative Implement & Drill-Down (Steps 4–6)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-11a | GIVEN critique feedback with create_new items WHEN the builder implements THEN classes are registered via `ontology_ops.py register_class`, instances via `create_instance`, and vocabulary via `add_vocabulary` — all writing to `.ontology/` | Unit |
| AC-059C-11b | GIVEN unprocessed nodes remain WHEN the builder selects the next node THEN it picks the node with the richest unexplored source content AND reads linked source_files in depth | Unit |
| AC-059C-11c | GIVEN detailed content from a drill-down WHEN the builder discovers finer-grained classes/properties/instances THEN it loops back to critique (Step 3) before writing | Unit |

### AC-059C-12: Ontology-Builder — Auto Mode Rubric (depth_limit="auto")

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-12a | GIVEN `depth_limit` is `"auto"` WHEN the builder runs THEN it evaluates rubric metrics (concept_coverage, instance_coverage, vocabulary_coverage, hierarchy_coherence) after each iteration | Unit |
| AC-059C-12b | GIVEN all rubric metrics reach 100% WHEN the builder checks depth THEN it stops iterating and returns the build report with final rubric scores | Unit |
| AC-059C-12c | GIVEN iteration count reaches 10 WHEN rubric metrics are not yet 100% THEN the builder stops (safety cap) and returns partial rubric scores with an explanation | Unit |

### AC-059C-13: Ontology-Builder — Single Operation Interface

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-13a | GIVEN the ontology-builder skill WHEN its SKILL.md is inspected THEN it exposes exactly ONE operation (`build_ontology`) with input `source_content: string[]` + `depth_limit: 1 \| 3 \| "auto"` | Unit |
| AC-059C-13b | GIVEN `build_ontology` completes WHEN the output is checked THEN `build_report` contains `ontology_summary` (classes_created, instances_created, vocabulary_terms_added, classes_reused) and `iterations_completed` | Unit |

### AC-059C-14: Ontology-Builder — Ephemeral Lifecycle Flag

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-14a | GIVEN ontology-builder creates entities referencing `.working/` paths WHEN the entity is written to `.ontology/` THEN the entity record includes `lifecycle: "Ephemeral"` | Unit |
| AC-059C-14b | GIVEN ontology-builder creates entities referencing persistent memory paths (e.g., `semantic/`, `procedural/`) WHEN the entity is written to `.ontology/` THEN the entity record includes `lifecycle: "Persistent"` | Unit |

### AC-059C-15: Skill Template Compliance

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-15a | GIVEN each of the 5 new skills WHEN their SKILL.md is inspected THEN it follows the `x-ipe-knowledge` template structure (Operations as top-level sections, Steps inside each operation, typed contracts with `writes_to`) | Unit |
| AC-059C-15b | GIVEN each skill's SKILL.md WHEN the operations table is checked THEN every operation has `input`, `output`, `writes_to`, and `constraints` defined | Unit |
| AC-059C-15c | GIVEN the 3 constructor skills WHEN their folder structure is inspected THEN each has SKILL.md + `templates/` + `references/` (no `scripts/`) | Unit |
| AC-059C-15d | GIVEN mimic-web-behavior-tracker WHEN its folder structure is inspected THEN it has SKILL.md + `scripts/` (tracker IIFE, post-processor) + `references/` | Unit |
| AC-059C-15e | GIVEN ontology-builder WHEN its folder structure is inspected THEN it has SKILL.md + `scripts/` (ontology write utilities) + `references/` | Unit |

### AC-059C-16: Deprecation of Old Tool Skills

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059C-16a | GIVEN `x-ipe-tool-knowledge-extraction-user-manual` WHEN this feature is implemented THEN a deprecation header is added pointing to `x-ipe-knowledge-constructor-user-manual` | Unit |
| AC-059C-16b | GIVEN `x-ipe-tool-knowledge-extraction-notes` WHEN this feature is implemented THEN a deprecation header is added pointing to `x-ipe-knowledge-constructor-notes` | Unit |
| AC-059C-16c | GIVEN `x-ipe-tool-knowledge-extraction-application-reverse-engineering` WHEN this feature is implemented THEN a deprecation header is added pointing to `x-ipe-knowledge-constructor-app-reverse-engineering` | Unit |
| AC-059C-16d | GIVEN `x-ipe-tool-learning-behavior-tracker-for-web` WHEN this feature is implemented THEN a deprecation header is added pointing to `x-ipe-knowledge-mimic-web-behavior-tracker` | Unit |

## Functional Requirements

**FR-1: Constructor — provide_framework**
- Input: `request_context` (what app/project, user goal), `output_format` (notes|manual|report)
- Process: Load domain template → adapt to request context → return framework with section stubs
- Output: `framework_document`, `toc_structure`
- Writes to: `.working/framework/`

**FR-2: Constructor — design_rubric**
- Input: `framework`, `overview`, `user_request`
- Process: Define completeness/accuracy criteria per section → weight by user priority → return metrics
- Output: `rubric_metrics[]`, `acceptance_criteria[]`
- Writes to: `.working/rubric/`

**FR-3: Constructor — request_knowledge**
- Input: `framework`, `current_state`, `rubric`
- Process: Walk framework sections → check current state for gaps → generate extraction requests per gap → prioritize by rubric weight
- Output: `knowledge_requests[]` (each with `target_section`, `what_needed`, `suggested_extractor`)
- Writes to: `.working/plan/`

**FR-4: Constructor — fill_structure**
- Input: `framework`, `gathered_knowledge[]`, `rubric`
- Process: Map gathered knowledge to framework sections → mark incomplete sections → produce draft
- Output: `completed_draft`
- Writes to: `.working/draft/`

**FR-5: Mimic — start_tracking**
- Input: `target_app` (URL), `session_config` (pii_whitelist, buffer_capacity)
- Process: Navigate via Chrome DevTools MCP → inject tracker IIFE → configure PII masking → return session ID
- Output: `tracking_session_id`
- Writes to: `x-ipe-docs/.mimicked/`

**FR-6: Mimic — stop_tracking**
- Input: `tracking_session_id`
- Process: Collect events from buffer → run post-processing (flow narrative, key paths, pain points) → consolidate
- Output: `observation_summary`, `raw_events[]`
- Writes to: `x-ipe-docs/.mimicked/`

**FR-7: Mimic — get_observations**
- Input: `tracking_session_id`, `filter` (optional criteria)
- Process: Read stored observations → apply filter → return matches
- Output: `observations[]`
- Read-only (no writes)

**FR-8: Ontology-Builder — build_ontology (Single Operation)**
- Input: `source_content` (paths to memory files), `depth_limit` (1 | 3 | "auto", default: "auto")
- Process: 6-step iterative workflow:
  1. Learn source content → produce content overview
  2. Suggest basic ontology graph (classes, instances, vocabulary)
  3. Sub-agent critique → evaluate existing ontology reuse, give constructive feedback
  4. Implement changes based on feedback (register classes, create instances, add vocabulary)
  5. Broad search drill-down → select next unprocessed node
  6. Learn details via source_files → loop back to step 3
- Output: `build_report` {ontology_summary, rubric_scores (if auto), iterations_completed}
- Writes to: `.ontology/` (schema/, instances/, vocabulary/)
- Auto mode: rubric evaluation (concept_coverage, instance_coverage, vocabulary_coverage, hierarchy_coherence) targets 100%, safety cap at iteration 10

## Non-Functional Requirements

**NFR-1: Write Discipline** — Constructors write to `.working/` subfolders only. Mimic writes to `x-ipe-docs/.mimicked/` (a dedicated folder outside the memory structure). Ontology-builder writes directly to `.ontology/`. No domain skill writes to persistent memory folders — that remains keeper-memory's responsibility.

**NFR-2: Statelessness** — All five skills are stateless services. The orchestrator (Librarian) passes full context per invocation. No session state is retained between calls.

**NFR-3: Template Compliance** — All SKILL.md files must follow the `x-ipe-knowledge` template from FEATURE-059-A. Skill creation must go through `x-ipe-meta-skill-creator`.

**NFR-4: Ephemeral Lifecycle** — Ontology entities created from `.working/` content must be flagged `lifecycle: "Ephemeral"`. Entities from persistent memory are `lifecycle: "Persistent"`. This enables downstream consumers to know when an entity's source may be removed.

**NFR-5: Domain Template Reuse** — Constructor templates/ should migrate and adapt content from the old tool skills' templates/ folders, not reinvent from scratch. This preserves institutional knowledge.

**NFR-6: PII Safety** — Mimic-web-behavior-tracker must maintain the same PII masking guarantees as the original behavior tracker: mask-everything by default, opt-in whitelist, password fields never revealed.

## UI/UX Requirements

N/A — These are backend knowledge skills with no UI components.

## Dependencies

**Internal:**
- FEATURE-059-A (Implemented) — `x-ipe-knowledge` template must exist in skill-creator
- FEATURE-059-B (Implemented) — `keeper-memory`, `extractor-web`, `extractor-memory` must exist (constructor operations reference them via `suggested_extractor`)
- `x-ipe-meta-skill-creator` — Used to create all 5 skill SKILL.md files
- `x-ipe-tool-rev-eng-*` (8 existing sub-skills) — Referenced by `constructor-app-reverse-engineering` for section-level extraction
- Chrome DevTools MCP — Required by `mimic-web-behavior-tracker` at runtime
- Existing `.ontology/` folder structure (created by keeper-memory's `init_memory.py`) — Required by ontology-builder writes

**External:**
- Web search API — Used internally by ontology-builder's critique sub-agent during the build_ontology iterative loop

## Business Rules

**BR-1:** Constructors are domain experts — they know the structure of their domain artifact (user manual, notes, RE report). The orchestrator (Librarian) does not have this domain knowledge and relies on the constructor's `request_knowledge` output to decide what to fetch.

**BR-2:** The 4-operation constructor interface (`provide_framework` → `design_rubric` → `request_knowledge` → `fill_structure`) is the standard pattern. All three constructors implement this interface with domain-specific templates and logic.

**BR-3:** Ontology-builder writes directly to `.ontology/` (not `.working/ontology/`). Entities linked to transient `.working/` content are marked `lifecycle: "Ephemeral"`.

**BR-4:** Mimic only writes to `x-ipe-docs/.mimicked/`. Promoting observations to persistent memory is done via `keeper-memory.promote`, not by mimic itself.

**BR-5:** The `x-ipe-tool-rev-eng-*` sub-skills remain as tool skills (not migrated to knowledge namespace). `constructor-app-reverse-engineering` references them as external dependencies.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Constructor invoked with no prior overview | `request_knowledge` identifies all sections as gaps, returns full extraction list |
| `fill_structure` with partial knowledge | Draft produced with `[INCOMPLETE: reason]` markers on unfilled sections |
| Mimic start on already-tracked page | IIFE guard prevents double injection, existing session ID returned |
| Mimic stop with invalid session ID | Error returned with SESSION_NOT_FOUND, no side effects |
| Ontology-builder discovers no classes in source | Empty build_report with classes_created=0; no writes to .ontology/ |
| Ontology-builder finds existing class in .ontology/ | Critique sub-agent suggests reuse; builder references existing class instead of creating duplicate |
| Entity references `.working/` path that was already cleaned up | Entity remains with `lifecycle: "Ephemeral"` — downstream consumers check source existence |
| Auto mode rubric cannot reach 100% within 10 iterations | Safety cap stops iteration; build_report includes partial rubric_scores and explanation |

## Out of Scope

- **Ontology-synthesizer** (discover_related, wash_terms, link_nodes) — deferred to FEATURE-059-D
- **Presenter skills** (render, connector) — deferred to FEATURE-059-D
- **Orchestrator/Librarian assistant** — deferred to FEATURE-059-E
- **Migration of existing knowledge-base content** — deferred to FEATURE-059-F
- **Modifications to `x-ipe-tool-rev-eng-*` sub-skills** — they remain as-is, referenced by constructor
- **Web app UI changes** — deferred to FEATURE-059-F
- **Chunk management for ontology files** — handled by ontology-builder's own scripts, not a separate concern

## Technical Considerations

- Each skill is a `.github/skills/x-ipe-knowledge-{sub-category}-{name}/` directory
- Constructor skills: SKILL.md + `templates/` (domain templates migrated from old tool skills) + `references/` (examples.md)
- Mimic skill: SKILL.md + `scripts/` (tracker-toolbar.js/mini.js, post_processor.py migrated from old behavior tracker) + `references/`
- Ontology-builder skill: SKILL.md + `scripts/` (ontology write utilities for JSONL files) + `references/`
- All skills created via `x-ipe-meta-skill-creator` (candidate/ → validate → merge workflow)
- Ontology-builder's `lifecycle` field should be added to entity JSONL records alongside existing fields
- Ontology-builder exposes a single `build_ontology` operation with iterative critique-implement loop — the orchestrator does NOT call separate discover/create/validate steps
- Constructor templates should be adapted (not copy-pasted) from old skills to fit the 4-operation interface

## Open Questions

None — all questions resolved during refinement.
