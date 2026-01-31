# Feature Acceptance Test Examples

This document provides concrete execution examples for the Feature Acceptance Test skill.

---

## Example 1: Standard Feature Acceptance Test

**Context:** FEATURE-022-C: Feedback Capture & Panel has been implemented and needs acceptance testing.

### Step 1: Check UI Scope

```
Query feature board:
  feature_id: FEATURE-022-C
  status: Implemented

Read technical design:
  Technical Scope: [Frontend, Backend]
  
Decision: Has web UI → Proceed to Step 2
```

### Step 2: Generate Test Plan

Read specification.md acceptance criteria:
```
AC-1: User can right-click any element to open context menu
AC-2: Context menu shows "Capture Feedback" option
AC-3: Clicking capture opens feedback panel
AC-4: Panel displays screenshot preview
AC-5: User can enter feedback description
AC-6: Submit button saves feedback
```

Generated acceptance-test-cases.md:
```markdown
### TC-001: Context Menu Opens on Right-Click

**Acceptance Criteria Reference:** AC-1

**Priority:** P0

**Preconditions:**
- User is on proxy page with injected inspector

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | /proxy/preview?url=... | Page loads |
| 2 | Right-click | `body` | - | Context menu appears |
| 3 | Verify | `.feedback-context-menu` | - | Menu is visible |

**Expected Outcome:** Context menu appears on right-click
```

### Step 3: Analyze HTML

Reviewed src/x_ipe/static/js/uiux-feedback.js:
```javascript
// Found context menu implementation
const contextMenu = document.createElement('div');
contextMenu.className = 'feedback-context-menu';
contextMenu.id = 'feedback-context-menu';

// Found feedback panel
const panel = document.createElement('div');
panel.id = 'feedback-panel';
panel.innerHTML = `
  <textarea id="feedback-description"></textarea>
  <button id="submit-feedback">Submit</button>
`;
```

Updated selectors:
```
- Context menu: #feedback-context-menu
- Capture option: .capture-feedback-btn
- Feedback panel: #feedback-panel
- Description input: #feedback-description
- Submit button: #submit-feedback
```

### Step 4: Test Data Preparation

**Context:** auto_proceed = false, so user is asked for test data.

Agent asks:
```markdown
## Test Data Required for FEATURE-022-C

### TC-005: Submit Feedback Successfully
- **Feedback description text:** (text to enter in textarea)
- **Expected success message:** (exact text to verify after submit)

### TC-006: Submit Feedback with Screenshot
- **Feedback description:** (text to enter)
- **Expected confirmation:** (what should appear after submission)

Please provide the test data, or type "use defaults" to use placeholder values.
```

User provides:
```
TC-005:
- Feedback description: "The button color is too light, hard to see"
- Expected success message: "Feedback submitted successfully"

TC-006:
- Feedback description: "Navigation menu overlaps content"
- Expected confirmation: "Feedback with screenshot saved"
```

Updated in each test case's Test Data table:
```markdown
### TC-005: Submit Feedback Successfully
...
**Test Data:**
> Data Source: User Provided

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | feedback-description | "The button color is too light, hard to see" | User provided |
| Expected | success-message | "Feedback submitted successfully" | Contains |

---

### TC-006: Submit Feedback with Screenshot
...
**Test Data:**
> Data Source: User Provided

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | feedback-description | "Navigation menu overlaps content" | User provided |
| Expected | success-message | "Feedback with screenshot saved" | Contains |
```

### Step 5: Reflect & Refine

Reflection on TC-001:
- ✅ Covers AC-1 completely
- ⚠️ Missing: Wait for context menu animation
- ⚠️ Missing: Verify menu position near click

Refined TC-001:
```markdown
| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | /proxy/preview?url=... | Page loads |
| 2 | Wait | `body` | 500ms | Page interactive |
| 3 | Right-click | `body` at (200, 200) | - | Click registered |
| 4 | Wait for | `#feedback-context-menu` | 300ms | Menu appears |
| 5 | Verify visible | `#feedback-context-menu` | - | Menu is visible |
| 6 | Verify position | `#feedback-context-menu` | - | Near click coords |
```

### Step 6: Execute via Chrome DevTools MCP

```javascript
// TC-001 Execution
await page.goto('http://localhost:5000/proxy/preview?url=https://example.com');
await page.waitForTimeout(500);
await page.click('body', { button: 'right', position: { x: 200, y: 200 } });
await page.waitForSelector('#feedback-context-menu', { timeout: 1000 });

const menuVisible = await page.isVisible('#feedback-context-menu');
assert(menuVisible === true); // PASS

// TC-002 Execution
await page.click('.capture-feedback-btn');
await page.waitForSelector('#feedback-panel');

const panelVisible = await page.isVisible('#feedback-panel');
assert(panelVisible === true); // PASS
```

### Step 7: Report Results

```markdown
## Execution Results

**Execution Date:** 01-28-2026
**Executed By:** Cipher
**Environment:** dev (localhost:5000)

