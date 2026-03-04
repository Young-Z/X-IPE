# Requirement Details - Part 14

> Continued from: [requirement-details-part-13.md](x-ipe-docs/requirements/requirement-details-part-13.md)  
> Created: 02-27-2026

---

## EPIC-042: CR-Optimize Feature Implementation — Workflow Prompts & Template Resolution (Part 3)

### Project Overview

Change request to introduce a dedicated `workflow-prompts` array in `copilot-prompt.json`, replace legacy placeholders with tag-based `$output:tag$` syntax, add conditional `<>` block parsing, default context dropdowns to prior deliverables, and provide a read-only resolved instructions preview. This is Part 3 of the CR-Optimize Feature Implementation series (after EPIC-040 and EPIC-041/CR-002).

### User Request

From Feedback-20260226-232440:
1. Context input should default to files from prior action deliverables, not auto-detect. If no deliverable, fall back to auto-detect.
2. Stop using `<input-file>` / `<current-idea-file>` placeholders in workflow mode. Instead, use `$output:raw-idea$` or `$output-folder:ideas-folder$` in prompts. When context is selected, preview resolved paths in instructions text box.
3. Add a `workflow-prompts` field in copilot-prompt.json to separate workflow-mode prompt definitions from free-mode prompts.
4. Support conditional `<>` block parsing — if a `$variable$` inside `<>` resolves to N/A, skip the entire block.
5. Migrate all workflow-mode prompts into the new `workflow-prompts` structure.

### Clarifications

| Question | Answer |
|----------|--------|
| Should each workflow-prompt map 1:1 to a workflow action? | Yes — one entry per action |
| What should the preview show for resolved paths? | Full file path (e.g., `x-ipe-docs/ideas/.../idea-summary-v1.md`) |
| Should INSTRUCTIONS be read-only or editable? | Read-only preview; EXTRA INSTRUCTIONS stays editable |
| What happens to existing free-mode prompts? | Keep untouched; `workflow-prompts` is additive |
| Should `$output:tag$` map to action_context ref names? | Yes — `$output:raw-idea$` resolves via action_context ref `raw-idea` dropdown |
| Which actions get workflow-prompt entries? | All 9 with prompts today: refine_idea, design_mockup, requirement_gathering, feature_breakdown, feature_refinement, technical_design, test_generation, implementation, acceptance_testing |
| Is `<>` nesting allowed? | No — flat parsing only, no nested `<>` blocks |

### Related Features (CR Impact)

This CR extends/replaces behavior from EPIC-040 and EPIC-041:

| Existing FR | Impact | Description |
|-------------|--------|-------------|
| FR-040.6 | **Replaced** | `<input-file>` placeholder → superseded by `$output:tag$` syntax in workflow mode |
| FR-040.9 | Extended | copilot-prompt entry structure → same fields plus new `workflow-prompts` array |
| FR-040.14 | Extended | Instruction display → becomes read-only resolved preview in workflow mode |
| FR-041.3 | Extended | Prompt entry structure → `workflow-prompts` uses same schema with `$output:tag$` commands |
| FR-041.5 | **Replaced** | `<input-file>` and `<feature-id>` placeholders → replaced by `$output:tag$` and `$feature-id$` |
| FR-041.14 | Changed | Dropdown source → driven by `action_context` refs, not `input_source` entries |
| FR-041.16 | Extended | Dynamic preview updates → now resolves `$output:tag$` + evaluates `<>` conditional blocks |

### High-Level Requirements

1. **HLR-042.1: Workflow Prompts Configuration** — copilot-prompt.json MUST have a `workflow-prompts` array that separates workflow-mode prompt definitions from free-mode prompts, with 1:1 mapping to workflow actions.
2. **HLR-042.2: Tag-Based Placeholder System** — Prompt templates in `workflow-prompts` MUST use `$output:tag$` / `$output-folder:tag$` / `$feature-id$` syntax instead of legacy `<input-file>` / `<current-idea-file>` / `<feature-id>` placeholders.
3. **HLR-042.3: Conditional Block Parsing** — The template resolver MUST support `<literal text $variable$>` blocks that are skipped when any `$variable$` resolves to N/A.
4. **HLR-042.4: Deliverable-Default Context Dropdowns** — Context dropdowns MUST default to prior action deliverables when available, falling back to auto-detect only when no deliverables exist.
5. **HLR-042.5: Read-Only Instructions Preview** — The instructions text box MUST display a read-only resolved preview with `$output:tag$` replaced by actual paths, updating live on dropdown changes.
6. **HLR-042.6: Workflow Prompt Migration** — All 9 existing workflow-mode actions MUST be migrated to the `workflow-prompts` array with multi-language support (en, zh).

