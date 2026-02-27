# Feature Specification: Workflow Prompts Config & Basic Template Resolution (MVP)

> **Feature ID:** FEATURE-042-A
> **Epic:** EPIC-042 — CR-Optimize Feature Implementation: Workflow Prompts & Template Resolution
> **Version:** v1.0
> **Status:** Refined
> **Last Updated:** 02-27-2026

---

## Version History

| Version | Date       | Author | Changes                          |
|---------|------------|--------|----------------------------------|
| v1.0    | 2025-07-15 | Agent  | Initial specification from FR-042.1–042.11, AC-042.1–042.9 |

---

## Linked Mockups

N/A — This feature modifies the existing Action Execution Modal. No new UI screens are introduced; changes are behavioral (prompt source switching and template variable resolution within the current modal layout).

---

## Overview

### What
Introduce a `"workflow-prompts"` top-level array in `copilot-prompt.json` that provides dedicated prompt templates for workflow-mode actions, along with a frontend template resolver that substitutes `$output:tag$`, `$output-folder:tag$`, and `$feature-id$` variable tokens with concrete values derived from workflow action context.

### Why
Currently, workflow-mode and free-mode share the same prompt entries in `copilot-prompt.json` (under `ideation.prompts`, `workflow.prompts`, `feature.prompts`). This creates coupling problems:
1. **Prompt divergence** — Workflow-mode prompts need `$output:tag$` variable syntax tied to `action_context` refs, while free-mode prompts use legacy `<input-file>` / `<current-idea-file>` placeholders.
2. **Maintenance burden** — Editing a shared prompt risks breaking the other mode.
3. **Template resolution gap** — No mechanism exists to parse `$...$` tokens and resolve them against the action context dropdowns populated from `workflow-template.json`.

Separating workflow prompts and adding a template resolver enables each mode to evolve independently and provides the foundation for subsequent features (conditional blocks, default dropdown values, read-only preview).

### Who
- **Primary users:** Developers and engineers using the X-IPE Engineering Workflow Manager in workflow mode.
- **Secondary users:** Free-mode users — must experience zero behavioral change.

---

## User Stories

### US-1: Workflow Prompt Source
**As** a developer using the Engineering Workflow in workflow mode,
**I want** the Action Execution Modal to load prompts from a dedicated `workflow-prompts` array,
**So that** workflow-mode prompts can use template variables (`$output:tag$`) without affecting free-mode prompts.

### US-2: Template Variable Resolution
**As** a developer triggering an action (e.g., "Refine Idea") in workflow mode,
**I want** `$output:raw-idea$` in the prompt template to automatically resolve to the actual file path selected in the context dropdown,
**So that** the generated command contains correct, concrete paths without manual editing.

### US-3: Feature ID Injection
**As** a developer working on a per-feature action (e.g., "Technical Design" for FEATURE-042-A),
**I want** `$feature-id$` in the prompt template to resolve to my current feature ID,
**So that** the skill receives the correct feature context automatically.

### US-4: Free-Mode Backward Compatibility
**As** a developer using X-IPE in free mode (no active workflow),
**I want** all existing prompts to continue working exactly as before,
**So that** the introduction of `workflow-prompts` does not disrupt my current workflow.

### US-5: Folder Path Resolution
**As** a developer whose action needs a folder of deliverables (e.g., refined ideas folder),
**I want** `$output-folder:refined-ideas-folder$` to resolve to the correct folder path,
**So that** skills that operate on directories receive the right input.

---

## Acceptance Criteria

### AC-042.1: Workflow-Prompts Array Exists
- **Given** the `copilot-prompt.json` configuration file
- **When** it is loaded by the frontend
- **Then** a top-level `"workflow-prompts"` array field exists containing at least 1 entry (the `refine_idea` action entry for initial testing)
- **Measurable:** Parse `copilot-prompt.json`; assert `Array.isArray(config["workflow-prompts"])` and `config["workflow-prompts"].length >= 1`.

