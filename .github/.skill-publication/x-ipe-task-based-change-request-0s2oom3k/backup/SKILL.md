---
name: x-ipe-task-based-change-request
description: Process change requests with critical goal/subgoal delta evaluation, actual requirements/spec/design/code/dependency conflicts and modification versus new-feature classification. Use when changing approved scope or acceptance. Triggers on "change request", "CR", "modify feature", "update requirement".
---

# Task-Based Skill: Change Request

## Purpose

Critically evaluate a CR against the full affected goal-to-acceptance pipeline,
classify modification versus new_feature, obtain bounded approval, and update
approved delta documents before implementation. Return original evidence and
successor suggestions, not an independently executed downstream pipeline or a
claim of achieved stakeholder benefit.

## Important Notes

BLOCKING: Load [shared workflow](.github/skills/x-ipe-workflow-task-execution/SKILL.md),
[common lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md)
and [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md).
Direct entry uses supplied task/readiness through Orient/Plan once, without
recursively dispatching this child. One owner handles registration, app/board/Git
persistence and completion/routing; child owns domain analysis and approved docs.
No board, Git, successor execution or recursive lifecycle work in this child.

BLOCKING: Goal/subgoal delta coverage is mandatory for new/changed scope in the
existing CR artifact, not new output keys, board fields, app tags or a goal DB.
Never covertly redefine goals, acceptance, success criteria, constraints or authority
to match implementation. Means aligned to an existing goal can be implementation
change; a new stakeholder outcome may need a new feature, but not automatically
any new subgoal. Preserve all unaffected IDs, history and evidence.
Read [integration boundaries](.github/skills/x-ipe-task-based-change-request/references/integration.md)
before interpreting source paths, workflow gates, tags or tool availability.

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: x-ipe-task-based-change-request
  execution_mode: free-mode | workflow-mode
  workflow:
    name: N/A
    action: change_request
    extra_context_reference:
      closing-report: "path | N/A | auto-detect"
      specification: "path | N/A | auto-detect"
  category: standalone
  next_task_based_skill:
    - skill: x-ipe-task-based-feature-refinement
      condition: When CR modifies an existing feature
    - skill: x-ipe-task-based-feature-breakdown
      condition: When CR requires a new feature
  process_preference:
    interaction_mode: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
  change_request_description: "{requested change}"
  business_justification: "{why}"
  requestor: "{name/role or unknown}"
  priority: medium
  requirement_details_path: x-ipe-docs/requirements/requirement-details.md
  features_path: x-ipe-docs/planning/features/features.json
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing lifecycle task/readiness; same supplied ID, no duplicate" />
  <field name="task_based_skill" source="exact discovered canonical name" />
  <field name="execution_mode" source="caller; default free-mode" />
  <field name="workflow.name" source="exact named workflow or N/A; no guessed identity" />
  <field name="workflow.action"><steps>Validate change_request against ACTION_MAP and current template; no invented action.</steps></field>
  <field name="workflow.extra_context_reference"><steps>Selected specification, declared/board link, then unique EPIC/FEATURE or legacy folder. closing-report optional; explicit selections validated. Required workflow specification must exist. Broken, ambiguous, wrong-feature, escaping links block, not hidden by fallback; retain anchors and hashes.</steps></field>
  <field name="process_preference.interaction_mode" source="lifecycle resolved exact enum/source; default interact-with-human; reject unknown" />
  <field name="change_request_description" source="source user intent; distinguish means from outcome" />
  <field name="business_justification" source="source rationale; consequential uncertainty uses decision policy" />
  <field name="requestor" source="actual name/role or unknown; not implied approver" />
  <field name="priority" source="supplied priority or medium; urgency does not waive gates" />
  <field name="requirement_details_path"><steps>Selected source, declared link/parts/index, then validated default; inspect affected parts and retain source anchors/approved roots.</steps></field>
  <field name="features_path" source="current JSON feature board read through owner/board manager; no legacy CRUD alias" />
  <field name="category" source="standalone from Output Result" />
  <field name="next_task_based_skill" source="original conditional suggestions; never execute successor" />
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Ownership and intent</name><verification>Same task/readiness, authorized paths, description, justification and exact mode known.</verification></checkpoint>
  <checkpoint required="true"><name>Requirements and features</name><verification>Sources/parts and current board resolve with revisions; related feature or honest no-match recorded.</verification></checkpoint>
  <checkpoint required="true"><name>Feature/workflow context</name><verification>Applicable specification and current gates resolve; optional closing-report not mandatory; no invented IDs.</verification></checkpoint>
  <checkpoint required="true"><name>Delta and review plan</name><verification>Full affected pipeline baseline, source/parent goals, gaps and approval/review needs identified; inference labeled.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Phase | Action | Gate |