### Functional Requirements

#### FR-042.1–042.7: Workflow Prompts Array (HLR-042.1)

- **FR-042.1:** copilot-prompt.json MUST include a top-level `"workflow-prompts"` array field.
- **FR-042.2:** Each entry in `workflow-prompts` MUST include: `id` (string), `action` (string, maps 1:1 to workflow action key), `icon` (Bootstrap icon class), `input_source` (array of prior action names, informational only), `prompt-details` (array of language objects).
- **FR-042.3:** Each `prompt-details` entry MUST include: `language` (ISO code, e.g. "en", "zh"), `label` (display name), `command` (template string with `$output:tag$` syntax).
- **FR-042.4:** The `action` field MUST map 1:1 to a workflow action key in `workflow-template.json`. No two entries may share the same `action` value.
- **FR-042.5:** The `input_source` field is informational only — `action_context` in `workflow-template.json` remains the authoritative source for context ref definitions and candidate resolution.
- **FR-042.6:** In workflow mode, the Action Execution Modal MUST look up prompt entries from `workflow-prompts` by matching the action key.
- **FR-042.7:** In free mode, the Action Execution Modal MUST continue using existing prompt sections (`ideation.prompts`, `workflow.prompts`, `feature.prompts`) unchanged.

#### FR-042.8–042.14: Tag-Based Placeholder System (HLR-042.2)

- **FR-042.8:** Three variable types MUST be supported in prompt templates: `$output:tag-name$` (deliverable file), `$output-folder:tag-name$` (deliverable folder), `$feature-id$` (modal context).
- **FR-042.9:** `$output:tag-name$` MUST resolve by finding the `action_context` ref with matching name `tag-name` and using its dropdown's selected value.
- **FR-042.10:** `$output-folder:tag-name$` MUST resolve to the folder path from the deliverable tagged with `$output-folder:tag-name` in the backend.
- **FR-042.11:** `$feature-id$` MUST resolve to the current feature ID from the modal runtime context.
- **FR-042.12:** When a variable cannot be resolved (no deliverable exists), the preview MUST show the raw placeholder text (e.g., `$output:raw-idea$`) with a visual warning indicator.
- **FR-042.13:** All `action_context` ref names (e.g., `raw-idea`, `uiux-reference`) MUST use the `$output:` prefix in prompt templates. There is no separate syntax for non-deliverable context refs.
- **FR-042.14:** Legacy placeholders (`<input-file>`, `<current-idea-file>`, `<feature-id>`) MUST continue to work in free-mode prompts.

#### FR-042.15–042.19: Conditional Block Parsing (HLR-042.3)

- **FR-042.15:** The template resolver MUST support `<literal text $variable$>` blocks where content between `<` and `>` contains a mix of literal text and `$variable$` references.
- **FR-042.16:** If ANY `$variable$` inside a `<>` block resolves to N/A or is empty, the ENTIRE `<>` block (including all literal text) MUST be skipped.
- **FR-042.17:** If ALL `$variable$` references inside a `<>` block resolve to real values, the `<>` delimiters MUST be stripped and the content included in the output.
- **FR-042.18:** Nesting of `<>` blocks is NOT allowed. The parser MUST treat `<` and `>` as flat delimiters (first `<` pairs with first `>`).
- **FR-042.19:** After skipping a `<>` block, the resolver MUST collapse any resulting double-spaces or leading/trailing whitespace artifacts.

#### FR-042.20–042.24: Deliverable-Default Dropdowns (HLR-042.4)

- **FR-042.20:** When the Action Execution Modal opens in workflow mode, it MUST query prior action deliverables for each `action_context` ref.
- **FR-042.21:** If a deliverable exists for a context ref, the dropdown MUST default to the deliverable file path (not "auto-detect").
- **FR-042.22:** If no deliverable exists for a context ref, the dropdown MUST default to "auto-detect" as fallback.
- **FR-042.23:** The user MUST always be able to override the default dropdown selection.
- **FR-042.24:** Deliverable resolution MUST be cached per modal open — dropdown changes do NOT trigger re-fetch from backend.

#### FR-042.25–042.29: Read-Only Instructions Preview (HLR-042.5)

