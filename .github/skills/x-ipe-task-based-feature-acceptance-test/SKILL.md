---
name: x-ipe-task-based-feature-acceptance-test
description: Execute acceptance tests for all feature types (frontend UI, backend API, CLI, library). Generates test cases from specification acceptance criteria, classifies by test type, and routes execution to the best available tool (Chrome DevTools MCP for UI, tool skills for backend/unit). Use after Code Implementation. Triggers on requests like "run acceptance tests", "test feature", "execute acceptance tests".
---

# Task-Based Skill: Feature Acceptance Test

## Purpose

Execute acceptance tests for features by:
1. Loading toolbox config to determine available testing tools
2. Classifying ALL acceptance criteria by test type (frontend-ui, backend-api, unit, integration)
3. Generating test case plan from specification criteria
4. Analyzing implementation to design precise test steps
5. Routing test execution to the best tool per test type
6. Reporting test results

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

**BLOCKING: Single Feature Only.** This skill operates on exactly ONE feature at a time. Do NOT batch or combine multiple features in a single execution. If multiple features need processing, run this skill separately for each feature.

**Workflow Mode:** When `execution_mode == "workflow-mode"`, the completion step MUST call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with `workflow_name` from `workflow.name` input, `action` from `workflow.action` input, `status: "done"`, and a `deliverables` keyed dict using ONLY the extract tags defined in `workflow-template.json` for this action (format: `{"tag-name": "path/to/file"}`). Do NOT pass a flat list of file paths. Verify the workflow state was updated before marking the task complete.

CRITICAL: Only use testing tools that are explicitly enabled (`true`) in `x-ipe-docs/config/tools.json` under `stages.quality.testing`. Only `true` counts as enabled — `false`, absent, or any other value means DISABLED. The tools.json config is the single source of truth for which tools are allowed.

MANDATORY: For frontend-ui tests, Chrome DevTools MCP is required. If `chrome-devtools-mcp` is disabled in tools.json or MCP is not available, generate test cases but mark UI test execution as blocked.

MANDATORY: Chrome must be launched with `--user-data-dir` (dedicated profile) or the chrome-devtools-mcp server must be configured with `--user-data-dir` or `--isolated=true` to avoid conflicts with existing Chrome sessions.

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer.

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
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

  # Required inputs
  feature_id: "{FEATURE-XXX}"       # Required (feature-stage) OR Optional (standalone)
  target_url: "{URL}"               # Required for UI tests; from feature dev server config or human input

  # Config
  toolbox_meta_path: "x-ipe-docs/config/tools.json"

  # Context (from previous task or project)
  specification_link: "x-ipe-docs/requirements/FEATURE-XXX/specification.md"
  mockup_link: "{path | N/A}"       # Derived from specification's Linked Mockups section; N/A if outdated or missing
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
  <field name="target_url" source="IF frontend-ui tests exist, resolve from feature's dev server config; IF standalone, from human input; IF no UI tests, N/A" />
  <field name="toolbox_meta_path" source="default: x-ipe-docs/config/tools.json" />
  <field name="specification_link" source="IF workflow mode AND extra_context_reference.specification is a path → use it; ELSE → x-ipe-docs/requirements/{feature_id}/specification.md" />
  <field name="technical_design_link" source="IF workflow mode AND extra_context_reference.impl-files is a path → use it; ELSE → x-ipe-docs/requirements/{feature_id}/technical-design.md" />
  <field name="mockup_link">
    <steps>
      1. READ specification at specification_link, find "Linked Mockups" section
      2. IF mockup found AND Linked Date >= latest spec/design update → set mockup_link = "{path}"
      3. ELSE (no mockup, missing section, or Linked Date outdated) → set mockup_link = "N/A"
    </steps>
  </field>
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
    <name>Code implementation is complete</name>
    <verification>Feature code merged and deployable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Specification with acceptance criteria exists</name>
    <verification>Read specification.md, confirm AC-X entries present</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Toolbox config accessible</name>
    <verification>x-ipe-docs/config/tools.json readable with stages.quality.testing section</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 Load Toolbox, 1.2 Generate Plan | Load tools config, classify ACs by type, create test cases | Config loaded, test cases defined |