| --- | --- | --- |
| 1. 博学之 — Study Broadly | Context, source goals and critical alternatives | Inspected baseline |
| 2. 审问之 / 慎思之 — Inquire and Think | Matrix and actual conflicts | Conflicts before classification |
| 3. 明辨之 — Discern Clearly | Classify and consolidate approval | Authority before target edits |
| 4. 笃行之 — Practice Earnestly | Approved document deltas | Histories retained; no implementation |
| 5. Verify and Return | Evidence and original result | One owner handles lifecycle boundary |

## Execution Procedure

```xml
<procedure name="change-request">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Study and critically evaluate scope</name>
    <action>
      1. Read exact intent/requirements/parts/index, related features/statuses/stories/GWT ACs/types/out-of-scope, mockups and prior CRs. Inspect relevant designs, actual implementation/tests and acceptance/closing/quality evidence when available.
      2. Evaluate the full affected pipeline: source intent → parent goal/subgoal → feature/story/AC → selected means/design/code → validation/review → delivery/outcome. Missing evidence is a named gap, not all stages passed; do not execute every downstream skill.
      3. Challenge necessity, existing configuration, alternative means, not-changing effects, compliance and unintended effects. Configured enabled research only for consequential uncertainty; document unavailable/N/A, no mandatory web ceremony.
      4. Draft CR goal delta: stakeholder, observable before/proposed outcome, source/parent, credible contribution, all-required versus selected alternatives, justified measure or qualitative success scenario, constraints/non-goals, story/AC/evidence links and delta kind.
      5. Legacy explicit so-that intent is inferred with exact source, not confirmed. Ambiguity blocks pertinent outcome/coverage claims and needs bounded clarification; no unrelated retrofit or invented metrics/benefit.
    </action>
    <output>Inspected baseline, critical evaluation, source-goal delta and gaps</output>
  </step_1>
  <step_2>
    <name>Analyze impact and actual conflicts</name>
    <action>
      1. Fill Users, Workflow, Data Model, UI Elements and API Endpoints matrix: before/proposed facts, artifact clauses/revisions, feature boundaries, callers/dependencies and reasoned N/A.
      2. Examine actual requirement/specification/design/code/tests, dependent features, pending CRs and current mockup clauses. Conflict Detector independent review for meaningful workflow/executable/safety/public-contract risk; unavailable reviewer is recorded, not fabricated.
      3. Each conflict records type, affected feature/goal/AC, severity, expected/unexpected, exact source/anchor/hash, consequence and mitigation. No-conflict claim names inspected sources; unavailable artifacts are gaps, not empty conflicts.
      4. Distinguish minor inline delta from major contradiction/structural redesign needing retirement/replacement. Unanalyzed conflicts block classification; unresolved unexpected conflicts block application/completion until authorized mitigation, narrowed scope or approved bounded deferral with residual risk.
    </action>
    <output>Evidence-backed matrix, classified conflicts and proposed resolutions</output>
  </step_2>
  <step_3>
    <name>Classify and approve once at the real boundary</name>
    <action>
      1. No related feature, fundamentally changed purpose or independent stakeholder/workflow boundary favors new_feature; within approved outcome/acceptance/constraints favors modification. UI/API/data/components/effort alone do not decide; new enabling subgoal is not automatically new_feature.
      2. Record goal-delta/matrix/conflict reasoning. Propose separately authorized split for incompatible intents; do not invent tasks or IDs.
      3. Present one consolidated decision for necessary clarifications, classification, conflicts, goal/acceptance/success/constraint delta, exact changed sections, mockup/version/retirement plan and write authority before any target document mutation.
      4. Re-read mode: Human asks the human within skill and waits; full DAO and hybrid answer actual bounded questions through common message_context/instruction_units/execution_plan. DAO guidance is not human permission. Beyond-approved scope/acceptance/goal changes and large-scope changes require actual human approval in every mode (multiple features, structural redesign, major AC rewrites or new workflows).
      5. Reuse exact-revision approval already supplied and covering classification/conflict dispositions; clear approved inputs need no repeated confirmation or ceremonial DAO. Changed proposal returns only to affected analysis and consequential missing approval; missing authority returns blocked draft, not silently applied edits.
    </action>
    <output>Bounded classification and exact-revision approval or blocker</output>
  </step_3>
  <step_4>
    <name>Apply only approved artifact deltas before implementation</name>
    <action>
      1. One complete template CR in validated existing owning feature folder; stable reserved CR ID, no duplicate record/version/decision on unchanged resume. Integration's explicit no-feature intake exception applies; never recurse to allocate a folder.
      2. Modification updates affected specification/history and requirements for high-level capability/constraints/user types/multiple features/project rules. new_feature updates requirements and any affected existing specification/history; no existing specification is explicit free-mode N/A, not fake update. New specification belongs to later approved breakdown/refinement; new_feature_ids empty until real allocation.
      3. Approved minor conflicts inline; major preserve old sections under [RETIRED by CR-XXX] with reason/date/source CR/replacement. Preserve prior version rows and reserved IDs/old-to-new mapping; no silent contract deletion.
      4. Update affected source/goal/story/GWT AC/type/validation links and design context before implementation. Changed scope maps to planned checks and honest outcome gaps; never weaken ACs to make faulty code pass. Invalidate affected dependent design/test/review/outcome evidence; preserve unaffected section/evidence bytes.
      5. UI/UX changes with existing mockups create new version preserving originals; update Linked Mockups and CR impact. Current in-scope mockups map to UI acceptance; outdated directional references cannot override requirements by date.
      6. No code implementation, successor execution or feature-status mutation; record actual document deltas and remaining work; suggest refinement versus breakdown to owner.
    </action>
    <output>Approved delta artifacts, retained history, invalidation and actual links</output>
  </step_4>
  <step_5>
    <name>Verify and return</name>
    <action>
      1. Verify complete CR, affected source/parent/subgoal/story/AC/type/success/constraint links, approval revision, conflicts, histories and mockups. Rehash relevant inputs; stale edits invalidate affected checks/review/approval, not unrelated evidence.
      2. Separate verified engineering delivery from observed stakeholder outcome or not measured. Document checks, fixtures, approval and DAO are not observations; missing required independent review blocks the pertinent claim.
      3. Return every original output key unchanged in shape/order with actual artifacts/IDs/deltas. completed requires applicable domain gates; blocked retains partial links and unresolved decisions in CR. No new goal/output/action schema.
      4. Return exact changed paths/evidence to one lifecycle owner. Workflow owner verifies current action/context/predecessors and both cr-doc/cr-folder tags, writes once and reads back. Free-mode no app writes; writer success alone cannot prove domain completion.
      5. Owner handles one boundary: human and hybrid require human review and completion/route confirmation; hybrid uses DAO only within skill; full DAO selects only authorized routes. Explicit human approval binds in every mode. No duplicate child routing or implicit successor permission.
    </action>
    <output>Original task_completion_output and evidence/owner handoff</output>
  </step_5>
</procedure>
```

