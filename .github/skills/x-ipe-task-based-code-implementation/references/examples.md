# Code Implementation — Authored Mappings and Scenarios

These authored artifact/scaffold fixtures are planned, not autonomous routing,
executed production code, actual review/approval or stakeholder observations.
Installed workflow/board helper tests execute in temporary projects only. The
original fullstack, skills, fallback and retry scenarios remain below with
current lifecycle/output/verification contracts, not legacy count-based claims.

## 1. New read-only status badge — outcome to AC to tests to means

Read both parts of the approved FEATURE-061-A design and original specification.
Same supplied task/readiness/owner; actual Designed feature. Goal/story/AC table
below is byte-equivalent in values to upstream design, not a new product goal.

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-061-A-01 | FR-061-01; explicit badge request | Operator | Recognize available versus absent current state | FEATURE-061-A readable badge selected; all-required available and absent-state handling | planned available/absent-state UI scenario; no operator observation yet | Read-only; no state controls | AC-061-A-01, AC-061-A-02 | not measured |

Selected BadgeView and StateSelector remain means within the approved design.
Rejected dashboard rewrite is not a backlog mandate. Select compatible pure
adapter/render details without silently changing contracts, no invented latency
or timing targets and no chasing test/tool/component/activity counts.

| Source / Parent Goal | Story / Subgoal | AC ID | Selected Means | Test / Assert | Delivery State | Outcome State |
| --- | --- | --- | --- | --- | --- | --- |
| FR-061-01; explicit badge request | US-061-A-01 | AC-061-A-01 | BadgeView + StateSelector | UI assert approved current label; no mutation | planned | not measured |
| FR-061-01; explicit badge request | US-061-A-01 | AC-061-A-02 | BadgeView + StateSelector | UI assert approved unavailable label; no controls/mutation | planned | not measured |

### Ordinary AAA/TDD plan

```text
@frontend
Test Scenario: AC-061-A-01 available current state
  Arrange:
    - Existing read-only panel, authoritative approved state label
  Act:
    - Render current state through existing adapter/panel
  Assert:
    - Badge text equals approved current label
    - Existing state is unchanged; no state controls added

@frontend
Test Scenario: AC-061-A-02 absent current state
  Arrange:
    - Existing read-only panel, absent current state
  Act:
    - Render through existing adapter/panel
  Assert:
    - Badge text equals approved unavailable label
    - No controls added and no state mutation
```

Original UI acceptance type remains UI; unit selection and mocked integration
are additional means checks, not replacements. Actual test paths/commands must
come from the inspected project. New behavior's relevant assertion fails before
implementation, then passes; existing satisfied expectations keep baseline and
regression. Never weaken/delete/skip assertions to claim delivery. HTML5 matches
actual enabled vanilla HTML/CSS/JS declaration. Invoke once sequentially with
original tagged scenarios, source/test paths and current mockups if supplied.
General is eligible fallback, not extra mandatory invocation.

Qualitative outcome scenario: operator sees approved labels for available/absent
state and can recognize those conditions. Source US-061-A-01, no observation yet.
Passing UI checks would support verified engineering delivery at recorded hashes,
not prove the operator experienced the outcome. This fixture remains planned.

### Real file/directory handoff adaptation

Illustrative temporary owned artifacts: src/status/badge.js,
src/status/select-label.js and tests/status/badge.test.js. Owner passes keyed
impl-files as their nonempty file array and impl-folder as scalar src/status.
Test file is outside browsing folder but remains real/scoped/safe. Original
output task_output_links remain directories src/ and tests/ for this layout;
never blindly use them as file tags. Actual Installed writer accepts arrays and
upgrades state schema to 4.0; owner still verifies files/contexts/done/readback.
No real workflow write, board update or code execution is claimed by this text.

## 2. Authorized parent/means delta — affected tests invalidated

Illustrative approved CR-061-01 now includes source-flagged stale state as
unavailable. No new clock/freshness threshold; all-required available, absent and
flagged-stale cases retain original US/AC identities. Same upstream delta frame:

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-061-A-01 | FR-061-01; illustrative authorized CR-061-01 parent goal delta | Operator | Recognize available versus absent or stale current state | FEATURE-061-A badge selected; all-required available, absent and flagged-stale cases | planned flagged-stale unavailable-label scenario; actual outcome unobserved | Read-only; source stale flag; no new timing target | AC-061-A-01, AC-061-A-02 | not measured |

| Source / Parent Goal | Story / Subgoal | AC ID | Selected Means | Test / Assert | Delivery State | Outcome State |
| --- | --- | --- | --- | --- | --- | --- |
| FR-061-01; CR-061-01 parent delta | US-061-A-01 | AC-061-A-01 | BadgeView + StateSelector | prior affected evidence invalidated; UI assert flagged-stale unavailable and non-stale current labels, preserve no-mutation assertions | invalidated by goal delta | not measured |
| FR-061-01; explicit badge request | US-061-A-01 | AC-061-A-02 | BadgeView + StateSelector | UI assert approved unavailable label; no controls/mutation | planned | not measured |

