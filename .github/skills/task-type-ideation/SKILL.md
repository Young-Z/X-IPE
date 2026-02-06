---
name: task-type-ideation
description: Learn and refine user ideas through brainstorming. Use when user uploads idea files to the Workplace. Analyzes uploaded content, asks clarifying questions, and produces structured idea summary. Triggers on requests like "ideate", "brainstorm", "refine idea", "analyze my idea".
---

# Task Type: Ideation

## Purpose

Learn and refine user ideas through collaborative brainstorming by:
1. Analyzing uploaded idea files from Workplace
2. Generating an initial understanding summary
3. Asking clarifying questions to brainstorm with user
4. Creating a structured idea summary document with visual infographics
5. Preparing for Idea Mockup, Idea to Architecture, or Requirement Gathering

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` and `task-board-management` skill, please learn them first before executing this skill.
- **Infographic Skill:** Learn `infographic-syntax-creator` skill to generate visual infographics in the idea summary.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Ideation |
| Category | ideation-stage |
| Standalone | No |
| Next Task | Idea Mockup OR Idea to Architecture (human choice) |
| Auto-advance | No |
| Human Review | Yes |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |
| Ideation Toolbox Meta | `{project_root}/x-ipe-docs/config/tools.json` |
| Extra Instructions | N/A |

### Extra Instructions Attribute

**Purpose:** Provides additional context or requirements for the ideation process.

**Source:** This value can be obtained from:
1. Human input (explicit instructions provided)
2. `x-ipe-docs/config/tools.json` → `stages.ideation.ideation._extra_instruction` field
3. Default: N/A (no extra instructions)

**Loading Logic:**
```
1. IF human provides explicit Extra Instructions:
   → Use human-provided value

2. ELSE IF x-ipe-docs/config/tools.json exists:
   a. Read stages.ideation.ideation._extra_instruction field
   b. IF field exists AND is not empty:
      → Use value from config
   c. ELSE:
      → Use default: N/A

3. IF Extra Instructions != N/A:
   → Apply these instructions throughout the ideation process
   → Consider them when generating understanding summary
   → Factor them into brainstorming questions
   → Include relevant aspects in idea summary
```

**Usage:** When Extra Instructions are provided, the agent MUST incorporate them into the ideation workflow, particularly during brainstorming and summary generation.

### Ideation Toolbox Meta File

**Location:** `x-ipe-docs/config/tools.json` (relative to project root)

**Purpose:** Defines which tools are enabled for ideation, mockup creation, and idea sharing.

**Format:**
```json
{
  "version": "2.0",
  "stages": {
    "ideation": {
      "ideation": {
        "antv-infographic": false,
        "mermaid": true
      },
      "mockup": {
        "frontend-design": true
      },
      "sharing": {}
    }
  }
}
```

**Configuration Sections:**

| Section | Purpose | Example Tools |
|---------|---------|---------------|
| `stages.ideation.ideation` | Visual representation during brainstorming | `antv-infographic`, `mermaid` |
| `stages.ideation.mockup` | UI/UX mockup creation | `frontend-design`, `figma-mcp` |
| `stages.ideation.sharing` | Export/share idea artifacts | `pptx-export`, `pdf-export` |

**Tool Loading Rules:**

1. **File exists:** Load and parse the JSON configuration
2. **File missing:** 
   - Create default file with all tools set to `false`
   - Inform user: "No ideation tools configured. Create `x-ipe-docs/config/tools.json` to enable tools."
3. **Tool enabled (`true`):** Attempt to use the tool during ideation
4. **Tool disabled (`false`):** Skip the tool
5. **Tool unavailable:** Log limitation and proceed without it

See [references/tool-usage-guide.md](references/tool-usage-guide.md) for detailed tool behavior, mapping, and usage examples.

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Idea files uploaded to `x-ipe-docs/ideas/{folder}/` | Yes |
| 2 | Human available for brainstorming | Yes |
| 3 | Idea folder path provided | Yes |

---

## Execution Flow

Execute Ideation by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Load Toolbox Meta | Read `x-ipe-docs/config/tools.json` config | Config loaded |
| 2 | Analyze Files | Read all files in idea folder | Files analyzed |
| 3 | Initialize Tools | Set up enabled tools from config | Tools ready (or skipped) |
| 4 | Generate Summary | Create understanding summary for user | Summary shared |
| 5 | Brainstorm | Ask clarifying questions (3-5 at a time) | Idea refined |
| 6 | Research | Search for common principles if topic is established | Research complete |
| 7 | Create Summary | Write `idea-summary-vN.md` with infographics | Summary created |
| 8 | Rename Folder | If folder is "Draft Idea - xxx", rename based on idea content | Folder renamed |
| 9 | Complete | Request human review and approval | Human approves |

**⛔ BLOCKING RULES:**
- Step 5: Continue brainstorming until idea is well-defined
- Step 9 → Human Review: Human MUST approve idea summary before proceeding

---

## Execution Procedure

### Step 1: Load Ideation Toolbox Meta

**Action:** Read and parse the ideation tools configuration file

**Default Path:** `x-ipe-docs/config/tools.json`

```
1. Check if x-ipe-docs/config/tools.json exists
2. If exists:
   a. Parse JSON file
   b. Validate version and structure
   c. Extract enabled tools from stages.ideation.ideation section
   d. Extract _extra_instruction from stages.ideation.ideation section (if exists)
