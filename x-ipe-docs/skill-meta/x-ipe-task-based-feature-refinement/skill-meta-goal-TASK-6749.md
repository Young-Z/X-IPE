# Goal extension metadata — feature refinement (candidate only)

Supplement to existing template-derived metadata; preserve the entire prior
unpromoted refactor, all domain fields/gates, exact outputs and legacy history.

```yaml
skill_name: x-ipe-task-based-feature-refinement
skill_type: x-ipe-task-based
status: candidate
publication_state: candidate_ready
task_id: TASK-6749
updated: 2026-10-13
summary: Honest new/changed source-parent-subgoal-story-AC-validation coverage with outcome gaps in one specification.
workflow:
  category: feature-stage
  next_task_based_skill: existing conditional Technical Design suggestion
  human_review: existing completeness gate; main independent reviewer before promotion
inputs: {contract: unchanged original single-feature fields and exact interaction enum}
outputs: {contract: unchanged original task_completion_output fields and order}
acceptance_criteria:
  must:
    - {id: AC-G01, criterion: Existing complete specification scaffold maps goal/subgoal to source/stories/AC/evidence and outcome gaps, test: parsed examples plus actual rendered scaffold}
    - {id: AC-G02, criterion: New/changed leaf acceptance remains GWT and valid primary types; qualitative observable evidence allowed, test: parsed real tables and negative GWT/duplicate/claim defects}
    - {id: AC-G03, criterion: Legacy explicit so-that inference source-labeled with historical prose/AC unchanged, test: exact actual FEATURE-047-A source-line comparison}
    - {id: AC-G04, criterion: Parent CR delta keeps stable IDs/unaffected AC and invalidates affected evidence, test: parsed old/new authored delta fixtures}
    - {id: AC-G05, criterion: No fixed minimum or three-goal cap; means adaptable within authorized contracts, test: descriptive contract review; autonomous decisions not claimed}
    - {id: AC-G06, criterion: Prior unpromoted integration resource and all required domains/output schemas preserved, test: prework candidate hash plus fresh production/output/domain tests}
dependencies:
  artifacts: [staged workflow candidate goal-contract.md, baseline-goal-TASK-6749.json, prework-candidate-goal-TASK-6749.json]
test_scenarios:
  happy_path: [new badge goal and two GWT ACs with planned evidence]
  edge_cases: [historical US-1 inference, stable-ID stale-state parent delta, qualitative success scenario]
  error_cases: [false stakeholder observation, fabricated delivery, missing evidence, orphan/duplicate AC]
evaluation:
  risk: meaningful specification/acceptance semantics; independent review required
  independent_review: awaiting_main_independent_reviewer
  selected_lessons: []
  production_baseline_sha256: df22cd0e7c750ee170dfc9f541968f07a79eac54076d20fd1c17a9b16ea3a30d
  prework_candidate: separate full manifest; prior refactor was NOT promoted
  shared_goal_contract_sha256: fd007a0f946ee3ccf60507f88c898358de9ea045b18de6446b65079d62911074
  validation_receipt: validation-receipt-goal-TASK-6749.json
  tests: 303 passed / 0 failed across goal, pipeline, lifecycle and creator foundation suites
  warnings: 3 retained placeholder mockup links in scaffold/guide
  behavior_limit: authored/rendered fixtures and existing helper tests; no autonomous specification/CR/confirmation or stakeholder-observation pilot
  promotion: prohibited in this scope
```

Plan executed last after breakdown validation. Relative to prior candidate:
4 changed, 0 added/removed; 5 files / 228 body lines. Relative to production:
4 changed and 1 prior integration addition retained, 0 removed. Historical
baseline/receipts remain unchanged. Only this authorized delta is layered onto
the prior candidate; production and actual EPIC-047/059 documents remain read-only.
Staged shared links require main review, authorized dependency publication and
fresh validation before any later child publication. No review or promotion here.