# FEATURE-027-F: Codex CLI Adapter — Technical Design

## Part 1: Agent Summary

### Architecture Decision

Codex is config-driven wherever the adapter registry already supports it. Two mechanisms need code: (1) an explicit verbatim translation branch, (2) a new MCP config format `codex-toml` that delegates MCP registration to the `codex mcp add` subprocess — Codex keeps MCP servers in the global `~/.codex/config.toml` (TOML shared with user settings), so letting the codex CLI mutate its own config avoids a TOML-writer dependency and zero-risk of mangling user settings (marketplaces, plugins, model config).

### Components Modified

1. **`cli-adapters.yaml` (×2)** — new `codex` entry; both copies must stay identical (wheel force-includes `x-ipe-docs/config/` as `x_ipe/resources/config/`)
2. **`cli_adapter_service.py`** — append `'codex'` to `AUTO_DETECT_PRIORITY`
3. **`skill_translator.py`** — explicit `codex` branch → verbatim copy (reuses claude-code strategy; codex accepts the Agent Skills SKILL.md format as-is)
4. **`mcp_deployer_service.py`** — `codex-toml` format branch: `_deploy_codex_cli()` subprocess helper; `resolve_target_path()` treats `codex-toml` like `global` (expanduser)
5. **`cli/main.py`** — `--cli` help text; init MCP flow: for `codex-toml` format skip the target-path prompt and call `deployer.deploy(adapter, servers_to_merge=...)` directly
6. No new services, no new dependencies

### Key Design Decisions

- **Adapter key `codex`** (not `codex-cli`): matches the binary name, consistent with `copilot`/`opencode` pattern
- **`codex mcp add` subprocess over TOML merge**: stdlib has no TOML writer; codex manages its own config atomically and preserves user formatting
- **Existence check** via `codex mcp get <name>` exit code → skip unless `force` (force = `codex mcp remove` then `add`), preserving the JSON path's skip/merge counting semantics
- **run_args `exec --dangerously-bypass-approvals-and-sandbox`**: non-interactive + full autonomy, parity with claude-code's `bypassPermissions`
- **Migration away from codex** does not touch `~/.codex/config.toml` (deploy only adds; global configs are never backed up)

### Design Change Log

| Date | Change |
|------|--------|
| 2026-08-21 | Added optional `source_servers` param to `MCPDeployerService.deploy()` — `init` reads MCP servers from package resources (project config file doesn't exist yet on first init for non-copilot CLIs), so the codex init path passes them explicitly |
| 2026-08-21 | Feature-closing review found `upgrade`'s trailing MCP block lacked the codex-toml branch: with codex active it would prompt for a target path and call `ScaffoldManager.merge_mcp_config(mcp_format='codex-toml')`, which JSON-parses and overwrites `~/.codex/config.toml`. Fixed by routing `upgrade` through `MCPDeployerService.deploy()` for `codex-toml` (same as `init`); regression guard added in `tests/test_cli_init_selection.py::TestCodexUpgrade` |

---

## Part 2: Implementation Guide

### YAML entry (identical in both copies)

```yaml
  codex:
    display_name: "Codex CLI"
    command: "codex"
    run_args: "exec --dangerously-bypass-approvals-and-sandbox"
    inline_prompt_flag: ""
    prompt_format: '{command} {run_args} "{escaped_prompt}"'
    instructions_file: "AGENTS.md"
    skills_folder: ".codex/skills/"
    mcp_config_path: "~/.codex/config.toml"
    mcp_config_format: "codex-toml"
    detection_command: "codex"
```

### `mcp_deployer_service.py` — codex-toml branch

```python
# in deploy(): dry_run is handled BEFORE the format branch (applies to all formats)
if adapter.mcp_config_format == "codex-toml":
    return self._deploy_codex_cli(adapter, source_servers, force)

def _deploy_codex_cli(self, adapter, servers, force) -> MCPDeployResult:
    # 1. shutil.which(adapter.detection_command) → None: warn + return skipped
    # 2. per server: subprocess.run(["codex","mcp","get",name]) rc==0 → exists
    #    exists and not force → skipped_count++; force → remove then add
    #    add: ["codex","mcp","add",name] + ["--env",f"{k}={v}"]* + ["--", command, *args]
    #    subprocess timeout=30, capture_output; failure → log stderr, collect in result
```

### `skill_translator.py` — explicit branch

```python
elif adapter.name == 'codex':
    return self._translate_claude_code(source, target)  # verbatim preserve
```

### `cli/main.py` — init MCP flow

In the MCP selection block: when resolved `mcp_format == 'codex-toml'`, skip the target-path `click.prompt` and call `deployer.deploy(adapter, servers_to_merge=servers_to_merge, force=force)`; keep `scaffold.merge_mcp_config` for JSON formats. Update `--cli` help to `(copilot, opencode, claude-code, codex)`.

### Tests

- `test_cli_adapter.py`: `SAMPLE_ADAPTERS_YAML` += codex entry; `len(adapters) == 3` → `4`; `build_command` codex case
- `test_mcp_deployer.py`: codex fixtures — happy add, skip-when-exists, force re-add, not-installed warning, dry-run (mock `subprocess.run` / `shutil.which`)
- `test_skill_translator.py`: codex verbatim copy preserves frontmatter + body, subdirs copied, `AGENTS.md` generated
- `test_cli_init_selection.py::TestCodexUpgrade`: steady-state `upgrade` with codex active routes MCP through the deployer and never calls `ScaffoldManager.merge_mcp_config` (regression guard added during Feature Closing)
