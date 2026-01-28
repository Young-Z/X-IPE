---
name: task-type-code-refactor-v2
description: Execute code refactoring based on validated scope, suggestions, and principles. Use after Improve Code Quality Before Refactoring. Follows refactoring plan based on suggestions and principles, executes changes, updates all references. Triggers on requests like "execute refactoring", "refactor code", "apply refactoring plan".
---

# Task Type: Code Refactor V2

## Purpose

Execute safe code refactoring with full traceability by:
1. **Reflect** on requirements and features involved in scope
2. **Plan** refactoring following suggestions and principles
3. **Execute** refactoring incrementally with test validation
4. **Update** references in features and requirements
5. **Output** updated code_quality_evaluated confirming improvements

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.
- This skill REQUIRES output from `task-type-improve-code-quality-before-refactoring` skill.
- All documentation MUST be aligned before this skill executes.

### ⚠️ Prerequisite Chain Required
- This skill is part of the **code-refactoring-stage** chain:
  1. `task-type-refactoring-analysis` → produces refactoring_suggestion, refactoring_principle
  2. `task-type-improve-code-quality-before-refactoring` → produces code_quality_evaluated
  3. `task-type-code-refactor-v2` → executes refactoring (this skill)

- **If user requests "refactor" directly without prior analysis:**
  → DO NOT execute this skill
  → REDIRECT to `task-type-refactoring-analysis` to start the proper chain

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Code Refactor V2 |
| Category | code-refactoring-stage |
| Next Task Type | null |
| Require Human Review | Yes |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |
| refactoring_scope | (required - from previous task) |
| refactoring_suggestion | (required - from Refactoring Analysis task) |
| refactoring_principle | (required - from Refactoring Analysis task) |
| code_quality_evaluated | (required - from Improve Code Quality task) |

**refactoring_scope Structure:**
```yaml
refactoring_scope:
  files: [<list of file paths>]
  modules: [<list of module names>]
  dependencies: [<identified dependencies>]
  scope_expansion_log: [<log of scope expansions>]
```

**refactoring_suggestion Structure:**
```yaml
refactoring_suggestion:
  summary: "<high-level description of suggested refactoring>"
  goals:
    - goal: "<specific improvement goal>"
      priority: high | medium | low
      rationale: "<why this goal matters>"
      principle: "<SOLID | DRY | KISS | YAGNI | Modular Design | etc.>"
  target_structure: "<description of desired structure after refactoring>"
```

**refactoring_principle Structure:**
```yaml
refactoring_principle:
  primary_principles:
    - principle: <SOLID | DRY | KISS | YAGNI | SoC | Modular Design | etc.>
      rationale: "<why this principle applies>"
      applications:
        - area: "<code area>"
          action: "<specific application>"
  secondary_principles:
    - principle: <name>
      rationale: "<supporting rationale>"
  constraints:
    - constraint: "<what to avoid or preserve>"
      reason: "<why this constraint exists>"
```

**code_quality_evaluated Structure (from Improve Code Quality):**
```yaml
code_quality_evaluated:
  requirements_alignment: { status: aligned, updates_made: [...] }
  specification_alignment: { status: aligned, updates_made: [...] }
  test_coverage: { status: sufficient, line_coverage: XX%, tests_added: N }
  code_alignment:
    status: aligned | needs_attention | critical
    file_size_violations: [<files to split>]
    solid_assessment: { srp, ocp, lsp, isp, dip }
    kiss_assessment: { over_engineering, straightforward_logic, minimal_dependencies, clear_intent }
    modular_design_assessment: { module_cohesion, module_coupling, single_entry_point, folder_structure, reusability, testability }
    code_smells: [<smells to address>]
  overall_quality_score: <1-10>
```

---

## Skill/Task Completion Output Attributes

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: code-refactoring-stage
  status: completed | blocked
  next_task_type: null
  require_human_review: Yes
  auto_proceed: {from input Auto Proceed}
  task_output_links: [<paths to refactored files>]
  
  # Dynamic attributes
  refactoring_summary:
    files_modified: <count>
    files_created: <count>
    files_deleted: <count>
    tests_updated: <count>
    principles_applied:
      - principle: <SOLID | DRY | KISS | YAGNI | SoC | Modular Design>
        application_count: <N>
        areas: [<code areas where applied>]
    goals_achieved:
      - goal: "<from refactoring_suggestion>"
        status: achieved | partially | skipped
        notes: "<any relevant notes>"
    constraints_respected: [<list of constraints verified>]
    
  code_quality_evaluated:
    quality_score_before: <1-10>
    quality_score_after: <1-10>
    
    # Code Alignment Improvements
    code_alignment:
      file_size_violations:
        before: <count>
        after: <count>
        resolved: [<files that were split>]
      solid_assessment:
        before: { srp: status, ocp: status, ... }
        after: { srp: status, ocp: status, ... }
      kiss_assessment:
        before: { over_engineering: status, ... }
        after: { over_engineering: status, ... }
      modular_design_assessment:
        before: { module_cohesion: status, ... }
        after: { module_cohesion: status, ... }
      code_smells:
        before: <count>
        after: <count>
        resolved: [<smells addressed>]
    
    test_coverage:
      before: <XX%>
      after: <XX%>
      status: maintained | improved | degraded
      
    references_updated:
      requirements: [<paths>]
      specifications: [<paths>]
      technical_designs: [<paths>]
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | refactoring_scope provided | Yes |
| 2 | refactoring_suggestion provided | Yes |
| 3 | refactoring_principle provided | Yes |
| 4 | code_quality_evaluated provided (from Improve Code Quality) | Yes |
| 5 | All documentation aligned (requirements, specs) | Yes |
| 6 | Test coverage ≥80% | Yes |
| 7 | All tests passing | Yes |

