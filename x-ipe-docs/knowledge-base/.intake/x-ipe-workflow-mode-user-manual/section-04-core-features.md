# 4. Core Features

## Navigation & UI Structure (Web Mixin)

### Main Navigation

X-IPE has a persistent **header bar** visible across all pages:

| Element | Location | Action |
|---------|----------|--------|
| **X IPE** logo | Top-left | Click to return to home page |
| Tagline | Center | "An AI native integrated project environment..." |
| **FREE / WORKFLOW** toggle | Center-right | Switch between file browsing and workflow modes |
| **KB** button | Right | Open Knowledge Base browser |
| **Toolbox** button | Right | Stage Toolbox — manage development tools |
| **Skills** button | Right | Browse available AI skills |
| **⚙ Settings** link | Far right | Navigate to Settings page |

### Home / Dashboard

- **FREE mode**: Shows a file explorer sidebar, content viewer, and terminal console
- **WORKFLOW mode**: Shows the Engineering Workflows panel (the focus of this manual)

---

## Feature 1: Mode Toggle (FREE ↔ WORKFLOW)

**Interaction Pattern:** TOGGLE

**What it does:** Switches the entire application view between Free mode (file browsing) and Workflow mode (engineering lifecycle management).

**How to use:**
1. Locate the toggle switch in the header bar, between the labels "FREE" and "WORKFLOW"
2. **Click the toggle** to switch modes
3. The active mode label appears highlighted

**Behavior:**
- **Toggling TO Workflow mode**: The sidebar file browser hides. The main area shows Engineering Workflows panel. Background polling starts to keep workflow data fresh.
- **Toggling TO Free mode**: The workflow panel hides. The sidebar file browser and content editor reappear. Workflow polling stops.

**Edge cases:**
- Toggling modes does not lose any data — workflow state persists on disk
- You can toggle freely at any time, even during active workflows

---

## Feature 2: Create Workflow

**Interaction Pattern:** MODAL

**What it does:** Creates a new engineering workflow with an initial state at the Ideation stage.

**How to use:**
1. In Workflow mode, click the **"➕ Create Workflow"** button
2. A modal dialog appears with:
   - Text input field labeled "Workflow Name"
   - "Cancel" button (dismisses without creating)
   - "Create" button (creates the workflow)
3. **Type a workflow name** (alphanumeric, hyphens, underscores only; max 100 characters)
4. Click **"Create"**

**What happens on creation:**
- A new workflow card appears in the list
- Workflow file is created at: `x-ipe-docs/engineering-workflow/workflow-{name}.json`
- Initial stage: `ideation` (with `in_progress` status)
- Default interaction mode: `interact-with-human` (👤 Human Direct)
- All subsequent stages are `locked` until prerequisites are met

**Validation rules:**
- Name pattern: `^[\w-]+$` — only letters, numbers, hyphens, underscores
- Maximum length: 100 characters
- Duplicate names are rejected with "ALREADY_EXISTS" error

**Error messages:**
- "INVALID_NAME" — name contains spaces or special characters
- "ALREADY_EXISTS" — a workflow with that name already exists

---

## Feature 3: Workflow Stages

**Interaction Pattern:** NAVIGATION (stage progression is automatic)

**What it does:** Each workflow progresses through 5 sequential stages. Stages unlock automatically when their prerequisites are met.

### The 5 Stages

| # | Stage | Type | Unlocked When | Actions |
|---|-------|------|---------------|---------|
| 1 | **Ideation** | Shared | Workflow created | Compose Idea (mandatory), Reference UIUX, Refine Idea, Design Mockup |
| 2 | **Requirement** | Shared | Ideation mandatory actions done | Requirement Gathering, Feature Breakdown (both mandatory) |
| 3 | **Implement** | Per-Feature | Feature Breakdown done | Feature Refinement, Technical Design, Implementation (all mandatory) |
| 4 | **Validation** | Per-Feature | Implement mandatory actions done (per feature) | Acceptance Testing, Code Refactor, Feature Closing (all mandatory) |
| 5 | **Feedback** | Per-Feature | Validation mandatory actions done (per feature) | Human Playground, Change Request (both optional) |

