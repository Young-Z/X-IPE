---
name: x-ipe-task-based-bug-fix
description: Restore documented intended behavior through reproduced failures, bounded root-cause/conflict analysis, goal/subgoal constraints and failing-before/fixed-after regression evidence. Use when existing behavior is broken. Triggers on "fix bug", "something is broken", "not working".
---

# Task-Based Skill: Bug Fix

## Purpose

Diagnose the reported deviation and restore documented intended behavior, not
invent a new product goal. Link original reproduction, minimal fix and regression
evidence to existing source/goal/subgoal/story/AC constraints. Keep verified
engineering delivery separate from an observed stakeholder outcome or not measured.

## Important Notes

Load the [single-loop delivery policy](.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md)
once in the current context. Execute this skill in the same agent loop; another
skill is expertise, not a new agent. Use proportional checks and reuse current
evidence; independent review is conditional on concrete risk, not the skill name.

BLOCKING: Load [shared workflow](.github/skills/x-ipe-workflow-task-execution/SKILL.md),
[common lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md)
and [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md).
Direct entry uses same task/readiness through Orient/Plan once, without recursively
dispatching this child. One owner handles registration, completion and routing.
No board, Git, app writes or successor execution in this child; no automatic commit.

BLOCKING: Restore source-authorized behavior; no arbitrary success metrics,
covert AC weakening, grace period, new goal or scope expansion to make tests pass.
Changed scope/goal/acceptance/constraint changes require actual human authority
through the CR boundary; full DAO guidance is not human permission. A clear
bounded restoration needs no repeated approval or ceremonial DAO call.

BLOCKING: Actual reproduction and behavioral test MUST fail for the reported
behavior before fix; unchanged test MUST pass after fix. Setup/import/tool failures
are not reproduction. Read [integration](.github/skills/x-ipe-task-based-bug-fix/references/integration.md)
for current action absence, real tool routing, browser and tracing gates.

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: x-ipe-task-based-bug-fix
  execution_mode: free-mode | workflow-mode
  workflow:
    name: N/A
    action: null
    extra_context_reference: {}
  category: standalone
  next_task_based_skill: null
  process_preference:
    interaction_mode: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
  bug_description: "{reported deviation}"
  expected_behavior: "{source-authorized intended behavior}"
  actual_behavior: "{observed behavior}"
  reproduction_steps: "steps or N/A"
  environment_info: "relevant runtime/browser/config or N/A"
  program_type: "frontend | backend | fullstack | cli | library | skills | mcp | ..."
  tech_stack: []
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="same supplied lifecycle task/readiness; no duplicate" />
  <field name="task_based_skill" source="exact canonical discovered name" />
  <field name="execution_mode"><steps>Caller mode; default free-mode. Current ACTION_MAP/template have no bug-fix association; workflow-mode blocks absent supported mapping, never silently converts.</steps></field>
  <field name="workflow.name" source="exact caller identity or N/A; contextual workflow does not imply supported action" />
  <field name="workflow.action"><steps>Current action null; bug_fix is a tool route only. Require real skill/action/template association before any workflow claim.</steps></field>
  <field name="workflow.extra_context_reference"><steps>Preserve caller keys; explicit selected source first, declared source/board link, then unique EPIC/FEATURE or legacy folder. Validate anchors, kind, content, identity, containment and symlink escape; broken/ambiguous explicit links block, not fallback.</steps></field>
  <field name="process_preference.interaction_mode" source="caller exact enum/source; default interact-with-human; reject unknown" />
  <field name="bug_description" source="original report; keep original wording and scope" />
  <field name="expected_behavior"><steps>Reconcile user report with approved requirements/spec/story/GWT AC/design. Disagreement needs bounded decision; do not silently choose code as authority.</steps></field>
  <field name="actual_behavior" source="reported symptoms then actual reproduction evidence; not assumed verified" />
  <field name="reproduction_steps" source="provided steps followed exactly, or explicit hypothesis when N/A" />
  <field name="environment_info" source="actual relevant runtime/version/config/browser/test data; redact secrets" />
  <field name="program_type"><steps>Inspect affected behavior and project entry/config, not file extension alone; JS may backend, Python may CLI/library/skill. UI uses actual UI evidence.</steps></field>
  <field name="tech_stack" source="caller or verified project manifests, installed runtime and affected layers" />
  <field name="category" source="standalone from original Output Result" />
  <field name="next_task_based_skill" source="null from original Output Result; suggestions only in report to owner" />
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Owner and scope</name><verification>Same task/readiness, exact policy, authorized roots/write paths and original bug report known.</verification></checkpoint>
  <checkpoint required="true"><name>Expected versus actual</name><verification>Approved intended behavior/source clauses and reported deviation identified; material ambiguity named.</verification></checkpoint>
  <checkpoint required="true"><name>Reproduction readiness</name><verification>Known steps or bounded hypothesis, relevant environment and actual runnable test capability available.</verification></checkpoint>
  <checkpoint required="true"><name>Domain integration</name><verification>Actual program/stack, enabled tool interfaces, action absence/free-mode or supported workflow mapping, review plan and protected baseline resolved.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Step | Name | Action | Gate |
