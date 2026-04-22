---
name: x-ipe-assistant-knowledge-librarian-DAO
description: Central orchestrator for the knowledge pipeline. Discovers available knowledge skills at runtime, classifies requests, routes to constructors/extractors/ontology skills, and drives the full 格物致知 workflow. Triggers on requests like "build a user manual", "extract knowledge", "run knowledge pipeline", "discover ontology graphs".
---

# Knowledge Librarian — Assistant Skill

## Purpose

AI Agents follow this skill to orchestrate the knowledge pipeline by:
1. Discovering available `x-ipe-knowledge-*` skills at runtime and classifying incoming requests
2. Driving the 格物致知 workflow: plan (framework → overview → rubric → requests) then execute (extract → fill → critique → ontology → store → present)
3. Tracking pipeline state step-by-step with graceful degradation on individual failures

---

## Important Notes

BLOCKING: This skill coordinates knowledge skills — it does NOT perform extraction, construction, or ontology operations itself. Each step delegates to the appropriate knowledge skill.
CRITICAL: Knowledge skills CAN be invoked directly without this orchestrator as a degraded-mode fallback (AC-059E-08a/b).
CRITICAL: The 格物致知 backbone is the INTERNAL orchestration methodology — callers see only pipeline_summary output, never phase names.

CRITICAL: **Best-Model Requirement.** When this skill is delegated to a sub-agent, it MUST use the most capable (premium) LLM model available. The orchestration logic requires nuanced semantic matching and critique evaluation.

---

## About

This skill serves as the central coordinator for the entire knowledge pipeline (Layers 1–3). Given a knowledge request (e.g., "build a user manual for app X"), it discovers which skills are available, classifies the request type, selects the best-matching constructor, and orchestrates the full plan-execute cycle.

**CORE Backbone — 格物致知 (Investigate to Reach Understanding):** The Librarian's orchestration follows a two-phase framework: 格物 (plan the knowledge acquisition) gathers framework, overview, rubric, and knowledge requests; 致知 (execute the plan) dispatches extractors, fills drafts, critiques quality, processes ontology, stores results, and presents output.

**Key Concepts:**
- **Skill Discovery** — Runtime glob scan of `.github/skills/x-ipe-knowledge-*/SKILL.md` builds a categorized registry
- **Semantic Routing** — Request text matched against constructor descriptions for best-fit selection
- **Critique Loop** — Sub-agent evaluates draft against rubric; max 3 iterations before accepting partial quality
- **Pipeline State** — Each step tracked independently; failures are logged and pipeline continues where possible

---

## When to Use

```yaml
triggers:
  - "Build a user manual for an application"
  - "Extract knowledge from a website or memory"
  - "Construct notes from source material"
  - "Discover and link ontology graphs across domains"
  - "Run the full knowledge pipeline"
  - "Store knowledge to persistent memory"

not_for:
  - "Direct knowledge skill invocation (skills work standalone as fallback)"
  - "Task board management (use x-ipe-tool-task-board-manager)"
  - "Feature workflow orchestration (use x-ipe-workflow-task-execution)"
  - "Non-knowledge operations (code implementation, testing, etc.)"
```

---

## Input Parameters

```yaml
input:
  request: "string"                          # Required — the knowledge task description
  request_type_override: "string | null"     # Optional — skip classification (construction|extraction|ontology_only|presentation|storage)
  target_constructor: "string | null"        # Optional — skip routing (specific constructor skill name)
  max_iterations: 3                          # Optional — critique loop max iterations
  output_format: "markdown"                  # Optional — structured | markdown | graph
  session_context:                           # Optional — caller context
    task_id: "{TASK-XXX | N/A}"
    feature_id: "{FEATURE-XXX | N/A}"
    workflow_name: "{name | N/A}"
```

### Input Initialization