### Stage Types

- **Shared stages** (Ideation, Requirement): Apply to the whole workflow. One set of actions for the entire project.
- **Per-Feature stages** (Implement, Validation, Feedback): Each feature has its own independent progression through these stages.

### Stage Status Values

| Status | Meaning | Visual |
|--------|---------|--------|
| `in_progress` | Stage is active, actions can be performed | Highlighted, clickable |
| `locked` | Waiting for previous stage(s) to complete | Grayed out, not clickable |
| `completed` | All mandatory actions done | ✓ checkmark |

### Visual Indicators

The stage progression bar shows all 5 stages horizontally:
```
✓ Ideation › ✓ Requirement › Implement › Validation › 5 Feedback
```
- **✓** = completed stage
- **Bold/highlighted** = current active stage
- **Number badge** = pending items count

---

## Feature 4: Workflow Actions

**Interaction Pattern:** CLI_DISPATCH (most actions) or MODAL (Compose Idea)

**What it does:** Each stage contains actions that advance the workflow. Most actions dispatch commands to the AI CLI tool running in the terminal.

### Action Types

**Manual actions (MODAL):**
- **Compose Idea**: Opens a text editor where you manually write your idea

**AI-dispatched actions (CLI_DISPATCH):**
All other actions send a command to the connected AI CLI terminal.

### How CLI_DISPATCH Actions Work

1. **Click** the action button (e.g., "💡 Refine Idea")
2. A command is **generated and sent** to the terminal console at the bottom of the page
3. The command targets your connected AI CLI tool (Copilot, Claude, or OpenCode)
4. **The AI CLI executes the command** — processing may take 1-5 minutes
5. Watch the terminal for output and completion signals
6. When done, the action status updates to ✓

**Important for CLI_DISPATCH:**
- The terminal at the bottom must show **"Connected"** status
- Commands are sent via WebSocket to the AI CLI running in the terminal
- If the AI CLI is not connected, commands will fail silently
- Some actions may require you to **press Enter** in the terminal to confirm execution
- **Completion signal**: The action status changes from ⏳ to ✓ in the workflow card

### Complete Action Catalog

#### Ideation Stage

| Action | Icon | Required | Pattern | AI Skill |
|--------|------|----------|---------|----------|
| Compose Idea | 📝 | ✅ Mandatory | MODAL | (manual) |
| Reference UIUX | 🎨 | Optional | CLI_DISPATCH | `x-ipe-tool-uiux-reference` |
| Refine Idea | 💡 | Optional | CLI_DISPATCH | `x-ipe-task-based-ideation` |
| Design Mockup | 🖼 | Optional | CLI_DISPATCH | `x-ipe-task-based-idea-mockup` |

#### Requirement Stage

| Action | Icon | Required | Pattern | AI Skill |
|--------|------|----------|---------|----------|
| Requirement Gathering | 📋 | ✅ Mandatory | CLI_DISPATCH | `x-ipe-task-based-requirement-gathering` |
| Feature Breakdown | 🔀 | ✅ Mandatory | CLI_DISPATCH | `x-ipe-task-based-feature-breakdown` |

#### Implement Stage (per feature)

| Action | Icon | Required | Pattern | AI Skill |
|--------|------|----------|---------|----------|
| Feature Refinement | 📐 | ✅ Mandatory | CLI_DISPATCH | `x-ipe-task-based-feature-refinement` |
| Technical Design | ⚙ | ✅ Mandatory | CLI_DISPATCH | `x-ipe-task-based-technical-design` |
| Implementation | 💻 | ✅ Mandatory | CLI_DISPATCH | `x-ipe-task-based-code-implementation` |

#### Validation Stage (per feature)

