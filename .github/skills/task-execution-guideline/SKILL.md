---
name: task-execution-guideline
description: Execute development tasks with planning and tracking. Triggers on requests like "implement feature", "fix bug", "create PR", "design architecture", "set up project". Provides 6-step workflow for task planning, execution, category-based closing, and auto-advance chaining.
---

# Task Execution Guideline

## Purpose

AI Agents follow this skill to execute development work through a standardized 6-step lifecycle:

1. **Plan** tasks by matching request to task types
2. **Verify** prerequisites (Global DoR)
3. **Execute** core work via task type skills
4. **Close** via category-based skill loading
5. **Validate** completion (Global DoD)
6. **Route** to next task if auto-advance enabled

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

**Important:** NEVER use `manage_todo_list` (VS Code internal) as substitute for task-board.md (project tracking)

---

## Task Data Model

### Task Structure

```yaml
Task:
  # Core fields (set during planning)
  task_id: TASK-XXX
  task_type: <Task Type>
  task_description: <≤50 words>
  category: <derived from suffix> | Standalone
  role_assigned: <Role Name>
  status: pending | in_progress | blocked | deferred | completed | cancelled
  last_updated: <MM-DD-YYYY HH:MM:SS>
  
  # Execution fields (set by task type skill)
  next_task_type: <Task Type> | null
  require_human_review: true | false
  task_output_links: [<links>] | null
  {Dynamic Attributes}: <from task type skill>   # Fully dynamic per task type
  
  # Closing fields (set by category skill)
  category_level_change_summary: <≤100 words> | null
  
  # Control fields
  auto_advance: true | false
```

### Category Derivation

| Task Type Suffix | Category |
|------------------|----------|
| `-@feature-stage` | feature-stage |
| `-@requirement-stage` | requirement-stage |
| No suffix | Standalone |

### Task States

| State | Terminal? | Description |
|-------|-----------|-------------|
| `pending` | No | Created, waiting to start |
| `in_progress` | No | Currently being worked on |
| `blocked` | No | Waiting for dependency |
| `deferred` | No | Human paused |
| `completed` | Yes | Successfully done |
| `cancelled` | Yes | Stopped |

### Valid State Transitions

```
pending → in_progress
in_progress → completed | blocked | deferred | cancelled
blocked → in_progress
deferred → in_progress
```

---

## Task Lifecycle

Execute tasks by following these 6 steps in order:

| Step | Name | Action | Mandatory Output | Next Step |
|------|------|--------|------------------|-----------|
| 1 | Planning | Match request → **Create task(s) on board** | Tasks visible on task-board.md | → Step 2 |
| 2 | Global DoR | Verify prerequisites | All checks pass | → Step 3 (pass) or STOP (fail) |
| 3 | Execute | Load task-type skill → Do work | Skill output collected | → Step 4 |
| 4 | Closing | Load category level skills → Update boards | Boards updated | → Step 5 |
| 5 | Global DoD | Validate → Output summary | Summary displayed | → Step 6 (pass) or STOP (review) |
| 6 | Routing | Check auto_advance → Next task or STOP | Next action decided | → Step 2 (next task) or END |

**⛔ BLOCKING RULES:**
- Step 1 → Step 2: BLOCKED if task not created on task-board.md
- Step 3 → Step 4: BLOCKED if task-board-management skill not loaded
- Step 4 → Step 5: BLOCKED if task-board.md not updated

**⚠️ CRITICAL: Step 1 MUST create tasks on the board BEFORE any work begins.**
**Step 2 will BLOCK if tasks are not found on the board.**

---

### Step 1: Task Planning

**Trigger:** Receive work request from human or system

**Process:**
```
1. Match request to task type using Task Types Registry below
2. Derive category from task type suffix
3. Check task:
   - IF task not exists → Create with status: pending
   - ELSE IF exists AND assigned to you → Continue
   - ELSE → STOP
4. **[MANDATORY]** Load task-board-management skill to create/update tasks on board
   → This step CANNOT be skipped
   → Tasks MUST appear on board BEFORE proceeding to Step 2
5. IF task type defines next_task_type → Create ALL chained tasks upfront
6. **[VERIFICATION]** Confirm all tasks are visible on task board before proceeding
```

**Request Matching Examples:**

