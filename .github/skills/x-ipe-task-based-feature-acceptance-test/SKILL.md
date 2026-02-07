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

CRITICAL: This skill is ONLY for features with web UI. If the feature is backend API only, CLI tool only, or library/SDK only, skip this skill and proceed to Feature Closing.

MANDATORY: This skill requires Chrome DevTools MCP for test execution. If MCP is not available, generate test cases but mark execution as blocked.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Feature Acceptance Test"

  # Task type attributes
  category: "standalone | feature-stage"
  next_task_based_skill: "Feature Closing | null"
  require_human_review: "no"

  # Required inputs
  auto_proceed: false
  feature_id: "{FEATURE-XXX}"       # Required (feature-stage) OR Optional (standalone)
  target_url: "{URL}"               # Required (standalone) OR from feature (feature-stage)

  # Context (from previous task or project)
  specification_link: "x-ipe-docs/requirements/FEATURE-XXX/specification.md"
  technical_design_link: "x-ipe-docs/requirements/FEATURE-XXX/technical-design.md"
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

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Check UI Scope | Determine if feature has web UI | Has web UI OR skip |
| 2 | Generate Plan | Create test cases from acceptance criteria | Test cases defined |
| 3 | Analyze HTML | Extract element selectors from UI code | Selectors identified |
| 4 | Test Data Prep | Ask user for test data (if auto_proceed=false) | Data collected OR skipped |
| 5 | Reflect & Refine | Review and update test cases | Cases validated |
| 6 | Execute Tests | Run tests via Chrome DevTools MCP | Tests complete |
| 7 | Report Results | Document test results and metrics | Results documented |

BLOCKING: Step 1 - If no web UI, output status=skipped and proceed to next_task_based_skill.
BLOCKING: Step 4 - If auto_proceed=true, skip this step and use placeholder/generated data.
BLOCKING: Step 6 - If MCP unavailable, output status=blocked; test cases ready for manual execution.

---

## Execution Procedure

