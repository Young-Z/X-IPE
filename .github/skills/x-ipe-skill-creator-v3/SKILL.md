---
name: x-ipe-skill-creator
description: Guide for creating effective X-IPE skills with templates, testing, and validation. Use when creating a new skill or updating an existing skill for the X-IPE framework. Triggers on requests like "create skill", "new skill", "add task type skill", "update skill".
---

# X-IPE Skill Creator

## Purpose

Guide for creating effective X-IPE skills by:
1. Identifying skill type and selecting appropriate template
2. Gathering concrete usage examples
3. Creating skill with sub-agent DAG workflow
4. Validating against acceptance criteria
5. Merging to production or iterating on failures

---

## About X-IPE Skills

Skills are modular, self-contained packages that extend AI Agent capabilities by providing specialized knowledge, workflows, and tools.

### What Skills Provide

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for working with specific file formats or APIs
3. **Domain expertise** - Project-specific knowledge, schemas, business logic
4. **Bundled resources** - Templates, references, and scripts for complex tasks

### Skill Types

| Type | Purpose | Naming Convention | Template |
|------|---------|-------------------|----------|
| Task Type | Development lifecycle workflows | `task-type-{name}` | [task-type-skill.md](templates/task-type-skill.md) |
| Tool Skill | Utility functions and tool integrations | `{tool-name}` | [tool-skill.md](templates/tool-skill.md) |
| Workflow Orchestration | Multi-skill coordination | `{category}+{operation}` | [workflow-skill.md](templates/workflow-skill.md) |
| Meta Skill | Creates/manages skills | `x-ipe-{name}` | [meta-skill.md](templates/meta-skill.md) |

---

## Important Notes

BLOCKING: Read [skill-general-guidelines-v2.md](references/skill-general-guidelines-v2.md) for core principles and patterns before creating skills.

CRITICAL: SKILL.md body must stay under 500 lines. Move examples to references/.

MANDATORY: All 4 skill types have complete templates in the templates/ folder.

---

## Input Parameters

