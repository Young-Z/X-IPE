# Mockup Guidelines Reference

This document contains detailed mockup creation techniques, tool-specific examples, and design principles.

---

## UI/UX Focus Guidelines

### What to Focus On vs. Ignore

| Focus On | Ignore |
|----------|--------|
| Visual layout and composition | Backend tech stack (Python, Node.js, etc.) |
| User interaction patterns | Database choices (PostgreSQL, MongoDB, etc.) |
| Navigation and flow | API implementation details |
| Color schemes and typography | Framework specifics (React, Vue, Django, etc.) |
| Responsive design | Infrastructure and deployment |
| Component placement | Authentication mechanisms |
| User experience | Server architecture |

**Rationale:** Mockups visualize the user experience, not technical implementation. Tech stack decisions come later during Technical Design.

### Example Application

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

## Extra Instructions Handling

### Purpose
Provides additional context or requirements for mockup creation.

### Source Priority
1. Human input (explicit instructions provided)
2. `x-ipe-docs/config/tools.json` → `stages.ideation.mockup._extra_instruction` field
3. Default: N/A (no extra instructions)

### Loading Logic

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

**Usage:** When Extra Instructions are provided, incorporate them into the mockup creation workflow, particularly when designing UI elements and choosing visual styles.

---

## Current Idea Folder Handling

### Validation Procedure

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

### Usage
- All mockups saved to `{Current Idea Folder}/mockups/`
- Idea summary updates reference `{Current Idea Folder}/idea-summary-vN.md`
- Output links use `{Current Idea Folder}` as base path

---

## Tool Configuration Details

### Relevant Config Section

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

### Tool Loading Rules

1. **File exists:** Load and parse the JSON configuration
2. **File missing:** Inform user mockup tools not configured, proceed with manual description
3. **Tool enabled (`true`):** Invoke corresponding skill/capability
4. **Tool disabled (`false`):** Skip the tool
5. **Tool unavailable:** Log limitation and provide alternative

### Mockup Tool Mapping

| Config Key | Skill/Capability | What It Creates |
|------------|------------------|-----------------|
| `stages.ideation.mockup.tool-frontend-design` | `tool-frontend-design` skill | HTML/CSS mockups, interactive prototypes |
| `stages.ideation.mockup.figma-mcp` | Figma MCP server | Figma design files |
| `stages.ideation.mockup.excalidraw` | Excalidraw integration | Sketch-style wireframes |

---

## Mockup Analysis Guidelines

### Analysis Questions

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

### Mockup Types by Idea Content

| Idea Contains | Mockup Type | Priority |
|---------------|-------------|----------|
| Dashboard description | Dashboard layout | High |
| Form/input mentions | Form mockup | High |
| List/table data | Data display mockup | Medium |
| Navigation mentions | Nav structure | Medium |
| Charts/graphs | Data visualization | Medium |
| Mobile mentions | Mobile-responsive mockup | High |

---

## Tool Invocation Details

### Tool-Frontend-Design Invocation

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

**Skill Invocation Format:**
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

### Figma MCP Invocation

**IF `mockup.figma-mcp: true`:**
```
1. Check Figma MCP server connection
2. Create new Figma file or use template
3. Generate basic layout based on idea
4. Return Figma file link
```

### Manual Mode

**IF no tools enabled:**
```
1. Create detailed mockup description in markdown
2. Include ASCII art or text-based layout
3. Document component specifications
4. Save as mockup-description.md in {Current Idea Folder}/mockups/
```

---

## Artifact Management

### Directory Structure

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

### Naming Convention

```
{mockup-type}-v{version}.{extension}

Examples:
- dashboard-v1.html
- user-form-v1.html
- mobile-home-v1.html
```

---

## Summary Update Template

**Add to new summary version:**
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

---

## Completion Output Format

```yaml
category: ideation-stage
task_type: Idea Mockup
auto_proceed: {from input Auto Proceed}
idea_id: IDEA-XXX
current_idea_folder: {Current Idea Folder}
mockup_tools_used:
  - tool-frontend-design
mockups_created:
  - type: dashboard
    path: {Current Idea Folder}/mockups/dashboard-v1.html
  - type: form
    path: {Current Idea Folder}/mockups/user-form-v1.html
mockup_list:
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

**Mockup List Flow:**
```
Idea Mockup → Requirement Gathering → Feature Breakdown → Feature Refinement → Technical Design
```
Each subsequent task receives and passes the mockup_list to ensure mockups are referenced throughout the development lifecycle.
