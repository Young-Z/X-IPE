---
name: x-ipe-task-based-user-manual
description: Create or update the user manual (README.md) with instructions on how to install, configure, and run the application. Use when minimum features are implemented or when specifically asked to document how to run the project. Triggers on requests like "create user manual", "document how to run", "update README".
---

# Task-Based Skill: User Manual

## Purpose

Execute **User Manual** tasks by:
1. Identifying the correct run commands for the application.
2. Verifying the commands by executing them.
3. Updating the project's `README.md` with a clear "How to Run" section.

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
  task_based_skill: "user-manual"

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null
  require_human_review: "yes"

  # Required inputs
  auto_proceed: false
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Application code is implemented and runnable</name>
    <verification>Check that source files exist and entry point is identifiable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Development environment is set up</name>
    <verification>Verify dependencies are installed and toolchain is available</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Identify Commands | Analyze config files to find run/test commands | Commands identified |
| 2 | Verify Commands | Execute commands to confirm they work | Commands verified |
| 3 | Update README | Add/update "How to Run" section in README.md | README updated |
| 4 | Complete | Verify DoD | DoD validated |

BLOCKING: Step 2 to 3 is blocked until run command executes successfully.

---

## Execution Procedure

```xml
<procedure name="user-manual">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Identify Run Instructions</name>
    <action>
      1. Determine how to start the application based on configuration files
         (e.g., pyproject.toml, package.json).
      2. Python (uv): Look for `uv run` usage or entry points (e.g., src/app.py).
      3. Node.js: Check `scripts` in package.json (e.g., npm start, npm run dev).
    </action>
    <output>Run command and test command identified</output>
  </step_1>

  <step_2>
    <name>Verify Run Command</name>
    <action>
      1. Execute the identified command in the terminal.
      2. Check for successful startup (e.g., "Running on http://...", "Server started").
      3. If it fails, debug the issue (missing dependencies, wrong path) before documenting.
      4. For background services, verify start and then stop/kill the process.
    </action>
    <constraints>
      - BLOCKING: Do not proceed to Step 3 until command executes successfully.
    </constraints>
    <output>Verified run command and test command</output>
  </step_2>

  <step_3>
    <name>Update README.md</name>
    <action>
      1. Add or update the "How to Run" section in README.md.
      2. Include Prerequisites: dependencies needing installation (e.g., "Install uv").
      3. Include Installation: commands to setup (e.g., uv sync).
      4. Include Running: the verified command to start the app.
      5. Include Testing: command to run tests (e.g., uv run pytest).
    </action>
    <success_criteria>
      - README contains Prerequisites, Installation, Running, and Testing subsections.
      - All documented commands are verified working.
    </success_criteria>
    <output>Updated README.md with run instructions</output>
  </step_3>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill: null
  require_human_review: "yes"
  task_output_links:
    - "README.md"
  # Dynamic attributes
  run_command: "{verified command}"
  test_command: "{verified test command}"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Run command identified and verified</name>
    <verification>Command was executed successfully in terminal</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>README.md updated with clear run instructions</name>
    <verification>README.md contains Prerequisites, Installation, Running sections</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>README.md includes test execution instructions</name>
    <verification>README.md contains Testing section with verified command</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Python Project

**When:** pyproject.toml exists
**Then:**
```
1. Check for uv.lock -> use `uv run`
2. Find entry point in pyproject.toml
3. Test: uv run python src/{entry}.py
4. Document: uv sync + run command
```

### Pattern: Node.js Project

**When:** package.json exists
**Then:**
```
1. Check scripts section for start/dev
2. Test: npm start or npm run dev
3. Document: npm install + run command
```

### Pattern: Web Application

**When:** App serves on a port
**Then:**
```
1. Run command and verify server starts
2. Include the URL in README
3. Add browser access instructions
4. Note any default credentials
```

### Pattern: Human Communication on Completion

**When:** Task is completed and requires human review
**Then:**
```
1. Inform the human with verified run and test commands
2. Request confirmation that README is clear
3. Example message:
   "User Manual updated in README.md.
    Verified Run Command: `{command}`
    Verified Test Command: `{test_command}`
    Please check the README and confirm it is clear."
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Document without testing | Commands may fail | Verify all commands work |
| Missing prerequisites | Users can't run | List all dependencies |
| Outdated instructions | Misleading | Verify before documenting |
| Skip test commands | Incomplete manual | Always include test instructions |
| Assume environment | Portability issues | Document setup from scratch |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.