| Request Pattern | Task Type |
|-----------------|-----------|
| "new feature", "add feature" | Requirement Gathering |
| "break down", "split features" | Feature Breakdown |
| "refine", "clarify requirements" | Feature Refinement |
| "design", "architecture" | Technical Design |
| "implement", "code", "build" | Code Implementation |
| "playground", "demo", "test manually" | Human Playground |
| "close feature", "create PR" | Feature Closing |
| "fix bug", "not working" | Bug Fix |
| "set up project", "initialize" | Project Initialization |

**Output:** Task Data Model with core fields populated AND tasks created on board

---

### Step 2: Check Global DoR

**⚠️ GATE CHECK: This step validates that Step 1 was completed correctly.**

**Prerequisites (ALL must be checked):**
- [ ] Task exists on task board ← **IF MISSING: STOP, go back to Step 1**
- [ ] Task status is `pending` or `blocked` (valid for starting)
- [ ] Git repository initialized (invoke git-version-control skill if needed)

**Task Board Verification:**
```
1. Read task board at docs/planning/task-board.md
2. Search for task_id in Active Tasks section
3. IF task NOT found:
   → ⛔ STOP execution
   → Log: "Task {task_id} not found on board. Returning to Step 1."
   → Return to Step 1 and create task on board
4. IF task found but status is not pending/blocked:
   → ⛔ STOP execution
   → Log: "Task {task_id} has invalid status for starting: {status}"
```

**Git Repository Check:**
```
CALL git-version-control skill:
  operation: status
  directory: {project_root}

IF not a git repository:
  CALL git-version-control skill:
    operation: init
    directory: {project_root}
  
  CALL git-version-control skill:
    operation: create_gitignore
    directory: {project_root}
    tech_stack: {detect from project or ask human}
```

**On Failure:** STOP and report missing prerequisites

**On Success:** Transition task status: `pending → in_progress`

---

### Step 3: Task Work Execution

**Process:**
```
1. Load task type skill: task-type-{task_type} or task-type-{task_type}-@{category}
2. Pass Task Data Model to skill
3. Check task type DoR (defined in skill)
4. Execute core work (defined in skill)
5. Check task type DoD (defined in skill)
6. Collect skill output into Task Data Model
```

**Task Type Skill Output Contract:**
Each task type skill MUST return:
```yaml
Output:
  status: <new status>
  next_task_type: <task type> | null
  require_human_review: true | false
  task_output_links: [<links>] | null
  # Plus any dynamic attributes the skill defines
  {dynamic_attribute_1}: <value>
  {dynamic_attribute_2}: <value>
  ...
```

**Output:** Task Data Model updated with execution results

---

### Step 4: Category Closing

**Process:**
```
1. MANDATORY: Load skill task-board-management
   → Update task status on board
   → Pass Task Data Model

2. IF category != "Standalone":
   TRY:
     → Load skill @{category}+{category-skill-name}
     → Pass Task Data Model
     → Collect category_level_change_summary
   CATCH SkillNotFound:
     → Log: "No category-level skill found for {category}, skipping"
     → Continue without error (category_level_change_summary = null)
```

**Category Skill Mapping:**

| Category | Additional Skill | Required? |
|----------|------------------|-----------|
| Standalone | (none) | N/A |
| feature-stage | `@feature-stage+feature-board-management` | Yes (must exist) |
| requirement-stage | `@requirement-stage+requirement-board-management` | No (optional, disabled) |

**Notes:**
- If category skill not found, execution continues without error
- This allows requirement-stage tasks to work without requirement board management
- Category-level change summary will be null if skill is skipped

**Output:** `category_level_change_summary` added to Task Data Model (or null if skipped)

---

### Step 5: Check Global DoD

**Validation:**
- [ ] Task status updated on task board
- [ ] Category-level changes committed (if applicable)
- [ ] All task type DoD met
- [ ] Changes committed to git (if files were created/modified)

**Git Commit Check:**
```
IF task_output_links is NOT empty AND files were created/modified:
  CALL git-version-control skill:
    operation: add
    directory: {project_root}
    files: null  # Stage all changes
  
  CALL git-version-control skill:
    operation: commit
    directory: {project_root}
    task_data:
      task_id: {task_id}
      task_description: {task_description}
      feature_id: {feature_id | null}
      # Pass full Task Data Model for context

OPTIONAL - Push to remote (based on project settings or human preference):
  IF auto_push = true:
    CALL git-version-control skill:
      operation: push
      directory: {project_root}
```

