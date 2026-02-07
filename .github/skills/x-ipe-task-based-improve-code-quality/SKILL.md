---
name: x-ipe-task-based-improve-code-quality
description: Update documentation to reflect current code before refactoring. Use after Refactoring Analysis to sync requirements, features, technical design, and tests with actual code state. Triggers on requests like "improve quality before refactoring", "sync docs with code", "update specs for refactoring".
---

# Task-Based Skill: Improve Code Quality Before Refactoring

## Purpose

Ensure documentation accurately reflects current code state before refactoring by:
1. Syncing requirements with actual code behavior
2. Syncing feature specs with implemented functionality
3. Syncing technical design with actual architecture
4. Updating tests to cover current behavior (reach 80%+)

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.
This skill REQUIRES output from `x-ipe-task-based-refactoring-analysis` skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  # Task attributes
  task_id: "{TASK-XXX}"
  task_based_skill: "Improve Code Quality Before Refactoring"

  # Task type attributes
  category: "code-refactoring-stage"
  next_task_based_skill: "Code Refactor V2"
  require_human_review: "yes"

  # Required inputs
  auto_proceed: false
  refactoring_scope:
    files: ["{list of file paths}"]
    modules: ["{list of module names}"]
    dependencies: ["{identified dependencies}"]
    scope_expansion_log: ["{log of scope expansions}"]

  # Context (from refactoring-analysis task)
  code_quality_evaluated:
    requirements_alignment:
      status: "aligned | needs_update | not_found"
      gaps: ["{list of gaps with type: undocumented|unimplemented|deviated}"]
      related_docs: ["{paths}"]
    specification_alignment:
      status: "aligned | needs_update | not_found"
      gaps: ["{list of gaps}"]
      feature_ids: ["{FEATURE-XXX}"]
      spec_docs: ["{paths}"]
    test_coverage:
      status: "sufficient | insufficient | no_tests"
      line_coverage: "{XX%}"
      branch_coverage: "{XX%}"
      target_percentage: 80
      critical_gaps: ["{untested areas}"]
      external_api_mocked: "true | false"
    code_alignment:
      status: "aligned | needs_attention | critical"
      file_size_violations: ["{files exceeding 800 lines}"]
      solid_assessment: "{srp, ocp, lsp, isp, dip}"
      kiss_assessment: "{over_engineering, straightforward_logic, minimal_dependencies, clear_intent}"
      modular_design_assessment: "{module_cohesion, module_coupling, single_entry_point, folder_structure, reusability, testability}"
      code_smells: ["{detected smells}"]
    overall_quality_score: "{1-10}"

  # Pass-through attributes
  refactoring_suggestion: "{from previous task}"
  refactoring_principle: "{from previous task}"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>refactoring_scope provided</name>
    <verification>Files list exists and all files accessible on filesystem</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>code_quality_evaluated provided</name>
    <verification>All 4 alignment sections present with valid overall_quality_score</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Write access to documentation folders</name>
    <verification>Can write to x-ipe-docs/requirements/ and x-ipe-docs/refactoring/</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Validate Inputs | Verify required inputs from analysis | Inputs valid |
| 2 | Sync Requirements | Update requirement docs to match code | Docs aligned |
| 3 | Sync Features | Update feature specs to match code | Specs aligned |
| 4 | Sync Tech Design | Update technical designs to match code | Designs aligned |
| 5 | Update Tests | Add/fix tests to reach 80% coverage | Coverage >= 80% |
| 6 | Generate Output | Compile updated code_quality_evaluated | Human approves |

BLOCKING: Step 5 to 6 blocked if test coverage < 80%.
BLOCKING: Step 6 blocked if any alignment status is not "aligned".

---

## Execution Procedure

