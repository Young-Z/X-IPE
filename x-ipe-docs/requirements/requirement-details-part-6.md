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
