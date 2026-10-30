---
name: x-ipe-task-based-feature-closing
description: Close one implemented and accepted feature with source-goal/subgoal/AC-to-current-evidence verification, truthful delivery and outcome gaps, proportionate independent review and bounded documentation corrections. Release or PR work requires explicit authority. Use when a feature is ready for final verification or authorized release. Triggers on requests like "close feature", "create PR", "ship feature".
---

# Task-Based Skill: Feature Closing

## Purpose

Close one approved feature, not merely finish activities:
1. Verify goals → subgoals → all scoped ACs → actual current acceptance evidence.
2. Distinguish verified engineering delivery from observed benefits and outcome gaps.
3. Review only relevant risks and correct documentation that would mislead a reader.
4. Return original outputs and bounded release/next-feature recommendations to one owner.

## Important Notes

BLOCKING: Load `x-ipe-workflow-task-execution` and the
[common lifecycle contract](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md).
Direct entry calls Orient/Plan for supplied task/original context without recursively dispatching
this skill; normal entry reuses readiness. One feature only, one owner for
registration, task/category/feature/app updates, Git and the single next boundary.
No child task creation, duplicate completion, successor execution or auto playground.

BLOCKING: Adopt the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
in the existing closing report. Preserve source/parent/story/subgoal IDs,
Given/When/Then criteria, original assertions and test types, all-required branches
and bounded selected alternatives. No invented goals/KPIs/targets/manual observation,
stakeholder approval or achieved benefits. Actual stakeholder/context observation
is distinct from passing tests, fixtures, document review or DAO guidance.
Outcome not measured is an explicit gap, not automatic failed delivery. Missing
intent blocks only the pertinent claim; label legacy so-that inference with anchor.

CRITICAL: Reuse fresh suitable acceptance evidence with same relevant hashes and
current environment; not run twice just because closing follows acceptance.
Hash/coverage consistency is necessary, not semantic proof. Inspect actual
execution/review artifacts and original assertions; stale/partial/blocked evidence
blocks affected delivery, rerun only changed or unproven dependent scope through
authorized acceptance capability. UI requires actual browser navigation/feature
trigger/console/all assertions, not source/jsdom review or invented manual GWT type.
API/CLI/library/integration/structured evidence retains applicable actual boundaries.

CRITICAL: No automatic commit, push, PR, branch switch, stash/reset or broad staging.
Uncommitted delivery may close when approved scope is engineering-only. Explicit
release scope without permission/evidence is blocked, not silently waived. DAO
cannot grant release or human approval. Respect existing Git strategy and dirty
baseline; owner alone performs separately authorized exact-path operations.

