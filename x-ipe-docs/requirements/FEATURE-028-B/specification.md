# Feature Specification: CLI Language Selection & Instructions

> Feature ID: FEATURE-028-B
> Version: v1.0
> Status: Refined
> Last Updated: 02-11-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.1 | 02-11-2026 | CR-001: Separate bilingual template into two files (`copilot-instructions-en.md`, `copilot-instructions-zh.md`) instead of single file with language markers |
| v1.0 | 02-11-2026 | Initial specification |

## Overview

FEATURE-028-B adds language selection to the `x-ipe init` and `x-ipe upgrade` CLI commands, creates a bilingual copilot-instructions.md template with language markers, and implements extraction logic to copy only the selected language section into the project.

The bilingual template uses custom text markers `---LANG:en---` / `---LANG:zh---` to delimit language-specific sections. During init, only the selected language part is extracted and written to the project. The Chinese section includes skill routing keyword examples so that agents can match Chinese user requests to the correct task-based skills — without modifying any SKILL.md files.

## User Stories

1. **As a** Chinese-speaking developer, **I want** to select Chinese during `x-ipe init`, **so that** my copilot instructions are in Chinese and my AI agent understands Chinese commands.
2. **As an** existing user, **I want** to switch language via `x-ipe upgrade --lang`, **so that** I can change my instructions language without re-initializing the project.
3. **As a** non-interactive CI/CD pipeline operator, **I want** to specify `--lang en` or `--lang zh` directly, **so that** language selection doesn't block automation.
4. **As a** package maintainer, **I want** a single bilingual template file, **so that** I maintain one source of truth for both EN and ZH instructions.

## Acceptance Criteria

### AC Group 1: Init Language Selection

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-B.1 | `x-ipe init` MUST prompt for language selection after CLI detection, presenting choices: English (default), 中文 | Must |
| AC-028-B.2 | `x-ipe init --lang en` MUST skip the interactive language prompt and select English | Must |
| AC-028-B.3 | `x-ipe init --lang zh` MUST skip the interactive language prompt and select Chinese | Must |
| AC-028-B.4 | Invalid `--lang` values MUST produce a clear error message listing valid options | Must |
| AC-028-B.5 | Selected language MUST be stored in `.x-ipe.yaml` under `language` key (e.g., `language: zh`) | Must |

### AC Group 2: Bilingual Instructions Template

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-B.6 | Package MUST ship a single bilingual copilot-instructions.md template containing both EN and ZH sections | Must |
| AC-028-B.7 | EN section MUST be delimited by `---LANG:en---` marker at the start | Must |
| AC-028-B.8 | ZH section MUST be delimited by `---LANG:zh---` marker at the start | Must |
| AC-028-B.9 | ZH section MUST include Chinese keyword examples for skill routing (e.g., "优化创意" → ideation, "修复缺陷" → bug fix) | Must |
| AC-028-B.10 | ZH section MUST be functionally equivalent to the EN section (same structure, same skill references) | Must |
| AC-028-B.11 | ZH section instructions MUST be written in natural, idiomatic Chinese | Must |

### AC Group 3: Language Extraction Logic

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-B.12 | Init MUST extract only the content between the selected language marker and the next marker (or EOF) | Must |
| AC-028-B.13 | Extracted content MUST NOT include the `---LANG:xx---` marker line itself | Must |
| AC-028-B.14 | Existing merge behavior MUST be preserved: if copilot-instructions.md exists, append X-IPE section | Must |
| AC-028-B.15 | Extraction logic MUST be a reusable utility function (not inline in init command) | Should |

### AC Group 4: Upgrade --lang

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-B.16 | `x-ipe upgrade --lang` MUST present interactive language prompt (same as init) | Must |
| AC-028-B.17 | `x-ipe upgrade --lang zh` MUST accept inline value and skip interactive prompt | Must |
| AC-028-B.18 | `x-ipe upgrade --lang` MUST update `language` key in `.x-ipe.yaml` | Must |
| AC-028-B.19 | `x-ipe upgrade --lang` MUST re-extract and overwrite the copilot-instructions.md X-IPE section with the new language | Must |
| AC-028-B.20 | `x-ipe upgrade --lang` MUST also re-scaffold copilot-prompt.json v3.0 template (unchanged — language filtering is client-side) | Should |

