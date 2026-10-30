---
name: x-ipe-task-based-feature-refinement
description: Refine one feature into a complete, testable specification using board context, current mockups and delta-first updates. Use when a feature needs detailed requirements. Triggers on requests like "refine feature", "detail specification", "clarify requirements".
---

# Task-Based Skill: Feature Refinement

## Purpose

Create or update one complete specification with user stories, testable acceptance,
functional/nonfunctional requirements, mockup traceability and scope decisions.
Reuse fresh breakdown findings; refine only authorized deltas without rewriting
stable AC IDs, language, unrelated sections or the feature's execution history.

## Important Notes

BLOCKING: Load the [common lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md).
Caller provides readiness; direct entry loads the workflow and calls Orient/Plan
once, returning here without recursively dispatching this child. Lifecycle owns
task registration/status, category/feature status and specification_link updates,
Git and the single completion/routing boundary. Child owns specification artifacts,
questions and the agreed verified application action, not task creation or routing.
Never create/close a task, commit, reset feature status or execute the successor.

CRITICAL: Exactly ONE feature per execution. Preserve legacy FEATURE-{nnn} and
new FEATURE-{nnn}-{X}, matching board epic_id and EPIC/FEATURE or legacy FEATURE
folders. Do not renumber, batch features or migrate existing paths implicitly.

BLOCKING: New refinement requires a real Planned feature. Authorized CR/resume
of an advanced feature needs explicit delta/readiness and its matching existing
specification; preserve status/history, never reset to Planned to pass the gate.
Missing/Retired/wrong-identity or unauthorized advanced features block.

BLOCKING: Adopt the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
for honest new/changed goal coverage in the existing specification. Preserve
legacy stories/ACs; explicit so-that inference is source-labeled, not confirmed.
No goal database, fixed minimum/three-goal cap or board/output/tag additions.

## Input Parameters

