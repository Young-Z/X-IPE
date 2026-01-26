---
name: task-type-code-refactor
description: Refactor and validate existing code by analyzing quality, ensuring test coverage, and improving structure. Use when code needs cleanup, restructuring, or splitting into smaller files. Follows a safe refactoring workflow with test-first approach.
---

# Task Type: Code Refactor & Validate

## Purpose

Safely refactor and validate existing code through:
1. **Assess** - Analyze code quality, feature alignment, and test coverage gaps
2. **Prepare** - Ensure feature details exist; add missing tests to gain confidence
3. **Execute** - Refactor code into smaller, cleaner files with principles
4. **Update** - Sync technical design with implementation changes

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Code Refactor |
| Category | Standalone |
| Next Task Type | N/A |
| Require Human Review | Yes |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |

---

## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: standalone
  status: completed | blocked
  next_task_type: null
  require_human_review: Yes
  auto_proceed: {from input Auto Proceed}
  task_output_links: [<paths to refactored files>]
  
  # Dynamic attributes
  refactor_scope: <files/modules affected>
  quality_score_before: <1-10>
  quality_score_after: <1-10>
  tests_added: <count>
  files_split: <count>
  principles_applied: [<list of principles>]
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Target code/module identified | Yes |
| 2 | Code compiles/runs without errors | Yes |
| 3 | Feature ID identified (if feature-related) | No |
| 4 | Technical design exists (if feature-related) | No |

---

## Execution Flow

Execute refactoring by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Identify Scope | Determine files/modules to refactor | Scope documented |
| 2 | Analyze Quality | Rate code quality 1-10, find code smells | Quality scored |
| 3 | Check Feature Alignment | Compare code vs spec/design (if feature-related) | Gaps documented |
| 4 | Check Test Coverage | Verify coverage ≥80% | Coverage sufficient |
| 5 | Generate Plan | Select principles, define refactor phases | **Human approves plan** |
| 6 | Add Missing Tests | Write tests to reach ≥80% coverage | All tests pass |
| 7 | Refactor Code | Apply principles, split files | Tests pass after each change |
| 8 | Verify Quality | Re-score quality, compare before/after | Quality improved |
| 9 | Update Technical Designs | Sync docs with new file structure | Docs updated |
| 10 | Complete | Verify DoD, generate output, request review | Human review |

**⛔ BLOCKING RULES:**
- Step 5 → 6: BLOCKED until human approves refactoring plan
- Step 6 → 7: BLOCKED if test coverage < 80%
- Step 9: MUST update all technical designs that reference changed files
- Step 10: MUST verify ALL DoD checkpoints before marking complete

---

## Refactoring Principles by Application Type

See [references/refactoring-principles.md](references/refactoring-principles.md) for detailed principles organized by:
- Web Application (Frontend) - Component isolation, state management
- Web Application (Backend) - Service layer, repository pattern
- CLI Application - Command pattern, config management
- Library/Package - Public API surface, type definitions
- Monolith to Modules - Domain boundaries, shared kernel

---

## Execution Procedure

### Phase 1: Assessment

#### Step 1.1: Identify Scope & Context

**Action:** Determine what code to refactor and gather context

```
1. IDENTIFY target code:
   - Specific file(s) to refactor
   - Module/package boundaries
   - Related dependencies

2. DETERMINE application type:
   - Web Frontend (React, Vue, vanilla JS, etc.)
   - Web Backend (Flask, Express, Django, etc.)
   - CLI Application
   - Library/Package
   - Other (specify)

3. IF feature-related:
   - Locate feature ID
   - Read specification: x-ipe-docs/requirements/FEATURE-XXX/specification.md
   - Read technical design: x-ipe-docs/requirements/FEATURE-XXX/technical-design.md

4. Document scope:
   refactor_scope:
     files: [list of files]
     modules: [list of modules]
     feature_id: FEATURE-XXX | null
```

---

#### Step 1.2: Analyze Code Quality

**Action:** Evaluate current code state

```
1. RUN static analysis (if available):
   - Linter: ruff/eslint/etc.
   - Type checker: mypy/tsc/etc.
   - Complexity: radon/complexity reports

2. MANUAL assessment - Rate 1-10 on each:
   - Readability: Can a new developer understand it?
   - Maintainability: How hard to modify?
   - Testability: Can components be tested in isolation?
   - Cohesion: Does each file have single responsibility?
   - Coupling: How interdependent are modules?
   - DRY: Is there code duplication?

3. CALCULATE quality_score_before:
   - Average of manual assessment scores
   - Note major issues found

4. IDENTIFY code smells:
   - Large files (>300 lines)
   - God classes/modules
   - Deep nesting
   - Long functions (>50 lines)
   - Magic numbers/strings
   - Dead code
   - Circular dependencies
```

---

#### Step 1.3: Analyze Feature Alignment

**Action:** Check if code matches feature requirements and design