Read [integration](.github/skills/x-ipe-task-based-feature-closing/references/integration.md),
[report scaffold](.github/skills/x-ipe-task-based-feature-closing/templates/closing-report.md),
and [examples](.github/skills/x-ipe-task-based-feature-closing/references/examples.md).
Keep both original [PR](.github/skills/x-ipe-task-based-feature-closing/references/templates/pr-template.md)
and [changelog](.github/skills/x-ipe-task-based-feature-closing/references/templates/changelog-template.md)
templates. Instantiate only actual authorized applicable facts; legacy playground
checkbox is N/A without explicit request, not mandatory new work or fake tested state.

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-feature-closing"
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A"
    action: "feature_closing"
    extra_context_reference:
      specification: "path | N/A | auto-detect"
      refactor-report: "path | N/A | auto-detect"
  category: "feature-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "Start the next unstarted feature from backlog. Continue the feature-by-feature pipeline (refinement → design → implementation → testing → closing)."
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  feature_phase: "Feature Closing"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  git_strategy: "main-branch-only | dev-session-based"
  git_main_branch: "{auto-detected}"
  git_dev_branch: "dev/{git_user_name}"
  specification_path: "x-ipe-docs/features/{FEATURE-XXX}/specification.md"
  test_results: "{actual acceptance report and revision evidence; legacy all passing not proof}"
  optional_tools:
    readme_updator: false
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing supplied lifecycle task/readiness; no new ID" />
  <field name="task_based_skill" source="canonical skill and authorized caller" />
  <field name="execution_mode" source="lifecycle; default free-mode" />
  <field name="workflow.name" source="exact lifecycle identity or N/A" />
  <field name="workflow.action"><steps>Resolve ACTION_MAP/template feature_closing, per-feature validation; conflicting explicit action blocks.</steps></field>
  <field name="workflow.extra_context_reference"><steps>Preserve selected specification and optional refactor-report in either mode; required specification must resolve. No closing-report output tag invented.</steps></field>
  <field name="category" source="feature-stage; exactly one feature" />
  <field name="next_task_based_skill" source="original conditional backlog suggestion only; owner authorizes successor" />
  <field name="process_preference.interaction_mode"><steps>Exact lifecycle enum/source: interact-with-human, dao-represent-human-to-interact, dao-represent-human-to-interact-for-questions-in-skill. Human asks human and waits within skill; full DAO and hybrid use bounded message_context, instruction_units and execution_plan. Human and hybrid require human completion/route confirmation; full DAO selects only authorized successors. Clear inputs need neither; explicit human approval binds in every mode.</steps></field>
  <field name="feature_phase" source="Feature Closing" />
  <field name="feature_id"><steps>Prior actual acceptance/refactor output or explicit authorized identity; owner read-only feature query verifies unique matching record, never fabricate from title.</steps></field>
  <field name="feature_title"><steps>Actual feature record then scoped specification header; mismatch blocks pertinent claim, no invented title.</steps></field>
  <field name="feature_version"><steps>Actual feature record/approved source revision, retain existing identity/history; do not invent version when missing.</steps></field>
  <field name="specification_path"><steps>Explicit selected specification first, declared path/previous output/board specification_link next. Only absent/N/A/auto uses unique owning EPIC/FEATURE or legacy FEATURE folder. Broken/wrong-feature explicit links block, no newest-file fallback. Validate regular nonsymlink file/root/content/source identity.</steps></field>
  <field name="test_results"><steps>Actual owning acceptance-test-cases.md/previous report plus source/spec/both design parts/actual implementation_files/tests/config/mockups/interfaces/environment/evidence dependencies. Selected refactor-report if present must be real current owning file, not acceptance or design substitute. Legacy all passing string cannot prove delivery. Inspect authoritative original AC/types/assertions and complete actual evidence.</steps></field>
  <field name="git_strategy" source="approved lifecycle .x-ipe.yaml policy; main-branch-only or dev-session-based, no implicit release permission" />
  <field name="git_main_branch" source="owner's verified configured/local identity; ambiguity blocks branch-sensitive release, no assumed checkout" />
  <field name="git_dev_branch" source="owner's actual sanitized Git identity only for dev-session-based; never agent nickname" />
  <field name="optional_tools.readme_updator"><steps>Literal caller true enables optional updater; default false. Load actual declared operation only for needed authorized README corrections, same-task no duplicate lifecycle.</steps></field>
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Identity and scope</name><verification>One supplied task/readiness/owner/feature, protected dirty baseline and engineering versus release authority known.</verification></checkpoint>
  <checkpoint required="true"><name>Implemented and accepted capability</name><verification>Feature status Implemented or Tested with real complete current acceptance evidence; authorized Completed resume preserves advanced status. No compulsory commit, push, merge or duplicate test suite.</verification></checkpoint>
  <checkpoint required="true"><name>Authoritative sources</name><verification>Source/parent/story/subgoal/all ACs/assertions/types, spec/both design parts/implementation inventory/mockups and actual relevant evidence resolve; gaps explicit.</verification></checkpoint>
  <checkpoint required="true"><name>Workflow and review readiness</name><verification>Actual action/template/runtime contexts/tags and preceding mandatory gates verified; proportionate required independent review available or completion blocked. Free-mode needs no app write.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Phase | Step | Action | Gate |
