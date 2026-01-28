---
name: task-type-idea-mockup
description: Create visual mockups and prototypes for refined ideas. Use after ideation when idea needs visual representation. Invokes tool-frontend-design skill or other mockup tools based on x-ipe-docs/config/tools.json config. Triggers on requests like "create mockup", "visualize idea", "prototype UI", "design mockup".
---

# Task Type: Idea Mockup

## Purpose

Create visual mockups and prototypes for refined ideas by:
1. Reading the idea summary from ideation task
2. Loading mockup tools from `x-ipe-docs/config/tools.json` config
3. Creating visual representations (UI mockups, wireframes, prototypes)
4. Saving artifacts to the idea folder
5. Preparing for Requirement Gathering

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` and `task-board-management` skill, please learn them first before executing this skill.
- **Frontend Design Skill:** Learn `tool-frontend-design` skill if `stages.ideation.mockup.tool-frontend-design` is enabled in config.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

### ⚠️ UI/UX Focus Only

**When generating mockups, focus ONLY on UI/UX presentation:**

| Focus On | Ignore |
|----------|--------|
| Visual layout and composition | Backend tech stack (Python, Node.js, etc.) |
| User interaction patterns | Database choices (PostgreSQL, MongoDB, etc.) |
| Navigation and flow | API implementation details |
| Color schemes and typography | Framework specifics (React, Vue, Django, etc.) |
| Responsive design | Infrastructure and deployment |
| Component placement | Authentication mechanisms |
| User experience | Server architecture |

**Rationale:** Mockups are for visualizing the user experience, not technical implementation. Tech stack decisions come later during Technical Design.

**Example:**
```
Idea mentions: "Build with React and Node.js, use PostgreSQL"

Mockup should show:
✓ How the dashboard looks
✓ Where buttons and inputs are placed
✓ User flow between screens

Mockup should NOT include:
✗ React component structure
✗ API endpoint labels
✗ Database schema hints
```

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Idea Mockup |
| Category | ideation-stage |
| Standalone | No |
| Next Task | Requirement Gathering |
| Auto-advance | No |
| Human Review | Yes |

---

## Task Type Required Input Attributes

| Attribute | Default Value | Description |
|-----------|---------------|-------------|
| Auto Proceed | False | Auto-advance to next task |
| Ideation Toolbox Meta | `{project_root}/x-ipe-docs/config/tools.json` | Config file for enabled tools |
| Current Idea Folder | N/A | **Required from context** - path to current idea folder (e.g., `x-ipe-docs/ideas/mobile-app-idea`) |
| Extra Instructions | N/A | Additional context or requirements for mockup creation |

### Extra Instructions Attribute

**Purpose:** Provides additional context or requirements for the mockup creation process.

**Source:** This value can be obtained from:
1. Human input (explicit instructions provided)
2. `x-ipe-docs/config/tools.json` → `stages.ideation.mockup._extra_instruction` field
3. Default: N/A (no extra instructions)

**Loading Logic:**
```
1. IF human provides explicit Extra Instructions:
   → Use human-provided value

2. ELSE IF x-ipe-docs/config/tools.json exists:
   a. Read stages.ideation.mockup._extra_instruction field
   b. IF field exists AND is not empty:
      → Use value from config
   c. ELSE:
      → Use default: N/A

3. IF Extra Instructions != N/A:
   → Apply these instructions when identifying mockup needs
   → Consider them when invoking mockup tools
   → Factor them into design preferences
   → Reference them during human review
```

**Usage:** When Extra Instructions are provided, the agent MUST incorporate them into the mockup creation workflow, particularly when designing UI elements and choosing visual styles.

### Current Idea Folder Attribute

**Source:** This value MUST be obtained from context:
- From previous Ideation task output (`idea_folder` field)
- From task board (associated idea folder)
- From human input if not available in context

**Validation:**
```
1. IF Current Idea Folder == N/A:
   → Ask human: "Which idea folder should I create mockups for?"
   → List available folders under x-ipe-docs/ideas/
   → Wait for human selection

2. IF Current Idea Folder provided:
   → Validate folder exists
   → Verify idea-summary-vN.md exists in folder
   → Proceed with mockup creation
