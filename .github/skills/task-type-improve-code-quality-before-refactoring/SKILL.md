---
name: task-type-improve-code-quality-before-refactoring
description: Update documentation to reflect current code before refactoring. Use after Refactoring Analysis to sync requirements, features, technical design, and tests with actual code state. Triggers on requests like "improve quality before refactoring", "sync docs with code", "update specs for refactoring".
---

# Task Type: Improve Code Quality Before Refactoring

## Purpose

Ensure documentation accurately reflects current code state before refactoring by:
1. **Sync Requirements** with actual code behavior
2. **Sync Features** with implemented functionality  
3. **Sync Technical Design** with actual architecture
4. **Update Tests** to cover current behavior (reach 80%+)
5. **Output** updated code_quality_evaluated for refactoring phase

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.
- This skill REQUIRES output from `task-type-refactoring-analysis` skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Improve Code Quality Before Refactoring |
| Category | code-refactoring-stage |
| Next Task Type | Code Refactor V2 |
| Require Human Review | Yes |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |
| refactoring_scope | (required - from previous task) |
| code_quality_evaluated | (required - from previous task) |

**refactoring_scope Structure:**
```yaml
refactoring_scope:
  files: [<list of file paths>]
  modules: [<list of module names>]
  dependencies: [<identified dependencies>]
  scope_expansion_log: [<log of scope expansions>]
```

**code_quality_evaluated Structure:**
```yaml
code_quality_evaluated:
  requirements_alignment:
    status: aligned | needs_update | not_found
    gaps: [<list of gaps>]
    related_docs: [<paths>]
    
  specification_alignment:
    status: aligned | needs_update | not_found
    gaps: [<list of gaps>]
    feature_ids: [<FEATURE-XXX>]
    spec_docs: [<paths>]
    
  test_coverage:
    status: sufficient | insufficient | no_tests
    line_coverage: <XX%>
    branch_coverage: <XX%>
    target_percentage: 80
    critical_gaps: [<untested areas>]
    external_api_mocked: true | false
    
  code_alignment:
    status: aligned | needs_attention | critical
    file_size_violations: [<files exceeding 800 lines>]
    files_approaching_threshold: [<files 500-800 lines>]
    solid_assessment: {srp, ocp, lsp, isp, dip}
    kiss_assessment: {over_engineering, straightforward_logic, minimal_dependencies, clear_intent}
    modular_design_assessment: {module_cohesion, module_coupling, single_entry_point, folder_structure, reusability, testability}
    code_smells: [<detected smells>]
    
  overall_quality_score: <1-10>
```

---

## Skill/Task Completion Output Attributes

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: code-refactoring-stage
  status: completed | blocked
  next_task_type: Code Refactor V2
  require_human_review: Yes
  auto_proceed: {from input Auto Proceed}
  task_output_links: [<paths to updated docs>]
  
  # Dynamic attributes - MUST be passed to next task
  refactoring_scope: {passed through unchanged}
  refactoring_suggestion: {passed through unchanged}
  refactoring_principle: {passed through unchanged}
  
  code_quality_evaluated:
    requirements_alignment:
      status: aligned  # Should now be aligned
      gaps: []         # Should be empty
      updates_made: [<list of doc updates>]
      
    specification_alignment:
      status: aligned
      gaps: []
      updates_made: [<list of spec updates>]
      
    test_coverage:
      status: sufficient
      line_coverage: <XX%>  # Should be ≥80
      branch_coverage: <XX%>
      external_api_mocked: true
      tests_added: <count>
      tests_updated: <count>
      
    code_alignment:
      status: {from input - not modified in this phase}
      file_size_violations: {from input}
      solid_assessment: {from input}
      kiss_assessment: {from input}
      modular_design_assessment: {from input}
      code_smells: {from input}
      # NOTE: Code alignment issues are addressed in Code Refactor V2, not here
      
    overall_quality_score: <improved score>
    
    validation_summary:
      docs_created: <count>
      docs_updated: <count>
      tests_added: <count>
      ready_for_refactoring: true | false
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | refactoring_scope provided from analysis | Yes |
| 2 | code_quality_evaluated provided from analysis | Yes |
| 3 | All files in scope accessible | Yes |
| 4 | Write access to documentation folders | Yes |

