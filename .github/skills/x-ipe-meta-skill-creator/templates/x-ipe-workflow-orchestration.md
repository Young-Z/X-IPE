# Workflow Orchestration Skill Template

Use this template when creating a skill that orchestrates multiple other skills in a coordinated workflow. Workflow orchestration skills manage the execution order, data flow, and decision points across multiple skills. Task-category skills share this procedure/registry/output scaffold; substitute the canonical `x-ipe+{category}+{name}` identity and category-completion inputs. They do not own board CRUD.

**Section Order (Cognitive Flow):**
1. CONTEXT: Purpose → Important Notes → About
2. DECISION: Input Parameters → Definition of Ready
3. ACTION: Execution Flow Summary → Execution Procedure
4. VERIFY: Output Result → Definition of Done
5. REFERENCE: Registry (Skill Mapping) → Error Handling → Examples

---

```markdown
---
name: x-ipe-workflow-{name}
description: Orchestrates {description of workflow}. Use when {trigger conditions}. Coordinates skills: {skill-1}, {skill-2}, {skill-3}. Triggers on requests like "{trigger 1}", "{trigger 2}".
---

# {Workflow Name}

## Purpose

Orchestrate a multi-skill workflow by:
1. **Coordinate** - {Brief description of coordination}
2. **Sequence** - {Brief description of sequencing logic}
3. **Aggregate** - {Brief description of result aggregation}
4. **Handle Failures** - {Brief description of error handling}

---

## Important Notes

Default to one model/context open-ended loop; apply tool skills in the same loop.
Use [authoring policy](.github/skills/x-ipe-meta-skill-creator/references/single-loop-authoring.md)
for bounded delegation and risk-triggered independent review, not per-skill agents.
This policy also applies when this scaffold is used for task-category skills.

BLOCKING: All orchestrated skills must exist and be valid before execution.

CRITICAL: Workflow orchestration skills do NOT implement logic themselves - they coordinate existing skills.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills.

---

## About

Workflow orchestration manages skills sequentially in shared context by default.
Independent parallel work is an opt-in execution choice, not a mandatory agent topology.

**Key Concepts:**
- **Pipeline** - Sequential execution where output of one skill feeds the next
- **Parallel Group** - Skills that can execute concurrently
- **Decision Point** - Conditional branching based on skill output
- **Rollback** - Recovery actions when skills fail

---

## Input Parameters

```yaml
input:
  # Workflow trigger
  workflow_trigger: "{what initiates this workflow}"
  
  # Context passed to all skills
  shared_context:
    {context_field_1}: "{value}"
    {context_field_2}: "{value}"
  
  # Workflow options
  options:
    parallel_execution: false  # Opt in only for substantial independent work
    stop_on_first_failure: true | false
    max_retries: {number}
```

### Input Initialization

Describes how to resolve each input field value before execution begins. Acts as the skill's constructor — all resolution logic is centralized here instead of in execution steps.

BLOCKING: All input fields with non-trivial initialization MUST be documented here. Do NOT embed field initialization logic in execution procedure steps.

```xml
<input_init>
  <field name="workflow_trigger" source="{where the trigger comes from}" />

  <field name="shared_context.{context_field_1}">
    <steps>
      1. {If condition, resolve value}
      2. {Fallback action}
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>All Skills Available</name>
    <verification>Each skill in registry exists at .github/skills/{skill-name}/SKILL.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Input Context Complete</name>
    <verification>All required context fields are populated</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Prerequisites Met</name>
    <verification>Any workflow-level prerequisites are satisfied</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Skills | Mode | Gate |
|-------|--------|------|------|
| 1 | {skill-1} | Sequential | {skill-1} complete |
| 2 | {skill-2}, {skill-3} | Sequential by default | Both complete |
| 3 | {skill-4} | Sequential | Decision: {condition} |
| 4 | {skill-5} OR {skill-6} | Conditional | Based on Phase 3 decision |

BLOCKING: Opt-in parallel work must have no data dependencies or shared writes.

---

## Execution Procedure

```xml
<procedure name="{workflow-name}">
  <!-- Check readiness in the same loop. -->
  <execute_dor_checks_before_starting/>

  <phase_1>
    <name>{Phase Name}</name>
    <skills>
      <skill name="{skill-1}">
        <input_mapping>
          - shared_context.{field} → skill_input.{field}
        </input_mapping>
        <output_capture>
          - skill_output.{field} → workflow_state.{field}
        </output_capture>
      </skill>
    </skills>
    <gate>workflow_state.{field} is valid</gate>
  </phase_1>

  <phase_2>
    <name>{Phase Name}</name>
    <mode>sequential</mode>
    <skills>
      <skill name="{skill-2}">
        <input_mapping>
          - workflow_state.{field} → skill_input.{field}
        </input_mapping>
      </skill>
      <skill name="{skill-3}">
        <input_mapping>
          - workflow_state.{field} → skill_input.{field}
        </input_mapping>
      </skill>
    </skills>
    <merge_strategy>
      - Aggregate results into workflow_state.{merged_field}
    </merge_strategy>
    <gate>Both skills complete</gate>
  </phase_2>

  <phase_3>
    <name>{Decision Phase}</name>
    <decision>
      IF: workflow_state.{condition_field} == {value_a}
      THEN: Execute {skill-5}
      ELSE: Execute {skill-6}
    </decision>
  </phase_3>

</procedure>
```

