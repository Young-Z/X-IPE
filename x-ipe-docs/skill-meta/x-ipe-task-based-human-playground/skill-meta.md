# Skill Meta: x-ipe-task-based-human-playground

```yaml
# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based
# ═══════════════════════════════════════════════════════════

skill_name: x-ipe-task-based-human-playground
skill_type: x-ipe-task-based
version: "1.1.0"
status: candidate
created: 2026-03-10
updated: 2026-03-30

summary: |
  Create interactive playground examples for human validation — human-initiated only,
  not auto-suggested by the engineering pipeline.

triggers:
  - "create playground"
  - "human testing"
  - "interactive demo"
  - "I want to test this"

not_for:
  - "x-ipe-task-based-feature-acceptance-test: for automated acceptance testing"
  - "x-ipe-task-based-feature-closing: for closing features (standard pipeline end)"

workflow:
  category: standalone
  phase: "Human Playground"
  next_task_based_skill: "x-ipe-task-based-feature-closing"
  human_review: false

inputs:
  required:
    - name: interaction_mode
      type: string
      default: "interact-with-human"
      description: "Interaction mode"
    - name: feature_id
      type: string
      default: null
      description: "Feature ID to create playground for"
      validation: "must match FEATURE-\\d+"

outputs:
  state:
    - name: category
      value: "standalone"
    - name: status
      value: completed | blocked
    - name: next_task_based_skill
      value: "x-ipe-task-based-feature-closing"
    - name: require_human_review
      value: false
    - name: interaction_mode
      value: "${inputs.interaction_mode}"
  artifacts:
    - name: playground_file
      type: file
      path: "playground/playground_{feature_name}.{ext}"
      description: "Runnable playground example"
    - name: playground_readme
      type: file
      path: "playground/README.md"
      description: "Usage instructions"

acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name and description fields present
    - id: AC-S02
      category: structure
      criterion: Description explicitly states human-initiated only
      test: content_check
      expected: description contains "Human-initiated only" or "HUMAN-INITIATED ONLY"
    - id: AC-S03
      category: content
      criterion: Important Notes contains human-initiated gate
      test: content_check
      expected: Important Notes section mentions "ONLY be invoked when the human explicitly requests"
    - id: AC-B01
      category: behavior
      criterion: Skill is NOT auto-suggested by engineering workflow
      test: content_check
      expected: engineering-workflow.md does not list human_playground in feature_closing Next Actions
  should:
    - id: AC-C01
      category: content
      criterion: Feature-closing description does not mention playground as prerequisite
      test: content_check
      expected: feature-closing description does not say "validated the playground"

test_scenarios:
  happy_path:
    - name: "Human requests playground"
      given: "Feature is implemented and tested"
      when: "Human says 'create playground for feature X'"
      then: "Skill is invoked, playground created"
  edge_cases:
    - name: "Pipeline does not auto-suggest"
      given: "Feature closing is complete"
      when: "Agent determines next action"
      then: "Human playground is NOT suggested as next step"
  blocking:
    - name: "No explicit request"
      given: "Feature is at feature_closing stage"
      when: "Agent considers next steps"
      then: "Human playground is NOT invoked"

evaluation:
  self_check:
    - "SKILL.md description contains 'Human-initiated only'"
    - "Important Notes has HUMAN-INITIATED ONLY gate"
    - "engineering-workflow.md updated"
    - "feature-closing description updated"
```

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `99300e005ef5e062929f20013a09e6f35a7c639e46bc581426c74d06070899e7`
- Previous revision: `e0b8ee27a9f4126a9136e8c9caef372c5b231456eed1e8fe2cb1ed270a1220cf`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.

## TASK-6752 proportional-delivery revision

Published through the installed manifest-safe publisher after bounded compatibility review, correction of its TypeScript test-path finding, deterministic validation and affected post-publication regressions. Prior metadata remains historical.

- Current revision: `635b419d7582d5a6875dd93421f8f3d17e806155875cb8a8ad6997c1e8ec6953`
- Previous revision: `99300e005ef5e062929f20013a09e6f35a7c639e46bc581426c74d06070899e7`
- Evidence: `lean-delivery-TASK-6752.json`, `publication-receipt-TASK-6752.json`, `validation-receipt-TASK-6752.json`.
- Verification: 599 selected checks passed; exact installed/candidate byte parity. No resource removals, mirror synchronization or Git mutation.
- Live-agent efficacy, token/latency savings and stakeholder outcome remain unmeasured.
