---
name: x-ipe-task-based-code-refactor
description: Execute code refactoring based on validated scope, suggestions, and principles. Use after Improve Code Quality Before Refactoring. Follows refactoring plan based on suggestions and principles, executes changes, updates all references. Triggers on requests like "execute refactoring", "refactor code", "apply refactoring plan".
---

# Task-Based Skill: Code Refactor V2

## Purpose

Execute safe code refactoring with full traceability by:
1. **Reflect** on requirements and features involved in scope
2. **Plan** refactoring following suggestions and principles
3. **Execute** refactoring incrementally with test validation
4. **Update** references in features and requirements

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

This skill REQUIRES output from `x-ipe-task-based-improve-code-quality` skill.

This skill is part of the **code-refactoring-stage** chain:
1. `x-ipe-task-based-refactoring-analysis` - produces refactoring_suggestion, refactoring_principle
2. `x-ipe-task-based-improve-code-quality` - produces code_quality_evaluated
3. `x-ipe-task-based-code-refactor` - executes refactoring (this skill)

BLOCKING: If user requests "refactor" directly without prior analysis, REDIRECT to `x-ipe-task-based-refactoring-analysis` to start the proper chain.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Code Refactor V2"

  # Task type attributes
  category: "code-refactoring-stage"
  next_task_based_skill: null
  require_human_review: yes

  # Required inputs
  auto_proceed: false
  refactoring_scope: "{from previous task}"
  refactoring_suggestion: "{from Refactoring Analysis task}"
  refactoring_principle: "{from Refactoring Analysis task}"
  code_quality_evaluated: "{from Improve Code Quality task}"

  # Context (from previous task or project)
  # See references/refactoring-techniques.md for full input structure definitions
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>refactoring_scope provided</name>
    <verification>Verify scope object contains file list and boundaries</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>refactoring_suggestion provided</name>
    <verification>Verify suggestions include goals, priorities, target_structure</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>refactoring_principle provided</name>
    <verification>Verify principles include names and application areas</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>code_quality_evaluated provided</name>
    <verification>Verify quality evaluation includes scores and gap analysis</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All documentation aligned</name>
    <verification>Requirements, features, and tech specs reflect current code</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test coverage at or above 80%</name>
    <verification>Run coverage report and verify threshold met</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All tests passing</name>
    <verification>Run full test suite with zero failures</verification>
  </checkpoint>
  <prerequisite_chain_enforcement>
    IF refactoring_suggestion OR refactoring_principle MISSING:
      STOP - REDIRECT to x-ipe-task-based-refactoring-analysis
    IF code_quality_evaluated MISSING:
      STOP - REDIRECT to x-ipe-task-based-improve-code-quality
    ONLY proceed if ALL prerequisites present
  </prerequisite_chain_enforcement>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Reflect on Context | Analyze requirements, features, suggestions/principles | Context understood |
| 2 | Generate Plan | Propose refactoring plan | Human approves |
| 3 | Execute Refactoring | Apply changes incrementally | All tests pass |
| 4 | Update References | Sync docs with new structure | Docs updated |
| 5 | Validate and Complete | Verify quality improvement, apply tracing | Human approves |

BLOCKING: Step 2 to 3 requires human approval of plan.
BLOCKING: Step 3 halts if any test fails (must fix or revert).
BLOCKING: Step 4 to 5 requires all references updated.

---

## Execution Procedure

