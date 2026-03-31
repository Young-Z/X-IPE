# 3. Getting Started

## Quick Start: Your First Workflow

This guide walks you through creating and running your first engineering workflow in X-IPE. By the end, you'll have created a workflow, composed an idea, and started the AI-assisted engineering process.

**Prerequisites:**
- X-IPE server running (`x-ipe serve`)
- Browser open at `http://127.0.0.1:5858`
- AI CLI tool connected (console shows "Connected")

---

### Step 1: Switch to Workflow Mode

1. Look at the **header bar** at the top of the page
2. Find the toggle labeled **"FREE"** on the left and **"WORKFLOW"** on the right
3. **Click the toggle switch** to move it to the WORKFLOW position

![Workflow Mode Toggle](screenshots/01-overview-workflow-mode-main.png)

**Expected result:** The file browser sidebar disappears. You now see the **"Engineering Workflows"** panel with the subtitle "Manage your project delivery lifecycle from ideation to feedback."

---

### Step 2: Create a New Workflow

1. Click the **"➕ Create Workflow"** button in the top-right of the Engineering Workflows panel
2. A modal dialog appears with a text input field labeled "Workflow Name"
3. **Type your workflow name** using only letters, numbers, hyphens, and underscores (e.g., `my-first-feature`)
4. Click the **"Create"** button

![Create Workflow Modal](screenshots/04-core-features-create-workflow-modal.png)

**Naming rules:**
- Only alphanumeric characters, hyphens (`-`), and underscores (`_`) allowed
- Maximum 100 characters
- No spaces or special characters

**Expected result:** A new workflow card appears in the list showing:
- ⚡ Your workflow name
- Creation date
- "0 features"
- "ideation Stage"
- Default interaction mode: "👤 Human Direct"

---

### Step 3: Compose Your Idea

1. On your new workflow card, find the **stage progression bar** showing: Ideation → Requirement → Implement → Validation → Feedback
2. The **Ideation** stage is highlighted as active
3. Under **"COMPLETED ACTIONS"**, find the action labeled **"📝 Compose Idea"**
4. **Click** on "📝 Compose Idea"
5. A text editor area appears where you can write your project idea
6. **Write your idea description** — describe what you want to build, the problem it solves, and key features
7. **Save** when done

**Expected result:** The "📝 Compose Idea" action shows a ✓ checkmark. The Ideation stage now has one completed mandatory action.

---

### Step 4: (Optional) Refine with AI

After composing your idea, you can optionally enhance it with AI:

1. Click **"💡 Refine Idea"** — the AI refines your raw idea into a polished concept
2. Click **"🎨 Reference UIUX"** — the AI searches for relevant UI/UX design references
3. Click **"🖼 Design Mockup"** — the AI creates visual mockups

**How AI actions work (CLI_DISPATCH pattern):**
1. Clicking an AI action generates a command in the **console terminal** at the bottom of the page
2. The command is automatically sent to your connected AI CLI tool via WebSocket
3. You may need to **press Enter** in the terminal to confirm execution
4. Watch the terminal output — the AI processes the request (typically 1-5 minutes)
5. **How to know it's complete:** The action status changes from ⏳ to ✓ in the workflow card
6. Results appear as new files in the Deliverables panel

---

### Step 5: Move to Requirements

Once at least the mandatory "Compose Idea" action is complete:

1. The **Requirement** stage unlocks automatically
2. Click **"📋 Requirement Gathering"** — a command is dispatched to the terminal
3. **Press Enter** in the terminal if it waits for confirmation
4. Wait for the AI to complete (~3-5 minutes). **How to know it's done:** ✓ appears next to "Requirement Gathering"
5. Click **"🔀 Feature Breakdown"** — another command is dispatched to the terminal
6. **Press Enter** in the terminal if prompted. Wait for completion (~2-5 minutes)

**Expected result:** After Feature Breakdown completes (✓ appears), you'll see **Feature Lanes** appear — horizontal progress bars for each feature, showing per-feature stages:
```
Refinement → Tech Design → Implement → Testing → Refactor → Closing → Playground → CR
```

---

### Step 6: Track Progress

With features defined, the workflow enters per-feature mode:

1. Each feature has its own **lane** with 8 action steps
2. Features marked **"⇉ Parallel"** can be worked on simultaneously
3. Features marked **"⛓ needs FEATURE-XXX"** must wait for dependencies
4. Click any action in a feature lane to start/complete it
5. Track all generated artifacts in the **Deliverables** panel at the bottom

---

## Understanding the Interface

### Header Bar

| Element | Purpose |
|---------|---------|
| **X IPE** logo | Click to go to home page |
| **FREE / WORKFLOW** toggle | Switch between file browser and workflow mode |
| **KB** button | Open Knowledge Base browser |
| **Toolbox** button | Stage Toolbox — manage development tools |
| **Skills** button | Browse available AI skills |
| **⚙ Settings** | Open application settings |

### Workflow Card

Each workflow card displays:
- **Name** with ⚡ icon
- **Creation date** and **feature count**
- **Current stage** indicator
- **Interaction Mode** dropdown (Human Direct / DAO)
- **⋮ Actions menu** (Delete workflow)
- **Stage progression bar** (5 stages with ✓ for completed)
- **Action list** under each stage
- **Feature Lanes** (after Feature Breakdown)
- **Deliverables panel** (collapsible, shows file counts)

### Console / Terminal

The bottom bar shows:
- **"Console"** label with connection status ("Connected" in green)
- **Command input** area with microphone and command buttons
- **Toggle buttons**: Explorer, Zen Mode, Terminal visibility
