# Requirement Summary

## EPIC-040: CR-Generalize Action Execution Modal for All Workflow Actions

### Project Overview

Generalize the Action Execution Modal — currently only wired for "Refine Idea" — so that **every CLI-based workflow action** gets the same first-class modal UX: auto-resolved input files from the deliverable chain, instruction display, extra-instructions textarea, terminal dispatch, status polling, and deliverable rendering.

This is a **Change Request** extending EPIC-038 (CR-Refine Idea Action), specifically FEATURE-038-A (Action Execution Modal).

### User Request

> now let's work on design mockup, requirement gathering and feature breakdown actions in the work flow as an CR to the workflow requirement. they should be just like Refine idea action, when clicks on it, should show the mockup, with target inputs [...] also show the instruction and extract instructions textbox and text area as well. and the logic to execute, update action status and show the delivery should also be the same, try to reuse as much as you can.
>
> — Feedback-20260222-132751

### Clarifications

| Question | Answer |
|----------|--------|
| Scope: cover only 3 actions or all CLI actions? | **All CLI actions** — future-proof (12+ actions across 5 stages) |
| Input file resolution strategy? | **Auto-resolve from previous action deliverables** — follows natural workflow flow |
| Extra instructions for all actions? | **Yes** — consistent UX, all actions get instruction + extra instructions textarea |
| Execution pattern for all actions? | **Terminal dispatch via Copilot CLI** — same pattern as Refine Idea for all |
| Add copilot-prompt.json entries for all? | **Yes** — add placeholder prompts for all actions, even untested ones |
| Include skill updates in this CR? | **Yes** — one big CR covering frontend, config, backend, and skill updates |
| Per-feature selector for implement stage? | **Auto-resolved from workflow context** — add `deliverable_folder` field to workflow action/template config so next action auto-detects input source |
| Backend changes needed? | **Minimal** — copilot-prompt.json entries + ensure deliverable_folder field propagates through workflow API |

### High-Level Requirements

#### HLR-1: Generalize Input File Resolution
The `ActionExecutionModal` MUST replace the hardcoded `_resolveIdeaFiles()` with a generic `_resolveInputFiles(actionKey)` method that auto-resolves input files from the previous action's deliverables in the current workflow.

**Functional Requirements:**

- **FR-040.1:** The modal MUST read the action's `deliverable_folder` or `input_source` from the copilot-prompt.json config to determine which previous action(s) provide input files.
- **FR-040.2:** The modal MUST fetch deliverables from the specified source action(s) using the existing `/api/workflow/{name}` endpoint.
- **FR-040.3:** When multiple source actions are specified, deliverables MUST be merged and grouped by source action in the dropdown selector.
- **FR-040.4:** When no deliverables are found from source actions, the modal MUST show a manual file path input as fallback.
- **FR-040.5:** File filtering MUST default to `.md` files but be configurable per action via the copilot-prompt config.
- **FR-040.6:** The `<current-idea-file>` placeholder in command templates MUST be replaced with a generic `<input-file>` placeholder that works for all actions.
- **FR-040.7:** For per-feature actions (implement stage), the modal MUST auto-resolve the feature context from the workflow's current feature lane or `deliverable_folder` field.

#### HLR-2: Complete Copilot-Prompt Configuration
Every CLI-based workflow action MUST have a corresponding entry in `copilot-prompt.json`.

**Functional Requirements:**

- **FR-040.8:** Add copilot-prompt entries for ALL missing CLI actions: `requirement-gathering`, `feature-breakdown`, `feature-refinement`, `technical-design`, `test-generation`, `implementation`, `acceptance-testing`, `change-request`.
- **FR-040.9:** Each entry MUST include: `id`, `prompt-details` (with `language`, `label`, `command`), and `input_source` (array of source action keys).
- **FR-040.10:** Each entry SHOULD include `deliverable_folder` to specify where the action's deliverables reside for the next action's resolution.
- **FR-040.11:** Existing entries (`refine-idea`, `generate-mockup`, etc.) MUST remain backward-compatible.
- **FR-040.12:** The `quality-evaluation` action MUST have a placeholder entry marked as deferred.

#### HLR-3: Consistent Modal UX for All Actions
Every CLI action MUST present the same modal layout: target input selector, instruction display, extra-instructions textarea, and execute button.

**Functional Requirements:**

