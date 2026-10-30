# Task-Based Skill Metadata — Requirement Gathering

## Goal extension — independently promoted

Prior metadata/receipts describe the already-promoted upstream refactor, not
the new goal delta. [Goal metadata](x-ipe-docs/skill-meta/x-ipe-task-based-requirement-gathering/skill-meta-goal-TASK-6749.md)
records historical drafting scope. Current independent gate and exact publication
are in evaluation-goal-promotion-TASK-6749.md and promotion-receipt-goal-TASK-6749.json.

```yaml
skill_name: x-ipe-task-based-requirement-gathering
skill_type: x-ipe-task-based
version: "2.2.0"
status: production
created: 2026-02-11
updated: 2026-10-13
task_id: TASK-6749
publication_state: published
independent_review: approved_main_distinct_from_prior_author
summary: >-
  Gather new/small/CR requirements with revision-bound context reuse, bounded
  questions, resolved feature impacts, Epic documents and real app deliverables.
triggers: [new feature, add feature, I want to build, create requirement, gather requirements]
not_for:
  - "x-ipe-task-based-feature-breakdown: assigning feature units"
  - "x-ipe-task-based-change-request: separately authorized CR processing"
workflow:
  category: requirement-stage
  phase: Requirements
  next_task_based_skill:
    - skill: x-ipe-task-based-feature-breakdown
      condition: Break requirements into features
  human_review: mode-aware lifecycle boundary; explicit domain human gates retained
inputs:
  required:
    - name: task_id
      type: string
      description: Existing supplied lifecycle identity and readiness
    - name: process_preference.interaction_mode
      type: string
      default: interact-with-human
      validation: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
    - name: user_request
      type: context
      description: Original user request or valid idea artifact; preserve what/who/why
  optional:
    - name: workflow
      type: object
      description: Exact resolved name/action/extra_context_reference; required refined idea in workflow-mode
    - name: epic_id
      type: string
      description: Reuse task-associated Epic on resume; otherwise collision-safe next EPIC number
    - name: mockup_list
      type: array-or-NA
      description: Validated mockup_name/mockup_link entries or N/A
outputs:
  state:
    - {name: category, value: requirement-stage}
    - {name: status, value: completed | blocked}
    - name: next_task_based_skill
      value: conditional canonical Feature Breakdown suggestion retained
    - {name: process_preference.interaction_mode, value: resolved exact caller enum}
  artifacts:
    - name: requirement_details
      type: file
      path: x-ipe-docs/requirements/requirement-details.md or actual active numbered part
      description: Complete domain content, impacts, source/coverage/verification evidence
    - name: epic_folder
      type: directory
      path: x-ipe-docs/requirements/EPIC-{nnn}/
      description: New intake grouping with mockups subdirectory; not a Feature ID
    - name: requirements_folder
      type: directory
      path: x-ipe-docs/requirements
      description: Scalar app folder output, not an array or Epic-only folder
  data:
    - {name: workflow_action, type: string, description: requirement_gathering}
    - {name: workflow_action_updated, type: boolean, description: true only after actual successful write/readback}
    - {name: requirement_summary_updated, type: boolean, description: actual document mutation}
    - {name: requirement_details_part, type: integer, description: actual active number; single file is 1}
    - {name: conflict_review_completed, type: boolean, description: complete current revision-bound coverage}
    - {name: conflicts_found, type: integer, description: actual reviewed conflicts}
    - {name: impacted_features, type: array, description: existing FEATURE IDs with CR markers}
    - {name: conflicting_docs_updated, type: array, description: actual minor conflict paths}
    - {name: conflicting_docs_retired, type: array, description: actual major retirement paths}
    - {name: epic_id, type: string, description: allocated/reused intake Epic}
    - {name: mockup_list, type: array-or-NA, description: resolved upstream/input references}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: Complete candidate with discovery and referenced resources, test: installed creator validator}
    - {id: AC-S02, category: structure, criterion: About 200-300 entry lines with <=1000 logical body-line ceiling, test: body count}
    - {id: AC-C01, category: contract, criterion: Preserve full original task_completion_output keys and conditional successor list, test: YAML comparison to live entry}
    - {id: AC-C02, category: ownership, criterion: Common lifecycle once with no child board/Git/successor boilerplate, test: contract inspection}
    - {id: AC-C03, category: domain, criterion: Input initialization preserves idea/mockups/language/Epic identity, test: XML and domain assertions}
    - {id: AC-C04, category: domain, criterion: Fresh all-part coverage can reuse summaries with affected delta review; missing coverage establishes baseline, test: resource inspection}
    - {id: AC-C05, category: domain, criterion: Bounded questions and all three modes use common lifecycle authority, test: policy contract assertions}
    - {id: AC-C06, category: domain, criterion: Preserve CR markers/minor edits/major retirement and unrelated FRs/ACs, test: domain template/resource assertions}
    - {id: AC-C07, category: domain, criterion: Preserve pre-append >500 split boundary/index/links and legacy/new IDs, test: contract assertions; authoring pilot not claimed}
    - {id: AC-I01, category: integration, criterion: Mandatory shared action and both keyed outputs match real app/prompt/tool config, test: consumer assertions}
    - {id: AC-I02, category: integration, criterion: Real write/readback succeeds in temporary projects without completing successor, test: installed CLI subprocess tests}
    - {id: AC-I03, category: integration, criterion: Invalid tags/folder arrays or missing state/action/locked prerequisite do not mutate existing temporary state, test: negative helper tests}
    - {id: AC-I04, category: honesty, criterion: Missing-tag/nonexistent-file writer acceptance is NOT domain completion, test: helper characterization plus explicit domain guard assertions}
  should:
    - {id: AC-R01, criterion: Reuse one canonical template through compatible resource path}
    - {id: AC-R02, criterion: Small/new/CR/blocked examples contain no contradictory mandatory orchestration}
  could:
    - {id: AC-E01, criterion: Add future representative authoring pilots after independent review}
  wont:
    - {id: AC-W01, criterion: Board/memory/Git/source/other skill writes, reason: expressly excluded by current scope}
    - {id: AC-W02, criterion: Broader pipeline completion, reason: only this package is published; breakdown remains separately reviewed}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: lifecycle, description: one owner/readiness/policy/boundary}
    - {name: x-ipe-tool-x-ipe-app-interactor, relationship: integration, description: workflow-mode actual installed update/read helpers}
  artifacts:
    - {path: x-ipe-docs/config/workflow-template.json, description: shared action gates/contexts/tags}
    - {path: x-ipe-docs/config/tools.json, description: stages.requirement.gathering tool policy}
    - {path: src/x_ipe/static/js/features/workflow-stage.js, description: authoritative action/skill map}
test_scenarios:
  happy_path:
    - {name: Single and numbered requirement output, given: real temp document/folder/state, when: installed CLI update and read, then: exact outputs done; successor remains pending}
  edge_cases:
    - {name: Fresh small or CR context, given: complete hash-bound coverage, when: domain review, then: reuse unchanged summaries and inspect affected delta; contract only here}
  error_cases:
    - {name: Writer lacks semantic validation, given: missing folder tag/nonexistent file, when: helper called, then: acceptance characterized but candidate requires blocked domain claim}
  blocking:
    - {name: Missing workflow/action or locked prerequisite, given: invalid temp state, when: helper called, then: nonzero exit and preserved state}
evaluation:
  self_check:
    - Installed validator and common requirement-specific tests pass at recorded revisions
    - Complete package has five retained/updated paths and one new context reference; no removals
    - Historical execution-log.yaml is not current evidence; use TASK-6749 receipts
  judge_agent:
    - criterion: Semantic lifecycle/domain integration review
      rubric: Main independent review approved; see independent-review-TASK-6749.md and promotion-receipt-TASK-6749.json
version_history:
  - version: "2.2.0"
    date: 2026-10-13
    task_id: TASK-6749
    changes: Independently reviewed goal coverage with canonical shared contract; six-file byte parity, 307 tests passed
    candidate_hash: c020a439d33be6e4653d954d644ed183b01ca05ce7cb6a0adaed1ee0a41ab6e0
    parity_receipt: promotion-receipt-goal-TASK-6749.json
  - version: "2.1.0"
    date: 2026-10-13
    task_id: TASK-6749
    changes: Single-owner lifecycle adoption with delta-first requirements and verified domain/action contracts
    candidate_hash: fda78fe5234e0d054a4b720e0773ed30cac8f1e39a10215ce277882576ab294b
    parity_receipt: promotion-receipt-TASK-6749.json
```

  ## R2 recovered publication history

  - Version 2.2.1, TASK-6749; verified 2026-10-14T04:28:27.605298+00:00.
  - Current production/candidate fingerprint: 1aed46f6ca4829599fd330117b0dc400d4a8d36c3bd493e03458991da6a51a27.
  - [Recovered verification receipt](publication-receipt-TASK-6749-R2.json); prior history above remains historical, not current parity evidence.
  - Hybrid inner guidance and human completion/route boundary independently reviewed at exact R2 hash. Prior-worker promotion time is unknown; no production replay or atomic writer journal claimed.

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `8ca70bc159288e95f302ae3b00516edc3a875d96213046f9a95992cc95d855cc`
- Previous revision: `1aed46f6ca4829599fd330117b0dc400d4a8d36c3bd493e03458991da6a51a27`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.