| --- | --- | --- | --- |
| 1 | Understand | Source goal and intended behavior | Scope/constraints understood |
| 2 | Reproduce | Original steps, relevant environment | Actual behavioral failure |
| 3 | Diagnose | Root cause, callers and boundaries | Evidence-backed cause |
| 4 | Design Fix | Minimal means, design impact | Contract preserved or authorized CR |
| 5 | Conflict Analysis | Actual logic and original request | Unexpected conflicts resolved |
| 6 | Write Test | mini AAA in actual domain | Behavioral red before fix |
| 7 | Implement | Enabled tool operation fix sequentially | Same test green; no new regressions |
| 8 | Verify and Return | Reproduction, full suite, evidence | Domain DoD; one owner handoff |

BLOCKING: Conflict analysis precedes failing-test/fix execution. Key interface,
data model or workflow design impact updates approved technical design and Design
Change Log before implementation; design edits cannot authorize changed acceptance.
A genuine pre-existing behavioral failing test may be reused with recorded red
revision and unchanged assertions; never fabricate another failure or commit gate.

## Execution Procedure

```xml
<procedure name="bug-fix">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Understand the Bug and Intended Goal</name>
    <action>
      1. Read original report, approved requirements/parts, specification/story/GWT AC/type, design and relevant prior CRs. Record expected versus actual and severity: Critical system/data loss; High broken feature; Medium partial behavior; Low minor issue.
      2. In the existing bug report record stakeholder, intended observable outcome, source/parent goal/subgoal, restoration contribution, justified qualitative success scenario, constraints/non-goals and source/story/AC/type links. all-required branches need coverage; alternatives select one bounded means, not new backlog.
      3. Legacy explicit so-that only may supply inferred intent with source anchor, not confirmed. Missing goal blocks pertinent outcome/coverage claim; unclear intended behavior blocks the fix. No unrelated retrofit or invented metrics.
      4. For genuine decisions human asks the human within skill and waits; full DAO and hybrid use common message_context/instruction_units/execution_plan for bounded guidance. Reuse exact current authority; beyond-contract change returns blocked for CR/owner disposition, not automatic successor. Explicit human approval binds in every mode.
    </action>
    <output>Original report, severity, source restoration frame and bounded gaps</output>
  </step_1>
  <step_2>
    <name>Reproduce the Bug</name>
    <action>
      1. Follow original reproduction steps exactly; if absent state hypothesis and attempt a controlled reproduction. Capture actual expected/actual values, environment/config/data, commands, errors and source revisions. Intermittent bugs need controlled schedule/seed and observed failure, not an arbitrary retry success rate.
      2. UI bugs: inspect current stages.feedback.bug_fix browser configuration and actual available tools. Enabled/available capability reproduces UI with snapshot/screenshot/console; disabled optional browser relies on actual domain tests with explicit visual gap. Enabled required capability unavailable blocks browser claim, not fake screenshot evidence.
      3. No reproduction means blocked with attempts/limits, not fixed. A syntax/setup error is not the original failing behavior.
    </action>
    <output>Actual reproducible failure or honest blocker</output>
  </step_2>
  <step_3>
    <name>Diagnose Root Cause</name>
    <action>
      1. Trace actual values/control/data flow from symptom through affected code and callers/dependents. Read actual technical design via validated source lookup. Optional history inspection only if useful; no branch/index mutation.
      2. Record root cause, trigger, source locations/revisions, design flaw versus implementation error, affected layers/interfaces/data/workflows and root-cause boundaries. Rule out symptom-only hypotheses with evidence.
      3. Inspect upstream/downstream behavior, shared helpers, concurrency, resources, security and error paths; enumerate side effects and unaffected behavior with preservation checks. Missing artifacts remain gaps, not no conflicts.
    </action>
    <output>Evidence-backed root cause, scope boundaries and risk</output>
  </step_3>
  <step_4>
    <name>Design Minimal Restoration</name>
    <action>
      1. Compare smallest viable means and selected alternative against intended goal/subgoal/AC/constraints, regression risk and design compatibility. No broad refactor or unrelated cleanup.
      2. Key component/interface/data/workflow changes require approved technical design plus Design Change Log before implementation. Contract expansion or incompatible behavior requires actual human CR authority first; do not redefine expected behavior to justify fix.
      3. Record exact allowed files/sections, expected restored behavior and unchanged boundaries. Invalidate only affected prior test/review/outcome evidence; retain unaffected IDs, history and checks. No forced tracing: consult tracing_enabled and existing infrastructure only as applicable.
    </action>
    <output>Minimal fix and design/authority disposition</output>
  </step_4>
  <step_5>
    <name>Conflict Analysis</name>
    <action>
      1. Conflict Detector examines actual affected logic, callers/dependents, interfaces, data models, assumptions and workflows, not fix prose alone. Conflict Validator compares each consequence to ORIGINAL report, expected behavior and source constraints, not revised fix design.
      2. Record expected/unexpected classifications with exact clause/code/revision, consequence, severity and disposition. No-conflict claim lists inspected sources. Expected restoration within authority proceeds without repeated approval.
      3. Unexpected conflicts require authorized narrowing/mitigation or real consequential decision per mode; unresolved conflicts block Step 6. Scope/acceptance changes still need actual human authority in all modes. DAO cannot authorize lost guest access, relaxed expiry or another boundary.
      4. Use self-checks and targeted tests by default; independent review is required only for an explicit request or concrete high-risk uncertainty under the shared single-loop policy. Reuse suitable current review; missing required review blocks the affected claim, not drafting. Never invent detector/validator execution.
    </action>
    <output>Conflict evidence, preserved boundaries and authorized resolution</output>
  </step_5>
  <step_6>
    <name>Write Failing Test and Route mini AAA</name>
    <action>
      1. Prepare mini AAA: Arrange actual bug preconditions/environment/source/AC, Act original failing action, Assert intended correct behavior and each constraint/regression branch; one assertion per Assert clause. Preserve GWT AC and actual domain types, no text matching as runtime proof.
      2. Read stages.feedback.bug_fix enabled tools and exact operation interfaces; semantically group relevant stack/layer scenarios and pass operation: fix, aaa_scenarios scenario_text, source_code_path, test_code_path and actual feature_context when available. See integration for ephemeral tool-only synthetic fallback, never actual IDs.
      3. Python/server/CLI/library uses project pytest conventions; JS/TS behavior uses real Vitest/Jest/component runtime; fullstack covers both; Java/MCP/skills use actual domain runners/protocol or disposable helper scenarios. Missing runner setup needs authorized scope, else blocked.
      4. Tool fix operation owns red then minimal fix then green sequence. Before allowing its fix stage, run/record test failing for intended behavioral assertion against unfixed revision. If already green, refine reproduction/test without changing source contract; setup failure does not satisfy gate.
    </action>
    <output>Actual failing regression evidence, immutable assertions and tool route context</output>
  </step_6>
  <step_7>
    <name>Implement Minimal Fix</name>
    <action>
      1. Continue the selected operation fix exactly once, sequentially per group; preserve one same-task context and cross-layer boundaries. Tool operation_output is not task_completion_output; collect actual implementation_files/test_files/assert-level test_results/lint_status/errors without dropping fields.
      2. Only after behavioral red implement minimal approved fix; unchanged test MUST pass against fixed revision. Recheck original expected behavior, side effects and regression branches, then run all existing tests/full suite and applicable lint.
      3. All existing tests must pass for all-green completion; new regressions block. Pre-existing failures stay named with before/after evidence and block all-green claim, never delete/skip/weaken assertions or claim full completion. Unavailable suites are gaps, not passed.
      4. Bound fixes/retries to affected scope; after three failed iterations escalate with actual partial outputs. Tool failure returns blocked, no destructive rollback or forced tracing installation.
    </action>
    <output>Minimal fixed bytes and current green/regression evidence or blocker</output>
  </step_7>
  <step_8>
    <name>Verify Fix and Return Once</name>
    <action>
      1. Repeat original reproduction at fixed revision, run full regression and smoke checks; UI enabled/available browser route validates original interaction, fixed snapshot/console and surrounding visual behavior. Failed required browser checks block; authored fixture or jsdom is not browser evidence.
      2. Document root cause, exact fix/why, design impact, boundaries/conflicts, side effects, retained constraints and before/after results. Bind source/spec/design/tests/config/review hashes and commands/exits; edits invalidate affected evidence and require rerun.
      3. Verify every scoped existing goal/subgoal/AC/type and all-required branch has current restoration/regression evidence. Report engineering delivery separately from observed stakeholder outcome or not measured; tests, plans, fixtures and DAO are not stakeholder observations.
      4. Return entire original output declaration and dynamic fields unchanged; actual links only, completed only when all applicable domain gates pass. Blocked preserves partial source/test/report links, cause and unresolved conflicts. Existing optional legacy fields such as require_human_review, if supplied, pass through to owner; never fabricate them as mandatory.
      5. One lifecycle owner handles domain-required review/completion and one next boundary; no app bug_fix writes/tags in current configuration and no implicit successor from null. Human and hybrid require human completion/route confirmation; hybrid uses DAO only within skill; full DAO selects only authorized successors, not repeated child routing. Explicit human approval binds in every mode.
    </action>
    <output>Original task_completion_output plus evidence handoff to owner</output>
  </step_8>
</procedure>
```

