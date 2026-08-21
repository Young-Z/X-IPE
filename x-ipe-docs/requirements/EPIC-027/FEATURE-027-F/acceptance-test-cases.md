# Acceptance Test Cases

> Feature: FEATURE-027-F - Codex CLI Adapter
> Generated: 2026-08-21
> Status: Executed — 13/13 passed (100%)

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-027-F |
| Feature Title | Codex CLI Adapter |
| Total Test Cases | 13 |
| Priority | P0 (Critical) / P1 (High) / P2 (Medium) |
| Target URL | N/A — backend/CLI feature, no frontend-ui tests |

**Test type routing** (tools.json `stages.validation.acceptance_test` all enabled):
- unit → pytest via `x-ipe-tool-implementation-python` conventions
- integration → real CLI execution (`codex-cli 0.149.0` installed locally)
- structured-review → agent self-review of deliverables

**Safety note:** Integration tests that invoke real `codex mcp` commands run with an isolated `CODEX_HOME` (temp dir) so the user's `~/.codex/config.toml` is never modified.

---

## Prerequisites

- [x] Feature implemented (board status Implemented, TASK-1158 completed)
- [x] `codex` binary installed (`codex-cli 0.149.0`, `/Users/yzhang/.local/bin/codex`)
- [x] pytest suite runnable via `uv run python -m pytest`

---

## Unit Tests

Implemented in tests/test_cli_adapter.py, tests/test_skill_translator.py, tests/test_mcp_deployer.py, tests/test_cli_init_selection.py during TASK-1158. Acceptance run = execute selections below and record results.

### TC-U1: Registry includes codex with all 10 config fields (AC-1.1, AC-1.2) — P0
| Item | Value |
|------|-------|
| Test | `tests/test_cli_adapter.py::TestCodexAdapter::test_bundled_registry_includes_codex` |
| Steps | Load service from bundled YAML → get_adapter('codex') |
| Expected | All 10 field values match spec AC-1.2 exactly |

### TC-U2: Auto-detection picks codex (AC-1.3) — P0
| Item | Value |
|------|-------|
| Test | `tests/test_cli_adapter.py::TestCodexAdapter::test_auto_detect_picks_codex_when_only_codex_installed` |
| Steps | No `cli` key; only `codex` on PATH (mocked) → get_active_adapter() |
| Expected | Active adapter name == `codex` |

### TC-U3: build_command produces codex exec form (AC-1.4) — P0
| Item | Value |
|------|-------|
| Test | `tests/test_cli_adapter.py::TestCodexAdapter::test_build_command_codex_exec` |
| Expected | `codex exec --dangerously-bypass-approvals-and-sandbox "test prompt"` |

### TC-U4: Verbatim skill translation + AGENTS.md generation (AC-2.1, AC-2.2) — P0
| Item | Value |
|------|-------|
| Tests | `tests/test_skill_translator.py::TestCodexTranslation` (4 tests), `tests/test_cli_init_selection.py::TestCodexInit::test_copy_skills_codex_verbatim` |
| Expected | Skills copied byte-identical to `.codex/skills/`; instructions template written to `AGENTS.md` |

### TC-U5: MCP deployment semantics (AC-3.1–3.3, AC-3.5, EC-1, EC-2) — P0
| Item | Value |
|------|-------|
| Tests | `tests/test_mcp_deployer.py::TestCodexTomlDeploy` (9 tests) |
| Expected | add via subprocess w/ correct argv + `--env`; skip existing; force re-add; not-installed → warn+skip; dry-run → no subprocess; per-server failure isolation; timeout recorded |

### TC-U6: YAML copies in sync (packaging guard) — P1
| Item | Value |
|------|-------|
| Test | `tests/test_cli_adapter.py::TestCodexAdapter::test_bundled_and_project_configs_in_sync` |
| Expected | `src/x_ipe/resources/config/cli-adapters.yaml` == `x-ipe-docs/config/cli-adapters.yaml` (wheel force-include) |

### TC-U7: Init MCP flow routes to deployer without target prompt (AC-3.4) — P0
| Item | Value |
|------|-------|
| Test | `tests/test_cli_init_selection.py::TestCodexInit::test_init_mcp_codex_uses_deployer_without_target_prompt` |
| Expected | deployer.deploy called with servers_to_merge + source_servers; no target-path prompt consumed |

## Integration Tests (real execution)

### TC-I1: `x-ipe init --cli codex` end-to-end (AC-4.1) — P0
| Step | Action | Expected |
|------|--------|----------|
| 1 | Run `x-ipe init --cli codex` in temp project (non-interactive: decline MCP via stdin) | Exit 0 |
| 2 | Read `.x-ipe.yaml` | `cli: codex`, `paths.skills: .codex/skills` |
| 3 | Check `AGENTS.md` at project root | File exists, non-empty |

