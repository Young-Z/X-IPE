---
name: task-type-project-init
description: Initialize a new project with standard folder structure and documentation. Use when starting a fresh project or onboarding to existing project. Triggers on requests like "init project", "start new project", "set up project", "onboard to project".
---

# Task Type: Project Initialization

## Purpose

Set up or onboard to a project with consistent folder structure and documentation.

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Project Initialization |
| Category | Standalone |
| Next Task Type | Development Environment Setup |
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
  next_task_type: Development Environment Setup
  require_human_review: No
  auto_proceed: {from input Auto Proceed}
  task_output_links: [x-ipe-docs/planning/task-board.md]
  # Dynamic attributes (skill-specific)
  project_structure_created: true | false
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
|  |  |  |

---

## Execution Flow

Execute Project Initialization by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Scan Existing | Check if project exists, read structure if so | Scan complete |
| 2 | Create Structure | Create `x-ipe-docs/planning/`, `x-ipe-docs/reference/`, etc. | Folders created |
| 3 | Init Task Board | Call task-board-management skill | Task board created |
| 4 | Init Docs | Create `lessons_learned.md` and other docs | Docs initialized |

**⛔ BLOCKING RULES:**
- Step 3: MUST use task-board-management skill (not manual file creation)
- Existing projects: Only ADD missing files, do NOT restructure

---

## Execution Procedure

### Step 1: Scan Existing Structure

```
IF project exists:
  1. Read all files (focus on: README, x-ipe-docs/, config files)
  2. Understand current architecture
ELSE:
  → Go to Step 2
```

### Step 2: Create Standard Structure

**Standard Project Structure:**

```
project-root/
├── x-ipe-docs/
│   ├── planning/
│   │   ├── task-board.md          # Task tracking (via task-board-management)
│   │   ├── feature-*.md           # Feature specifications
│   │   └── technical-design-*.md  # Design documents
│   ├── reference/
│   │   └── lessons_learned.md     # Project learnings
│   └── project-management-guideline/        # Collaboration docs
├── README.md                      # Project overview
└── .gitignore                     # Git ignore rules
```

**Enforced Creation Rules:**
```
`x-ipe-docs/`: IF missing, CREATE
`x-ipe-docs/planning/`: IF missing, CREATE
`x-ipe-docs/reference/`: IF missing, CREATE
`x-ipe-docs/project-management-guideline/`: IF missing, CREATE
.gitignore: IF missing, CREATE
README.md: IF missing, CREATE
```

### Step 3: Initialize Task Board

```
Load skill: task-board-management
Execute: Operation 1 - Init Task Board

This creates: x-ipe-docs/planning/task-board.md
```

### Step 4: Initialize Documentation

**Create `x-ipe-docs/reference/lessons_learned.md`:**

```markdown
# Lessons Learned

## Template
| Date | Category | Lesson | Context |
|------|----------|--------|---------|
| YYYY-MM-DD | <category> | <what learned> | <situation> |
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Standard folder structure exists | Yes |
| 2 | Task board initialized (via task-board-management) | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: Minimal Setup

**When:** Quick project start needed
**Then:**
```
1. Create only: x-ipe-docs/planning/
2. Init task board (via task-board-management)
3. Initialize: README.md, .gitignore
4. Skip: x-ipe-docs/reference/, x-ipe-docs/project-management-guideline/ (add later)
```

### Pattern: Existing Project Onboarding

**When:** Joining existing project
**Then:**
```
1. READ first (don't create files)
2. Map existing structure to standard
3. Only ADD missing critical files
4. Preserve existing conventions
5. Init task board if missing
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Restructure existing project | Breaks working code | Add missing files only |
| Create empty placeholder files | Noise, maintenance burden | Create when needed |
| Skip task board | No task tracking | Always init via task-board-management |
| Copy template blindly | May not fit tech stack | Adapt to project |

---

## File Creation Rules

**Critical:** Only create files in these locations:
- `x-ipe-docs/` - Documentation

**Never create:**
- Files in project root (except README, config)
- Arbitrary folders outside structure
- Duplicate documentation

---

## Example

**Request:** "Initialize a new Python API project"

**Execution:**
```
1. Execute Task Flow from task-execution-guideline skill

2. Scan existing structure:
   → No existing project found

3. Create structure:
   x-ipe-docs/planning/
   x-ipe-docs/reference/lessons_learned.md
   x-ipe-docs/project-management-guideline/
   README.md
   .gitignore

4. Init task board:
   → Load skill: task-board-management
   → Execute: Operation 1 - Init Task Board
   → Created: x-ipe-docs/planning/task-board.md

5. Return Task Completion Output:
   category: standalone
   next_task_type: Development Environment Setup
   require_human_review: No
   task_output_links:
     - x-ipe-docs/planning/task-board.md

6. Resume Task Flow from task-execution-guideline skill
```
