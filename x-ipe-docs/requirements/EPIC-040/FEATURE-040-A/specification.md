# Feature Specification: Modal Generalization & Core Actions (MVP)

> Feature ID: FEATURE-040-A
> Epic ID: EPIC-040
> Version: v1.0
> Status: Refined
> Last Updated: 02-22-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-22-2026 | Initial specification |

## Linked Mockups

N/A — This feature extends an existing modal (FEATURE-038-A). No new mockup needed.

## Overview

Generalize the `ActionExecutionModal` class so it works for **any** CLI-based workflow action, not just "Refine Idea". The core change is replacing the hardcoded `_resolveIdeaFiles()` method with a generic `_resolveInputFiles(actionKey)` that reads an `input_source` declaration from the copilot-prompt config to determine which previous action's deliverables to offer as input files.

Additionally, add copilot-prompt.json entries for the three actions explicitly requested: **Design Mockup** (verify existing `generate-mockup`), **Requirement Gathering**, and **Feature Breakdown**.

This is the MVP that delivers the user's core request while maintaining full backward compatibility with the existing Refine Idea flow.

## User Stories

- **US-1:** As a developer, I want to click "Requirement Gathering" in the workflow and see a modal with auto-resolved idea/mockup files, so I can start the requirement gathering process without manually typing CLI commands.
- **US-2:** As a developer, I want to click "Feature Breakdown" and see a modal with the requirement document pre-selected, so I can break down features directly from the workflow UI.
- **US-3:** As a developer, I want to click "Design Mockup" and see a modal with the refined idea file pre-selected, so I can generate mockups from the workflow UI.
- **US-4:** As a developer, when I click any unconfigured action, I want to see a clear message that the config is not yet available, so I know what's missing.

## Acceptance Criteria

### Input File Resolution
- [ ] AC-1: When the modal opens for `design_mockup`, the file selector shows `.md` files from `refine_idea` action deliverables and `compose_idea` deliverables.
- [ ] AC-2: When the modal opens for `requirement_gathering`, the file selector shows `.md` files from `refine_idea` and/or `design_mockup` action deliverables.
- [ ] AC-3: When the modal opens for `feature_breakdown`, the file selector shows `.md` files from `requirement_gathering` action deliverables.
- [ ] AC-4: When no deliverables are found from source actions, the modal shows a text input for manual file path entry as fallback.
- [ ] AC-5: When multiple source actions have deliverables, all files are shown in the dropdown (merged).
- [ ] AC-6: The `<input-file>` placeholder in command templates is replaced with the selected file path.
- [ ] AC-7: The existing `<current-idea-file>` placeholder continues to work for backward compatibility (aliased to `<input-file>` behavior).

### Copilot-Prompt Configuration
- [ ] AC-8: `copilot-prompt.json` contains an entry for `requirement-gathering` with `id`, `prompt-details`, and `input_source` fields.
- [ ] AC-9: `copilot-prompt.json` contains an entry for `feature-breakdown` with `id`, `prompt-details`, and `input_source` fields.
- [ ] AC-10: The existing `generate-mockup` entry is verified/updated to include `input_source` field.
- [ ] AC-11: The existing `refine-idea` entry has `input_source` added (pointing to `compose_idea`) without breaking current behavior.
- [ ] AC-12: The `placeholder` section in copilot-prompt.json includes `input-file` alongside the existing `current-idea-file`.

### Modal UX Consistency
- [ ] AC-13: All three core actions show instruction text from copilot-prompt.json in the modal.
- [ ] AC-14: All three core actions have a 500-character extra-instructions textarea.
- [ ] AC-15: The "Execute with Copilot" button constructs the command with `--workflow-mode@{workflowName}` prefix.
- [ ] AC-16: The `--extra-instructions` flag is appended when extra instructions are provided.

### Error Handling & Edge Cases
- [ ] AC-17: When no copilot-prompt config exists for an action, the modal shows "Configuration not yet available" and the execute button is disabled.
- [ ] AC-18: The existing "Refine Idea" flow works identically (no regression).
- [ ] AC-19: If the workflow API returns an error during deliverable resolution, the modal gracefully falls back to manual input.

## Functional Requirements

### FR-1: Generic Input File Resolution

**Input:** `actionKey` (e.g., `requirement_gathering`), `workflowName`
**Process:**
1. Load copilot-prompt config for the action (by mapping `actionKey` → config `id`)
2. Read `input_source` array from the config entry (e.g., `["refine_idea", "compose_idea"]`)
3. For each source action in `input_source`:
   a. Fetch workflow state via `GET /api/workflow/{workflowName}`
   b. Extract deliverables from the source action
   c. Filter for `.md` files (or configured extensions)
   d. If deliverable is a folder path, scan using `/api/workflow/{name}/deliverables/tree`
4. Merge all resolved files into a single list (deduplicated)
5. If no files resolved, enable manual path input fallback
**Output:** Array of file paths for the dropdown selector

### FR-2: Action Key to Config ID Mapping

**Input:** `actionKey` (underscore format, e.g., `requirement_gathering`)
**Process:**
1. Convert underscore to hyphen: `requirement_gathering` → `requirement-gathering`
2. Look up in copilot-prompt.json sections (ideation.prompts, workflow.prompts, etc.)
3. Return matching config entry or null
**Output:** Config object or null

### FR-3: copilot-prompt.json Schema Extension

Add a `workflow` section to copilot-prompt.json alongside the existing `ideation` and `evaluation` sections:

