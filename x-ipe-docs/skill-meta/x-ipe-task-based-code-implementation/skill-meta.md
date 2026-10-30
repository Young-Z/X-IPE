# Task-Based Skill Metadata — Code Implementation

## TASK-6749 sequential candidate slice

Technical-design independently reviewed and promoted first; its exact candidate/
production parity passed before this draft. Complete implementation production
and prework candidate inventories captured before edits. Preserve all three
original resource paths and their AAA/coding/error/mockup/retry/batching domain
purpose; add one integration reference, no removals. Prework entry's earlier
board-alias migration is retained via current board-manager read-only context,
not blindly reset from production. The initial worker was candidate-only; current
fresh main review and explicitly authorized exact-file promotion are recorded below.

Creator/general guidelines/task-based templates and lifecycle/goal contracts
loaded. Existing raw LL-001 async propagation and LL-002 candidate-first gate
were read and checked against current source declarations/contracts; map them
only to runtime-syntax guidance and special-delegation gate. No lesson status,
memory, board, Git, other source or unrelated dirty docs changed. This does not
claim historical incident freshness or adopted/applied lesson settlement.

```yaml
skill_name: x-ipe-task-based-code-implementation
skill_type: x-ipe-task-based
version: "2.1.0"
status: production
created: 2026-03-01
updated: 2026-10-13
task_id: TASK-6749
publication_state: published
independent_review: passed_main_reviewer
candidate_hash: 90e610664b20308b105c9839c3bbf82a082d2d3d7b2f7525b4f7095e0d213cf0
summary: One approved feature capability with source/outcome-to-AC-to-test traceability, sequential enabled semantic routing and honest fresh delivery evidence.
triggers: [implement feature, write code, develop feature, code implementation]
not_for:
  - "code-refactor: restructuring without new acceptance"
  - "bug-fix: restoration of existing expected behavior"
  - "skill-creator: direct skill maintenance; delegated here only for approved feature skill scope"
workflow:
  category: feature-stage
  phase: Code Implementation
  next_task_based_skill:
    - skill: x-ipe-task-based-feature-acceptance-test
      condition: Verify implementation with acceptance tests
  human_review: mode-aware owner boundary and explicit domain risk approval
inputs:
  required:
    - {name: task_id, type: string, description: existing supplied task/readiness}
    - {name: feature_id, type: string, description: exactly one approved actual feature}
    - name: process_preference.interaction_mode
      type: string
      default: interact-with-human
      validation: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
    - {name: specification_link, type: string, description: resolved authoritative specification with source/story/ACs}
    - {name: technical_design_link, type: string, description: resolved two-part design from context/output; not board field}
    - {name: program_type, type: string, description: actual approved extensible lowercase type}
    - {name: tech_stack, type: array, description: actual approved technologies and test frameworks}
  optional:
    - {name: execution_mode, type: string, default: free-mode, description: lifecycle execution mode}
    - {name: workflow, type: object, description: exact implementation action and required specification/tech-design contexts}
    - {name: mockup_link, type: string-or-NA, description: singular legacy field; all current scoped mockups still read}
    - {name: git_strategy, type: string, description: validated owner-only strategy context}
    - {name: git_main_branch, type: string, description: validated owner context; no child Git}
outputs:
  state:
    - {name: category, value: feature-stage}
    - {name: status, value: completed | blocked}
    - {name: next_task_based_skill, value: original conditional Acceptance Test suggestion}
    - {name: process_preference.interaction_mode, value: resolved exact enum}
  artifacts:
    - {name: implementation, type: directory, path: actual approved source/delegation folder, description: original directory-oriented task links adapted to real layout}
    - {name: tests, type: directory, path: actual approved test folder, description: suitable original-assertion checks and affected regression}
    - {name: impl-files, type: file-array, path: actual owned source/test/delegation files, description: separate nonempty workflow array; not output directories or design}
    - {name: impl-folder, type: directory, path: actual browsing directory, description: one scalar directory; files may span outside it}
  data:
    - {name: execution_mode, type: string, description: original caller context}
    - {name: workflow, type: object, description: original workflow name}
    - {name: workflow_action, type: string, description: implementation not tool config key}
    - {name: workflow_action_updated, type: boolean, description: true only verified actual/prior action write}
    - {name: task_output_links, type: array, description: original directory links src/ and tests/ are layout examples}
    - {name: feature_id, type: string, description: actual immutable feature identity}
    - {name: feature_title, type: string, description: actual title}
    - {name: feature_version, type: string, description: actual approved version}
    - {name: feature_phase, type: string, description: Code Implementation}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: complete original three paths plus integration reference and valid body within 1000 logical lines, test: installed validator and manifests}
    - {id: AC-C01, category: contract, criterion: original parsed output keys/order/value types and conditional successor retained, test: exact YAML comparison including src/tests directory examples}
    - {id: AC-C02, category: lifecycle, criterion: same supplied owner/task and no duplicate create/status/Git/route in entry or references, test: parsed procedure/init and all-resource exclusions}
    - {id: AC-G01, category: goal, criterion: authoritative source/parent/story/AC-to-selected-means-to-original-tests map with no invented targets or activity-count surrogate, test: concrete upstream/downstream authored tables and negative mutations}
    - {id: AC-G02, category: evidence, criterion: planned/verified delivery separate from not measured/actual cited observation, test: authored artifact negative claims; no autonomous agent or stakeholder execution claimed}
    - {id: AC-G03, category: delta, criterion: affected-only invalidation preserves unaffected IDs/rows/assertions and dependency-bound freshness, test: authored delta and real temporary hash mutations}
    - {id: AC-R01, category: routing, criterion: actual stages.implement.code_implementation with missing/metadata-only opt-in booleans disabled/undeclared general fallback and sequential enabled semantic matching, test: actual config/declarations plus candidate contract inspection; not autonomous routing execution}
    - {id: AC-R02, category: delegation, criterion: skill-creator/MCP gate precedes ordinary scenario/routing and retains scoped tests/DoD/acceptance, test: parsed order and complete references; publication boundary explicit}
    - {id: AC-T01, category: testing, criterion: original assertions/all ACs/test types retained; genuine RED/GREEN for changed behavior and baseline/regression; no live-tool RED assumption, test: candidate contract and authored scenarios plus negative checks}
    - {id: AC-T02, category: tracing, criterion: only applicable existing infrastructure runtime functions redacted/opt-in and tested; missing infrastructure skips not mandatory setup, test: entry/reference contract inspection}
    - {id: AC-I01, category: integration, criterion: actual implementation action with required contexts/done design and real file array/scalar browsing folder independent of directory task links, test: actual installed temporary writer/readback schema4 and real artifact checks}
    - {id: AC-I02, category: safety, criterion: helper gaps do not imply completion; invalid arrays/keys/feature/locks preserve bytes and advanced CR status stays advanced, test: actual temporary helper rejection/permissiveness/resume/feature queries}
  should:
    - {id: AC-C09, criterion: bounded one retry and integration conflict through actual mode without erasing original expectations}
    - {id: AC-C10, criterion: complete cross-layer map retained across large-context per-layer batching}
    - {id: AC-C11, criterion: existing coding/naming/error/mockup guidance and async/browser syntax caution retained}
  could:
    - {id: AC-E01, criterion: separately authorized autonomous skill/MCP/tool routing and runtime implementation pilots}
  wont:
    - {id: AC-W01, criterion: unreviewed or implicit production promotion, reason: explicit user permission plus independent review and exact parity required}
    - {id: AC-W02, criterion: real board/memory/Git/other-source/dirty-doc changes, reason: user maintenance boundary; helper fixtures use temporary projects only}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: lifecycle, description: single owner and goal/common contracts}
    - {name: x-ipe-tool-task-board-manager, relationship: integration, description: actual Designed/Implemented statuses and supported schema; no design-link field}
    - {name: x-ipe-tool-x-ipe-app-interactor, relationship: integration, description: actual installed workflow helper/readback}
    - {name: x-ipe-tool-test-generation, relationship: fallback, description: no invented expectations; full original acceptance retained}
    - {name: x-ipe-meta-skill-creator, relationship: delegation, description: skill-file complete candidate validation and permission gate}
    - {name: mcp-builder, relationship: delegation, description: MCP protocol/build scope before ordinary routing}
    - {name: x-ipe-tool-implementation-general, relationship: fallback, description: always eligible safety net; insufficient means blocked}
    - {name: x-ipe-tool-tracing-instrumentation, relationship: conditional, description: applicable existing infrastructure only}
  artifacts:
    - {path: resolved specification and two-part technical design, description: authoritative acceptance and approved means}
    - {path: x-ipe-docs/config/tools.json, description: actual code_implementation config}
    - {path: x-ipe-docs/config/workflow-template.json, description: actual implementation action/contexts/tags}
test_scenarios:
  happy_path:
    - {name: Badge mapping, given: upstream authored design with all-required two ACs, when: parse/render selected means and original checks, then: exact source/goal/AC coverage and honest planned/not measured states}
    - {name: Actual file-array handoff, given: temporary Designed feature with done design and real source/test artifacts, when: installed writer and readback, then: schema4 file array/scalar directory and owner Implemented without task allocation}
  edge_cases:
    - {name: Parent delta, given: authorized stale flag scope fixture, when: compare mappings, then: affected current-state evidence invalidated with absent row identical}
    - {name: Relevant freshness, given: actual temporary spec/design/source/test/config/mockup bytes, when: mutate each and unrelated doc separately, then: only relevant revisions invalidate evidence}
    - {name: No-op advanced resume, given: temporary Completed feature, when: owner action plus read-only queries, then: immutable record/status preserved}
  error_cases:
    - {name: Helper permissiveness, given: pending design/absent context/missing or empty or directory file paths, when: installed writer, then: success characterized but never semantic completion}
    - {name: Broken authored claim, given: missing/orphan/duplicate AC or wrong source/goal/empty assertion/false delivery/outcome, when: parse coverage, then: rejected}
  blocking:
    - {name: Invalid helper contract, given: extra tag/folder array/invalid element/missing feature/genuinely locked stage, when: installed writer, then: nonzero and unchanged bytes}
    - {name: Missing main review, given: current candidate-only drafting, when: release boundary reached, then: no production promotion}
evaluation:
  self_check:
    - Final exact commands/counts/hashes are in validation receipt and review-handoff-TASK-6749.md.
    - Current continuation baseline was 94 passing upstream/downstream tests; final five-suite run was 379 passed, zero failed/skipped/deselected, exit 0.
    - Prior worker reported an earlier 22-failure RED run and fixture corrections; those historical counts were not rerun or independently evidenced by this continuation.
    - Direct tool-input YAML parsing exposed malformed mockup_link nesting despite passing substring tests; actual parse failed before correction and passed after literal editor repair. No test source or assertions changed.
    - Six related candidate validators passed; implementation has 264 body lines, four files, zero errors/warnings. Six root metadata YAML mappings and the implementation test-case YAML parsed successfully.
    - Actual helpers run only in temporary EPIC and legacy projects; authored tables and content checks are not autonomous routing or stakeholder evidence.
    - Before promotion original three-file baseline matched; after authorized review/edit-tool publication exact four-file candidate parity and unchanged validator receipt passed.
  judge_agent:
    - criterion: Independent main review
      rubric: Passed by fresh main reviewer; see review-main-TASK-6749.md and publication-receipt-goal-TASK-6749.json. No autonomous routing or stakeholder observation claimed.
version_history:
  - version: "2.1.0"
    date: 2026-10-13
    task_id: TASK-6749
    candidate_hash: 90e610664b20308b105c9839c3bbf82a082d2d3d7b2f7525b4f7095e0d213cf0
    changes: Independent main review and verified exact-file editor promotion of goal-oriented implementation package; original output and TDD assertions retained.
```

