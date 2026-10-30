# Task-Based Skill Metadata — Technical Design

## TASK-6749 technical-design sequential slice — reviewed and promoted

Creator goal/lifecycle contracts, both task-based templates, general guidelines,
all prior domain resources and actual configuration were loaded before drafting.
No relevant target lesson file exists; no lessons/memory changed. Same supplied
owner/task; board writes/registration, Git mutations, other production and dirty
documents explicitly excluded. Existing candidate had obsolete board aliases and
duplicated routing; their domain purpose is preserved, not blindly overwritten
from production. Full production/prework inventories are recorded separately.

All four original resource paths retained; one integration reference added;
no resource removal. Scaffold keeps two parts, tags/dependencies/usage, API/CLI/
data/interface examples, algorithms, planned tests, current mockups, tracing
redaction, safe paths and version/change history. Goal coverage uses upstream
FR/US/AC identifiers inside the existing design, not new schemas or KPIs.

```yaml
skill_name: x-ipe-task-based-technical-design
skill_type: x-ipe-task-based
version: "1.0.0"
status: production
created: 2026-10-13
updated: 2026-10-13
task_id: TASK-6749
publication_state: published
independent_review: new_main_session_review_passed_after_bounded_fix
candidate_hash: 7df91e86fe0264b67730e891af1b3a1196b07e18067d86757303ca0aee55944d
summary: One two-part design with authoritative goal-to-AC-to-means coverage, complete implementation contracts and same-owner lifecycle handoff.
triggers: [design feature, technical design, architecture planning]
not_for:
  - "feature-refinement: changing acceptance without authorized CR"
  - "code-implementation: executing consulted tools"
workflow:
  category: feature-stage
  phase: Technical Design
  next_task_based_skill:
    - skill: x-ipe-task-based-code-implementation
      condition: Implement the designed feature
  human_review: mode-aware lifecycle boundary plus required risk review
inputs:
  required:
    - {name: task_id, type: string, description: existing lifecycle task/readiness}
    - {name: feature_id, type: string, description: exactly one actual authorized feature}
    - name: process_preference.interaction_mode
      type: string
      default: interact-with-human
      validation: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
  optional:
    - {name: workflow, type: object, description: technical_design and required selected specification context}
    - {name: mockup_list, type: array-or-NA, description: actual current scoped mockups with full fallback resolution}
outputs:
  state:
    - {name: category, value: feature-stage}
    - {name: status, value: completed | blocked}
    - {name: next_task_based_skill, value: original conditional Code Implementation suggestion}
    - {name: process_preference.interaction_mode, value: resolved exact mode}
  artifacts:
    - {name: design, type: file, path: resolved owning feature folder/technical-design.md, description: one populated complete two-part design}
    - {name: feature-docs-folder, type: directory, path: resolved owning feature folder, description: existing scalar workflow tag}
  data:
    - {name: execution_mode, type: string, description: original caller context}
    - {name: workflow, type: object, description: original name}
    - {name: workflow_action, type: string, description: technical_design}
    - {name: workflow_action_updated, type: boolean, description: actual verified current/prior write only}
    - {name: task_output_links, type: array, description: actual design link in existing output, not board schema field}
    - {name: mockup_list, type: array-or-NA, description: original scoped mockups}
    - {name: feature_id, type: string, description: actual immutable identity}
    - {name: feature_title, type: string, description: actual title}
    - {name: feature_version, type: string, description: approved actual version}
    - {name: feature_phase, type: string, description: Technical Design}
    - {name: program_type, type: string, description: actual evidence-backed type}
    - {name: tech_stack, type: array, description: actual approved technologies}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: complete four original paths plus one integration reference, test: validator/manifests}
    - {id: AC-C01, category: contract, criterion: exact parsed original output keys/order/values and successor, test: YAML comparison}
    - {id: AC-C02, category: ownership, criterion: no duplicate task CRUD/Git/routing or recursive lifecycle, test: parsed procedure and resource inspection}
    - {id: AC-D01, category: domain, criterion: full two-part scaffold preserves interfaces/data/algorithms/tests/mockups/tracing and paths, test: scaffold rendering and contract review}
    - {id: AC-G01, category: goal, criterion: real upstream goal/subgoal/source and every scoped AC map to justified means and planned validation, test: concrete authored mapping plus negative mutations}
    - {id: AC-G02, category: goal, criterion: qualitative outcome scenario without invented KPI/scope or false delivery/outcome claim, test: artifacts and negative mutations; autonomous reasoning not claimed}
    - {id: AC-G03, category: delta, criterion: affected-only invalidation retains unaffected IDs/mapping bytes, test: authored upstream delta comparison}
    - {id: AC-I01, category: integration, criterion: actual action/both tags/required context/Designed status without new schema, test: installed temporary CLI/readback and UNKNOWN_FIELD rejection}
    - {id: AC-I02, category: config, criterion: semantic type/stack consultation respects technical_design config and no execution, test: actual config/tool declarations plus explicit contract inspection}
    - {id: AC-I03, category: safety, criterion: advanced CR status preserved and helper permissiveness not semantic completion, test: actual temporary helper cases}
  should:
    - {id: AC-R01, criterion: safe root links and all diagram/interface/data examples remain reusable}
    - {id: AC-R02, criterion: real type matching consultation is documented, not represented as executed routing}
  could:
    - {id: AC-E01, criterion: separately authorized autonomous design/consultation/CR reasoning pilots}
  wont:
    - {id: AC-W01, criterion: automatic release, reason: only technical-design editor promotion explicitly authorized after new main review}
    - {id: AC-W02, criterion: board/memory/Git/other production/dirty document writes, reason: explicit user boundary}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: lifecycle, description: same owner and goal/lifecycle contracts}
    - {name: x-ipe-tool-task-board-manager, relationship: integration, description: actual Refined/Designed and no design-link schema field}
    - {name: x-ipe-tool-x-ipe-app-interactor, relationship: integration, description: actual technical_design action readback}
  artifacts:
    - {path: resolved authoritative feature specification, description: source goal/story/AC/constraints}
    - {path: x-ipe-docs/config/tools.json, description: actual technical_design consultation config}
test_scenarios:
  happy_path:
    - {name: New design, given: upstream real authored goal/AC fixture, when: map selected means and render actual scaffold, then: complete mapping and honest planned/not measured states}
    - {name: Actual contracts, given: temporary new/legacy feature with done refinement, when: installed writer/readback and owner Designed update, then: exact tags/context/status and no task allocation}
  edge_cases:
    - {name: Parent delta, given: authored CR-061-01, when: compare upstream and downstream mappings, then: affected evidence invalidated and absence row unchanged}
    - {name: Advanced CR/resume, given: temporary Completed feature, when: actual supported version update/read-only queries, then: immutable identity/status/dependencies preserved}
  error_cases:
    - {name: Actual schema, given: attempted technical_design_link, when: installed board helper, then: UNKNOWN_FIELD and unchanged bytes}
    - {name: Permissive writer, given: missing file/tag/context and pending refinement, when: installed workflow writer, then: characterized success is not domain completion}
  blocking:
    - {name: Invalid helper contract, given: extra tags/folder array/missing feature/locked stage, when: installed writer, then: nonzero with unchanged state}
    - {name: Broken artifact claim, given: orphan/missing AC or false source/outcome/delivery, when: parse concrete authored mapping, then: rejected}
evaluation:
  self_check:
    - "Independent review revision: 337 passed before promotion; added Part-2-authority regression failed first and passed after candidate correction. Final downstream receipt carries later combined run."
    - "Installed validator: ok; 248 body lines; five-file manifest; four explicit uninstantiated scaffold link warnings."
    - "Earlier failed collection/import and six helper assumption failures were corrected; no hidden deselection."
    - "Original production baseline checked before explicitly authorized editor promotion; final full tree bytes equal reviewed candidate. No trusted managed provenance, transactional publisher backup or atomic recovery claimed."
  judge_agent:
    - criterion: Independent semantic/lifecycle/config/safety review
      rubric: New main session independent review covered goals/alternatives/two parts/config/deliverables/lifecycle; one scaffold wording finding fixed. User separately authorized editor promotion.
version_history:
  - {version: "1.0.0", date: 2026-10-13, task_id: TASK-6749, description: Reviewed goal-oriented design promoted via exact-file editor delta; five-file parity verified}
```