```

**Usage:**
- All mockups are saved to `{Current Idea Folder}/mockups/`
- Idea summary updates reference `{Current Idea Folder}/idea-summary-vN.md`
- Output links use `{Current Idea Folder}` as base path

### Ideation Toolbox Meta File

**Location:** `x-ipe-docs/config/tools.json` (relative to project root)

**Relevant Config Section:**
```json
{
  "version": "2.0",
  "stages": {
    "ideation": {
      "mockup": {
        "tool-frontend-design": true
      }
    }
  }
}
```

**Tool Loading Rules:**

1. **File exists:** Load and parse the JSON configuration
2. **File missing:** Inform user mockup tools not configured, proceed with manual description
3. **Tool enabled (`true`):** Invoke corresponding skill/capability
4. **Tool disabled (`false`):** Skip the tool
5. **Tool unavailable:** Log limitation and provide alternative

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | `Current Idea Folder` is set (not N/A) | Yes |
| 2 | Refined idea summary exists (`{Current Idea Folder}/idea-summary-vN.md`) | Yes |
| 3 | `x-ipe-docs/config/tools.json` accessible | Yes |
| 4 | At least one mockup tool enabled OR manual mode accepted | Yes |

---

## Execution Flow

Execute Idea Mockup by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Validate Folder | Verify Current Idea Folder exists | Folder validated |
| 2 | Load Config | Read `x-ipe-docs/config/tools.json` mockup section | Config loaded |
| 3 | Read Idea Summary | Load latest idea-summary-vN.md from folder | Summary loaded |
| 4 | Identify Mockup Needs | Extract UI/visual elements from idea | Needs identified |
| 5 | Create Mockups | Invoke enabled mockup tools | Mockups created |
| 6 | Save Artifacts | Store mockups in `{Current Idea Folder}/mockups/` | Artifacts saved |
| 7 | Update Summary | Add mockup links to idea summary | Summary updated |
| 8 | Complete | Request human review and approval | Human approves |

**⛔ BLOCKING RULES:**
- Step 1: BLOCKED if Current Idea Folder is N/A → Ask human for folder path
- Step 5: BLOCKED if no mockup tools available AND human doesn't accept manual mode
- Step 8 → Human Review: Human MUST approve mockups before proceeding

---

## Execution Procedure

### Step 1: Validate Current Idea Folder

**Action:** Verify the Current Idea Folder input and ensure it exists

```
1. Check if Current Idea Folder is set:
   IF Current Idea Folder == N/A:
     → List available folders under x-ipe-docs/ideas/
     → Ask human: "Which idea folder should I create mockups for?"
     → Options: [list of folders]
     → Wait for selection
     → Set Current Idea Folder = selected folder

2. Validate folder exists:
   IF folder does NOT exist:
     → Error: "Idea folder not found: {Current Idea Folder}"
     → STOP execution

3. Verify idea summary exists:
   IF no idea-summary-vN.md in folder:
     → Error: "No idea summary found. Run Ideation task first."
     → STOP execution

4. Log: "Working with idea folder: {Current Idea Folder}"
```

**Output:** Validated `Current Idea Folder` path

### Step 2: Load Mockup Tool Configuration

**Action:** Read and parse the mockup section from ideation tools config

**Default Path:** `x-ipe-docs/config/tools.json`

```
1. Check if x-ipe-docs/config/tools.json exists
2. If exists:
   a. Parse JSON file
   b. Extract stages.ideation.mockup section configuration
   c. Identify enabled tools (value = true)
   d. Extract _extra_instruction from stages.ideation.mockup section (if exists)
3. If NOT exists:
   a. Inform user: "No mockup tools configured"
   b. Ask: "Proceed with manual mockup description? (Y/N)"
4. Load Extra Instructions:
   a. IF human provided explicit Extra Instructions → Use human value
   b. ELSE IF _extra_instruction field exists and is not empty → Use config value
   c. ELSE → Set Extra Instructions = N/A
