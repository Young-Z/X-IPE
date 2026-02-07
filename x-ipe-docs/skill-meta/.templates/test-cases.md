# Test Cases Template

> Timestamp format: `YYYYMMDD-HHMMSS`. Summary is auto-generated.

## Example

```yaml
skill_name: x-ipe-task-based-bug-fix
generated_date: # Auto-generated
version: 1.0.0
config:
  sandbox_path: "x-ipe-docs/skill-meta/x-ipe-task-based-bug-fix/test-20250127-143022/sandbox/"
  timeout_seconds: 300

test_cases:
  - id: TC-001
    source_ac: AC-001
    priority: must
    test_type: structural
    evaluator: self_check
    setup:
      description: "Create a sample bug report file"
      artifacts:
        - path: "input/bug-report.md"
          content: "# Bug: Login button unresponsive\nSteps: Click login → nothing happens"
    execution:
      skill_invocation: "Load skill: x-ipe-task-based-bug-fix with input bug-report.md"
      inputs: { bug_file: "input/bug-report.md" }
      expected_outputs: [{ path: "output/fix-report.md" }]
    validation:
      method: structural_check
      checks:
        - { type: file_exists, path: "output/fix-report.md" }
        - { type: section_exists, file: "output/fix-report.md", sections: ["Root Cause", "Fix Applied"] }
    result: { status: pending } # pending|passed|failed, filled after run
    expected: { pass_criteria: "Fix report created with required sections" }

  - id: TC-002  # Optional: quality test example
    source_ac: AC-003
    priority: should
    test_type: quality
    evaluator: judge_agent
    setup: { description: "Complex bug with multiple symptoms" }
    execution:
      skill_invocation: "Load skill: x-ipe-task-based-bug-fix with complex-bug.md"
      inputs: { bug_file: "input/complex-bug.md" }
    validation:
      method: judge_evaluation
      rubric:
        - { criterion: "Root cause accuracy", weight: 0.5 }
        - { criterion: "Fix completeness", weight: 0.5 }
      pass_threshold: 3.5
    result: { status: pending, score: null, feedback: null } # Optional
    expected: { pass_criteria: "Quality score >= 3.5" }

summary: { total: 2, passed: 0, failed: 0, pending: 2 } # Auto-generated
```

## Reference

| Field | Values |
|-------|--------|
| priority | `must`, `should`, `could` |
| test_type | `structural`, `content`, `execution`, `integration`, `quality`, `edge_case` |
| evaluator | `self_check`, `judge_agent` |
| result.status | `pending`, `passed`, `failed` |

| Check Type | Params |
|------------|--------|
| `file_exists` | path |
| `section_exists` | file, sections[] |
| `content_contains` | file, patterns[] |
| `structure_matches` | file, template |
| `yaml_valid` | file |
| `no_crash` | - |
| `graceful_error` | expected_message |

---
# COPY FROM HERE — Minimal Skeleton

```yaml
skill_name: your-skill-name
generated_date: # Auto-generated
version: 1.0.0
config: { sandbox_path: "x-ipe-docs/skill-meta/your-skill/test-YYYYMMDD-HHMMSS/sandbox/", timeout_seconds: 300 }

test_cases:
  - id: TC-001
    source_ac: AC-001
    priority: must
    test_type: structural
    evaluator: self_check
    setup: { description: "Describe setup" }
    execution:
      skill_invocation: "Load skill: your-skill with your-input"
      inputs: { input_name: "value" }
      expected_outputs: [{ path: "output/result.md" }]
    validation:
      checks: [{ type: file_exists, path: "output/result.md" }]
    result: { status: pending } # Optional
    expected: { pass_criteria: "Output file exists" }

summary: { total: 1, passed: 0, failed: 0, pending: 1 } # Auto-generated
```
