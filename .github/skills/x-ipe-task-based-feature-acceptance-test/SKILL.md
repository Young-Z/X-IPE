---
name: x-ipe-task-based-feature-acceptance-test
description: Execute acceptance tests for features with web UI. Generates test cases from specification acceptance criteria, analyzes HTML for selectors, and runs tests via Chrome DevTools MCP. Use after Code Implementation for features with web UI. Triggers on requests like "run acceptance tests", "test feature UI", "execute acceptance tests".
---

# Task-Based Skill: Feature Acceptance Test

## Purpose

Execute acceptance tests for web UI features by:
1. Checking if feature has web UI component (skip if backend-only)
2. Generating acceptance test case plan from specification criteria
3. Analyzing HTML to design precise test steps with selectors
4. Reflecting and refining test cases for completeness
5. Executing tests via Chrome DevTools MCP
6. Reporting test results

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

**BLOCKING: Single Feature Only.** This skill operates on exactly ONE feature at a time. Do NOT batch or combine multiple features in a single execution. If multiple features need processing, run this skill separately for each feature.

**Workflow Mode:** When `execution_mode == "workflow-mode"`, the completion step MUST call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with `workflow_name` from `workflow.name` input, `action` from `workflow.action` input, `status: "done"`, and a `deliverables` keyed dict using ONLY the extract tags defined in `workflow-template.json` for this action (format: `{"tag-name": "path/to/file"}`). Do NOT pass a flat list of file paths. Verify the workflow state was updated before marking the task complete.

CRITICAL: This skill is ONLY for features with web UI. If the feature is backend API only, CLI tool only, or library/SDK only, skip this skill and proceed to Feature Closing.

MANDATORY: This skill requires Chrome DevTools MCP for test execution. If MCP is not available, generate test cases but mark execution as blocked.

MANDATORY: Chrome must be launched with `--user-data-dir` (dedicated profile) or the chrome-devtools-mcp server must be configured with `--user-data-dir` or `--isolated=true` to avoid conflicts with existing Chrome sessions. Example: `chrome --remote-debugging-port=9222 --user-data-dir=/tmp/x-ipe-chrome-profile` or configure MCP with `--user-data-dir=/tmp/x-ipe-chrome-profile`.

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-feature-acceptance-test"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      specification: "path | N/A | auto-detect"
      impl-files: "path | N/A | auto-detect"

  # Task type attributes
  category: "standalone | feature-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-code-refactor"
      condition: "Refactor code for quality improvements"
    - skill: "x-ipe-task-based-feature-closing"
      condition: "Close feature if acceptance tests pass"
    - skill: "x-ipe-task-based-human-playground"
      condition: "Manual validation before closing"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

  # Required inputs
  feature_id: "{FEATURE-XXX}"       # Required (feature-stage) OR Optional (standalone)
  target_url: "{URL}"               # Required (standalone) OR from feature (feature-stage)

  # Context (from previous task or project)
  specification_link: "x-ipe-docs/requirements/FEATURE-XXX/specification.md"
  technical_design_link: "x-ipe-docs/requirements/FEATURE-XXX/technical-design.md"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="feature_id" source="from previous task output or task board or human input" />
  <field name="target_url" source="IF feature-stage, resolve from feature's dev server config; IF standalone, from human input" />
  <field name="specification_link" source="auto-detect from x-ipe-docs/requirements/{feature_id}/specification.md" />
  <field name="technical_design_link" source="auto-detect from x-ipe-docs/requirements/{feature_id}/technical-design.md" />
  <field name="extra_context_reference" source="from workflow context or auto-detect from feature artifacts" />
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Feature exists on feature board</name>
    <verification>Query feature board for feature_id</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature status is Implemented or Test Generation Complete</name>
    <verification>Check feature board status field</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Code implementation is complete</name>
    <verification>Feature code merged and deployable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Specification with acceptance criteria exists</name>
    <verification>Read specification.md, confirm AC-X entries present</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature is deployed and accessible via URL</name>
    <verification>Navigate to target URL, confirm page loads</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 Check UI Scope, 1.2 Generate Plan | Determine UI scope, create test cases from ACs | Has web UI, test cases defined |