5. Log active mockup tool configuration and Extra Instructions (if any)
```

**Mockup Tool Mapping:**

| Config Key | Skill/Capability | What It Creates |
|------------|------------------|-----------------|
| `stages.ideation.mockup.tool-frontend-design` | `tool-frontend-design` skill | HTML/CSS mockups, interactive prototypes |
| `stages.ideation.mockup.figma-mcp` | Figma MCP server | Figma design files |
| `stages.ideation.mockup.excalidraw` | Excalidraw integration | Sketch-style wireframes |

**Output:** List of enabled mockup tools

### Step 3: Read Idea Summary

**Action:** Load the latest idea summary from Current Idea Folder

```
1. Navigate to {Current Idea Folder}/
2. Find latest idea-summary-vN.md (highest version number)
3. Parse the summary content
4. Extract:
   - Overview and description
   - Key Features list
   - UI/UX mentions
   - User flow descriptions
```

**Output:** Parsed idea summary with UI-relevant sections

### Step 4: Identify Mockup Needs

**Action:** Analyze idea summary to determine what mockups to create

**Analysis Questions:**
```
1. Does the idea describe a user interface?
   → If yes, identify screens/pages needed
   
2. Does the idea mention user interactions?
   → If yes, identify interactive elements
   
3. Does the idea describe a workflow?
   → If yes, identify flow visualization needs
   
4. What is the primary user-facing component?
   → Prioritize mockup for this component
```

**Mockup Types to Consider:**

| Idea Contains | Mockup Type | Priority |
|---------------|-------------|----------|
| Dashboard description | Dashboard layout | High |
| Form/input mentions | Form mockup | High |
| List/table data | Data display mockup | Medium |
| Navigation mentions | Nav structure | Medium |
| Charts/graphs | Data visualization | Medium |
| Mobile mentions | Mobile-responsive mockup | High |

**Output:** Prioritized list of mockups to create

### Step 5: Create Mockups

**Action:** Invoke enabled mockup tools to create visual artifacts

**⚠️ REMINDER: Focus on UI/UX only. Ignore all tech stack mentions from idea files.**

**IF `stages.ideation.mockup.tool-frontend-design: true`:**
```
1. Invoke `tool-frontend-design` skill
2. Pass context:
   - Current Idea Folder path
   - Idea summary content (UI/UX elements only)
   - Identified mockup needs
   - Design preferences (if mentioned in idea)
   - NOTE: Do NOT pass tech stack information
3. Request HTML/CSS mockup generation
4. Skill will create interactive prototype
```

**Tool-Frontend-Design Skill Invocation:**
```yaml
skill: tool-frontend-design
context:
  type: idea-mockup
  idea_folder: {Current Idea Folder}
  idea_summary: {parsed summary - UI/UX content only}
  mockup_needs:
    - type: dashboard
      description: "Main analytics dashboard with charts"
    - type: form
      description: "User registration form"
  design_preferences:
    style: modern | minimal | professional
    colors: {from idea or default}
```

**IF `mockup.figma-mcp: true`:**
```
1. Check Figma MCP server connection
2. Create new Figma file or use template
3. Generate basic layout based on idea
4. Return Figma file link
```

**IF no tools enabled (Manual Mode):**
```
1. Create detailed mockup description in markdown
2. Include ASCII art or text-based layout
3. Document component specifications
4. Save as mockup-description.md in {Current Idea Folder}/mockups/
```

**Output:** Generated mockup files/links

### Step 6: Save Artifacts

**Action:** Store all mockup artifacts in the Current Idea Folder

**Directory Structure:**
```
{Current Idea Folder}/
├── idea-summary-vN.md
├── mockups/
│   ├── dashboard-v1.html      (if tool-frontend-design used)
│   ├── dashboard-v1.css       (if tool-frontend-design used)
│   ├── form-v1.html           (if tool-frontend-design used)
│   ├── mockup-description.md  (if manual mode)
│   └── figma-link.md          (if figma-mcp used)
└── files/
    └── (original idea files)
```

**Naming Convention:**
```
{mockup-type}-v{version}.{extension}

Examples:
- dashboard-v1.html
- user-form-v1.html
- mobile-home-v1.html
```

**Output:** List of saved artifact paths (relative to Current Idea Folder)

### Step 7: Update Idea Summary

**Action:** Add mockup references to the idea summary

**DO NOT modify existing idea-summary files.**
Instead, create a new version: `{Current Idea Folder}/idea-summary-v{N+1}.md`

**Add to Summary:**
```markdown
## Mockups & Prototypes

