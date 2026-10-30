---
name: x-ipe-task-based-feature-breakdown
description: Break requirements into Epics and features with MVP-first sizing, dependencies and verified feature-board registration. Use when requirements need to be split into discrete features. Triggers on requests like "break down features", "split into features", "create feature list", "organize epics".
---

# Task-Based Skill: Feature Breakdown

## Purpose

Translate approved requirements into cohesive Epics and independently deliverable
features, a runnable MVP-first order, direct dependencies and real board entries.
Reuse fresh requirement findings; carry only authorized new/small/CR deltas into
consolidated Feature Lists and details without regenerating stable features.

## Important Notes

Load the [single-loop delivery policy](.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md)
once in the current context. Execute this skill in the same agent loop; another
skill is expertise, not a new agent. Use proportional checks and reuse current
evidence; independent review is conditional on concrete risk, not the skill name.

BLOCKING: Load the [common lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md).
Caller supplies readiness; direct entry loads the workflow and calls Orient/Plan
once, returning here without recursively dispatching this child. Lifecycle owns
task registration/status, Git and completion/routing. This child owns breakdown
documents, feature registration and the agreed verified application action.
Never create/close a task, commit or execute the suggested successor here.

CRITICAL: New IDs are FEATURE-{nnn}-{X}, matching parent EPIC-{nnn}; never use an
EPIC ID as a Feature ID. Preserve legacy FEATURE-{nnn} IDs and both legacy
FEATURE folders and EPIC/FEATURE folders. Resume reuses identities and artifacts.
Board feature creation is domain work, NOT duplicate lifecycle task registration.

BLOCKING: Apply the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
to every new/changed feature in the existing consolidated details: deliverable
contributes a subgoal with parent requirement/source, success evidence and gaps.
Keep stable shared folders/index and identities; legacy inference is labeled.

BLOCKING: Use x-ipe-tool-task-board-manager for actual feature CRUD, never edit
features.json manually or invent batch/archive/delete operations. New features
start Planned; existing statuses and specifications are not reset by breakdown.
All feature details remain in requirement-details (or its selected part), not
individual feature.md files. Specifications belong to later Feature Refinement.

## Input Parameters

