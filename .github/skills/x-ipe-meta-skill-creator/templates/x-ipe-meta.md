# Meta Skill Template

Use this template when creating a skill that creates, manages, or operates on other skills. Meta skills are X-IPE framework-level tools.

**Section Order (Cognitive Flow):**
1. CONTEXT: Purpose → About → Important Notes
2. DECISION: Input Parameters → Definition of Ready
3. ACTION: Execution Flow Summary → Execution Procedure
4. VERIFY: Output Result → Definition of Done
5. REFERENCE: Templates → Examples

---

```markdown
---
name: x-ipe-meta-{skill-name}
description: {Brief description of what this meta skill does}. Use when {trigger conditions}. Triggers on requests like "{trigger 1}", "{trigger 2}".
---

# {Meta Skill Name}

## Purpose

{Brief description of what this meta skill accomplishes} by:
1. {Step 1}
2. {Step 2}
3. {Step 3}
4. {Step 4}

---

## About

{Domain explanation of what this meta skill operates on and why it exists}

### Key Concepts

- **{Concept 1}** - {Definition}
- **{Concept 2}** - {Definition}
- **{Concept 3}** - {Definition}

### Scope

```yaml
operates_on:
  - "{What this skill creates/manages}"
  - "{Related entities}"
  
does_not_handle:
  - "{Out of scope items}"
```

---

## Important Notes

BLOCKING: {Critical prerequisite or constraint}

CRITICAL: {Important consideration that affects quality}

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  # Primary input
  {primary_input}: "{description}"
  
  # Configuration options
  {option_1}: "{default_value}"
  {option_2}: "{default_value}"
  
  # Context (from project or previous execution)
  {context_field}: "{value_or_path}"
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
| 4 | Validate | Verify DoD | DoD validated |

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
    <!-- Conditional logic goes inside <action> as inline IF/THEN/ELSE -->
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
  category: standalone
  status: completed | blocked
  next_task_based_skill: null
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
  <checkpoint required="true">
    <name>{Quality Check Passed}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
</definition_of_done>
```

---

## Templates

| File | Purpose | When to Use |
|------|---------|-------------|
| `templates/{template-1}.md` | {Purpose} | {When to use} |
| `templates/{template-2}.md` | {Purpose} | {When to use} |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.
```

---

## Template Usage Notes

### Naming Convention

Meta skills use the `x-ipe-` prefix:
- `x-ipe-{name}` format
- Examples:
  - `x-ipe-skill-creator` - Creates and manages skills
  - `x-ipe-skill-validator` - Validates skill structure
  - `x-ipe-skill-registry` - Manages skill registry

### Section Order (v2 Cognitive Flow)

MANDATORY: Sections must appear in this sequence:

```yaml
meta_skills:
  section_order:
    # CONTEXT
    1: Purpose
    2: About
    3: Important Notes
    # DECISION
    4: Input Parameters
    5: Definition of Ready (DoR)
    # ACTION
    6: Execution Flow Summary
    7: Execution Procedure
    # VERIFY
    8: Output Result
    9: Definition of Done (DoD)
    # REFERENCE
    10: Templates
    11: Examples
```

### Format Standards

| Element | Format |
|---------|--------|
| Execution procedure | XML `<procedure>` blocks |
| Data models | YAML |
| DoR/DoD | XML checkpoints |
| Importance signals | Keywords (BLOCKING, CRITICAL, MANDATORY) |

### Key Characteristics of Meta Skills

| Aspect | Description |
|--------|-------------|
| Scope | Operates on X-IPE framework itself |
| Output | Creates/modifies skills or framework components |
| Naming | Always prefixed with `x-ipe-` |
| Category | Always `standalone` |
| Self-reference | May reference other meta skills |

### Common Meta Skill Patterns

```yaml
patterns:
  skill_creation:
    description: "Creates new skills from templates"
    key_steps:
      - Identify skill type
      - Apply template
      - Validate structure
      - Register in framework
      
  skill_validation:
    description: "Validates existing skills against standards"
    key_steps:
      - Load skill
      - Check structure
      - Verify cross-references
      - Report findings
      
  skill_maintenance:
    description: "Updates skills based on lessons or changes"
    key_steps:
      - Identify changes needed
      - Apply updates
      - Re-validate
      - Update version
```

### Sub-Agent Pattern for Meta Skills

Meta skills often use sub-agents for complex operations:

```yaml
sub_agent_workflow:
  round_1_parallel:
    - agent: "meta_analyzer"
      task: "Analyze input and plan"
    - agent: "template_loader"
      task: "Load appropriate templates"
      
  round_2_sequential:
    - agent: "content_creator"
      task: "Create skill content"
      
  round_3_parallel:
    - agent: "validator"
      task: "Validate output"
    - agent: "test_generator"
      task: "Generate tests"
      
  round_4_sequential:
    - agent: "finalizer"
      task: "Finalize and register"
```
