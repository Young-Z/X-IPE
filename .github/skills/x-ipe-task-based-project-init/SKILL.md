---
name: x-ipe-task-based-project-init
description: Initialize a new project with standard folder structure and documentation. Use when starting a fresh project or onboarding to existing project. Triggers on requests like "init project", "start new project", "set up project", "onboard to project".
---

# Task-Based Skill: Project Initialization

## Purpose

Set up or onboard to a project with consistent folder structure and documentation by:
1. Scanning existing project structure (if any)
2. Creating standard `x-ipe-docs/` folder hierarchy
3. Initializing task board via `x-ipe+all+task-board-management` skill
4. Creating baseline documentation files

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
  task_based_skill: "Project Initialization"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A

  # Task type attributes
  category: "standalone"
  next_task_based_skill: "Development Environment Setup"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"

  # Required inputs
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.auto_proceed" source="from caller (x-ipe-workflow-task-execution) or default 'manual'" />
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
| 3 | Init Task Board | Call x-ipe+all+task-board-management skill | Task board created |
| 4 | Init Docs | Create `lessons_learned.md` | Docs initialized |
| 5 | Routing | DAO-assisted next task routing | Routing decision made |

BLOCKING: Step 3 MUST use x-ipe+all+task-board-management skill (not manual file creation).
BLOCKING: Existing projects - only ADD missing files, do NOT restructure.

---

## Execution Procedure

```xml
<procedure name="project-init">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

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
    <name>Initialize Task Board</name>
    <action>
      1. Load skill: x-ipe+all+task-board-management
      2. Execute: Operation 1 - Init Task Board
    </action>
    <constraints>
      - BLOCKING: Must use x-ipe+all+task-board-management skill, not manual file creation
    </constraints>
    <output>x-ipe-docs/planning/task-board.md created</output>
  </step_3>

  <step_4>
    <name>Initialize Documentation</name>
    <action>
      1. Create `x-ipe-docs/reference/lessons_learned.md` using template from references/examples.md
    </action>
    <output>Baseline documentation files created</output>
  </step_4>

  <step_5>
    <name>Routing</name>
    <actions>
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
    </actions>
    <constraints>
      - BLOCKING (manual): Human MUST confirm or redirect before routing to next task
      - BLOCKING (auto/stop_for_question): Proceed after DoD verification; auto-select next task via DAO
    </constraints>
    <routing>
      **Execute next task based on the decision from above with related task based skill**
    </routing>
  </step_5>

</procedure>
```

See [references/examples.md](.github/skills/x-ipe-task-based-project-init/references/examples.md) for the standard project structure diagram and lessons learned template.

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill: "Development Environment Setup"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "x-ipe-docs/planning/task-board.md"
  # Dynamic attributes
  project_structure_created: true | false
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Standard folder structure exists</name>
    <verification>Verify x-ipe-docs/planning/, x-ipe-docs/reference/, x-ipe-docs/project-management-guideline/ directories exist</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Task board initialized via x-ipe+all+task-board-management</name>
    <verification>Verify x-ipe-docs/planning/task-board.md exists and was created by x-ipe+all+task-board-management skill</verification>
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
2. Init task board (via x-ipe+all+task-board-management)
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
| Skip task board | No task tracking | Always init via x-ipe+all+task-board-management |
| Copy template blindly | May not fit tech stack | Adapt to project |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-project-init/references/examples.md) for concrete execution examples.
