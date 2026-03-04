# Decision Quality Guidelines

> Reference for AI agents using x-ipe-tool-decision-making.
> Helps agents evaluate decision quality and determine when to mark UNRESOLVED.

## Good Decision Indicators

A well-made autonomous decision should exhibit:

1. **Clear rationale** — The "why" is specific and traceable to project artifacts (requirements, specs, code)
2. **Alternatives considered** — At least 2 options were evaluated before choosing
3. **Critique addressed** — Sub-agent feedback was incorporated or explicitly acknowledged
4. **Consistent with patterns** — Decision aligns with existing project conventions and architecture
5. **Minimal blast radius** — Chosen option affects the fewest other components
6. **Reversible** — Prefer decisions that can be undone later if needed

## Bad Decision Indicators

Flags that a decision may be low quality:

1. **No rationale** — "Just picked option A" without explanation
2. **Ignores critique** — Sub-agent raised valid concerns that were not addressed
3. **Contradicts requirements** — Decision conflicts with documented FRs or ACs
4. **Breaks existing patterns** — Introduces inconsistency without justification
5. **High-risk irreversible** — Architectural or security decision made without confidence

## When to Mark UNRESOLVED

Mark a problem as UNRESOLVED when ANY of these apply:

1. **Conflicting hard constraints** — Two requirements directly contradict and neither can be relaxed
2. **Insufficient context** — Not enough information in project docs or web to make a confident choice
3. **Security or compliance implications** — Decision affects authentication, authorization, data privacy, or regulatory compliance
4. **Irreversible architectural choice** — Choosing a database, framework, or protocol that's costly to change
5. **Human-value judgment required** — The decision involves user experience preferences, business priorities, or ethical considerations
6. **Equal alternatives** — Two or more options are genuinely equivalent with no distinguishing factor

## Routing Decision Heuristics

When resolving `type: routing` problems (choosing next task/feature):

1. **No-dependency first** — Prefer features with no unresolved dependencies
2. **MVP priority** — Prefer features marked as MVP or P0
3. **Unblock the most** — Prefer features that are dependencies for the most downstream features
4. **Sequential before parallel** — Complete the current dependency chain before starting new ones
5. **Smallest scope first** — When tied, prefer the feature with fewer ACs (faster completion)

## Conflict Resolution Heuristics

When resolving `type: conflict` problems:

1. **Specification over assumption** — If the spec says X but code assumes Y, trust the spec
2. **Later document wins** — If two docs conflict, the more recently updated one takes precedence
3. **Stricter constraint wins** — When in doubt, choose the more restrictive option (easier to relax later)
4. **Ask the test** — If a test exists that validates one interpretation, that interpretation is correct
