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

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-bug-fix"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A

  # Task type attributes
  category: "standalone"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-acceptance-test"
      condition: "Verify the bug fix with acceptance tests"
    - skill: "x-ipe-task-based-code-refactor"
      condition: "Clean up code after fix"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

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
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
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
| 9.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| 9.2 | Execute Next Action | Load skill, generate plan, execute | Execution started |

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
         - Present unexpected conflicts with clear explanation of what will change
         - Ask: (a) confirm the change is acceptable, OR (b) clarify the original request
         - IF confirmed: proceed to Step 6
         - IF clarified: return to Step 4 (Design Fix) with updated understanding

         Response source (based on interaction_mode):
         IF process_preference.interaction_mode == "dao-represent-human-to-interact":
           → Resolve via x-ipe-dao-end-user-representative
         ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
           → Ask human for decision
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
      1. Auto-detect program_type and tech_stack from affected files (extensions + project config)
      2. GENERATE mini AAA scenario(s) from bug context:
         - Arrange: reproduction preconditions
         - Act: action that triggers the bug
         - Assert: expected correct behavior (what SHOULD happen)
      3. TOOL SKILL ROUTING (config-filtered):
         a. DISCOVER: Scan .github/skills/x-ipe-tool-implementation-*/
         b. READ CONFIG: Read x-ipe-docs/config/tools.json → stages.feature.bug_fix
            - IF section missing/empty → config_active = false (all tools enabled)
            - ELSE → config_active = true (opt-in); force-enable general
         c. FILTER: IF config_active → only ENABLED tools participate
         d. SEMANTIC MATCH: Match tech_stack to enabled tool skill
         e. IF no match → fall back to inline test generation (current behavior)
      4. INVOKE matched tool skill with operation: "fix", AAA scenarios, source/test paths
         - feature_context is optional; tool skill uses synthetic fallback (BUG-{task_id})
      5. VERIFY: test generated by tool skill MUST FAIL (TDD gate)
         - IF test passes → revise AAA scenario, re-invoke tool skill
    </action>
    <constraints>
      - BLOCKING: Test MUST fail before proceeding to Step 7
      - BLOCKING: Do NOT write fix code before test fails
      - CRITICAL: If test passes, revise it — test does not capture the bug
    </constraints>
    <output>Failing test that reproduces the bug (generated by tool skill)</output>
  </step_6>

  <step_7>
    <name>Implement Fix</name>
    <action>
      1. INVOKE same matched tool skill to implement minimal fix using language-specific practices
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
      3. VERIFY tool skill output lint_status == "pass" (if tool skill was used)
      4. Document: what was changed, why it fixes the bug, any side effects
    </action>
    <success_criteria>
      - Bug can no longer be reproduced
      - Full test suite passes
      - lint_status verified (if tool routed)
      - Fix is documented
    </success_criteria>
    <output>Verified fix with documentation</output>
  </step_8>

  <phase_9 name="继续执行（Continue Execute）">
    <step_9_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Invoke x-ipe-dao-end-user-representative with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the context and full output to decide best next action."
          → DAO studies the complete context and decides the best next action
        ELSE (interact-with-human):
          → Present next task suggestion to human and wait for instruction
      </action>
      <constraints>
        - BLOCKING (manual): Human MUST confirm or redirect before proceeding
        - BLOCKING (auto): Proceed after DoD verification; auto-select next task via DAO
      </constraints>
      <output>Next action decided with execution context</output>
    </step_9_1>
    <step_9_2>
      <name>Execute Next Action</name>
      <action>
        Based on the decision from Step 9.1:
        1. Load the target task-based skill's SKILL.md
        2. Generate an execution plan from the skill's Execution Flow table
        3. Start execution from the skill's first phase/step
      </action>
      <constraints>
        - MUST load the skill before executing — do not skip skill loading
        - Execution follows the target skill's procedure, not this skill's
      </constraints>
      <output>Next task execution started</output>
    </step_9_2>
  </phase_9>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-acceptance-test"
      condition: "Verify the bug fix with acceptance tests"
    - skill: "x-ipe-task-based-code-refactor"
      condition: "Clean up code after fix"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
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
