# Task-Based Skill Metadata — Feature Refinement

## Verified complete goal publication — TASK-6749

The complete prior refactor plus goal extension is now installed with five-file
exact candidate parity at the independently approved revision. The interrupted
publication had concatenated entry/examples tails and two old references; all
four mismatches are corrected through editor-only publication, not new semantics.
[Goal metadata](x-ipe-docs/skill-meta/x-ipe-task-based-feature-refinement/skill-meta-goal-TASK-6749.md)
and original evaluation/validation/execution records remain historical candidate-stage
evidence, not current readiness assertions. Current authority is the
[independent goal gate](x-ipe-docs/skill-meta/x-ipe-task-based-feature-refinement/evaluation-goal-promotion-TASK-6749.md),
[fresh validation](x-ipe-docs/skill-meta/x-ipe-task-based-feature-refinement/validation-receipt-goal-recovery-TASK-6749.json)
and [promotion receipt](x-ipe-docs/skill-meta/x-ipe-task-based-feature-refinement/promotion-receipt-goal-TASK-6749.json).
Baseline: 160 passed / 2 failed; after byte recovery and receipt settlement:
162 passed / 0 failed / 0 deselected (22 goal, 113 pipeline, 27 lifecycle).
Tests and candidate bytes are unchanged; prior 407/303/307-test records remain
historical results, not reruns or evidence to conceal the observed baseline.
Version 1.0.0 is the first recorded complete publication using the existing
external metadata version; no earlier production release or refactor-only release
is invented. No downstream, board, memory, Git or user-document work.

