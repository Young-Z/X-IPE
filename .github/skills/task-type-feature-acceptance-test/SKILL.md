---
name: task-type-feature-acceptance-test
description: Execute acceptance tests for features with web UI. Generates test cases from specification acceptance criteria, analyzes HTML for selectors, and runs tests via Chrome DevTools MCP. Use after Code Implementation for features with web UI. Triggers on requests like "run acceptance tests", "test feature UI", "execute acceptance tests".
---

# Task Type: Feature Acceptance Test

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

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

### Web UI Only
This skill is **ONLY for features with web UI**. If the feature is:
- Backend API only → Skip this skill, proceed to Feature Closing
- CLI tool only → Skip this skill, proceed to Feature Closing
- Library/SDK only → Skip this skill, proceed to Feature Closing

### MCP Requirement
This skill requires Chrome DevTools MCP for test execution. If MCP is not available, generate test cases but mark execution as blocked.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Feature Acceptance Test |
| Category | Standalone OR feature-stage |
| Next Task Type | Feature Closing (if feature-stage) |
| Require Human Review | No |
| Feature Phase | Acceptance Testing |

**Category Behavior:**
- **Standalone**: Called directly to test any web UI (no feature board interaction)
- **feature-stage**: Called as part of feature workflow (after Code Implementation)

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |
| feature_id | Required (feature-stage) OR Optional (standalone) |
| target_url | Required (standalone) OR from feature (feature-stage) |

---

## Skill/Task Completion Output Attributes

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: Standalone | feature-stage  # Based on how skill was invoked
  status: completed | blocked | skipped
  next_task_type: Feature Closing | null  # null if standalone
  require_human_review: No
  auto_proceed: {from input}
  task_output_links: [x-ipe-docs/requirements/FEATURE-XXX/acceptance-test-cases.md] | [{output_path}]
  
  # Feature-stage specific (only if category=feature-stage)
  feature_id: FEATURE-XXX
  feature_title: {title}
  feature_version: {version}
  feature_phase: Acceptance Testing
  
  # Acceptance test specific
  skip_reason: "No web UI" | null
  test_cases_created: {count}
  tests_passed: {count}
  tests_failed: {count}
  pass_rate: "{X}%"
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Feature exists on feature board | Yes |
| 2 | Feature status is "Implemented" or "Test Generation Complete" | Yes |
| 3 | Code implementation is complete | Yes |
| 4 | Specification with acceptance criteria exists | Yes |
| 5 | Feature is deployed and accessible via URL | Yes |

---

## Execution Flow

Execute Feature Acceptance Test by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Check UI Scope | Determine if feature has web UI | Has web UI OR skip |
| 2 | Generate Plan | Create test cases from acceptance criteria | Test cases defined |
| 3 | Analyze HTML | Extract element selectors from UI code | Selectors identified |
| 4 | Test Data Prep | Ask user for test data (if auto_proceed=false) | Data collected OR skipped |
| 5 | Reflect & Refine | Review and update test cases | Cases validated |
| 6 | Execute Tests | Run tests via Chrome DevTools MCP | Tests complete |
| 7 | Report Results | Document test results | Results documented |

**⛔ BLOCKING RULES:**
- Step 1: If no web UI → output status=skipped, proceed to next_task_type
- Step 4: If auto_proceed=true → skip this step, use placeholder/generated data
- Step 6: If MCP unavailable → output status=blocked, test cases ready for manual execution

---

## Execution Procedure

### Step 1: Check UI Scope

**Action:** Determine if feature has web UI component

```
1. QUERY feature board for Feature Data Model:
   - feature_id
   - specification_link
   - technical_design_link

2. READ technical design → Check "Technical Scope" section:
   
   IF scope includes [Frontend] OR [Full Stack]:
     - Proceed to Step 2
     
   ELSE (Backend, API Only, Database, CLI):
     - SET status = "skipped"
     - SET skip_reason = "No web UI"
     - RETURN to task-execution-guideline with:
       next_task_type: Feature Closing
       status: skipped

3. VERIFY feature is accessible:
   - Check if playground/demo URL exists
   - Confirm feature can be triggered via web UI
```

**Output:** Decision to proceed or skip

---

### Step 2: Generate Acceptance Test Plan

**Action:** Create test cases from specification acceptance criteria

