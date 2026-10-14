---
name: x-ipe-task-based-code-refactor
description: Study or restructure authorized code or skills while preserving externally-visible behavior and verifying a named measurable or qualitative quality improvement against its baseline. Orchestrates analysis, targeted sync, safe execution and evidence. Use when refactoring. Triggers on "refactor code", "execute refactoring", "analyze for refactoring", "code quality assessment".
---

# Task-Based Skill: Code Refactor

## Purpose

Preserve externally-visible behavior while achieving a named measurable or qualitative quality improvement.
An internal enabling subgoal contributes to maintainers' safe change confidence;
record its source/parent, inspected baseline, preservation contract, after evidence
and trade-off. Restructuring is a means, not stakeholder gain; no arbitrary scores.
Study-only produces recommendations, not implementation or achieved improvement.

## Important Notes

BLOCKING: Load [shared workflow](.github/skills/x-ipe-workflow-task-execution/SKILL.md),
[common lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md)
and [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md).
Use same task/readiness and one owner; direct entry obtains Orient/Plan once without
redispatching this child. No board, Git, app writes or successor execution here.
The owner handles completion/routing; default no commit, no automatic checkpoint,
dirty branch/index changes, broad staging or destructive rollback.

BLOCKING: Preserve approved goals, GWT ACs/types, interfaces, results, data, errors,
side effects and constraints. Intentional behavior/acceptance/scope changes require
actual human CR authority before behavior change in every mode. Never rewrite
requirements to bless accidental deviations or weaken assertions to pass. Detected
bugs are findings for the owner, not incidental refactor repairs.

This is the single refactor entry for study-only/local/broad. Read
[integration](.github/skills/x-ipe-task-based-code-refactor/references/integration.md)
for installed analysis/sync limitations, configuration gating, creator special
routing and mandatory app action. Inspection expansion is not write permission.

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: x-ipe-task-based-code-refactor
  execution_mode: free-mode | workflow-mode
  workflow:
    name: N/A
    action: null
    extra_context_reference:
      test-report: "path | N/A | auto-detect"
      specification: "path | N/A | auto-detect"
      tech-design: "path | N/A | auto-detect"
  category: feature-stage | standalone
  next_task_based_skill:
    - skill: x-ipe-task-based-feature-acceptance-test
      condition: Re-verify after refactoring
    - skill: x-ipe-task-based-feature-closing
      condition: Close feature if refactoring is the final step
  process_preference:
    interaction_mode: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
  refactoring_scope:
    scope_level: feature | custom
    feature_id: "{FEATURE-XXX or N/A}"
    refactoring_purpose: "{named quality goal and contribution}"
    files: []
    modules: []
    description: "{authorized intent and boundaries}"
  refactoring_mode: study-only | local | broad
  program_type: "frontend | backend | fullstack | cli | library | skills | mcp | ..."
  tech_stack: []
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="same supplied lifecycle task/readiness; no duplicate" />
  <field name="task_based_skill" source="exact canonical discovered name" />
  <field name="execution_mode" source="caller mode; default free-mode; never silently convert" />
  <field name="workflow.name" source="exact caller identity or N/A" />
  <field name="workflow.action"><steps>Resolve ACTION_MAP code_refactor and actual template; free-mode null. Verify current required contexts/predecessors; study-only cannot fake mandatory action completion.</steps></field>
  <field name="workflow.extra_context_reference"><steps>Explicit selected source first, declared artifact/specification link, unique EPIC/FEATURE then legacy feature folder. Validate anchors, kind/content/identity, containment and symlink escape. Explicit broken or ambiguous link blocks, not fallback. Preserve caller keys.</steps></field>
  <field name="process_preference.interaction_mode" source="caller exact enum/source; default interact-with-human; reject unknown" />
  <field name="category" source="original Output Result and actual caller context" />
  <field name="next_task_based_skill" source="original conditional suggestions only; not successor authority" />
  <field name="refactoring_scope.scope_level"><steps>Explicit value first; feature when actual feature ID exists, otherwise custom with bounded files/modules/description. Missing material scope needs bounded decision.</steps></field>
  <field name="refactoring_scope.feature_id" source="actual caller/source feature identity or N/A; no allocation" />
  <field name="refactoring_scope.refactoring_purpose"><steps>Derive named improvement, credible parent contribution and concrete success comparison from authorized intent; missing material criterion is a pertinent gap, not an invented score.</steps></field>
  <field name="refactoring_scope.files" source="explicit authorized files or validated feature source component links; inspect dependencies separately" />
  <field name="refactoring_scope.modules" source="caller or verified component ownership; not neighboring-module write permission" />
  <field name="refactoring_scope.description" source="original scope/constraints and exclusions" />
  <field name="refactoring_mode"><steps>Explicit study-only/local/broad wins. Assessment-only intent defaults study-only; bounded approved edits default local; broad requires explicit scope/risk rationale. Never auto-expand local to broad.</steps></field>
  <field name="program_type" source="actual runtime/behavior/domain, not extension alone; skills use creator" />
  <field name="tech_stack" source="caller or verified manifests/runtime and affected layers" />
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Owner and authority</name><verification>Same task/readiness, mode source, approved roots/paths/exclusions known; dirty baseline protected.</verification></checkpoint>
  <checkpoint required="true"><name>Scope and goal</name><verification>Study/local/broad selected, target readable, named improvement and preservation boundaries identified; material ambiguity explicit.</verification></checkpoint>
  <checkpoint required="true"><name>Baseline capability</name><verification>Relevant tests/build/lint available or known gap; baseline failures named, not forced global repair before study.</verification></checkpoint>
  <checkpoint required="true"><name>Integration and review</name><verification>Tool contracts/adapters, workflow gates and required review resolved; candidate versus publication explicit.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Step | Action | Gate |
