# Task-Based Skill Metadata — Feature Acceptance Test

## TASK-6749 sequential candidate slice

Current continuation: independent main review completed, fresh 465-test run
passed, user-authorized exact-file editor promotion verified six-file byte parity.
EOF-only candidate integration normalization separately authorized; current
validator/hash and publication receipt refreshed. Earlier candidate-only statements
below are historical author evidence, superseded by review-main-TASK-6749.md.

Implementation independently reviewed/verified/promoted first; exact four-file
parity and post-promotion 379-test run passed before acceptance drafting.
Fresh continuation checked saved implementation baseline, publication and validation
receipts against actual four-file live/candidate byte parity; fingerprint remains
90e610664b20308b105c9839c3bbf82a082d2d3d7b2f7525b4f7095e0d213cf0.
Existing acceptance production and candidate inventories captured before edits.
Original candidate had deprecated board alias, removed board blocks and simplified
human route prompt; retain the single-owner intent, replace obsolete routing/API
semantics rather than reset blindly. Four original resource paths/domain purposes
retained, one integration reference and one read-only consistency helper added;
no resource removals. Production acceptance remains byte-identical to baseline.

Creator guidelines and both subtype templates, lifecycle/goal contracts loaded.
Existing raw LL-001 browser-smoke lesson read and checked against current explicit
browser gate: map to actual path/console assertions and no source/jsdom UI pass.
This is not incident revalidation, lesson adoption/applied settlement or memory
mutation. No board/Git/memory/other-production/dirty-doc writes. No main review or
acceptance promotion claimed. Receipt/helper checks do not observe stakeholder
impact or prove autonomous agent routing/execution.

Continuation found an unclosed metadata YAML fence (initial focused run 138
passed/1 failed) and reproduced assertion borrowing across all five types
(5 failed/6 passed/139 deselected). The candidate helper now requires complete
original clauses for EACH expected AC/type; same-type cases may split clauses.
No interface/output schema changed. Added all-type authored source/goal/AC report
coverage and negative original-clause tests. Existing source/live/other metadata
and all preexisting tests remain preserved; only new downstream tests appended.
Fresh counts, receipts, relevant hashes and limits are recorded in the review
handoff and test-cases metadata, not inferred from prior blank output.