3. If NOT exists:
   a. Create default config file with all tools disabled
   b. Inform user: "Created default x-ipe-docs/config/tools.json - configure tools to enable"
4. Load Extra Instructions:
   a. IF human provided explicit Extra Instructions → Use human value
   b. ELSE IF _extra_instruction field exists and is not empty → Use config value
   c. ELSE → Set Extra Instructions = N/A
5. Log active tool configuration and Extra Instructions (if any)
```

**Expected Format:**
```json
{
  "version": "2.0",
  "stages": {
    "ideation": {
      "ideation": {
        "antv-infographic": false,
        "mermaid": true
      },
      "mockup": {
        "frontend-design": true
      },
      "sharing": {}
    }
  }
}
```

**Output:** Tool configuration summary showing enabled tools per section

### Step 2: Locate and Analyze Idea Files

**Action:** Read all files in the specified idea folder

```
1. Navigate to x-ipe-docs/ideas/{folder}/files/
2. Read each file (text, markdown, code, etc.)
3. Identify key themes, concepts, and goals
4. Note any gaps or ambiguities
```

**Output:** Initial analysis summary

### Step 3: Initialize Ideation Tools (Based on Config)

**Action:** Set up and test tools enabled in `x-ipe-docs/config/tools.json`

**When:** Any tool is set to `true` in the config file

**Process:** Check tool availability and test connectivity for each enabled tool in config sections.

See [references/tool-usage-guide.md](references/tool-usage-guide.md) for tool mapping tables and skill invocation rules.

**Output:** Tools status report (enabled/disabled/unavailable)

### Step 4: Generate Understanding Summary

**Action:** Create a summary of what you understand from the uploaded content

**Summary Structure:**
```markdown
## Idea Understanding Summary

### Core Concept
{What is the main idea about?}

### Key Goals
{What does the user want to achieve?}

### Identified Components
{What features/parts are mentioned?}

### Questions & Ambiguities
{What needs clarification?}

### Enabled Tools (from x-ipe-docs/config/tools.json)
- Ideation: {list enabled ideation tools}
- Mockup: {list enabled mockup tools}
- Sharing: {list enabled sharing tools}
```

**Output:** Share summary with user for validation

### Step 5: Brainstorming Session

**Action:** Engage user with clarifying questions to refine the idea

**Tool-Enhanced Brainstorming:** When tools are enabled, invoke corresponding skills during brainstorming. See [references/tool-usage-guide.md](references/tool-usage-guide.md) for detailed examples.

**Rules:**
- Ask questions in batches (3-5 at a time)
- Wait for human response before proceeding
- Build on previous answers
- Challenge assumptions constructively
- Suggest alternatives when appropriate
- **Check config before using tools** - only invoke if enabled

**Important:**
1. This is a collaborative brainstorming session, not an interview
2. Offer creative suggestions and perspectives
3. Help user think through implications
4. Continue until idea is well-defined
5. **Invoke enabled skills** to make abstract concepts concrete

### Step 6: Research Common Principles (If Applicable)

**Action:** Identify if the idea involves common/established topics and research relevant principles

**When to Research:**
- The idea touches well-known domains (e.g., authentication, e-commerce, data pipelines)
- Industry best practices exist for the problem space

See [references/tool-usage-guide.md](references/tool-usage-guide.md#research-common-principles) for detailed research process and example topics.

**Output:** List of relevant principles with sources to include in idea summary

---

### Step 7: Create Idea Summary Document

**Action:** Create versioned summary file `x-ipe-docs/ideas/{folder}/idea-summary-vN.md`

**Important:** 
- Do NOT update existing idea-summary files
- Always create a NEW versioned file: `idea-summary-v1.md`, `idea-summary-v2.md`, etc.
- The version number auto-increments based on existing files in the folder
- **Use visualization tools based on config** (see `references/visualization-guide.md`)
- **If tools were used:** Include artifacts created (mockups, prototypes) in the summary

**Mockup Versioning:** When creating mockups, version aligns with idea-summary (e.g., `idea-summary-v1.md` → `mockup-v1.html`). Save to `x-ipe-docs/ideas/{folder}/mockup-vN.html`.

**Config-Driven Visualization:** Check `x-ipe-docs/config/tools.json` and use enabled tools (infographic, mermaid, architecture-dsl) for visualizations. If all disabled, use standard markdown.

See [references/tool-usage-guide.md](references/tool-usage-guide.md#config-driven-visualization-for-idea-summary) for detailed config-driven visualization rules.

**Template:** See `templates/idea-summary.md`

**Visualization Guide:** See `references/visualization-guide.md`

**Output:** New versioned idea summary file and aligned mockup file (if mockup tools enabled)

---

### Step 8: Rename Folder (If Draft Idea)

**Action:** If the idea folder has the default "Draft Idea" name, rename it based on the refined idea content

**When:** Folder name matches pattern `Draft Idea - MMDDYYYY HHMMSS` and idea has a clear identity.

See [references/folder-naming-guide.md](references/folder-naming-guide.md) for detailed naming logic, guidelines, and examples.

**Output:** Folder renamed (or skipped if already named)

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | `x-ipe-docs/config/tools.json` loaded and parsed | Yes |
| 2 | All idea files analyzed | Yes |
| 3 | Enabled tools initialized (based on config) | If Tools Enabled |
| 4 | Brainstorming session completed | Yes |
| 5 | Enabled skills invoked during brainstorming | If Tools Enabled |
| 6 | Common principles researched (if topic is common/established) | If Applicable |
| 7 | `x-ipe-docs/ideas/{folder}/idea-summary-vN.md` created (versioned) | Yes |
| 8 | Visualization used based on config (infographic/mermaid) | If Tools Enabled |
| 9 | Ideation artifacts documented (mockups, prototypes) | If Mockup Tools Used |
| 10 | Folder renamed if "Draft Idea - xxx" pattern | If Applicable |
| 11 | References included for researched principles | If Applicable |
| 12 | Human has reviewed and approved idea summary | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:
```yaml
category: ideation-stage
auto_proceed: {from input Auto Proceed}
idea_id: IDEA-XXX
idea_status: Refined
idea_version: vN
idea_folder: {new folder name if renamed, otherwise original}
folder_renamed: true | false
next_task_type: Idea Mockup | Idea to Architecture  # Human chooses based on idea type
require_human_review: true
task_output_links:
  - x-ipe-docs/ideas/{folder}/idea-summary-vN.md
  - x-ipe-docs/ideas/{folder}/mockup-vN.html  # if mockup tools enabled