| --- | --- | --- |
| 1 | Analyze scope and quality | Inspected baseline and named gap |
| 2 | Targeted sync and preservation baseline | Mode/risk evidence; no contract rewriting |
| 3 | Plan structural means | Scope, trade-offs and preservation tests |
| 4 | Execute or study recommendations | No new regressions; authorized edits only |
| 5 | Compare and return | Current evidence; original output; no fake done |

## Execution Procedure

```xml
<procedure name="code-refactor">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Analyze Scope and Quality</name>
    <action>
      1. Read approved sources/requirements/spec/story/GWT AC/type/design and inspect actual code/callers/dependencies/config. Record inspected versus authorized scope and gaps; dependency discovery grants no write authority.
      2. Load x-ipe-tool-refactoring-analysis. Receive/preserve actual full_analysis operation_output when its full contract is authorized and satisfied; otherwise use disclosed scoped analysis adapter in integration, never invented tool success or numeric metrics. Retain scope, code_quality_evaluated, refactoring_suggestion, refactoring_principle and report_path when actually returned.
      3. In existing analysis/refactor report map goal/subgoal, source/parent/stakeholder, indirect contribution, inspected baseline, justified measure or qualitative success, constraints/non-goals and existing story/AC/type preservation links. all-required branches need checks; alternatives select one bounded means, not all options as backlog.
      4. Legacy explicit so-that only may supply inferred intent with anchor; missing intent blocks pertinent outcome/coverage claim, not unrelated delivery or whole-project retrofit. Separate engineering delivery from not measured stakeholder outcome.
      5. Self-check each suggestion against inspected gap/purpose/scope. For genuine decisions human asks the human within skill and waits; full DAO and hybrid use common message_context/instruction_units/execution_plan. Human and hybrid require human completion/route confirmation; full DAO selects only authorized successors. Clear authority needs no repeated confirmation; changed contract needs actual human CR authority in every mode.
    </action>
    <output>Actual analysis output or disclosed scoped adapter report; goal/baseline/preservation frame</output>
  </step_1>
  <step_2>
    <name>Sync Affected Documentation and Tests</name>
    <action>
      1. Feed Step 1 scope/quality/suggestions/principles into x-ipe-tool-code-quality-sync only under its supported authorized full_sync contract; otherwise use disclosed targeted adapter. Preserve actual result/errors/pass-through fields, not invented aligned status for absent documents.
      2. Study-only performs read-only gap assessment; no source/test/doc mutation except authorized analysis deliverable. Local reconciles affected documentation and adds targeted risk-based tests only; no blanket 80% coverage, full-global docs alignment or unrelated full-suite prerequisite. Broad plans relevant integration/full suite and justified measured coverage within authorized scope.
      3. Preserve requirements/ACs; document deviations as findings, not acceptance additions/removals to bless current code. do not skip failing tests. Relevant baseline failure blocks mutation without explicit safe disposition, not study; bugs return to owner, not incidental repair.
      4. Run applicable baseline tests/build/lint in actual domain; capture commands/exits/source/test/config hashes and pre-existing failures. Characterize approved observable interfaces/results/errors/data/side effects/concurrency/security/caller boundaries as implicated. Refactor tests need not fail first.
    </action>
    <output>Targeted sync evidence, unchanged preservation assertions, baseline failures/gaps</output>
  </step_2>
  <step_3>
    <name>Plan Improvement and Trade-offs</name>
    <action>
      1. Choose structural means using actual suggestions/principles SOLID/DRY/KISS/YAGNI/SoC; map each plan item to quality goal/baseline/after comparison/preservation checks. Small clear scope may use one combined report, not duplicate documents.
      2. Record exact allowed edits, phases, dependencies/docs/tests, trade-off, restoration using owned prework bytes and review needs. No arbitrary score or guaranteed stakeholder gain. YAGNI public removal requires verified no observable consumer, not guessed dead code.
      3. Validate bounded scope, cross-phase independence and all-required checks. Scope expansion needs actual authority; intentional behavior change needs prior actual human CR authority. Structural design Change Log never grants changed product contract.
    </action>
    <output>Bounded plan or study recommendations with trade-offs and evidence plan</output>
  </step_3>
  <step_4>
    <name>Execute Structural Changes or Study</name>
    <action>
      1. Study-only stops at recommendations without mutation. Local/broad discover and semantically route enabled stages.validation.code_refactor tools sequentially, loading operation: refactor, AAA source/AC/preservation scenarios and source/test paths. Skill-package refactors instead delegate same task/readiness to x-ipe-meta-skill-creator; no arbitrary production edits. Read integration for actual tool exceptions.
      2. Before each phase retain owned baseline bytes/hashes, not Git checkpoint commits. Tool owns its one operation; collect operation_output success/result/files/tests/lint/errors without coercion. No inline production fallback or invented feature IDs.
      3. Apply structural edits incrementally; preserve public exports/import paths/results/errors/data/workflow/side effects and existing tracing/redaction. Run unchanged assertions after each phase; new regressions block. Repair imports/re-exports, not tests masking broken public API. Restore only owned edits; never reset/stash/checkout foreign dirty work.
      4. After three failed iterations return partial outputs/blocker. Tool failure/unavailable required evidence/meaningful review gap blocks pertinent completion/publication, not candidate drafting. Disabled/absent tracing requires no new installation; enabled instrumentation needs authorized scope and preservation tests.
    </action>
    <output>Actual structural changes and preservation results, or unchanged-source study report</output>
  </step_4>
  <step_5>
    <name>Compare Before / After and Return Once</name>
    <action>
      1. Run mode/risk-appropriate final tests/build/lint; broad includes planned integration/full suite. Compare public behavior and scoped goal/AC/type/constraints, named baseline/after evidence and trade-off. New regressions block; pre-existing/unavailable checks remain explicit, never all-green or hidden by deselection.
      2. Update only affected authorized references/design Change Log, counts/paths. Measure applicable coverage with same method/scope before/after; unmeasured is a gap, not maintained. Preserve tracing/redaction; no forced setup.
      3. Bind evidence/review to actual source/test/config hashes. Report engineering delivery separately from stakeholder outcome not measured; study is recommendations, not achieved structural improvement. Edits invalidate affected evidence; retain unrelated IDs/history/evidence.
      4. Fill full original task_completion_output with actual links/counts/principles/goals and supplied legacy/dynamic attributes. Designated score strings may say not measured; no sentinel in numeric tool schema or synthetic aggregate score. Coverage strings and comparison status explicitly allow null; explain not measured/non-applicability in report. A required missing measurement blocks that claim, not unrelated study delivery.
      5. Workflow-mode completion depends on actual mandatory code_refactor gates and completed refactor report, not study-only. Return exact refactor-report mapping to owner for one authorized write/readback; no child app mutation or successors. Candidate readiness/study evidence is distinct from larger-task closure or publication.
    </action>
    <output>Original task output, report, revision-bound comparison and honest blockers</output>
  </step_5>
</procedure>
```