```yaml
skill_name: x-ipe-task-based-feature-acceptance-test
skill_type: x-ipe-task-based
version: "2.0.0"
status: production
created: 2025-01-30
updated: 2026-10-13
task_id: TASK-6749
publication_state: published
independent_review: completed_main_reviewer
candidate_hash: 04872899595a2e65bfa11eb54024f349cf35fe812d8f59694eb451b8f57d3843
summary: Verify all scoped original ACs against source goals/subgoals with actual type-appropriate revision-bound evidence; engineering delivery separate from stakeholder observation and conditional routing.
triggers: [run acceptance tests, test feature, execute acceptance tests, acceptance testing]
not_for:
  - "code-implementation: feature code changes or genuine implementation RED/GREEN"
  - "bug-fix: restoration of failed behavior; owner may recommend but not execute here"
  - "human-playground: explicit manual interactive testing, not forced acceptance metric"
workflow:
  category: standalone | feature-stage
  phase: Acceptance Testing
  next_task_based_skill:
    - {skill: x-ipe-task-based-code-refactor, condition: Refactor code for quality improvements}
    - {skill: x-ipe-task-based-feature-closing, condition: Close feature if no refactoring needed}
  human_review: actual mode and independent risk/domain approval gate; owner boundary
inputs:
  required:
    - {name: task_id, type: string, description: same supplied task/readiness; no allocation}
    - {name: specification_link, type: string, description: approved source/specification and all scoped ACs}
    - name: process_preference.interaction_mode
      type: string
      default: interact-with-human
      validation: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
    - {name: technical_design_link, type: string, description: actual both-part design; not implementation-file context or board field}
    - {name: implementation_files, type: file-array, description: normalized real impl-files input or actual scoped previous inventory; document-local not output/board addition}
    - {name: toolbox_meta_path, type: string, default: x-ipe-docs/config/tools.json, description: strict current stages.validation.acceptance_test execution authority}
  optional:
    - {name: feature_id, type: string, description: required for feature/workflow; approved standalone N/A}
    - {name: target_url, type: string-or-NA, description: actual reachable URL for frontend-ui only}
    - {name: mockup_link, type: string-or-NA, description: current scoped content, singular field retained while all scoped mockups inspected}
    - {name: execution_mode, type: string, default: free-mode, description: owner mode}
    - {name: workflow, type: object, description: actual acceptance_testing action and specification/impl-files contexts}
outputs:
  state:
    - {name: category, value: standalone | feature-stage}
    - {name: status, value: completed | blocked}
    - {name: next_task_based_skill, value: original two conditional suggestions; not execution authority}
    - {name: process_preference.interaction_mode, value: resolved exact enum; repair original empty field}
  artifacts:
    - {name: acceptance-test-cases, type: file, path: actual owning EPIC/FEATURE or legacy folder or approved standalone report path, description: original report link semantics with TC/AC/goal/type/evidence/outcome/gap sections}
    - {name: test-folder, type: directory, path: actual scalar test browsing directory, description: separate keyed app artifact; not invented output key}
  data:
    - {name: test_types_tested, type: array, description: original types actually executed or verified reused; CLI/library in existing groups}
    - {name: results_by_type, type: object, description: original typed result mappings; not schematic YAML sets at runtime}
    - {name: test_cases_created, type: count, description: actual total planned; diagnostics not goal}
    - {name: tests_passed, type: count, description: current suitable passing cases}
    - {name: tests_failed, type: count, description: actual failures preserved}
    - {name: tests_blocked, type: count, description: unavailable/unsupported groups retained}
    - {name: pass_rate, type: string, description: passed over ALL planned including blocked/not-run/partial; zero N/A}
    - {name: workflow_action, type: string, description: acceptance_testing not testing config key}
    - {name: workflow_action_updated, type: boolean, description: only actual/prior verified owner write; false free-mode/unverified}
    - {name: feature_id, type: string, description: actual immutable identity or approved standalone N/A}
    - {name: feature_title, type: string, description: actual title}
    - {name: feature_version, type: string, description: actual version}
    - {name: feature_phase, type: string, description: Acceptance Testing}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: complete four original resource paths plus integration/helper; valid frontmatter and body at most 1000 lines, test: installed API/CLI validator and inventory}
    - {id: AC-C01, category: contract, criterion: original output key order/value types/report semantics/conditional successors unchanged except required nested interaction_mode repair, test: parsed YAML equality per key and original order}
    - {id: AC-L01, category: lifecycle, criterion: same supplied task/readiness; no child task/feature/Git/route/app mutation ownership, test: all-resource inspection and temporary read-only resume/no task-folder}
    - {id: AC-G01, category: goal, criterion: authoritative source/parent/story/subgoal and every scoped AC/original assertion/type mapped with all-required versus alternatives and qualitative outcome gaps, test: authored tables/scaffold and negative missing/orphan/source/assertion claims}
    - {id: AC-G02, category: evidence, criterion: delivery separate from not measured/cited actual stakeholder observation; counts not achieved goals and no forced manual metrics, test: negative false-delivery/outcome claims and complete report contract}
    - {id: AC-T01, category: types, criterion: backend API CLI library UI integration and structured skill checks suitable and not UI-only/review-only; actual browser path/console/all assertions or Blocked, test: all-resource contract and actual app/consistency helpers; real feature browser/API execution not claimed}
    - {id: AC-T02, category: tooling, criterion: only literal true at actual testing key; disabled/undeclared/missing config never force-enables general or aliases browser; test-only adapter no feature code changes, test: actual config/declaration inspection and explicit domain contract}
    - {id: AC-E01, category: reuse, criterion: explicit current source/spec/code/config/tests/evidence and applicable dependencies independently selected; all relevant AC/type/assertions checked and rehashed, test: actual consistency API/CLI success/error and per-role mutations}
    - {id: AC-E02, category: reuse, criterion: missing role/file/AC/type/original clause or duplicate/unsafe/stale/failed/partial/no-provenance rejects reuse; no cross-type assertion borrowing; helper consistency not semantic/observation proof, test: negative expected/report fixtures and readonly CLI errors; five-type regression and same-type split}
    - {id: AC-I01, category: integration, criterion: real implementation_files input separate from design, actual acceptance_testing action/specification/impl-files contexts/test-report/test-folder/readback and authorized Tested or advanced preserved, test: installed temporary EPIC/legacy helper/board queries; authored reports not acceptance execution}
    - {id: AC-I02, category: routing, criterion: conditional refactor not compulsory churn; current mandatory template gate retained with closing blocker/no fake skip/done/report until legitimate completion or later authorized migration, test: actual helper suggested code_refactor plus permissive closing and genuinely locked feedback fixtures}
    - {id: AC-H01, category: honesty, criterion: failed/blocked/stale/partial/not-run scope blocks delivery and never writes done; metrics denominator all planned, test: resource/scaffold/examples and permissive helper warning; no autonomous domain execution claimed}
  should:
    - {id: AC-D01, criterion: current mockup content and precise selectors/waits/console; data provenance and safe disposable setup/teardown retained}
    - {id: AC-D02, criterion: affected-only invalidation preserves stable IDs/history/unaffected maps with dependency independence; no timestamps-only freshness}
    - {id: AC-D03, criterion: known fixtures do not force ceremonial human questions; actual human/hybrid/full DAO policy and approval boundary retained}
  could:
    - {id: AC-P01, criterion: separately authorized real autonomous acceptance pilot and real stakeholder observation}
  wont:
    - {id: AC-W01, criterion: promotion without review and user authority, reason: main review and authorized promotion now evidenced separately}
    - {id: AC-W02, criterion: current app/config mandatory-gate migration, reason: separately authorized later task}
    - {id: AC-W03, criterion: real board/memory/Git/other-production/dirty-doc edits, reason: user explicit boundary; CLI fixtures temporary only}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: lifecycle, description: same owner and common/goal contracts}
    - {name: x-ipe-tool-x-ipe-app-interactor, relationship: integration, description: actual installed helper/tag/readback semantics; no assumed semantic enforcement}
    - {name: x-ipe-tool-task-board-manager, relationship: owner-only, description: real statuses/immutable feature context; no child writes}
    - {name: x-ipe-tool-ui-testing-via-chrome-mcp, relationship: conditional, description: enabled UI operation and actual Chrome MCP isolated profile}
    - {name: discovered enabled test capabilities, relationship: execution, description: semantic matched existing runner or supported same-task test-only adapter}
  artifacts:
    - {path: x-ipe-docs/config/tools.json, description: actual acceptance_test config; not code_implementation defaults}
    - {path: x-ipe-docs/config/workflow-template.json, description: current mandatory code_refactor and action contexts/tags}
    - {path: src/x_ipe/static/js/features/workflow-stage.js, description: actual ACTION_MAP acceptance_testing identity}
    - {path: approved source/spec/design/implementation/test/environment evidence, description: explicit independently resolved relevant revision dependency scope}
test_scenarios:
  happy_path:
    - {name: Approved badge frame, given: authored upstream implementation frame, when: render report scaffold, then: exact source/goal/AC/all original assertions/type and planned/not measured states}
    - {name: Explicit evidence consistency, given: temporary current source/spec/code/config/test/evidence and full AC expectation, when: API and CLI verify, then: reusable consistency true with read-only bytes and semantic limit; no actual CLI feature acceptance claim}
    - {name: Real action adapter, given: temporary Implemented/done implementation and real report/folder paths, when: installed writer/readback, then: exact contexts/tags/owner-only Tested and readonly resume}
    - {name: All-type same-schema report, given: authored diagnostic source/goal and six ACs across seven TCs, when: render existing report and run five-type consistency fixtures, then: exact original assertions and all-required types; actual feature flows not claimed}
  edge_cases:
    - {name: Parent dependency change, given: explicit current source inventory, when: add expected parent or mutate each role while unrelated docs unchanged, then: relevant claim invalidation only}
    - {name: Completed resume, given: temporary advanced feature, when: helper write/read-only board query, then: immutable advanced status/identity preserved}
    - {name: No evidenced refactor need, given: current mandatory template, when: actual acceptance write, then: pending refactor suggestion and closing route blocker retained}
  error_cases:
    - {name: Incomplete reuse, given: omitted current input/AC/type/assertion or stale/failed/partial/unsafe/duplicate/no-provenance report, when: actual helper, then: non-reusable API or nonzero CLI without writes}
    - {name: Helper permissiveness, given: missing report/context/pending implementation or pending refactor in open stage, when: actual writer, then: success characterized but never semantic acceptance/closing proof}
    - {name: Cross-type assertion borrowing, given: two required types with missing clauses in one, when: consistency helper executes, then: non-reusable despite another type covering all assertions; same-type split remains valid}
  blocking:
    - {name: Genuine app lock, given: pending implementation/validation lock or pending validation gates/feedback lock, when: actual helper, then: nonzero STAGE_LOCKED and unchanged bytes}
    - {name: Browser or review unavailable, given: missing authorized runtime or independent reviewer, when: relevant claim attempted, then: Blocked group or candidate_ready only; no review/promotion fabricated}
evaluation:
  self_check:
    - Fresh exact validator, commands/counts/hash-bound relevant inputs and known editor failures recorded in review-handoff-TASK-6749.md and validation receipt.
    - Initial selected acceptance readiness run was 36 failed/12 passed/72 deselected, because old candidate lacked mappings/valid output/resources; these are package-readiness failures, not a fake feature behavior RED or actual browser execution.
    - Prior worker reported editor tail/replacement problems; fresh continuation directly observed and fixed unclosed metadata fence. Historical claims are not fresh execution evidence. No existing test assertion weakened.
    - Existing implementation tests retain original assertions/types/TDD contracts; two publication-state assertions now additionally verify strict receipts/baseline/fingerprint/parity, not relaxed delivery checks.
    - Helper consistency cannot discover omitted dependencies/authenticate logs/prove actual execution or stakeholder impact; independent current semantic review still required.
    - All actual board/workflow writes run only in temporary projects. Real source/config/browser/stakeholder acceptance pilot not executed or claimed.
  judge_agent:
    - criterion: Independent main review
      rubric: Completed in review-main-TASK-6749.md; six-resource package and fresh actual temporary consumer contracts reviewed, no autonomous feature execution or stakeholder observation claimed.
version_history:
  - version: "2.0.0"
    date: 2026-10-13
    task_id: TASK-6749
    change: Authorized reviewed six-file editor promotion, exact live/candidate parity and refreshed EOF-normalized validator receipt.
    evidence: publication-receipt-goal-TASK-6749.json
```

  ## R2 recovered publication history

  - Version 2.0.1, TASK-6749; verified 2026-10-14T04:28:27.605298+00:00.
  - Current production/candidate fingerprint: 1914c1922c58995fa5380e995c312e1a6b811313acd40c74ea01db73d1170644.
  - [Recovered verification receipt](publication-receipt-TASK-6749-R2.json); prior history above remains historical, not current parity evidence.
  - Hybrid inner guidance and human completion/route boundary independently reviewed at exact R2 hash; every AC/type and real boundary evidence gate retained. Prior-worker promotion time is unknown; no production replay or atomic writer journal claimed.

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `58d73c6792c7ee6bd2b4aea8d3d25ec7b039474c97a9e81f636138666e6abaab`
- Previous revision: `1914c1922c58995fa5380e995c312e1a6b811313acd40c74ea01db73d1170644`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.