```xml
<procedure name="feature-acceptance-test">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Check UI Scope</name>
    <action>
      1. QUERY feature board for feature_id, specification_link, technical_design_link
      2. READ technical design, check "Technical Scope" section
      3. VERIFY feature is accessible (playground/demo URL exists)
    </action>
    <branch>
      IF: scope includes [Frontend] OR [Full Stack]
      THEN: Proceed to Step 2
      ELSE: SET status="skipped", skip_reason="No web UI", RETURN next_task_based_skill=Feature Closing
    </branch>
    <output>Decision to proceed or skip</output>
  </step_1>

  <step_2>
    <name>Generate Acceptance Test Plan</name>
    <action>
      1. READ specification.md at x-ipe-docs/requirements/FEATURE-XXX/specification.md
      2. EXTRACT all acceptance criteria (AC-X) with testable conditions
      3. CREATE acceptance-test-cases.md using templates/acceptance-test-cases.md
      4. FOR EACH acceptance criterion: create test case (TC-XXX), map to AC, set priority (P0/P1/P2), write high-level steps, define expected outcomes
      5. PRIORITIZE: P0=Critical (must pass), P1=High (should pass), P2=Medium (edge cases)
    </action>
    <constraints>
      - MANDATORY: Each AC must have at least one test case
      - CRITICAL: Test cases must be independent and self-contained
    </constraints>
    <output>Initial acceptance-test-cases.md with test case outlines</output>
  </step_2>

  <step_3>
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
  </step_3>

  <step_4>
    <name>Test Data Preparation</name>
    <action>
      1. ANALYZE each test case for data requirements (Input, Selection, Expected, Compare)
      2. ASK user for test data per test case
      3. UPDATE Test Data table in each test case section
    </action>
    <branch>
      IF: auto_proceed = true
      THEN: SKIP this step, use placeholder/generated test data
      ELSE: PAUSE and collect test data from user (see references/detailed-procedures.md)
    </branch>
    <output>Test Data tables populated in each test case</output>
  </step_4>

  <step_5>
    <name>Reflect and Refine Test Cases</name>
    <action>
      1. FOR EACH test case, validate: AC coverage, preconditions, actionable steps, selector existence, measurable expected results, edge cases
      2. REFLECT: false negative risks, missing steps, vague expectations, split candidates
      3. REFINE: add missing steps, clarify results, add wait conditions, handle dynamic content
      4. UPDATE acceptance-test-cases.md with refinements
    </action>
    <constraints>
      - MANDATORY: Every test case must pass reflection checklist (see references/detailed-procedures.md)
    </constraints>
    <output>Refined and validated test cases</output>
  </step_5>

  <step_6>
    <name>Execute Tests via Chrome DevTools MCP</name>
    <action>
      1. CHECK MCP availability
      2. FOR EACH test case (ordered by priority):
         a. SETUP: Navigate to test URL, verify page loaded
         b. EXECUTE: Perform each action via MCP, capture results, screenshot on failure
         c. VERIFY: Check element states, validate text content, confirm UI changes
         d. RECORD: Status (Pass/Fail/Blocked), execution time, failure reason, screenshot link
      3. CONTINUE with remaining tests even if some fail
    </action>
    <branch>
      IF: Chrome DevTools MCP available
      THEN: Execute tests via MCP (see references/detailed-procedures.md for command patterns)
      ELSE: SET status="blocked", document "Test cases ready for manual execution"
    </branch>
    <output>Test execution results per test case</output>
  </step_6>

  <step_7>
    <name>Report Test Results</name>
    <action>
      1. UPDATE acceptance-test-cases.md: set status per test case (Pass/Fail/Not Run), add execution notes, fill Execution Results section
      2. DOCUMENT failures with reason and recommended action
      3. CALCULATE metrics: total, passed, failed, blocked, pass_rate = (passed/total)*100
      4. RETURN task completion output with results
    </action>
    <success_criteria>
      - All test cases have a status recorded
      - Metrics calculated and documented
      - acceptance-test-cases.md saved to feature folder
    </success_criteria>
    <output>Completed acceptance-test-cases.md with execution results</output>
  </step_7>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "{standalone | feature-stage}"
  status: completed | blocked | skipped
  next_task_based_skill: "Feature Closing | null"
  require_human_review: "no"
  auto_proceed: "{from input}"
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
    <verification>Step 1 completed with proceed or skip decision</verification>
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
    <verification>Test Data tables populated (if auto_proceed=false and has UI)</verification>
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
  <checkpoint required="true">
    <name>acceptance-test-cases.md saved to feature folder</name>
    <verification>File exists at x-ipe-docs/requirements/FEATURE-XXX/acceptance-test-cases.md</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Form Submission Test

**When:** Feature includes form input and submission
**Then:**
```
1. Test empty form submission (validation)
2. Test invalid input formats
3. Test valid submission, verify success state
4. Verify success message/redirect
```

### Pattern: CRUD Operations Test

**When:** Feature includes Create/Read/Update/Delete
**Then:**
```
1. Test Create, verify appears in list
2. Test Read, verify data displayed correctly
3. Test Update, verify changes persisted
4. Test Delete, verify removed from list
```

### Pattern: Navigation/Routing Test

**When:** Feature includes page navigation
**Then:**
```
1. Test direct URL access
2. Test navigation via links/buttons
3. Verify correct page renders
4. Test back/forward browser navigation
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Test without selectors | Tests will fail to find elements | Analyze HTML first |
| Skip reflection step | Miss edge cases and errors | Always reflect on each TC |
| Test implementation details | Brittle tests | Test user-visible behavior |
| One massive test | Hard to debug failures | Split into focused tests |
| Ignore async loading | Flaky tests | Add explicit wait steps |
| Hard-coded test data | Hard to maintain | Use variables/fixtures |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples including:
- Standard feature acceptance test flow
- Skipped execution (no web UI)
- Blocked execution (no MCP available)
- Partial test failure handling

See [references/detailed-procedures.md](references/detailed-procedures.md) for:
- Selector best practices and priority order
- MCP command patterns
- Test data collection process
- Reflection checklist
- Result reporting format
