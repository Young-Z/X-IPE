---
name: x-ipe-task-based-bug-fix
description: Diagnose and fix bugs in existing code. Use when something is broken, not working as expected, or producing errors. Triggers on requests like "fix bug", "something is broken", "not working".
---

# Task-Based Skill: Bug Fix

## Purpose

Systematically diagnose, fix, and verify bug resolutions by:
1. Understanding and reproducing the reported bug
2. Diagnosing root cause through code analysis
3. Writing a failing test before implementing the minimal fix
4. Verifying the fix with no regressions

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

**Bug Categories Reference:**

| Category | Symptoms | Typical Causes |
|----------|----------|----------------|
| Logic Error | Wrong output | Incorrect conditions |
| Null Reference | Crash/exception | Missing null checks |
| Race Condition | Intermittent failure | Async timing issues |
| Off-by-One | Wrong count | Loop/index errors |
| Resource Leak | Slowdown/crash | Missing cleanup |
| Integration | External fail | API changes |

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Bug Fix"

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null
  require_human_review: yes

  # Required inputs
  auto_proceed: false
  bug_description: "{description of the bug}"
  expected_behavior: "{what should happen}"
  actual_behavior: "{what actually happens}"

  # Context (optional)
  reproduction_steps: "{steps to reproduce, if known}"
  environment_info: "{environment details, if relevant}"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Bug description provided</name>
    <verification>Check that a clear description of the bug exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Expected vs actual behavior documented</name>
    <verification>Both expected and actual behavior are stated</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Steps to reproduce provided</name>
    <verification>Check if reproduction steps are available</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Environment info provided</name>
    <verification>Check if environment details are relevant and available</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Understand | Read bug description, categorize severity | Bug understood |
| 2 | Reproduce | Follow steps to confirm bug occurs | Bug reproduced |
| 3 | Diagnose | Trace root cause, check technical design | Root cause found |
| 4 | Design Fix | Identify fix options, choose minimal fix | Fix approach selected |
| 5 | Write Test | Create failing test that reproduces bug | Test fails |
| 6 | Implement | Write minimum code to fix bug | Test passes |
| 7 | Verify | Confirm bug fixed, all tests pass | DoD validated |

BLOCKING: Step 5 to 6 is blocked until test is written and FAILS.
BLOCKING: Step 6 to 7 is blocked until the new test PASSES.
BLOCKING: If fix changes key interfaces, update technical design FIRST.

---

## Execution Procedure