## Output Result

Preserve original keys, values, nested shape/order and dynamic attributes. Goal,
red/green, tool results and outcome gaps live in bug evidence, not new board fields
or app tags. Actual free-mode output retains workflow.name N/A.

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill: null
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "{path to fixed source file}"
    - "{path to test file}"
  # Dynamic attributes
  bug_severity: "Critical | High | Medium | Low"
  root_cause: "{brief description of root cause}"
  conflicts_found: []  # list of conflicts identified, empty if none
```

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Original reproduction restored</name><verification>Original steps and source-authorized expected behavior checked at fixed revision; actual before/after failure/results.</verification></checkpoint>
  <checkpoint required="true"><name>Goal and constraints</name><verification>Existing source/parent/subgoal/story/GWT AC/type and all-required restoration/regression branches mapped; inference/pertinent gaps and outcome not measured honest.</verification></checkpoint>
  <checkpoint required="true"><name>Root cause and conflict boundaries</name><verification>Actual cause/callers/dependencies, expected/unexpected consequences and authorized dispositions recorded; no unresolved unexpected conflict.</verification></checkpoint>
  <checkpoint required="true"><name>Red before green</name><verification>Behavioral regression fails on unfixed source before mutation and unchanged test passes after; source/test hashes and commands/exits, not a required Git commit.</verification></checkpoint>
  <checkpoint required="true"><name>Regression and domain tests</name><verification>All existing tests pass and applicable smoke/lint/current actual-domain checks verified; pre-existing failures unavailable checks and new regressions not hidden.</verification></checkpoint>
  <checkpoint required="true"><name>Minimal fix and design</name><verification>Only bounded restoration; key impact design/Change Log approved before implementation; exact changes and side effects documented.</verification></checkpoint>
  <checkpoint required="conditional"><name>Browser validation</name><verification>UI plus configured enabled/available browser checks pass original interaction, console and surrounding visual checks; disabled gap or unavailable required claim explicit.</verification></checkpoint>
  <checkpoint required="true"><name>Fresh review/evidence</name><verification>Source/test/config/design revisions match relevant evidence; meaningful independent review present or pertinent completion blocked; no fabricated outcome.</verification></checkpoint>
  <checkpoint required="true"><name>Original owner handoff</name><verification>Original/dynamic/legacy output fields preserved, exact tool results retained, unsupported workflow claim blocked; one owner no duplicate board/Git/next work.</verification></checkpoint>
</definition_of_done>
```

