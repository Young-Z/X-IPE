---
name: x-ipe-meta-skill-creator
description: Guide for creating effective X-IPE skills with templates, testing, and validation. Use when creating a new skill or updating an existing skill for the X-IPE framework. Triggers on requests like "create skill", "new skill", "add task-based skill", "update skill".
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

| Type | Purpose | Naming Convention | SKILL.md Template | skill-meta.md Template |
|------|---------|-------------------|-------------------|------------------------|
| x-ipe-task-based | Belong to end-to-end project lifecycle workflows | `x-ipe-task-based-{name}` | [x-ipe-task-based.md](templates/x-ipe-task-based.md) | [skill-meta-x-ipe-task-based.md](templates/skill-meta-x-ipe-task-based.md) |
| x-ipe-task-category | Category orchestration when related tasks complete | `x-ipe-{category}-{operation}` | [x-ipe-workflow-orchestration.md](templates/x-ipe-workflow-orchestration.md) | [skill-meta-x-ipe-task-category.md](templates/skill-meta-x-ipe-task-category.md) |
| x-ipe-tool | Utility functions and tool integrations | `x-ipe-tool-{name}` | [x-ipe-tool.md](templates/x-ipe-tool.md) | [skill-meta-x-ipe-tool.md](templates/skill-meta-x-ipe-tool.md) |
| x-ipe-workflow-orchestration | Multi-skill coordination | `x-ipe-workflow-{name}` | [x-ipe-workflow-orchestration.md](templates/x-ipe-workflow-orchestration.md) | [skill-meta-x-ipe-task-based.md](templates/skill-meta-x-ipe-task-based.md) |
| x-ipe-meta | Creates/manages skills | `x-ipe-meta-{name}` | [x-ipe-meta.md](templates/x-ipe-meta.md) | [skill-meta-x-ipe-meta.md](templates/skill-meta-x-ipe-meta.md) |

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
  skill_type: x-ipe-task-based | x-ipe-task-category | x-ipe-tool | x-ipe-workflow-orchestration | x-ipe-meta
  user_request: "{description of what skill should do}"
  examples: []  # Concrete usage examples (optional)
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Skill Type Identified</name>
    <verification>One of: x-ipe-task-based, x-ipe-task-category, x-ipe-tool, x-ipe-workflow-orchestration, x-ipe-meta</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Skill Name Compliant</name>
    <verification>Matches naming convention: x-ipe-{type}-{name} (lowercase, hyphens only, 1-64 chars)</verification>
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
| 3 | Plan Resources | Identify scripts/references/templates | resources planned |
| 4 | Round 1: Meta + Draft | Create skill-meta.md + candidate/ (parallel sub-agents 1,2) | both complete |
| 5 | Round 2: Reflect + Tests | Reflect on candidate + generate tests (parallel sub-agents 3,4) | both complete |
| 6 | Round 3: Run Tests | Execute tests in sandbox (sub-agent 5) | tests executed |
| 7 | Round 4: Evaluate | Evaluate results (sub-agent 6) | evaluation complete |
| 8 | Merge/Iterate | Merge if pass, iterate if fail | decision made |
| 9 | Cross-References | Validate external references | all valid |

---

## Execution Procedure

