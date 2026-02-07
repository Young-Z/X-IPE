# Acceptance Test Cases

> Feature: {FEATURE-XXX} - {Feature Title}
> Generated: {date}
> Status: Draft | Ready for Execution | Executed

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | {FEATURE-XXX} |
| Feature Title | {title} |
| Total Test Cases | {count} |
| Priority | P0 (Critical) / P1 (High) / P2 (Medium) |
| Target URL | {base URL for testing} |

---

## Prerequisites

- [ ] Feature is deployed and accessible
- [ ] Test environment is ready
- [ ] Chrome DevTools MCP is available

---

## Test Cases

### TC-001: {Test Case Title}

**Acceptance Criteria Reference:** AC-{X} from specification.md

**Priority:** P0 | P1 | P2

**Preconditions:**
- {precondition 1}
- {precondition 2}

**Test Data:**
> Data Source: User Provided | Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | {field_name} | "{value}" | {notes} |
| Input | {field_name} | "{value}" | {notes} |
| Selection | {dropdown} | "{option}" | {notes} |
| Expected | {element} | "{expected_text}" | Match: Exact/Contains |
| Compare | {counter} | Before: X, After: Y | {notes} |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | {URL} | Page loads successfully |
| 2 | Click | `{CSS selector}` | - | {expected behavior} |
| 3 | Enter text | `{CSS selector}` | "{input value}" | Text appears in field |
| 4 | Click | `{CSS selector}` | - | {expected behavior} |
| 5 | Verify | `{CSS selector}` | - | Element contains "{expected text}" |

**Expected Outcome:** {overall expected result}

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

**Execution Notes:** {notes after execution}

---

### TC-002: {Test Case Title}

**Acceptance Criteria Reference:** AC-{X} from specification.md

**Priority:** P0 | P1 | P2

**Preconditions:**
- {precondition 1}

**Test Data:**
> Data Source: User Provided | Generated Defaults

| Type | Field/Element | Value | Notes |
|------|---------------|-------|-------|
| Input | {field_name} | "{value}" | {notes} |
| Expected | {element} | "{expected_value}" | Match: Exact |

**Test Steps:**

| Step | Action | Element Selector | Input Data | Expected Result |
|------|--------|------------------|------------|-----------------|
| 1 | Navigate to | - | {URL} | Page loads successfully |
| 2 | {action} | `{selector}` | {input} | {expected} |

**Expected Outcome:** {overall expected result}

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

**Execution Notes:** {notes after execution}

---

## Test Execution Summary

| Test Case | Title | Priority | Status | Notes |
|-----------|-------|----------|--------|-------|
| TC-001 | {title} | P0 | ⬜ Not Run | |
| TC-002 | {title} | P1 | ⬜ Not Run | |

---

## Execution Results

**Execution Date:** {date}
**Executed By:** {agent nickname}
**Environment:** {dev/staging/prod}

| Metric | Value |
|--------|-------|
| Total Tests | {X} |
| Passed | {X} |
| Failed | {X} |
| Blocked | {X} |
| Pass Rate | {X}% |

### Failed Tests

| Test Case | Failure Reason | Screenshot | Recommended Action |
|-----------|----------------|------------|-------------------|
| TC-XXX | {reason} | {link if any} | {action} |

---

## Notes

- {any additional notes about testing}
