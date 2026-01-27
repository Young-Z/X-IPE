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

### Tool Behavior by Section

When tools are enabled in the meta file, the agent MUST attempt to use them during the ideation process:

| Tool Type | When to Use | Example Tools |
|-----------|-------------|---------------|
| Design Tools | Visual mockups, wireframes | `frontend-design`, Figma MCP |
| Diagram Tools | Flowcharts, architecture diagrams | `mermaid`, `antv-infographic` |
| Research Tools | Market analysis, competitor research | Web search, databases |
| Prototyping Tools | Quick demos, proof of concepts | Code generation, no-code tools |

**Usage Rules:**
1. Read `x-ipe-docs/config/tools.json` at start of ideation task
2. For each section (`stages.ideation.ideation`, `stages.ideation.mockup`, `stages.ideation.sharing`), check enabled tools
3. If tool is enabled (`true`) → Attempt to use during relevant steps
4. If tool is unavailable or fails → Document the limitation and proceed manually
5. Always inform user which tools are active based on config

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

```
1. For each section in config (stages.ideation.ideation, stages.ideation.mockup, stages.ideation.sharing):
   a. Identify tools with value = true
   b. For each enabled tool:
      - Check if tool is available (skill, MCP, API)
      - Test basic connectivity/functionality
      - Document tool capabilities and limitations
2. If tool unavailable:
   a. Log the issue
   b. Inform user of limitation
   c. Proceed with manual alternatives
```

**Tool Mapping & Skill Invocation:**

| Config Key | Skill/Capability | How to Invoke |
|------------|------------------|---------------|
| `stages.ideation.ideation.antv-infographic` | `infographic-syntax-creator` skill | Call skill to generate infographic DSL syntax |
| `stages.ideation.ideation.mermaid` | Mermaid code blocks | Generate mermaid diagrams directly in markdown |
| `stages.ideation.ideation.tool-architecture-dsl` | `tool-architecture-dsl` skill | Generate Architecture DSL directly in markdown (IPE renders it) |
| `stages.ideation.mockup.frontend-design` | `frontend-design` skill | Call skill to create HTML/CSS mockups |
| `stages.ideation.mockup.figma-mcp` | Figma MCP server | Use MCP tools for Figma integration |

**Skill Invocation Rules:**

```
For each enabled tool in config:
  IF config.stages.ideation.ideation["antv-infographic"] == true:
    → Load and invoke `infographic-syntax-creator` skill for visual summaries
    → Use infographic DSL in idea-summary document
    
  IF config.stages.ideation.ideation["mermaid"] == true:
    → Generate mermaid diagrams for flowcharts, sequences
    → Embed as ```mermaid code blocks in documents
    
  IF config.stages.ideation.ideation["tool-architecture-dsl"] == true:
    → Load `tool-architecture-dsl` skill for layered architecture diagrams
    → Generate Architecture DSL directly in markdown
    → Embed as ```architecture-dsl code blocks (IPE renders natively)
    → Use for: module view (layers, services), landscape view (integrations)
    
  IF config.stages.ideation.mockup["frontend-design"] == true:
    → Load and invoke `frontend-design` skill during brainstorming
    → Create interactive HTML mockups when discussing UI concepts
    → Save mockups to x-ipe-docs/ideas/{folder}/mockup-vN.html (version aligned with idea-summary)
    
  IF config.stages.ideation.mockup["figma-mcp"] == true:
    → Use Figma MCP tools if available
    → Create/update designs in connected Figma files
```

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

**Tool-Enhanced Brainstorming (Based on Config):**

When tools are enabled in `x-ipe-docs/config/tools.json`, invoke corresponding skills during brainstorming:

| Config Enabled | Skill to Invoke | When to Use |
|----------------|-----------------|-------------|
| `stages.ideation.mockup.frontend-design: true` | `frontend-design` skill | User describes UI → Create HTML mockup |
| `stages.ideation.ideation.mermaid: true` | Mermaid syntax | User describes flow → Generate diagram |
| `stages.ideation.ideation.antv-infographic: true` | `infographic-syntax-creator` skill | Visualize lists, comparisons |
| `stages.ideation.ideation.tool-architecture-dsl: true` | `tool-architecture-dsl` skill | User describes layers/services → Generate architecture DSL |

**Example: Config-Driven Tool Usage:**
```
Config: { "stages": { "ideation": { "mockup": { "frontend-design": true } } } }

User: "I want a dashboard with charts and filters"
Agent Action:
  1. Ask clarifying questions about chart types, layout preferences
  2. IF stages.ideation.mockup.frontend-design == true:
     → Invoke `frontend-design` skill
     → Create interactive HTML mockup
     → Save to x-ipe-docs/ideas/{folder}/mockup-vN.html (aligned with idea-summary version)
  3. Share mockup: "I've created a mockup - does this match your vision?"
  4. Iterate based on feedback
```

**Example: Mermaid Diagram Generation:**
```
Config: { "stages": { "ideation": { "ideation": { "mermaid": true } } } }

User: "The user flow goes from login to dashboard to settings"
Agent Action:
  1. IF stages.ideation.ideation.mermaid == true:
     → Generate mermaid flowchart
     → Share in conversation:
     
     ```mermaid
     flowchart LR
       Login --> Dashboard --> Settings
     ```
  2. Ask: "Does this capture the flow correctly?"
```

