---
name: task-type-idea-mockup
description: Create visual mockups and prototypes for refined ideas. Use after ideation when idea needs visual representation. Invokes frontend-design skill or other mockup tools based on .ideation-tools.json config. Triggers on requests like "create mockup", "visualize idea", "prototype UI", "design mockup".
---

# Task Type: Idea Mockup

## Purpose

Create visual mockups and prototypes for refined ideas by:
1. Reading the idea summary from ideation task
2. Loading mockup tools from `.ideation-tools.json` config
3. Creating visual representations (UI mockups, wireframes, prototypes)
4. Saving artifacts to the idea folder
5. Preparing for Requirement Gathering

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` and `task-board-management` skill, please learn them first before executing this skill.
- **Frontend Design Skill:** Learn `frontend-design` skill if mockup.frontend-design is enabled in config.

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

## Quick Reference

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
| Ideation Toolbox Meta | `{project_root}/docs/ideas/.ideation-tools.json` | Config file for enabled tools |
| Current Idea Folder | N/A | **Required from context** - path to current idea folder (e.g., `docs/ideas/mobile-app-idea`) |

### Current Idea Folder Attribute

**Source:** This value MUST be obtained from context:
- From previous Ideation task output (`idea_folder` field)
- From task board (associated idea folder)
- From human input if not available in context

**Validation:**
```
1. IF Current Idea Folder == N/A:
   → Ask human: "Which idea folder should I create mockups for?"
   → List available folders under docs/ideas/
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

**Location:** `docs/ideas/.ideation-tools.json` (relative to project root)

**Relevant Config Section:**
```json
{
  "version": "1.0",
  "mockup": {
    "frontend-design": true,
    "figma-mcp": false
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
| 3 | `.ideation-tools.json` accessible | Yes |
| 4 | At least one mockup tool enabled OR manual mode accepted | Yes |

---

## Execution Flow

Execute Idea Mockup by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Validate Folder | Verify Current Idea Folder exists | Folder validated |
| 2 | Load Config | Read `.ideation-tools.json` mockup section | Config loaded |
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
     → List available folders under docs/ideas/
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

**Default Path:** `docs/ideas/.ideation-tools.json`

```
1. Check if .ideation-tools.json exists at docs/ideas/
2. If exists:
   a. Parse JSON file
   b. Extract mockup section configuration
   c. Identify enabled tools (value = true)
3. If NOT exists:
   a. Inform user: "No mockup tools configured"
   b. Ask: "Proceed with manual mockup description? (Y/N)"
4. Log active mockup tool configuration
```

**Mockup Tool Mapping:**

| Config Key | Skill/Capability | What It Creates |
|------------|------------------|-----------------|
| `mockup.frontend-design` | `frontend-design` skill | HTML/CSS mockups, interactive prototypes |
| `mockup.figma-mcp` | Figma MCP server | Figma design files |
| `mockup.excalidraw` | Excalidraw integration | Sketch-style wireframes |

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

**IF `mockup.frontend-design: true`:**
```
1. Invoke `frontend-design` skill
2. Pass context:
   - Current Idea Folder path
   - Idea summary content (UI/UX elements only)
   - Identified mockup needs
   - Design preferences (if mentioned in idea)
   - NOTE: Do NOT pass tech stack information
3. Request HTML/CSS mockup generation
4. Skill will create interactive prototype
```

**Frontend-Design Skill Invocation:**
```yaml
skill: frontend-design
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
│   ├── dashboard-v1.html      (if frontend-design used)
│   ├── dashboard-v1.css       (if frontend-design used)
│   ├── form-v1.html           (if frontend-design used)
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
| Dashboard | HTML | mockups/dashboard-v1.html | frontend-design |
| User Form | HTML | mockups/user-form-v1.html | frontend-design |

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
| 2 | `.ideation-tools.json` loaded and mockup section parsed | Yes |
| 3 | Idea summary read and analyzed | Yes |
| 4 | Mockup needs identified and prioritized | Yes |
| 5 | Mockups created using enabled tools (or manual description) | Yes |
| 6 | Artifacts saved to `{Current Idea Folder}/mockups/` | Yes |
| 7 | New idea summary version created with mockup links | Yes |
| 8 | Human has reviewed and approved mockups | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Task Completion Output