## Patterns & Anti-Patterns

| Pattern | When | Then |
| --- | --- | --- |
| Test-first restoration | Reproducible deviation | Source-linked red, minimal fix, identical assertions green and regression |
| Conflict-aware narrowing | Shared helper affects other callers | Preserve unrelated guest/API behavior; actual source and authority decide |
| Legacy goal gap | Explicit so-that or absent intent | Label inferred or block pertinent claim; no whole-project retrofit |
| Intermittent failure | Schedule/environment dependent | Controlled reproduction and root cause; no arbitrary statistical target |

| Anti-Pattern | Consequence | Correction |
| --- | --- | --- |
| Fix symptom without cause | Bug persists elsewhere | Trace real values/callers and boundary checks |
| Large refactor/multiple bugs | Unbounded regression risk | Minimal original-scope restoration |
| Test already passes/setup fails | False red evidence | Reproduce actual wrong behavior before fix |
| Weaken AC or add grace period | Covert product change | Preserve constraints; actual human CR boundary |
| Skip conflicts / invent reviewer | Silent break/false authority | Actual code analysis and honest review gate |
| Commit before fix required | Duplicate lifecycle/Git | Evidence chronology/hashes, no forced commit |
| bug_fix tool key as app action | Unsupported workflow state | Authorized free-mode or block requested workflow |

## Examples

Read [bounded examples](.github/skills/x-ipe-task-based-bug-fix/references/examples.md),
[bug report scaffold](.github/skills/x-ipe-task-based-bug-fix/templates/bug-report.md)
and [integration boundaries](.github/skills/x-ipe-task-based-bug-fix/references/integration.md).
