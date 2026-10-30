# Bug Fix — bounded examples, not executed application fixes

These are authored fixtures, not actual user approvals, source audits or observed
stakeholder outcomes. The dedicated test suite separately executes a miniature
Python fixture red/green and regression in a disposable directory; it does not
fix this application's authentication code or autonomously run this skill.

## 1. Token boundary: restore the source contract, not a grace period

Original report: token accepted at exact expiry. Authored approved contract:
only expiry > now permits authorization; equality is expired. Earlier example
claimed the opposite inequality without a source and invented full-suite totals;
those claims are not evidence. Real execution must inspect actual source first.

| Goal / Subgoal | Parent / Source | Stakeholder | Intended Behavior | Contribution / Selection | Constraints / Non-goals | Story / AC / Type | Failing Scenario | Fixed / Regression Evidence | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-AUTH-01 | FR-AUTH-01; specification#AC-AUTH-01 | account owner | only unexpired tokens authorize access; equality is expired | all-required reject expired/boundary and accept unexpired; strict comparison selected from alternatives | no grace period; preserve clock source and unrelated auth callers | US-AUTH-01; AC-AUTH-01; Unit | expiry == now incorrectly accepted; expected rejected | actual disposable fixture only: same assertion red then green; expired/unexpired regressions preserved; not application authentication evidence | not measured |

Understand/reproduce: arrange expiry=now=10, act valid(expiry, now), assert false.
Actual miniature broken predicate is expiry >= now; selected fix expiry > now.
Root cause: inclusive predicate violates strict source boundary, not failed setup.
Conflict Detector/Validator in a real run inspect login/refresh/middleware callers
and relevant clock units; expected rejection versus unexpected clock/API changes
are classified against ORIGINAL request. Authored no-conflict is not real audit.
No new goal, grace period or weakened expectation. Unit type retained; additional
integration/UI checks use actual layers if implicated. Key design impact requires
approved design/Change Log before implementation. Full suite and original UI
reproduction are required in a real app run, not replaced by these three fixtures.

mini AAA route (authored Python fixture context):

```yaml
input:
  operation: fix
  aaa_scenarios:
    - scenario_text: "Arrange expiry equals now under AC-AUTH-01; Act valid(expiry, now); Assert false (expired)."
    - scenario_text: "Arrange expiry greater than now; Act valid; Assert true (unexpired preserved)."
    - scenario_text: "Arrange expiry less than now; Act valid; Assert false (expired preserved)."
  source_code_path: "actual approved source directory"
  test_code_path: "actual approved test directory"
```

No feature_context is needed for a non-feature fix under the tool's explicit fix
operation. Synthetic fallback, if used internally by that tool, is not an actual
feature allocation or returned task/workflow ID.

Original full output example: blocked because this authored example has no real
application reproduction/full-suite/review. No require_human_review field invented.

```yaml
task_completion_output:
  category: standalone
  status: blocked
  next_task_based_skill: null
  process_preference:
    interaction_mode: interact-with-human
  execution_mode: free-mode
  workflow:
    name: N/A
  task_output_links: []
  bug_severity: High
  root_cause: "Authored fixture inclusive expiry predicate; actual application cause unverified"
  conflicts_found: []
```

## 2. Empty regular password versus intentional guest access

Original report: regular password login accepts empty input. Intended contract
requires nonempty regular credentials while guest access follows a separate
approved mechanism. Do not claim bcrypt accepts an empty hash or invent actual
security behavior without inspected implementation.

A shared validator guard might break a guest caller: unexpected relative to the
regular-login report. Inspect actual regular/guest callers, source constraints and
existing tests. Narrow fix to regular handler if supported by the source; otherwise
ask the consequential question (human asks human; full DAO and hybrid bounded guidance).
Changing guest access or password policy needs real human CR authority in all modes.
No actual approval is supplied here. Missing authority means blocked, not bypass.

mini AAA branches: empty regular password is rejected (bug-specific red before
fix); valid regular credential retains original behavior; guest access retains
its documented mechanism. Preserved regression tests may already pass; only the
bug-specific test must fail. Never damage a passing constraint to manufacture red.
JS implementation uses actual Vitest/Jest behavior, not Python string matching.
Selected enabled tool operation fix owns red/fix/green and returns operation_output;
review/verify original reproduction and full existing suite without invented totals.
Original output includes all fields from example 1 and actual conflict records,
not a truncated legacy schema. Optional caller-supplied require_human_review or
other dynamic fields pass through unchanged; absence does not waive domain review.

## 3. Legacy, disabled browser and unavailable mapping

Legacy story explicitly says so-that I can retry a failed upload: inferred parent
recovery intent with exact story anchor, not confirmed. Preserve retry/error/data
constraints and existing GWT AC/type; missing intent blocks only pertinent outcome
claims, unclear expected behavior blocks restoration. No arbitrary success target.

A CSS visual defect uses browser reproduction/verification when UI capability is
configured and available. Disabled optional browser records visual evidence gap;
actual component tests are not browser evidence. Enabled but unavailable required
browser capability blocks its claim; never fabricate screenshots or enable config.
No forced tracing when tracing_enabled is false or infrastructure absent.

Current UI ACTION_MAP/template has no bug-fix action even though tools.feedback
has bug_fix routing. Requested workflow-mode is blocked, not changed silently or
recorded as done. Owner may obtain authorized free-mode disposition with null
app action/N/A workflow; do not allocate a feature/action/tag to fill the gap.

## 4. Regression failure and bounded side effects

Reported serialization bug implicates callers, stored schema and API behavior.
Minimal restoration includes original bug scenario and preserved consumers; inspect
actual root-cause boundaries, not just the touched function. A key interface change
updates approved design/Change Log first, never changes ACs to fit code.

Any new regression blocks completion. Pre-existing suite failures remain cited
with before/after hashes and results; they do not become a full-suite green claim
or disappear via deselection. Changed source/test/config invalidates affected red/
green/review evidence; rerun required checks. Missing independent review blocks
pertinent completion/publication; candidate drafting remains possible. Return full
original blocked output and partial links to the same owner, no next-task execution.