### AC Group 5: Backward Compatibility

| AC ID | Acceptance Criteria | Priority |
|-------|---------------------|----------|
| AC-028-B.21 | Existing projects without `language` key in `.x-ipe.yaml` MUST default to `"en"` | Must |
| AC-028-B.22 | `x-ipe upgrade` (without `--lang`) MUST NOT change the existing language setting | Must |
| AC-028-B.23 | `x-ipe init` without `--lang` flag MUST still work interactively (prompt user) | Must |

## Functional Requirements

| FR ID | Requirement |
|-------|-------------|
| FR-1 | The system MUST provide a bilingual copilot-instructions.md template in `src/x_ipe/resources/` |
| FR-2 | The system MUST provide `extract_language_section(template: str, language: str) -> str` utility |
| FR-3 | The init command MUST add `--lang` option accepting `en` or `zh` |
| FR-4 | The upgrade command MUST add `--lang` option accepting `en` or `zh` or no value (interactive) |
| FR-5 | The `create_config_file()` method in ScaffoldManager MUST accept and store `language` parameter |
| FR-6 | The `copy_copilot_instructions()` method MUST use language extraction when the bilingual template is detected |

## Non-Functional Requirements

| NFR ID | Requirement | Priority |
|--------|-------------|----------|
| NFR-1 | Language extraction MUST handle edge cases (missing marker, single-language template) gracefully | Must |
| NFR-2 | Chinese instructions MUST cover all skill routing keywords documented in EN version | Must |
| NFR-3 | CLI prompts MUST use `rich` library consistent with existing CLI styling | Should |
| NFR-4 | Language extraction logic MUST be unit-testable (pure function, no file I/O) | Must |

## Dependencies

### Internal Dependencies

| Dependency | Reason |
|------------|--------|
| FEATURE-028-A | v3.0 copilot-prompt.json template must exist for init to scaffold it |

### External Dependencies

| Dependency | Reason |
|------------|--------|
| `click` library | CLI option/argument framework (already in use) |
| `rich` library | Interactive prompts and styling (already in use) |

## Business Rules

| BR ID | Rule |
|-------|------|
| BR-1 | Default language is always English when not specified |
| BR-2 | `upgrade --lang` overwrites instructions (like init), no merge attempt |
| BR-3 | Language key in `.x-ipe.yaml` is the single source of truth for project language |
| BR-4 | Skills MUST NOT be modified — Chinese keyword mappings live only in the ZH instructions |
| BR-5 | The ZH instructions section MUST map all task-based skill trigger keywords to Chinese equivalents |

## Edge Cases & Constraints

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| EC-1 | `--lang xyz` (invalid language) | Error: "Invalid language 'xyz'. Supported: en, zh" |
| EC-2 | Template file has no `---LANG:xx---` markers (old format) | Treat entire file as EN content, copy as-is |
| EC-3 | `.x-ipe.yaml` doesn't exist during upgrade | Error: "Project not initialized. Run `x-ipe init` first." |
| EC-4 | User has manually edited copilot-instructions.md | `upgrade --lang` overwrites the X-IPE section (by design, per user decision) |
| EC-5 | Non-copilot CLI (opencode/claude-code) | Language extraction applies to their instruction files too |
| EC-6 | Template has only EN marker, no ZH | Extract EN section, warn that ZH is not available |

## Out of Scope

- Frontend language switching (FEATURE-028-C)
- copilot-prompt.json schema changes (FEATURE-028-A)
- Additional languages beyond EN/ZH
- Full UI internationalization
- Translation of SKILL.md files

## Technical Considerations

- Init flow currently: CLI detection → scaffold → copy instructions → create config. Language selection inserts after CLI detection
- `copy_copilot_instructions()` in scaffold.py (line ~161) needs modification to accept language parameter
- `create_config_file()` in scaffold.py (line ~402) needs to write `language` key
- `_handle_cli_migration()` in main.py (line ~324) may need language awareness
- ZH instructions content must be authored by hand (not machine-translated) for quality

## Open Questions

- None (all clarifications resolved during ideation and requirement gathering)