## Output Result

Preserve original fields/order/nested shape/counts/enums/conditional next tasks and
dynamic attributes. The two quality-score fields are designated strings allowing
`not measured`; numeric strings require a cited measurement method and comparable
before/after evidence. No new aggregate, arbitrary score, metric or app tag.
Unmeasured coverage cannot claim maintained/improved/degraded. Coverage before and
after are percentage strings or actual YAML/JSON null (not the string "null");
status is maintained/improved/degraded only for comparable measurements, otherwise
actual null. Preserve a measured side when only one side exists. Explain method,
scope, denominator, applicability and missing evidence in the report. A required
coverage claim returns blocked with these partial values; optional/non-applicable
study/local coverage does not block unrelated delivery. Consumers rejecting null
remain a disclosed compatibility blocker, never silently coerced. See integration.

```yaml
task_completion_output:
  category: "feature-stage | standalone"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-acceptance-test"
      condition: "Re-verify after refactoring"
    - skill: "x-ipe-task-based-feature-closing"
      condition: "Close feature if refactoring is the final step"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "x-ipe-docs/refactoring/analysis-{context}.md"
    - "x-ipe-docs/refactoring/validation-{context}.md"
    - "{paths to refactored files}"
  feature_id: "{from input refactoring_scope.feature_id or N/A}"
  refactoring_summary:
    files_modified: "<count>"
    files_created: "<count>"
    files_deleted: "<count>"
    principles_applied:
      - principle: "<name>"
        application_count: "<count>"
        areas: "<list>"
    goals_achieved:
      - goal: "<name>"
        status: "achieved | partial | skipped"
        notes: "<details>"
  code_quality_evaluated:
    quality_score_before: "<1-10 | not measured>"
    quality_score_after: "<1-10 | not measured>"
    test_coverage:
      before: "<percentage string | null>"
      after: "<percentage string | null>"
      status: "maintained | improved | degraded | null"
    references_updated:
      requirements: "<count>"
      specifications: "<count>"
      technical_designs: "<count>"
```

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Scope and analysis</name><verification>Inspected/authorized scope, named quality goal/baseline/source/parent and actual analysis or disclosed adapter evidenced.</verification></checkpoint>
  <checkpoint required="true"><name>Mode-aware sync</name><verification>Study gaps/local affected docs and targeted tests/broad justified integration baseline; no global retrofit or fake tool success.</verification></checkpoint>
  <checkpoint required="true"><name>Behavior preserved</name><verification>Public behavior/contracts/AC/types/constraints/callers verified; changed intent needs prior actual human CR authority.</verification></checkpoint>
  <checkpoint required="true"><name>Quality comparison</name><verification>Named measured or qualitative improvement versus baseline with trade-off; study recommendations only; no invented score/outcome.</verification></checkpoint>
  <checkpoint required="true"><name>Current verification</name><verification>Required risk checks pass at current hashes; failures/unavailable checks named, new regressions block.</verification></checkpoint>
  <checkpoint required="true"><name>Bounded records</name><verification>Affected references only, tracing/redaction preserved, dirty bytes protected, default no commit.</verification></checkpoint>
  <checkpoint required="conditional"><name>Independent review</name><verification>Meaningful workflow/executable/safety/public-contract change reviewed; unavailable blocks pertinent completion/publication, not drafting.</verification></checkpoint>
  <checkpoint required="conditional"><name>App gates</name><verification>Actual mandatory action/predecessors/contexts/refactor-report and owner readback; no study shortcut or fake done.</verification></checkpoint>
  <checkpoint required="true"><name>Original handoff</name><verification>Full original/dynamic task fields and actual tool results retained; one owner no duplicate registration/routing or successor.</verification></checkpoint>
