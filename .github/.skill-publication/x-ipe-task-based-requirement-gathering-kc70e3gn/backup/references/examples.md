# Requirement gathering examples

## Worked outcome frame — authored requirement artifact excerpt

This is fixture content, not verified delivery or observed operator behavior.
The explicit source request is: operators need to distinguish available from
unavailable current state without changing that state. FR-061-01 is the stable
requirement identity reused as the root goal, not a persisted goal record.

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-061-01 | explicit request above | Operator | Distinguish available from unavailable current state | all-required: current-state label and unavailable-state handling | planned scenario: operator sees the available label with current state, unavailable label with absent state | Read-only; no state controls or arbitrary time target | AC-061-A-01, AC-061-A-02 (planned refinement) | not measured |

| Requirement ID | Goal ID | Source / Evidence | Constraints |
| --- | --- | --- | --- |
| FR-061-01 | FR-061-01 | explicit request above; planned available/absent-state scenario | Read-only; no state mutation |

Delivery evidence: no tests run in this example; not yet verified engineering
delivery. Alternatives badge versus text are means, selected at breakdown; they
are not two additional required product outcomes or separate feature mandates.

## Domain scenarios

Examples illustrate domain decisions, not recorded successful agent executions.
The caller supplies one lifecycle readiness context. Each example returns the
same task_completion_output schema; none creates/closes tasks, commits or starts
a successor. Completion/routing is handled once by the common lifecycle.

## Example 1 — Small clear new requirement, free-mode

Request: add a read-only status badge; upstream idea already states users, business
value, scope, acceptance and language. Existing conflict baseline covers every
part with current hashes and scope/dependency summaries.

1. Reuse fresh intent and compare this delta against all covered scopes. Inspect
   only affected dependencies; no full reanalysis, compulsory web research or
   ceremonial clarification. Record reviewed zero conflicts and reuse provenance.
2. Allocate next EPIC-061 (if 060 is highest), create its mockups directory even
   with mockup_list N/A, and fill a concise complete Epic section in the active
   requirement-details file. Feature Breakdown later assigns FEATURE-061-A;
   requirement gathering does not put EPIC-061 in a Feature ID row.
3. At 473 or 500 current lines append in place; at 501 follow the split procedure.
   Record actual output path/part and verify links, language and acceptance.
4. Free-mode: no app action write, workflow_action_updated false. Return documents
   and suggested Feature Breakdown; the lifecycle applies its actual boundary.

## Example 2 — Standard new work, workflow-mode, ZH

Resolved Chinese refined idea requests a session explorer separate from terminal
I/O. Required idea path and optional mockup content are valid; no reusable conflict
baseline exists. Read all current parts once and record a complete baseline.

Comparison finds existing legacy FEATURE-005 (terminal I/O) and FEATURE-028-B
(settings) but only a dependency, not a changed responsibility. Present any real
choice under current policy with coupling/cohesion rationale. Document the actual
independent-work decision and Related Features root-relative links in Chinese;
stable IDs/tags remain unchanged. New intake uses an EPIC header, not a premature
FEATURE-029 assignment from the old examples.

Copy validated local mockup into EPIC-061/mockups without overwriting foreign
bytes; URL-only mockups remain checked/linked. Verify domain gates, then write
requirement_gathering done using BOTH requirement-doc active file and scalar
requirements-folder. Read shared.requirement.actions.requirement_gathering back
and verify exact artifacts/prerequisites before returning true. Do not mark
feature_breakdown done, execute it or precreate its task.

## Example 3 — Existing-feature CR delta and conflicts

Request: add persistent dark/light toggle to FEATURE-028-B theme settings.
Reuse an authorized CR delta and complete fresh coverage map. A changed part
requires reading affected settings FRs/ACs plus dependencies, not regenerating
all prior analyses. Compare against all unchanged scope summaries too.

Record recommendation: same responsibility, UI, users and store → CR. Human
answers real within-skill questions; full DAO and hybrid get bounded guidance.
Human and hybrid wait for human completion/route confirmation; explicit human
approval remains binding in every mode.
Allocate this intake's next Epic; existing FEATURE-028-B identity stays intact.
Append idempotent marker with date/task/ref, change, FR-028-B.1/FR-028-B.3 and
specification follow-up. Minor conflict updates only agreed text inline. A major
contradiction instead retains old sections under [RETIRED by EPIC-061] with reason,
date and linked replacement. Preserve unrelated FRs/ACs and list actual updated
and retired paths in conflicting_docs_updated/conflicting_docs_retired.

## Example 4 — Material uncertainty or invalid sources

An explicit selected idea path is broken or escapes the root: blocked, no fallback
to a newer unrelated idea. A required workflow refined idea of N/A also blocks.
No response to a material question/conflict means blocked, not an invented answer.
DAO guidance cannot substitute for explicitly required human authority.

## Example 5 — Incomplete app output or stale evidence

Writer may accept only requirement-doc or paths to nonexistent files. Its exit 0
does NOT justify workflow_action_updated true or domain completed. Verify both
real artifacts, exact state and gates; otherwise return blocked, false flag and
actual partial links. Never set a missing prerequisite skipped/done to unlock.
Changed idea/part/config invalidates affected checks/decisions; timestamps alone
cannot authorize reuse. Keep independent-review availability separate from
contract tests and helper evidence; candidate-ready is not promoted.

