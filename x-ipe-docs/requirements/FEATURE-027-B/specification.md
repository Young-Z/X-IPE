# Feature Specification: CLI Init & Selection

> Feature ID: FEATURE-027-B  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-07-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-07-2026 | Initial specification |

## Linked Mockups

N/A — This is a CLI command feature with no UI.

## Overview

FEATURE-027-B extends the existing `x-ipe init` command to support multi-CLI initialization. Currently, `x-ipe init` hardcodes GitHub Copilot artifacts: it copies skills to `.github/skills/`, deploys `copilot-instructions.md`, and merges MCP config to `~/.copilot/mcp-config.json`. 

This feature adds CLI auto-detection and selection to the init flow so that artifacts are deployed to the correct CLI-specific locations. The init command will detect installed CLIs (using FEATURE-027-A's `CLIAdapterService`), present a selection prompt, store the choice in `.x-ipe.yaml`, and pass the selected adapter to downstream scaffold operations.

**Important scope boundary:** This feature handles the init flow orchestration and CLI selection only. The actual skill translation (FEATURE-027-C) and MCP deployment to CLI-native locations (FEATURE-027-D) are separate features. This feature ensures the selected adapter is available for those features to consume.

## User Stories

| ID | User Story | Priority |
|----|-----------|----------|
| US-027-B.1 | As a developer running `x-ipe init`, I want the system to auto-detect my installed CLIs, so that I get a sensible default without guessing | Must |
| US-027-B.2 | As a developer, I want to choose which CLI to use during init, so that artifacts deploy to the right locations | Must |
| US-027-B.3 | As a developer with no supported CLI installed, I want init to still work with copilot as default, so I can set up the project structure | Must |
| US-027-B.4 | As a developer, I want a `--cli` flag to skip the interactive prompt, so I can script init in CI/CD | Should |

## Acceptance Criteria

**1. CLI Auto-Detection During Init**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-1.1 | `x-ipe init` MUST call `CLIAdapterService.detect_installed_clis()` to find available CLIs | Mock service, verify `detect_installed_clis()` called during init |
| AC-1.2 | Detected CLIs MUST be displayed to the user with their display names | Capture stdout, verify CLI names printed |
| AC-1.3 | If no CLIs are detected, init MUST display a notice and default to Copilot | Run with no CLIs installed, verify Copilot selected and notice shown |

**2. CLI Selection Prompt**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-2.1 | `x-ipe init` MUST present a selection prompt listing all registered adapters | Capture prompt output, verify all adapter names listed |
| AC-2.2 | The first detected CLI (by priority) MUST be pre-selected as default | Verify default value in prompt matches priority order |
| AC-2.3 | User MUST be able to select a CLI that is not installed (with a warning) | Select uninstalled CLI, verify warning displayed but init continues |

**3. CLI Flag (Non-Interactive)**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-3.1 | `x-ipe init --cli copilot` MUST skip the selection prompt and use the specified CLI | Run with --cli flag, verify no prompt and correct CLI used |
| AC-3.2 | `x-ipe init --cli unknown` MUST exit with error listing available adapters | Run with invalid --cli, verify exit code 1 and error message |

**4. Config Storage**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-4.1 | The selected CLI MUST be stored in `.x-ipe.yaml` under the `cli` key | After init, read `.x-ipe.yaml` and verify `cli` key present |
| AC-4.2 | If `.x-ipe.yaml` already has a `cli` key, init MUST use it as the default selection | Create `.x-ipe.yaml` with `cli: opencode`, verify opencode is default |

**5. Backward Compatibility**

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-5.1 | `x-ipe init` without `--cli` in a Copilot-detected environment MUST produce identical results to the current init behavior | Compare init output before/after this feature on a Copilot-only system |
| AC-5.2 | All existing init flags (`--force`, `--dry-run`, `--no-skills`, `--no-mcp`) MUST continue working | Run with each flag, verify behavior unchanged |

## Functional Requirements

| # | Requirement | Input | Process | Output |
|---|-------------|-------|---------|--------|
| FR-1 | Detect installed CLIs | CLIAdapterService | Call `detect_installed_clis()`, get list | List of installed CLI names |
| FR-2 | Present CLI selection | Installed list + all adapters | Show prompt with detected CLIs highlighted, default from priority or existing config | Selected CLI name |
| FR-3 | Validate CLI selection | CLI name string | Check name exists in adapter registry | Valid adapter or error |
| FR-4 | Store CLI selection | Selected name + .x-ipe.yaml path | Write `cli` key to config during `create_config_file()` | Updated .x-ipe.yaml |
| FR-5 | Pass adapter to scaffold | Selected adapter | Make adapter available for skill copy, instructions deploy, MCP merge | Adapter-aware scaffold operations |

## Non-Functional Requirements

| # | Requirement | Metric | Priority |
|---|-------------|--------|----------|
| NFR-1 | CLI detection during init MUST complete within 5 seconds | Time from init start to prompt display < 5s | Should |
| NFR-2 | Non-interactive mode (`--cli` flag) MUST work in headless/CI environments | Run in non-TTY, verify no prompts | Must |

## Dependencies

### Internal Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-027-A | Hard | Uses `CLIAdapterService` for detection, listing, and adapter lookup |
| FEATURE-019 | Soft | Simplified Project Setup — init command structure exists here |

### External Dependencies

| Dependency | Description |
|-----------|-------------|
| Click | CLI framework — already in project deps, used for prompts and options |

## Business Rules

| # | Rule |
|---|------|
| BR-1 | The `--cli` flag takes absolute precedence over detection and existing config |
| BR-2 | If `.x-ipe.yaml` already has a `cli` key, it becomes the default in the prompt (not auto-detection) |
| BR-3 | Selecting an uninstalled CLI is allowed but must show a warning |
| BR-4 | `--dry-run` MUST show the CLI that would be selected without writing config |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|------------------|
| No CLIs installed | Notice displayed; copilot used as default |
| All 3 CLIs installed | Copilot pre-selected (priority order) |
| `--cli` with valid but uninstalled CLI | Warning printed, init proceeds |
| `--cli` with invalid name | Exit with error, list available adapters |
| `.x-ipe.yaml` already exists with `cli` key | Existing value used as prompt default; `--force` overwrites |
| `--dry-run` mode | CLI selection shown in output but not written |
| `--no-skills` and `--no-mcp` | CLI still selected and stored, but skill/MCP operations skipped |

## Out of Scope

- Skill translation logic (FEATURE-027-C)
- MCP config deployment to CLI-native paths (FEATURE-027-D)
- CLI migration/switching between CLIs after init (FEATURE-027-E)
- Interactive TUI with arrow-key selection (simple `click.prompt` is sufficient)

## Technical Considerations

- Modify `src/x_ipe/cli/main.py` `init()` command — add `--cli` option, add detection + selection logic before scaffold operations
- Modify `src/x_ipe/core/scaffold.py` `create_config_file()` — accept optional `cli_name` parameter to include in `.x-ipe.yaml`
- `CLIAdapterService` is instantiated without Flask context — already designed for this (FEATURE-027-A NFR-4)
- Use `click.prompt` with `type=click.Choice()` for CLI selection — provides built-in validation
- The selected adapter name is passed through to scaffold operations via a local variable (no global state)

## Open Questions

None.
