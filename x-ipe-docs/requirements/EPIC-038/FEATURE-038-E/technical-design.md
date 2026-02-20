# Technical Design: Execution Skill DoD Update

> Feature ID: FEATURE-038-E | Version: v1.0 | Last Updated: 02-20-2026

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating large projects.
> **📌 AI Coders:** Focus on this section for implementation context.

### Key Components Implemented

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| `workflow-task-execution Step 5` | Add workflow status verification checkpoint | Global task execution flow | #workflow #dod #verification #skills |

### Dependencies

| Dependency | Source | Design Link | Usage Description |
|------------|--------|-------------|-------------------|
| `x-ipe-workflow-task-execution` | Foundation | `.github/skills/x-ipe-workflow-task-execution/SKILL.md` | The skill being modified — Step 5 gains new checkpoint |
| `update_workflow_action` MCP | FEATURE-036 | `src/x_ipe/mcp/app_agent_interaction.py` | The MCP tool whose execution is verified |
| Workflow JSON | Runtime | `instance/workflows/workflow-{name}.json` | Status file checked during verification |

### Major Flow

1. Task-based skill completes → task-execution skill reaches Step 5 (Check Global DoD)
2. Step 5 checks if skill's `task_completion_output` declares `workflow_action` field
3. If yes → read `instance/workflows/workflow-{name}.json` → check action status ≠ `pending`
4. If status still `pending` → flag task as incomplete with remediation message
5. If no workflow interaction declared → skip checkpoint (no-op)

### Usage Example

```yaml
# In a task-based skill's Output Result:
task_completion_output:
  workflow_action: "refine_idea"        # <-- triggers verification
  workflow_name: "hello"                # <-- used to locate JSON
  status: completed

# Step 5 verification logic (pseudo):
# IF task_completion_output.workflow_action exists:
#   READ instance/workflows/workflow-{workflow_name}.json
#   CHECK actions[workflow_action].status != "pending"
#   IF still pending → FLAG "Workflow action not updated"
```

---

## Part 2: Implementation Guide

> **Purpose:** Detailed guide for the skill update.

### Change Description

Add 5-7 lines to Step 5's `<action>` block in `x-ipe-workflow-task-execution/SKILL.md`. The change adds a conditional checkpoint that reads the workflow JSON file when the completed skill declares workflow interaction.

### Implementation Steps

1. **Skill Update:** Add workflow verification logic to Step 5 `<action>` numbered list in `.github/skills/x-ipe-workflow-task-execution/SKILL.md`
2. **Candidate Workflow:** All changes go through `x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/candidate/`

### Exact Change Location

In Step 5 (`Check Global DoD`), after existing DoD checkpoints, add:

```
N. IF completed skill's task_completion_output contains workflow_action field:
   a. Extract workflow_name and workflow_action from output
   b. READ instance/workflows/workflow-{workflow_name}.json
   c. CHECK that actions.{workflow_action}.status is NOT "pending"
   d. IF status is "pending" → FLAG task as incomplete:
      "Workflow action '{workflow_action}' status not updated. 
       Call update_workflow_action MCP tool before completing."
   e. IF workflow JSON file not found → WARN and skip (non-blocking)
```

### Edge Cases & Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| Workflow JSON doesn't exist | Skip verification with warning (non-blocking) |
| Action key not in JSON | Skip verification with warning |
| Status is `in_progress` or `done` | Verification passes |
| No `workflow_action` in output | Checkpoint skipped entirely |

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 02-20-2026 | Initial Design | Skill-only update: add workflow status verification checkpoint to task-execution Step 5. No code changes needed. |
