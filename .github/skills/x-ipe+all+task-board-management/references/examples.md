# Task Board Management - Examples

## Example 1: Create Task Board and First Task

**Request:** "Start tracking a new feature implementation"

```
Step 1: Locate Task Board
  -> Not found at x-ipe-docs/planning/task-board.md
  -> Trigger Init Task Board operation

Step 2: Create Task
  -> task_based_skill: Code Implementation
  -> role_assigned: Nova
  -> Generate task_id: TASK-001
  -> status: pending
  -> next_task_based_skill: Feature Closing

Result: Board created at x-ipe-docs/planning/task-board.md with TASK-001
```

---

## Example 2: Update Task Status

**Request:** "Mark TASK-001 as in progress"

```
Step 1: Locate Task Board
  -> Found at x-ipe-docs/planning/task-board.md

Step 2: Find Task
  -> TASK-001 found in Active Tasks

Step 3: Validate Transition
  -> pending -> in_progress (Valid)

Step 4: Update
  -> status: in_progress
  -> last_updated: 2026-01-15T10:30:00

Result: TASK-001 now in_progress
```

---

## Example 3: Complete Task and Move

**Request:** "Complete TASK-001"

```
Step 1: Locate Task Board
  -> Found at x-ipe-docs/planning/task-board.md

Step 2: Find Task
  -> TASK-001 found in Active Tasks

Step 3: Validate Transition
  -> in_progress -> completed (Valid)

Step 4: Update
  -> status: completed
  -> last_updated: 2026-01-15T11:00:00
  -> Move from Active Tasks to Completed Tasks

Step 5: Update Stats
  -> Total Active: -1
  -> Completed Today: +1

Result: TASK-001 moved to Completed Tasks
```

---

## Example 4: Query Tasks

**Request:** "Show all blocked tasks"

```
Step 1: Locate Task Board
  -> Found at x-ipe-docs/planning/task-board.md

Step 2: Query
  -> Filter: status = blocked
  -> Search Active Tasks section

Result:
  - TASK-003: Technical Design (blocked)
  - TASK-007: Code Implementation (blocked)
```

---

## Example 5: Board Integrity Validation

**Scenario:** Task board has misplaced tasks after manual edits

```
Initial State (corrupted):
  Active Tasks:
    - TASK-001: Code Implementation | completed   <- WRONG
    - TASK-002: Bug Fix | in_progress
    - TASK-003: Feature Closing | cancelled        <- WRONG

  Completed Tasks:
    - TASK-004: Technical Design | in_progress     <- WRONG

Step 1: Scan Active Tasks
  -> TASK-001 status=completed -> Move to Completed Tasks
  -> TASK-003 status=cancelled -> Move to Cancelled Tasks

Step 2: Scan Completed Tasks
  -> TASK-004 status=in_progress -> Move to Active Tasks

Step 3: Reconcile Stats
  -> Total Active: 2 (was showing 3)
  -> Corrected

Result:
  Active Tasks:
    - TASK-002: Bug Fix | in_progress
    - TASK-004: Technical Design | in_progress

  Completed Tasks:
    - TASK-001: Code Implementation | completed

  Cancelled Tasks:
    - TASK-003: Feature Closing | cancelled

Validation Report:
  tasks_fixed: [TASK-001, TASK-003, TASK-004]
  stats_corrected: true
```
