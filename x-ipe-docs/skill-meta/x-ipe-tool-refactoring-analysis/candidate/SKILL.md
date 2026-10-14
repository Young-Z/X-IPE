---
name: x-ipe-tool-refactoring-analysis
description: Analyze bounded refactoring scope and verified dependencies against the actual quality goal, assess five perspectives with honest evidence states, and recommend behavior-preserving improvements. Triggers on "analyze for refactoring", "evaluate refactoring scope", "assess code quality".
---

# Refactoring Analysis Tool

## Purpose

Produce analysis-only recommendations serving the caller's actual refactoring_purpose,
with source/parent contribution, inspected baseline, preservation boundaries,
measured or qualitative success comparison and trade-off. Refactoring is a means,
not stakeholder gain. Evaluate Requirements, Features, Tech Spec, Test Coverage and
Tracing with evidence and applicability, not arbitrary numerical quality gates.

## Important Notes

BLOCKING: Tool operation only: no task lifecycle, registration, closure, successors,
approval choreography or execution of refactors. No source/test/config, board, Git
or app mutation. Write only the caller-authorized analysis report; discovery is
inspection, not write authority. Return operation_output, not task output.
CRITICAL: Called by x-ipe-task-based-code-refactor Step 1. A study can finish with
missing evidence explicitly recorded; required preservation verification gaps
block later mutation claims, not unrelated read-only analysis.
No blanket compile or all-green/global coverage gate for skills/documents/analysis.
No arbitrary weighted score; numeric only from measured inputs with comparable
rubric, method, same scope and denominator. Otherwise actual null, report not measured.

## About

Refactoring analysis distinguishes authorized target from inspected dependency
closure. Goal-relevant evidence bounds discovery; it does not promise all hidden
dependencies found. Preserve baseline facts and unknowns instead of repairing them.

**Key Concepts:**
- **Scope Expansion** — Iteratively discover related files via imports, shared interfaces, and coupling
- **Quality Perspectives** — 5 dimensions: requirements, features, tech spec, test coverage, tracing
- **Gap Analysis** — Categorized gaps (undocumented, unimplemented, deviated, missing, etc.)

## When to Use

```yaml
triggers:
  - "analyze for refactoring"
  - "evaluate refactoring scope"
  - "assess code quality"
  - "code quality analysis"

not_for:
  - "execute refactoring" → use x-ipe-task-based-code-refactor
  - "sync docs with code" → use x-ipe-tool-code-quality-sync
```

## Input Parameters

```yaml
input:
  operation: "full_analysis"
  scope:
    scope_level: "feature | custom"
    feature_id: "{FEATURE-XXX}"       # required when scope_level=feature
    refactoring_purpose: "<named quality goal, parent contribution and comparison>"
    files: []                          # optional when scope_level=feature (auto-resolved)
    modules: []                        # optional when scope_level=feature (auto-resolved)
    description: "<user's refactoring intent>"
  quality_baseline_path: "x-ipe-docs/planning/project-quality-evaluation.md"
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies — currently only full_analysis" />

  <field name="scope.scope_level">
    <steps>
      1. IF caller provides scope_level → use provided value
      2. IF feature_id is provided but scope_level is not → default to "feature"
      3. IF files[] is provided but feature_id is not → default to "custom"
      4. ELSE → default to "custom"
    </steps>
  </field>

  <field name="scope.feature_id">
    <steps>
      1. IF caller provides feature_id → use provided value
      2. IF scope_level == "feature" AND feature_id is null → return FEATURE_NOT_FOUND to caller
      3. IF scope_level == "custom" → set to null
    </steps>
  </field>

  <field name="scope.files">
    <steps>
      1. Retain explicit caller files; feature links may supplement inspection, not override them.
      2. Resolve explicit selected links first, declared artifact links, unique EPIC/FEATURE then legacy feature folder. Check identity, anchors, kind/content, containment and symlink escape; explicit broken/ambiguous link blocks, not fallback.
      3. Extract referenced component/test paths from specification/design. Custom scope needs readable files or identifiable modules; unresolved material scope returns error to caller, no tool-level human workflow.
    </steps>
  </field>
  <field name="scope.modules" source="Caller modules or verified ownership from manifests/design; never siblings by proximity" />
  <field name="scope.refactoring_purpose"><steps>Retain actual goal/source/parent, stakeholder contribution, constraints and preservation. A missing pertinent comparison is a gap; do not invent metrics or substitute file size for intent.</steps></field>
  <field name="scope.description" source="Caller boundaries/exclusions and study intent; no scope expansion authority" />
  <field name="quality_baseline_path"><steps>Use exact caller path or declared default; missing default is exists=false, not failure. Validate selected path/readability/identity. Historical report is not fresh evidence without comparable method/scope/revisions.</steps></field>
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Scope provided</name>
    <verification>full_analysis and feature/custom identity, readable target roots/files/modules, actual purpose and report authorization resolved; missing material input returns error to caller</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Target code accessible</name>
    <verification>All listed files/modules can be read from filesystem</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Evidence applicability resolved</name>
    <verification>Domain/risk checks available, unavailable or not applicable; baseline failures recorded, not repaired or a prerequisite to read-only study</verification>
  </checkpoint>
</definition_of_ready>
```

