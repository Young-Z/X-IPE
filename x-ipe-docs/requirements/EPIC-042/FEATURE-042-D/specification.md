# Feature Specification: Full Migration & i18n

> **Feature ID:** FEATURE-042-D
> **Epic:** EPIC-042 — CR-Optimize Feature Implementation: Workflow Prompts & Template Resolution
> **Version:** v1.0
> **Status:** Refined
> **Last Updated:** 02-27-2026
> **Dependencies:** FEATURE-042-A, FEATURE-042-B, FEATURE-042-C

## Version History

| Version | Date       | Author | Changes                                            |
|---------|------------|--------|----------------------------------------------------|
| v1.0    | 2025-07-15 | Agent  | Initial specification from FR-042.30–042.33, AC-042.9–042.10 |

---

## Linked Mockups

N/A — This feature is a data-migration task that populates the `workflow-prompts` array in `copilot-prompt.json` with all 9 action entries and their bilingual translations. No new UI components or screens are introduced.

---

## Overview

### What
Populate the `workflow-prompts` array in `copilot-prompt.json` with all 9 workflow action entries, each containing English and Chinese `prompt-details`. Add `// DEPRECATED` comments to the old prompt entries that are superseded by the new `workflow-prompts` entries. Ensure that existing free-mode prompts remain completely unchanged and functional.

### Why
FEATURE-042-A introduced the `workflow-prompts` structure and template resolver, FEATURE-042-B added conditional block parsing, and FEATURE-042-C implemented deliverable-default dropdowns with a read-only preview. However, only a minimal set of entries may exist in `workflow-prompts` for testing purposes. This feature completes the migration by:
1. **Defining all 9 action prompt entries** with the new `$output:tag$` / `$feature-id$` syntax and conditional `<>` blocks where optional context exists.
2. **Providing bilingual support (en + zh)** so that language-switching works immediately for all workflow actions.
3. **Marking old entries as deprecated** to signal that they are superseded by `workflow-prompts` for workflow-mode use, while preserving them for free-mode backward compatibility.

### Who
- **Developers** using the X-IPE Engineering Workflow in workflow mode — they benefit from properly templated, language-aware prompts for all 9 actions.
- **Chinese-speaking users** — they gain first-class prompt support for all workflow actions.
- **Maintainers** — deprecation comments clarify which old entries are superseded, reducing confusion during future cleanup.

---

## User Stories

### US-042-D.1: All 9 Workflow Actions Available
**As a** developer using the Engineering Workflow in workflow mode,
**I want** every workflow action to have a corresponding `workflow-prompts` entry,
**So that** the template resolver can load and display the correct prompt for any action I execute.

### US-042-D.2: Chinese Translation for All Actions
**As a** Chinese-speaking developer,
**I want** all 9 workflow actions to include a Chinese `prompt-details` entry,
**So that** I can execute workflow actions in my preferred language without seeing English-only fallbacks.

### US-042-D.3: English Translation for All Actions
**As an** English-speaking developer,
**I want** all 9 workflow actions to include an English `prompt-details` entry,
**So that** I can read and verify the prompt template before executing an action.

### US-042-D.4: Free-Mode Prompts Unchanged
**As a** user in free mode,
**I want** the existing prompts (in `ideation.prompts`, `workflow.prompts`, `feature.prompts`) to continue working exactly as before,
**So that** the migration does not introduce any regressions.

### US-042-D.5: Deprecated Old Entries Clearly Marked
**As a** maintainer of `copilot-prompt.json`,
**I want** old workflow-mode prompt entries to carry deprecation comments,
**So that** I know which entries are superseded and should not be modified for workflow-mode use.

---

## Acceptance Criteria

### AC-042-D.1: All 9 Entries Present (AC-042.10)
**Given** the `workflow-prompts` array in `copilot-prompt.json`
**When** a developer inspects the file
**Then** exactly 9 entries exist, one for each action key: `refine_idea`, `design_mockup`, `requirement_gathering`, `feature_breakdown`, `feature_refinement`, `technical_design`, `test_generation`, `implementation`, `acceptance_testing`

