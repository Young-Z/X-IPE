# Quality reporting examples — authored scenarios, not observations

## 1. First-time evaluation: delivery and outcome separated

```yaml
input:
  operation: "generate"
  scope:
    type: "all"
```

For an approved saved-preferences feature, report the following document-local
mapping after inspecting its real sources. This example is an authored fixture;
it contains no actual test execution, score or stakeholder observation.

| Goal / Subgoal | Parent / Source | Stakeholder / Outcome | Contribution / Selection | Constraints / Non-goals | Story / AC / Type | Success Evidence | Delivery / Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| US-005-01 | FR-005-01; approved account preferences scope | account owner; saved preferences survive reload | all-required save and reload; selected existing persistence means, no extra alternative implementation | no coworker sharing; preserve authorization | AC-005-01; GIVEN saved preferences WHEN account owner reloads THEN saved values remain; UI | planned account-owner reload scenario; no observation supplied | delivery not verified in this authored fixture; outcome not measured |

An actual current UI reload pass with command/results/date/revision and hashes
can support verified engineering delivery, while the outcome remains not measured
without a real observation. Inspect each original rubric dimension before numeric
scoring; no overall_score or healthy claim is emitted from this authored example.

## 2. Post-refactoring evaluation and compare

```yaml
input:
  operation: "generate"
  scope:
    type: "feature_ids"
    filter: ["FEATURE-001", "FEATURE-003"]
```

An internal enabling goal may be "same approved pricing behavior with fewer
duplicated rule decisions," linked to the parent's consistent quotation outcome.
Record the inspected base/target source, unchanged preservation assertions and
actual before/after inspection. Do not invent a percentage improvement or claim
customers benefit from a fixture. Compare prior/current reports only where rubric,
scope and denominators match; otherwise explain incomparable numeric evidence.
Retain unrelated features' original evidence date/revision rather than refreshing
their claims merely because a new report was generated.

Original integration recommendation, owned by the caller:
baseline quality report → refactoring analysis → quality sync → midpoint quality
report → code refactor → final quality report + compare. This skill performs none
of those successors, task/Git operations or releases automatically.

## 3. Missing evidence: no schema change or synthetic score

A backend test invocation cannot run because the configured interpreter is
unavailable, while source inspection found test files. This is unavailable evidence,
not no_tests, failed execution, zero coverage or score ten. An executed failing AC
is instead failed engineering evidence and remains a distinct high-priority gap.

```yaml
operation_output:
  success: false
  operation: generate
  result: {}
  errors:
    - "EVALUATION_INCOMPLETE: current scoped test execution unavailable; numeric aggregate unsupported"
```

No null overall_score, healthy status, new goal schema key, fabricated observation
or planned label is added. The narrative may retain legitimate unrelated inspected
evidence and a proposed observation owner/scenario; it must not imply completion.

## 4. Legacy and actual bug boundaries

Explicit story "so that saved preferences persist" can support an inferred goal
with its exact story source. Mark inferred, not confirmed. If no such intent is
present, block that pertinent outcome claim while retaining established delivery
evidence. If code and docs both allow another user's preferences despite approved
authorization constraints, report deviation/bug, not descriptive drift to fix by
rewriting the requirement. Acceptance changes require the existing CR authority.

## 5. Observed outcome requires real evidence

An observation source must identify privacy-safe stakeholder context, approved
scenario, relevant revision/date and actual result. A quality report may say
observed stakeholder outcome only after inspecting that source. This example
supplies no observation and therefore makes no such claim. A DAO confirmation,
simulated browser interaction, passed API route test or improved score cannot
replace the observation. All-required versus selected alternative contribution
and unrelated unmet outcome gaps remain explicit.