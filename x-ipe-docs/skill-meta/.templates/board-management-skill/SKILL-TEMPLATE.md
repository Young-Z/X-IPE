---
name: {category}+{board-name}-board-management
description: Manage {board_name} board (`{board_file_path}`) - central tracking for {what_is_tracked}. Two modes - (1) Category-Level Skill invoked during Step 4 of task execution to update board on task completion, (2) Query Interface called by other skills to provide {Entity} Data Model. Triggers on {category} task completion or when other skills need {entity} status/data.
---

# {Board Name} Board Management

**Board Template:** `templates/{board-name}-board.md`

## {Entity} Data Model

```yaml
{entity_id_field}: {ID_PREFIX}-XXX
title: <Title>
status: {status_1} | {status_2} | ... | {final_status}
description: <Brief description>
dependencies: [{ID_PREFIX}-XXX, ...]  # Optional
{artifact_link_1}: {path} | null       # Optional
created: MM-DD-YYYY
last_updated: MM-DD-YYYY HH:MM:SS
```

## {Entity} Status Lifecycle

```
{status_1} → {status_2} → ... → {final_status}
         ↘ {error_status} (if applicable)
```

| Status | Description | Triggered By |
|--------|-------------|--------------|
| **{status_1}** | {description} | {triggering_task_type} |
| **{status_2}** | {description} | {triggering_task_type} |
| **{final_status}** | {description} | {triggering_task_type} |

## Operations

### Op 1: Locate or Init Board

**When:** Any board operation (always runs first)

1. Check if board exists at `{board_file_path}`
2. IF not exists → Create from `templates/{board-name}-board.md`
3. Return board location

### Op 2: Create or Update {Entity}

**When:** New {entity} needed or existing {entity} changes

| Input | Output |
|-------|--------|
| `{entity_id_field}`, `title`, `description` | Created/updated {entity} with `last_updated` |

Execution: Create board if needed → For each {entity}: exists? Update : Add with `status={initial_status}` → Update timestamp

### Op 3: Query {Entity}

**When:** Need full {Entity} Data Model

| Input | Output |
|-------|--------|
| `{entity_id_field}: {ID_PREFIX}-001` | Full {Entity} Data Model |

### Op 4: Update Status (Category-Level)

**When:** Step 4 (Category Closing) for {category} tasks

**Input (from Task Data Model):**
```yaml
task_id: TASK-XXX
task_type: {Task Type}
category: {category}
status: completed
{entity_id_field}: {ID_PREFIX}-XXX
{phase_field}: {phase_value}
```

**Status Update Logic:**

| {phase_field} | New Status | Link Updates |
|---------------|------------|--------------|
| `{phase_1}` | {status_1} | {link_updates} |
| `{phase_2}` | {status_2} | {link_updates} |

**Output:** `{success, {entity_id_field}, old_status, new_status, summary}`

### Op 5: Validate Board Integrity

**When:** Periodically or before major operations

1. Load board, check all {entities} have required fields
2. Verify status values are valid, check for orphaned references
3. Return: `{valid: bool, issues: [], auto_fixed: []}`

## Board File Structure

**Location:** `{board_file_path}`

| Section | Content |
|---------|---------|
| 1 | Overview/status definitions |
| 2 | {Entity} Tracking Table |
| 3 | Status Details (grouped) |

## Status Symbols

| Status | Symbol |
|--------|--------|
| {status_1} | {emoji} |
| {status_2} | {emoji} |
| {final_status} | {emoji} |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| {Entity} not found | Invalid {entity_id_field} | Check ID exists on board |
| Board file missing | First operation | Auto-creates from template |
| Invalid status transition | Skipped phase | Follow lifecycle order |

## Related Skills

- **task-board-management** - Task tracking (may reference {entities})
- **{related_board}-board-management** - Cross-board relationships