```xml
<input_init>
  <field name="request" source="Caller provides the knowledge task description">
    <validation>MUST be non-empty string. FAIL FAST if missing.</validation>
  </field>
  <field name="request_type_override" source="Caller may override classification">
    <steps>
      1. IF caller provides a value in {construction, extraction, ontology_only, presentation, storage} → use it
      2. ELSE → null (perform classification in Phase 1)
    </steps>
  </field>
  <field name="target_constructor" source="Caller may specify a constructor directly">
    <steps>
      1. IF caller provides a constructor name → use it, set request_type_override = "construction"
      2. ELSE → null (perform semantic routing in Phase 1)
    </steps>
  </field>
  <field name="max_iterations" source="Caller or default">
    <validation>Integer >= 1. Default: 3.</validation>
  </field>
  <field name="output_format" source="Caller or default">
    <validation>One of: structured, markdown, graph. Default: markdown.</validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Request provided</name>
    <verification>input.request is non-empty string</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Knowledge skills exist</name>
    <verification>At least one .github/skills/x-ipe-knowledge-*/SKILL.md exists on disk</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 0 | 0.1 | 礼 — Greet | Announce identity | Greeting delivered |
| 1 | 1.1–1.6 | 格物 — Plan | Discover skills, classify request, framework, overview, rubric, plan | Plan complete |
| 2 | 2.1–2.6 | 致知 — Execute | Extract, fill, critique loop, ontology, store, present | Pipeline complete |
| 3 | 3.1 | 录 — Record | Write pipeline execution log | Log written |
| 4 | 4.1 | 示 — Present | Return pipeline_summary to caller | Output delivered |

BLOCKING: All phases execute in order. No phase may be skipped.
BLOCKING: Phase 1 (格物) adapts based on request_type — non-construction types skip framework/rubric steps.

---

## Execution Procedure

```xml
<procedure name="knowledge-librarian">
  <execute_dor_checks_before_starting/>

  <phase_0 name="礼 — Greet">
    <step_0_1>
      <name>Announce Identity</name>
      <action>
        1. Print: "道 · Knowledge Librarian — ready."
        2. Initialize pipeline_state with session_id = "librarian-{ISO-8601-timestamp}"
        3. Create session working directory: x-ipe-docs/memory/.working/{session_id}/
      </action>
      <output>Greeting printed, pipeline_state initialized</output>
    </step_0_1>
  </phase_0>

  <phase_1 name="格物 — Plan">

    <step_1_1>
      <name>Discover Skills</name>
      <action>
        1. GLOB: .github/skills/x-ipe-knowledge-*/SKILL.md
        2. FOR EACH SKILL.md found:
           a. READ YAML frontmatter → extract name, description
           b. CATEGORIZE by prefix:
              - x-ipe-knowledge-extractor-*   → extractors[]
              - x-ipe-knowledge-constructor-* → constructors[]
              - x-ipe-knowledge-keeper-*      → keepers[]
              - x-ipe-knowledge-present-*     → presenters[]
              - x-ipe-knowledge-ontology-*    → ontology[]
              - x-ipe-knowledge-mimic-*       → mimics[]
        3. BUILD discovered_skills registry
        4. IF discovered_skills is empty → pipeline_status = "failed", STOP
        5. Mark pipeline_state.discovery = "done"
      </action>
      <constraints>
        - No hardcoded skill names — registry built fresh each invocation
        - Only x-ipe-knowledge-* namespace scanned (not x-ipe-tool-*, x-ipe-task-based-*, etc.)
      </constraints>
      <output>discovered_skills registry with categorized skills</output>
    </step_1_1>

    <step_1_2>
      <name>Classify Request</name>
      <action>
        1. IF request_type_override provided → use it, skip classification
        2. IF target_constructor provided → type = "construction", skip routing
        3. ELSE analyze request text:
           a. Construction verbs (build, create, construct, write) + domain → "construction"
           b. Extraction verbs (extract, get, fetch, find) → "extraction"
           c. Ontology verbs (discover, link, synthesize, normalize) → "ontology_only"
           d. Presentation verbs (render, summarize, show, present) → "presentation"
           e. Storage verbs (store, save, promote, persist) → "storage"
           f. No match → "classification_failed"
        4. IF type = "construction" AND target_constructor is null:
           a. FOR EACH constructor in discovered_skills.constructors[]:
              Compare request against constructor description (semantic similarity)
           b. Select highest-scoring constructor
           c. On tie → alphabetical first, log tie-breaking
           d. On zero matches → "classification_failed"
        5. Mark pipeline_state.classification = "done"
      </action>
      <output>request_type + selected_constructor (if applicable)</output>
    </step_1_2>

    <step_1_3>
      <name>Provide Framework</name>
      <action>
        1. IF request_type != "construction" → SKIP (mark "skipped")
        2. INVOKE selected_constructor's `provide_framework` operation with request context
        3. RECEIVE framework_document
        4. SAVE to .working/{session_id}/framework/
        5. Mark pipeline_state.格物_1_framework = "done"
      </action>
      <output>framework_document (or skipped)</output>
    </step_1_3>

    <step_1_4>
      <name>Gather Overview</name>
      <action>
        1. IF request_type != "construction" → SKIP
        2. SELECT appropriate extractor (extractor-web for URLs, extractor-memory for existing knowledge)
        3. INVOKE extractor to gather high-level overview of the target
        4. SAVE to .working/{session_id}/overview/
        5. Mark pipeline_state.格物_2_overview = "done"
      </action>
      <output>overview_content (or skipped)</output>
    </step_1_4>

    <step_1_5>
      <name>Design Rubric</name>
      <action>
        1. IF request_type != "construction" → SKIP
        2. INVOKE selected_constructor's `design_rubric` with framework + overview
        3. RECEIVE rubric_metrics[]
        4. SAVE to .working/{session_id}/rubric/
        5. Mark pipeline_state.格物_3_rubric = "done"
      </action>
      <output>rubric_metrics[] (or skipped)</output>
    </step_1_5>

    <step_1_6>
      <name>Plan Knowledge Requests</name>
      <action>
        1. IF request_type != "construction" → SKIP
        2. INVOKE selected_constructor's `request_knowledge` with framework + rubric
        3. RECEIVE knowledge_requests[] specifying what, for which section, which extractor
        4. SAVE to .working/{session_id}/plan/
        5. Mark pipeline_state.格物_4_plan = "done"
      </action>
      <output>knowledge_requests[] (or skipped)</output>
    </step_1_6>

  </phase_1>

  <phase_2 name="致知 — Execute">

    <step_2_1>
      <name>Execute Extraction</name>
      <action>
        1. IF request_type = "construction":
           FOR EACH request in knowledge_requests[]:
             INVOKE appropriate extractor (extractor-web for URLs, extractor-memory for existing)
             COLLECT gathered_knowledge[]
        2. IF request_type = "extraction":
           INVOKE appropriate extractor directly with request content
           COLLECT gathered_knowledge[]
        3. IF request_type in {ontology_only, presentation, storage}:
           SKIP extraction (mark "skipped")
        4. Mark pipeline_state.致知_1_execute = "done"
      </action>
      <output>gathered_knowledge[] (or skipped)</output>
    </step_2_1>

    <step_2_2>
      <name>Fill Structure</name>
      <action>
        1. IF request_type != "construction" → SKIP
        2. INVOKE selected_constructor's `fill_structure` with framework + gathered_knowledge
        3. RECEIVE completed_draft (incomplete sections marked [INCOMPLETE: reason])
        4. SAVE to .working/{session_id}/draft/
        5. Mark pipeline_state.致知_2_fill = "done"
      </action>
      <output>completed_draft (or skipped)</output>
    </step_2_2>

    <step_2_3>
      <name>Critique Against Rubric</name>
      <action>
        1. IF request_type != "construction" → SKIP
        2. SET iteration_count = 0
        3. LOOP:
           a. INVOKE critique sub-agent (premium model) with (draft, rubric_metrics)
           b. RECEIVE critique_result: { verdict: pass|fail, gaps[], scores{} }
           c. IF verdict == "pass" → EXIT loop
           d. IF iteration_count >= max_iterations → mark "partial_quality", log gaps, EXIT loop
           e. iteration_count++
           f. INVOKE constructor's `request_knowledge` for gap sections only (replan)
           g. INVOKE extractors for new knowledge requests
           h. INVOKE constructor's `fill_structure` for gap sections
           i. CONTINUE loop
        4. Mark pipeline_state.致知_3_critique = "done"
      </action>
      <constraints>
        - Critique sub-agent MUST use premium model
        - max_iterations prevents infinite loops (default: 3)
      </constraints>
      <output>critique_result + iteration_count</output>
    </step_2_3>

    <step_2_4>
      <name>Process Ontology</name>
      <action>
        1. IF request_type = "ontology_only":
           INVOKE ontology-synthesizer pipeline: discover_related → wash_terms → link_nodes
        2. ELIF request_type = "construction" OR request_type = "extraction":
           a. INVOKE ontology-builder's `build_ontology` on the draft/extracted content
           b. INVOKE ontology-synthesizer pipeline on new entities
        3. ELSE → SKIP
        4. COLLECT ontology_result
        5. Mark pipeline_state.致知_4_ontology = "done"
      </action>
      <output>ontology_result (or skipped)</output>
    </step_2_4>

    <step_2_5>
      <name>Store Results</name>
      <action>
        1. IF request_type = "storage":
           INVOKE keeper-memory's `store` with request content directly
        2. ELIF request_type = "construction":
           INVOKE keeper-memory's `store` with completed_draft
           Determine memory_type: procedural for manuals/patterns, semantic for facts, episodic for session notes
        3. ELIF request_type = "extraction":
           INVOKE keeper-memory's `store` with gathered_knowledge
        4. ELSE → SKIP
        5. COLLECT stored_path
        6. Mark pipeline_state.致知_5_store = "done"
      </action>
      <output>stored_path (or skipped)</output>
    </step_2_5>

    <step_2_6>
      <name>Present Output</name>
      <action>
        1. IF request_type = "presentation" OR output_format != null:
           INVOKE present-to-user's `render` with appropriate content + output_format
        2. IF output_format = "graph" OR caller requests visualization:
           INVOKE present-to-knowledge-graph's `connect` to push ontology to frontend
        3. COLLECT presented_output
        4. Mark pipeline_state.致知_6_present = "done"
      </action>
      <output>presented_output (or skipped)</output>
    </step_2_6>

  </phase_2>

  <phase_3 name="录 — Record">
    <step_3_1>
      <name>Write Pipeline Log</name>
      <action>
        1. COMPUTE pipeline_status from pipeline_state:
           - ALL steps "done" or "skipped" → "success"
           - ANY step "failed" → "partial"
           - Phase 1 failed → "failed"
        2. LOG pipeline execution summary to session working directory
        3. DO NOT write to x-ipe-docs/dao/ — this is an orchestrator log, not a DAO decision log
      </action>
      <output>Pipeline log written</output>
    </step_3_1>
  </phase_3>

  <phase_4 name="示 — Present">
    <step_4_1>
      <name>Return Pipeline Summary</name>
      <action>
        1. ASSEMBLE pipeline_output:
           - pipeline_status: success | partial | failed
           - pipeline_summary: human-readable description of what was done
           - completed_steps[]: list of step names and their status
           - stored_path: path to stored artifact (if applicable)
           - ontology_result: ontology processing results (if applicable)
           - presented_output: rendered content (if applicable)
        2. RETURN pipeline_output to caller
      </action>
      <output>pipeline_output returned</output>
    </step_4_1>
  </phase_4>