| Metric | Value |
|--------|-------|
| Total Tests | 6 |
| Passed | 6 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |
```

### Final Output

```yaml
Output:
  category: feature-stage
  status: completed
  next_task_type: Feature Closing
  require_human_review: No
  task_output_links: [x-ipe-docs/requirements/FEATURE-022-C/acceptance-test-cases.md]
  feature_id: FEATURE-022-C
  feature_title: Feedback Capture & Panel
  feature_version: v1.0
  feature_phase: Acceptance Testing
  test_cases_created: 6
  tests_passed: 6
  tests_failed: 0
  pass_rate: "100%"
```

---

## Example 2: Skipped Execution (No Web UI)

**Context:** FEATURE-018: CLI Tool has been implemented.

### Step 1: Check UI Scope

```
Query feature board:
  feature_id: FEATURE-018
  status: Implemented

Read technical design:
  Technical Scope: [CLI]
  
Decision: No web UI → Skip acceptance test
```

### Final Output

```yaml
Output:
  category: feature-stage
  status: skipped
  next_task_type: Feature Closing
  require_human_review: No
  task_output_links: []
  feature_id: FEATURE-018
  feature_title: X-IPE CLI Tool
  feature_version: v1.0
  feature_phase: Acceptance Testing
  skip_reason: "No web UI - CLI tool only"
  test_cases_created: 0
  tests_passed: 0
  tests_failed: 0
  pass_rate: "N/A"
```

---

## Example 3: Blocked Execution (No MCP)

**Context:** FEATURE-008: Idea Viewer needs acceptance testing but Chrome DevTools MCP is not configured.

### Steps 1-4: Complete as normal

Test cases generated and refined in acceptance-test-cases.md.

### Step 5: Execute Blocked

```
CHECK MCP availability:
  Chrome DevTools MCP: Not configured
  
ACTION:
  - Mark execution as blocked
  - Document test cases are ready for manual execution
```

### Step 6: Report Results

```markdown
## Execution Results

**Execution Date:** 01-30-2026
**Executed By:** Cipher
**Environment:** N/A (MCP not available)

| Metric | Value |
|--------|-------|
| Total Tests | 8 |
| Passed | 0 |
| Failed | 0 |
| Blocked | 8 |
| Pass Rate | N/A |

**Note:** Test cases ready for manual execution. Chrome DevTools MCP required for automated execution.
```

### Final Output

```yaml
Output:
  category: feature-stage
  status: blocked
  next_task_type: Feature Closing
  require_human_review: Yes  # Human should manually test or configure MCP
  task_output_links: [x-ipe-docs/requirements/FEATURE-008/acceptance-test-cases.md]
  feature_id: FEATURE-008
  feature_title: Idea Viewer
  feature_version: v1.4
  feature_phase: Acceptance Testing
  test_cases_created: 8
  tests_passed: 0
  tests_failed: 0
  pass_rate: "N/A"
  blocked_reason: "Chrome DevTools MCP not available"
```

---

## Example 4: Partial Test Failure

**Context:** FEATURE-010: Dashboard has some failing tests.

### Step 5: Execute with Failures

```javascript
// TC-001: Dashboard loads - PASS
await page.goto('/dashboard');
const title = await page.textContent('h1');
assert(title === 'Dashboard'); // PASS

// TC-002: Chart renders - PASS
await page.waitForSelector('.chart-container');
// PASS

// TC-003: Export button works - FAIL
await page.click('#export-btn');
await page.waitForSelector('.export-modal', { timeout: 3000 });
// TIMEOUT - Modal never appeared

// TC-004: Data refresh works - PASS
await page.click('#refresh-btn');
// PASS
```

### Step 6: Report with Failures

```markdown
## Test Execution Summary

| Test Case | Title | Priority | Status | Notes |
|-----------|-------|----------|--------|-------|
| TC-001 | Dashboard loads | P0 | ✅ Pass | |
| TC-002 | Chart renders | P0 | ✅ Pass | |
| TC-003 | Export button works | P1 | ❌ Fail | Modal timeout |
| TC-004 | Data refresh works | P1 | ✅ Pass | |

## Execution Results

| Metric | Value |
|--------|-------|
| Total Tests | 4 |
| Passed | 3 |
| Failed | 1 |
| Blocked | 0 |
| Pass Rate | 75% |

### Failed Tests

| Test Case | Failure Reason | Recommended Action |
|-----------|----------------|-------------------|
| TC-003 | Timeout waiting for .export-modal | Check export modal implementation |
```

### Final Output

```yaml
Output:
  category: feature-stage
  status: completed  # Tests ran, even with failures
  next_task_type: Feature Closing
  require_human_review: Yes  # Due to test failures
  task_output_links: [x-ipe-docs/requirements/FEATURE-010/acceptance-test-cases.md]
  feature_id: FEATURE-010
  feature_title: Dashboard
  feature_version: v1.0
  feature_phase: Acceptance Testing
  test_cases_created: 4
  tests_passed: 3
  tests_failed: 1
  pass_rate: "75%"
```
