# Goal contract — document-local outcome and evidence

An output is a delivered artifact/capability; an outcome is an observable change
for a stakeholder. A feature contributes to an outcome; shipping it is not proof
the stakeholder experienced that outcome. Internal enabling subgoals are valid
when their credible contribution chain to a parent is explained, not asserted.

## Minimal frame in an existing artifact

Use a short table or equivalent prose in the existing requirement, breakdown,
specification, design, acceptance, closing, CR, bug or quality artifact. No new
goal database, mandatory graph, board field, output key, action tag or approval
ritual. Reuse existing FR/US/AC identifiers and source/parent links. Optional
doc-local G identifiers are stable anchors, never persisted to the board; retain
reserved IDs and old-to-new mappings on changes rather than renumbering history.

For each new/changed scoped goal or subgoal record:

- Stakeholder and desired observable outcome, source intent and parent identity.
- Deliverable contribution, including indirect enabling rationale where relevant.
- Success evidence: a known measure if justified, or a concrete qualitative
  scenario with observable conditions/results. Do not force arbitrary metrics.
- Constraints/non-goals, source/story/leaf AC links and evidence gaps.
- Decomposition/dependencies: **all-required** children versus **alternatives**;
  select and bound an alternative with rationale, not build every possible means.

Leaf ACs remain stable Given/When/Then (GWT) criteria and retain domain test types.
Means choices are adaptable within the approved outcome/acceptance/constraint
contract; implementation choices are not independent stakeholder goals by default.
Bound goal count by coherent scope and justified coverage, not fixed minimums or
three-goal caps. A small feature may have one goal; necessary cases still apply.

## Honest evidence states

- **not measured**: no relevant stakeholder observation yet; record the planned
  scenario/owner or unavailable evidence, never imply failed or achieved outcome.
- **verified engineering delivery**: current revision-bound artifact/AC checks
  support delivery only. Record actual commands/results/source and test hashes.
- **observed stakeholder outcome**: actual stakeholder/context observation matches
  the goal scenario at the relevant revision; cite that observation and limits.

Record delivery and outcome separately: delivery may be verified while outcome
remains not measured. A test plan, simulated fixture, document review, DAO guidance,
or approval is not a stakeholder observation. No fake confirmation or success.

## Legacy and bounded replanning

For legacy scopes reuse explicit story **so-that** intent only, label the goal
**inferred** with the exact source/story anchor. This is not confirmed intent.
If missing or ambiguous, block the pertinent outcome/coverage claim and request
only the consequential clarification; do not rewrite history, retrofit every
old AC or block unrelated established delivery evidence. New/changed scopes
require honest goal coverage (mapped AC/validation plus explicit outcome gaps),
not proof of an unobserved outcome before engineering delivery can complete.

Changes to intent, selected means or parent contract trigger bounded replanning:
identify affected goals/ACs/dependencies, retain unaffected IDs/evidence, and
invalidate affected evidence. Use the authorized CR and human-intent boundary
for scope/acceptance changes; no autonomous scope expansion or new approval loop.

## Downstream adoption (not a live migration claim)

| Domain | Goal/evidence use in its existing artifact |
| --- | --- |
| Design / implementation | Explain chosen means against parent/subgoal and constraints; link source/story/AC to planned then actual checks; rejected alternatives are not backlog mandates. |
| Acceptance / closing | Verify leaf AC evidence at current revision; report engineering delivery separately from observed stakeholder outcome and unmeasured gaps. |
| CR | Record goal delta and parent link; invalidate affected prior design/test/outcome evidence, preserve unrelated history; replan only authorized scope. |
| Bug | Restore documented expected behavior, linking failing scenario and regression evidence to existing goal/AC; no invented new product goal. |
| Quality / refactor | An internal goal such as same behavior with fewer duplicated decisions needs an inspected baseline, defined affected scope, preservation tests and after comparison; no fabricated percentage improvement or stakeholder gain. |

The lifecycle link is available to children; only an explicitly adopting child's
domain gate makes this coverage mandatory. Existing downstream skills are not
declared migrated by this reference or by workflow candidate validation.
