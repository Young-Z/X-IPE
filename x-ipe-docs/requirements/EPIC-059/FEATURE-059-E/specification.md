# Feature Specification: Layer 4 — Orchestrator (Knowledge Librarian + User Representative Migration)

> Feature ID: FEATURE-059-E  
> Version: v1.0  
> Status: Refined  
> Last Updated: 04-20-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-20-2026 | Initial specification |

## Linked Mockups

N/A — Assistant skills are non-visual (SKILL.md + templates/ + references/).

## Overview

FEATURE-059-E delivers the orchestration layer for the knowledge pipeline — the Knowledge Librarian assistant that coordinates all knowledge skills into a coherent end-to-end workflow, plus the migration of the existing user representative from the deprecated `dao` namespace to the new `assistant` namespace.

The Knowledge Librarian (`x-ipe-assistant-knowledge-librarian-DAO`) is the central coordinator for all knowledge operations. It implements the 格物致知 (investigate things to extend knowledge) workflow — a two-phase process where 格物 (investigate/plan) gathers context and designs a rubric, and 致知 (reach understanding/execute) fulfills knowledge requests, builds the draft, runs critique loops, processes ontology, stores results, and presents output. The Librarian follows a **constructor-driven paradigm**: the constructor is the domain expert that provides the framework, designs rubrics, and requests specific knowledge; the Librarian coordinates fulfillment by dispatching extractors and sub-agents.

The User Representative migration (`x-ipe-assistant-user-representative-Engineer`) renames `x-ipe-assistant-user-representative-Engineer` to the assistant namespace and adapts its structure to conform to the `x-ipe-assistant` template (FEATURE-059-A). Functionality is preserved; the skill structure is modernized.

Both skills follow the `x-ipe-assistant` template and are created via `x-ipe-meta-skill-creator`.

## User Stories

1. **As** a developer or agent, **I want** a single entry point for complex knowledge tasks (e.g., "build a user manual for app X"), **so that** I don't need to manually orchestrate extractors, constructors, ontology tools, and storage.

2. **As** the Knowledge Librarian, **I want** to discover available knowledge skills at runtime via glob pattern, **so that** newly added knowledge skills are automatically available without hardcoded registries.

3. **As** the Knowledge Librarian, **I want** to semantically understand an incoming request and route it to the best-matching constructor, **so that** the right domain expert handles the knowledge construction.

4. **As** the Knowledge Librarian, **I want** to run a critique loop with a max-3-iteration guard, **so that** the constructed draft meets the rubric quality bar without falling into infinite loops.

5. **As** the Knowledge Librarian, **I want** to handle pure ontology operations (discover + wash + link) without needing a constructor, **so that** ontology maintenance tasks don't require unnecessary knowledge construction overhead.

6. **As** the Knowledge Librarian, **I want** the constructor to drive the process by providing a framework first, then iteratively requesting what knowledge it needs, **so that** the extraction effort is targeted and efficient rather than broad and wasteful.

7. **As** a developer, **I want** the user representative to work under the new `x-ipe-assistant-*` namespace while preserving all existing functionality, **so that** the namespace migration doesn't break existing DAO call sites during transition.

8. **As** the system, **I want** the Librarian to support replanning — if the critique loop identifies gaps, the Librarian returns to the plan phase for the constructor to request additional knowledge, **so that** the process is iterative and self-correcting.

## Acceptance Criteria

### AC-059E-01: Librarian — Skill Discovery

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059E-01a | GIVEN the Librarian is invoked WHEN it initializes THEN it discovers available knowledge skills by scanning `.github/skills/x-ipe-knowledge-*/SKILL.md` via glob pattern AND builds a `discovered_skills[]` registry with skill name, operations, and description | Unit |
| AC-059E-01b | GIVEN a new knowledge skill is added to `.github/skills/` WHEN the Librarian is invoked THEN the new skill appears in `discovered_skills[]` without any configuration change | Unit |
| AC-059E-01c | GIVEN the glob scan completes WHEN `discovered_skills[]` is examined THEN skills are categorized by role: `extractors[]`, `constructors[]`, `keepers[]`, `presenters[]`, `ontology[]`, `mimics[]` based on the skill name prefix pattern (e.g., `x-ipe-knowledge-extractor-*` → extractors) | Unit |
| AC-059E-01d | GIVEN the Librarian discovers skills WHEN a non-knowledge skill exists at `.github/skills/x-ipe-tool-*` THEN it is NOT included in `discovered_skills[]` (only `x-ipe-knowledge-*` namespace is scanned) | Unit |

