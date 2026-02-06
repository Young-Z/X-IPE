# Example: Task Status Update (Pattern 1 - YAML)

Demonstrates Pattern 1 (Simple Workflow) with branching logic for status transition validation.

```yaml
workflow:
  name: "Update Task Status"
  steps:
    - step: 1
      name: "Locate Task"
      action: "Find task by {task_id} in task board"
      gate: "task_found == true"
      
    - step: 2
      name: "Validate Transition"
      action: "Check if status transition is valid"
      branch:
        if: "current_status == pending AND new_status == in_progress"
        then: "Valid transition"
        else: "Check transition table"
      gate: "transition_valid == true"
      
    - step: 3
      name: "Update Status"
      action: "Set task.status = {new_status}"
      gate: "status_updated == true"
      
    - step: 4
      name: "Update Timestamp"
      action: "Set task.last_updated = current_time"
      gate: "timestamp_updated == true"

  blocking_rules:
    - "BLOCKING: Invalid transitions must be rejected"
  
  critical_notes:
    - "CRITICAL: Always update timestamp after status change"
```
