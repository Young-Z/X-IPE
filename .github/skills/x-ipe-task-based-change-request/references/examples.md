# Change Request — authored examples, not executed stakeholder outcomes

Use actual canonical EPIC/FEATURE or legacy ownership, source links and revisions.
The following are authored fixtures, not human approvals or actual source audits.
All proposed tests are planned; stakeholder outcomes remain not measured. Fixture
approval labels explain the intended authorized path, not a real project decision.

## 1. Settings auto-save: modification of selected means

Request: make settings auto-save instead of a save button. Existing approved
FR-005-01/US-005-01 outcome is preferences persist across reload; no sharing.
Critically evaluate explicit save versus auto-save failure/retry semantics before
approval. Current source/code must really be inspected in an actual CR run.

| Goal / Subgoal | Parent / Source | Stakeholder | Before Outcome | Proposed Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | Story / AC Links | Delta Kind | Authority | Affected Evidence | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-005-01 | FR-005-01; approved preferences scope | account owner | preferences persist across reload | preferences persist across reload | all-required persistence + reload; auto-save selected instead of explicit save | planned qualitative edit, wait for saved state, reload and see same value | no sharing; preserve retry/error visibility | US-005-01; AC-005-01 | selected means only | human-approved CR-002 scope; fixture only | AC-005-01 design/test/outcome evidence invalidated; rerun planned UI reload check | not measured |
| US-005-02 | FR-005-02; unchanged privacy scope | account owner | preferences remain private | preferences remain private | unchanged privacy rule | original qualitative owner-only scenario retained | no coworker access | US-005-02; AC-005-02 | unchanged | original source contract unchanged | retain original AC-005-02 source and evidence bytes | not measured |

| Aspect | CR Requirement | Existing Feature(s) | Evidence / Boundary Decision |
| --- | --- | --- | --- |
| Users | account owner | account owner | FR-005-01 source unchanged; same users |
| Workflow | edit triggers save with visible failure | explicit save then reload | AC-005-01 changes trigger, not persistence outcome |
| Data Model | same preference schema | existing owner preference map | actual schema/callers inspected in real run; no new sharing |
| UI Elements | saved/pending indicator | save button and preference fields | mockup-v1 retained; proposed mockup-v2 |
| API Endpoints | same settings save contract | existing settings endpoint | design/caller inspection required; no API-only classification |

| # | Type | Affected Feature | Severity | Classification | Description | Source / Revision | Resolution / Authority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | specification | FEATURE-005 | medium | expected | explicit save trigger conflicts with auto-save | specification.md#AC-005-01; fixture source, hash recorded only in real run | approved trigger delta only; preserve failure/retry contract |

| AC ID | Criterion (Given/When/Then) | Test Type |
| --- | --- | --- |
| AC-005-01 | GIVEN saved preferences WHEN owner edits and sees saved state then reloads THEN new value persists AND failed saves remain visible with retry | UI |
| AC-005-02 | GIVEN owner preferences WHEN another account views settings THEN owner values remain inaccessible | UI |

Approved authored path: one CR in actual legacy FEATURE-005 or EPIC/FEATURE owner;
minor specification/history trigger delta, applicable design context invalidation,
new mockup-v2 preserving v1. Requirement unchanged because high-level outcome is
unchanged. Neither reload tests nor actual stakeholder benefit are claimed here.

Original full output example (authored planned disposition; not actual execution):

```yaml
task_completion_output:
  category: standalone
  status: blocked
  next_task_based_skill:
    - skill: x-ipe-task-based-feature-refinement
      condition: When CR modifies an existing feature
    - skill: x-ipe-task-based-feature-breakdown
      condition: When CR requires a new feature
  process_preference:
    interaction_mode: interact-with-human
  execution_mode: free-mode
  workflow:
    name: N/A
  task_output_links: []
  feature_id: FEATURE-005
  cr_id: CR-002
  cr_classification: modification
  affected_features: [FEATURE-005]
  new_feature_ids: []
  requirement_updated: false
  mockup_updated: false
  updated_mockup_paths: []
  conflicts_found:
    - feature: FEATURE-005
      type: specification
      severity: medium
      classification: expected
      description: explicit save trigger; authored source not a real audit
  conflicts_resolution: none
  conflicting_docs_updated: []
  conflicting_docs_retired: []
```

