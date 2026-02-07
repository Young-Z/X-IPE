# Feature Specification: CLI Adapter Registry & Service

> Feature ID: FEATURE-027-A  
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

FEATURE-027-A introduces the **CLI Adapter Registry** — the foundational infrastructure that enables X-IPE to support multiple AI coding CLIs (GitHub Copilot CLI, OpenCode CLI, Claude Code CLI). Currently, X-IPE is tightly coupled to GitHub Copilot CLI: the terminal integration hardcodes `copilot` commands, skills assume `.github/skills/` paths, and MCP config targets `~/.copilot/mcp-config.json`.

This feature creates a configuration-driven adapter registry where each supported CLI is defined in a YAML config file with its command syntax, argument format, instruction file location, skills folder path, and MCP config details. A `CLIAdapterService` provides a programmatic interface to query adapters, detect installed CLIs, and manage the active CLI selection stored in `.x-ipe.yaml`.

**Target users:** X-IPE developers, teams evaluating different AI coding agents, and the X-IPE init/upgrade system (which consumes adapters for artifact deployment).

## User Stories

| ID | User Story | Priority |
|----|-----------|----------|
| US-027-A.1 | As an X-IPE developer, I want to define CLI adapters in a YAML config, so that adding a new CLI requires only configuration changes | Must |
| US-027-A.2 | As an X-IPE developer, I want the system to auto-detect which CLIs are installed, so that I get a sensible default without manual configuration | Must |
| US-027-A.3 | As the X-IPE init/upgrade system, I want to query the active adapter's properties, so that I can deploy CLI-specific artifacts correctly | Must |
| US-027-A.4 | As an X-IPE user with an existing Copilot-based project, I want the system to work without changes, so that upgrading X-IPE doesn't break my workflow | Must |
| US-027-A.5 | As a frontend consumer, I want an API endpoint exposing the active CLI adapter, so that the UI can display CLI-specific information | Must |

## Acceptance Criteria

**1. Adapter Configuration**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-1.1 | A `cli-adapters.yaml` config file MUST exist at `src/x_ipe/resources/config/cli-adapters.yaml` | File exists at specified path and is valid YAML |
| AC-1.2 | Each adapter entry MUST define: `display_name`, `command`, `run_args`, `inline_prompt_flag`, `prompt_format`, `instructions_file`, `skills_folder`, `mcp_config_path`, `mcp_config_format`, `detection_command` | Parse YAML, verify all 10 fields present for each adapter |
| AC-1.3 | The registry MUST include adapters for: `copilot`, `opencode`, `claude-code` | Parse YAML, verify 3 adapter keys exist |

**2. Service Layer**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-2.1 | `CLIAdapterService` MUST provide `get_active_adapter()` returning the current adapter config | Call method, receive adapter dict with all required fields |
| AC-2.2 | `CLIAdapterService` MUST provide `list_adapters()` returning all registered adapters | Call method, receive list of 3 adapters |
| AC-2.3 | `CLIAdapterService` MUST provide `detect_installed_clis()` returning list of detected CLI names | Call method, receive list (may be empty if no CLIs installed) |
| AC-2.4 | `CLIAdapterService` MUST provide `switch_cli(name)` to change the active CLI | Call method with valid name, verify `.x-ipe.yaml` updated |
| AC-2.5 | `switch_cli()` MUST raise a clear error if name is not a registered adapter | Call with invalid name, expect ValueError |

**3. Active CLI Selection**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-3.1 | The active CLI MUST be stored in `.x-ipe.yaml` under a `cli` key | Write CLI selection, read `.x-ipe.yaml`, verify `cli` key present |
| AC-3.2 | If `.x-ipe.yaml` has no `cli` key, the system MUST fall back to auto-detection with priority: Copilot > OpenCode > Claude Code | Remove `cli` key, call `get_active_adapter()`, verify priority order |
| AC-3.3 | If no CLI is detected and no `cli` key exists, the system MUST default to `copilot` | Mock no CLIs installed, verify default is copilot |

**4. API Endpoint**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-4.1 | `GET /api/config/cli-adapter` MUST return active adapter info | HTTP GET request, receive JSON with adapter_name, command, prompt_format, detection_status |
| AC-4.2 | Response MUST include: `adapter_name`, `display_name`, `command`, `prompt_format`, `is_installed` | Validate response schema contains all 5 fields |

**5. Prompt Escaping**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-5.1 | `build_command(prompt)` MUST properly escape quotes in prompt text | Pass prompt with single/double quotes, verify escaped output |
| AC-5.2 | `build_command(prompt)` MUST properly escape backticks, dollar signs, and newlines | Pass prompt with special chars, verify safe shell command output |
| AC-5.3 | Command construction MUST use the adapter's `prompt_format` template | Build command for each adapter, verify format matches template |

**6. Backward Compatibility**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-6.1 | Existing Copilot-based projects MUST continue working without any configuration changes | Load service without `.x-ipe.yaml` `cli` key, verify copilot behavior |
| AC-6.2 | The Copilot adapter MUST use `.github/skills/` and `.github/copilot-instructions.md` as native paths | Query copilot adapter, verify paths match existing structure |

