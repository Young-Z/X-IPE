# Skill Meta: x-ipe-tool-implementation-java

```yaml
skill_name: x-ipe-tool-implementation-java
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
summary: Preserve implementation/fix/refactor contracts with proportional regression verification.
inputs:
  required: [operation, aaa_scenarios, source_code_path, test_code_path]
  optional: [feature_context]
outputs:
  state: [success]
  data: [operation_output]
acceptance_criteria:
  must:
    - id: AC-LEAN-01
      criterion: Same-loop execution with unchanged operation inputs and outputs.
    - id: AC-LEAN-02
      criterion: Fix retains actual behavioral failure before minimal fix and unchanged test passing afterward.
    - id: AC-LEAN-03
      criterion: Refactor verifies the same affected preservation selection before and after.
    - id: AC-LEAN-04
      criterion: Broaden regression scope for coupling, failures or binding policy, not every handoff.
    - id: AC-LEAN-05
      criterion: No automatic Git checkpoints, hidden failures or claims that unrun suites passed.
independent_review: required for this batch's instruction compatibility review
```

Baseline and managed provenance: clean tracked HEAD bytes captured by TASK-6752;
the exact manifest is retained alongside the publication receipt after promotion.
No application behavior or language-tool execution is claimed by static checks.

## TASK-6752 proportional-delivery revision

Published through the installed manifest-safe publisher after bounded compatibility review, correction of its TypeScript test-path finding, deterministic validation and affected post-publication regressions. Prior metadata remains historical.

- Current revision: `333ab2554f39b7e969915f29c3cfd7d7c4d75be23619e9608a06420f157880a8`
- Previous revision: `bfd0ebd487dd87f3b983f2df138d44053c331044b9256a51f5d032e4095e1338`
- Evidence: `lean-delivery-TASK-6752.json`, `publication-receipt-TASK-6752.json`, `validation-receipt-TASK-6752.json`.
- Verification: 599 selected checks passed; exact installed/candidate byte parity. No resource removals, mirror synchronization or Git mutation.
- Live-agent efficacy, token/latency savings and stakeholder outcome remain unmeasured.
