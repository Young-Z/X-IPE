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
| x-ipe-task-based | Belong to end-to-end project lifecycle workflows | `x-ipe-task-based-{name}` | [x-ipe-task-based.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-task-based.md) | [skill-meta-x-ipe-task-based.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-task-based.md) |
| x-ipe-task-category | Category orchestration when related tasks complete | `x-ipe+{category}+{name}` (`all` for cross-category) | [x-ipe-workflow-orchestration.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-workflow-orchestration.md) | [skill-meta-x-ipe-task-category.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-task-category.md) |
| x-ipe-tool | Utility functions and tool integrations | `x-ipe-tool-{name}` | [x-ipe-tool.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-tool.md) | [skill-meta-x-ipe-tool.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-tool.md) |
| x-ipe-workflow-orchestration | Multi-skill coordination | `x-ipe-workflow-{name}` | [x-ipe-workflow-orchestration.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-workflow-orchestration.md) | [skill-meta-x-ipe-task-based.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-task-based.md) |
| x-ipe-meta | Creates/manages skills | `x-ipe-meta-{name}` | [x-ipe-meta.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-meta.md) | [skill-meta-x-ipe-meta.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-meta.md) |
| x-ipe-knowledge | Knowledge pipeline services (Operations + Steps) | `x-ipe-knowledge-{sub-category}-{name}` | [x-ipe-knowledge.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-knowledge.md) | N/A |
| x-ipe-assistant | Assistant/orchestrator skills (格物致知 backbone) | `x-ipe-assistant-{name}` | [x-ipe-assistant.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-assistant.md) | [skill-meta-x-ipe-assistant.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-assistant.md) |
| x-ipe-dao ⚠️ | DEPRECATED → use x-ipe-assistant | `x-ipe-dao-{name}` | [x-ipe-dao.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-dao.md) | [skill-meta-x-ipe-dao.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-dao.md) |

> See [skill-type-comparison.md](.github/skills/x-ipe-meta-skill-creator/references/skill-type-comparison.md) for detailed comparison of all skill types.

---

## Important Notes

BLOCKING: **NEVER directly edit files in `.github/skills/{skill-name}/`.**
All skill modifications MUST go through the candidate workflow:
1. Edit in `x-ipe-docs/skill-meta/{skill-name}/candidate/`
2. Validate via reflection + tests (Rounds 2–3)
3. Merge candidate → `.github/skills/{skill-name}/` only after validation

BLOCKING: Read [skill-general-guidelines-v2.md](.github/skills/x-ipe-meta-skill-creator/references/skill-general-guidelines-v2.md) for core principles and patterns before creating skills.

CRITICAL: SKILL.md body must stay under 500 lines (600 for x-ipe-tool type). Move examples to references/. DoR ≤ 5 checkpoints, DoD ≤ 10 checkpoints — if over limit, merge related checks.

MANDATORY: All 8 skill types have complete templates in the templates/ folder. See [skill-type-comparison.md](.github/skills/x-ipe-meta-skill-creator/references/skill-type-comparison.md) for details.

CRITICAL: Each step MUST have exactly ONE `<action>` block containing ALL actions. Do NOT split actions into separate blocks (e.g., `<branch>`). Conditional logic (IF/THEN/ELSE) belongs inline within the `<action>` numbered list.

CRITICAL: Before populating skill content, check `x-ipe-docs/skill-meta/{related-skill}/x-ipe-meta-lesson-learned.md` for lessons from similar skills. Apply relevant lessons to avoid repeating known mistakes. Reference: [12. reference-production-patterns.md](.github/skills/x-ipe-meta-skill-creator/references/12.%20reference-production-patterns.md)

---

## Input Parameters

