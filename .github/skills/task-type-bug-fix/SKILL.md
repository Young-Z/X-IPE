---
name: task-type-bug-fix
description: Diagnose and fix bugs in existing code. Use when something is broken, not working as expected, or producing errors.
---

# Task Type: Bug Fix

## Purpose

Systematically diagnose, fix, and verify bug resolutions. Focus on minimal, targeted fixes that don't introduce regressions.

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Bug Fix |
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
  task_output_links: [<paths to fixed files>]
  # Dynamic attributes (skill-specific)
  bug_severity: Critical | High | Medium | Low
  root_cause: <brief description>
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Bug description provided | Yes |
| 2 | Steps to reproduce (if known) | No |
| 3 | Expected vs actual behavior | Yes |
| 4 | Environment info (if relevant) | No |

---

## Execution Flow

Execute Bug Fix by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Understand | Read bug description, categorize severity | Bug understood |
| 2 | Reproduce | Follow steps to confirm bug occurs | Bug reproduced |
| 3 | Diagnose | Trace root cause, check technical design | Root cause found |
| 4 | Design Fix | Identify fix options, choose minimal fix | Fix approach selected |
| 5 | Write Test | Create failing test that reproduces bug | Test fails |
| 6 | Implement | Write minimum code to fix bug | Test passes |
| 7 | Verify | Confirm bug fixed, all tests pass | Verification complete |

**⛔ BLOCKING RULES:**
- Step 5 → 6: BLOCKED until test is written and FAILS
- Step 6 → 7: BLOCKED until the new test PASSES
- If fix changes key interfaces: MUST update technical design FIRST

---

## Execution Procedure

### Step 1: Understand the Bug

```
1. Read bug description carefully
2. Clarify if unclear:
   - What was expected?
   - What actually happened?
   - When did it start?
   - Can it be reproduced?
3. Categorize severity:
   - Critical: System down/data loss
   - High: Feature broken
   - Medium: Partial functionality
   - Low: Minor issue
```

### Step 2: Reproduce the Bug

```
1. IF reproduction steps provided:
   - Follow steps exactly
   - Confirm bug occurs
   
2. IF no reproduction steps:
   - Analyze symptoms
   - Create hypothesis
   - Design test case
   - Attempt to reproduce

3. Document:
   - Exact steps to reproduce
   - Environment conditions
   - Error messages/logs
```

### Step 3: Diagnose Root Cause

```
1. Read related code:
   - Start from error location
   - Trace backwards
   - Check recent changes (git log)

2. READ Technical Design (if feature-related bug):
   - Check x-ipe-docs/requirements/FEATURE-XXX/technical-design.md
   - Verify implementation matches design
   - Check if bug is due to design flaw vs implementation error

3. Identify root cause:
   - What line(s) cause the issue?
   - Why does the bug occur?
   - What conditions trigger it?
   - Is this a design issue or implementation issue?

4. Document diagnosis:
   - Root cause: <explanation>
   - Affected files: <list>
   - Risk assessment: <impact of fix>
   - Design impact: <does fix require design update?>
```

### Step 4: Design Fix

```
1. Identify fix options:
   - Option A: <description>
   - Option B: <description>

2. Evaluate each:
   - Code impact (how many files)
   - Risk of regression
   - Complexity
   - Design compatibility (does it align with technical design?)

3. Choose minimal fix:
   - Smallest change
   - Lowest risk
   - Most maintainable

4. IF fix requires changes to key components or interfaces:
   - UPDATE technical-design.md FIRST:
     - Modify affected sections
     - Add entry to Design Change Log:
       | Date | Phase | Change Summary |
       |------|-------|----------------|
       | {today} | Bug Fix | {Bug description, what changed in design, impact ~100 words} |
   - THEN proceed with implementation

5. Present to human for approval
```

**⚠️ STRICT REQUIREMENT:**
- If fix changes component interfaces, data models, or workflows documented in technical design:
  - UPDATE the technical design document BEFORE implementing the fix
  - Add entry to Design Change Log
- Do NOT make incompatible changes to key components without updating design first

### Step 5: Write Failing Test FIRST (⚠️ MANDATORY)

**This step MUST be completed before writing any fix code.**

