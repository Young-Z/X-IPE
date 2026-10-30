# Acceptance Testing — Authored Plans and Honest Evidence

These are authored plans/scaffolds, not autonomous skill execution, approval,
browser/API acceptance, release or observed stakeholder behavior. Installed
workflow CLI and consistency helper scenarios run in temporary test projects.

## 1. Read-only status badge — full source-to-AC coverage

Reuse approved FEATURE-061-A implementation/design frame verbatim in values.
Selected BadgeView and StateSelector are means, not new stakeholder goals.
All-required available and absent-state checks remain original frontend-ui type.

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-061-A-01 | FR-061-01; explicit badge request | Operator | Recognize available versus absent current state | FEATURE-061-A readable badge selected; all-required available and absent-state handling | planned available/absent-state UI scenario; no operator observation yet | Read-only; no state controls | AC-061-A-01, AC-061-A-02 | not measured |

| Source / Parent Goal | Story / Subgoal | AC ID | TC / Type | Original Assertions | Evidence / Revision | Delivery State | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FR-061-01; explicit badge request | US-061-A-01 | AC-061-A-01 | TC-061-01 / frontend-ui | approved current label; no controls/mutation | not executed; relevant input hashes required | planned | not measured |
| FR-061-01; explicit badge request | US-061-A-01 | AC-061-A-02 | TC-061-02 / frontend-ui | approved unavailable label; no controls/mutation | not executed; relevant input hashes required | planned | not measured |

Planned UI execution: resolve actual enabled Chrome MCP/dedicated profile/URL,
navigate to existing panel, trigger available/absent state, inspect badge label,
controls and state non-mutation plus browser console. Source/jsdom checks cannot
replace this. Fixture selectors/URLs are not invented as actual app evidence.
If browser unavailable, both cases Blocked, no fake Pass/done/Tested. Independent
unit checks may proceed but cannot erase blocked UI assertions. Operator outcome
scenario is recognizing the two states; no actual observation, no invented target.

Actual temporary helper fixture uses done implementation, selected specification
and impl-files file array, actual authored report and tests/status folder. Owner
write acceptance_testing passes keyed test-report/test-folder and verifies matching
validation action/readback. These path fixtures do not execute badge acceptance.
Original report-link output stays file-oriented. No actual board/app write here.

## 2. Authorized source/parent delta and explicit reuse

Illustrative approved CR-061-01 maps source-flagged stale state to unavailable,
without new clock/latency threshold. Preserve stable US/AC IDs and original
no-mutation clauses. Invalidate current-state/stale dependent design/tests/review/
outcome evidence; absence mapping unchanged does not alone justify reuse if shared
selector changed. Independently inventory source/spec/code/config/tests and
applicable design/mockup/environment/evidence. Rehash; if shared dependency changed,
rerun absence too without rewriting its stable mapping or history. Unrelated dirty
docs do not invalidate a claim when explicit dependencies establish independence.

Read-only verify_evidence checks report against independently selected expected
inputs and AC/types/assertions, never a receipt against itself. Omitted source,
specification, implementation, config, tests or evidence rejects reuse; so do stale
hashes, wrong feature, missing AC/type/assertion, failed/partial/blocked cases,
missing actual result/environment/artifact provenance or unsafe paths. A helper
consistency pass is not runtime execution or semantic acceptance. Reused actual
browser evidence requires same relevant code/mockup/URL/environment/config and
original assertions plus reviewed actual captured observations, not just log text.

## 3. Full-stack article feature (original example 1)

Illustrative FEATURE-049-A source explicitly approves creation/storage/listing
and editor/save behavior. Retain all five ACs: storage setup unit; POST creates
article with approved status/body; GET lists actual article API; New Article opens
modal UI; save title/content/tags UI with specified persistence behavior. These
expected codes/content must come from that source, not from this example.
Inspect actual route schemas/auth/data and selectors; use enabled Python/API
runner and actual configured browser for editor/save, integration where required.
Test real contracts and side effects, not just tool counts or successful file writes.
Actual evidence records methods/inputs/status/body plus UI trigger/console/state,
hashes and boundary (in-process versus deployed). This example is not_run and
does not assert five passes or stakeholder adoption. Missing browser blocks UI
while independent API checks proceed; no activity pass implies goal achieved.

## 4. CLI and library without frontend (original example 2)

FEATURE-018 explicitly approves --init filesystem creation, config validation
and error exit 1. Classify CLI entry behavior as integration: run actual executable
in disposable cwd, assert exit/stdout/stderr and specified files; invalid config
retains error message and no-mutation assertions. Config parser unit checks are
additional, not substitutes for CLI error exit. No browser/target_url prerequisite.
Match enabled stack declarations and existing runner/test-only adapter; never
invoke ordinary implement and change production behavior during acceptance.

For a library scope, inspect/import actual public API, valid/boundary inputs,
return values/errors/side effects and applicable integration/import compatibility.
All approved assertions retained; no UI-only or manual invented metric test.
Known valid fixtures require no ceremonial human data question. These remain
planned scenarios; subprocess helper tests elsewhere execute only temporary fixtures.

## 5. Disabled UI and mixed failures (original examples 3 and 4)

FEATURE-010 has two UI cases and one API case. If chrome-devtools-mcp false,
retain UI Blocked; actual passing API evidence would be 1/3 = 33.33% diagnostic
pass rate, not 50% or completed delivery. Original cases/types stay in report;
goal outcome remains not measured. No empty-config enablement or Playwright alias.