```yaml
input:
  task_id: "{existing TASK-XXX}"
  task_based_skill: "x-ipe-task-based-feature-breakdown"
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A or resolved workflow"
    action: "feature_breakdown"
    extra_context_reference:
      requirement-doc: "path | N/A | auto-detect"
  category: "requirement-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "Refine the first unstarted feature. Each feature goes through the complete pipeline (refinement → design → implementation → testing → closing) one at a time before starting the next."
  process_preference:
    interaction_mode: "interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill"
  mockup_list: "N/A"  # or [{mockup_name, mockup_link}]
  requirement_doc: "x-ipe-docs/requirements/requirement-details.md"  # or selected part
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing lifecycle identity/readiness; no child task allocation" />
  <field name="task_based_skill" source="this canonical entry; category and next suggestion from Output Result" />
  <field name="execution_mode" source="caller context; default free-mode" />
  <field name="workflow.name" source="validated caller workflow; N/A only free-mode" />
  <field name="workflow.action">
    <steps>Verify feature_breakdown against ACTION_MAP and workflow template; shared mandatory action, not a tool configuration key.</steps>
  </field>
  <field name="process_preference.interaction_mode" source="common lifecycle exact resolved enum/source" />
  <field name="workflow.extra_context_reference.requirement-doc">
    <steps>Explicit selected context first, then requirement_doc/upstream output, then legacy auto-detection. Validate contents, root containment, source/Epic identity and SHA256; explicit broken or conflicting selections block rather than fall back. Workflow-mode requires a populated requirement-doc even if N/A was supplied.</steps>
  </field>
  <field name="requirement_doc">
    <steps>Absent/auto input uses highest numeric requirement-details-part-X, else requirement-details.md. Reconcile all parts/index and locate affected older features too. Explicit affected-part selection outranks newest-part fallback. Free-mode direct request is allowed only when documented into real requirement artifacts before completion.</steps>
  </field>
  <field name="mockup_list">
    <steps>Use explicit validated links, then Requirement Gathering/Idea Mockup output, then selected Epic/mockups or linked idea/mockups. No unrelated-folder scan. Preserve mockup_name/mockup_link; absent optional mockups are N/A.</steps>
  </field>
  <field name="breakdown_context">
    <steps>Reuse fresh requirement source/parts/index hashes, scope/conflict decisions, acceptance, risks and impacted_features. Inventory current feature IDs/reservations, board and workflow entries; record changed/affected boundaries and evidence invalidation, not timestamps alone.</steps>
  </field>
  <field name="epic_context">
    <steps>Reuse intake Epic from gathered document/output or matching existing feature. For additional authorized groupings scan Epic folders, headers and board reservations; allocate highest number + 1 and recheck collisions. Never allocate a second Epic merely because this is the next task.</steps>
  </field>
  <field name="document_language" source="explicit requested language, else established requirement language; retain EN/ZH IDs/paths/tags unchanged" />
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Owner and intent</name><verification>Supplied task/readiness, approved scope/root, mode and authorized new/small/CR delta match.</verification></checkpoint>
  <checkpoint required="true"><name>Sources and coverage</name><verification>Requirement contents or free-mode request resolved; Epic, current parts/index, upstream findings and affected features identified.</verification></checkpoint>
  <checkpoint required="true"><name>Integration safe</name><verification>Actual board/helper schemas loaded; inventory is readable, write scope and app action owner known; no unresolved destructive/identity decisions.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Step | Domain work | Gate |
| --- | --- | --- |
| 1 | Reuse context, bound delta and assess Epic grouping | Current scope and grouping rationale |
| 2 | Size units, separate MVP, validate dependencies | Coverage and deliverable order decided |
| 3 | Author targeted lists/details, register real features | Documents, IDs and board consistent |
| 4 | Verify action/artifacts and return full result | DoD evidence or honest blocked output |

Load [domain guidelines](.github/skills/x-ipe-task-based-feature-breakdown/references/breakdown-guidelines.md)
and [integration](.github/skills/x-ipe-task-based-feature-breakdown/references/integration.md)
before domain work. Study/inquiry/reflection/decision combine proportionately;
no forced re-interview, five-phase ceremony or duplicate upstream research.

## Execution Procedure

```xml
<procedure name="feature-breakdown">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Bound scope and grouping</name>
    <action>
      1. Reuse fresh what/who/why, acceptance, scope, conflicts, risk and mockup findings. Compare current SHA256 revisions and inventory; refresh changed/affected facts only, or establish missing coverage. Do not redo the requirement interview.
      2. Classify new/single-feature/CR delta; preserve approved existing-feature impact decisions. Challenge only material unresolved MVP, overlap, domain or priority choices; human asks the human within skill and waits; full DAO and hybrid receive bounded guidance through common message_context/instruction_units/execution_plan.
      3. Assess estimated feature count, domain diversity, dependency clusters and team boundaries. Reuse intake Epic for single domain &lt;=7 features; 2-3 domains/8-15 features suggest 2-3 Epics; 4+ domains or >15 suggest multiple Epics. Borderline cases need cohesion/coupling rationale, not automatic allocation.
      4. Decide grouping before assigning new feature IDs. Additional Epics require approved scope/links to intake. Existing CR targets keep their original Epic even when the intake has a newer Epic. Record actual grouping, scope and deferred capabilities without silently dropping requirements.
    </action>
    <output>Revision-bound context reuse, scoped delta and Epic assessment</output>
  </step_1>
  <step_2>
    <name>Size, separate MVP and order</name>
    <action>
      1. Count ACs per proposed feature: under 10 likely one; 10-20 evaluate distinct capabilities and outcome contributions; more than 20 ACs MUST split along natural boundaries. Layers/files signal risk, not a feature per technical layer reflex; assess user value and foundation/consumer depth; keep 5-7 features per Epic maximum.
      2. Apply Single Responsibility, Independence, Deliverable Value and Reasonable Size. First new feature in each Epic is Minimum Runnable Feature (MVP), a testable vertical runnable outcome, not a bare interface. Subsequent features add value without bloating the MVP; do not reselect a stable existing MVP for a CR.
      2a. Explain each feature deliverable's credible subgoal contribution to its parent requirement, including indirect enabling value. Reuse existing FR/US/AC or stable doc-local G IDs; bound goals by coherent scope without fixed minimums/caps. Separate all-required decomposition from alternatives: select/bound one means with rationale, do not create features for every rejected option.
      3. Preserve every requirement/FR/AC through explicit feature coverage or approved deferral. Aim for 3-7 concise ACs without padding; retain required edge/security cases and &lt;=20 ceiling. Use &lt;=50-word brief descriptions and specific action-oriented titles.
      4. Reserve new FEATURE-{nnn}-{A|B|C...} suffixes from current documents, folders, board and history; never renumber/reuse retired IDs or fill historic gaps. New features use v1.0; existing versions change only for an approved minor v1.1/v1.2 or major v2.0 delta.
      5. Record only direct dependencies with reasons, including cross-Epic or legacy targets. Validate references, self/circular dependencies and the DAG across changed plus existing impacted edges; foundations first and topological implementation order. No synthetic dependency just to force sequential routing.
      5a. Existing board dependencies contain only selected actual all-required edges. Alternative selection and non-selected rationale stay in document coverage, not unsupported dependency/goal fields; chosen means remain adaptable within approved contracts.
      6. Single-feature lightweight path records one feature, MVP rationale, ACs and actual registration; no ceremonial split. Incremental CR updates only affected rows/details/dependencies; preserve stable IDs, versions, status and specifications outside authorized changes.
      7. Confirm prioritized feature-list completeness before refinement: human and hybrid require human completion/route confirmation; full DAO uses bounded common-policy guidance and only authorized routing. Reuse a recorded confirmation only when it covers this exact list/revision; material edits invalidate it. Explicit domain human approval binds in every mode. Return unresolved confirmation as blocked, never silently waive this domain gate or execute refinement.
    </action>
    <output>Covered feature units, stable IDs, MVP and validated dependency order</output>
  </step_2>
  <step_3>
    <name>Author and register delta</name>
    <action>
      1. Upsert Feature List and detailed sections only in selected owning requirement part; list never lives only in index. Free-mode request gets a real populated document. Keep requirement_id if present; do not invent REQ IDs for Epic-only inputs.
      2. Use retained templates for Feature ID/Epic ID/title/version/brief description/dependency, ACs, technical considerations, mockups and coverage/evidence. Create/reuse new EPIC/FEATURE folders; preserve legacy folders. Do not create specifications or individual feature.md files here.
      2a. Add subgoal/parent/source, GWT leaf ACs, success scenario and outcome evidence gaps in the existing details/coverage section. Require honest coverage for new/changed scopes; CR carries parent delta and affected evidence invalidation, legacy explicit so-that inference keeps its source/label without historical rewrites.
      3. Keep shared mockups at EPIC-{nnn}/mockups; preserve extension, validate local/URL sources and copy only missing authorized files, never overwrite foreign bytes. Generated links are project-root-relative, never ../mockups, ./ or absolute paths. Map actual mockups to covered features; N/A stays honest.
      4. Update index coverage/line counts when parts exist, preserving other part contents. Do not re-split or regenerate all stable documents as a CR side effect; use requirement splitting contract only if genuinely needed within approved scope.
      5. Load board manager; query before create/update. Sequential feature_create.py --feature JSON for absent new IDs uses actual required fields/status Planned. Query readback verifies identity, title/version/dependencies. Matching resume is read-only, not another create; collision/corrupt state blocks. No task CRUD or manual features.json.
      6. CR uses feature_update.py only for authorized mutable fields after matching current identity; epic_id is immutable. Never reset existing status to Planned. For a genuine split compare each parent FR/AC against children: partial coverage retains parent and dedup_gaps; full coverage permits authorized Retired status and removal from active breakdown, preserving historical record and redirects. Do not invent archive/delete API; list parent_features_removed only after both actual changes.
    </action>
    <output>Populated lists/details/folders/mockups/index and verified feature registrations</output>
  </step_3>
  <step_4>
    <name>Verify action and return</name>
    <action>
      1. Verify domain DoD and current source/document/board/config hashes, coverage, language, dependency order, actual new Planned records and preserved stable state. Use self-checks and targeted tests by default; independent review is required only for an explicit request or concrete high-risk uncertainty under the shared single-loop policy. Reuse suitable current review; missing required review blocks the affected claim, not drafting.
      2. Workflow-mode checks requirement_gathering is actually done with valid artifacts and required context. Verify prerequisite states, not helper success or skipped flags. Free-mode makes no app write and returns workflow_action_updated false.
      3. Initial workflow action uses installed workflow_update_action.py --workflow NAME --action feature_breakdown --status done --deliverables keyed JSON --features JSON --format json. Supply BOTH features-list = actual populated Feature List file and breakdown-folder = scalar existing folder containing the breakdown; one requirement part/root requirements directory can satisfy these real artifacts.
      4. Workflow feature payload is id/name/depends_on, not board feature_id/title/dependencies. Query current state first; helper appends blindly. Send only absent new entries after validating collisions/edges; never resend existing entries or reset per-feature stages. Completed unchanged resume verifies without replay.
      5. CR-only already-done action verifies preserved entries/deliverables and current actual artifacts without write; true only with verified prior write evidence. If pending/failed action has only existing entries, helper requires nonempty --features and would duplicate them: return blocked, do not bypass. Needed existing workflow dependency changes require separately supported authorized reconciliation; no silent JSON edits or false synchronization.
      6. Read workflow_get_state.py; shared.requirement.actions.feature_breakdown must be done with both exact artifacts and intended features/depends_on, unique IDs and preserved existing stages. Missing/invalid artifacts, failures or unsatisfied gates block; writer success alone is insufficient. Return full output/evidence once; lifecycle owns human review and one sequential first-unstarted-feature suggestion boundary.
    </action>
    <output>Verified domain result or blocked output with actual partial links</output>
  </step_4>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: "requirement-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "Refine the first unstarted feature. Each feature goes through the complete pipeline (refinement → design → implementation → testing → closing) one at a time before starting the next."
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"
  workflow_action_updated: true | false
  task_output_links:
    - "x-ipe-docs/requirements/requirement-details.md"  # actual selected part
  mockup_list: "{inherited from input or N/A}"
  requirement_id: "REQ-XXX"  # retain actual ID; N/A if no REQ identity
  epic_ids: ["EPIC-001", "EPIC-002"]
  epic_count: 2
  feature_ids: ["FEATURE-001-A", "FEATURE-001-B", "FEATURE-002-A"]
  feature_count: 3
  requirement_details_part: null | 1 | 2
  parent_features_removed: []
  dedup_gaps: []
  linked_mockups:
    - mockup_name: "Description of mockup function"
      mockup_link: "x-ipe-docs/requirements/EPIC-XXX/mockups/mockup-name.html"
