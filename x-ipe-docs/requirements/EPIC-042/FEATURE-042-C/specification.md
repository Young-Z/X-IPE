# Feature Specification: Deliverable-Default Dropdowns & Read-Only Preview

> Feature ID: FEATURE-042-C  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-27-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 2025-07-14 | Initial specification | EPIC-042 |

## Linked Mockups

N/A

## Overview

### What

This feature enhances the action execution modal with two key UX improvements for workflow mode:

1. **Deliverable-Default Dropdowns** — Context dropdowns automatically default to prior action deliverable file paths instead of "auto-detect", giving users immediate visibility into which files will be used as input.
2. **Read-Only Instructions Preview** — The INSTRUCTIONS textarea becomes a live, read-only preview of the fully resolved command, with `$output:tag$` placeholders replaced by actual file paths, conditional `<>` blocks evaluated, and real-time updates as the user changes dropdown selections.

EXTRA INSTRUCTIONS remains fully editable and is appended to the resolved command during composition.

### Why

Without smart defaults, users must manually inspect deliverables and mentally map which files feed into each action. The read-only preview eliminates guesswork by showing exactly what the skill will receive — reducing errors and building confidence in workflow execution. Together, these improvements bridge the gap between the abstract template definition and the concrete command that will be sent.

### Who

- **Primary:** Human reviewers executing workflow actions through the modal
- **Secondary:** AI agents that rely on correctly composed commands from the modal

## User Stories

- As a **human reviewer**, I want **context dropdowns to default to the deliverable file from the prior action**, so that **I don't have to manually look up which file was produced**.

- As a **human reviewer**, I want **the dropdown to fall back to "auto-detect" when no deliverable exists**, so that **I'm never stuck with a blank or broken default**.

- As a **human reviewer**, I want **to override any dropdown default**, so that **I can point an action at a different file if needed**.

- As a **human reviewer**, I want **the INSTRUCTIONS box to show the fully resolved command in real-time**, so that **I can see exactly what will be sent to the skill before I execute it**.

- As a **human reviewer**, I want **the preview to update immediately when I change a dropdown**, so that **I can verify the impact of my selection without extra steps**.

- As a **human reviewer**, I want **EXTRA INSTRUCTIONS to remain editable**, so that **I can append custom guidance that gets included in the final command**.

## Acceptance Criteria

- [ ] AC-042.5: Context dropdown for `raw-idea` defaults to the `compose_idea` deliverable file path when a deliverable exists
- [ ] AC-042.6: INSTRUCTIONS text box is read-only and displays the fully resolved command (all `$output:tag$` replaced, `<>` conditionals evaluated)
- [ ] AC-042.7: Changing a context dropdown selection immediately updates the read-only INSTRUCTIONS preview
- [ ] AC-042.8: EXTRA INSTRUCTIONS textarea remains editable and its content is appended to the resolved command in the final composed output
- [ ] AC-042.C1: When no prior deliverable exists for a given action_context ref, the dropdown defaults to "auto-detect"
- [ ] AC-042.C2: User can override any dropdown default (deliverable or auto-detect) with a manual selection
- [ ] AC-042.C3: Deliverable resolution results are cached per modal open — dropdown changes do NOT trigger re-fetch of deliverables
- [ ] AC-042.C4: When the modal is opened in free mode (non-workflow), INSTRUCTIONS textarea is NOT read-only and no template resolution occurs
- [ ] AC-042.C5: Command composition follows the format: `{resolved_instructions}\n\n{extra_instructions}` when EXTRA INSTRUCTIONS is non-empty; otherwise only `{resolved_instructions}`
- [ ] AC-042.C6: Conditional `<>` blocks are evaluated in real-time based on current dropdown selections

## Functional Requirements

### FR-042.20: Deliverable Default Resolution

**Description:** On modal open in workflow mode, resolve prior action deliverables for each action_context ref and set dropdown defaults.

**Details:**
- Input: Workflow instance JSON containing action definitions with `action_context` refs (e.g., `raw-idea`, `uiux-reference`); prior action completion state with deliverable paths
- Process:
  1. For each `action_context` ref in the current action's prompt definition, query the workflow instance for the prior action's deliverable file path
  2. If a deliverable file path exists for the ref → set dropdown default to that path
  3. If no deliverable exists → set dropdown default to "auto-detect"