```
1. LOCATE existing test file:
   - Check tests/ folder for related test file
   - Check if component already has test coverage
   
2. IF no test file exists for the affected component:
   - CREATE test file following project test conventions
   - Add basic imports and test class/describe block
   
3. WRITE test case that reproduces the bug:
   - Test name should describe the bug (e.g., test_terminal_survives_idle_period)
   - Test should exercise the exact conditions that trigger the bug
   - Include assertions for expected (correct) behavior
   
4. RUN the test:
   - ⚠️ TEST MUST FAIL before proceeding
   - If test passes, your test doesn't capture the bug - revise it
   - Document the failure output

5. ONLY after test fails, proceed to Step 6
```

**⚠️ NO EXCEPTIONS:**
- Do NOT skip this step
- Do NOT write fix code before test fails
- Do NOT proceed if test passes (test is wrong)

### Step 6: Implement Fix

```
1. Implement the minimal fix:
   - Only change what's necessary
   - Follow code style
   - Add comments if complex

2. Run the new test:
   - ⚠️ TEST MUST NOW PASS
   - If test still fails, fix is incomplete

3. Run ALL existing tests:
   - All tests must pass
   - No regressions allowed
```

### Step 7: Verify Fix

```
1. Verify original bug:
   - Follow reproduction steps
   - Confirm bug is fixed

2. Verify no regressions:
   - Run full test suite
   - Manual smoke test

3. Document fix:
   - What was changed
   - Why it fixes the bug
   - Any side effects
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Bug can no longer be reproduced | Yes |
| 2 | **Failing test written BEFORE fix** | Yes |
| 3 | Test now passes after fix | Yes |
| 4 | All existing tests pass | Yes |
| 5 | Fix documented | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: Test-First Bug Fix

**When:** Bug is clearly reproducible
**Then:**
```
1. Write test that reproduces bug
2. Verify test fails
3. Fix code
4. Verify test passes
5. Verify no regressions
```

### Pattern: Binary Search Diagnosis

**When:** Bug source is unclear
**Then:**
```
1. Find last known working state (git bisect)
2. Find first broken state
3. Narrow down to specific commit
4. Analyze changes in that commit
```

### Pattern: Defensive Fix

**When:** Root cause is external/unclear
**Then:**
```
1. Add input validation
2. Add null checks
3. Add error handling
4. Log diagnostic info
5. Document workaround
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Fix without understanding | May fix symptom not cause | Diagnose root cause |
| Large refactor as fix | High regression risk | Minimal targeted fix |
| Skip test for bug | Bug may recur | Always add test |
| Blame external factors | Delays real fix | Take ownership |
| Fix multiple bugs at once | Hard to verify | One bug per fix |

---

## Bug Categories

| Category | Symptoms | Typical Causes |
|----------|----------|----------------|
| Logic Error | Wrong output | Incorrect conditions |
| Null Reference | Crash/exception | Missing null checks |
| Race Condition | Intermittent failure | Async timing issues |
| Off-by-One | Wrong count | Loop/index errors |
| Resource Leak | Slowdown/crash | Missing cleanup |
| Integration | External fail | API changes |

---

## Example

**Bug Report:** "Login fails with 'invalid token' error"

**Execution:**

```
1. Execute Task Flow from task-execution-guideline skill

2. Step 1 - Understand:
   - Expected: User logs in successfully
   - Actual: Error "invalid token" on login
   - Severity: High (feature broken)

3. Step 2 - Reproduce:
   1. Go to login page
   2. Enter valid credentials
   3. Click login
   4. Error appears
   ✅ Reproduced

4. Step 3 - Diagnose:
   - Error in: authService.validateToken()
   - Root cause: Token expiry check uses > instead of >=
   - Tokens expiring at exact boundary fail

5. Step 4 - Design Fix:
   - Option A: Change > to >= (1 line, low risk) ✅
   - Option B: Add grace period (more changes)
   - Recommend: Option A

6. Step 5 - Implement:
   - Add test: test_token_at_exact_expiry_boundary()
   - Fix: token.expiry > now → token.expiry >= now
   - Run tests: All pass

7. Step 6 - Verify:
   - Reproduction steps: ✅ Now works
   - Full test suite: ✅ 156/156 pass

8. Return Task Completion Output:
   category: Standalone
   next_task_type: N/A
   require_human_review: Yes
   task_output_links:
     - src/auth/tokenValidator.js
     - tests/auth/tokenValidator.test.js

9. Resume Task Flow from task-execution-guideline skill
```
