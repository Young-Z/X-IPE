---
name: x-ipe-task-based-evaluate-change-request-efforts
description: Independently assess a Vendor Change Request against a readable local codebase and publish versioned effort, CIO, and Vendor-executable technical-design reports. Use when evaluating CR effort, comparing Vendor estimates, or generating an AI suggested solution. Triggers on requests like "evaluate change request effort", "assess vendor CR estimate", "generate CR technical design".
---

# Task-Based Skill: Evaluate Change Request Efforts

## Purpose

Produce an evidence-based CR assessment by inspecting local code at Quick, Standard, or Deep scope, building one Structured Report Model, and invoking the deterministic publisher for three offline reports.

## Important Notes

Load the [single-loop delivery policy](.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md)
once in the current context. Execute this skill in the same agent loop; another
skill is expertise, not a new agent. Use proportional checks and reuse current
evidence; independent review is conditional on concrete risk, not the skill name.

Load `x-ipe-workflow-task-execution` and its
[common lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md).
Reuse the supplied task/readiness; direct entry calls Orient/Plan once without
recursively dispatching this skill. One owner handles task/feature/app writes,
Git and the next boundary. Return full output; do not register or execute a
successor. Within-skill questions follow the three existing interaction modes;
clear inputs need no question or DAO call. Explicit human approvals still bind.

BLOCKING: Learn `x-ipe-workflow-task-execution` before execution.
BLOCKING: Never modify the assessed codebase or directly compose final HTML in reasoning.
MANDATORY: Read [assessment method](.github/skills/x-ipe-task-based-evaluate-change-request-efforts/references/assessment-method.md) and validate against the bundled schema.

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX | N/A}"
  task_based_skill: x-ipe-task-based-evaluate-change-request-efforts
  execution_mode: "free-mode | workflow-mode"
  workflow: {name: N/A}
  category: standalone
  next_task_based_skill: null
  process_preference:
    interaction_mode: "interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill"
  case_folder: "{project-relative case folder}"
  analysis_depth: "quick | standard | deep"
```

### Input Initialization

```xml
<input_init>
  <field name="case_folder" source="Console prompt; normalize relative to project root and require a FEATURE-060-A case folder" />
  <field name="analysis_depth" source="Console prompt; lowercase; default standard; allow only quick, standard, deep" />
  <field name="process_preference.interaction_mode" source="caller or interact-with-human" />
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Case contract valid</name><verification>CaseRecord envelope and latest invocation snapshot parse successfully</verification></checkpoint>
  <checkpoint required="true"><name>Codebase readable</name><verification>Snapshot codebase_path is a readable local directory</verification></checkpoint>
  <checkpoint required="true"><name>Required evidence present</name><verification>CR description and Vendor estimate references resolve within the case folder</verification></checkpoint>
  <checkpoint required="true"><name>Depth valid</name><verification>Depth is quick, standard, or deep</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Phase | Step | Name | Action | Gate |
|---|---|---|---|---|
| 1. 博学之 (Study Broadly) | 1.1 | Load case | Validate snapshot, evidence, repository, method, benchmarks, schema | Inputs valid |
| 1. 博学之 (Study Broadly) | 1.2 | Inspect code | Inspect required depth and record observed/inferred/unverified evidence | Coverage recorded |
| 2. 审问之 (Inquire Thoroughly) | 2.1 | Resolve gaps | Identify missing evidence and qualify scope without silent downgrade | Gaps explicit |
| 3. 慎思之 (Think Carefully) | 3.1 | Estimate and design | Decompose modules, ranges, confidence, comparison, and implementation blueprint | Totals reconcile |
| 4. 明辨之 (Discern Clearly) | 4.1 | Validate model | Challenge unsupported factors, asymmetric conclusions, and unverifiable design | Model schema-ready |
| 5. 笃行之 (Practice Earnestly) | 5.1 | Publish | Save candidate model and run publisher | Receipt returned |
| 5. 笃行之 (Practice Earnestly) | 5.2 | Complete | Verify outputs and report status | DoD valid |
| 6. 继续执行 | 6.1 | Decide next action | Return reports for human review | Decision recorded |

BLOCKING: Do not publish until every model total reconciles and every AI productivity factor has module evidence.

## Execution Procedure

