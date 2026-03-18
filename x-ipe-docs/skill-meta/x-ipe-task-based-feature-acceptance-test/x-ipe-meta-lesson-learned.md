---
skill: x-ipe-task-based-feature-acceptance-test
last_updated: 2026-03-18
---

# Lesson Learned — x-ipe-task-based-feature-acceptance-test

## LL-001

| Field | Value |
|-------|-------|
| ID | LL-001 |
| Date | 2026-03-18 |
| Severity | major |
| Status | raw |
| Task ID | TASK-977 |
| Feature | FEATURE-049-F (CR-008) |

### Context

Agent executed acceptance testing for CR-008 (shared FilePreviewRenderer). 16 ACs were classified: 13 as "unit" and 3 as "frontend-ui" (AC-18m, 18n, 18o). All unit tests passed (36 tests via Vitest). The 3 UI-classified ACs were verified via **source code review** instead of Chrome DevTools MCP, even though Chrome DevTools MCP was enabled in tools.json.

### Observed Behavior

Agent classified AC-18m, 18n, 18o as "UI (code review)" and verified them by reading source code to confirm FilePreviewRenderer was instantiated correctly in both consumers. Agent's rationale: "these ACs test code delegation patterns, not visual rendering."

This skipped the browser-based smoke test that would have immediately caught the `await`-in-non-async `SyntaxError` in `kb-browse-modal.js` — the method `_renderArticleScene()` was not declared `async` but used `await` inside it. jsdom/Vitest cannot detect this class of error because it evaluates scripts differently from a real browser.

### Expected Behavior

When ACs are classified as "frontend-ui" and Chrome DevTools MCP is enabled in tools.json, the skill procedure MANDATES using Chrome DevTools for browser-based testing. The agent should have:

1. Started the dev server
2. Navigated to the KB browse modal in Chrome
3. Opened a file to trigger the preview path
4. Observed the SyntaxError in browser console
5. Reported AC-18m as FAIL with the error

### Ground Truth

**Rule:** When Chrome DevTools MCP is enabled and ACs are classified as `frontend-ui`, the agent MUST perform at minimum a browser smoke test — navigate to the relevant page, trigger the feature path, and check the browser console for errors. Source code review alone is insufficient because:

- jsdom does not enforce `async/await` syntax rules the same way browsers do
- Script loading order issues only manifest in real browsers
- Runtime type errors from missing globals only appear in browser context

**Correct flow for AC-18m:**
1. Start app server
2. Chrome DevTools: navigate to KB browse page
3. Click an article to trigger `_renderArticleScene()` → `FilePreviewRenderer.renderPreview()`
4. Check console: SyntaxError detected → AC-18m FAIL
5. Report failure with error details → triggers bug fix before feature closing

### Proposed Improvement

```yaml
type: update_instruction
target: "Phase 4 Step 4.1, frontend-ui execution block"
description: |
  Add MANDATORY browser smoke test rule: When Chrome DevTools MCP is enabled,
  frontend-ui ACs MUST include a browser smoke test that navigates to the
  relevant page, triggers the feature interaction, and checks the browser
  console for errors. Source code review alone is NOT sufficient for
  frontend-ui classified ACs.

  Suggested addition to Step 4.1 frontend-ui block:
  "MANDATORY: Even if the AC appears to test code structure rather than
  visual rendering, a browser smoke test MUST be performed to catch
  runtime errors (SyntaxError, ReferenceError, TypeError) that jsdom
  cannot detect. At minimum: navigate → trigger feature → check console."

proposed_ac:
  - id: AC-NEW
    description: "Frontend-ui ACs always include browser console error check"
    test_method: smoke_test
    expected: "Browser console shows no errors after feature interaction"
```
