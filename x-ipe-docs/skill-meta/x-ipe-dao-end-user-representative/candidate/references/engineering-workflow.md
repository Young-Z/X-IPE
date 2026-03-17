# Engineering Workflow Reference

DAO uses this reference in Step 2.1 to suggest the engineering-correct next skill — not just keyword-matched, but process-aware.

## Stage Pipeline

```
IDEATION → REQUIREMENT → IMPLEMENT → VALIDATION → FEEDBACK
(shared)    (shared)      (per-feat)  (per-feat)   (per-feat)
```

## Stage Actions & Skill Mapping

### Stage 1: IDEATION (shared)

| Action | Skill | Required | Next Actions |
|--------|-------|----------|--------------|
| compose_idea | x-ipe-task-based-ideation | yes | refine_idea, reference_uiux |
| reference_uiux | (UIUX reference workflow) | no | design_mockup, refine_idea |
| refine_idea | x-ipe-task-based-ideation | yes | design_mockup, requirement_gathering |
| design_mockup | x-ipe-task-based-idea-mockup | no | requirement_gathering |
| (architecture) | x-ipe-task-based-idea-to-architecture | no | requirement_gathering |
| (share) | x-ipe-task-based-share-idea | no | TERMINAL |

### Stage 2: REQUIREMENT (shared)

| Action | Skill | Required | Next Actions |
|--------|-------|----------|--------------|
| requirement_gathering | x-ipe-task-based-requirement-gathering | yes | feature_breakdown |
| feature_breakdown | x-ipe-task-based-feature-breakdown | yes | → enters IMPLEMENT per feature |

### Stage 3: IMPLEMENT (per feature)

| Action | Skill | Required | Next Actions |
|--------|-------|----------|--------------|
| feature_refinement | x-ipe-task-based-feature-refinement | yes | technical_design |
| technical_design | x-ipe-task-based-technical-design | yes | code_implementation |
| code_implementation | x-ipe-task-based-code-implementation | yes | → enters VALIDATION |

### Stage 4: VALIDATION (per feature)

| Action | Skill | Required | Next Actions |
|--------|-------|----------|--------------|
| acceptance_test | x-ipe-task-based-feature-acceptance-test | yes | code_refactor |
| code_refactor | x-ipe-task-based-code-refactor | no | feature_closing |
| feature_closing | x-ipe-task-based-feature-closing | yes | → enters FEEDBACK |

### Stage 5: FEEDBACK (per feature)

| Action | Skill | Required | Next Actions |
|--------|-------|----------|--------------|
| bug_fix | x-ipe-task-based-bug-fix | no | acceptance_test (re-enters VALIDATION) |
| human_playground | x-ipe-task-based-human-playground | no (human-initiated only) | change_request |
| change_request | x-ipe-task-based-change-request | no | feature_refinement or feature_breakdown |

## Standalone Skills (any-time entry)

| Skill | Purpose |
|-------|---------|
| x-ipe-task-based-dev-environment | Set up dev environment |
| x-ipe-task-based-project-init | Initialize project structure |
| x-ipe-task-based-user-manual | Create/update README |
| x-ipe-task-based-doc-viewer | Generate doc viewer (TERMINAL) |

## Feedback Loops

```
Quality loop:    acceptance_test → code_refactor → feature_closing → acceptance_test
Discovery loop:  human_playground → bug_fix → acceptance_test
Scope loop:      change_request → feature_refinement (or feature_breakdown)
```

## How DAO Uses This

In Step 2.1 (Scan Skills), after keyword-matching, also check:

1. **Current position:** What stage/action did the user just complete or is working on?
2. **Engineering next:** What does the workflow DAG say comes next?
3. **Alignment:** Does the keyword-matched skill align with the engineering-correct next step?

Priority: If keyword match and engineering-next agree → high confidence.
If they conflict → flag in rationale, prefer engineering-next unless user explicitly overrides.