```
1. READ specification.md for feature:
   Location: x-ipe-docs/requirements/FEATURE-XXX/specification.md

2. EXTRACT all acceptance criteria (AC-X):
   - Note the exact wording of each criterion
   - Identify testable conditions
   - Note any edge cases mentioned

3. CREATE acceptance-test-cases.md:
   Location: x-ipe-docs/requirements/FEATURE-XXX/acceptance-test-cases.md
   Template: Use templates/acceptance-test-cases.md

4. FOR EACH acceptance criterion:
   - Create at least one test case (TC-XXX)
   - Map TC to AC reference
   - Define priority (P0/P1/P2)
   - Write high-level test steps (without selectors yet)
   - Define expected outcomes

5. PRIORITIZE test cases:
   P0 (Critical): Core functionality, must pass
   P1 (High): Important flows, should pass
   P2 (Medium): Edge cases, nice to pass
```

**Output:** Initial acceptance-test-cases.md with test case outlines

---

### Step 3: Analyze HTML for Selectors

**Action:** Extract precise CSS/XPath selectors from UI code

```
1. LOCATE UI implementation files:
   - Templates: src/x_ipe/templates/*.html
   - Static JS: src/x_ipe/static/js/*.js
   - Components: (project-specific paths)

2. FOR EACH test case, identify UI elements:
   
   ELEMENT IDENTIFICATION PRIORITY:
   1. data-testid attribute (preferred)
   2. id attribute
   3. aria-label for accessibility
   4. Unique class combinations
   5. CSS selector path (last resort)

3. UPDATE test steps with selectors:
   
   | Step | Action | Element Selector | Input Data | Expected Result |
   |------|--------|------------------|------------|-----------------|
   | 1 | Click | `[data-testid="submit-btn"]` | - | Form submits |
   | 2 | Enter | `#email-input` | "test@example.com" | Value appears |
   | 3 | Verify | `.success-message` | - | Contains "Saved" |

4. VERIFY selectors are:
   - Unique on the page
   - Stable (not dynamically generated IDs)
   - Descriptive of element purpose
```

**Selector Best Practices:**
```
PREFER:
- [data-testid="..."]     # Explicit test hooks
- #unique-id              # Stable IDs
- [aria-label="..."]      # Accessibility labels
- form[name="..."]        # Named forms

AVOID:
- .class1.class2.class3   # Fragile class chains
- div > div > span        # Position-dependent
- [id^="auto_"]           # Auto-generated IDs
```

---

### Step 4: Test Data Preparation (Conditional)

**Action:** Collect test data from user when auto_proceed is false

```
IF auto_proceed = true:
   - SKIP this step
   - Use placeholder/generated test data
   - Proceed to Step 5

IF auto_proceed = false:
   - PAUSE and ask user for test data
```

**Data Collection Process:**

```
1. ANALYZE each test case for data requirements:
   
   DATA TYPES (per test case):
   - Input: Values to enter in forms, fields
   - Selection: Options to select from dropdowns
   - Expected: Expected text, values to verify
   - Compare: Before/after values for validation

2. ASK user for each test case:
   
   "For TC-001 ({title}):
   - Input for '{field}': ___
   - Expected result: ___"

3. UPDATE Test Data table in each test case:
   
   | Type | Field/Element | Value | Notes |
   |------|---------------|-------|-------|
   | Input | email | "user@test.com" | Valid email |
   | Expected | success-msg | "Saved" | Contains |
```

**Output:** Test Data table populated in each test case section

---

### Step 5: Reflect and Refine Test Cases

**Action:** Review each test case for completeness and accuracy

```
FOR EACH test case:

1. VALIDATION CHECKLIST:
   □ Does test case cover the AC completely?
   □ Are preconditions clearly defined?
   □ Are all steps actionable?
   □ Are selectors verified to exist?
   □ Is expected result specific and measurable?
   □ Are edge cases covered?

2. REFLECTION QUESTIONS:
   - What could cause this test to fail incorrectly?
   - Are there missing steps between actions?
   - Is the expected result too vague?
   - Should this be split into multiple tests?

3. REFINE based on reflection:
   - Add missing steps
   - Clarify expected results
   - Add wait conditions if needed
   - Handle dynamic content loading

