---
name: x-ipe-tool-code-quality-sync
description: Sync documentation and tests with actual code state before refactoring. Use after refactoring analysis to align requirements, features, technical design, and reach 80%+ test coverage. Triggers on requests like "sync docs with code", "improve quality before refactoring", "update specs for refactoring".
---

# Code Quality Sync Tool

## Purpose

AI Agents follow this skill to sync documentation with actual code state by:
1. Syncing requirements with implemented behavior
2. Syncing feature specs with actual functionality
3. Syncing technical design with real architecture
4. Updating tests to reach 80%+ coverage

## Important Notes

BLOCKING: This is a **tool skill** — it performs doc/test sync only, no task board interaction.
CRITICAL: Called by `x-ipe-task-based-code-refactor` as Step 2 of the refactoring workflow.
CRITICAL: Requires output from `x-ipe-tool-refactoring-analysis` as input.

## About

Before refactoring, documentation must accurately reflect the current code state. This tool bridges the gap between what docs say and what code does, ensuring a safe refactoring baseline.

**Key Concepts:**
- **Doc Sync** — Update requirements, specs, and designs to match actual code behavior
- **Test Baseline** — Reach 80%+ coverage so refactoring changes can be validated
- **Gap Resolution** — Handle undocumented, unimplemented, and deviated behaviors

## When to Use

```yaml
triggers:
  - "sync docs with code"
  - "improve quality before refactoring"
  - "update specs for refactoring"
  - "align documentation"

not_for:
  - "analyze for refactoring" → use x-ipe-tool-refactoring-analysis
  - "execute refactoring" → use x-ipe-task-based-code-refactor
```

## Input Parameters

```yaml
input:
  operation: "full_sync"
  refactoring_scope:
    scope_level: "feature | custom"
    feature_id: "{FEATURE-XXX or null}"
    refactoring_purpose: "<purpose>"
    files: [<file list>]
    modules: [<module list>]
  code_quality_evaluated:
    requirements_alignment: { status: "<aligned|needs_update|not_found>", gaps: [], related_docs: [] }
    specification_alignment: { status: "<aligned|needs_update|not_found>", gaps: [], spec_docs: [] }
    test_coverage: { status: "<sufficient|insufficient|no_tests>", line_coverage: "<XX%>", critical_gaps: [] }
    code_alignment: { status: "<aligned|needs_attention|critical>" }
    overall_quality_score: "<1-10>"
  refactoring_suggestion: "{from analysis — pass-through}"
  refactoring_principle: "{from analysis — pass-through}"
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies — currently only full_sync" />

  <field name="refactoring_scope" source="x-ipe-tool-refactoring-analysis output">
    <steps>
      1. IF analysis output contains refactoring_scope → use directly
      2. ELSE → ERROR: analysis must run first
    </steps>
  </field>

  <field name="code_quality_evaluated" source="x-ipe-tool-refactoring-analysis output">
    <steps>
      1. IF analysis output contains code_quality_evaluated → use directly
      2. ELSE → ERROR: analysis must run first
    </steps>
  </field>

  <field name="refactoring_suggestion" source="x-ipe-tool-refactoring-analysis output (pass-through)" />
  <field name="refactoring_principle" source="x-ipe-tool-refactoring-analysis output (pass-through)" />
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Analysis output provided</name>
    <verification>refactoring_scope and code_quality_evaluated contain valid data from analysis</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Write access to documentation</name>
    <verification>Can write to x-ipe-docs/requirements/ and x-ipe-docs/refactoring/</verification>
  </checkpoint>
</definition_of_ready>
```

## Operations

### Operation: Full Sync

**When:** After refactoring analysis — sync all docs and tests with code before refactoring.

