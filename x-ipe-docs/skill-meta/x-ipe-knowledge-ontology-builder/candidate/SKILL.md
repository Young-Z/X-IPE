---
name: x-ipe-knowledge-ontology-builder
description: Builds ontology graph (classes, instances, vocabulary) from source content through an iterative discover-critique-implement loop. Delegates JSONL I/O to scripts/ontology_ops.py. Triggers on operations like "build_ontology".
---

# Ontology Builder — Knowledge Skill

## Purpose

AI Agents follow this skill to build and refine ontology graphs from source knowledge:
1. Learn source content and produce an overview
2. Suggest a basic ontology graph (classes, instances, vocabulary)
3. Critique against existing ontology for reuse opportunities
4. Implement changes based on constructive feedback
5. Drill down into nodes for deeper discovery, then iterate

---

## Important Notes

BLOCKING: This is a single-operation skill. The `build_ontology` operation runs an iterative loop internally — the orchestrator does NOT need to call separate discover/create/validate steps.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.
CRITICAL: This skill writes DIRECTLY to `.ontology/` (not `.working/ontology/`). Ontology data is the persistent structure — there is no staging area.
CRITICAL: Every class meta and instance record MUST include `synthesize_id: null` and `synthesize_message: null` on creation. These fields are populated later by the ontology-synthesizer (FEATURE-059-D).

---

## About

This skill serves as the ontology construction gateway. Given source knowledge files, it autonomously discovers domain structure (classes, properties, instances, vocabulary) and registers the results in `.ontology/`. It absorbs build capabilities from the retired `x-ipe-tool-ontology`.

**Key Concepts:**
- **Iterative Discovery** — The builder doesn't try to discover everything in one pass. It starts with a broad overview, then drills down node-by-node, refining the graph at each iteration.
- **Critique-Driven** — A sub-agent evaluates each proposed graph change against existing ontology, suggesting reuse opportunities and catching inconsistencies before writes happen.
- **Rubric Evaluation (auto mode)** — When `depth_limit` is `"auto"`, the builder defines coverage metrics and loops until 100% is achieved (with a safety cap at depth 10).
- **writes_to Discipline** — All writes go to `.ontology/` sub-paths. The builder declares this in its contract so the orchestrator can predict side effects.
- **Lifecycle Flag** — Instances referencing `.working/` content are `Ephemeral`; those referencing persistent memory are `Persistent`.
- **JSONL Event Sourcing** — All schema and instance data uses append-only JSONL with `{op, type, id, ts, props}` envelope.

---

## When to Use

```yaml
triggers:
  - "Build ontology graph from source content"
  - "Discover classes, instances, and vocabulary from knowledge files"
  - "Update ontology with new knowledge content"

not_for:
  - "Relationship/edge creation between entities (use ontology-synthesizer in 059-D)"
  - "Memory file CRUD (use x-ipe-knowledge-keeper-memory)"
  - "Searching/reading ontology (use x-ipe-tool-ontology search ops)"
  - "Orchestration decisions (belong to assistant skills)"
```

---

## Input Parameters

```yaml
input:
  operation: "build_ontology"
  context:
    source_content: "string[]"          # Paths to memory files to analyze
    depth_limit: "1 | 3 | auto"        # 1=flat, 3=standard, auto=rubric-driven (default: "auto")
```

### Input Initialization

BLOCKING: All input fields with non-trivial initialization MUST be documented here.