| 2. 审问之 — Inquire Thoroughly | 2.1 Analyze HTML, 2.2 Test Data Prep | Extract selectors, collect test data | Selectors identified, data collected |
| 3. 慎思之 — Think Carefully | 3.1 Reflect & Refine | Review and validate test cases | Cases validated |
| 4. 明辨之 — Discern Clearly | 4.1 Execute Tests, 4.2 Report Results | Run tests via MCP, document results | Tests complete, results documented |
| 5. 笃行之 — Practice Earnestly | 5.1 Update Workflow Status | Update workflow and complete | Status updated |
| 继续执行 | 6.1 | Decide Next Action | Next action decided |
| 继续执行 | 6.2 | Execute Next Action | Execution started |

BLOCKING: Step 1.1 - If no web UI, output status=skipped and proceed to next_task_based_skill.
BLOCKING: Step 2.2 - If process_preference.interaction_mode=="auto", skip and use placeholder/generated data.
BLOCKING: Step 4.1 - If MCP unavailable, output status=blocked; test cases ready for manual execution.

---

## Execution Procedure

```xml
<procedure name="feature-acceptance-test">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">

    <step_1_1>
      <name>Check UI Scope</name>
      <action>
        1. QUERY feature board for feature_id, specification_link, technical_design_link
        2. READ technical design, check "Technical Scope" section
        3. VERIFY feature is accessible (playground/demo URL exists)
        4. IF scope does NOT include [Frontend] or [Full Stack]:
           SET status="skipped", skip_reason="No web UI", RETURN next_task_based_skill=x-ipe-task-based-code-refactor
      </action>
      <output>Decision to proceed or skip</output>
    </step_1_1>

    <step_1_2>
      <name>Generate Acceptance Test Plan</name>
      <action>
        0. Resolve extra_context_reference inputs:
           - FOR EACH ref in [specification, impl-files]:
             IF workflow mode AND extra_context_reference.{ref} is a file path → READ the file
             ELIF "auto-detect" → use existing discovery logic below
             ELIF "N/A" → skip; ELSE (free-mode/absent) → use existing behavior
        1. DETECT tech_stack from specification and implementation files
        2. TOOL SKILL ROUTING (config-filtered):
           a. DISCOVER: Scan .github/skills/x-ipe-tool-implementation-*/
           b. READ CONFIG: Read x-ipe-docs/config/tools.json → stages.quality.testing
              - IF section missing/empty → config_active = false (all tools enabled)
              - ELSE → config_active = true (opt-in); force-enable general
           c. FILTER: IF config_active → only ENABLED tools participate
           d. SEMANTIC MATCH: Match tech_stack to enabled tool skill
           e. STORE matched_tool_skill for use in Step 3.1
        3. READ specification.md at x-ipe-docs/requirements/FEATURE-XXX/specification.md
        4. EXTRACT all acceptance criteria (AC-X) with testable conditions
        5. CHECK Linked Mockups section:
           a. IF current mockups: READ from mockups/, note for Step 3.1
           b. IF outdated: FLAG for human, do NOT generate mockup test cases
           c. IF no mockups: proceed without mockup validation
        6. CREATE acceptance-test-cases.md using templates/acceptance-test-cases.md
        7. FOR EACH AC: create TC-XXX, map to AC, set priority (P0/P1/P2), write steps, define expected outcomes
        8. PRIORITIZE: P0=Critical, P1=High, P2=Medium (edge cases)
      </action>
      <constraints>
        - MANDATORY: Each AC must have at least one test case
        - CRITICAL: Test cases must be independent and self-contained
      </constraints>
      <output>Initial acceptance-test-cases.md with test case outlines, matched_tool_skill identified</output>
    </step_1_2>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">

    <step_2_1>
      <name>Analyze HTML for Selectors</name>
      <action>
        1. LOCATE UI implementation files (templates, static JS, components)
        2. FOR EACH test case, identify UI elements using selector priority (see references/detailed-procedures.md)
        3. UPDATE test steps with precise selectors in step table format
        4. VERIFY selectors are unique, stable, and descriptive
      </action>
      <constraints>
        - CRITICAL: Use selector priority order: data-testid > id > aria-label > class > CSS path
        - BLOCKING: Never use auto-generated IDs or fragile class chains
      </constraints>
      <output>Test cases updated with element selectors</output>
    </step_2_1>

    <step_2_2>
      <name>Test Data Preparation</name>
      <action>
        1. ANALYZE each test case for data requirements (Input, Selection, Expected, Compare)
        2. Collect test data per test case (see references/detailed-procedures.md)
        3. UPDATE Test Data table in each test case section

        Response source (based on interaction_mode):
        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Use placeholder/generated test data (auto-populate)
        ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
          → Ask human for test data per test case
      </action>
      <output>Test Data tables populated in each test case</output>
    </step_2_2>

  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">

    <step_3_1>
      <name>Reflect and Refine Test Cases</name>
      <action>
        1. FOR EACH test case, validate: AC coverage, preconditions, actionable steps, selector existence, measurable expected results, edge cases
        2. REFLECT: false negative risks, missing steps, vague expectations, split candidates
        3. REFINE: add missing steps, clarify results, add wait conditions, handle dynamic content
        4. IF current mockups identified in Step 1.2:
           a. ADD UI/UX visual validation TCs (P1): layout, styling, interactive states, responsive behavior
           b. Reference specific mockup file in each TC description
           c. Use screenshot comparison during execution (Step 4.1) to validate
        5. ROUTE TEST CODE GENERATION (if matched_tool_skill from Step 1.2):
           a. CONVERT refined test cases to AAA scenarios
           b. INVOKE matched_tool_skill with operation: "implement", aaa_scenarios, feature_context
           c. Tool skill generates test scaffolding using language-specific conventions
           d. IF no matched tool skill → fall back to current inline test generation
           e. Chrome DevTools MCP for browser interaction remains unchanged
        6. UPDATE acceptance-test-cases.md with refinements
      </action>
      <constraints>
        - MANDATORY: Every test case must pass reflection checklist (see references/detailed-procedures.md)
        - MANDATORY: All internal markdown links MUST use full project-root-relative paths
      </constraints>
      <output>Refined test cases with language-specific test code (if tool routed)</output>
    </step_3_1>

  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">

    <step_4_1>
      <name>Execute Tests via Chrome DevTools MCP</name>
      <action>
        1. CHECK Chrome DevTools MCP availability
        2. IF MCP not available: SET status="blocked", document "Test cases ready for manual execution"
        3. ELSE: FOR EACH test case (ordered by priority):
           a. SETUP: Navigate to test URL, verify page loaded (see references/detailed-procedures.md for command patterns)
           b. EXECUTE: Perform each action via MCP, capture results, screenshot on failure
           c. VERIFY: Check element states, validate text content, confirm UI changes
           d. RECORD: Status (Pass/Fail/Blocked), execution time, failure reason, screenshot link
        4. FOR mockup UI/UX validation test cases (if applicable):
           a. Take screenshot of the implemented UI
           b. Open the referenced mockup file side-by-side (or load in separate tab)
           c. Visually compare: layout structure, component placement, colors, spacing, typography
           d. Document deviations: element, mockup expectation, actual implementation, severity (major/minor)
           e. Mark as Pass (matches mockup), Partial (minor deviations), or Fail (major deviations)
        5. CONTINUE with remaining tests even if some fail
      </action>
      <output>Test execution results per test case, including mockup comparison findings</output>
    </step_4_1>

    <step_4_2>
      <name>Report Test Results</name>
      <action>
        1. UPDATE acceptance-test-cases.md: set status per test case (Pass/Fail/Not Run), add execution notes, fill Execution Results section
        2. DOCUMENT failures with reason and recommended action
        3. IF mockup UI/UX validation was performed:
           a. Add "Mockup Validation Summary" section with deviation table
           b. Note which mockup(s) were compared and their status
        4. IF outdated mockups were flagged in Step 1.2:
           a. Add prominent notice: "⚠ Outdated Mockup(s) Detected"
           b. List outdated mockup files and recommend updating them
           c. Inform: "The following mockup(s) are outdated and were NOT used for UI/UX validation: {filenames}. Consider updating mockups to enable visual comparison in future acceptance tests."
              Response source (based on interaction_mode):
              IF process_preference.interaction_mode == "dao-represent-human-to-interact":
                → Log notice via x-ipe-dao-end-user-representative
              ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
                → Inform human directly
        5. CALCULATE metrics: total, passed, failed, blocked, pass_rate = (passed/total)*100
        6. RETURN task completion output with results
      </action>
      <success_criteria>
        - All test cases have a status recorded
        - Metrics calculated and documented
        - acceptance-test-cases.md saved to feature folder
        - Outdated mockups flagged to human (if any)
      </success_criteria>
      <output>Completed acceptance-test-cases.md with execution results and mockup validation</output>
    </step_4_2>

  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">

    <step_5_1>
      <name>Update Workflow Status</name>
      <action>
        1. IF execution_mode == "workflow-mode":
           a. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with:
              - workflow_name: {from context}
              - action: {workflow.action}
              - status: "done"
              - feature_id: {feature_id}
              - deliverables: {"test-report": "{path to acceptance-test-cases.md}", "test-folder": "{path to test folder}"}
           b. Log: "Workflow action status updated to done"
      </action>
      <output>workflow_action_updated</output>
    </step_5_1>

  </phase_5>

  <phase_6 name="继续执行（Continue Execute）">
    <step_6_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Invoke x-ipe-dao-end-user-representative with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the context and full output to decide best next action."
          → DAO studies the complete context and decides the best next action
        ELSE (interact-with-human):
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
        Based on the decision from Step 6.1:
        1. Load the target task-based skill's SKILL.md
        2. Generate an execution plan from the skill's Execution Flow table
        3. Start execution from the skill's first phase/step
      </action>
      <constraints>
        - MUST load the skill before executing — do not skip skill loading
        - Execution follows the target skill's procedure, not this skill's
      </constraints>
      <output>Next task execution started</output>
    </step_6_2>
  </phase_6>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "{standalone | feature-stage}"
  status: completed | blocked | skipped
  next_task_based_skill:
    - skill: "x-ipe-task-based-code-refactor"
      condition: "Refactor code for quality improvements"
    - skill: "x-ipe-task-based-feature-closing"
      condition: "Close feature if acceptance tests pass"
    - skill: "x-ipe-task-based-human-playground"
      condition: "Manual validation before closing"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"   # triggers workflow status update when execution_mode == workflow-mode
  workflow_action_updated: true | false # true if update_workflow_action was called
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/acceptance-test-cases.md"

  # Feature-stage specific (only if category=feature-stage)
  feature_id: "FEATURE-XXX"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Acceptance Testing"

  # Acceptance test results
  skip_reason: "No web UI | null"
  test_cases_created: "{count}"
  tests_passed: "{count}"
  tests_failed: "{count}"
  pass_rate: "{X}%"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Feature checked for web UI scope</name>
    <verification>Step 1.1 completed with proceed or skip decision</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Acceptance test cases created from ACs</name>
    <verification>acceptance-test-cases.md exists with TC mapped to AC (if has UI)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>HTML analyzed for element selectors</name>
    <verification>Test steps contain valid CSS selectors (if has UI)</verification>
  </checkpoint>
  <checkpoint required="conditional">
    <name>Test data collected from user</name>
    <verification>Test Data tables populated (if process_preference.interaction_mode=="manual" and has UI)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test cases reflected and refined</name>
    <verification>Reflection checklist passed for each TC (if has UI)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tests executed via MCP or marked blocked</name>
    <verification>Each TC has Pass/Fail/Blocked status (if has UI)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test results documented</name>
    <verification>Execution Results section complete with metrics (if has UI)</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Mockup UI/UX validation performed</name>
    <verification>If current mockups exist, visual validation test cases executed and deviations documented; if outdated mockups found, human notified</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>acceptance-test-cases.md saved to feature folder</name>
    <verification>File exists at x-ipe-docs/requirements/FEATURE-XXX/acceptance-test-cases.md</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Workflow Action Updated</name>
    <verification>If execution_mode == "workflow-mode", called the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with status "done" and deliverables keyed dict</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

| Pattern | When | Then |
|---------|------|------|
| Form Submission | Form input/submission | Test empty (validation), invalid formats, valid submission, success state |
| CRUD Operations | Create/Read/Update/Delete | Test Create→list, Read→display, Update→persist, Delete→remove |
| Navigation/Routing | Page navigation | Test direct URL, link/button nav, correct render, back/forward |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Test without selectors | Fail to find elements | Analyze HTML first |
| Skip reflection step | Miss edge cases | Always reflect on each TC |
| Test implementation details | Brittle tests | Test user-visible behavior |
| One massive test | Hard to debug | Split into focused tests |
| Ignore async loading | Flaky tests | Add explicit wait steps |
| Hard-coded test data | Hard to maintain | Use variables/fixtures |
| Skip mockup comparison | UI drifts from design | Validate against current mockups |
| Use outdated mockup | False failures | Flag outdated mockups to human |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-feature-acceptance-test/references/examples.md) for execution examples.
See [references/detailed-procedures.md](.github/skills/x-ipe-task-based-feature-acceptance-test/references/detailed-procedures.md) for selector practices, MCP patterns, and reflection checklist.