```yaml
input:
  task_id: "{existing TASK-XXX}"
  task_based_skill: "x-ipe-task-based-feature-refinement"
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A or resolved workflow"
    action: "feature_refinement"
    extra_context_reference:
      requirement-doc: "path | N/A | auto-detect"
      features-list: "path | N/A | auto-detect"
  category: "feature-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-technical-design"
      condition: "Design the refined feature"
  process_preference:
    interaction_mode: "interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill"
  feature_phase: "Feature Refinement"
  mockup_list: "N/A"  # or [{mockup_name, mockup_link}]
  feature_id: "{FEATURE-XXX or FEATURE-XXX-X}"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing lifecycle identity/readiness; no child allocation" />
  <field name="task_based_skill" source="this canonical entry; category and successor from Output Result" />
  <field name="execution_mode" source="caller context; default free-mode" />
  <field name="workflow.name" source="validated caller context; N/A only free-mode" />
  <field name="workflow.action"><steps>Verify feature_refinement is the mandatory per-feature implement action in ACTION_MAP/template, not a guessed tool key.</steps></field>
  <field name="process_preference.interaction_mode" source="exact resolved common lifecycle enum/source" />
  <field name="feature_phase" source="Feature Refinement; preserve declared output" />
  <field name="feature_id"><steps>Use explicit authorized feature, then caller's single selected first-unstarted breakdown feature or matching task context. A feature_ids list is not permission to iterate; unresolved/ambiguous selection uses actual decision policy. Validate board identity and existing specification links.</steps></field>
  <field name="workflow.extra_context_reference"><steps>For requirement-doc and features-list use explicit selected paths first, then upstream artifact links, then owning requirement part containing the feature (reconcile index/parts; never blindly latest part). Both are required in workflow-mode even if N/A. Free-mode retains validated requirement document/Feature List fallback. A populated owning part may serve both tags. Explicit broken/wrong-feature/escaping/ambiguous links block, not fall back.</steps></field>
  <field name="feature_docs_folder"><steps>Explicit authorized specification artifact, then board specification_link, then matching EPIC/FEATURE folder, then legacy requirements/FEATURE folder. Strip supported anchors for lookup; validate containment, feature content and file kind. Multiple matches block. Preserve existing owning folder. For absent new suffix feature create EPIC-{nnn}/FEATURE-{nnn}-{X}; new legacy ID uses legacy folder. No silent migration.</steps></field>
  <field name="mockup_list"><steps>Explicit validated links first, then breakdown mockup_list/linked_mockups or Idea Mockup output, then existing selected feature mockups, linked idea-summary/idea mockups and matching Epic mockups. Scope-filter every source, including preexisting copies; no unrelated scans. Preserve mockup_name/mockup_link and shared root-relative links. N/A only after bounded discovery confirms no applicable mockup.</steps></field>
  <field name="refinement_context"><steps>Reuse upstream scope, source/parts/index/board/specification/mockup SHA256, dependency findings, confirmed decisions and approved CR identity. Refresh changed/affected facts; missing coverage needs a baseline. Record which AC/story/FR/NFR/edge/UI/scope sections are affected.</steps></field>
  <field name="document_language" source="explicit requested language, else established specification/requirement EN/ZH; stable IDs, paths and tags unchanged" />
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Owner and scope</name><verification>One feature, supplied task/readiness, mode, approved root and new/CR/resume delta known.</verification></checkpoint>
  <checkpoint required="true"><name>Board identity and phase</name><verification>Actual matching Planned record, or explicitly authorized advanced-feature CR/resume with existing matching specification; no status reset.</verification></checkpoint>
  <checkpoint required="true"><name>Artifacts and integration</name><verification>Sources, board specification link/folder, dependencies and scoped mockups resolved; required workflow context/prerequisites and one action owner known.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Step | Domain work | Gate |
| --- | --- | --- |
| 1 | Reuse current feature context | Current revision and affected scope |
| 2 | Resolve targeted gaps, validate ACs and decide scope | Complete testable acceptance and confirmation |
| 3 | Author delta in one complete specification | Full domain, stable IDs/language and links |
| 4 | Verify artifacts/action and return full result | Current evidence or honest blocked result |

Load [specification scaffold](.github/skills/x-ipe-task-based-feature-refinement/references/specification-template.md),
[writing guide](.github/skills/x-ipe-task-based-feature-refinement/references/specification-writing-guide.md)
and [integration](.github/skills/x-ipe-task-based-feature-refinement/references/integration.md)
before domain work. Study/inquiry/reflection/decision combine proportionately;
clear fresh scope needs no repeated interview, forced research or phase ceremony.

## Execution Procedure

```xml
<procedure name="feature-refinement">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Reuse current feature context</name>
    <action>
      1. Load board manager; validate readable inventory before feature_query.py --feature-id ID. Consume data.feature, not guessed task envelope. Reuse full title/version/status/description/dependencies/specification_link context; do not create missing features here.
      2. Compare SHA256 source/specification/mockup/board revisions and actual affected coverage. Reuse fresh business/user/risk findings; read dependency specs/integration points and architecture only where implicated. Research domain/compliance/accessibility only for real missing facts, not every execution.
      2a. Locate parent requirement/source and subgoal stakeholder/outcome/contribution. Reuse stable FR/US/AC or optional doc-local G IDs; for legacy use only explicit story so-that intent labeled inferred with source. Ambiguity blocks the pertinent claim, not historical acceptance or unrelated verified delivery.
      3. Analyze every scoped mockup for layout, styling, components, interactions, flows, responsiveness and error/loading/empty states. Decide current/outdated from content and approved scope; dates alone do not decide precedence. Material spec/mockup conflicts require a documented decision under actual mode policy.
      4. Keep valid shared Epic links; if a local copy is actually needed, copy only scope-relevant missing authorized files into selected feature mockups, preserving extension and foreign bytes. Existing copies still need scope/freshness analysis. Outdated mockups are directional only and never generate comparison ACs.
    </action>
    <output>Revision-bound context, dependencies and analyzed current/outdated mockup map or confirmed N/A</output>
  </step_1>
  <step_2>
    <name>Resolve gaps and validate acceptance</name>
    <action>
      1. Review affected personas/stories, functional and nonfunctional coverage, dependencies, business rules, error/loading/empty/boundary/security/accessibility cases. Ask only unresolved material questions, up to 3-5 per batch, no padding or re-interview of confirmed unchanged facts. Human asks the human within skill and waits; full DAO and hybrid use bounded common message_context/instruction_units/execution_plan guidance. Record answers, assumptions and unresolved blockers.
      2. Every new/changed AC has a stable unique ID, specific observable achievable story-linked result and Given/When/Then syntax, with AND for extra clauses. Known justified measures or qualitative scenarios are valid. Preserve established EN/ZH prose and unaffected legacy ACs; retain GWT tokens for authored leaf ACs. Classify primary Test Type as exactly UI, API, Unit or Integration; Manual is not allowed. Never convert a vague requirement into an invented threshold.
      2a. Map each new/changed goal/subgoal to source, parent requirement, stories, ACs and planned/actual validation evidence. Explain indirect enabling contribution, all-required decomposition or selected bounded alternatives, constraints/non-goals and outcome gaps. Coherent scope bounds count; no arbitrary metrics, fixed minimum or three-goal cap. Means remain adaptable within contracts; material scope/acceptance changes use authorized CR/human intent.
      3. Map each current in-scope mockup element/interaction to story, UI/UX requirement and AC, including layout/styling/interactive comparison ACs with UI type. Uncovered current in-scope elements block. Out-of-feature elements are excluded explicitly, not copied into scope. Outdated links remain directional and never become acceptance authority.
      4. Decide in/out scope, deferred work and edge behaviors. Preserve breakdown coverage and stable AC IDs; append new IDs after highest reserved identifier, never reuse deleted IDs. Changed/retired ACs retain CR rationale, mapping/history and downstream acceptance invalidation; no silent deletion or wholesale rewording.
      5. Human and hybrid must confirm specification completeness and completion/route before Technical Design. Reuse a recorded confirmation only for exact unchanged scope/specification revisions; material edits invalidate it. Full DAO uses bounded guidance, verified DoD and only authorized routing, not invented human approval. Explicit domain human approval binds in every mode. If scope grows beyond one coherent feature, return recommendation to lifecycle for authorized breakdown, not batch/split execution here.
    </action>
    <output>Resolved targeted decisions, complete GWT/primary-type acceptance and revision-bound scope confirmation</output>
  </step_2>
  <step_3>
    <name>Author one complete specification delta</name>
    <action>
      1. Create/update specification.md in the resolved owning feature folder; never specification-v2.md or a second competing file. New version follows actual board v1.0; authorized minor/major CR updates only this feature's approved version. Keep old Version History and Change Request links/records; no gratuitous version bump on unchanged resume.
      2. Fill every scaffold domain: Version History, Linked Mockups, Overview, User Stories, Acceptance Criteria, Functional Requirements, Non-Functional Requirements, UI/UX Requirements, Dependencies, Business Rules, Edge Cases and Constraints, Out of Scope, Technical Considerations, Open Questions and Acceptance Traceability. N/A requires explicit rationale; material open questions block completion. Describe WHAT, not implementation HOW.
      3. AC groups use table columns AC ID, Criterion (Given/When/Then), Test Type. Map source FR/AC and stories to specification ACs, mockup elements and planned primary validation; do not invent passing tests. Record approved deferrals with reasons. Validate every changed AC plus affected cross-references without regenerating unchanged acceptance.
      3a. Fill Goal / Subgoal Coverage and separate engineering delivery from stakeholder outcome state in existing Context and Verification Evidence. not measured is an honest gap, verified engineering delivery needs actual current checks, observed stakeholder outcome needs an actual sourced observation. Parent goal delta invalidates affected evidence; preserve unaffected IDs and history, never fake confirmation or observation.
      4. Linked Mockups retain type/path/description/status current or outdated/Linked Date MM-DD-YYYY. Record actual date when first linked or changed, not every resume. Current mockups drive stories/UI/ACs; outdated are explicitly directional. Preserve project-root-relative Markdown links; no ../, ./ or absolute filesystem paths. Validate local kind/containment/content and actual URL reachability where required.
      5. Preserve stable US/FR/AC IDs, existing language and unaffected section bytes. Delta-only CR adds/changes only approved affected content, version/CR records, traceability and evidence. Recheck referenced older requirement parts, dependent acceptance/design/test evidence and board link handoff; do not falsely relabel old evidence current.
    </action>
    <output>One complete specification with stable acceptance, CR/version records and actual artifact links</output>
  </step_3>
  <step_4>
    <name>Verify integration and return</name>
    <action>
      1. Verify full DoD, actual artifact identity/content, all GWT/type/traceability/scope/mockup gates and current SHA256 revisions. Meaningful workflow/public-contract/risky changes require independent review; unavailable review blocks the relevant claim, not drafting. Missing confirmation returns blocked, never Technical Design execution.
      2. Free-mode has no application mutation and workflow_action_updated false. Workflow-mode requires unique matching feature entry, feature_breakdown actually done with valid artifacts, both resolved context tags and mandatory gates. Do not mark prerequisites skipped/done to unlock refinement.
      3. With one agreed action owner, use installed workflow_update_action.py --workflow NAME --action feature_refinement --status done --feature-id ID --deliverables keyed JSON --format json. Supply BOTH specification = actual populated matching file and feature-docs-folder = scalar existing owning directory. Do not pass --features or create another workflow feature. Preserve context; populate required missing selected tags through supported --context JSON only when authorized.
      4. Read workflow_get_state.py; matching features[].implement.actions.feature_refinement must be done with exact both artifacts and selected context, no duplicate identity, unrelated entries/status/history unchanged. Writer success alone is insufficient. Completed unchanged resume verifies prior actual write evidence without replay; changed specification invalidates downstream design/implementation/acceptance evidence, never silently resets or claims it current.
      5. Return exact full output and actual links once. Lifecycle owns category/feature board handoff (verified specification_link and authorized Refined transition for new refinement; no downgrade of advanced CR state), task closure/Git and one conditional Technical Design suggestion boundary. If required handoff or supported invalidation cannot be verified, return blocked with actual partial artifacts, not false completion.
    </action>
    <output>Verified full feature result, board-link handoff and action evidence or honest blocked output</output>
  </step_4>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-technical-design"
      condition: "Design the refined feature"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"
  workflow_action_updated: true | false
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/specification.md"
  feature_id: "FEATURE-XXX"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Feature Refinement"
  mockup_list: "{updated with copied paths if mockups were copied}"
  linked_mockups:
    - mockup_name: "Description of mockup function"
      mockup_link: "x-ipe-docs/requirements/FEATURE-XXX/mockups/mockup-name.html"