Only affected interface/algorithm/tests/design-log change with authorized scope;
absence row and original assertions remain identical. Relevant RED must precede
fix, then rerun affected current/stale checks plus dependent regression/review.
Keep no invented targets, observation or acceptance rewrite. Dependency analysis may
require absent-state rerun too without rewriting its mapping; unchanged bytes
alone never prove evidence independence. Advanced Completed status stays Completed
unless separately authorized. No-op resume verifies hashes/owner action read-only.

## 3. Standard backend + frontend project feature (original example 1)

FEATURE-010-A project creation is approved fullstack Python/Flask + vanilla
HTML/CSS/JS with ProjectService/ProjectAPI/ProjectUI and current form mockup.
Use its actual parent/story intent and full ACs, not a generic example KPI.
Approved API scenarios: create a project returns 201/new ID; duplicate name returns
409 and already-exists message. Approved form scenario: fields name/description
appear and Create stays disabled until valid name. Cross-layer create scenario:
project appears and the mock backend receives the correct POST. Retain all those
assertions and their specification test types; actual network/UI checks supplement
mocked integration where needed. These behaviors require source authority.

Inspect source/design/current mockup/config hashes and baseline; create suitable
RED checks, then match only enabled declarations semantically. Invoke Python
backend first and HTML5 frontend second, each once for owned scope. Record actual
implementation_files/test_files/per-original-assert test_results/lint_status and
run cross-layer/regression checks. Missing original ACs or failures block; scenario
counts never substitute for coverage. Existing applicable runtime tracing only,
INFO public/DEBUG helpers and redaction/opt-in checks; no infrastructure creation.
Return original task_completion_output with conditional Acceptance Test suggestion,
directory links adapted to real layout; same owner handles action/Implemented
and next boundary. No fake pass/observed outcome is asserted here.

## 4. Skills and MCP special delegation (original example 2)

FEATURE-045-A has approved skill-package scope. Detect skill files/program_type
skills before ordinary AAA/routing; use x-ipe-meta-skill-creator with same supplied
task/readiness, complete candidates and actual package-scoped AC checks. No
obsolete nine-step/round shortcut, no blanket skip-validation. Keep unrelated
source/dirty docs and publication boundary: candidate_ready remains candidate,
not implemented-and-published until authorized reviewed promotion is evidenced.
Acceptance Testing still performs structured review later; no child routes it.

MCP server scope likewise goes through mcp-builder before normal routing. Preserve
protocol/API/transport/security/error/assertion tests and builder quality checks;
its guidance is not a test pass. Any separate runtime/frontend ordinary code
still uses enabled semantic routing sequentially after special delegation.
Collect all scoped acceptance evidence and apply tracing only where existing
infrastructure is actually applicable. Unmigrated delegate board/Git/routing
instructions require an explicit same-owner adapter, not duplicate lifecycle.

## 5. AAA fallback with unresolved acceptance (original example 3)

FEATURE-020-B has vague error acceptance. x-ipe-tool-test-generation is a safety
net for mapping an already approved contract into suitable tests, not authority
to invent missing expected errors/KPIs. If ambiguity persists, human asks
the bounded human question; full DAO and hybrid offer bounded guidance under common contract
without confirming unknown intent. Block affected generation/implementation until
expectations resolve. Once resolved retain all ACs/Assert clauses, demonstrate
relevant RED then GREEN/regression; file/test counts are not completion evidence.

## 6. One retry and integration failure (original example 4)

FEATURE-015-C approved pagination assertion expects total_count metadata.
Backend result fails with missing serializer field. Retry the failed tool ONCE
with unchanged scenarios/original assertions and exact KeyError context; fix
behavior, not the expectation. Preserve passing output; second failure blocks
its delivery. Invoke dependent frontend only when appropriate contract evidence
exists. Integration mismatch cannot be dismissed because unit checks pass;
resolve specifically through actual mode and authorized affected design/CR gate,
then rerun dependent assertions/regression. No pass count/outcome fabricated.

## 7. Permissive helpers, unavailable evidence and resume

Real temporary helper cases preserve schema4 file arrays/scalar browsing folder
and verify readback/Implemented; read-only resume keeps board/state bytes. Extra
keys, folder arrays, invalid elements, absent feature and genuinely locked stages
fail without state change. Writer also accepts missing tags/empty arrays/missing
files/directories/pending design; characterize that gap, never claim completion.
Owner requires all mandatory prior actions done, actual contexts/files/revisions
and every scoped AC; no skipped prerequisites or design file relabeled as code.
Missing trace infrastructure means justified skip, not automatic new setup. Source/
design/test/mockup/config edits invalidate relevant evidence; unrelated dirty docs
are protected. Outcome remains not measured unless actual cited observation exists.
Legacy explicit so-that inference uses exact anchor; missing intent blocks only
its pertinent claim. Main reviewer unavailable means candidate drafting only,
never promotion. No board/memory/Git/other-source writes in this maintenance slice.
