---
name: x-ipe+all+task-board-management
description: Manage task boards for tracking development work. Accepts Task Data Model as input. Provides operations for task board CRUD, task state management, and board queries. Triggers on "create task", "update task", "query tasks", "init task board", "validate board".
---

# Task Board Management

## Purpose

AI Agents follow this skill to manage task boards — the central tracking system for all development work:
1. **Locate** or create task boards
2. **Create** tasks on the board
3. **Update** task states and properties
4. **Query** tasks by various criteria
5. **Validate** board integrity

---

## Important Notes

MANDATORY: This skill is the foundation for all task execution. When executing any task-based skill, the agent MUST use this skill to track work on the task board.

BLOCKING: If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point for each skill.

---

## About

The task board at `x-ipe-docs/planning/task-board.md` is the single source of truth for all development work.

**Key Concepts:**

- **Task Data Model** — Structured input containing task_id, task_based_skill, category, status, and execution fields
- **Task States** — `pending`, `in_progress`, `blocked`, `deferred` (non-terminal); `completed`, `cancelled` (terminal)
- **Valid Transitions** — `pending -> in_progress`; `in_progress -> completed | blocked | deferred | cancelled`; `blocked -> in_progress`; `deferred -> in_progress`
- **Board Sections** — Global Settings, Active Tasks, Completed Tasks, Cancelled Tasks
- **Active Tasks** — Contains ONLY non-terminal tasks (pending, in_progress, blocked, deferred). CRITICAL: Never contains completed or cancelled tasks.
- **Completed Tasks** — Contains ONLY tasks with status = completed. Tasks MUST be moved here from Active when completed.
- **Cancelled Tasks** — Contains ONLY tasks with status = cancelled. Tasks MUST be moved here from Active when cancelled.
- **Status Symbols** — pending: `⏳`, in_progress: `🔄`, blocked: `🚫`, deferred: `⏸️`, completed: `✅`, cancelled: `❌`
- **Categories** — `Standalone` (no additional board tracking), `feature-stage` (updates feature board), `requirement-stage` (updates requirement board)

---

## When to Use

```yaml
triggers:
  - "create task"
  - "update task"
  - "query tasks"
  - "init task board"
  - "validate board"
  - "update auto-proceed"
  - "complete task"
  - "cancel task"

not_for:
  - "Feature board management (use feature-board-management)"
  - "Requirement board management (use requirement-board-management)"
```

---

## Input Parameters

```yaml
input:
  operation: "init_board | locate_board | create_task | update_status | query_tasks | update_auto_proceed | validate_integrity"
  task:
    task_id: "TASK-XXX"
    task_based_skill: "{task_based_skill}"
    task_description: "{description, max 50 words}"
    category: "{Standalone | feature-stage | requirement-stage}"
    role_assigned: "{role_name}"
    status: "{pending | in_progress | blocked | deferred | completed | cancelled}"
    last_updated: "{MM-DD-YYYY HH:MM:SS}"
    next_task_based_skill: "{task_based_skill} | null"
    require_human_review: "true | false"
    task_output_links: "[{links}] | null"
    auto_proceed: "true | false"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Task Data Model provided</name>
    <verification>Input contains required fields: task_based_skill, category, role_assigned, status</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Operation identified</name>
    <verification>Caller specifies which operation to perform</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Board location known or discoverable</name>
    <verification>x-ipe-docs/planning/task-board.md exists or can be created</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Init Task Board

**When:** No task board exists

```xml
<operation name="init_board">
  <action>
    1. Use template from `templates/task-board.md`
    2. Create at `x-ipe-docs/planning/task-board.md`
    3. Initialize with default settings: auto_proceed: false, empty task lists
  </action>
  <output>Board file path</output>
</operation>
```

### Operation: Locate Task Board

**When:** Need to access the task board

```xml
<operation name="locate_board">
  <action>
    1. Check for board at `x-ipe-docs/planning/task-board.md`
    2. IF not found: trigger init_board operation
  </action>
  <output>Board file path</output>