### TC-I2: Real `codex mcp add` via MCPDeployerService, isolated CODEX_HOME (AC-3.1) — P0
| Step | Action | Expected |
|------|--------|----------|
| 1 | Temp project with `.github/copilot/mcp-config.json` (chrome-devtools); `CODEX_HOME=$TMP` |
| 2 | `deployer.deploy(codex_adapter)` | merged_count == 1, exit 0 |
| 3 | Read `$CODEX_HOME/config.toml` | `[mcp_servers.chrome-devtools]` with `command = "npx"`, args containing `chrome-devtools-mcp@latest` |
| 4 | User's `~/.codex/config.toml` mtime unchanged | No side effect on real config |

### TC-I3: Skip-existing against real codex (AC-3.2) — P1
| Step | Action | Expected |
|------|--------|----------|
| 1 | After TC-I2, deploy again without force | skipped_count == 1, merged_count == 0 |
| 2 | Deploy with force=True | merged_count == 1 (remove + re-add) |

### TC-I4: `--cli` help text lists codex (AC-4.2) — P2
| Step | Action | Expected |
|------|--------|----------|
| 1 | `x-ipe init --help` | help contains `codex` |

### TC-I5: `x-ipe upgrade --cli codex` migration (AC-4.1, EC-4) — P1
| Step | Action | Expected |
|------|--------|----------|
| 1 | Temp project initialized as copilot; add skills artifact |
| 2 | Run `x-ipe upgrade --cli codex` | Exit 0; `.x-ipe.yaml` cli → codex; skills migrated to `.codex/skills/` |

## Structured-Review Tests

### TC-S1: Deliverables complete and consistent — P1
Deliverables: [specification.md](x-ipe-docs/requirements/EPIC-027/FEATURE-027-F/specification.md), [technical-design.md](x-ipe-docs/requirements/EPIC-027/FEATURE-027-F/technical-design.md), [README.md](README.md) Multi-CLI section.
Checks: spec ACs traceable to code+tests; design matches implementation (no drift); README table lists codex for all three artifact types.

---

## Execution Results

**Executed:** 2026-08-21 · **Environment:** macOS, codex-cli 0.149.0, isolated `CODEX_HOME` for all real `codex mcp` invocations

### Unit (pytest) — 7/7 test cases, 20/20 tests passed

| TC | Result | Evidence |
|----|--------|----------|
| TC-U1 | ✅ Pass | `TestCodexAdapter::test_bundled_registry_includes_codex` — all 10 fields match AC-1.2 |
| TC-U2 | ✅ Pass | `test_auto_detect_picks_codex_when_only_codex_installed` |
| TC-U3 | ✅ Pass | `test_build_command_codex_exec` |
| TC-U4 | ✅ Pass | `TestCodexTranslation` 4/4 + `test_copy_skills_codex_verbatim` |
| TC-U5 | ✅ Pass | `TestCodexTomlDeploy` 9/9 |
| TC-U6 | ✅ Pass | `test_bundled_and_project_configs_in_sync` |
| TC-U7 | ✅ Pass | `test_init_mcp_codex_uses_deployer_without_target_prompt` |

### Integration (real execution) — 5/5 passed

| TC | Result | Evidence |
|----|--------|----------|
| TC-I1 | ✅ Pass | `x-ipe -p <tmp> init --cli codex` exit 0; `.x-ipe.yaml` `cli: codex`, `paths.skills: .codex/skills`; `AGENTS.md` created (192 lines) |
| TC-I2 | ✅ Pass | Real `codex mcp add` via deployer → `$CODEX_HOME/config.toml` contains `[mcp_servers.chrome-devtools]` with `command = "npx"`, `args = ["-y", "chrome-devtools-mcp@latest", "--isolated"]`; merged=1; user `~/.codex/config.toml` mtime unchanged |
| TC-I3 | ✅ Pass | Re-deploy no-force: merged=0 skipped=1; force: merged=1 (remove+re-add) |
| TC-I4 | ✅ Pass | `x-ipe init --help` shows `(copilot, opencode, claude-code, codex)` |
| TC-I5 | ✅ Pass | `upgrade --cli codex` exit 0; config cli/skills updated; `demo-skill` migrated verbatim to `.codex/skills/`; "Deployed 1 MCP server(s) for codex"; backup `copilot-20260821-100723` created. Note: upgrade's trailing interactive MCP prompt aborts on closed stdin — pre-existing behavior for ALL CLIs, not codex-specific |

### Structured-Review — 1/1 passed

| TC | Result | Evidence |
|----|--------|----------|
| TC-S1 | ✅ Pass | Every spec AC (1.1–4.2) maps to ≥1 executed TC above with definitive result; design Part 2 values asserted byte-exact by TC-U1; README Multi-CLI table lists codex for skills folder / instructions file / MCP config. Design Change Log added for the `source_servers` param |

### Metrics

| Type | Passed | Failed | Blocked |
|------|--------|--------|---------|
| unit | 7 | 0 | 0 |
| integration | 5 | 0 | 0 |
| structured-review | 1 | 0 | 0 |
| **Total** | **13** | **0** | **0** |

**Pass rate: 100%** (20 underlying pytest tests + 3 real-CLI scenarios + 1 review)