## Functional Requirements

| # | Requirement | Input | Process | Output |
|---|-------------|-------|---------|--------|
| FR-1 | Load adapter registry from YAML config | `cli-adapters.yaml` path | Parse YAML, validate required fields per adapter, build in-memory registry | Dict of adapter name → adapter config |
| FR-2 | Detect installed CLIs | Adapter registry | For each adapter, run `detection_command` (e.g., `which copilot`) with 5s timeout | List of installed CLI names |
| FR-3 | Resolve active adapter | `.x-ipe.yaml` config | Read `cli` key → if present, use it; if absent, auto-detect with priority; if none detected, default to `copilot` | Active adapter config |
| FR-4 | Switch active CLI | CLI name string | Validate name exists in registry → update `.x-ipe.yaml` `cli` key | Updated config file |
| FR-5 | Build CLI command from prompt | Prompt string + active adapter | Escape special characters → substitute into adapter's `prompt_format` template | Shell-safe command string |
| FR-6 | Expose adapter via API | HTTP GET request | Call `get_active_adapter()`, add detection status | JSON response |

## Non-Functional Requirements

| # | Requirement | Metric | Priority |
|---|-------------|--------|----------|
| NFR-1 | Adding a new CLI adapter MUST require only a YAML config entry (no code changes to registry/service) | New adapter works after adding YAML entry + restart | Must |
| NFR-2 | CLI detection MUST complete within 5 seconds (all adapters combined) | Time `detect_installed_clis()` < 5s | Should |
| NFR-3 | All new code MUST follow existing project patterns (service layer, route layer, `@x_ipe_tracing` decorators) | Code review against `config_service.py` pattern | Must |
| NFR-4 | Service MUST be importable and usable without Flask context (for CLI commands) | Import and call from non-Flask script succeeds | Must |

## Dependencies

### Internal Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-010 | Soft | Uses `.x-ipe.yaml` config file (adds `cli` key to existing structure) |
| FEATURE-018 | Soft | CLI Tool provides the `x-ipe` command infrastructure; this feature adds adapter awareness to it |

### External Dependencies

| Dependency | Description |
|-----------|-------------|
| PyYAML | Already in project dependencies — used for `.x-ipe.yaml` and `cli-adapters.yaml` parsing |
| `shutil.which` / subprocess | Standard library — used for CLI detection |

## Business Rules

| # | Rule |
|---|------|
| BR-1 | Only one CLI can be active per project at any time |
| BR-2 | The `copilot` adapter is always the ultimate fallback when no CLI is configured or detected |
| BR-3 | Auto-detection priority order is fixed: Copilot > OpenCode > Claude Code |
| BR-4 | An adapter can be selected even if the CLI is not installed (warn, don't block) |
| BR-5 | The canonical skill format (`.github/skills/`) remains the source of truth regardless of active CLI |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|------------------|
| `.x-ipe.yaml` does not exist | Service uses auto-detection; defaults to `copilot` if nothing detected |
| `.x-ipe.yaml` exists but has no `cli` key | Same as above — auto-detect, fallback to `copilot` |
| `.x-ipe.yaml` has `cli: unknown-cli` | `get_active_adapter()` raises clear error with available adapter names |
| `cli-adapters.yaml` is malformed YAML | Service raises error at initialization with parse error details |
| All `detection_command` calls fail/timeout | Empty detection list; falls back to configured or default adapter |
| `detection_command` hangs | 2-second timeout per command (5s total across all adapters) |
| Prompt contains shell metacharacters (`$`, `` ` ``, `"`, `'`, `\n`) | `build_command()` escapes all metacharacters for safe shell execution |
| Multiple CLIs installed | Auto-detection returns all; priority determines default selection |
| `.x-ipe.yaml` is read-only | `switch_cli()` raises IOError with descriptive message |

## Out of Scope

- Terminal UI integration (FEATURE-027 Phase 2 — future feature)
- Runtime CLI mode detection in terminal (Phase 2)
- Skill translation logic (FEATURE-027-C)
- MCP configuration deployment (FEATURE-027-D)
- `x-ipe init` / `x-ipe upgrade` command changes (FEATURE-027-B, 027-E)
- OpenCode commands mapping (deferred post-v1)
- Claude Code `.claude/rules/` translation (deferred)

## Technical Considerations

- `CLIAdapterService` should follow the pattern of `ConfigService` — dataclass for adapter data, service class with load/query methods, `@x_ipe_tracing` decorators
- The adapter YAML should be bundled as package data in `src/x_ipe/resources/config/`
- CLI detection should use `shutil.which()` rather than subprocess for speed and simplicity
- The service must work both inside Flask context (API route) and outside (CLI commands) — avoid Flask-specific imports in the service layer
- API route should go in a new `config_routes.py` or extend existing route structure
- The `prompt_format` field uses Python `.format()` style templates with named placeholders: `{command}`, `{run_args}`, `{inline_prompt_flag}`, `{escaped_prompt}`

## Open Questions

None — all clarifications resolved during requirement gathering.
