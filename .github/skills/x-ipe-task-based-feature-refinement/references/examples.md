# Feature Refinement Examples

Illustrative domain scenarios, not autonomous authoring/decision receipts. One
supplied lifecycle identity throughout; no child task allocation, status mutation,
commit or successor execution. Both EPIC/FEATURE and legacy FEATURE folders work.

## 1. Fresh clear Planned feature

Board query returns FEATURE-061-A, EPIC-061, Status Badge, v1.0, Planned. Selected
owning requirement part contains its complete Feature List/details and approved
badge scope. Reuse fresh findings, no forced interview. No specification link
exists: use x-ipe-docs/requirements/EPIC-061/FEATURE-061-A/specification.md.
Fill the complete scaffold, including explicit no-mockup rationale, NFRs, edge
states, exclusions, dependencies, version history and source/story/AC mapping.

### Worked new goal/story mapping

US-061-A-01: As an operator I want readable state labels so that I can recognize
available versus absent current state. Source is the explicit read-only badge
request; parent FR-061-01 is reused from the owning requirement artifact.

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-061-A-01 | FR-061-01; explicit badge request | Operator | Recognize available versus absent current state | FEATURE-061-A readable badge selected; all-required available and absent-state handling | planned available/absent-state UI scenario; no operator observation yet | Read-only; no state controls | AC-061-A-01, AC-061-A-02 | not measured |

| AC ID | Criterion (Given/When/Then) | Test Type |
| --- | --- | --- |
| AC-061-A-01 | GIVEN operator views the status panel WHEN current state is available THEN the badge shows the approved state label | UI |
| AC-061-A-02 | GIVEN no current state exists WHEN the status panel renders THEN an unavailable-state label appears | UI |

| AC ID | Validation Evidence | Delivery State | Outcome State |
| --- | --- | --- | --- |
| AC-061-A-01 | planned UI check of current-state label | planned | not measured |
| AC-061-A-02 | planned UI check of absent-state label | planned | not measured |

Human/hybrid confirmation is required for the actual specification revision.
Full DAO receives bounded guidance where a decision is needed. Workflow-mode:
feature_breakdown actually done, matching unique workflow feature exists; write
feature_refinement for that feature with specification and scalar
feature-docs-folder, both selected contexts and exact readback. Return links for
lifecycle's verified board specification_link/authorized Refined handoff; no
child feature-status update. Free-mode workflow_action_updated remains false.

```yaml
task_completion_output:
  category: feature-stage
  status: completed
  next_task_based_skill:
    - skill: x-ipe-task-based-technical-design
      condition: Design the refined feature
  process_preference:
    interaction_mode: interact-with-human
  execution_mode: free-mode
  workflow:
    name: N/A
  workflow_action: feature_refinement
  workflow_action_updated: false
  task_output_links: [x-ipe-docs/requirements/EPIC-061/FEATURE-061-A/specification.md]
  feature_id: FEATURE-061-A
  feature_title: Status Badge
  feature_version: v1.0
  feature_phase: Feature Refinement
  mockup_list: N/A
  linked_mockups: []
```

## 2. Authorized legacy CR preserves acceptance and language

FEATURE-005 is Completed, with board specification_link pointing to its existing
legacy x-ipe-docs/requirements/FEATURE-005/specification.md. Approved CR adds one
settings preference. Caller readiness explicitly covers the advanced-feature
change; do not reset Planned or downgrade Completed. Preserve stable Chinese
US/FR/AC prose and IDs, original Epic, unrelated sections and old version rows.
Add only approved preference story/AC, NFR/edge implications, minor version/CR
link and traceability delta; invalidate affected design/test evidence. A changed
scope needs current human/hybrid confirmation, not reuse of an old approval.
Unchanged resume verifies hashes/link/action without version/date bump or replay.

## 3. Current versus outdated shared mockups

Explicit current Epic settings mockup overlaps FEATURE-028-B; an unrelated cart
scene does not. Scope-filter BOTH new and existing copies. Keep shared root link
unless a local copy is needed; never overwrite foreign bytes. Analyze layout,
spacing, styling, interactions and error/loading/empty states. Map each current
in-scope element to user story/UI requirements/AC, comparison type UI. An omitted
current element blocks. An outdated mockup remains directional only, generates
no comparison AC and cannot override approved acceptance. Linked dates remain
MM-DD-YYYY provenance, not automatic newer-wins authority.

