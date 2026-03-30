---
skill: x-ipe-task-based-code-implementation
last_updated: 2026-03-30
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

---

## LL-002

| Field | Value |
|-------|-------|
| ID | LL-002 |
| Date | 2026-03-30 |
| Severity | critical |
| Status | raw |
| Task ID | TASK-1025 |
| Feature | FEATURE-052-D (Skill Migration & MCP Removal) |

### Context

Agent (Sage 🌿) was implementing FEATURE-052-D which required updating 17 skill SKILL.md files to replace MCP tool references with standalone script invocations. Agent used a Python batch-replacement script to directly edit all 17 production files in `.github/skills/*/SKILL.md`, plus created a new `x-ipe-tool-x-ipe-app-interactor/SKILL.md` directly in the production folder.

### Observed Behavior

Agent directly edited 17 files under `.github/skills/` and created 1 new SKILL.md there — all without going through the mandatory candidate→validate→merge process via `x-ipe-meta-skill-creator`. The changes were committed to main without candidate folder validation.

This violates the Copilot Instructions rule:
> ⛔ **NEVER directly edit files in `.github/skills/{skill-name}/`.** All changes MUST be made in the candidate folder (`x-ipe-docs/skill-meta/{skill-name}/candidate/`) first, validated, then merged to production.

### Expected Behavior

1. For the **new** skill (`x-ipe-tool-x-ipe-app-interactor`): invoke `x-ipe-meta-skill-creator` to scaffold the candidate folder, create SKILL.md there, validate, then merge to production.
2. For the **17 updated** skills: create candidate copies, apply text replacements there, validate against skill-creator checklist, then merge each to production.
3. Only after candidate validation should production `.github/skills/` files be touched.

### Ground Truth

The correct workflow for any skill modification is:

```
1. Load x-ipe-meta-skill-creator skill
2. Create/update in x-ipe-docs/skill-meta/{skill-name}/candidate/SKILL.md
3. Validate against skill-creator checklist
4. Merge candidate → .github/skills/{skill-name}/SKILL.md
5. Commit
```

For batch operations affecting many skills (like this migration), each skill's candidate should be prepared, but the validation and merge can be batched.

### Improvement Proposal

```yaml
type: update_instruction
target: x-ipe-task-based-code-implementation/SKILL.md
section: "Execution Procedure → implementation step"
description: |
  Add a pre-edit gate check: "IF any target files are under `.github/skills/*/`,
  STOP — these are skill files. Route through x-ipe-meta-skill-creator candidate
  process before editing. Direct edits to production skill files are forbidden."
severity: critical
```

### Test Case

```yaml
test:
  id: TC-LL-002
  scenario: "Implementation task modifies SKILL.md files"
  given: "Task requires editing files under .github/skills/"
  when: "Agent reaches the implementation step"
  then: "Agent routes skill file changes through x-ipe-meta-skill-creator candidate process"
  description: "Skill file edits must go through candidate folder validation"
  test_method: process_review
  expected: "No direct edits to .github/skills/*/SKILL.md without candidate validation"
```