```

Keep original output fields and conditional successor, not renamed schemas. Lists
and counts cover actual scoped affected features/Epics (new/reused), not the
whole board; evidence distinguishes created/updated/reused. Single file uses
null part as legacy contract; numbered part uses its actual integer. Blocked
output reports only produced artifacts and no intended-action success flags.

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Grouping and identity</name><verification>Epic rationale, stable legacy/new IDs, correct folders and no second intake Epic verified.</verification></checkpoint>
  <checkpoint required="true"><name>Feature artifacts</name><verification>Selected populated Feature List and all scoped details cover acceptance/scope and new/changed subgoal-parent-source-evidence mapping with explicit outcome gaps; descriptions &lt;=50 words; requested language/root-relative links intact.</verification></checkpoint>
  <checkpoint required="true"><name>MVP and dependencies</name><verification>Runnable MVP-first, &lt;=20 ACs per feature, 5-7 maximum per Epic, approved deferrals and valid direct DAG including existing impacted edges.</verification></checkpoint>
  <checkpoint required="true"><name>Board registration</name><verification>Real board create/query/update results verified; only new records Planned, existing identities/status/specifications preserved; no manual edits or task duplication.</verification></checkpoint>
  <checkpoint required="conditional"><name>Parts and mockups</name><verification>Index accurate if parts exist, shared mockups checked or N/A, unchanged content/folders preserved.</verification></checkpoint>
  <checkpoint required="conditional"><name>Split dedup</name><verification>Parent coverage complete before authorized retirement/active removal; partial coverage retained with gaps/history; output reflects actual supported operations.</verification></checkpoint>
  <checkpoint required="if-applicable"><name>Application action</name><verification>Actual done state/readback, both keyed outputs, unique correct feature payloads and mandatory prerequisites evidenced; no append replay, duplicate or reset.</verification></checkpoint>
  <checkpoint required="true"><name>Fresh honest return</name><verification>Relevant checks/review revisions current; known failures/partial state reported; full result returned once to lifecycle without successor execution.</verification></checkpoint>
</definition_of_done>
```