```yaml
input:
  skill_name: "{skill-name}"  # lowercase, hyphens, 1-64 chars
  skill_type: x-ipe-task-based | x-ipe-task-category | x-ipe-tool | x-ipe-workflow-orchestration | x-ipe-meta | x-ipe-knowledge | x-ipe-assistant | x-ipe-dao
  user_request: "{description of what skill should do}"
  examples: []  # Concrete usage examples (optional)
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Skill Type Identified</name>
    <verification>One of: x-ipe-task-based, x-ipe-task-category, x-ipe-tool, x-ipe-workflow-orchestration, x-ipe-meta, x-ipe-knowledge, x-ipe-assistant, x-ipe-dao</verification>
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
| 4 | Self-Critique Scope | AI validates scope; escalates only specific ambiguities | scope validated |
| 5 | Round 1: Meta + Draft | Create skill-meta.md + candidate/ (sub-agent 1) | both complete |
| 6 | Round 2: Reflect + Tests | Reflect on candidate + generate tests (sub-agent 2) | both complete |
| 7 | Round 3: Run Tests | Execute tests in sandbox (sub-agent 3) | tests executed |
| 8 | Round 4: Evaluate | Evaluate results (sub-agent 4) | evaluation complete |
| 9 | Merge/Iterate | Merge if pass, iterate if fail | decision made |
| 10 | Cross-References | Validate external references | all valid |

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
      8. IF Human representative skill → x-ipe-dao: ⚠️ DEPRECATED → redirects to x-ipe-assistant
         - SKILL.md: templates/x-ipe-assistant.md
         - skill-meta.md: templates/skill-meta-x-ipe-assistant.md
      9. IF Category orchestration → x-ipe-task-category:
         - SKILL.md: templates/x-ipe-workflow-orchestration.md
         - skill-meta.md: templates/skill-meta-x-ipe-task-category.md
      10. IF Knowledge pipeline service (Operations + Steps, called by assistant orchestrator) → x-ipe-knowledge:
          - SKILL.md: templates/x-ipe-knowledge.md
          - skill-meta.md: N/A (no dedicated skill-meta template yet)
      11. IF Assistant/orchestrator skill (格物致知 backbone, coordinates other skills) → x-ipe-assistant:
          - SKILL.md: templates/x-ipe-assistant.md
          - skill-meta.md: templates/skill-meta-x-ipe-assistant.md
    </action>
    <constraints>
      - BLOCKING: Must select exactly one skill type
      - BLOCKING: Must identify both SKILL.md and skill-meta.md templates
    </constraints>
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
    <name>Self-Critique Scope</name>
    <requires>skill_type, skill_template_path, examples[], resources_plan[]</requires>
    <action>
      1. AI self-critique — validate scope against objective criteria:
         a. Skill type matches the description (e.g., not a tool skill disguised as task-based)
         b. Template path exists and is correct for the chosen type
         c. Examples cover at least 2 distinct trigger patterns
         d. Resources plan references only files that will be created (no dangling refs)
         e. No naming conflicts with existing skills in .github/skills/
      2. Collect unresolved_questions[] — ONLY genuine ambiguities:
         - "This skill could be task-based OR tool type — which fits better?"
         - "Example 2 overlaps with existing skill X — should we merge or keep separate?"
      3. IF unresolved_questions is EMPTY → scope validated, proceed
      4. IF unresolved_questions is NON-EMPTY:
         IF process_preference.interaction_mode == "dao-represent-human-to-interact":
           → Invoke x-ipe-assistant-user-representative-Engineer with specific questions
         ELSE:
           → Present ONLY the specific questions to human
         → Incorporate answers, revise scope
    </action>
    <constraints>
      - MUST NOT ask broad "is this scope correct?" — only ask specific, bounded questions
      - IF self-critique passes with zero questions → skip human/DAO entirely
    </constraints>
    <output>scope_validated</output>
  </step_4>

  <step_5>
    <name>Round 1: Create Meta + Draft</name>
    <requires>skill_type, skill_template_path, skill_meta_template_path, examples[], resources_plan[]</requires>
    <action>
      1. Load skill-meta template from {skill_meta_template_path}
      2. Create skill-meta.md under x-ipe-docs/skill-meta/{skill-name}/ by filling template
      3. Load SKILL.md template from {skill_template_path}
      4. Create candidate/ under x-ipe-docs/skill-meta/{skill-name}/ with full skill structure
      5. Create ALL bundled resources from resources_plan[] inside candidate/:
         - candidate/references/ — all reference files
         - candidate/scripts/ — all script files
         - candidate/templates/ — all template files
    </action>
    <constraints>
      - BLOCKING: Both outputs must complete before Round 2
      - BLOCKING: skill-meta.md MUST be created from template, not from scratch
      - BLOCKING: SKILL.md MUST be created from template, not from scratch
      - BLOCKING: ALL bundled resources (references/, scripts/, templates/) MUST be created inside candidate/ — never directly in .github/skills/{skill-name}/
      - MANDATORY: All internal markdown links in generated skill files MUST use full project-root-relative paths (e.g., `x-ipe-docs/requirements/EPIC-XXX/specification.md`, `.github/skills/x-ipe-task-based-XXX/SKILL.md`). Do NOT use relative paths like `../` or `./`.
    </constraints>
    <success_criteria>
      - skill-meta.md exists (created from {skill_meta_template_path})
      - candidate/ folder with SKILL.md exists (created from {skill_template_path})
      - All planned resources from resources_plan[] exist inside candidate/
    </success_criteria>
    <output>skill-meta.md, candidate/</output>
  </step_5>

  <step_6>
    <name>Round 2: Reflect + Test Cases</name>
    <requires>skill-meta.md, candidate/</requires>
    <action>
      1. Reflect on candidate against skill-meta using this checklist:
         a. Does skill load all referenced tool skills explicitly? (not guess behavior)
         b. Does it gate optional features via project config (tools.json/.x-ipe.yaml)?
         c. Does it document anti-patterns? (if 3+ steps) Limitations? (if external deps)
         d. Are output naming conventions defined? (if skill produces files)
         e. Were lessons from related skills consulted and applied?
      2. Generate test cases from acceptance criteria
    </action>
    <success_criteria>
      - Candidate refined based on reflection
      - test-cases.yaml created
    </success_criteria>
    <output>candidate/, test-cases.yaml</output>
  </step_6>

  <step_7>
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
  </step_7>

  <step_8>
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
  </step_8>

  <step_9>
    <name>Merge or Iterate</name>
    <requires>evaluation-report.yaml</requires>
    <action>
      1. Check evaluation results
      2. IF must_pass_rate == 100% AND should_pass_rate >= 80%:
         - Validate candidate/ completeness: verify all files referenced by candidate/SKILL.md exist inside candidate/ (references/, scripts/, templates/)
         - IF missing files found: add them to candidate/ before merging
         - cp -r candidate/* .github/skills/{skill-name}/
         - Update skill-version-history.md
         - Proceed to Step 10
      3. IF tests failed AND iteration_count < 3:
         - Update candidate, re-run from Round 2
      4. IF tests failed AND iteration_count >= 3:
         - Escalate to human
    </action>
    <constraints>
      - BLOCKING: Pre-merge validation must confirm candidate/ contains ALL files that will exist in production — no direct writes to .github/skills/{skill-name}/ after merge
    </constraints>
    <success_criteria>
      - Skill merged OR iteration documented
    </success_criteria>
    <output>merge_status</output>
  </step_9>

  <step_10>
    <name>Validate Cross-References</name>
    <requires>merge_status == merged</requires>
    <action>
      1. Verify skill's Output Result YAML declares: category, next_task_based_skill, interaction_mode (x-ipe-task-based only)
      2. Verify skill description contains trigger keywords for auto-discovery (x-ipe-task-based only)
      3. Verify bidirectional references
      4. Verify Input Initialization subsection exists under Input Parameters with <input_init> XML block
      5. Verify DoR ≤ 5 checkpoints AND DoD ≤ 10 checkpoints. If over, trim to most critical checks.
    </action>
    <constraints>
      - MANDATORY: Task-based skills must declare category, next_task_based_skill, interaction_mode in Output Result for auto-discovery
      - CRITICAL: DoR ≤ 5 checkpoints, DoD ≤ 10 checkpoints
    </constraints>
    <success_criteria>
      - Cross-references validated
    </success_criteria>
    <output>cross_references_valid</output>
  </step_10>

  <sub-agent-planning>
    <!-- Constraint: One step = one sub-agent; one sub-agent = many steps -->
    <sub_agent_1>
      <sub_agent_definition>
        <role>Meta & Draft Creator</role>
        <prompt>Load skill-meta template from {skill_meta_template_path} and SKILL.md template from {skill_template_path}. Fill both with skill-specific content. Output: x-ipe-docs/skill-meta/{skill-name}/skill-meta.md and x-ipe-docs/skill-meta/{skill-name}/candidate/</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_5</workflow_step_reference>
    </sub_agent_1>
    <sub_agent_2>
      <sub_agent_definition>
        <role>Reflector & Test Generator</role>
        <prompt>Review candidate against skill-meta, identify gaps, suggest improvements. Then generate test-cases.yaml from acceptance criteria in skill-meta.md</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_6</workflow_step_reference>
      <starting_condition>
        - "START after sub_agent_1 completes"
      </starting_condition>
    </sub_agent_2>
    <sub_agent_3>
      <sub_agent_definition>
        <role>Test Runner</role>
        <prompt>Execute test cases in sandbox, record outputs and execution log</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_7</workflow_step_reference>
      <starting_condition>
        - "START after sub_agent_2 completes"
      </starting_condition>
    </sub_agent_3>
    <sub_agent_4>
      <sub_agent_definition>
        <role>Evaluator</role>
        <prompt>Evaluate sandbox outputs against expectations, generate evaluation-report.yaml</prompt>
      </sub_agent_definition>
      <workflow_step_reference>step_8</workflow_step_reference>
      <starting_condition>
        - "START after sub_agent_3 completes"
      </starting_condition>
    </sub_agent_4>
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
  <checkpoint required="true">
    <name>Planning Complete</name>
    <verification>skill_type, template_path, examples[], resources_plan[] defined; skill-meta.md created from template</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Candidate Created</name>
    <verification>candidate/SKILL.md + all bundled resources (references/, scripts/, templates/) exist in candidate/</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Validation Passed</name>
    <verification>test-cases.yaml created, sandbox executed, evaluation passed (must_pass=100%, should_pass>=80%)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Merged with Parity</name>
    <verification>Skill merged to .github/skills/{skill-name}/ AND every production file has corresponding candidate/ file</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>SKILL.md Structure Valid</name>
    <verification>Frontmatter valid (name + triggers), section order correct, keywords used, line count under limit (500; 600 for x-ipe-tool)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>DoR/DoD Within Limits</name>
    <verification>Created skill has DoR at most 5 and DoD at most 10 checkpoints</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Step Outputs Covered</name>
    <verification>Every step output in created skill has a corresponding DoD checkpoint</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Cross-References Valid</name>
    <verification>Auto-discovery fields in Output Result (if task-based), Input Initialization present, bidirectional refs verified</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Input Initialization Present</name>
    <verification>Skills with non-trivial input resolution have Input Initialization subsection with input_init block</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Examples Documented</name>
    <verification>references/examples.md exists with concrete usage scenarios</verification>
  </checkpoint>
</definition_of_done>
```