### AC-042-D.2: English Translation for Each Entry (AC-042.10)
**Given** each of the 9 `workflow-prompts` entries
**When** inspecting the `prompt-details` array
**Then** each entry contains at least one object with `"language": "en"`, a non-empty `label`, and a non-empty `command` using `$output:tag$` / `$feature-id$` syntax

### AC-042-D.3: Chinese Translation for Each Entry (AC-042.10)
**Given** each of the 9 `workflow-prompts` entries
**When** inspecting the `prompt-details` array
**Then** each entry contains at least one object with `"language": "zh"`, a non-empty `label`, and a non-empty `command` using `$output:tag$` / `$feature-id$` syntax

### AC-042-D.4: Chinese Style Consistency
**Given** the Chinese `prompt-details` in `workflow-prompts`
**When** compared to the existing Chinese prompts in `ideation.prompts` and `workflow.prompts`
**Then** the style is consistent: imperative verb first, comma-separated clauses, no unnecessary English fragments, and tag variables (`$output:tag$`, `$feature-id$`) embedded inline

### AC-042-D.5: Correct Tags Per Action
**Given** the migration table mapping each action to its expected tags
**When** inspecting the `command` field in the English `prompt-details` for each entry
**Then** the tags match the specification:

| Action Key | Expected Tags |
|------------|---------------|
| `refine_idea` | `$output:raw-idea$`, `$output:uiux-reference$` |
| `design_mockup` | `$output:refined-idea$`, `$output:uiux-reference$` |
| `requirement_gathering` | `$output:refined-idea$`, `$output:mockup-html$` |
| `feature_breakdown` | `$output:requirement-doc$` |
| `feature_refinement` | `$feature-id$`, `$output:requirement-doc$` |
| `technical_design` | `$feature-id$`, `$output:specification$` |
| `test_generation` | `$feature-id$`, `$output:tech-design$` |
| `implementation` | `$feature-id$`, `$output:tech-design$`, `$output:specification$` |
| `acceptance_testing` | `$feature-id$`, `$output:specification$` |

### AC-042-D.6: Conditional Blocks for Optional Tags
**Given** entries where a tag is optional (e.g., `$output:uiux-reference$` for `refine_idea`)
**When** inspecting the `command` template
**Then** the optional tag is wrapped in a `<>` conditional block (e.g., `<and uiux reference: $output:uiux-reference$>`)

### AC-042-D.7: Free-Mode Prompts Unchanged (AC-042.9)
**Given** the existing `ideation.prompts`, `workflow.prompts`, and `feature.prompts` sections
**When** comparing the file after migration to the version before
**Then** the content of these sections is byte-identical (no modifications, only additions to the top-level `workflow-prompts` array and deprecation comments)

### AC-042-D.8: Deprecation Comments on Old Entries
**Given** each old prompt entry in `ideation.prompts`, `workflow.prompts`, and `feature.prompts` that is superseded by a `workflow-prompts` entry
**When** inspecting the entry
**Then** the entry contains a `"_deprecated"` field with value `"DEPRECATED: superseded by workflow-prompts[{action}]"` where `{action}` is the corresponding action key

### AC-042-D.9: Backward Compatibility (NFR-042.3)
**Given** the modified `copilot-prompt.json`
**When** the application loads the file
**Then** the JSON parses without error, the `version` field is incremented, and the existing sections (`ideation`, `evaluation`, `workflow`, `feature`, `placeholder`) retain their structure

### AC-042-D.10: Prompt ID Matches Existing Convention
**Given** each `workflow-prompts` entry
**When** inspecting the `id` field
**Then** the `id` uses kebab-case and matches the prompt ID used in the existing sections (e.g., `refine-idea`, `technical-design`)

### AC-042-D.11: Action Field Matches Workflow Template
**Given** each `workflow-prompts` entry
**When** inspecting the `action` field
**Then** the `action` value uses snake_case and corresponds exactly to the action key in `workflow-template.json`

---

## Functional Requirements

### FR-042.30: Populate All 9 Workflow-Prompt Entries

