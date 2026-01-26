---
name: task-type-dev-environment
description: Set up development environment with appropriate tech stack (Python with uv or Node.js with npm/yarn), project structure, and git version control. Use when initializing project environments or preparing workspace for development. Triggers on requests like "set up environment", "create dev environment", "configure workspace", "initialize project".
---

# Task Type: Development Environment Setup

## Purpose

Set up development environment with tech stack selection, proper folder structure, package manager initialization, and git version control integration.

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Development Environment Setup |
| Category | Standalone |
| Next Task Type | N/A |
| Require Human Review | No |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |

---

## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: standalone
  status: completed | blocked
  next_task_type: null
  require_human_review: No
  auto_proceed: {from input Auto Proceed}
  task_output_links: [x-ipe-docs/environment/setup.md, .gitignore, README.md]
  
  # Dynamic attributes (skill-specific)
  tech_stack: python | nodejs
  package_manager: uv | npm | yarn
  git_initialized: true | false
  initial_commit_hash: <commit-hash> | null
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Project root directory exists | Yes |
| 2 | Project name determined | Yes |

---

## Execution Flow

Execute Development Environment Setup by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Determine Stack | Identify tech stack (Python/Node.js) from context or ask user | Stack selected |
| 2 | Init Package Manager | Run `uv init` or `npm init`, create src/tests folders | Package manager ready |
| 3 | Init Git | Call git-version-control skill to init repo and .gitignore | Git initialized |
| 4 | Document Setup | Create `x-ipe-docs/environment/setup.md` with instructions | Documentation created |
| 5 | Commit | Stage and commit all setup files | Initial commit done |

**⛔ BLOCKING RULES:**
- Step 2: BLOCKED until tech stack is confirmed
- Step 3: BLOCKED if git-version-control skill fails

---

## Execution Procedure

### Step 1: Determine Tech Stack

**Actions:**
```
1. Check if user explicitly specified tech stack in request
2. If not specified, analyze context (project requirements, task description)
3. If still unclear, present options to user:
   
   "I'll set up the development environment. Which tech stack would you like to use?
   
   1. Python Application (default) - Python with uv
   2. Node.js Application - Node.js with npm/yarn
   
   [If context suggests a choice, recommend it]"

4. Default to Python if no preference or timeout
```

**Output:** Selected tech_stack (python | nodejs)

---

### Step 2: Initialize Package Manager

**Based on tech_stack, execute appropriate initialization:**

#### If tech_stack = "python":

```
1. Run: uv init
2. Run: uv venv
3. Create src/ folder
4. Create src/__init__.py
5. Create tests/ folder  
6. Create tests/__init__.py
```

**Resulting Structure:**
```
project-root/
├── .venv/
├── src/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
└── README.md
```

#### If tech_stack = "nodejs":

```
1. Ask user: "Would you like to use npm or yarn?"
   Default to npm if no answer
2. Run: npm init -y  OR  yarn init -y
3. Create src/ folder
4. Create src/index.js
5. Create tests/ folder
6. Create tests/index.test.js
```

**Resulting Structure:**
```
project-root/
├── node_modules/
├── src/
│   └── index.js
├── tests/
│   └── index.test.js
├── package.json
└── README.md
```

---

### Step 3: Initialize Git Repository

**Use git-version-control skill:**

```
1. Call git-version-control skill:
   operation: init
   directory: {project_root}

2. Call git-version-control skill:
   operation: create_gitignore
   directory: {project_root}
   tech_stack: {selected_tech_stack}
```

**Output:** Git repository initialized with appropriate .gitignore

---

### Step 4: Document Setup

**Create `x-ipe-docs/environment/setup.md` based on tech stack:**

#### For Python:

```markdown
# Environment Setup

## Tech Stack
- Python with uv package manager
- Virtual environment: .venv

## Structure
```
project-root/
├── .venv/              # Virtual environment
├── src/                # Source code
├── tests/              # Test files
├── pyproject.toml      # Project configuration
└── x-ipe-docs/               # Documentation
```

## Prerequisites
- Python 3.8+
- uv package manager (install: `pip install uv`)

## Setup Steps

1. **Clone or navigate to project:**
   ```bash
   cd /path/to/project
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\activate    # Windows
   ```

3. **Install dependencies (when added):**
   ```bash
   uv pip install -r requirements.txt
   # or
   uv pip install <package-name>
   ```

## Development

- **Run application:** `python src/main.py` (or your entry point)
- **Run tests:** `pytest tests/`
- **Add packages:** `uv pip install <package>`
- **Freeze dependencies:** `uv pip freeze > requirements.txt`

## Notes
- Keep all source code in `src/`
- Keep all tests in `tests/`
- Use .gitignore to exclude .venv/ and other generated files
```

#### For Node.js:

