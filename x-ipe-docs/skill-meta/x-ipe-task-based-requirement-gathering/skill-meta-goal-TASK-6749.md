# Goal extension metadata — requirement gathering (candidate only)

Supplement to existing template-derived metadata: all prior domain acceptance,
required sections, input/output fields/order, safety gates and history retained.

```yaml
skill_name: x-ipe-task-based-requirement-gathering
skill_type: x-ipe-task-based
status: candidate
publication_state: candidate_ready
task_id: TASK-6749
updated: 2026-10-13
summary: Outcome frame and stable requirement-to-goal/source/evidence/constraint mapping in existing requirement details.
workflow:
  category: requirement-stage
  next_task_based_skill: existing conditional feature-breakdown suggestion
  human_review: existing mode/domain gates; main independent reviewer before promotion
inputs: {contract: unchanged original fields and exact interaction enum}
outputs: {contract: unchanged original task_completion_output including field order}
acceptance_criteria:
  must:
    - {id: AC-G01, criterion: Canonical template and compatible entry include outcome frame and requirement mapping, test: original domain tests extended plus rendered scaffold}
    - {id: AC-G02, criterion: Concrete requirement parent ID survives breakdown and refinement maps, test: parsed authored source-parent-subgoal-AC-evidence chain}
    - {id: AC-G03, criterion: Success scenario may be qualitative; new/changed coverage and outcome gaps honest, test: authored fixtures and negative unsupported claims}
    - {id: AC-G04, criterion: All prior domain contracts and fresh production baseline preserved, test: exact output equality and existing pipeline regressions}
dependencies:
  artifacts: [staged workflow candidate goal-contract.md, baseline-goal-TASK-6749.json]
test_scenarios:
  happy_path: [explicit request and FR-061-01 goal frame]
  edge_cases: [legacy source-labeled inference, parent CR delta, qualitative evidence]
  error_cases: [unsupported success claim, orphan goal-to-AC link]
evaluation:
  risk: meaningful requirement semantics; independent review required
  independent_review: awaiting_main_independent_reviewer
  selected_lessons: []
  production_baseline_sha256: fda78fe5234e0d054a4b720e0773ed30cac8f1e39a10215ce277882576ab294b
  prework_candidate: identical to fresh production baseline
  shared_goal_contract_sha256: fd007a0f946ee3ccf60507f88c898358de9ea045b18de6446b65079d62911074
  validation_receipt: validation-receipt-goal-TASK-6749.json
  tests: 303 passed / 0 failed across goal, pipeline, lifecycle and creator foundation suites
  warnings: 2 retained uninstantiated scaffold links; not runtime missing-artifact claims
  behavior_limit: authored fixture and template expressiveness; no autonomous requirement/confirmation pilot
  promotion: prohibited in this scope
```

Plan executed after shared contract validation, before breakdown. Delta: 0 added,
5 changed, 0 removed; 6 files / 253 body lines. File-splitting resource unchanged.
Historical promotion/validation receipts remain unchanged and are not fresh goal
evidence. No user-intent confirmation or outcome observation is fabricated.
Before any later publication, reconcile staged shared-reference links under main
independent review and rerun affected receipts/tests; no production promotion here.