```xml
<input_init>
  <field name="operation" source="Assistant orchestrator">
    <validation>Must be "build_ontology"</validation>
  </field>
  <field name="context.source_content" source="Orchestrator provides paths to memory files">
    <validation>Non-empty string array; each path must exist</validation>
  </field>
  <field name="context.depth_limit" source="Orchestrator or default" default="auto">
    <validation>Must be one of: 1, 3, "auto". When "auto", builder loops with rubric evaluation until 100% coverage metrics achieved.</validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Source content provided</name>
    <verification>source_content is non-empty string array with existing paths</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Ontology directory accessible</name>
    <verification>x-ipe-docs/memory/.ontology/ exists or can be created</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: build_ontology

> **Contract:**
> - **Input:** source_content: string[], depth_limit: 1 | 3 | "auto" (default: "auto")
> - **Output:** build_report: dict {ontology_summary, rubric_scores, iterations_completed}, writes_to: string
> - **Writes To:** x-ipe-docs/memory/.ontology/ (schema/, instances/, vocabulary/)
> - **Delegates To:** `scripts/ontology_ops.py` (register_class, add_properties, create_instance, add_vocabulary, validate_terms)
> - **Constraints:** Iterative loop; critique before every write; lifecycle flags; auto mode targets 100% rubric metrics

**When:** Orchestrator needs to build or extend the ontology graph from source knowledge.

```xml
<operation name="build_ontology">

  <phase_1 name="博学之 — Study Broadly (Step 1: Learn Content)">
    <action>
      1. READ all source_content paths — load each memory file
      2. BUILD content overview:
         - Key domain concepts and entities mentioned
         - Relationships hinted at (hierarchies, associations)
         - Approximate complexity (number of distinct concepts)
      3. LOAD existing .ontology/ state:
         - Read class-registry.jsonl for existing classes
         - Read instance chunks for existing instances
         - Read vocabulary/ for existing schemes and terms
      4. RESOLVE depth_limit (default: "auto")
    </action>
    <output>Content overview + existing ontology state loaded</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly (Step 2: Suggest Basic Ontology Graph)">
    <action>
      1. VALIDATE source_content is non-empty, all paths exist
      2. VALIDATE depth_limit is one of: 1, 3, "auto"
      3. PROPOSE initial ontology graph from the overview:
         a. **Classes** — Top-level domain concepts as class candidates
            - Each with: label, description, parent (if hierarchical), source_files[]
         b. **Instances** — Concrete entities mentioned in source content
            - Each with: label, class assignment, key properties, source_files[]
         c. **Vocabulary** — Controlled terms that appear repeatedly
            - Each with: label, scheme, broader/narrower if obvious
      4. OUTPUT proposed_graph: {classes[], instances[], vocabulary[]}
    </action>
    <constraints>
      - BLOCKING: Empty source_content → return error INPUT_VALIDATION_FAILED
      - BLOCKING: Invalid depth_limit → return error INPUT_VALIDATION_FAILED
      - Propose, do NOT write yet — critique comes first
    </constraints>
    <output>Proposed ontology graph ready for critique</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully (Steps 3–6: Iterative Critique–Implement Loop)">
    <action>
      IF depth_limit is "auto":
        DEFINE rubric metrics:
          - concept_coverage: % of distinct domain concepts in source that have a class
          - instance_coverage: % of concrete entities in source that have an instance
          - vocabulary_coverage: % of repeated controlled terms registered in vocabulary
          - hierarchy_coherence: % of classes with correct parent assignment
          Target: ALL metrics = 100%

      SET iteration = 0
      SET unprocessed_nodes = [all nodes in proposed_graph]

      LOOP:
        --- Step 3: Critique ---
        a. LAUNCH sub-agent to evaluate proposed changes:
           - Can any existing class/instance/vocabulary be REUSED instead of creating new?
           - Are there CONFLICTS with existing ontology entries?
           - Is the proposed hierarchy COHERENT?
           - Constructive feedback: {reuse: [], modify: [], create_new: [], skip: []}
        b. INCORPORATE feedback — adjust proposed changes

        --- Step 4: Implement ---
        c. For each item in create_new + modify:
           - Classes: `python3 scripts/ontology_ops.py register_class --label "{label}" --description "{desc}" --source-files '{json}' --parent "{parent_id}" --ontology-dir x-ipe-docs/memory/.ontology`
           - Properties: `python3 scripts/ontology_ops.py add_properties --class-id "{id}" --properties '{json}' --ontology-dir x-ipe-docs/memory/.ontology`
           - Instances: `python3 scripts/ontology_ops.py create_instance --class "{class_id}" --label "{label}" --source-files '{json}' --properties '{json}' --ontology-dir x-ipe-docs/memory/.ontology`
             (lifecycle determined automatically: Ephemeral if .working/ in source_files, else Persistent)
           - Vocabulary: `python3 scripts/ontology_ops.py add_vocabulary --scheme "{scheme}" --label "{label}" --broader "{b}" --narrower '{json}' --ontology-dir x-ipe-docs/memory/.ontology`
        d. Validate writes via `python3 scripts/ontology_ops.py validate_terms` for term consistency

        --- Depth Check ---
        IF depth_limit is 1 → BREAK (flat mode, single pass)
        IF depth_limit is 3 AND iteration >= 3 → BREAK
        IF depth_limit is "auto":
           EVALUATE rubric metrics
           IF all metrics == 100% → BREAK (goal achieved)
           IF iteration >= 10 → BREAK (safety cap)

        --- Step 5: Drill Down — Select Next Node ---
        e. From unprocessed_nodes, SELECT the node with richest unexplored source content
        f. REMOVE selected node from unprocessed_nodes

        --- Step 6: Learn Details ---
        g. READ source_files linked to the selected node in depth
        h. DISCOVER finer-grained classes, properties, instances from the detailed content
        i. ADD new discoveries to proposed_graph
        j. iteration += 1
        k. GOTO Step 3

    </action>
    <output>Ontology graph built through iterative refinement</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly (Final Validation)">
    <action>
      1. VERIFY all registered classes exist in class-registry.jsonl
      2. VERIFY all instances have required fields (label, class, source_files, lifecycle)
      3. VERIFY synthesize_id and synthesize_message are null on all new records
      4. VERIFY vocabulary terms are deduplicated and hierarchy is bidirectional
      5. IF depth_limit == "auto": COMPILE final rubric scores
      6. IF any verification fails → log warnings but do not rollback
    </action>
    <output>Final validation complete</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly (Output Results)">
    <action>
      1. COMPILE build_report:
         - ontology_summary: {classes_created, instances_created, vocabulary_terms_added, classes_reused}
         - rubric_scores: {concept_coverage, instance_coverage, vocabulary_coverage, hierarchy_coherence} (if auto)
         - iterations_completed: int
         - depth_reached: int
      2. RETURN operation_output
    </action>
    <output>build_ontology complete</output>
  </phase_5>