### AC-042.2: Workflow-Mode Prompt Source
- **Given** the user opens the "Refine Idea" modal in workflow mode (an active workflow is selected)
- **When** the modal loads instructions
- **Then** the prompt displayed comes from the `workflow-prompts` entry where `action === "refine_idea"`, NOT from the legacy `ideation.prompts` section
- **Measurable:** Compare the displayed prompt text against the `workflow-prompts[action=refine_idea].prompt-details[lang].command` value; they must match (after template resolution).

### AC-042.3: Output Variable Resolution
- **Given** the `refine_idea` workflow prompt contains `$output:raw-idea$`
- **And** the context dropdown for `raw-idea` has a selected value (e.g., `x-ipe-docs/ideas/my-project/raw-idea.md`)
- **When** template resolution runs
- **Then** `$output:raw-idea$` is replaced with the exact file path from the dropdown selection
- **Measurable:** The resolved command string contains the literal path `x-ipe-docs/ideas/my-project/raw-idea.md` where `$output:raw-idea$` was.

### AC-042.9: Free-Mode Backward Compatibility
- **Given** no active workflow (free mode)
- **When** the user opens any action modal (e.g., "Refine Idea" from the sidebar)
- **Then** the prompt is loaded from the existing section (`ideation.prompts`, `workflow.prompts`, or `feature.prompts`) using the current placeholder mechanism (`<current-idea-file>`, `<input-file>`)
- **Measurable:** Free-mode prompts produce identical commands to the pre-FEATURE-042-A behavior.

### AC-MVP.1: Output-Folder Variable Resolution
- **Given** a workflow prompt contains `$output-folder:ideas-folder$`
- **And** the context dropdown for `ideas-folder` has a selected folder path
- **When** template resolution runs
- **Then** `$output-folder:ideas-folder$` is replaced with the folder path
- **Measurable:** The resolved command string contains the folder path where the token was.

### AC-MVP.2: Feature-ID Variable Resolution
- **Given** the modal is opened for a per-feature action with `featureId = "FEATURE-042-A"`
- **And** the prompt template contains `$feature-id$`
- **When** template resolution runs
- **Then** `$feature-id$` is replaced with `FEATURE-042-A`
- **Measurable:** The resolved command contains the literal string `FEATURE-042-A` where `$feature-id$` was.

### AC-MVP.3: Schema Validation
- **Given** a `workflow-prompts` entry
- **When** it is parsed
- **Then** it contains all required fields: `id` (string), `action` (string), `icon` (string), `input_source` (array), `prompt-details` (array with at least one entry containing `language`, `label`, `command`)
- **Measurable:** Schema validation passes for every entry in the array.

---

## Functional Requirements

### FR-042.1: Workflow-Prompts Array Field
- **Input:** `copilot-prompt.json` file structure.
- **Process:** Add a new top-level key `"workflow-prompts"` whose value is a JSON array. The array sits alongside existing keys (`ideation`, `evaluation`, `workflow`, `feature`, `placeholder`). No existing keys are modified or removed.
- **Output:** `copilot-prompt.json` contains `"workflow-prompts": [...]` at the top level. The `version` field increments to reflect the schema change.

### FR-042.2: Entry Schema
- **Input:** Each object in the `workflow-prompts` array.
- **Process:** Validate that each entry contains the following fields:
  - `id` (string) — Unique identifier for the prompt entry (e.g., `"refine-idea"`).
  - `action` (string) — Maps 1:1 to a workflow action key in `workflow-template.json` (e.g., `"refine_idea"`).
  - `icon` (string) — Bootstrap icon class for UI display (e.g., `"bi-stars"`).
  - `input_source` (array of strings) — Names of prior actions whose deliverables feed this action. Informational only.
  - `prompt-details` (array) — One or more language-specific prompt definitions.
- **Output:** Each entry is a well-formed object conforming to the schema. Entries missing any required field are rejected at development time (schema validation).