MANDATORY: Return to `x-ipe-workflow-task-execution` for its single completion boundary.

## Patterns & Anti-Patterns

See [patterns](.github/skills/x-ipe-task-based-feature-breakdown/references/patterns.md).
Small single-feature registration is complete domain work, not a workflow skip.
Fresh CR review narrows analysis, not artifact or integration truthfulness.

| Anti-pattern | Consequence | Correction |
| --- | --- | --- |
| Regenerate stable features | Lost IDs/state and repeated work | Target authorized CR delta |
| Interface-only MVP or monolithic scope | No runnable value | Vertical MVP then separable enhancements |
| Replay --features or fake done | Duplicates and misleading action | Query, absent delta only, exact artifact/state readback |

## Examples

- [Single/multi-Epic, CR, split and blocked cases](.github/skills/x-ipe-task-based-feature-breakdown/references/examples.md)
- [Grouping, sizing and identity](.github/skills/x-ipe-task-based-feature-breakdown/references/breakdown-guidelines.md)
- [Actual board/workflow integration](.github/skills/x-ipe-task-based-feature-breakdown/references/integration.md)
- [Feature list](.github/skills/x-ipe-task-based-feature-breakdown/templates/features.md)
- [Consolidated details](.github/skills/x-ipe-task-based-feature-breakdown/templates/requirement-details.md)
- [Retained downstream specification scaffold](.github/skills/x-ipe-task-based-feature-breakdown/templates/specification.md)