```

Keep exact original keys/order/category/conditional successor; illustrative legacy
paths above become the actual resolved EPIC/FEATURE or legacy paths, and shared
mockup links remain shared when no copy is needed. N/A means absent optional
mockups, not fabricated files. workflow_action_updated is true only with actual
verified write/prior write evidence; blocked output retains real partial links.

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Identity and one specification</name><verification>Matching feature and owning legacy/new folder, real populated single specification and resolved board link handoff.</verification></checkpoint>
  <checkpoint required="true"><name>Full domain</name><verification>All scaffold sections filled, user/functional/nonfunctional/business/edge/dependency/out-of-scope coverage and justified N/A; no unresolved material questions.</verification></checkpoint>
  <checkpoint required="true"><name>Acceptance and traceability</name><verification>Unique stable story/FR/AC IDs, new/changed observable GWT tables with exactly UI/API/Unit/Integration types, source/parent/goal/story/mockup/validation mappings, explicit outcome gaps and approved deferrals; legacy unchanged content preserved.</verification></checkpoint>
  <checkpoint required="true"><name>Delta preservation</name><verification>Existing language, unaffected content/IDs, version/CR history and advanced board state preserved; affected downstream evidence invalidated, not falsely current.</verification></checkpoint>
  <checkpoint required="if-applicable"><name>Mockups</name><verification>Scoped analysis and valid current/outdated links/dates; all current in-scope elements covered by stories/UI/ACs, UI comparison types; outdated directional only; no foreign overwrite.</verification></checkpoint>
  <checkpoint required="true"><name>Confirmation</name><verification>Human/hybrid completeness and completion/route confirmation or exact-revision prior confirmation; full DAO bounded guidance/DoD and only authorized routing; explicit human approval binds in every mode without invented authority.</verification></checkpoint>
  <checkpoint required="if-applicable"><name>Application action</name><verification>Actual per-feature done/readback, specification and scalar feature-docs-folder, both selected contexts/prerequisites verified; no replay/duplicate/reset.</verification></checkpoint>
  <checkpoint required="true"><name>Fresh honest return</name><verification>Checks/review and hashes current; output fields/links and category handoff retained; one return to lifecycle, no child task/Git/next execution.</verification></checkpoint>
</definition_of_done>
```

