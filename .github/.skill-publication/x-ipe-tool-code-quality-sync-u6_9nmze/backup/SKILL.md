---
name: x-ipe-tool-code-quality-sync
description: Align affected documentation and preservation tests to authoritative user goals and approved behavior before refactoring, with study/local/broad scope and honest revision-bound evidence. Triggers on "sync docs with code", "improve quality before refactoring", "update specs for refactoring", "align documentation".
---

# Code Quality Sync Tool

## Purpose

Prepare a trustworthy refactoring baseline: reconcile requirements, feature specs
and technical design against source-authoritative user goals and approved behavior;
characterize critical affected paths; return honest evidence and remaining gaps.
Current implementation is evidence of what happens, not authority for what ought
to happen. Sync is an enabling means for the caller's named quality goal, not proof
of stakeholder gain or an opportunity to rewrite acceptance to bless faulty code.

## Important Notes

BLOCKING: Tool operation only. No task registration, board, Git, app writes,
lifecycle duplication, successor execution or approval choreography. Called by
x-ipe-task-based-code-refactor Step 2; return operation_output once to its owner.
Requires actual analysis scope/quality/suggestions/principles, not invented success.

BLOCKING: Preserve approved goals, source/parent links, story/GWT AC IDs and test
types, behavior, constraints and non-goals. Do not weaken assertions, delete or
automatically skip failing tests. Bugs return as findings for bug-fix; changed
scope/acceptance/behavior needs actual human CR authority, not DAO or code inference.
Never perform implementation repair as documentation/test sync.

CRITICAL: Inspection scope is not write authority. Study-only is read-only except
the authorized report; local affects approved docs/tests; broad includes relevant
integration/full-suite checks within authorized scope, not unrelated global repair.
No forced new infrastructure for skills/documents, compile gates or tracing setup.
Load the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
for document-local goal/evidence semantics, not a second lifecycle.

## About

**Key Concepts:**
- **Authoritative intent** — Actual user/source goal and approved requirement/AC;
  implementation observations and historical analysis remain evidence, not approval.
- **Doc drift** — Stale descriptive docs inconsistent with approved, verified behavior.
- **Preservation baseline** — Unchanged approved public contract assertions exercised
  at base and target revisions, including implicated callers and failure paths.
- **Evidence state** — aligned, divergent or unavailable; absence, non-applicability,
  not measured and executed failure are distinct dispositions, never assumed green.

## When to Use

```yaml
triggers:
  - "sync docs with code"
  - "improve quality before refactoring"
  - "update specs for refactoring"
  - "align documentation"
not_for:
  - "analyze for refactoring: x-ipe-tool-refactoring-analysis"
  - "execute refactoring: x-ipe-task-based-code-refactor"
  - "fix a deviation: x-ipe-task-based-bug-fix"
  - "change approved intent: x-ipe-task-based-change-request"
```

## Input Parameters

