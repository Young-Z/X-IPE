# Feature Specification: Action Context Modal UI & Persistence

> Feature ID: FEATURE-041-F
> Epic ID: EPIC-041
> CR: CR-002
> Version: v1.0
> Status: Refined
> Last Updated: 02-26-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-26-2026 | Initial specification from CR-002 Feature Breakdown |

## Linked Mockups

N/A — Extends existing Action Execution Modal pattern. The existing modal mockups from EPIC-041 apply directionally (the "Input Files" section is renamed to "Action Context" with template-driven dropdowns).

## Overview

FEATURE-041-F replaces the ad-hoc `_resolveInputFiles()` logic in the Action Execution Modal with template-driven context dropdowns. The modal reads `action_context` from `workflow-template.json` (established by FEATURE-041-E) and renders one labeled dropdown per context reference. Each dropdown is populated with the specific `$output` file + all files within the `$output-folder` path from prior action deliverables. Every dropdown includes an "auto-detect" option. User selections are persisted in the workflow instance `context` field, and reopening an action pre-populates dropdowns from saved context.

**Who:** Developers using the workflow UI to execute actions via Copilot CLI.

**Why:** The current `_resolveInputFiles()` uses hardcoded per-action logic and only lists `.md` files. Template-driven context makes the UI data-driven, supports all file types, and enables reopen with previous selections.

## User Stories

- **US-1:** As a developer, I want the Action Context section in the modal to show labeled dropdowns based on the action's `action_context` template definition, so I know exactly what context each action needs.
- **US-2:** As a developer, I want each dropdown to list the specific output file + all files in the candidate folder from prior actions, so I can pick the exact file I want.
- **US-3:** As a developer, I want every dropdown to include "auto-detect", so the AI agent can discover context on its own when I don't want to specify.
- **US-4:** As a developer, I want required context refs to enforce selection (or auto-detect), and optional refs to allow N/A, so I don't miss critical inputs.
- **US-5:** As a developer, when I reopen a completed action, I want the dropdowns pre-populated with my previous selections from the instance, so I don't have to re-select everything.
- **US-6:** As a developer, I want feature-level actions to also support reopen with context restoration, so per-feature workflows are consistent with shared actions.
- **US-7:** As a developer, if `action_context` is not defined for an action, I want the modal to fall back to legacy `input_source` from `copilot-prompt.json`, so existing actions still work.

## Acceptance Criteria

- [ ] **AC-1:** "Input Files" section is renamed to "Action Context" in the modal.
- [ ] **AC-2:** One labeled dropdown rendered per `action_context` entry. Label = context ref name as human-readable subtitle.
- [ ] **AC-3:** Dropdown options include: the specific `$output` file from the producing action + all files within the `$output-folder` path. All file types shown (not just `.md`).
- [ ] **AC-4:** Every dropdown includes "auto-detect" as the first option.
- [ ] **AC-5:** Required context refs (`required: true`) must have a selection or auto-detect before execution. Optional refs allow N/A.
- [ ] **AC-6:** User selections saved to instance `context` field before launching CLI command.
- [ ] **AC-7:** Reopening a shared-level action pre-populates dropdowns from instance `context`.
- [ ] **AC-8:** Reopening a feature-level action pre-populates dropdowns from `features[id].{stage}.{action}.context`.
- [ ] **AC-9:** When `action_context` is absent in template → legacy `input_source` from `copilot-prompt.json` used as fallback.
- [ ] **AC-10:** Reopen state: status remains `done` until re-execution starts (→ `in_progress`). Old deliverables preserved. No downstream cascade.
- [ ] **AC-11:** Dropdowns handle large folders (100+ files) without UI lag.

## Functional Requirements

### FR-1: Modal Section Rename

- **FR-1.1:** Rename "Input Files" section label to "Action Context" in the Action Execution Modal.
- **FR-1.2:** If `action_context` is absent in template for the current action → show legacy `input_source` UI with old label "Input Files".

### FR-2: Template-Driven Dropdown Rendering

- **FR-2.1:** Read `action_context` from `workflow-template.json` for the action being executed.
- **FR-2.2:** For each context entry, render a labeled dropdown with the ref name as subtitle (e.g., "raw-idea", "uiux-reference").
- **FR-2.3:** `required: true` entries get a red asterisk or "(required)" label. `required: false` entries show "(optional)".

### FR-3: Dropdown Population

- **FR-3.1:** When `candidates` is specified in the context entry:
  1. Call the candidate resolution algorithm (FEATURE-041-E FR-7) to find the producing action
  2. Get the `$output` file path from the instance
  3. List all files within the `$output-folder` path from the instance
  4. Combine: `$output` file at top, then folder contents sorted alphabetically
- **FR-3.2:** When `candidates` is NOT specified:
  1. Search prior action deliverables for a tag matching the ref name
  2. If found, show that file; otherwise show empty dropdown with manual path input
- **FR-3.3:** Add "auto-detect" as the first option in every dropdown.
- **FR-3.4:** For `required: false` entries, add "N/A" as an option after "auto-detect".
- **FR-3.5:** All file types shown in dropdown (remove `.md`-only filter from current `_resolveInputFiles()`).

### FR-4: Context Persistence

- **FR-4.1:** When user clicks "Execute", save the dropdown selections to the instance `context` field for the action being executed.
- **FR-4.2:** For shared actions: `stages.{stage}.actions.{action}.context = { refName: selectedPath | "N/A" | "auto-detect" }`.
- **FR-4.3:** For feature-level actions: `features[id].{stage}.{action}.context = { ... }`.
- **FR-4.4:** `"auto-detect"` persists in context until explicitly changed.

