# Code Refactor — TASK-6749 candidate metadata

## Current publication — 2026-10-14

Published version 2.0.0 after independent final-revision review, fresh tests and
exact five-file candidate/live parity. Three changed files, two additions, no
deletions. User-authorized editors only; no publisher transaction/recovery claim.
See review-main-TASK-6749.md and publication-receipt-goal-TASK-6749.json. Final
candidate includes the dependency-version correction and is re-reviewed, not
approved on obsolete draft bytes. No board/memory/Git/other production writes.

## Historical candidate notes (superseded, retained)

Template-derived root metadata; no prior root metadata existed and no historical
version/history is invented. Live three-file baseline and prework candidate delta
are recorded externally. Original examples/techniques use cases remain, with
unsupported scores/commits/behavior-changing test updates removed. Five-file
candidate adds integration and report scaffold; no publishable resource deletion.
No lessons selected. Same supplied task; no board/memory/Git/app/other source writes.

Named internal quality improvement: bounded behavior-preserving refactoring with
inspected baseline, explicit trade-offs and actual evidence instead of forced
lifecycle/global prerequisites or synthetic scores. Entry has five domain actions;
all three resource files are complete. Actual fixture demonstrates two repeated
price decisions to one, same six public/error checks at both revisions, unchanged
tests, extra-call trade-off. This is fixture engineering, not application refactor,
autonomous agent execution or observed stakeholder outcome.

Installed analysis/sync remain full-only with numeric/80%/global assumptions;
scoped adapters disclose non-invocation. Real app code_refactor optional=false is
unchanged. Coverage retains original keys with percentage-string-or-null sides
and nullable comparison; not measured is explained in the report. Strict legacy
consumers require verified integration, not fictional completion or forced 80%.
Promotion is authorized but blocked by unavailable independent review of the
corrected revision. No publication receipt or production writes.

Blank-output recovery verified the complete current five-file draft without
redrafting resources or weakening tests. The saved receipt predated the current
integration reference; refreshed receipt and metadata now bind its actual bytes.
Fresh focused suite: 72 passed, zero failures/skips/deselections (1.74s). Both
installed validators pass without errors or warnings. Existing bug promotion
has exact four-file candidate/live/publication-receipt parity; no re-promotion.
See review-handoff-TASK-6749.md for current fingerprints, limits and reviewer gates.

The preceding recovery run is historical. Current corrected candidate and every
resource agree on nullable coverage. Fresh combined dedicated/creator suites:
232 passed, zero failures/skips/deselections, exit 0 (3.85s). Current fingerprints,
protection and review blocker are in test-cases.yaml and review-correction-TASK-6749.md.
No promotion performed; old review-handoff fingerprint is superseded.

## Current settled metadata