</procedure>
```

---

## Output Result

```yaml
pipeline_output:
  pipeline_status: "success | partial | failed"
  pipeline_summary: "Human-readable pipeline execution summary"
  completed_steps:
    - { name: "discovery", status: "done" }
    - { name: "classification", status: "done" }
    - { name: "格物_1_framework", status: "done | skipped" }
    - { name: "格物_2_overview", status: "done | skipped" }
    - { name: "格物_3_rubric", status: "done | skipped" }
    - { name: "格物_4_plan", status: "done | skipped" }
    - { name: "致知_1_execute", status: "done | skipped | failed" }
    - { name: "致知_2_fill", status: "done | skipped | failed" }
    - { name: "致知_3_critique", status: "done | skipped | failed" }
    - { name: "致知_4_ontology", status: "done | skipped | failed" }
    - { name: "致知_5_store", status: "done | skipped | failed" }
    - { name: "致知_6_present", status: "done | skipped | failed" }
  stored_path: "x-ipe-docs/memory/{type}/{slug}.md"
  ontology_result: { entities_created: 0, relations_created: 0, terms_normalized: 0 }
  presented_output: { format: "markdown", content: "..." }
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Skills Discovered</name>
    <verification>discovered_skills registry is non-empty with categorized skills</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Request Classified</name>
    <verification>request_type resolved to one of: construction, extraction, ontology_only, presentation, storage (or classification_failed)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Pipeline Executed</name>
    <verification>All applicable steps executed (non-applicable steps marked "skipped")</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Pipeline Summary Returned</name>
    <verification>pipeline_output returned with pipeline_status, pipeline_summary, and completed_steps</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `DISCOVERY_EMPTY` | No x-ipe-knowledge-* skills found | Return pipeline_status: failed with error message listing expected skill location |
| `CLASSIFICATION_FAILED` | Request doesn't match any known type | Return available capabilities list; caller can retry with request_type_override |
| `CONSTRUCTOR_UNAVAILABLE` | Selected constructor skill missing or errored | Mark step as "failed", return partial result |
| `EXTRACTOR_TIMEOUT` | Extractor skill timed out | Log timeout, pass partial gathered_knowledge to next step |
| `CRITIQUE_UNAVAILABLE` | Critique sub-agent failed to respond | Skip critique loop, proceed with draft as-is, mark "partial_quality" |
| `STORE_FAILED` | keeper-memory store operation failed | Log error, continue to present step; caller still gets presented_output |

---

## References

| File | Purpose |
|------|---------|
| [references/examples.md](.github/skills/x-ipe-assistant-knowledge-librarian-DAO/references/examples.md) | Worked examples for construction, extraction, and ontology_only pipelines |
| [references/pipeline-state-format.md](.github/skills/x-ipe-assistant-knowledge-librarian-DAO/references/pipeline-state-format.md) | Pipeline state tracker schema documentation |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-assistant-knowledge-librarian-DAO/references/examples.md) for detailed execution examples.
