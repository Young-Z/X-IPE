---
name: x-ipe-tool-readme-updator
description: Update project-related instructional documentation (README.md) by identifying, verifying, and documenting run/test commands. Use when a calling skill needs to update project documentation as a sub-step. Triggers on requests like "update README", "generate README run section", "document how to run", "update project docs".
---

# README Updator Tool

## Purpose

AI Agents follow this skill to update project-related instructional documentation by:
1. Identifying run and test commands from project configuration files
2. Verifying commands execute successfully
3. Updating README.md with a clear "How to Run" section

---

## Important Notes

BLOCKING: This is a **tool skill** — it updates project instructional docs only, no task board interaction.
CRITICAL: Called by `x-ipe-task-based-feature-closing` as an optional step in Phase 3 when enabled by end user.

---

## About

This tool extracts the core README-update logic into a reusable tool for updating project-related instructional documentation. It can be invoked by any task-based skill that needs to update project docs as part of its workflow.

**Key Concepts:**
- **Command Discovery** — Scan pyproject.toml, package.json, or similar config to find run/test commands
- **Command Verification** — Execute discovered commands to confirm they work before documenting
- **README Update** — Add or update Prerequisites, Installation, Running, and Testing subsections

---

## When to Use

```yaml
triggers:
  - "update README"
  - "generate README run section"
  - "document how to run"
  - "update project docs"
  - "update README with run instructions"

not_for:
  - "knowledge extraction from applications" → use x-ipe-task-based-application-knowledge-extractor
```

---

## Input Parameters

```yaml
input:
  operation: "update_readme"
  config:
    readme_path: "README.md"              # path to README file, default: README.md
    feature_context:                       # optional, from calling skill
      feature_id: "{FEATURE-XXX}"
      feature_title: "{title}"
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies 'update_readme'" />
  <field name="config.readme_path" source="Caller provides or defaults to 'README.md'" />
  <field name="config.feature_context" source="Optional — provided by calling skill (e.g., feature-closing) for context">
    <steps>
      1. IF caller provides feature context → use it to scope documentation
      2. ELSE → document project-wide run instructions
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Project config exists</name>
    <verification>At least one of pyproject.toml or package.json exists in project root</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Application code is runnable</name>
    <verification>Source files exist and entry point is identifiable from config</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: update_readme

**When:** A calling skill or user needs README.md updated with verified run instructions.

```xml
<operation name="update_readme">
  <action>
    1. Identify run and test commands:
       a. IF pyproject.toml exists → look for uv run usage, entry points (e.g., src/app.py)
       b. IF package.json exists → check scripts section (start, dev, test)
       c. IF neither exists → return error MANUAL_NO_CONFIG
    2. Verify run command:
       a. Execute the identified command in terminal
       b. Check for successful startup (e.g., "Running on http://...", "Server started")
       c. For background services, verify start then stop the process
       d. IF command fails → return error MANUAL_CMD_FAILED with details
    3. Verify test command:
       a. Execute the identified test command
       b. Check for passing test output
       c. IF no test command found → note "no test command identified"
    4. Update README.md:
       a. Read existing README.md (or create if missing)
       b. Add or replace "How to Run" section with:
          - Prerequisites: dependencies needing installation
          - Installation: setup commands (e.g., uv sync, npm install)
          - Running: the verified run command
          - Testing: the verified test command
       c. IF feature_context provided → mention the feature in the section header
    5. Return operation_output with verified commands
  </action>
  <constraints>
    - BLOCKING: Do NOT document commands that have not been verified
    - CRITICAL: All documented commands must execute successfully
    - MANDATORY: All internal markdown links MUST use full project-root-relative paths
  </constraints>
  <output>operation_output with success, run_command, test_command, readme_path</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    run_command: "{verified command to run the application}"
    test_command: "{verified command to run tests}"
    readme_path: "{path to updated README}"
    sections_updated: ["Prerequisites", "Installation", "Running", "Testing"]
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Commands identified</name>
    <verification>Run command and test command extracted from project config</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Commands verified</name>
    <verification>Both commands executed successfully in terminal</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>README updated</name>
    <verification>README.md contains Prerequisites, Installation, Running, Testing subsections</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Operation output returned</name>
    <verification>operation_output contains success=true, run_command, test_command</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `MANUAL_NO_CONFIG` | Neither pyproject.toml nor package.json found | Ensure project has a config file, or provide run commands manually |
| `MANUAL_CMD_FAILED` | Identified run/test command failed to execute | Debug command failure (missing deps, wrong path) before retrying |
| `MANUAL_README_WRITE_FAIL` | Cannot write to README.md | Check file permissions and path |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-readme-updator/references/examples.md) for usage examples.