| Action | Icon | Required | Pattern | AI Skill |
|--------|------|----------|---------|----------|
| Acceptance Testing | ✅ | ✅ Mandatory | CLI_DISPATCH | `x-ipe-task-based-feature-acceptance-test` |
| Code Refactor | 🔧 | ✅ Mandatory | CLI_DISPATCH | `x-ipe-task-based-code-refactor` |
| Feature Closing | 🏁 | ✅ Mandatory | CLI_DISPATCH | `x-ipe-task-based-feature-closing` |

#### Feedback Stage (per feature)

| Action | Icon | Required | Pattern | AI Skill |
|--------|------|----------|---------|----------|
| Human Playground | 🎮 | Optional | CLI_DISPATCH | `x-ipe-task-based-human-playground` |
| Change Request | 🔄 | Optional | CLI_DISPATCH | `x-ipe-task-based-change-request` |

### Action Status Values

| Status | Icon | Meaning |
|--------|------|---------|
| `pending` | ○ | Not started |
| `in_progress` | ⏳ | Currently executing |
| `done` | ✓ | Completed successfully |
| `skipped` | ⊘ | Intentionally skipped (optional actions only) |
| `failed` | ✗ | Error occurred during execution |

### Re-opening Actions

- **Completed actions cannot be re-opened** if later stages have already started
- Example: If "Feature Breakdown" has started in the Requirement stage, you cannot re-open "Compose Idea" in the Ideation stage
- Error message: "Cannot re-open: {action} in {stage} stage is already started"

---

## Feature 5: Interaction Mode

**Interaction Pattern:** FORM (dropdown selection)

**What it does:** Controls how the AI agents interact with you during workflow execution. Each workflow has its own interaction mode setting.

### Three Interaction Modes

| Mode | Icon | Badge | Behavior |
|------|------|-------|----------|
| **Human Direct** | 👤 | Gray | AI asks you for every decision. Full human control and sign-off at each step. |
| **DAO Represents Human** | 🤖 | Green | DAO (Decision-Assisting Oracle) acts as your proxy for non-critical decisions. Escalates major decisions to you. |
| **DAO Inner-Skill Only** | 🤖⚡ | Yellow | Maximum autonomy. DAO operates within skill execution. Only escalates for skill-level design questions. |

### How to Change Interaction Mode

1. On any workflow card, find the **"Interaction Mode"** label
2. Click the **dropdown button** showing the current mode (e.g., "👤 Human Direct")
3. A dropdown menu appears with three options:
   - 👤 Human Direct
   - 🤖 DAO Represents Human
   - 🤖⚡ DAO Inner-Skill Only
4. **Click your preferred mode**
5. The dropdown closes and the mode updates immediately

![Interaction Mode Dropdown](screenshots/04-core-features-interaction-mode-dropdown.png)

**Where the setting is stored:** `workflow.global.process_preference.interaction_mode` in the workflow JSON file.

**When to use each mode:**
- **Human Direct**: When you want full control, learning a new workflow, or working on critical features
- **DAO Represents Human**: When you trust the AI to handle routine decisions but want oversight on important ones
- **DAO Inner-Skill Only**: For maximum speed when running well-understood workflows

---

## Feature 6: Feature Lanes

**Interaction Pattern:** NAVIGATION (click to open feature actions)

**What it does:** After Feature Breakdown completes, each feature gets a horizontal lane showing its progression through 8 per-feature action steps.

### Lane Structure

Each feature lane shows:
```
[Feature ID] [Feature Name] [Dependency Status]
Refinement › Tech Design › Implement › Testing › Refactor › Closing › Playground › CR
```

### Lane Elements

| Element | Description |
|---------|-------------|
| **Feature ID** | e.g., FEATURE-050-A |
| **Feature Name** | e.g., "Extractor Skill Foundation & Input Detection" |
| **Dependency Badge** | "⇉ Parallel" (no blockers) or "⛓ needs FEATURE-XXX" (blocked) |
| **Action Steps** | 8 boxes with status indicators (✓ done, ⏳ in progress, ○ pending) |

### Dependency Management

