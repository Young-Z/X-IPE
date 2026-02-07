---
name: x-ipe-task-based-human-playground
description: Create interactive examples for human validation. Use when code is implemented and ready for human testing. Triggers on requests like "create playground", "human testing", "interactive demo".
---

# Task-Based Skill: Human Playground

## Purpose

Execute **Human Playground** tasks by:
1. Creating runnable examples
2. Documenting usage instructions
3. Setting up and running test scenarios
4. Enabling human interaction

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Human Playground"

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null
  require_human_review: yes
  feature_phase: "Human Playground"

  # Required inputs
  auto_proceed: false

  # Context (from previous task or project)
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Code implementation complete</name>
    <verification>Verify feature code is implemented and merged</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature status is "Done Code Implementation"</name>
    <verification>Check feature board for current status</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All tests passing</name>
    <verification>Run test suite and confirm zero failures</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Create Examples | Build runnable playground files in `playground/` | Playground file created |
| 2 | Document Usage | Add entry to `playground/README.md` | README updated |
| 3 | Create Tests | Write human simulation tests in `playground/tests/` | Test files created |
| 4 | Validate | Run playground command and verify exit code 0 | Command succeeds |
| 5 | Run Tests | Execute human simulation tests | All tests pass |
| 6 | Complete | Verify DoD, output summary, request human review | Human review |

BLOCKING: Step 4 is blocked until playground command runs without error.
BLOCKING: Step 5 is blocked until human simulation tests pass.
BLOCKING: Step 6 requires human validation before Feature Closing.

---

## Execution Procedure

```xml
<procedure name="human-playground">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Create Runnable Examples</name>
    <action>
      1. Create `playground/` directory if it does not exist
      2. Place playground files directly in `playground/` (no subfolders per feature)
      3. Name files as `playground_{feature_name}.py`
      4. Identify key functionality to demonstrate
      5. Create minimal, self-contained runnable examples
      6. Include both happy path and edge cases
    </action>
    <constraints>
      - BLOCKING: File naming must follow `playground_{feature_name}.py` convention
      - CRITICAL: Examples must be self-contained and runnable without manual setup
    </constraints>
    <output>Playground file(s) in `playground/`</output>
  </step_1>

  <step_2>
    <name>Document Usage</name>
    <action>
      1. Create `README.md` inside `playground/` folder if it does not exist
      2. Add entry for the new playground with the command to run it
      3. Keep documentation minimal - explain how to run each playground
    </action>
    <constraints>
      - CRITICAL: README must include exact run command for each playground
    </constraints>
    <output>Updated `playground/README.md`</output>
  </step_2>

  <step_3>
    <name>Create and Validate Tests</name>
    <action>
      1. Create `playground/tests/` directory for test scripts
      2. Name test files as `test_playground_{feature_name}.py`
      3. Write tests that simulate human interaction scenarios (NOT unit tests)
      4. Tests must validate expected behavior from a human perspective
    </action>
    <constraints>
      - CRITICAL: These are human simulation tests, not unit tests
      - BLOCKING: Test file naming must follow `test_playground_{feature_name}.py`
    </constraints>
    <output>Test files in `playground/tests/`</output>
  </step_3>

  <step_4>
    <name>Validate Playground</name>
    <action>
      1. Execute playground command (e.g., `uv run python playground/playground_{feature}.py`)
      2. Verify it runs without error (exit code 0)
      3. If it fails, fix the playground script or surrounding code
    </action>
    <success_criteria>
      - Playground command exits with code 0
      - No runtime errors or unhandled exceptions
    </success_criteria>
    <output>Verified working playground</output>
  </step_4>

  <step_5>
    <name>Run Tests</name>
    <action>
      1. Execute human simulation tests
      2. Verify all tests pass
      3. If tests fail, fix the playground or test scripts
    </action>
    <success_criteria>
      - All human simulation tests pass
    </success_criteria>
    <output>All tests passing</output>
  </step_5>

  <step_6>
    <name>Enable Interaction</name>
    <action>
      1. Provide start/stop commands
      2. Include sample data
      3. Add reset capability
      4. Log outputs for debugging
      5. Inform human that playground is ready for review
    </action>
    <output>Playground ready for human validation</output>
  </step_6>

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
    - "playground/playground_{feature_name}.py"
    - "playground/tests/test_playground_{feature_name}.py"
    - "playground/README.md"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Human Playground"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Runnable examples created</name>
    <verification>Verify playground/playground_{feature_name}.py exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>README entry added</name>
    <verification>Verify playground/README.md contains run command for this feature</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human simulation tests created</name>
    <verification>Verify playground/tests/test_playground_{feature_name}.py exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Playground command verified</name>
    <verification>Agent has run playground command and confirmed exit code 0</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human simulation tests pass</name>
    <verification>Agent has executed tests and confirmed all pass</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human can interact with feature</name>
    <verification>Start/stop commands documented and sample data included</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Standard Playground Structure

**When:** Creating any playground
**Then:**
```
playground/
  README.md                            # How to run all playgrounds
  playground_{feature1}.py             # Interactive playground for feature 1
  playground_{feature2}.py             # Interactive playground for feature 2
  tests/
    test_playground_{feature1}.py      # Human simulation tests
    test_playground_{feature2}.py      # Human simulation tests
```

### Pattern: API Playground

**When:** Feature exposes an API
**Then:**
```
playground/
  README.md                  # How to run all playgrounds
  playground_api.py          # Interactive API testing script
  sample-data.json           # Test data (optional)
  tests/
    test_playground_api.py   # Human simulation tests
```

### Pattern: CLI Playground

**When:** Feature is command-line based
**Then:**
```
playground/
  README.md                    # How to run all playgrounds
  playground_cli.py            # Interactive CLI playground
  tests/
    test_playground_cli.py     # Human simulation tests
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| No instructions | Human cannot start | Write clear README |
| Hard-coded config | Does not work elsewhere | Use environment variables |
| No sample data | Nothing to test with | Provide seed data |
| Complex setup | Human gives up | Keep setup to 1-2 commands |
| No expected outputs | Human cannot tell if it works | Document what to expect |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.
