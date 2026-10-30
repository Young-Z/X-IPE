---
name: x-ipe-task-based-requirement-gathering
description: Gather requirements from user requests and create requirement summary. Use when starting a new feature or receiving a new user request. Triggers on requests like "new feature", "add feature", "I want to build", "create requirement".
---

# Task-Based Skill: Requirement Gathering

## Purpose

Turn user intent into durable requirement details: what, who, why, acceptance,
constraints, scope, conflict decisions and impacted features. Carry a bounded
new/small/CR delta forward rather than regenerate fresh upstream analysis.
Produce the Epic context and real artifacts needed by Feature Breakdown.

## Important Notes

Load the [single-loop delivery policy](.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md)
once in the current context. Execute this skill in the same agent loop; another
skill is expertise, not a new agent. Use proportional checks and reuse current
evidence; independent review is conditional on concrete risk, not the skill name.

BLOCKING: Use the [shared lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md)
once: caller supplies readiness; direct entry loads the workflow and calls its
Orient/Plan entry, returning here without recursively dispatching this skill.
Lifecycle owns task registration/status, Git and the completion/next-task boundary.
This child owns domain documents, questions and verified application action work;
return the full result, never create/close a task or execute a successor here.

BLOCKING: For new/changed scope apply the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
in the existing requirement artifact. Legacy inference is source-labeled; missing
intent blocks the pertinent goal claim, not a rewrite of unchanged history.

CRITICAL: Every newly gathered requirement creates one `EPIC-{nnn}` grouping
context, including a CR intake; resume reuses its existing Epic, not a second one.
Feature Breakdown assigns `FEATURE-{nnn}-{X}` with the parent's number. Never put
an EPIC ID in a Feature ID column or feature entry. Preserve legacy FEATURE-{nnn}
IDs and both legacy FEATURE folders and EPIC/FEATURE folders when reading impacts.

BLOCKING: Delta-first does not skip conflict review, required app actions or
deliverables. A combined artifact must satisfy each real action contract; no
automatic prerequisite completion, skipped gate or fake done claim.

## Input Parameters

