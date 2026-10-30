# Refactoring analysis operation schema

Entry operation_output is authoritative. This reference expands retained domain
fields, not a task result/next-task instruction/approval workflow. Preserve all
original keys and supplied extensions; historical optional fields remain available.

## Types and evidence status

Scores: number | null, 1–10 only with actual measured inputs, authoritative comparable
rubric, method/scope/denominator/revisions. Actual null, not the string "null" or
"not measured" in numeric fields. Explain not measured with reason in report.
Percentages: legacy percentage string | null; measured zero is "0%", unknown null.
Absent tests/docs do not measure zero. Retain historical values/provenance separately
from fresh measurements. Unknown SOLID/KISS/modular status is null with notes, not good.

Evidence status (explicit schema delta): aligned | needs_attention | critical |
not_found | not_measured | not_applicable | failed. Original alignment/attention/
critical values require findings, not score bands. not_found is absence;
not_measured missing applicable measurement; not_applicable justified domain;
failed attempted applicable failed check with exit/output. Unavailable versus
executed failure stays distinguishable in evidence/limitations.

success=true: authorized analysis delivered, all five dispositions, traceable
suggestions (possibly empty), actual report and transparent limits. Not approval,
runtime preservation, aligned code or achieved outcome. success=false: required
input/scope/report cannot be satisfied, errors exact reason/path/revision and actual
partial result retained. Optional missing docs/coverage alone is not failure.
Strict consumers rejecting nullable/status delta receive compatibility blocker,
never fabricated values. Operation remains full_analysis; no new mode operation.

## Complete domain declaration

This is a declaration, not instantiated successful analysis evidence.

```yaml
operation_output:
  success: true | false
  result:
    quality_baseline:
      exists: true | false
      overall_score: "<number 1-10 | null>"
      evaluated_date: "<report date | null>"
      code_violations: {file_size: [], approaching_threshold: []}
      feature_gaps: []
      test_coverage: "<percentage string | null>"
      provenance: {report_path: null, hash: null, method: null, scope: [], comparable: false}
    refactoring_scope:
      scope_level: feature | custom
      feature_id: "<actual identity | null>"
      refactoring_purpose: "<caller quality goal>"
      files: []
      modules: []
      dependencies: []
      scope_expansion_log: []
      authorized_files: []
      expansion_state: stable | capped | bounded | unresolved
      remaining_frontier: []
      exclusions: []
    code_quality_evaluated:
      requirements_alignment:
        score: "<number 1-10 | null>"
        status: "<evidence status>"
        gaps: []
        related_docs: []
        violations: []
      specification_alignment:
        score: "<number 1-10 | null>"
        status: "<summary evidence status>"
        gaps: []
        feature_ids: []
        spec_docs: []
        violations: []
      feature_alignment: {score: null, status: not_measured, gaps: [], feature_ids: []}
      technical_spec_alignment: {score: null, status: not_measured, gaps: [], spec_docs: []}
      test_coverage:
        score: "<number 1-10 | null>"
        line_coverage: "<percentage string | null>"
        critical_gaps: []
        status: "<evidence status>"
        branch_coverage: "<percentage string | null>"
        current_percentage: "<legacy percentage number 0-100 | null when supplied>"
        target_percentage: "<applicable authoritative number | null>"
        external_api_mocked: "<observed boolean | null>"
        violations: []
        file_coverage: []
      tracing_coverage:
        score: "<number 1-10 | null>"
        status: "<evidence status>"
        coverage_percentage: "<measured percentage number | null>"
        untraced_functions: []
        unredacted_params: []
        gaps: []
      code_alignment:
        score: "<number 1-10 | null>"
        file_size_violations: []
        solid_assessment: {}
        kiss_assessment: {}
        status: "<evidence status>"
        files_approaching_threshold: []
        modular_design_assessment: {}
        code_smells: []
      overall_quality_score: "<number 1-10 | null>"
    refactoring_suggestion:
      summary: "<findings/limits>"
      goals: []
      target_structure: "<selected means or no justified change>"
    refactoring_principle:
      primary_principles: []
      secondary_principles: []
      constraints: []
    report_path: "<actual authorized report | null if not produced>"
  errors: []
```

Each perspective records applicability/reason, source/anchor/hash, check command/
exit when executed, limitations and measurement method/scope/denominator/rubric.
Report-linked records suffice, no new database. Specification summary keeps
separate feature/technical evidence; one source alone cannot substantiate both.

The historical optional test_coverage.current_percentage remains available and
passes through when supplied. Do not silently drop or overwrite it with
line_coverage: retain its original method/scope/provenance, and identify conflicts
if the two are not comparable. An absent alias need not be invented; absence is
not measured zero. Only an actual same-method measurement may populate an alias.
The original example uses a numeric percentage (62, not "62%"); retain that
number type for current_percentage, unlike line_coverage's percentage string.

## Retained structured records

- Dependencies: directed canonical source/target, verified reason/anchor/revision/
  resolution; unresolved explicit, not fictitious files. Log iteration/files_added/
  modules_added/reason plus checked edges/remaining frontier/exclusions.
- Violations: original type/importance/weight retained; weight number | null only
  from authoritative rubric, no invented severity mapping.
- Size: file/lines/severity/recommendation and approaching file/lines/buffer retained.
  Applicable threshold only; no automatic risk defect from size alone.
- SOLID srp/ocp/lsp/isp/dip status/notes retains good/partial/violation when inspected;
  KISS over_engineering/straightforward_logic/minimal_dependencies/clear_intent;
  modular module_cohesion/module_coupling/single_entry_point/folder_structure/
  reusability/testability. Unknown status null with notes.
- Smells retain smell/file/severity/details and god_class/long_method/large_file/
  deep_nesting/too_many_params/duplicate_code with evidence of actual goal risk.
- Goals retain goal/priority/rationale/principle, trace gap/source/revision/parent/
  baseline/success_evidence/preservation/trade_off/outcome_state in linked report.
  No size-only goal or automatic stakeholder outcome claim.
- Principles retain principle/rationale/applications area/action, constraints retain
  constraint/reason with API/backward behavior/security/performance/external boundaries.

## Original gap vocabulary and contextual thresholds

| Perspective | Gap Types |
| --- | --- |
| Requirements | undocumented, unimplemented, deviated |
| Features | missing, extra, deviated |
| Tech Spec | structure, interface, data_model, pattern |
| Test Coverage | business_logic, error_handling, edge_case |
| Tracing Coverage | untraced, unredacted, wrong_level |

Legacy quality-board context: line 80%, branch 70%, file 800, function 50, class
500, complexity 10. Only under applicable authoritative rubric, never universal
gates or safe preservation proof. External mocks depend on isolation contract;
integration may need real service evidence. No default weighted aggregate.