| Aspect | Detail |
|--------|--------|
| **Input** | The migration table (9 actions with their prompt IDs, tags, icons, and `input_source` arrays) |
| **Process** | 1. For each of the 9 actions, add an entry to the `workflow-prompts` array in `copilot-prompt.json`. 2. Each entry MUST include: `id` (kebab-case prompt ID), `action` (snake_case action key), `icon` (Bootstrap icon class), `input_source` (array of prior action names), and `prompt-details` (array of language-specific prompt objects). 3. The `prompt-details` array MUST contain at least two objects: one for `"language": "en"` and one for `"language": "zh"`. 4. The `command` field in each prompt-detail MUST use `$output:tag$` / `$output-folder:tag$` / `$feature-id$` syntax — NOT legacy `<input-file>` / `<current-idea-file>` placeholders. 5. Optional tags (where the prior deliverable may not exist) MUST be wrapped in `<>` conditional blocks. |
| **Output** | The `workflow-prompts` array contains exactly 9 entries, each with bilingual prompt-details using the new template syntax |

### FR-042.31: English Prompt Templates for All 9 Actions

| Aspect | Detail |
|--------|--------|
| **Input** | The existing English prompts from `ideation.prompts`, `workflow.prompts`, and `feature.prompts` as style reference; the migration tag table for variable substitution |
| **Process** | 1. For each action, compose an English `command` string that replaces legacy placeholders with `$output:tag$` / `$feature-id$` variables. 2. Wrap optional context in `<>` conditional blocks. 3. The command MUST end with the appropriate skill reference (e.g., "with ideation skill", "with feature refinement skill") to match the existing convention. 4. The `label` field provides a human-readable name (e.g., "Refine Idea", "Technical Design"). |
| **Output** | 9 English `prompt-details` objects, each with a `label` and `command` field using the new template syntax |

### FR-042.32: Chinese Prompt Templates for All 9 Actions

| Aspect | Detail |
|--------|--------|
| **Input** | The existing Chinese prompts in `copilot-prompt.json` (from `ideation.prompts` and `workflow.prompts`) as style reference |
| **Process** | 1. For each action, compose a Chinese `command` string that follows the existing Chinese prompt conventions: imperative verb first (e.g., 使用, 基于, 完善, 收集), comma-separated clauses, `$output:tag$` / `$feature-id$` variables embedded inline. 2. Wrap optional context in `<>` conditional blocks with Chinese literal text (e.g., `<以及UIUX参考: $output:uiux-reference$>`). 3. The `label` provides a concise Chinese name matching the existing style (e.g., "完善创意", "需求收集", "功能拆分"). 4. Where no existing Chinese prompt exists (e.g., `feature-refinement`, `technical-design`), create one following the established pattern from prompts that DO have Chinese translations. |
| **Output** | 9 Chinese `prompt-details` objects, each with a `label` and `command` field using the new template syntax and consistent Chinese style |

### FR-042.33: Deprecation Comments on Superseded Entries

| Aspect | Detail |
|--------|--------|
| **Input** | The mapping between old prompt entries and their `workflow-prompts` replacements |
| **Process** | 1. For each old prompt entry in `ideation.prompts`, `workflow.prompts`, and `feature.prompts` that has a corresponding `workflow-prompts` entry, add a `"_deprecated"` field. 2. The value MUST follow the format: `"DEPRECATED: superseded by workflow-prompts[{action_key}]"` where `{action_key}` is the snake_case action key (e.g., `refine_idea`, `design_mockup`). 3. Old entries MUST NOT be deleted — they continue to serve free-mode use and provide backward compatibility. 4. The deprecation field is a JSON key (not a code comment) because JSON does not support comments. |
| **Output** | Each superseded old entry contains a `"_deprecated"` field indicating its replacement |

---

## Non-Functional Requirements

### NFR-042.3: Backward Compatible JSON Structure
The `copilot-prompt.json` structure MUST remain backward compatible. The migration is purely additive:
- A new top-level `"workflow-prompts"` array is added (or populated if already present from FEATURE-042-A)
- Existing sections (`ideation`, `evaluation`, `workflow`, `feature`, `placeholder`) retain their structure and content
- A `"_deprecated"` field is added to superseded entries but no fields are removed
- The `version` field is incremented to reflect the migration

### NFR-042.4: JSON Validity
The resulting `copilot-prompt.json` MUST be valid JSON. Since JSON does not support comments, deprecation markers use the `"_deprecated"` JSON key convention (not `//` comments). Any reference to "deprecation comments" in requirements means this `"_deprecated"` field approach.

