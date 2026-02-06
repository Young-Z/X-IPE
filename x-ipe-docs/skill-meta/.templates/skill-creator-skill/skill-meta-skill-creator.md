# Skill Meta: X-IPE Skill Creator

```yaml
---
skill_name: x-ipe-skill-creator
skill_type: meta_skill
version: 2.0.0
last_updated: 2026-02-04
implementation_path: .github/skills/x-ipe-skill-creator/

purpose: Guide for creating effective X-IPE skills with templates, testing, and validation
target_skill_types:
  - task_type
  - tool_skill
  - workflow_orchestration
  - meta_skill

inputs:
  - name: skill_name
    type: string
    required: true
    description: Name of skill to create
    validation: "lowercase, hyphens, 1-64 chars"
  - name: skill_type
    type: string
    required: true
    description: Type of skill
    validation: "task_type | tool_skill | workflow_orchestration | meta_skill"
  - name: user_request
    type: string
    required: true
    description: Description of what the skill should do
  - name: examples
    type: array
    required: false
    description: Concrete usage examples

outputs:
  - name: skill_package
    type: skill_package
    path: ".github/skills/{skill_name}/"
    description: Complete skill with SKILL.md and bundled resources
  - name: skill_meta
    type: file
    path: "x-ipe-docs/skill-meta/{skill_name}/skill-meta.md"
    description: Skill specification with acceptance criteria

acceptance_criteria:
  must:
    - id: AC-M01
      description: SKILL.md exists with valid frontmatter (name, description)
      test_method: file_exists
      expected: ".github/skills/{skill_name}/SKILL.md with YAML frontmatter"
    - id: AC-M02
      description: SKILL.md body under 500 lines
      test_method: structure_validation
      expected: "wc -l < 500"
    - id: AC-M03
      description: Section order follows cognitive flow per skill type
      test_method: content_check
      expected: "Sections in order: Purpose → DoR → Execution → DoD → Examples"
    - id: AC-M04
      description: Importance signals use keywords (BLOCKING, CRITICAL, MANDATORY)
      test_method: content_check
      expected: "No emoji importance signals (⛔, ⚠️)"
    - id: AC-M05
      description: references/examples.md exists for task_type skills
      test_method: file_exists
      expected: "references/examples.md when skill_type == task_type"
  should:
    - id: AC-S01
      description: DoR/DoD use XML checkpoint format
      test_method: structure_validation
      expected: "<definition_of_ready> and <definition_of_done> tags"
    - id: AC-S02
      description: Description includes trigger phrases
      test_method: content_check
      expected: "Triggers on requests like..."
    - id: AC-S03
      description: Cross-references validated (copilot-instructions.md for task_type)
      test_method: custom
      expected: "grep -r {skill-name} shows correct registrations"
  could:
    - id: AC-C01
      description: Sub-agent workflow used for complex skills
      test_method: structure_validation
      expected: "DAG workflow for 5+ step skills"
  wont:
    - id: AC-W01
      description: Runtime code generation
      reason: "Skills provide guidance, not executable code"

evaluation:
  self_check:
    - "File existence checks"
    - "Line count validation"
    - "Section order validation"
    - "Keyword vs emoji check"
  judge_agent:
    - "Quality of execution procedure clarity"
    - "Completeness of acceptance criteria coverage"

workflow:
  sub_agent_dag: true
  test_driven: true
  supports_iteration: true

dependencies:
  skills:
    - lesson-learned
  artifacts:
    - path: "x-ipe-docs/skill-meta/templates/"
      description: "Skill meta templates for different skill types"
  templates:
    - task-type-skill.md
    - skill-category-skill.md
    - workflow-orchestration-skill.md
    - meta-skill.md
---
```

Guide for creating effective X-IPE skills with templates, testing, and validation. This skill orchestrates skill creation using a sub-agent DAG workflow with test-driven development.

## Core Capabilities

| Capability | Description |
|------------|-------------|
| Skill Types | task_type, tool_skill, workflow_orchestration, meta_skill |
| Templates | Task type, skill category, workflow orchestration, meta skill |
| Testing | Sub-agent DAG with sandbox testing and evaluation |
| Iteration | Automatic refinement on test failures (max 3 iterations) |

## Required Files

| File | Purpose |
|------|---------|
| SKILL.md | Entry point with creation workflow |
| templates/ | Skill templates for different skill types |
| references/ | Sub-agent workflows, patterns, structure docs |

## Test Scenarios

- **Create Task Type:** Given requirement gathering skill request → When create invoked → Then valid task-type-requirement-gathering skill produced
- **Validate Structure:** Given draft skill → When validate invoked → Then section order issues reported
- **Iterate on Failure:** Given failed acceptance tests → When iterate invoked → Then candidate updated and re-tested