```xml
<procedure name="evaluate-change-request-efforts">
  <execute_dor_checks_before_starting/>
  <phase_1 name="博学之 — Study Broadly">
    <step_1_1><name>Load and Validate</name><action>1. Resolve case_folder and depth. 2. Parse CaseRecord and latest snapshot. 3. Read required evidence and assessment-method.md. 4. Load benchmarks-v1.json and report-model-v1.schema.json.</action><output>Validated context and provenance</output></step_1_1>
    <step_1_2><name>Inspect Repository</name><action>1. For quick inspect targets and immediate implementation/tests. 2. For standard add dependencies, integrations, data and regression impact. 3. For deep add full reachable baseline and systemic risk. 4. Tag every finding observed, inferred, or unverified with project-relative evidence.</action><output>Coverage and evidence inventory</output></step_1_2>
  </phase_1>
  <phase_2 name="审问之 — Inquire Thoroughly">
    <step_2_1><name>Resolve Evidence Gaps</name><action>1. Identify unreachable or ambiguous scope. 2. Continue with a qualified result when mandatory inputs remain valid. 3. Record gaps, evidence needed, and confidence reduction. 4. Never silently downgrade the requested depth.</action><output>Qualified scope statement</output></step_2_1>
  </phase_2>
  <phase_3 name="慎思之 — Think Carefully">
    <step_3_1><name>Build Assessment</name><action>1. Decompose ordered modules/work packages. 2. Prefer repository evidence over benchmarks. 3. Apply AI adjustment only per module with reuse, tooling, coverage, and bounded-ambiguity evidence. 4. Produce symmetric Vendor comparison. 5. Create adoption summary plus contracts, data, sequences, tests, rollout, rollback, and traceability. 6. Use the dominant case language while preserving technical identifiers.</action><output>Structured Report Model candidate</output></step_3_1>
  </phase_3>
  <phase_4 name="明辨之 — Discern Clearly">
    <step_4_1><name>Validate Conclusions</name><action>1. Reconcile module and work-package totals. 2. Reject blanket AI discounts and unsupported confidence. 3. Verify design reuse and effort savings share the same evidence. 4. Verify Mermaid source contains no click callbacks or HTML labels. 5. Write model JSON to a temporary case-local path.</action><output>Publisher-ready model</output></step_4_1>
  </phase_4>
  <phase_5 name="笃行之 — Practice Earnestly">
    <step_5_1><name>Publish Reports</name><action>1. Run `python .github/skills/x-ipe-task-based-evaluate-change-request-efforts/scripts/publish_reports.py --case-folder {case_folder} --model {model_path}`. 2. If nonzero, preserve prior latest version and report the non-sensitive error. 3. If zero, parse the JSON receipt and verify every output.</action><output>Publication receipt and four artifacts</output></step_5_1>
    <step_5_2><name>Complete</name><action>1. Verify DoD. 2. Present latest report links and qualified gaps. 3. Require human review for commercial use.</action><output>Task completion output</output></step_5_2>
  </phase_5>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: standalone
  status: "completed | blocked"
  next_task_based_skill: null
  process_preference:
    interaction_mode: "{from input}"
  execution_mode: "{from input}"
  workflow: {name: "{from input}"}
  task_output_links: ["{CaseRecord}", "{effort_report}", "{design_report}", "{report_model}"]
  assessment_depth: "{depth}"
  coverage: "complete | qualified"
```

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Evidence traceable</name><verification>Every module cites observed, inferred, or unverified evidence</verification></checkpoint>
  <checkpoint required="true"><name>Estimate auditable</name><verification>Ranges, confidence, assumptions, benchmarks, AI factors, and totals reconcile</verification></checkpoint>
  <checkpoint required="true"><name>Design executable</name><verification>Contracts, work packages, tests, rollout, rollback, and acceptance trace to effort</verification></checkpoint>
  <checkpoint required="true"><name>Publication complete</name><verification>Receipt lists model and three reports; CaseRecord latest/history metadata is consistent</verification></checkpoint>
  <checkpoint required="true"><name>Prior version safe</name><verification>No failed run replaces the latest valid version</verification></checkpoint>
</definition_of_done>
```

## Patterns & Anti-Patterns

| Pattern | When | Then |
|---|---|---|
| Qualified assessment | Selected depth has unreachable scope | Publish gaps and reduced confidence; do not downgrade |
| Evidence-gated AI factor | Reuse, tooling, tests, and ambiguity support acceleration | Apply and explain a module-only factor |

| Anti-Pattern | Why Bad | Do Instead |
|---|---|---|
| Blanket AI discount | Unsupported and commercially misleading | Gate each module adjustment with evidence |
| Benchmark overrides code | Ignores actual delivery context | Use repository evidence first |
| Generate HTML in reasoning | Unsafe and inconsistent | Generate the model and invoke the publisher |
| Modify assessed code | Violates assessment independence | Read only and propose changes in the design report |

## Examples

See [examples](.github/skills/x-ipe-task-based-evaluate-change-request-efforts/references/examples.md).