```yaml
input:
  skill_name: "{skill-name}"  # lowercase, hyphens, 1-64 chars
  skill_type: task_type | tool_skill | workflow_orchestration | meta_skill
  user_request: "{description of what skill should do}"
  examples: []  # Concrete usage examples (optional)
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
    <name>User Request Clear</name>
    <verification>Clear description of what skill should do</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Concrete Examples Gathered</name>
    <verification>At least 2 usage scenarios documented</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Skill Meta Folder Exist</name>
    <verification>Folder x-ipe-docs/skill-meta/ exists with necessary files</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Identify Skill Type | Determine type, select template | type selected |
| 2 | Gather Examples | Collect usage scenarios | >= 2 examples |
| 3 | Plan Resources | Identify scripts/references/templates needed | resources planned |
| 4-5 | Round 1 (Parallel) | Create skill-meta.md + candidate draft | both complete |
| 6-7 | Round 2 (Parallel) | Reflect on candidate + generate tests | both complete |
| 8 | Round 3 | Run tests in sandbox | tests executed |
| 9 | Round 4 | Evaluate results | evaluation complete |
| 10 | Merge/Iterate | Merge if pass, iterate if fail | decision made |
| 11 | Cross-References | Validate external references | all valid |

---

## Execution Procedure

```xml
<procedure name="skill-creation">

  <step_1>
    <name>Identify Skill Type</name>
    <action>
      1. Determine skill type based on purpose
      2. Select corresponding template from templates/
    </action>
    <branch>
      IF: Development lifecycle workflow → task_type → templates/task-type-skill.md
      IF: Utility functions or integrations → tool_skill → templates/tool-skill.md
      IF: Orchestrates other skills → workflow_orchestration → templates/workflow-skill.md
      IF: Creates/manages skills → meta_skill → templates/meta-skill.md
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
    <output>examples[], trigger_patterns[]</output>
  </step_2>

  <step_3>
    <name>Plan Bundled Resources</name>
    <action>
      1. Analyze examples for reusable patterns
      2. Identify which resource types needed
    </action>
    <resource_types>
      | Type | When to Include |
      |------|-----------------|
      | scripts/ | Same code rewritten repeatedly |
      | references/ | Documentation agent should reference |
      | templates/ | Skill produces standardized documents |
    </resource_types>
    <output>resources_plan[]</output>
  </step_3>

  <step_4_5>
    <name>Round 1: Create Meta + Draft (Parallel)</name>
    <sub_agents>
      - Sub-agent 1: Create skill-meta.md under x-ipe-docs/skill-meta/{skill-name} using template
      - Sub-agent 2: Create candidate/ under x-ipe-docs/skill-meta/{skill-name} with full skill structure
    </sub_agents>
    <constraints>
      - BLOCKING: Both sub-agents must complete before Round 2
    </constraints>
    <output>skill-meta.md, candidate/</output>
  </step_4_5>

  <step_6_7>
    <name>Round 2: Reflect + Test Cases (Parallel)</name>
    <sub_agents>
      - Sub-agent 3: Reflect on candidate against skill-meta
      - Sub-agent 4: Generate test cases from acceptance criteria
    </sub_agents>
    <output>candidate/, test-cases.yaml</output>
  </step_6_7>

  <step_8>
    <name>Round 3: Run Tests</name>
    <sub_agents>
      - Sub-agent 5: Execute tests, save outputs to sandbox/
    </sub_agents>
    <output>sandbox/{outputs}, execution-log.yaml</output>
  </step_8>

  <step_9>
    <name>Round 4: Evaluate Results</name>
    <sub_agents>
      - Sub-agent 6: Evaluate sandbox outputs against expectations
    </sub_agents>
    <evaluation_types>
      - self_check: Structural/content validation
      - judge_agent: Quality scoring with rubric
    </evaluation_types>
    <output>evaluation-report.yaml</output>
  </step_9>

  <step_10>
    <name>Merge or Iterate</name>
    <action>
      1. Check evaluation results
      2. Merge if passing, iterate if failing
    </action>
    <branch>
      IF: must_pass_rate == 100% AND should_pass_rate >= 80%
      THEN: 
        1. cp -r candidate/* .github/skills/{skill-name}/
        2. Update skill-version-history.md
        3. Proceed to Step 11
      
      IF: tests failed AND iteration_count < 3
      THEN: Update candidate, re-run from Round 2
      
      IF: tests failed AND iteration_count >= 3
      THEN: Escalate to human
    </branch>
    <output>merge_status</output>
  </step_10>

  <step_11>
    <name>Validate Cross-References</name>
    <action>
      1. Check copilot-instructions.md registration (task_type only)
      2. Check task-execution-guideline registration (task_type only)
      3. Verify bidirectional references
    </action>
    <constraints>
      - MANDATORY: Task type skills must be registered in copilot-instructions.md
    </constraints>
    <for_task_type>
      Check 1: grep "{skill-name}" .github/copilot-instructions.md
      Check 2: grep "{skill-name}" .github/skills/task-execution-guideline/SKILL.md
      Check 3: grep -r "{skill-name}" .github/skills/
    </for_task_type>
    <output>cross_references_valid</output>
  </step_11>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: standalone
  status: completed | blocked
  next_task_type: null
  require_human_review: yes
  task_output_links:
    - ".github/skills/{skill-name}/SKILL.md"
    - "x-ipe-docs/skill-meta/{skill-name}/skill-meta.md"
  # Dynamic attributes
  skill_name: "{skill-name}"
  skill_type: "{skill_type}"
  test_pass_rate: "{percentage}"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <!-- Step Output Verification -->
  <checkpoint required="true">
    <name>Step 1-3 Outputs Complete</name>
    <verification>skill_type, template_path, examples[], resources_plan[] defined</verification>
    <step_output>skill_type, template_path, examples[], trigger_patterns[], resources_plan[]</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 4-5 Outputs Complete</name>
    <verification>skill-meta.md and candidate/ folder created</verification>
    <step_output>skill-meta.md, candidate/</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 6-7 Outputs Complete</name>
    <verification>test-cases.yaml exists in x-ipe-docs/skill-meta/{skill-name}/</verification>
    <step_output>candidate/, test-cases.yaml</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 8 Outputs Complete</name>
    <verification>sandbox/ folder with test outputs and execution-log.yaml exist</verification>
    <step_output>sandbox/{outputs}, execution-log.yaml</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 9 Outputs Complete</name>
    <verification>evaluation-report.yaml exists with pass/fail results</verification>
    <step_output>evaluation-report.yaml</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 10 Output Complete</name>
    <verification>Skill merged to .github/skills/{skill-name}/ or iteration documented</verification>
    <step_output>merge_status</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 11 Output Complete</name>
    <verification>Cross-references validated (copilot-instructions.md if task_type)</verification>
    <step_output>cross_references_valid</step_output>
  </checkpoint>
  
  <!-- Quality Verification -->
  <checkpoint required="true">
    <name>Candidate SKILL.md Created</name>
    <verification>File exists at x-ipe-docs/skill-meta/{skill-name}/candidate/SKILL.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>SKILL.md Created</name>
    <verification>File exists at .github/skills/{skill-name}/SKILL.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Frontmatter Valid</name>
    <verification>name (1-64 chars) and description (includes triggers)</verification>
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
    <name>Keywords Used</name>
    <verification>Uses BLOCKING/CRITICAL/MANDATORY (not emoji)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Step Outputs Covered in Created Skill</name>
    <verification>Every step output in created skill has corresponding DoD checkpoint</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Cross-References Valid</name>
    <verification>Registered in copilot-instructions.md (if task_type)</verification>
  </checkpoint>
</definition_of_done>
```

---

## Templates

| File | Purpose | When to Use |
|------|---------|-------------|
| [templates/task-type-skill.md](templates/task-type-skill.md) | Task type template | Creating task_type skills |
| [templates/tool-skill.md](templates/tool-skill.md) | Tool skill template | Creating tool_skill skills (including board management) |
| [templates/workflow-skill.md](templates/workflow-skill.md) | Workflow orchestration template | Creating workflow_orchestration skills |
| [templates/meta-skill.md](templates/meta-skill.md) | Meta skill template | Creating meta_skill skills |

---

## References

| File | Purpose | When to Read |
|------|---------|--------------|
| [references/skill-general-guidelines-v2.md](references/skill-general-guidelines-v2.md) | Core principles, patterns, standards | Before creating any skill |
| [references/skill-creation-procedure.md](references/skill-creation-procedure.md) | Detailed step-by-step procedure | During skill creation |
| [references/sub-agent-workflow.md](references/sub-agent-workflow.md) | Sub-agent DAG workflow details | For parallel execution steps |
| [references/examples.md](references/examples.md) | Concrete execution examples | When learning the skill |

---

## Example

See [references/examples.md](references/examples.md) for concrete execution examples including:
1. Creating a task type skill (task-type-bug-fix)
2. Creating a tool skill (pdf)
3. Creating a workflow orchestration skill (feature-pipeline)

---

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `lesson-learned` | Capture issues and feedback | After skill execution with problems |
