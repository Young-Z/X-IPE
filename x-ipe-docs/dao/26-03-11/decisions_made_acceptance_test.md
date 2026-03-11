# DAO Decisions — Acceptance Test

> Semantic task type: `acceptance_test`
> Date: 26-03-11

---

## DAO-039 — Revert skip & re-execute acceptance testing for FEATURE-049-A

| Field | Value |
|-------|-------|
| **Decision ID** | DAO-039 |
| **Timestamp** | 2026-03-11T11:15:00Z |
| **Source** | human |
| **Calling Skill** | x-ipe-task-based-feature-acceptance-test |
| **Task ID** | TASK-838 |
| **Feature ID** | FEATURE-049-A |
| **Workflow** | Knowledge-Base-Implementation |
| **Disposition** | `instruction` |
| **Confidence** | 0.95 |

### Context

The human updated `.github/skills/x-ipe-task-based-feature-acceptance-test/SKILL.md` to support ALL feature types (`frontend-ui`, `backend-api`, `unit`, `integration`), replacing the old logic that skipped backend-only features. The agent had already set FEATURE-049-A `acceptance_testing → skipped` under the old rule. Human directed: *"I have updated ac test scope, now you shall continue."*

### Decision

1. **Revert** workflow action `acceptance_testing` for FEATURE-049-A from `skipped` → `pending`.
2. **Instruct** downstream agent to invoke `x-ipe-task-based-feature-acceptance-test` for FEATURE-049-A using the updated skill definition.
3. The updated skill will classify all 11 AC groups (40+ individual ACs) by test type and route to appropriate testing tools per `tools.json` config.

### Rationale

- Human gave an explicit directive — no ambiguity.
- FEATURE-049-A is the foundation feature (12 REST endpoints, 11 AC groups). Skipping its acceptance testing leaves all downstream features (B–G) on an unvalidated base.
- The updated skill now correctly handles backend-api testing via classification and tool routing.
- Workflow integrity requires correcting stale state when the governing rules change.

### Perspectives Considered

| Perspective | Position | Weight |
|-------------|----------|--------|
| QA advocate (supporting) | Backend foundation must be tested; 40+ ACs unvalidated | High |
| Velocity advocate (opposing) | Adds testing cycle; but human explicitly directed it | Low (overruled) |
| Process expert (neutral) | `skipped → pending` is valid transition; rules changed | Neutral-positive |

### Workflow Action Taken

- `update_workflow_action(workflow=Knowledge-Base-Implementation, feature=FEATURE-049-A, action=acceptance_testing, status=pending)` — ✅ Success

---

## DAO-040 — Revert feature_closing & execute skipped code_refactor for FEATURE-049-A and FEATURE-049-B

| Field | Value |
|-------|-------|
| **Decision ID** | DAO-040 |
| **Timestamp** | 2026-03-11T12:05:00Z |
| **Source** | human |
| **Calling Skill** | x-ipe-task-based-feature-closing |
| **Task ID** | TASK-838 |
| **Feature ID** | FEATURE-049-A, FEATURE-049-B |
| **Workflow** | Knowledge-Base-Implementation |
| **Disposition** | `instruction` |
| **Confidence** | 0.97 |

### Context

The workflow validation stage defines 3 ordered actions per feature: `acceptance_testing` → `code_refactor` → `feature_closing`. For both FEATURE-049-A and FEATURE-049-B, the agent completed `acceptance_testing` (which explicitly set `next_actions_suggested: ["code_refactor"]`) but jumped directly to `feature_closing`, leaving `code_refactor` in `pending` state. The human flagged: *"why refactor action has been missed?"*

Evidence of the skip:
- Workflow state: `acceptance_testing.next_actions_suggested = ["code_refactor"]` — agent ignored this signal
- Workflow state: `code_refactor.status = "pending"` with no deliverables for both A and B
- Workflow state: `feature_closing.status = "done"` — executed out of order
- The `x-ipe-task-based-feature-closing` skill Phase 3, Step 3.2 ("Refactoring Analysis") invokes `x-ipe-tool-refactoring-analysis` — this analysis step within closing depends on code_refactor having been executed first
- The `x-ipe-task-based-code-refactor` skill is a full end-to-end refactoring cycle (analyze → sync docs → plan → execute → validate) that was entirely skipped