- **FR-042.25:** In workflow mode, the INSTRUCTIONS text box MUST be read-only, showing the fully resolved command with all `$output:tag$` variables replaced by their actual file paths.
- **FR-042.26:** The preview MUST update live when the user changes any context dropdown selection.
- **FR-042.27:** Conditional `<>` blocks MUST be evaluated in real-time in the preview.
- **FR-042.28:** The EXTRA INSTRUCTIONS text box MUST remain editable and does NOT support `$output:tag$` substitution — content is sent as-is.
- **FR-042.29:** The final command sent to the agent MUST be: `{resolved_instructions}` + newline + `{extra_instructions}` (if non-empty). EXTRA INSTRUCTIONS is appended, not embedded.

#### FR-042.30–042.33: Migration (HLR-042.6)

- **FR-042.30:** All 9 workflow actions MUST have entries in `workflow-prompts`: refine_idea, design_mockup, requirement_gathering, feature_breakdown, feature_refinement, technical_design, test_generation, implementation, acceptance_testing.
- **FR-042.31:** Each entry MUST include `prompt-details` in at least English (`en`) and Chinese (`zh`).
- **FR-042.32:** Existing free-mode prompts in `ideation.prompts`, `workflow.prompts`, and `feature.prompts` MUST remain unchanged.
- **FR-042.33:** Old workflow-mode entries that are now duplicated by `workflow-prompts` MUST be marked with a deprecation comment (not deleted) for future cleanup.

### Non-Functional Requirements

- **NFR-042.1:** Template resolution (placeholder substitution + conditional parsing) MUST complete in <50ms for any prompt template.
- **NFR-042.2:** The `<>` conditional parser MUST be frontend-only — no backend calls for template resolution.
- **NFR-042.3:** copilot-prompt.json structure MUST be backward compatible — adding `workflow-prompts` MUST NOT break any existing functionality.

### Acceptance Criteria

- **AC-042.1:** `workflow-prompts` array exists in copilot-prompt.json with all 9 action entries.
- **AC-042.2:** Opening the "Refine Idea" modal in workflow mode shows the prompt from `workflow-prompts` (not the old `ideation.prompts` entry).
- **AC-042.3:** `$output:raw-idea$` in the prompt resolves to the actual file path from the `compose_idea` deliverable.
- **AC-042.4:** Conditional block `<and uiux reference: $output:uiux-reference$>` is skipped when uiux-reference is N/A, and included with the path when available.
- **AC-042.5:** Context dropdown for `raw-idea` defaults to the compose_idea deliverable file (not "auto-detect").
- **AC-042.6:** Instructions text box is read-only and shows the fully resolved command.
- **AC-042.7:** Changing a context dropdown immediately updates the instructions preview.
- **AC-042.8:** EXTRA INSTRUCTIONS text box remains editable and its content is appended to the resolved command.
- **AC-042.9:** In free mode, all existing prompts work unchanged (backward compatibility).
- **AC-042.10:** All 9 workflow-prompt entries have English and Chinese translations.
- **AC-042.11:** Unresolved `$output:tag$` shows raw placeholder with warning style.
- **AC-042.12:** No double-spaces or whitespace artifacts after `<>` block is skipped.

### Constraints

- Backward compatibility: Free-mode prompts must work unchanged.
- `action_context` in `workflow-template.json` is the authoritative source for context ref definitions.
- Template parser is frontend-only; no backend changes for parsing.
- copilot-prompt.json changes are additive (new field, not modifying existing ones).
- `<>` blocks are flat (no nesting).

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| N/A | No mockups needed — UI changes are to existing modal |

### Open Questions

- None — all clarifications resolved during ideation.

---

## Feature List (EPIC-042)

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-042-A | EPIC-042 | Workflow Prompts Config & Basic Template Resolution | v1.0 | Add `workflow-prompts` array to copilot-prompt.json; implement `$output:tag$` / `$output-folder:tag$` / `$feature-id$` variable resolution; modal picks workflow-prompts in workflow mode | None |
| FEATURE-042-B | EPIC-042 | Conditional Block Parsing & Error Handling | v1.0 | Implement `<>` conditional block parser (skip when any $var$ is N/A, no nesting); add unresolved variable warning; preserve legacy placeholder compat in free mode | FEATURE-042-A |
| FEATURE-042-C | EPIC-042 | Deliverable-Default Dropdowns & Read-Only Preview | v1.0 | Context dropdowns default to prior deliverables (auto-detect fallback); INSTRUCTIONS becomes read-only resolved preview with live updates; command composition with EXTRA INSTRUCTIONS | FEATURE-042-A |
| FEATURE-042-D | EPIC-042 | Full Migration & i18n | v1.0 | Migrate all 9 workflow actions to `workflow-prompts` with English/Chinese translations; deprecate old entries with comments | FEATURE-042-A, FEATURE-042-B, FEATURE-042-C |