```
IF feature_id exists:
  1. COMPARE implementation vs specification:
     - Are all acceptance criteria implemented?
     - Any missing functionality?
     - Any extra functionality not in spec?
  
  2. COMPARE implementation vs technical design:
     - Does code follow designed architecture?
     - Are interfaces as designed?
     - Are data models correct?
  
  3. DOCUMENT gaps:
     feature_gaps:
       missing_from_code: [list]
       extra_in_code: [list]
       design_deviations: [list]

ELSE:
  → Note: No feature context, proceeding with code-only analysis
```

---

#### Step 1.4: Analyze Test Coverage

**Action:** Evaluate existing test coverage

```
1. RUN coverage report:
   - pytest --cov=src tests/ (Python)
   - npm test -- --coverage (Node.js)
   - go test -cover ./... (Go)

2. IDENTIFY coverage gaps:
   - Files with <80% coverage
   - Untested functions/methods
   - Missing edge case tests
   - Missing integration tests

3. DOCUMENT coverage state:
   coverage_before:
     overall: XX%
     target_files:
       - file1.py: XX%
       - file2.py: XX%
     critical_gaps: [list of untested areas]

4. DETERMINE if coverage is sufficient for safe refactoring:
   - ≥80% on target files: ✅ Safe to refactor
   - <80% on target files: ⚠️ Need more tests first
```

---

#### Step 1.5: Generate Refactoring Plan

**Action:** Create prioritized refactoring plan based on assessment

```
1. SELECT applicable principles from application type section

2. PRIORITIZE refactoring targets:
   Priority 1: Code that blocks other improvements
   Priority 2: High-impact, low-risk changes
   Priority 3: Medium complexity improvements
   Priority 4: Nice-to-have cleanups

3. CREATE refactoring plan:
   refactoring_plan:
     principles: [selected principles]
     phases:
       - phase: 1
         description: <what to do>
         files_affected: [list]
         risk: low | medium | high
         estimated_effort: <time>
       - phase: 2
         ...

4. ESTIMATE quality_score_after (target)
```

---

### Phase 2: Preparation

#### Step 2.1: Verify Feature Details (If Feature-Related)

**Action:** Ensure feature documentation is complete

```
IF feature_gaps.missing_from_code is NOT empty:
  ⚠️ STOP - Notify human:
  "Feature gaps detected. Missing implementations:
   - [list gaps]
   
   Options:
   1. Update specification to remove these requirements
   2. Implement missing functionality first
   3. Proceed with refactoring existing code only
   
   Please confirm how to proceed."

  WAIT for human response

  IF human chooses to update spec:
    → Update x-ipe-docs/requirements/FEATURE-XXX/specification.md
    → Remove or mark deferred the missing requirements
  
  IF human chooses to implement:
    → STOP this task
    → Create Code Implementation task for missing items
    → Resume refactoring after implementation complete

IF feature_gaps.design_deviations is NOT empty:
  ⚠️ NOTIFY human:
  "Code deviates from technical design:
   - [list deviations]
   
   These will be addressed in the design update at the end.
   Proceeding with refactoring."
```

---

#### Step 2.2: Add Missing Tests

**Action:** Bring test coverage to safe level before refactoring

```
IF coverage on target files < 80%:
  1. FOR EACH coverage gap:
     a. WRITE unit test for the function/method
     b. Cover happy path
     c. Cover edge cases
     d. Cover error cases
  
  2. RUN new tests:
     - All tests MUST PASS (testing existing behavior)
     - If test fails, either:
       - Fix the test (if test is wrong)
       - Document as bug (if code is wrong)
  
  3. RUN coverage again:
     - Target: ≥80% on files to refactor
     - If still below, add more tests
  
  4. Document:
     tests_added: X
     coverage_after_prep: XX%

⚠️ CRITICAL: Do NOT proceed to refactoring until:
   - Coverage ≥80% on target files
   - All existing tests pass
   - All new tests pass
```

---

### Phase 3: Execution

#### Step 3.1: Refactor Incrementally

**Action:** Apply refactoring plan, testing after each change

```
FOR EACH phase in refactoring_plan:
  1. BACKUP current state (git commit):
     git add -A
     git commit -m "checkpoint: before refactor phase X"
  
  2. APPLY refactoring principle:
     - Make ONE logical change at a time
     - Follow the principle guidelines
     - Keep changes minimal and focused
  
  3. RUN all tests immediately:
     - All tests MUST pass
     - If tests fail:
       a. Check if test needs update (behavior unchanged, structure changed)
       b. If behavior unchanged, update test carefully
       c. If behavior changed unexpectedly, REVERT and investigate
  
  4. COMMIT successful change:
     git add -A
     git commit -m "refactor: [principle applied] - [brief description]"

  5. REPEAT until phase complete

DO NOT:
  - Make multiple unrelated changes at once
  - Skip test runs between changes
  - Change behavior (only structure)
  - Delete tests without replacement
```

---

