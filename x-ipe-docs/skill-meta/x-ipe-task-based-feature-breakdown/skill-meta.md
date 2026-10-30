# Task-Based Skill Metadata — Feature Breakdown

## Goal extension — independently promoted

Prior metadata/receipts describe the already-promoted upstream refactor, not
the new goal delta. [Goal metadata](x-ipe-docs/skill-meta/x-ipe-task-based-feature-breakdown/skill-meta-goal-TASK-6749.md)
records historical drafting scope. Current gate and exact publication are in
evaluation-goal-promotion-TASK-6749.md and promotion-receipt-goal-TASK-6749.json.

```yaml
skill_name: x-ipe-task-based-feature-breakdown
skill_type: x-ipe-task-based
version: "3.2.0"
status: production
created: 2026-02-11
updated: 2026-10-13
task_id: TASK-6749
publication_state: published
independent_review: independent-review-TASK-6749.md
current_evaluation: evaluation-promotion-TASK-6749.yaml
promotion_receipt: promotion-receipt-TASK-6749.json
summary: >-
  Turn approved new/small/CR requirements into stable Epic/Feature units, runnable
  MVP-first order, direct dependencies and actual board/application artifacts.
triggers: [break down features, split into features, create feature list, organize epics]
not_for:
  - "x-ipe-task-based-requirement-gathering: initial intent and conflict decisions"
  - "x-ipe-task-based-feature-refinement: detailed feature specification"
workflow:
  category: requirement-stage
  phase: Requirements
  next_task_based_skill:
    - skill: x-ipe-task-based-feature-refinement
      condition: Refine first unstarted feature through full sequential pipeline before next feature
  human_review: mode-aware lifecycle boundary; explicit domain human authority retained
inputs:
  required:
    - {name: task_id, type: string, description: existing lifecycle identity/readiness}
    - name: process_preference.interaction_mode
      type: string
      default: interact-with-human
      validation: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
    - {name: requirement_doc, type: string, description: explicit selected populated document or validated fallback; free-mode request must become real artifacts}
  optional:
    - {name: workflow, type: object, description: exact shared action and required requirement-doc context in workflow-mode}
    - {name: mockup_list, type: array-or-NA, description: validated mockup_name/mockup_link entries or N/A}
    - {name: breakdown_context, type: context, description: upstream revision-bound findings and approved delta}
    - {name: epic_context, type: context, description: reuse intake/existing Epic; additional groups only when justified}
outputs:
  state:
    - {name: category, value: requirement-stage}
    - {name: status, value: completed | blocked}
    - {name: next_task_based_skill, value: original conditional sequential Feature Refinement suggestion}
    - {name: process_preference.interaction_mode, value: exact resolved input enum}
  artifacts:
    - {name: feature_list_details, type: file, path: selected x-ipe-docs/requirements/requirement-details file or part, description: populated table and all scoped detailed sections}
    - {name: breakdown_folder, type: directory, path: x-ipe-docs/requirements, description: actual scalar containing directory; Epic and new Feature folders retained}
    - {name: feature_board, type: file, path: x-ipe-docs/planning/features/features.json, description: actual CLI registrations and supported mutable deltas; never manual edits}
  data:
    - {name: workflow_action, type: string, description: feature_breakdown}
    - {name: workflow_action_updated, type: boolean, description: actual verified write or evidenced prior done readback; false for free-mode/unverified}
    - {name: requirement_id, type: string, description: existing REQ ID or N/A; never invent for Epic-only input}
    - {name: epic_ids, type: array, description: actual scoped Epic identities}
    - {name: epic_count, type: integer, description: length of actual epic_ids}
    - {name: feature_ids, type: array, description: actual scoped created/updated/reused identities}
    - {name: feature_count, type: integer, description: length of actual feature_ids}
    - {name: requirement_details_part, type: integer-or-null, description: actual numbered part or legacy null single file}
    - {name: parent_features_removed, type: array, description: actual approved active removal plus Retired board history retained}
    - {name: dedup_gaps, type: array, description: uncovered parent FR/AC IDs; retained parent}
    - {name: linked_mockups, type: array, description: verified shared links using mockup_name/mockup_link}
    - {name: mockup_list, type: array-or-NA, description: resolved upstream input contract}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: complete candidate; all seven legacy paths retained plus integration resource, test: installed validator/manifests}
    - {id: AC-S02, category: structure, criterion: 200-300 entry lines and <=1000 logical body ceiling, test: body count}
    - {id: AC-C01, category: contract, criterion: all original output keys/order/category/status/conditional successor retained, test: YAML comparison}
    - {id: AC-C02, category: ownership, criterion: one common lifecycle owner without child task/Git/routing duplication, test: package contract inspection}
    - {id: AC-D01, category: domain, criterion: fresh requirement findings reused; delta-only CR preserves stable state, test: contracts plus temp CLI stable state tests}
    - {id: AC-D02, category: domain, criterion: Epic grouping matrix; stable legacy/new IDs; collision reservations and no second intake Epic, test: domain assertions}
    - {id: AC-D03, category: domain, criterion: runnable vertical MVP first; <=20 AC ceiling; <=7 per Epic and direct referenced DAG, test: contract assertions; reasoning pilot not claimed}
    - {id: AC-D04, category: domain, criterion: selected owning part/index details and shared root-relative mockups; EN/ZH, test: templates/resource assertions}
    - {id: AC-D05, category: domain, criterion: full parent coverage and authorized Retired active removal; partial retained gaps/history, test: domain contract and actual retirement helper}
    - {id: AC-D06, category: domain, criterion: prioritized list completeness confirmed by human in human/hybrid or bounded DAO guidance in full DAO; only same-revision confirmation reused, test: explicit retained gate contract; autonomous confirmation pilot not claimed}
    - {id: AC-I01, category: integration, criterion: actual Planned feature CLI create/query/update and read-only HTTP envelopes, test: temporary real helpers/API}
    - {id: AC-I02, category: integration, criterion: mandatory shared action and both features-list/breakdown-folder match actual consumers, test: config/prompt contracts and tmp writer/readback}
    - {id: AC-I03, category: integration, criterion: id/name/depends_on differs from board schema; absent delta append preserves stable stages, test: real helper tmp scenarios}
    - {id: AC-I04, category: safety, criterion: empty-feature CR/pending and replay/semantic permissiveness cannot fake completion, test: helper negative/characterization and explicit domain guards}
  should:
    - {id: AC-R01, criterion: single-feature lightweight registration remains complete and truthful}
    - {id: AC-R02, criterion: no stale Markdown boards/batch/archive commands or duplicate downstream action ownership}
  could:
    - {id: AC-E01, criterion: future separate autonomous authoring/decision pilots}
  wont:
    - {id: AC-W01, criterion: unreviewed or unauthorized publication, reason: exact reviewed edit-only publication recorded separately}
    - {id: AC-W02, criterion: real board/memory/Git/app-source/other skill mutation, reason: explicit task exclusions; tmp helper fixtures only}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: lifecycle, description: one task and decision boundary}
    - {name: x-ipe-tool-task-board-manager, relationship: domain integration, description: installed feature CRUD only}
    - {name: x-ipe-tool-x-ipe-app-interactor, relationship: workflow integration, description: actual shared action/readback and append limitations}
  artifacts:
    - {path: x-ipe-docs/config/workflow-template.json, description: actual mandatory action/contexts/outputs}
    - {path: src/x_ipe/static/js/features/workflow-stage.js, description: authoritative action mapping}
test_scenarios:
  happy_path:
    - {name: Single feature and numbered part, given: populated tmp files/prerequisite state, when: real board create/query plus workflow write/readback, then: Planned unique feature and exact two outputs}
  edge_cases:
    - {name: Delta/resume, given: completed legacy/new state, when: real query or absent append delta, then: unchanged existing status/spec/stages and no replay}
    - {name: Parent retirement, given: approved complete coverage, when: actual Retired update, then: history still queryable; active removal separately required}
  error_cases:
    - {name: Existing-only initial workflow action, given: no absent new features, when: empty --features done, then: MISSING_FEATURES and preserved state}
    - {name: Permissive helper semantics, given: missing tags/files/pending prerequisite or duplicate IDs, when: direct helper, then: gaps characterized; not domain success}
  blocking:
    - {name: Invalid tags/folder arrays/identity status, given: bad actual contract, when: helper invoked, then: nonzero without existing state mutation}
evaluation:
  self_check:
    - Installed validator and current pipeline/helper regressions pass at recorded revisions
    - Production breakdown byte-identical to validated candidate; original baseline retained, downstream template unchanged
    - Prior execution-log.yaml/test-cases.yaml/sandbox are archival, not current evidence
  judge_agent:
    - criterion: independent domain/lifecycle/append-only safety review
      rubric: independent-review-TASK-6749.md; no invented separate subagent or pilot score
```

    ## Version History

    | Version | Date | Record |
    | --- | --- | --- |
    | 3.0.0 | Before TASK-6749 publication | Preserved candidate metadata baseline; no earlier history invented |
    | 3.1.0 | 2026-10-13 | Reviewed common-lifecycle/delta migration; parsed XML defect corrected; eight-file exact parity, 385 focused tests passed |
    | 3.2.0 | 2026-10-13 | Independently reviewed goal contribution/selected means; eight-file exact parity, 307 focused tests; fingerprint 9cae32f8fb61fafbec7cfc712a91626b2ae05e34df2f86ae3ac05ad690f20fdc; promotion-receipt-goal-TASK-6749.json |

  ## R2 recovered publication history

  - Version 3.2.1, TASK-6749; verified 2026-10-14T04:28:27.605298+00:00.
  - Current production/candidate fingerprint: 98f6245afee8bfd64bb58ef9be50f20b3a727fea5c145b4db479a2dcd96dd466.
  - [Recovered verification receipt](publication-receipt-TASK-6749-R2.json); prior history above remains historical, not current parity evidence.
  - Hybrid inner guidance and human completion/route boundary independently reviewed at exact R2 hash. Prior-worker promotion time is unknown; no production replay or atomic writer journal claimed.

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `e6410373de1e84d5f2e6d447f7ee0ac03f1086b4e730724af690f4f6cd9bd2a6`
- Previous revision: `98f6245afee8bfd64bb58ef9be50f20b3a727fea5c145b4db479a2dcd96dd466`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.
