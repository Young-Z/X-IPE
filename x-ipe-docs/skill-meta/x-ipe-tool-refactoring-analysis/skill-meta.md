# Refactoring analysis — TASK-6749 candidate metadata

## Current publication — 2026-10-14

Published version 2.0.0 after sequential independent final-revision review and
exact four-file candidate/live parity. Four changed files, no additions/deletions.
Final corrections cover malformed consultation flags and the numeric optional
legacy coverage alias. See review-main-TASK-6749.md and the exact editor receipt.
No publisher transaction/recovery or strict legacy consumer migration claimed.

## Historical candidate notes (superseded, retained)

Tool-template-derived metadata. Complete original four-path package; no resource
removal. Existing single-file candidate inspected/preserved in prework manifest,
then expanded with coherent domain references. No historical version invented.
Independent review pending until next review; publication not authorized for this
tool. No board/memory/Git/source/config/app/live writes.

Named contribution: useful behavior-preserving refactor recommendations linked to
actual caller goals/baselines/preservation/trade-offs, not size-only splits or
synthetic scores. Tool result preserved, contradictory task reference removed.
Numeric/status nullability is an explicit candidate schema delta; strict legacy
consumers remain a compatibility gap, no runtime integration claimed.

## Current settled metadata

```yaml
skill_name: x-ipe-tool-refactoring-analysis
skill_type: x-ipe-tool
version: "2.0.0"
planned_version: "2.0.0"
status: production
created: 2026-10-13
updated: 2026-10-14
task_id: TASK-6749
publication_state: published
independent_review: passed_final_revision_review
candidate_hash: f1c848402913264155e36e76397512d2ea9fa11a7571eb8e25a926b84ce17d97
summary: Goal-risk scoped analysis with verified bounded dependencies, five evidence perspectives and traceable recommendations; no invented metrics or source changes.
triggers: [analyze for refactoring, evaluate refactoring scope, assess code quality, code quality analysis]
not_for:
  - "x-ipe-task-based-code-refactor: execute refactoring or manage task lifecycle"
  - "x-ipe-tool-code-quality-sync: authorized synchronization"
inputs:
  required:
    - {name: operation, type: string, validation: full_analysis only, description: Single analysis operation}
    - {name: scope, type: object, description: Original feature/custom purpose/files/modules/description and actual identity}
  optional:
    - {name: quality_baseline_path, type: string, default: x-ipe-docs/planning/project-quality-evaluation.md, description: Historical baseline checked for comparability; missing default valid}
outputs:
  state:
    - {name: success, value: true | false}
  artifacts:
    - {name: analysis_report, type: file, path: "x-ipe-docs/refactoring/analysis-{context}.md", description: Caller-authorized actual report; no source/test/config writes}
  data:
    - {name: operation_output, type: object, description: Original success/result/errors and all result keys; numeric null and explicit evidence status extensions}
    - {name: quality_baseline, type: object, description: Original exists/overall_score plus historical domain fields/provenance}
    - {name: refactoring_scope, type: object, description: Actual purpose/files/modules/dependencies/log with bounded frontier and authorized versus inspected distinction}
    - {name: code_quality_evaluated, type: object, description: Original summaries plus separate five perspectives and all domain assessment fields}
    - {name: refactoring_suggestion, type: object, description: Original summary/goals/target_structure and report-linked source/goal/baseline/success/preservation/trade-off}
    - {name: refactoring_principle, type: object, description: Original primary/secondary principles and stability constraints}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: Complete original four-file tool candidate with valid frontmatter/XML/sections/body/checkpoints, test: Installed creator validator and manifest comparison}
    - {id: AC-P01, category: preservation, criterion: full_analysis operation_output legacy keys and domain references preserved; no task output/lifecycle/source writes, test: Original output comparison and forbidden contracts}
    - {id: AC-G01, category: goals, criterion: Each suggestion cites actual gap/source/goal/parent/baseline/success/preservation/trade-off; outcome not measured, test: Authored temporary report and negative trace cases}
    - {id: AC-D01, category: scope, criterion: Verified outgoing/inverse dependency edges with bounded visited closure and disclosed cap/frontier; no sibling proximity expansion, test: Actual disposable AST cycle and chain cap fixtures plus policy checks}
    - {id: AC-E01, category: evidence, criterion: All five perspectives separate; absent/unmeasured/not applicable/unavailable distinct from executed failure; no global compile gate, test: Domain policy and actual attempted exit versus unavailable fixture}
    - {id: AC-N01, category: measurement, criterion: Numbers only actual measured inputs with comparable authoritative rubric; otherwise null not fabricated weighted score, test: Nullable authored output and schema/policy checks}
    - {id: AC-C01, category: configuration, criterion: Existing analysis route metadata-first matched consultation; boolean opt-in and malformed-config failure; no mass tool loading, test: Actual config and malformed/all-false/metadata-only policy regressions}
    - {id: AC-R01, category: resources, criterion: Original API/payment/baseline/gap/tracing/SOLID/KISS/modular records preserved without contradictory task schema, test: Complete resources and domain/example checks}
    - {id: AC-F01, category: freshness, criterion: Fresh receipt/current candidate/meta/cases match; independent final review and exact live publication parity, test: Recompute receipt/hash/must-case mapping and baseline-bound editor publication receipt}
  should:
    - {id: AC-L01, criterion: Canonical links and explicit selected source identity/containment; invalid source does not silently fall back}
  could:
    - {id: AC-X01, criterion: Future authorized autonomous analysis pilot or strict consumer integration}
  wont:
    - {id: AC-W01, criterion: Promote without independent final review, reason: Actual review and user permission required}
    - {id: AC-W02, criterion: Execute source repair or task workflow, reason: Tool analysis-only responsibility}
dependencies:
  skills:
    - {name: x-ipe-task-based-code-refactor, relationship: caller}
    - {name: semantically matched allowed implementation tools, relationship: conditional consultation}
  artifacts:
    - {path: x-ipe-docs/config/tools.json, description: Existing refactoring_analysis and tracing policy; not new configuration}
test_scenarios:
  happy_path:
    - {name: Goal trace, given: Actual fixture repeated decision gap, when: Read-only recommendation, then: Linked baseline/preservation/trade-off and no achieved outcome claim}
  error_cases:
    - {name: Missing docs or tool, given: No available perspective evidence, when: Analysis report, then: Absent/unmeasured distinct from attempted failure and no zero score}
    - {name: Capped chain, given: Pending frontier after ten passes, when: Return bounded analysis, then: Explicit incomplete scope not cycle/full closure claim}
evaluation:
  self_check:
    - Installed structural validator and dedicated authored-contract/disposable evidence tests.
    - No autonomous agent execution or application refactor/outcome proof claimed.
  judge_agent:
    - {criterion: Independent review, rubric: Separate main reviewer re-read final corrected four-file package and actual dependency contracts}
version_history:
  - {version: "2.0.0", date: 2026-10-14, task_id: TASK-6749, changes: Goal-risk bounded analysis with honest evidence and safe consultation plus legacy coverage preservation, receipt: publication-receipt-goal-TASK-6749.json}
```

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `c0d56d08b5c3d2de3ec53e1deff4069ac52ae842c3fc2a40027ce7e1609a732e`
- Previous revision: `f1c848402913264155e36e76397512d2ea9fa11a7571eb8e25a926b84ce17d97`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.