```xml
<procedure name="bug-fix">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Understand the Bug</name>
    <action>
      1. Read bug description carefully
      2. Clarify if unclear: What was expected? What actually happened? When did it start?
      3. Categorize severity:
         - Critical: System down or data loss
         - High: Feature broken
         - Medium: Partial functionality
         - Low: Minor issue
    </action>
    <output>Bug understood with severity classification</output>
  </step_1>

  <step_2>
    <name>Reproduce the Bug</name>
    <action>
      1. Follow provided reproduction steps exactly, confirm bug occurs
      2. Document exact steps, environment conditions, and error messages
    </action>
    <branch>
      IF: No reproduction steps provided
      THEN: Analyze symptoms, create hypothesis, design test case, attempt to reproduce
      ELSE: Follow provided steps and confirm bug occurs
    </branch>
    <output>Documented reproduction steps with confirmed bug occurrence</output>
  </step_2>

  <step_3>
    <name>Diagnose Root Cause</name>
    <action>
      1. Read related code starting from error location, trace backwards
      2. Check recent changes via git log
      3. If feature-related bug, read technical design at
         x-ipe-docs/requirements/FEATURE-XXX/technical-design.md
      4. Identify root cause: what lines, why it occurs, what triggers it
      5. Document: root cause, affected files, risk assessment, design impact
    </action>
    <constraints>
      - CRITICAL: Distinguish design flaw vs implementation error
    </constraints>
    <output>Root cause analysis with affected files and risk assessment</output>
  </step_3>

  <step_4>
    <name>Design Fix</name>
    <action>
      1. Identify fix options (Option A, Option B, etc.)
      2. Evaluate each: code impact, regression risk, complexity, design compatibility
      3. Choose minimal fix: smallest change, lowest risk, most maintainable
      4. Present to human for approval
    </action>
    <branch>
      IF: Fix requires changes to key components or interfaces
      THEN: UPDATE technical-design.md FIRST, add entry to Design Change Log, then proceed
      ELSE: Proceed directly to implementation
    </branch>
    <constraints>
      - BLOCKING: Do NOT make incompatible changes to key components without updating design first
      - CRITICAL: If fix changes component interfaces, data models, or workflows documented in
        technical design, update the document and add Design Change Log entry before implementing
    </constraints>
    <output>Selected fix approach with human approval</output>
  </step_4>

  <step_5>
    <name>Write Failing Test</name>
    <action>
      1. Locate existing test file in tests/ folder for the affected component
      2. If no test file exists, create one following project test conventions
      3. Write test case that reproduces the bug with descriptive name
      4. Run the test and confirm it FAILS
    </action>
    <constraints>
      - BLOCKING: Test MUST fail before proceeding to Step 6
      - BLOCKING: Do NOT write fix code before test fails
      - CRITICAL: If test passes, revise it - test does not capture the bug
    </constraints>
    <output>Failing test that reproduces the bug</output>
  </step_5>

  <step_6>
    <name>Implement Fix</name>
    <action>
      1. Implement the minimal fix: only change what is necessary, follow code style
      2. Run the new test: it MUST now pass
      3. Run ALL existing tests: all must pass, no regressions allowed
    </action>
    <constraints>
      - BLOCKING: New test must pass after fix
      - BLOCKING: All existing tests must pass
    </constraints>
    <output>Minimal code fix with all tests passing</output>
  </step_6>

  <step_7>
    <name>Verify Fix</name>
    <action>
      1. Follow original reproduction steps, confirm bug is fixed
      2. Run full test suite, perform manual smoke test
      3. Document: what was changed, why it fixes the bug, any side effects
    </action>
    <success_criteria>
      - Bug can no longer be reproduced
      - Full test suite passes
      - Fix is documented
    </success_criteria>
    <output>Verified fix with documentation</output>
  </step_7>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill: null
  require_human_review: yes
  auto_proceed: "{from input auto_proceed}"
  task_output_links:
    - "{path to fixed source file}"
    - "{path to test file}"
  # Dynamic attributes
  bug_severity: "Critical | High | Medium | Low"
  root_cause: "{brief description of root cause}"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Bug can no longer be reproduced</name>
    <verification>Follow original reproduction steps and confirm bug does not occur</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Failing test written before fix</name>
    <verification>Confirm test was committed before fix code, and test fails without fix</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test passes after fix</name>
    <verification>Run the bug-specific test and confirm it passes</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All existing tests pass</name>
    <verification>Run full test suite and confirm zero failures</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Fix documented</name>
    <verification>Check that root cause, fix description, and any side effects are documented</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

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

**When:** Root cause is external or unclear
**Then:**
```
1. Add input validation
2. Add null checks
3. Add error handling
4. Log diagnostic info
5. Document workaround
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Fix without understanding | May fix symptom not cause | Diagnose root cause |
| Large refactor as fix | High regression risk | Minimal targeted fix |
| Skip test for bug | Bug may recur | Always add test |
| Blame external factors | Delays real fix | Take ownership |
| Fix multiple bugs at once | Hard to verify | One bug per fix |

---

## Examples

**Bug Report:** "Login fails with 'invalid token' error"

**Execution:**
```
1. Step 1 - Understand:
   - Expected: User logs in successfully
   - Actual: Error "invalid token" on login
   - Severity: High (feature broken)

2. Step 2 - Reproduce:
   - Go to login page, enter valid credentials, click login
   - Error appears -- Reproduced

3. Step 3 - Diagnose:
   - Error in: authService.validateToken()
   - Root cause: Token expiry check uses > instead of >=
   - Tokens expiring at exact boundary fail

4. Step 4 - Design Fix:
   - Option A: Change > to >= (1 line, low risk) -- Selected
   - Option B: Add grace period (more changes)

5. Step 5 - Write Test:
   - Add test: test_token_at_exact_expiry_boundary()
   - Run test: FAILS (confirms bug)

6. Step 6 - Implement:
   - Fix: token.expiry > now -> token.expiry >= now
   - Run new test: PASSES
   - Run all tests: 156/156 pass

7. Step 7 - Verify:
   - Reproduction steps: Now works
   - Full test suite: 156/156 pass

8. Output Result:
   category: standalone
   next_task_based_skill: null
   require_human_review: yes
   bug_severity: High
   root_cause: "Token expiry boundary check used > instead of >="
   task_output_links:
     - src/auth/tokenValidator.js
     - tests/auth/tokenValidator.test.js
```
