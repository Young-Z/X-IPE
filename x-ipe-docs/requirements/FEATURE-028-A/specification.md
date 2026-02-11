# Feature Specification: Bilingual Prompt Schema & Migration

> Feature ID: FEATURE-028-A
> Version: v1.0
> Status: Refined
> Last Updated: 02-11-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-11-2026 | Initial specification |

## Overview

FEATURE-028-A defines the copilot-prompt.json v3.0 schema that supports bilingual (EN/ZH) prompts via a `prompt-details` array on each prompt entry, and provides a v2.0→v3.0 migration utility for existing projects.

The v3.0 schema replaces the top-level `label` and `command` fields with a `prompt-details` array where each entry specifies `{ language, label, command }`. This allows the same prompt to carry translations for multiple languages. The migration utility wraps existing v2.0 `label`/`command` into the English entry and adds corresponding Chinese translations.

This is the **foundation feature** for the Prompt Bi-language Support initiative — FEATURE-028-B (CLI) and FEATURE-028-C (Frontend) both consume the v3.0 schema defined here.

## User Stories

1. **As a** package maintainer, **I want** copilot-prompt.json to carry both EN and ZH prompt content in a single file, **so that** I don't need to maintain separate prompt files per language.
2. **As an** existing X-IPE user upgrading, **I want** my copilot-prompt.json to auto-migrate to v3.0 format, **so that** I get bilingual prompts without manual editing.
3. **As a** developer consuming the prompt config, **I want** backward compatibility with v2.0 format, **so that** old configs still work without errors.

## Acceptance Criteria

### AC Group 1: v3.0 Schema Definition

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-A.1 | copilot-prompt.json template MUST set `"version": "3.0"` | Must |
| AC-028-A.2 | Each prompt in `ideation.prompts[]` array MUST have a `prompt-details` array with objects containing `{ language, label, command }` | Must |
| AC-028-A.3 | Each prompt in `evaluation.refactoring[]` array MUST have a `prompt-details` array with objects containing `{ language, label, command }` | Must |
| AC-028-A.4 | The singleton `evaluation.evaluate` object MUST have a `prompt-details` array with objects containing `{ language, label, command }` | Must |
| AC-028-A.5 | The `label` field MUST NOT exist at the prompt level — only inside `prompt-details` entries | Must |
| AC-028-A.6 | Each prompt MUST have `prompt-details` entries for both `"en"` and `"zh"` languages | Must |
| AC-028-A.7 | Top-level `id` and `icon` fields MUST remain at the prompt level (language-neutral) | Must |
| AC-028-A.8 | The `placeholder` section MUST remain unchanged (language-neutral) | Must |

### AC Group 2: Chinese Prompt Content

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-A.9 | All `ideation.prompts[]` entries MUST have accurate Chinese `label` and `command` translations | Must |
| AC-028-A.10 | All `evaluation.refactoring[]` entries MUST have accurate Chinese `label` and `command` translations | Must |
| AC-028-A.11 | The `evaluation.evaluate` singleton MUST have accurate Chinese `label` and `command` translation | Must |
| AC-028-A.12 | Chinese `command` text MUST preserve all `<placeholder>` tokens exactly (e.g., `<current-idea-file>`, `<evaluation-file>`) | Must |

### AC Group 3: v2.0→v3.0 Migration

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-A.13 | A migration utility function MUST exist that converts v2.0 JSON to v3.0 format | Must |
| AC-028-A.14 | Migration MUST wrap existing v2.0 `label`/`command` into `prompt-details[{language:"en", label:..., command:...}]` | Must |
| AC-028-A.15 | Migration MUST add a `{language:"zh", label:..., command:...}` entry with Chinese translations for each prompt | Must |
| AC-028-A.16 | Migration MUST remove top-level `label` and `command` fields from each prompt after wrapping into `prompt-details` | Must |
| AC-028-A.17 | Migration MUST update `"version"` from `"2.0"` to `"3.0"` | Must |
| AC-028-A.18 | Migration MUST be idempotent — running on an already-migrated v3.0 file MUST produce the same output | Must |
| AC-028-A.19 | Migration MUST preserve any user-added custom prompts (wrap them as EN-only if no ZH translation available) | Must |
| AC-028-A.20 | Migration MUST preserve the `placeholder` section unchanged | Must |

