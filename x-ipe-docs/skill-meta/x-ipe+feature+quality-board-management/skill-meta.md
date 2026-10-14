# Quality reporting — TASK-6749 candidate metadata

Existing-operation-scaffold metadata for the exact legacy category identity.
Generic category completion is not imposed: this skill retains its reporting
operations. Complete seven-file candidate, five original resources
retained, two additions, no deletions. Full original input/output declarations and
data-model bytes verified; template sections/content/placeholders preserved with
principles moved before feature results. No application schema changes.

Published after current main independent review and user-authorized patch promotion.
Read-only committed Git blobs establish the exact clean five-file baseline; all
seven production resources match candidate. Actual installed creator API/CLI
validate the category without adaptation. One final LF normalized in candidate
entry; fresh validation-category-TASK-6749.json supersedes its prior hash.
Historical adapted receipts and earlier blocked review remain historical. See
[current review](../x-ipe-meta-skill-creator/main-independent-review-TASK-6749.md)
and [publication receipt](publication-receipt-goal-TASK-6749.json).

```yaml
skill_name: x-ipe+feature+quality-board-management
skill_type: x-ipe-task-category
identity_compatibility: exact_existing_legacy_category_reporting_operations
version: "2.0.0"
planned_version: "2.0.0"
status: published
created: 2026-10-14
updated: 2026-10-14
task_id: TASK-6749
publication_state: published
independent_review: completed_by_current_main_reviewer
candidate_hash: d0a801c33c3daff2c9d31c30c5012dc9ee067f6bd80264060c786bb73dc6a137
summary: Preserve the original six-dimensional quality/report/suggestion contracts while reporting source-authoritative goals and revision-bound delivery separately from actual stakeholder outcomes.
triggers: [evaluate project quality, generate quality report, assess code alignment, quality evaluation, compare quality snapshots, check feature quality]
not_for:
  - "x-ipe-task-based-code-refactor: perform source restructuring"
  - "x-ipe-task-based-bug-fix: restore broken approved behavior"
  - "x-ipe-task-based-change-request: authorize changed intent or acceptance"
inputs:
  required:
    - {name: operation, type: string, description: Original caller operation, validation: generate or update or query or compare}
  optional:
    - {name: scope, type: object, default: all, description: Original all/feature_ids/module_paths and exact filter contract}
    - {name: compare, type: object, default: null, description: Original version_a/version_b latest/previous/vN contract}
outputs:
  state:
    - {name: success, value: true | false}
  artifacts:
    - {name: quality_report, type: file, path: x-ipe-docs/quality-evaluation/project-quality-evaluation.md, description: Original report structure plus document-local source/AC/evidence narrative; one current plus four historical reports}
  data:
    - {name: operation_output, type: object, description: Exact original success/operation/result/report_path/version/overall_score/health_status/features_evaluated/gaps/errors declaration; operation-specific query/compare meanings retained}
    - {name: QualityEvaluation, type: object, description: Exact original data-model bytes including all priority_gaps/refactoring_suggestions/principles/applications/constraints/recommendations fields; no goal or outcome schema key}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: Complete exact legacy category candidate retaining reporting operations and original result with initialized inputs/resources/limits, test: Actual installed creator validator API/CLI category receipt without adaptation}
    - {id: AC-P01, category: preservation, criterion: Entire original input/output/model and report field/section content preserved, test: Original YAML declaration equality/model byte parity/reference prefix equality/template block and placeholder equality}
    - {id: AC-G01, category: goals, criterion: Approved source/parent/stakeholder/outcome/contribution/selection/constraints and stable GWT AC/test type mapped in original artifact, test: Positive authored table and nine negative mutants}
    - {id: AC-E01, category: evidence, criterion: Revision-bound engineering evidence separate from real observation; no synthetic scores or unknown-as-planned, test: Authored guidance checks/failure-envelope equality and actual candidate Markdown service readback}
    - {id: AC-D01, category: domain, criterion: Six original dimensions/weights and suggestion model retained; bugs/docs drift/unimplemented intent/CR remain separate, test: Reference content preservation plus authored source-authority scenarios}
    - {id: AC-R01, category: compatibility, criterion: Real original report service and frontend tests unchanged and pass, test: Actual backend 28 tests/frontend 10 tests and disposable Flask current/history/content/404 checks}
    - {id: AC-F01, category: freshness, criterion: Actual category receipt matches candidate and unchanged production baseline; no promotion while preservation/review/ownership blockers remain, test: Fresh installed receipt and seven-file production parity; trusted committed baseline and actual patch publication receipt}
  should:
    - {id: AC-L01, criterion: Disclose legacy identity validator gap and original fractional-status/severity ambiguity without inventing a schema or silent rounding policy}
  could:
    - {id: AC-X01, criterion: Separately authorized autonomous quality evaluation and real stakeholder observation}
  wont:
    - {id: AC-W01, criterion: Promote despite blocking review or ownership evidence, reason: Creator publication gates remain mandatory despite current publication authority}
    - {id: AC-W02, criterion: New goal database/board/API model fields or source repairs, reason: Existing document-local report contract and authorized scope}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: Existing lifecycle owner and goal-contract reference only; no recursive invocation}
    - {name: x-ipe-tool-refactoring-analysis, relationship: Actual inspected contract for suggestion handoff; no successor execution}
  artifacts:
    - {path: .github/skills/x-ipe-workflow-task-execution/references/goal-contract.md, description: Document-local goal/evidence authority}
    - {path: src/x_ipe/routes/quality_evaluation_routes.py, description: Existing Markdown/version metadata serving; no scoring or retention implementation}
test_scenarios:
  happy_path:
    - {name: Source/AC mapping, given: Approved preferences authored fixture, when: Validate all mapping cells and domain UI GWT criterion, then: Complete source-linked mapping without observed outcome or numeric score}
    - {name: Actual report serving, given: Candidate template/examples in disposable report folder, when: Invoke unchanged Flask status/content routes, then: Exact Markdown readback and original response keys/current/history behavior}
  error_cases:
    - {name: Unsupported numeric success, given: Current test execution unavailable, when: Parse existing failure envelope, then: EVALUATION_INCOMPLETE and result empty without synthetic score/new schema}
    - {name: Invalid authored authority/outcome, given: Nine mutated mapping cells, when: Execute test-local assertions, then: Every mutant rejected; not autonomous agent evaluation}
    - {name: Legacy category identity, given: Exact existing plus-name reporting category, when: Invoke actual reviewed creator candidate validator with x-ipe-task-category, then: Pass without TYPES mutation; wrong tool subtype and lookalikes remain invalid}
evaluation:
  self_check:
    - Full original declaration/data-model preservation and seven-resource inventory.
    - Actual unchanged report service/frontend tests and disposable route readback are bounded; not score/retention/agent/outcome validation.
  judge_agent:
    - {criterion: Independent reporter review, rubric: Current main review covers final newline-normalized hash and creator executable delta; actual patch parity and preserved cache hashes recorded}
version_history:
  - version: "2.0.0"
    date: 2026-10-14
    task_id: TASK-6749
    publication_receipt: publication-receipt-goal-TASK-6749.json
    candidate_hash: d0a801c33c3daff2c9d31c30c5012dc9ee067f6bd80264060c786bb73dc6a137
    change: Source-authoritative document-local goals and revision-bound delivery/outcome evidence; original schema and seven resources preserved
```