```yaml
skill_name: x-ipe-task-based-feature-refinement
skill_type: x-ipe-task-based
version: "1.0.0"  # first recorded complete publication; original external metadata version retained
status: production
created: 2026-10-13
updated: 2026-10-13
task_id: TASK-6749
publication_state: published
independent_review: approved_evaluation_goal_promotion_TASK_6749
summary: Complete one feature specification with stable testable acceptance, full domain and delta-first lifecycle integration.
triggers: [refine feature, detail specification, clarify requirements]
not_for:
  - "x-ipe-task-based-feature-breakdown: creating/splitting feature identities"
  - "x-ipe-task-based-technical-design: implementation architecture and HOW"
workflow:
  category: feature-stage
  phase: Feature Refinement
  next_task_based_skill:
    - skill: x-ipe-task-based-technical-design
      condition: Design the refined feature
  human_review: human/hybrid domain completeness gate; mode-aware lifecycle boundary
inputs:
  required:
    - {name: task_id, type: string, description: existing lifecycle identity/readiness}
    - name: process_preference.interaction_mode
      type: string
      default: interact-with-human
      validation: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
    - {name: feature_id, type: string, description: exactly one existing authorized legacy/new feature}
  optional:
    - {name: workflow, type: object, description: per-feature feature_refinement with both required selected contexts}
    - {name: mockup_list, type: array-or-NA, description: actual scoped mockup_name/mockup_link entries or confirmed N/A}
    - {name: refinement_context, type: context, description: revision-bound upstream/CR findings}
    - {name: document_language, type: string, description: requested or established EN/ZH language}
outputs:
  state:
    - {name: category, value: feature-stage}
    - {name: status, value: completed | blocked}
    - {name: next_task_based_skill, value: original conditional Technical Design suggestion}
    - {name: process_preference.interaction_mode, value: resolved exact input enum}
  artifacts:
    - {name: specification, type: file, path: resolved feature folder/specification.md, description: one populated full-domain specification with embedded version/CR history}
    - {name: feature-docs-folder, type: directory, path: resolved owning feature folder, description: scalar folder output in legacy/new layout}
  data:
    - {name: execution_mode, type: string, description: original context}
    - {name: workflow, type: object, description: original workflow name}
    - {name: workflow_action, type: string, description: feature_refinement}
    - {name: workflow_action_updated, type: boolean, description: actual verified write/prior write; false for free-mode/unverified}
    - {name: task_output_links, type: array, description: actual resolved artifact paths}
    - {name: feature_id, type: string, description: actual immutable identity}
    - {name: feature_title, type: string, description: actual title}
    - {name: feature_version, type: string, description: approved actual version}
    - {name: feature_phase, type: string, description: Feature Refinement}
    - {name: mockup_list, type: array-or-NA, description: actual scoped paths, copies only if needed}
    - {name: linked_mockups, type: array, description: original mockup_name/mockup_link schema}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: complete four existing resources plus one integration reference; no shipped task metadata, test: installed validator and manifests}
    - {id: AC-S02, category: structure, criterion: ordered sections and parseable four-step XML with checkpoint limits, test: parsed structure and negative mutation}
    - {id: AC-C01, category: contract, criterion: exact original output keys/order/values and conditional successor, test: YAML production/candidate/example comparison}
    - {id: AC-C02, category: ownership, criterion: one common lifecycle without task CRUD/Git/child routing, test: all-resource inspection and parsed procedure}
    - {id: AC-D01, category: domain, criterion: complete user stories/FR/NFR/UI/dependency/business/edge/out-of-scope/open-question/traceability/version-CR sections, test: scaffold headings/tables}
    - {id: AC-D02, category: domain, criterion: stable unique GWT acceptance and exactly one primary UI/API/Unit/Integration type; no Manual, test: parsed example tables plus three negative mutations}
    - {id: AC-D03, category: domain, criterion: delta-first stable IDs/language/unaffected bytes and targeted questions; material gaps block, test: domain contract inspection; agent reasoning not claimed}
    - {id: AC-D04, category: domain, criterion: current mockup scope/story/UI/AC coverage; outdated directional only; dates not precedence, test: scaffold and contract checks}
    - {id: AC-D05, category: domain, criterion: new Planned gate or authorized advanced CR/resume; no status reset, test: real temporary advanced-status/link/version updates}
    - {id: AC-I01, category: integration, criterion: actual board specification links and old/new folder outputs, test: parameterized actual temp feature CRUD/action readback}
    - {id: AC-I02, category: integration, criterion: per-feature action with both exact artifact tags and source contexts, test: actual template/prompt/CLI contracts and temp readback}
    - {id: AC-I03, category: safety, criterion: bad tags/folder array/missing identity/locked gates preserve state; permissive semantic gaps are not completion, test: real helper failures and characterization}
    - {id: AC-D06, category: domain, criterion: human/hybrid completeness confirmation and downstream invalidation revision-bound, test: explicit gates; autonomous approval pilot not claimed}
  should:
    - {id: AC-R01, criterion: no stale Draft/Specified/Complex statuses, Markdown board or timestamp-only conflict rule}
    - {id: AC-R02, criterion: existing reference scaffold/guide retained without redundant template or fake runtime utility}
  could:
    - {id: AC-E01, criterion: separately authorized autonomous specification/CR/language reasoning pilots}
  wont:
    - {id: AC-W01, criterion: unreviewed refinement production promotion, reason: original candidate-only exclusion; independent goal gate now approved exact complete manifest}
    - {id: AC-W02, criterion: real board/memory/Git/other source writes, reason: explicit exclusions}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: lifecycle, description: one identity/category handoff/decision boundary}
    - {name: x-ipe-tool-task-board-manager, relationship: integration, description: actual read and lifecycle specification_link/status handoff}
    - {name: x-ipe-tool-x-ipe-app-interactor, relationship: integration, description: actual per-feature action/readback}
  artifacts:
    - {path: resolved owning requirement part and Feature List, description: both source contexts with actual feature coverage}
    - {path: matching existing specification for CR/resume, description: stable delta baseline}
test_scenarios:
  happy_path:
    - {name: New and legacy artifacts, given: temp Planned board record and real fixture specification, when: installed action writer/readback and owner handoff, then: exact tags/context/identity/link with no task registration}
  edge_cases:
    - {name: Advanced CR, given: Completed legacy/new feature, when: authorized actual link/version update, then: status/Epic/created_at/dependencies unchanged}
    - {name: Resume, given: completed action and actual artifacts, when: query only, then: byte-identical board/workflow and no replay}
  error_cases:
    - {name: Permissive semantics, given: skipped breakdown/missing contexts/files/tag, when: installed writer, then: actual helper success characterized but domain claim blocked}
  blocking:
    - {name: Bad contracts/identity/locked prerequisite, given: temp state, when: writer invoked, then: nonzero and unchanged state}
evaluation:
  self_check:
    - Historical candidate evaluation recorded 407 focused passes; original records retained unchanged
    - Current canonical candidate and isolated installed-snapshot validation pass with exact five-file parity
    - Requested suites initially 160 passed / 2 failed; post-settlement unfiltered run 162 passed / 0 failed
    - Three scaffold placeholder warnings are explicit, not real artifact evidence
  judge_agent:
    - criterion: separate independent review of domain, scope, source resolution, approval and lifecycle handoff
      rubric: evaluation-goal-promotion-TASK-6749.md approves complete current candidate; no new reviewer score or autonomous authoring pilot claimed
version_history:
  - version: "1.0.0"
    date: 2026-10-13
    task_id: TASK-6749
    changes: First recorded complete publication of preserved lifecycle/domain refactor plus independently reviewed goal extension; interrupted editor publication recovered, five-file exact parity and 162 requested tests passed
    candidate_hash: 094644928517509cd6818629cb00ce5ab9908829c18dcdd32dfaf241b6d48ccc
    parity_receipt: promotion-receipt-goal-TASK-6749.json
  ```

## R2 recovered publication history

- Version 1.0.1, TASK-6749; verified 2026-10-14T04:28:27.605298+00:00.
- Current production/candidate fingerprint: 176ca77478fb25292817d8288c9fd78b012e30202cea3f8e5280bc66b8da8b96.
- [Recovered verification receipt](publication-receipt-TASK-6749-R2.json); prior history above remains historical, not current parity evidence.
- Hybrid inner guidance and human completion/route boundary independently reviewed at exact R2 hash; revision-bound completeness approval retained. Prior-worker promotion time is unknown; no production replay or atomic writer journal claimed.

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `0b545277710c133fbe786468d8f8f1d86a2e0368eb9d56bb532a96422aa26384`
- Previous revision: `176ca77478fb25292817d8288c9fd78b012e30202cea3f8e5280bc66b8da8b96`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.