---

## Execution Flow

Execute Validate Quality Before Refactoring by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Validate Inputs | Verify required inputs from analysis | Inputs valid |
| 2 | Sync Requirements | Update requirement docs to match code | Docs updated |
| 3 | Sync Features | Update feature specs to match code | Specs updated |
| 4 | Sync Tech Design | Update technical designs to match code | Designs updated |
| 5 | Update Tests | Add/fix tests to reach 80% coverage | Coverage ≥80% |
| 6 | Generate Output | Compile updated code_quality_evaluated | **Human approves** |

**⛔ BLOCKING RULES:**
- Step 5 → 6: BLOCKED if test coverage < 80%
- Step 6: BLOCKED if any alignment status ≠ aligned

---

## Execution Procedure

### Step 1: Validate Inputs

**Action:** Verify required inputs from Refactoring Analysis

```
1. CHECK refactoring_scope:
   - files list exists and is non-empty
   - All files exist on filesystem
   
2. CHECK code_quality_evaluated:
   - All 4 alignment sections present
   - overall_quality_score is valid number
   
3. IF any input missing:
   → BLOCK with error: "Missing required input: {input_name}"
   → Return to Refactoring Analysis task
   
4. LOG starting state:
   - Initial quality score
   - Number of gaps per category
   - Current test coverage
```

---

### Step 2: Sync Requirements with Code

**Action:** Update requirement documentation to match actual code behavior

```
IF requirements_alignment.status = "needs_update":
  FOR EACH gap in requirements_alignment.gaps:
    CASE gap.type:
      "undocumented":
        → Document the implemented behavior
        → Add to requirement doc with section: "Discovered Behavior"
        → Note: "Documented from code during refactoring prep"
        
      "unimplemented":
        → Ask human: "Requirement not in code. Options:
           1. Mark as deferred/out-of-scope
           2. Implement before refactoring
           3. Remove from requirements"
        → Apply human's choice
        
      "deviated":
        → Ask human: "Code differs from requirement. Options:
           1. Update requirement to match code (code is correct)
           2. Note as bug to fix during refactoring"
        → Apply human's choice
    
  UPDATE requirements_alignment:
    status: aligned
    gaps: []
    updates_made: [<list of changes>]

ELSE IF requirements_alignment.status = "not_found":
  ASK human: "No requirement docs found. Options:
    1. Create requirement doc from code behavior
    2. Skip requirements (not recommended)
    3. Block until requirements created"
    
  IF human chooses create:
    → Analyze code behavior
    → Generate requirement doc: x-ipe-docs/requirements/{module}-requirements.md
    → Use template from code behavior
```

---

### Step 3: Sync Features with Code

**Action:** Update feature specifications to match implemented functionality

```
IF feature_alignment.status = "needs_update":
  FOR EACH gap in feature_alignment.gaps:
    1. READ feature specification:
       x-ipe-docs/requirements/{feature_id}/specification.md
    
    2. CASE gap.type:
         "missing":
           → Add acceptance criteria for implemented behavior
           → Mark as "Added during refactoring prep"
           
         "extra":
           → Ask human: "Code has feature not in spec:
              {gap.description}
              Options:
              1. Add to specification
              2. Mark for removal during refactoring"
           → Apply choice
           
         "deviated":
           → Update specification to match code
           → Note deviation in change log
    
    3. UPDATE specification file
    
  UPDATE feature_alignment:
    status: aligned
    gaps: []
    updates_made: [<list of spec updates>]

ELSE IF feature_alignment.status = "not_found":
  FOR EACH module in refactoring_scope.modules:
    → Create feature documentation from code
    → Generate FEATURE-XXX folder and specification.md
    → Extract acceptance criteria from code behavior
```

---

### Step 4: Sync Technical Design with Code

**Action:** Update technical design documents to match actual architecture