Upon completion, return:
```yaml
task_type: Idea Mockup
idea_id: IDEA-XXX
current_idea_folder: {Current Idea Folder}   # e.g., docs/ideas/mobile-app-idea
mockup_tools_used:
  - frontend-design
mockups_created:
  - type: dashboard
    path: {Current Idea Folder}/mockups/dashboard-v1.html
  - type: form
    path: {Current Idea Folder}/mockups/user-form-v1.html
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
5. Use frontend-design skill with dashboard template
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
| Ignoring .ideation-tools.json config | Inconsistent tool usage | Always check config |
| Overwriting existing mockups | Loses previous versions | Use version numbering |
| Skipping human review | May create wrong visuals | Always get approval |
| Using disabled tools | Violates config rules | Only use enabled tools |
| Creating too many mockups at once | Overwhelms review | Start with 1-3 key mockups |
| Including tech stack in mockups | Mockups are for UI/UX, not implementation | Focus only on visual presentation |
| Labeling components with framework names | Confuses design with implementation | Use descriptive UI labels |

---

## Example

**Scenario:** Create mockups for mobile-app-idea after ideation

**Input:**
- `Current Idea Folder`: `docs/ideas/mobile-app-idea` (from previous Ideation task)

**Config:** `docs/ideas/.ideation-tools.json`
```json
{
  "version": "1.0",
  "mockup": {
    "frontend-design": true,
    "figma-mcp": false
  }
}
```

**Idea Summary Excerpt:**
```markdown
## Key Features
- User dashboard with activity charts
- Settings page for preferences
- Mobile-responsive design
```

**Execution:**
```
1. Execute Task Flow from task-execution-guideline skill

2. Validate Current Idea Folder:
   - Current Idea Folder = docs/ideas/mobile-app-idea
   - Folder exists ✓
   - idea-summary-v1.md exists ✓

3. Load Config:
   - Read .ideation-tools.json
   - mockup.frontend-design: true → enabled
   - mockup.figma-mcp: false → disabled

4. Read Idea Summary:
   - Load docs/ideas/mobile-app-idea/idea-summary-v1.md
   - Extract: dashboard, settings page, mobile-responsive

5. Identify Mockup Needs:
   - Priority 1: User dashboard (charts, mobile)
   - Priority 2: Settings page

6. Create Mockups:
   - Invoke frontend-design skill:
     → Create dashboard-v1.html (responsive, with chart placeholders)
     → Create settings-v1.html (form layout)

7. Save Artifacts:
   - docs/ideas/mobile-app-idea/mockups/dashboard-v1.html
   - docs/ideas/mobile-app-idea/mockups/dashboard-v1.css
   - docs/ideas/mobile-app-idea/mockups/settings-v1.html
   - docs/ideas/mobile-app-idea/mockups/settings-v1.css

8. Update Summary:
   - Create docs/ideas/mobile-app-idea/idea-summary-v2.md with mockup links

9. Human Review:
   - Present mockups for approval
   - "Open docs/ideas/mobile-app-idea/mockups/dashboard-v1.html in browser to preview"

10. Output:
    task_output_links:
      - docs/ideas/mobile-app-idea/mockups/dashboard-v1.html
      - docs/ideas/mobile-app-idea/mockups/settings-v1.html
      - docs/ideas/mobile-app-idea/idea-summary-v2.md

11. Resume Task Flow from task-execution-guideline skill
```

---

## Example WITHOUT Mockup Tools

**Input:**
- `Current Idea Folder`: `docs/ideas/simple-idea`

**Config:** `docs/ideas/.ideation-tools.json`
```json
{
  "version": "1.0",
  "mockup": {
    "frontend-design": false,
    "figma-mcp": false
  }
}
```

**Execution:**
```
1. Validate Current Idea Folder:
   - Current Idea Folder = docs/ideas/simple-idea ✓

2. Load Config:
   - All mockup tools disabled
   - Ask human: "No mockup tools enabled. Proceed with manual description?"

3. If human approves manual mode:
   - Create mockup-description.md with:
     - Detailed layout descriptions
     - Component specifications
     - ASCII wireframes (optional)
   - Save to docs/ideas/simple-idea/mockups/mockup-description.md

4. Output:
   task_output_links:
     - docs/ideas/simple-idea/mockups/mockup-description.md

5. If human declines:
   - Skip mockup creation
   - Note in idea summary: "Mockups deferred - no tools available"
   - Proceed to next task
```
