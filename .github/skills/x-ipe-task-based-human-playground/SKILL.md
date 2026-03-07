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

IMPORTANT: When `process_preference.auto_proceed == "auto"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Human Playground"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      specification: "path | N/A | auto-detect"
      impl-files: "path | N/A | auto-detect"

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  feature_phase: "Human Playground"

  # Required inputs

  # Context (from previous task or project)
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.auto_proceed" source="from caller (x-ipe-workflow-task-execution) or default 'manual'" />
  <field name="feature_id" source="previous task output OR task board OR human input">
    <steps>
      1. IF previous task output contains feature_id → use it
      2. ELIF task board has feature_id in task data → use it
      3. ELSE → IF auto_proceed == "auto": derive from workflow context or x-ipe-dao-end-user-representative; ELSE: ask human for feature_id
    </steps>
  </field>
  <field name="feature_title" source="feature specification OR features.md">
    <steps>
      1. Query feature board for feature_id → extract title
      2. ELIF x-ipe-docs/features/{feature_id}/specification.md exists → extract title
      3. ELSE → IF auto_proceed == "auto": derive from feature_id context; ELSE: ask human
    </steps>
  </field>
  <field name="feature_version" source="features.md OR default '1.0.0'">
    <steps>
      1. Query feature board for feature_id → extract version
      2. ELIF not found → default to "1.0.0"
    </steps>
  </field>
</input_init>
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
| 6 | Complete | Verify DoD, output summary, inform human playground is ready | Playground delivered |
| 7.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| 7.2 | Execute Next Action | Delegate to x-ipe-workflow-task-execution sub-agent | Sub-agent started |

BLOCKING: Step 4 is blocked until playground command runs without error.
BLOCKING: Step 5 is blocked until human simulation tests pass.
BLOCKING: Step 6 requires validation before Feature Closing (manual/stop_for_question: human validation; auto: skipped).

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
      1. IF execution_mode == "workflow-mode":
         a. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with:
            - workflow_name: {from context}
            - action: "human_playground"
            - status: "done"
            - feature_id: {feature_id}
            - deliverables: {"playground-url": "{path}"}
         b. Log: "Workflow action status updated to done"
      2. Provide start/stop commands
      3. Include sample data
      4. Add reset capability
      5. Log outputs for debugging
      6. Inform that playground is ready for testing

        Completion gate (based on auto_proceed):
        IF process_preference.auto_proceed == "auto":
          → Auto-proceed after DoD verification
        ELSE (manual/stop_for_question):
          → Ask human to validate playground
    </action>
    <output>Playground ready for human validation</output>
  </step_6>

  <phase_7 name="继续执行（Continue Execute）">
    <step_7_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.auto_proceed == "auto":
          → Invoke x-ipe-dao-end-user-representative with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the context and full output to decide best next action."
          → DAO studies the complete context and decides the best next action
        ELSE (manual):
          → Present next task suggestion to human and wait for instruction
      </action>
      <constraints>
        - BLOCKING (manual): Human MUST confirm or redirect before proceeding
        - BLOCKING (auto): Proceed after DoD verification; auto-select next task via DAO
      </constraints>
      <output>Next action decided with execution context</output>
    </step_7_1>
    <step_7_2>
      <name>Execute Next Action</name>
      <action>
        Based on the decision from Step 7.1, delegate execution to a sub-agent:
        1. Invoke x-ipe-workflow-task-execution as a sub-agent (use premium model)
        2. Pass the decided next task and full context from Step 7.1
        3. The workflow skill handles: skill loading, execution plan generation, and execution
      </action>
      <constraints>
        - MUST delegate to x-ipe-workflow-task-execution — do not execute the next skill directly
        - Sub-agent MUST use premium model (Best-Model Requirement)
        - Execution follows the workflow skill's 6-step orchestration
      </constraints>
      <output>Sub-agent started with x-ipe-workflow-task-execution</output>
    </step_7_2>
  </phase_7>

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

See [references/examples.md](.github/skills/x-ipe-task-based-human-playground/references/examples.md) for concrete execution examples.