- **FR-040.13:** Clicking any CLI action in the workflow stage ribbon MUST open the ActionExecutionModal with the correct context for that action.
- **FR-040.14:** The modal MUST display the action's instruction text from copilot-prompt.json.
- **FR-040.15:** The modal MUST include a 500-character extra-instructions textarea for all actions.
- **FR-040.16:** The "Execute with Copilot" button MUST construct the command with `--workflow-mode@{workflowName}` prefix and `--extra-instructions` flag.
- **FR-040.17:** If no copilot-prompt config exists for an action, the modal MUST show "Configuration not yet available" and disable the execute button.
- **FR-040.18:** Action execution MUST use the existing terminal dispatch pattern (find idle session → send command).
- **FR-040.19:** Action status polling and deliverable rendering MUST reuse the existing FEATURE-038-A infrastructure.

#### HLR-4: Workflow Template & Config Updates
The workflow template and action configurations MUST support a `deliverable_folder` field for auto-resolution.

**Functional Requirements:**

- **FR-040.20:** The workflow template (`workflow-template.json` or equivalent) MUST include a `deliverable_folder` field per action, indicating the folder where deliverables are stored.
- **FR-040.21:** The workflow JSON (`workflow-{name}.json`) MUST propagate `deliverable_folder` values through the `/api/workflow/{name}` API response.
- **FR-040.22:** The `deliverable_folder` field MUST support relative paths from the workflow's idea/epic root folder.
- **FR-040.23:** For per-feature actions, `deliverable_folder` MUST support `{feature_id}` placeholder that resolves to the active feature folder path.

#### HLR-5: Skill Workflow-Mode Updates
All task-based skills referenced in ACTION_MAP MUST support workflow-mode execution.

**Functional Requirements:**

- **FR-040.24:** Each skill MUST accept `execution_mode` and `workflow.name` input parameters.
- **FR-040.25:** Each skill MUST call `update_workflow_action` MCP tool on completion when `execution_mode == "workflow-mode"`.
- **FR-040.26:** Each skill MUST declare `workflow_action` in its Output Result YAML section.
- **FR-040.27:** Skills not yet workflow-mode ready MUST be identified and updated:
  - `x-ipe-task-based-idea-mockup` (partial — add `workflow_action` output)
  - `x-ipe-task-based-requirement-gathering` (add execution_mode + workflow_action)
  - `x-ipe-task-based-feature-breakdown` (add execution_mode + workflow_action)
  - `x-ipe-task-based-feature-refinement` (add execution_mode + workflow_action)
  - `x-ipe-task-based-technical-design` (add execution_mode + workflow_action)
  - `x-ipe-task-based-code-implementation` (add execution_mode + workflow_action)
  - `x-ipe-task-based-feature-acceptance-test` (add execution_mode + workflow_action)
  - `x-ipe-task-based-change-request` (add execution_mode + workflow_action)

### Non-Functional Requirements

- **NFR-040.1:** Deliverable chain resolution MUST complete within 200ms (1-3 local API calls at ~50ms each).
- **NFR-040.2:** Existing Refine Idea flow MUST continue to work without regression.
- **NFR-040.3:** Modal MUST gracefully degrade when configs are missing (show message, disable button).
- **NFR-040.4:** All changes MUST be backward-compatible with the existing copilot-prompt.json schema.

### Acceptance Criteria

- [ ] AC-040.1: Clicking "Design Mockup" action opens modal with auto-resolved idea files from `refine_idea` deliverables
- [ ] AC-040.2: Clicking "Requirement Gathering" action opens modal with auto-resolved files from `refine_idea`/`design_mockup` deliverables
- [ ] AC-040.3: Clicking "Feature Breakdown" action opens modal with auto-resolved requirement docs from `requirement_gathering` deliverables
- [ ] AC-040.4: Clicking "Feature Refinement" action opens modal with auto-resolved feature specs (per-feature context)
- [ ] AC-040.5: Clicking "Technical Design" action opens modal with auto-resolved feature spec from `feature_refinement` deliverables
- [ ] AC-040.6: Clicking "Implementation" action opens modal with auto-resolved technical design from `technical_design` deliverables
- [ ] AC-040.7: Clicking "Acceptance Testing" action opens modal with auto-resolved implementation deliverables
- [ ] AC-040.8: Clicking "Change Request" action opens modal with manual file path input (no auto-resolution)
- [ ] AC-040.9: All actions show instruction text from copilot-prompt.json
- [ ] AC-040.10: All actions have extra-instructions textarea (500 char limit)
- [ ] AC-040.11: All actions dispatch commands with `--workflow-mode@{name}` prefix
- [ ] AC-040.12: Existing "Refine Idea" flow works without regression
- [ ] AC-040.13: Missing copilot-prompt config shows "Configuration not yet available" message
- [ ] AC-040.14: copilot-prompt.json entries exist for all CLI actions
- [ ] AC-040.15: `deliverable_folder` field present in workflow template and propagated via API
- [ ] AC-040.16: All 8 skills updated with `execution_mode` input + `workflow_action` output
- [ ] AC-040.17: Per-feature actions (feature_refinement, technical_design, implementation) resolve feature context from workflow

