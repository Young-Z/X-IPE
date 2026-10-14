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

Load [common lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md)
and [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md).
Reuse supplied task/readiness; direct entry calls Orient/Plan once and returns
here without recursively dispatching this child. One lifecycle owner handles
registration/status, Git, app/feature persistence and successor boundary. Agree
one writer for any declared domain action; no duplicate child/owner writes.
This child returns full original output, not automatic next-task execution.

For new/changed scope, map source/parent/stakeholder → goal/subgoal → stable
story/leaf Given/When/Then AC/type → planned then actual revision-bound checks
in existing artifacts. Define contribution, constraints, all-required children
versus selected bounded alternatives, and concrete qualitative or justified
measured success. Preserve IDs/assertions/types; legacy explicit so-that inference
is labeled with source. Missing intent blocks only the pertinent claim. Separate
engineering delivery from observed stakeholder outcome; unobserved is not measured.
No new board/output/action fields, mandatory graph or invented stakeholder approval.

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
    interaction_mode: "interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill"  # default: interact-with-human

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
  <field name="task_id" source="existing task supplied by x-ipe-workflow-task-execution; do not create a duplicate" />
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
| Return | — | Owner handoff | Full output/evidence and conditional next suggestions | Owner verifies and decides boundary once |

Use this phase scaffold when it clarifies the domain workflow; a short task may combine learning activities into flat steps. Preserve its input/output and lifecycle contracts. Skipped phases use `—` for Step and Gate when retaining the scaffold.
BLOCKING: {Additional rule that must not be skipped}

### Phase Definitions (5-Phase Learning Method — 博学之，审问之，慎思之，明辨之，笃行之)

| Phase | Chinese | English | SE Purpose | Typical Activities |
|-------|---------|---------|------------|-------------------|
| 1 | 博学之 (Bóxué) | Study Broadly | Gather comprehensive context | Read specs, study domain, research patterns, load context |
| 2 | 审问之 (Shěnwèn) | Inquire Thoroughly | Question assumptions, probe gaps | Ask clarifying questions, challenge inputs, validate constraints |
| 3 | 慎思之 (Shènsī) | Think Carefully | Reflect on trade-offs and risks | Analyze alternatives, assess risk, evaluate impact |
| 4 | 明辨之 (Míngbiàn) | Discern Clearly | Make informed decisions | Choose approach, document rationale, resolve conflicts |
| 5 | 笃行之 (Dǔxíng) | Practice Earnestly | Execute with discipline | Implement, test, verify, deliver, commit |

**Phase Rules:**

- Context gathering and verification of execution remain required activities, not mandatory named phases.
- Inquiry, reflection, and discernment may be combined or omitted with a reason when non-applicable.
- When using this scaffold, retain bilingual names and its existing phase order.
- Resolve genuine questions through the caller's explicit current interaction policy; do not force a DAO call for clear inputs. Human asks human; full DAO and hybrid use bounded representative guidance within skill. Hybrid retains human completion/route confirmation; full DAO selects only authorized successors. Explicit human authority remains binding in every mode. Preserve all three enums and report conflicting child wording rather than silently invert actual UI/specification behavior.

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
  <!-- Check DoR; schedule independent DoD review when semantic risk warrants it. -->
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
        2. No actual question or unresolved decision → do not invoke DAO or ask ceremonially.
           IF process_preference.interaction_mode IN ["dao-represent-human-to-interact", "dao-represent-human-to-interact-for-questions-in-skill"]:
             Invoke x-ipe-assistant-user-representative-Engineer using existing message_context;
             consume operation_output.result.instruction_units and execution_plan for bounded guidance.
           ELSE IF process_preference.interaction_mode == "interact-with-human":
             Ask human for clarification and wait.
           ELSE: Block invalid mode; never guess or override caller policy.
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
        3. Return current evidence, actual failures/review gaps and full original
           output to the same lifecycle owner. Explicit required human authority
           remains binding in every mode; representative guidance is not approval.
           No board/Git/successor execution here. Owner handles the boundary once.
      </action>
      <output>Task completion output</output>
    </step_5_N_complete>
  </phase_5>

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
    interaction_mode: "{from input process_preference.interaction_mode}"
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

CRITICAL: Validate DoD deterministically where possible. Require independent review for meaningful workflow, executable, safety, or public-contract changes; document a lightweight self-review rationale for cosmetic/document-only work.

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

CRITICAL: SKILL.md body MUST be ≤ 1000 logical lines, excluding frontmatter. Exactly 1000 passes and 1001 fails; LF/CRLF and a trailing newline count consistently. This is a ceiling, not a target.

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
| standalone | No category-specific board; lifecycle task tracking still applies | x-ipe-tool-task-board-manager via lifecycle |
| feature-stage | Feature lifecycle/category outputs | x-ipe-tool-task-board-manager via lifecycle |
| requirement-stage | Requirement/category outputs; preserve domain persistence contracts | Delegate to lifecycle; no invented board |
| ideation-stage | Ideation/category outputs; preserve domain persistence contracts | Delegate to lifecycle; no invented board |
