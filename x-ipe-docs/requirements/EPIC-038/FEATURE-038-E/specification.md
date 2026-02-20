# Feature Specification: Execution Skill DoD Update

> Feature ID: FEATURE-038-E
> Version: v1.0
> Status: Refined
> Last Updated: 02-20-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-20-2026 | Initial specification — workflow status verification checkpoint in task-execution skill |

## Linked Mockups

None — this feature is a skill update with no direct UI.

## Overview

This feature adds a **workflow status verification checkpoint** to the `x-ipe-workflow-task-execution` skill's Step 5 (Check Global DoD). When a completed task-based skill declares workflow action interaction in its `task_completion_output`, the execution workflow should verify that `update_workflow_action` was actually called — i.e., the action status in the workflow JSON is no longer `pending`.

Currently, the task-execution skill checks the task-based skill's DoD but does not verify that external side effects (like MCP workflow status updates) actually happened. This creates a gap where a skill can claim completion without the workflow UI reflecting it.

This is a **standalone skill update** — modifies `.github/skills/x-ipe-workflow-task-execution/SKILL.md` only.

**Target Users:**
- AI Agents following the task-execution workflow
- Workflow system requiring consistent status across task board and workflow JSON

## User Stories

- **US-038-E.1:** As the workflow system, I want task completion to verify that workflow action status was updated, so that the UI accurately reflects execution state.
- **US-038-E.2:** As a developer debugging a failed workflow update, I want a clear error message when the status verification fails, so that I know exactly what MCP call was missed.

## Acceptance Criteria

- [ ] AC-038-E.1: `x-ipe-workflow-task-execution` Step 5 includes a new checkpoint: "Workflow Status Verification"
- [ ] AC-038-E.2: Checkpoint activates only when the completed skill's `task_completion_output` declares a `workflow_action` field (or equivalent indicator of workflow interaction)
- [ ] AC-038-E.3: Verification reads the workflow JSON file (`instance/workflows/workflow-{name}.json`) and checks that the relevant action status is NOT `pending`
- [ ] AC-038-E.4: If verification fails (status still `pending`), the task is flagged as incomplete with message: "Workflow action status not updated. Call update_workflow_action MCP before completing."
- [ ] AC-038-E.5: If the completed skill does NOT declare workflow interaction, the checkpoint is skipped (no false positives)
- [ ] AC-038-E.6: Skill update follows the candidate workflow (edit in `x-ipe-docs/skill-meta/` → validate → merge)

## Functional Requirements

**FR-038-E.1: Workflow Interaction Detection**
- Input: Completed skill's `task_completion_output` YAML
- Process: Check for presence of `workflow_action` or `workflow_name` field in the output declaration
- Output: Boolean indicating whether workflow verification is needed

**FR-038-E.2: Workflow JSON Status Check**
- Input: `workflow_name` and `action_key` from the completed skill's output
- Process: Read `instance/workflows/workflow-{name}.json`, navigate to the action's status field, verify it is NOT `pending`
- Output: `pass` (status updated) or `fail` (status still pending)

**FR-038-E.3: Failure Flagging**
- Input: Verification failure
- Process: Add error message to task completion output, set task status to incomplete/blocked
- Output: Clear error message with remediation instruction

## Non-Functional Requirements

- **NFR-038-E.1:** Skill SKILL.md must stay under 500 lines after changes
- **NFR-038-E.2:** Verification adds no more than 5 lines to the existing Step 5 DoD section

## UI/UX Requirements

None — skill update only.

## Dependencies

### Internal

| Dependency | Type | Description |
|-----------|------|-------------|
| `x-ipe-workflow-task-execution` | Modification target | Step 5 (Check Global DoD) being extended |
| `update_workflow_action` MCP | Referenced | The MCP tool whose execution is being verified |
| `instance/workflows/workflow-{name}.json` | Data source | Workflow state file to check action status |

### External

None.

## Business Rules

- **BR-038-E.1:** Verification only applies when the skill explicitly declares workflow interaction — no implicit inference.
- **BR-038-E.2:** A status of `in_progress` or `done` is considered "updated" (passing). Only `pending` is a failure.
- **BR-038-E.3:** This is an advisory checkpoint — it flags the issue but does not automatically call the MCP.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Workflow JSON file doesn't exist | Skip verification with warning (workflow may not be initialized) |
| Action key not found in workflow JSON | Skip verification with warning (action may be new/unregistered) |
| Skill declares workflow interaction but no workflow_name | Skip verification — cannot locate workflow file |
| Multiple actions declared | Verify each action individually |

## Out of Scope

- **Auto-calling MCP on failure** — only flags the issue
- **Verifying deliverables content** — only checks status field
- **Retrying failed verifications** — one-shot check

## Technical Considerations

- Add 3-5 lines to Step 5's `<action>` block in `x-ipe-workflow-task-execution/SKILL.md`
- Pattern: IF skill output has `workflow_action` → read workflow JSON → check status → flag if pending
- Must go through `x-ipe-meta-skill-creator` candidate workflow
- Workflow JSON path: `instance/workflows/workflow-{workflow_name}.json`

## Open Questions

None.