### FR-042.3: Prompt-Details Language Entries
- **Input:** The `prompt-details` array within a `workflow-prompts` entry.
- **Process:** Each element in `prompt-details` must contain:
  - `language` (string) — ISO 639-1 language code (e.g., `"en"`, `"zh"`).
  - `label` (string) — Human-readable display name shown in the modal (e.g., `"Refine Idea"`).
  - `command` (string) — Prompt template string that may contain `$output:tag$`, `$output-folder:tag$`, and/or `$feature-id$` variable tokens.
- **Output:** The modal can retrieve the correct language-specific prompt based on the user's language preference.

### FR-042.4: One-to-One Action Mapping
- **Input:** The `action` field of each `workflow-prompts` entry, cross-referenced with action keys in `workflow-template.json`.
- **Process:** Enforce that:
  1. Every `action` value corresponds to exactly one action key in `workflow-template.json`.
  2. No two `workflow-prompts` entries share the same `action` value (uniqueness constraint).
  3. An action key in `workflow-template.json` may exist without a corresponding `workflow-prompts` entry (some actions like `compose_idea` may not need CLI prompts).
- **Output:** A clean 1:1 mapping from workflow-prompts entries to workflow-template actions, enabling unambiguous prompt lookup.

### FR-042.5: Input-Source Is Informational
- **Input:** The `input_source` array in a `workflow-prompts` entry (e.g., `["compose_idea"]`).
- **Process:** The `input_source` field provides documentation about which prior actions produce inputs for this action. It is NOT used for runtime resolution. The authoritative source for context references and candidate resolution is the `action_context` object in `workflow-template.json`.
- **Output:** `input_source` is displayed or logged for informational purposes only. Template resolution uses `action_context` exclusively.

### FR-042.6: Workflow-Mode Prompt Lookup
- **Input:** An action key (e.g., `"refine_idea"`) and the loaded `copilot-prompt.json` config.
- **Process:** When the modal opens in workflow mode:
  1. Read the `workflow-prompts` array from config.
  2. Find the entry where `entry.action === actionKey`.
  3. Select the `prompt-details` element matching the current UI language.
  4. Use the matched `command` as the prompt template.
- **Output:** The modal displays the workflow-specific prompt template (before variable resolution). If no matching entry is found, fall back to legacy prompt sections (see Edge Cases).

### FR-042.7: Free-Mode Prompt Routing
- **Input:** The current mode (workflow vs. free) and an action key.
- **Process:** When the modal opens in free mode (no active workflow):
  1. Do NOT read from `workflow-prompts`.
  2. Continue using existing prompt lookup logic: search `ideation.prompts`, `workflow.prompts`, and `feature.prompts` by matching the prompt `id` (converting action_key underscores to dashes).
  3. Resolve legacy placeholders (`<current-idea-file>`, `<input-file>`, `<feature-id>`) using existing `_resolveInputFiles()` and `_resolveIdeaFiles()` methods.
- **Output:** Free-mode prompt behavior is identical to pre-FEATURE-042-A behavior. No regressions.

### FR-042.8: Three Variable Types
- **Input:** A prompt template string from `workflow-prompts[].prompt-details[].command`.
- **Process:** The template resolver recognizes three variable token patterns:
  1. **`$output:tag-name$`** — Resolves to a deliverable file path. The `tag-name` matches an `action_context` ref key.
  2. **`$output-folder:tag-name$`** — Resolves to a deliverable folder path. The `tag-name` matches an `action_context` ref key whose candidates point to a folder.
  3. **`$feature-id$`** — Resolves to the current feature ID string from the modal's runtime context (e.g., `"FEATURE-042-A"`).
- **Output:** All three token types are recognized by the parser. Unrecognized patterns (not matching any of these three forms) are left as-is.

