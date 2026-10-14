# Goal extension metadata — feature breakdown (candidate only)

Supplement to existing template-derived metadata; preserve prior domain criteria,
feature/list schemas, grouping/AC ceilings, shared folders/index and history.

```yaml
skill_name: x-ipe-task-based-feature-breakdown
skill_type: x-ipe-task-based
status: candidate
publication_state: candidate_ready
task_id: TASK-6749
updated: 2026-10-13
summary: Each feature deliverable contributes a source-linked parent requirement subgoal; selected alternatives are not extra mandated features.
workflow:
  category: requirement-stage
  next_task_based_skill: existing conditional first-unstarted-feature refinement suggestion
  human_review: existing feature-list domain gate; main independent reviewer before promotion
inputs: {contract: unchanged original fields and exact interaction enum}
outputs: {contract: unchanged original task_completion_output and six-column list}
acceptance_criteria:
  must:
    - {id: AC-G01, criterion: Feature maps subgoal to stakeholder/parent/source/AC/evidence with credible contribution, test: authored parent-chain parsing and rendered existing detail scaffold}
    - {id: AC-G02, criterion: All-required edges distinguished from selected bounded alternatives; no feature-per-layer reflex, test: actual one-feature/two-means example plus descriptive guidance}
    - {id: AC-G03, criterion: Retained downstream scaffold now has GWT ACs and goal coverage without authorizing specifications during breakdown, test: retained original headings and table assertions}
    - {id: AC-G04, criterion: Prior publication bytes tested independently of this new candidate; fresh baseline preserved, test: historical receipt fingerprint plus fresh manifest/output checks}
dependencies:
  artifacts: [staged workflow candidate goal-contract.md, baseline-goal-TASK-6749.json]
test_scenarios:
  happy_path: [one badge feature contributes to FR-061-01 via US-061-A-01]
  edge_cases: [text-only alternative not built, legacy dependency identity, incremental parent delta]
  error_cases: [orphan AC/evidence, replay or invalid helper state in retained domain tests]
evaluation:
  risk: meaningful decomposition semantics; independent review required
  independent_review: awaiting_main_independent_reviewer
  selected_lessons: []
  production_baseline_sha256: bb6482e2e3915fbe2e9806b42510253bc6851ea923509f398b0af581ed28669c
  prework_candidate: identical to fresh production baseline
  shared_goal_contract_sha256: fd007a0f946ee3ccf60507f88c898358de9ea045b18de6446b65079d62911074
  validation_receipt: validation-receipt-goal-TASK-6749.json
  tests: 303 passed / 0 failed across goal, pipeline, lifecycle and creator foundation suites
  behavior_limit: authored selection/coverage fixtures and real temporary helper checks; not proof an agent decomposes correctly
  promotion: prohibited in this scope
```

Plan executed after requirement validation, before refinement. Delta: 0 added,
6 changed, 0 removed; 8 files / 245 body lines. Integration/patterns unchanged.
One intermediate regression correctly detected that an old promotion receipt
does not cover the new candidate; test now retains historical publication checks
and separately checks the fresh production baseline and scaffold domain sections.
No domain test is waived. Final suite is passing; staged shared links require
reviewed reconciliation and fresh validation before separately authorized promotion.