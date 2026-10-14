# TASK-6749 — goal-orientation candidate evaluation

Date: 2026-10-13. State: **all four candidates ready for main independent review;
no promotion**. This is a scoped contract/artifact assessment, not a project-wide
quality score or proof of autonomous behavior. No speculative Explore percentages
or previous downstream maturity claims were used.

## Scope and preservation

Implemented sequentially, validating each before proceeding:

| Candidate | Package files | SKILL body lines | Added / changed / removed vs fresh production | Validator |
| --- | ---: | ---: | --- | --- |
| [Workflow](x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/candidate/SKILL.md) | 6 | 250 | 1 / 3 / 0 | pass; no warnings |
| [Requirements](x-ipe-docs/skill-meta/x-ipe-task-based-requirement-gathering/candidate/SKILL.md) | 6 | 253 | 0 / 5 / 0 | pass; 2 placeholder-link warnings |
| [Breakdown](x-ipe-docs/skill-meta/x-ipe-task-based-feature-breakdown/candidate/SKILL.md) | 8 | 245 | 0 / 6 / 0 | pass; no warnings |
| [Refinement](x-ipe-docs/skill-meta/x-ipe-task-based-feature-refinement/candidate/SKILL.md) | 5 | 228 | 1 / 4 / 0 | pass; 3 placeholder-link warnings |

Total: 25 package files / 976 entry-body lines. The refinement integration addition
was already in its prior unpromoted candidate; the goal delta adds no refinement
resource and preserves that integration file byte-for-byte. The other three
prework candidates matched their already-promoted production bundles. Fresh
production inventories are separate from historical pre-promotion baselines.
All four current production manifests remain unchanged. No version history is
updated as though this delta were published.

Only candidate packages, their approved metadata, two test files and this report
were edited using patches. No board, memory, Git, app/config, actual EPIC source
or unrelated dirty-document edits. Existing required domain sections, field/key
order, action tags, output schemas, status/identity rules and safety/approval
gates remain; original domain tests continue to exercise them.

## Direct source evidence — sampled, not a census

