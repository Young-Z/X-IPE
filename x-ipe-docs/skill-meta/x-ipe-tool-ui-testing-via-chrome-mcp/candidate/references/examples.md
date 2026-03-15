# Examples: x-ipe-tool-ui-testing-via-chrome-mcp

## Example 1: Execute 3 UI Test Cases for a Form Feature

**Context:** Feature has a contact form with name, email, and submit button.

### Input

```yaml
operation: execute_ui_tests
target_url: "http://localhost:5001"
test_cases:
  - id: "TC-001"
    title: "Submit contact form with valid data"
    ac_ref: "AC-01"
    steps:
      - action: navigate
        target: "http://localhost:5001/contact"
        description: "Navigate to contact page"
      - action: fill
        target: "contact-name"
        value: "John Doe"
        description: "Fill in name field"
      - action: fill
        target: "contact-email"
        value: "john@example.com"
        description: "Fill in email field"
      - action: click
        target: "submit-btn"
        description: "Click submit button"
      - action: wait
        target: "Thank you"
        description: "Wait for success message"
    expected_results:
      - "Thank you message is displayed"

  - id: "TC-002"
    title: "Validate empty form submission"
    ac_ref: "AC-02"
    steps:
      - action: navigate
        target: "http://localhost:5001/contact"
        description: "Navigate to contact page"
      - action: click
        target: "submit-btn"
        description: "Click submit without filling fields"
      - action: assert_visible
        target: "Please fill out this field"
        description: "Validation error should appear"
    expected_results:
      - "Validation error message visible"

  - id: "TC-003"
    title: "Verify form fields are visible"
    ac_ref: "AC-01"
    steps:
      - action: navigate
        target: "http://localhost:5001/contact"
        description: "Navigate to contact page"
      - action: assert_visible
        target: "contact-name"
        description: "Name field is visible"
      - action: assert_visible
        target: "contact-email"
        description: "Email field is visible"
      - action: assert_visible
        target: "submit-btn"
        description: "Submit button is visible"
    expected_results:
      - "All form fields are visible"
screenshot_on_failure: true
screenshot_dir: "x-ipe-docs/requirements/FEATURE-001/screenshots/"
```

### Expected Output

```yaml
operation_output:
  success: true
  result:
    overall_status: "success"
    summary:
      total: 3
      passed: 3
      failed: 0
      blocked: 0
      pass_rate: "100%"
    test_results:
      - id: "TC-001"
        title: "Submit contact form with valid data"
        ac_ref: "AC-01"
        status: "pass"
        notes: []
      - id: "TC-002"
        title: "Validate empty form submission"
        ac_ref: "AC-02"
        status: "pass"
        notes: []
      - id: "TC-003"
        title: "Verify form fields are visible"
        ac_ref: "AC-01"
        status: "pass"
        notes: []
    screenshots: []
  errors: []
```

---

## Example 2: Mixed Pass/Fail with Screenshot

**Context:** Sidebar navigation test where one element is missing.

### Input

```yaml
operation: execute_ui_tests
target_url: "http://localhost:5001"
test_cases:
  - id: "TC-010"
    title: "Sidebar shows folder tree"
    ac_ref: "AC-05"
    steps:
      - action: navigate
        target: "http://localhost:5001"
        description: "Navigate to main page"
      - action: assert_visible
        target: "kb-sidebar"
        description: "Sidebar container is visible"
      - action: assert_visible
        target: "folder-tree"
        description: "Folder tree is rendered"
    expected_results:
      - "Sidebar with folder tree is visible"

  - id: "TC-011"
    title: "Click folder expands children"
    ac_ref: "AC-06"
    steps:
      - action: navigate
        target: "http://localhost:5001"
        description: "Navigate to main page"
      - action: click
        target: "folder-item-docs"
        description: "Click on docs folder"
      - action: assert_visible
        target: "child-item"
        description: "Child items appear after expand"
    expected_results:
      - "Child items are visible after folder click"
screenshot_on_failure: true
screenshot_dir: "x-ipe-docs/requirements/FEATURE-049-B/screenshots/"
```

### Expected Output (TC-011 fails)

```yaml
operation_output:
  success: false
  result:
    overall_status: "partial_failure"
    summary:
      total: 2
      passed: 1
      failed: 1
      blocked: 0
      pass_rate: "50%"
    test_results:
      - id: "TC-010"
        title: "Sidebar shows folder tree"
        ac_ref: "AC-05"
        status: "pass"
        notes: []
      - id: "TC-011"
        title: "Click folder expands children"
        ac_ref: "AC-06"
        status: "fail"
        notes:
          - "UI_SELECTOR_NOT_FOUND: child-item"
          - "Screenshot: x-ipe-docs/requirements/FEATURE-049-B/screenshots/TC-011-failure.png"
    screenshots:
      - "x-ipe-docs/requirements/FEATURE-049-B/screenshots/TC-011-failure.png"
  errors: []
```

---

## Example 3: App Unreachable — All Blocked

### Input

```yaml
operation: execute_ui_tests
target_url: "http://localhost:9999"
test_cases:
  - id: "TC-020"
    title: "Check homepage loads"
    ac_ref: "AC-01"
    steps:
      - action: navigate
        target: "http://localhost:9999"
        description: "Navigate to homepage"
    expected_results:
      - "Homepage loads"
```

### Expected Output

```yaml
operation_output:
  success: false
  result:
    overall_status: "failure"
    summary:
      total: 1
      passed: 0
      failed: 0
      blocked: 1
      pass_rate: "0%"
    test_results:
      - id: "TC-020"
        title: "Check homepage loads"
        ac_ref: "AC-01"
        status: "blocked"
        notes: ["UI_APP_UNREACHABLE: http://localhost:9999"]
    screenshots: []
  errors:
    - "UI_APP_UNREACHABLE: Target URL http://localhost:9999 is not reachable"
```
