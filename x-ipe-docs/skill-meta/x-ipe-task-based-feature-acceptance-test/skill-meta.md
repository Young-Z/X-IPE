# Skill Meta: Feature Acceptance Test

```yaml
skill_name: x-ipe-task-based-feature-acceptance-test
skill_type: x-ipe-task-based
version: "2.0.0"
status: candidate
created: 2025-01-30
updated: 2026-03-11

summary: |
  Execute acceptance tests for ALL feature types by classifying acceptance criteria
  by test type (frontend-ui, backend-api, unit, integration) and routing each to
  the best available tool from tools.json config.

triggers:
  - "run acceptance tests"
  - "test feature"
  - "execute acceptance tests"
  - "acceptance testing"

not_for:
  - "x-ipe-task-based-code-implementation: writing feature code"
  - "x-ipe-task-based-human-playground: interactive manual testing"

workflow:
  category: feature-stage
  phase: "Acceptance Testing"
  next_task_based_skill: "Feature Closing"
  human_review: false

inputs:
  required:
    - name: feature_id
      type: string
      default: null
      description: "Feature identifier (FEATURE-XXX format)"
      validation: "must match FEATURE-\\d+-[A-Z]"

    - name: toolbox_meta_path
      type: string
      default: "x-ipe-docs/config/tools.json"
      description: "Path to tools configuration"

  optional:
    - name: target_url
      type: string
      default: null
      description: "URL for frontend-ui tests (resolved from feature config if not provided)"

outputs:
  state:
    - name: category
      value: "feature-stage"
    - name: status
      value: "completed | blocked"
    - name: next_task_based_skill
      value: "Feature Closing"

  artifacts:
    - name: acceptance-test-cases
      type: file
      path: "x-ipe-docs/requirements/FEATURE-XXX/acceptance-test-cases.md"
      description: "Test cases with execution results, grouped by test type"

  data:
    - name: test_types_tested
      type: array
      description: "List of test types that were tested"
    - name: results_by_type
      type: object
      description: "Pass/fail/blocked counts per test type"
    - name: pass_rate
      type: string
      description: "Overall pass rate percentage"

acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name and description fields present

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 1 example

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-C01
      category: content
      criterion: Frontmatter describes all test types, not just web UI
      test: content_check
      expected: description mentions "all feature types" or "frontend UI, backend API"

    - id: AC-C02
      category: content
      criterion: Step 1.1 loads tools.json config like ideation skill
      test: content_check
      expected: step reads stages.quality.testing from tools.json

    - id: AC-C03
      category: content
      criterion: Step 1.2 classifies ACs by test_type
      test: content_check
      expected: classification into frontend-ui, backend-api, unit, integration

    - id: AC-B01
      category: behavior
      criterion: Backend-only features are NOT skipped
      test: execution
      expected: all ACs get test cases regardless of type

    - id: AC-B02
      category: behavior
      criterion: chrome-devtools-mcp is configurable in tools.json
      test: content_check
      expected: tools.json stages.quality.testing contains chrome-devtools-mcp key

  should:
    - id: AC-C04
      category: content
      criterion: Results reported by test type
      test: content_check
      expected: results_by_type in output with per-type breakdown

    - id: AC-C05
      category: content
      criterion: Disabled tools cause blocked status per type, not skip
      test: content_check
      expected: blocked instead of skipped when tool disabled

    - id: AC-B03
      category: behavior
      criterion: Tool routing matches ideation pattern
      test: content_check
      expected: enabled_tools built from tools.json config with true/false check

  could:
    - id: AC-C06
      category: content
      criterion: Supports custom test runners beyond built-in tools
      test: content_check
      expected: extensible tool routing

  wont:
    - id: AC-W01
      criterion: Generate test code for all languages
      reason: Delegated to matched tool skills

test_scenarios:
  happy_path:
    - name: "Full-stack feature with UI + API"
      given: "Feature with frontend-ui and backend-api acceptance criteria"
      when: "Acceptance tests executed"
      then: "UI tests via chrome-devtools-mcp, API tests via tool skill, all pass"

    - name: "Backend-only feature"
      given: "Feature with only backend-api and unit acceptance criteria"
      when: "Acceptance tests executed"
      then: "All tests via tool skills, no chrome-devtools-mcp used"

  edge_cases:
    - name: "chrome-devtools-mcp disabled"
      given: "tools.json has chrome-devtools-mcp: false"
      when: "Feature has frontend-ui tests"
      then: "UI tests marked blocked, backend tests still execute"

  error_cases:
    - name: "tools.json missing"
      given: "x-ipe-docs/config/tools.json does not exist"
      when: "Toolbox config loaded"
      then: "config_active=false, all tools enabled by default"

  blocking:
    - name: "No specification"
      given: "specification.md does not exist"
      when: "Attempt to generate test plan"
      then: "BLOCKED with missing specification"

evaluation:
  self_check:
    - "All ACs have test cases regardless of type"
    - "tools.json config read correctly"
    - "Results grouped by test type"
  judge_agent:
    - criterion: "Multi-type test routing quality"
      rubric: |
        5: All types correctly classified and routed
        4: Minor classification issues
        3: Some types misrouted
        2: Major routing errors
        1: Falls back to UI-only
```
