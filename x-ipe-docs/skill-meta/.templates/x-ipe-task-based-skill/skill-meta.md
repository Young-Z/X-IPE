# Skill Meta Template: Task Type

Use this template to create skill-meta.md for task-type skills. The skill-meta defines **acceptance criteria** for automated testing.

---

## Template

```yaml
# ═══════════════════════════════════════════════════════════
# SKILL META - Task Type
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-type-{name}
skill_type: x-ipe-task-based
version: "1.0.0"
status: draft | candidate | production
created: YYYY-MM-DD
updated: YYYY-MM-DD

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  {One sentence: What this skill produces and its key value.}

triggers:
  - "{trigger phrase 1}"
  - "{trigger phrase 2}"

not_for:
  - "{alternative skill}: {when to use instead}"

# ─────────────────────────────────────────────────────────────
# WORKFLOW POSITION
# ─────────────────────────────────────────────────────────────
workflow:
  category: feature-stage | requirement-stage | ideation-stage | code-refactoring-stage | standalone
  phase: "{phase name if category != standalone}"
  next_task_type: "{TaskName}" | null
  human_review: true | false

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: auto_proceed
      type: boolean
      default: false
      description: Whether to auto-proceed to next task

    - name: {input_name}
      type: string | number | boolean | array | object
      default: {value}
      description: "{what this controls}"
      validation: "{constraint, e.g., 'must match FEATURE-\\d+'}"

  optional:
    - name: {input_name}
      type: string
      default: null
      description: "{what this controls}"

outputs:
  state:
    - name: category
      value: "${workflow.category}"
    - name: status
      value: completed | blocked
    - name: next_task_type
      value: "${workflow.next_task_type}"
    - name: require_human_review
      value: "${workflow.human_review}"
    - name: auto_proceed
      value: "${inputs.auto_proceed}"

  artifacts:
    - name: {artifact_name}
      type: file | directory
      path: "{relative path from project root}"
      description: "{what this contains}"

  data:
    - name: {output_name}
      type: string | object
      description: "{what this represents}"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    # STRUCTURE - Skill file organization
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

    # CONTENT - Required sections and content quality
    - id: AC-C01
      category: content
      criterion: All 10 required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, Input Parameters, 
         Definition of Ready, Execution Flow, Execution Procedure, 
         Output Result, Definition of Done, Patterns & Anti-Patterns, Examples]

    - id: AC-C02
      category: content
      criterion: Frontmatter description includes WHAT + TRIGGERS
      test: content_check
      expected: description contains "Use when" and "Trigger"

    - id: AC-C03
      category: content
      criterion: DoR has verifiable checkpoints
      test: table_parse
      expected: ≥2 rows with specific conditions (not vague terms)

    - id: AC-C04
      category: content
      criterion: DoD has verifiable outcomes
      test: table_parse
      expected: ≥2 rows with measurable criteria

    # BEHAVIOR - Execution produces correct results
    - id: AC-B01
      category: behavior
      criterion: Skill produces expected outputs
      test: execution
      expected: all outputs.artifacts exist after execution

    - id: AC-B02
      category: behavior
      criterion: Output YAML has correct structure
      test: yaml_validate
      expected: category is first field, all required fields present

  should:
    - id: AC-S04
      category: structure
      criterion: Procedure steps use pseudocode for precise operations
      test: content_check
      expected: ≥1 pseudocode block per procedure step

    - id: AC-C05
      category: content
      criterion: Patterns cover common scenarios
      test: section_parse
      expected: ≥2 patterns with When/Then structure

    - id: AC-C06
      category: content
      criterion: Anti-patterns prevent common mistakes
      test: table_parse
      expected: ≥2 anti-patterns with consequence + correction

    - id: AC-B03
      category: behavior
      criterion: Blocking rules prevent incorrect progression
      test: execution
      expected: skill blocks when preconditions not met

  could:
    - id: AC-C07
      category: content
      criterion: Web search guidance included
      test: content_check
      expected: 🌐 markers with search terms

    - id: AC-C08
      category: content
      criterion: Freedom markers indicate flexibility
      test: content_check
      expected: 🔒🔧🎨 markers present

  wont:
    - id: AC-W01
      criterion: Board status updates
      reason: Handled by category skill, not task-type skill

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: task-execution-guideline
      relationship: prerequisite
      description: Must be learned before executing this skill

    - name: "{category}+{board}-management"
      relationship: integration
      description: Called for board updates (if not standalone)

  artifacts:
    - path: "{required artifact path}"
      description: "{what must exist before skill can run}"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "{scenario name}"
      given: "{precondition setup}"
      when: "{action taken}"
      then: "{expected outcome}"

  edge_cases:
    - name: "{edge case name}"
      given: "{edge condition}"
      when: "{action taken}"
      then: "{handling behavior}"

  error_cases:
    - name: "{error scenario name}"
      given: "{error condition}"
      when: "{action taken}"
      then: "{error response/recovery}"

  blocking:
    - name: "{blocking scenario}"
      given: "{missing precondition}"
      when: "{attempt to proceed}"
      then: "BLOCKED with {message}"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs.artifacts exist"
    - "Output YAML validates against schema"
    - "DoD checkpoints all verified"

  judge_agent:
    - criterion: "Output quality meets production standards"
      rubric: |
        5: Excellent - ready for production
        4: Good - minor improvements needed
        3: Acceptable - some gaps
        2: Poor - significant issues
        1: Fail - does not meet requirements
```