### NFR-042.5: Translation Quality
Chinese translations MUST:
- Use proper Chinese grammar and sentence structure
- Match the imperative, action-oriented style of existing Chinese prompts (e.g., "使用...技能", "完善...", "收集...")
- Not be literal word-for-word translations of the English commands
- Embed `$output:tag$` and `$feature-id$` variables inline without translating the variable names

---

## UI/UX Requirements

N/A — This feature is a configuration data migration. All UI behavior is provided by FEATURE-042-A (template resolver), FEATURE-042-B (conditional blocks), and FEATURE-042-C (dropdowns and preview). Once the `workflow-prompts` data is populated, the existing UI infrastructure automatically picks up the entries.

---

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-042-A | Hard (must exist) | Provides the `workflow-prompts` array structure in `copilot-prompt.json`, the `$output:tag$` / `$feature-id$` variable syntax definition, and the frontend template resolver that reads from `workflow-prompts`. Without this, added entries have no consumer. |
| FEATURE-042-B | Hard (must exist) | Provides the conditional `<>` block parser. Several prompts in this migration use `<>` blocks for optional context (e.g., `$output:uiux-reference$`). Without the parser, `<>` blocks would appear as literal text in the preview. |
| FEATURE-042-C | Hard (must exist) | Provides deliverable-default dropdowns and the read-only instructions preview. Without this, context dropdowns still default to "auto-detect" and the instructions box is not read-only, undermining the purpose of the migrated prompts. |
| `workflow-template.json` | Data (must align) | The `action` field in each `workflow-prompts` entry MUST match an action key in `workflow-template.json`. The `action_context` refs in `workflow-template.json` define what `$output:tag$` variables are valid for each action. |

---

## Business Rules

### BR-042-D.1: One Prompt Entry Per Workflow Action
Each of the 9 workflow actions has exactly one corresponding entry in `workflow-prompts`. There are no duplicate entries for the same action and no entries for actions that don't exist in `workflow-template.json`.

### BR-042-D.2: Language Fallback Order
If the user's selected language is not present in an entry's `prompt-details`, the frontend falls back to `"en"`. Therefore, English is the mandatory base language and Chinese is the first additional language. Future languages can be added without modifying existing entries.

### BR-042-D.3: Deprecation Does Not Mean Deletion
Adding `"_deprecated"` to an old entry does NOT remove it. The entry remains fully functional for free-mode use. Actual deletion is a separate future task that requires verifying no free-mode consumers depend on the entry.

### BR-042-D.4: Variable Names Are Not Translated
`$output:raw-idea$`, `$output:specification$`, `$feature-id$`, etc., appear identically in both English and Chinese commands. Only the surrounding literal text is translated.

### BR-042-D.5: Conditional Blocks Surround Optional Context Only
A tag is optional when the prior deliverable may not exist (e.g., `$output:uiux-reference$` — the user may not have created a UIUX reference). Required tags (e.g., `$output:raw-idea$` for `refine_idea`) appear outside `<>` blocks.

---

## Edge Cases & Constraints

### EC-042-D.1: Action Key Mismatch Between workflow-template and workflow-prompts
**Scenario:** A `workflow-prompts` entry has `"action": "refine-idea"` (kebab-case) instead of `"action": "refine_idea"` (snake_case as defined in `workflow-template.json`).
**Expected:** The template resolver fails to find the prompt entry for the action. The modal shows no instructions.
**Mitigation:** The `action` field MUST use the exact snake_case key from `workflow-template.json`. Validation should be added as part of integration testing.

### EC-042-D.2: Missing Chinese Translation for an Entry
**Scenario:** A `workflow-prompts` entry is added with only an English `prompt-details` object — no Chinese object.
**Expected:** When a Chinese-speaking user opens the modal, the frontend falls back to the English prompt (per BR-042-D.2). This is functional but violates the i18n requirement.
**Mitigation:** Every entry MUST include both `"language": "en"` and `"language": "zh"` objects. This should be verified as a merge-gate check.

