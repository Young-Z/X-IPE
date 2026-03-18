---
skill: x-ipe-task-based-code-implementation
last_updated: 2026-03-18
---

# Lesson Learned — x-ipe-task-based-code-implementation

## LL-001

| Field | Value |
|-------|-------|
| ID | LL-001 |
| Date | 2026-03-18 |
| Severity | major |
| Status | raw |
| Task ID | TASK-976 |
| Feature | FEATURE-049-F (CR-008) |

### Context

Agent implemented CR-008: extracted shared FilePreviewRenderer and refactored two consumers (kb-browse-modal.js, deliverable-viewer.js) to delegate to it. In `kb-browse-modal.js`, agent added `await this._filePreviewRenderer.renderPreview(...)` inside `_renderArticleScene()` without checking whether the method was declared `async`.

### Observed Behavior

Agent added `await` on line 637 of `kb-browse-modal.js` inside `_renderArticleScene(data)` which was declared as a synchronous method (no `async` keyword). The Vitest test suite (859 tests) passed because jsdom evaluates scripts differently and doesn't enforce browser-level `async/await` syntax rules. The bug only manifested at runtime in the browser as:

```
Uncaught SyntaxError: await is only valid in async functions and the top level bodies of modules
```

### Expected Behavior

When adding `await` calls inside an existing method, the agent MUST:

1. Check if the method is already declared `async`
2. If NOT async, either:
   a. Add `async` to the method declaration
   b. Verify the caller can handle an async return (i.e., `await`s the call or doesn't depend on sync completion)
3. Check the call chain upward — if the caller also needs to `await`, make it async too

### Ground Truth

**Rule:** Before inserting `await` into any function/method body, ALWAYS verify the function is declared `async`. This is a mechanical pre-flight check:

```
✅ Pre-flight: Adding await to method X
  1. Is X declared async? → if NO, add async keyword
  2. Does caller Y of X need the result synchronously? → if YES, add await + async to Y
  3. Repeat up the call chain until reaching an event handler or top-level
```

**Correct implementation for CR-008:**
```javascript
// Line 516: caller must await
await this._renderArticleScene(data);

// Line 522: method must be async
async _renderArticleScene(data) {
```

### Proposed Improvement

```yaml
type: update_instruction
target: "Execution Procedure, code modification steps"
description: |
  Add async/await pre-flight check: When inserting `await` into an existing
  function or method, ALWAYS verify the function is declared `async` first.
  Check the call chain upward — if callers need to await, propagate async.
  This is a mechanical verification that prevents SyntaxError in browsers.

  Suggested addition to implementation checklist:
  "PRE-FLIGHT CHECK — async/await propagation: Before adding `await` to
  any function body, verify: (1) function has `async` keyword, (2) callers
  that need the result use `await`, (3) async propagates up the call chain
  to an event handler or top-level scope."

proposed_ac:
  - id: AC-NEW
    description: "All await insertions verify async declaration on containing function"
    test_method: code_review
    expected: "No await used in non-async functions"
```
