# Skill Creation Procedure

Step-by-step procedure for creating X-IPE skills using Pattern 2 (XML-Tagged) format.

BLOCKING: Read [skill-general-guidelines-v2.md](../../skill-creation-best-practice/skill-general-guidelines-v2.md) before starting.

---

## Input Parameters

```yaml
input:
  skill_name: "{skill-name}"  # lowercase, hyphens, 1-64 chars
  skill_type: task_type | tool_skill | workflow_orchestration | meta_skill
  examples: []  # Concrete usage examples from user
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Skill Type Identified</name>
    <verification>One of: task_type, tool_skill, workflow_orchestration, meta_skill</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Concrete Examples Gathered</name>
    <verification>At least 2 usage scenarios documented</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Guidelines Read</name>
    <verification>skill-general-guidelines-v2.md reviewed</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Procedure

```xml
<procedure name="skill-creation">

  <step_1>
    <name>Identify Skill Type</name>
    <action>
      1. Determine skill type based on purpose
      2. Select corresponding template
    </action>
    <constraints>
      - BLOCKING: Must match exactly one skill type
    </constraints>
    <branch>
      IF: Development lifecycle workflow
      THEN: task_type → use task-type-skill.md template
      
      IF: Utility functions or integrations
      THEN: tool_skill → use tool-skill.md template
      
      IF: Orchestrates other skills
      THEN: workflow_orchestration → use workflow-skill.md template
      
      IF: Creates/manages skills
      THEN: meta_skill → use meta-skill.md template
    </branch>
    <output>skill_type, template_path</output>
  </step_1>

  <step_2>
    <name>Gather Concrete Examples</name>
    <action>
      1. Ask user for functionality requirements
      2. Collect trigger phrase examples
      3. Document expected outputs
    </action>
    <constraints>
      - CRITICAL: Skip only if patterns already clearly understood
    </constraints>
    <questions>
      - "What functionality should this skill support?"
      - "Can you give examples of how this skill would be used?"
      - "What would a user say that should trigger this skill?"
    </questions>
    <success_criteria>
      - At least 2 usage examples documented
      - Trigger patterns identified
    </success_criteria>
    <output>examples[], trigger_patterns[]</output>
  </step_2>

  <step_3>
    <name>Plan Bundled Resources</name>
    <action>
      1. Analyze examples for reusable patterns
      2. Identify which resource types needed
    </action>
    <constraints>
      - Follow Progressive Disclosure principle (Level 3 resources)
    </constraints>
    <resource_types>
      | Type | When to Include |
      |------|-----------------|
      | scripts/ | Same code rewritten repeatedly, deterministic reliability needed |
      | references/ | Documentation agent should reference while working |
      | templates/ | Skill produces standardized documents |
    </resource_types>
    <output>resources_plan[]</output>
  </step_3>

  <step_4>
    <name>Create Skill Directory</name>
    <action>
      1. Create skill folder at .github/skills/{skill-name}/
      2. Create needed subfolders based on resources_plan
    </action>
    <constraints>
      - BLOCKING: Folder name must be lowercase with hyphens, 1-64 chars
    </constraints>
    <command>mkdir -p .github/skills/{skill-name}/{templates,references,scripts}</command>
    <output>skill_directory_path</output>
  </step_4>

  <step_5>
    <name>Write SKILL.md Frontmatter</name>
    <action>
      1. Write YAML frontmatter with name and description
      2. Include trigger conditions in description
    </action>
    <constraints>
      - BLOCKING: description is PRIMARY triggering mechanism
      - CRITICAL: Include BOTH what skill does AND when to use it
      - MANDATORY: No separate "When to Use" section in body
    </constraints>
    <template>
      ```yaml
      ---
      name: {skill-name}
      description: {What it does}. Use when {trigger conditions}. Triggers on requests like "{trigger 1}", "{trigger 2}".
      ---
      ```
    </template>
    <output>frontmatter_complete</output>
  </step_5>

  <step_6>
    <name>Write SKILL.md Body</name>
    <action>
      1. Follow section order from reference-section-order.md
      2. Apply appropriate workflow pattern per section complexity
    </action>
    <constraints>
      - BLOCKING: Follow cognitive flow (CONTEXT → DECISION → ACTION → VERIFY → REFERENCE)
      - CRITICAL: SKILL.md must be < 500 lines
      - Use keywords (BLOCKING, CRITICAL, MANDATORY) for importance signals
    </constraints>
    <section_order_by_type>
      task_type: Purpose → Important Notes → Input Parameters → DoR → Execution Flow → Execution Procedure → Output Result → DoD → Patterns/Anti-Patterns → Examples
      
      tool_skill: Purpose → Important Notes → About → When to Use → Input Parameters → DoR → Operations → Output Result → DoD → Error Handling → Templates → Examples
      
      workflow_orchestration: Purpose → Important Notes → Input Parameters → DoR → Execution Flow → Execution Procedure → Output Result → DoD → Registry → Error Handling → Templates → Examples
      
      meta_skill: Purpose → About → Important Notes → Input Parameters → DoR → Execution Flow → Execution Procedure → Output Result → DoD → Templates → Examples
    </section_order_by_type>
    <pattern_selection>
      | Pattern | Use For |
      |---------|---------|
      | YAML (Pattern 1) | Complex branching logic, if/else, multi-path decisions |
      | XML (Pattern 2) | Linear steps with distinct constraints/outputs |
      | Phase Blocks (Pattern 3) | 5+ phases, multi-domain processes |
    </pattern_selection>
    <output>skill_body_complete</output>
  </step_6>

  <step_7>
    <name>Create Reference Files</name>
    <action>
      1. Create references/examples.md (mandatory for task_type)
      2. Create additional bundled resources per plan
    </action>
    <constraints>
      - MANDATORY: Task type skills must have references/examples.md
    </constraints>
    <examples_template>
      ```markdown
      # {Skill Name} - Examples
      
      ## Example 1: {Happy Path}
      **Request:** "{request}"
      **Execution:** [step-by-step]
      **Output:** [files created]
      
      ## Example 2: {Edge Case}
      ...
      
      ## Example 3: {Error/Blocked Scenario}
      ...
      ```
    </examples_template>
    <output>reference_files[]</output>
  </step_7>

  <step_8>
    <name>Validate Structure</name>
    <action>
      1. Run files check
      2. Run content check
      3. Run section order check
    </action>
    <constraints>
      - BLOCKING: All required checks must pass
    </constraints>
    <files_check>
      | File | Required For |
      |------|--------------|
      | SKILL.md | All skills |
      | references/examples.md | task_type skills |
    </files_check>
    <content_check>
      | Check | Criteria |
      |-------|----------|
      | Frontmatter | Has name and description |
      | Description | Includes trigger phrases |
      | DoR | Uses XML checkpoint format |
      | DoD | Uses XML checkpoint format |
      | Execution | Uses appropriate pattern (YAML/XML/Phase) |
      | Keywords | Uses BLOCKING/CRITICAL/MANDATORY (not emojis) |
      | Line count | SKILL.md < 500 lines |
    </content_check>
    <success_criteria>
      - All files present
      - All content checks pass
      - Section order matches skill type
    </success_criteria>
    <output>validation_result</output>
  </step_8>

  <step_9>
    <name>Validate Cross-References</name>
    <action>
      1. Check copilot-instructions.md registration (task_type only)
      2. Check task-execution-guideline registration (task_type only)
      3. Check related skill bidirectional references
    </action>
    <constraints>
      - CRITICAL: Task type skills must be registered in copilot-instructions.md
    </constraints>
    <for_task_type>
      Check 1: grep "{skill-name}" .github/copilot-instructions.md
        - Skill in Task Types Registry table
        - Category, Next Task, Human Review correct
      
      Check 2: grep "{skill-name}" .github/skills/task-execution-guideline/SKILL.md
        - Skill in Category Derivation table
        - Category assignment correct
      
      Check 3: grep -r "{skill-name}" .github/skills/
        - Related skills updated
        - Prerequisites bidirectionally consistent
    </for_task_type>
    <for_all_skills>
      - No broken links to templates/references
      - Referenced skills exist
      - Category assignments match
    </for_all_skills>
    <output>cross_references_valid</output>
  </step_9>

  <step_10>
    <name>Final Review</name>
    <action>
      1. Review against core principles
      2. Confirm readiness
    </action>
    <principles_check>
      | Principle | Verification |
      |-----------|--------------|
      | Concise is Key | No unnecessary explanations? Token-justified? |
      | Degrees of Freedom | Appropriate specificity per section? |
      | Progressive Disclosure | Heavy content in references (Level 3)? |
      | Agent-Optimized Formats | Keywords not emojis? Structured data? |
    </principles_check>
    <output>skill_ready</output>
  </step_10>