FEATURE-022-C feedback example keeps two API and four UI cases; hypothetical
observed submit timeout/export missing modal must be Fail with actual screenshot/
console/result, not assumed pass. Four actual passes of six = 66.67% diagnostic,
status blocked until all required assertions pass at current revisions. Reports
propose bounded fix scope; no code repair/expectation weakening or hidden UI failures.
Numbers are illustrative arithmetic, not actual execution or observed outcome.

## 6. Skills, prompts and configuration contracts

Approved skill feature has source/parent/goal/AC links; read complete candidate
package, cite precise section/line, verify actual contracts and consumer config,
run enabled appropriate validator/temporary workflow helper scenarios when AC
requires behavior. Structured review alone cannot turn keyword presence into
browser/runtime/lifecycle proof. No fake executable RED for prose-only changes;
existing implementation TDD/regression/assertions remain intact where applicable.
Candidate_ready is not published capability. Required independent main review
and explicit permission remain prerequisites for promotion. Automated helper/
content checks are fixture evidence, not autonomous agent execution or stakeholder
observation. Outcome not measured explicitly; no forced manual observation metric.

## 7. Conditional quality and existing mandatory app gates

Source acceptance passed at current revisions; inspected quality analysis finds
no evidenced refactor need. Original output still suggests conditional closing.
Free-mode may return that suggestion to owner. Workflow-mode current template
code_refactor optional false and actual helper suggests code_refactor pending:
record closing routing blocker; no fake skip/done/refactor-report, mandatory code
churn or imaginary quality problem. Existing actual gate must legitimately finish
or later authorized config migration resolves it. Acceptance action/delivery
evidence can be supported separately from downstream route availability.

Temporary helper tests prove correct acceptance_testing tags/context/readback,
reject folder arrays/extra tags/wrong feature/locked stage preserving bytes,
and characterize permissive missing report/context/pending-prerequisite writes.
Writer success alone is insufficient. Read-only resume never replays app/board
writes; advanced Completed feature status/identity remain unchanged. One owner,
no duplicate task/Git/routing or unrelated source changes in this maintenance slice.

## 8. All-type authored coverage using one report schema

Illustrative approved source FR-062-01 requests a reusable read-only diagnostic
snapshot across UI, HTTP, public library, CLI and a composed flow, plus a complete
skill package. These are authored source expectations, not requirements or actual
execution of this repository. All-required channels contribute to one source
story; no branch is an alternative that can be silently dropped. Each row uses
the existing coverage schema and every case uses the same acceptance_evidence
keys regardless of type. Planned commands/selectors are resolved from the real
scope before execution, never asserted as actual runtime proof by this example.

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-062-01 | FR-062-01; authored diagnostic request | Maintainer | Inspect the same diagnostic state through approved channels without changing it | all-required UI, HTTP, library, CLI, composed flow and skill contract | planned qualitative scenario; no maintainer observation | Read-only; no invented latency or adoption target | AC-062-UI, AC-062-API, AC-062-LIB, AC-062-CLI, AC-062-FLOW, AC-062-SKILL | not measured |

| Source / Parent Goal | Story / Subgoal | AC ID | TC / Type | Original Assertions | Evidence / Revision | Delivery State | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FR-062-01; authored diagnostic request | US-062-01 | AC-062-UI | TC-062-UI / frontend-ui | snapshot label; no controls/mutation; console free of runtime errors | not executed; relevant input hashes required | planned | not measured |
| FR-062-01; authored diagnostic request | US-062-01 | AC-062-API | TC-062-API / backend-api | GET status 200; approved body; no storage mutation | not executed; relevant input hashes required | planned | not measured |
| FR-062-01; authored diagnostic request | US-062-01 | AC-062-LIB | TC-062-LIB / unit | public import and return; documented invalid-input error; no argument mutation | not executed; relevant input hashes required | planned | not measured |
| FR-062-01; authored diagnostic request | US-062-01 | AC-062-CLI | TC-062-CLI / integration | actual executable exit/stdout; invalid input exit 1/stderr; no file mutation | not executed; relevant input hashes required | planned | not measured |
| FR-062-01; authored diagnostic request | US-062-01 | AC-062-FLOW | TC-062-FLOW / integration | real component handoff yields same snapshot; isolated setup/cleanup; no state mutation | not executed; relevant input hashes required | planned | not measured |
| FR-062-01; authored diagnostic request | US-062-01 | AC-062-SKILL | TC-062-REVIEW / structured-review | complete resources; original output and same-owner lifecycle; actual app tags and contexts | not executed; relevant input hashes required | planned | not measured |
| FR-062-01; authored diagnostic request | US-062-01 | AC-062-SKILL | TC-062-HELPER / integration | actual validator/helper exits and results; required error rejection; no source mutation | not executed; relevant input hashes required | planned | not measured |

The skill AC needs both structured-review and integration, with independently
resolved type-specific clauses and explicit reuse partitions retaining its AC ID.
Full report coverage must include both rows. Five-type consistency tests exercise
the helper API/schema only, not these fictional browser/HTTP/library/CLI flows.
Real UI still needs isolated enabled Chrome, navigation/trigger/console/assertions;
all others need actual applicable boundaries and current command/results/artifacts.
No Pass/done/Tested or observed stakeholder outcome is inferred from this plan.
