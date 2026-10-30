# Single-loop authoring policy

Source: [Building agents: When to fold subagents into your main agent loop](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop).
This is an authoring policy, not measured evidence of token or latency savings.

## Default execution

Use one model/context open-ended loop. Keep sequential planning, domain reasoning,
drafting, verification, and revision in shared context. A skill supplies a procedure;
invoking a tool skill in the same loop does not spawn an agent. Load only the
selected subtype templates and relevant references/tools when needed, not every
skill or historical lesson. Preserve each subtype's input/output and interaction
contracts. Existing packages are update scaffolds, not wholesale rewrite targets.

## Bounded delegation

Delegate only when at least one concrete reason is recorded:
- Measurable context degradation, such as repeated lost constraints or retrieval
  failures; skill length or task complexity alone does not establish degradation.
- Substantial independent parallel work whose fresh working context is discardable,
  with no shared writes or sequential dependency on the main reasoning trace.
- Conflicting instructions, observed tool-selection trouble, or a genuine permission
  isolation boundary. A separate context alone does not enforce permissions.

Give the worker a bounded objective, minimal inputs, owned paths, expected output,
and stopping condition. Keep routing and synthesis in the main loop. Do not assign
one agent per step, skill, domain, or DoD checkpoint; do not prescribe model names,
premium tiers, or a mandatory decomposition/scheduling block in templates.

## Proportional verification and review

Use deterministic checks and same-loop self-review by default, including ordinary
workflow, executable, and public-contract edits. Artifact type alone never requires
a fresh reviewer. Require independent review when a concrete security/trust/permission
or destructive change, explicit user review request, or meaningful ambiguity/observed
failure cannot be resolved by same-loop evidence. Scope that review to the actual
risk; if required review is unavailable, report the promotion blocker honestly.
Do not add mandatory judge rounds, score thresholds, coverage percentages, or
reviewer counts. Preserve actual user approvals in all three interaction modes;
representative guidance cannot invent release authorization.

Run the smallest checks covering changed behavior and affected consumers; reuse
valid revision-bound evidence, rerunning only checks invalidated by changed inputs.
Escalate validation scope for observed regressions or real risk, not every handoff.
Keep candidate staging, deterministic validation, path/ownership/concurrency checks,
explicit deletions, safe publication/recovery, and byte parity. Tools enforce hard
permissions and data contracts; prose procedures are not a security boundary.

## End-to-end evaluation

Maintain a compact set of about 10 golden outcome scenarios for material workflow
changes: representative happy paths, failures, safety boundaries, and all interaction
modes. Compare old/new outcomes, transitions, and preserved rules rather than counting
agents or grading every step. Reuse scenarios across skills instead of multiplying
gates. Static contract tests and hypothetical examples do not establish live-agent
behavior, user outcomes, or performance savings. Report what actually ran and leave
unmeasured token/latency and live-agent outcomes explicitly unmeasured.
