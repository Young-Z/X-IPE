---
name: x-ipe-tool-refactoring-analysis
description: Analyze refactoring scope, expand dependencies, and evaluate code quality across 5 dimensions. Use when starting a refactoring initiative or assessing code quality gaps. Triggers on requests like "analyze for refactoring", "evaluate refactoring scope", "assess code quality".
---

# Refactoring Analysis Tool

## Purpose

AI Agents follow this skill to analyze and expand refactoring scope, then evaluate code quality by:
1. Checking existing quality baseline
2. Parsing and iteratively expanding scope via dependency analysis
3. Evaluating quality across 5 perspectives (requirements, features, tech spec, tests, tracing)
4. Generating actionable refactoring suggestions with applicable principles

## Important Notes

BLOCKING: This is a **tool skill** — it performs analysis only, no task board interaction.
CRITICAL: Called by `x-ipe-task-based-code-refactor` as Step 1 of the refactoring workflow.

## About

Refactoring analysis is the foundation of safe refactoring. It discovers the true scope of changes by iteratively expanding from initial files to all related code, then evaluates how well documentation, specs, and tests align with the actual code state.

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
    refactoring_purpose: "<why refactoring is needed>"
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
      2. IF scope_level == "feature" AND feature_id is null → ASK human
      3. IF scope_level == "custom" → set to null
    </steps>
  </field>

  <field name="scope.files">
    <steps>
      1. IF scope_level == "feature" → auto-resolve from feature artifacts:
         a. Read specification.md → extract file references
         b. Read technical-design.md → extract component files
         c. Collect test files referenced in technical design
      2. IF scope_level == "custom" AND caller provides files[] → use provided list
      3. IF scope_level == "custom" AND files[] is empty → ASK human
    </steps>
  </field>

  <field name="quality_baseline_path" source="default: x-ipe-docs/planning/project-quality-evaluation.md" />
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Scope provided</name>
    <verification>scope_level set; if feature: feature_id exists; if custom: files[] non-empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Target code accessible</name>
    <verification>All listed files/modules can be read from filesystem</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Code compiles without errors</name>
    <verification>Run build/lint to confirm no pre-existing failures</verification>
  </checkpoint>
</definition_of_ready>
```

## Operations

### Operation: Full Analysis

**When:** Starting a refactoring initiative — analyze scope and evaluate quality.

```xml
<operation name="full_analysis">
  <action>
    Phase 1 — Baseline Check:
      1. CHECK for quality evaluation at quality_baseline_path
      2. IF exists: READ report, EXTRACT baseline data (scores, violations, gaps)
      3. IF not exists: SET quality_baseline.exists = false

    Phase 2 — Parse & Expand Scope:
      1. IF scope_level == "feature":
         a. RESOLVE feature artifacts from x-ipe-docs/requirements/EPIC-XXX/FEATURE-XXX/
         b. READ specification.md → extract file references
         c. READ technical-design.md → extract component files, module boundaries
         d. POPULATE files[] and modules[] from resolved artifacts
      2. VALIDATE scope (files exist, modules identifiable)
      3. SCOPE EXPANSION LOOP (max 10 iterations):
         a. FOR EACH file: ANALYZE imports/dependencies
         b. FOR EACH module: IDENTIFY sibling/parent/child modules, assess coupling
         c. REFLECT: check hidden dependencies, config files, test files
         d. LOG expansion (iteration, files added, reason)
         e. REPEAT until no new items found OR iteration > 10

    Phase 3 — Evaluate Quality (5 perspectives):
      When scope_level=feature, use feature_id as primary anchor.
      3a. Requirements: SEARCH x-ipe-docs/requirements/**/*.md, compare with code, identify gaps
          Gap types: undocumented | unimplemented | deviated
      3b. Features: READ specification.md, compare behavior, identify gaps
          Gap types: missing | extra | deviated
      3c. Tech Spec: READ technical-design.md, compare structure/interfaces/patterns
          Gap types: structure | interface | data_model | pattern
      3d. Test Coverage: RUN coverage tool, analyze line/branch coverage
          Gap types: business_logic | error_handling | edge_case
      3e. Tracing: SCAN for @x_ipe_tracing decorators, check coverage and redaction
          Gap types: untraced | unredacted | wrong_level
      CRITICAL: Evaluate ALL 5 perspectives even if docs missing (set status: not_found)

    Phase 4 — Generate Suggestions:
      1. CONSULT TOOL SKILLS (config-filtered):
         a. DISCOVER: Scan .github/skills/x-ipe-tool-implementation-*/ for available tools
         b. READ CONFIG: Read x-ipe-docs/config/tools.json → stages.feedback.refactoring_analysis
            - IF section missing/empty → config_active = false (all tools enabled)
            - ELSE → config_active = true (opt-in filtering); force-enable general
         c. FILTER: IF config_active → only ENABLED tools participate
         d. FOR detected tech_stack: read matched tool's "Built-In Practices"
      2. ANALYZE quality gaps → derive suggestion categories
      3. SCAN code for principle violations (SRP, DRY, KISS, YAGNI, SoC)
      4. CROSS-REFERENCE gaps against tool built-in practices:
         - IF tool already enforces a practice → mark gap as "auto-enforced by tool"
         - IF tool provides conventions → reference them in suggestion
      5. PRIORITIZE into primary (MUST) and secondary (nice-to-have) principles
      6. FORMULATE specific, measurable goals with priority and rationale
      7. DEFINE target structure and constraints (backward compat, API stability)
      BLOCKING: Every suggestion must trace back to a documented gap

    Phase 5 — Compile Output:
      1. CALCULATE dimension scores (1-10): score = 10 - SUM(violations × weights), clamped 1-10
      2. DERIVE status: 8-10 = aligned, 6-7 = needs_attention, 1-5 = critical
      3. CALCULATE overall_quality_score (weighted avg: req 0.20, feat 0.20, tech 0.20, test 0.20, tracing 0.10, code 0.10)
      4. GENERATE report to x-ipe-docs/refactoring/analysis-{context}.md
      5. SELF-REVIEW: check for missing content, inconsistencies
  </action>
  <constraints>
    - BLOCKING: Scope expansion must iterate until stable (no new items) or cap at 10
    - BLOCKING: Every suggestion must trace to a documented gap
    - CRITICAL: Constraints must include backward compatibility and API stability
    - MANDATORY: All markdown links use project-root-relative paths
  </constraints>
  <output>
    refactoring_scope, code_quality_evaluated, refactoring_suggestion, refactoring_principle
  </output>
