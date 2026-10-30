# Skill Meta: x-ipe-tool-implementation-typescript

```yaml
skill_name: x-ipe-tool-implementation-typescript
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

- Current revision: `3ad2157ec732823a82d6562228b18e69f124dfc69166acdf62b54d38454bf8b6`
- Previous revision: `1a97aa59e6ad333ce4340fdddfa77c528284a54c61b6bcf0ade5781e4938b686`
- Evidence: `lean-delivery-TASK-6752.json`, `publication-receipt-TASK-6752.json`, `validation-receipt-TASK-6752.json`.
- Verification: 599 selected checks passed; exact installed/candidate byte parity. No resource removals, mirror synchronization or Git mutation.
- Live-agent efficacy, token/latency savings and stakeholder outcome remain unmeasured.
