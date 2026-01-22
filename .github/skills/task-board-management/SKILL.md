---
name: task-board-management
description: Manage task boards for tracking development work. This is a MANDATORY skill called during Step 4 (Category Closing) of the task lifecycle. Accepts Task Data Model as input. Provides operations for task board CRUD, task state management, and board queries.
---

# Task Board Management

## Purpose

AI Agents follow this skill to manage task boards - the central tracking system for all development work. This skill is **MANDATORY** and is always executed during Step 4 (Category Closing) of the task lifecycle.

**Operations:**
1. **Locate** or create task boards
2. **Create** tasks on the board
3. **Update** task states and properties
4. **Query** tasks by various criteria

---

## Important Notes

**Important:** This skill is the foundation for all task execution. when executing any task type skill, the agent MUST follow the general workflow mentioned below to ensure every steps are fully covered.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Input: Task Data Model

This skill receives the Task Data Model from task execution:

```yaml
Task:
  # Core fields
  task_id: TASK-XXX
  task_type: <Task Type>
  task_description: <≤50 words>
  category: <category>
  role_assigned: <Role Name>
  status: <status>
  last_updated: <MM-DD-YYYY HH:MM:SS>
  
  # Execution fields (from task type skill)
  next_task_type: <Task Type> | null
  require_human_review: true | false
  task_output_links: [<links>] | null
  {Dynamic Attributes}: <from task type skill>
  
  # Control fields
  auto_advance: true | false
```

---

## Task States

| State | Terminal? | Description |
|-------|-----------|-------------|
| `pending` | No | Created, waiting |
| `in_progress` | No | Being worked on |
| `blocked` | No | Waiting for dependency |
| `deferred` | No | Human paused |
| `completed` | Yes | Done |
| `cancelled` | Yes | Stopped |

### Valid Transitions

```
pending → in_progress
in_progress → completed | blocked | deferred | cancelled
blocked → in_progress
deferred → in_progress
```

---

## Task Board Operations

### Operation 1: Init Task Board

**When:** No task board exists
**Then:** Create from template

```
1. Use template from `templates/task-board.md`
2. Create at `docs/planning/task-board.md`
3. Initialize with default settings:
    - auto_advance: false
    - Empty task lists
4. Return board location
```

### Operation 2: Locate Task Board

**When:** Need to access task board
**Then:** Find or create board

```
1. Most of the time, task board is at `/docs/planning/task-board.md``
2. IF not found:
   → Trigger Operation 1: Init Task Board
3. Return board location
```

### Operation 3: Create Task

**When:** New task needed (Step 1: Task Planning)
**Then:** Add to board

```
Input: Task Data Model (from planning)

Process:
1. Locate task board
2. Generate next task_id (TASK-XXX format)
3. Create task record with:
   - task_id, task_type, category
   - role_assigned, status: pending
   - last_updated: current timestamp
4. Add to Active Tasks section
5. Update Quick Stats
```

**Task ID Generation:**
```
1. Find highest existing TASK-XXX number
2. Increment by 1
3. Format as TASK-XXX (zero-padded 3 digits)
   Example: TASK-001, TASK-002, ..., TASK-999
```

### Operation 4: Update Task Status

**When:** Task state changes (Step 4: Category Closing)
**Then:** Update board with Task Data Model

```
Input: Task Data Model (from task execution)

Process:
1. Locate task on board by task_id
2. Validate state transition
3. Update all fields from Task Data Model:
   - status, last_updated
   - task_output_links
   - category (if changed)
4. IF status is terminal (completed/cancelled):
   → Move to appropriate section
   → Add category_level_change_summary to notes
5. Update Quick Stats
```

### Operation 5: Query Tasks

**When:** Need task information
**Then:** Search board

```
Query Types:
1. By task_id: Find specific task
2. By status: List all tasks with status
3. By task_type: List all tasks of type
4. By role: List all tasks assigned to role
5. All active: List non-terminal tasks