### ⚠️ Prerequisite Chain Enforcement

**Before executing this skill, verify the refactoring chain was followed:**

```
1. CHECK if refactoring_suggestion AND refactoring_principle exist:
   - These attributes are ONLY produced by task-type-refactoring-analysis
   
2. IF refactoring_suggestion OR refactoring_principle is MISSING:
   → ⛔ STOP execution of this skill
   → LOG: "Missing prerequisite: task-type-refactoring-analysis not executed"
   → REDIRECT: Load and execute `task-type-refactoring-analysis` skill first
   → After completion, chain will auto-proceed through:
     task-type-refactoring-analysis → task-type-improve-code-quality-before-refactoring → task-type-code-refactor-v2

3. IF code_quality_evaluated is MISSING:
   → ⛔ STOP execution of this skill
   → LOG: "Missing prerequisite: task-type-improve-code-quality-before-refactoring not executed"
   → REDIRECT: Load and execute `task-type-improve-code-quality-before-refactoring` skill first

4. ONLY proceed to Execution Flow if ALL prerequisites are present
```

---

## Execution Flow

Execute Code Refactor V2 by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Reflect on Context | Analyze requirements, features, and input suggestions/principles | Context understood |
| 2 | Generate Plan | Propose refactoring plan following suggestions and principles | **Human approves plan** |
| 3 | Execute Refactoring | Apply changes per principles incrementally | All tests pass |
| 4 | Update References | Sync docs with new structure | Docs updated |
| 5 | Validate & Complete | Verify quality improvement against principles | **Human approves** |

**⛔ BLOCKING RULES:**
- Step 1 → 2: BLOCKED if documentation not aligned
- Step 2 → 3: BLOCKED until human approves refactoring plan
- Step 3: BLOCKED if any test fails (must fix or revert)
- Step 4 → 5: BLOCKED if references not updated

---

## Execution Procedure

### Step 1: Reflect on Context

**Action:** Analyze requirements, features, and input suggestions/principles

```
1. FOR EACH file in scope:
   - IDENTIFY associated requirements, features, tech specs
   - BUILD context_map with all relationships

2. REVIEW refactoring_suggestion:
   - EXTRACT goals and priorities
   - NOTE target_structure as end-state vision
   - UNDERSTAND rationale for each goal

3. REVIEW refactoring_principle:
   - EXTRACT primary_principles and their applications
   - NOTE constraints and preservation requirements
   - MAP principles to specific code areas

4. IDENTIFY impacts (docs, tests, downstream code)

5. VALIDATE alignment:
   - Suggestions align with code_quality_evaluated gaps?
   - Principles applicable to identified problem areas?
   - Constraints achievable with current codebase?
```

**Output:** context_map with code relationships and principle-to-code mapping

---

### Step 2: Generate Refactoring Plan

**Action:** Create detailed refactoring plan following suggestions and principles

```
1. ANALYZE current structure (sizes, smells, principle violations)

2. DESIGN target structure per refactoring_suggestion.target_structure:
   FOR EACH primary_principle in refactoring_principle:
     - Apply principle to specific areas as defined in applications
     - SOLID: Extract classes/modules for SRP violations
     - DRY: Plan abstractions for duplications
     - KISS: Plan simplifications
     - YAGNI: Remove unused code
     - SoC: Separate mixed concerns

3. CREATE refactoring_plan with phases:
   FOR EACH goal in refactoring_suggestion.goals (by priority):
     - phase, name, changes (type/from/to/reason/principle_applied), risk, tests_affected
     - ENSURE each change references the principle driving it

4. VALIDATE plan against constraints:
   FOR EACH constraint in refactoring_principle.constraints:
     - VERIFY plan respects constraint
     - IF violation → revise plan

5. CREATE test_plan and doc_plan

6. PRESENT plan to human:
   "Refactoring Plan Summary:
   - Goals: {goals_addressed}
   - Principles Applied: {principle_list}
   - Phases: {phase_count}
   - Constraints Respected: {constraint_list}
   
   [Detailed phase breakdown...]"

7. WAIT for human approval
```