```xml
<operation name="full_sync">
  <action>
    Phase 1 — Sync Requirements:
      IF requirements_alignment.status == "needs_update":
        FOR EACH gap in gaps, handle by type:
        - "undocumented": Document implemented behavior, add "Discovered Behavior" section
        - "unimplemented": Ask human to defer, implement, or remove
        - "deviated": Ask human to update requirement or note as bug
        SET status to "aligned", gaps to empty
      IF status == "not_found":
        Ask human: create from code, skip, or block
        If create: generate requirement docs from code behavior

    Phase 2 — Sync Feature Specs:
      IF specification_alignment.status == "needs_update":
        FOR EACH gap, read specification.md for affected features
        Handle by type:
        - "missing": Add acceptance criteria, mark "Added during refactoring prep"
        - "extra": Ask human to add to spec or mark for removal
        - "deviated": Update specification to match code, note in change log
        SET status to "aligned", gaps to empty
      IF status == "not_found":
        Create feature docs from code for each module in scope

    Phase 3 — Sync Technical Design:
      IF technical_spec_alignment.status == "needs_update":
        FOR EACH gap, read technical-design.md
        Handle by type:
        - "structure": Update component list and directory structure
        - "interface": Update interface definitions, add new public APIs
        - "data_model": Update data model with actual field names/types
        - "pattern": Document actual patterns, note deviations
        Add entry to Design Change Log: date, "Pre-Refactor Sync", summary
        SET status to "aligned", gaps to empty
      IF status == "not_found":
        Create technical design from code analysis as baseline

    Phase 4 — Update Tests:
      FOR EACH file in test_coverage.critical_gaps:
        1. Analyze untested code (signatures, types, edge cases)
        2. Generate tests: happy path, edge cases, error handling
        3. Write tests following project conventions
      RUN all tests — must pass (testing existing behavior)
      RUN coverage — repeat adding tests until ≥ 80%
      CRITICAL: If test fails due to code bug, DO NOT fix the bug.
        Document it, mark test as @skip, add to refactoring scope.

    Phase 5 — Compile Output:
      1. VERIFY all alignments are "aligned" and coverage ≥ 80%
      2. CALCULATE new overall_quality_score
      3. COMPILE validation_summary: docs_created, docs_updated, tests_added
      4. SAVE report to x-ipe-docs/refactoring/validation-{context}.md
  </action>
  <constraints>
    - BLOCKING: Coverage must reach 80% before completing
    - BLOCKING: All alignment statuses must be "aligned" before completing
    - MANDATORY: All markdown links use project-root-relative paths
  </constraints>
  <output>
    Updated code_quality_evaluated with aligned statuses, pass-through refactoring_suggestion and refactoring_principle
  </output>
</operation>
```

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    code_quality_evaluated:
      requirements_alignment:
        status: "aligned"
        gaps: []
        updates_made: [<list of doc updates>]
      specification_alignment:
        status: "aligned"
        gaps: []
        updates_made: [<list of spec updates>]
      test_coverage:
        status: "sufficient"
        line_coverage: "<XX% — should be ≥ 80>"
        tests_added: "<count>"
        tests_updated: "<count>"
      code_alignment:
        status: "{from input — not modified in this phase}"
      overall_quality_score: "<improved score>"
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
  <checkpoint required="true">
    <name>Requirements synced</name>
    <verification>requirements_alignment.status == "aligned" and gaps is empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature specs synced</name>
    <verification>specification_alignment.status == "aligned" and gaps is empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Technical design synced</name>
    <verification>technical_spec_alignment.status == "aligned" and gaps is empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test coverage ≥ 80%</name>
    <verification>Run coverage tool, verify line_coverage ≥ 80</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All tests passing</name>
    <verification>Run full test suite, zero failures</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Validation report generated</name>
    <verification>File exists at x-ipe-docs/refactoring/validation-{context}.md</verification>
  </checkpoint>
</definition_of_done>
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `MISSING_ANALYSIS` | Analysis output not provided | Run x-ipe-tool-refactoring-analysis first |
| `COVERAGE_UNREACHABLE` | Cannot reach 80% (e.g., untestable code) | Document reason, ask human to accept lower threshold |
| `BUG_FOUND` | Test fails due to code bug | Mark test @skip, document bug, add to scope |
| `WRITE_DENIED` | Cannot write to documentation folders | Check filesystem permissions |

## Patterns & Anti-Patterns

### Pattern: Handle Bugs Found During Testing

**When:** New test fails because code is buggy
**Then:**
```
1. DO NOT fix the bug now
2. Document bug with test as evidence
3. Mark test as @skip with reason
4. Add to refactoring_scope as bug to fix
5. Continue with coverage target
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip doc sync | Refactoring without context | Always sync docs first |
| Fix bugs during sync | Scope creep | Document bugs, fix in refactor phase |
| Lower coverage target | Risk during refactoring | Keep 80% minimum |
| Delete failing tests | Lose behavior contracts | Fix or document as bug |

## References

| File | Purpose |
|------|---------|
| [references/examples.md](.github/skills/x-ipe-tool-code-quality-sync/references/examples.md) | Concrete usage examples |