| --- | --- | --- | --- |
| 1. 博学之 — Study Broadly | 1.1 | Trace acceptance and reuse current evidence | Every original scoped assertion supported |
| 2. 审问之 — Inquire Thoroughly | 2.1 | Review relevant risk and misleading docs | No concealed delivery gap |
| 3. 慎思之 — Think Carefully | 3.1 | Apply bounded documentation corrections | Relevant evidence refreshed, no scope drift |
| 4. 明辨之 — Discern Clearly | 4.1 | Resolve release authority and actual app contract | Honest release and completion disposition |
| 5. 笃行之 — Practice Earnestly | 5.1 | Report delivery/outcome and return owner handoff | Original output, one lifecycle boundary |

## Execution Procedure

```xml
<procedure name="feature-closing">
  <execute_dor_checks_before_starting/>
  <phase_1 name="博学之 — Study Broadly"><step_1_1><name>Verify Goal-to-Current-Acceptance Evidence</name><action>
    1. Read approved source/parent/subgoal/story frame, all scoped ACs and original assertions/types/constraints; map through actual source files/acceptance TCs/results/hashes in closing report. Preserve stable GWT IDs and every all-required clause; alternatives are selected means, not extra backlog mandates.
    2. Independently resolve relevant dependencies/current hashes, exact feature/environment/tool config and actual execution/review provenance. Reuse existing acceptance helper for consistency when appropriate; no duplicate helper/schema, expected inputs never copied from claimed pass. Same relevant hashes and suitable current semantic evidence mean reuse, not run twice. Timestamp/count/receipt/all passing strings insufficient.
    3. UI actual isolated authorized browser path/trigger/console/all original assertions/current mockup evidence required; source/jsdom not UI proof. Backend requests, CLI subprocess exit/streams/files, library public API, integration setup/state/cleanup and structured complete-package plus required executable scenarios retain original types/boundaries. Changed live environment invalidates reuse even if files match.
    4. Failed/missing/stale/blocked/partial/unrun assertions block delivery. Return bounded rerun/fix/CR decision to owner; no implementation fix or AC alteration here. Authorized delta invalidates affected dependent tests/review/outcome; preserve unaffected IDs/history/independent evidence with rationale. No retrofitting old criteria to manufacture green.
    5. Record verified engineering delivery only with complete actual suitable evidence; stakeholder outcome not measured unless cited actual stakeholder/context observation matches source scenario/current revision. Fixtures/tests/approval/DAO not observed benefit; qualitative scenario/gap suffices, no invented KPI or stakeholder approval.
  </action><output>Full goal/subgoal/AC/evidence map, justified reuse and explicit gaps</output></step_1_1></phase_1>
  <phase_2 name="审问之 — Inquire Thoroughly"><step_2_1><name>Proportionate Code-to-Docs and Risk Review</name><action>
    1. Compare relevant actual implementation/spec/both design parts/tests/report/current mockups and consumer contracts. For low-risk bounded cosmetic/docs work, deterministic plus self-review with rationale suffices; meaningful workflow/executable/safety/public-contract change requires independent review. Reuse fresh independent review at same revision/scope, not a compulsory second reviewer. Missing required review blocks completion, not drafting.
    2. Identify concrete misleading references, API/run instructions or omitted documentation of already approved behavior. Ignore harmless cosmetics. Behavioral code-versus-AC contradiction is a delivery defect, not documentation drift. Never modify AC/tests to match faulty code without an approved CR and fresh downstream validation; no implementation or refactoring here.
    3. Write bounded change report with actual review provenance, risk/scope/hash, gaps and dispositions. Human asks only genuine decisions and waits; full DAO and hybrid consume message_context/instruction_units/execution_plan, cannot invent approval or authorize scope/release.
  </action><output>Actual proportionate review and bounded misleading-doc delta</output></step_2_1></phase_2>
  <phase_3 name="慎思之 — Think Carefully"><step_3_1><name>Correct Only Misleading Documentation</name><action>
    1. Update authorized owned spec explanatory material/design/test documentation/README/API/changelog only where current approved behavior would otherwise mislead. Preserve original AC assertions, protected dirty docs/history; no blanket rewrite or compulsory every-file update. No needed change is a valid documented disposition.
    2. If needed and optional updater true, use actual declared README operation within same task/readiness; otherwise bounded manual documentation correction. Original PR/changelog templates remain available; no unrequested playground or fictional release/checklist facts.
    3. Any relevant doc/test/code/config/intent change invalidates affected evidence/review; independently rehash and rerun only affected/dependent checks via authorized test capability, preserving unaffected evidence; no compulsory refactoring analysis or fabricated score/suggestions. Existing current quality/refactor evidence may inform recommendation; unavailable assessment is N/A, not acceptable quality proof.
  </action><output>Necessary documentation delta or no-change rationale, refreshed affected evidence</output></step_3_1></phase_3>
  <phase_4 name="明辨之 — Discern Clearly"><step_4_1><name>Resolve Release and Workflow Contract</name><action>
    1. Separate engineering closure from release. Default no commit/push/PR; owner executes only explicitly authorized exact paths with protected staged/unstaged baseline, actual branch/identity and strategy. No broad staging, dirty branch switch/stash/reset, implicit network or auto commit. Main-branch-only no new branch/PR; dev-session-based real identity, scoped meaningful PR description/test/feature/design links only if authorized. Required release without authority blocks release-scope completion; engineering-only may close uncommitted, release gap explicit.
    2. Workflow-mode owner inspects actual ACTION_MAP/template/runtime and matching state: feature_closing under validation, required specification, optional refactor-report. Verify current acceptance and preceding mandatory implementation/validation gates done, not skipped; writer success alone insufficient. Current code_refactor mandatory remains a blocker until legitimate evidenced fulfillment or separately authorized later integration migration; no fake skip/done/report or invented need/churn.
    3. Current feature_closing deliverables [] means owner uses deliverables {} with exact matching action/feature/status done readback, once, only after domain/gate evidence. Keep closing report as task artifact/task_output_links, NOT pretend closing-report tag. If a later approved template declares tags, resolve exact real paths and validate runtime before writing, not silently edit config here. Free-mode no app write; current verified done resume read-only, no replay.
    4. Change-request optional closing-report may be absent: preserve report task link for explicit handoff; required specification still resolves. No invented app tag, automatic discovery or claim that app extracts the task artifact. No application/config edits in this skill migration.
  </action><output>Engineering/release disposition and actual owner action mapping or blocker</output></step_4_1></phase_4>
  <phase_5 name="笃行之 — Practice Earnestly"><step_5_1><name>Report and Return One Owner Handoff</name><action>
    1. Complete existing closing report with source/parent/subgoal/AC/assertion/type/current evidence, reused versus rerun checks, review/docs delta, actual release state and explicit outcome gaps. Counts/activities are diagnostics, not achieved goals; no invented observations or human acknowledgment.
    2. Return exact task_completion_output fields and original conditional next-feature suggestion. Keep refactoring_analysis compatibility fields; actual assessed results only, N/A/no assessment with empty suggestions when unavailable, no score threshold or compulsory analysis. Populate task_output_links only actual report/owning folder/existing assessment/authorized PR or release evidence, never fictional pushed to main or missing analysis path.
    3. One lifecycle owner alone verifies required category/app/readback/release-scope gates then marks feature Completed and task completed once via real board adaptation. Feature Implemented or Tested accepted only with actual full evidence; Completed resume read-only/preserved. Blocked/stale scope never Completed; larger partial candidate slice never falsely closes task. Board/task/output schemas unchanged.
    4. Owner re-reads mode once at boundary: human and hybrid require human review and completion/route confirmation; hybrid uses DAO only within skill; full DAO bounded guidance and only authorized routing. Explicit required human approval remains binding in every mode; no stakeholder approval invented. Suggest next actual unstarted feature only within authority; no successor task/skill execution by child, no automatic human playground.
  </action><output>Original output and truthful report, current gates/owner next boundary</output></step_5_1></phase_5>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "Start the next unstarted feature from backlog. Continue the feature-by-feature pipeline (refinement → design → implementation → testing → closing)."
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "{PR link (dev-session-based) or 'pushed to main' (main-branch-only)}"
    - "x-ipe-docs/features/{FEATURE-XXX}/"
    - "x-ipe-docs/refactoring/analysis-{task_id}.md"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Feature Closing"
  refactoring_analysis:
    overall_quality_score: "{1-10}"
    refactoring_recommended: "true | false"
    top_suggestions: ["{summary of key suggestions}"]
```