### AC-059E-02: Librarian — Request Classification & Constructor Routing

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059E-02a | GIVEN a knowledge request (e.g., "build a user manual for app X") WHEN the Librarian classifies it THEN it identifies the request type as `construction` AND selects the best-matching constructor from `discovered_skills.constructors[]` by semantic analysis of the request against each constructor's description and operations | Unit |
| AC-059E-02b | GIVEN a request like "extract knowledge from this website" with no construction target WHEN the Librarian classifies it THEN it identifies the request type as `extraction` AND routes directly to the appropriate extractor without involving a constructor | Unit |
| AC-059E-02c | GIVEN a request like "discover related graphs and link ontology nodes" WHEN the Librarian classifies it THEN it identifies the request type as `ontology_only` AND routes to the synthesizer pipeline (discover → wash → link) without involving a constructor or extractor | Unit |
| AC-059E-02d | GIVEN an ambiguous request that could match multiple constructors WHEN the Librarian classifies it THEN it selects the constructor with the highest semantic relevance score AND logs the selection reasoning | Unit |
| AC-059E-02e | GIVEN a request that matches no known constructor or operation type WHEN the Librarian classifies it THEN it returns a `classification_failed` response with a list of available capabilities AND does not proceed with an arbitrary constructor | Unit |

### AC-059E-03: Librarian — 格物 Phase (Plan)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059E-03a | GIVEN a classified `construction` request WHEN the 格物 phase begins THEN the Librarian invokes the selected constructor's `provide_framework` operation AND receives a `framework_document` with domain-appropriate structure | Unit |
| AC-059E-03b | GIVEN a `framework_document` from the constructor WHEN the Librarian needs topic context THEN it invokes the appropriate extractor's `extract_overview` operation to gather high-level context AND passes the overview back to the constructor | Unit |
| AC-059E-03c | GIVEN the constructor has received the framework and overview WHEN `design_rubric` is invoked THEN the constructor returns `rubric_metrics[]` with measurable quality criteria per framework section | Unit |
| AC-059E-03d | GIVEN rubric metrics are defined WHEN the constructor's `request_knowledge` operation is invoked THEN it returns `knowledge_requests[]` specifying what knowledge is needed, for which section, and which extractor to use | Unit |
| AC-059E-03e | GIVEN the 格物 phase completes WHEN all intermediate artifacts are examined THEN framework is in `.working/framework/`, rubric is in `.working/rubric/`, and plan is in `.working/plan/` (all ephemeral, no persistent writes) | Unit |

### AC-059E-04: Librarian — 致知 Phase (Execute)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059E-04a | GIVEN `knowledge_requests[]` from the constructor WHEN the 致知 execute step begins THEN the Librarian dispatches each request to the appropriate extractor (extractor-web for URLs, extractor-memory for existing knowledge) AND collects `gathered_knowledge[]` | Unit |
| AC-059E-04b | GIVEN `gathered_knowledge[]` is collected WHEN the Librarian invokes the constructor's `fill_structure` operation THEN the constructor returns a `completed_draft` with knowledge mapped to framework sections AND incomplete sections marked with `[INCOMPLETE: reason]` | Unit |
| AC-059E-04c | GIVEN a `completed_draft` and `rubric_metrics[]` WHEN the critique sub-agent evaluates the draft THEN it returns a `critique_result` with per-section scores, identified gaps, and a `pass` or `fail` overall verdict | Unit |
| AC-059E-04d | GIVEN critique returns `fail` with identified gaps WHEN the Librarian processes the critique THEN it returns to 格物 Phase Step 4 (request_knowledge) for the constructor to request additional knowledge for the gap sections AND increments `iteration_count` | Unit |
| AC-059E-04e | GIVEN `iteration_count` reaches 3 AND critique still returns `fail` WHEN the Librarian evaluates whether to continue THEN it stops the loop, logs a warning with remaining gaps, marks the draft as `partial_quality`, and proceeds to the ontology step | Unit |
| AC-059E-04f | GIVEN critique returns `pass` WHEN the Librarian processes the result THEN it proceeds directly to the ontology step without further iteration | Unit |

### AC-059E-05: Librarian — Ontology Processing

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059E-05a | GIVEN a completed or partial-quality draft WHEN the Librarian runs the ontology step THEN it invokes `ontology-builder`'s `build_ontology` operation on the draft content AND receives `ontology_result` with created/updated entities | Unit |
| AC-059E-05b | GIVEN ontology entities are built WHEN the Librarian invokes `ontology-synthesizer` THEN it runs the full synthesizer pipeline (discover_related → wash_terms → link_nodes) AND receives `synthesis_result` with cross-graph relationships | Unit |
| AC-059E-05c | GIVEN an `ontology_only` request type (no constructor) WHEN the Librarian processes the request THEN it skips framework/rubric/extraction/draft steps AND directly invokes `ontology-synthesizer` on the specified graphs | Unit |
| AC-059E-05d | GIVEN the ontology step completes WHEN examining `.ontology/` THEN new entities have `synthesize_id` timestamps AND new relations exist in `_relations.NNN.jsonl` | Unit |

