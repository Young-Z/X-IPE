---
name: x-ipe-task-based-human-playground
description: "Create interactive examples for human validation. Human-initiated only — invoke ONLY when user explicitly requests a playground. Triggers on requests like \"create playground\", \"human testing\", \"interactive demo\", \"I want to test this\". Do NOT auto-suggest after feature_closing."
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

Load the [single-loop delivery policy](.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md)
once in the current context. Execute this skill in the same agent loop; another
skill is expertise, not a new agent. Use proportional checks and reuse current
evidence; independent review is conditional on concrete risk, not the skill name.

Load `x-ipe-workflow-task-execution` and its
[common lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md).
Reuse the supplied task/readiness; direct entry calls Orient/Plan once without
recursively dispatching this skill. One owner handles task/feature/app writes,
Git and the next boundary. Return full output; do not register or execute a
successor. Within-skill questions follow the three existing interaction modes;
clear inputs need no question or DAO call. Explicit human approvals still bind.

⚠️ **HUMAN-INITIATED ONLY:** This skill should ONLY be invoked when the human explicitly requests a playground (e.g., "create playground", "I want to test this interactively", "set up a demo"). It is NOT part of the standard engineering pipeline. The standard pipeline ends at `feature_closing`. Agents MUST NOT auto-suggest this skill as the next step after any pipeline stage.

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.


---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-human-playground"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      specification: "path | N/A | auto-detect"
      impl-files: "path | N/A | auto-detect"

  # Task type attributes
  category: "standalone"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-closing"
      condition: "Close feature after successful validation"
    - skill: "x-ipe-task-based-bug-fix"
      condition: "Fix bugs discovered during playground testing"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
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
  <field name="task_id" source="existing lifecycle task/readiness; no duplicate registration" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="feature_id" source="previous task output OR task board OR human input">
    <steps>
      1. IF previous task output contains feature_id → use it
      2. ELIF task board has feature_id in task data → use it
      3. ELSE → IF interaction_mode == "dao-represent-human-to-interact": derive from workflow context or x-ipe-assistant-user-representative-Engineer; ELSE: ask human for feature_id
    </steps>
  </field>
  <field name="feature_title" source="feature specification OR features.md">
    <steps>
      1. Query feature board for feature_id → extract title
      2. ELIF x-ipe-docs/features/{feature_id}/specification.md exists → extract title
      3. ELSE → IF interaction_mode == "dao-represent-human-to-interact": derive from feature_id context; ELSE: ask human
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

BLOCKING: Step 4 is blocked until playground command runs without error.
BLOCKING: Step 5 is blocked until human simulation tests pass.
Step 6 returns a verified playground to the owner. Actual required human validation
must not be skipped by an interaction-mode setting.

---

## Execution Procedure

```xml
<procedure name="human-playground">
  <execute_dor_checks_before_starting/>

  <step_1>
    <name>Create Runnable Examples</name>
    <action>
      1. DETECT tech_stack from feature implementation files and project config
      2. TOOL SKILL ROUTING (config-filtered):
         a. DISCOVER: Scan .github/skills/x-ipe-tool-implementation-*/
         b. READ CONFIG: Read x-ipe-docs/config/tools.json → stages.feedback.human_playground
            - Use [capability routing](.github/skills/x-ipe-workflow-task-execution/references/capability-routing.md): missing/empty/metadata-only retains discovery
            - Explicit booleans activate opt-in: true enables, false/undeclared disables; nonbooleans block
         c. FILTER: Only eligible tools participate; never force-enable general. Refresh changed config/catalog revisions
         d. SEMANTIC MATCH: Match tech_stack to enabled tool skill
         e. IF no match → use enabled suitable general only; otherwise return a capability gap, not Python defaults
      3. DETERMINE file extension and run command from matched tool:
         - Python: ext=.py, cmd="uv run python"
         - TypeScript: ext=.ts, cmd="npx tsx"
         - JavaScript: ext=.js, cmd="node"
         - Java: ext=.java, cmd="java"
         - General: ext determined by context, cmd determined by context
      4. Create `playground/` directory if it does not exist
      5. Place playground files directly in `playground/` (no subfolders per feature)
      6. Name files as `playground_{feature_name}.{ext}` (dynamic extension)
      7. Identify key functionality to demonstrate
      8. Create minimal, self-contained runnable examples (happy path + edge cases)
    </action>
    <constraints>
      - BLOCKING: File naming must follow `playground_{feature_name}.{ext}` convention
      - CRITICAL: Examples must be self-contained and runnable without manual setup
    </constraints>
    <output>Playground file(s) in `playground/`, matched tool skill and run command</output>
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
      2. Name test files as `test_playground_{feature_name}.{ext}` (same ext as Step 1)
      3. Write tests that simulate human interaction scenarios (NOT unit tests)
      4. Tests must validate expected behavior from a human perspective
    </action>
    <constraints>
      - CRITICAL: These are human simulation tests, not unit tests
      - BLOCKING: Test file naming must follow `test_playground_{feature_name}.{ext}`
    </constraints>
    <output>Test files in `playground/tests/`</output>
  </step_3>

  <step_4>
    <name>Validate Playground</name>
    <action>
      1. Execute playground using the run command determined in Step 1 (e.g., `uv run python`, `npx tsx`, `node`)
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
      1. Return actual playground path, verification evidence and required validation gaps to owner. In workflow-mode only the owner verifies the current human_playground action, writes its exact configured deliverables and checks readback once; free-mode performs no app write.
      2. Provide start/stop commands
      3. Include sample data
      4. Include a safe reset only for isolated sample state when actually needed
      5. Log outputs for debugging
      6. Inform that playground is ready for testing

        Return to owner for the shared mode-aware completion boundary.
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
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-closing"
      condition: "Close feature after successful validation"
    - skill: "x-ipe-task-based-bug-fix"
      condition: "Fix bugs discovered during playground testing"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "playground/playground_{feature_name}.{ext}"
    - "playground/tests/test_playground_{feature_name}.{ext}"
    - "playground/README.md"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Human Playground"
```

---

## Definition of Done

Verify the applicable outcomes in the current loop; use independent review only when concrete risk warrants it.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Runnable examples created</name>
    <verification>Verify playground/playground_{feature_name}.{ext} exists (ext from Step 1)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>README entry added</name>
    <verification>Verify playground/README.md contains run command for this feature</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human simulation tests created</name>
    <verification>Verify playground/tests/test_playground_{feature_name}.{ext} exists</verification>
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
  README.md                               # How to run all playgrounds
  playground_{feature1}.{ext}             # Interactive playground (ext from tool skill)
  playground_{feature2}.{ext}             # Interactive playground
  tests/
    test_playground_{feature1}.{ext}      # Human simulation tests
    test_playground_{feature2}.{ext}      # Human simulation tests
```

### Pattern: API/CLI Playground

**When:** Feature exposes an API or CLI
**Then:** Same structure, include sample-data.json if needed for test data.

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
