# Requirement Details - Part 6

> Continued from: [requirement-details-part-5.md](requirement-details-part-5.md)  
> Created: 02-07-2026

---

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-027-A | CLI Adapter Registry & Service | v1.0 | Core adapter registry, service layer, API endpoint, auto-detection, and backward compatibility for multi-CLI support | FEATURE-018 |
| FEATURE-027-B | CLI Init & Selection | v1.0 | Update `x-ipe init` to auto-detect CLIs, present selection, deploy CLI-specific artifacts | FEATURE-027-A, FEATURE-019 |
| FEATURE-027-C | Skill & Instruction Translation | v1.0 | Translate canonical X-IPE skills to Copilot, OpenCode, and Claude Code native formats | FEATURE-027-A |
| FEATURE-027-D | MCP Configuration Deployment | v1.0 | Deploy MCP server config in each CLI's native format and location | FEATURE-027-A |
| FEATURE-027-E | CLI Migration & Upgrade | v1.0 | `x-ipe upgrade --cli` to switch between CLIs with non-destructive backup and redeployment | FEATURE-027-B, FEATURE-027-C, FEATURE-027-D |
| FEATURE-028-A | Bilingual Prompt Schema & Migration | v1.0 | copilot-prompt.json v3.0 schema with prompt-details array, bilingual prompt content, v2.0→v3.0 auto-migration | None |
| FEATURE-028-B | CLI Language Selection & Instructions | v1.0 | Language selection at init/upgrade, bilingual copilot-instructions.md template with ---LANG:xx--- markers, extraction logic | FEATURE-028-A |
| FEATURE-028-C | Frontend Prompt Language Filtering | v1.0 | Client-side prompt-details filtering by language, API language field, fallback chain for v2.0 compat | FEATURE-028-A, FEATURE-028-B |
| FEATURE-028-D | Settings Language Switch (Web UI) | v1.0 | Language dropdown in Settings page with confirmation dialog, AJAX switch via POST /api/config/language, reuses ScaffoldManager logic | FEATURE-028-B |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| N/A | FEATURE-027 | No UI mockup (backend/CLI feature) |

---

## Feature Details (Continued)

### Multi-CLI Adapter Support Overview

**Source:** [Idea Summary v1](../ideas/013.%20Feature-Adding%20Support%20to%20OpenCode%20CLI/idea-summary-v1.md)

#### Problem Statement

X-IPE is currently tightly coupled to GitHub Copilot CLI:
1. Terminal integration (`terminal.js`) hardcodes `copilot --allow-all-tools ...` command construction
2. Skill/instruction system assumes `.github/copilot-instructions.md` and `.github/skills/` paths
3. MCP configuration is Copilot-specific (`~/.copilot/mcp-config.json`)
4. `x-ipe init` and `x-ipe upgrade` only deploy Copilot artifacts
5. No mechanism to select or switch between alternative AI coding CLIs

#### Solution Overview

Introduce a **CLI Adapter Registry** — a configuration-driven system where each supported CLI is defined as an adapter with its command syntax, instruction file format, skill folder structure, and MCP config location. Phase 1 covers adapter infrastructure, init/upgrade, and skill translation. Phase 2 (separate feature) will cover terminal UI integration and runtime CLI detection.

#### Phasing

| Phase | Scope | Feature |
|-------|-------|---------|
| Phase 1 | Adapter registry, init/upgrade CLI selection, skill/instruction translation, MCP config deployment | FEATURE-027 (this feature) |
| Phase 2 | Terminal UI dynamic command construction, runtime CLI detection, prompt format templating | Future feature (TBD) |

#### Clarifications

| Question | Answer |
|----------|--------|
| Should all 5 areas go into single requirement set? | Split into 2 phases: Phase 1 (adapter + init/upgrade + translation), Phase 2 (terminal UI + runtime detection) |
| All 3 CLIs from start? | Yes — Copilot, OpenCode, Claude Code all in v1 |
| OpenCode commands mapping? | Deferred to post-v1 — prompt system handles CLI invocation generically |
| Claude Code rules? | CLAUDE.md + skills only — no .claude/rules/ translation |
| MCP config handling? | Handle MCP config for all CLIs during init |
| Auto-detection? | Yes — auto-detect and suggest, but allow override |
| CLI not installed? | Warn but proceed — user may install CLI later |
| Migration strategy? | Backup old artifacts to .x-ipe/backup/, deploy new ones (non-destructive) |
| Default CLI? | Auto-detected CLI (first found), with priority: Copilot > OpenCode > Claude Code |
| Skill filtering? | No — copy all skills to all CLIs regardless |