| Mockup | Type | Path | Tool Used |
|--------|------|------|-----------|
| Dashboard | HTML | mockups/dashboard-v1.html | tool-frontend-design |
| User Form | HTML | mockups/user-form-v1.html | tool-frontend-design |

### Preview Instructions
- Open HTML files in browser to view interactive mockups
- Figma link: {link if figma-mcp used}
```

**Output:** Updated idea summary version

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | `Current Idea Folder` validated and exists | Yes |
| 2 | `x-ipe-docs/config/tools.json` loaded and mockup section parsed | Yes |
| 3 | Idea summary read and analyzed | Yes |
| 4 | Mockup needs identified and prioritized | Yes |
| 5 | Mockups created using enabled tools (or manual description) | Yes |
| 6 | Artifacts saved to `{Current Idea Folder}/mockups/` | Yes |
| 7 | New idea summary version created with mockup links | Yes |
| 8 | Human has reviewed and approved mockups | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:
```yaml
category: ideation-stage
task_type: Idea Mockup
auto_proceed: {from input Auto Proceed}
idea_id: IDEA-XXX
current_idea_folder: {Current Idea Folder}   # e.g., x-ipe-docs/ideas/mobile-app-idea
mockup_tools_used:
  - tool-frontend-design
mockups_created:
  - type: dashboard
    path: {Current Idea Folder}/mockups/dashboard-v1.html
  - type: form
    path: {Current Idea Folder}/mockups/user-form-v1.html
mockup_list:   # List of all mockup paths - passed to next tasks in chain
  - {Current Idea Folder}/mockups/dashboard-v1.html
  - {Current Idea Folder}/mockups/user-form-v1.html
idea_summary_version: vN+1
next_task_type: Requirement Gathering
require_human_review: true
task_output_links:
  - {Current Idea Folder}/mockups/dashboard-v1.html
  - {Current Idea Folder}/mockups/user-form-v1.html
  - {Current Idea Folder}/idea-summary-v{N+1}.md
```

**Output Links:** All paths in `task_output_links` are clickable/viewable:
- HTML mockups can be opened in browser
- Idea summary is markdown viewable in editor

**Mockup List Flow:** The `mockup_list` attribute is passed through the task chain:
```
Idea Mockup → Requirement Gathering → Feature Breakdown → Feature Refinement → Technical Design
```
Each subsequent task receives and passes the mockup_list to ensure mockups are referenced throughout the development lifecycle.

---

## Patterns

### Pattern: Dashboard-Heavy Idea

**When:** Idea focuses on data visualization and dashboards
**Then:**
```
1. Prioritize dashboard mockup
2. Include chart placeholders
3. Add filter/control areas
4. Consider responsive layout
5. Use tool-frontend-design skill with dashboard template
```

### Pattern: Form-Heavy Idea

**When:** Idea involves data input or user registration
**Then:**
```
1. Prioritize form mockups
2. Include validation states
3. Show error/success messages
4. Consider multi-step flows
5. Include mobile view
```

### Pattern: No UI Description

**When:** Idea summary lacks UI details
**Then:**
```
1. Ask clarifying questions about UI needs
2. Suggest common patterns based on idea type
3. Create minimal viable mockup
4. Request feedback before expanding
```

### Pattern: Multiple User Roles

**When:** Idea mentions different user types
**Then:**
```
1. Create separate mockups for each role
2. Name clearly: admin-dashboard-v1.html, user-dashboard-v1.html
3. Document role-specific features
4. Consider permission variations
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Creating mockup before reading idea | May miss requirements | Always analyze idea first |
| Ignoring x-ipe-docs/config/tools.json config | Inconsistent tool usage | Always check config |
| Overwriting existing mockups | Loses previous versions | Use version numbering |
| Skipping human review | May create wrong visuals | Always get approval |
| Using disabled tools | Violates config rules | Only use enabled tools |
| Creating too many mockups at once | Overwhelms review | Start with 1-3 key mockups |
| Including tech stack in mockups | Mockups are for UI/UX, not implementation | Focus only on visual presentation |
| Labeling components with framework names | Confuses design with implementation | Use descriptive UI labels |

---

## Example

See [references/examples.md](references/examples.md) for detailed execution examples including:
- Mockup with frontend-design tool enabled
- Mockup without tools (manual mode)
- Missing idea folder (blocked scenario)
- No idea summary (blocked scenario)
