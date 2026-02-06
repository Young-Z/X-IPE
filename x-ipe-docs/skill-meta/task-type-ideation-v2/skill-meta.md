# Skill Meta: task-type-ideation-v2

## Basic Information

| Attribute | Value |
|-----------|-------|
| Skill Name | task-type-ideation-v2 |
| Skill Type | task_type |
| Category | ideation-stage |
| Template | templates/task-type-skill.md |

## Purpose

Learn and refine user ideas through collaborative brainstorming by:
1. Analyzing uploaded idea files from Workplace
2. Generating an initial understanding summary
3. Asking clarifying questions to brainstorm with user
4. Creating a structured idea summary document with visual infographics
5. Preparing for Idea Mockup, Idea to Architecture, or Requirement Gathering

## Triggers

- "ideate"
- "brainstorm"
- "refine idea"
- "analyze my idea"
- "start ideation"
- User uploads idea files to `x-ipe-docs/ideas/{folder}/files/`

## Example Scenarios

### Scenario 1: Business Plan with Tools Enabled
- User uploads business plan to ideas folder
- Config has antv-infographic and mermaid enabled
- Agent analyzes, brainstorms with visual aids, creates rich summary

### Scenario 2: Raw Notes without Tools
- User uploads unstructured notes
- Config has all tools disabled
- Agent analyzes, brainstorms via text, creates markdown summary

### Scenario 3: Draft Folder Rename
- Folder named "Draft Idea - MMDDYYYY HHMMSS"
- After refinement, rename based on idea content

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_type: "Ideation"
  category: ideation-stage
  next_task_type: "Idea Mockup | Idea to Architecture"
  require_human_review: yes
  auto_proceed: false
  idea_folder_path: "x-ipe-docs/ideas/{folder}"
  toolbox_meta_path: "x-ipe-docs/config/tools.json"
  extra_instructions: "{N/A or from config or human}"
```

## Output Parameters

```yaml
task_completion_output:
  category: ideation-stage
  status: completed | blocked
  next_task_type: "Idea Mockup | Idea to Architecture"
  require_human_review: yes
  task_output_links:
    - "x-ipe-docs/ideas/{folder}/idea-summary-vN.md"
    - "x-ipe-docs/ideas/{folder}/mockups/mockup-vN.html"
  idea_id: "IDEA-XXX"
  idea_status: Refined
  idea_version: "vN"
  idea_folder: "{renamed folder name or original}"
  folder_renamed: true | false
```

## Acceptance Criteria

### MUST Pass (Required)

| AC ID | Description | Verification |
|-------|-------------|--------------|
| AC-M1 | SKILL.md follows v3 section order | Sections: Purpose → Important Notes → Input Parameters → DoR → Execution Flow → Execution Procedure → Output Result → DoD → Patterns & Anti-Patterns → Examples |
| AC-M2 | SKILL.md under 500 lines | `wc -l SKILL.md` < 500 |
| AC-M3 | Frontmatter valid | name (1-64 chars) + description with triggers |
| AC-M4 | DoR uses XML format | `<definition_of_ready>` with checkpoints |
| AC-M5 | DoD uses XML format | `<definition_of_done>` with checkpoints |
| AC-M6 | Execution procedure uses XML format | `<procedure name="ideation-v2">` |
| AC-M7 | Keywords used for importance | BLOCKING/CRITICAL/MANDATORY (not emoji) |
| AC-M8 | Examples in references/ | `references/examples.md` exists |
| AC-M9 | Draft-Critique-Improve flow | Steps 7, 8, 9 implement refinement cycle |

### SHOULD Pass (Recommended)

| AC ID | Description | Verification |
|-------|-------------|--------------|
| AC-S1 | Config loading documented | Step for loading tools.json |
| AC-S2 | Brainstorming rules clear | 3-5 questions per batch |
| AC-S3 | Folder rename logic documented | Pattern match and rename rules |
| AC-S4 | Next task selection documented | Human choice between Mockup/Architecture |
| AC-S5 | Critique sub-agent defined | Step 8 has sub_agent specification |

## Resources Plan

| Resource Type | Files | Purpose |
|---------------|-------|---------|
| templates/ | idea-summary.md | Template for idea summary output |
| references/ | examples.md | Detailed execution examples |
| references/ | tool-usage-guide.md | Tool configuration and invocation |
| references/ | folder-naming-guide.md | Draft folder rename logic |
| references/ | visualization-guide.md | Infographic/mermaid usage |

## Related Skills

| Skill | Relationship |
|-------|-------------|
| task-execution-guideline | Prerequisite |
| task-board-management | Task tracking |
| infographic-syntax-creator | Visual infographics (if enabled) |
| frontend-design | Mockups (if enabled) |
| tool-architecture-dsl | Architecture diagrams (if enabled) |