### Decision

1. **Revert** workflow action `feature_closing` for FEATURE-049-A from `done` → `pending`.
2. **Revert** workflow action `feature_closing` for FEATURE-049-B from `done` → `pending`.
3. **Instruct** downstream agent to execute `code_refactor` for FEATURE-049-A first (foundation feature), then FEATURE-049-B, using the `x-ipe-task-based-code-refactor` skill.
4. **After** `code_refactor` completes for each feature, **re-execute** `feature_closing` with the `x-ipe-task-based-feature-closing` skill — Step 3.2 will now have actual refactoring results to analyze.
5. The corrected execution order must be: `code_refactor(A)` → `code_refactor(B)` → `feature_closing(A)` → `feature_closing(B)`.

### Rationale

- The workflow engine's `next_actions_suggested` is a sequencing directive, not a suggestion — the agent must not skip actions in the validation pipeline.
- `code_refactor` is a quality gate: it catches design debt, test gaps, and doc drift before closing. Skipping it means features ship without quality validation.
- FEATURE-049-A is the foundation layer (KB service, routes, 12 REST endpoints). Unrefactored foundation code propagates technical debt to all 6 downstream features (B–G).
- FEATURE-049-B depends on A — both must be refactored in dependency order.
- `feature_closing` must be re-run because its Step 3.2 (refactoring analysis) should reflect the actual refactoring outcome, not run on un-refactored code.

### Perspectives Considered

| Perspective | Position | Weight |
|-------------|----------|--------|
| QA advocate (supporting) | Validation stage exists to catch quality issues; skipping code_refactor defeats purpose | High |
| Process integrity (supporting) | `next_actions_suggested` is a sequencing contract; violations corrupt workflow state | High |
| Velocity advocate (opposing) | Re-running feature_closing adds overhead; but correctness > speed for foundation features | Low (overruled) |
| Architecture advocate (supporting) | Foundation feature (A) must be clean before downstream features build on it | High |

### Workflow Actions Taken

- `update_workflow_action(workflow=Knowledge-Base-Implementation, feature=FEATURE-049-A, action=feature_closing, status=pending)` — ✅ Success
- `update_workflow_action(workflow=Knowledge-Base-Implementation, feature=FEATURE-049-B, action=feature_closing, status=pending)` — ✅ Success
- Next: Agent must execute `code_refactor` for A, then B, then re-close both

---

## DAO-003

### Registry

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-003 | 2026-03-11T12:00:00Z | TASK-838 | human-direct | instruction | 0.85 | Execute acceptance testing + refactoring for FEATURE-049-E |

### Detail

> **Timestamp:** 2026-03-11T12:00:00Z
> **Task ID:** TASK-838
> **Feature ID:** FEATURE-049-E
> **Workflow:** N/A
> **Calling Skill:** human-direct
> **Source:** human
> **Disposition:** instruction (2 units)
> **Confidence:** 0.85

### Original Message
> Execute acceptance testing + refactoring for FEATURE-049-E (KB File Upload)

### Guidance Returned
> Unit 1: Proceed with acceptance testing using x-ipe-task-based-feature-acceptance-test. Derive ACs from implementation since no specification.md exists.
> Unit 2: Proceed with refactoring using x-ipe-task-based-code-refactor. Evaluate kb-file-upload.js quality, apply safe refactoring if < 7.

### Rationale
> Both tasks are in VALIDATION stage per engineering workflow. TASK-838 is active and covers this work. No specification exists but user explicitly allows deriving ACs from implementation files.

### Suggested Skills
> - x-ipe-task-based-feature-acceptance-test (strong match, Unit 1)
> - x-ipe-task-based-code-refactor (strong match, Unit 2)

### Follow-up
> Quality loop: if refactoring changes code, re-run acceptance tests
