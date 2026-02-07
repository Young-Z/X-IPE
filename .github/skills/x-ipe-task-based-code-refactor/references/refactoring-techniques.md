# Refactoring Techniques Reference

## Input Structure Definitions

### refactoring_scope Structure
```yaml
refactoring_scope:
  files: [<list of file paths>]
  modules: [<list of module names>]
  dependencies: [<identified dependencies>]
  scope_expansion_log: [<log of scope expansions>]
```

### refactoring_suggestion Structure
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

### refactoring_principle Structure
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

### code_quality_evaluated Structure (from Improve Code Quality)
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

## Detailed Execution Procedures

### Step 1: Reflect on Context - Detail

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

### Step 2: Generate Refactoring Plan - Detail

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

### Step 3: Execute Refactoring - Detail

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

### Step 4: Update References - Detail

```
1. UPDATE technical designs:
   - Update component list, file locations, import paths
   - ADD to Design Change Log with date and summary

2. UPDATE feature specifications (file references, code snippets)

3. UPDATE requirements (implementation notes, file references)

4. COMPILE references_updated with all paths
```

### Step 5: Validate and Complete - Detail

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

## Tracing Instrumentation

**Action:** Ensure tracing instrumentation is preserved and applied to new code

```
1. CHECK existing tracing preservation:
   - FOR EACH moved function:
     - VERIFY @x_ipe_tracing decorator still attached
     - VERIFY redact=[] parameters unchanged
   - FOR EACH renamed function:
     - VERIFY decorator remains attached

2. IDENTIFY new code needing tracing:
   - List all NEW public functions created during refactor
   - List all functions that were SPLIT into multiple functions

3. INVOKE x-ipe-tool-tracing-instrumentation skill:
   - Target: All NEW files created during refactoring
   - Target: All files with NEW public functions
   - Example: "Add tracing to src/x_ipe/services/extracted_module.py"

4. REVIEW and APPLY proposed decorators:
   - Verify level assignments match original if function was moved
   - Verify new functions get appropriate levels
   - Apply decorators

5. RE-RUN tests to ensure decorators work:
   pytest tests/ -v

6. UPDATE tracing_preserved and tracing_applied counts in summary
```

**Skip Conditions:**
- Skip if project has no tracing infrastructure
- Skip if refactoring only touched non-code files (docs, config)

### Tracing Preservation Rules

During refactoring, tracing instrumentation MUST be preserved:

1. **When moving functions:**
   - Keep existing `@x_ipe_tracing` decorators intact
   - Preserve `redact=[]` parameters unchanged
   - Update imports if decorator location changes

2. **When splitting modules:**
   - Each new module's public functions retain/get decorators
   - Maintain consistent tracing levels (INFO for public, DEBUG for internal)

3. **When renaming functions:**
   - Decorator stays attached to function
   - Consider if trace logs will now show new name (expected)

4. **When adding new code during refactor:**
   - Apply `@x_ipe_tracing` to new public functions
   - Use `x-ipe-tool-tracing-instrumentation` skill if needed

---

## Safety Check Procedures

### Prerequisite Chain Enforcement

**Before executing this skill, verify the refactoring chain was followed:**

```
1. CHECK if refactoring_suggestion AND refactoring_principle exist:
   - These attributes are ONLY produced by x-ipe-task-based-refactoring-analysis
   
2. IF refactoring_suggestion OR refactoring_principle is MISSING:
   → ⛔ STOP execution of this skill
   → LOG: "Missing prerequisite: x-ipe-task-based-refactoring-analysis not executed"
   → REDIRECT: Load and execute `x-ipe-task-based-refactoring-analysis` skill first
   → After completion, chain will auto-proceed through:
     x-ipe-task-based-refactoring-analysis → x-ipe-task-based-improve-code-quality → x-ipe-task-based-code-refactor

3. IF code_quality_evaluated is MISSING:
   → ⛔ STOP execution of this skill
   → LOG: "Missing prerequisite: x-ipe-task-based-improve-code-quality not executed"
   → REDIRECT: Load and execute `x-ipe-task-based-improve-code-quality` skill first

4. ONLY proceed to Execution Flow if ALL prerequisites are present
```

### Rollback Procedure

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

## Output Structure Definition

```yaml
Output:
  category: code-refactoring-stage
  status: completed | blocked
  next_task_based_skill: null
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