---

### FEATURE-027-A: CLI Adapter Registry & Service

**Version:** v1.0  
**Brief Description:** Core adapter registry with YAML config, service layer, API endpoint, CLI auto-detection, and backward compatibility. This is the MVP foundation — all other sub-features depend on it.

**Dependencies:** FEATURE-018 (X-IPE CLI Tool)

**Acceptance Criteria:**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-027-A.1 | A `cli-adapters.yaml` config file MUST exist at `src/x_ipe/resources/config/cli-adapters.yaml` defining adapter schemas for all supported CLIs | Must |
| AC-027-A.2 | Each adapter MUST define: `display_name`, `command`, `run_args`, `inline_prompt_flag`, `prompt_format`, `instructions_file`, `skills_folder`, `mcp_config_path`, `mcp_config_format`, `detection_command` | Must |
| AC-027-A.3 | The registry MUST include adapters for: `copilot`, `opencode`, `claude-code` | Must |
| AC-027-A.4 | A `CLIAdapterService` MUST provide methods: `get_active_adapter()`, `list_adapters()`, `detect_installed_clis()`, `switch_cli(name)` | Must |
| AC-027-A.5 | The active CLI selection MUST be stored in `.x-ipe.yaml` under a `cli` key | Must |
| AC-027-A.6 | If no CLI is configured in `.x-ipe.yaml`, the system MUST fall back to auto-detection with priority: Copilot > OpenCode > Claude Code | Must |
| AC-027-A.7 | An API endpoint `/api/config/cli-adapter` MUST expose active adapter info (adapter name, command, prompt format, detection status) | Must |
| AC-027-A.8 | Existing Copilot-based projects MUST continue working without any configuration changes | Must |
| AC-027-A.9 | If `.x-ipe.yaml` has no `cli` key, the system MUST behave as if Copilot is selected (after auto-detection priority check) | Must |
| AC-027-A.10 | If adapter YAML contains an unknown CLI name, the system MUST raise a clear error | Must |
| AC-027-A.11 | Prompt escaping MUST handle quotes, backticks, dollar signs, and newlines in prompt text | Must |

**Non-Functional Requirements:**

| # | Requirement | Priority |
|---|-------------|----------|
| NFR-027-A.1 | Adding a new CLI adapter MUST require only a YAML config entry (no core code changes for registry) | Must |
| NFR-027-A.2 | CLI detection MUST complete within 5 seconds (all adapters combined) | Should |
| NFR-027-A.3 | All new code MUST follow existing project patterns (service layer, route layer, tracing decorators) | Must |

**Technical Considerations:**
- `CLIAdapterService` goes in `src/x_ipe/services/cli_adapter_service.py`
- API route added to `src/x_ipe/routes/config_routes.py`
- Auto-detection uses `shutil.which()` or subprocess for each adapter's `detection_command`
- Copilot adapter is the no-op / native adapter

---

### FEATURE-027-B: CLI Init & Selection

**Version:** v1.0  
**Brief Description:** Update `x-ipe init` to auto-detect installed CLIs, present selection to user, and deploy CLI-specific artifacts (instructions file, skills folder, config).

**Dependencies:** FEATURE-027-A (CLI Adapter Registry), FEATURE-019 (Simplified Project Setup)

**Acceptance Criteria:**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-027-B.1 | `x-ipe init` MUST auto-detect installed CLIs by running each adapter's `detection_command` | Must |
| AC-027-B.2 | `x-ipe init` MUST present detected CLIs to the user with the first detected one pre-selected (priority: Copilot > OpenCode > Claude Code) | Must |
| AC-027-B.3 | User MUST be able to override the auto-detected selection | Must |
| AC-027-B.4 | If the selected CLI is not installed, `x-ipe init` MUST display a warning but still proceed with deployment | Must |
| AC-027-B.5 | `x-ipe init` MUST store the selected CLI in `.x-ipe.yaml` | Must |
| AC-027-B.6 | `x-ipe init` MUST deploy CLI-specific artifacts based on selection (instructions file, skills, MCP config) | Must |