### EC-042-D.3: Deprecation Comment Formatting Inconsistency
**Scenario:** Different old entries use different deprecation message formats (e.g., `"DEPRECATED: ..."` vs `"Deprecated — ..."` vs a boolean `true`).
**Expected:** Automated tools that scan for deprecation markers may miss some entries.
**Mitigation:** ALL deprecated entries MUST use the exact format: `"_deprecated": "DEPRECATED: superseded by workflow-prompts[{action_key}]"`. No variation.

### EC-042-D.4: Actions Without Prior Deliverables — feature_breakdown
**Scenario:** `feature_breakdown` takes `$output:requirement-doc$` which comes from `requirement_gathering`. However, there is no optional tag — the requirement doc is always expected to exist when feature_breakdown runs.
**Expected:** The `command` template for `feature_breakdown` uses `$output:requirement-doc$` outside any `<>` block (it is a required input, not optional).
**Mitigation:** Only truly optional tags are wrapped in `<>` blocks. Required inputs remain as bare `$output:tag$` references; if they are N/A, the unresolved variable warning (from FEATURE-042-B) alerts the user.

### EC-042-D.5: Prompt ID Collision
**Scenario:** A `workflow-prompts` entry uses `"id": "refine-idea"` — the same ID as the existing `ideation.prompts` entry.
**Expected:** This is intentional — the IDs match by design. The modal determines which to use based on mode (workflow vs. free). Both entries coexist without collision because they live in separate arrays (`workflow-prompts` vs `ideation.prompts`).
**Mitigation:** No mitigation needed. Document that ID overlap between `workflow-prompts` and legacy sections is expected and by design.

### EC-042-D.6: Stale input_source After Workflow Changes
**Scenario:** A future workflow-template change adds or removes actions from the pipeline. The `input_source` field in a `workflow-prompts` entry may become stale.
**Expected:** `input_source` is informational only (per idea-summary-v1.md). The authoritative source for context refs is `action_context` in `workflow-template.json`. A stale `input_source` does not break functionality but may cause incorrect default pre-population.
**Mitigation:** Document that `input_source` must be updated whenever the workflow pipeline changes.

### EC-042-D.7: test_generation — New Action Without Existing Prompt
**Scenario:** `test_generation` does not have an existing prompt entry in the current `copilot-prompt.json`. This is a net-new entry.
**Expected:** A new `workflow-prompts` entry is created. No deprecation comment is needed for an entry that doesn't exist in the old sections.
**Mitigation:** Only add `"_deprecated"` to old entries that actually exist. Do not create placeholder old entries for the purpose of deprecating them.

### EC-042-D.8: Chinese Conditional Block Literal Text
**Scenario:** An English conditional block is `<and uiux reference: $output:uiux-reference$>`. The Chinese equivalent should not be a literal translation but should follow Chinese grammar: `<以及UIUX参考: $output:uiux-reference$>`.
**Expected:** Chinese conditional blocks use Chinese literal text around the variable, maintaining natural readability when included and clean removal when skipped.
**Mitigation:** Review Chinese translations for natural phrasing within `<>` blocks.

### EC-042-D.9: Version Bump Conflict
**Scenario:** Multiple features (042-A, 042-B, 042-C, 042-D) each modify `copilot-prompt.json` and may bump the version field.
**Expected:** Each feature's implementation should increment the minor version. This feature sets the version to reflect that full migration is complete.
**Mitigation:** The version bump for this feature should be the final bump in the EPIC-042 series (e.g., from `3.2` to `4.0` to signify workflow-prompts migration complete).

### EC-042-D.10: Empty command Field
**Scenario:** A `prompt-details` object is added with an empty `"command": ""`.
**Expected:** The template resolver resolves an empty string, producing no instructions in the preview. The user sees a blank instructions box.
**Mitigation:** All `command` fields MUST be non-empty. Validation should reject empty commands.

### Constraints Summary
- All 9 entries must be present — no partial migration
- Both `en` and `zh` prompt-details are required per entry
- `action` field must exactly match `workflow-template.json` action keys (snake_case)
- `id` field must match existing prompt ID convention (kebab-case)
- Old entries are deprecated, not deleted
- JSON must remain valid (no `//` comments — use `"_deprecated"` field)

---

## Out of Scope