</operation>
```

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    quality_baseline:
      exists: true | false
      overall_score: "<1-10>"
    refactoring_scope:
      scope_level: "feature | custom"
      feature_id: "{FEATURE-XXX or null}"
      refactoring_purpose: "<purpose>"
      files: [<expanded file list>]
      modules: [<expanded module list>]
      dependencies: [<identified dependencies>]
      scope_expansion_log: [<log entries>]
    code_quality_evaluated:
      requirements_alignment: { score: "<1-10>", status: "<aligned|needs_attention|critical>", gaps: [] }
      specification_alignment: { score: "<1-10>", status: "<aligned|needs_attention|critical>", gaps: [] }
      test_coverage: { score: "<1-10>", line_coverage: "<XX%>", critical_gaps: [] }
      code_alignment: { score: "<1-10>", file_size_violations: [], solid_assessment: {}, kiss_assessment: {} }
      overall_quality_score: "<1-10>"
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

**Evaluation Thresholds:** Line Coverage ≥80%, File Size ≤800 lines, Function Size ≤50 lines

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Scope expansion completed</name>
    <verification>Loop terminated with no new items or at iteration cap</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All 5 quality perspectives evaluated</name>
    <verification>Requirements, features, tech spec, test coverage, tracing all have status and gaps</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Suggestions generated with principles</name>
    <verification>refactoring_suggestion and refactoring_principle populated</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Analysis report generated</name>
    <verification>Report at x-ipe-docs/refactoring/analysis-{context}.md exists</verification>
  </checkpoint>
</definition_of_done>
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `SCOPE_EMPTY` | No files provided or resolved | Ask caller for file paths |
| `FEATURE_NOT_FOUND` | Feature artifacts not at expected path | Verify feature_id, check x-ipe-docs/requirements/ |
| `CIRCULAR_DEPS` | Scope expansion exceeds 10 iterations | Warn about circular dependencies, cap scope |
| `BUILD_FAILURE` | Code doesn't compile before analysis | Fix build errors before analysis |

## References

| File | Purpose |
|------|---------|
| [references/detailed-procedures.md](.github/skills/x-ipe-tool-refactoring-analysis/references/detailed-procedures.md) | Detailed sub-steps, scoring formulas, gap definitions |
| [references/output-schema.md](.github/skills/x-ipe-tool-refactoring-analysis/references/output-schema.md) | Complete output data model schema |
| [references/examples.md](.github/skills/x-ipe-tool-refactoring-analysis/references/examples.md) | Concrete usage examples |