### AC Group 4: Backward Compatibility

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-A.21 | Existing v2.0 copilot-prompt.json (without `prompt-details`) MUST continue to be readable by the API without errors | Must |
| AC-028-A.22 | Consumers reading prompts MUST handle both v2.0 (top-level `label`/`command`) and v3.0 (`prompt-details`) formats | Must |

## Functional Requirements

| FR ID | Requirement |
|-------|-------------|
| FR-1 | The system MUST provide a v3.0 copilot-prompt.json template file in the package resources |
| FR-2 | The system MUST provide a `migrate_prompt_config(data: dict) -> dict` utility that converts v2.0 format to v3.0 |
| FR-3 | The migration utility MUST detect the current version and skip migration if already v3.0 |
| FR-4 | The migration utility MUST handle all prompt structures: `prompts[]` arrays, singleton objects, and `refactoring[]` arrays |
| FR-5 | The v3.0 template MUST include Chinese translations for all existing prompts |

## Non-Functional Requirements

| NFR ID | Requirement | Priority |
|--------|-------------|----------|
| NFR-1 | Migration MUST be idempotent (running twice = same result) | Must |
| NFR-2 | Migration MUST complete in under 100ms for typical config files | Should |
| NFR-3 | Migration code MUST follow existing project patterns (service layer, tracing) | Must |
| NFR-4 | JSON output MUST be pretty-printed with 2-space indentation (matching existing format) | Should |

## Dependencies

### Internal Dependencies

| Dependency | Reason |
|------------|--------|
| None | This is the foundation feature — no upstream dependencies |

### External Dependencies

| Dependency | Reason |
|------------|--------|
| None | Pure JSON schema definition and transformation |

### Downstream Consumers

| Feature | How it uses 028-A |
|---------|-------------------|
| FEATURE-028-B | CLI init scaffolds the v3.0 template; CLI upgrade calls migration utility |
| FEATURE-028-C | Frontend reads `prompt-details` array from v3.0 JSON |

## Business Rules

| BR ID | Rule |
|-------|------|
| BR-1 | Chinese translations MUST be natural and idiomatic, not literal machine translations |
| BR-2 | Placeholder tokens (`<current-idea-file>`, `<evaluation-file>`) MUST appear in both EN and ZH commands verbatim |
| BR-3 | If a user-added custom prompt has no ZH translation, migration MUST wrap it as EN-only (single prompt-details entry) |
| BR-4 | The `id` field is the canonical prompt identifier — it MUST remain unchanged across schema versions |

## Edge Cases & Constraints

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| EC-1 | v2.0 file with user-added custom prompts | Migrate: wrap as EN-only entry in prompt-details |
| EC-2 | v2.0 file with prompts user has deleted | Preserve deletions — only migrate what exists |
| EC-3 | v3.0 file passed to migration | No-op — return unchanged |
| EC-4 | v1.0 file (legacy, `data.prompts` format) | Migration handles v1.0→v3.0 if encountered |
| EC-5 | Malformed JSON | Migration raises clear error, does not silently corrupt |
| EC-6 | `evaluate` singleton missing `id` field | Migration adds `id: "evaluate"` during conversion |
| EC-7 | Empty prompts array | Migration produces empty `prompts[]` with version bump |

## Out of Scope

- CLI init/upgrade integration (FEATURE-028-B)
- Frontend display logic (FEATURE-028-C)
- Language selection UX (FEATURE-028-B)
- copilot-instructions.md bilingual template (FEATURE-028-B)
- Additional languages beyond EN/ZH

## Technical Considerations

- Migration utility should be a pure function (`dict → dict`) for easy testing
- The v3.0 template file replaces the existing v2.0 template at `src/x_ipe/resources/config/copilot-prompt.json`
- The project-level config at `x-ipe-docs/config/copilot-prompt.json` may have user customizations — migration must handle this
- Consider placing migration logic in a service (e.g., `prompt_config_service.py`) or utility module

## Open Questions

- None (all clarifications resolved during ideation and requirement gathering)