---

## Feature Details

### FEATURE-042-A: Workflow Prompts Config & Basic Template Resolution (MVP)

**Scope:** Foundation feature — introduces the `workflow-prompts` array structure and basic variable resolution.

**Functional Requirements:**
- FR-042.1–042.7: `workflow-prompts` array structure, entry schema, 1:1 action mapping, `input_source` informational, modal lookup logic
- FR-042.8–042.11: Three variable types (`$output:tag$`, `$output-folder:tag$`, `$feature-id$`), resolution via action_context ref matching

**Acceptance Criteria:**
- AC-042.1: `workflow-prompts` array exists in copilot-prompt.json with at least 1 entry (refine_idea for testing)
- AC-042.2: Opening "Refine Idea" modal in workflow mode shows prompt from `workflow-prompts`
- AC-042.3: `$output:raw-idea$` resolves to actual file path from compose_idea deliverable
- AC-042.9: In free mode, existing prompts work unchanged

**Technical Notes:**
- Add `workflow-prompts` as top-level field in copilot-prompt.json (additive, no breaking changes)
- Template resolver function: parse `$...$` tokens, look up action_context ref dropdown value
- Modal checks mode (workflow vs free) to determine prompt source

---

### FEATURE-042-B: Conditional Block Parsing & Error Handling

**Scope:** Template enhancements — conditional blocks and graceful error handling for unresolved variables.

**Functional Requirements:**
- FR-042.12–042.14: Unresolved variable warning display, `$output:` prefix convention, legacy placeholder backward compat
- FR-042.15–042.19: `<>` conditional block syntax, skip when any var is N/A, strip delimiters when all resolve, no nesting, whitespace cleanup

**Acceptance Criteria:**
- AC-042.4: Conditional block `<and uiux reference: $output:uiux-reference$>` skipped when N/A, included when available
- AC-042.11: Unresolved `$output:tag$` shows raw placeholder with warning style
- AC-042.12: No double-spaces or whitespace artifacts after `<>` block is skipped

**Technical Notes:**
- Parser uses flat `<` / `>` delimiter matching (first `<` pairs with first `>`)
- Whitespace collapsing: regex replace `\s{2,}` → single space after resolution
- Legacy `<input-file>` / `<current-idea-file>` still works in free-mode prompts

---

### FEATURE-042-C: Deliverable-Default Dropdowns & Read-Only Preview

**Scope:** UX improvements — smarter defaults and resolved preview.

**Functional Requirements:**
- FR-042.20–042.24: Default to deliverables, auto-detect fallback, user override, cached resolution
- FR-042.25–042.29: Read-only instructions, live preview updates, `<>` evaluation in real-time, EXTRA INSTRUCTIONS editable, command composition

**Acceptance Criteria:**
- AC-042.5: Context dropdown for `raw-idea` defaults to compose_idea deliverable file
- AC-042.6: Instructions text box is read-only showing fully resolved command
- AC-042.7: Changing context dropdown immediately updates preview
- AC-042.8: EXTRA INSTRUCTIONS remains editable and appended to resolved command

**Technical Notes:**
- Cache deliverable resolution results on modal open (avoid re-fetch per dropdown change)
- INSTRUCTIONS textarea: set `readonly` attribute in workflow mode
- Command composition: `resolved + "\n\n" + extra` (if extra is non-empty)

---

### FEATURE-042-D: Full Migration & i18n

**Scope:** Content migration — populate all 9 workflow-prompt entries with translations.

**Functional Requirements:**
- FR-042.30–042.33: All 9 entries, English + Chinese translations, free-mode untouched, deprecation comments

**Acceptance Criteria:**
- AC-042.10: All 9 workflow-prompt entries have English and Chinese translations
- AC-042.9 (verify): In free mode, existing prompts still work unchanged after migration

**Technical Notes:**
- 9 actions: refine_idea, design_mockup, requirement_gathering, feature_breakdown, feature_refinement, technical_design, test_generation, implementation, acceptance_testing
- Add `// DEPRECATED: superseded by workflow-prompts[action]` comments to old entries
- Chinese translations should match the style of existing Chinese prompts in copilot-prompt.json