```xml
<procedure name="skill-creation">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Identify Skill Type</name>
    <action>
      1. Determine skill type based on purpose
      2. Select corresponding SKILL.md template from templates/
      3. Select corresponding skill-meta.md template from templates/
      4. IF Belong to end-to-end project lifecycle workflows → x-ipe-task-based:
         - SKILL.md: templates/x-ipe-task-based.md
         - skill-meta.md: templates/skill-meta-x-ipe-task-based.md
      5. IF Utility functions or integrations → x-ipe-tool:
         - SKILL.md: templates/x-ipe-tool.md
         - skill-meta.md: templates/skill-meta-x-ipe-tool.md
      6. IF Orchestrates other skills → x-ipe-workflow-orchestration:
         - SKILL.md: templates/x-ipe-workflow-orchestration.md
         - skill-meta.md: templates/skill-meta-x-ipe-task-based.md (same structure)
      7. IF Creates/manages skills → x-ipe-meta:
         - SKILL.md: templates/x-ipe-meta.md
         - skill-meta.md: templates/skill-meta-x-ipe-meta.md
      8. IF Category orchestration → x-ipe-task-category:
         - SKILL.md: templates/x-ipe-workflow-orchestration.md
         - skill-meta.md: templates/skill-meta-x-ipe-task-category.md
    </action>
    <constraints>
      - BLOCKING: Must select exactly one skill type
      - BLOCKING: Must identify both SKILL.md and skill-meta.md templates
    </constraints>
    <success_criteria>
      - Skill type identified
      - SKILL.md template path determined
      - skill-meta.md template path determined
    </success_criteria>
    <output>skill_type, skill_template_path, skill_meta_template_path</output>
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
    <success_criteria>
      - At least 2 usage scenarios documented
      - Trigger patterns identified
    </success_criteria>
    <output>examples[], trigger_patterns[]</output>
  </step_2>

  <step_3>
    <name>Plan Bundled Resources</name>
    <action>
      1. Analyze examples for reusable patterns
      2. Identify which resource types needed:
         - scripts/: Same code rewritten repeatedly
         - references/: Documentation agent should reference
         - templates/: Skill produces standardized documents
    </action>
    <success_criteria>
      - Resource requirements documented
    </success_criteria>
    <output>resources_plan[]</output>
  </step_3>

  <step_4>
    <name>Round 1: Create Meta + Draft</name>
    <requires>skill_type, skill_template_path, skill_meta_template_path, examples[], resources_plan[]</requires>
    <action>
      1. Load skill-meta template from {skill_meta_template_path}
      2. Create skill-meta.md under x-ipe-docs/skill-meta/{skill-name}/ by filling template
      3. Load SKILL.md template from {skill_template_path}
      4. Create candidate/ under x-ipe-docs/skill-meta/{skill-name}/ with full skill structure
    </action>
    <constraints>
      - BLOCKING: Both outputs must complete before Round 2
      - BLOCKING: skill-meta.md MUST be created from template, not from scratch
      - BLOCKING: SKILL.md MUST be created from template, not from scratch
    </constraints>
    <success_criteria>
      - skill-meta.md exists (created from {skill_meta_template_path})
      - candidate/ folder with SKILL.md exists (created from {skill_template_path})
    </success_criteria>
    <output>skill-meta.md, candidate/</output>
  </step_4>

  <step_5>
    <name>Round 2: Reflect + Test Cases</name>
    <requires>skill-meta.md, candidate/</requires>
    <action>
      1. Reflect on candidate against skill-meta
      2. Generate test cases from acceptance criteria
    </action>
    <success_criteria>
      - Candidate refined based on reflection
      - test-cases.yaml created
    </success_criteria>
    <output>candidate/, test-cases.yaml</output>
  </step_5>

  <step_6>
    <name>Round 3: Run Tests</name>
    <requires>test-cases.yaml</requires>
    <action>
      1. Execute tests in sandbox environment
      2. Save outputs to sandbox/ folder
    </action>
    <success_criteria>
      - All tests executed
      - Execution log recorded
    </success_criteria>
    <output>sandbox/{outputs}, execution-log.yaml</output>
  </step_6>

  <step_7>
    <name>Round 4: Evaluate Results</name>
    <requires>sandbox/{outputs}, execution-log.yaml</requires>
    <action>
      1. Evaluate sandbox outputs against expectations
      2. Use self_check for structural/content validation
      3. Use judge_agent for quality scoring with rubric
    </action>
    <success_criteria>
      - Evaluation report generated
      - Pass/fail determination made
    </success_criteria>
    <output>evaluation-report.yaml</output>
  </step_7>

  <step_8>
    <name>Merge or Iterate</name>
    <requires>evaluation-report.yaml</requires>
    <action>
      1. Check evaluation results
      2. IF must_pass_rate == 100% AND should_pass_rate >= 80%:
         - cp -r candidate/* .github/skills/{skill-name}/
         - Update skill-version-history.md
         - Proceed to Step 9
      3. IF tests failed AND iteration_count < 3:
         - Update candidate, re-run from Round 2
      4. IF tests failed AND iteration_count >= 3:
         - Escalate to human
    </action>
    <success_criteria>
      - Skill merged OR iteration documented
    </success_criteria>
    <output>merge_status</output>
  </step_8>

  <step_9>
    <name>Validate Cross-References</name>
    <requires>merge_status == merged</requires>
    <action>
      1. Check copilot-instructions.md registration (x-ipe-task-based only)
      2. Check x-ipe-workflow-task-execution registration (x-ipe-task-based only)
      3. Verify bidirectional references
    </action>
    <constraints>
      - MANDATORY: Task type skills must be registered in copilot-instructions.md
    </constraints>
    <success_criteria>
      - Cross-references validated
    </success_criteria>
    <output>cross_references_valid</output>
  </step_9>

  <sub-agent-planning>
    <sub_agent_1>
      <sub_agent_definition>
        <role>Meta Creator</role>
        <prompt>Load skill-meta template from {skill_meta_template_path}, fill with skill-specific content (purpose, acceptance criteria, test scenarios). Output: x-ipe-docs/skill-meta/{skill-name}/skill-meta.md</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_4</workflow_step_reference>
    </sub_agent_1>
    <sub_agent_2>
      <sub_agent_definition>
        <role>Draft Creator</role>
        <prompt>Load SKILL.md template from {skill_template_path}, fill with skill-specific content following guidelines. Output: x-ipe-docs/skill-meta/{skill-name}/candidate/</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_4</workflow_step_reference>
    </sub_agent_2>
    <sub_agent_3>
      <sub_agent_definition>
        <role>Reflector</role>
        <prompt>Review candidate against skill-meta, identify gaps, suggest improvements</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_5</workflow_step_reference>
      <starting_condition>
        - "START after sub_agent_1 and sub_agent_2 complete"
      </starting_condition>
    </sub_agent_3>
    <sub_agent_4>
      <sub_agent_definition>
        <role>Test Generator</role>
        <prompt>Generate test-cases.yaml from acceptance criteria in skill-meta.md</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_5</workflow_step_reference>
      <starting_condition>
        - "START after sub_agent_1 and sub_agent_2 complete"
      </starting_condition>
    </sub_agent_4>
    <sub_agent_5>
      <sub_agent_definition>
        <role>Test Runner</role>
        <prompt>Execute test cases in sandbox, record outputs and execution log</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_6</workflow_step_reference>
      <starting_condition>
        - "START after sub_agent_3 and sub_agent_4 complete"
      </starting_condition>
    </sub_agent_5>
    <sub_agent_6>
      <sub_agent_definition>
        <role>Evaluator</role>
        <prompt>Evaluate sandbox outputs against expectations, generate evaluation-report.yaml</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_7</workflow_step_reference>
      <starting_condition>
        - "START after sub_agent_5 completes"
      </starting_condition>
    </sub_agent_6>
  </sub-agent-planning>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: standalone
  status: completed | blocked
  next_task_based_skill: null
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
    <name>Step 4 Outputs Complete</name>
    <verification>skill-meta.md and candidate/ folder created</verification>
    <step_output>skill-meta.md, candidate/</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 5 Outputs Complete</name>
    <verification>test-cases.yaml exists in x-ipe-docs/skill-meta/{skill-name}/</verification>
    <step_output>candidate/, test-cases.yaml</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 6 Outputs Complete</name>
    <verification>sandbox/ folder with test outputs and execution-log.yaml exist</verification>
    <step_output>sandbox/{outputs}, execution-log.yaml</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 7 Outputs Complete</name>
    <verification>evaluation-report.yaml exists with pass/fail results</verification>
    <step_output>evaluation-report.yaml</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 8 Output Complete</name>
    <verification>Skill merged to .github/skills/{skill-name}/ or iteration documented</verification>
    <step_output>merge_status</step_output>
  </checkpoint>
  <checkpoint required="true">
    <name>Step 9 Output Complete</name>
    <verification>Cross-references validated (copilot-instructions.md if x-ipe-task-based)</verification>
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
    <verification>Registered in copilot-instructions.md (if x-ipe-task-based)</verification>
  </checkpoint>
</definition_of_done>
```