#### Step 3.2: Split Large Files

**Action:** Break down files following principles

```
1. IDENTIFY split candidates:
   - Files >300 lines
   - Files with multiple classes/modules
   - Files with mixed concerns

2. FOR EACH file to split:
   a. IDENTIFY logical boundaries:
      - By class/component
      - By domain concept
      - By layer (data/logic/presentation)
   
   b. CREATE new files:
      - Name clearly by responsibility
      - Move related code together
      - Update imports in all consumers
   
   c. MAINTAIN backward compatibility:
      - Keep original file as re-export hub (optional)
      - OR update all import statements
   
   d. RUN tests after each split:
      - All tests MUST pass
      - Update test imports if needed

3. Document:
   files_split: X
   new_structure:
     - original: src/big_file.py
       split_into:
         - src/models/user.py
         - src/services/user_service.py
         - src/utils/validators.py
```

---

#### Step 3.3: Update Tests (If Needed)

**Action:** Carefully update tests to match new structure

```
WHEN updating tests:
  1. PRESERVE test behavior:
     - Same assertions
     - Same test scenarios
     - Same edge cases covered
  
  2. UPDATE only:
     - Import paths
     - Mock targets (if class moved)
     - Setup/teardown (if structure changed)
  
  3. VERIFY equivalence:
     - Run test, should pass
     - If behavior test fails, structure change broke something
     - REVERT and investigate

⚠️ WARNING:
  - DO NOT delete tests without equivalent replacement
  - DO NOT change assertion values
  - DO NOT reduce test coverage
```

---

### Phase 4: Finalization

#### Step 4.1: Verify Quality Improvement

**Action:** Re-assess code quality after refactoring

```
1. RUN static analysis again:
   - Compare linter warnings before/after
   - Compare complexity metrics before/after

2. RE-ASSESS manual scores:
   - Readability: improved?
   - Maintainability: improved?
   - Testability: improved?
   - Cohesion: improved?
   - Coupling: reduced?
   - DRY: improved?

3. CALCULATE quality_score_after:
   - Should be higher than quality_score_before
   - If not, review what went wrong

4. RUN full test suite:
   - All tests MUST pass
   - Coverage should be maintained or improved
```

---

#### Step 4.2: Update Technical Design

**Action:** Sync documentation with new code structure

```
IF feature_id exists AND technical-design.md exists:
  1. UPDATE Part 1 (Agent-Facing Summary):
     - Update component list
     - Update file locations
     - Update any changed interfaces
  
  2. UPDATE Part 2 (Implementation Guide):
     - Update data model locations
     - Update import paths in examples
     - Update architecture diagram (if present)
  
  3. ADD Design Change Log entry:
     | Date | Phase | Change Summary |
     |------|-------|----------------|
     | {today} | Code Refactor | Refactored for [principles]. Split X files into Y. Updated [components]. No behavior changes. ~100 words |

ELSE:
  → Note: No technical design to update
  → Consider creating one for future maintenance
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Code quality assessed | Yes |
| 2 | Feature gaps identified (if applicable) | Yes |
| 3 | Test coverage ≥80% before refactoring | Yes |
| 4 | All tests pass after refactoring | Yes |
| 5 | No behavior changes (unless documented) | Yes |
| 6 | Code structure improved | Yes |
| 7 | Technical design updated (if exists) | Yes |
| 8 | Human review requested | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: Safe Refactor

**When:** Code has sufficient test coverage (≥80%)
**Then:**
```
1. Run tests to confirm baseline
2. Make incremental changes
3. Run tests after each change
4. Commit working states
```

### Pattern: Low Coverage

**When:** Test coverage < 80%
**Then:**
```
1. STOP refactoring
2. Add tests for uncovered code
3. Reach 80% coverage
4. Resume refactoring
```

### Pattern: Feature-Related Refactor

**When:** Code is part of documented feature
**Then:**
```
1. Read feature specification
2. Read technical design
3. Ensure refactor aligns with design
4. Update technical design if needed
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Refactor without tests | High regression risk | Add tests first, get ≥80% coverage |
| Big bang refactor | Hard to debug failures | Small incremental changes |
| Change behavior during refactor | Hidden bugs | Structure-only changes |
| Delete tests | Lose coverage | Update tests, keep assertions |
| Skip design update | Docs become stale | Always sync documentation |
| Refactor everything | Scope creep | Focus on target scope only |
| Ignore failing tests | Technical debt | Fix or investigate immediately |

---

## Example

See [references/examples.md](references/examples.md) for detailed execution examples including:
- Large file refactoring (850 lines → 3 modules)
- Low coverage blocking scenario
- Feature-related refactoring with design updates

---

## Notes

- Always add tests BEFORE refactoring (safety net)
- Make small, incremental changes
- Run tests after EVERY change
- Structure changes only - no behavior changes
- Update documentation at the end
- Human review required - refactoring can introduce subtle bugs
- When in doubt, add more tests