```markdown
# Environment Setup

## Tech Stack
- Node.js with {npm|yarn} package manager

## Structure
```
project-root/
├── node_modules/       # Dependencies
├── src/                # Source code
├── tests/              # Test files
├── package.json        # Project configuration
└── x-ipe-docs/               # Documentation
```

## Prerequisites
- Node.js 16+
- npm (comes with Node.js) or yarn

## Setup Steps

1. **Clone or navigate to project:**
   ```bash
   cd /path/to/project
   ```

2. **Install dependencies (when added):**
   ```bash
   npm install
   # or
   yarn install
   ```

## Development

- **Run application:** `node src/index.js` (or use npm scripts)
- **Run tests:** `npm test` or `yarn test`
- **Add packages:** `npm install <package>` or `yarn add <package>`
- **Add dev packages:** `npm install -D <package>` or `yarn add -D <package>`

## Notes
- Keep all source code in `src/`
- Keep all tests in `tests/`
- Use .gitignore to exclude node_modules/ and other generated files
- Define scripts in package.json for common tasks
```

---

### Step 5: Commit Setup

**Use git-version-control skill to commit all setup:**

```
1. Call git-version-control skill:
   operation: add
   directory: {project_root}
   files: null  # Add all files

2. Call git-version-control skill:
   operation: commit
   directory: {project_root}
   task_data: {current_task_data_model}
```

**Generated commit message example:**
```
TASK-001 commit for: Set up Python development environment with uv and project structure
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Tech stack-appropriate directory structure created | Yes |
| 2 | Package manager initialized (uv/npm/yarn) | Yes |
| 3 | Git repository initialized | Yes |
| 4 | .gitignore created for tech stack | Yes |
| 5 | Setup documented in x-ipe-docs/environment/setup.md | Yes |
| 6 | Initial commit created with structured message | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Tech Stack Selection Guidelines

### Auto-Detection Hints

| Context Clue | Suggested Stack |
|--------------|-----------------|
| "Python", "Django", "Flask", "FastAPI" | python |
| "Node", "Express", "React", "Next.js" | nodejs |
| "API", "backend", "web service" | python (default) |
| "uv", "pip", "conda" | python |
| "npm", "yarn", "package.json" | nodejs |

### User Confirmation Examples

**Example 1: Clear Context**
```
User: "Set up environment for a FastAPI project"
Agent: "I'll set up a Python development environment with uv for your FastAPI project."
[Proceeds with python stack]
```

**Example 2: Ambiguous Context**
```
User: "Initialize development environment"
Agent: "I'll set up the development environment. Which tech stack would you like to use?

1. Python Application (default) - Python with uv
2. Node.js Application - Node.js with npm/yarn"

User: "Python"
[Proceeds with python stack]
```

**Example 3: No Response / Default**
```
User: "Set up dev environment"
Agent: [Presents options, waits 5 seconds]
Agent: "No preference specified. Using default Python with uv."
[Proceeds with python stack]
```

---

## Patterns

### Pattern: Explicit Stack Request

**When:** User specifies tech stack in request
**Then:**
```
1. Extract stack from request
2. Skip selection prompt
3. Proceed with initialization
```

### Pattern: Context Detection

**When:** Project files hint at tech stack
**Then:**
```
1. Check for pyproject.toml → Python
2. Check for package.json → Node.js
3. Recommend detected stack
4. Confirm with user
```

### Pattern: Existing Git Repo

**When:** .git folder already exists
**Then:**
```
1. Skip git init
2. Update .gitignore if needed
3. Proceed with package manager setup
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip git init | No version control | Always initialize git |
| Wrong .gitignore | Track unwanted files | Use tech-stack-specific template |
| Missing src/tests folders | Inconsistent structure | Always create standard folders |
| No initial commit | Lose setup state | Commit after setup |
| Assume tech stack | Wrong environment | Ask or detect from context |
| Skip venv (Python) | Global package pollution | Always create virtual environment |

---

## Example

See [references/examples.md](references/examples.md) for detailed execution examples including:
- Python project setup with uv and venv
- Node.js project setup with npm
- Missing setup guide (blocked scenario)
- Existing VS Code config (merge mode)

---

## Integration with git-version-control Skill

This skill heavily relies on the `git-version-control` skill for version control operations:

**Operation Sequence:**
```
1. init → Initialize repository
2. create_gitignore → Create tech stack-specific .gitignore
3. add → Stage all files
4. commit → Commit with structured message
```

See `skills/git-version-control/SKILL.md` for detailed operation documentation.

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| uv not found | uv not installed | Install: `pip install uv` |
| npm not found | Node.js not installed | Install Node.js from nodejs.org |
| Git not initialized | Step 3 failed | Manually run `git init` |
| Permission denied | Directory permissions | Use `sudo` or change directory owner |

### Validation Commands

**After Python setup:**
```bash
uv --version              # Check uv installed
source .venv/bin/activate # Activate venv
python --version          # Check Python version
git status                # Verify git initialized
```

**After Node.js setup:**
```bash
node --version   # Check Node.js installed
npm --version    # Check npm installed
git status       # Verify git initialized
```
