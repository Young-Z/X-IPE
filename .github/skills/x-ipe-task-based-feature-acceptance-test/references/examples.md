# Feature Acceptance Test Examples

> **Legacy Note:** Examples below use the Epic-aware folder structure (`EPIC-{nnn}/FEATURE-{nnn}-{X}/`). Projects created before the Epic migration may still use the legacy format (`FEATURE-{nnn}/`). Both formats are supported during the transition period.

This document provides concrete execution examples for the Feature Acceptance Test skill.

---

## Example 1: Full-Stack Feature (UI + Backend)

**Context:** FEATURE-049-A: KB Backend & Storage Foundation — has both backend API and is consumed by frontend.

### Step 1.1: Load Toolbox Config

```
Read x-ipe-docs/config/tools.json → stages.validation.acceptance_test:
  chrome-devtools-mcp: true
  x-ipe-tool-implementation-python: true
  x-ipe-tool-implementation-typescript: true
  (others enabled)

enabled_tools:
  frontend_ui_tool: chrome-devtools-mcp ✓
  code_test_tools: [python, typescript, ...] ✓
```

### Step 1.2: Classify & Generate Test Plan

```
Read specification.md → ACs:
  AC-1: System creates kb-articles directory on startup
  AC-2: User can create article via POST /api/kb/articles
  AC-3: User can list articles via GET /api/kb/articles
  AC-4: Article editor modal displays when clicking "New Article"
  AC-5: User can save article with title, content, and tags

Classification:
  AC-1 → test_type: unit         (file system setup logic)
  AC-2 → test_type: backend-api  (POST endpoint)
  AC-3 → test_type: backend-api  (GET endpoint)
  AC-4 → test_type: frontend-ui  (modal interaction)
  AC-5 → test_type: frontend-ui  (form submission)

Tool Assignment:
  TC-001 (AC-1) → x-ipe-tool-implementation-python (pytest)
  TC-002 (AC-2) → x-ipe-tool-implementation-python (pytest + httpx)
  TC-003 (AC-3) → x-ipe-tool-implementation-python (pytest + httpx)
  TC-004 (AC-4) → chrome-devtools-mcp
  TC-005 (AC-5) → chrome-devtools-mcp
```

### Step 2.1: Analyze Implementation

```
backend-api group:
  - POST /api/kb/articles → src/x_ipe/routes/kb_routes.py:create_article
    Request: {"title": str, "content": str, "tags": [str]}
    Response: 201 {"id": str, "title": str, ...}
  - GET /api/kb/articles → src/x_ipe/routes/kb_routes.py:list_articles
    Response: 200 [{"id": str, "title": str, ...}]

frontend-ui group:
  - "New Article" button: #kb-new-article-btn
  - Article editor modal: #kb-article-editor-modal
  - Title input: #article-title
  - Content editor: .EasyMDEContainer
  - Save button: #save-article-btn
```

### Step 4.1: Execute Tests

```
=== backend-api group (pytest) ===
TC-001: test_kb_directory_creation → PASS
TC-002: test_create_article_api → PASS
TC-003: test_list_articles_api → PASS

=== frontend-ui group (chrome-devtools-mcp) ===
TC-004: Navigate → click #kb-new-article-btn → verify modal visible → PASS
TC-005: Fill form → click save → verify success → PASS
```

### Step 4.2: Report

```yaml
results_by_type:
  unit: { passed: 1, failed: 0, blocked: 0 }
  backend_api: { passed: 2, failed: 0, blocked: 0 }
  frontend_ui: { passed: 2, failed: 0, blocked: 0 }
total: 5, passed: 5, pass_rate: 100%
```

---

## Example 2: Backend-Only Feature

**Context:** FEATURE-018: CLI Tool — no frontend component at all.

### Step 1.1: Load Toolbox Config

```
enabled_tools: {chrome-devtools-mcp: true, python: true, ...}
```

### Step 1.2: Classify & Generate Test Plan

