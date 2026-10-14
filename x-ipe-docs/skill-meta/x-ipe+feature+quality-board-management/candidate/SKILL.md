---
name: x-ipe+feature+quality-board-management
description: Generate and manage project quality evaluation reports from feature perspective. Evaluates requirements, features, test coverage, and code alignment status with gap analysis. Generates consistent markdown reports to x-ipe-docs/quality-evaluation folder. Triggers on requests like "evaluate project quality", "generate quality report", "assess code alignment".
---

# Project Quality Board Management

## Purpose

Generate, update, query and compare feature-perspective project quality reports.
Evaluate the six original dimensions against approved intent and revision-bound
evidence; report delivery separately from stakeholder outcomes. Quality reporting
does not authorize fixing code, changing acceptance or shipping a feature.

## Important Notes

BLOCKING: Work under the existing lifecycle owner and authorized scope; do not
create/update tasks, invoke recursive lifecycle, run Git or execute successors.
Load the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
for document-local goal/evidence semantics, not new persistent fields.

CRITICAL: Load the actual current
[refactoring analysis](.github/skills/x-ipe-tool-refactoring-analysis/SKILL.md)
input/output contract before integrating suggestions. Preserve this skill's
original model; unsupported handoffs are compatibility gaps, not silent coercion.

BLOCKING: No synthetic scores, coverage, progress or stakeholder observations.
Unknown is not planned, zero, ten, failed or achieved. Existing schema cannot
represent every evidence state: keep those states in report prose; if numeric
success is unsupported, return failure rather than inventing new result keys/enums.

## About

**Key Concepts:**
- **Quality Evaluation:** actual rubric-based 1-10 assessment of requirements,
  specification, test coverage, code alignment, tracing and security.
- **Health Status:** healthy (at least 8), attention_needed (at least 5, below 8),
  critical (below 5); never evidence that stakeholders achieved their outcomes.
- **Score-to-Status:** 8-10 aligned, 6-7 needs_attention, 1-5 critical; retain
  original declarations and disclose fractional-score ambiguity rather than round
  silently. Planned applies to verified future work, not missing evidence.
- **Report Versioning:** one current plus four historical reports at most.
- **Output Location:** x-ipe-docs/quality-evaluation/project-quality-evaluation.md.
- **Goal Reporting:** source/parent/stakeholder/outcome/contribution/AC links in
  existing report text, not a new API or data-model schema.

## When to Use

```yaml
triggers:
  - "evaluate project quality"
  - "generate quality report"
  - "assess code alignment"
  - "quality evaluation"
  - "compare quality snapshots"
  - "check feature quality"
not_for:
  - "Code refactoring (use x-ipe-task-based-code-refactor)"
  - "Bug fixing (use x-ipe-task-based-bug-fix)"
```

## Input Parameters

```yaml
input:
  operation: "generate | update | query | compare"
  scope:
    type: "all | feature_ids | module_paths"
    filter: "[FEATURE-XXX, ...] | [src/module/*, ...]"
  compare:
    version_a: "latest | v{N}"
    version_b: "previous | v{N}"
```

The [original data model](.github/skills/x-ipe+feature+quality-board-management/references/quality-evaluation-data-model.yaml)
is unchanged, including every suggestion/principle/constraint field.

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller selects generate, update, query or compare; version_report is an internal save helper" />
  <field name="scope">
    <steps>Default to all features. Resolve exact existing feature IDs, including EPIC folders and legacy flat folders, or inspected module paths. Reject broken explicit IDs, symlinks, path escape and unsupported filters; do not guess code ownership from a name alone.</steps>
  </field>
  <field name="compare">
    <steps>Resolve latest/previous or exact vN from actual report files. Require both snapshots for compare; retain each snapshot's scope, date and source revision rather than interpreting an old pass as current evidence.</steps>
  </field>
  <field name="evaluation_context">
    <steps>Read the caller's existing authorized paths/exclusions and source requirements, stories, stable GWT ACs and test types. Resolve project version, actual commands/results/dates/source-test-doc-config hashes, applicable rubric/thresholds and observation sources. This is working context from inspected artifacts, not a new input/output key. Missing consequential intent blocks only the pertinent claim; clear inputs require no additional human ritual.</steps>
  </field>
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Operation and authority identified</name><verification>Existing caller selects operation/scope; writes are limited to authorized reports and retention paths.</verification></checkpoint>
  <checkpoint required="true"><name>Feature discovery available</name><verification>Actual requirements feature folders, including EPIC children, and scoped code/test ownership are inspectable.</verification></checkpoint>
  <checkpoint required="true"><name>References and evidence available</name><verification>Original principles/procedures/model/template and approved source goal/AC links are resolved; absent evidence is explicit.</verification></checkpoint>
