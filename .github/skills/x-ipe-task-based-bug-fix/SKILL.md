---
name: x-ipe-task-based-bug-fix
description: Diagnose and fix bugs in existing code. Use when something is broken, not working as expected, or producing errors. Triggers on requests like "fix bug", "something is broken", "not working".
---

# Task-Based Skill: Bug Fix

## Purpose

Systematically diagnose, fix, and verify bug resolutions by:
1. Understanding and reproducing the reported bug
2. Diagnosing root cause through code analysis
3. Analyzing proposed fix for conflicts with existing logic
4. Writing a failing test before implementing the minimal fix
5. Verifying the fix with no regressions

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

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"

  # Required inputs
  bug_description: "{description of the bug}"
  expected_behavior: "{what should happen}"
  actual_behavior: "{what actually happens}"

  # Context (optional)
  reproduction_steps: "{steps to reproduce, if known}"
  environment_info: "{environment details, if relevant}"

  # Tech context (optional — auto-detected from affected files if not provided)
  program_type: "frontend | backend | fullstack | cli | library | skills | mcp | ..."  # non-exhaustive
  tech_stack: []  # e.g. ["Python/Flask", "JavaScript/Vanilla"]
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="bug_description" source="from human input" />
  <field name="expected_behavior" source="from human input" />
  <field name="actual_behavior" source="from human input" />
  <field name="reproduction_steps" source="from human input or 'N/A'" />
  <field name="program_type" source="auto-detect from affected files if not provided (check file extensions: .py→backend, .js/.ts/.css/.html→frontend)" />
  <field name="tech_stack" source="auto-detect from project config files (pyproject.toml, package.json) if not provided" />
</input_init>
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
| 5 | Conflict Analysis | Detect conflicts with existing logic, validate against user request | Conflicts resolved |
| 6 | Write Test | Create failing test that reproduces bug | Test fails |
| 7 | Implement | Write minimum code to fix bug | Test passes |
| 8 | Verify | Confirm bug fixed, all tests pass | DoD validated |

BLOCKING: Step 5 must complete before Step 6 — do NOT write tests with unresolved conflicts.
BLOCKING: Step 6 to 7 is blocked until test is written and FAILS.
BLOCKING: Step 7 to 8 is blocked until the new test PASSES.
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
      1. IF reproduction steps provided: follow them exactly, confirm bug occurs
         ELSE: analyze symptoms, create hypothesis, design test case, attempt to reproduce
      2. Document exact steps, environment conditions, and error messages
    </action>
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
      4. IF fix requires changes to key components or interfaces:
         UPDATE technical-design.md FIRST, add entry to Design Change Log
    </action>
    <constraints>
      - BLOCKING: Do NOT make incompatible changes to key components without updating design first
      - CRITICAL: If fix changes component interfaces, data models, or workflows documented in
        technical design, update the document and add Design Change Log entry before implementing
    </constraints>
    <output>Selected fix approach</output>
  </step_4>

  <step_5>
    <name>Conflict Analysis</name>
    <action>
      1. Spawn sub-agent (Conflict Detector) to analyze the proposed fix against existing logic:
         - Read the affected files and their callers/dependents
         - Identify behavioral changes: existing functionality that will behave differently after fix
         - Identify interface changes: public APIs, data models, or contracts affected
         - Identify assumption changes: implicit assumptions in related code the fix may violate
         - Output: list of conflicts with description and affected code locations (empty if none)
      2. IF no conflicts found: proceed to Step 6
      3. IF conflicts found: spawn sub-agent (Conflict Validator) to check each conflict:
         - Compare each conflict against the user's original bug_description and expected_behavior
         - Classify each conflict as:
           - "expected": the user's request explicitly or implicitly requires this behavioral change
           - "unexpected": the change goes beyond what the user requested
         - Output: classified conflict list
      4. IF all conflicts are "expected": proceed to Step 6
      5. IF any conflicts are "unexpected":
         - Present unexpected conflicts to user with clear explanation of what will change
         - Ask user to either: (a) confirm the change is acceptable, OR (b) clarify the original request
         - IF user confirms: proceed to Step 6
         - IF user clarifies: return to Step 4 (Design Fix) with updated understanding
    </action>
    <constraints>
      - BLOCKING: Do NOT proceed to Step 6 if unexpected conflicts are unresolved
      - CRITICAL: Conflict Detector must examine actual codebase (callers, dependents), not just the fix in isolation
      - CRITICAL: Conflict Validator must compare against user's ORIGINAL bug request, not the fix design
    </constraints>
    <output>Validated fix approach with all conflicts resolved or confirmed</output>
  </step_5>

  <step_6>
    <name>Write Failing Test</name>
    <action>
      1. Determine test type from program_type/tech_stack and affected file:
         - Backend bug (Python/server code) → pytest test
         - Frontend bug (JS/CSS file) → JS test using Vitest/Jest + jsdom (NOT string matching in pytest)
         - Fullstack bug → test both layers: pytest for backend, Vitest for frontend
         - If program_type not provided, auto-detect from affected file extensions
         - CRITICAL: For JS logic bugs, use a proper JS test runner. If not configured, set it up.
      2. Locate existing test file in tests/ folder for the affected component
      3. If no test file exists, create one following project test conventions
      4. Write test case that reproduces the bug with descriptive name
      5. Run the test and confirm it FAILS
    </action>
    <constraints>
      - BLOCKING: Test MUST fail before proceeding to Step 7
      - BLOCKING: Do NOT write fix code before test fails
      - CRITICAL: If test passes, revise it - test does not capture the bug
      - CRITICAL: For frontend bugs, ensure test covers the JS/CSS behavior, not just backend
    </constraints>
    <output>Failing test that reproduces the bug</output>
  </step_6>

  <step_7>
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
  </step_7>

  <step_8>
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
  </step_8>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill: null
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "{path to fixed source file}"
    - "{path to test file}"
  # Dynamic attributes
  bug_severity: "Critical | High | Medium | Low"
  root_cause: "{brief description of root cause}"
  conflicts_found: []  # list of conflicts identified, empty if none
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
    <name>Conflict analysis completed</name>
    <verification>Confirm conflicts were checked and all unexpected conflicts resolved with user</verification>
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

### Pattern: Conflict-Aware Fix

**When:** Fix changes behavior that other code depends on
**Then:**
```
1. Design fix approach
2. Detect conflicts with existing logic (sub-agent)
3. Validate conflicts against user's original request (sub-agent)
4. If unexpected conflicts: ask user to confirm or clarify
5. Only then proceed to write test and implement
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
| Skip conflict analysis | May break existing behavior silently | Always check for conflicts before implementing |
| Fix multiple bugs at once | Hard to verify | One bug per fix |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-bug-fix/references/examples.md) for concrete execution examples.