The prior author handoff below remains historical candidate-only evidence, not
the current publication state. publication-receipt-goal-TASK-6749.json records
explicit editor authorization, exact hashes/parity, and nontransactional limits.
The code-implementation slice remains candidate-only until its main reviewer.

## R2 recovered publication history

- Version 1.0.1, TASK-6749; verified 2026-10-14T04:28:27.605298+00:00.
- Current production/candidate fingerprint: 8a542b7595b566778f29127307fdcdcf00c740820e15063d070bebba5dd90aca.
- [Recovered verification receipt](publication-receipt-TASK-6749-R2.json); prior history above remains historical, not current parity evidence.
- Hybrid inner guidance and human completion/route boundary independently reviewed at exact R2 hash. Prior-worker promotion time is unknown; no production replay or atomic writer journal claimed.

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `a583877806d925bb99de7690e10cfa6a238aad42c17de714842a7678a778c523`
- Previous revision: `8a542b7595b566778f29127307fdcdcf00c740820e15063d070bebba5dd90aca`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.

## TASK-6752 proportional-delivery revision

Published through the installed manifest-safe publisher after bounded compatibility review, correction of its TypeScript test-path finding, deterministic validation and affected post-publication regressions. Prior metadata remains historical.

- Current revision: `3aed5a97ca72dfec5f6b6b699bd1f29bd2dee4cf8b211282b70b3aaf045f5051`
- Previous revision: `a583877806d925bb99de7690e10cfa6a238aad42c17de714842a7678a778c523`
- Evidence: `lean-delivery-TASK-6752.json`, `publication-receipt-TASK-6752.json`, `validation-receipt-TASK-6752.json`.
- Verification: 599 selected checks passed; exact installed/candidate byte parity. No resource removals, mirror synchronization or Git mutation.
- Live-agent efficacy, token/latency savings and stakeholder outcome remain unmeasured.
