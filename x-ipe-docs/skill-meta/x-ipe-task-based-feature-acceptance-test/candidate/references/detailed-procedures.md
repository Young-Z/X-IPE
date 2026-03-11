# Feature Acceptance Test - Detailed Procedures

This document contains detailed procedural guidance extracted from the main SKILL.md.

---

## Test Type Classification Guide

### frontend-ui
Tests that require browser interaction: rendering, clicking, form filling, visual verification.
**Tool:** chrome-devtools-mcp
**Indicators in AC:** "user sees", "displays", "click", "form", "modal", "page loads", "responsive"

### backend-api
Tests that verify HTTP/API behavior: endpoints, responses, status codes, error handling.
**Tool:** Matched code test tool skill (python/typescript/etc.)
**Indicators in AC:** "API returns", "endpoint", "status code", "request", "response", "JSON"

### unit
Tests that verify individual functions, classes, or logic at code level.
**Tool:** Matched code test tool skill
**Indicators in AC:** "calculates", "validates input", "converts", "parses", "returns error when"

### integration
Tests that verify multi-component interaction: data flow between services, state propagation.
**Tool:** Code test tool skill or chrome-devtools-mcp
**Indicators in AC:** "data flows from X to Y", "when service A updates, B reflects", "end-to-end"

---

## Per-Type Implementation Analysis Patterns

### Frontend-UI Analysis
1. LOCATE UI implementation files (templates, static JS, components)
2. FOR EACH test case, identify UI elements:
   - Search HTML/JSX for `data-testid`, `id`, `aria-label` attributes
   - Map each test step to a specific element
3. UPDATE test steps with precise selectors in step table format
4. VERIFY selectors are unique, stable, and descriptive

### Backend-API Analysis
1. LOCATE API route files (e.g., `routes/*.py`, `routes/*.ts`)
2. FOR EACH test case:
   - Document: endpoint URL, HTTP method, content-type
   - Document: request body schema (required/optional fields)
   - Document: expected response status code, response body structure
   - Note: authentication requirements, rate limits
3. UPDATE test steps with curl/httpx command patterns

### Unit Analysis
1. LOCATE source modules under test
2. FOR EACH test case:
   - Document: module path, function/method signature
   - Document: input parameters with types and valid ranges
   - Document: expected return value or side effect
   - Note: dependencies that need mocking
3. UPDATE test steps with assertion patterns

### Integration Analysis
1. LOCATE service interaction points
2. FOR EACH test case:
   - Document: setup steps (seed data, start services)
   - Document: trigger action (API call, UI action, event)
   - Document: verification points across services
3. UPDATE test steps with end-to-end flow

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

---

## MCP Command Patterns (Frontend-UI)

### Chrome Launch Prerequisites

MANDATORY: Before using Chrome DevTools MCP, ensure Chrome is running with a dedicated user data directory:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/x-ipe-chrome-profile

# Linux
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/x-ipe-chrome-profile
```

### Chrome DevTools MCP Test Patterns

```
Navigate:  chrome-devtools-navigate_page (url)
Click:     chrome-devtools-click (uid)
Fill:      chrome-devtools-fill (uid, value)
Verify:    chrome-devtools-take_snapshot → check element text/state
Wait:      chrome-devtools-wait_for (text)
Screenshot: chrome-devtools-take_screenshot (on failure)
```

---

## Backend-API Test Patterns

### API Call via Tool Skill

```python
# Python (pytest + httpx)
def test_create_article():
    response = client.post("/api/kb/articles", json={"title": "Test", "content": "..."})
    assert response.status_code == 201
    assert response.json()["title"] == "Test"

def test_get_articles():
    response = client.get("/api/kb/articles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### API Call via curl (standalone)

```bash
# Create
curl -X POST http://localhost:5000/api/kb/articles \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"body"}' \
  -w "\n%{http_code}"

# Verify response
curl http://localhost:5000/api/kb/articles | jq '.[] | select(.title=="Test")'
```

---

## Unit Test Patterns

### Python (pytest)

```python
def test_validate_article_frontmatter():
    result = validate_frontmatter({"title": "Test", "tags": ["a"]})
    assert result.is_valid is True

def test_validate_article_missing_title():
    result = validate_frontmatter({"tags": ["a"]})
    assert result.is_valid is False
    assert "title" in result.errors
```

### JavaScript (vitest)

```javascript
import { describe, it, expect } from 'vitest';

describe('validateArticle', () => {
  it('accepts valid article', () => {
    expect(validateArticle({title: 'Test', content: 'body'})).toBe(true);
  });
  it('rejects missing title', () => {
    expect(() => validateArticle({content: 'body'})).toThrow();
  });
});
```

---

## Test Data Collection Process

### Data Types Per Test Case

| Type | Description | Example |
|------|-------------|---------|
| Input | Values to enter in forms/fields | Email, name, description |
| Selection | Options to select from dropdowns | Category, status |
| Expected | Expected text/values to verify | Success message, count |
| Compare | Before/after values for validation | Counter increment |
| API Payload | JSON request body | `{"title": "Test"}` |
| API Expected | Expected response body/status | `201`, `{"id": "..."}` |

---

## Reflection Checklist

Use this checklist when refining each test case:

### Validation Points

- Does test case cover the acceptance criterion completely?
- Are preconditions clearly defined?
- Are all steps actionable?
- Is expected result specific and measurable?
- Are edge cases covered?

### Per-Type Checks

| Type | Additional Checks |
|------|------------------|
| frontend-ui | Selectors verified? Wait conditions added? Dynamic content handled? |
| backend-api | Error responses tested (4xx, 5xx)? Auth requirements met? |
| unit | Boundary conditions tested? Dependencies mocked? |
| integration | Setup/teardown defined? State cleanup included? |

---

## Test Result Reporting Format

### Per-Test Summary Table

```markdown
| Test Case | Title | Type | Priority | Status | Notes |
|-----------|-------|------|----------|--------|-------|
| TC-001 | {title} | frontend-ui | P0 | Pass | |
| TC-002 | {title} | backend-api | P1 | Fail | {reason} |
```

### Execution Metrics (by type)

```markdown
| Type | Total | Passed | Failed | Blocked |
|------|-------|--------|--------|---------|
| frontend-ui | X | X | X | X |
| backend-api | X | X | X | X |
| unit | X | X | X | X |
| integration | X | X | X | X |
| **TOTAL** | X | X | X | X |
| **Pass Rate** | | X% | | |
```
