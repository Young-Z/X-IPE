# Task-Based Skill Metadata — Feature Closing

## TASK-6749 independently reviewed closing publication

Current final reviewer approved and editor-promoted the six-file closing package
on 2026-10-13, after consolidated 503/503 focused checks on the final reviewed
hash. Exact candidate/live byte parity verified; two EOF-only candidate corrections,
two production replacements, two additions, zero removals; both original templates
unchanged. Review and publication receipt are authoritative current records.
The following readiness narrative is retained as prior history, not current state.
No board/memory/Git/test/app/config/other source writes; TASK-6749 remains in_progress.

Postpublication unfiltered same five-suite run: 499 passed, four stale assertions
failed in 31.33s (three candidate-only/baseline checks and one obsolete rejected
closing-report tag expectation). Tests untouched; no green final suite claim.

Acceptance independently reviewed and editor-promoted first with fresh tests,
receipt and six-file byte parity. This closing slice is candidate-only pending
main review; no closing live edit, board/task completion, memory/Git/app/config
mutation or other production work. Larger TASK-6749 remains unclosed.

Loaded creator guidelines/both subtype templates and lifecycle/goal contracts.
Captured full live four-file baseline and preexisting two-file candidate before
changes. Retained old candidate's single-owner intent, replaced obsolete board
alias/routing/release/refactor behavior. Restored both missing original templates
byte-for-byte; original example/template use cases retained with honest planned
dispositions. Add integration and report scaffold; no resource removals.

Actual template/runtime reviewed and exercised: closing action outputs [] and
both CLI/runtime service reject closing-report tag; empty {} valid. Closing report
is task artifact, not app extract tag. CR optional closing-report absent compatible;
required specification retained. Current mandatory code_refactor remains explicit
workflow blocker despite permissive open-stage helper. No phantom gate completion.
No relevant verified finite lesson selected; no historical lesson migration.

Continuation inspected actual acceptance publication receipt and exact six-file
candidate/live parity, and verified closing's four live files against its original
baseline. Closing all-type authored coverage now preserves all seven upstream
cases in the same report scaffold, with original source/AC/type/clause parity and
no execution/outcome claim. Root readiness records added; independent review is
still pending and no closing promotion is authorized. Protected-file inventory
captured before this continuation: 2,790 files outside closing metadata/candidate
and the approved downstream test, fingerprint
1cb707da3052091b46113e981ab79a3b3033ea1be832ac83097ddec7e7718056.

Fresh five-suite readiness run: 501 passed and two assertion failures; both
affected checks corrected and passed without repeating the 501 unaffected checks.
503 distinct tests covered, no unresolved failures; not a single all-green run.
The stale lifecycle assertion was updated to verify actual promoted acceptance
implementation-array versus independent both-parts design input contracts.
Reconstructing only that original test block read-only matches the original
2,790-file snapshot exactly; remaining 2,789 protected files are unchanged.
Details and honest execution/review limits are in test-cases.yaml and
review-handoff-TASK-6749.md; independent review and closing publication pending.

