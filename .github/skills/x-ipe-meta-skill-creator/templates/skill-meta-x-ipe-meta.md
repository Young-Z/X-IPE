# Skill Meta Template: Meta Skill

Use this template to create skill-meta.md for meta skills. Meta skills create, validate, or manage other skills.

---

## Template

```yaml
---
skill_name: x-ipe-meta-{name}
skill_type: x-ipe-meta
version: 1.0.0
last_updated: {YYYY-MM-DD}
implementation_path: .github/skills/x-ipe-meta-{name}/

purpose: "{Description of what this meta skill does}"
target_skill_types:
  - x-ipe-task-based
  - x-ipe-tool
  - x-ipe-workflow-orchestration
  - x-ipe-meta

inputs:
  - name: skill_name
    type: string
    required: true
    description: Name of skill to create/manage
    validation: "lowercase, hyphens, 1-64 chars"
  - name: skill_type
    type: string
    required: true
    description: Type of skill
    validation: "x-ipe-task-based | x-ipe-tool | x-ipe-workflow-orchestration | x-ipe-meta"
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
      description: references/examples.md exists
      test_method: file_exists
      expected: "references/examples.md with at least 1 example"
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
      description: Cross-references validated
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
    - x-ipe-meta-lesson-learned
  artifacts:
    - path: "x-ipe-docs/skill-meta/.templates/"
      description: "Skill meta templates for different skill types"
  templates:
    - x-ipe-task-based-skill/skill-meta-task-type.md
    - task-category-skill/skill-meta-task-category.md
    - tool-skill/skill-meta-tool.md
    - workflow-orchestration-skill/skill-meta-workflow-orchestration.md
    - meta-skill/skill-meta-meta.md
---
```

---

## Field Reference

| Section | Field | Required | Description |
|---------|-------|----------|-------------|
| Identity | skill_name | Yes | `x-ipe-meta-{name}` format |
| Identity | version | Yes | Semver format |
| Purpose | purpose | Yes | Single sentence description |
| Purpose | target_skill_types | Yes | Which skill types this can manage |
| Interface | inputs | Yes | Required and optional parameters |
| Interface | outputs | Yes | skill_package and skill_meta |
| Acceptance | must | Yes | All must pass for merge |
| Acceptance | should | Yes | 80% must pass |
| Testing | test_scenarios | Recommended | happy_path, edge_cases, error_cases |
| Evaluation | self_check | Yes | Automated checks |
| Evaluation | judge_agent | Optional | Quality assessment |

---

## Test Scenarios

- **Create Task-Based Skill:** Given task-based skill request → When create invoked → Then valid x-ipe-task-based-{name} skill produced
- **Validate Structure:** Given draft skill → When validate invoked → Then section order issues reported
- **Iterate on Failure:** Given failed acceptance tests → When iterate invoked → Then candidate updated and re-tested
