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
- Learn `task-execution-guideline` and `task-board-management` skills first.
- Learn `tool-frontend-design` skill if enabled in config.

**Important:** If Agent lacks skill capability, go to `.github/skills/` folder to learn skills via SKILL.md files.

### ⚠️ UI/UX Focus Only

**Focus ONLY on UI/UX presentation—ignore all tech stack mentions.**

See [references/mockup-guidelines.md](references/mockup-guidelines.md) for detailed focus guidelines.

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
| Current Idea Folder | N/A | **Required from context** - path to current idea folder |
| Extra Instructions | N/A | Additional context or requirements for mockup creation |

**Attribute Details:** See [references/mockup-guidelines.md](references/mockup-guidelines.md) for:
- Extra Instructions loading logic and usage
- Current Idea Folder validation procedure
- Tool configuration details and loading rules

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

**Action:** Read and parse mockup section from `x-ipe-docs/config/tools.json`

```
1. Check if config file exists
2. If exists: Parse JSON, extract stages.ideation.mockup section
3. If NOT exists: Ask "Proceed with manual mockup description? (Y/N)"
4. Load Extra Instructions (human input > config > N/A)
5. Log active configuration
```

**Tool Mapping:** See [references/mockup-guidelines.md](references/mockup-guidelines.md) for detailed tool mapping table.

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

**Analysis:** Identify screens/pages, interactive elements, workflow visualizations, and primary user-facing components.

**Mockup Types:** See [references/mockup-guidelines.md](references/mockup-guidelines.md) for mockup type priority table.

**Output:** Prioritized list of mockups to create

### Step 5: Create Mockups

**Action:** Invoke enabled mockup tools to create visual artifacts

**⚠️ REMINDER: Focus on UI/UX only. Ignore all tech stack mentions from idea files.**

**Tool-specific invocation details:** See [references/mockup-guidelines.md](references/mockup-guidelines.md) for:
- `tool-frontend-design` skill invocation format
- Figma MCP invocation procedure
- Manual mode procedure

**Output:** Generated mockup files/links

### Step 6: Save Artifacts

**Action:** Store all mockup artifacts in `{Current Idea Folder}/mockups/`

**Directory structure and naming conventions:** See [references/mockup-guidelines.md](references/mockup-guidelines.md).

**Output:** List of saved artifact paths (relative to Current Idea Folder)

### Step 7: Update Idea Summary

**Action:** Create new version `{Current Idea Folder}/idea-summary-v{N+1}.md` with mockup references

**DO NOT modify existing idea-summary files.**

**Summary update template:** See [references/mockup-guidelines.md](references/mockup-guidelines.md).

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

This skill MUST return these attributes to the Task Data Model upon task completion.

**Output format:** See [references/mockup-guidelines.md](references/mockup-guidelines.md) for complete output YAML structure.

**Key output attributes:**
- `category`: ideation-stage
- `task_type`: Idea Mockup  
- `current_idea_folder`: {Current Idea Folder}
- `mockup_list`: List of all mockup paths (passed to next tasks in chain)
- `next_task_type`: Requirement Gathering
- `require_human_review`: true

**Mockup List Flow:** The `mockup_list` is passed through: Idea Mockup → Requirement Gathering → Feature Breakdown → Feature Refinement → Technical Design

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
