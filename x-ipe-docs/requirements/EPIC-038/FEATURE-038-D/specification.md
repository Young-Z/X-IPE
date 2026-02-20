# Feature Specification: Refinement Skill Integration

> Feature ID: FEATURE-038-D
> Version: v1.0
> Status: Refined
> Last Updated: 02-20-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-20-2026 | Initial specification — update ideation skill for modal integration |

## Linked Mockups

None — this feature is a skill update with no direct UI.

## Overview

This feature updates the existing `x-ipe-task-based-ideation-v2` skill to integrate with the Action Execution Modal (FEATURE-038-A) and Session Idle Detection (FEATURE-038-B). Specifically:

1. **Accept `extra_instructions` parameter** — the skill's input parameters section gains an optional `extra_instructions` field that the agent reads from the CLI prompt
2. **Output to `refined-idea/` subfolder** — instead of `idea-summary-vN.md` at the idea root, output files go to `{idea_folder}/refined-idea/` using overwrite mode (clear and replace on each run)
3. **Call `update_workflow_action` MCP** — at the skill's DoD, invoke MCP to report completion status back to the workflow manager, enabling the UI status refresh chain

This is a **standalone skill update** — modifies `.github/skills/` files only, no application code changes.

**Target Users:**
- AI Agents executing the ideation skill via the modal flow
- Workflow system consuming action completion status

## User Stories

- **US-038-D.1:** As a workflow user who typed extra instructions in the modal, I want the agent to use those instructions during ideation, so that the refinement reflects my specific guidance.
- **US-038-D.2:** As a workflow user, I want ideation output in a dedicated subfolder with overwrite semantics, so that each refinement run produces clean output without version file proliferation.
- **US-038-D.3:** As the workflow system, I want the ideation skill to report completion via MCP, so that the UI can automatically update the action status to "done".

## Acceptance Criteria

- [ ] AC-038-D.1: Skill input section declares `extra_instructions: "{optional text from modal}"` parameter
- [ ] AC-038-D.2: When `extra_instructions` is provided, the agent incorporates it into the brainstorming/refinement process
- [ ] AC-038-D.3: When `extra_instructions` is empty or absent, the skill executes normally (backward compatible)
- [ ] AC-038-D.4: Skill output is written to `{idea_folder}/refined-idea/` subfolder
- [ ] AC-038-D.5: Each execution overwrites previous `refined-idea/` contents (clear folder, then write)
- [ ] AC-038-D.6: Skill's DoD section includes calling `update_workflow_action` MCP with `status: done` and `deliverables: ["{idea_folder}/refined-idea/"]`
- [ ] AC-038-D.7: `idea-summary.md` (or `idea-summary-v1.md`) at idea root is still updated in-place per current skill behavior — `refined-idea/` is additional output
- [ ] AC-038-D.8: Skill update follows the candidate workflow (edit in `x-ipe-docs/skill-meta/` → validate → merge)

## Functional Requirements

**FR-038-D.1: Extra Instructions Parameter**
- Input: Skill SKILL.md input parameters section
- Process: Add `extra_instructions` to input YAML with description noting it comes from the Action Execution Modal
- Output: Updated input section with optional `extra_instructions` field

**FR-038-D.2: Extra Instructions Usage**
- Input: `extra_instructions` text (may be empty)
- Process: In the brainstorming step, prepend extra instructions as additional context/guidance. If empty, skip.
- Output: Agent considers extra instructions during refinement

**FR-038-D.3: Output Folder Configuration**
- Input: Skill output section
- Process: Define `refined-idea/` as output folder. Add step to clear folder before writing.
- Output: Skill declares `{idea_folder}/refined-idea/` as deliverable folder

**FR-038-D.4: Overwrite Mode**
- Input: Prior contents of `refined-idea/` folder (if any)
- Process: Before writing new output, remove all files in `refined-idea/`. Then write fresh output.
- Output: Clean folder with only current run's output

**FR-038-D.5: MCP Workflow Status Update**
- Input: Completed skill execution
- Process: In DoD section, add checkpoint: call `update_workflow_action` MCP tool with `workflow_name`, `action: refine_idea`, `status: done`, `deliverables: ["{idea_folder}/refined-idea/"]`
- Output: Workflow JSON updated, UI receives status change

## Non-Functional Requirements

- **NFR-038-D.1:** Skill SKILL.md must stay under 500 lines after changes
- **NFR-038-D.2:** Backward compatibility — skill must work identically when `extra_instructions` is not provided

## UI/UX Requirements

None — skill update only.

## Dependencies

### Internal

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-038-A | Runtime | Action Execution Modal provides `extra_instructions` via CLI prompt |
| FEATURE-038-B | Runtime | Session Idle Detection provides session for agent execution |
| `update_workflow_action` MCP | Integration | Reports completion status to workflow manager |
| `x-ipe-meta-skill-creator` | Process | Candidate workflow for skill updates |

### External

None.

## Business Rules

- **BR-038-D.1:** `refined-idea/` coexists with `idea-summary.md` — both are maintained.
- **BR-038-D.2:** Overwrite mode means NO version history within `refined-idea/` — each run produces a fresh set of files.
- **BR-038-D.3:** MCP call is in the DoD, not a step — it happens after all skill steps complete.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| First run (no `refined-idea/` folder exists) | Create folder, write output |
| `extra_instructions` contains special characters | Agent handles as plain text context |
| `extra_instructions` is exactly 500 chars (max) | Accepted as-is, no truncation by skill |
| MCP call fails (workflow manager unavailable) | Skill still marks as complete in task board; log warning |
| `refined-idea/` folder has read-only files | Overwrite should handle gracefully (force remove) |

## Out of Scope

- **New skill steps** — only modifying existing input/output/DoD sections
- **Changing the brainstorming algorithm** — only adding extra context input
- **UI changes** — this is purely a skill file update

## Technical Considerations

- Modify `.github/skills/x-ipe-task-based-ideation-v2/SKILL.md`
- Changes touch: Input Parameters section, Output Result section, DoD checkpoints
- Must go through `x-ipe-meta-skill-creator` candidate workflow
- The `update_workflow_action` MCP tool signature: `update_workflow_action(workflow_name, action, status, deliverables=[])`

## Open Questions

None.