```
IF technical_spec_alignment.status = "needs_update":
  FOR EACH gap in technical_spec_alignment.gaps:
    1. READ technical design:
       x-ipe-docs/requirements/{feature_id}/technical-design.md
    
    2. CASE gap.type:
         "structure":
           → Update component list to match actual files
           → Update directory structure documentation
           
         "interface":
           → Update interface definitions to match code
           → Add any new public APIs
           
         "data_model":
           → Update data model diagrams/definitions
           → Reflect actual field names and types
           
         "pattern":
           → Document actual patterns used
           → Note deviation from original design
    
    3. ADD to Design Change Log:
       | Date | Phase | Change Summary |
       | {today} | Pre-Refactor Sync | Updated {type} to match implementation |
    
  UPDATE technical_spec_alignment:
    status: aligned
    gaps: []
    updates_made: [<list of design updates>]

ELSE IF technical_spec_alignment.status = "not_found":
  → Create technical design from code analysis
  → Document current architecture as-is
  → This becomes baseline for refactoring changes
```

---

### Step 5: Update Tests to Target Coverage

**Action:** Add and fix tests to reach 80% coverage

```
1. FOR EACH file in test_coverage.critical_gaps:
   a. ANALYZE untested code:
      - Identify function signatures
      - Identify input/output types
      - Identify edge cases
   
   b. GENERATE test cases:
      - Happy path tests
      - Edge case tests  
      - Error handling tests
   
   c. WRITE tests:
      - Follow project test conventions
      - Use existing test patterns
      - Add to appropriate test file

2. RUN new tests:
   - All tests MUST pass (testing existing behavior)
   - IF test fails:
     → Code has a bug → Document for refactoring phase
     → OR test is wrong → Fix test

3. RUN coverage:
   - Check if target (80%) reached
   - IF still below:
     → Add more tests
     → Repeat until ≥80%

4. UPDATE test_coverage:
   status: sufficient
   current_percentage: {new coverage}
   tests_added: {count}
   tests_updated: {count}
```

---

### Step 6: Generate Output

**Action:** Compile updated code_quality_evaluated and request human review

```
1. VERIFY all alignments:
   - requirements_alignment.status = aligned
   - feature_alignment.status = aligned
   - technical_spec_alignment.status = aligned
   - test_coverage.status = sufficient
   
   IF any not aligned:
     → Return to appropriate step
     → Cannot proceed until all aligned

2. CALCULATE new overall_quality_score:
   - All aligned = 10
   - Deduct for any remaining minor issues

3. COMPILE validation_summary:
   validation_summary:
     docs_created: {count}
     docs_updated: {count}
     tests_added: {count}
     ready_for_refactoring: true

4. SAVE validation report:
   - Path: x-ipe-docs/refactoring/validation-{task_id}.md
   - Include all updates made
   - Include new coverage metrics

5. PRESENT to human:
   "Quality Validation Complete
   
   Documentation Sync:
   - Requirements: ✅ Aligned ({X} updates)
   - Features: ✅ Aligned ({X} updates)
   - Tech Design: ✅ Aligned ({X} updates)
   
   Test Coverage: {before}% → {after}%
   - Tests Added: {count}
   - All tests passing: ✅
   
   Ready for Refactoring: ✅
   
   Approve to proceed to Code Refactor V2?"

6. WAIT for human approval
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Requirements synced with code | Yes |
| 2 | Feature specs synced with code | Yes |
| 3 | Technical design synced with code | Yes |
| 4 | Test coverage ≥80% | Yes |
| 5 | All tests passing | Yes |
| 6 | Validation report generated | Yes |
| 7 | Human review approved | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

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

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip documentation sync | Refactoring without context | Always sync docs first |
| Fix bugs during validation | Scope creep | Document bugs, fix in refactor phase |
| Lower coverage target | Risk during refactoring | Keep 80% minimum |
| Delete failing tests | Lose behavior contracts | Fix or document as bug |
| Proceed with gaps | Unknown risks | All alignments must be "aligned" |

---

## Example

See [references/examples.md](references/examples.md) for concrete execution examples.
