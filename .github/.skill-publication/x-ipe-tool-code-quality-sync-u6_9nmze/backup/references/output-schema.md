# Quality sync operation schema

Preserve original operation_output.success/result/errors and all original result
keys/nesting. Preserve caller extensions, including quality_baseline if supplied,
refactoring_scope dependencies/goal frame and unknown domain fields. No task output.

## Types and compatibility delta

Alignment status retains legacy aligned/needs_update/not_found and analysis states
needs_attention/critical/not_measured/not_applicable/failed; explicit divergent and
unavailable are also permitted. Add alignment_state aligned|divergent|unavailable
plus reason/evidence, not a blanket replacement for detailed status. A not_applicable
record uses unavailable alignment_state with a reason, not false aligned.
Tests retain sufficient/insufficient/no_tests and allow not_measured/not_applicable/
failed/unavailable. sufficient requires applicable critical evidence and any adopted
authoritative threshold, never coverage alone.

line_coverage is percentage string | null. Unknown is actual null, not the string
"null", zero or "not measured". overall_quality_score and supplied score fields
are number | null; measured 1–10 only under an actual comparable authoritative
rubric with method/scope/denominator. No arbitrary score or fabricated improvement.
Preserve historical measured fields with their original provenance; current missing
measurement is null with reason. Preserve optional legacy current_percentage as
number 0–100|null when supplied, never coerce it to a percentage string or replace
its method/scope from line_coverage; flag conflicts. Absent alias need not be invented.

Counts are actual nonnegative integers in instantiated outputs. Declaration strings
below are placeholders, not executed success. report_path actual authorized file
or null when not produced; errors include exact reason/path/revision and partial
results. Strict consumers of old statuses/non-null metrics need verified adapters;
unsupported handoffs remain blocked, not coerced. No runtime compatibility claim.

## Complete domain declaration

```yaml
operation_output:
  success: true | false
  result:
    code_quality_evaluated:
      requirements_alignment:
        status: "<evidence status>"
        gaps: []
        updates_made: []
        related_docs: []
        alignment_state: "aligned | divergent | unavailable"
        evidence: []
      specification_alignment:
        status: "<evidence status>"
        gaps: []
        updates_made: []
        spec_docs: []
        alignment_state: "aligned | divergent | unavailable"
        evidence: []
      technical_spec_alignment:
        status: "<evidence status>"
        gaps: []
        updates_made: []
        spec_docs: []
        alignment_state: "aligned | divergent | unavailable"
        evidence: []
      test_coverage:
        status: "<evidence status>"
        line_coverage: "<percentage string | null>"
        tests_added: "<count>"
        tests_updated: "<count>"
        critical_gaps: []
        current_percentage: "<legacy numeric percentage | null when supplied>"
        evidence: []
      code_alignment: "{exact input object, not modified}"
      overall_quality_score: "<number 1-10 | null>"
      validation_summary:
        docs_created: "<count>"
        docs_updated: "<count>"
        tests_added: "<count>"
        ready_for_refactoring: true | false
    refactoring_scope: "{exact input including target goals/extensions}"
    refactoring_suggestion: "{exact input including goals/target_structure}"
    refactoring_principle: "{exact input including constraints}"
    report_path: "<actual authorized report | null>"
  errors: []
```

Preserve feature_alignment, tracing_coverage, quality scores, violations and other
analysis domain fields when supplied; rechecked updates name their evidence.
Do not collapse the technical and feature perspectives into specification status.
Evidence mapping can live in the existing report, not mandatory new schema fields.

## Readiness and goal coverage

Consider source goal/parent and all required AC/test-type/constraint branches;
preserve selected alternatives. Evidence records cite actual dates and fingerprints
for base/target/source/test/doc/config, command/cwd/exit/result and limitations.
aligned needs approval-consistent current verification; divergent needs conflicting
evidence; unavailable needs a reason. Missing documents/tests cannot establish zero
coverage, wrong-behavior passing tests cannot establish goal coverage.

Completed authorized assessment can have success=true, unresolved gaps and
ready_for_refactoring=false. Study always returns false readiness for mutation.
Failed required execution or incomplete operation returns false with partial result.
80% is a default broad guideline, not arbitrary readiness gate; an applicable
authoritative threshold and critical preservation checks are binding. Coverage
above threshold never excuses a failed critical path; optional unavailable measurement
does not block unrelated delivery. Stakeholder outcome remains not measured unless
an actual relevant observation exists; fixtures/approval do not establish it.