---

## Output Result

```yaml
workflow_output:
  status: completed | partial | failed
  phases_completed: {number}
  total_phases: {number}
  results:
    phase_1: {result_summary}
    phase_2: {result_summary}
    phase_3: {result_summary}
  failed_skills: []  # If any
  rollback_executed: true | false
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>All Required Phases Complete</name>
    <verification>Each mandatory phase executed successfully</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output Aggregated</name>
    <verification>Final workflow output contains all expected data</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No Failed Skills</name>
    <verification>failed_skills array is empty OR failures handled by rollback</verification>
  </checkpoint>
</definition_of_done>
```

---

## Skill Registry

MANDATORY: List all skills this workflow orchestrates with their role. Load the
registry before the DoR availability check even though it is a reference section.

| Skill | Role in Workflow | Required Input | Produced Output |
|-------|------------------|----------------|-----------------|
| `{skill-1}` | {Role description} | {input fields} | {output fields} |
| `{skill-2}` | {Role description} | {input fields} | {output fields} |
| `{skill-3}` | {Role description} | {input fields} | {output fields} |
| `{skill-4}` | {Role description} | {input fields} | {output fields} |

### Data Flow Diagram

```yaml
data_flow:
  phase_1:
    input: shared_context
    skill: {skill-1}
    output: result_1
  phase_2:
    input: result_1
    skills: [{skill-2}, {skill-3}]
    output: [result_2a, result_2b]
    merge: merged_result
  phase_3:
    input: merged_result
    decision: condition_check
    branch_a: {skill-5} → final_result_a
    branch_b: {skill-6} → final_result_b
```

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| `SKILL_NOT_FOUND` | Referenced skill doesn't exist | Fail workflow, report missing skill |
| `SKILL_EXECUTION_FAILED` | Skill returned error | Retry (if max_retries > 0), then rollback |
| `DATA_MAPPING_ERROR` | Input/output field mismatch | Fail workflow, report mapping issue |
| `PARALLEL_DEADLOCK` | Circular dependency detected | Fail workflow, report dependency cycle |

### Rollback Strategy

```yaml
rollback:
  trigger: Any skill failure when stop_on_first_failure == true
  actions:
    - step: 1
      action: "Log failure details"
    - step: 2  
      action: "Execute compensating actions for completed skills (if defined)"
    - step: 3
      action: "Restore workflow_state to pre-execution snapshot"
    - step: 4
      action: "Report final status with rollback flag"
```

---

## Examples

See [references/examples.md](references/examples.md) for workflow orchestration examples.
```

---

## Template Usage Notes

### Naming Convention

Workflow orchestration uses `x-ipe-workflow-{name}` (for example,
`x-ipe-workflow-full-pipeline`). Category orchestration uses
`x-ipe+{category}+{name}` (for example, `x-ipe+feature-stage+release`).
Use the task-category metadata template for category completion gates and child
outputs. Board persistence belongs to `x-ipe-tool-task-board-manager`; do not
instantiate a Markdown board or reinterpret category completion as CRUD.

### Section Order (v2 Cognitive Flow)

MANDATORY: Sections must appear in this sequence:

```yaml
workflow_orchestration_skills:
  section_order:
    # CONTEXT
    1: Purpose
    2: Important Notes
    3: About (Domain Concepts)
    # DECISION
    4: Input Parameters
    4a: "  └─ Input Initialization (### subsection)"
    5: Definition of Ready (DoR)
    # ACTION
    6: Execution Flow Summary (same-loop sequence by default)
    7: Execution Procedure (Steps)
    # VERIFY
    8: Output Result
    9: Definition of Done (DoD)
    # REFERENCE
    10: Skill Registry
    11: Error Handling
    12: Examples
```

### Format Standards

| Element | Format |
|---------|--------|
| Execution procedure | XML `<procedure>` with `<phase_N>` blocks |
| Skill registry | Markdown table |
| Data flow | YAML diagram |
| Decision points | IF/THEN/ELSE in XML |
| DoR/DoD | XML checkpoints |
| Importance signals | Keywords (BLOCKING, CRITICAL, MANDATORY) |

### Key Differences from Task-Based Skills

| Aspect | Task-Based | Workflow Orchestration |
|--------|-----------|------------------------|
| Implements logic | Yes | No - coordinates other skills |
| Produces artifacts | Directly | Aggregates from coordinated skills |
| Execution unit | Single skill | Multiple skills in phases |
| Error handling | Self-contained | Rollback across skills |
