# TASK-6749 — CLI and callback test semantic audit

Date: 2026-10-14. Bounded test-only handoff; not task closure or release approval.

## Authority, scope and objective

The current user request supplies TASK-6749 identity/readiness and authorizes only
the four test modules below and this fragment. No production, mirror, board,
memory or Git operations were performed. No skill package was edited. The shared
lifecycle and code-refactor procedures were loaded; this is a disclosed local
analysis/test-sync adapter, not a claimed full-tool operation or publication.
The caller retains lifecycle/board/completion ownership. Clear supplied authority
required no additional question, DAO dispatch or successor registration.

Goal: give maintainers trustworthy release-triage evidence by separating broken
fixtures/import targets/environment from stale expectations, while preserving
documented CLI destinations, copied content, backups and dry-run behavior.
Engineering evidence is reported below; stakeholder outcome/coverage scores are
not measured. No requirements were rewritten to bless implementation behavior.

Authorized modified tests:

- [tests/test_cli_init_selection.py](../../tests/test_cli_init_selection.py)
- [tests/test_cli_language.py](../../tests/test_cli_language.py)
- [tests/test_cli_migration.py](../../tests/test_cli_migration.py)
- [tests/test_ui_callback.py](../../tests/test_ui_callback.py)

## Inspected authority

| ID | Source | Application |
| --- | --- | --- |
| S1 | [027-B specification](../requirements/EPIC-027/FEATURE-027-B/specification.md), [027-C specification](../requirements/EPIC-027/FEATURE-027-C/specification.md), [adapter registry](../config/cli-adapters.yaml) | Init selects an adapter; instructions use its declared path. Current OpenCode is root **Agents.md**, skills remain .opencode/skills. Earlier 027-A design examples are not the current registry. |
| S2 | [027-F specification](../requirements/EPIC-027/FEATURE-027-F/specification.md), [closing report](../requirements/EPIC-027/FEATURE-027-F/closing-report.md) | Codex remains root **AGENTS.md**. Closing review explicitly reconciled other adapters to registry values, including OpenCode Agents.md. Do not change Codex's path. |
| S3 | [027-E specification](../requirements/EPIC-027/FEATURE-027-E/specification.md), [CLI implementation](../../src/x_ipe/cli/main.py), [skills implementation](../../src/x_ipe/core/skills.py) | Validate CLI names, skip same-CLI migration, preserve backups, update config, retain dry-run and continue normal skills sync. Interactive skill-update choices must actually be answered. |
| S4 | [028-B CR-001](../requirements/EPIC-028/FEATURE-028-B/CR-001.md), [current EN instructions](../../src/x_ipe/resources/copilot-instructions-en-no-dao.md), [current ZH instructions](../../src/x_ipe/resources/copilot-instructions-zh-no-dao.md), [project instructions](../../.github/copilot-instructions.md) | Latest language CR replaces marker extraction with direct localized-file copying. Current instruction authority requires dynamic discovery from skill descriptions/frontmatter and prohibits a hardcoded registry; the older keyword-table wording is stale. |
| S5 | [058-F CR-001](../requirements/EPIC-058/FEATURE-058-F/CR-001.md), [current specification](../requirements/EPIC-058/FEATURE-058-F/specification.md), [callback implementation](../../.github/skills/x-ipe-tool-ontology/scripts/ui-callback.py) | Actual per-port HTTP callback uses localhost, bearer token, JSON payload and one retry. Token precedence is CLI flag, environment, script-relative instance file. No production proxy/URL/token logic changed. |
| S6 | [058-F CR-002](../requirements/EPIC-058/FEATURE-058-F/CR-002.md) | Latest callback-related CR says the callback already passes enriched subgraphs through unchanged; test string nodes, mixed edges and virtual-node metadata without changing networking or production transformations. |

The 028-B specification still contains pre-CR marker/keyword prose; CR-001 and
current source instructions bound this audit. The 058-F specification also retains
some session-id rows alongside its explicit refined per-port broadcast contract.
These are documentation drift, not authority to invent a session-id fixture or
claim complete feature acceptance. Neither specification was edited.

## Baseline and actual root causes

The supplied historical terminal log ending in
copilot-terminal-output-d94c5095-bb40-41e9-8f5e-7cbf6adfc7b8.txt was inspected,
including the actual CLI failures and callback HTTP 502 exceptions. Its whole-suite
result was **58 failed, 3917 passed, 24 skipped, 68 warnings**. It is historical
evidence, not a fresh full-suite result or authority from the unreliable Explore
report. No unrelated failure in that log was rewritten here.