```yaml
input:
  operation: full_sync
  refactoring_scope:
    scope_level: "feature | custom"
    feature_id: "{FEATURE-XXX or null}"
    refactoring_purpose: "<caller quality goal and source/parent contribution>"
    files: []
    modules: []
  code_quality_evaluated:
    requirements_alignment: {status: "<analysis status>", gaps: [], related_docs: []}
    specification_alignment: {status: "<analysis status>", gaps: [], spec_docs: []}
    technical_spec_alignment: {status: "<analysis status>", gaps: [], spec_docs: []}
    test_coverage: {status: "<analysis status>", line_coverage: null, critical_gaps: []}
    code_alignment: {status: "<analysis status>"}
    overall_quality_score: null
  refactoring_suggestion: "{analysis pass-through, including goals/target_structure}"
  refactoring_principle: "{analysis pass-through, including constraints}"
  refactoring_mode: "study-only | local | broad"
  program_type: "<actual domain, including skills/documents>"
  sync_context:
    authorized_paths: []
    exclusions: []
    source_links: []
    base_revision: "<actual fingerprint or unavailable>"
    target_revision: "<actual fingerprint or unavailable>"
    report_path: "<authorized report path>"
    required_checks: []
    coverage_policy: "<applicable authoritative policy or broad guideline>"
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies; full_sync only, including read-only study disposition" />
  <field name="refactoring_scope"><steps>Require actual analysis scope; preserve purpose/files/modules/feature identity/dependencies/goals/extensions exactly. Expanded inspection does not authorize edits. Missing material input returns MISSING_ANALYSIS.</steps></field>
  <field name="code_quality_evaluated"><steps>Require actual analysis quality object; retain original fields and domain extensions. Recheck dates/hashes/applicability, never import historical alignment as fresh. Preserve separate requirements/specification/feature/technical/tracing records and alias provenance; absent technical record is unavailable, not aligned.</steps></field>
  <field name="refactoring_suggestion" source="Required analysis pass-through including summary/goals/target_structure; no substituted goals" />
  <field name="refactoring_principle" source="Required analysis pass-through including primary/secondary principles and constraints" />
  <field name="refactoring_mode"><steps>Use exact caller study-only/local/broad; reject unknown. Legacy omitted mode defaults broad full_sync guideline within existing authorized scope; it grants no edits or scope expansion. Never upgrade explicit local/study.</steps></field>
  <field name="program_type"><steps>Caller or inspected actual domain and affected layers; not file extension alone. Skills/documents use existing applicable validators/scenarios, no forced runtime instrumentation.</steps></field>
  <field name="sync_context"><steps>Resolve caller-approved doc/test/report paths, exclusions, base/target revision evidence, required checks and coverage policy. Explicit selected sources first, declared links then unique EPIC/FEATURE or legacy identity; validate anchors/kind/content/containment/symlink escape. Broken/ambiguous explicit source fails, never silent fallback. Missing authority permits inspection/report only, not mutation. Missing pertinent intent or check is a disclosed gap.</steps></field>
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Analysis contract</name><verification>Actual full_sync inputs, original scope/purpose/quality/suggestions/principles and extensions retained.</verification></checkpoint>
  <checkpoint required="true"><name>Authority and sources</name><verification>Mode, approved paths/exclusions/report, readable authoritative intent and preservation boundaries resolved or pertinent gaps recorded.</verification></checkpoint>
  <checkpoint required="true"><name>Evidence plan</name><verification>Domain/risk base-to-target checks, required versus optional evidence and baseline failures known; no all-green prerequisite for study.</verification></checkpoint>
</definition_of_ready>
```

## Operations

### Operation: Full Sync

**When:** After analysis; assess in study-only or reconcile authorized docs/tests
in local/broad mode. Full means all relevant domain perspectives are considered,
not that every project file is rewritten or every perspective becomes aligned.