## 2. Bulk import: new outcome versus implementation alternative

Bulk import to product management is not automatically new_feature because an
ImportService, endpoint or screen is new. If approved outcome is managing many
products efficiently and import is a bounded means, modification may fit.
If current source only authorizes individual product editing and operations staff
request a new stakeholder outcome of validating/ingesting supplier catalogs with
reject/recovery reporting, propose new_feature after actual five-axis/conflict study.

Goal delta: supplier operator; existing individual edits → approved catalog
ingestion outcome; parent product-operations source; selected import alternative;
all-required parsing/validation/reject-report children; qualitative valid/invalid
catalog scenario; no silent data loss; new FR/US/AC IDs reserved only when approved;
affected product API/design/test evidence invalidated, unrelated inventory retained.
Outcome not measured; approval pending is blocked, not a confirmed benefit.
Keep CR in existing product owner folder, update affected spec/history and new
requirements before implementation; suggest breakdown; new_feature_ids: [].
No related feature: approved free-mode requirements intake with spec N/A; workflow
per-feature readiness blocked. Never run breakdown here to obtain a CR folder.

## 3. Profile flattening: actual conflict evidence and major retirement

Existing profile outcome unchanged; scalar flattening can be modification even
with API/data changes. Inspect source specifications/designs and real callers:
search AC-007-03 reads profile.address.city; dashboard destructures
profile.preferences.theme; admin bulk edit iterates profile.permissions.roles[].
Record actual source anchors and SHA256 in the real CR, not invented hashes here.
Scalar path changes are expected; lost role-array semantics is unexpected/high.
Propose keep arrays nested and preserve search/theme adapters; blocked until
actual human approval of multi-feature solution, even full DAO. Then conflicts
resolution may be mitigated; no document mutation before that approval.

Minor AC references updated inline. Major contradictory data contract is retained
under [RETIRED by CR-003] with reason, date, CR reference and replacement. Preserve
all old version rows and source-to-replacement IDs. Approved requirement/spec/design
delta occurs before implementation; only affected dependent checks/review/outcome
are invalidated. Unrelated caller evidence remains intact. Not measured outcome.

## 4. Better error handling: consequential ambiguity and legacy inference

"better error handling" could mean upload errors, developer logs or user recovery.
Ask only consequential scope/source questions per mode; no repeated confirmation
after current consolidated approval. Legacy explicit story "so-that I can retry
failed uploads" permits inferred recovery goal with exact story source, not
confirmed intent. Missing/ambiguous goal blocks only pertinent outcome/coverage
claims, not unrelated original delivery evidence. New/changed scope remains
blocked until actual intended behavior/success constraints are clear and approved.

## 5. Safari crash: bug intake, not a third classification enum

Login crashes on Safari against documented existing behavior. Return blocked CR
intake with bug-fix suggestion to lifecycle owner; do not fabricate classification,
new outcome, CR-completed evidence or output fields. No child automatically starts
bug-fix or registers another task; owner handles actual authorized disposition.

## 6. Enabling subgoal and multi-feature CR chain

Approved parent preferences persistence outcome can add retry subgoal AC-005-03
within existing constraints: all-required save/retry/reload branches. Qualitative
offline then reconnect scenario, original UI/API checks appropriate to changed
clauses, no fabricated benefit. Compared alternatives (explicit retry versus bounded
queue) select one; do not build all alternatives. New enabling subgoal is not
automatically new_feature; modification may be correct after actual impact study.
Approved changed acceptance/source/context updates and affected invalidation happen
before implementation. Audit reporting for compliance stakeholders may instead be
new_feature; logging mechanism alone is not proof. Subsequent import validation or
error reporting CRs reuse real feature ownership, check pending CRs and preserve
histories; mixed unrelated intents require proposed separately approved splits,
not speculative tasks or recursive routing.
