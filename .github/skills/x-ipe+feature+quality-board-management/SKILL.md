---
name: x-ipe+feature+quality-board-management
description: Generate and manage project quality evaluation reports from feature perspective. Evaluates requirements, features, test coverage, and code alignment status with gap analysis. Generates consistent markdown reports to x-ipe-docs/quality-evaluation folder. Triggers on requests like "evaluate project quality", "generate quality report", "assess code alignment".
---

# Project Quality Board Management

## Purpose

AI Agents follow this skill to generate and manage project-wide quality evaluation reports:
1. **Generate** quality evaluation reports across all features
2. **Update** existing reports with re-evaluated features
3. **Query** quality status for specific features
4. **Compare** quality between evaluation snapshots

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill. If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point for each skill.

CRITICAL: Learn `x-ipe-task-based-refactoring-analysis` skill to understand `refactoring_suggestion` and `refactoring_principle` data models for integration.

---

## About

This skill evaluates the project from a **feature perspective**, analyzing four primary dimensions plus tracing and security coverage.

**Key Concepts:**

- **Quality Evaluation** -- Scored assessment (1-10) of a feature across six dimensions: requirements, specification, test coverage, code alignment, tracing, security
- **Health Status** -- Overall project health: `healthy` (8-10), `attention_needed` (5-7), `critical` (1-4)
- **Score-to-Status** -- 8-10: aligned, 6-7: needs_attention, 1-5: critical, N/A: planned
- **Report Versioning** -- Up to 5 most recent reports retained (1 current + 4 historical)
- **Output Location** -- `x-ipe-docs/quality-evaluation/project-quality-evaluation.md`
- **Evaluation Principles** -- See [references/evaluation-principles.md](references/evaluation-principles.md)
- **Evaluation Procedures** -- See [references/evaluation-procedures.md](references/evaluation-procedures.md)

---

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

---

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

**Quality Evaluation Data Model:** See [references/quality-evaluation-data-model.yaml](references/quality-evaluation-data-model.yaml) for the complete data model structure.

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Operation identified</name>
    <verification>Caller specifies generate, update, query, or compare</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature discovery path exists</name>
    <verification>x-ipe-docs/requirements/FEATURE-* directories are scannable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Evaluation references available</name>
    <verification>references/evaluation-principles.md and references/evaluation-procedures.md exist</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Generate Quality Report

**When:** Need to evaluate project quality from scratch or on schedule

```xml
<operation name="generate">
  <action>
    1. DETERMINE scope (default: all features; filter by feature_ids or module_paths if provided)
    2. DISCOVER features by scanning x-ipe-docs/requirements/FEATURE-* directories
    3. FOR EACH feature:
       a. EVALUATE requirements alignment (see references/evaluation-procedures.md)
       b. EVALUATE specification alignment
       c. EVALUATE test coverage
       d. EVALUATE code alignment
       e. EVALUATE tracing coverage
       f. EVALUATE security
       g. COLLECT violations per category
       h. CALCULATE feature score using dimension weights (req:0.20, spec:0.20, test:0.20, code:0.20, tracing:0.10, security:0.10)
    4. AGGREGATE results: calculate overall_score (average of non-planned features), determine health_status, collect priority_gaps, generate recommendations
    5. GENERATE report using template at references/quality-report-template.md
    6. SAVE report with versioning (see Versioning Workflow below)
    7. SELF-REVIEW: read report completely, check for missing content, inconsistencies, features mentioned but not evaluated, gaps without severity, recommendations not matching gaps; fix any issues found
  </action>
  <constraints>
    - BLOCKING: Report MUST follow structure rules (see Report Structure Rules below)
    - CRITICAL: Planned features are excluded from score calculation
    - CRITICAL: Report header must include Project Version (from pyproject.toml) and Evaluated Date
  </constraints>
  <output>Evaluation summary with overall_score, health_status, feature_count, gap_counts</output>
</operation>
```

### Operation: Update Existing Report

**When:** Need to re-evaluate specific features without full project scan

```xml
<operation name="update">
  <action>
    1. LOAD latest report from x-ipe-docs/quality-evaluation/project-quality-evaluation.md
    2. FOR EACH feature_id in scope:
       a. RE-EVALUATE all six dimensions
       b. UPDATE feature entry in report
    3. RE-CALCULATE aggregates (overall_score, health_status)
    4. UPDATE priority_gaps and recommendations
    5. SAVE using versioning workflow
  </action>
  <output>Updated evaluation summary with changed features highlighted</output>
</operation>
```

### Operation: Query Quality Status

**When:** Need to check quality for specific features without generating a new report