Return: Matching task(s) or empty if none found
```

### Operation 6: Update Auto-Advance

**When:** Changing advance behavior
**Then:** Update board setting

```
Input:
  - auto_advance: true | false

Process:
1. Locate task board
2. Update auto_advance in Global Settings
3. Confirm change
```

---

## Task Board Sections

The task board has these sections:

### Global Settings
```yaml
auto_advance: false  # Controls task chaining
```

### Active Tasks
| Task ID | Task Type | Category | Role | Status | Next Task |
|---------|-----------|----------|------|--------|-----------|

Contains: pending, in_progress, blocked, deferred tasks

### Completed Tasks
| Task ID | Task Type | Category | Completed | Category Changes |
|---------|-----------|----------|-----------|------------------|

Contains: Tasks with status = completed

### Cancelled Tasks
| Task ID | Task Type | Reason | Cancelled |
|---------|-----------|--------|-----------|

Contains: Tasks with status = cancelled

---

## Status Symbols

| Status | Symbol | Description |
|--------|--------|-------------|
| pending | ⏳ | Waiting to start |
| in_progress | 🔄 | Working |
| blocked | 🚫 | Waiting for dependency |
| deferred | ⏸️ | Paused by human |
| completed | ✅ | Done |
| cancelled | ❌ | Stopped |

---

## Category Legend

| Category | Description |
|----------|-------------|
| Standalone | No additional board tracking |
| feature-stage | Updates feature board via @feature-stage+feature-board-management |
| requirement-stage | Updates requirement board via @requirement-stage+requirement-board-management |

---

## Templates

- `templates/task-board.md` - Task board template
- `templates/task-record.yaml` - Individual task template

---

## Examples

### Example 1: Create Task Board and First Task

**Request:** "Start tracking a new feature implementation"

```
Step 1: Locate Task Board
→ Not found in project root
→ Not found in docs/ or .github/
→ Create new board

Step 2: Create Task
→ task_type: Code Implementation
→ role_assigned: Nova
→ Generate task_id: TASK-001
→ status: pending
→ next_task_type: Human Playground

Result: Board created at task-board.md with TASK-001
```

### Example 2: Update Task Status

**Request:** "Mark TASK-001 as in progress"

```
Step 1: Locate Task Board
→ Found at task-board.md

Step 2: Find Task
→ TASK-001 found in Active Tasks

Step 3: Validate Transition
→ pending → in_progress ✓ Valid

Step 4: Update
→ status: in_progress
→ last_updated: 2026-01-15T10:30:00

Result: TASK-001 now in_progress
```

### Example 3: Complete Task and Move

**Request:** "Complete TASK-001"

```
Step 1: Locate Task Board
→ Found at task-board.md

Step 2: Find Task
→ TASK-001 found in Active Tasks

Step 3: Validate Transition
→ in_progress → completed ✓ Valid

Step 4: Update
→ status: completed
→ last_updated: 2026-01-15T11:00:00
→ Move from Active Tasks to Completed Tasks

Step 5: Update Stats
→ Total Active: -1
→ Completed Today: +1

Result: TASK-001 moved to Completed Tasks
```

### Example 4: Query Tasks

**Request:** "Show all blocked tasks"

```
Step 1: Locate Task Board
→ Found at task-board.md

Step 2: Query
→ Filter: status = blocked
→ Search Active Tasks section

Result:
- TASK-003: Technical Design (blocked)
- TASK-007: Code Implementation (blocked)
```

### Example 5: Board After Multiple Operations

```yaml
Task_Board:
  auto_advance: true
  
  Active Tasks:
    - TASK-002: Human Playground | Nova | in_progress | Feature Closing
    - TASK-003: Feature Closing | Nova | pending | null
    - TASK-004: Bug Fix | Nova | blocked | null
  
  Completed Tasks:
    - TASK-001: Code Implementation | Nova | 2026-01-15 | Feature done
  
  Cancelled Tasks:
    - (none)
  
  Quick Stats:
    - Total Active: 3
    - In Progress: 1
    - Blocked: 1
    - Completed Today: 1
```