```yaml
input:
  task_id: "{existing TASK-XXX}"
  task_based_skill: "x-ipe-task-based-requirement-gathering"
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A or resolved workflow"
    action: "requirement_gathering"
    extra_context_reference:
      refined-idea: "path | N/A | auto-detect"
      mockup-html: "path | N/A | auto-detect"
  category: "requirement-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-breakdown"
      condition: "Break requirements into features"
  process_preference:
    interaction_mode: "interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill"
  epic_id: "EPIC-{nnn} or auto-assigned"
  mockup_list:  # or N/A
    - mockup_name: "function represented"
      mockup_link: "validated local path or URL"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing lifecycle task and readiness; do not allocate another" />
  <field name="task_based_skill" source="this canonical entry; category/next suggestion from Output Result" />
  <field name="execution_mode" source="resolved caller context; default free-mode" />
  <field name="workflow.name" source="resolved caller identity; N/A only in free-mode" />
  <field name="workflow.action">
    <steps>Verify requirement_gathering against ACTION_MAP and current workflow template; missing or mismatched workflow identity/action blocks workflow claims.</steps>
  </field>
  <field name="process_preference.interaction_mode" source="resolved common lifecycle policy; retain its exact enum and source" />
  <field name="workflow.extra_context_reference">
    <steps>
      1. Preserve refined-idea/mockup-html tags; validate explicit links first, then declared upstream output, then unambiguous legacy auto-detection.
      2. Read actual contents and hashes; explicit missing, escaping, wrong-context or ambiguous links block rather than falling back.
      3. In workflow-mode refined-idea is required by action_context, even if N/A was supplied; mockup-html is optional. In free-mode a user request suffices and unavailable optional context is N/A.
    </steps>
  </field>
  <field name="epic_id">
    <steps>
      1. Resume a validated Epic already associated with this task; reject a supplied unrelated or colliding ID.
      2. For new intake scan x-ipe-docs/requirements/ EPIC-{nnn} folders and document headers/reservations; allocate highest number + 1, initially EPIC-001.
      3. Recheck before creation; a concurrent collision requires reallocation before writing, never overwrite another Epic.
    </steps>
  </field>
  <field name="mockup_list">
    <steps>Reuse previous Idea Mockup output or explicit links, then resolved mockup-html; validate names, source identity and content. Ask only if a missing mockup affects scope; otherwise N/A, not a ceremonial question.</steps>
  </field>
  <field name="document_language">
    <steps>Use explicit requested language, then established requirement document/project language. Preserve EN/ZH context; clarify only a consequential mixed-language ambiguity. IDs, paths, tags and schema keys remain unchanged.</steps>
  </field>
  <field name="requirement_context">
    <steps>Resolve active requirement-details file, all parts/index, affected legacy/new features and existing revision-bound review per context-review reference. Record selected inputs, hashes and reuse/invalidation reasons.</steps>
  </field>
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Intent and owner</name><verification>User request and approved root/write scope known; lifecycle readiness and supplied task match.</verification></checkpoint>
  <checkpoint required="true"><name>Sources resolved</name><verification>Required idea context validated, optional mockups resolved or N/A, existing requirement inventory and language identified.</verification></checkpoint>
  <checkpoint required="true"><name>Delta and decisions</name><verification>New/small/CR path, risk and unresolved decision list are bounded; actual questions can reach the policy-selected responder.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Step | Domain work | Gate |
| --- | --- | --- |
| 1 | Reuse fresh intent/context; classify delta and risk | What/who/why and evidence coverage known |
| 2 | Resolve questions and review conflicts/feasibility | Every material conflict and scope choice decided |
| 3 | Apply bounded impacts and author requirement details | Epic, mockups, active part and index consistent |
| 4 | Verify documents and real app action; return result | DoD evidenced or honest blocked output |

Study, inquiry, reflection and discernment combine where justified; no required
five-phase ceremony, full research round or repeated clear-input interview.
Load [context review](.github/skills/x-ipe-task-based-requirement-gathering/references/context-review.md)
for reuse, risk, conflict and workflow verification rules before domain work.

## Execution Procedure

```xml
<procedure name="requirement-gathering">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Understand the delta</name>
    <action>
      1. Extract what/who/why, high-level requirements, acceptance, constraints and non-goals from resolved inputs. Link fresh upstream analysis instead of repeating it.
      1a. Frame stakeholder desired observable outcome and source/parent using existing FR/US/AC IDs or optional stable doc-local G anchors. Distinguish deliverable from outcome, map requirement IDs to goal/source, success evidence and constraints; a qualitative scenario is valid where no justified metric exists.
      2. Classify small compatible, standard new, or CR intake using affected boundaries, not line count. Reuse an authorized CR delta without launching a separate CR pipeline.
      3. Identify security, public API, data/destructive change, cross-feature and uncertain-domain risks; expand affected context and review only where justified.
      4. Research standards, terminology, competitor/compliance facts only for a material knowledge gap and allowed tools. Read stages.requirement.gathering config; metadata-only configuration is not implicit web-tool enablement.
    </action>
    <output>Intent/delta, risk, source revisions and context reuse decision</output>
  </step_1>
  <step_2>
    <name>Decide questions, conflicts and scope</name>
    <action>
      1. Ask only unresolved material scope, user, edge-case, priority or constraint questions, at most 3-5 per batch; await responses and record answers. Clear inputs need no question/DAO call.
      2. Use the common lifecycle decision policy: human asks the human within skill and waits; full DAO and hybrid receive bounded representative guidance through message_context/instruction_units/execution_plan. Unresolved material ambiguity blocks; guidance cannot supply missing human authority.
      3. Reconcile all requirement-details parts/index with current inventory. Reuse complete fresh conflict coverage, inspect changed/affected parts and dependencies, or establish full baseline if coverage is absent/stale/incomplete.
      4. Compare functional, scope and dependency overlap. Record feature IDs, FRs/ACs, paths, decision and rationale for EACH conflict: CR on existing or independent new work, using Single Responsibility, Cohesion, Independence and Minimal Coupling.
      5. Document feasibility, integration/resource/timeline risks, mitigation and design assumptions without dropping requirements. Resolve consequential uncertainty; nonblocking design assumptions remain explicitly identified.
      6. Record in/out scope and confirmed decisions once. Route an actual unresolved scope confirmation through policy; do not re-interview already approved fresh input.
    </action>
    <output>Complete conflict coverage, decisions, scope, risks and bounded assumptions</output>
  </step_2>
  <step_3>
    <name>Apply impacts and document</name>
    <action>
      1. For each CR decision append an identifiable CR impact note with date, task/ref, change, affected feature/FRs/ACs, required specification follow-up and new Epic/document link; avoid duplicate markers on resume.
      2. Resolve only agreed conflicting sections: minor/additive conflict updates inline; major contradiction/redesign retains old text under [RETIRED by EPIC-{nnn}] with reason/date/replacement link. Preserve unrelated FRs/ACs.
      3. Independent new work gets Related Features dependency notes, not a false CR marker. With no conflicts, record zero and no impact edits.
      4. Check active file BEFORE appending new content; if already >500 lines use file-splitting reference. Preserve index and repair links affected by first rename; do not split a 473-line file merely from estimated growth.
      5. Create/reuse EPIC-{nnn}/ and mockups/; copy validated local mockups without destructive overwrite. External URLs require applicable content/reachability checks and remain linked when not locally copied.
      6. Fill canonical requirement-details template and append to active part with ## EPIC-{nnn}: {Title}. Include what/who/why, acceptance, scope, constraints, clarifications, risk, conflict/impact evidence and mockups.
      6a. Include the outcome frame and requirement mapping in this same artifact; state all-required versus selected/bounded alternatives, planned evidence and not measured outcome gaps. CR records parent goal delta and invalidates affected evidence without changing unrelated identities or claiming fresh confirmation.
      7. For small/new/CR paths a concise Epic section may combine these fields; retain separately addressable app artifacts. Keep project-root-relative Markdown links, never ../, ./ or absolute filesystem paths.
    </action>
    <output>Real requirement document, Epic/mockups folders, index and bounded impact edits</output>
  </step_3>
  <step_4>
    <name>Verify and return</name>
    <action>
      1. Verify DoD, link targets, language, IDs, conflict decisions, split integrity and current source/document/config revisions. Rerun affected checks if changed; retain known failures.
      1a. Require honest goal coverage for every new/changed requirement: source/stakeholder/outcome, contribution, success scenario, constraints/non-goals and planned validation. Preserve legacy story so-that inference labels; do not assert observed outcome from artifact delivery or planned tests.
      2. Use self-checks and targeted tests by default; independent review is required only for an explicit request or concrete high-risk uncertainty under the shared single-loop policy. Reuse suitable current review; missing required review blocks the affected claim, not drafting.
      3. In workflow-mode perform the completion action exactly once by this child, after domain gates pass; if lifecycle already performed the agreed write, verify it instead. Load app interactor and use installed workflow_update_action.py with --workflow, --action requirement_gathering, --status done, --deliverables keyed JSON and --format json.
      4. Supply BOTH requirement-doc = actual active populated file and requirements-folder = scalar x-ipe-docs/requirements directory. Verify exit 0 and workflow_get_state.py readback at shared.requirement.actions.requirement_gathering: status done plus exact verified deliverables. Writer success alone is insufficient.
      5. Missing action/state, missing or invalid artifacts, failed write/readback or unsatisfied mandatory prerequisite blocks completion. Never mark prerequisites done/skipped to unlock; free-mode does not mutate app state and returns workflow_action_updated false.
      6. Return full task_completion_output and evidence to lifecycle for its single completion/route boundary. Human and hybrid require human requirements review and completion/route confirmation; full DAO selects only authorized successors. Explicit domain human approval remains binding in every mode.
    </action>
    <output>Verified result or blocked result with actual partial links and false unverified flags</output>
  </step_4>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: "requirement-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-breakdown"
      condition: "Break requirements into features"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"
  workflow_action_updated: true | false  # true only for verified actual write/readback
  task_output_links:
    - "x-ipe-docs/requirements/requirement-details.md"  # or actual active part
  mockup_list: "{resolved input or N/A}"
  requirement_summary_updated: true | false
  requirement_details_part: 1  # single file counts as part 1
  conflict_review_completed: true | false
  conflicts_found: 0
  impacted_features: []  # existing FEATURE IDs, never EPIC IDs
  conflicting_docs_updated: []
  conflicting_docs_retired: []
  epic_id: "EPIC-{nnn}"