```xml
<operation name="full_sync">
  <action>
    1. Inspect source-authoritative user goals/subgoals, source/parent contribution, baseline/target and preservation/story/GWT AC/type. Use the existing validation report to map all-required checks and selected alternatives, constraints/non-goals, named success comparison and trade-off. Explicit legacy so-that intent may be inferred with source anchor; missing intent blocks pertinent claims, not unrelated evidence. Delivery and stakeholder outcome remain separate; fixture checks are not stakeholder observations.
    2. Compare each requirements gap (undocumented/unimplemented/deviated) to approved intent and actual evidence. Update only authorized descriptive drift when verified behavior is already approved. Undocumented observations belong in a labeled current-state note, not automatic requirements or acceptance. Keep unimplemented/deviated intent intact, record bug/CR/ambiguity for caller. Missing docs are not_found; propose an observational draft only when authorized, never manufacture approval or goal IDs.
    3. Reconcile affected feature/specification gaps (missing/extra/deviated) independently. Retain stories, GWT AC IDs/types, parent constraints and unaffected evidence. Correct stale links/descriptions against approved behavior; do not add/remove ACs from code or mark tests passing by changing expected results. Conflict between approval sources returns to caller; do not choose code as authority. Preserve supplied feature_alignment separately from specification summary.
    4. Reconcile technical design gaps (structure/interface/data_model/pattern) to inspected approved implementation, callers and interfaces. Correct affected descriptive architecture/API/schema/pattern references with actual date/source hashes and Design Change Log. Observed deviations remain labeled findings, not a replacement intended design. Missing design may be an authorized observed baseline draft with intent/evidence gaps; it is not verified alignment. Preserve existing tracing/redaction/config; disabled/absent instrumentation needs no new infrastructure.
    5. Characterize critical changed paths and affected callers/dependencies, not just lines: public results/imports/errors/data/side effects plus implicated security/concurrency/external boundaries. Identify base-to-target paths from actual fingerprints/diff evidence without Git mutation; check approved assertions at base and target with unchanged expected behavior. Cover happy path, error handling and edge cases. Study assesses/plans only; local adds targeted authorized preservation tests and applicable checks; broad runs planned relevant integration/full suite and coverage. A broad line coverage target of 80% is a default guideline, not an arbitrary blocking threshold or proof of goal coverage. Only an applicable authoritative requirement makes a numeric threshold mandatory. Unrelated failures/coverage do not force code changes or block independent study/local delivery.
    6. Record actual commands/exits/results/dates and source/test/doc/config fingerprints, denominator/method/scope for measured coverage. New regressions and unresolved required critical preservation failures block readiness; retain relevant base failures and unavailable checks without skipping or relabeling them. Return bugs to owner; no repair or adding bugs to authorized refactor scope. Capture insufficient evidence and safely approved dispositions with exact authority/risk, never blanket waiver. Characterize existing domain contracts for skills/docs with installed validators and real fixtures where pertinent, not forced new infrastructure.
    7. Re-evaluate each affected alignment only from current evidence. Keep aligned/divergent/unavailable separate from legacy statuses and precise absent/unmeasured/not_applicable/failed reasons; never clear unresolved gaps after editing. Keep code_alignment unchanged from input and record newly found deviations in report. Preserve measured historical values/provenance separately; unknown coverage or numeric quality score is actual null, not zero or a string sentinel. Numeric scores require an actual comparable authoritative rubric, not synthetic weights or automatic improvement.
    8. Compile original operation_output fields, actual doc/test counts, pass-through scope/goals/targets/suggestions/principles/extensions, evidence mapping and report path. success means the authorized sync/assessment deliverable is complete, not ready_for_refactoring, aligned code or achieved outcome. Required operation inputs/report/write/check failures return false with partial evidence/errors. Required preservation gaps may allow a completed assessment with ready_for_refactoring=false. Study never asserts mutation readiness. Self-check freshness, links, authority and counts; return once to caller.
  </action>
  <constraints>
    - BLOCKING: No requirements/AC rewriting to bless faulty implementation, source repair or unauthorized writes
    - BLOCKING: No new regressions hidden by weakened assertions, automatic skips or invented evidence
    - CRITICAL: All original operation result fields and supplied domain extensions retained
    - MANDATORY: All markdown links use project-root-relative paths
  </constraints>
  <output>Updated evidence-backed quality records, unchanged code_alignment, actual summary/report/errors and exact analysis pass-through fields.</output>
</operation>
```

## Output Result

Original fields and nesting remain; statuses now explicitly allow honest evidence
states, line_coverage is percentage string | null and overall_quality_score is
number | null. This is a schema delta, not proven strict-consumer compatibility.
See [complete schema](.github/skills/x-ipe-tool-code-quality-sync/references/output-schema.md).