</procedure>
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently. This improves quality gate accuracy through isolation.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>SKILL.md Created</name>
    <verification>File exists at .github/skills/{skill-name}/SKILL.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Frontmatter Valid</name>
    <verification>name (1-64 chars) and description (1-1024 chars with triggers)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Section Order Correct</name>
    <verification>Follows cognitive flow per skill type</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Line Count Under Limit</name>
    <verification>SKILL.md < 500 lines</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Cross-References Valid</name>
    <verification>Registered in copilot-instructions.md (if task_type)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Examples Created</name>
    <verification>references/examples.md exists (if task_type)</verification>
  </checkpoint>
</definition_of_done>
```

---

## Quick Reference

```yaml
checklist:
  - step: 1 - Identify skill type
  - step: 2 - Gather concrete examples
  - step: 3 - Plan bundled resources
  - step: 4 - Create skill directory
  - step: 5 - Write frontmatter
  - step: 6 - Write body sections (cognitive flow order)
  - step: 7 - Create reference files
  - step: 8 - Validate structure
  - step: 9 - Validate cross-references
  - step: 10 - Final review

skill_types:
  task_type: "task-type-{name}" → Development lifecycle workflows
  tool_skill: "{tool-name}" → Utility functions, integrations
  workflow_orchestration: "{category}+{operation}" → Multi-skill coordination
  meta_skill: "x-ipe-{name}" → Skills for creating/managing skills

importance_keywords:
  BLOCKING: Must not skip, halts execution
  CRITICAL: High priority, affects correctness
  MANDATORY: Required, continue with warning if missing
```