### AC-059E-06: Librarian — Storage & Presentation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059E-06a | GIVEN a completed draft with ontology processed WHEN the Librarian runs the store step THEN it invokes `keeper-memory`'s `store` operation with the appropriate `memory_type` (semantic for facts/findings, procedural for user manuals/patterns, episodic for session-specific notes) | Unit |
| AC-059E-06b | GIVEN storage is complete WHEN the Librarian runs the respond step THEN it invokes `present-to-user`'s `render` operation AND returns the formatted summary to the caller | Unit |
| AC-059E-06c | GIVEN the caller requests graph visualization WHEN the Librarian processes the present step THEN it additionally invokes `present-to-knowledge-graph`'s `connect` operation to push the ontology to the frontend viewer | Unit |
| AC-059E-06d | GIVEN the full pipeline completes WHEN examining `.working/` THEN all intermediate artifacts remain for audit AND no `.working/` content was written to persistent memory (only `keeper-memory` promotes content) | Unit |

### AC-059E-07: Librarian — End-to-End Pipeline

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059E-07a | GIVEN a complete knowledge request (e.g., "build a user manual for app X") WHEN the Librarian executes the full pipeline THEN it runs: classify → framework → overview → rubric → plan → extract → fill → critique → ontology → store → present AND returns a success result with `pipeline_summary` | Integration |
| AC-059E-07b | GIVEN the Librarian starts the pipeline WHEN any individual skill invocation fails THEN the Librarian logs the error, marks the pipeline step as `failed`, and returns a partial result with `pipeline_status: partial` AND a list of completed vs failed steps | Integration |
| AC-059E-07c | GIVEN multiple knowledge requests in sequence WHEN the Librarian processes them THEN each request gets its own `.working/` session subfolder AND pipelines do not interfere with each other | Unit |

### AC-059E-08: Librarian — Direct Invocation Support

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059E-08a | GIVEN a caller invokes a knowledge skill directly (e.g., `extractor-memory` called by `code-implementation`) WHEN the call bypasses the Librarian THEN the knowledge skill executes normally without requiring Librarian coordination | Unit |
| AC-059E-08b | GIVEN the Librarian is not available (e.g., not discovered or errored) WHEN an agent needs knowledge operations THEN the agent can fall back to direct skill invocation as a degraded-mode fallback | Unit |

### AC-059E-09: User Representative — Namespace Migration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059E-09a | GIVEN the existing `x-ipe-assistant-user-representative-Engineer` skill WHEN migrated to `x-ipe-assistant-user-representative-Engineer` THEN the new skill folder exists at `.github/skills/x-ipe-assistant-user-representative-Engineer/` with SKILL.md, references/, and templates/ subfolders | Unit |
| AC-059E-09b | GIVEN the migrated skill WHEN its SKILL.md is examined THEN it conforms to the `x-ipe-assistant` template structure (from `.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-assistant.md`) while preserving all existing functionality (disposition types, instruction units, human shadow, execution plan) | Unit |
| AC-059E-09c | GIVEN the migrated skill WHEN invoked with the same input as the old `x-ipe-assistant-user-representative-Engineer` THEN it produces functionally identical output (same disposition types, same instruction_units format, same fallback behavior) | Integration |
| AC-059E-09d | GIVEN custom instructions reference `x-ipe-assistant-user-representative-Engineer` WHEN the migration is complete THEN the old skill name still resolves (redirect/alias) during the transition period AND new code uses `x-ipe-assistant-user-representative-Engineer` | Unit |
| AC-059E-09e | GIVEN the migrated skill WHEN its name/description metadata is examined THEN it uses the name `x-ipe-assistant-user-representative-Engineer` AND the description includes "工程師" (Engineer) persona context | Unit |

