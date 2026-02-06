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
- Learn `task-execution-guideline` skill first before executing this skill.
- This skill REQUIRES output from `task-type-improve-code-quality-before-refactoring` skill.

### ⚠️ Prerequisite Chain Required
This skill is part of the **code-refactoring-stage** chain:
1. `task-type-refactoring-analysis` → produces refactoring_suggestion, refactoring_principle
2. `task-type-improve-code-quality-before-refactoring` → produces code_quality_evaluated
3. `task-type-code-refactor-v2` → executes refactoring (this skill)

**If user requests "refactor" directly without prior analysis:**
→ REDIRECT to `task-type-refactoring-analysis` to start the proper chain

---

## Task Type Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Code Refactor V2 |
| Category | code-refactoring-stage |
| Next Task Type | null |
| Require Human Review | Yes |

### Required Input Attributes

| Attribute | Source |
|-----------|--------|
| Auto Proceed | False (default) |
| refactoring_scope | previous task |
| refactoring_suggestion | Refactoring Analysis task |
| refactoring_principle | Refactoring Analysis task |
| code_quality_evaluated | Improve Code Quality task |

> **📚 Input/Output Structure Definitions:** See [references/refactoring-techniques.md](references/refactoring-techniques.md#input-structure-definitions)

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | refactoring_scope provided | Yes |
| 2 | refactoring_suggestion provided | Yes |
| 3 | refactoring_principle provided | Yes |
| 4 | code_quality_evaluated provided | Yes |
| 5 | All documentation aligned | Yes |
| 6 | Test coverage ≥80% | Yes |
| 7 | All tests passing | Yes |

### Prerequisite Chain Enforcement

```
1. IF refactoring_suggestion OR refactoring_principle MISSING:
   → ⛔ STOP → REDIRECT to `task-type-refactoring-analysis`

2. IF code_quality_evaluated MISSING:
   → ⛔ STOP → REDIRECT to `task-type-improve-code-quality-before-refactoring`

3. ONLY proceed if ALL prerequisites present
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Reflect on Context | Analyze requirements, features, suggestions/principles | Context understood |
| 2 | Generate Plan | Propose refactoring plan | **Human approves** |
| 3 | Execute Refactoring | Apply changes incrementally | All tests pass |
| 4 | Update References | Sync docs with new structure | Docs updated |
| 5 | Validate & Complete | Verify quality improvement | **Human approves** |
| 6 | Apply Tracing | Preserve/add tracing decorators | Tests pass |

**⛔ BLOCKING RULES:**
- Step 2→3: BLOCKED until human approves plan
- Step 3: BLOCKED if any test fails (must fix or revert)
- Step 4→5: BLOCKED if references not updated

---

## Execution Procedure

### Step 1: Reflect on Context

1. FOR EACH file in scope → BUILD context_map with requirements, features, tech specs
2. REVIEW refactoring_suggestion → EXTRACT goals, priorities, target_structure
3. REVIEW refactoring_principle → MAP principles to code areas, note constraints
4. IDENTIFY impacts (docs, tests, downstream code)
5. VALIDATE alignment with code_quality_evaluated gaps

**Output:** context_map with code relationships and principle-to-code mapping

---

### Step 2: Generate Refactoring Plan

1. ANALYZE current structure (sizes, smells, violations)
2. DESIGN target structure applying principles:
   - SOLID: Extract classes/modules for SRP violations
   - DRY: Plan abstractions | KISS: Simplifications | YAGNI: Remove unused
3. CREATE refactoring_plan with phases (by goal priority)
4. VALIDATE plan against constraints
5. PRESENT plan → WAIT for human approval

---

### Step 3: Execute Refactoring

```
FOR EACH phase:
  1. CREATE checkpoint: git commit -m "checkpoint: before phase {N}"
  2. Apply changes following principle_applied, update imports
  3. RUN tests after each change
  4. IF tests fail: Fix import | REVERT if behavior changed | Update test if legitimate
  5. COMMIT: git commit -m "refactor({scope}): {desc} [principle: {p}]"
```

---

### Step 4: Update References

1. UPDATE technical designs (component list, paths, Design Change Log)
2. UPDATE feature specifications (file references)
3. UPDATE requirements (implementation notes)
4. COMPILE references_updated list

---

### Step 5: Validate and Complete

1. RUN final test suite (coverage maintained/improved)
2. VALIDATE goals achieved from refactoring_suggestion
3. VALIDATE principles applied, constraints respected
4. CALCULATE quality improvements (before/after scores)
5. PRESENT summary → WAIT for human approval
6. CREATE final commit

---

### Step 6: Apply Tracing

> **📚 Detailed Procedure:** See [references/refactoring-techniques.md](references/refactoring-techniques.md#tracing-instrumentation)

1. CHECK tracing preserved on moved/renamed functions
2. IDENTIFY new code needing tracing
3. INVOKE `tool-tracing-instrumentation` skill for new files/functions
4. RE-RUN tests → UPDATE tracing counts in summary

**Skip if:** No tracing infrastructure or only non-code files touched

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
| 10 | Existing tracing preserved | Yes |
| 11 | New/moved code has tracing decorators | Yes |

### Tracing Preservation Rules

| Scenario | Action |
|----------|--------|
| Moving functions | Keep `@x_ipe_tracing` decorators, preserve `redact=[]` |
| Splitting modules | Each new module's public functions get decorators |
| Renaming functions | Decorator stays attached |
| Adding new code | Apply `@x_ipe_tracing` via `tool-tracing-instrumentation` |

---

## Output Attributes

```yaml
Output:
  category: code-refactoring-stage
  status: completed | blocked
  next_task_type: null
  require_human_review: Yes
  task_output_links: [<paths to refactored files>]
  
  refactoring_summary:
    files_modified: <count>
    files_created: <count>
    files_deleted: <count>
    principles_applied: [{ principle, application_count, areas }]
    goals_achieved: [{ goal, status, notes }]
    
  code_quality_evaluated:
    quality_score_before: <1-10>
    quality_score_after: <1-10>
    test_coverage: { before, after, status }
    references_updated: { requirements, specifications, technical_designs }
```

> **📚 Full Output Structure:** See [references/refactoring-techniques.md](references/refactoring-techniques.md#output-structure-definition)

---

## Patterns

### Extract Module
**When:** File has multiple responsibilities
**Then:** Identify cohesive blocks → Create new file per responsibility → Move with tests → Update imports → Test after each move

### Apply SOLID Principles
**When:** refactoring_principle includes SOLID
**Then:** S-Split classes → O-Extract interfaces → L-Ensure substitutability → I-Split fat interfaces → D-Inject dependencies

### Rollback on Failure
**When:** Tests fail after change
**Then:** STOP → Analyze cause → Revert if behavior changed → Fix if import issue → Update test if legitimate

---

## Anti-Patterns

| Anti-Pattern | Do Instead |
|--------------|------------|
| Big bang refactor | Small incremental changes |
| Skip test runs | Test after EVERY change |
| Change behavior | Structure only, same behavior |
| Ignore failing tests | Fix immediately or revert |
| Skip doc updates | Always update docs at end |
| Ignore suggestions | Follow refactoring_suggestion goals |
| Violate constraints | Always respect constraints |

---

## References

- [Refactoring Techniques](references/refactoring-techniques.md) - Detailed procedures, input/output structures, tracing rules
- [Examples](references/examples.md) - Concrete execution examples
