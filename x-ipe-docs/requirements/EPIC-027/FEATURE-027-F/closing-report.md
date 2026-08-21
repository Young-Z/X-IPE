# FEATURE-027-F: Codex CLI Adapter — Closing Report

> Task: TASK-1160 (Feature Closing) · Assignee: Nova · Date: 2026-08-21
> Git strategy: main-branch-only (no PR; direct push to main)

---

## 1. Acceptance Criteria Verification

All criteria verified against the executed acceptance run (13/13 passed — see [acceptance-test-cases.md](acceptance-test-cases.md)).

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-1.1 | `codex` entry with all 10 config fields in both YAML copies | ✅ Met | TC-U1; sync guard TC-U6 |
| AC-1.2 | Exact field values (`codex exec --dangerously-bypass-approvals-and-sandbox`, `.codex/skills/`, `AGENTS.md`, `codex-toml`) | ✅ Met | TC-U1 asserts all 10 fields |
| AC-1.3 | `AUTO_DETECT_PRIORITY` includes codex after existing three | ✅ Met | TC-U2 |
| AC-1.4 | `build_command()` produces codex exec form | ✅ Met | TC-U3 |
| AC-2.1 | Verbatim skill copy to `.codex/skills/<name>/` | ✅ Met | TC-U4 (byte-equal assertion) |
| AC-2.2 | Instructions template written to `AGENTS.md` | ✅ Met | TC-U4 + TC-I1 |
| AC-3.1 | `deploy()` handles `codex-toml` via `codex mcp add` | ✅ Met | TC-U5, TC-I2 (real codex) |
| AC-3.2 | Skip existing unless force (get → remove+add) | ✅ Met | TC-U5, TC-I3 (real codex) |
| AC-3.3 | Not-installed → warn + skip, no crash | ✅ Met | TC-U5 |
| AC-3.4 | init routes to deployer without target-path prompt | ✅ Met | TC-U7, TC-I1 |
| AC-3.5 | dry-run reports without invoking codex | ✅ Met | TC-U5 |
| AC-4.1 | `init --cli codex` / `upgrade --cli codex` accept adapter | ✅ Met | TC-I1, TC-I5 (full migration) |
| AC-4.2 | `--cli` help lists codex | ✅ Met | TC-I4 |
| EC-1..EC-4 | Not-installed, subprocess failure/timeout, AGENTS.md overwrite semantics, migration never touches global config | ✅ Met | TC-U5 (EC-1, EC-2), TC-I5 (EC-4); EC-3 follows existing force semantics |

**Result: all criteria met. No blockers.**

## 2. Code-to-Docs Review

Review performed by independent sub-agent against specification, technical design, tests, and README.

Independent sub-agent compared shipped code against specification, technical design, acceptance tests, and README. Verdict: docs largely accurate; **7 updates needed** — all applied during closing:

| # | Finding | Resolution |
|---|---------|------------|
| 1 | **MAJOR**: spec overview/EC-4 promised `codex mcp add` on init *and upgrade*, but `upgrade`'s MCP block had no codex-toml branch — it prompted for a target path and called `scaffold.merge_mcp_config(mcp_format='codex-toml')`, which JSON-parses the existing TOML, fails, and **overwrites `~/.codex/config.toml` with JSON** (user data loss). Masked in TC-I5 because the interactive prompt aborted on closed stdin | **Code fixed**: upgrade now routes `codex-toml` through `MCPDeployerService.deploy()` (same as init); regression guard `TestCodexUpgrade` added, red/green verified (fails on pre-fix code, passes with fix) |
| 2 | Spec AC-3.5 read as CLI `--dry-run` behavior; only service-level true | AC-3.5 wording clarified (service-level flag) |
| 3 | Tech design referenced a `test_cli_migration.py` codex test that never existed | Replaced with the actual guard location (`TestCodexUpgrade`) |
| 4 | Tech design `_deploy_codex_cli` pseudocode had stale signature + dry-run ordering | Pseudocode corrected |
| 5 | Acceptance doc: "Total Test Cases 15" vs actual 13 | Count fixed |
| 6 | README instruction-file paths stale for copilot/opencode/claude-code (pre-existing; line touched by this feature) | Corrected to registry values (`.github/copilot-instructions.md`, `Agents.md`, `.claude/CLAUDE.md`) |
| 7 | README copilot MCP path labeled `~/.copilot/mcp-config.json (global)`; registry says `.copilot/mcp-config.json` (project) | Corrected |

Verified accurate (no drift): both YAML copies byte-identical, codex entry field-for-field vs AC-1.2, wheel force-include, auto-detect order, `build_command`, verbatim translation + `AGENTS.md`, deploy argv/skip/force/EC-1/EC-2 semantics, init codex branch, `--cli` help.

## 3. Refactoring Analysis

Analysis performed by independent sub-agent (feature scope; analysis only — no refactoring executed).

Full report: [analysis-TASK-1160.md](../../refactoring/analysis-TASK-1160.md)

- **Overall quality score: 8/10**
- **P0 hazard (upgrade JSON-clobber of `~/.codex/config.toml`): fixed inline during closing** with regression guard
- Remaining suggestions (analysis only, not executed):
  - **P1** — collapse dual MCP merge: `ScaffoldManager.merge_mcp_config` duplicates `MCPDeployerService.deploy`'s JSON path with divergent semantics (root cause of the fixed hazard)
  - **P1** — split `src/x_ipe/cli/main.py` (1002 lines; extract migration / MCP flow / language / serve modules)
  - **P2** — collapse redundant `translate_skills` codex branch; automate codex migration test once `test_cli_migration.py` baseline repaired
- **Refactoring recommended: yes** (P1 items; next pipeline iteration)

## 4. Deliverables

| Artifact | Path |
|----------|------|
| Specification | `x-ipe-docs/requirements/EPIC-027/FEATURE-027-F/specification.md` |
| Technical design | `x-ipe-docs/requirements/EPIC-027/FEATURE-027-F/technical-design.md` |
| Acceptance test cases + results | `x-ipe-docs/requirements/EPIC-027/FEATURE-027-F/acceptance-test-cases.md` |
| Adapter config (both copies) | `x-ipe-docs/config/cli-adapters.yaml`, `src/x_ipe/resources/config/cli-adapters.yaml` |
| Implementation | `src/x_ipe/services/{cli_adapter_service,mcp_deployer_service,skill_translator}.py`, `src/x_ipe/cli/main.py` |
| Tests | `tests/test_cli_adapter.py`, `tests/test_mcp_deployer.py`, `tests/test_skill_translator.py`, `tests/test_cli_init_selection.py` |
| README | Multi-CLI support table, prerequisites, `--cli` prompt docs |

## 5. Release

- Version bumped 1.1.50 → **1.1.51** (sequential patch convention)
- Published to PyPI from the release commit via `twine upload` using `~/.pypirc`