### AC-059E-10: Librarian — SKILL.md Structure

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059E-10a | GIVEN `x-ipe-assistant-knowledge-librarian-DAO` WHEN its SKILL.md is examined THEN it conforms to the `x-ipe-assistant` template with orchestration procedure sections (Purpose, Input Parameters, Execution Procedure with phases, Output Result) | Unit |
| AC-059E-10b | GIVEN the Librarian's SKILL.md WHEN the execution procedure is examined THEN it documents the full 格物致知 workflow with phase markers (格物.1 through 格物.4, 致知.1 through 致知.6) AND each step specifies the actor (DAO, Constructor, Extractor, Sub-agent) | Unit |
| AC-059E-10c | GIVEN the Librarian's SKILL.md WHEN the input parameters are examined THEN it documents: `request` (the knowledge task), `request_type_override` (optional — skip classification), `target_constructor` (optional — skip routing), `max_iterations` (default: 3), `output_format` (structured\|markdown\|graph) | Unit |
| AC-059E-10d | GIVEN the Librarian's SKILL.md WHEN the output result is examined THEN it documents: `pipeline_summary`, `pipeline_status` (success\|partial\|failed), `completed_steps[]`, `stored_path`, `ontology_result`, `presented_output` | Unit |

## Functional Requirements

### FR-1: Skill Discovery Engine

The Librarian MUST discover knowledge skills at runtime using the glob pattern `.github/skills/x-ipe-knowledge-*/SKILL.md`. It categorizes discovered skills by their name prefix into roles: extractors (`extractor-*`), constructors (`constructor-*`), keepers (`keeper-*`), presenters (`present-*`), ontology tools (`ontology-*`), and mimics (`mimic-*`). The discovery result is cached for the duration of a single pipeline execution (no cross-session caching).

### FR-2: Semantic Request Classification

The Librarian MUST semantically analyze incoming requests to determine the request type:
- `construction` — requires a constructor (matched by semantic similarity to constructor descriptions/operations)
- `extraction` — raw extraction without construction (e.g., "get content from URL")
- `ontology_only` — pure ontology operations (e.g., "discover and link graphs")
- `presentation` — render existing knowledge (e.g., "summarize this knowledge")
- `storage` — promote working content to memory (e.g., "save this to semantic memory")

The constructor selection uses semantic analysis — comparing the request content against each constructor's SKILL.md description and operation definitions to find the best match.

### FR-3: 格物致知 Workflow Engine

The Librarian MUST implement the two-phase workflow:

**格物 (Plan) Phase:**
1. **Input Init**: Classify request → identify request type → select constructor (if applicable)
2. **Framework**: Invoke constructor's `provide_framework` → receive domain structure
3. **Overview**: Invoke extractor to gather topic overview → pass back to constructor
4. **Rubric**: Invoke constructor's `design_rubric` → receive quality metrics
5. **Plan**: Invoke constructor's `request_knowledge` → receive extraction plan

**致知 (Execute) Phase:**
1. **Execute**: Dispatch extractors per knowledge_requests[] → collect gathered_knowledge[]
2. **Fill & Draft**: Invoke constructor's `fill_structure` → receive completed_draft
3. **Critique**: Launch sub-agent evaluator against rubric → loop back to 格物.4 if gaps (max 3 iterations)
4. **Ontology**: Invoke ontology-builder → ontology-synthesizer pipeline
5. **Store**: Invoke keeper-memory to persist to appropriate tier
6. **Respond**: Invoke present-to-user (and optionally present-to-knowledge-graph) to deliver output

### FR-4: Critique Loop with Iteration Guard

The critique step MUST:
- Launch a sub-agent to evaluate the draft against rubric_metrics[]
- Return per-section scores and identified gaps
- If gaps exist and iteration_count < 3: return to 格物 Phase Step 4 for replanning
- If iteration_count reaches 3: stop looping, log warning, proceed with `partial_quality` flag
- Track iteration_count as state within the pipeline execution

### FR-5: Pipeline Error Handling

When any skill invocation fails during the pipeline:
- Log the error with skill name, operation, and error details
- Mark the pipeline step as `failed`
- Continue with remaining steps where possible (graceful degradation)
- Return partial results with `pipeline_status: partial` and a step-by-step completion log

### FR-6: User Representative Migration

The migration MUST:
- Create `x-ipe-assistant-user-representative-Engineer` as a new skill folder
- Adapt the existing `x-ipe-assistant-user-representative-Engineer` SKILL.md to conform to the `x-ipe-assistant` template
- Preserve all existing functionality: disposition types, instruction units, human shadow, execution plan, fallback behavior
- Add "工程師" (Engineer) persona context to the description
- Ensure the old skill name resolves via redirect/alias during transition

## Non-Functional Requirements

### NFR-1: Performance
- Skill discovery via glob MUST complete in < 2 seconds
- Request classification MUST complete in < 5 seconds
- The full pipeline timeout is governed by individual skill timeouts, not a global timer

