---
name: x-ipe-task-based-feature-acceptance-test
description: Verify all feature types against source goals/subgoals and every scoped AC with revision-bound evidence. Execute actual browser UI, backend API, CLI, library, integration and structured skill checks using enabled testing capabilities. Return honest delivery/outcome results and conditional quality/closing handoff. Use after Code Implementation. Triggers on requests like "run acceptance tests", "test feature", "execute acceptance tests".
---

# Task-Based Skill: Feature Acceptance Test

## Purpose

Verify one approved capability, not successful activities:
1. Trace source/parent goals and stable story/subgoal/ACs to every original assertion.
2. Execute suitable all-type checks or validate explicit hash-bound reusable evidence.
3. Report verified engineering delivery separately from stakeholder outcome or not measured.
4. Return original outputs and conditional recommendations to one owner.

## Important Notes

Load the [single-loop delivery policy](.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md)
once in the current context. Execute this skill in the same agent loop; another
skill is expertise, not a new agent. Use proportional checks and reuse current
evidence; independent review is conditional on concrete risk, not the skill name.

BLOCKING: Load `x-ipe-workflow-task-execution` and the
[common lifecycle contract](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md).
Direct entry calls Orient/Plan for supplied task/original context without recursively dispatching
this skill. Reuse readiness; one owner handles task/category/feature/app writes,
Git and routing. Delegates receive same task/readiness and test-only ownership
adapter or block; no duplicate task, close/commit/route or successor invocation.

BLOCKING: Adopt the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
at acceptance coverage/evidence. One feature or approved standalone scope, all scoped ACs,
source/parent/story/subgoal/constraints and original assertions in existing report.
All-required branches remain covered; alternatives are selected means, not extra
features. No invented goals/KPIs/targets/manual confirmation/observations or
activity-count success. Source-derived qualitative outcome scenarios suffice.
Passing tests are not goal achievement. Stakeholder impact not observed explicitly
stays not measured, not failed or achieved; automation/fixtures/DAO/approval do
not observe stakeholder benefit. No new goal database, board/output/action schema.

CRITICAL: Read stages.validation.acceptance_test before planning: only literal true
permits an executable testing tool. False/absent/nonboolean/missing/empty/metadata-only
config cannot enable execution; no force-enable general or implementation-config
fallback. Missing/malformed config blocks affected executable groups, not structured
reading. Required executable structured scenarios still need authorized capability.

Frontend-ui requires configured enabled available Chrome DevTools MCP and actual browser
with dedicated --user-data-dir or isolated profile. Enabled UI skill if used;
otherwise enabled direct MCP. Navigate → trigger feature → check console and every
original assertion. Source/jsdom/unit review cannot pass UI. Unavailable/disabled/
unreachable browser means Blocked; Playwright is not an implicit enabled Chrome
alias. Non-UI API/CLI/library/skill-only scopes need no browser or universal URL.

