# DAO Decisions — Remediation Phase (26-03-12)

---

## DAO-053
- **Timestamp:** 2026-03-12T00:00:00Z
- **Task ID:** TASK-848
- **Feature ID:** N/A
- **Workflow:** Knowledge-Base-Implementation
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** critique
- **Confidence:** 0.95

### Message
> for UI testing why you didn't call chrome-devtools mcp?

### 3-Perspective Analysis

| Perspective | Assessment |
|-------------|-----------|
| **🧑 Supporting** | User is right to question this. The acceptance test skill (`x-ipe-task-based-feature-acceptance-test`) explicitly mandates: "For frontend-ui tests, Chrome DevTools MCP is required." The tools.json config has `chrome-devtools-mcp: true`. The specification.md files classify multiple ACs as `frontend-ui` test type. The agent had every signal to use chrome-devtools-mcp and did not. |
| **🤖 Opposing** | The agent achieved 100% pass rate across all 6 features using vitest and pytest. All tests pass. The functional correctness may be covered even without browser-based testing. Chrome DevTools MCP testing adds complexity and may not find additional bugs if unit tests already cover the logic. |
| **⚖️ Neutral** | The skill spec is unambiguous — `frontend-ui → chrome-devtools-mcp (if enabled)`. It is enabled. The agent deviated from the skill's mandatory procedure. Passing unit tests do NOT substitute for browser-based UI testing: unit tests verify logic in isolation, while chrome-devtools-mcp verifies rendered DOM, user interaction flows, visual rendering, and end-to-end browser behavior. The 100% pass rate is real but incomplete — it covers backend-api, unit, and integration test types but NOT the frontend-ui test type. This is a procedural gap, not a test failure. |

### Phase 2: 致知 — Understanding

**Skill Scan:**
- `x-ipe-task-based-feature-acceptance-test` (strong match) — this is the skill that was executed in TASK-848. Its procedure explicitly states:
  - Test type classification: `frontend-ui → chrome-devtools-mcp (if enabled)`
  - MANDATORY rule: "For frontend-ui tests, Chrome DevTools MCP is required. If chrome-devtools-mcp is disabled in tools.json or MCP is not available, generate test cases but mark UI test execution as blocked."
  - tools.json has `chrome-devtools-mcp: true` under `quality.testing`
- **Engineering workflow position:** VALIDATION stage → `acceptance_testing` action. The agent completed this action but with incomplete tool coverage. The correct remediation is to re-run acceptance testing for frontend-ui classified ACs using chrome-devtools-mcp.

**Disposition Reasoning:**
- `critique` selected because the user is pointing out a procedural deviation, not asking a question or giving a new instruction. The agent failed to follow a MANDATORY rule in the skill it was executing. The DAO must acknowledge this gap clearly and provide corrective guidance.
- NOT `answer` — this is not a neutral information request; the user is flagging a mistake.
- NOT `instruction` — the user hasn't yet commanded a re-run; they're asking WHY it wasn't done.

### Guidance Returned
> The agent did not use chrome-devtools-mcp for frontend-ui acceptance testing, which is a procedural deviation from the `x-ipe-task-based-feature-acceptance-test` skill. The skill mandates: `frontend-ui → chrome-devtools-mcp (if enabled)`, and tools.json confirms `chrome-devtools-mcp: true`. The agent used only vitest (unit/integration) and pytest (backend) — these cover backend-api, unit, and integration test types but do NOT substitute for browser-based UI testing. Frontend-ui ACs (DOM rendering, click interactions, form submissions, visual state) require actual browser execution via chrome-devtools-mcp to be properly validated. The 100% pass rate reported is accurate for the test types that WERE executed, but frontend-ui test type ACs remain unvalidated. **Corrective action:** Re-run acceptance testing for all features that have `frontend-ui` classified ACs, this time routing those specific ACs through chrome-devtools-mcp as the skill requires. The agent should: (1) identify all ACs with Test Type = `frontend-ui` across the 6 features, (2) for each, execute browser-based validation using chrome-devtools-mcp (navigate to page, interact with UI elements, verify rendered output), (3) update acceptance-test-cases.md with browser-test results.

### Rationale
> `critique` — user correctly identified that the agent skipped a mandatory tool routing rule in the acceptance test skill. chrome-devtools-mcp was enabled in tools.json, frontend-ui ACs exist in specs, but the agent used only vitest/pytest. Unit tests ≠ browser tests. This is a skill compliance gap that must be remediated by re-running frontend-ui ACs through chrome-devtools-mcp.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-acceptance-test"
>     match_strength: "strong"
>     reason: "Re-run frontend-ui classified ACs using chrome-devtools-mcp as the skill mandates"
>     execution_steps:
>       - phase: "2. Generate Test Cases"
>         step: "2.1 Classify ACs by Test Type"
>       - phase: "3. Execute Tests"
>         step: "3.1 Route frontend-ui tests to chrome-devtools-mcp"

### Execution Plan

| Field | Value |
|-------|-------|
| **Strategy** | `sequential` |
| **Groups** | `[[0]]` |
| **Rationale** | Single instruction unit — critique with corrective guidance. Downstream agent should re-run acceptance testing for frontend-ui ACs using chrome-devtools-mcp. |

### Follow-up
> Agent should re-run acceptance testing specifically for frontend-ui test type ACs across all 6 MVP features using chrome-devtools-mcp. Backend-api, unit, and integration test results from the prior run remain valid and do not need re-execution.

---

### DAO-054 — Replace native dialogs with Bootstrap 5 modals

| Field | Value |
|-------|-------|
| **Timestamp** | 2026-03-12T13:45:00Z |
| **Source** | human |
| **Task ID** | TASK-849 |
| **Feature ID** | EPIC-049 (cross-cutting) |
| **Workflow** | Knowledge-Base-Implementation |
| **Disposition** | instruction |
| **Confidence** | 0.85 |

**User Need:** Replace all native browser dialogs (alert, confirm, prompt) across the application with Bootstrap 5 styled modal dialogs for consistent UI.

**Unit 0 — instruction:**
Replace all native `alert()`, `confirm()`, and `prompt()` calls with custom Bootstrap 5 modal dialogs. Scope: KB features first (kb-article-editor.js has 1 confirm), then broader codebase (workplace.js has 6, content-editor.js has 3, folder-view.js has 1, quality-evaluation.js has 2, tracing-dashboard.js has 1, kb-article-editor.js has 1). Note: workflow-stage.js and workflow.js already have `_showConfirmModal()` and `_showPromptModal()` implementations that can serve as patterns. This is a change request — use x-ipe-task-based-change-request skill to properly scope and implement.

**Rationale:** User explicitly requested Bootstrap 5 modals over native dialogs. Native dialogs are visually inconsistent with the dark-themed UI. Existing modal patterns in workflow code prove feasibility.