Candidate_ready was the prior worker handoff state. Current main review and
explicitly authorized promotion are recorded in the separate publication receipt;
all four production bytes match that reviewed candidate. Historical raw lessons
and conceptual test cases remain attributed, not observed executions. Larger-task
completion is not claimed; no board write or acceptance promotion is authorized.

## R2 recovered publication history

- Version 2.1.1, TASK-6749; verified 2026-10-14T04:28:27.605298+00:00.
- Current production/candidate fingerprint: 2a7786151253ccd3d6ef0817f9e7c52a06403efcfcfbc8299279dbf8e04ed720.
- [Recovered verification receipt](publication-receipt-TASK-6749-R2.json); prior history above remains historical, not current parity evidence.
- Hybrid inner guidance and human completion/route boundary independently reviewed at exact R2 hash; original assertion/TDD gates retained. Prior-worker promotion time is unknown; no production replay or atomic writer journal claimed.

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `e8dfc5e09ace2e8763eaf50cbd5c39677229218efca2878f48c85ba8d7ea7c35`
- Previous revision: `2a7786151253ccd3d6ef0817f9e7c52a06403efcfcfbc8299279dbf8e04ed720`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.

## TASK-6752 proportional-delivery revision

Published through the installed manifest-safe publisher after bounded compatibility review, correction of its TypeScript test-path finding, deterministic validation and affected post-publication regressions. Prior metadata remains historical.

- Current revision: `dbc498d7958b52bd95aa477cdcc6a0d04eef91623840613fb07822aa297934a4`
- Previous revision: `e8dfc5e09ace2e8763eaf50cbd5c39677229218efca2878f48c85ba8d7ea7c35`
- Evidence: `lean-delivery-TASK-6752.json`, `publication-receipt-TASK-6752.json`, `validation-receipt-TASK-6752.json`.
- Verification: 599 selected checks passed; exact installed/candidate byte parity. No resource removals, mirror synchronization or Git mutation.
- Live-agent efficacy, token/latency savings and stakeholder outcome remain unmeasured.