```json
{
  "workflow": {
    "prompts": [
      {
        "id": "requirement-gathering",
        "icon": "bi-clipboard-data",
        "input_source": ["refine_idea", "design_mockup"],
        "prompt-details": [
          {
            "language": "en",
            "label": "Requirement Gathering",
            "command": "gather requirements from <input-file> with requirement gathering skill"
          }
        ]
      }
    ]
  }
}
```

Also add `input_source` to existing ideation entries:
- `refine-idea`: `input_source: ["compose_idea"]`
- `generate-mockup`: `input_source: ["refine_idea", "compose_idea"]`

### FR-4: Placeholder System Extension

**Current:** Only `<current-idea-file>` placeholder exists.
**New:** Add `<input-file>` as a generic placeholder.
**Backward compat:** When the modal encounters `<current-idea-file>`, treat it identically to `<input-file>` (both are replaced with the selected file path).

### FR-5: Fallback to Manual Input

When `_resolveInputFiles()` returns an empty array:
1. Hide the dropdown selector
2. Show a text input field with placeholder "Enter file path..."
3. The entered path replaces the `<input-file>` placeholder in the command

### FR-6: Missing Config Handling

When no copilot-prompt config is found for an `actionKey`:
1. Display message: "Configuration not yet available for this action."
2. Disable the "Execute with Copilot" button
3. Show the action label and icon in the modal header (from ACTION_MAP)

## Non-Functional Requirements

- **NFR-1: Performance** — Input file resolution must complete within 200ms (local API calls).
- **NFR-2: Backward Compatibility** — Existing Refine Idea flow must work identically. All existing copilot-prompt.json entries must continue to function.
- **NFR-3: Graceful Degradation** — API errors during resolution must fall back to manual input without crashing.

## UI/UX Requirements

### Modal Layout (unchanged from FEATURE-038-A)

The modal retains the same layout. The only visible changes:
1. **File selector label** changes from "Idea File" to "Target Input" (generic)
2. **Dropdown** may show files from multiple source actions (merged list)
3. **Fallback** text input appears when no files are auto-resolved

### User Flow

```
1. User clicks action button (e.g., "Requirement Gathering") in workflow stage ribbon
2. WorkflowStage._dispatchCliAction() creates ActionExecutionModal
3. Modal loads copilot-prompt config for the action
   → IF config found: show instructions + file selector + extra instructions
   → IF config NOT found: show "Configuration not yet available" message
4. Modal calls _resolveInputFiles(actionKey) to populate file selector
   → IF files found: show dropdown with resolved files
   → IF no files: show manual path text input
5. User optionally adds extra instructions
6. User clicks "Execute with Copilot"
7. Command dispatched to terminal with --workflow-mode prefix
```

## Dependencies

### Internal Dependencies
- **FEATURE-038-A** (Action Execution Modal) — Base modal implementation being extended
- **FEATURE-038-B** (Session Idle Detection) — Terminal session management (no changes needed)

### External Dependencies
- `/api/workflow/{name}` endpoint — Already exists, returns action deliverables
- `/api/workflow/{name}/deliverables/tree` — Already exists, scans folders
- `/api/config/copilot-prompt` — Already exists, serves config

No new backend endpoints required for this feature.

## Business Rules

- **BR-1:** The `input_source` field is optional in copilot-prompt entries. If absent, the modal falls back to existing `_resolveIdeaFiles()` behavior for backward compatibility.
- **BR-2:** The `input_source` array is ordered by priority — first source is preferred, subsequent sources are fallbacks.
- **BR-3:** File extension filter defaults to `.md` unless overridden by a `file_filter` field in the config.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Source action has no deliverables yet | Show empty dropdown + manual path fallback |
| Source action completed but files deleted | Show empty dropdown + manual path fallback |
| Multiple source actions with overlapping files | Deduplicate by full path |
| copilot-prompt.json doesn't exist | Show "Configuration not available" for all actions |
| Workflow API returns 500 | Log error, show manual path fallback |
| `<current-idea-file>` in legacy command template | Treat as `<input-file>` (backward compat alias) |
| Action has `deferred: true` in ACTION_MAP | Modal still opens if config exists; deferred is just a visual hint |

## Out of Scope

- **Per-feature resolution** — Implement stage actions with feature lane context (FEATURE-040-B)
- **`deliverable_folder` field** — Workflow template config changes (FEATURE-040-B)
- **Skill workflow-mode updates** — SKILL.md file changes (FEATURE-040-C)
- **Prompt configs for implement/validation stage** — Beyond the 3 core actions (FEATURE-040-B)
- **Backend API changes** — No new endpoints; this feature uses existing APIs only

## Technical Considerations

- The `_resolveIdeaFiles()` method (lines 79-110) should be refactored into `_resolveInputFiles(actionKey)` with the original logic preserved as a special case when `input_source` is not configured.
- The copilot-prompt config lookup needs to search across all sections (`ideation.prompts`, `workflow.prompts`, `evaluation`) — consider a unified lookup function.
- The `<current-idea-file>` → `<input-file>` alias should be handled at the placeholder replacement level, not by modifying existing config entries.
- The `src/x_ipe/resources/config/copilot-prompt.json` and `x-ipe-docs/config/copilot-prompt.json` appear to be two copies — ensure both are updated or determine which is authoritative.
- Existing unit tests in `action-execution-modal.test.js` must be updated to cover the new `_resolveInputFiles()` code path.

## Open Questions

None — all questions resolved during ideation and requirement gathering.
