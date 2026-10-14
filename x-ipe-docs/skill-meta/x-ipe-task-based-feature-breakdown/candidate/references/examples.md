# Feature Breakdown Examples

## Worked subgoal excerpt — same approved badge requirement

Authored document fixture, not autonomous execution or outcome observation.

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
| --- | --- | --- | --- | --- | --- |
| FEATURE-061-A | EPIC-061 | Status Badge | v1.0 | Read-only available/unavailable state labels | None |

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-061-A-01 | FR-061-01; explicit badge request | Operator | Recognize available versus absent current state | FEATURE-061-A supplies readable state; all-required: available and absent-state handling; alternatives: badge selected, text-only deferred/not built | planned UI scenarios for current and absent state; stakeholder observation unavailable | Read-only; no state controls | AC-061-A-01, AC-061-A-02 | not measured |

| Means | Selection | Bound / Rationale |
| --- | --- | --- |
| Badge | selected | Approved read-only state display; no controls |
| Text-only panel | not selected | Alternative means, not an additional feature/dependency |

The selected feature contributes to FR-061-01, rather than claiming the badge
artifact itself is the parent's achieved outcome. No feature per layer; no new
goal-board columns. Planned AC checks are not verified engineering delivery.

## Domain scenarios

Illustrative domain scenarios, not autonomous pilot execution receipts. One
lifecycle task/readiness owner throughout; no task create/close or successor
execution in these examples. Actual helper tests use temporary projects only.

## 1. Small single-feature registration

Approved EPIC-061 requirement has six badge ACs and fresh complete context review.
Reuse what/who/why, scope and zero-conflict decision. One domain <=7 features:
retain EPIC-061, no second Epic. FEATURE-061-A is a runnable read-only badge MVP
with direct dependencies [] (or the actual existing prerequisite). Do not invent
B/C simply to follow a phase scaffold. Create its Epic/Feature folders, populate
Feature List and detail in selected requirement part, description <=50 words,
coverage/risk and mockup N/A. Query then register one real Planned feature through
feature_create.py --feature; verify query readback. New feature uses v1.0.

Workflow-mode: gathering actually done with valid source artifacts. Supply
features-list = that populated part, breakdown-folder = requirements directory,
and --features [{id: FEATURE-061-A, name: Status Badge, depends_on: []}]. Read
back done, both exact outputs and one unique entry with untouched prerequisites.
No downstream refinement action is completed. Free-mode has no workflow write.
Resume queries board/state and reuses artifacts, not another create or append.

## 2. Multi-Epic new scope

Intake EPIC-062 spans catalog, cart and checkout with 12 estimated units and
fresh approved scope. Three natural domain/dependency/team clusters warrant
three groupings. Retain 062 for catalog, allocate additional collision-checked
063/064 with intake links after grouping decision. Each Epic has <=7 features.
Each A is a runnable MVP (catalog listing; usable cart over catalog; minimal
checkout over cart), not API interfaces without an outcome. B/C add scoped
search/persistence/provider capabilities. List direct cross-Epic dependencies
and reasons, validate DAG/topological order and preserve approved deferrals.
Register actual new Planned IDs and real keyed artifacts; no Draft/Pending
feature-board status, no manual Markdown board or invented batch operation.
Return actual epic_ids/count and feature_ids/count for the scoped result only.

## 3. Incremental CR with legacy identity

Existing FEATURE-005 has completed terminal I/O; FEATURE-028-B is implemented
settings. Intake EPIC-065 asks for one settings preference. Reuse gathered CR
impact decisions and refresh only changed settings scope/dependencies. Preserve
FEATURE-028-B/its original Epic, status, specification and stable ACs outside
approved delta. Update the owning older part, not arbitrary latest part. No
FEATURE-065-A unless a separately justified new unit is actually required.

Board mutable-field update preserves epic_id/status; matching resume is read-only.
Already-done workflow breakdown with unchanged dependency graph: verify current
populated artifacts and prior write evidence without replay. Existing state
stages remain identical. Changed existing workflow dependencies need supported
reconciliation or blocked output, not silent JSON edits. Pending breakdown with
only preexisting workflow IDs cannot be safely completed by installed --features:
it would append duplicates. Return blocked with real partial links; do not
invent a successful workflow_action_updated flag.

## 4. Genuine split with parent dedup

Approved parent FEATURE-010 has 25 ACs. Split runnable minimum listing and separate
search/filter capabilities under the validated Epic with reserved new suffixes.
Coverage table maps EVERY parent FR/AC to child ACs. Full coverage plus explicit
retirement authority: remove parent from active Feature List, retain historical
section/redirects and update board to Retired via feature_update.py. Query confirms
history still exists. Only then parent_features_removed includes FEATURE-010.
No archive/delete operation is invented. Partial coverage of AC-010.25 instead
retains parent, reports dedup_gaps and does not claim full split completion.
Existing dependent references/stages require authorized reconciliation before
retirement; never leave dangling IDs or erase completed execution history.

## 5. Negative/action boundary cases

- Explicit broken/escaping/wrong-Epic source blocks; no latest-file fallback.
- Unresolved material grouping/MVP questions go to human in human mode and
  bounded representative in full DAO and hybrid. Human and hybrid wait for human
  completion/route confirmation. Explicit human approval binds in every mode.
  Clear fresh input needs neither ceremony.
- Writer may accept absent tags/nonexistent files, skipped/pending in-stage
  prerequisites or duplicate IDs. Exit 0 is NOT domain completion evidence.
- Both populated features-list and scalar existing breakdown-folder must match
  actual required tags/artifacts. Extra tags/folder arrays are real helper errors.
- No --features or [] for initial done fails MISSING_FEATURES. Empty CR delta is
  not license to resend existing IDs. Successful unchanged resume only reads.
- Board corrupt/unreadable inventory is blocking: query/create permissiveness
  must not overwrite history. Duplicate IDs are resolved by identity query, not
  renamed replacement. Future promotion requires separate independent review.