## Output Result

Retain the entire original declaration. Runtime paths resolve actual legacy or
EPIC ownership; never invent new-feature IDs/artifacts to fill placeholders.

```yaml
task_completion_output:
  category: standalone
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "When CR modifies an existing feature"
    - skill: "x-ipe-task-based-feature-breakdown"
      condition: "When CR requires a new feature"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md"
  feature_id: "{FEATURE-XXX}"
  cr_id: "CR-XXX"
  cr_classification: modification | new_feature
  affected_features: ["FEATURE-XXX"]
  new_feature_ids: ["FEATURE-XXX"]
  requirement_updated: true | false
  mockup_updated: true | false
  updated_mockup_paths: []
  conflicts_found: []
  conflicts_resolution: "none | all_expected | mitigated"
  conflicting_docs_updated: []
  conflicting_docs_retired: []
```

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>CR documented</name><verification>Complete actual owning CR or authorized no-feature free-mode intake; no fictional links/IDs.</verification></checkpoint>
  <checkpoint required="true"><name>Critical classification</name><verification>Full affected pipeline/five-axis matrix support modification/new_feature; conflicts analyzed first.</verification></checkpoint>
  <checkpoint required="true"><name>Goal delta</name><verification>Changed source/parent/stakeholder/outcome/contribution/success/constraint/story/AC/type/evidence covered; inference/gaps honest.</verification></checkpoint>
  <checkpoint required="true"><name>Conflicts resolved</name><verification>Actual clause/revision evidence and authorized expected/unexpected dispositions; no hidden blockers.</verification></checkpoint>
  <checkpoint required="true"><name>Approval before application</name><verification>Exact revision/sections/authority before edits; actual human large-scope/changed-contract gate in every mode, no repeated confirmation.</verification></checkpoint>
  <checkpoint required="true"><name>Documents and histories</name><verification>Applicable specs/requirements updated on both paths; no-feature N/A justified; major retirements and original IDs/history retained.</verification></checkpoint>
  <checkpoint required="if-applicable"><name>Mockups</name><verification>Originals preserved, new version and Linked Mockups/CR impact reflect approved UI delta.</verification></checkpoint>
  <checkpoint required="true"><name>Evidence and review</name><verification>Affected evidence invalidated, unrelated retained, current hashes and risk review present or blocked; no outcome invented.</verification></checkpoint>
  <checkpoint required="true"><name>Owner handoff</name><verification>All original fields preserved; actual tags/gates/evidence to one owner; suggestions only, no child lifecycle/Git work.</verification></checkpoint>
