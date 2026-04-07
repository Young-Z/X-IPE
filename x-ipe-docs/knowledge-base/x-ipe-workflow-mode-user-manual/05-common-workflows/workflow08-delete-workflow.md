---
title: "Delete Workflow"
section: "05-common-workflows"
extraction_round: 2
---

# Delete a Workflow

## Overview
You can permanently delete a workflow and its state file through the Actions menu.

## Step-by-Step

### Step 1: Open Actions Menu
1. Find the **⋮** (three dots) button on the workflow card header, next to the Interaction Mode dropdown
2. Click the button to open the actions menu

![Actions Menu](screenshots/actions-menu-delete.png)

### Step 2: Click Delete
1. The menu shows **"🗑 Delete"** option
2. Click "Delete"

### Step 3: Confirm
1. A confirmation dialog appears
2. Confirm to proceed with deletion

### Step 4: Result
- Workflow card is removed from the list
- State file (`workflow-{name}.json`) is deleted from disk
- **This action cannot be undone**

## Important Notes

- Deleting a workflow does NOT delete the deliverable files (ideas, requirements, code)
- Deliverable files remain in their original locations (`x-ipe-docs/ideas/`, `x-ipe-docs/requirements/`, etc.)
- Only the workflow state and tracking information is removed