---

## Field Reference

| Section | Field | Required | Description |
|---------|-------|----------|-------------|
| Identity | skill_name | Yes | `x-ipe-task-type-{name}` format |
| Identity | version | Yes | Semver format |
| Identity | status | Yes | draft → candidate → production |
| Purpose | summary | Yes | Single sentence outcome |
| Purpose | triggers | Yes | Phrases that invoke skill |
| Purpose | not_for | Yes | What to use instead |
| Workflow | category | Yes | Where in lifecycle |
| Workflow | next_task_type | Yes | Chain destination or null |
| Workflow | human_review | Yes | Pause for approval |
| Interface | inputs.required | Yes | At minimum auto_proceed |
| Interface | outputs.state | Yes | Task completion state |
| Interface | outputs.artifacts | If applicable | Created files |
| Acceptance | must | Yes | All must pass for merge |
| Acceptance | should | Yes | 80% must pass |
| Acceptance | could | Optional | Nice-to-have |
| Acceptance | wont | Optional | Explicit out-of-scope |
| Testing | happy_path | Yes | At least 1 scenario |
| Testing | blocking | Yes | At least 1 scenario |
| Evaluation | self_check | Yes | Automated checks |
| Evaluation | judge_agent | Optional | Quality assessment |

---

## Acceptance Criteria Categories

| Category | Focus | Test Methods |
|----------|-------|--------------|
| **structure** | File organization, sections | file_exists, line_count, section_parse |
| **content** | Information quality, completeness | content_check, table_parse, yaml_parse |
| **behavior** | Execution produces correct results | execution, yaml_validate |

---

## Test Method Reference

| Method | Description | Example Expected |
|--------|-------------|------------------|
| file_exists | File present at path | true |
| line_count | Count lines in file | < 500 |
| section_parse | Extract markdown sections | [list of section names] |
| table_parse | Parse markdown table | ≥2 rows |
| content_check | Search for content patterns | contains "X" |
| yaml_parse | Parse YAML/frontmatter | field present |
| yaml_validate | Validate YAML structure | schema compliance |
| execution | Run skill with inputs | outputs exist |

---

## Usage

1. Copy template YAML block
2. Fill all required fields
3. Define acceptance criteria (focus on MUST first)
4. Add test scenarios for key paths
5. Save as `x-ipe-docs/skill-meta/{skill-name}/skill-meta.md`
