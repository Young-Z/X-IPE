# Project Initialization - Examples

## Standard Project Structure

```
project-root/
├── x-ipe-docs/
│   ├── planning/
│   │   ├── task-board.md          # Task tracking (via x-ipe+all+task-board-management)
│   │   ├── feature-*.md           # Feature specifications
│   │   └── technical-design-*.md  # Design documents
│   ├── reference/
│   │   └── lessons_learned.md     # Project learnings
│   └── project-management-guideline/        # Collaboration docs
├── README.md                      # Project overview
└── .gitignore                     # Git ignore rules
```

## Lessons Learned Template

When creating `x-ipe-docs/reference/lessons_learned.md`, use this template:

```markdown
# Lessons Learned

## Template
| Date | Category | Lesson | Context |
|------|----------|--------|---------|
| YYYY-MM-DD | <category> | <what learned> | <situation> |
```

---

## Example 1: New Python API Project

**Request:** "Initialize a new Python API project"

**Execution:**
```
1. Execute Task Flow from x-ipe-workflow-task-execution skill

2. Scan existing structure:
   -> No existing project found

3. Create structure:
   x-ipe-docs/planning/
   x-ipe-docs/reference/lessons_learned.md
   x-ipe-docs/project-management-guideline/
   README.md
   .gitignore

4. Init task board:
   -> Load skill: x-ipe+all+task-board-management
   -> Execute: Operation 1 - Init Task Board
   -> Created: x-ipe-docs/planning/task-board.md

5. Return Task Completion Output:
   category: standalone
   next_task_based_skill: Development Environment Setup
   require_human_review: no
   task_output_links:
     - x-ipe-docs/planning/task-board.md

6. Resume Task Flow from x-ipe-workflow-task-execution skill
```

## Example 2: Onboarding to Existing Project

**Request:** "Onboard to this existing Node.js project"

**Execution:**
```
1. Execute Task Flow from x-ipe-workflow-task-execution skill

2. Scan existing structure:
   -> Found: README.md, package.json, src/, tests/
   -> Missing: x-ipe-docs/

3. Create only missing structure:
   x-ipe-docs/planning/
   x-ipe-docs/reference/lessons_learned.md
   -> Preserved existing README.md, .gitignore

4. Init task board:
   -> Load skill: x-ipe+all+task-board-management
   -> Execute: Operation 1 - Init Task Board
   -> Created: x-ipe-docs/planning/task-board.md

5. Return Task Completion Output:
   category: standalone
   next_task_based_skill: Development Environment Setup
   require_human_review: no
   task_output_links:
     - x-ipe-docs/planning/task-board.md

6. Resume Task Flow from x-ipe-workflow-task-execution skill
```