- Output: Each context dropdown is pre-populated with the appropriate default value

### FR-042.21: Auto-Detect Fallback

**Description:** When no deliverable is found for a given action_context ref, the dropdown gracefully falls back to "auto-detect".

**Details:**
- Input: Action context ref with no matching deliverable in the workflow instance
- Process: Set dropdown value to the sentinel "auto-detect" option, which signals downstream resolution to scan workspace for the best match
- Output: Dropdown displays "auto-detect" as the selected value

### FR-042.22: User Override of Defaults

**Description:** Users can change any dropdown selection regardless of whether it was defaulted to a deliverable or "auto-detect".

**Details:**
- Input: User interaction — selecting a different option from the context dropdown
- Process: Replace the current dropdown value with the user's selection; trigger preview re-resolution (FR-042.27)
- Output: Dropdown reflects user's choice; INSTRUCTIONS preview updates accordingly

### FR-042.23: Cached Deliverable Resolution

**Description:** Deliverable resolution is performed once when the modal opens and cached for the lifetime of that modal instance.

**Details:**
- Input: Modal open event in workflow mode
- Process:
  1. Query all deliverable paths for action_context refs in a single pass
  2. Store results in a local cache object (keyed by action_context ref)
  3. Subsequent dropdown interactions read from cache — no additional backend calls
- Output: Cache object mapping `{ ref_name: deliverable_path | null }` available for the modal session

### FR-042.24: Deliverable Existence Validation

**Description:** Validate that cached deliverable paths still point to existing files before using them as defaults.

**Details:**
- Input: Cached deliverable path for a given ref
- Process: If the deliverable file was deleted or moved after the prior action completed, treat as "no deliverable" and fall back to "auto-detect"
- Output: Dropdown defaults to either the valid deliverable path or "auto-detect"

### FR-042.25: Read-Only Instructions Display

**Description:** In workflow mode, the INSTRUCTIONS textarea becomes read-only and shows the fully resolved command.

**Details:**
- Input: Workflow prompt template containing `$output:tag$` placeholders and `<>` conditional blocks
- Process:
  1. Set the `readonly` attribute on the INSTRUCTIONS textarea element
  2. Resolve all `$output:tag$` placeholders using current dropdown selections (deliverable paths or "auto-detect" literal)
  3. Evaluate all `<>` conditional blocks based on whether the referenced tags have concrete values
  4. Display the fully resolved text in the textarea
- Output: INSTRUCTIONS textarea shows resolved command text; user cannot edit it directly

### FR-042.26: Live Preview Updates

**Description:** The INSTRUCTIONS preview updates immediately when any context dropdown selection changes.

**Details:**
- Input: Dropdown `change` event on any action_context dropdown
- Process:
  1. Read the new dropdown value
  2. Re-run template resolution against the prompt template using updated dropdown values
  3. Re-evaluate all `<>` conditional blocks
  4. Replace INSTRUCTIONS textarea content with newly resolved text
- Output: INSTRUCTIONS textarea reflects the updated resolved command within the same UI frame

### FR-042.27: Conditional Block Evaluation

**Description:** Conditional `<>` blocks in templates are evaluated in real-time based on current context values.

**Details:**
- Input: Template text containing conditional blocks (e.g., `<if $output:uiux-reference$ exists>...instructions...</>`)
- Process:
  1. For each conditional block, check whether the referenced tag resolves to a concrete file path (not "auto-detect" and not empty)
  2. If condition is met → include the block content in the resolved output
  3. If condition is not met → omit the block entirely
- Output: Resolved template text with conditional blocks either expanded or removed

### FR-042.28: EXTRA INSTRUCTIONS Editability

**Description:** EXTRA INSTRUCTIONS textarea remains fully editable in workflow mode; no template substitution is applied to it.

**Details:**
- Input: User-typed text in the EXTRA INSTRUCTIONS textarea
- Process: EXTRA INSTRUCTIONS is treated as raw user input — no `$output:tag$` substitution, no `<>` evaluation; the textarea does NOT have the `readonly` attribute
- Output: User's text is preserved exactly as entered

### FR-042.29: Command Composition