**Technical Considerations:**
- Modifies `src/x_ipe/cli/main.py` (init command)
- Uses `CLIAdapterService.detect_installed_clis()` from FEATURE-027-A
- Calls skill translation (FEATURE-027-C) and MCP deployment (FEATURE-027-D) during init
- Interactive CLI selection via `click.prompt` or `inquirer`

---

### FEATURE-027-C: Skill & Instruction Translation

**Version:** v1.0  
**Brief Description:** Engine that translates canonical X-IPE skills (`.github/skills/`) and instructions to each CLI's native format during init/upgrade.

**Dependencies:** FEATURE-027-A (CLI Adapter Registry)

**Acceptance Criteria:**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-027-C.1 | A `SkillTranslator` service MUST exist at `src/x_ipe/services/skill_translator.py` | Must |
| AC-027-C.2 | **Copilot translation**: Skills MUST remain at `.github/skills/<name>/SKILL.md` (native format, no transformation needed) | Must |
| AC-027-C.3 | **Copilot translation**: Instructions file MUST be `.github/copilot-instructions.md` | Must |
| AC-027-C.4 | **OpenCode translation**: Skills MUST be copied to `.opencode/skills/<name>/SKILL.md` with frontmatter containing `name` and `description` (drop unsupported fields) | Must |
| AC-027-C.5 | **OpenCode translation**: An `AGENTS.md` file MUST be generated from the canonical instructions template | Must |
| AC-027-C.6 | **Claude Code translation**: Skills MUST be copied to `.claude/skills/<name>/SKILL.md` with frontmatter remapped (add `context` field if applicable) | Must |
| AC-027-C.7 | **Claude Code translation**: A `CLAUDE.md` file MUST be generated from the canonical instructions template | Must |
| AC-027-C.8 | All skills MUST be copied to the target CLI regardless of CLI-specific applicability (no filtering) | Must |
| AC-027-C.9 | Skill body content (markdown after frontmatter) MUST be preserved exactly during translation | Must |
| AC-027-C.10 | Translation MUST handle subdirectories within skill folders (e.g., `templates/`, `references/`) | Must |
| AC-027-C.11 | The Copilot adapter MUST be a no-op translation (existing `.github/` structure is native) | Must |
| AC-027-C.12 | If skill translation fails for a specific skill, the system MUST log a warning and continue with remaining skills | Should |

**Non-Functional Requirements:**

| # | Requirement | Priority |
|---|-------------|----------|
| NFR-027-C.1 | Skill translation MUST be idempotent — running it twice produces the same output | Must |

**Technical Considerations:**
- Per-adapter translation logic (strategy pattern)
- Frontmatter parsing with `python-frontmatter` or manual YAML parsing
- Template files for AGENTS.md and CLAUDE.md generation
- Copilot = no-op, OpenCode = copy + filter frontmatter, Claude Code = copy + remap frontmatter

---

### FEATURE-027-D: MCP Configuration Deployment

**Version:** v1.0  
**Brief Description:** Deploy MCP server configuration in each CLI's native format and location, preserving existing non-X-IPE entries.

**Dependencies:** FEATURE-027-A (CLI Adapter Registry)

**Acceptance Criteria:**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-027-D.1 | **Copilot MCP**: MCP servers MUST be merged into `~/.copilot/mcp-config.json` (global scope) | Must |
| AC-027-D.2 | **OpenCode MCP**: MCP servers MUST be added to `opencode.json` under `mcpServers` key (project scope) | Must |
| AC-027-D.3 | **Claude Code MCP**: MCP servers MUST be written to `.mcp.json` at project root (project scope) | Must |
| AC-027-D.4 | MCP config deployment MUST preserve existing MCP server entries that are not managed by X-IPE | Must |
| AC-027-D.5 | Each adapter's `mcp_config_format` field MUST determine the MCP config structure (`standalone_json` or `embedded_json_key:mcpServers`) | Must |
| AC-027-D.6 | If MCP config file is malformed JSON, the system MUST log an error and skip MCP deployment (not crash) | Should |