</operation>
```

### Operation: Create Task

**When:** New task needed (Step 1: Task Planning)

```xml
<operation name="create_task">
  <action>
    1. Locate task board
    2. Generate next task_id: find highest TASK-XXX number, increment by 1, zero-pad to 3 digits
    3. Create task record with: task_id, task_based_skill, category, role_assigned, status: pending, last_updated: current timestamp
    4. Add to Active Tasks section
    5. Update Quick Stats
    6. Run validate_integrity operation
  </action>
  <constraints>
    - BLOCKING: task_id must be unique
    - BLOCKING: New tasks always start with status: pending
  </constraints>
  <output>Created task_id and board location</output>
</operation>
```

### Operation: Update Task Status

**When:** Task state changes (Step 4: Category Closing)

```xml
<operation name="update_status">
  <action>
    1. Locate task on board by task_id
    2. Validate state transition against valid transitions
    3. Update fields from Task Data Model: status, last_updated, task_output_links, category
    4. Handle terminal status:
       IF status = completed: REMOVE from Active Tasks, ADD to Completed Tasks with category_level_change_summary in Notes
       IF status = cancelled: REMOVE from Active Tasks, ADD to Cancelled Tasks with reason in Reason column
    5. Update Quick Stats: decrement Total Active (if moved), increment Completed Today (if completed)
    6. Run validate_integrity operation
  </action>
  <constraints>
    - CRITICAL: Completed tasks must be MOVED (deleted from Active, added to Completed), NOT just status-updated in place
    - BLOCKING: State transition must be valid per transition rules
  </constraints>
  <output>Updated task record</output>
</operation>
```

### Operation: Query Tasks

**When:** Need task information

```xml
<operation name="query_tasks">
  <action>
    1. Locate task board
    2. Search by query type:
       - By task_id: find specific task
       - By status: list all tasks with given status
       - By task_based_skill: list all tasks of given type
       - By role: list all tasks assigned to role
       - All active: list all non-terminal tasks
  </action>
  <output>Matching task(s) or empty list</output>
</operation>
```

### Operation: Update Auto-Proceed

**When:** Changing task chaining behavior

```xml
<operation name="update_auto_proceed">
  <action>
    1. Locate task board
    2. Update auto_proceed value in Global Settings section
    3. Confirm change
  </action>
  <output>Updated auto_proceed value</output>
</operation>
```

### Operation: Validate Board Integrity

**When:** After ANY other operation is performed on the task board

```xml
<operation name="validate_integrity">
  <action>
    1. Scan Active Tasks: IF any task has status completed -> move to Completed Tasks; IF status cancelled -> move to Cancelled Tasks
    2. Scan Completed Tasks: IF any task has status != completed -> move back to Active Tasks
    3. Scan Cancelled Tasks: IF any task has status != cancelled -> move back to Active Tasks
    4. Reconcile Quick Stats: count actual tasks in each section, update if mismatched
  </action>
  <constraints>
    - MANDATORY: Runs automatically as final step of ALL other operations
  </constraints>
  <output>Validation report: tasks_fixed list, stats_corrected boolean</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "{operation_name}"
  result:
    board_path: "x-ipe-docs/planning/task-board.md"
    task_id: "TASK-XXX"
    status: "{new_status}"
    tasks_fixed: []
    stats_corrected: false
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed successfully</name>
    <verification>operation_output.success is true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Board integrity validated</name>
    <verification>validate_integrity ran after the operation with no remaining issues</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Quick Stats accurate</name>
    <verification>Task counts in Quick Stats match actual tasks in each section</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No terminal tasks in Active</name>
    <verification>Active Tasks section contains zero completed or cancelled tasks</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `BOARD_NOT_FOUND` | Task board file missing | Run init_board operation to create from template |
| `INVALID_TRANSITION` | State transition not in valid transitions | Reject update; return current state and valid transitions |
| `DUPLICATE_TASK_ID` | Generated task_id already exists | Re-scan for highest ID and increment again |
| `TASK_NOT_FOUND` | task_id not found on board | Return error with task_id; suggest query_tasks to find |
| `INTEGRITY_VIOLATION` | Terminal task in Active or non-terminal in Completed/Cancelled | Auto-fix via validate_integrity operation |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/task-board.md` | Task board template with sections and default settings |
| `templates/task-record.yaml` | Individual task record template |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
