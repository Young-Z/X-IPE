# Refactoring Analysis — FEATURE-027-F (Codex CLI Adapter)

> Task: TASK-1160 (Feature Closing) · Date: 2026-08-21 · Scope: feature / FEATURE-027-F
> Analysis only — no refactoring executed.

## Scope (expanded, stable after 3 iterations)

Implementation: `src/x_ipe/resources/config/cli-adapters.yaml`, `x-ipe-docs/config/cli-adapters.yaml`, `src/x_ipe/services/{cli_adapter_service,skill_translator,mcp_deployer_service}.py`, `src/x_ipe/cli/main.py`
Expanded to: `src/x_ipe/core/scaffold.py` (parallel `merge_mcp_config`), `src/x_ipe/routes/config_routes.py`, `src/x_ipe/app.py`, `src/x_ipe/services/__init__.py`, `src/x_ipe/tracing/`, `tests/test_cli_migration.py`, `README.md`

## Quality Evaluation

| Dimension | Score | Status |
|---|---|---|
| Requirements | 9/10 | aligned |
| Features/spec | 9/10 | aligned |
| Tech spec | 8/10 | aligned (upgrade-path gap — since fixed, see below) |
| Test coverage | 7/10 | needs_attention (cli/main.py migration/upgrade flows now partially guarded; broader flows remain manual-only) |
| Tracing | 9.5/10 | aligned |
| Code alignment | 4/10 | critical (main.py size/SRP debt, pre-existing, feature widened) |

**Overall quality score: 8/10** (weighted 7.95)

## Key Gaps

1. ~~`upgrade` with codex active would JSON-overwrite `~/.codex/config.toml` via `scaffold.merge_mcp_config`~~ — **FIXED during Feature Closing**: upgrade now routes `codex-toml` through `MCPDeployerService.deploy()`; regression guard `TestCodexUpgrade::test_upgrade_mcp_codex_uses_deployer_never_scaffold_merge` (red/green verified).
2. DRY: two parallel MCP merge implementations (`ScaffoldManager.merge_mcp_config` vs `MCPDeployerService.deploy` JSON path) — root cause of gap 1. Open.
3. `src/x_ipe/cli/main.py` 1002 lines (>800 threshold); `init`/`upgrade`/`_handle_cli_migration` each >50 lines. Pre-existing, feature widened. Open.
4. Migration/upgrade flows rely on one-time manual evidence plus the single new guard; `tests/test_cli_migration.py` codex case still absent (file's existing tests fail as part of the 54-failure pre-existing baseline). Open.
5. Minor: `skill_translator.py` codex branch identical to else-fallback (design-mandated explicitness). No project quality baseline document exists.

## Suggestions

| # | Goal | Priority | Target |
|---|---|---|---|
| 1 | ~~Route upgrade codex-toml through deployer~~ | ~~P0~~ | **Done in Feature Closing** |
| 2 | ~~Guard test for upgrade codex path~~ | ~~P0~~ | **Done in Feature Closing** |
| 3 | Collapse dual JSON merge: `scaffold.merge_mcp_config` delegates to (or is replaced by) `MCPDeployerService.deploy` | P1 | `src/x_ipe/core/scaffold.py:251-352` vs `src/x_ipe/services/mcp_deployer_service.py` |
| 4 | Split `main.py` < 800 lines / functions < 50 lines: extract `cli/migration.py`, `cli/mcp_flow.py`, `cli/language.py`, `cli/serve.py` | P1 | `src/x_ipe/cli/main.py` |
| 5 | KISS: collapse `translate_skills` claude-code/codex branches; automate codex migration test once `test_cli_migration.py` baseline is repaired | P2 | `src/x_ipe/services/skill_translator.py`, `tests/test_cli_migration.py` |

## Constraints

`.x-ipe.yaml` format, adapter registry schema (10 fields), `MCPDeployResult` semantics, `/api/config/cli-adapter` response shape, CLI flags, JSON-format output byte-compatibility, EC-4 (never rewrite `~/.codex/config.toml` outside `codex mcp`), 20+1 FEATURE-027-F tests green, 54 pre-existing baseline failures unchanged.

**Verdict: refactoring recommended — yes (P1 items); the only P0 hazard was fixed inline during closing.**