Configured interpreter: workspace .venv, Python **3.12.9**. All main runs used
normal `python -m pytest`, without `--noconftest`, custom collection, import skips,
warning suppression, skips or xfails. Repository-wide discovery found **no
conftest** outside the virtual environment/dependency directory; none was added.

Unchanged baseline: run the four authorized modules with `-q --tb=long`:
**17 failed, 66 passed**, exit 1, 18.43 s. Exact failure categories:

- **3 OpenCode instruction tests** expected the obsolete nested destination;
  scaffold recorded root Agents.md.
- **1 ZH test** demanded an arbitrary keyword-table phrase and a fixed skill name,
  although current localized instructions explicitly describe dynamic discovery.
- **9 migration tests** reported exit 1. Actual captured invocation traceback was
  `click.exceptions.Abort` at the skill-update `click.prompt`, converted to
  `SystemExit(1)` by Click; output ended in the unanswered “Choose an option”.
- **4 callback tests** had actual `HTTP Error 502: Bad Gateway`, not a silent
  startup/ready-state failure.

### Import and prompt evidence

`importlib.import_module('x_ipe.cli.main')` and the src-prefixed import resolve to
the same physical [CLI source](../../src/x_ipe/cli/main.py), but are **different
module objects**. Their callback `__module__` values differ. The installed entry
point in [pyproject.toml](../../pyproject.toml) uses the canonical package.
Patching the canonical service did not affect a command from the duplicate import.

Before editing, four actual invocation variants were run with a disposable
project and a known adapter service. All requested migration to OpenCode:

| Invoked command module | Skill-update input | Exit | Canonical service factory calls | Actual outcome |
| --- | --- | --- | --- | --- |
| src-prefixed duplicate | empty | 1 | 0 | Migration wrote Agents.md, then prompt aborted |
| src-prefixed duplicate | `1` plus newline | 0 | 0 | Finished, but canonical mock was bypassed |
| canonical package | empty | 1 | 1 | Correct patch target, still prompt aborted |
| canonical package | `1` plus newline | 0 | 1 | Correct target and answered prompt |

Thus changing only the import or only the prompt would not establish test isolation.
The revised migration module imports the canonical CLI via importlib. A known
explicit registry disables host detection for no-flag cases. A disposable
package-only skill replaces host/bundled package discovery, not the sync function;
normal discovery, copy and hash persistence still execute. Tests choose `1` when
only migration is in scope; no-flag and continuation tests choose `2` and assert
the actual package-only skill was synced. No import is skipped.

### Proxy and token evidence

The actual subprocess probe found **no HTTP/HTTPS/ALL/NO_PROXY environment keys**
in the inherited environment, but `urllib.request.getproxies()` returned schemes
**http, https, socks** from macOS configuration. With both `NO_PROXY` and
`no_proxy` set to localhost/127.0.0.1/::1, schemes were **no**. No proxy values,
credentials or real internal token were printed. `proxy_bypass('localhost')`
returned true in both probes, so that function alone did not establish which
route the POST would take.

The decisive observation was actual HTTP behavior: scoped tests with the
loopback-only environment received exactly one POST at the bound server; a
fresh-process negative control removing only the fixture's NO_PROXY keys
reproduced **HTTP 502 twice** and exit 1. Restoring the unchanged fixture passed.
No readiness sleep, polling, retry inflation or production networking patch was
used. HTTPServer binds/listens before its serving thread starts; accepted socket
backlog is not a startup timing hypothesis. Teardown joins/closes the server.

The old “instance file” test did **not** test its file: it set an environment token,
and the production file lookup is relative to the script, not cwd. The corrected
test copies identical script bytes into a disposable root and creates the actual
script-relative instance fixture. Separate tests check environment lookup, CLI
precedence and no-token failure without reading a real project token.

An added bound-but-not-listening retry fixture was rejected after actual macOS
connects timed out (15-second test deadline; first warning was Errno 60). A focused
subprocess probe of a released ephemeral port instead produced **Errno 61,
Connection refused**. The final retry test uses that observed fixture and asserts
one warning, attempt 1/2, one final error and exactly two attempted failures. It
does not assert a random fixed port is unused. The released-port approach has a
small OS reassignment race; an unrelated listener would fail the assertions rather
than be accepted as success. Production's existing one-second retry remains.