```yaml
skill_name: x-ipe-task-based-code-refactor
skill_type: x-ipe-task-based
version: "2.0.0"
planned_version: "2.0.0"
status: production
created: 2026-10-13
updated: 2026-10-14
task_id: TASK-6749
publication_state: published
independent_review: passed_final_revision_review
candidate_hash: 10be4133be03f6c4c1a654c17232ed6e3edd0d23c32b0717ff980056c9232e3e
summary: Preserve approved externally-visible behavior while demonstrating a named measurable or qualitative quality improvement against inspected baseline with scope-aware verification and honest trade-offs.
triggers: [refactor code, execute refactoring, analyze for refactoring, code quality assessment]
not_for:
  - "x-ipe-task-based-bug-fix: restore a reported behavior deviation"
  - "x-ipe-task-based-change-request: change approved goal or behavior contract"
workflow:
  category: feature-stage | standalone
  phase: validation
  next_task_based_skill:
    - {skill: x-ipe-task-based-feature-acceptance-test, condition: Re-verify after refactoring}
    - {skill: x-ipe-task-based-feature-closing, condition: Close feature if refactoring is the final step}
  human_review: true
  current_app_action: code_refactor
  action_optional: false
inputs:
  required:
    - {name: task_id, type: string, description: Same supplied lifecycle task/readiness}
    - {name: task_based_skill, type: string, description: Exact canonical discovered name}
    - {name: process_preference.interaction_mode, type: string, default: interact-with-human, description: Exact three-mode caller policy/source}
    - {name: refactoring_scope, type: object, description: Authorized feature/custom scope and purpose/files/modules/description}
  optional:
    - {name: execution_mode, type: string, default: free-mode}
    - {name: workflow, type: object, description: Actual identity/action/context; required app contexts retained}
    - {name: category, type: string, description: Original feature-stage or standalone}
    - {name: next_task_based_skill, type: array, description: Original conditional suggestions not execution authority}
    - {name: refactoring_mode, type: string, description: Intent-derived study-only/local/broad; explicit mode wins}
    - {name: program_type, type: string, description: Actual runtime/domain not suffix; skills use creator}
    - {name: tech_stack, type: array, default: [], description: Verified stack/runtime and affected layers}
outputs:
  state:
    - {name: category, value: feature-stage | standalone}
    - {name: status, value: completed | blocked}
    - {name: next_task_based_skill, value: Original conditional list}
    - {name: process_preference.interaction_mode, value: Original nested caller enum}
  artifacts:
    - {name: analysis_report, type: file, path: "x-ipe-docs/refactoring/analysis-{context}.md", description: Actual findings/source/goal/baseline and disclosed tool/adapter output}
    - {name: validation_report, type: file, path: "x-ipe-docs/refactoring/validation-{context}.md", description: Actual affected sync and preservation evidence; combined report only if accepted}
    - {name: refactored_files, type: file, path: Actual approved changed paths, description: No study source mutation; actual partial links only}
    - {name: refactor_report, type: file, path: Actual report path, description: Existing workflow refactor-report tag only when gates met}
  data:
    - {name: execution_mode, type: string, description: Original actual mode}
    - {name: workflow.name, type: string, description: Exact original identity or N/A}
    - {name: task_output_links, type: array, description: Actual reports and changed files only}
    - {name: feature_id, type: string, description: Actual scope feature or N/A; no allocation}
    - {name: refactoring_summary.files_modified, type: string, description: Actual count}
    - {name: refactoring_summary.files_created, type: string, description: Actual count}
    - {name: refactoring_summary.files_deleted, type: string, description: Actual count}
    - {name: refactoring_summary.principles_applied, type: array, description: Original principle/application_count/areas fields}
    - {name: refactoring_summary.goals_achieved, type: array, description: Original goal/status achieved-or-partial-or-skipped/notes; study not achieved structure}
    - {name: code_quality_evaluated.quality_score_before, type: string, description: Comparable justified numeric string or not measured; no synthetic metric}
    - {name: code_quality_evaluated.quality_score_after, type: string, description: Comparable justified numeric string or not measured; no numeric-tool sentinel}
    - {name: code_quality_evaluated.test_coverage, type: object, description: Original before/after percentage strings or actual null; maintained-or-improved-or-degraded or actual null; unmeasured reason in report}
    - {name: code_quality_evaluated.references_updated, type: object, description: Original requirements/specifications/technical_designs actual count fields}
    - {name: supplied legacy/dynamic fields, type: passthrough, description: All existing optional fields retained; no alternative reference output schema}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: Complete five-file candidate with valid metadata/frontmatter/section/XML/body/checkpoint contracts, test: Installed validator and parse}
    - {id: AC-P01, category: preservation, criterion: All original output keys/order/nested fields retained with explicit unmeasured score strings and nullable coverage delta; live exact reviewed candidate parity, test: Frozen original output comparison and baseline-bound publication receipt plus concrete nullable handoff}
    - {id: AC-G01, category: goal, criterion: Source/parent/stakeholder/internal contribution/all-required or alternatives/baseline/success/preservation/AC/type/trade-off and honest outcome, test: Authored quality row/scaffold and negative fixtures}
    - {id: AC-G02, category: evidence, criterion: Named measurable or qualitative improvement with inspected before/after; study recommendations not achieved; no arbitrary score or stakeholder observation, test: Disposable six-check price fixture plus authored negative claims}
    - {id: AC-M01, category: modes, criterion: Study read-only/local targeted docs-risk tests/broad relevant integration and measured coverage; no study/local global 80% or full docs prerequisite, test: Three mode contracts and tool adapter limits}
    - {id: AC-A01, category: authority, criterion: Actual human CR before behavior change all modes; no spec rewrite to bless code or failing assertion skip, test: Three-mode source/authority policy}
    - {id: AC-L01, category: lifecycle, criterion: Same task/readiness one owner no duplicate registration/routes/Git checkpoint commits; dirty work protected default no commit, test: Five actions and all-resource forbidden-block assertions}
    - {id: AC-T01, category: tools, criterion: Actual analysis output consumed or disclosed scoped adapter; targeted sync uses findings; numeric schemas unchanged and no fake full operation, test: Installed contracts reviewed and non-invocation guidance}
    - {id: AC-T02, category: routing, criterion: Actual stages.validation.code_refactor opt-in semantic sequential operation refactor; explicit false respected; special creator for skill package not arbitrary production edits, test: Real config and routing reference}
    - {id: AC-I01, category: integration, criterion: Actual mandatory action/context/report tag/predecessors unchanged until verified integration; conditional owner write/readback no fake done, test: Real template/UI and disposable installed helper exact/missing report characterizations}
    - {id: AC-B01, category: behavior, criterion: Public results/errors preserved with same assertions at both revisions and named duplication decrease plus trade-off, test: Actual disposable fixture six passed before and after; unchanged test hashes}
    - {id: AC-R01, category: resources, criterion: Original module split/rollback/planning/tracing examples and techniques completed with plain output guidance not contradictory schema, test: Complete resources and scaffold contract}
    - {id: AC-E01, category: freshness, criterion: Saved receipt and rootmetadata/tests/current candidate fingerprint agree; independent final review passed and exact publication parity, test: Recompute receipt and must-case mapping plus baseline-bound publication receipt}
  should:
    - {id: AC-D01, criterion: Existing tracing/redaction retained; disabled/absent tracing not forced}
    - {id: AC-C01, criterion: Explicit nullable coverage schema and strict legacy consumer gap without fabricated comparison}
  could:
    - {id: AC-X01, criterion: Later authorized full application refactor or autonomous tool/browser pilot}
  wont:
    - {id: AC-W01, criterion: Promote without independent review, reason: Final complete revision requires actual independent review}
    - {id: AC-W02, criterion: Mutate tools/app/template or other source, reason: Explicit scope exclusion}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: prerequisite, description: Lifecycle and goal contract}
    - {name: x-ipe-tool-refactoring-analysis, relationship: tool, description: Actual full contract or disclosed bounded adapter}
    - {name: x-ipe-tool-code-quality-sync, relationship: tool, description: Consumes analysis; full or disclosed targeted adapter}
    - {name: x-ipe-meta-skill-creator, relationship: conditional, description: Mandatory skill-package route with same task}
    - {name: enabled implementation tool skills, relationship: routing, description: Load actual operation refactor contract}
  artifacts:
    - {path: x-ipe-docs/config/tools.json, description: Existing code_refactor routing and checkpoint advisory not authority}
    - {path: x-ipe-docs/config/workflow-template.json, description: Current mandatory app gate and refactor-report}
    - {path: src/x_ipe/static/js/features/workflow-stage.js, description: Actual skill/action mapping}
test_scenarios:
  happy_path:
    - {name: Local fixture, given: Two duplicated price decisions and six preservation checks, when: Shared private decision with public wrappers, then: Six pass at both revisions and one decision; extra call trade-off}
  edge_cases:
    - {name: Study-only, given: Missing docs and assessment intent, when: Read-only gap report, then: No forced global sync or fake action completion}
    - {name: Broad API split, given: Public consumers import old module, when: Function moved, then: Retain re-export and unchanged consumer assertions}
  error_cases:
    - {name: Permissive writer, given: Missing report path in disposable project, when: Installed helper writes done, then: Writer succeeds but semantic readiness not established}
  blocking:
    - {name: Missing review or changed contract, given: Candidate-only or unapproved changed behavior, when: Completion/publication claim, then: Pertinent blocked state and full actual partial evidence}
evaluation:
  self_check:
    - Installed deterministic validation and exact output/baseline/resource contract tests.
    - Actual disposable fixture and helper behavior distinct from authored policies and production changes.
    - Independent final-revision review passed; exact editor publication verified.
  judge_agent:
    - {criterion: Independent review, rubric: Separate main reviewer re-read final corrected package and current evidence before authorized publication}
version_history:
  - {version: "2.0.0", date: 2026-10-14, task_id: TASK-6749, changes: Goal-bound mode-aware preservation with nullable coverage and revision-specific dependency checks, receipt: publication-receipt-goal-TASK-6749.json}
```

