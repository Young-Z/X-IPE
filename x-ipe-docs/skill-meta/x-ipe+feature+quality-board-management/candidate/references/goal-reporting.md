# Goal reporting in the original quality artifact

Use the existing report Key Findings, per-feature Details, Recommendations and
Appendix. No new persistent goal graph, board field, action tag, quality dimension,
output key or data-model property. A short document-local table or equivalent
prose is sufficient; do not force a fixed goal count or arbitrary success metric.

## Source and contribution mapping

For each pertinent new/changed goal or subgoal record:

| Element | Required evidence and boundary |
| --- | --- |
| Goal / subgoal | Existing stable source/story identifier or justified document-local anchor; retain IDs and old-to-new mapping on authorized changes |
| Parent / source | Exact approved intent and parent link, not implementation-derived acceptance |
| Stakeholder / outcome | Who benefits and what observable change is intended; no fabricated confirmation |
| Contribution / selection | How deliverable enables the parent; all-required children versus alternatives, selected means and rationale; rejected alternatives are not mandatory backlog |
| Constraints / non-goals | Original behavior/security/scope limitations; a report cannot expand them |
| Story / AC / type | Stable leaf Given/When/Then criteria, source anchors and domain test types; don't replace UI/API/CLI checks with a document pass |
| Success evidence | Justified actual measure or concrete qualitative scenario; planned collection is not observed success |
| Delivery / outcome | Separate revision-bound engineering checks from real stakeholder/context observations and unmeasured gaps |

Trace approved goal → story/leaf AC → requirement/specification/design → source
and current test/validation evidence. Evaluate the six original dimensions against
this chain, not merely whether docs match code. Report orphan/missing/ambiguous
links as pertinent gaps without rewriting source acceptance. Internal enabling
goals are valid with an inspected baseline, credible parent contribution and
preservation comparison; no invented stakeholder gain or percent improvement.

## Evidence states and freshness

- **not measured:** relevant stakeholder observation absent. Record a proposed
  scenario/owner or unavailable evidence; it is neither failed nor achieved.
- **verified engineering delivery:** current artifact/AC checks support delivery
  at the exact inspected revision. Cite actual commands, results, date and
  source/test/doc/config hashes, failure/skips and limits. A checklist or test plan
  alone does not support this state.
- **observed stakeholder outcome:** actual contextual observation matches the
  approved outcome scenario at the relevant revision. Cite source, stakeholder
  context, conditions and result with privacy-safe details and limitations.

Both delivery and outcome remain explicit. A fixture, passing service test,
approval, DAO answer, scored report or simulated user is not a stakeholder
observation. Unavailable execution differs from a failed actual check; preserve
both rather than replacing them with synthetic score/coverage/progress.

Numeric rubric evaluation remains independent of these narrative states. Numeric
success requires actual evaluated eligible dimensions/features and denominator.
Keep original weights/fields/statuses and full suggestion structure. Missing
evidence does not justify zero, ten, null, exclusion-and-renormalization or a new
status enum. Return success=false with existing errors and result={} when the
original numeric result cannot be supported. An authorized narrative draft may
show N/A with a reason, never a misleading healthy/current completed report.

## Legacy, delta and recommendation authority

Reuse explicit legacy story so-that intent with an exact source anchor, labeled
**inferred**, not confirmed. Missing/ambiguous intent blocks only the pertinent
outcome/goal-coverage claim; preserve unrelated established engineering evidence
and do not retrofit all old ACs. Clear inputs need no human formatting ritual.

For updates/compare, identify affected goal/AC/dependency and revision, invalidate
only affected evidence, retain unaffected IDs and original dates. Changed rubric,
scope or denominator prevents an unexplained numeric improvement comparison.
Separate genuine descriptive doc drift, broken approved behavior, unimplemented
intent and proposed scope/acceptance changes. Recommend authorized doc sync,
bug-fix or CR routes accordingly; do not execute them or launder acceptance.

## Existing contracts and report service boundary

The original operation_output and QualityEvaluation model remain unchanged,
including report_path/version/overall_score/health_status/features_evaluated/gaps,
priority_gaps and every refactoring_suggestions source/goals/target_structure/
principles/applications/constraints field. Query/compare retain their historical
operation-specific result meanings; do not invent mandatory projection schemas.

The actual application routes serve Markdown and report-version metadata; they do
not validate goal semantics, compute rubric scores, verify stakeholder outcomes,
rotate saved files or execute this skill. Route/frontend tests prove their bounded
serving behavior only. Structural skill checks and authored examples likewise do
not prove an autonomous quality evaluation. Report those limits honestly.