</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "build_ontology"
  result:
    build_report:
      ontology_summary:
        classes_created: "int"
        instances_created: "int"
        vocabulary_terms_added: "int"
        classes_reused: "int"
      rubric_scores:                    # Present when depth_limit == "auto"
        concept_coverage: "float (0-1)"
        instance_coverage: "float (0-1)"
        vocabulary_coverage: "float (0-1)"
        hierarchy_coherence: "float (0-1)"
      iterations_completed: "int"
      depth_reached: "int"
    writes_to: "x-ipe-docs/memory/.ontology/"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Build completed successfully</name>
    <verification>operation_output.success == true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Classes registered in schema</name>
    <verification>New classes exist in .ontology/schema/class-registry.jsonl</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Instances created with lifecycle flags</name>
    <verification>Instances with .working/ sources have Ephemeral; others have Persistent</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Synthesize fields initialized</name>
    <verification>All new records have synthesize_id: null and synthesize_message: null</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Critique sub-agent was invoked</name>
    <verification>Build report shows at least 1 critique iteration ran</verification>
  </checkpoint>
  <checkpoint required="if_applicable">
    <name>Rubric metrics at 100% (auto mode)</name>
    <verification>If depth_limit == "auto", all rubric scores == 1.0 (or safety cap reached with explanation)</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INPUT_VALIDATION_FAILED` | Missing/invalid source_content or depth_limit | Return error with field details |
| `SOURCE_NOT_FOUND` | A source_content path does not exist | Skip missing file, log warning, continue |
| `ONTOLOGY_DIR_ERROR` | Cannot create/write to .ontology/ | Return error with path details |
| `CRITIQUE_TIMEOUT` | Sub-agent critique took too long | Accept current state, log warning, continue |
| `SAFETY_CAP_REACHED` | Auto mode hit iteration 10 without 100% | Return success with partial rubric scores |

---

## Patterns & Anti-Patterns

| Pattern | When | Key Actions |
|---------|------|-------------|
| Auto-discover | New domain, unknown depth | Use depth_limit="auto", let rubric drive iteration |
| Flat scan | Quick overview needed | Use depth_limit=1 for single-pass class discovery |
| Standard depth | Known moderate domain | Use depth_limit=3 for balanced coverage |
| Critique loop | Quality gate | Sub-agent critique runs every iteration before writes |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip critique | Inconsistent ontology, missed reuse | Critique runs every iteration — never bypass |
| Manual ID assignment | ID collision risk | Let ontology_ops.py generate IDs automatically |
| Separate operation calls | Orchestrator complexity | Use single build_ontology — it handles all steps internally |
| Ignore reuse suggestions | Duplicate classes/terms | Always incorporate critique feedback before writing |

---

## Examples

See `references/examples.md` for worked examples of the build_ontology operation.