## Changed-test ledger

Methods are named within their linked module; the table distinguishes stale
contract corrections from fixture/import/environment fixes and stronger controls.
Existing test IDs remain except the keyword-table test is renamed to describe
dynamic discovery. No original scenario was deleted.

### Init — [tests/test_cli_init_selection.py](../../tests/test_cli_init_selection.py)

| Test | Classification and reason | Preservation / negative assertion | Authority |
| --- | --- | --- | --- |
| `TestMCPPathResolution.test_init_mcp_uses_opencode_path` | Import/prompt fixture defect; previously used duplicate CLI, missed language prompt and conditionally asserted only if a file happened to exist | Canonical patch, fixed single-server resource, explicit language, accept default target rather than supply one; require exit 0, exact nested server JSON and no Copilot configs | S1; actual init invocation |
| `test_instructions_opencode_targets_opencode_path` | Stale nested path; explicit known registry declares root Agents.md | Exact created-path list, actual file bytes equal canonical no-DAO template; obsolete nested and Copilot targets absent | S1, S2 |
| `test_instructions_opencode_skips_if_exists` | Stale fixture location did not exercise root-path skip | Root content preserved, exact skipped list, no created entries, seeded legacy nested file untouched | S1 |
| `test_instructions_opencode_dry_run_no_file` | Stale reported destination | Exact root planned path, no skipped entries and entire empty project still empty | S1 |

The adapter fixture locks OpenCode to Agents.md and nested MCP format. Codex tests
and AGENTS.md assertions are unchanged. No false case-sensitive “AGENTS.md absent”
assertion is made on this macOS filesystem; expected spelling is checked through
the explicit registry and recorded path.

### Language — [tests/test_cli_language.py](../../tests/test_cli_language.py)

| Test / fixture | Classification and reason | Preservation / negative assertion | Authority |
| --- | --- | --- | --- |
| `initialized_project` | Stale flat skills-key fixture | Use current paths.skills mapping; retain cli/language scalars | S1, S4 |
| `test_extracts_en_section` | Historical extraction name retained, vacuous existence guard removed | Require real file and exact EN resource bytes; no LANG marker | S4 / CR-001 |
| `test_extracts_zh_section` | Same | Exact ZH bytes, no marker, unequal to EN | S4 / CR-001 |
| `test_zh_contains_dynamic_skill_discovery` (formerly `test_zh_contains_keyword_mapping`) | Stale hardcoded phrase/table contract | Both discovery globs and frontmatter reference required; dynamically parse task-skill YAML, require mapping, directory-consistent name and nonempty string description | S4 / current source instructions |
| `test_en_does_not_contain_zh_keywords` | Replace arbitrary phrase absence with source/selection semantics | Exact EN bytes, unequal ZH source and task-skill discovery guidance present | S4 |
| `test_init_with_lang_zh` | Vacuous config-existence guard | Require YAML mapping, zh scalar, copilot scalar and exact skills path | S1, S4 |
| `test_upgrade_with_lang_zh` | Routing assertions used to pass after command aborted | Answer skill-update prompt, explicitly exclude unrelated MCP prompt; require exit 0 and unchanged exact language helper calls | S4; actual second-prompt Abort observed |

Dynamic YAML metadata checks are schema/discovery evidence, not proof of autonomous
agent routing or natural-language understanding. They introduce no fixed keyword
table. Existing invalid-language, defaults and dry-run controls remain.

### Migration — [tests/test_cli_migration.py](../../tests/test_cli_migration.py)

All sixteen original command tests now invoke the canonical package, with the
same patch target and deterministic shared package/detection fixtures. The API
route test is unchanged. Old/global adapters in individual tests remain explicit
custom adapter fixtures; they are not presented as current default registry values.
OpenCode instruction fixtures now consistently declare root Agents.md.