```

Preserve every field, the conditional successor list and exact interaction enum.
Blocked output lists only artifacts actually produced; do not set success flags
from intended actions. Attach revision/decision evidence in the requirement section
or caller evidence, not a renamed output schema or new persisted board field.

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Requirement artifacts</name><verification>Populated active requirement-details, Epic/mockups folders, all domain template fields and root-relative links verified; new/changed goal/source/evidence/constraint coverage honest, outcome gaps explicit; requested language and ID conventions retained.</verification></checkpoint>
  <checkpoint required="true"><name>Decisions complete</name><verification>No material unresolved questions/conflicts; in/out scope, feasibility risks and bounded design assumptions recorded under actual mode policy.</verification></checkpoint>
  <checkpoint required="true"><name>Conflict coverage</name><verification>All current parts represented by fresh full baseline or revision-bound reuse plus affected delta review; every conflict has a recorded decision.</verification></checkpoint>
  <checkpoint required="conditional"><name>Impacts resolved</name><verification>CR markers and agreed inline/retirement edits exist for all CR decisions, dependency links for independent work; unrelated FRs/ACs preserved.</verification></checkpoint>
  <checkpoint required="conditional"><name>Split integrity</name><verification>If split, original rename/new active part/index and inbound links verified per file-splitting reference.</verification></checkpoint>
  <checkpoint required="if-applicable"><name>Application action</name><verification>Workflow-mode has real successful write and state readback done with both validated keyed outputs and mandatory gates satisfied; free-mode has no app write.</verification></checkpoint>
  <checkpoint required="true"><name>Fresh honest result</name><verification>Current revision checks/review evidenced, partial/blocked claims honest; full domain output returned once to lifecycle.</verification></checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

| Pattern | When | Then |
| --- | --- | --- |
| Fresh explicit idea | Scope/decisions already clear | Reuse and document delta; no repeated interview |
| Bounded CR | Existing responsibility changes | Target affected parts/FRs and carry impact forward |
| New broad/risky requirement | Coverage or domain facts insufficient | Expand only justified context; retain independent review |

| Anti-pattern | Consequence | Correction |
| --- | --- | --- |
| Latest-part-only or timestamp reuse | Missed/stale conflicts | Reconcile complete inventory and revision coverage |
| Mandatory full reanalysis | Duplicate effort | Reuse fresh evidence, inspect changed/affected scope |
| Invented feature/approval/action completion | Broken contracts | Retain IDs, mode authority and actual action evidence |

---

## Examples

- [Small/new/CR and blocked cases](.github/skills/x-ipe-task-based-requirement-gathering/references/examples.md)
- [Revision-bound context and app verification](.github/skills/x-ipe-task-based-requirement-gathering/references/context-review.md)
- [File splitting](.github/skills/x-ipe-task-based-requirement-gathering/references/file-splitting.md)
- [Canonical domain template](.github/skills/x-ipe-task-based-requirement-gathering/references/requirement-details-template.md)
- [Compatible template entry](.github/skills/x-ipe-task-based-requirement-gathering/templates/requirement-details.md)