---

## Templates

| Template | Purpose |
|----------|---------|
| [x-ipe-task-based.md](templates/x-ipe-task-based.md) | SKILL.md for task-based skills |
| [x-ipe-tool.md](templates/x-ipe-tool.md) | SKILL.md for tool skills |
| [x-ipe-workflow-orchestration.md](templates/x-ipe-workflow-orchestration.md) | SKILL.md for workflow/task-category skills |
| [x-ipe-meta.md](templates/x-ipe-meta.md) | SKILL.md for meta skills |
| [skill-meta-x-ipe-task-based.md](templates/skill-meta-x-ipe-task-based.md) | skill-meta for task-based/workflow skills |
| [skill-meta-x-ipe-tool.md](templates/skill-meta-x-ipe-tool.md) | skill-meta for tool skills |
| [skill-meta-x-ipe-task-category.md](templates/skill-meta-x-ipe-task-category.md) | skill-meta for task-category skills |
| [skill-meta-x-ipe-meta.md](templates/skill-meta-x-ipe-meta.md) | skill-meta for meta skills |

BLOCKING: Always use the appropriate template. Never create SKILL.md or skill-meta.md from scratch.

---

## References

| File | Purpose |
|------|---------|
| [skill-general-guidelines-v2.md](references/skill-general-guidelines-v2.md) | Core principles, patterns, standards |
| [2. reference-section-order.md](references/2.%20reference-section-order.md) | Section ordering guide |
| [3-6. example-*.md](references/) | Workflow pattern examples (step-based, function-based) |
| [7-10. example-*.md](references/) | Task IO, structured summary, DoR/DoD, gate conditions |
| [11. reference-quality-standards.md](references/11.%20reference-quality-standards.md) | Quality standards |
| [examples.md](references/examples.md) | Concrete execution examples |

---

## Example

See [references/examples.md](references/examples.md) for concrete execution examples.

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| `x-ipe-meta-lesson-learned` | Capture issues and feedback after skill execution |
