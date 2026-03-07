# Task-Based Skill Template

Use this template when creating a new task-based skill. Follow v2 guidelines format.

**Section Order (Cognitive Flow):**
1. CONTEXT: Purpose → Important Notes
2. DECISION: Input Parameters → Definition of Ready
3. ACTION: Execution Flow Summary (with Phase column) → Phase Definitions → Execution Procedure (phase hierarchy)
4. VERIFY: Output Result → Definition of Done
5. REFERENCE: Patterns & Anti-Patterns → Examples

---

```markdown
---
name: x-ipe-task-based-{skill-name}
description: {Brief description of what this task type does}. Use when {trigger conditions}. Triggers on requests like "{trigger 1}", "{trigger 2}".
---

# Task-Based Skill: {Skill Name}

## Purpose

{Brief description of what this task type accomplishes} by:
1. {Step 1}
2. {Step 2}
3. {Step 3}
4. {Step 4}

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "{task_based_skill}"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A

  # Task type attributes
  category: "{standalone | feature-stage | requirement-stage | ideation-stage}"
  next_task_based_skill: "{Next Task-Based Skill | null}"

  # Process preference (3-mode auto-proceed system)
  process_preference:
    auto_proceed: "manual | auto | stop_for_question"  # default: manual

  # Required inputs
  {input_1}: "{default_value}"
  {input_2}: "{default_value}"

  # Context (from previous task or project)
  {context_attr}: "{value_or_path}"
```

### Input Initialization

Describes how to resolve each input field value before execution begins. Acts as the skill's constructor — all resolution logic is centralized here instead of in execution steps.

BLOCKING: All input fields with non-trivial initialization MUST be documented here. Do NOT embed field initialization logic in execution procedure steps.