- **⇉ Parallel**: Feature has no dependencies — work can start immediately
- **⛓ needs FEATURE-XXX**: Feature is blocked until the specified feature's Implement stage completes
- Multiple dependencies: "⛓ needs FEATURE-050-A, FEATURE-050-B"

### Lane Status Legend

| Indicator | Status |
|-----------|--------|
| **Done** | Green, with count of completed features |
| **Active** | Blue/highlighted, currently being worked on |
| **Pending** | Gray, waiting to be started or unblocked |

---

## Feature 7: Deliverables Panel

**Interaction Pattern:** TOGGLE (expand/collapse) + NAVIGATION (browse files)

**What it does:** Shows all artifacts produced by workflow actions, organized by stage and feature. Located at the bottom of each workflow card.

### Panel Structure

The panel header shows:
- **"Deliverables"** label with a count badge (e.g., "52")
- **▾ / ▸** toggle to expand/collapse

### Content Organization

Deliverables are grouped into sections:

1. **SHARED DELIVERABLES** — Files from Ideation and Requirement stages
   - 📁 Workflow folder (e.g., `wf-008-knowledge-extraction`)
   - 💡 Idea files (raw ideas, refined ideas)
   - 📋 Requirement files
   - 📁 Sub-folders (refined-idea/, requirements/)

2. **FEATURE-XXX — FEATURE NAME** — Per-feature deliverables
   - 📋 specification.md
   - 📋 technical-design.md
   - 💻 Code files (SKILL.md, implementation files)
   - 📊 Test reports (acceptance-test-report.md)
   - 📁 Sub-folders

### Deliverable Icons

| Icon | Category | Examples |
|------|----------|----------|
| 💡 | Ideas | new idea.md, idea-summary-v1.md |
| 📋 | Requirements | specification.md, technical-design.md, requirement-details.md |
| 💻 | Code | SKILL.md, implementation files |
| 📊 | Quality | acceptance-test-report.md, refactor reports |
| 📁 | Folders | Sub-directories containing related files |

### File Paths

Each deliverable shows its relative file path, e.g.:
- `ideas/wf-008-knowledge-extraction/new idea.md`
- `requirements/EPIC-050/FEATURE-050-A/specification.md`
- `.github/skills/x-ipe-task-based-application-knowledge-extractor/SKILL.md`

---

## Feature 8: Workflow Actions Menu

**Interaction Pattern:** MODAL (dropdown menu)

**What it does:** Provides management actions for each workflow.

**How to use:**
1. On any workflow card, click the **"⋮"** (three dots) button
2. A dropdown menu appears with available actions:
   - **🗑 Delete** — Permanently remove the workflow

**Delete workflow:**
1. Click ⋮ → Delete
2. Confirm the deletion
3. The workflow card is removed and the workflow JSON file is deleted

---

## Feature 9: Console / Terminal

**Interaction Pattern:** CLI_DISPATCH target

**What it does:** The bottom panel provides an integrated terminal that communicates with the AI CLI tool via WebSocket.

### Terminal Elements

| Element | Description |
|---------|-------------|
| **"Console"** label | Shows connection status: "Connected" (green) or "Disconnected" (red) |
| **Command input** | Insert commands or text to send to the AI CLI |
| **🎙 Microphone** | Toggle voice input (Ctrl+Shift+V to record when enabled) |
| **📂 Explorer** | Toggle file explorer panel |
| **🧘 Zen Mode** | Toggle distraction-free mode |
| **📟 Terminal** | Toggle terminal visibility |

### Connection Status

- **Connected**: WebSocket active, commands will be dispatched to AI CLI
- **Disconnected**: No AI CLI tool detected. Workflow actions will not execute.

### How Commands Flow

1. User clicks a workflow action (e.g., "Refine Idea")
2. X-IPE generates a skill-specific command
3. Command is sent via WebSocket to the terminal
4. The AI CLI tool (Copilot/Claude/OpenCode) receives and executes it
5. AI processes the skill, reading/writing project files
6. Workflow state updates when the action completes
