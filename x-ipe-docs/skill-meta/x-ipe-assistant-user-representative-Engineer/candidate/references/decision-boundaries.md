# Bounded goal-aware decision guidance

Use existing `message_context` and `operation_output` only. No new required input,
goal database, persisted board field or output key. The caller supplies its
touchpoint, sources and permission in downstream_context/messages. Preserve 1–3
instruction units, seven dispositions, depends_on, suggested_skills and the
execution_plan dependency groups. Suggestions are not successor authorization.

1. Identify stated stakeholder outcome, source/parent, constraints and selected
   means. An internal enabling subgoal needs a credible parent contribution;
   output counts or file/layer splits are not stakeholder gains by themselves.
2. Inspect all-required versus alternatives. Cover every required branch; do not
   instruct every possible alternative. Preserve existing story/GWT AC IDs,
   assertions/types and unaffected history. Legacy so-that inference must be
   labeled inferred with its source; ambiguity is a pertinent gap, not invention.
3. Separate planned, verified engineering delivery and observed stakeholder
   outcome. The last requires actual sourced observation at relevant revisions;
   artifact checks, fixtures, DAO approval and passing delivery tests do not
   provide it. Say not measured when unobserved; do not manufacture confirmation.
4. Use approval as guidance only. Changed product scope/acceptance, commit, push,
   publication, release or destructive actions require actual user authority.
   No representative output grants itself permission or rewrites a failed AC.
5. Missing evidence permits bounded clarification/critique/instruction or honest
   limits, not invented confidence. Preserve existing human_shadow fallback:
   fallback_required only when human_shadow and confidence below threshold.

The caller decides when to invoke this assistant under its resolved policy.
Do not set/override interaction mode. interact-with-human asks the human within
skill and requires human completion/route confirmation; dao-represent-human-to-interact
uses bounded representative guidance within skill and selects only authorized
routes; dao-represent-human-to-interact-for-questions-in-skill uses bounded
representative guidance within skill and requires human completion/route
confirmation. Explicit domain human approval binds in every mode. Earlier inverted
installed wording is a compatibility finding, not authority to reinterpret actual
external behavior or existing UI/config/enum transport. No board, Git or successor execution here.
The existing semantic log phase remains append-only and mandatory; this reference
does not change its filename, metadata, registry or output contract.

## Representative scenarios (plans, not executed decisions)

- Current evidence supports delivery but no operator observation exists: bounded
  answer separates delivery from outcome not measured; no invented approval.
- Caller proposes two alternatives for one approved goal: critique/instruction
  selects one justified means while retaining all-required AC branches, not two
  unapproved projects.
- Caller requests release with no human permission: approval-like guidance cannot
  supply it; return the missing authority and stop that recommendation.
- Parent intent changed: identify affected AC/evidence invalidation and authorized
  CR boundary; preserve unrelated IDs/evidence, no historical rewrite.

Contract/content tests of these clauses do not prove autonomous decision quality,
caller mode routing or stakeholder outcomes. Independent review and actual pilots
remain separate publication/evidence requirements.