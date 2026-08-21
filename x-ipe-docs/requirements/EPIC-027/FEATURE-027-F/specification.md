# FEATURE-027-F: Codex CLI Adapter — Specification

## Overview

Add the OpenAI Codex CLI (`codex`) as a fourth CLI adapter alongside `copilot`, `opencode`, and `claude-code`. Codex is detected, selectable via `x-ipe init --cli codex`, receives translated skills in `.codex/skills/` and instructions in `AGENTS.md`, and gets MCP servers registered through `codex mcp add` during init/upgrade MCP selection.

**Dependencies:** FEATURE-027-A (registry), FEATURE-027-B (selection), FEATURE-027-C (translation), FEATURE-027-D (MCP deployment)

---

## Acceptance Criteria

### AC-1: Adapter Registration

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-1.1 | `cli-adapters.yaml` (both `x-ipe-docs/config/` and `src/x_ipe/resources/config/`) MUST include a `codex` entry with all 10 config fields | MUST |
| AC-1.2 | Codex entry MUST use: `command: codex`, `run_args: "exec --dangerously-bypass-approvals-and-sandbox"`, `inline_prompt_flag: ""`, `instructions_file: AGENTS.md`, `skills_folder: .codex/skills/`, `mcp_config_path: ~/.codex/config.toml`, `mcp_config_format: codex-toml`, `detection_command: codex` | MUST |
| AC-1.3 | `AUTO_DETECT_PRIORITY` MUST include `codex` after the existing three (existing users' detection unchanged) | MUST |
| AC-1.4 | `build_command()` MUST produce `codex exec --dangerously-bypass-approvals-and-sandbox "<prompt>"` | MUST |

### AC-2: Skill Translation

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-2.1 | `translate_skills()` for codex MUST copy skills verbatim to `.codex/skills/<name>/` (preserve frontmatter and body) — same strategy as claude-code | MUST |
| AC-2.2 | `generate_instructions()` for codex MUST write the instructions template to `AGENTS.md` at project root | MUST |

### AC-3: MCP Deployment

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-3.1 | `MCPDeployerService.deploy()` MUST handle `mcp_config_format: codex-toml` by invoking `codex mcp add <name> [--env K=V] -- <command> <args...>` for each selected server | MUST |
| AC-3.2 | Existing servers MUST be skipped unless `force=True` (existence checked via `codex mcp get <name>`; force removes then re-adds) | MUST |
| AC-3.3 | When codex is not installed, deploy MUST skip with a warning, not crash | MUST |
| AC-3.4 | `x-ipe init` with codex selected MUST register confirmed MCP servers via the deployer without prompting for a target path (target is fixed: `~/.codex/config.toml`, managed by the codex CLI itself) | MUST |
| AC-3.5 | `MCPDeployerService.deploy(dry_run=True)` MUST report intended server registrations without invoking codex (service-level flag; the CLI's `--dry-run` skips the MCP block entirely) | MUST |

### AC-4: CLI Surface

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-4.1 | `x-ipe init --cli codex` and `x-ipe upgrade --cli codex` MUST validate and accept the codex adapter | MUST |
| AC-4.2 | `--cli` help text MUST list codex | SHOULD |

---

## Edge Cases

| EC ID | Description | Expected Behavior |
|-------|-------------|-------------------|
| EC-1 | `codex` binary not installed at MCP deploy time | Log warning, mark skipped, continue init |
| EC-2 | `codex mcp add` subprocess fails (timeout / non-zero exit) | Record error in result, log stderr, continue with remaining servers |
| EC-3 | Project already has an `AGENTS.md` (e.g. from opencode) | Overwrite follows existing `force` semantics of instructions generation |
| EC-4 | Migration away from codex | Global `~/.codex/config.toml` is NOT backed up or modified (deploy only adds) |