## 4. Material unknowns, missing identity or oversized scope

Ask only actual unresolved domain/threshold/edge questions, up to 3-5 without
padding. Human asks the human within skill; full DAO and hybrid use common bounded
message_context guidance. Unanswered material questions block. Clear facts are
reused, not asked again. Missing board feature or broken explicit specification
link blocks; return partial evidence to lifecycle, not manual board creation or
fallback to a different feature. Genuine multi-feature scope growth is a
breakdown recommendation; do not batch refinement or mark an invented Complex
status. Preserve existing artifacts until authorized scope is resolved.

## 5. Helper success is not domain completion

The writer may accept missing files/tags/contexts or an incomplete prerequisite.
Verify both actual populated matching file/directory outputs, both selected
contexts, unique feature identity and prerequisite done state. Folder arrays,
unknown tags, absent feature and locked stage are helper failures with preserved
state. Completed unchanged resume reads only; no --features append. Unsupported
required handoff/invalidation remains blocked, never silent downgrade/reset.

## 6. Legacy intent inference — source preserved read-only

Source: [FEATURE-047-A story](x-ipe-docs/requirements/EPIC-047/FEATURE-047-A/specification.md#user-stories).
These exact historical lines remain untouched; this example is an inference,
not retroactive human confirmation, a GWT migration or a delivery receipt:

- **US-1:** As a skill creator, I want a dedicated skill type (`x-ipe-dao`) so that I can create human representative skills using the standard X-IPE workflow instead of ad hoc conventions.
- [ ] **AC-047-A.1:** `x-ipe-meta-skill-creator` supports `x-ipe-dao` as a selectable skill type in the same creation flow used for other supported skill categories.

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-1 | inferred from FEATURE-047-A specification User Stories / US-1 explicit so-that | Skill creator | Create human representative skills using standard workflow rather than ad hoc conventions | Existing skill-type support enables this workflow; no claim all creators used it | planned review of selectable type; stakeholder usage observation unavailable | Preserve historical terminology/AC; no history rewrite or confirmation | AC-047-A.1 | not measured |

| AC ID | Validation Evidence | Delivery State | Outcome State |
| --- | --- | --- | --- |
| AC-047-A.1 | planned historical artifact review; not executed by this fixture | planned | not measured |

If a legacy story has no explicit so-that, do not invent a goal: block its
pertinent intent/coverage claim, retain other established evidence and ask only
the material clarification. Historical non-GWT ACs are not silently reformatted.

## 7. Authorized parent-goal delta — authored fixture, not a live CR

Illustrative approved CR-061-01 changes FR-061-01 so stale current state is also
recognizable as unavailable. Preserve US-061-A-01 and both AC IDs; bounded new
scope changes only the current-state criterion. No arbitrary freshness threshold
is invented: the source contract already supplies the stale-state flag.

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-061-A-01 | FR-061-01; illustrative authorized CR-061-01 parent goal delta | Operator | Recognize available versus absent or stale current state | FEATURE-061-A badge selected; all-required available, absent and flagged-stale cases | planned UI scenario: flagged stale state displays unavailable; actual outcome unobserved | Read-only; source stale flag; no new timing target | AC-061-A-01, AC-061-A-02 | not measured |

| AC ID | Criterion (Given/When/Then) | Test Type |
| --- | --- | --- |
| AC-061-A-01 | GIVEN operator views the status panel with current state WHEN the panel renders THEN flagged-stale state shows the unavailable-state label AND non-stale state shows the approved state label | UI |
| AC-061-A-02 | GIVEN no current state exists WHEN the status panel renders THEN an unavailable-state label appears | UI |

| AC ID | Validation Evidence | Delivery State | Outcome State |
| --- | --- | --- | --- |
| AC-061-A-01 | prior current-state evidence invalidated by FR-061-01 parent delta; planned rerun includes flagged-stale scenario | invalidated by goal delta | not measured |
| AC-061-A-02 | unchanged planned UI check of absent-state label; no historical pass fabricated | planned | not measured |

Only affected design/test/outcome evidence is invalidated. Unaffected absence
criterion bytes remain identical. Revised scope needs its actual policy-selected
confirmation; this authored fixture does not provide one or execute replanning.