```yaml
operation_output:
  success: true | false
  result:
    code_quality_evaluated:
      requirements_alignment:
        status: "<evidence status>"
        gaps: []
        updates_made: []
      specification_alignment:
        status: "<evidence status>"
        gaps: []
        updates_made: []
      test_coverage:
        status: "<evidence status>"
        line_coverage: "<percentage string | null>"
        tests_added: "<count>"
        tests_updated: "<count>"
      code_alignment:
        status: "{from input — not modified in this phase}"
      overall_quality_score: "<number 1-10 | null>"
      validation_summary:
        docs_created: "<count>"
        docs_updated: "<count>"
        tests_added: "<count>"
        ready_for_refactoring: true | false
    refactoring_scope: "{pass-through from input}"
    refactoring_suggestion: "{pass-through from input}"
    refactoring_principle: "{pass-through from input}"
    report_path: "x-ipe-docs/refactoring/validation-{context}.md"
  errors: []
```

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Goal authority preserved</name><verification>Source/parent/goals/ACs/types/constraints mapped; drift distinguished from bugs/CRs; no changed acceptance or invented stakeholder outcome.</verification></checkpoint>
  <checkpoint required="true"><name>All relevant docs considered</name><verification>Requirements, features/specification and technical design each have current evidence, authorized actual updates or honest gaps; no forced aligned state for missing docs.</verification></checkpoint>
  <checkpoint required="true"><name>Mode-aware tests</name><verification>Critical changed paths and implicated callers characterized base-to-target as required; study plans/local targeted/broad relevant integration/full suite and justified coverage; required gaps block readiness, unrelated checks do not.</verification></checkpoint>
  <checkpoint required="true"><name>Fresh evidence</name><verification>Dates/commands/exits/fingerprints and comparable measurement methods retained; failed distinct from unavailable; coverage/score nullable when unmeasured.</verification></checkpoint>
  <checkpoint required="true"><name>Original handoff</name><verification>Actual report/counts, original result fields and supplied extensions/pass-throughs retained; success distinct from readiness; one operation no task/lifecycle/Git duplication.</verification></checkpoint>
</definition_of_done>
```

## Error Handling

| Error | Cause | Resolution |
| --- | --- | --- |
| MISSING_ANALYSIS | Missing required scope/quality/suggestions/principles | Return partial result; caller supplies actual analysis |
| SOURCE_INVALID | Broken, ambiguous or escaping explicit source | Fail pertinent operation; no fallback or repair |
| AUTHORITY_GAP | Intent/write permission or approval conflict | Assess only permitted scope; return exact gap to caller |
| BUG_FOUND | Observed behavior violates approved intent | Preserve failing test/requirement; owner considers bug-fix, no automatic skip |
| CR_REQUIRED | Desired behavior/acceptance/scope differs from approval | Caller obtains actual human CR authority before changes |
| EVIDENCE_UNAVAILABLE | Required critical check cannot execute or revision missing | Disclose unavailable, no fabricated pass; readiness false |
| CHECK_FAILED | Applicable executed check fails | Record base/target failure and impact; block relevant readiness, no unrelated repair |
| COVERAGE_UNREACHABLE | Applicable mandatory threshold not evidenced | Return measured value/null and scoped gap; guideline shortfall alone is not failure |
| WRITE_DENIED | Authorized doc/test/report cannot be written | Return false with retained partial evidence and exact path |
| CONSUMER_INCOMPATIBLE | Downstream rejects nullable/status contract | Block that handoff; do not coerce metrics or claim integration |

## Templates

- [Validation report](.github/skills/x-ipe-tool-code-quality-sync/templates/validation-report.md): existing artifact for goal-to-doc-to-test evidence and gaps.

## Examples

- [Examples](.github/skills/x-ipe-tool-code-quality-sync/references/examples.md): API doc drift, bug boundary, absent docs and skill study.
- [Detailed procedures](.github/skills/x-ipe-tool-code-quality-sync/references/detailed-procedures.md): authority, domain alignment, mode/risk checks and freshness.
- [Output schema](.github/skills/x-ipe-tool-code-quality-sync/references/output-schema.md): preserved fields, nullable metrics and readiness semantics.