Read [detailed procedures](.github/skills/x-ipe-task-based-feature-acceptance-test/references/detailed-procedures.md),
[integration](.github/skills/x-ipe-task-based-feature-acceptance-test/references/integration.md),
and [report template](.github/skills/x-ipe-task-based-feature-acceptance-test/templates/acceptance-test-cases.md).
Validate actual content/feature/file kind/canonical roots; reject symlinks/traversal.
Preserve dirty docs/source/history and assertions. Acceptance grants no code-fix,
TDD relaxation, skill promotion, app-gate bypass or release permission.

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-feature-acceptance-test"
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A"
    action: "acceptance_testing"
    extra_context_reference:
      specification: "path | N/A | auto-detect"
      impl-files: "file path | file array | N/A | auto-detect"
  category: "standalone | feature-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-code-refactor"
      condition: "Refactor code for quality improvements"
    - skill: "x-ipe-task-based-feature-closing"
      condition: "Close feature if no refactoring needed"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  feature_id: "{FEATURE-XXX | N/A for approved standalone}"
  target_url: "{actual UI URL | N/A}"
  toolbox_meta_path: "x-ipe-docs/config/tools.json"
  specification_link: "x-ipe-docs/requirements/FEATURE-XXX/specification.md"
  mockup_link: "{path | N/A}"
  technical_design_link: "x-ipe-docs/requirements/FEATURE-XXX/technical-design.md"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing supplied lifecycle task/readiness; no new ID" />
  <field name="task_based_skill" source="canonical skill and caller context" />
  <field name="execution_mode" source="lifecycle; default free-mode" />
  <field name="workflow.name" source="exact lifecycle identity or N/A" />
  <field name="workflow.action"><steps>Resolve ACTION_MAP/template acceptance_testing, not toolbox acceptance_test; explicit conflict blocks.</steps></field>
  <field name="workflow.extra_context_reference"><steps>Preserve specification and impl-files selected contexts in either mode; required workflow inputs cannot be waived with N/A.</steps></field>
  <field name="category"><steps>Retain standalone or feature-stage. Workflow per-feature requires real feature; standalone explicit approved source/acceptance scope, no invented goal.</steps></field>
  <field name="next_task_based_skill" source="original two conditional suggestions; actual mandatory app gates separately enforced" />
  <field name="process_preference.interaction_mode"><steps>Exact lifecycle enum/source: interact-with-human, dao-represent-human-to-interact, dao-represent-human-to-interact-for-questions-in-skill. Human asks human and waits within skill; full DAO and hybrid use bounded message_context/instruction_units/execution_plan. Human and hybrid require human completion/route confirmation; full DAO selects only authorized successors. Explicit human approval binds in every mode. Clear inputs need neither; no invented intent/approval/observation.</steps></field>
  <field name="feature_id"><steps>Previous implementation/explicit approved identity/task context; owner read-only board verifies one record or approved standalone N/A.</steps></field>
  <field name="specification_link"><steps>Selected specification first, declared/previous output/board specification_link next; unique owning EPIC/FEATURE or legacy FEATURE folder last for absent/N/A/auto. Broken explicit input blocks, never fallback.</steps></field>
  <field name="implementation_files"><steps>Selected impl-files is actual implementation-file input; normalize valid legacy scalar to nonempty file array. Otherwise previous actual inventory/done implementation output, unique explicit scoped source discovery in free-mode. Never output directories or design as implementation; validate every file/scope, no new persisted/output field.</steps></field>
  <field name="technical_design_link"><steps>Declared real design/previous design output or unique owning technical-design.md; no board design field. Read both parts; reject broken/wrong-feature/ambiguous paths. Implementation context is not a design initializer.</steps></field>
  <field name="mockup_link"><steps>All current scoped spec/design/explicit linked mockups, singular legacy field retained. Actual content/scope, not date; conflict uses decision policy; absent justified N/A.</steps></field>
  <field name="target_url"><steps>Only frontend-ui: explicit scoped actual URL, dev-server config then genuine bounded question; verify reachable. No universal URL for non-UI groups.</steps></field>
  <field name="toolbox_meta_path"><steps>Approved default x-ipe-docs/config/tools.json, readable JSON/testing section with strict enablement; no alternate config bypass.</steps></field>
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Identity and owner</name><verification>One approved task/readiness/scope/owner and protected baseline, real feature or explicit standalone, no duplicate lifecycle.</verification></checkpoint>
  <checkpoint required="true"><name>Implemented capability</name><verification>Actual implementation/package/evidence exists. New scope Implemented, authorized advanced Tested/Completed resume preserved. Deployment only for applicable tests, no compulsory merge/commit.</verification></checkpoint>
  <checkpoint required="true"><name>Authoritative acceptance</name><verification>Source/parent/story/subgoal/all ACs/assertions/types, spec/both design parts/current mockups resolve; missing intent blocks pertinent outcome claim.</verification></checkpoint>
  <checkpoint required="true"><name>Evidence and capabilities</name><verification>Config/runners/data/environment/browser where applicable and explicit relevant dependencies inspected; unavailable groups retained Blocked.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Phase | Steps | Action | Gate |
| --- | --- | --- | --- |
| 1. 博学之 — Study Broadly | 1.1 | Load config/source/goals and classify full acceptance | Complete original assertion/type map |
| 2. 审问之 — Inquire Thoroughly | 2.1 | Inspect implementation and source-derived data | Precise real interfaces/expectations |
| 3. 慎思之 — Think Carefully | 3.1 | Reflect and validate reuse | Explicit dependencies and coverage |
| 4. 明辨之 — Discern Clearly | 4.1 | Execute remaining checks and report | Current honest delivery/outcome evidence |
| 5. 笃行之 — Practice Earnestly | 5.1 | Same-owner handoff | Original outputs and actual app gates |