```yaml
skill_name: x-ipe-task-based-feature-closing
skill_type: x-ipe-task-based
version: "2.0.0"
status: production
created: 2026-10-13
updated: 2026-10-13
task_id: TASK-6749
publication_state: published
independent_review: completed_main_reviewer
candidate_hash: 9d5a17709cb1f911fd32fa3eb07b338c43eccbafeb064836debaa8485e77fee4
summary: Close one feature with full original goal/subgoal/AC/type-to-current-actual-evidence mapping, honest unobserved outcome gaps and bounded review/docs/release/owner handoff.
triggers: [close feature, create PR, ship feature, feature closing]
not_for:
  - "feature-acceptance-test: actual affected acceptance reruns via authorized capability"
  - "bug-fix or change-request: implementation defect or approved acceptance/scope change"
  - "code-refactor: optional evidenced quality implementation, not compulsory closing analysis"
workflow:
  category: feature-stage
  phase: Feature Closing
  next_task_based_skill:
    - skill: x-ipe-task-based-feature-refinement
      condition: Start the next unstarted feature from backlog. Continue the feature-by-feature pipeline (refinement → design → implementation → testing → closing).
  human_review: actual lifecycle mode, explicit domain human approval and proportionate independent risk gate
inputs:
  required:
    - {name: task_id, type: string, description: supplied same task/readiness; owner lifecycle only}
    - {name: feature_id, type: string, description: exact approved existing immutable feature identity}
    - name: process_preference.interaction_mode
      type: string
      default: interact-with-human
      validation: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
    - {name: specification_path, type: string, description: authoritative selected/declared/board/unique owning EPIC or legacy file}
    - {name: test_results, type: artifact-evidence, description: actual acceptance report/relevant dependency inventory/current execution evidence; legacy all passing not proof}
    - {name: git_strategy, type: string, description: lifecycle approved strategy; not release permission}
  optional:
    - {name: execution_mode, type: string, default: free-mode}
    - {name: workflow, type: object, description: exact feature_closing action and selected specification/optional refactor-report contexts}
    - {name: optional_tools.readme_updator, type: boolean, default: false, description: declared operation only for necessary owned misleading-doc correction}
    - {name: git_dev_branch, type: string, description: actual owner Git identity for authorized dev-session release only}
outputs:
  state:
    - {name: category, value: feature-stage}
    - {name: status, value: completed | blocked}
    - {name: next_task_based_skill, value: original conditional backlog suggestion}
    - {name: process_preference.interaction_mode, value: original exact enum}
  artifacts:
    - {name: closing-report, type: file, path: actual owning EPIC/FEATURE or legacy feature closing report, description: task artifact not app extract tag}
    - {name: task_output_links, type: array, path: actual report/folder/authorized release/existing assessment links only, description: preserve original schema; never fictional push or nonexistent analysis}
  data:
    - {name: feature_id, type: string, description: original immutable identity}
    - {name: feature_title, type: string, description: actual original title}
    - {name: feature_version, type: string, description: actual original version/history}
    - {name: feature_phase, type: string, description: Feature Closing}
    - {name: execution_mode, type: string, description: original lifecycle mode}
    - {name: workflow.name, type: string, description: original exact identity or N/A}
    - {name: refactoring_analysis, type: object, description: "original score/recommendation/suggestions keys; actual assessment only or N/A false [] with explicit not-assessed limit"}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: six-file complete candidate with all four original paths and unchanged PR/changelog templates; no removals; valid root validator, test: actual validator and byte inventory}
    - {id: AC-C01, category: contract, criterion: exact original output mapping/key order/nested types/conditional successor; runtime links actual and unassessed compatibility explicit, test: parsed live/candidate output equality and resource inspection}
    - {id: AC-L01, category: lifecycle, criterion: same supplied readiness and one owner; child never task/feature/app/Git/next writes; real owner Completed/task completed only once, test: candidate contract and temporary read-only board/status helpers}
    - {id: AC-G01, category: goal, criterion: source/parent/story/subgoal/all stable GWT AC/original assertions/types/all-required branch map to actual evidence; no invented goals or manual GWT type, test: badge and seven-case all-type upstream table parity/scaffold; seven badge false-claim and seven all-type omitted-clause negatives}
    - {id: AC-G02, category: outcome, criterion: delivered versus cited actual observed benefits separated; unobserved not measured/qualitative gaps explicit; no stakeholder approval fabricated, test: authored plan/scaffold and false outcome/approval negatives}
    - {id: AC-E01, category: freshness, criterion: independently resolved relevant inputs/full clauses/types/environment and actual provenance permit reuse without second identical tests; relevant deltas invalidate affected dependent checks/review/outcome, test: existing actual read-only consistency helper success/current-code mutation rejection plus scoped contract}
    - {id: AC-R01, category: review, criterion: proportionate risk independent review/current reuse or cosmetic self-check rationale; missing required review blocks, test: bounded review policy and pending main-review record}
    - {id: AC-D01, category: preservation, criterion: only misleading authorized docs changed; no implementation fix or AC/tests weakened to match faulty code without approved CR; no blanket rewrite, test: entry/resources and protected-source hash verification}
    - {id: AC-Q01, category: quality, criterion: no compulsory refactoring analysis/score threshold/churn; original assessment fields remain honest actual or unassessed, test: original output equality and procedure/refactor-policy check}
    - {id: AC-A01, category: authority, criterion: no auto commit/push/PR/broad dirty staging; engineering-only uncommitted valid, required release absent authority blocked, test: release/mode/strategy contracts; no real Git operation}
    - {id: AC-I01, category: integration, criterion: "actual feature_closing output [] maps {} valid; report task artifact no bogus tag; matching feature/context/status readback and runtime service parity", test: actual temporary CLI and service success/rejection/no-mutation}
    - {id: AC-I02, category: integration, criterion: optional CR closing-report absent compatible with required specification; no app/config edits or automatic report extraction claim, test: actual template plus temp CR context readback}
    - {id: AC-I03, category: status, criterion: Implemented/Tested readiness only with real full evidence, Completed resume preserved, current mandatory refactor gate remains blocker despite writer permissiveness, test: three-status fixtures/read-only resume/locked failures and explicit report limits}
  should:
    - {id: AC-D02, criterion: preserve original login example and verification/completion/human communication templates while labeling planned versus actual evidence}
    - {id: AC-D03, criterion: partial reuse preserves history/unaffected IDs and relevant dependency rationale}
    - {id: AC-D04, criterion: legacy EPIC/FEATURE folder resolution and broken explicit link blocking retained}
  could:
    - {id: AC-P01, criterion: separately authorized real autonomous closing and stakeholder observation pilot}
  wont:
    - {id: AC-W01, criterion: closing promotion before main review, reason: prohibited; independent main review now completed before authorized publication}
    - {id: AC-W02, criterion: app/config gate or tag migration, reason: later integration scope only}
    - {id: AC-W03, criterion: actual board/memory/Git/source/other production edits, reason: excluded; temporary scenarios only}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: lifecycle, description: single owner/common/goal contracts}
    - {name: x-ipe-task-based-feature-acceptance-test, relationship: evidence, description: published actual helper/schema and suitable evidence boundaries reused}
    - {name: x-ipe-tool-x-ipe-app-interactor, relationship: runtime, description: actual writer/readback/tag rules; success not semantic proof}
    - {name: x-ipe-tool-task-board-manager, relationship: owner, description: actual feature status schema; no real board writes here}
    - {name: x-ipe-tool-readme-updator, relationship: optional, description: declared operation only when enabled/needed/authorized}
  artifacts:
    - {path: x-ipe-docs/config/workflow-template.json, description: empty closing outputs, optional CR report, mandatory code_refactor}
    - {path: src/x_ipe/services/workflow_manager_service.py, description: actual runtime validation of empty/unexpected tags}
    - {path: src/x_ipe/static/js/features/workflow-stage.js, description: authoritative feature_closing action identity}
test_scenarios:
  happy_path:
    - {name: Badge plan continuity, given: actual upstream authored frame, when: render same closing report tables, then: source/subgoal/all AC/assertion/type parity and explicit planned/not measured}
    - {name: Empty output mapping, given: temporary real action/report/spec context, when: "installed helper {} and runtime validator", then: actual done/readback without pretend tag; writer permissiveness not feature acceptance}
    - {name: Current evidence reuse, given: temporary explicit existing acceptance record, when: actual helper verify read-only, then: consistency true without duplicate feature execution}
  edge_cases:
    - {name: Three feature states, given: temporary Implemented/Tested/Completed records, when: real app writer then owner fixture transition/query, then: writer doesn't change board and read-only Completed preserved}
    - {name: Optional CR report absent, given: current required specification and no closing output tag, when: temp explicitly open-stage context write/readback, then: report absent accepted without fake gate unlock}
  error_cases:
    - {name: False closing claim, given: missing/source/weakened assertion/type/false delivery/outcome/approval authored mutations, when: coverage checker, then: rejection not actual feature execution}
    - {name: Relevant code delta, given: previously consistent record, when: relevant implementation bytes change, then: actual read-only helper rejects reuse}
    - {name: Invalid tag or wrong feature, given: real existing report and scoped temp state, when: installed helper bogus closing-report/wrong ID, then: nonzero and byte preservation}
  blocking:
    - {name: Locked validation, given: temporary pending implementation and locked validation, when: "closing helper {}", then: actual STAGE_LOCKED and unchanged state}
    - {name: Missing review/release/UI evidence, given: no required actual evidence or permission, when: pertinent completion claimed, then: explicit blocker; not fictional pass or approval}
evaluation:
  self_check:
    - Root validator/actual helper/service tests and authored-plan checks evidenced in test-cases.yaml and review-handoff-TASK-6749.md.
    - Readiness failures are package coverage failures, not fabricated feature behavior TDD; no existing acceptance assertions weakened.
    - Runtime permissiveness is characterized honestly; temporary board writes and open-stage setup are not production or semantic closure evidence.
    - Reviewed six-file closing package is editor-promoted with exact parity; no autonomous closing execution, stakeholder outcome observation or TASK-6749 completion claimed.
  judge_agent:
    - criterion: Independent main review
      rubric: Completed; independent final reviewer inspected all six resources, exact schemas and actual runtime/helper/current evidence contracts; see review-main-TASK-6749.md.
version_history:
  - version: "2.0.0"
    date: 2026-10-13
    task_id: TASK-6749
    candidate_hash: 9d5a17709cb1f911fd32fa3eb07b338c43eccbafeb064836debaa8485e77fee4
    publication: publication-receipt-goal-TASK-6749.json
    review: review-main-TASK-6749.md
    summary: Independent core review and consolidated focused validation followed by authorized six-file exact-parity editor publication; two EOF-only corrections, no schema/source/board/Git migration.
```

  ## R2 recovered publication history

  - Version 2.0.1, TASK-6749; verified 2026-10-14T04:28:27.605298+00:00.
  - Current production/candidate fingerprint: f297a531cdd72120073a585ba1a5158cb67ee8c4d4df9546fce84efd063e9899.
  - [Recovered verification receipt](publication-receipt-TASK-6749-R2.json); prior history above remains historical, not current parity evidence.
  - Hybrid inner guidance and human completion/route boundary independently reviewed at exact R2 hash; release authority and engineering/outcome distinction retained. Prior-worker promotion time is unknown; no production replay or atomic writer journal claimed.
