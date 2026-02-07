---
name: x-ipe-task-based-dev-environment
description: Set up development environment with appropriate tech stack (Python with uv or Node.js with npm/yarn), project structure, and git version control. Use when initializing project environments or preparing workspace for development. Triggers on requests like "set up environment", "create dev environment", "configure workspace", "initialize project".
---

# Task-Based Skill: Development Environment Setup

## Purpose

Set up a development environment by:
1. Determining the tech stack (Python/Node.js) from context or user input
2. Initializing the package manager and standard folder structure
3. Initializing git with a tech-stack-specific .gitignore
4. Documenting the setup and creating an initial commit

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
  task_based_skill: "dev-environment"

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null
  require_human_review: no

  # Required inputs
  auto_proceed: false

  # Context (from previous task or project)
  project_root: "{absolute path to project root}"
  project_name: "{project name}"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Project root directory exists</name>
    <verification>Verify directory at {project_root} exists and is writable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Project name determined</name>
    <verification>Check {project_name} is set from task board or user input</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Determine Stack | Identify tech stack from context or ask user | Stack selected |
| 2 | Init Package Manager | Run `uv init` or `npm init`, create src/tests folders | Package manager ready |
| 3 | Init Git | Call x-ipe-tool-git-version-control skill for repo and .gitignore | Git initialized |
| 4 | Document Setup | Create `x-ipe-docs/environment/setup.md` | Documentation created |
| 5 | Commit | Stage and commit all setup files | Initial commit done |

BLOCKING: Step 2 cannot start until tech stack is confirmed.
BLOCKING: Step 3 cannot proceed if x-ipe-tool-git-version-control skill fails.

---

## Execution Procedure

```xml
<procedure name="dev-environment-setup">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Determine Tech Stack</name>
    <action>
      1. Check if user explicitly specified tech stack in request
      2. If not specified, analyze context clues (see references/tech-stack-details.md for detection hints)
      3. If still unclear, present options:
         "Which tech stack would you like to use?
          1. Python Application (default) - Python with uv
          2. Node.js Application - Node.js with npm/yarn"
      4. Default to Python if no preference given
    </action>
    <output>tech_stack: python | nodejs</output>
  </step_1>

  <step_2>
    <name>Initialize Package Manager</name>
    <action>
      1. Execute initialization for the selected stack
      2. Create standard folder structure (src/, tests/)
      3. Create entry-point files
    </action>
    <branch>
      IF: tech_stack = "python"
      THEN:
        1. Run: uv init
        2. Run: uv venv
        3. Create src/__init__.py and tests/__init__.py
      ELSE (tech_stack = "nodejs"):
        1. Ask user for npm or yarn preference (default: npm)
        2. Run: npm init -y OR yarn init -y
        3. Create src/index.js and tests/index.test.js
    </branch>
    <constraints>
      - BLOCKING: Must not proceed without confirmed tech stack
      - CRITICAL: Always create both src/ and tests/ directories
    </constraints>
    <output>Package manager initialized, folder structure created</output>
  </step_2>

  <step_3>
    <name>Initialize Git Repository</name>
    <action>
      1. Call x-ipe-tool-git-version-control skill:
         operation: init
         directory: {project_root}
      2. Call x-ipe-tool-git-version-control skill:
         operation: create_gitignore
         directory: {project_root}
         tech_stack: {tech_stack}
    </action>
    <constraints>
      - BLOCKING: If x-ipe-tool-git-version-control skill fails, halt and report
      - If .git already exists, skip init and update .gitignore only
    </constraints>
    <output>Git repository initialized with tech-stack-specific .gitignore</output>
  </step_3>

  <step_4>
    <name>Document Setup</name>
    <action>
      1. Create x-ipe-docs/environment/ directory if not exists
      2. Generate setup.md using template from templates/ folder:
         - Python: templates/setup-python.md
         - Node.js: templates/setup-nodejs.md
      3. If templates unavailable, use inline templates from references/tech-stack-details.md
    </action>
    <output>x-ipe-docs/environment/setup.md created</output>
  </step_4>

  <step_5>
    <name>Commit Setup</name>
    <action>
      1. Call x-ipe-tool-git-version-control skill:
         operation: add
         directory: {project_root}
         files: null (all files)
      2. Call x-ipe-tool-git-version-control skill:
         operation: commit
         directory: {project_root}
         task_data: {current_task_data_model}
    </action>
    <output>Initial commit created with structured message</output>
  </step_5>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill: null
  require_human_review: no
  task_output_links:
    - "x-ipe-docs/environment/setup.md"
    - ".gitignore"
    - "README.md"
  # Dynamic attributes
  tech_stack: python | nodejs
  package_manager: uv | npm | yarn
  git_initialized: true | false
  initial_commit_hash: "{commit-hash} | null"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Directory structure created</name>
    <verification>Verify src/ and tests/ directories exist with entry-point files</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Package manager initialized</name>
    <verification>Verify pyproject.toml (Python) or package.json (Node.js) exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Git repository initialized</name>
    <verification>Verify .git/ directory exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>.gitignore created</name>
    <verification>Verify .gitignore contains tech-stack-specific patterns</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Setup documented</name>
    <verification>Verify x-ipe-docs/environment/setup.md exists with setup instructions</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Initial commit created</name>
    <verification>Run `git log --oneline -1` and verify structured commit message</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Explicit Stack Request

**When:** User specifies tech stack in request (e.g., "set up FastAPI project")
**Then:**
```
1. Extract stack from request
2. Skip selection prompt
3. Proceed with initialization
```

### Pattern: Context Detection

**When:** Project files hint at tech stack (pyproject.toml, package.json)
**Then:**
```
1. Detect existing config files
2. Recommend detected stack
3. Confirm with user before proceeding
```

### Pattern: Existing Git Repo

**When:** .git folder already exists
**Then:**
```
1. Skip git init
2. Update .gitignore if needed
3. Proceed with package manager setup
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip git init | No version control | Always initialize git |
| Wrong .gitignore | Tracks unwanted files | Use tech-stack-specific template |
| Missing src/tests | Inconsistent structure | Always create standard folders |
| No initial commit | Loses setup state | Commit after setup |
| Assume tech stack | Wrong environment | Ask or detect from context |
| Skip venv (Python) | Global package pollution | Always create virtual environment |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples including:
- Python project setup with uv and venv
- Node.js project setup with npm
- Missing setup guide (blocked scenario)
- Existing VS Code config (merge mode)

See [references/tech-stack-details.md](references/tech-stack-details.md) for:
- Auto-detection hints table
- Detailed initialization commands per stack
- Setup document templates
- Troubleshooting and validation commands