## R2 recovered publication history

- Version 2.0.1, TASK-6749; verified 2026-10-14T04:28:27.605298+00:00.
- Current production/candidate fingerprint: 618798d24f0c149069d3ddbd50e3f0e92730840b75e595a1c05842a5733ae691.
- [Recovered verification receipt](publication-receipt-TASK-6749-R2.json); prior history above remains historical, not current parity evidence.
- Hybrid inner guidance and human completion/route boundary independently reviewed at exact R2 hash; study/local/broad, preservation and nullable honest measurements retained. Prior-worker promotion time is unknown; no production replay or atomic writer journal claimed.

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `40c0cdd5c16ef4faeb8419f85256bb4b6195fdaa8281da370df7e28916fe2422`
- Previous revision: `618798d24f0c149069d3ddbd50e3f0e92730840b75e595a1c05842a5733ae691`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.

## TASK-6752 proportional-delivery revision

Published through the installed manifest-safe publisher after bounded compatibility review, correction of its TypeScript test-path finding, deterministic validation and affected post-publication regressions. Prior metadata remains historical.

- Current revision: `ae3866637633d6423a0282d74da029be699b8358f115223e22caa1f52a54c17b`
- Previous revision: `40c0cdd5c16ef4faeb8419f85256bb4b6195fdaa8281da370df7e28916fe2422`
- Evidence: `lean-delivery-TASK-6752.json`, `publication-receipt-TASK-6752.json`, `validation-receipt-TASK-6752.json`.
- Verification: 599 selected checks passed; exact installed/candidate byte parity. No resource removals, mirror synchronization or Git mutation.
- Live-agent efficacy, token/latency savings and stakeholder outcome remain unmeasured.
