# Quality sync — TASK-6749 verified publication metadata

Tool-template-derived metadata, 2026-10-14. New metadata record for this candidate;
no historical release/version invented. Original two-file baseline is retained in recovery metadata.
Complete five-file candidate retains original operation fields and example domains,
adds procedures/schema/report scaffold; no resource deletion. See delta plan for
prior read-only receipt parity, prework inventories, named contribution and risks.

Independent final-revision review passed; current user authorized patch-only promotion.
Earlier publication stopped after three failed removal corrections. Current user
authorized preserving the harmless production blank in the two candidate files.
Fresh byte comparison proves exactly one LF added to each previously reviewed
candidate file; no substantive content changed. Full five-file parity is true,
fresh installed validation passes, and publication receipt/history now record
the reconciled revision. No authority for
board/memory/Git/lifecycle/app or unrelated production changes. No strict
consumer integration, autonomous agent run or stakeholder observation claimed.

```yaml
skill_name: x-ipe-tool-code-quality-sync
skill_type: x-ipe-tool
version: "2.0.0"
planned_version: "2.0.0"
status: production
created: 2026-10-14
updated: 2026-10-14
task_id: TASK-6749
publication_state: published
independent_review: passed_final_revision_review
candidate_hash: a9e1adf0066f237d4600b78be44f9ba205afba2fd9af3514488fc49768074753
summary: Align affected documentation and critical preservation tests against approved source-authoritative goals with mode-aware scope, honest evidence and no acceptance laundering.
triggers: [sync docs with code, improve quality before refactoring, update specs for refactoring, align documentation]
not_for:
  - "x-ipe-task-based-code-refactor: execute source refactor or own task lifecycle"
  - "x-ipe-tool-refactoring-analysis: inspect and recommend before sync"
  - "x-ipe-task-based-bug-fix: restore broken approved behavior"
  - "x-ipe-task-based-change-request: authorize changed scope or acceptance"
inputs:
  required:
    - {name: operation, type: string, validation: full_sync only, description: Single assessment or authorized sync operation}
    - {name: refactoring_scope, type: object, description: Exact actual analysis scope and purpose including target goals and supplied extensions}
    - {name: code_quality_evaluated, type: object, description: Actual analysis findings with independent domain states and provenance}
    - {name: refactoring_suggestion, type: object, description: Exact pass-through goals and target_structure}
    - {name: refactoring_principle, type: object, description: Exact pass-through principles and constraints}
  optional:
    - {name: refactoring_mode, type: string, default: broad, validation: study-only or local or broad, description: Explicit mode wins; legacy broad grants no write scope}
    - {name: program_type, type: string, default: null, description: Resolve actual domain including skills/documents from inspected target}
    - {name: sync_context, type: object, default: null, description: Actual approved paths/exclusions/intent/report/base-target/checks/coverage policy; missing write authority permits inspection only}
outputs:
  state:
    - {name: success, value: true | false}
  artifacts:
    - {name: validation_report, type: file, path: "x-ipe-docs/refactoring/validation-{context}.md", description: Authorized existing artifact with goal-to-doc-to-test mapping and readiness gaps}
  data:
    - {name: operation_output, type: object, description: Original success/result/errors and result nesting; explicit status/nullability delta}
    - {name: code_quality_evaluated, type: object, description: Actual aligned/divergent/unavailable evidence and counts; code_alignment exact input; numeric scores/coverage nullable}
    - {name: refactoring_scope, type: object, description: Exact original scope and target goal extensions; no bug repair scope appended}
    - {name: refactoring_suggestion, type: object, description: Exact original goals and target_structure}
    - {name: refactoring_principle, type: object, description: Exact original principles/constraints}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: Complete tool candidate with original resources plus domain procedures/schema/report and valid frontmatter/XML/sections/line limits, test: Installed creator validator and exact inventory}
    - {id: AC-P01, category: preservation, criterion: full_sync original operation_output fields/pass-through scope/goals/targets/principles and code_alignment retained; no task or Git duplication, test: Frozen original output plus concrete serialization and forbidden contracts}
    - {id: AC-G01, category: goals, criterion: Approved source goal/parent and story/GWT AC/type/constraints mapped to considered docs and critical evidence; no invented stakeholder outcome, test: Actual disposable authority/doc/check evaluator and negative goal/type/outcome fixtures}
    - {id: AC-D01, category: domain, criterion: Requirements/features/technical design gaps reconciled against approved behavior; descriptive drift separate from bug/CR and missing intent, test: Actual approved doc drift and wrong-behavior-green versus expected-failure fixtures plus policy checks}
    - {id: AC-M01, category: scope, criterion: Study read-only/local targeted/broad relevant integration checks; 80 percent broad guideline not unrelated blocking or critical-path waiver; skills/docs no forced newinfra, test: Mode policy and real below-guideline fixture coverage with explicit mandatory policy variant}
    - {id: AC-E01, category: evidence, criterion: Critical changed paths at base and target with unchanged assertions/current dates/source-test-doc-config hashes; failed and unavailable distinct; numeric null honest, test: Actual runtime fixture mapping evaluator with stale/missing/failed/hash/score negative cases and nullable serialization}
    - {id: AC-F01, category: freshness, criterion: Root metadata/cases/receipt match candidate fingerprint; unchanged live baseline/prior receipts; no promotion before independent review, test: Fresh receipt/meta/must-case mapping and live inventory checks}
  should:
    - {id: AC-L01, criterion: Explicit source containment/identity and consumer compatibility gaps; no silent fallback or null coercion}
  could:
    - {id: AC-X01, criterion: Future separately authorized autonomous sync pilot and strict-consumer integration}
  wont:
    - {id: AC-W01, criterion: Claim promotion without exact byte parity, reason: Review and user authority do not waive the parity gate}
    - {id: AC-W02, criterion: Perform broad source repair or rewrite approved requirements, reason: Sync domain is evidence and bounded docs/tests}
dependencies:
  skills:
    - {name: x-ipe-task-based-code-refactor, relationship: caller}
    - {name: x-ipe-tool-refactoring-analysis, relationship: required input provider}
  artifacts:
    - {path: .github/skills/x-ipe-workflow-task-execution/references/goal-contract.md, description: Document-local source/parent/outcome and evidence semantics only; no lifecycle invocation}
    - {path: x-ipe-docs/config/tools.json, description: Existing tracing policy when implicated; no configuration mutation}
test_scenarios:
  happy_path:
    - {name: Approved descriptive drift, given: Actual disposable price API/spec/requirements/design, when: Consider docs and execute unchanged base/target checks, then: Required goal/AC/type and hashes map; only descriptive design changes}
    - {name: Study nullable output, given: Skill/document study with no applicable coverage, when: Serialize original operation fields, then: Actual null and readiness false; goals/extensions preserved}
  error_cases:
    - {name: Bug is not drift, given: Equality-valid bug and green wrong-behavior test, when: Execute approved expected rejection, then: Actual failure retained and source/requirement unchanged}
    - {name: Stale evidence, given: Changed test/doc/config/source hash or missing goal/critical AC, when: Evaluate fixture linkage, then: Reject unsupported alignment claim}
    - {name: Binding threshold, given: Real below-80 scoped measurement, when: Guideline versus explicitly required fixture policy, then: Guideline alone does not block; mandatory policy does}
evaluation:
  self_check:
    - Installed structural validator plus authored policy/schema checks and actual disposable evidence fixtures.
    - Fixture evaluator is test-local and bounded; not an autonomous sync engine or production behavior proof.
  judge_agent:
    - {criterion: Independent review, rubric: Prior independent final-revision review retained; newline-only reconciliation independently checked against prior hashes with fresh deterministic validation}
version_history:
  - {version: "2.0.0", date: 2026-10-14, task_id: TASK-6749, candidate_hash: a9e1adf0066f237d4600b78be44f9ba205afba2fd9af3514488fc49768074753, change: Authorized patch promotion verified after adopting harmless production EOF blanks in candidate; no substantive delta from reviewed content}
```