**Example: Architecture DSL Generation:**
```
Config: { "stages": { "ideation": { "ideation": { "tool-architecture-dsl": true } } } }

User: "The system has 3 layers: frontend, backend services, and database"
Agent Action:
  1. IF stages.ideation.ideation.tool-architecture-dsl == true:
     → Load `tool-architecture-dsl` skill
     → Generate Architecture DSL directly in markdown
     → Embed in idea-summary as:
     
     ```architecture-dsl
     @startuml module-view
     title "System Architecture"
     theme "theme-default"
     direction top-to-bottom
     grid 12 x 6
     
     layer "Frontend" {
       color "#fce7f3"
       border-color "#ec4899"
       rows 2
       module "Web" { cols 12, rows 2, grid 1 x 1, component "React App" { cols 1, rows 1 } }
     }
     
     layer "Backend" {
       color "#dbeafe"
       border-color "#3b82f6"
       rows 2
       module "Services" { cols 12, rows 2, grid 2 x 1, component "API" { cols 1, rows 1 }, component "Workers" { cols 1, rows 1 } }
     }
     
     layer "Data" {
       color "#dcfce7"
       border-color "#22c55e"
       rows 2
       module "Storage" { cols 12, rows 2, grid 1 x 1, component "PostgreSQL" { cols 1, rows 1 } }
     }
     
     @enduml
     ```
  2. IPE renders this as interactive diagram in the browser
  3. Ask: "Does this architecture structure match your vision?"
```

**Question Categories:**

| Category | Example Questions |
|----------|-------------------|
| Problem Space | "What problem does this solve?" |
| Target Users | "Who will benefit from this?" |
| Scope | "What should be included in v1?" |
| Constraints | "Are there any technical limitations?" |
| Success Criteria | "How will we know it's successful?" |
| Alternatives | "Have you considered approach X?" |

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
- Established patterns or frameworks are relevant
- The idea could benefit from proven approaches

**Research Process:**
```
1. Identify if topic is common/established
2. Use web_search tool to research:
   - Industry best practices
   - Common design patterns
   - Established principles
   - Reference implementations
3. Document findings as "Common Principles"
4. Note authoritative sources for references
```

**Example Common Topics & Principles:**

| Topic | Common Principles to Research |
|-------|------------------------------|
| Authentication | OAuth 2.0, JWT best practices, MFA patterns |
| API Design | REST conventions, OpenAPI, rate limiting |
| Data Storage | ACID properties, CAP theorem, data modeling |
| UI/UX | Nielsen heuristics, accessibility (WCAG), mobile-first |
| Security | OWASP Top 10, zero-trust, encryption standards |
| Scalability | Horizontal scaling, caching strategies, CDN usage |
| DevOps | CI/CD pipelines, IaC, observability |

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

**Mockup Versioning:**

When creating mockups, the version MUST align with the idea-summary version:

```
Naming Convention: mockup-vN.html (where N matches idea-summary-vN.md)

Examples:
- idea-summary-v1.md → mockup-v1.html
- idea-summary-v2.md → mockup-v2.html
- idea-summary-v3.md → mockup-v3.html

Location: x-ipe-docs/ideas/{folder}/mockup-vN.html (same folder as idea-summary)
```

**Versioning Logic:**
```
1. Determine current idea-summary version (N)
2. If creating mockup during this ideation session:
   → Name it mockup-vN.html to match the idea-summary version
3. If mockup-vN.html already exists:
   → Overwrite it (mockup is tied to that idea version)
4. Reference mockup in idea-summary-vN.md:
   → Link: [View Mockup](./mockup-vN.html)
```

**Config-Driven Visualization:**

```
When creating idea summary, check x-ipe-docs/config/tools.json config:

IF config.stages.ideation.ideation["antv-infographic"] == true:
  → Invoke `infographic-syntax-creator` skill
  → Use infographic DSL for: feature lists, roadmaps, comparisons

IF config.stages.ideation.ideation["mermaid"] == true:
  → Use mermaid syntax for: flowcharts, sequences, state diagrams

IF config.stages.ideation.ideation["tool-architecture-dsl"] == true:
  → Use Architecture DSL for: layered architecture, module views, landscape views
  → Embed directly in markdown as ```architecture-dsl code blocks
  → IPE renders these natively as interactive diagrams

IF ALL are false:
  → Use standard markdown (bullet lists, tables)
```

**Template:** See `templates/idea-summary.md`

**Visualization Guide:** See `references/visualization-guide.md`

**Output:** New versioned idea summary file and aligned mockup file (if mockup tools enabled)

---

### Step 8: Rename Folder (If Draft Idea)

**Action:** If the idea folder has the default "Draft Idea" name, rename it based on the refined idea content

**When to Rename:**
- Folder name matches pattern: `Draft Idea - MMDDYYYY HHMMSS`
- Idea has been refined and has a clear identity

**Naming Logic:**
```
1. Check if folder name starts with "Draft Idea - "
2. If YES:
   a. Extract timestamp suffix (MMDDYYYY HHMMSS)
   b. Generate idea name from:
      - Core concept identified in brainstorming
      - Main theme from idea summary
      - Keep it concise (2-5 words)
   c. Format new name: "{Idea Name} - {timestamp}"
   d. Rename folder using filesystem/API
   e. Update any internal references if needed
3. If NO (already has custom name):
   a. Skip renaming
   b. Log: "Folder already has custom name"
```

**Naming Guidelines:**
- Use Title Case for idea name
- Keep name concise but descriptive (2-5 words)
- Avoid special characters (use only alphanumeric, spaces, hyphens)
- Preserve the original timestamp suffix

**Examples:**

| Original Folder | Idea Content | New Folder Name |
|-----------------|--------------|-----------------|
| `Draft Idea - 01232026 143500` | Mobile app for task management | `Task Manager App - 01232026 143500` |
| `Draft Idea - 01222026 091200` | AI-powered code review tool | `AI Code Reviewer - 01222026 091200` |
| `Draft Idea - 01212026 160000` | E-commerce checkout optimization | `Checkout Optimizer - 01212026 160000` |

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