| Test | Correction and retained/added assertion | Authority |
| --- | --- | --- |
| `test_ac_1_1_accepts_valid_cli_name` | Answer choice 1; exit 0 with diagnostic output/exception, service factory actually called, OpenCode migration still reported | S3 |
| `test_ac_1_2_same_cli_skips_migration` | Answer choice 1; same-CLI message, config bytes unchanged, no migration backup | S3 AC-1.2 |
| `test_ac_1_3_unknown_cli_raises_error` | Correct import so bad-name test exercises patched registry; require Click exit 2, exact available-name error and no backup | S3 AC-1.3 |
| `test_ac_2_1_backs_up_skills_folder` | Answer choice 1; exactly one old-CLI timestamp backup; verify backed-up skill/instruction content and both original sources preserved | S3 AC-2.1/2.2 |
| `test_ac_2_4_dry_run_no_backup` | Canonical import; retain no-backup assertion, check old source content and absent target instructions | S3 AC-2.4 |
| `test_skills_copied_to_new_folder` | Answer choice 1; actual target skill exists with exact original content | S3 |
| `test_instructions_copied_to_new_location` | Answer choice 1; require actual root Agents.md with original instruction content; seeded obsolete nested file and old source untouched | S1, S3 |
| `test_dry_run_no_copy` | Canonical import; no target skills/instructions, exact planned instruction path in output and full file-name/byte snapshot unchanged | S3 AC-2.4/3.2 |
| `test_force_rerun_scans_other_cli_folders` | Canonical import and known root destination; original force-scan/copy/content assertions unchanged | S3; existing force-rerun regression |
| `test_ac_3_1_updates_config_cli_key` | Answer choice 1; actual YAML cli equals opencode | S3 AC-3.1 |
| `test_ac_3_3_migration_updates_skills_path` | Answer choice 1; exact configured skills path remains required | S1, S3 |
| `test_ac_3_2_dry_run_no_config_write` | Canonical import; add successful exit and byte-exact config preservation to old-cli assertion | S3 AC-3.2 |
| `test_ec_1_no_config_errors` | Correct import and remove permissive OR assertion; require exit 1 and documented init-first diagnostic | S3 EC-1 |
| `test_ac_5_1_no_cli_flag_runs_normal_upgrade` | Known existing-CLI default, answer default selection then choice 2; no migration and actual package-only skill copied | S3 AC-5.1; current prompt flow |
| `test_upgrade_prompts_cli_selection_triggers_migration` | Patch helpers on same canonical module; answer choice 1 and require exit 0 plus exactly one migration call to opencode | S3; existing prompt regression |
| `test_upgrade_continues_after_migration` | Answer choice 2; require actual sync count/content in addition to old continuation message | S3 AC-5.1; current sync flow |
| **New:** `test_project_scoped_mcp_backup_preserves_content` | Known current project-scoped Copilot fixture, exactly one backup, original and backup MCP bytes equal; instruction backup content also preserved | S3 AC-2.3; current registry |

### Callback — [tests/test_ui_callback.py](../../tests/test_ui_callback.py)

All eight original scenarios use loopback proxy isolation and no inherited token;
success assertions remain strict. Two new token scenarios explain the count delta.

| Test | Correction / control | Authority |
| --- | --- | --- |
| `test_successful_post` | Environment defect; require exit 0, one exact endpoint POST, exact bearer/content-type/localhost host, original results/subgraph/query/scope and valid UUID | S5 |
| `test_output_contains_query_and_timestamp` | Shared proxy fixture only; original exit/log assertions unchanged | S5 |
| `test_missing_results_file` | Shared fixture; require old nonzero/error assertion and **zero HTTP requests** | S5 |
| `test_invalid_json_file` | Shared fixture; same zero-request negative control | S5 |
| `test_connection_failure_retries_and_fails` | Replace random port assumption with observed released-port refusal; strict one-warning/one-error/attempt counts | S5 |
| `test_accepts_matches_field_from_search_output` | Environment defect; one POST, exact matches-to-results preservation, exact enriched subgraph including virtual-node metadata, same query/scope | S5, S6 |
| `test_token_from_instance_file` | Fixture was mislabeled environment lookup; now real script-relative disposable instance file with environment absent | S5; actual token resolver |
| `test_no_token_exits_with_error` | Isolated script-relative root avoids accidental real-file token fallback; exact exit 1/no-token diagnostic and zero HTTP requests | S5 |
| **New:** `test_token_from_environment` | Separate environment-lookup scenario, exact fake bearer token and one request | S5 |
| **New:** `test_cli_token_takes_precedence` | Competing CLI/environment/file tokens; require exact CLI bearer and one request | S5 |

## Executed negative controls — no on-disk production mutation