```xml
<operation name="query">
  <action>
    1. LOAD latest report from x-ipe-docs/quality-evaluation/project-quality-evaluation.md
    2. FILTER features by provided criteria (feature_ids, status, score range)
    3. RETURN filtered evaluation data
  </action>
  <output>Matching feature evaluations or empty list</output>
</operation>
```

### Operation: Compare Evaluations

**When:** Need to track quality changes over time between two report versions

```xml
<operation name="compare">
  <action>
    1. LOAD both evaluation reports (latest vs previous, or v{A} vs v{B})
    2. FOR EACH feature present in both:
       a. COMPARE status changes
       b. CALCULATE score deltas per dimension
       c. IDENTIFY new and resolved gaps
    3. GENERATE comparison summary: improved features, degraded features, new gaps introduced, gaps resolved
  </action>
  <output>Comparison data with score deltas and gap changes per feature</output>
</operation>
```

### Versioning Workflow

Used by generate and update operations when saving reports.

```xml
<operation name="version_report">
  <action>
    1. ENSURE x-ipe-docs/quality-evaluation/ folder exists (create if not)
    2. IF project-quality-evaluation.md exists:
       a. SCAN for existing project-quality-evaluation-v*.md files
       b. FIND max version number N
       c. RENAME current file to project-quality-evaluation-v{N+1}.md
       d. IF more than 4 versioned files: DELETE oldest (lowest version number)
    3. SAVE new report as project-quality-evaluation.md
    4. VERIFY: at most 1 current + 4 historical files
  </action>
  <constraints>
    - BLOCKING: Never exceed 5 total report files
    - CRITICAL: Version number = max(existing versions) + 1
  </constraints>
  <output>Report file path and version number</output>
</operation>
```

### Report Structure Rules

```xml
<constraints name="report_structure_rules">
  <rule id="1">Evaluation Principles section MUST come BEFORE Feature-by-Feature Evaluation; MUST only explain principles and thresholds; MUST NOT contain evaluation results</rule>
  <rule id="2">Violation Details MUST be organized by feature with 6 subsections each: Requirements, Specification, Test Coverage, Code Alignment, Tracing Coverage, Security; ONLY show features with violations; show "No violations" for clean categories</rule>
  <rule id="3">Separation of concerns: Principles = WHAT and HOW (thresholds); Violations = RESULTS per feature</rule>
  <rule id="4">Tracing: threshold >=90% decorator coverage; sensitive params (password, token, secret, key) require redact=[]; levels: API=INFO, Business=INFO, Utilities=DEBUG</rule>
  <rule id="5">Security: input validation on endpoints, no hardcoded secrets, auth on protected routes, injection prevention, secure sensitive data handling</rule>
</constraints>
```

---

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

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>All features in scope evaluated</name>
    <verification>Every feature in scope has scores for all six dimensions</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Gaps identified and prioritized</name>
    <verification>All gaps have severity assigned and are collected in priority_gaps</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Overall score calculated</name>
    <verification>overall_score and health_status are set based on feature scores</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Report saved with versioning</name>
    <verification>Report exists at correct path; historical versions preserved per versioning rules</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Self-review completed</name>
    <verification>Report read completely; no missing content, inconsistencies, or unassigned severities</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `NO_FEATURES_FOUND` | No FEATURE-* directories in requirements | Return empty evaluation; suggest running feature-breakdown first |
| `REPORT_NOT_FOUND` | No existing report for update/query/compare | Run generate operation first |
| `VERSION_CONFLICT` | Version number collision during save | Re-scan for max version and retry |
| `EVALUATION_INCOMPLETE` | A dimension could not be evaluated (missing docs/code) | Mark dimension as planned; exclude from scoring |
| `SCOPE_INVALID` | Provided feature_ids or module_paths not found | Return error with list of valid feature_ids |

---

## Templates

| File | Purpose |
|------|---------|
| `references/quality-report-template.md` | Report template with sections and placeholder fields |
| `references/evaluation-principles.md` | Evaluation principles, thresholds, and score formulas |
| `references/evaluation-procedures.md` | Step-by-step procedures for each evaluation dimension |

---

## Examples

### First-Time Evaluation

```yaml
input:
  operation: "generate"
  scope:
    type: "all"
# Generates baseline report, sets initial metrics, flags features needing attention
```

### Post-Refactoring Evaluation

```yaml
input:
  operation: "generate"
  scope:
    type: "feature_ids"
    filter: ["FEATURE-001", "FEATURE-003"]
# After code-refactoring-stage, re-evaluate affected features and compare with baseline
```

### Integration with Code Refactoring Stage

```
Quality Report (baseline) -> x-ipe-task-based-refactoring-analysis
  -> x-ipe-task-based-improve-code-quality
  -> Quality Report (mid-point)
  -> x-ipe-task-based-code-refactor
  -> Quality Report (final) + Compare
```
