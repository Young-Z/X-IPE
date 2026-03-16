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
updated: 2026-03-16

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
