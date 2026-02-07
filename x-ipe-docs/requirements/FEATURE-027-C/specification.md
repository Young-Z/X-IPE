# Feature Specification: Skill & Instruction Translation

> Feature ID: FEATURE-027-C  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-07-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-07-2026 | Initial specification |

## Linked Mockups

N/A — This is a backend/CLI infrastructure feature with no UI.

## Overview

FEATURE-027-C introduces the **Skill & Instruction Translation Engine** — a service that translates X-IPE's canonical skill format (`.github/skills/<name>/SKILL.md`) and project instructions into each supported CLI's native format during `x-ipe init` and `x-ipe upgrade`. Currently, X-IPE skills are authored exclusively for GitHub Copilot CLI, which natively reads `.github/skills/`. Other CLIs (OpenCode, Claude Code) have their own skill folder locations, frontmatter conventions, and instruction file formats.

This feature creates a `SkillTranslator` service with per-adapter translation strategies. For Copilot, translation is a no-op since `.github/skills/` is already the native format. For OpenCode, skills are copied to `.opencode/skills/` with frontmatter filtered to only recognized fields (`name`, `description`), and an `AGENTS.md` instruction file is generated at the project root. For Claude Code, skills are copied to `.claude/skills/` with frontmatter preserved (Claude Code ignores unknown fields), and a `CLAUDE.md` instruction file is generated at the project root.

**Target users:** The `x-ipe init` and `x-ipe upgrade` commands (which invoke translation during CLI artifact deployment), and X-IPE developers who need to extend translation strategies for future CLIs.

## User Stories

| ID | User Story | Priority |
|----|-----------|----------|
| US-027-C.1 | As an X-IPE developer using OpenCode, I want my canonical skills automatically translated to `.opencode/skills/` with valid frontmatter, so that OpenCode discovers and loads them correctly | Must |
| US-027-C.2 | As an X-IPE developer using Claude Code, I want my canonical skills automatically translated to `.claude/skills/` with compatible frontmatter, so that Claude Code discovers and loads them correctly | Must |
| US-027-C.3 | As an X-IPE developer using Copilot, I want skill translation to be a no-op, so that my existing `.github/skills/` structure is preserved without duplication | Must |
| US-027-C.4 | As an X-IPE developer, I want an `AGENTS.md` file generated for OpenCode from a canonical instruction template, so that OpenCode has project-level instructions | Must |
| US-027-C.5 | As an X-IPE developer, I want a `CLAUDE.md` file generated for Claude Code from a canonical instruction template, so that Claude Code has project-level instructions | Must |
| US-027-C.6 | As an X-IPE developer, I want skill translation to be idempotent, so that running init/upgrade multiple times produces the same result | Must |
| US-027-C.7 | As an X-IPE developer, I want translation failures for individual skills to be logged and skipped without aborting the entire translation, so that partial deployments still work | Should |

## Acceptance Criteria

**1. Service Structure**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-1.1 | A `SkillTranslator` service MUST exist at `src/x_ipe/services/skill_translator.py` | File exists at specified path and is importable |
| AC-1.2 | `SkillTranslator` MUST accept a `CLIAdapterData` instance to determine translation strategy | Constructor or method accepts adapter; different adapters produce different outputs |
| AC-1.3 | `SkillTranslator` MUST provide a `translate_skills(source_dir, target_dir)` method that copies and transforms all skills | Call method, verify skills appear in target_dir |
| AC-1.4 | `SkillTranslator` MUST provide a `generate_instructions(template_path, target_path)` method that creates the CLI-specific instruction file | Call method, verify instruction file created at target_path |

**2. Copilot Translation (No-Op)**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-2.1 | When active adapter is `copilot`, `translate_skills()` MUST be a no-op (no files copied or modified) | Call translate_skills with copilot adapter, verify no files written |
| AC-2.2 | When active adapter is `copilot`, `generate_instructions()` MUST be a no-op (`.github/copilot-instructions.md` is already native) | Call generate_instructions with copilot adapter, verify no files written |

**3. OpenCode Translation**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-3.1 | Skills MUST be copied to `.opencode/skills/<name>/SKILL.md` | Translate skills, verify files exist under `.opencode/skills/` |
| AC-3.2 | Skill frontmatter MUST be filtered to only `name` and `description` fields (drop all other fields) | Parse translated SKILL.md, verify only `name` and `description` in frontmatter |
| AC-3.3 | Skill body content (markdown after frontmatter) MUST be preserved exactly | Compare body content before and after translation, verify identical |
| AC-3.4 | An `AGENTS.md` file MUST be generated at the project root from the canonical instructions template | Verify AGENTS.md exists at project root with expected content |
| AC-3.5 | Skill subdirectories (e.g., `templates/`, `references/`) MUST be copied alongside SKILL.md | Create skill with subdirectories, translate, verify subdirs present |