### Constraints

- **C-1:** Must reuse existing `ActionExecutionModal` class — no parallel modal implementation
- **C-2:** Must maintain backward compatibility with existing copilot-prompt.json entries
- **C-3:** Quality Evaluation action is deferred — placeholder config only
- **C-4:** Skill updates are documentation/config changes (SKILL.md files), not code changes
- **C-5:** Must coordinate with EPIC-039 (Folder Browser Modal) for deliverable folder interactions

### Related Features (CR Impact)

| Feature | Overlap Type | Decision |
|---------|-------------|----------|
| FEATURE-038-A (Action Execution Modal) | Direct extension — modal generalization | CR on EPIC-038 |
| FEATURE-038-D (Refinement Skill Integration) | Pattern reference for skill updates | Reference only |
| EPIC-039 (Folder Browser Modal) | Deliverable folder display | Coordinate — no conflict |

### Open Questions

- None (all resolved during ideation and clarification)

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| N/A (extends existing modal pattern — no new visual mockup needed) | - |

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|--------------------|
| FEATURE-040-A | EPIC-040 | Modal Generalization & Core Actions (MVP) | v1.0 | Replace `_resolveIdeaFiles()` with generic `_resolveInputFiles()`, add copilot-prompt configs for 3 primary actions, consistent modal UX | None |
| FEATURE-040-B | EPIC-040 | Workflow Config & Remaining Actions | v1.0 | Add `deliverable_folder` to workflow template/config, add remaining prompt configs, per-feature resolution for implement stage | FEATURE-040-A |
| FEATURE-040-C | EPIC-040 | Skill Workflow-Mode Compliance | v1.0 | Update 8 task-based skills with `execution_mode` input + `workflow_action` output for workflow-mode execution | None |

---

## Feature Details

### FEATURE-040-A: Modal Generalization & Core Actions (MVP)

**Summary:** The minimum viable change to make the Action Execution Modal work for design_mockup, requirement_gathering, and feature_breakdown — the 3 actions explicitly requested in the feedback. This is the core frontend refactoring.

**Scope:**
- Refactor `ActionExecutionModal._resolveIdeaFiles()` → `_resolveInputFiles(actionKey)` using `input_source` from copilot-prompt config
- Add copilot-prompt.json entries for: `generate-mockup` (verify existing), `requirement-gathering`, `feature-breakdown` with `input_source` arrays
- Generic `<input-file>` placeholder support in command templates
- Multi-source grouped dropdown (deliverables from multiple source actions)
- Fallback to manual path input when no deliverables found
- "Configuration not yet available" message for unconfigured actions
- Backward compatibility with existing `refine-idea` flow

**Covered FRs:** FR-040.1, FR-040.2, FR-040.3, FR-040.4, FR-040.5, FR-040.6, FR-040.8 (3 core), FR-040.9, FR-040.11, FR-040.13, FR-040.14, FR-040.15, FR-040.16, FR-040.17, FR-040.18, FR-040.19

**Acceptance Criteria:**
- [ ] AC-040.1: Clicking "Design Mockup" opens modal with auto-resolved idea files from `refine_idea` deliverables
- [ ] AC-040.2: Clicking "Requirement Gathering" opens modal with files from `refine_idea`/`design_mockup` deliverables
- [ ] AC-040.3: Clicking "Feature Breakdown" opens modal with requirement docs from `requirement_gathering` deliverables
- [ ] AC-040.9: All actions show instruction text from copilot-prompt.json
- [ ] AC-040.10: All actions have extra-instructions textarea (500 char limit)
- [ ] AC-040.11: All actions dispatch commands with `--workflow-mode@{name}` prefix
- [ ] AC-040.12: Existing "Refine Idea" flow works without regression
- [ ] AC-040.13: Missing copilot-prompt config shows "Configuration not yet available" message
- [ ] AC-040.14: copilot-prompt.json entries exist for 3 core actions (requirement-gathering, feature-breakdown + verify generate-mockup)

**Dependencies:** None (first feature, MVP)

**Technical Considerations:**
- `_resolveInputFiles()` reads `input_source` from copilot-prompt config to determine which source action(s) to fetch deliverables from
- The existing `/api/workflow/{name}` endpoint already returns action deliverables — no backend change needed for this feature
- `<current-idea-file>` placeholder should be aliased to `<input-file>` for backward compatibility
- copilot-prompt.json `input_source` is a new field — existing entries without it should fall back to current behavior

