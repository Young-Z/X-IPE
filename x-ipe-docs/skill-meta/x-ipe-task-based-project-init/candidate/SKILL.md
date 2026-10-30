---
name: x-ipe-task-based-project-init
description: Initialize a new project with standard folder structure and documentation. Use when starting a fresh project or onboarding to existing project. Triggers on requests like "init project", "start new project", "set up project", "onboard to project".
---

# Task-Based Skill: Project Initialization

## Purpose

Set up or onboard to a project with consistent folder structure and documentation by:
1. Scanning existing project structure (if any)
2. Creating standard `x-ipe-docs/` folder hierarchy
3. Initializing task board via `x-ipe-tool-task-board-manager` skill
4. Creating baseline documentation files

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

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.


---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-project-init"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A

  # Task type attributes
  category: "standalone"
  next_task_based_skill:
    - skill: "x-ipe-task-based-dev-environment"
      condition: "Set up development environment"
    - skill: "x-ipe-task-based-ideation"
      condition: "Start ideating on project features"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

  # Required inputs
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing lifecycle task/readiness; no duplicate registration" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>x-ipe-workflow-task-execution learned</name>
    <verification>Agent confirms guideline skill is loaded</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Scan Existing | Check if project exists, read structure if so | Scan complete |
| 2 | Create Structure | Create `x-ipe-docs/` directories and root files | Folders created |
| 3 | Init Task Board | Call x-ipe-tool-task-board-manager skill | Task board created |
| 4 | Init Docs | Create `lessons_learned.md` | Docs initialized |

BLOCKING: Step 3 MUST use x-ipe-tool-task-board-manager skill (not manual file creation).
BLOCKING: Existing projects - only ADD missing files, do NOT restructure.

---

## Execution Procedure

```xml
<procedure name="project-init">
  <execute_dor_checks_before_starting/>


  <step_1>
    <name>Scan Existing Structure</name>
    <action>
      1. Check if project directory has existing files
      2. If existing: read all files (focus on README, x-ipe-docs/, config files)
      3. If existing: understand current architecture and conventions
      4. If new: proceed to step 2
    </action>

    <output>Inventory of existing vs missing structure</output>
  </step_1>

  <step_2>
    <name>Create Standard Structure</name>
    <action>
      1. Create `x-ipe-docs/` if missing
      2. Create `x-ipe-docs/planning/` if missing
      3. Create `x-ipe-docs/reference/` if missing
      4. Create `x-ipe-docs/project-management-guideline/` if missing
      5. Create `.gitignore` if missing
      6. Create `README.md` if missing
    </action>
    <constraints>
      - BLOCKING: Only create files in `x-ipe-docs/` (documentation) or project root (README, config)
      - CRITICAL: Never create arbitrary folders outside standard structure
      - CRITICAL: Never create duplicate documentation
      - CRITICAL: For existing projects, preserve existing files and conventions
    </constraints>
    <output>Standard folder hierarchy in place</output>
  </step_2>

  <step_3>
    <name>Verify Owner Task Registration</name>
    <action>
      1. Reuse the owner's registered task ID.
      2. Have the owner query that task through x-ipe-tool-task-board-manager.
      3. If registration is missing, return blocked to the owner; do not create a duplicate task or invent an init operation.
    </action>
    <constraints>
      - BLOCKING: Must use x-ipe-tool-task-board-manager skill, not manual file creation
    </constraints>
    <output>Existing owner task verified in the JSON task board</output>
  </step_3>

  <step_4>
    <name>Initialize Documentation</name>
    <action>
      1. Create `x-ipe-docs/reference/lessons_learned.md` using template from references/examples.md
    </action>
    <output>Baseline documentation files created</output>
  </step_4>



</procedure>
```

See [references/examples.md](.github/skills/x-ipe-task-based-project-init/references/examples.md) for the standard project structure diagram and lessons learned template.

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-dev-environment"
      condition: "Set up development environment"
    - skill: "x-ipe-task-based-ideation"
      condition: "Start ideating on project features"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "x-ipe-docs/planning/tasks/"
  # Dynamic attributes
  project_structure_created: true | false
```

---

## Definition of Done

Verify the applicable outcomes in the current loop; use independent review only when concrete risk warrants it.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Standard folder structure exists</name>
    <verification>Verify x-ipe-docs/planning/, x-ipe-docs/reference/, x-ipe-docs/project-management-guideline/ directories exist</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Task board initialized via x-ipe-tool-task-board-manager</name>
    <verification>Verify x-ipe-docs/planning/tasks/ directory exists with tasks-index.json, created by x-ipe-tool-task-board-manager skill</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Minimal Setup

**When:** Quick project start needed
**Then:**
```
1. Create only: x-ipe-docs/planning/
2. Init task board (via x-ipe-tool-task-board-manager)
3. Initialize: README.md, .gitignore
4. Skip: x-ipe-docs/reference/, x-ipe-docs/project-management-guideline/ (add later)
```

### Pattern: Existing Project Onboarding

**When:** Joining existing project
**Then:**
```
1. READ first (do not create files)
2. Map existing structure to standard
3. Only ADD missing critical files
4. Preserve existing conventions
5. Init task board if missing
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Restructure existing project | Breaks working code | Add missing files only |
| Create empty placeholder files | Noise, maintenance burden | Create when needed |
| Skip task board | No task tracking | Always init via x-ipe-tool-task-board-manager |
| Copy template blindly | May not fit tech stack | Adapt to project |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-project-init/references/examples.md) for concrete execution examples.