**Technical Considerations:**
- MCP config logic can live in `skill_translator.py` or a separate `mcp_config_service.py`
- JSON merge strategy: read existing → merge X-IPE entries → write back
- X-IPE-managed entries should be identifiable (e.g., prefixed key or comment)
- Handle file creation when target doesn't exist

---

### FEATURE-027-E: CLI Migration & Upgrade

**Version:** v1.0  
**Brief Description:** `x-ipe upgrade --cli <name>` command to switch between CLIs with non-destructive backup of old artifacts and redeployment of new ones.

**Dependencies:** FEATURE-027-B (CLI Init), FEATURE-027-C (Skill Translation), FEATURE-027-D (MCP Deployment)

**Acceptance Criteria:**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-027-E.1 | `x-ipe upgrade` MUST accept a `--cli <name>` flag to switch CLI | Must |
| AC-027-E.2 | When switching CLI, old CLI artifacts MUST be backed up to `.x-ipe/backup/` (non-destructive) | Must |
| AC-027-E.3 | After backup, new CLI artifacts MUST be deployed from canonical skills | Must |
| AC-027-E.4 | `.x-ipe.yaml` MUST be updated with the new CLI selection | Must |
| AC-027-E.5 | `x-ipe upgrade` MUST inform the user which files were backed up and which were created | Must |
| AC-027-E.6 | If `--cli` is not provided, `x-ipe upgrade` MUST keep the current CLI selection | Must |
| AC-027-E.7 | If the target CLI is the same as current, `x-ipe upgrade` MUST skip migration and just redeploy artifacts | Should |

**Technical Considerations:**
- Modifies `src/x_ipe/cli/main.py` (upgrade command)
- Backup creates timestamped folder: `.x-ipe/backup/{cli-name}-{timestamp}/`
- Calls `SkillTranslator` (FEATURE-027-C) for skill deployment
- Calls MCP deployer (FEATURE-027-D) for MCP config
- Reports summary of backed up files and newly created files

---

### Shared Constraints (All FEATURE-027-* Sub-Features)

- Single CLI active at a time per project
- X-IPE's canonical skill format (`.github/skills/`) remains the source of truth
- OpenCode commands mapping is deferred to post-v1
- Claude Code `.claude/rules/` translation is deferred — only `CLAUDE.md` + skills
- Phase 2 (terminal UI + runtime detection) is a separate future feature
- No UI mockup needed — this is a backend/CLI infrastructure feature

### Dependency Graph

```
FEATURE-027-A (Registry & Service) ──┬── FEATURE-027-B (Init & Selection) ──┐
                                     ├── FEATURE-027-C (Skill Translation) ──┤── FEATURE-027-E (Migration & Upgrade)
                                     └── FEATURE-027-D (MCP Deployment) ─────┘
```

### Open Questions

- None (all clarifications resolved during gathering)

---

## References