**Description:** The final command sent to the skill is composed from the resolved INSTRUCTIONS and EXTRA INSTRUCTIONS.

**Details:**
- Input: Resolved INSTRUCTIONS text (from FR-042.25/FR-042.26); EXTRA INSTRUCTIONS text (from FR-042.28)
- Process:
  1. If EXTRA INSTRUCTIONS is empty or whitespace-only → final command = resolved INSTRUCTIONS
  2. If EXTRA INSTRUCTIONS has content → final command = `{resolved_instructions}\n\n{extra_instructions}`
- Output: Single composed command string ready for skill execution

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-042.1 | Template resolution (placeholder replacement + conditional evaluation) MUST complete in <50 ms | < 50 ms per resolution pass |
| NFR-042.2 | All template resolution MUST happen in the frontend — no backend round-trips for resolution | Frontend-only |
| NFR-042.3 | Deliverable cache MUST be populated in a single request on modal open | 1 request max |
| NFR-042.4 | Live preview updates MUST feel instantaneous to the user (no visible flicker or delay) | < 16 ms UI update |

## UI/UX Requirements

### User Flow: Modal Open in Workflow Mode

```
Modal opens (workflow mode)
  │
  ├─ 1. Fetch & cache deliverable paths for all action_context refs
  │
  ├─ 2. For each context dropdown:
  │     ├─ Deliverable exists?  →  Default = deliverable path
  │     └─ No deliverable?     →  Default = "auto-detect"
  │
  ├─ 3. INSTRUCTIONS textarea:
  │     ├─ Set readonly attribute
  │     └─ Resolve template → display resolved command
  │
  └─ 4. EXTRA INSTRUCTIONS textarea: editable, empty by default
```

### User Flow: Dropdown Change

```
User changes a context dropdown
  │
  ├─ 1. Read new dropdown value (from cache — no re-fetch)
  ├─ 2. Re-resolve template with updated context values
  ├─ 3. Re-evaluate <> conditional blocks
  └─ 4. Update INSTRUCTIONS textarea content (live)
```

### User Flow: Execute Action

```
User clicks Execute
  │
  ├─ 1. Read resolved INSTRUCTIONS text
  ├─ 2. Read EXTRA INSTRUCTIONS text
  ├─ 3. Compose final command:
  │     ├─ Extra empty?     →  command = resolved_instructions
  │     └─ Extra non-empty? →  command = resolved + "\n\n" + extra
  └─ 4. Send composed command to skill
```

### UI Element Behavior

| Element | Workflow Mode | Free Mode |
|---------|--------------|-----------|
| Context dropdowns | Visible; defaults from deliverables or "auto-detect" | Visible; no deliverable defaults |
| INSTRUCTIONS textarea | `readonly`; shows resolved template | Editable; user writes freely |
| EXTRA INSTRUCTIONS textarea | Editable; appended to resolved command | Editable; appended to user's instructions |
| Live preview indicator | Active (optional visual cue) | Not applicable |

## Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-042-A | Internal (blocking) | Workflow-prompts array and basic template resolution must exist. FEATURE-042-C builds on top of the `$output:tag$` syntax and `<>` conditional block parsing defined in 042-A. |
| Workflow instance JSON | Internal | Must contain deliverable paths from completed prior actions |
| `src/frontend/js/action-execution-modal.js` | Internal | Primary file where dropdown logic and preview rendering are implemented |
| `src/frontend/js/workflow-template.json` | Internal (read-only) | Contains `action_context` definitions; this feature reads but does NOT modify this file |

## Business Rules

1. **Deliverable Priority Rule:** When a prior action has produced a deliverable for a given `action_context` ref, that deliverable MUST be the dropdown default — "auto-detect" is only used as a fallback when no deliverable exists.

2. **Cache Immutability Rule:** Deliverable resolution is performed exactly once per modal open. Dropdown changes use cached results only. The cache is discarded when the modal closes.

3. **Read-Only Scope Rule:** Only the INSTRUCTIONS textarea is made read-only in workflow mode. EXTRA INSTRUCTIONS is always editable. In free mode (non-workflow), neither textarea is read-only.

4. **Composition Rule:** The final command is always `{resolved_instructions}` alone or `{resolved_instructions}\n\n{extra_instructions}`. No other separators, headers, or formatting are injected between the two parts.

