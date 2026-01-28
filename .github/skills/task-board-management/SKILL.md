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
  auto_proceed: true | false
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
2. Create at `x-ipe-docs/planning/task-board.md`
3. Initialize with default settings:
    - auto_proceed: false
    - Empty task lists
4. Return board location
```

### Operation 2: Locate Task Board

**When:** Need to access task board
**Then:** Find or create board

```
1. Most of the time, task board is at `/x-ipe-docs/planning/task-board.md``
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
4. ⚠️ CRITICAL - Handle terminal status:
   IF status = completed:
     → REMOVE task row from "Active Tasks" section
     → ADD task row to "Completed Tasks" section
     → Include category_level_change_summary in Notes column
   IF status = cancelled:
     → REMOVE task row from "Active Tasks" section  
     → ADD task row to "Cancelled Tasks" section
     → Include cancellation reason in Reason column
5. Update Quick Stats:
   - Decrement Total Active (if moved out of Active)
   - Increment Completed Today (if completed)
```

**IMPORTANT:** Completed tasks must be MOVED (deleted from Active, added to Completed), 
NOT just have their status updated while remaining in the Active Tasks section.

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

### Operation 6: Update Auto-Proceed

**When:** Changing advance behavior
**Then:** Update board setting

```
Input:
  - auto_proceed: true | false

Process:
1. Locate task board
2. Update auto_proceed in Global Settings
3. Confirm change
```

### Operation 7: Validate Board Integrity (DoD Check)

**When:** ANY operation is performed on the task board
**Then:** Validate and fix misplaced tasks

```
Process:
1. Scan Active Tasks section:
   FOR each task in Active Tasks:
     IF status = completed:
       → MOVE to Completed Tasks section
       → Log: "Fixed: TASK-XXX moved to Completed"
     IF status = cancelled:
       → MOVE to Cancelled Tasks section
       → Log: "Fixed: TASK-XXX moved to Cancelled"

2. Scan Completed Tasks section:
   FOR each task in Completed Tasks:
     IF status ≠ completed:
       → MOVE back to Active Tasks section
       → Log: "Fixed: TASK-XXX moved to Active"

3. Scan Cancelled Tasks section:
   FOR each task in Cancelled Tasks:
     IF status ≠ cancelled:
       → MOVE back to Active Tasks section
       → Log: "Fixed: TASK-XXX moved to Active"

4. Reconcile Quick Stats:
   - Count actual tasks in each section
   - Update stats if mismatched
   - Log any corrections made

5. Return validation report:
   - tasks_fixed: [list of moved tasks]
   - stats_corrected: true | false
```

**⚠️ MANDATORY:** This operation runs automatically as the final step of ALL other operations (Create, Update, Query, etc.) to ensure board integrity.

---

## Task Board Sections

The task board has these sections:

### Global Settings
```yaml
auto_proceed: false  # Controls task chaining
```

### Active Tasks
| Task ID | Task Type | Category | Role | Status | Next Task |
|---------|-----------|----------|------|--------|-----------|

Contains: pending, in_progress, blocked, deferred tasks ONLY
⛔ **NEVER contains completed or cancelled tasks**

### Completed Tasks
| Task ID | Task Type | Category | Completed | Category Changes |
|---------|-----------|----------|-----------|------------------|

Contains: Tasks with status = completed ONLY
✅ **Tasks MUST be moved here when completed (removed from Active)**

### Cancelled Tasks
| Task ID | Task Type | Reason | Cancelled |
|---------|-----------|--------|-----------|

Contains: Tasks with status = cancelled ONLY
❌ **Tasks MUST be moved here when cancelled (removed from Active)**

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
| feature-stage | Updates feature board via feature-stage+feature-board-management |
| requirement-stage | Updates requirement board via requirement-stage+requirement-board-management |

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
→ Not found in x-ipe-docs/ or .github/
→ Create new board

Step 2: Create Task
→ task_type: Code Implementation
→ role_assigned: Nova
→ Generate task_id: TASK-001
→ status: pending
→ next_task_type: Feature Closing

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

### Example 6: Board Integrity Validation

**Scenario:** Task board has misplaced tasks after manual edits

```
Initial State (corrupted):
  Active Tasks:
    - TASK-001: Code Implementation | ✅ completed  ← WRONG!
    - TASK-002: Bug Fix | 🔄 in_progress
    - TASK-003: Feature Closing | ❌ cancelled  ← WRONG!
  
  Completed Tasks:
    - TASK-004: Technical Design | 🔄 in_progress  ← WRONG!

Step 1: Scan Active Tasks
→ TASK-001 status=completed → Move to Completed Tasks
→ TASK-003 status=cancelled → Move to Cancelled Tasks

Step 2: Scan Completed Tasks
→ TASK-004 status=in_progress → Move to Active Tasks

Step 3: Reconcile Stats
→ Total Active: 2 (was showing 3)
→ Corrected

Result:
  Active Tasks:
    - TASK-002: Bug Fix | 🔄 in_progress
    - TASK-004: Technical Design | 🔄 in_progress
  
  Completed Tasks:
    - TASK-001: Code Implementation | ✅ completed
  
  Cancelled Tasks:
    - TASK-003: Feature Closing | ❌ cancelled

Validation Report:
  tasks_fixed: [TASK-001, TASK-003, TASK-004]
  stats_corrected: true
```