- [IDEA-013: Multi-CLI Support](../ideas/013.%20Feature-Adding%20Support%20to%20OpenCode%20CLI/idea-summary-v1.md)
- [OpenCode Documentation](https://opencode.ai/docs)
- [OpenCode Skills](https://opencode.ai/docs/skills/)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code Skills](https://docs.anthropic.com/en/docs/claude-code/skills)

---

## FEATURE-028: Prompt Bi-language Support

**Source:** [IDEA-019: Prompt Bi-language Support](../ideas/015.%20Feature-Prompt%20Bi-language%20Support/idea-summary-v1.md)

### Problem Statement

X-IPE's copilot-prompt.json labels and commands are English-only. The copilot-instructions.md file also only uses English skill routing keywords. Chinese-speaking users — the primary user base — must mentally translate button labels and write requests in English for correct skill routing. This creates friction and limits adoption.

### Solution Overview

Add bilingual (EN/ZH) support across three areas:

1. **copilot-prompt.json** — New `prompt-details` array per prompt with per-language `label` + `command`
2. **copilot-instructions.md** — Single template file with EN and ZH parts separated by `---LANG:xx---` markers; init/upgrade extracts the selected part
3. **CLI + Frontend** — Language selection at `x-ipe init` / `x-ipe upgrade --lang`; frontend filters prompts client-side by language setting

### Clarifications

| Question | Answer |
|----------|--------|
| Scope of bi-language? | copilot-prompt.json + copilot-instructions.md only. X-IPE web UI stays English-only. |
| copilot-prompt.json structure? | `prompt-details[]` array per prompt. No `label` at prompt level — only inside prompt-details entries. |
| Language separator in instructions template? | `---LANG:en---` / `---LANG:zh---` custom text markers |
| Where to store language preference? | `.x-ipe.yaml` (alongside CLI selection) |
| `x-ipe upgrade --lang` with user edits? | Behave like `x-ipe init` — overwrite with selected language part |
| How frontend gets language? | Added to existing `/api/config/*` response — no new endpoint |
| v2.0 → v3.0 migration timing? | Auto-migrate on any `x-ipe upgrade` |
| Default language for existing projects? | English (en) |
| Modify SKILL.md files? | No — skills stay as-is. CN skill keywords only in the ZH part of copilot-instructions.md |
| Future languages? | Only zh/en for now — no extensibility framework |

### Acceptance Criteria

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-028.1 | `x-ipe init` MUST prompt for language selection after CLI detection (choices: English/中文, default: en) | Must |
| AC-028.2 | `x-ipe init` MUST support `--lang <en\|zh>` flag for non-interactive language selection | Must |
| AC-028.3 | The selected language MUST be stored in `.x-ipe.yaml` under a `language` key | Must |
| AC-028.4 | copilot-prompt.json MUST bump schema version from `"2.0"` to `"3.0"` | Must |
| AC-028.5 | Each prompt entry in v3.0 MUST contain a `prompt-details` array with objects: `{ language, label, command }` | Must |
| AC-028.6 | The `label` field MUST NOT exist at the prompt level — only inside `prompt-details` entries | Must |
| AC-028.7 | Each prompt MUST have `prompt-details` entries for both `"en"` and `"zh"` languages | Must |
| AC-028.8 | The `prompt-details` structure MUST apply uniformly to `prompts[]` arrays, singleton `evaluate` objects, and `refactoring[]` arrays | Must |
| AC-028.9 | The package MUST ship a single bilingual `copilot-instructions.md` template with EN and ZH parts separated by `---LANG:en---` and `---LANG:zh---` markers | Must |
| AC-028.10 | `x-ipe init` MUST extract only the selected language part from the bilingual template and copy it into the project as `copilot-instructions.md` | Must |
| AC-028.11 | The ZH part of copilot-instructions.md MUST include Chinese keyword examples for skill routing (e.g., "优化创意" → Ideation, "修复bug" → Bug Fix) | Must |
| AC-028.12 | `x-ipe upgrade --lang` MUST present an interactive language selection prompt | Must |
| AC-028.13 | `x-ipe upgrade --lang` MUST update `.x-ipe.yaml` language setting and re-extract the matching instructions part (same behavior as init) | Must |
| AC-028.14 | `x-ipe upgrade` (without `--lang`) MUST auto-migrate copilot-prompt.json from v2.0 to v3.0 format | Must |
| AC-028.15 | v2.0 → v3.0 migration MUST wrap existing `command`/`label` into `prompt-details[{language:"en",...}]` and add `{language:"zh",...}` entries | Must |
| AC-028.16 | The existing `/api/config/*` response MUST include the `language` field from `.x-ipe.yaml` | Must |
| AC-028.17 | Frontend Copilot button JS MUST filter `prompt-details` by the language setting and display the matching `label` and `command` | Must |
| AC-028.18 | Frontend MUST fall back to `"en"` entry if no matching language found in `prompt-details` | Must |
| AC-028.19 | Frontend MUST fall back to top-level `command`/`label` fields if `prompt-details` is absent (v2.0 backward compatibility) | Must |
| AC-028.20 | Existing v2.0 copilot-prompt.json (without `prompt-details`) MUST continue working without errors | Must |
| AC-028.21 | Existing projects upgrading without a `language` key in `.x-ipe.yaml` MUST default to `"en"` | Must |
| AC-028.22 | SKILL.md files MUST NOT be modified — skills remain English-only | Must |
| AC-028.23 | X-IPE web UI (sidebar, page titles, buttons) MUST remain English-only — bi-language applies to prompts and instructions only | Must |

### Non-Functional Requirements

| # | Requirement | Priority |
|---|-------------|----------|
| NFR-028.1 | Adding a new language SHOULD only require adding entries to `prompt-details`, a new `---LANG:xx---` section in the instructions template, and updating CLI choices | Should |
| NFR-028.2 | copilot-prompt.json v2.0 → v3.0 migration MUST be idempotent (running upgrade twice produces the same result) | Must |
| NFR-028.3 | Language switching via `--lang` MUST complete in under 5 seconds | Should |
| NFR-028.4 | All new code MUST follow existing project patterns (service layer, tracing decorators, route patterns) | Must |

### Technical Considerations

- Modifies `src/x_ipe/cli/main.py` (init + upgrade commands)
- Modifies copilot-prompt.json template in `src/x_ipe/resources/config/`
- Modifies copilot-instructions.md template in `src/x_ipe/resources/` (add ZH part with `---LANG:zh---` separator)
- Modifies frontend JS for client-side prompt filtering (likely `workplace.js` or wherever Copilot button prompts are rendered)
- Modifies config API route to include language field
- `.x-ipe.yaml` gains `language` key
- v2.0 → v3.0 JSON migration logic needed in upgrade command

### Dependency Graph

```
FEATURE-027-A (CLI Registry) ──── FEATURE-027-B (CLI Init) ──── FEATURE-028 (Bi-language Support)
```

FEATURE-028 depends on the CLI init/upgrade infrastructure from FEATURE-027 since language selection is added to the same init flow and stored in the same `.x-ipe.yaml` config.

### Open Questions

- None (all clarifications resolved during gathering)

---

### FEATURE-028-A: Bilingual Prompt Schema & Migration

**Version:** v1.0
**Brief Description:** Define the copilot-prompt.json v3.0 schema with `prompt-details` array, create bilingual EN/ZH prompt content for all existing prompts, and implement v2.0→v3.0 auto-migration logic.

**Acceptance Criteria:**
- [ ] copilot-prompt.json MUST bump schema version to `"3.0"` (AC-028.4)
- [ ] Each prompt entry MUST contain a `prompt-details` array with `{ language, label, command }` objects (AC-028.5)
- [ ] `label` MUST NOT exist at the prompt level — only inside `prompt-details` entries (AC-028.6)
- [ ] Each prompt MUST have entries for both `"en"` and `"zh"` (AC-028.7)
- [ ] `prompt-details` MUST apply to `prompts[]` arrays, singleton `evaluate`, and `refactoring[]` (AC-028.8)
- [ ] v2.0→v3.0 migration MUST wrap existing `command`/`label` into `prompt-details[{language:"en",...}]` and add ZH entries (AC-028.14, AC-028.15)
- [ ] Existing v2.0 copilot-prompt.json MUST continue working without errors (AC-028.20)

**Dependencies:**
- None (foundation feature — defines the schema all others consume)

**Technical Considerations:**
- New v3.0 template at `src/x_ipe/resources/config/copilot-prompt.json`
- Migration utility function in CLI or service layer
- Migration must be idempotent (NFR-028.2)
- Chinese translations for all existing prompts needed

---

### FEATURE-028-B: CLI Language Selection & Instructions

**Version:** v1.0
**Brief Description:** Add language selection to `x-ipe init` and `x-ipe upgrade --lang`, create bilingual copilot-instructions.md template with `---LANG:xx---` markers, and implement extraction logic to copy only the selected language part.

**Acceptance Criteria:**
- [ ] `x-ipe init` MUST prompt for language selection after CLI detection (default: en) (AC-028.1)
- [ ] `x-ipe init` MUST support `--lang <en|zh>` for non-interactive mode (AC-028.2)
- [ ] Selected language MUST be stored in `.x-ipe.yaml` under `language` key (AC-028.3)
- [ ] Package MUST ship bilingual copilot-instructions.md template with `---LANG:en---` / `---LANG:zh---` markers (AC-028.9)
- [ ] `x-ipe init` MUST extract only the selected language part into the project (AC-028.10)
- [ ] ZH part MUST include Chinese keyword examples for skill routing (AC-028.11)
- [ ] `x-ipe upgrade --lang` MUST present interactive language prompt (AC-028.12)
- [ ] `x-ipe upgrade --lang` MUST update `.x-ipe.yaml` and re-extract instructions (AC-028.13)
- [ ] Existing projects without `language` key MUST default to `"en"` (AC-028.21)

**Dependencies:**
- FEATURE-028-A: v3.0 copilot-prompt.json must exist for init to scaffold it

**Technical Considerations:**
- Modifies `src/x_ipe/cli/main.py` (init + upgrade commands)
- Bilingual instructions template in `src/x_ipe/resources/`
- Language extraction: parse `---LANG:xx---` markers, extract matching section
- Chinese instructions content authoring required

---

### FEATURE-028-C: Frontend Prompt Language Filtering

**Version:** v1.0
**Brief Description:** Frontend client-side filtering of `prompt-details` by language setting, with fallback chain for v2.0 backward compatibility. Language field added to existing config API response.

**Acceptance Criteria:**
- [ ] Existing `/api/config/*` response MUST include `language` field from `.x-ipe.yaml` (AC-028.16)
- [ ] Frontend Copilot button JS MUST filter `prompt-details` by language and display matching `label`/`command` (AC-028.17)
- [ ] Frontend MUST fall back to `"en"` entry if no matching language found (AC-028.18)
- [ ] Frontend MUST fall back to top-level `command`/`label` if `prompt-details` absent (v2.0 compat) (AC-028.19)

**Dependencies:**
- FEATURE-028-A: v3.0 schema defines the `prompt-details` structure consumed by frontend
- FEATURE-028-B: Language setting in `.x-ipe.yaml` must be available via API

**Technical Considerations:**
- Modifies config API route to read language from `.x-ipe.yaml`
- Modifies frontend JS (likely `workplace.js`) for prompt-details filtering
- Fallback chain: prompt-details[lang] → prompt-details["en"] → top-level command/label
- No new API endpoint — adds field to existing response

---

### Sub-Feature Dependency Graph

```
FEATURE-028-A (Schema & Migration) ──┬── FEATURE-028-B (CLI & Instructions) ──── FEATURE-028-D (Settings Language Switch)
                                     │                    │
                                     └────────────────────┴── FEATURE-028-C (Frontend Filtering)
```

---

### FEATURE-028-D: Settings Language Switch (Web UI)

**Version:** v1.0
**Brief Description:** Add a language dropdown to the Settings web UI page that replicates `x-ipe upgrade --lang` behavior — switching language and re-extracting copilot instructions via AJAX without page reload.
**Source:** [CR-002](../FEATURE-028-D/CR-002.md) — [IDEA-020](../../ideas/016.%20CR-Switch%20Language%20in%20Settings/idea-summary-v1.md)

**Acceptance Criteria:**
- [ ] Settings page MUST display a dedicated "Language" section with current language badge and dropdown (en / 中文) (AC-CR2-1, AC-CR2-2)
- [ ] Selecting a different language MUST show a confirmation dialog warning about instruction regeneration (AC-CR2-3)
- [ ] Backend MUST expose `POST /api/config/language` endpoint that calls ScaffoldManager (AC-CR2-4)
- [ ] Instructions MUST be extracted BEFORE updating `.x-ipe.yaml` for atomicity (AC-CR2-5)
- [ ] Success/error feedback via toast notification without page reload (AC-CR2-6)
- [ ] Same-language selection MUST be a no-op with informational toast (AC-CR2-7)
- [ ] Dropdown MUST be disabled during switch operation (AC-CR2-8)
- [ ] Custom edits outside X-IPE markers MUST be preserved (AC-CR2-9)

**Dependencies:**
- FEATURE-028-B: ScaffoldManager language switch logic (reused from CLI)

**Technical Considerations:**
- New `POST /api/config/language` endpoint in `settings_routes.py`
- ScaffoldManager imported into web layer (currently CLI-only)
- Settings page HTML: new Language section with dropdown, confirmation dialog
- Inline JS: LanguageManager class following ProjectFoldersManager pattern
- Atomic ordering: extract instructions → update config → respond

### Shared Constraints (All FEATURE-028-* Sub-Features)

- Only zh/en supported — no extensibility framework
- SKILL.md files remain unmodified (AC-028.22)
- X-IPE web UI stays English-only (AC-028.23)
- All new code follows existing patterns (NFR-028.4)