### FR-042.9: Output Variable Resolution via Action Context
- **Input:** A `$output:tag-name$` token and the current state of action context dropdowns.
- **Process:**
  1. Parse the token to extract `tag-name` (e.g., `"raw-idea"` from `$output:raw-idea$`).
  2. Locate the action context dropdown whose ref name matches `tag-name`.
  3. Read the currently selected value from that dropdown.
  4. If the dropdown value is a valid path (not "auto-detect" or "N/A"), replace the token with that path.
  5. If the dropdown value is "auto-detect", replace the token with the string `"auto-detect"`.
  6. If the dropdown value is "N/A" (optional ref), replace the token with `"N/A"`.
- **Output:** The token is replaced with the concrete value from the dropdown. The resolution is deterministic based on dropdown state.

### FR-042.10: Output-Folder Variable Resolution
- **Input:** A `$output-folder:tag-name$` token and the current state of action context dropdowns.
- **Process:**
  1. Parse the token to extract `tag-name` (e.g., `"ideas-folder"` from `$output-folder:ideas-folder$`).
  2. Locate the action context dropdown whose ref name matches `tag-name`.
  3. Read the currently selected value from that dropdown (which is a folder path).
  4. Replace the token with the folder path.
- **Output:** The token is replaced with the folder path string.

### FR-042.11: Feature-ID Variable Resolution
- **Input:** A `$feature-id$` token and the modal's runtime context.
- **Process:**
  1. Detect the `$feature-id$` token in the template.
  2. Read the `featureId` property from the modal context (passed when the modal is opened for a per-feature action).
  3. Replace the token with the feature ID string (e.g., `"FEATURE-042-A"`).
  4. If `featureId` is not set (shared-stage action like `refine_idea`), replace with empty string or leave unresolved (see Edge Cases).
- **Output:** The token is replaced with the feature ID or handled gracefully when unavailable.

---

## Non-Functional Requirements

### NFR-042.1: Template Resolution Performance
- Template resolution (all token parsing + substitution for a single prompt template) MUST complete in **< 50ms**.
- This includes scanning for all `$...$` tokens, looking up dropdown values, and producing the final resolved string.
- Measurement: Use `performance.now()` around the resolver call; assert elapsed < 50ms across all prompt templates.

### NFR-042.3: Backward Compatibility
- Adding the `workflow-prompts` array to `copilot-prompt.json` MUST NOT break any existing functionality.
- All existing top-level keys (`version`, `ideation`, `evaluation`, `workflow`, `placeholder`, `feature`) remain unchanged.
- All existing prompt IDs (23 prompts across 5 sections) continue to function in free mode.
- The config API endpoint (`/api/config/copilot-prompt`) returns the augmented JSON without errors.

### NFR-MVP.1: Maintainability
- The template resolver function must be a self-contained, testable unit (pure function taking template string + context map, returning resolved string).
- No side effects during resolution — dropdown reading happens before resolver invocation.

### NFR-MVP.2: Error Resilience
- Malformed tokens (e.g., `$output:$`, `$output:tag`, `$$`, `$unknown-type:tag$`) must not crash the resolver. They are left as-is in the output string.

---

## UI/UX Requirements

### User Flow: Workflow-Mode Action Execution

1. **User clicks an action** (e.g., "Refine Idea") in the Workflow Manager panel.
2. **Modal opens** with `actionKey = "refine_idea"` and `workflowName = "my-project"`.
3. **Mode detection:** Modal checks if `workflowName` is set → workflow mode.
4. **Prompt lookup:** Modal fetches `copilot-prompt.json`, reads `workflow-prompts`, finds entry with `action === "refine_idea"`.
5. **Language selection:** Picks `prompt-details` entry matching current UI language (default: `"en"`).
6. **Context dropdowns rendered:** Modal reads `action_context` from `workflow-template.json` for `refine_idea` (refs: `raw-idea` required, `uiux-reference` optional). Dropdowns populate with candidates from API.
7. **Template resolution:** The `command` string (e.g., `"refine the idea $output:raw-idea$ with ideation skill"`) is resolved by replacing `$output:raw-idea$` with the dropdown's selected value.
8. **Instructions displayed:** The resolved command appears in the instructions area.
9. **User reviews, optionally adds extra instructions, clicks Execute.**

