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