### FR-5: Reopen Pre-Population

- **FR-5.1:** When opening a modal for an action with `status: "done"`, check the instance `context` field.
- **FR-5.2:** For each dropdown, set the selected value to the stored context value.
- **FR-5.3:** If stored value is a file path, select it in dropdown. If "auto-detect", select "auto-detect". If "N/A", select "N/A".
- **FR-5.4:** If stored path no longer exists in dropdown options (file deleted), show it as selected but mark "(missing)".

### FR-6: Reopen State Machine

- **FR-6.1:** Reopening a `done` action opens the modal with pre-populated context; status stays `done`.
- **FR-6.2:** When user clicks "Execute" on a reopened action, status transitions `done → in_progress`.
- **FR-6.3:** Old deliverables preserved until new execution completes and overwrites.
- **FR-6.4:** No automatic downstream cascade — downstream actions keep their existing context/deliverables.

### FR-7: CLI Command Context Injection

- **FR-7.1:** When constructing the CLI command, include context selections as parameters.
- **FR-7.2:** The context is passed to the skill via the workflow instance — the CLI command itself doesn't change, but the instance is updated before the CLI command runs.

### FR-8: Fallback to Legacy input_source

- **FR-8.1:** If the action has no `action_context` in template, check `copilot-prompt.json` for `input_source`.
- **FR-8.2:** If `input_source` found, use existing `_resolveInputFiles()` logic with "Input Files" label.
- **FR-8.3:** If neither `action_context` nor `input_source` found, show no context section.

## Non-Functional Requirements

- **NFR-1:** Dropdown file listing for folders with 100+ files must use lazy loading or virtualized list.
- **NFR-2:** Modal open time must not increase by more than 200ms with new context rendering.
- **NFR-3:** Context persistence (write to instance) must complete before CLI command launch.

## UI/UX Requirements

### Action Context Section Layout

```
┌─────────────────────────────────────────┐
│  Action Context                          │
│                                          │
│  raw-idea * (required)                   │
│  ┌─────────────────────────────────┐     │
│  │ ▾ auto-detect                   │     │
│  │   x-ipe-docs/.../new idea.md    │     │
│  │   x-ipe-docs/.../notes.md       │     │
│  │   x-ipe-docs/.../reference.pdf  │     │
│  └─────────────────────────────────┘     │
│                                          │
│  uiux-reference (optional)               │
│  ┌─────────────────────────────────┐     │
│  │ ▾ auto-detect                   │     │
│  │   N/A                           │     │
│  │   x-ipe-docs/.../uiux-ref.md   │     │
│  └─────────────────────────────────┘     │
│                                          │
└─────────────────────────────────────────┘
```

- Dropdowns use the same styling as existing modal form elements
- "auto-detect" is always the first option (default selection for new actions)
- Required fields show asterisk and prevent execution without selection
- Optional fields show "(optional)" and include N/A

## Dependencies

### Internal Dependencies

- **FEATURE-041-E** (MUST be complete first): Provides the `action_context` schema in template, keyed deliverables in instance, and the candidate resolution algorithm.
- **FEATURE-041-A** (Testing Complete): Provides the per-feature modal infrastructure and `_resolveInputFiles()` that this feature replaces.

### External Dependencies

None.

## Business Rules

- **BR-1:** "auto-detect" is the default selection for all dropdowns on first execution.
- **BR-2:** Required context MUST be resolved before execution. Modal disables "Execute" button if required fields are empty.
- **BR-3:** Reopen never cascades downstream — each action is independent.
- **BR-4:** Legacy `input_source` fallback is temporary — will be removed after full migration.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Action has no `action_context` and no `input_source` | No context section shown; action executes with no context |
| `$output-folder` is empty (no files) | Dropdown shows only "auto-detect" (+ "N/A" if optional) |
| `$output-folder` has 500+ files | Lazy-load with search/filter input |
| Stored context path points to deleted file | Show as selected with "(missing)" label; allow reselection |
| Feature-level action opened but feature has no prior deliverables | Fall back to shared-stage deliverables |
| Action being executed for the first time (no context in instance) | Default all dropdowns to "auto-detect" |
| User selects "auto-detect" for a required field | Valid — "auto-detect" satisfies required constraint |
| Multiple prior actions produce same-named folder | Later-stage/later-action takes precedence (per FR-7 algorithm) |

### Constraints

- **C-1:** Must extend existing `ActionExecutionModal` class — not rewrite.
- **C-2:** Must use existing CSS framework and component patterns.
- **C-3:** `_resolveInputFiles()` is replaced, not kept alongside new logic.

## Out of Scope

- Template/instance schema definition (→ FEATURE-041-E)
- Skill `extra_context_reference` input (→ FEATURE-041-G)
- Context display in workflow stage view action panels (context only in modal)
- File preview/content inspection in dropdown

## Technical Considerations

- **Affected frontend files:**
  - `src/x_ipe/static/js/features/action-execution-modal.js` — replace `_resolveInputFiles()` with template-driven context resolution, add dropdown rendering, add context persistence
  - `src/x_ipe/static/js/features/workflow-stage.js` — feature-level action reopen support
- **Affected backend files:**
  - Possibly `src/x_ipe/routes/workflow_routes.py` — API to list files in a folder path (for `$output-folder` contents)
- **Affected tests:**
  - `tests/frontend-js/action-execution-modal-040a.test.js` — update existing tests, add context dropdown tests
- **API needed:** endpoint to list files within a folder path given the `$output-folder` resolved path; or client-side directory listing via existing file API

## Open Questions

None — all questions resolved during IDEA-029 brainstorming.
