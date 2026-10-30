# Closing — consumer compatibility, evidence and authority

## Real action and empty outputs

ACTION_MAP in workflow-stage.js maps this skill to feature_closing in per-feature
validation. Current workflow-template.json requires specification context; the
refactor-report input is optional. Its deliverables list is **[]**. Runtime
WorkflowManagerService.validate_action_deliverables and installed
workflow_update_action.py reject unexpected dictionary keys: closing-report is
not an extract tag. Both accept the empty dictionary. Owner uses deliverables {}
for this action, keeping the actual closing report as a **task artifact** and
task_output_links entry. This is a bounded mapping using existing schemas, not
a production config/runtime migration or an assertion that the app extracts it.

Installed writer invocation uses --workflow exact-name --action feature_closing
--feature-id exact-feature --status done --deliverables '{}' --format json.
Check domain readiness first; matching workflow_get_state.py readback must show
features[].validation.actions.feature_closing status done, deliverables {},
correct feature and actual specification context. One owner performs/verifies
one write; already current verified done is read-only resume, not replay.
No new workflow_action output key: owner records actual evidence in its existing
dynamic context/report. Free-mode no workflow mutation.

Writer success alone is insufficient: verify current complete acceptance,
specification/implementation identity and all actual preceding mandatory gates.
Default code_refactor is optional. No need means direct closing, with no refactor
report, compulsory assessment, invented churn or agent-authored skip/done record.
Optional actions are initialized as skipped by the service; do not treat that as
refactoring evidence. A project may explicitly customize mandatory actions;
honor its actual template. Acceptance and closing remain required. Empty closing
outputs are valid, not a blocker. An incomplete required implementation still
locks validation.

Tests explicitly characterize permissive temporary writer done with empty mapping,
not actual semantic feature completion. They never mark refactor done to fake
domain gate evidence. Runtime validator, actual CLI rejection/readback/locks and
feature transitions execute only against disposable roots.

## Change-request context

Current change_request action has required specification and **optional closing-report**
input. Missing closing-report is compatible: do not demand a nonexistent extract
tag or mark closing incomplete just because its report is a task link. Explicit
provided report must be a real current owning file; caller may select it from
verified task artifacts. Absence is valid, specification remains required. No
automatic app discovery/forwarding is claimed. Existing change-request skill
consumer still needs its own authorized integration review; this candidate does
not migrate it or manufacture an eval-report alias. Temp context tests deliberately
open a fixture stage to isolate optional-input compatibility; this is not real
feedback-stage unlocking or mandatory-gate bypass evidence.

## Revision-bound reuse without duplicate tests

Resolve scope from source/parent/story/subgoal and all current stable GWT ACs,
every original assertion/type and constraints before inspecting claimed report.
Explicit current source/spec/both design parts/actual implementation_files/tests/
config/mockup/interfaces/environment/evidence dependencies and semantic sufficiency
control reuse. Source-derived qualitative scenario suffices; no invented targets.
Use existing acceptance [consistency helper](.github/skills/x-ipe-task-based-feature-acceptance-test/scripts/verify_evidence.py)
API or CLI with independently resolved expected inputs/ACs. Do not copy expected
from report, invent a duplicate helper or replace type-specific proof with hashes.

Same relevant hashes plus actual execution artifacts, full original clauses/types,
environment/config and sufficient current review permit reuse. Closing does not
run tests twice as ritual. No timestamps-only receipt reuse. Failed, partial,
blocked, not-run, missing dependency or changed live setup invalidates affected
claims. UI actual authorized isolated browser navigation/trigger/console/assertions
cannot be replaced by source/jsdom review. API/CLI/library/integration/structured
evidence keeps applicable real boundaries. Generic browser availability is not
Chrome configuration permission. Required reruns use authorized acceptance
capabilities/same-task test-only adapter, no production repair in closing.

Any relevant misleading-doc correction, approved parent/means/intent delta or
test/config/code change invalidates affected tests/review/outcome; rehash again
before handoff, preserving unaffected IDs/history/dependency-independent evidence.
An unobserved stakeholder benefit alone does not invalidate proven engineering
delivery. Tests/fixtures/DAO/human approval are not stakeholder observation.
Record not measured and planned scenario/gap/owner (or unknown owner honestly),
never claim goal achieved or stakeholder approved without actual cited evidence.

## Docs, review, status and original output

Use self-checks and targeted tests by default; independent review is required only for an explicit request or concrete high-risk uncertainty under the shared single-loop policy. Reuse suitable current review; missing required review blocks the affected claim, not drafting.
Only misleading authorized docs need changes; no blanket spec/design/test rewrite.
No implementation changes. Code violating AC is defect, not authoritative new
acceptance: never weaken AC/tests to match faulty code without an approved CR.
Need test changes? Preserve original assertions/types, require scope/runner
authority and current affected acceptance, not convenient green checks.

Implemented or Tested are valid initial feature states only with current full
real acceptance evidence. Tested alone does not prove acceptance; Implemented
is not rejected solely because acceptance already transitions to Tested.
Authorized Completed resume preserves status/identity/history; source change
requires new approved scope and current evidence, not silent terminal task reopen.
Owner alone marks feature Completed and task completed once after required gates;
child never creates/closes tasks, app/feature/board/Git/routing duplicate work.
Current TASK-6749 candidate slice never means the larger task is completed.

Exact original task_completion_output schema, key order, feature fields,
process_preference enum, workflow/name and original conditional next-feature
suggestion remain. task_output_links is actual list, not mandatory fictional push,
PR or assessment entries. No new goal/outcome/release/action tag/output field.
Original refactoring_analysis fields remain compatible: unassessed score N/A,
refactoring_recommended false (no evidenced recommendation, not verified quality),
top_suggestions []. Actual previous assessment may populate real results only.
No fabricated numeric quality threshold; report states not assessed and limits.
Both original PR/changelog templates retained byte-for-byte; instantiate truthfully.

## Release scope and modes

Default engineering-only closure may be uncommitted; distinguish release not
requested/not performed from shipped. Explicit required release without authority
or successful actual evidence blocks that scope; never silently reinterpret it.
Owner alone, user-approved exact paths, protected preexisting staging/dirty work,
real strategy/identity and no broad staging/auto branch switch/stash/reset/network.
Main-branch-only prohibits new branches/PR; dev-session-based needs actual identity
and authorized scoped nonempty PR description/feature/design/test evidence.
Commit permission is not push/PR permission. Existing PR template playground
checkbox stays N/A absent explicit request; do not create playground automatically.
Human asks human within skill; full DAO and hybrid use bounded guidance. One owner
requires human completion/route confirmation for human and hybrid; full DAO selects
only authorized successors. Explicit human approval/release in every mode is never supplied by
DAO, tests or mere summary delivery. Return suggestions, no child next execution.