## Operations

### Operation: Full Analysis

**When:** Starting a refactoring initiative — analyze scope and evaluate quality.

```xml
<operation name="full_analysis">
  <action>
    1. Inspect caller goal/subgoal/source/parent, constraints/non-goals and preservation/story/AC/type. Record all-required checks versus selected alternatives. Missing intent blocks pertinent outcome claims, not unrelated analysis. Recommendations are not achieved improvements or stakeholder observation.
    2. Read scoped quality baseline; retain date, original facts/gaps/violations and provenance. Recheck changed evidence, do not treat absent report as zero score or reuse stale results as fresh.
    3. Expand inspection using bounded frontier/visited algorithm in detailed procedures: actual imports/inverse callers/shared types/state/config/tests/docs, justified goal-risk edges, containment and unresolved external/dynamic dependencies. At most 10 passes; distinguish stable closure from capped/incomplete. Preserve actual known dependencies with their correct project paths. No write scope expansion.
    4. Evaluate all five perspectives, including absent/not applicable states. Requirements: undocumented/unimplemented/deviated; Features: missing/extra/deviated; Tech Spec: structure/interface/data_model/pattern; Test Coverage: business_logic/error_handling/edge_case; Tracing: untraced/unredacted/wrong_level. Distinguish not_found, not_measured, not_applicable and failed from verified aligned/needs_attention/critical findings. Observe tracing_enabled/infrastructure and existing redaction, no forced setup. Run only applicable scoped checks with commands/exits/hashes; no fake coverage or repair.
    5. Consult configuration-filtered semantically matched practice excerpts sequentially, metadata first; no full loading of all enabled tools. Use existing analysis configuration, not execution permission. Reference practices as guidance, not automatically enforced results.
    6. Each suggestion traces an inspected gap/source/revision to caller goal/parent, baseline, selected means, success evidence, preservation and trade-off. Prioritize by actual risk and contribution, not smell totals. SOLID/DRY/KISS/YAGNI/SoC are candidate means; size alone is not a defect or useful success criterion. Behavior deviations are findings for owner, not authorization to rewrite specs or repair source.
    7. Fill original operation_output with actual scope/purpose/baseline/findings/goals/principles/report/errors and domain fields. Numeric only from measured inputs and comparable justified rubric; otherwise null with not measured reason. No synthetic weighted aggregate or scores derived from missing docs. Generate only authorized analysis report, self-check links/scope/trace/evidence freshness and exact schema; return once to caller.
  </action>
  <constraints>
    - BLOCKING: Scope expansion must terminate stable or at 10 with incomplete frontier disclosed, never false closure
    - BLOCKING: Every suggestion must trace to a documented gap
    - CRITICAL: Constraints must include backward compatibility and API stability
    - MANDATORY: All markdown links use project-root-relative paths
  </constraints>
  <output>
    operation_output with quality_baseline, refactoring_scope, code_quality_evaluated, refactoring_suggestion, refactoring_principle, report_path and errors
  </output>
</operation>
```

## Output Result

Preserve original operation_output keys and caller-supplied domain extensions.
Scores are number | null, never string sentinels; percent measurements retain
legacy percentage strings or actual null. Explicit nullable/evidence-status delta
is documented in the complete schema; consumers rejecting it are a disclosed
compatibility gap, not coerced success. success means the authorized analysis
deliverable was produced, not all perspectives aligned or refactor approved.
Missing required analysis inputs/output fails with errors and actual partial result.