## Execution Procedure

```xml
<procedure name="feature-acceptance-test">
  <execute_dor_checks_before_starting/>
  <phase_1 name="博学之 — Study Broadly"><step_1_1><name>Load and Classify Complete Acceptance</name><action>
    1. Read current testing config before planning. Discover/match actual enabled capability declarations semantically, ignore underscore metadata, load matched skills only. Missing/disabled executable tools block relevant groups; structured reading still possible.
    2. Read specification/source/parent/story/subgoal/outcome frame, all scoped ACs/original assertions, constraints/non-goals, both design parts and implementation evidence. Legacy explicit so-that inference labeled with exact source anchor; missing intent blocks pertinent claim only.
    3. Classify frontend-ui, backend-api, unit, integration, structured-review. CLI subprocess/exit/streams/filesystem integration and library public import/API checks executable; skills may need structured plus helper/validator execution. Split cross-type AC, retain every clause/all-required branch, no UI-only/manual invented metrics.
    4. Create existing report at owning EPIC/FEATURE or legacy folder, approved standalone path otherwise. Stable TC/source/goal/subgoal/AC, P0/P1/P2, original types/tools, preconditions/data/steps/observable expectations. Counts diagnostics, not goals; qualitative outcome scenario/gaps without invented observation.
    5. Installed tools implement/fix/refactor are not test-only operations. Use authorized existing runner within enabled matching capability or agreed test-generation/execution-only same-task adapter preserving source bytes; unsupported restriction blocks, never normal implement to change code.
  </action><output>Complete typed goal/AC report plan and actual capability/adapter</output></step_1_1></phase_1>
  <phase_2 name="审问之 — Inquire Thoroughly"><step_2_1><name>Inspect Implementation and Safe Data</name><action>
    1. Inspect real implementation inventory: UI stable selectors/scripts/load order/current mockups; API route/method/schema/auth; CLI entry/flags/cwd/exit/streams/files; library signature/import/returns/errors/side effects; integration setup/state/teardown; structured package/contracts/consumers.
    2. Preserve exact observable checkpoints for every original assertion. UI data-testid, stable id, aria-label then robust unique selector; no generated IDs/class chains, proper waits/console capture. Mock-only review cannot replace applicable actual HTTP/CLI/public API/browser boundaries.
    3. Collect explicit relevant source/spec/design/code/config/test/mockup/interfaces/environment/evidence hashes and dependency rationale. Scoped visual checks only, no invented match_score. Known fixtures need no ceremonial manual data request.
    4. Safe existing/authorized synthetic data has provenance; expected values from acceptance, not generated targets. Disposable setup/cleanup and specified before/after no-mutation assertions. Human asks genuine gaps and waits; full DAO and hybrid use bounded guidance; no secrets or production mutation to fabricate proof.
  </action><output>Precise typed checks/data and relevant dependency inventory</output></step_2_1></phase_2>
  <phase_3 name="慎思之 — Think Carefully"><step_3_1><name>Reflect and Validate Evidence Reuse</name><action>
    1. Verify all ACs/original assertions/types/branches, precise preconditions/actionable steps and applicable error/edge/regression. Preserve IDs/history/unaffected mappings; no deleting/weakening/xfail/skipping checks for green. Acceptance preserves genuine implementation RED/GREEN/baseline gates, does not force existing satisfied criteria red.
    2. Reuse only actual execution/review with independently resolved explicit dependencies and same current feature/source/spec/code/config/tests plus applicable design/mockup/interfaces/environment/evidence, same original assertions/types and ALL relevant ACs. Missing/stale inputs, changed environment/context, failed/partial/blocked evidence invalidate affected claims; timestamps/receipt/pass counts insufficient.
    3. Read-only verify_evidence checks report against explicit expected inputs and full AC/types/assertions using one case schema for all types and complete clauses per AC/type; never borrow assertions across types. Expected derives from authoritative sources/inspected dependencies, never copied from claimed report. reusable true means consistency only. Independently verify semantic sufficiency/type-specific actual execution artifacts/live environment; helper cannot discover omitted relevant paths or authenticate logs.
    4. Partition any subset reuse explicitly and prove full report coverage after merge, rerun affected/dependent checks. Authorized parent/intent/means delta invalidates affected review/outcome/tests; preserve independent unaffected evidence with rationale, no shrinking acceptance to pass helper.
    5. Missing scaffolding permits authorized tests only via enabled supported runner/adapter, not source repair or speculative expectations. Unsupported operation/scope change blocks; proposed fix/CR goes to owner.
  </action><output>Refined coverage and valid reuse or affected rerun set</output></step_3_1></phase_3>
  <phase_4 name="明辨之 — Discern Clearly"><step_4_1><name>Execute and Report Honest Evidence</name><action>
    1. Execute unproven/stale groups sequentially with safe data/cleanup; reuse only gated actual evidence with provenance. Continue independent groups after failures, preserve all gaps.
    2. UI actual enabled available browser/dedicated profile/reachable target: enabled UI skill execute_ui_tests or enabled direct Chrome MCP. Navigate, trigger relevant feature, inspect console/load/runtime errors, observe every original assertion/scoped mockup state. Failure screenshot/snapshot/errors; source/jsdom not UI evidence, unavailable browser Blocked.
    3. API actual requests/application route tests assert specified status/body/headers/auth/errors/side effects, disclose in-process/mocked/deployed limits. CLI actual subprocess in temporary cwd asserts exit/stdout/stderr/files/no-mutation. Library actual import/public API asserts return/error/side effects. Integration actual relevant setup/flow/state/cleanup; mocks cannot replace required real boundaries.
    4. Structured checks inspect the deliverable against each AC and actual consumer contracts. Run required enabled validator/temporary executable scenarios once; keyword presence is not behavioral proof. Self-check by default; independent review only for explicit requests or concrete high-risk uncertainty under shared policy, reusing current suitable review.
    5. Record actual command/review, exit/expected-versus-actual, environment, artifacts/hashes per TC/AC and Fail/Blocked/Partial/Not Run. Report original types/totals/failure actions; no code fix/assertion relaxation during acceptance. pass_rate = passed / ALL planned cases including blocked/not-run/partial; zero cases N/A, not 100%. Measured comparison only with actual method/source, no invented scores/KPIs.
    6. Engineering delivery requires every scoped original assertion current suitable passing evidence plus required review. Test pass is not goal achievement; stakeholder outcome not measured unless actual cited stakeholder/context observation at relevant revision. Automation/fixtures/approval/DAO/document review not that observation; unobserved impact alone does not negate supported delivery.
    7. Rehash explicit dependencies and recheck environment/config before handoff; changed inputs invalidate affected checks/review/dependent claims. Failed/stale/partial/blocked evidence returns blocked with artifacts, preserve independent history/results, never fake success.
  </action><output>Current per-AC results, honest delivery/outcome states and gaps</output></step_4_1></phase_4>
  <phase_5 name="笃行之 — Practice Earnestly"><step_5_1><name>Return Same-Owner Conditional Handoff</name><action>
    1. Return original task_completion_output/report links/results/feature fields and two conditional successors. Owner alone persists category/task/feature/app/Git/routing. Successful new Implemented acceptance may transition to Tested; authorized advanced Completed stays Completed. Free-mode no app writes.
    2. Workflow owner verifies done implementation/preceding mandatory actions, actual specification/impl-files context/artifacts, current full acceptance and required review. Perform or verify ONE acceptance_testing done write with exact test-report real file/test-folder scalar real directory, matching validation action/readback; failed/blocked evidence never done. Writer success alone insufficient, prior fresh verified done supports read-only resume, not replay.
    3. Refactor only for an evidenced quality/preservation need or explicit request. Default template code_refactor is optional and acceptance suggests feature_closing first; no need means route directly to closing. Respect a project's explicitly customized mandatory refactor action, without fake done/report or invented need. Never write skip records merely to unlock closing.
    4. Owner re-reads mode at one boundary: human and hybrid require human review and completion/route confirmation; hybrid uses DAO only within skill; full DAO bounded guidance and only authorized routing. Explicit human approval/release still binds in every mode. Return to caller, no child new task/Git/PR/successor execution.
  </action><output>Original output, actual owner adaptation and conditional route/blockers</output></step_5_1></phase_5>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: "{standalone | feature-stage}"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-code-refactor"
      condition: "Refactor code for quality improvements"
    - skill: "x-ipe-task-based-feature-closing"
      condition: "Close feature if no refactoring needed"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"
  workflow_action_updated: true | false
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/acceptance-test-cases.md"
  feature_id: "FEATURE-XXX"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Acceptance Testing"
  test_types_tested: ["frontend-ui", "backend-api", "unit", "integration", "structured-review"]
  test_cases_created: "{count}"
  tests_passed: "{count}"
  tests_failed: "{count}"
  tests_blocked: "{count}"
  pass_rate: "{X}%"
  results_by_type: { frontend_ui: {passed, failed, blocked}, backend_api: {...}, unit: {...}, integration: {...}, structured_review: {...} }
```