```

### Next Task Selection

After ideation completes, ask human to choose the next task:

```
Your idea has been refined. What would you like to do next?

1. **Idea Mockup** - Create UI/UX mockups and visual prototypes
   → Best for: Ideas with strong user interface focus
   
2. **Idea to Architecture** - Create system architecture diagrams
   → Best for: Ideas requiring system design, integrations, or technical planning

3. **Skip to Requirement Gathering** - Go directly to requirements
   → Best for: Simple ideas or when mockups/architecture are not needed
```

**Selection Logic:**
- If idea mentions UI, screens, user interactions → Suggest Mockup
- If idea mentions services, integrations, data flow → Suggest Architecture
- If idea is simple or clear → Allow skip to Requirements
- Human makes final decision

---

## Patterns

### Pattern: Raw Notes Upload

**When:** User uploads unstructured notes or braindump
**Then:**
```
1. Extract key themes from notes
2. Organize into logical categories
3. Ask clarifying questions about each category
4. Help structure into coherent idea
```

### Pattern: Technical Specification Upload

**When:** User uploads detailed technical spec
**Then:**
```
1. Validate technical feasibility
2. Ask about business goals (why this spec?)
3. Identify missing user context
4. Connect technical details to user value
```

### Pattern: Competitive Analysis Upload

**When:** User uploads competitor analysis or inspiration
**Then:**
```
1. Identify what user likes about competitors
2. Ask what should be different/better
3. Help define unique value proposition
4. Document differentiators
```

### Pattern: Multiple Conflicting Ideas

**When:** Uploaded files contain conflicting approaches
**Then:**
```
1. Surface the conflicts clearly
2. Ask user to prioritize or choose
3. Help evaluate trade-offs
4. Document decision rationale
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Just summarizing without questions | Misses refinement opportunity | Engage in brainstorming |
| Too many questions at once | Overwhelms user | Batch 3-5 questions |
| Accepting everything at face value | May miss issues | Challenge assumptions constructively |
| Skipping to requirements | Idea not refined | Complete ideation first |
| Being passive | Not collaborative | Offer suggestions actively |
| Ignoring `x-ipe-docs/config/tools.json` | Misses tool capabilities | Always check config first |
| Using tools when disabled in config | Unexpected behavior | Respect config settings |
| Plain text when visualization enabled | Harder to scan visually | Use configured tools (infographic/mermaid/architecture-dsl) |
| Creating separate HTML for architecture | Unnecessary when DSL enabled | Embed `architecture-dsl` directly in markdown (IPE renders it) |

---

## Example

See [references/examples.md](references/examples.md) for detailed execution examples including:
- Business plan ideation with tools enabled (infographics, mermaid, mockups)
- Ideation without tools (all disabled)
- Missing config file handling
- Draft folder rename scenario

---

## Skill Resources

| Resource | Path | Description |
|----------|------|-------------|
| Idea Summary Template | `templates/idea-summary.md` | Template for creating idea summary documents |
| Visualization Guide | `references/visualization-guide.md` | Detailed guide for infographic and mermaid usage |
