---
skill_name: x-ipe-workflow-task-execution
skill_type: x-ipe-workflow-orchestration
version: "2.1.1"
status: production
publication_state: published
created: 2026-10-13
updated: 2026-10-14
task_id: TASK-6749
summary: Shared five-phase lifecycle with one owner, exact modes, safe resume and revision-bound evidence.
triggers: [implement feature, fix bug, refactor code, set up project, direct task skill entry]
not_for: [domain implementation itself, app skip support, automatic publication, child migration]
workflow:
  phases: [Orient, Plan, Execute, Verify, Record]
  human_review: true
  contract: existing output aggregate retained; task_completion_output and operation_output not renamed
inputs:
  required:
    - {name: task, type: object, description: Approved task identity and original context; supplied ID resumes exactly}
    - {name: execution.process_preference.interaction_mode, type: string, default: interact-with-human, description: Exact three-mode enum and current policy source}
  optional:
    - {name: workflow, type: object, description: Existing name/action/extra_context_reference fields}
    - {name: git, type: object, description: Configured strategy with protected dirty baseline}
outputs:
  state:
    - {name: output.status, value: completed | blocked | deferred | in_progress | cancelled | skipped}
    - {name: output.process_preference.interaction_mode, value: resolved exact enum}
  artifacts:
    - {name: domain_artifacts, type: array, path: child-declared paths, description: Validated child output links}
  data:
    - {name: output, type: object, description: Existing workflow aggregate with full child-specific dynamic fields}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: Valid complete candidate with ordered subtype sections, test: installed validator, expected: No errors or warnings; body at most 1000 lines}
    - {id: AC-C01, category: content, criterion: Five ordered phases and mandatory common child reference, test: XML and schema assertions, expected: One owner and no recursion or speculative chain}
    - {id: AC-C02, category: content, criterion: Preserve established external modes, test: contract table plus actual service settings and UI enum transport, expected: Human asks human; full DAO bounded guidance and authorized routing; hybrid DAO within skill and human completion/route confirmation; explicit human approval binds in every mode}
    - {id: AC-B01, category: behavior, criterion: Supplied task ensure and duplicate/context behavior, test: Installed CLI subprocess tmp_path, expected: Idempotent unchanged resume; conflict bytes preserved}
    - {id: AC-B02, category: behavior, criterion: Candidate evidence changes invalidate review receipt, test: Installed validator and dry-run publisher in tmp_path, expected: Changed hash rejected without publication}
    - {id: AC-B03, category: behavior, criterion: Real keyed action writer and readback compatibility, test: Installed app helpers in tmp_path, expected: implementation is separate from code_implementation; required artifacts verified by contract}
    - {id: AC-C03, category: content, criterion: Git safety source validation and small-path honesty, test: Contract assertions and preservation fingerprint, expected: No implicit commit/push/dirty switch or fake done/skips}
  should:
    - {id: AC-S02, category: structure, criterion: Concrete direct entry and boundary examples, test: Content review, expected: Examples cover resume modes source freshness and candidate boundary}
  wont:
    - {id: AC-W01, criterion: Migrate children/app workflow schemas, reason: Separately tested adoption required; workflow publication alone does not migrate consumers}
dependencies:
  skills:
    - {name: x-ipe-tool-task-board-manager, relationship: integration, description: Installed ensure and JSON CRUD owner adapter}
    - {name: x-ipe-assistant-user-representative-Engineer, relationship: integration, description: Bounded decision guidance only}
    - {name: x-ipe-tool-x-ipe-app-interactor, relationship: integration, description: Workflow-mode actual action state and write contracts}
  artifacts:
    - {path: src/x_ipe/static/js/features/workflow-stage.js, description: Authoritative ACTION_MAP}
    - {path: x-ipe-docs/config/workflow-template.json, description: Action contexts stages and deliverable tags}
    - {path: x-ipe-docs/config/tools.json, description: Separate enabled implementation tool selection}
test_scenarios:
  happy_path:
    - {name: supplied-ID direct entry, given: Matching in_progress task, when: Ensure twice in sandbox, then: One unchanged task and return to domain caller}
  edge_cases:
    - {name: terminal resume, given: Completed cancelled or skipped task, when: Ensure, then: No reopening mutation}
    - {name: hybrid boundary, given: Hybrid mode, when: Domain asks and completes, then: DAO guides bounded within-skill questions and human confirms completion/routing; explicit domain human approval remains required}
  error_cases:
    - {name: context conflict, given: Original description or role differs, when: Ensure, then: Error and all bytes preserved}
  blocking:
    - {name: stale evidence, given: Candidate changed after validation, when: Publisher dry-run with old hash, then: Rejected without mutation}
    - {name: reviewer unavailable, given: Semantic workflow and safety changes, when: Candidate checks pass, then: candidate_ready only and promotion blocked}