5. **No Substitution in EXTRA INSTRUCTIONS:** The `$output:tag$` syntax and `<>` conditional blocks are NEVER evaluated inside EXTRA INSTRUCTIONS — it is treated as literal user text.

## Edge Cases & Constraints

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | **No prior deliverables exist** (all action_context refs have no deliverables) | All dropdowns default to "auto-detect"; INSTRUCTIONS preview resolves template with "auto-detect" literals for all tags |
| 2 | **Deliverable file was deleted** after prior action completed | Deliverable existence validation (FR-042.24) detects missing file; dropdown falls back to "auto-detect" for that ref |
| 3 | **Modal opened in free mode** (non-workflow) | No deliverable resolution occurs; INSTRUCTIONS textarea is editable (no `readonly`); no template resolution; no live preview |
| 4 | **EXTRA INSTRUCTIONS is empty** | Final composed command equals resolved INSTRUCTIONS only — no trailing newlines appended |
| 5 | **Very long resolved command** (template expands to thousands of characters) | INSTRUCTIONS textarea scrolls vertically; no truncation; full resolved text is preserved and sent on execute |
| 6 | **Multiple dropdowns changed rapidly** (user switches several dropdowns in quick succession) | Each change triggers re-resolution synchronously (frontend-only, <50 ms); the final state after all changes reflects the last set of selections — no race conditions since resolution is synchronous |
| 7 | **Conditional block references a tag set to "auto-detect"** | The conditional evaluates to false ("auto-detect" is not a concrete file path); the block content is omitted from the resolved output |
| 8 | **All conditional blocks evaluate to false** | All conditional content is removed; the resolved INSTRUCTIONS contains only the unconditional portions of the template |
| 9 | **Deliverable path contains special characters** (spaces, unicode) | Path is used as-is in the resolved template; no encoding or escaping is applied — file system paths are treated as opaque strings |
| 10 | **Modal is reopened for the same action** | Fresh deliverable resolution is performed; previous cache is discarded; defaults are re-evaluated |

## Out of Scope

- **Modifying `workflow-template.json`** — This feature reads template definitions but does not alter them.
- **Backend template resolution** — All resolution is frontend-only (NFR-042.2). No new API endpoints for resolution.
- **Deliverable file content preview** — Dropdowns show file paths, not file contents. Content preview is a separate concern.
- **EXTRA INSTRUCTIONS template syntax** — No `$output:tag$` or `<>` processing in EXTRA INSTRUCTIONS. If this is needed in the future, it would be a new feature.
- **Multi-file deliverables** — Each action_context ref maps to a single deliverable path. Support for multiple deliverables per ref is out of scope.
- **Undo/redo for dropdown selections** — Standard browser undo behavior applies; no custom undo stack.

## Technical Considerations

- **Cache structure:** Deliverable resolution results should be stored as a simple key-value map (`ref_name → file_path | null`) scoped to the modal instance lifecycle. The cache is populated on modal open and discarded on modal close.
- **Read-only mechanism:** The `readonly` HTML attribute on the INSTRUCTIONS textarea is sufficient — it prevents user editing while still allowing programmatic content updates and text selection/copy.
- **Resolution performance:** Since templates are short (typically <2 KB) and the number of `$output:tag$` placeholders is small (typically <10), string replacement and conditional evaluation can be done with simple regex or string scanning — no AST parsing needed.
- **Synchronous resolution:** Because resolution is frontend-only and fast (<50 ms), it can be performed synchronously on each dropdown change event, eliminating race conditions from async operations.
- **Dropdown change handler:** A single event listener on dropdown changes triggers re-resolution, ensuring the INSTRUCTIONS preview is always consistent with current selections.

## Open Questions

| # | Question | Status | Resolution |
|---|----------|--------|------------|
| 1 | Should "auto-detect" in the resolved preview show a placeholder like `[auto-detect]` or the literal string "auto-detect"? | Open | — |
| 2 | Should there be a visual indicator (e.g., icon or badge) showing which dropdowns were auto-defaulted vs. deliverable-defaulted? | Open | — |
| 3 | If a deliverable file is deleted between modal open and execute, should re-validation occur at execute time? | Open | — |