</definition_of_done>
```

## Patterns & Anti-Patterns

| Pattern | When | Then |
| --- | --- | --- |
| Study-only | Assessment requested | Inspect/recommend without mutation or achieved change claim |
| Local | Bounded structure change | Target risks/affected docs and unchanged assertions |
| Broad | Authorized cross-module risk | Integration/full suite and justified comparable measurement |
| Skill refactor | Skill package target | Creator candidate/review/publication gates, same task |

| Anti-Pattern | Consequence | Correction |
| --- | --- | --- |
| Invent scores | Synthetic quality | Named baseline/after evidence; designated string not measured |
| Rewrite spec to code | Covert behavior change | Actual human CR authority first |
| Forced checkpoint commits | Dirty work exposure | Owned bytes/hashes; default no commit |
| Global sync for study | Scope creep | Mode-aware adapter/pertinent gaps |
| Fix public import by weakening test | External behavior lost | Preserve re-export and unchanged caller assertion |
| Study marked app done | Mandatory gate bypass | Actual integration required; partial/blocked handoff |

## Examples

Read [examples](.github/skills/x-ipe-task-based-code-refactor/references/examples.md),
[techniques](.github/skills/x-ipe-task-based-code-refactor/references/refactoring-techniques.md),
[integration](.github/skills/x-ipe-task-based-code-refactor/references/integration.md)
and [report scaffold](.github/skills/x-ipe-task-based-code-refactor/templates/refactor-report.md).