evaluation:
  self_check: [Installed validator passes, Focused tests pass, Baseline preserved, All limitations explicit]
  judge_agent:
    - {criterion: Independent workflow safety and compatibility review, rubric: Current candidate and consumer hashes must match reviewed scope before promotion}
---

# Published metadata

## Established-mode correction — native R2 publication

The unchanged prior-author candidate was independently reviewed in this session,
then published with the native publisher. Actual current evidence:
[R2 review](x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/review-mode-TASK-6749-R2.md)
and [R2 receipt](x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/publication-receipt-mode-TASK-6749-R2.json).
Earlier receipts and mode assertions are historical, not authority to invert UI.
Ten child corrections remain staged and unpromoted; current invocation requires
the common explicit adapter or blocks. No task-board, memory, Git or app writes.

## Goal extension — independently promoted

The published fields/history below describe the prior lifecycle revision, not
the current goal-extended candidate. Fresh scope, baseline, risk, acceptance and
tests: [goal metadata](x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/skill-meta-goal-TASK-6749.md).
Goal extension independently reviewed and published with exact parity; see
[current evaluation](x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/evaluation-goal-promotion-TASK-6749.md)
and [receipt](x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/promotion-receipt-goal-TASK-6749.json).
The candidate-only goal supplement is historical drafting evidence, not current status.

Derived from promoted workflow orchestration and task-based metadata scaffolds.
Compatibility exception: retain the existing workflow `output` aggregate rather
than rename it to generic `workflow_output`. Board CRUD remains a separate schema.
This shared-lifecycle slice is published with explicit review/promotion authority.
TASK-6749 board state is not completed or updated by this work; no board access.
The candidate-only historical board template is retained as non-authoritative
compatibility documentation, not a new JSON board substitute or live deletion.
Independent review validates the adoption contract, not execution of unmigrated
children. Explicit bounded adapter or separately validated child migration remains
required before conflicting invocation; existing children have not been edited.

## Version History

- 2026-10-13 — 2.0.0 promoted for TASK-6749 via apply_patch only: five complete
  package files, three changes, two additions, zero removals. Candidate SHA256
  90b220f8d92463eae43e18f7f2157c1cfd6ecb90a6f7fce0531173233186ed25.
  Exact byte parity verified; installed validator passes on canonical candidate.
  Review and known consumer mismatches: review-report.md. Publication method,
  preserved prepublication baseline and recovery limits: publication-receipt.json.
- 2026-10-13 — 2.1.0 goal extension promoted via editor apply_patch only; six-file
  exact parity, 307 focused tests passed. Candidate SHA256
  89ddfa5a1abd55dca9a5e16177340c806fa194e575e5c3cd58396fa8e40d4764.
  Fresh baseline/managed provenance, independent gate and limitations are recorded
  in promotion-receipt-goal-TASK-6749.json; prior receipts/history remain unchanged.
- 2026-10-14 — 2.1.1 established-mode correction promoted with the native publisher
  after independent review of the unchanged prior-author candidate. Six-file exact
  parity; three changes, zero additions/removals/protected conflicts. Candidate
  SHA256 b79761fd9d6c36700b1312dc98b7e6b69c7099e14e05d8a10ded9f6ef21dcc00.
  Actual transaction, retained backup and baseline are in
  publication-receipt-mode-TASK-6749-R2.json. Prior receipts/history retained.
- 2026-10-14 — 2.1.1 bounded policy re-review and publication verification,
  not a new release: exact six-file production/candidate/R2-receipt parity at
  b79761fd9d6c36700b1312dc98b7e6b69c7099e14e05d8a10ded9f6ef21dcc00.
  FEATURE-044-E and current explicit user intent confirm hybrid DAO within skill
  with human completion/routing. Installed validator: zero errors/warnings;
  targeted lifecycle policy assertions: 3 passed. Trusted native dry-run has
  zero changes; publication is not replayed and version remains unchanged.
  Review appended in review-mode-TASK-6749-R2.md; fresh exact evidence in
  policy-verification-receipt-TASK-6749.json. Only workflow metadata edited via
  apply_patch; no live package, other skill, test, board, memory or Git edits.
