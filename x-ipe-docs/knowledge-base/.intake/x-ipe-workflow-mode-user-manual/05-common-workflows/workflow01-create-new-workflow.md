---
title: "Create New Workflow"
section: "05-common-workflows"
extraction_round: 2
---

# Create New Workflow

## Prerequisites
- X-IPE web app running at `http://127.0.0.1:5858/`
- AI CLI tool connected (console shows "Connected")

## Steps

### Step 1: Switch to Workflow Mode
1. Look at the top header bar
2. Find the **FREE / WORKFLOW** toggle switch
3. Click the toggle to switch to **WORKFLOW** mode
4. The main content area changes from the file browser to "Engineering Workflows" view

![Workflow Mode Overview](screenshots/workflow-mode-overview.png)

### Step 2: Click Create Workflow
1. Click the **"+ Create Workflow"** button at the top of the Engineering Workflows view
2. A modal dialog appears with the title "Create New Workflow"

![Create Workflow Modal](screenshots/create-workflow-modal.png)

### Step 3: Enter Workflow Name
1. Type a descriptive name in the text field (e.g., "E-Commerce Checkout Flow")
2. The placeholder text shows: "e.g., E-Commerce Checkout Flow"
3. The helper text reads: "Choose a descriptive name for your project delivery workflow"

### Step 4: Submit
1. Click **"Create Workflow"** button
2. The modal closes
3. A new workflow card appears in the list

### What Happens After Creation
- Workflow starts at the **Ideation** stage
- Default interaction mode: **👤 Human Direct**
- State file created at `.x-ipe/engineering-workflow/workflow-{name}.json`
- The workflow card shows: name, creation date, "0 features", "ideation Stage"
- You can now expand the card and start the first action: **📝 Compose Idea**

### Cancel
- Click **"Cancel"** or the **×** button to close without creating