**4. Claude Code Translation**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-4.1 | Skills MUST be copied to `.claude/skills/<name>/SKILL.md` | Translate skills, verify files exist under `.claude/skills/` |
| AC-4.2 | Skill frontmatter MUST be preserved as-is (Claude Code ignores unknown fields) | Parse translated SKILL.md, verify frontmatter matches source |
| AC-4.3 | Skill body content (markdown after frontmatter) MUST be preserved exactly | Compare body content before and after translation, verify identical |
| AC-4.4 | A `CLAUDE.md` file MUST be generated at the project root from the canonical instructions template | Verify CLAUDE.md exists at project root with expected content |
| AC-4.5 | Skill subdirectories (e.g., `templates/`, `references/`) MUST be copied alongside SKILL.md | Create skill with subdirectories, translate, verify subdirs present |

**5. Translation Behavior**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-5.1 | All skills MUST be copied to the target CLI regardless of CLI-specific applicability (no filtering by content) | Translate all skills, verify count matches source |
| AC-5.2 | Translation MUST be idempotent — running it twice produces the same output | Run translate_skills twice, compare output directories, verify identical |
| AC-5.3 | If a single skill translation fails, the system MUST log a warning and continue with remaining skills | Force failure on one skill, verify others still translated and warning logged |
| AC-5.4 | The canonical skill source (`.github/skills/`) MUST never be modified during translation | Snapshot source dir before translation, verify unchanged after |

**6. Frontmatter Processing**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-6.1 | Frontmatter parsing MUST handle skills with no frontmatter (treat as body-only) | Translate skill without frontmatter, verify body preserved |
| AC-6.2 | Frontmatter parsing MUST handle skills with empty frontmatter (`---\n---`) | Translate skill with empty frontmatter, verify no crash |
| AC-6.3 | Frontmatter parsing MUST handle multi-line YAML values in frontmatter | Translate skill with multi-line description, verify parsed correctly |
| AC-6.4 | The `name` field in OpenCode frontmatter MUST match the skill directory name | Translate skill `my-skill/SKILL.md`, verify frontmatter `name: my-skill` |

## Functional Requirements

| # | Requirement | Input | Process | Output |
|---|-------------|-------|---------|--------|
| FR-1 | Translate all skills from canonical source to CLI-specific target | Source dir (`.github/skills/`), target dir from adapter's `skills_folder`, adapter config | For each skill: parse frontmatter → apply adapter-specific transformation → write to target dir with subdirs | Translated skills in target directory |
| FR-2 | Filter OpenCode frontmatter | SKILL.md with arbitrary frontmatter | Extract only `name` and `description`; if `name` missing, derive from directory name; discard other fields | SKILL.md with filtered frontmatter + preserved body |
| FR-3 | Preserve Claude Code frontmatter | SKILL.md with arbitrary frontmatter | Copy frontmatter as-is (Claude Code ignores unknown fields) | SKILL.md with identical frontmatter + preserved body |
| FR-4 | Generate CLI-specific instruction file | Canonical instruction template, adapter's `instructions_file` path | Read template → write to adapter-specified location (e.g., `AGENTS.md` for OpenCode, `CLAUDE.md` for Claude Code) | Instruction file at target path |
| FR-5 | Copy skill subdirectories | Skill directory containing templates/, references/, etc. | Recursively copy all non-SKILL.md files and subdirectories | Complete skill directory structure in target |
| FR-6 | Determine translation strategy from adapter | `CLIAdapterData` with `skills_folder` and `instructions_file` fields | Check adapter name → select strategy (no-op for copilot, filter for opencode, preserve for claude-code) | Translation strategy function |

## Non-Functional Requirements

| # | Requirement | Metric | Priority |
|---|-------------|--------|----------|
| NFR-1 | Translation MUST be idempotent — running it multiple times on the same source produces the same output | Byte-identical output on repeated runs | Must |
| NFR-2 | Adding a new translation strategy for a future CLI MUST require only adding a new strategy function (no changes to core translation loop) | New CLI works by adding strategy + adapter YAML entry | Should |
| NFR-3 | All new code MUST follow existing project patterns (service layer, `@x_ipe_tracing` decorators) | Code review against `cli_adapter_service.py` pattern | Must |
| NFR-4 | Service MUST be importable and usable without Flask context (for CLI commands) | Import and call from non-Flask script succeeds | Must |
| NFR-5 | Translation of a typical project (~40 skills) MUST complete within 10 seconds | Time `translate_skills()` < 10s for 40 skills | Should |