Original keys/order/value types/successors/report semantics retained; repair legacy
empty process_preference with required interaction_mode. Actual type/count fields
reflect executed/verified reused scope; report holds not-run/partial detail, no new
output fields. Runtime results_by_type is real mapping, not schematic legacy sets/
ellipses above. Standalone feature fields N/A; report path actual approved scope,
EPIC/FEATURE or legacy, never fabricated feature. No new goal/evidence schema.

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Complete acceptance</name><verification>All source/parent/story/subgoal/AC/original assertions/types mapped, no invented goal/metric/confirmation or lost branch.</verification></checkpoint>
  <checkpoint required="true"><name>Suitable actual checks</name><verification>Strict testing config, actual API/CLI/library/integration/structured checks; UI browser/path/console/all assertions or Blocked, never source-only pass.</verification></checkpoint>
  <checkpoint required="true"><name>Fresh explicit evidence</name><verification>Actual commands/results/review/environment/artifacts, source/spec/code/config/tests and dependencies rehashed; reuse full relevant AC/types/assertions, consistency not semantic proof.</verification></checkpoint>
  <checkpoint required="true"><name>Honest results/outcome</name><verification>All TC/AC states/typed metrics/gaps reported; delivery separate from not measured/cited actual stakeholder observation. Failed/partial/stale scope blocks delivery.</verification></checkpoint>
  <checkpoint required="if_applicable"><name>Independent risk review</name><verification>Meaningful workflow/executable/safety/public-contract review; absent required review blocks promotion/completion, not drafting.</verification></checkpoint>
  <checkpoint required="true"><name>Original owner handoff</name><verification>Original outputs/mode retained; owner verified action/tags/contexts/readback and appropriate Tested or preserved advanced status. Conditional refactor respects mandatory app gates, no duplicate task/Git/route.</verification></checkpoint>
