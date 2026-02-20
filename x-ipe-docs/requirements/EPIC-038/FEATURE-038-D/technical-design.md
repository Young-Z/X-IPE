# Technical Design: Refinement Skill Integration

> Feature ID: FEATURE-038-D | Version: v1.0 | Last Updated: 02-20-2026

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating large projects.
> **📌 AI Coders:** Focus on this section for implementation context.

### Key Components Implemented

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| `ideation-v2 Input Params` | Accept `extra_instructions` parameter | Skill input section | #skills #ideation #input |
| `ideation-v2 Output Config` | Output to `refined-idea/` subfolder | Skill output section | #skills #ideation #output |
| `ideation-v2 DoD` | Call `update_workflow_action` MCP | Skill completion flow | #skills #mcp #workflow |

### Dependencies

| Dependency | Source | Design Link | Usage Description |
|------------|--------|-------------|-------------------|
| `x-ipe-task-based-ideation-v2` | Foundation | `.github/skills/x-ipe-task-based-ideation-v2/SKILL.md` | The skill being modified |
| `update_workflow_action` MCP | FEATURE-036 | `src/x_ipe/mcp/app_agent_interaction.py` | Reports completion status to workflow manager |
| `x-ipe-meta-skill-creator` | Process | `.github/skills/x-ipe-meta-skill-creator/SKILL.md` | Candidate workflow for skill updates |

### Major Flow

1. Action Execution Modal constructs CLI command with `extra_instructions` appended
2. Agent receives prompt, loads ideation skill → sees `extra_instructions` in input parameters
3. During brainstorming, agent incorporates extra instructions as additional context
4. Output written to `{idea_folder}/refined-idea/` (overwrite mode: clear folder first)
5. In DoD, agent calls `update_workflow_action(workflow_name, "refine_idea", "done", deliverables=["{idea_folder}/refined-idea/"])`

### Usage Example

```yaml
# Skill input (received from CLI prompt):
input:
  idea_folder: "x-ipe-docs/ideas/025. CR-Refine Idea Action"
  extra_instructions: "Focus on the UX flow and keep the scope narrow"

# Skill output (after execution):
task_completion_output:
  task_output_links:
    - "x-ipe-docs/ideas/025. CR-Refine Idea Action/refined-idea/"
  workflow_action: "refine_idea"
  workflow_name: "hello"
```

---

## Part 2: Implementation Guide

> **Purpose:** Detailed guide for the skill update.

### Changes to SKILL.md

#### 1. Input Parameters Section

Add `extra_instructions` to input YAML:

```yaml
input:
  # ... existing params ...
  extra_instructions: "{optional text from Action Execution Modal, max 500 chars}"
```

#### 2. Brainstorming Step

Add instruction in the brainstorming/refinement step:

```
N. IF extra_instructions is provided and non-empty:
   - Incorporate extra_instructions as additional context/guidance for the refinement
   - Treat as user preference that supplements (not replaces) the idea content
```

#### 3. Output Configuration

Update output to specify `refined-idea/` subfolder:

```yaml
task_completion_output:
  task_output_links:
    - "{idea_folder}/refined-idea/"
  workflow_action: "refine_idea"
  workflow_name: "{from context}"
```

Add step before writing output:
```
N. Clear {idea_folder}/refined-idea/ folder if it exists (overwrite mode)
N+1. Write all refined output files to {idea_folder}/refined-idea/
```

#### 4. DoD Section

Add checkpoint:
```xml
<checkpoint required="true">
  <name>Workflow action status updated</name>
  <verification>Called update_workflow_action MCP with status "done" and deliverables list</verification>
</checkpoint>
```

### Implementation Steps

1. **Candidate:** Create/update candidate at `x-ipe-docs/skill-meta/x-ipe-task-based-ideation-v2/candidate/`
2. **Edit SKILL.md:** Modify input params, brainstorming step, output config, DoD
3. **Validate:** Run through skill-creator validation
4. **Merge:** Copy candidate → `.github/skills/x-ipe-task-based-ideation-v2/`

### Edge Cases & Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| `extra_instructions` empty/absent | Skill works identically to before (backward compatible) |
| `refined-idea/` doesn't exist yet | Create folder, write output |
| MCP call fails | Log warning, skill still completes in task board |
| `refined-idea/` has read-only files | Force remove before overwrite |

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 02-20-2026 | Initial Design | Skill-only update: add extra_instructions input, refined-idea/ output folder, MCP workflow status call in DoD. No application code changes. |