</definition_of_done>
```

## Patterns & Anti-Patterns

| Pattern | When | Then |
| --- | --- | --- |
| Enhancement/means change | Same approved goal/boundaries | modification; preserve outcome, update affected means/AC docs |
| New capability | Separate outcome/boundary or no owner | new_feature; approved requirements/actual intake, no invented allocation |
| Multi-feature/CR chain | Shared impact/subsequent extension | Inspect callers/pending CRs; one coherent classification or approved split |
| Major conflict | Contradicts approved contract | Human-approved retirement/history/replacement before implementation |

| Anti-Pattern | Consequence | Correction |
| --- | --- | --- |
| Skip conflict analysis / classify first | Miss dependency break | Inspect actual clauses/code before classification |
| New subgoal/screen automatically new feature | Means mistaken for intent | Parent contribution and approved boundaries decide |
| Redefine success to match code | Covert scope change | Preserve source contract; changed-contract authority |
| Apply conflict edits then ask | Unauthorized mutation | Consolidated approval before all target writes |
| Repeat every confirmation | Ceremonial duplication | Reuse current bounded approval; consequential delta only |
| Fake tag/ID or recursive breakdown | False completion | Required contexts/exact tags and one owner |

## Examples

Read [complete use cases](.github/skills/x-ipe-task-based-change-request/references/examples.md),
[classification patterns](.github/skills/x-ipe-task-based-change-request/references/patterns.md),
[CR template](.github/skills/x-ipe-task-based-change-request/templates/change-request.md),
[version history rules](.github/skills/x-ipe-task-based-change-request/references/version-history-template.md)
and the authoritative [specification scaffold](.github/skills/x-ipe-task-based-feature-refinement/references/specification-template.md).
