# Single-loop delivery policy

Source: [Building agents: When to fold subagents into your main agent loop](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop).

## One owner, shared context

The same agent owns the authorized delivery goal, plan, domain reasoning,
implementation and verification. Invoke another **skill** in that same loop:
loading expertise does not mean spawning a subagent. Preserve what was learned
from ideation through closing rather than replacing it with specialist summaries.
Only the lifecycle owner registers/resumes tasks, records completion and resolves
the next-task boundary. A child returns artifacts and evidence to that owner.

Discover short descriptions first. Load only the selected skill, needed resource
sections and tools needed for the current decision. Enabled means permitted, not
mandatory to load or execute. Prefer parallel independent tool calls over agents.
Do not repeatedly reload an unchanged shared policy in the same context.

Keep the plan in context and revise it when evidence changes. A small feature can
combine intent, scope, acceptance and design in sections of one existing artifact;
preserve required app action tags and link the appropriate real deliverable.
Do not create a planning document, role, task or fresh context for each thought.
The user may authorize an end-to-end scope once; follow existing interaction modes
and explicit approval boundaries without manufacturing extra confirmation gates.

## When a subagent pays for itself

Default: no subagent. Record the concrete benefit before delegating:

- Measurable context degradation that selective loading cannot resolve.
- Substantial independent work with little shared context, such as parallel
  research or separate components with stable interfaces.
- Conflicting instructions/tool-selection problems, or a genuine permission
  boundary requiring isolated tools and authority.
- A bounded independent verification explicitly requested or warranted by a
  concrete high-risk uncertainty (trust/auth boundaries, destructive migration,
  safety effects, repeated unexplained failures), not simply a changed file.

Provide a bounded objective, minimal complete inputs, exact permitted paths,
expected evidence and a stop condition. Return compact findings/artifacts, not
the whole transcript. Do not split sequential design/build/test work or assign a
mandatory critic, judge or DoD checker to each skill. Never use a reviewer to
grant missing human authority. Reuse an existing suitable independent review.

## Proportional verification

One verification plan covers the current authorized goal. Reuse current evidence
through implementation, acceptance and closing when assertions, relevant inputs
and environment remain unchanged. Record commands, exits, scope and relevant
revisions in existing test/design/task artifacts; no new receipt file per thought.

- Small bounded change: self-check the affected acceptance and run the smallest
  relevant tests/lint/build. Documentation-only work needs link/content checks,
  not application builds or a new reviewer.
- Cross-boundary or uncertain change: add the affected integration/regression
  checks; broaden only when coupling, a failure, or an explicit policy requires it.
- Concrete high-risk change: retain required human approvals and targeted
  independent review. Missing required evidence blocks only the affected claim.

No universal coverage percentage, quality score, visual-match score, iteration
quota, full-suite rerun or automatic code refactoring. An explicit project policy
or acceptance requirement still binds. Never weaken assertions, change expected
behavior, hide failures or mark unexecuted tests passed to reduce work.
Unchanged acceptance can consume implementation evidence without executing the
same checks again; changed code/config/criteria/environment invalidates affected
evidence. UI claims require actual browser evidence, not source-only inspection.

Closing verifies the final result and reuses checks; it does not start another
quality pipeline. Refactor only for a concrete evidenced need or explicit request.
Leave optional action state untouched; the service may initialize it as skipped,
while existing pending/in-progress/history stays intact. Do not write fake
skipped/done records or refactor reports. Honor actual project-specific mandatory actions.

Path containment, task ownership, configured tool permissions, state/schema
integrity and explicit commit/push/publication authority are essential controls,
not optional quality ceremony. Tools enforce mechanical constraints; a passing
tool receipt cannot manufacture consent or semantic correctness.

## Ten migration scenarios

These are shared end-to-end evaluation scenarios, not claims of live-agent
execution. Contract tests and temporary workflow tests cover the mechanical
parts; real agent traces are needed to measure behavior, cost and latency.

| Scenario | Expected completion behavior |
| --- | --- |
| Small feature | Same agent carries idea, ACs, design and code; no role-per-step chain. |
| Independent research | Optional bounded parallel context; compact cited results return to owner. |
| Context degradation | Selective loading first; delegate only with a documented actual limitation. |
| Permission boundary | Isolate authority if needed; no tools or subagents bypass user consent. |
| Clear requirements | Reuse approved answers; no ceremonial questions or DAO routing calls. |
| Changed acceptance | Refresh affected checks and dependent design/evidence without weakening assertions. |
| Unchanged acceptance | Reuse suitable passing implementation evidence through acceptance and closing. |
| Low-risk documentation | Direct self-check/content/link validation; no forced reviewer/build/coverage. |
| High-risk change | Targeted safety/regression checks and justified independent review/approval remain. |
| No refactoring need | Acceptance routes to closing; optional refactor remains untouched. |

Compare baseline and candidate traces for each applicable scenario, including
forbidden actions and a repeated trial where routing is nondeterministic. Capture
actual tool/skill selections, handoffs, outcome correctness and any measured
tokens/latency. Until those traces exist, cost and latency gains are **not measured**.