</definition_of_ready>
```

## Operations

### Operation: Generate Quality Report

```xml
<operation name="generate">
  <action>
    1. DISCOVER every feature in the initialized scope; record actual ownership and exclusions.
    2. FOR EACH feature evaluate requirements, specification, test coverage, code alignment, tracing and security using references/evaluation-procedures.md and applicable principles.
    3. MAP approved goal/subgoal, parent/source, stakeholder, observable outcome, contribution/selection, constraints and story/leaf AC/test-type to current evidence using references/goal-reporting.md. Reuse IDs; never invent intent from implementation.
    4. COLLECT actual violations, severity and rubric rationale per original category. Calculate dimension and feature scores only from sufficient scoped evidence under the original six weights (0.20/0.20/0.20/0.20/0.10/0.10).
    5. AGGREGATE non-planned features only when eligible features/dimensions are evaluable; identify numeric denominator, excluded planned work and pertinent evidence gaps. Missing evidence cannot inflate an aggregate by exclusion.
    6. GENERATE the complete original report structure, adding goal/delivery/outcome evidence in existing Key Findings, Details, Recommendations and Appendix sections; principles contain thresholds only.
    7. SELF-REVIEW the complete report for source/AC coverage, consistency, severities, recommendation authority, numeric provenance and false outcome claims. SAVE via version_report only with authorized paths and honest evidence; return EVALUATION_INCOMPLETE on unsupported numeric success.
  </action>
  <constraints>
    - BLOCKING: Approved source intent outranks doc/code agreement. Bugs, unimplemented intent, doc drift and changed scope are distinct; recommendations do not authorize repairs.
    - CRITICAL: Header includes actual project version and evaluated date. Planned features are excluded only when inspected future-work evidence supports that status.
    - BLOCKING: No observed stakeholder outcome without actual contextual observation; tests/fixtures/document checks support engineering delivery only.
  </constraints>
  <output>Evaluation summary with overall_score, health_status, feature_count, gap_counts; original operation_output envelope.</output>
</operation>
```

### Operation: Update Existing Report

```xml
<operation name="update">
  <action>
    1. LOAD the latest report; preserve unchanged feature entries and their original evidence dates/revisions, never relabel old evidence as fresh.
    2. RE-EVALUATE all six dimensions and goal/AC links for each scoped feature. Changes invalidate affected delivery/outcome evidence, not every unrelated feature.
    3. RE-CALCULATE original aggregates, priority_gaps and recommendations only with valid inputs; disclose mixed revisions and comparability limits.
    4. SELF-REVIEW and SAVE through version_report; unsupported aggregate or stale pertinent evidence returns EVALUATION_INCOMPLETE, not a fabricated green report.
  </action>
  <output>Updated evaluation summary with changed features highlighted; original operation_output envelope.</output>
</operation>
```

### Operation: Query Quality Status

```xml
<operation name="query">
  <action>
    1. LOAD the latest report without writing or evaluating new source.
    2. FILTER by supplied feature criteria and any established caller-supported status/score criteria; retain evidence dates, scope and delivery/outcome limits.
    3. RETURN matching feature evaluations or empty list. Report an unsupported structured projection as a compatibility gap, never introduce new persistent schema fields.
  </action>
  <output>Matching feature evaluations or empty list; preserve original operation result contract and report reference.</output>
</operation>
```

### Operation: Compare Evaluations

```xml
<operation name="compare">
  <action>
    1. LOAD both initialized reports without mutation.
    2. COMPARE shared features' statuses, actual per-dimension score deltas and new/resolved gaps; disclose changed rubric, scope, denominator or revision that prevents a valid numeric comparison.
    3. COMPARE goal/AC delivery evidence and stakeholder observations separately. A higher score, new report or passing test is not an observed stakeholder gain.
    4. RETURN improved/degraded features and gap changes with source references and limits; do not invent numbers for incomparable/unmeasured cases.
  </action>
  <output>Comparison data with score deltas and gap changes per feature; original operation result contract.</output>
</operation>
```

### Versioning Workflow

```xml
<operation name="version_report">
  <action>
    1. ENSURE the authorized x-ipe-docs/quality-evaluation/ folder exists; reject escaping/symlinked paths and unexpected concurrent changes.
    2. IF current report exists, SCAN existing exact project-quality-evaluation-vN.md files, find max N (zero if none), RENAME current to vN+1 only when nonconflicting, and remove oldest historical reports if needed to retain four.
    3. SAVE the new current project-quality-evaluation.md; retain one current plus at most four historical files. Do not delete unrelated files or modify source evidence.
    4. VERIFY content/readback, actual version number and bounded retention. A failure is not success; no atomic save or recovery guarantee is implied.
  </action>
  <constraints><rule>Never exceed five report files; re-scan collisions before retry. Missing retention/write authority blocks save, not inspection.</rule></constraints>
  <output>Report file path and version number.</output>
