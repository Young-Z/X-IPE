---
title: "Context Menu Manual Override"
section: "04-core-features"
extraction_round: 2
source_files:
  - src/x_ipe/static/js/features/workflow-stage.js
---

# Context Menu — Manual Override

## Overview

Right-clicking any workflow action button reveals a context menu that allows you to manually override the action's status. This is useful for recovering from stuck actions or correcting incorrect states.

## How to Use

1. **Right-click** on any action button in the workflow view (shared actions or feature lane steps)
2. A context menu appears at your cursor position with two options:
   - ✅ **Mark as Done** — Forces the action status to "done"
   - 🔄 **Reset to Pending** — Reverts the action to "pending"
3. Click an option → the action status updates immediately
4. The workflow view re-renders to reflect the change

## When to Use

| Scenario | Action |
|----------|--------|
| Action stuck in "in_progress" | Right-click → **Mark as Done** or **Reset to Pending** |
| AI completed work but didn't update status | Right-click → **Mark as Done** |
| Want to re-run an action | Right-click → **Reset to Pending** |
| Accidentally triggered an action | Right-click → **Reset to Pending** |

## Backend API Call

When you select a context menu option, the UI sends:

```
POST /api/workflow/{workflowName}/action
Body: {
  "action": "compose_idea",       // action key
  "status": "done" | "pending",   // new status
  "feature_id": "FEATURE-050-A"   // only for feature-lane actions
}
```

## Error Handling

- On success: workflow view re-renders with updated status
- On error: Toast message appears: "Failed to update action status"
- Menu is always removed after selection (regardless of success/failure)

## UI Details

| Element | Selector | Description |
|---------|----------|-------------|
| Menu container | `.wf-context-menu` | Positioned at cursor |
| Menu items | `.wf-context-menu-item` | Clickable options |
| Positioning | `Math.min()` viewport bounds | Menu stays within window |

## Important Notes

- Context menu works on **both** shared actions (ideation, requirement) and feature lane actions
- For feature lane actions, the `feature_id` is automatically included
- This does NOT bypass stage gating — if you mark an action as done, the stage may still require other actions to complete
- The menu dismisses when clicking anywhere outside it