```xml
<input_init>
  <!-- Standard fields (auto-populated by workflow) -->
  <field name="task_id" source="task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="category" derive="Read from this skill's Output Result `category` field" />

  <!-- Skill-specific fields (document resolution per field) -->
  <field name="{input_1}">
    <steps>
      1. {If condition, use value from previous task output}
      2. {Fallback action}
    </steps>
  </field>

  <field name="{context_attr}" source="{previous task output or project config}" />
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>{Prerequisite 1}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>{Prerequisite 2}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>{Optional Prerequisite}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 1. 博学之 (Study Broadly) | 1.1 | {Step Name} | {Gather context, read specs} | {gate condition} |
| 2. 审问之 (Inquire Thoroughly) | — | SKIP | {skip reason} | — |
| 3. 慎思之 (Think Carefully) | 3.1 | {Step Name} | {Analyze trade-offs} | {gate condition} |
| 4. 明辨之 (Discern Clearly) | — | SKIP | {skip reason} | — |
| 5. 笃行之 (Practice Earnestly) | 5.1 | {Step Name} | {Execute core work} | {gate condition} |
| | 5.2 | Complete | Verify DoD | DoD validated |
| 6. 继续执行 | 6.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| 6. 继续执行 | 6.2 | Execute Next Action | Delegate to x-ipe-workflow-task-execution sub-agent | Sub-agent started |

BLOCKING: All 5 phases MUST appear in the table. Skipped phases use `—` for Step and Gate.
BLOCKING: {Additional rule that must not be skipped}

### Phase Definitions (5-Phase Learning Method — 博学之，审问之，慎思之，明辨之，笃行之)

| Phase | Chinese | English | SE Purpose | Typical Activities |
|-------|---------|---------|------------|-------------------|
| 1 | 博学之 (Bóxué) | Study Broadly | Gather comprehensive context | Read specs, study domain, research patterns, load context |
| 2 | 审问之 (Shěnwèn) | Inquire Thoroughly | Question assumptions, probe gaps | Ask clarifying questions, challenge inputs, validate constraints |
| 3 | 慎思之 (Shènsī) | Think Carefully | Reflect on trade-offs and risks | Analyze alternatives, assess risk, evaluate impact |
| 4 | 明辨之 (Míngbiàn) | Discern Clearly | Make informed decisions | Choose approach, document rationale, resolve conflicts |
| 5 | 笃行之 (Dǔxíng) | Practice Earnestly | Execute with discipline | Implement, test, verify, deliver, commit |
| 6 | 继续执行（Continue Execute） | Route and Execute | Decide next task, then load and execute | DAO-assisted decision + execution plan generation |

**Phase Rules:**
- Phase 1 (博学之) and Phase 5 (笃行之) are NEVER skippable.
- Phases 2, 3, 4 may use `<skip reason="..." />` when genuinely non-applicable.
- Phase names MUST always be bilingual (Chinese + English).
- Phase order is fixed: 1 → 2 → 3 → 4 → 5. No reordering.
- auto_proceed in Phase 2: agent self-resolves via `x-ipe-dao-end-user-representative` (not skipped).

**Common Skip Reasons:**

| Phase | Skip Reason |
|-------|-------------|
| 2 (审问之) | "Input is fully specified by upstream skill; no ambiguity to resolve" |
| 3 (慎思之) | "No design decisions or trade-offs; purely procedural execution" |
| 4 (明辨之) | "Single valid approach; no alternatives to evaluate" |

---

## Execution Procedure

```xml
<procedure name="{skill-name}">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">
    <step_1_1>
      <name>{Step Name}</name>
      <action>
        1. {Sub-action 1: gather context, read specs, research domain}
        2. {Sub-action 2}
        3. {Sub-action 3}
      </action>
      <constraints>
        - BLOCKING: {Must not violate}
        - CRITICAL: {Important consideration}
      </constraints>
      <output>{What this step produces}</output>
    </step_1_1>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <!-- Option A: Active inquiry -->
    <step_2_1>
      <name>{Step Name}</name>
      <action>
        1. {Question assumptions, probe gaps, challenge inputs}
        2. IF process_preference.auto_proceed == "auto":
             Invoke x-ipe-dao-end-user-representative to self-resolve
           ELSE:
             Ask human for clarification
      </action>
      <output>{Clarified requirements / resolved ambiguities}</output>
    </step_2_1>
    <!-- Option B: Skip (uncomment if phase not applicable) -->
    <!-- <skip reason="Input is fully specified by upstream skill; no ambiguity to resolve" /> -->
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <!-- Option A: Active reflection -->
    <step_3_1>
      <name>{Step Name}</name>
      <action>
        1. {Analyze trade-offs, evaluate risks, reflect on approaches}
      </action>
      <output>{Analysis results / risk assessment}</output>
    </step_3_1>
    <!-- Option B: Skip (uncomment if phase not applicable) -->
    <!-- <skip reason="No design decisions or trade-offs; purely procedural execution" /> -->
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <!-- Option A: Active discernment -->
    <step_4_1>
      <name>{Step Name}</name>
      <action>
        1. {Choose approach, document decision rationale}
      </action>
      <output>{Decision with rationale}</output>
    </step_4_1>
    <!-- Option B: Skip (uncomment if phase not applicable) -->
    <!-- <skip reason="Single valid approach; no alternatives to evaluate" /> -->
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <step_5_1>
      <name>{Step Name}</name>
      <action>
        1. {Execute the core work: create, implement, test}
      </action>
      <success_criteria>
        - {Criterion 1}
        - {Criterion 2}
      </success_criteria>
      <output>{Deliverable produced}</output>
    </step_5_1>

    <!-- MODE-AWARE COMPLETION (always last step in Phase 5): -->
    <step_5_N_complete>
      <name>Complete</name>
      <action>
        1. Verify all DoD checkpoints
        2. Output task completion summary
        3. Mode-aware review gate:
           IF process_preference.auto_proceed == "auto":
             Skip human review. If any open questions remain, invoke
             x-ipe-dao-end-user-representative to resolve them autonomously.
           ELIF process_preference.auto_proceed == "stop_for_question" OR "manual":
             Present results to human and wait for approval.
      </action>
      <output>Task completion output</output>
    </step_5_N_complete>
  </phase_5>

  <!-- CONTINUE EXECUTE (always last phase — handles next task transition): -->
  <phase_6 name="继续执行（Continue Execute）">
    <step_6_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.auto_proceed == "auto":
          → Invoke x-ipe-dao-end-user-representative with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the context and full output to decide best next action."
          → DAO studies the complete context and decides the best next action
        ELSE (manual):
          → Present next task suggestion to human and wait for instruction
      </action>
      <constraints>
        - BLOCKING (manual): Human MUST confirm or redirect before proceeding
        - BLOCKING (auto): Proceed after DoD verification; auto-select next task via DAO
      </constraints>
      <output>Next action decided with execution context</output>
    </step_6_1>
    <step_6_2>
      <name>Execute Next Action</name>
      <action>
        Based on the decision from Step 6.1, delegate execution to a sub-agent:
        1. Invoke x-ipe-workflow-task-execution as a sub-agent (use premium model)
        2. Pass the decided next task and full context from Step 6.1
        3. The workflow skill handles: skill loading, execution plan generation, and execution
      </action>
      <constraints>
        - MUST delegate to x-ipe-workflow-task-execution — do not execute the next skill directly
        - Sub-agent MUST use premium model (Best-Model Requirement)
      </constraints>
      <output>Sub-agent started with x-ipe-workflow-task-execution</output>
    </step_6_2>
  </phase_6>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "{standalone | feature-stage | requirement-stage | ideation-stage}"
  status: completed | blocked
  next_task_based_skill: "{Next Task-Based Skill}"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "{output_file_path_1}"
    - "{output_file_path_2}"
  # Dynamic attributes
  {dynamic_attr_1}: "{value}"
  {dynamic_attr_2}: "{value}"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>{Output 1 Created}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>{Verification 1 Passed}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>{Optional Checkpoint}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: {Pattern Name}

