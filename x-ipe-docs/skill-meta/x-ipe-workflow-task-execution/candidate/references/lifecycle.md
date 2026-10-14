# Common lifecycle contract — child entry and caller boundary

MANDATORY: The workflow and every adopting child read this reference before
domain execution. Existing children are not silently migrated by publication.
Adoption adds this link to child Important Notes and replaces duplicate lifecycle
blocks in that child's own validated candidate; until then use an explicit
bounded ownership adapter or block conflicting invocation.

## Optional goal-contract adoption

The [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
defines document-local outcome/subgoal and evidence semantics. It is mandatory
only at an explicitly adopting child's domain gate; loading this lifecycle does
not migrate every child. Reuse existing artifacts/identifiers and domain GWT ACs,
not a goal database, persisted field, output/action tag or extra approval ritual.
Report delivery evidence separately from not measured or observed stakeholder
outcome; authorized CR/human intent bounds replanning and evidence invalidation.

## Direct entry and one owner

Direct task skill invocation first loads x-ipe-workflow-task-execution and calls
Orient/Plan ensure/resume with the supplied ID, original task_type/description/
role and authorized scope. The lifecycle entry returns readiness context to the
already-entered child; it MUST NOT dispatch that same child recursively. A normal
workflow invocation passes readiness context and invokes domain once. Do not add
new persisted board fields for an invocation marker; maintain caller context.

The child owns domain artifacts, tests, domain DoR/DoD and bounded questions.
The lifecycle owner owns registration, lifecycle status, Git scope and the single
completion/next-task boundary. A child returns suggested next actions; it never
starts the successor. If a delegated domain skill is needed for the SAME task,
pass the same ID/readiness and return its result; no second lifecycle registration.
Separately approved successor work receives its own task only after the boundary.

## Exact child output contract (no renamed schemas)

Task-based children retain:

```yaml
task_completion_output:
  category: "child-declared category; retain case including legacy Standalone"
  status: completed | blocked | deferred | in_progress | cancelled | skipped
  next_task_based_skill: null  # retain child's string/list conditional form if declared
   # require_human_review is optional: preserve only if declared by child
  process_preference:
    interaction_mode: "resolved exact enum"
  task_output_links: []       # existing nullable links contract accepted as null
  # All child-specific output fields preserved, e.g. feature_id, workflow_action,
  # publication_state, candidate_hash, unresolved_issues; do not nest/rename them.
```

Some children declare a narrower status set; retain it, do not force new values.
Do not reject a child solely for omitting require_human_review; many live task
outputs omit it. An explicit domain approval gate remains binding in every mode.
Tools/assistants retain operation_output and never fabricate category/task fields.
Workflow aggregate remains `output` with the existing task/context/dynamic fields.
Generic workflow template `workflow_output` is not a migration instruction.

Board adaptation uses task_id, task_type, description, role, status, output_links
(list), next_task (string). No category, assignee, title, dynamic_attributes,
require_human_review or invocation marker is persisted in task CRUD. Preserve
board-generated created_at/last_updated. next_task null adapts to empty string;
conditional successor selection uses current context, retaining original result.

Board statuses: pending, in_progress, completed, blocked, cancelled, skipped,
deferred. pending → in_progress; in_progress → completed/blocked/deferred/
cancelled; blocked/deferred → in_progress only after resolving cause/permission.
completed/cancelled/skipped are terminal: ensure returns unchanged; do not reopen,
execute or replay routing automatically. A skipped task is not evidence of domain
completion. Partial slice of a larger task retains in_progress, with scope recorded
in existing output evidence, not false completed or a new persisted state.

## Interaction modes

| interaction_mode | Actual within-skill decision | Completion / next-task boundary |
| --- | --- | --- |
| interact-with-human | Ask human and wait | Human review and route confirmation |
| dao-represent-human-to-interact | DAO bounded answer/guidance | DAO selects authorized route; no invented scope |
| dao-represent-human-to-interact-for-questions-in-skill | DAO bounded answer/guidance | Human review and route confirmation |

Hybrid means DAO within skill, human completion/route confirmation. Preserve
the current externally-visible contract in FEATURE-044-E specification AC-044-E.4,
CR-002 and the existing UI's DAO Inner-Skill Only label/transport tests. Explicit
domain approval/release gates remain human in every mode. Earlier lifecycle
review claimed a user-requested inversion; that inversion was not authorized by
the current user. Earlier stop_for_question prose and some installed children
also conflict with this current contract. Record those baselines; do not silently
invert UI, enum transport or source requirements to make documentation agree.
Conflicting child policy requires an explicit bounded compatibility adapter
under this contract or blocks that invocation. This candidate correction is not
an already-published repair of those children.

Clear inputs require neither question nor ceremonial representative call. Re-read
policy source at real decisions and boundaries. Explicit task --interaction@MODE
or current user override takes precedence over workflow global.process_preference;
otherwise legacy --proceed@auto = full DAO, --proceed@stop-for-question = hybrid,
manual = human, default = interact-with-human. Record source; reject unknown mode.
Representative execution_strategy cannot silently overwrite human-selected mode.

Actual representative call:

```yaml
input:
  message_context:
    source: ai
    calling_skill: "current skill"
    task_id: "current TASK-NNN"
    feature_id: "feature or N/A"
    workflow_name: "name or N/A"
    downstream_context: "full completed child output + bounded scope and question"
    messages:
      - content: "actual decision, options, current evidence and constraints"
        preferred_dispositions: [answer, clarification, instruction, approval]
  human_shadow: false
```

Consume operation_output.success, result.instruction_units (1–3), execution_plan,
confidence and fallback_required; failures/fallback follow actual policy and
do not grant authority. `approval` is guidance, NOT human approval. Never use
obsolete type:routing or completed_skill_output as substitute for message_context.
Full DAO does not authorize promotion, release, scope expansion, commit, push,
destructive work, playground creation, or external publication absent user intent.

## Source artifact resolution

1. Preserve child field names and workflow.extra_context_reference tag names.
   For each required source: explicit selected path first; then declared child
   artifact link / feature board link; then legacy child-specific auto-detect.
2. Explicit broken, wrong-feature, escaping or ambiguous link blocks; never mask
   it with fallback. Absent, N/A or auto-detect may use documented legacy search.
   In workflow-mode template action_context.required still requires resolution.
3. Validate existence, file/directory kind, canonical containment in approved
   project/source roots, feature/workflow identity and required content; reject
   traversal and symlink escape. Strip supported Markdown anchors for file lookup.
   URL artifacts need an actual reachability/content check where required, not a
   filesystem existence assertion. Never fetch secrets from unrelated sources.
4. Legacy feature lookup may use declared feature specification_link and matching
   EPIC/FEATURE folders, then legacy requirements/FEATURE folder. Multiple matches
   block rather than choose the newest. Free-mode remains supported without an
   app workflow, but missing required artifacts still blocks domain readiness.
5. Record resolved links and content hashes; stale revisions invalidate downstream
   evidence. Do not use filenames or modification time alone as revision proof.

## Workflow actions and completion

Authoritative skill/action association: [workflowStage.ACTION_MAP](src/x_ipe/static/js/features/workflow-stage.js).
Action stages/types, action_context and extract-tag keys:
[workflow-template.json](x-ipe-docs/config/workflow-template.json).
Enabled tools/consultation flags: [tools.json](x-ipe-docs/config/tools.json).
Do not mechanically replace hyphens with underscores to invent action names.
`x-ipe-task-based-code-implementation` maps to app action `implementation`;
tool routing uses `stages.implement.code_implementation`, not an app action.

Pass workflow.name/action and existing workflow_action output unchanged. If output
and authoritative mapping disagree, block; if action is absent, resolve uniquely
from the authoritative source. A skill with no app mapping remains free-mode or
requires an explicit supported association; do not invent an action.

Read workflow state through the installed app interactor, not a guessed filename.
Shared actions live at shared.stage.actions.action; per-feature actions live at
features[].stage.actions.action matched by feature_id. Workflow action statuses
are pending, in_progress, done, skipped, failed — distinct from task statuses.
Only `done` plus verified required artifacts supports a completed action claim.
Writer may allow missing tags/skipped; lifecycle must not treat that as readiness.

Use workflow_update_action.py --workflow --action --status done, --feature-id when
per_feature, --deliverables JSON, --format json. Deliverables are keyed dicts:
keys are current extract tags without $output:/$output-folder: prefixes; all
declared required outputs must resolve. File tags allow nonempty strings or
arrays of strings where supported; folder tags are scalar directory strings.
Empty/missing/wrong-feature outputs block. Verify exit success and re-read state.
Never update a mandatory prerequisite to skipped/done to unlock the next stage.

Current repaired contracts: feature-closing returns its closing report as a task
artifact with no extract tags; acceptance uses impl-files for implementation
outputs and both-parts design for technical_design_link. Earlier mismatch prose
was a historical baseline, not current ground truth. Change-request uses
closing-report input while a legacy test expects eval-report; retain that known
conflict, never invent tags or treat writer success as domain proof.
Code-implementation task_output_links declares src/ and tests/ directories, while
the action requires impl-files file paths and an impl-folder scalar directory;
the owner must collect actual changed files separately, not blindly copy links.

## Evidence and Git safety

Bind each claim to relevant source, implementation, test and config SHA256 hashes,
commands, exits, result and review scope. Verify hashes again before record/routing;
any changed tested input invalidates affected receipts/review and requires rerun.
Record unavailable checks as unavailable; content assertions do not prove agent
decision behavior. Independent review required for meaningful safety/workflow/
executable/public-contract changes; candidate_ready is not publication/release.

Capture branch and dirty/staged baseline before work. Respect .x-ipe.yaml Git
strategy and real identity for dev-session-based; wrong branch plus dirty work
blocks branch-sensitive mutation, never auto-switch/stash/reset/pull. Clean branch
preparation also needs authority. No implicit network fetch/push/PR.
Default no commit. Explicit user-approved commit stages exact owned approved
paths only after diff review and freshness checks. No git add -A, git add . or
files=null. Preexisting staged changes block committing; do not unstage foreign
work. DAO guidance cannot supply missing user approval. No commit is a valid
completed outcome when domain criteria do not require a separately authorized
release; domain-required release without authority is blocked, not silently waived.

## Proportional small path

For clear bounded low-risk work, name a combined deliverable with explicit scope,
acceptance, design/impact and verification sections. Reuse source links instead
of speculative duplicate documents. Preserve domain-specific TDD/review gates.
In app workflow-mode keep all mandatory actions/gates and actual required tags;
combined artifact integration must be tested before using it to satisfy multiple
actions. No app workflow skips introduced by this contract. This is an adoption
contract, not a declaration that every child or UI integration already supports it.