| 2. 审问之 — Inquire Thoroughly | 2.1 Analyze Implementation, 2.2 Test Data Prep | Extract selectors/endpoints, collect test data | Analysis complete, data collected |
| 3. 慎思之 — Think Carefully | 3.1 Reflect & Refine | Review and validate test cases | Cases validated |
| 4. 明辨之 — Discern Clearly | 4.1 Execute Tests, 4.2 Report Results | Run tests via appropriate tools, document results | Tests complete, results documented |
| 5. 笃行之 — Practice Earnestly | 5.1 Update Workflow Status | Update workflow and complete | Status updated |
| 继续执行 | 6.1 | Decide Next Action | Next action decided |
| 继续执行 | 6.2 | Execute Next Action | Execution started |

BLOCKING: Step 1.1 - tools.json MUST be loaded before test plan generation.
BLOCKING: Step 4.1 - Tests for a given type are blocked if the required tool is disabled in config.

---

## Execution Procedure

```xml
<procedure name="feature-acceptance-test">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">

    <step_1_1>
      <name>Load Toolbox Config</name>
      <action>
        1. CHECK if x-ipe-docs/config/tools.json exists
        2. IF exists: parse JSON, extract tools from stages.quality.testing
        3. IF NOT exists: config_active = false (all tools enabled by default)
        4. Build enabled_tools list — only tools with value `true` count as enabled
        5. Classify enabled tools by capability:
           - frontend_ui_tool: "chrome-devtools-mcp" (browser interaction for UI tests)
           - frontend_ui_skill: "x-ipe-tool-ui-testing-via-chrome-mcp" (structured UI test execution via chrome MCP)
           - code_test_tools: x-ipe-tool-implementation-* (for backend/unit/integration tests)
        6. BLOCKING: For each enabled tool that has a corresponding skill at .github/skills/{tool-name}/SKILL.md, LOAD that skill now
        7. Output enabled_tools list with capability classification
      </action>
      <constraints>
        - BLOCKING: tools.json is the single source of truth; do NOT use disabled tools
      </constraints>
      <output>enabled_tools list with capability classification</output>
    </step_1_1>

    <step_1_2>
      <name>Classify & Generate Acceptance Test Plan</name>
      <action>
        1. READ specification at specification_link (resolved in Input Initialization)
        2. READ technical design at technical_design_link to determine Technical Scope
        3. EXTRACT all acceptance criteria (AC-X) with testable conditions
        4. CLASSIFY each AC by test_type:
           - "frontend-ui": requires browser interaction (UI rendering, clicks, forms, visual)
           - "backend-api": requires HTTP/API calls (endpoints, responses, status codes)
           - "unit": requires code-level testing (functions, classes, logic)
           - "integration": requires multi-component verification (data flow, service interaction)
        5. MATCH each test_type to the best enabled tool:
           - frontend-ui → chrome-devtools-mcp (if enabled)
           - backend-api → matched code_test_tool skill (python/typescript/etc.)
           - unit → matched code_test_tool skill
           - integration → matched code_test_tool skill or chrome-devtools-mcp
        6. DETECT tech_stack from specification and implementation files
        7. SEMANTIC MATCH tech_stack to enabled tool skills (same as code-implementation routing)
        8. CHECK mockup_link (resolved in Input Initialization):
           a. IF mockup_link != "N/A": note mockup available for Step 3.1 and Step 4.1
           b. IF mockup_link == "N/A": proceed without mockup validation
        9. CREATE acceptance-test-cases.md using templates/acceptance-test-cases.md
        10. FOR EACH AC: create TC-XXX, map to AC, set priority (P0/P1/P2), set test_type, assign tool, write steps, define expected outcomes
        11. PRIORITIZE: P0=Critical, P1=High, P2=Medium (edge cases)
        12. GROUP and STORE test cases by test_type in acceptance-test-cases.md:
            - Create a section per test_type: "## Frontend-UI Tests", "## Backend-API Tests", "## Unit Tests", "## Integration Tests"
            - Each section lists only TCs of that type with their assigned tool
            - This grouping enables batch execution per type in Phase 4
      </action>
      <constraints>
        - MANDATORY: Each AC must have at least one test case regardless of type
        - CRITICAL: Test cases must be independent and self-contained
        - MANDATORY: Each TC must declare its test_type and assigned_tool
      </constraints>
      <output>acceptance-test-cases.md with typed test cases and tool assignments</output>
    </step_1_2>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">

    <step_2_1>
      <name>Analyze Implementation</name>
      <action>
        FOR EACH test_type group (see references/detailed-procedures.md for per-type analysis patterns):
        1. frontend-ui: Locate UI files, identify selectors (priority: data-testid > id > aria-label > class), update test steps
        2. backend-api: Locate route files, document endpoint/method/schema, update test steps with API details
        3. unit: Locate source modules, document function signatures/inputs/expected outputs
        4. integration: Locate service interaction points, document setup/trigger/verification
      </action>
      <constraints>
        - CRITICAL: For frontend-ui, use selector priority order from references/detailed-procedures.md
        - BLOCKING: Never use auto-generated IDs or fragile class chains
      </constraints>
      <output>Test cases updated with implementation-specific details per type</output>
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
        1. FOR EACH test case, validate: AC coverage, preconditions, actionable steps, measurable expected results, edge cases
        2. FOR frontend-ui tests: validate selector existence, add wait conditions, handle dynamic content
        3. FOR backend-api tests: validate endpoint existence, check error cases (4xx, 5xx), auth requirements
        4. FOR unit tests: validate function signatures, check boundary conditions
        5. REFLECT: false negative risks, missing steps, vague expectations, split candidates
        6. IF mockup_link != "N/A" (frontend-ui only):
           a. ADD UI/UX visual validation TCs (P1): layout, styling, interactive states
           b. Reference mockup_link in each TC description
        7. ROUTE TEST CODE GENERATION (if matched_tool_skill from Step 1.1):
           a. CONVERT refined test cases to AAA scenarios (per test_type group)
           b. INVOKE matched_tool_skill with operation: "implement", aaa_scenarios, feature_context
           c. Tool skill generates test scaffolding using language-specific conventions
           d. IF no matched tool skill → fall back to inline test generation
        8. UPDATE acceptance-test-cases.md with refinements
      </action>
      <constraints>
        - MANDATORY: Every test case must pass reflection checklist (see references/detailed-procedures.md)
        - MANDATORY: All internal markdown links MUST use full project-root-relative paths
      </constraints>
      <output>Refined test cases with implementation-specific test code</output>
    </step_3_1>

  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">

    <step_4_1>
      <name>Execute Tests</name>
      <action>
        GROUP test cases by test_type and assigned_tool. FOR EACH group:

        1. frontend-ui (x-ipe-tool-ui-testing-via-chrome-mcp):
           - CHECK if "x-ipe-tool-ui-testing-via-chrome-mcp" is enabled in tools.json
           - IF enabled AND chrome-devtools-mcp is available:
             a. LOAD skill x-ipe-tool-ui-testing-via-chrome-mcp (if not already loaded in Step 1.1)
             b. INVOKE the skill's execute_ui_tests operation with:
                - test_cases: all frontend-ui TCs from the grouped test plan
                - target_url: {from input}
                - mockup_link: {from input, resolved in Input Initialization}
                - screenshot_on_failure: true
                - screenshot_dir: x-ipe-docs/requirements/{feature_id}/screenshots/
             c. COLLECT per-TC results from the tool skill's operation_output
           - ELIF chrome-devtools-mcp enabled but skill NOT enabled: fall back to direct MCP
           - ELSE: SET group status="blocked"

        2. backend-api (tool skill):
           - Make API calls (curl, httpx, fetch, or test framework), verify response status/body/headers

        3. unit (tool skill):
           - Run unit tests via matched tool skill or test runner (pytest, vitest, etc.)

        4. integration (tool skill or chrome-devtools-mcp):
           - Initialize services, trigger flow, verify end-to-end state

        See references/detailed-procedures.md for command patterns per type.
        5. CONTINUE with remaining tests even if some fail
      </action>
      <output>Test execution results per test case, grouped by type</output>
    </step_4_1>

    <step_4_2>
      <name>Report Test Results</name>
      <action>
        1. UPDATE acceptance-test-cases.md: set status per test case, add execution notes, fill Execution Results
        2. DOCUMENT failures with reason and recommended action
        3. IF mockup_comparison returned by UI tool: add "Mockup Comparison Summary" with gaps and match_score
        4. GROUP results by test_type in summary (frontend-ui / backend-api / unit / integration: X passed / Y total)
        5. CALCULATE metrics: total, passed, failed, blocked, pass_rate
        6. RETURN task completion output with results
      </action>
      <success_criteria>
        - All test cases have a status recorded
        - Metrics calculated and documented
        - acceptance-test-cases.md saved to feature folder
      </success_criteria>
      <output>Completed acceptance-test-cases.md with execution results</output>
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
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-code-refactor"
      condition: "Refactor code for quality improvements"
  process_preference:
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"
  workflow_action_updated: true | false
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/acceptance-test-cases.md"

  # Feature-stage specific
  feature_id: "FEATURE-XXX"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Acceptance Testing"

  # Acceptance test results
  test_types_tested: ["frontend-ui", "backend-api", "unit", "integration"]
  test_cases_created: "{count}"
  tests_passed: "{count}"
  tests_failed: "{count}"
  tests_blocked: "{count}"
  pass_rate: "{X}%"
  results_by_type: { frontend_ui: {passed, failed, blocked}, backend_api: {...}, unit: {...}, integration: {...} }
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Toolbox config loaded</name>
    <verification>Step 1.1 completed — enabled_tools list built from tools.json stages.quality.testing</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All ACs classified and test cases created</name>
    <verification>acceptance-test-cases.md exists with TC mapped to AC, each TC has test_type and assigned_tool</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Implementation analyzed per test type</name>
    <verification>Frontend-ui tests have selectors; backend-api tests have endpoints; unit tests have function refs</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test cases reflected and refined</name>
    <verification>Reflection checklist passed for each TC</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tests executed or marked blocked per type</name>
    <verification>Each TC has Pass/Fail/Blocked status; blocked only if required tool disabled/unavailable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test results documented with per-type breakdown</name>
    <verification>Execution Results section has overall metrics and results_by_type summary</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>acceptance-test-cases.md saved to feature folder</name>
    <verification>File exists at x-ipe-docs/requirements/FEATURE-XXX/acceptance-test-cases.md</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Workflow Action Updated</name>
    <verification>If execution_mode == "workflow-mode", called update_workflow_action with status "done"</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

| Pattern | When | Then |
|---------|------|------|
| Multi-Type Feature | Feature has both UI and API | Classify each AC separately, run UI via tool skill, API via code tool |
| Backend-Only Feature | No frontend component | ALL tests route to code tool skills |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip non-UI ACs | Incomplete coverage | Test ALL ACs regardless of type |
| Use disabled tools | Violates config | Only use tools enabled in tools.json |
| Test without selectors | Fail to find elements | Analyze HTML first |
| Skip reflection | Miss edge cases | Always reflect on each TC |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-feature-acceptance-test/references/examples.md) for execution examples.
See [references/detailed-procedures.md](.github/skills/x-ipe-task-based-feature-acceptance-test/references/detailed-procedures.md) for selector practices, MCP patterns, and reflection checklist.