</operation>
```

### Report Structure Rules

```xml
<constraints name="report_structure_rules">
  <rule id="1">Evaluation Principles MUST precede Feature-by-Feature Evaluation and contain only principles and thresholds, never results.</rule>
  <rule id="2">Violation Details are grouped by feature with six original subsections: Requirements, Specification, Test Coverage, Code Alignment, Tracing Coverage, Security. Show only features with violations; say No violations only for actually checked clean categories.</rule>
  <rule id="3">Goal linkage/evidence states belong in existing results/details/appendix sections; no schema extension or synthetic scoring dimension.</rule>
  <rule id="4">Tracing retains the applicable 90% threshold, explicit sensitive-parameter redaction, API/Business INFO and Utilities DEBUG checks. Absence of relevant functions is not 100% coverage.</rule>
  <rule id="5">Security checks validation, secrets, protected-route auth, injection and sensitive-data handling; redact evidence values and report actual risk.</rule>
</constraints>
```

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "generate | update | query | compare"
  result:
    report_path: "x-ipe-docs/quality-evaluation/project-quality-evaluation.md"
    version: "v{N}"
    overall_score: "<1-10>"
    health_status: "healthy | attention_needed | critical"
    features_evaluated: "<count>"
    gaps:
      high: "<count>"
      medium: "<count>"
      low: "<count>"
  errors: []
```

Preserve all original keys/types/enums and the complete data model. Query/compare
retain their original operation-specific result meanings; no invented stricter
schema is imposed on historical callers. A failed evaluation may return the
original envelope with success=false, result={} and explanatory errors; do not
serialize unknown numeric evidence as zero/null or add goal/outcome result keys.
Narrative N/A/unavailable does not mean schema status planned. See
[goal reporting](.github/skills/x-ipe+feature+quality-board-management/references/goal-reporting.md).

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Scope evaluated honestly</name><verification>Every scoped feature/dimension evaluated or explicit EVALUATION_INCOMPLETE; unknown is not planned or a synthetic score.</verification></checkpoint>
  <checkpoint required="true"><name>Goal and evidence linkage</name><verification>Source/parent/contribution/constraints and AC/test-type links support each pertinent delivery claim; outcome measured separately.</verification></checkpoint>
  <checkpoint required="true"><name>Gaps prioritized</name><verification>Actual gaps have severity and source; recommendations preserve approval boundaries and original suggestion structure.</verification></checkpoint>
  <checkpoint required="true"><name>Scores justified</name><verification>Original rubric, weights, statuses and denominator are retained; success only when numeric aggregates are supported.</verification></checkpoint>
  <checkpoint required="true"><name>Operation and persistence verified</name><verification>Generate/update readback/versioning succeeds within authority; query/compare read-only. Original output contract retained.</verification></checkpoint>
  <checkpoint required="true"><name>Self-review complete</name><verification>Entire report checked for completeness, false freshness/outcomes, unassigned severity and principles/results separation.</verification></checkpoint>
</definition_of_done>
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `NO_FEATURES_FOUND` | No actual scoped feature folders | Return empty evaluation without invented score; suggest feature-breakdown, do not execute it |
| `REPORT_NOT_FOUND` | Missing report for update/query/compare | Report failure; suggest authorized generate |
| `VERSION_CONFLICT` | Save collision | Re-scan and protect concurrent files before bounded retry |
| `EVALUATION_INCOMPLETE` | Missing docs/code, relevant goal authority, current evidence or applicable rubric | Explain pertinent unavailable/failed evidence in narrative; planned only for verified future work, never unknown |
| `SCOPE_INVALID` | Explicit feature/module filter invalid | Return valid discovered IDs; do not broaden scope silently |

## Templates

| File | Purpose |
|------|---------|
| references/quality-report-template.md | All original report sections/fields with principles before results |
| references/evaluation-principles.md | Original six-dimensional thresholds and scoring formulas |
| references/evaluation-procedures.md | All original evaluation and suggestion procedures with goal/freshness boundaries |
| references/quality-evaluation-data-model.yaml | Exact original full data model; no schema changes |
| references/goal-reporting.md | Document-local goal/AC/delivery/outcome and evidence limits |

## Examples

See [examples](.github/skills/x-ipe+feature+quality-board-management/references/examples.md)
for first evaluation, post-refactoring compare and incomplete/legacy cases.
The original baseline → analysis → quality-sync → midpoint → code-refactor →
final+compare integration remains a caller-owned recommendation, not automatic
successor execution or release permission.