**Human Review Check:**
```
IF require_human_review = true AND auto_advance = false:
   → Output summary and STOP for human review
```

**Agent Output (Standard Summary):**
```
> Task ID: <task_id>
> Task Type: <task_type>
> Description: <task_description>
> Category: <category>
> Assignee: <role_assigned>
> Status: <status>
> Category Changes: <category_level_change_summary>
> Require Human Review: <require_human_review>
> Task Output Links: <task_output_links>
> Auto Advance: <auto_advance>
> --- Dynamic Attributes ---
> <attr_1>: <value>
> <attr_2>: <value>
> ...
```

---

### Step 6: Task Routing

**Process:**
```
IF auto_advance = true AND next_task_type EXISTS:
   → Find next task on board (already created in Step 1)
   → Start execution from Step 2
ELSE:
   → STOP (wait for human)
```

---

## Task Types Registry

| Task Type | Skill | Category | Next Task | Human Review |
|-----------|-------|----------|-----------|--------------|
| Requirement Gathering | `task-type-requirement-gathering-@requirement-stage` | requirement-stage | Feature Breakdown | Yes |
| Feature Breakdown | `task-type-feature-breakdown-@requirement-stage` | requirement-stage | Feature Refinement | Yes |
| Feature Refinement | `task-type-feature-refinement-@feature-stage` | feature-stage | Technical Design | Yes |
| Technical Design | `task-type-technical-design-@feature-stage` | feature-stage | Test Generation | Yes |
| Test Generation | `task-type-test-generation-@feature-stage` | feature-stage | Code Implementation | No |
| Code Implementation | `task-type-code-implementation-@feature-stage` | feature-stage | Human Playground | No |
| Human Playground | `task-type-human-playground-@feature-stage` | feature-stage | Feature Closing | Yes |
| Feature Closing | `task-type-feature-closing-@feature-stage` | feature-stage | User Manual | No |
| Bug Fix | `task-type-bug-fix` | Standalone | - | Yes |
| Project Initialization | `task-type-project-init` | Standalone | Dev Environment | No |
| Dev Environment | `task-type-dev-environment` | Standalone | - | No |
| User Manual | `task-type-user-manual` | Standalone | - | Yes |

---

## Quick Example

### Scenario: "Implement the user login feature"

**Step 1: Planning**
```
Match: "implement" → Code Implementation
Category: feature-stage (from suffix -@feature-stage)
Description: "Implement user login feature with authentication"

⚠️ MANDATORY: Create tasks on board BEFORE proceeding
→ Load task-board-management skill
→ Create: TASK-001 (Code Implementation) - status: pending
→ Create: TASK-002 (Human Playground) - status: pending
→ Create: TASK-003 (Feature Closing) - status: pending
→ Verify all 3 tasks appear in Active Tasks section of task-board.md
```

**Step 2: DoR**
```
✓ Read task-board.md
✓ Find TASK-001 in Active Tasks section
✓ Confirm status: pending (valid for starting)
✓ Git repository initialized
→ Update TASK-001 status: pending → in_progress
```

**Step 3: Execute**
```
Load: task-type-code-implementation-@feature-stage
Work: Write code, tests
Output:
  status: completed
  next_task_type: Human Playground
  require_human_review: false
  task_output_links: [src/auth/login.ts, tests/auth/login.test.ts]
  feature_id: FEATURE-001
  feature_phase: Code Implementation
```

**Step 4: Closing**
```
Load: task-board-management → Update TASK-001 to completed
Load: @feature-stage+feature-board-management → Update feature status
Output:
  category_level_change_summary: "FEATURE-001 updated to Done Code Implementation"
```

**Step 5: DoD**
```
✓ Board updated
✓ Feature board updated
Output standard summary
```

**Step 6: Routing**
```
auto_advance = true, next_task_type = Human Playground
→ Start TASK-002 from Step 2
```

---

## Templates

- `templates/task-record.yaml` - Task data template
- `templates/task-board.md` - Task tracking board