```xml
<procedure name="code-refactor-v2">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Reflect on Context</name>
    <action>
      1. FOR EACH file in scope, BUILD context_map with requirements, features, tech specs
      2. REVIEW refactoring_suggestion, EXTRACT goals, priorities, target_structure
      3. REVIEW refactoring_principle, MAP principles to code areas, note constraints
      4. IDENTIFY impacts (docs, tests, downstream code)
      5. VALIDATE alignment with code_quality_evaluated gaps
    </action>
    <output>context_map with code relationships and principle-to-code mapping</output>
  </step_1>

  <step_2>
    <name>Generate Refactoring Plan</name>
    <action>
      1. ANALYZE current structure (sizes, smells, violations)
      2. DESIGN target structure applying principles:
         - SOLID: Extract classes/modules for SRP violations
         - DRY: Plan abstractions
         - KISS: Simplifications
         - YAGNI: Remove unused code
      3. CREATE refactoring_plan with phases ordered by goal priority
      4. VALIDATE plan against constraints
      5. PRESENT plan to human, WAIT for approval
    </action>
    <constraints>
      - BLOCKING: Do not proceed to step 3 without human approval
    </constraints>
    <output>Approved refactoring_plan with phases and principle mappings</output>
  </step_2>

  <step_3>
    <name>Execute Refactoring</name>
    <action>
      FOR EACH phase in refactoring_plan:
        1. CREATE checkpoint: git commit -m "checkpoint: before phase {N}"
        2. Apply changes following principle_applied, update imports
        3. RUN tests after each change
        4. IF tests fail:
           - Fix if import issue
           - REVERT if behavior changed
           - Update test if change is legitimate
        5. COMMIT: git commit -m "refactor({scope}): {desc} [principle: {p}]"
    </action>
    <constraints>
      - BLOCKING: Must fix or revert if any test fails before continuing
      - CRITICAL: Structure changes only, preserve existing behavior
    </constraints>
    <output>Refactored code with incremental commits per phase</output>
  </step_3>

  <step_4>
    <name>Update References</name>
    <action>
      1. UPDATE technical designs (component list, paths, Design Change Log)
      2. UPDATE feature specifications (file references)
      3. UPDATE requirements (implementation notes)
      4. COMPILE references_updated list
    </action>
    <constraints>
      - BLOCKING: All references must be updated before proceeding to step 5
    </constraints>
    <output>references_updated list of all modified documents</output>
  </step_4>

  <step_5>
    <name>Validate and Complete</name>
    <action>
      1. RUN final test suite (coverage maintained or improved)
      2. VALIDATE goals achieved from refactoring_suggestion
      3. VALIDATE principles applied and constraints respected
      4. CALCULATE quality improvements (before/after scores)
      5. CHECK tracing preserved on moved/renamed functions
      6. IDENTIFY new code needing tracing
      7. IF tracing infrastructure exists:
         - INVOKE x-ipe-tool-tracing-instrumentation skill for new files/functions
         - RE-RUN tests, UPDATE tracing counts in summary
      8. PRESENT summary to human, WAIT for approval
      9. CREATE final commit
    </action>
    <branch>
      IF: No tracing infrastructure or only non-code files touched
      THEN: Skip tracing sub-steps (5-7)
      ELSE: Apply full tracing validation
    </branch>
    <success_criteria>
      - All tests passing
      - Quality score improved
      - All goals achieved or documented
      - Tracing preserved on existing code
      - Human review approved
    </success_criteria>
    <output>Refactoring summary with quality scores and tracing status</output>
  </step_5>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "code-refactoring-stage"
  status: completed | blocked
  next_task_based_skill: null
  require_human_review: yes
  task_output_links:
    - "{paths to refactored files}"

  refactoring_summary:
    files_modified: "{count}"
    files_created: "{count}"
    files_deleted: "{count}"
    principles_applied:
      - principle: "{name}"
        application_count: "{count}"
        areas: "{list}"
    goals_achieved:
      - goal: "{name}"
        status: "{achieved | partial | skipped}"
        notes: "{details}"

  code_quality_evaluated:
    quality_score_before: "{1-10}"
    quality_score_after: "{1-10}"
    test_coverage:
      before: "{percentage}"
      after: "{percentage}"
      status: "{maintained | improved | degraded}"
    references_updated:
      requirements: "{count}"
      specifications: "{count}"
      technical_designs: "{count}"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>All planned changes executed</name>
    <verification>Compare completed phases against refactoring_plan</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All tests passing</name>
    <verification>Run full test suite with zero failures</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test coverage maintained or improved</name>
    <verification>Compare coverage before/after, verify no regression</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Quality score improved</name>
    <verification>Compare quality_score_before vs quality_score_after</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Technical designs updated</name>
    <verification>Verify component list, paths, and Design Change Log reflect new structure</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature specs updated if affected</name>
    <verification>Check file references in affected feature specifications</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Requirements updated if affected</name>
    <verification>Check implementation notes in affected requirements</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All changes committed</name>
    <verification>Verify clean git status with no uncommitted changes</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human review approved</name>
    <verification>Explicit approval received from human reviewer</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tracing preserved and applied</name>
    <verification>Existing decorators preserved on moved/renamed functions; new public functions have @x_ipe_tracing decorators</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Extract Module

**When:** File has multiple responsibilities
**Then:**
```
1. Identify cohesive blocks
2. Create new file per responsibility
3. Move with tests
4. Update imports
5. Test after each move
```

### Pattern: Apply SOLID Principles

**When:** refactoring_principle includes SOLID
**Then:**
```
1. S - Split classes with multiple responsibilities
2. O - Extract interfaces for extension points
3. L - Ensure substitutability in hierarchies
4. I - Split fat interfaces into focused ones
5. D - Inject dependencies instead of hard-coding
```

### Pattern: Rollback on Failure

**When:** Tests fail after a change
**Then:**
```
1. STOP current work
2. Analyze failure cause
3. REVERT if behavior changed
4. Fix if import/reference issue
5. Update test if change is legitimate
```

### Pattern: Tracing Preservation

**When:** Moving, splitting, or renaming functions
**Then:**
```
1. Keep @x_ipe_tracing decorators on moved functions
2. Preserve redact=[] parameters
3. Add decorators to new public functions in split modules
4. Apply x-ipe-tool-tracing-instrumentation for new code
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Big bang refactor | High risk, hard to debug failures | Small incremental changes |
| Skip test runs | Silent regressions | Test after EVERY change |
| Change behavior | Refactoring must preserve semantics | Structure only, same behavior |
| Ignore failing tests | Compounds errors | Fix immediately or revert |
| Skip doc updates | Docs drift from code | Always update docs at end |
| Ignore suggestions | Misaligned with analysis goals | Follow refactoring_suggestion goals |
| Violate constraints | Breaks agreed boundaries | Always respect constraints |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.

See [references/refactoring-techniques.md](references/refactoring-techniques.md) for detailed procedures, input/output structures, and tracing rules.
