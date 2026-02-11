# Feature Specification: Frontend Prompt Language Filtering

> Feature ID: FEATURE-028-C
> Version: v1.0
> Status: Refined
> Last Updated: 02-11-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-11-2026 | Initial specification |

## Overview

FEATURE-028-C adds client-side language filtering to the frontend so that prompt buttons display only the label and command matching the user's configured language. The API serves the full bilingual v3.0 copilot-prompt.json unchanged; JavaScript filters `prompt-details` by language and falls back gracefully to English when a translation is missing.

The language value is read from the existing `/api/config` endpoint (which serves `.x-ipe.yaml` content). The web UI itself remains English-only — only prompt labels and commands are language-aware.

## User Stories

1. **As a** Chinese-speaking developer, **I want** prompt buttons to show Chinese labels and send Chinese commands, **so that** my AI agent receives instructions in my language.
2. **As a** user with an older v2.0 config, **I want** prompts to still display correctly, **so that** I'm not blocked by the schema upgrade.
3. **As a** developer, **I want** the language filtering to happen client-side, **so that** the API stays simple and stateless.

## Acceptance Criteria

### AC Group 1: Language-Aware Prompt Display

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-C.1 | Frontend MUST read the `language` value from the `/api/config` response | Must |
| AC-028-C.2 | When rendering prompt buttons, frontend MUST select `label` from the `prompt-details` entry matching the configured language | Must |
| AC-028-C.3 | When executing a prompt, frontend MUST use the `command` from the `prompt-details` entry matching the configured language | Must |
| AC-028-C.4 | Prompt `id` and `icon` MUST continue to be read from the top-level prompt object (not from prompt-details) | Must |

### AC Group 2: Fallback Chain

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-C.5 | If `prompt-details` has no entry for the configured language, frontend MUST fall back to the `"en"` entry | Must |
| AC-028-C.6 | If `prompt-details` has no `"en"` entry either, frontend MUST fall back to `prompt.label` and `prompt.command` (v2.0 compat) | Must |
| AC-028-C.7 | If neither `prompt-details` nor top-level `label`/`command` exist, the prompt MUST be skipped (not rendered) | Should |

### AC Group 3: v2.0 Backward Compatibility

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-C.8 | v2.0 prompts (with top-level `label`/`command`, no `prompt-details`) MUST display correctly | Must |
| AC-028-C.9 | The `_loadCopilotPrompts()` function MUST handle both v2.0 and v3.0 prompt formats | Must |

### AC Group 4: API Language Field

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-C.10 | The `/api/config` response MUST include the `language` field from `.x-ipe.yaml` | Must |
| AC-028-C.11 | If `language` is not set in `.x-ipe.yaml`, the API MUST default to `"en"` | Must |

## Functional Requirements

| FR ID | Requirement |
|-------|-------------|
| FR-1 | The frontend MUST implement a `resolvePromptDetails(prompt, language)` helper that extracts `{label, command}` from a prompt object for a given language |
| FR-2 | The helper MUST implement the fallback chain: prompt-details[lang] → prompt-details["en"] → top-level label/command |
| FR-3 | `_loadCopilotPrompts()` MUST fetch language from `/api/config` (or cache from existing config fetch) |
| FR-4 | `_renderCopilotButton()` MUST use resolved label for display |
| FR-5 | `_handleCopilotPromptClick()` MUST use resolved command for execution |

## Non-Functional Requirements

| NFR ID | Requirement | Priority |
|--------|-------------|----------|
| NFR-1 | Language resolution MUST add zero additional API calls (reuse existing `/api/config` response) | Must |
| NFR-2 | Prompt rendering performance MUST not degrade (O(n) where n = number of prompts) | Must |
| NFR-3 | Frontend code MUST follow existing project JavaScript patterns (no framework changes) | Must |

## Dependencies

### Internal Dependencies

| Dependency | Reason |
|------------|--------|
| FEATURE-028-A | v3.0 schema with `prompt-details` array must be defined |
| FEATURE-028-B | Language stored in `.x-ipe.yaml`, served via `/api/config` |

### External Dependencies

| Dependency | Reason |
|------------|--------|
| None | Pure JavaScript, no new libraries |

## Business Rules

| BR ID | Rule |
|-------|------|
| BR-1 | Web UI chrome (menus, headers, navigation) stays English-only — only prompt labels/commands are language-aware |
| BR-2 | Language fallback MUST always produce a displayable prompt (never show undefined or empty) |
| BR-3 | Placeholder tokens in commands (e.g., `<current-idea-file>`) MUST be replaced regardless of language |

## Edge Cases & Constraints

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| EC-1 | v2.0 JSON with no `prompt-details` at all | Use top-level `label`/`command` directly (existing behavior) |
| EC-2 | v3.0 JSON but only `"en"` entries (no ZH) | Display EN content for ZH users (fallback) |
| EC-3 | Mixed v2.0/v3.0 prompts in same file | Handle each prompt independently |
| EC-4 | `/api/config` returns no `language` field | Default to `"en"` |
| EC-5 | `prompt-details` is empty array | Skip prompt (don't render) |
| EC-6 | `evaluate` singleton (no `id` field in v2.0) | Handle with or without `id` |

## Out of Scope

- Server-side language filtering (by design, filtering is client-side)
- Web UI internationalization (menus, navigation stay English)
- copilot-prompt.json schema changes (FEATURE-028-A)
- CLI commands (FEATURE-028-B)
- Evaluation section UI (follows same pattern as ideation prompts)

## Technical Considerations

- `workplace.js` line ~48-60: `_loadCopilotPrompts()` currently reads `data.ideation?.prompts || data.prompts`
- `workplace.js` line ~1174-1194: `_renderCopilotButton()` reads `prompt.label` and `prompt.icon` directly
- `workplace.js` line ~1234-1250: `_handleCopilotPromptClick()` reads `prompt.command`
- Language value already available via `/api/config` (settings_routes.py line ~103-143)
- `resolvePromptDetails()` helper could be added as a method on the Workplace class or as a standalone utility

## Open Questions

- None (all clarifications resolved during ideation and requirement gathering)