```
Read specification.md → ACs:
  AC-1: CLI accepts --init flag to create project
  AC-2: CLI validates config file format
  AC-3: CLI returns exit code 1 on error

Classification:
  AC-1 → test_type: integration  (CLI + file system)
  AC-2 → test_type: unit         (config validation logic)
  AC-3 → test_type: unit         (error handling)

Note: NO frontend-ui tests. chrome-devtools-mcp not needed.

Tool Assignment:
  TC-001 (AC-1) → x-ipe-tool-implementation-python
  TC-002 (AC-2) → x-ipe-tool-implementation-python
  TC-003 (AC-3) → x-ipe-tool-implementation-python
```

### Final Output

```yaml
Output:
  status: completed
  test_types_tested: ["unit", "integration"]
  test_cases_created: 3
  tests_passed: 3
  tests_failed: 0
  pass_rate: "100%"
  results_by_type:
    frontend_ui: { passed: 0, failed: 0, blocked: 0 }
    backend_api: { passed: 0, failed: 0, blocked: 0 }
    unit: { passed: 2, failed: 0, blocked: 0 }
    integration: { passed: 1, failed: 0, blocked: 0 }
```

---

## Example 3: Frontend-UI Tests Blocked (MCP Disabled)

**Context:** FEATURE-010: Dashboard — tools.json has `chrome-devtools-mcp: false`.

### Step 1.1: Load Toolbox Config

```
Read tools.json → stages.validation.acceptance_test:
  chrome-devtools-mcp: false  ← DISABLED
  x-ipe-tool-implementation-python: true

enabled_tools:
  frontend_ui_tool: NONE (chrome-devtools-mcp disabled)
  code_test_tools: [python]
```

### Step 1.2: Classify

```
AC-1: Dashboard loads with charts → frontend-ui → chrome-devtools-mcp → BLOCKED (disabled)
AC-2: API returns dashboard data → backend-api → python → OK
AC-3: Data refresh updates charts → frontend-ui → chrome-devtools-mcp → BLOCKED

Tool Assignment:
  TC-001 (AC-1) → blocked (chrome-devtools-mcp disabled)
  TC-002 (AC-2) → x-ipe-tool-implementation-python
  TC-003 (AC-3) → blocked (chrome-devtools-mcp disabled)
```

### Final Output

```yaml
Output:
  status: completed  # Ran what we could
  test_cases_created: 3
  tests_passed: 1
  tests_failed: 0
  tests_blocked: 2
  pass_rate: "50%"
  results_by_type:
    frontend_ui: { passed: 0, failed: 0, blocked: 2 }
    backend_api: { passed: 1, failed: 0, blocked: 0 }
```

---

## Example 4: Mixed Results with Failures

**Context:** FEATURE-022-C: Feedback Capture — has UI and API tests, some failures.

### Step 4.1: Execute

```
=== backend-api (pytest) ===
TC-001: POST /api/feedback → 201 → PASS
TC-002: GET /api/feedback → 200 → PASS

=== frontend-ui (chrome-devtools-mcp) ===
TC-003: Right-click context menu → PASS
TC-004: Panel opens with screenshot → PASS
TC-005: Submit feedback form → FAIL (timeout waiting for success message)
TC-006: Export feedback → FAIL (modal never appeared)
```

### Step 4.2: Report

```markdown
| Type | Total | Passed | Failed | Blocked |
|------|-------|--------|--------|---------|
| backend-api | 2 | 2 | 0 | 0 |
| frontend-ui | 4 | 2 | 2 | 0 |
| **TOTAL** | 6 | 4 | 2 | 0 |
| **Pass Rate** | | 67% | | |

### Failed Tests
| Test Case | Type | Failure Reason | Recommended Action |
|-----------|------|----------------|-------------------|
| TC-005 | frontend-ui | Timeout for success message | Check submit handler |
| TC-006 | frontend-ui | Export modal not rendered | Check export implementation |
```