Exact legacy output schema/keys/order/nested types/conditional successor retained;
placeholder links are illustrative, not mandatory fictional artifacts. Runtime
list contains only actual artifact/release links, including closing report.
Unassessed compatibility: overall_quality_score string N/A, refactoring_recommended
false means no evidenced recommendation (NOT quality verified), top_suggestions [].
Report records not assessed and inspected limits. Actual assessment retains genuine
score/recommendation/suggestions; do not fabricate it to fill compatibility fields.
No new workflow_action/goal/outcome/release keys; report carries domain evidence and
owner lifecycle dynamic context records matching app write/readback separately.

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Full current acceptance</name><verification>Every scoped source/parent/subgoal/AC/GWT/original assertion/type linked to actual suitable current evidence; reuse justified, stale/unproven checks blocked or rerun.</verification></checkpoint>
  <checkpoint required="true"><name>Honest delivery and outcome</name><verification>Delivery separate from not measured/cited actual stakeholder observation; qualitative scenario and outcome gaps explicit, no invented benefits or approval.</verification></checkpoint>
  <checkpoint required="true"><name>Proportionate review and docs</name><verification>Required independent review current or low-risk rationale; only misleading authorized docs corrected, no code fix/AC relaxation without approved CR; affected evidence revalidated.</verification></checkpoint>
  <checkpoint required="true"><name>Authority and action mapping</name><verification>Engineering/release scope distinguished, authorized release evidence or explicit gap; actual template/runtime contexts/gates/empty-tag mapping and readback, no pretend tag or mandatory gate bypass.</verification></checkpoint>
  <checkpoint required="true"><name>Original single-owner return</name><verification>Original output/compatibility fields and actual report links; owner alone verified Completed/task lifecycle boundary, no duplicate board/Git/routing/automatic playground or compulsory analysis.</verification></checkpoint>