### User Flow: Free-Mode (Unchanged)

1. **User clicks an action** from the sidebar (no active workflow).
2. **Modal opens** without `workflowName`.
3. **Mode detection:** `workflowName` is null → free mode.
4. **Prompt lookup:** Modal uses existing logic — searches `ideation.prompts`, `workflow.prompts`, `feature.prompts` by `id`.
5. **Legacy placeholder resolution:** `<current-idea-file>` and `<input-file>` resolved via existing `_resolveIdeaFiles()` / `_resolveInputFiles()`.
6. **User executes as before.**

### UI Elements Affected

| Element | Change | Details |
|---------|--------|---------|
| Instructions text area | Source change | In workflow mode, populated from `workflow-prompts` instead of legacy sections |
| Context dropdowns | No change | Already rendered from `action_context` (FEATURE-041-F) |
| Execute button | No change | Command construction unchanged |
| Extra Instructions | No change | Remains editable, appended to command |

---

## Dependencies

### Upstream Dependencies
- **None** — This is the MVP foundation feature for EPIC-042. It does not depend on other EPIC-042 features.

### Existing Infrastructure (Pre-Requisites Already Met)
- `copilot-prompt.json` exists with version 3.2 schema (additive change only).
- `workflow-template.json` exists with `action_context` definitions for all 12 actions.
- `action-execution-modal.js` already implements mode detection, context dropdown rendering, and placeholder resolution.
- Config API endpoint (`/api/config/copilot-prompt`) already serves the JSON file.

### Downstream Dependents
- **FEATURE-042-B** (Conditional Block Parsing) — Builds on the template resolver to add `<>` block evaluation.
- **FEATURE-042-C** (Default Dropdown Values) — Uses `workflow-prompts` to inform dropdown defaults.
- **FEATURE-042-D** (Read-Only Preview + Live Update) — Relies on template resolution for live preview rendering.
- **FEATURE-042-E** (Full Prompt Migration) — Migrates all 9 workflow actions to `workflow-prompts`, building on the schema defined here.

---

## Business Rules

### BR-1: Mode Determines Prompt Source
The modal's operating mode (workflow vs. free) is the sole determinant of which prompt source is used:
- **Workflow mode** (`workflowName` is set) → `workflow-prompts` array.
- **Free mode** (`workflowName` is null/undefined) → Legacy sections (`ideation.prompts`, `workflow.prompts`, `feature.prompts`).

### BR-2: Action Context Is Authoritative
The `action_context` object in `workflow-template.json` is the single source of truth for:
- Which context refs an action requires.
- Whether a ref is required or optional.
- Where candidates are sourced from.
The `input_source` field in `workflow-prompts` is documentation only and never drives runtime behavior.

### BR-3: One Prompt Per Action Per Language
For a given `action` value in `workflow-prompts`, there is exactly one prompt template per language. The `prompt-details` array contains at most one entry per `language` code.

### BR-4: Variable Resolution Order
Template variables are resolved in a single pass:
1. Scan the template string for all `$...$` tokens.
2. For each token, determine type (`output`, `output-folder`, or `feature-id`).
3. Look up the value from the corresponding source (dropdown or modal context).
4. Replace all tokens simultaneously (no cascading re-resolution).

### BR-5: Additive Schema Changes Only
The `copilot-prompt.json` schema change is strictly additive. No existing field is renamed, removed, or restructured. The `version` field is incremented to signal the new capability.

---

## Edge Cases & Constraints

### Edge Cases