---

### Step 3: Execute Refactoring

**Action:** Apply refactoring plan per principles incrementally with test validation

```
FOR EACH phase:
  1. CREATE checkpoint: git commit -m "checkpoint: before phase {N}"
  
  2. FOR EACH change:
     - Apply change following the principle_applied for this change
     - VERIFY change aligns with constraint requirements
     - Update imports and exports
  
  3. RUN tests immediately after each change
  
  4. IF tests fail:
     - Import error → Fix import
     - Behavior changed → REVERT to checkpoint, revise plan
     - Legitimate update → Update test, document why
  
  5. LOG principle application:
     "Applied {principle} to {area}: {action}"
  
  6. COMMIT: git commit -m "refactor({scope}): {description} [principle: {principle}]"
  
  7. LOG phase completion with principles applied
```

---

### Step 4: Update References

**Action:** Update all documentation to reflect new code structure

```
1. UPDATE technical designs:
   - Update component list, file locations, import paths
   - ADD to Design Change Log with date and summary

2. UPDATE feature specifications (file references, code snippets)

3. UPDATE requirements (implementation notes, file references)

4. COMPILE references_updated with all paths
```

---

### Step 5: Validate and Complete

**Action:** Verify quality improvement against suggestions and principles

```
1. RUN final test suite (all must pass, coverage maintained/improved)

2. VALIDATE against refactoring_suggestion.goals:
   FOR EACH goal:
     - VERIFY goal achieved
     - NOTE if partially achieved or skipped

3. VALIDATE against refactoring_principle:
   FOR EACH primary_principle:
     - VERIFY principle applied in specified areas
     - VERIFY no new violations introduced
   FOR EACH constraint:
     - VERIFY constraint respected

4. CALCULATE quality improvements:
   - Run static analysis (before vs after)
   - Score: readability, maintainability, testability, cohesion, coupling
   - Calculate overall quality_score_before and quality_score_after

5. VERIFY test coverage (if degraded → add tests before completing)

6. COMPILE refactoring_summary:
   - files_modified, files_created, files_deleted
   - tests_updated
   - principles_applied: [<list with application counts>]
   - goals_achieved: [<from refactoring_suggestion>]

7. PRESENT summary to human:
   "Refactoring Complete
   
   Goals Achieved: {goal_list}
   Principles Applied: {principle_list with counts}
   Constraints Respected: {constraint_list}
   
   Quality: {before_score} → {after_score}
   Coverage: {before}% → {after}%"

8. WAIT for human approval

9. CREATE final commit
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | All planned changes executed | Yes |
| 2 | All tests passing | Yes |
| 3 | Test coverage maintained or improved | Yes |
| 4 | Quality score improved | Yes |
| 5 | Technical designs updated | Yes |
| 6 | Feature specs updated (if affected) | Yes |
| 7 | Requirements updated (if affected) | Yes |
| 8 | All changes committed | Yes |
| 9 | Human review approved | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: Extract Module

**When:** File has multiple responsibilities
**Then:**
```
1. Identify cohesive code blocks
2. Create new file per responsibility
3. Move code with tests
4. Update imports everywhere
5. Run tests after each move
```

### Pattern: Apply SOLID Principles

**When:** refactoring_principle includes SOLID in primary_principles
**Then:**
```
1. Review applications defined for SOLID principle
2. S - Split classes with multiple reasons to change
3. O - Extract interfaces for extension points
4. L - Ensure subtypes are substitutable
5. I - Split fat interfaces
6. D - Inject dependencies instead of creating
6. LOG each application for traceability
```

### Pattern: Rollback on Failure

**When:** Tests fail after change
**Then:**
```
1. STOP immediately
2. Analyze failure cause
3. If behavior change: git revert to checkpoint
4. If import issue: fix and retry
5. If legitimate update: update test carefully
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Big bang refactor | Hard to debug | Small incremental changes |
| Skip test runs | Miss regressions | Test after EVERY change |
| Change behavior | Hidden bugs | Structure only, same behavior |
| Ignore failing tests | Technical debt | Fix immediately or revert |
| Skip doc updates | Stale documentation | Always update docs at end |
| Lower coverage | Reduced safety | Maintain or improve coverage |
| Ignore suggestions | Miss goals | Follow refactoring_suggestion goals |
| Violate constraints | Break requirements | Always respect constraints |

---

## Example

See [references/examples.md](references/examples.md) for concrete execution examples.