**When:** {Condition}
**Then:**
```
1. {Action 1}
2. {Action 2}
3. {Action 3}
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| {Anti-pattern 1} | {Reason} | {Better approach} |
| {Anti-pattern 2} | {Reason} | {Better approach} |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.
```

---

## Template Usage Notes

### Line Limit

CRITICAL: SKILL.md body MUST stay under 500 lines.

**Keep in SKILL.md:**
- Purpose, Input Parameters, DoR, DoD (core structure)
- Execution Flow (overview table with Phase column)
- Execution Procedure (phase-based hierarchy, essential steps only)

**Move to references/:**
- `references/examples.md` - Detailed execution examples (MANDATORY)
- `references/detailed-procedures.md` - Complex step-by-step guides

### Section Order (v2 Cognitive Flow)

MANDATORY: Sections must appear in this sequence:

```yaml
task_based_skill_skills:
  section_order:
    # CONTEXT
    1: Purpose
    2: Important Notes
    # DECISION
    3: Input Parameters
    3a: "  └─ Input Initialization (### subsection)"
    4: Definition of Ready (DoR)
    # ACTION
    5: Execution Flow Summary (with Phase column)
    5a: "  └─ Phase Definitions (### subsection)"
    6: Execution Procedure (phase_N → step_N_M hierarchy)
    # VERIFY
    7: Output Result
    8: Definition of Done (DoD)
    # REFERENCE
    9: Patterns & Anti-Patterns
    10: Examples
```

### Format Standards

| Element | Format | Example |
|---------|--------|---------|
| Importance signals | Keywords | `BLOCKING:`, `CRITICAL:`, `MANDATORY:` |
| DoR/DoD | XML checkpoints | `<definition_of_ready>` |
| Execution procedure | XML procedure with phases | `<phase_1 name="博学之 — Study Broadly">` |
| Steps within phases | XML step with phase prefix | `<step_1_1>`, `<step_2_1>`, `<step_5_N_complete>` |
| Skipped phases | XML skip element | `<skip reason="..." />` |
| Data models | YAML | `input:`, `output:` |
| Variables | Braces | `{skill_name}`, `{task_id}` |

### Category Values

| Category | Description | Board Skill |
|----------|-------------|-------------|
| standalone | No board tracking | None |
| feature-stage | Updates feature board | feature-board-management |
| requirement-stage | Updates requirement board | requirement-board-management |
| ideation-stage | Updates ideation board | ideation-board-management |
