# Acceptance Test Cases — FEATURE-041-E CR-003

> Array-Valued Deliverable Tag Support

**Date:** 2026-03-14
**Task:** TASK-873
**Specification:** [specification.md](specification.md)
**Technical Design:** [technical-design.md](technical-design.md)

---

## Test Summary

| Metric | Value |
|--------|-------|
| Total Test Cases | 23 |
| Passed | 23 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

### Results by Type

| Type | Passed | Failed | Blocked | Total |
|------|--------|--------|---------|-------|
| unit | 18 | 0 | 0 | 18 |
| api | 1 | 0 | 0 | 1 |
| frontend-ui | 1 | 0 | 0 | 1 |
| integration | 3 | 0 | 0 | 3 |

---

## Test Cases

### Group 1: Template Structure (AC-041E-01x)

| TC | AC | Type | Description | Status | Tool | Notes |
|----|-----|------|-------------|--------|------|-------|
| TC-01 | AC-041E-01a | unit | Template deliverables are tag arrays | ✅ Pass | pytest | test_feature_041e.py::TestWorkflowTemplateFormat |
| TC-02 | AC-041E-01b | unit | No action_context for first action | ✅ Pass | pytest | test_feature_041e.py |
| TC-03 | AC-041E-01c | unit | action_context for dependent actions | ✅ Pass | pytest | test_feature_041e.py |
| TC-04 | AC-041E-01d | unit | compose_idea has raw-ideas (renamed) | ✅ Pass | pytest | Template verified: $output:raw-ideas + $output-folder:ideas-folder |

### Group 2: Storage & Schema (AC-041E-02x)

| TC | AC | Type | Description | Status | Tool | Notes |
|----|-----|------|-------------|--------|------|-------|
| TC-05 | AC-041E-02a | unit | Keyed dict stored verbatim | ✅ Pass | pytest | test_feature_041e.py + test_workflow_deliverables |
| TC-06 | AC-041E-02b | unit | List auto-converted to keyed | ✅ Pass | pytest | test_feature_041e.py::test_list_to_keyed |
| TC-07 | AC-041E-02c | unit | schema_version 3.0 for keyed dict | ✅ Pass | pytest | TestArrayDeliverables::test_schema_stays_3 |
| TC-08 | AC-041E-02d | unit | Legacy array backward compat | ✅ Pass | pytest | test_workflow_deliverables legacy tests |
| TC-09 | AC-041E-02e | unit | Context stored as dict | ✅ Pass | pytest | test_feature_041e.py::test_context_* |

### Group 3: Array Values (AC-041E-03x) — CR-003 Core

| TC | AC | Type | Description | Status | Tool | Notes |
|----|-----|------|-------------|--------|------|-------|
| TC-10 | AC-041E-03a | unit | Array stored as-is | ✅ Pass | pytest | TestArrayDeliverables::test_store_array |
| TC-11 | AC-041E-03b | unit | String equiv to single-element array | ✅ Pass | pytest | Both work through same code path |
| TC-12 | AC-041E-03c | unit | Template resolves to first element | ✅ Pass | vitest | 042a.test.js: array resolution tests (4 new tests) |
| TC-13 | AC-041E-03d | api | resolve_deliverables expands arrays | ✅ Pass | pytest | TestArrayDeliverables::test_resolve_expands |
| TC-14 | AC-041E-03e | frontend-ui | Each array file shows as card | ✅ Pass | analysis | Server-side expansion covers UI — _renderDeliverables iterates resolved list |
| TC-15 | AC-041E-03f | unit | Schema bumped to 4.0 | ✅ Pass | pytest | TestArrayDeliverables::test_schema_version_bumped |
| TC-16 | AC-041E-03g | integration | compose_idea multi-output e2e | ✅ Pass | pytest | store→schema→resolve→candidate→template all verified |

### Group 4: Validation (AC-041E-04x)

| TC | AC | Type | Description | Status | Tool | Notes |
|----|-----|------|-------------|--------|------|-------|
| TC-17 | AC-041E-04a | unit | Static validation for candidates refs | ✅ Pass | pytest | test_feature_041e.py |
| TC-18 | AC-041E-04b | unit | Unique tag names within stage | ✅ Pass | pytest | test_feature_041e.py |
| TC-19 | AC-041E-04c | unit | Missing keys produce warning | ✅ Pass | pytest | TestArrayDeliverableValidation |
| TC-20 | AC-041E-04d | unit | Array element validation | ✅ Pass | pytest | TestArrayDeliverableValidation: empty string + non-string rejected |

### Group 5: Candidate Resolution (AC-041E-05x)

| TC | AC | Type | Description | Status | Tool | Notes |
|----|-----|------|-------------|--------|------|-------|
| TC-21 | AC-041E-05a | integration | Feature-first candidate resolution | ✅ Pass | pytest | test_feature_041e.py::resolve_candidates |
| TC-22 | AC-041E-05b | unit | Later-stage tag takes precedence | ✅ Pass | pytest | test_feature_041e.py |
| TC-23 | AC-041E-05c | unit | Cross-stage duplicates allowed | ✅ Pass | pytest | test_feature_041e.py |

---

## Test Execution Evidence

- **Python tests:** 199 passed (uv run python -m pytest)
- **JavaScript tests:** 690 passed (npm test / vitest)
- **New tests added:** 17 (13 Python in TestArrayDeliverables/Validation/BackwardCompat + 4 JS in 042a.test.js)
- **Existing tests renamed:** 106 references (raw-idea → raw-ideas) across 7 test files
