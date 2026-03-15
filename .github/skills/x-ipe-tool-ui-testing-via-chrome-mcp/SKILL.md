---
name: x-ipe-tool-ui-testing-via-chrome-mcp
description: Execute frontend-ui acceptance test cases via Chrome DevTools MCP following UI testing best practices (selector strategy, wait patterns, screenshot-on-failure, grouped execution). Use when running browser-based UI tests. Triggers on requests like "run UI tests via chrome", "execute frontend-ui tests", "browser test via chrome devtools".
---

> **⚠️ CRITICAL RULE FOR AI AGENTS EXECUTING SUGGESTED SKILLS:**
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.

# Tool Skill: UI Testing via Chrome MCP

## Purpose

AI Agents follow this skill to execute frontend-ui acceptance test cases via Chrome DevTools MCP:
1. Navigate to the application under test
2. Execute test steps using Chrome DevTools MCP tools (snapshot, click, fill, wait, assert)
3. Verify expected outcomes against actual page state
4. Capture screenshots on failure
5. Report per-TC pass/fail results with summary metrics

---

## Important Notes

BLOCKING: Chrome DevTools MCP must be available and connected before invoking this skill. If unavailable, return all TCs as `blocked`.

CRITICAL: Use the **selector priority order**: `data-testid` > `id` > `aria-label` > CSS selector. Never use auto-generated IDs or fragile class chains.

CRITICAL: Always `take_snapshot` after navigation and after each significant action to get fresh element UIDs. Snapshot UIDs are invalidated by page mutations.

MANDATORY: Continue executing remaining test cases even if one fails. Never abort the batch on a single failure.

---

## About

This tool skill encapsulates UI testing best practices for executing acceptance test cases through Chrome DevTools MCP. It is called by `x-ipe-task-based-feature-acceptance-test` to run the `frontend-ui` classified test cases.

**Key Concepts:**
- **Test Case (TC)** — A single acceptance test with steps and expected outcomes
- **Snapshot** — A text representation of the page's accessibility tree, providing element UIDs for interaction
- **Selector Strategy** — Prioritized approach: `data-testid` > `id` > `aria-label` > CSS selector
- **Wait Pattern** — Using `wait_for` with text assertions before interacting, to handle async loading
- **Screenshot-on-Failure** — Capturing visual evidence when a test fails

---

## When to Use

```yaml
triggers:
  - "run UI tests via chrome"
  - "execute frontend-ui acceptance tests"
  - "browser test via chrome devtools"
  - "UI testing via chrome MCP"

not_for:
  - "backend-api tests: use x-ipe-tool-implementation-* skills"
  - "unit/integration tests: use language-specific tool skills"
  - "test case generation: handled by x-ipe-task-based-feature-acceptance-test"
```

---

## Input Parameters

