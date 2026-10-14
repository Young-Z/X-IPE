# Goal extension metadata — workflow (candidate only)

Supplement to the existing template-derived metadata; retain all prior domain
acceptance criteria, inputs/outputs and published history. No version bump or
ownership claim is made by this supplement.

```yaml
skill_name: x-ipe-workflow-task-execution
skill_type: x-ipe-workflow-orchestration
status: candidate
publication_state: candidate_ready
task_id: TASK-6749
updated: 2026-10-13
summary: Document-local goal and outcome-evidence contract with explicit child adoption.
workflow:
  phases: [Orient, Plan, Execute, Verify, Record]
  human_review: main independent reviewer before any promotion
inputs: {contract: unchanged original Task Data Model}
outputs: {contract: unchanged original output aggregate and child schemas}
acceptance_criteria:
  must:
    - {id: AC-G01, criterion: Source-parent-stakeholder-outcome frame with stable reused IDs and qualitative evidence, test: parsed artifact chain and scaffold rendering}
    - {id: AC-G02, criterion: All-required versus selected bounded alternatives with credible enabling contribution, test: authored breakdown scenario plus descriptive downstream contract review}
    - {id: AC-G03, criterion: Delivery distinct from not measured or observed stakeholder outcome; legacy inference and authorized delta invalidation, test: new/legacy/delta and negative claim fixtures}
    - {id: AC-G04, criterion: Adoption optional until child domain gate; no schema or approval ritual change, test: exact parsed outputs and adoption boundary guidance tests}
    - {id: AC-G05, criterion: Production unchanged; complete resource delta and current receipts, test: fresh manifests plus installed validator}
dependencies:
  artifacts: [candidate/references/goal-contract.md, baseline-goal-TASK-6749.json]
test_scenarios:
  happy_path: [new authored goal-to-AC-to-evidence chain, rendered existing scaffold]
  edge_cases: [legacy explicit so-that inference, bounded parent delta, alternative not built]
  error_cases: [orphan AC, missing evidence, fabricated delivery/outcome, missing GWT, duplicate ID]
evaluation:
  risk: meaningful workflow semantics; independent review required
  independent_review: awaiting_main_independent_reviewer
  selected_lessons: []
  production_baseline_sha256: 90b220f8d92463eae43e18f7f2157c1cfd6ecb90a6f7fce0531173233186ed25
  prework_candidate: identical to fresh production baseline
  validation_receipt: validation-receipt-goal-TASK-6749.json
  tests: 303 passed / 0 failed across goal, pipeline, lifecycle and creator foundation suites
  behavior_limit: authored/rendered artifacts and CLI compatibility do not prove autonomous goal seeking or stakeholder outcomes
  promotion: prohibited in this scope
```

Plan executed sequentially: shared contract → requirement → breakdown → refinement,
with installed validation before each successor. Candidate delta: 1 added, 3
changed, 0 removed; 6 package files / 250 body lines. Prior production remains
the fresh baseline after its earlier promotion, not the historical baseline.
No board/memory/Git/source-document edits. No independent review is claimed.

Promotion requires a separately authorized, current-revision main independent
review. Child staged goal links must be reconciled to the reviewed canonical
shared reference after its authorized publication; rerun validation/tests and
review affected dependencies before any child promotion. No publication run here.