## Dependencies

### Internal Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-027-A | Hard | Uses `CLIAdapterData` to determine target paths (`skills_folder`, `instructions_file`) and translation strategy |
| FEATURE-018 | Soft | CLI Tool provides the `x-ipe` command infrastructure; init/upgrade will invoke `SkillTranslator` |

### External Dependencies

| Dependency | Description |
|-----------|-------------|
| PyYAML | Already in project dependencies — used for frontmatter parsing |
| `shutil` / `pathlib` | Standard library — used for directory copying and path manipulation |

## Business Rules

| # | Rule |
|---|------|
| BR-1 | The canonical skill format (`.github/skills/`) is the single source of truth; translated copies are derived artifacts |
| BR-2 | All skills are translated to the target CLI regardless of content — no per-skill filtering or skip logic |
| BR-3 | Copilot translation is always a no-op since `.github/skills/` is already the native Copilot format |
| BR-4 | OpenCode frontmatter MUST only contain `name` and `description` — other fields are silently dropped per OpenCode documentation |
| BR-5 | Claude Code frontmatter is passed through unchanged — Claude Code ignores unknown fields per its documentation |
| BR-6 | The `name` field for OpenCode MUST be lowercase alphanumeric with single hyphen separators (matching the directory name) |
| BR-7 | Instruction file generation uses a canonical template — the template content is the same for all CLIs, only the filename and location differ |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|------------------|
| Skill has no frontmatter (body only) | Copy body as-is; for OpenCode, generate minimal frontmatter from directory name |
| Skill has empty frontmatter (`---\n---`) | Treat as no frontmatter; for OpenCode, generate minimal frontmatter from directory name |
| Skill directory name has uppercase or special chars | For OpenCode, derive a valid `name` by lowercasing and replacing invalid chars with hyphens |
| Target skills directory already exists | Overwrite existing files (idempotent behavior) |
| Source skills directory does not exist | Log warning, return empty result (no crash) |
| Source skills directory is empty | No-op, return empty result |
| Skill SKILL.md has malformed YAML frontmatter | Log warning for that skill, skip it, continue with remaining skills |
| Skill has nested subdirectories (e.g., `templates/subdir/file.md`) | Recursively copy entire directory tree |
| Instruction template file does not exist | Log error, skip instruction generation (do not crash) |
| Target instruction file already exists | Overwrite with regenerated content (idempotent) |
| Skill frontmatter has multi-line YAML values | Parse correctly using YAML parser; preserve in output |
| Skill directory contains non-markdown files (e.g., `.py`, `.json`) | Copy all files regardless of extension |
| Copilot adapter selected but source is `.github/skills/` which is also the target | No-op detected; no files copied |

## Out of Scope

- Terminal UI integration (FEATURE-027 Phase 2)
- Runtime CLI mode detection (Phase 2)
- MCP configuration deployment (FEATURE-027-D — separate feature)
- `x-ipe init` / `x-ipe upgrade` command changes (FEATURE-027-B, 027-E — separate features)
- OpenCode commands mapping (deferred post-v1)
- Claude Code `.claude/rules/` translation (deferred — only `CLAUDE.md` + skills)
- Per-skill filtering based on CLI compatibility (all skills copied to all CLIs)
- Skill content rewriting (only frontmatter is transformed; body is preserved)

## Technical Considerations

- `SkillTranslator` should follow the service pattern established by `CLIAdapterService` — stateless methods, `@x_ipe_tracing` decorators, no Flask dependency
- Translation strategy selection should use the adapter name from `CLIAdapterData` to dispatch to strategy functions (strategy pattern)
- Frontmatter parsing should split on `---` delimiters and use `yaml.safe_load()` for the YAML block
- Directory copying should use `shutil.copytree()` with `dirs_exist_ok=True` for idempotent overwrites
- The canonical instructions template should be a bundled resource at `src/x_ipe/resources/templates/` with placeholder substitution for CLI-specific values
- The service must work outside Flask context since it's called by CLI commands (`x-ipe init`, `x-ipe upgrade`)

## Open Questions

None — all clarifications resolved during requirement gathering and domain research.