```yaml
input:
  operation: "execute_ui_tests"

  # Required
  test_cases:               # Array of frontend-ui TC objects
    - id: "TC-XXX"
      title: "{test title}"
      ac_ref: "AC-XXX"      # Which acceptance criterion this tests
      steps:                 # Ordered test steps
        - action: "navigate | click | fill | select | wait | assert_visible | assert_text | assert_not_visible | screenshot"
          target: "{selector or URL or text}"
          value: "{input value, if applicable}"
          description: "{human-readable step description}"
      expected_results:
        - "{expected outcome 1}"
        - "{expected outcome 2}"

  target_url: "{base URL}"  # e.g., http://localhost:5001

  # Optional
  screenshot_on_failure: true
  screenshot_dir: "x-ipe-docs/requirements/{feature_id}/screenshots/"
  wait_timeout_ms: 5000
  viewport: null             # e.g., "1280x720" or null for default
  mockup_link: "N/A"          # Path to mockup HTML file; if provided, compare actual UI against mockup
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies 'execute_ui_tests'" />
  <field name="test_cases" source="From acceptance-test-cases.md, filtered to test_type='frontend-ui'" />
  <field name="target_url" source="From feature dev server config or caller input" />
  <field name="screenshot_on_failure" source="Default true; caller may override" />
  <field name="screenshot_dir" source="Default: x-ipe-docs/requirements/{feature_id}/screenshots/" />
  <field name="wait_timeout_ms" source="Default 5000; caller may override" />
  <field name="viewport" source="Default null (browser default); caller may set for responsive testing" />
  <field name="mockup_link" source="From AC skill input (derived from specification's Linked Mockups); 'N/A' if no mockup or outdated" />
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Chrome DevTools MCP available</name>
    <verification>Chrome MCP tools (navigate_page, take_snapshot, click, fill, wait_for, take_screenshot) are accessible</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test cases provided</name>
    <verification>test_cases array is non-empty, each TC has id, steps[], expected_results[]</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Target URL reachable</name>
    <verification>target_url responds to HTTP request (app is running)</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: execute_ui_tests

**When:** Caller has a set of frontend-ui test cases ready for browser execution.

```xml
<operation name="execute_ui_tests">
  <action>
    1. INITIALIZE results array and summary counters (passed=0, failed=0, blocked=0)
    2. IF viewport is set: call emulate with viewport dimensions
    3. VERIFY app reachable: navigate_page to target_url
       - IF navigation fails: mark ALL TCs as "blocked" with reason "UI_APP_UNREACHABLE", RETURN
       - take_snapshot to confirm page loaded

    4. FOR EACH test_case in test_cases:
       a. SET tc_status = "running", tc_notes = []
       b. TRY:
          - FOR EACH step in test_case.steps:
            Execute step based on step.action:

            "navigate":
              → navigate_page url={step.target}
              → wait_for text from expected content (if specified), timeout={wait_timeout_ms}
              → take_snapshot (refresh UIDs)

            "click":
              → take_snapshot (get fresh UIDs)
              → Find element by step.target using selector priority:
                1. Search snapshot for data-testid="{step.target}"
                2. If not found, search by id="{step.target}"
                3. If not found, search by aria-label containing "{step.target}"
                4. If not found, search by text content matching "{step.target}"
              → IF element not found: FAIL TC with "UI_SELECTOR_NOT_FOUND: {step.target}"
              → click uid={found_uid}
              → take_snapshot (refresh UIDs after mutation)

            "fill":
              → take_snapshot
              → Find input element by step.target (same selector priority)
              → IF not found: FAIL TC with "UI_SELECTOR_NOT_FOUND: {step.target}"
              → fill uid={found_uid} value={step.value}
              → take_snapshot

            "select":
              → take_snapshot
              → Find select element by step.target
              → fill uid={found_uid} value={step.value}
              → take_snapshot

            "wait":
              → wait_for text=[step.target] timeout={wait_timeout_ms}
              → IF timeout: FAIL TC with "UI_WAIT_TIMEOUT: {step.target}"

            "assert_visible":
              → take_snapshot
              → Search snapshot for element matching step.target
              → IF not found: FAIL TC with "UI_ASSERT_VISIBLE_FAILED: {step.target}"

            "assert_text":
              → take_snapshot
              → Search snapshot for text content matching step.target
              → IF not found: FAIL TC with "UI_ASSERT_TEXT_FAILED: {step.target}"

            "assert_not_visible":
              → take_snapshot
              → Search snapshot for element matching step.target
              → IF found: FAIL TC with "UI_ASSERT_NOT_VISIBLE_FAILED: {step.target}"

            "screenshot":
              → take_screenshot filePath={screenshot_dir}/{tc.id}-step-{N}.png

          - AFTER all steps pass: verify expected_results
            → FOR EACH expected in test_case.expected_results:
              take_snapshot, search for expected text/element
              IF not found: FAIL TC with "UI_EXPECTED_RESULT_MISSING: {expected}"

          - IF all steps and expected_results pass:
            SET tc_status = "pass", increment passed

       c. CATCH any failure:
          SET tc_status = "fail", add failure reason to tc_notes, increment failed
          IF screenshot_on_failure:
            → take_screenshot filePath={screenshot_dir}/{tc.id}-failure.png
            → Add screenshot path to tc_notes

       d. RECORD result: {id, title, ac_ref, status: tc_status, notes: tc_notes}
       e. CONTINUE to next test case (never abort batch)

    5. COMPUTE summary:
       total = len(test_cases)
       pass_rate = (passed / total) * 100
       overall_status = "success" if failed==0 AND blocked==0
                        ELSE "partial_failure" if passed > 0
                        ELSE "failure"

    6. MOCKUP COMPARISON (if mockup_link != "N/A" and mockup_link is not null):
       a. OPEN mockup in a new browser tab: new_page url=file://{mockup_link} or serve via local path
       b. take_screenshot filePath={screenshot_dir}/mockup-reference.png of mockup page
       c. FOR EACH page/view tested in the actual app:
          - Navigate to the corresponding app page
          - take_screenshot filePath={screenshot_dir}/actual-{view_name}.png
       d. COMPARE mockup screenshot vs actual screenshots visually:
          - take_snapshot of mockup page → extract layout structure, key elements, text content
          - take_snapshot of actual page → extract same
          - IDENTIFY GAPS: missing elements, different text, layout misalignment, style differences
       e. PRODUCE mockup_comparison section in results:
          - gaps_found: [{element, mockup_state, actual_state, severity: "high|medium|low"}]
          - mockup_match_score: percentage of mockup elements correctly present in actual UI
          - screenshots: {mockup: path, actual: path}
       f. IF gaps found: add to overall notes; do NOT change TC pass/fail (mockup gaps are advisory)
  </action>
  <constraints>
    - BLOCKING: Always take_snapshot before interacting with elements — UIDs change after page mutations
    - BLOCKING: Never abort batch on single TC failure — continue with remaining TCs
    - CRITICAL: Use selector priority order: data-testid > id > aria-label > CSS selector
    - CRITICAL: Add wait_for after navigation to handle async loading
    - MANDATORY: Record detailed failure reasons for each failed TC
  </constraints>
  <output>operation_output with per-TC results and summary</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false       # true if overall_status != "failure"
  result:
    overall_status: "success | partial_failure | failure"
    summary:
      total: "{count}"
      passed: "{count}"
      failed: "{count}"
      blocked: "{count}"
      pass_rate: "{X}%"
    test_results:              # Per-TC results
      - id: "TC-XXX"
        title: "{title}"
        ac_ref: "AC-XXX"
        status: "pass | fail | blocked"
        notes: ["{failure reason or screenshot path}"]
    screenshots: ["{paths to failure screenshots}"]
    mockup_comparison:           # Present only when mockup_link provided
      mockup_link: "{path}"
      mockup_match_score: "{X}%"
      gaps: []                   # [{element, mockup_state, actual_state, severity}]
      screenshots: {mockup: "{path}", actual: ["{paths}"]}
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>All TCs executed or blocked</name>
    <verification>Every TC in test_cases has a status (pass/fail/blocked) in results</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Per-TC results reported</name>
    <verification>Each result has id, title, ac_ref, status, and notes</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Summary metrics computed</name>
    <verification>total, passed, failed, blocked, pass_rate all present</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Screenshots captured on failure</name>
    <verification>If screenshot_on_failure=true and any TC failed, screenshot files exist</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No batch abort</name>
    <verification>All TCs attempted even if earlier TCs failed</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Mockup comparison completed</name>
    <verification>If mockup_link provided, mockup_comparison section in output with gaps and match_score</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `UI_APP_UNREACHABLE` | target_url doesn't respond or page fails to load | Verify app is running; check target_url; all TCs marked blocked |
| `UI_SELECTOR_NOT_FOUND` | Element matching step.target not found in snapshot | Verify selector exists in HTML; check selector priority order; use take_snapshot first |
| `UI_WAIT_TIMEOUT` | wait_for text didn't appear within timeout | Increase wait_timeout_ms; verify text actually appears on page; check async loading |
| `UI_ASSERT_VISIBLE_FAILED` | Expected element not visible in snapshot | Element may be hidden, not rendered, or selector is wrong |
| `UI_ASSERT_TEXT_FAILED` | Expected text not found in snapshot | Text may differ (case, whitespace); check dynamic content loading |
| `UI_ASSERT_NOT_VISIBLE_FAILED` | Element expected to be hidden is still visible | Action that should hide it may not have completed; add wait step |
| `UI_MCP_UNAVAILABLE` | Chrome DevTools MCP not connected | Ensure MCP server is running; check connection; all TCs marked blocked |
| `UI_MOCKUP_LOAD_FAILED` | Mockup file at mockup_link could not be opened in browser | Verify file exists and is valid HTML; check file permissions |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-ui-testing-via-chrome-mcp/references/examples.md) for usage examples.