- **New workflow actions** — Only the 9 actions listed in the migration table are migrated. Actions like `compose_idea`, `reference_uiux`, `quality_evaluation`, and `change_request` are not part of this migration.
- **Prompt template resolver** — Implemented in FEATURE-042-A; this feature only provides the data.
- **Conditional block parser** — Implemented in FEATURE-042-B; this feature only uses `<>` syntax in command templates.
- **Dropdown defaulting logic** — Implemented in FEATURE-042-C; this feature defines `input_source` for informational purposes only.
- **Read-only preview UI** — Implemented in FEATURE-042-C.
- **Deletion of old entries** — Old entries are deprecated, not removed. Cleanup is a separate future task.
- **Additional languages beyond en/zh** — Future i18n extensions (e.g., Japanese, Korean) are out of scope.
- **Prompt content optimization** — The command wording is migrated from existing prompts with updated syntax. Rewording for better agent performance is a separate concern.
- **workflow-template.json changes** — This feature does not modify `workflow-template.json`; it only reads `action_context` definitions to ensure tag alignment.

---

## Technical Considerations

> **Note:** This section describes WHAT the system must do, not HOW it should be implemented.

### TC-042-D.1: Migration Entry Schema
Each `workflow-prompts` entry MUST conform to the schema established by FEATURE-042-A:

```json
{
  "id": "<kebab-case-prompt-id>",
  "action": "<snake_case_action_key>",
  "icon": "<bootstrap-icon-class>",
  "input_source": ["<prior_action_1>", "<prior_action_2>"],
  "prompt-details": [
    {
      "language": "en",
      "label": "<English Label>",
      "command": "<English command with $output:tag$ and <conditional blocks>>"
    },
    {
      "language": "zh",
      "label": "<Chinese Label>",
      "command": "<Chinese command with $output:tag$ and <conditional blocks>>"
    }
  ]
}
```

### TC-042-D.2: Tag-to-Action-Context Alignment
Every `$output:tag$` variable used in a `command` field MUST correspond to an `action_context` ref defined for that action in `workflow-template.json`. If a command references `$output:uiux-reference$`, then the action's `action_context` in `workflow-template.json` must include a ref named `uiux-reference`.

### TC-042-D.3: Conditional Block Usage Pattern
Optional context tags MUST be wrapped in `<>` blocks:
- `$output:uiux-reference$` in `refine_idea` and `design_mockup` — UIUX reference may not exist
- `$output:mockup-html$` in `requirement_gathering` — mockup may not have been generated
- `$output:specification$` in `implementation` — specification complements tech-design but the primary input is tech-design

Required tags appear outside `<>` blocks as bare `$output:tag$` references.

### TC-042-D.4: Deprecation Mapping
The following old entries should receive `"_deprecated"` markers:

| Old Section | Old Prompt ID | Superseded By (workflow-prompts action) |
|-------------|---------------|----------------------------------------|
| `ideation.prompts` | `refine-idea` | `refine_idea` |
| `ideation.prompts` | `design-mockup` | `design_mockup` |
| `workflow.prompts` | `requirement-gathering` | `requirement_gathering` |
| `workflow.prompts` | `feature-breakdown` | `feature_breakdown` |
| `feature.prompts` | `feature-refinement` | `feature_refinement` |
| `feature.prompts` | `technical-design` | `technical_design` |
| `feature.prompts` | `implementation` | `implementation` |
| `feature.prompts` | `acceptance-testing` | `acceptance_testing` |

Note: `test_generation` has no old entry — it is a net-new prompt entry.

### TC-042-D.5: Key Files
- `src/frontend/js/copilot-prompt.json` — Receives all 9 `workflow-prompts` entries, `"_deprecated"` fields on old entries, and a version bump
- `src/frontend/js/workflow-template.json` — Read-only reference for validating `action` keys and `action_context` ref alignment

### TC-042-D.6: Version Increment Strategy
The `version` field in `copilot-prompt.json` should be incremented to signal the complete workflow-prompts migration (e.g., from the current version to the next major or minor version appropriate for the project convention).

---

## Open Questions

None — all migration details were specified during ideation (idea-summary-v1.md §8 Migration Plan) and requirement gathering (FR-042.30–042.33, AC-042.9–042.10).