</definition_of_done>
```

## Patterns & Anti-Patterns

| Pattern | When | Then |
| --- | --- | --- |
| Mixed/non-UI feature | API, CLI or library | Preserve all original types/assertions and actual boundaries |
| Skills/non-code | Contract plus executable helper | Cited structured checks plus required actual temporary scenarios |
| Reusable evidence | Explicit current dependencies/full ACs | Hash/case consistency then semantic review, rerun affected gaps |
| No quality need | Conditional closing | Route directly to closing under default optional-refactor policy |

| Anti-Pattern | Consequence | Correction |
| --- | --- | --- |
| Source review passes UI | Hidden runtime defect | Actual browser/path/console/assertions or Blocked |
| Activity passes mean goals achieved | False stakeholder claim | Delivery versus not measured/cited actual observation |
| Copy receipt as expected inputs | Circular freshness | Independently select current sources/dependencies/all ACs |
| Fix code/weaken tests in acceptance | Scope/TDD violation | Preserve assertions, return bounded failure/authority |
| Writer success or fake skipped mandatory gate | False app completion | Owner verifies real evidence/gates/readback |

## Examples

See [authored scenarios](.github/skills/x-ipe-task-based-feature-acceptance-test/references/examples.md)
and [integration/reuse limits](.github/skills/x-ipe-task-based-feature-acceptance-test/references/integration.md).
