# Feature Acceptance Test - Detailed Procedures

This document contains detailed procedural guidance extracted from the main SKILL.md.

---

## Selector Best Practices

### Element Identification Priority

When identifying UI elements for test steps, use this priority order:

1. `data-testid` attribute (preferred - explicit test hooks)
2. `id` attribute (stable unique identifiers)
3. `aria-label` for accessibility
4. Unique class combinations
5. CSS selector path (last resort)

### Preferred Selectors

```
- [data-testid="..."]     # Explicit test hooks
- #unique-id              # Stable IDs
- [aria-label="..."]      # Accessibility labels
- form[name="..."]        # Named forms
```

### Selectors to Avoid

```
- .class1.class2.class3   # Fragile class chains
- div > div > span        # Position-dependent
- [id^="auto_"]           # Auto-generated IDs
```

### Selector Validation

Verify all selectors are:
- Unique on the page
- Stable (not dynamically generated IDs)
- Descriptive of element purpose

---

## MCP Command Patterns

Chrome DevTools MCP commands used during test execution:

```javascript
// Navigate to page
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

// Check visibility
const visible = await page.isVisible('{selector}');
assert(visible === true);

// Wait for timeout
await page.waitForTimeout(500);

// Right-click
await page.click('{selector}', { button: 'right', position: { x: 200, y: 200 } });
```

---

## Test Data Collection Process

When `auto_proceed = false`, collect test data from the user:

### Data Types Per Test Case

| Type | Description | Example |
|------|-------------|---------|
| Input | Values to enter in forms/fields | Email, name, description |
| Selection | Options to select from dropdowns | Category, status |
| Expected | Expected text/values to verify | Success message, count |
| Compare | Before/after values for validation | Counter increment |

### Collection Format

Ask user for each test case:

```
"For TC-001 ({title}):
- Input for '{field}': ___
- Expected result: ___"
```

### Test Data Table Format

```markdown
**Test Data:**
> Data Source: User Provided | Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | {field_name} | "{value}" | {notes} |
| Expected | {element} | "{expected_text}" | Match: Exact/Contains |
```

---

## Test Step Table Format

Each test case uses this format for steps:

```markdown
| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | {URL} | Page loads |
| 2 | Click | `{selector}` | - | {behavior} |
| 3 | Enter | `{selector}` | "{value}" | Value appears |
| 4 | Verify | `{selector}` | - | Contains "{text}" |
```

---

## Reflection Checklist

Use this checklist when refining each test case in Step 5:

### Validation Points

- Does test case cover the acceptance criterion completely?
- Are preconditions clearly defined?
- Are all steps actionable?
- Are selectors verified to exist in the HTML?
- Is expected result specific and measurable?
- Are edge cases covered?

### Reflection Questions

- What could cause this test to fail incorrectly (false negative)?
- Are there missing steps between actions?
- Is the expected result too vague?
- Should this be split into multiple tests?

### Common Refinements

- Add explicit wait steps for async operations
- Add verification steps between major actions
- Split complex tests into focused smaller tests
- Add cleanup/reset steps if needed
- Handle dynamic content loading with waitForSelector

---

## Test Result Reporting Format

### Per-Test Summary Table

```markdown
| Test Case | Title | Priority | Status | Notes |
|-----------|-------|----------|--------|-------|
| TC-001 | {title} | P0 | Pass | |
| TC-002 | {title} | P1 | Fail | {reason} |
```

### Execution Metrics

```markdown
| Metric | Value |
|--------|-------|
| Total Tests | {X} |
| Passed | {X} |
| Failed | {X} |
| Blocked | {X} |
| Pass Rate | {X}% |
```

### Failure Documentation

```markdown
| Test Case | Failure Reason | Recommended Action |
|-----------|----------------|-------------------|
| TC-XXX | {reason} | {action} |
```