### NFR-2: Reliability
- Max-3-iteration guard MUST be enforced — no infinite loops under any circumstance
- Pipeline failures MUST be gracefully handled with partial results returned
- Direct invocation fallback MUST always work if the Librarian is unavailable

### NFR-3: Extensibility
- Adding a new knowledge skill MUST require zero Librarian configuration changes
- New constructors are automatically discoverable and routable

### NFR-4: Auditability
- Each pipeline execution MUST log: request classification, constructor selection reasoning, iteration count, step completion status
- All intermediate artifacts persist in `.working/` for post-execution audit

## UI/UX Requirements

N/A — Assistant skills are invoked programmatically by agents, not directly by end users.

## Dependencies

### Internal Dependencies
| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-059-A | Prerequisite | Provides `x-ipe-assistant` template in skill-creator |
| FEATURE-059-B | Prerequisite | Provides `keeper-memory`, `extractor-web`, `extractor-memory` skills |
| FEATURE-059-C | Prerequisite | Provides all 3 constructors, `mimic`, and `ontology-builder` skills |
| FEATURE-059-D | Prerequisite | Provides `ontology-synthesizer`, `present-to-user`, `present-to-knowledge-graph` skills |
| `x-ipe-meta-skill-creator` | Tool | Creates the assistant skill structure |
| `x-ipe-assistant-user-representative-Engineer` | Source | Existing skill to migrate for E.2 |

### External Dependencies
None.

## Business Rules

| Rule ID | Rule |
|---------|------|
| BR-1 | The Librarian is the PREFERRED entry point for complex multi-step knowledge tasks, but NOT a mandatory gateway. Knowledge skills CAN be invoked directly by other agents. |
| BR-2 | The critique loop MUST NOT exceed 3 iterations. After 3 iterations, the draft is accepted as `partial_quality` regardless of rubric score. |
| BR-3 | All intermediate artifacts (framework, rubric, plan, gathered knowledge, drafts) MUST be written to `.working/` only. Only `keeper-memory` writes to persistent memory. |
| BR-4 | The Librarian MUST NOT expand the scope of a request beyond what was asked. If a user requests extraction only, do not auto-trigger construction. |
| BR-5 | Constructor-driven paradigm: the constructor defines WHAT knowledge is needed. The Librarian fulfills HOW to get it. The Librarian does not decide knowledge structure — the constructor does. |
| BR-6 | If the Librarian misbehaves or is unavailable, agents MUST be able to fall back to direct skill invocation (pre-Librarian behavior). |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| No constructors discovered | Classification returns `classification_failed` with available capabilities (extractors, ontology, etc.) — no construction requests accepted |
| Constructor's `request_knowledge` returns empty list | Skip extraction, proceed directly to fill_structure with existing overview knowledge |
| All extractors fail during Execute step | Log errors, pass empty gathered_knowledge to fill_structure — constructor marks all sections as `[INCOMPLETE]` |
| Critique returns `pass` on first iteration | Skip replanning, proceed directly to ontology step |
| Pure ontology request with no existing graphs | ontology-synthesizer's discover_related returns empty — Librarian logs "no graphs to synthesize" and returns success with empty synthesis result |
| Request matches multiple constructors equally | Select the first match alphabetically and log the tie-breaking decision |
| Pipeline interrupted mid-execution | `.working/` retains all artifacts up to the interruption point for manual recovery |

## Out of Scope

- **Tool skill discovery** — The Librarian does NOT discover or coordinate `x-ipe-tool-*` skills
- **Assistant skill delegation** — The Librarian does NOT dispatch to other assistant skills
- **Deprecation of old `x-ipe-assistant-user-representative-Engineer`** — That is tracked in FEATURE-059-F
- **Web app UI changes** — No frontend changes in this feature
- **Content migration** — Existing knowledge content stays in old locations
- **Cross-session state** — Each pipeline execution is stateless; no persistent Librarian state between sessions

## Technical Considerations

- The Librarian is an `x-ipe-assistant` type skill — it uses the orchestration procedure template, not Operations + Steps
- Skill discovery uses filesystem glob, not a registry — this means the Librarian is always in sync with deployed skills
- The critique sub-agent should use a premium model (e.g., `claude-opus-4.6`) for high-quality evaluation
- Constructor selection via semantic analysis means the Librarian needs to read each constructor's SKILL.md description at discovery time
- The 格物致知 workflow maps naturally to a state machine with well-defined transitions; pipeline_status tracks the current state
- `.working/` session isolation: each pipeline execution should use a unique subfolder (e.g., `.working/session-{timestamp}/`) to prevent cross-execution interference

## Open Questions

None — all questions resolved during specification review.