```yaml
operation_output:
  success: true | false
  result:
    quality_baseline:
      exists: true | false
      overall_score: "<number 1-10 | null>"
    refactoring_scope:
      scope_level: "feature | custom"
      feature_id: "{FEATURE-XXX or null}"
      refactoring_purpose: "<purpose>"
      files: [<expanded file list>]
      modules: [<expanded module list>]
      dependencies: [<identified dependencies>]
      scope_expansion_log: [<log entries>]
    code_quality_evaluated:
      requirements_alignment: { score: "<number 1-10 | null>", status: "<evidence status>", gaps: [] }
      specification_alignment: { score: "<number 1-10 | null>", status: "<evidence status>", gaps: [] }
      test_coverage: { score: "<number 1-10 | null>", line_coverage: "<percentage string | null>", critical_gaps: [] }
      code_alignment: { score: "<number 1-10 | null>", file_size_violations: [], solid_assessment: {}, kiss_assessment: {} }
      overall_quality_score: "<number 1-10 | null>"
    refactoring_suggestion:
      summary: "<high-level description>"
      goals: [{ goal: "<specific goal>", priority: "<high|medium|low>", rationale: "<why>" }]
      target_structure: "<desired end state>"
    refactoring_principle:
      primary_principles: [{ principle: "<name>", rationale: "<why>", applications: [] }]
      secondary_principles: [{ principle: "<name>", rationale: "<why>" }]
      constraints: [{ constraint: "<what>", reason: "<why>" }]
    report_path: "x-ipe-docs/refactoring/analysis-{context}.md"
  errors: []
```

Read complete schema for five perspective records and preserved domain fields.
Legacy quality-board thresholds (coverage 80%, files 800, functions 50) are context
only when an applicable authoritative rubric adopts them; not universal gates,
proof of defects, permission to split, or the separate skill body's 1,000-line cap.

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Scope expansion completed</name>
    <verification>Verified edges and authorized versus inspected paths; stable or capped/incomplete frontier disclosed without claiming all hidden dependencies found</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All 5 quality perspectives evaluated</name>
    <verification>Requirements, features, tech spec, test coverage, tracing each have applicability/status/gaps/evidence and unavailable versus failed disposition; numeric claims justified or null</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Suggestions generated with principles</name>
    <verification>Each useful suggestion has source/gap/goal/baseline/success/preservation/trade-off; no forced suggestion if no justified gap; retained original result contract</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Analysis report generated</name>
    <verification>Authorized report exists with current hashes, scoped evidence, missing/failed checks and outcome limits; no source mutation or task workflow</verification>
  </checkpoint>
</definition_of_done>
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `SCOPE_EMPTY` | No readable target files/modules resolved | Return bounded missing input to caller |
| `FEATURE_NOT_FOUND` | Feature artifacts not at expected path | Verify feature_id, check x-ipe-docs/requirements/ |
| `CIRCULAR_DEPS` | Verified cyclic edges | Retain edges and visited termination; cycle need not fail analysis |
| `SCOPE_LIMIT` | Ten passes or approved inspection boundary leaves frontier | Report incomplete frontier; fail only if required analysis deliverable cannot be satisfied |
| `BUILD_FAILURE` | Applicable executed check fails | Record command/exit/revision; continue read-only analysis; no source repair |
| `EVIDENCE_UNAVAILABLE` | Required measurement/check inaccessible | Distinguish unavailable from executed failure; return limits for owner |
| `SOURCE_INVALID` | Explicit target/link escapes, is ambiguous or unreadable | Fail pertinent analysis with actual partial evidence, no silent fallback |
| `CONFIG_INVALID` | Selected consultation configuration is unreadable, malformed or has non-boolean tool flags | Return path/key error to caller with partial analysis; no consultation, config repair or permissive fallback |

## References

| File | Purpose |
|------|---------|
| [references/detailed-procedures.md](.github/skills/x-ipe-tool-refactoring-analysis/references/detailed-procedures.md) | Bounded discovery, evidence, configuration and recommendation procedures |
| [references/output-schema.md](.github/skills/x-ipe-tool-refactoring-analysis/references/output-schema.md) | Complete output data model schema |
| [references/examples.md](.github/skills/x-ipe-tool-refactoring-analysis/references/examples.md) | Concrete usage examples |