MANDATORY: Return to `x-ipe-workflow-task-execution` for its single completion boundary.

## Patterns & Anti-Patterns

| Pattern | When | Then |
| --- | --- | --- |
| Fresh clear feature | Breakdown decisions current | Reuse findings, full domain/AC validation, no ceremonial questions |
| Approved CR/resume | Existing spec and bounded delta | Stable IDs/language/history, affected-only updates and evidence invalidation |
| Current/outdated mockups | Applicable scoped references | Current traceable stories/UI/ACs; outdated directional, dates not precedence |

| Anti-pattern | Consequence | Correction |
| --- | --- | --- |
| Rewrite all ACs or use latest part blindly | Lost identity/coverage | Preserve stable IDs and owning artifact links |
| Auto-copy all Epic mockups/newer always wins | Scope bloat or false authority | Scope/content review and recorded conflict decision |
| Writer success/child routing replaces lifecycle | False done or duplicate actions | Exact state/artifact readback and one owner |

## Examples

- [New, delta, mockup and blocked scenarios](.github/skills/x-ipe-task-based-feature-refinement/references/examples.md)
- [Full specification scaffold](.github/skills/x-ipe-task-based-feature-refinement/references/specification-template.md)
- [Specification quality and delta guide](.github/skills/x-ipe-task-based-feature-refinement/references/specification-writing-guide.md)
- [Artifact/board/workflow integration](.github/skills/x-ipe-task-based-feature-refinement/references/integration.md)