| Inspected source | Direct finding | Bounded interpretation |
| --- | --- | --- |
| [FEATURE-047-A stories](x-ipe-docs/requirements/EPIC-047/FEATURE-047-A/specification.md#L33-L40) | US-1 explicitly says standard workflow instead of ad hoc conventions; US-2 says bounded guidance without downstream scope change. | Legacy outcome intent can be inferred from explicit so-that text with exact source/ID, not declared confirmed or achieved. |
| [FEATURE-047-A criterion](x-ipe-docs/requirements/EPIC-047/FEATURE-047-A/specification.md#L44-L49) | AC-047-A.1 checks selectable skill-type support, in historical checkbox form rather than GWT. | This is an enabling delivery criterion, not evidence that stakeholders used the workflow; preserve historical prose/IDs rather than retrofit all legacy ACs. |
| [FEATURE-059-C stories](x-ipe-docs/requirements/EPIC-059/FEATURE-059-C/specification.md#L40-L54) | Constructor knowledge requests, evaluation rubric and mimic behavior capture have explicit stakeholder benefits. | Layer/domain organization is not itself an outcome chain. Internal enabling subgoals need credible links to these stated benefits. |
| [FEATURE-059-C GWT ACs](x-ipe-docs/requirements/EPIC-059/FEATURE-059-C/specification.md#L83-L93) | AC-059C-03e/04d/04e define subpage requests, manifest and per-feature/workflow output. | These define observable engineering output; the inspected text is not a stakeholder-use observation. |
| [CR-003 delta and non-goals](x-ipe-docs/requirements/EPIC-059/FEATURE-059-C/CR-003.md#L39-L54) | Stable affected AC IDs are named; not every section must become a folder; keeper promotion/new extractors excluded. | Good bounded delta source for parent-goal/affected-evidence mapping, not authority to implement every alternative or expand scope. |
| [CR-003 recorded actions](x-ipe-docs/requirements/EPIC-059/FEATURE-059-C/CR-003.md#L57-L64) | Document records specification/design/candidate updates. | Historical checkmarks are document claims, not fresh validation or observed stakeholder outcome receipts for this task. |

Samples were read-only. Their SHA256s, test sources, validator and inspected
downstream entries are recorded in [evidence](x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/evidence-goal-TASK-6749.json).

## Current downstream contracts — not fully goal-driven

Directly inspected current source clauses, not assumed from previous analysis:

| Domain | Existing contract evidence | Gap / adoption boundary |
| --- | --- | --- |
| [Design](.github/skills/x-ipe-task-based-technical-design/SKILL.md#L201-L231) | Reads stories/ACs, rules, edge cases and dependencies. | No demonstrated end-to-end stakeholder outcome observation from these clauses; goal means-choice mapping is proposed adoption, not a migrated consumer. |
| [Implementation](.github/skills/x-ipe-task-based-code-implementation/SKILL.md#L286-L329) | Routes AAA scenarios to tools; aggregates Assert/lint/integration results. | Engineering checks do not establish a stakeholder outcome; existing configuration routing is unchanged here. |
| [Acceptance](.github/skills/x-ipe-task-based-feature-acceptance-test/SKILL.md#L321-L334) | Structured review maps every AC to results and cited evidence. | Artifact review/keyword/structure checks are useful delivery evidence, not autonomous behavior or stakeholder observation. |
| [Closing](.github/skills/x-ipe-task-based-feature-closing/SKILL.md#L205-L226) | Checks each criterion and blocks unresolved criteria; produces verification table. | Preserve this gate; separate delivery and outcome gaps when this domain explicitly adopts the contract. |
| [CR](.github/skills/x-ipe-task-based-change-request/SKILL.md#L186-L218) | Challenges need/alternatives, confirms scope and reads affected stories/ACs. | Parent-goal delta/evidence invalidation guidance is in the shared candidate reference; no live CR migration claimed. |
| [Bug](.github/skills/x-ipe-task-based-bug-fix/SKILL.md#L115-L139) | Reproduction, diagnosis, conflicts, failing test, minimal fix and passing regression gates. | Use existing expected behavior/goal for restoration, not invented product scope; live bug skill untouched. |
| [Refactor](.github/skills/x-ipe-task-based-code-refactor/SKILL.md#L306-L339) | Validates goals from refactoring suggestion, final tests, before/after quality scores. | Existing goal language is not proof of observed improvement. Internal same-behavior/fewer-duplication goals require inspected baseline and after comparison. |
| [Quality](.github/skills/x-ipe+feature+quality-board-management/SKILL.md#L28-L39) | Scores requirement/spec/test/code/tracing/security dimensions. | Score model is not observed stakeholder outcome evidence; this task does not recalculate quality scores or declare gains. |

Assessment: the inspected system has intent, scope, acceptance and delivery-evidence
contracts, and some explicit refactoring goals. **It is not demonstrated to be a
fully goal-driven pipeline.** This four-candidate slice establishes consistent
upstream goal semantics and downstream adoption guidance, not the entire migrated
design-to-closing/CR/bug/quality pipeline.

## Implemented goal semantics

The [shared reference](x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/candidate/references/goal-contract.md)
defines stakeholder desired observable outcome, source/parent stable IDs,
credible direct/indirect contribution, success measure if known or qualitative
scenario, constraints/non-goals, and all-required versus selected/bounded
alternatives. Existing FR/US/AC IDs suffice; optional doc-local G anchors are not
persisted. No new goal database, mandatory graph, approval ritual or schema/tag.

- Requirements embed an outcome frame and requirement-ID mapping in their existing
  canonical summary. The compatible template entry delegates to that same form.
- Breakdown details link feature deliverables to subgoal/parent requirement; the
  six-column list is unchanged. Layer/file signals remain sizing context, not
  automatic per-layer feature splits. Unselected alternatives are not board edges.
- Refinement embeds goal/subgoal/story/AC/validation/outcome-gap mapping in the
  complete specification. New/changed leaf ACs remain GWT with original primary
  test types. Qualitative scenarios are valid; no forced numbers or goal-count caps.
- Legacy inference requires explicit story so-that and an inferred/source label.
  Ambiguity blocks only the pertinent claim, not historical rewrites or unrelated
  engineering evidence. Authorized parent deltas invalidate affected evidence.
- Delivery and outcome states are separate: planned checks are not verified
  engineering delivery; verified delivery can coexist with outcome **not measured**.
  **Observed stakeholder outcome** needs actual sourced observation, not fixtures,
  review, guidance or invented confirmation. Means adapt within approved contracts;
  scope/acceptance changes follow bounded CR/human intent.

## Verification and limits

Before edits: existing pipeline suite **111 passed**. Final expanded command in
the evidence record: **303 passed, 0 failed** (18 goal-artifact tests, 113 pipeline
tests, 27 lifecycle tests, 145 creator-foundation tests). Editor diagnostics report
no errors in either changed test file. All four installed validators pass.

The five warnings concern retained placeholder links in authoring scaffolds;
they are not missing concrete deliverables. No validator ceiling/domain gate is
waived. Newly introduced Markdown title/list spacing alerts were corrected and
affected receipts refreshed. Existing scaffold formatting alerts and editor
diagnostics that resolve project-root links relative to the candidate directory
or expect the canonical skill name to equal `candidate` remain; the installed
validator resolves the approved root/candidate mapping and passes. These editor
alerts are not silently treated as proof of broken or working runtime behavior.
One intermediate failure detected an old promotion assertion incorrectly
comparing already-published production to a newly edited candidate. The test now
checks the historical receipt/fingerprint, fresh production baseline and retained
scaffold sections separately; it does not discard publication/domain checks.

[Goal tests](tests/test_goal_oriented_skills.py) parse actual authored new/legacy/
delta examples, source-parent-subgoal-AC-evidence chains and selected alternatives;
render existing scaffolds into a temporary artifact; compare exact historical
source lines and unchanged delta AC; reject orphan/missing/duplicate/non-GWT and
unsupported delivery/outcome claims. [Pipeline tests](tests/test_skill_pipeline_refactor.py)
retain helper/domain checks and add new scaffold sections without schema changes.
These prove artifact expressiveness and assertions, not autonomous authoring,
judgment, confirmation, replanning or stakeholder outcomes. No such pilot ran.

## Hypotheses and next boundary

Hypotheses, not measured gains: source-to-goal mapping may expose misaligned
deliverables earlier; bounded alternatives may prevent overbuilding; explicit
evidence states may prevent false outcome closure. Testing those requires
separately authorized representative task executions, independent artifact review
and actual stakeholder observations. No efficiency, duplication, quality or
business-impact percentages are asserted.

Fresh metadata/receipts use the separate goal-TASK-6749 suffix; prior promotion
records remain historical. Main independent review is still pending, and no
publication was attempted. Child references deliberately point to the staged
shared contract while production lacks it. Any later release must reconcile
those links to the reviewed canonical shared reference, revalidate affected
candidate/dependency hashes/tests, and obtain explicit publication authority.
Downstream domains require their own reviewed adoption; this report does not
authorize continuing those migrations or marking TASK-6749 complete on the board.