---

## Templates

| Template | Purpose |
|----------|---------|
| [x-ipe-task-based.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-task-based.md) | SKILL.md for task-based skills |
| [x-ipe-tool.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-tool.md) | SKILL.md for tool skills |
| [x-ipe-workflow-orchestration.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-workflow-orchestration.md) | SKILL.md for workflow/task-category skills |
| [x-ipe-meta.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-meta.md) | SKILL.md for meta skills |
| [x-ipe-dao.md](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-dao.md) | SKILL.md for human representative skills (x-ipe-dao type) |
| [skill-meta-x-ipe-task-based.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-task-based.md) | skill-meta for task-based/workflow skills |
| [skill-meta-x-ipe-tool.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-tool.md) | skill-meta for tool skills |
| [skill-meta-x-ipe-task-category.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-task-category.md) | skill-meta for task-category skills |
| [skill-meta-x-ipe-meta.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-meta.md) | skill-meta for meta skills |
| [skill-meta-x-ipe-dao.md](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-dao.md) | skill-meta for human representative skills (x-ipe-dao type) |

BLOCKING: Always use the appropriate template. Never create SKILL.md or skill-meta.md from scratch.

---

## References

| File | Purpose |
|------|---------|
| [skill-general-guidelines-v2.md](.github/skills/x-ipe-meta-skill-creator/references/skill-general-guidelines-v2.md) | Core principles, patterns, standards |
| [2-10. reference/example files](.github/skills/x-ipe-meta-skill-creator/references) | Section ordering, workflow patterns, DoR/DoD, gates, task IO |
| [11. reference-quality-standards.md](.github/skills/x-ipe-meta-skill-creator/references/11. reference-quality-standards.md) | Quality standards |
| [12. reference-production-patterns.md](.github/skills/x-ipe-meta-skill-creator/references/12.%20reference-production-patterns.md) | Production patterns, lessons, config gating |
| [skill-type-comparison.md](.github/skills/x-ipe-meta-skill-creator/references/skill-type-comparison.md) | Detailed comparison of all 8 skill types |
| [examples.md](.github/skills/x-ipe-meta-skill-creator/references/examples.md) | Concrete execution examples |

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| `x-ipe-meta-lesson-learned` | Capture issues and feedback after skill execution |