</definition_of_done>
```

## Patterns & Anti-Patterns

| Pattern | When | Then |
| --- | --- | --- |
| Fresh full acceptance | Same dependencies/environment/assertions | Reuse actual evidence, not duplicate testing |
| UI evidence unavailable | Source-only or missing browser proof | Block UI-dependent delivery, not fictional manual type |
| Delivery verified, benefit unobserved | Source scenario lacks real observation | Explicit not measured gap, no fabricated approval |
| Bounded docs correction | Approved behavior documented misleadingly | Small delta and affected revalidation, no AC downgrade |
| Empty app outputs | Actual closing template/runtime declares no tags | deliverables {}, report task artifact, optional CR context absent |

| Anti-Pattern | Consequence | Correction |
| --- | --- | --- |
| Rewrite AC to match faulty code | Concealed product defect | Block and propose bounded fix/approved CR |
| Push/PR by default or broad staging | Foreign dirty work released | Explicit authority, exact paths, owner only |
| Compulsory second test/refactor review | Activity churn, fabricated scores | Current justified reuse/proportionate review |
| Invent closing-report app tag | Runtime rejection or false done claim | Actual extract tags and readback, empty mapping valid |
| Tests/DAO mean observed benefits | False stakeholder success | Separate delivery from explicit outcome gap |

## Examples

See [authored cases and templates](.github/skills/x-ipe-task-based-feature-closing/references/examples.md)
and [actual consumer boundaries](.github/skills/x-ipe-task-based-feature-closing/references/integration.md).