#### EC-1: Empty Workflow-Prompts Array
- **Scenario:** `workflow-prompts` exists but is an empty array (`[]`).
- **Expected behavior:** In workflow mode, no entry is found for the requested action. The modal falls back to legacy prompt sections. A console warning is logged: `"No workflow-prompt found for action: {actionKey}, falling back to legacy prompts"`.

#### EC-2: Action Not Found in Workflow-Prompts
- **Scenario:** The modal opens for `action = "compose_idea"` in workflow mode, but no `workflow-prompts` entry has `action === "compose_idea"`.
- **Expected behavior:** Same as EC-1 — fallback to legacy prompt sections with a console warning. This is a valid state since not all actions need workflow-specific prompts (e.g., `compose_idea` uses a modal-only flow).

#### EC-3: Requested Language Not Available
- **Scenario:** User's UI language is `"de"` (German) but the `prompt-details` array only has `"en"` and `"zh"` entries.
- **Expected behavior:** Fall back to the first entry in `prompt-details` (typically `"en"`). No error thrown.

#### EC-4: Malformed Variable Token — Missing Tag Name
- **Scenario:** Template contains `$output:$` (colon but no tag name).
- **Expected behavior:** Token is not recognized as a valid variable. Left as-is in the output string. No error thrown.

#### EC-5: Malformed Variable Token — Missing Closing Dollar Sign
- **Scenario:** Template contains `$output:raw-idea` (no closing `$`).
- **Expected behavior:** Not matched by the `$...$` regex pattern. Left as-is in the output. No error thrown.

#### EC-6: Malformed Variable Token — Empty Token
- **Scenario:** Template contains `$$` (two consecutive dollar signs with nothing between).
- **Expected behavior:** Not matched as a valid variable token. Left as-is. No error thrown.

#### EC-7: Malformed Variable Token — Unknown Type Prefix
- **Scenario:** Template contains `$unknown-type:some-tag$`.
- **Expected behavior:** The parser does not recognize `unknown-type` as a valid variable type (`output`, `output-folder`, `feature-id`). Token is left as-is in the output. No error thrown.

#### EC-8: Dropdown Value Is "auto-detect"
- **Scenario:** `$output:raw-idea$` is in the template, but the `raw-idea` dropdown is set to "auto-detect".
- **Expected behavior:** The token resolves to the literal string `"auto-detect"`. The downstream skill handles auto-detection logic.

#### EC-9: Dropdown Value Is "N/A" (Optional Ref)
- **Scenario:** `$output:uiux-reference$` is in the template, and `uiux-reference` is optional with dropdown set to "N/A".
- **Expected behavior:** The token resolves to `"N/A"`. (Note: Conditional block handling of N/A is out of scope for this MVP — that is FEATURE-042-B.)

#### EC-10: Feature-ID Not Set for Shared Action
- **Scenario:** `$feature-id$` appears in a shared-stage action prompt (e.g., `refine_idea`) where no feature is selected.
- **Expected behavior:** `$feature-id$` resolves to an empty string `""`. A console warning is logged: `"$feature-id$ used but no featureId set in modal context"`.

#### EC-11: Dropdown Ref Name Does Not Match Any Token
- **Scenario:** Action context has a ref `"specification"` but the prompt template has no `$output:specification$` token.
- **Expected behavior:** The dropdown renders normally. No resolution attempt is made for non-existent tokens. This is a valid state — not all context refs need to appear in the prompt.

#### EC-12: Multiple Occurrences of Same Token
- **Scenario:** Template contains `$output:raw-idea$` twice (e.g., in both a file reference and a log statement).
- **Expected behavior:** Both occurrences are resolved to the same value from the dropdown. Resolution is global within the template string.

#### EC-13: Duplicate Action Value in Workflow-Prompts
- **Scenario:** Two entries in `workflow-prompts` have `action: "refine_idea"`.
- **Expected behavior:** The first matching entry is used. A console warning is logged: `"Duplicate workflow-prompt action: refine_idea"`. This should be caught by development-time validation.

### Constraints