Five fresh child processes ran normal pytest on individual exact node IDs with a
process-local hook temporarily altering behavior/environment. Each returned pytest
exit 1 with **one expected failure**, not a skip/xfail. Controls were not used for
the passing final suite; sources remained unchanged. Exact method names below are
the same names in the ledger's linked modules.

| Node | Deliberate defect | Actual failed assertion |
| --- | --- | --- |
| `TestCLISpecificInstructions.test_instructions_opencode_targets_opencode_path` | Instruction writer no-op | Empty created list differs from expected root path |
| `TestCopilotInstructionsExtraction.test_extracts_zh_section` | Force EN source while ZH requested | Actual target bytes differ from ZH source |
| `TestConfigUpdate.test_ac_3_1_updates_config_cli_key` | Migration handler no-op | YAML cli remains copilot, not opencode |
| `TestSkillsMigration.test_dry_run_no_copy` | Force actual migration despite dry-run | Target skill directory exists unexpectedly |
| `TestUICallbackSuccess.test_successful_post` | Remove only NO_PROXY fixture keys | Actual subprocess HTTP 502 on both attempts, exit 1 |

The exact five nodes then ran unmutated at the final test revision: **5 passed**,
exit 0, 0.74 s. These repeated nodes are not added to unique-test totals.

## Run ledger and counts

Main command shape: configured interpreter, `-m pytest`, the four authorized
modules in init/language/migration/callback order, `-q --tb=long`. Adjacent command
uses the three linked unmodified modules below with `-q --tb=short`.

| Run | Result | Interpretation |
| --- | --- | --- |
| Unchanged four-module baseline | 17 failed, 66 passed; exit 1; 18.43 s | 83 original tests, all collected/executed |
| Intermediate collection attempts | 1 collection error each | Test-edit indentation issue; corrected, never called a pass |
| Intermediate fixture verification | 1 failed, 83 passed | Bound non-listening macOS port caused timeout; investigated, not hidden |
| First complete scoped pass | 85 passed; exit 0; 7.35 s | Two new token tests; before new MCP-backup control |
| Strengthened language exit check | 1 failed, 85 passed | Exposed unrelated unanswered MCP prompt; bounded with explicit no-MCP flag |
| **Final four-module run** | **86 passed; exit 0; 7.41 s** | All original scenarios plus three new controls |
| Unchanged adjacent regressions | **106 passed; exit 0; 0.32 s** | Adapter/translator/deployer compatibility, not whole repository |
| Negative controls | 5 deliberately failed individual runs | Assertions reject violations/environment contamination |
| Exact control-node restoration | 5 passed; exit 0; 0.74 s | Repeated coverage, not five additional unique tests |

Final scoped distribution: **36 init + 22 language + 18 migration + 10 callback =
86**. Baseline was **36 + 22 + 17 + 8 = 83**. Three added tests are one
project-scoped MCP backup and two token-resolution controls; renaming the stale
keyword-table test does not increase the count. All **17 baseline failures** pass
under corrected authoritative expectations/fixtures. Scoped plus adjacent total:
**192 unique passing tests**, zero skips/xfails/deselections. No warning filter was
installed and final runs emitted no warning summary. Historical whole-suite skips,
warnings and failures remain historical, unmodified evidence; no whole-suite-green
claim or release approval is made.

Adjacent modules:
[tests/test_cli_adapter.py](../../tests/test_cli_adapter.py),
[tests/test_skill_translator.py](../../tests/test_skill_translator.py),
[tests/test_mcp_deployer.py](../../tests/test_mcp_deployer.py).

## Revision and preservation evidence

Before/after protected inventory covers 5090 regular files under production src,
GitHub skills/instructions and Claude/Codex mirrors; excludes only Python bytecode
cache directories and bytecode files. Algorithm: SHA256 of Python repr of sorted
(workspace-relative POSIX path, file SHA256) pairs. Both fingerprints equal:

**0b3f14270eaff7258dc1708e18d4e915a79dd580da0acea12ee576b2a62bd7f4**.

No production/mirror bytes changed. No board, memory or Git tool/CLI was invoked.
pytest creates ordinary runtime caches and disposable test roots; these are not
source edits. The scope did not authorize release/promotion or full-suite repairs.