```xml
<procedure name="improve-code-quality-before-refactoring">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Validate Inputs</name>
    <action>
      1. CHECK refactoring_scope: files list non-empty, all files exist
      2. CHECK code_quality_evaluated: all 4 alignment sections present, overall_quality_score valid
      3. LOG starting state: initial quality score, gap counts per category, current test coverage
    </action>
    <constraints>
      - BLOCKING: If any input missing, return error "Missing required input: {input_name}" and return to Refactoring Analysis
    </constraints>
    <output>Validated inputs, logged baseline metrics</output>
  </step_1>

  <step_2>
    <name>Sync Requirements with Code</name>
    <action>
      1. IF requirements_alignment.status = "needs_update":
         FOR EACH gap in gaps, handle by type:
         - "undocumented": Document implemented behavior, add "Discovered Behavior" section
         - "unimplemented": Ask human to defer, implement, or remove
         - "deviated": Ask human to update requirement or note as bug
         SET status to "aligned", gaps to empty
      2. IF status = "not_found":
         Ask human: create from code, skip, or block
         If create: generate x-ipe-docs/requirements/{module}-requirements.md from code behavior
    </action>
    <output>requirements_alignment.status = "aligned", updates_made list</output>
  </step_2>

  <step_3>
    <name>Sync Features with Code</name>
    <action>
      1. IF specification_alignment.status = "needs_update":
         FOR EACH gap, read x-ipe-docs/requirements/{feature_id}/specification.md
         Handle by type:
         - "missing": Add acceptance criteria, mark "Added during refactoring prep"
         - "extra": Ask human to add to spec or mark for removal
         - "deviated": Update specification to match code, note in change log
         SET status to "aligned", gaps to empty
      2. IF status = "not_found":
         Create feature docs from code for each module in scope
    </action>
    <output>specification_alignment.status = "aligned", updates_made list</output>
  </step_3>

  <step_4>
    <name>Sync Technical Design with Code</name>
    <action>
      1. IF technical_spec_alignment.status = "needs_update":
         FOR EACH gap, read x-ipe-docs/requirements/{feature_id}/technical-design.md
         Handle by type:
         - "structure": Update component list and directory structure
         - "interface": Update interface definitions, add new public APIs
         - "data_model": Update data model diagrams with actual field names/types
         - "pattern": Document actual patterns, note deviations
         Add entry to Design Change Log: date, "Pre-Refactor Sync", change summary
         SET status to "aligned", gaps to empty
      2. IF status = "not_found":
         Create technical design from code analysis as baseline for refactoring
    </action>
    <output>technical_spec_alignment.status = "aligned", updates_made list</output>
  </step_4>

  <step_5>
    <name>Update Tests to Target Coverage</name>
    <action>
      1. FOR EACH file in test_coverage.critical_gaps:
         - Analyze untested code (signatures, types, edge cases)
         - Generate tests: happy path, edge cases, error handling
         - Write tests following project conventions and existing patterns
      2. RUN all tests - must pass (testing existing behavior)
      3. RUN coverage - repeat adding tests until >= 80%
    </action>
    <constraints>
      - BLOCKING: Coverage must reach 80% before proceeding
      - CRITICAL: If test fails due to code bug, DO NOT fix the bug.
        Document it, mark test as @skip, add to refactoring_scope
    </constraints>
    <output>test_coverage.status = "sufficient", tests_added count, tests_updated count</output>
  </step_5>

  <step_6>
    <name>Generate Output</name>
    <action>
      1. VERIFY all alignments are "aligned" and test_coverage is "sufficient"
         If any not aligned, return to appropriate step
      2. CALCULATE new overall_quality_score (10 if all aligned, deduct for minor issues)
      3. COMPILE validation_summary: docs_created, docs_updated, tests_added, ready_for_refactoring
      4. SAVE report to x-ipe-docs/refactoring/validation-{task_id}.md
      5. PRESENT summary to human showing alignment status, coverage change, and readiness
      6. WAIT for human approval
    </action>
    <constraints>
      - BLOCKING: Cannot proceed until all alignment statuses = "aligned"
    </constraints>
    <output>Validation report, human approval</output>
  </step_6>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "code-refactoring-stage"
  status: "completed | blocked"
  next_task_based_skill: "Code Refactor V2"
  require_human_review: "yes"
  auto_proceed: "{from input}"
  task_output_links:
    - "x-ipe-docs/refactoring/validation-{task_id}.md"

  # Pass-through attributes (unchanged)
  refactoring_scope: "{from input}"
  refactoring_suggestion: "{from input}"
  refactoring_principle: "{from input}"

  # Updated quality evaluation
  code_quality_evaluated:
    requirements_alignment:
      status: "aligned"
      gaps: []
      updates_made: ["{list of doc updates}"]
    specification_alignment:
      status: "aligned"
      gaps: []
      updates_made: ["{list of spec updates}"]
    test_coverage:
      status: "sufficient"
      line_coverage: "{XX% - should be >= 80}"
      branch_coverage: "{XX%}"
      external_api_mocked: true
      tests_added: "{count}"
      tests_updated: "{count}"
    code_alignment:
      status: "{from input - not modified in this phase}"
      # NOTE: Code alignment issues are addressed in Code Refactor V2
    overall_quality_score: "{improved score}"
    validation_summary:
      docs_created: "{count}"
      docs_updated: "{count}"
      tests_added: "{count}"
      ready_for_refactoring: "true | false"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Requirements synced with code</name>
    <verification>requirements_alignment.status = "aligned" and gaps is empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature specs synced with code</name>
    <verification>specification_alignment.status = "aligned" and gaps is empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Technical design synced with code</name>
    <verification>technical_spec_alignment.status = "aligned" and gaps is empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test coverage at or above 80%</name>
    <verification>Run coverage tool, verify line_coverage >= 80</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All tests passing</name>
    <verification>Run full test suite, zero failures</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Validation report generated</name>
    <verification>File exists at x-ipe-docs/refactoring/validation-{task_id}.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human review approved</name>
    <verification>Human explicitly approved the validation summary</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Create Missing Documentation

**When:** status = "not_found" for any category
**Then:**
```
1. Analyze code to understand behavior
2. Create documentation from code (reverse engineering)
3. Mark as "Generated from code - requires review"
4. Continue with validation
```

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
| Skip documentation sync | Refactoring without context | Always sync docs first |
| Fix bugs during validation | Scope creep | Document bugs, fix in refactor phase |
| Lower coverage target | Risk during refactoring | Keep 80% minimum |
| Delete failing tests | Lose behavior contracts | Fix or document as bug |
| Proceed with gaps | Unknown risks | All alignments must be "aligned" |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.