---

### FEATURE-040-B: Workflow Config & Remaining Actions

**Summary:** Extend the modal to support all remaining workflow actions (implement + validation + feedback stages) and add the `deliverable_folder` field to workflow template/config for auto-resolution.

**Scope:**
- Add `deliverable_folder` field to workflow template (workflow-template.json or equivalent config)
- Propagate `deliverable_folder` through `/api/workflow/{name}` API response
- Add copilot-prompt.json entries for: `feature-refinement`, `technical-design`, `test-generation`, `implementation`, `acceptance-testing`, `change-request`, `quality-evaluation` (deferred placeholder)
- Per-feature resolution: for implement stage actions, use `deliverable_folder` + feature context to resolve the correct feature's deliverables
- `change-request` action uses `user-selected` input_source (manual path input, no auto-resolution)

**Covered FRs:** FR-040.7, FR-040.8 (remaining), FR-040.10, FR-040.12, FR-040.20, FR-040.21, FR-040.22, FR-040.23

**Acceptance Criteria:**
- [ ] AC-040.4: "Feature Refinement" opens modal with per-feature context
- [ ] AC-040.5: "Technical Design" opens modal with feature spec from `feature_refinement` deliverables
- [ ] AC-040.6: "Implementation" opens modal with technical design from `technical_design` deliverables
- [ ] AC-040.7: "Acceptance Testing" opens modal with implementation deliverables
- [ ] AC-040.8: "Change Request" opens modal with manual file path input
- [ ] AC-040.15: `deliverable_folder` field present in workflow template and propagated via API
- [ ] AC-040.17: Per-feature actions resolve feature context from workflow

**Dependencies:** FEATURE-040-A (requires generalized modal infrastructure)

**Technical Considerations:**
- `deliverable_folder` is a relative path from the workflow's idea/epic root folder (e.g., `refined-idea/`, `EPIC-040/FEATURE-040-A/`)
- For per-feature actions, `deliverable_folder` may include `{feature_id}` placeholder that resolves at runtime
- Backend change: workflow template loader + API response must include `deliverable_folder`
- `change_request` is special — always shows manual input, no auto-resolution

---

### FEATURE-040-C: Skill Workflow-Mode Compliance

**Summary:** Update all 8 task-based skills that are not yet workflow-mode compliant. This is a documentation/config change (SKILL.md files), not a code change.

**Scope:**
- For each skill, add `execution_mode` and `workflow.name` to Input Parameters
- Add `workflow_action` to Output Result YAML
- Add conditional `update_workflow_action` MCP call in execution procedure (when `execution_mode == "workflow-mode"`)
- Skills to update:
  1. `x-ipe-task-based-idea-mockup` (partial → add workflow_action output)
  2. `x-ipe-task-based-requirement-gathering`
  3. `x-ipe-task-based-feature-breakdown`
  4. `x-ipe-task-based-feature-refinement`
  5. `x-ipe-task-based-technical-design`
  6. `x-ipe-task-based-code-implementation`
  7. `x-ipe-task-based-feature-acceptance-test`
  8. `x-ipe-task-based-change-request`

**Covered FRs:** FR-040.24, FR-040.25, FR-040.26, FR-040.27

**Acceptance Criteria:**
- [ ] AC-040.16: All 8 skills updated with `execution_mode` input + `workflow_action` output

**Dependencies:** None (skill updates are independent of frontend/config changes)

**Technical Considerations:**
- Follow the pattern established by `x-ipe-task-based-ideation-v2` (updated in FEATURE-038-D) as the reference implementation
- Each skill update is a SKILL.md file edit — no application code changes
- Skills can be updated in parallel since they are independent files

> **⚠️ CR Impact Note** (added 2026-02-27, ref: EPIC-042/CR-003)
> - **Change:** Legacy `<input-file>` placeholder replaced by `$output:tag$` syntax in workflow mode; instructions become read-only resolved preview; new `workflow-prompts` array in copilot-prompt.json
> - **Affected FRs:** FR-040.6 (placeholder replaced), FR-040.9 (prompt structure extended), FR-040.14 (instructions display → read-only preview)
> - **Action Required:** Workflow-mode behavior superseded by EPIC-042 `workflow-prompts`; free-mode remains unchanged
> - **New Feature Ref:** EPIC-042 — see [requirement-details-part-14.md](x-ipe-docs/requirements/requirement-details-part-14.md)