1. **Free-mode prompts must work unchanged** — Zero regressions in free-mode behavior.
2. **`action_context` in `workflow-template.json` is authoritative** — `input_source` in `workflow-prompts` is never used for resolution.
3. **Template parser is frontend-only** — All resolution happens in the browser; no server-side template processing.
4. **`copilot-prompt.json` changes are additive** — No existing fields removed or restructured.
5. **No mockups needed** — All changes occur within the existing Action Execution Modal UI.
6. **MVP scope: basic resolution only** — Conditional blocks (`<>` syntax), default dropdown values, read-only preview, and live update are OUT OF SCOPE (subsequent features).

---

## Out of Scope

The following are explicitly NOT part of FEATURE-042-A:

| Item | Covered By |
|------|------------|
| Conditional `<>` block parsing (skip block if variable is N/A) | FEATURE-042-B |
| Dropdown defaults to prior action deliverables (instead of "auto-detect") | FEATURE-042-C |
| Read-only instructions preview with live update on dropdown change | FEATURE-042-D |
| Full migration of all 9 workflow actions to `workflow-prompts` | FEATURE-042-E |
| EXTRA INSTRUCTIONS editability changes | FEATURE-042-D |
| Server-side template resolution | Not planned |
| Nested variable resolution (`$output:$output:inner$$`) | Not planned |
| Custom user-defined variable types beyond the three specified | Not planned |

---

## Technical Considerations

> These describe WHAT the system must support, not HOW to implement it.

### TC-1: Config Schema Extension
The `copilot-prompt.json` schema must support a new top-level array without breaking existing parsers. Any consumer of this config (frontend modal, API endpoint) must gracefully handle the new field — either using it or ignoring it.

### TC-2: Template Token Grammar
The variable token grammar follows the pattern `$type:tag-name$` where:
- Delimiter: `$` (dollar sign) on both sides.
- Type: one of `output`, `output-folder`, or the special token `feature-id` (no colon).
- Tag name: alphanumeric with hyphens, matching `action_context` ref keys.
- The regex must not greedily match across multiple tokens (e.g., `$output:a$ and $output:b$` must match two separate tokens).

### TC-3: Resolution Context Map
The resolver needs a context map that maps tag names to their current values. This map is constructed from:
- Action context dropdown values (for `$output:tag$` and `$output-folder:tag$`).
- Modal runtime properties (for `$feature-id$`).
The resolver itself should be a pure function: `resolve(template: string, contextMap: Record<string, string>) → string`.

### TC-4: Mode Detection
The system must reliably distinguish workflow mode from free mode. The presence of `workflowName` in the modal's initialization parameters is the indicator. This detection must happen before prompt lookup to route to the correct source.

### TC-5: Language Fallback
When the user's preferred language has no matching `prompt-details` entry, the system must fall back to a default language (first entry in the array) rather than showing no prompt or an error.

### TC-6: Backward-Compatible API Response
The `/api/config/copilot-prompt` endpoint returns the full JSON. Adding `workflow-prompts` to the JSON must not cause errors in any existing consumer. Consumers that don't know about `workflow-prompts` simply ignore the extra field.

---

## Open Questions

| # | Question | Status | Resolution |
|---|----------|--------|------------|
| OQ-1 | Should `workflow-prompts` include an entry for `compose_idea` (which uses a modal-only flow, not a CLI prompt)? | Open | Tentatively no — `compose_idea` doesn't send a CLI command. Validate during implementation. |
| OQ-2 | What is the exact `version` value for the updated `copilot-prompt.json`? | Open | Propose `"3.3"` to signal additive change. |
| OQ-3 | Should the fallback from workflow-prompts to legacy sections log a warning or silently proceed? | Resolved | Log a console warning for debuggability (see EC-1, EC-2). |
| OQ-4 | For `$feature-id$` on shared-stage actions, should the token resolve to empty string or be left unresolved? | Resolved | Resolve to empty string with console warning (see EC-10). |