| Tested file | Final SHA256 |
| --- | --- |
| [init tests](../../tests/test_cli_init_selection.py) | cd52c1320804acece09e1a848bdeadf05d58f5621420fa505085b76efc7287c5 |
| [language tests](../../tests/test_cli_language.py) | 9381f1d01ee1af6df981a74c3b333b2aa4ec504a5eace427cf077536878b586e |
| [migration tests](../../tests/test_cli_migration.py) | 237dd014a51f23469a8be6550af927149be6b6e30ebc76553a03ae3333079e90 |
| [callback tests](../../tests/test_ui_callback.py) | 0a4e8f6573a90f8713dafca6793b80c799531f32c5cf6ba587dc7c4689e6fea7 |
| [CLI source](../../src/x_ipe/cli/main.py) | abff68503e53d2f75d1093940e01f6aa755221248ccd8b0e71b7897138585091 |
| [scaffold source](../../src/x_ipe/core/scaffold.py) | 514480149c0d3a55113fdd9f9bb72bccd641c0f5f3602b69d7aca59173859f85 |
| [skills source](../../src/x_ipe/core/skills.py) | 0f4174158047c9eb536b35335eae41c042b468031483313b7d12161cc32e3956 |
| [adapter source](../../src/x_ipe/services/cli_adapter_service.py) | b69eaf6b70c9850d649e6d5ecdbaea53b85cfc7852bd273aecac8be9476f3d16 |
| [translator source](../../src/x_ipe/services/skill_translator.py) | 5e1796d6b10496d361d6d1a9d12d05b53d8163128ddd2ab87ce1c2d743061c1c |
| [callback script](../../.github/skills/x-ipe-tool-ontology/scripts/ui-callback.py) | 8408952bb31a3daca5d81a9079015fc311cb9f3265d94f40bc79ad9a2eeee45a |
| [project adapter registry](../config/cli-adapters.yaml) | d5bb99e326575dc6fabc45b40219617abfb473502d0b3e88c265e040bf0627a4 |
| [bundled adapter registry](../../src/x_ipe/resources/config/cli-adapters.yaml) | d5bb99e326575dc6fabc45b40219617abfb473502d0b3e88c265e040bf0627a4 |
| [instruction template](../../src/x_ipe/resources/templates/instructions-template-no-dao.md) | db317ea5dceaf0fc567a814250e4ed348b1543af8e989b35c92abc5000bb8962 |
| [EN resource](../../src/x_ipe/resources/copilot-instructions-en-no-dao.md) | db317ea5dceaf0fc567a814250e4ed348b1543af8e989b35c92abc5000bb8962 |
| [ZH resource](../../src/x_ipe/resources/copilot-instructions-zh-no-dao.md) | b4657d305b8035787a9de709e068939c691cd1999988b0619b3e0ed5817119c7 |
| [package configuration](../../pyproject.toml) | 25f054e4525d6f8f7f8255b3f7ad8b8699e19abef3b97c63963d9036e0fde1d6 |
| [027-E specification](../requirements/EPIC-027/FEATURE-027-E/specification.md) | 99730c85cb0a8ebe61f0bdb104649aa382bbe703b5f380bd8845225d2d91f429 |
| [027-C specification](../requirements/EPIC-027/FEATURE-027-C/specification.md) | 333c920a97fb23081d491800484e4ca76edf12e1b22b91a0f3e585260cb51dc8 |
| [027-F specification](../requirements/EPIC-027/FEATURE-027-F/specification.md) | ba3ef61b37533906e663446bdc07c6db48d647c70a6d01136257a46f7f271315 |
| [027-F closing review](../requirements/EPIC-027/FEATURE-027-F/closing-report.md) | b9a3195ebac2cd570f5e5d68ba21f017998928125cb17b57bfdfcd2b4836101b |
| [028-B CR-001](../requirements/EPIC-028/FEATURE-028-B/CR-001.md) | cc09d68e525ec176d094b3053c9b7fd74ffe0879b6e6a1e75da4cf4aaebc8de0 |
| [058-F CR-002](../requirements/EPIC-058/FEATURE-058-F/CR-002.md) | b5360e2b0047602600dd6bc4a0918a5948389d223ece94c9c1150b599cbaecca |

## Handoff limits

No genuine production defect was established by these scoped failures after the
observed fixture/import/environment corrections. This is not evidence that all
features or the remaining historical failures are correct. Genuine documented
deviations encountered by the owner must remain red until an authorized bug fix;
do not normalize them into permissive assertions. The task owner must separately
review this slice and remaining whole-suite semantics before release. Independent
review/publication was not performed or claimed. No follow-on board state was
written.
