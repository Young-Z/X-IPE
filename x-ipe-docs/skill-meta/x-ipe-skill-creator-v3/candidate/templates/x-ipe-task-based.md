# Task Type Skill Template

Use this template when creating a new task type skill. Follow v2 guidelines format.

**Section Order (Cognitive Flow):**
1. CONTEXT: Purpose → Important Notes
2. DECISION: Input Parameters → Definition of Ready
3. ACTION: Execution Flow Summary → Execution Procedure
4. VERIFY: Output Result → Definition of Done
5. REFERENCE: Patterns & Anti-Patterns → Examples

---

```markdown
---
name: x-ipe-task-based-{skill-name}
description: {Brief description of what this task type does}. Use when {trigger conditions}. Triggers on requests like "{trigger 1}", "{trigger 2}".
---

# Task Type: {Skill Name}

## Purpose

{Brief description of what this task type accomplishes} by:
1. {Step 1}
2. {Step 2}
3. {Step 3}
4. {Step 4}

---

## Important Notes

BLOCKING: Learn `task-execution-guideline` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_type: "{task_type}"
  
  # Task type attributes
  category: "{standalone | feature-stage | requirement-stage | ideation-stage}"
  next_task_type: "{Next Task Type | null}"
  require_human_review: "{yes | no}"
  
  # Required inputs
  auto_proceed: false
  {input_1}: "{default_value}"
  {input_2}: "{default_value}"
  
  # Context (from previous task or project)
  {context_attr}: "{value_or_path}"
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

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | {Step Name} | {Brief action} | {gate condition} |
| 2 | {Step Name} | {Brief action} | {gate condition} |
| 3 | {Step Name} | {Brief action} | {gate condition} |
| 4 | Complete | Verify DoD | DoD validated |

BLOCKING: {Rule that must not be skipped}

---

## Execution Procedure

```xml
<procedure name="{skill-name}">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>{Step Name}</name>
    <action>
      1. {Sub-action 1}
      2. {Sub-action 2}
      3. {Sub-action 3}
    </action>
    <constraints>
      - BLOCKING: {Must not violate}
      - CRITICAL: {Important consideration}
    </constraints>
    <output>{What this step produces}</output>
  </step_1>

  <step_2>
    <name>{Step Name}</name>
    <action>
      1. {Sub-action 1}
      2. {Sub-action 2}
    </action>
    <branch>
      IF: {condition}
      THEN: {action if true}
      ELSE: {action if false}
    </branch>
    <output>{What this step produces}</output>
  </step_2>

  <step_3>
    <name>{Step Name}</name>
    <action>
      1. {Sub-action 1}
      2. {Sub-action 2}
    </action>
    <success_criteria>
      - {Criterion 1}
      - {Criterion 2}
    </success_criteria>
    <output>{What this step produces}</output>
  </step_3>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "{standalone | feature-stage | requirement-stage | ideation-stage}"
  status: completed | blocked
  next_task_type: "{Next Task Type}"
  require_human_review: "{yes | no}"
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

MANDATORY: After completing this skill, return to `task-execution-guideline` to continue the task execution flow.

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
- Execution Flow (overview table)
- Execution Procedure (essential steps only)

**Move to references/:**
- `references/examples.md` - Detailed execution examples (MANDATORY)
- `references/detailed-procedures.md` - Complex step-by-step guides

### Section Order (v2 Cognitive Flow)

MANDATORY: Sections must appear in this sequence:

```yaml
task_type_skills:
  section_order:
    # CONTEXT
    1: Purpose
    2: Important Notes
    # DECISION
    3: Input Parameters
    4: Definition of Ready (DoR)
    # ACTION
    5: Execution Flow Summary
    6: Execution Procedure
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
| Execution procedure | XML procedure | `<procedure name="...">` |
| Data models | YAML | `input:`, `output:` |
| Variables | Braces | `{skill_name}`, `{task_id}` |

### Category Values

| Category | Description | Board Skill |
|----------|-------------|-------------|
| standalone | No board tracking | None |
| feature-stage | Updates feature board | feature-board-management |
| requirement-stage | Updates requirement board | requirement-board-management |
| ideation-stage | Updates ideation board | ideation-board-management |