4. UPDATE acceptance-test-cases.md with refinements
```

**Common Refinements:**
- Add explicit wait steps for async operations
- Add verification steps between major actions
- Split complex tests into focused smaller tests
- Add cleanup/reset steps if needed

---

### Step 6: Execute Tests via Chrome DevTools MCP

**Action:** Run acceptance tests using Chrome DevTools MCP

```
1. CHECK MCP availability:
   
   IF Chrome DevTools MCP available:
     - Proceed with execution
   ELSE:
     - SET status = "blocked"
     - Document: "Test cases ready for manual execution"
     - RETURN results with test_cases_created count

2. FOR EACH test case (ordered by priority):
   
   a. SETUP:
      - Navigate to test URL
      - Verify page loaded
      
   b. EXECUTE steps:
      - Perform each action via MCP
      - Capture results after each step
      - Take screenshot on failure
      
   c. VERIFY expected outcomes:
      - Check element states
      - Validate text content
      - Confirm UI changes
      
   d. RECORD result:
      - Status: Pass | Fail | Blocked
      - Execution time
      - Failure reason (if any)
      - Screenshot link (if failure)

3. CONTINUE with remaining tests even if some fail
```

**MCP Commands Pattern:**
```javascript
// Navigate
await page.goto('{URL}');

// Click element
await page.click('{selector}');

// Enter text
await page.fill('{selector}', '{value}');

// Verify text content
const text = await page.textContent('{selector}');
assert(text.includes('{expected}'));

// Wait for element
await page.waitForSelector('{selector}');
```

---

### Step 7: Report Test Results

**Action:** Document comprehensive test results

```
1. UPDATE acceptance-test-cases.md:
   
   - Set status for each test case (✅ Pass | ❌ Fail | ⬜ Not Run)
   - Add execution notes
   - Fill in Execution Results section:
     - Execution date
     - Environment
     - Pass/Fail counts
     - Pass rate percentage

2. DOCUMENT failures:
   
   | Test Case | Failure Reason | Recommended Action |
   |-----------|----------------|-------------------|
   | TC-003 | Button not found | Verify selector |
   | TC-007 | Timeout waiting | Check async loading |

3. CALCULATE metrics:
   - Total tests
   - Passed count
   - Failed count  
   - Blocked count
   - Pass rate = (passed / total) * 100

4. RETURN task output with results
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Feature checked for web UI scope | Yes |
| 2 | Acceptance test cases created from ACs | Yes (if has UI) |
| 3 | HTML analyzed for element selectors | Yes (if has UI) |
| 4 | Test data collected from user (if auto_proceed=false) | Conditional |
| 5 | Test cases reflected and refined | Yes (if has UI) |
| 6 | Tests executed via MCP (or marked blocked) | Yes (if has UI) |
| 7 | Test results documented | Yes (if has UI) |
| 8 | acceptance-test-cases.md saved to feature folder | Yes (if has UI) |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: Form Submission Test

**When:** Feature includes form input and submission
**Then:**
```
1. Test empty form submission (validation)
2. Test invalid input formats
3. Test valid submission → success state
4. Verify success message/redirect
```

### Pattern: CRUD Operations Test

**When:** Feature includes Create/Read/Update/Delete
**Then:**
```
1. Test Create → verify appears in list
2. Test Read → verify data displayed correctly
3. Test Update → verify changes persisted
4. Test Delete → verify removed from list
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

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Test without selectors | Tests will fail to find elements | Analyze HTML first |
| Skip reflection step | Miss edge cases and errors | Always reflect on each TC |
| Test implementation details | Brittle tests | Test user-visible behavior |
| One massive test | Hard to debug failures | Split into focused tests |
| Ignore async loading | Flaky tests | Add explicit wait steps |
| Hard-coded test data | Hard to maintain | Use variables/fixtures |

---

## Example

See [references/examples.md](references/examples.md) for concrete execution examples including:
- Standard feature acceptance test flow
- Skipped execution (no web UI)
- Blocked execution (no MCP available)

---

## Notes

- This skill is specifically for **web UI acceptance testing**
- Backend/API testing is handled by Test Generation skill
- Test cases should map 1:1 with acceptance criteria
- Prioritize stable selectors (data-testid > id > class)
- MCP execution is preferred but manual execution fallback exists
- All test artifacts go in the feature folder alongside specification
