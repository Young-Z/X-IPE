```yaml
# ═══════════════════════════════════════════════════════════
# SKILL META - x-ipe-meta-skill-creator-v3
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-meta-skill-creator-v3
skill_type: x-ipe-meta
version: "1.0.0"
status: candidate
created: 2026-02-05
updated: 2026-02-06
implementation_path: .github/skills/x-ipe-skill-creator-v3/

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
purpose: |
  Guide for creating effective X-IPE skills with complete template coverage, 
  sub-agent DAG workflow, and validation against skill-general-guidelines-v2.

target_skill_types:
  - x-ipe-task-based
  - x-ipe-tool
  - x-ipe-workflow-orchestration
  - x-ipe-meta
  - x-ipe-task-category

triggers:
  - "create a new skill"
  - "build a skill for {task}"
  - "generate skill template"

not_for:
  - "lesson-learned: for capturing feedback on existing skills"
  - "task-execution-guideline: for executing tasks, not creating skills"

# ─────────────────────────────────────────────────────────────
# VERSION HISTORY
# ─────────────────────────────────────────────────────────────
upgraded_from: x-ipe-meta-skill-creator-v2

improvements_over_v2:
  - area: Templates
    v2_issue: "4 mentioned, only 2 exist"
    v3_fix: "All 5 templates exist and validated (added task-category)"
  - area: Examples
    v2_issue: ">= 2 examples"
    v3_fix: ">= 3 concrete usage examples required"
  - area: Keywords
    v2_issue: "Mentioned but not enforced"
    v3_fix: "BLOCKING/CRITICAL/MANDATORY validation (no emoji)"
  - area: Sub-agent workflow
    v2_issue: "Basic"
    v3_fix: "Full DAG with model hints (haiku/sonnet)"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: skill_name
      type: string
      description: Name of skill to create/manage
      validation: "lowercase, hyphens, 1-64 chars"
    - name: skill_type
      type: string
      description: Type of skill
      validation: "x-ipe-task-based | x-ipe-tool | x-ipe-workflow-orchestration | x-ipe-meta | x-ipe-task-category"
    - name: user_request
      type: string
      description: Description of what the skill should do

  optional:
    - name: examples
      type: array
      default: null
      description: Concrete usage examples provided by user

outputs:
  artifacts:
    - name: skill_package
      type: directory
      path: ".github/skills/{skill_name}/"
      description: Complete skill with SKILL.md and bundled resources
      created_from: "candidate/templates/{skill_type}.md"
    - name: skill_meta
      type: file
      path: "x-ipe-docs/skill-meta/{skill_name}/skill-meta.md"
      description: Skill specification with acceptance criteria
      created_from: "candidate/templates/skill-meta-{skill_type}.md"

  state:
    - name: status
      value: completed | blocked
    - name: templates_validated
      value: true | false

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    # STRUCTURE - File organization
    - id: AC-M01
      category: structure
      criterion: All 5 template files exist in templates/ folder
      test: file_exists
      expected: |
        x-ipe-task-based.md, x-ipe-tool.md, x-ipe-workflow-orchestration.md, 
        x-ipe-meta.md, skill-meta-x-ipe-task-based.md (and others)
    
    - id: AC-M02
      category: structure
      criterion: Each template follows skill-general-guidelines-v2.md section order
      test: structure_validation
      expected: Section order matches cognitive flow per skill type

    - id: AC-M03
      category: structure
      criterion: SKILL.md body under 500 lines
      test: line_count
      expected: "wc -l < 500"

    # CONTENT - Required sections and quality
    - id: AC-M04
      category: content
      criterion: At least 3 concrete usage examples in references/examples.md
      test: content_check
      expected: ">= 3 examples with ## Example headers"

    - id: AC-M05
      category: content
      criterion: Importance signals use keywords (BLOCKING, CRITICAL, MANDATORY)
      test: content_check
      expected: "No emoji importance signals (⛔, ⚠️, 🔴, 🟢)"

    - id: AC-M06
      category: content
      criterion: YAML frontmatter has name (1-64 chars) and description (includes triggers)
      test: yaml_parse
      expected: "name and description fields present with trigger phrases"

    - id: AC-M07
      category: content
      criterion: BLOCKING reference to skill-general-guidelines-v2.md in Important Notes
      test: content_check
      expected: "BLOCKING.*skill-general-guidelines pattern found"

    # BEHAVIOR - Execution produces correct results
    - id: AC-M08
      category: behavior
      criterion: Sub-agent DAG defined with parallel groups and model hints
      test: structure_validation
      expected: "parallel_groups with merge points and haiku/sonnet hints"

    - id: AC-M09
      category: behavior
      criterion: Every step output has corresponding DoD checkpoint
      test: content_comparison
      expected: "<output> tags map to <step_output> tags in DoD"

    - id: AC-M10
      category: behavior
      criterion: Created skill has complete step output coverage in DoD
      test: content_comparison
      expected: "Created skill's outputs all have DoD checkpoints"

  should:
    - id: AC-S01
      category: content
      criterion: Section order follows cognitive flow (CONTEXT → DECISION → ACTION → VERIFY → REFERENCE)
      test: section_parse
      expected: "Sections in correct order"

    - id: AC-S02
      category: structure
      criterion: Complex details delegated to references/ folder
      test: content_check
      expected: "Progressive disclosure applied"

    - id: AC-S03
      category: content
      criterion: DoR/DoD use XML checkpoint format
      test: structure_validation
      expected: "<definition_of_ready> and <definition_of_done> tags"

    - id: AC-S04
      category: content
      criterion: Uses {variable_name} pattern throughout procedures
      test: content_check
      expected: "Consistent variable syntax"

  could:
    - id: AC-C01
      category: content
      criterion: Cross-reference validation for x-ipe-task-based skills
      test: custom
      expected: "Bidirectional references validated"

    - id: AC-C02
      category: behavior
      criterion: Skill update workflow checks lesson-learned.md
      test: content_check
      expected: "Lesson integration documented"

    - id: AC-C03
      category: behavior
      criterion: Sub-agent model hints prefer haiku for simple, sonnet for complex
      test: content_check
      expected: "Cost efficiency applied"

  wont:
    - id: AC-W01
      criterion: Runtime code generation
      reason: "Skills provide guidance, not executable code"

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: lesson-learned
      relationship: integration
      description: Check for accumulated feedback before updates

  artifacts:
    - path: "x-ipe-docs/skill-meta/.templates/skill-creation-best-practice/references/"
      description: "Guideline v2 and reference files"

  # ═══════════════════════════════════════════════════════════
  # TEMPLATE MAPPING
  # ═══════════════════════════════════════════════════════════
  # CRITICAL: Use these templates instead of creating from scratch
  # Location: x-ipe-docs/skill-meta/x-ipe-skill-creator-v3/candidate/templates/
  # ═══════════════════════════════════════════════════════════
  
  skill_templates:
    description: "SKILL.md templates - use to create skill implementation"
    mapping:
      x-ipe-task-based: x-ipe-task-based.md
      x-ipe-tool: x-ipe-tool.md
      x-ipe-workflow-orchestration: x-ipe-workflow-orchestration.md
      x-ipe-meta: x-ipe-meta.md
      x-ipe-task-category: x-ipe-workflow-orchestration.md  # Same structure

  skill_meta_templates:
    description: "skill-meta.md templates - use to create acceptance criteria"
    mapping:
      x-ipe-task-based: skill-meta-x-ipe-task-based.md
      x-ipe-tool: skill-meta-x-ipe-tool.md
      x-ipe-task-category: skill-meta-x-ipe-task-category.md
      x-ipe-meta: skill-meta-x-ipe-meta.md
      x-ipe-workflow-orchestration: skill-meta-x-ipe-task-based.md  # Same structure

# ─────────────────────────────────────────────────────────────
# TEMPLATE USAGE PROCEDURE
# ─────────────────────────────────────────────────────────────
template_usage:
  step_1:
    action: "Identify skill_type from user request"
    output: "skill_type value"
  
  step_2:
    action: "Load SKILL.md template"
    source: "candidate/templates/{skill_templates.mapping[skill_type]}"
    output: "SKILL.md scaffold"
  
  step_3:
    action: "Load skill-meta.md template"  
    source: "candidate/templates/{skill_meta_templates.mapping[skill_type]}"
    output: "skill-meta.md scaffold"
  
  step_4:
    action: "Fill templates with skill-specific content"
    inputs: [user_request, skill_name, examples]
    output: "Complete SKILL.md and skill-meta.md"
  
  step_5:
    action: "Validate against guideline-v2"
    reference: "references/1. skill-general-guidelines-v2.md"
    output: "Validation result"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Create task-type skill from template"
      given: "User request for task-type skill"
      when: "Load x-ipe-task-based.md and skill-meta-x-ipe-task-based.md templates"
      then: "Valid SKILL.md and skill-meta.md produced from templates"

    - name: "Create tool skill from template"
      given: "User request for utility tool"
      when: "Load x-ipe-tool.md and skill-meta-x-ipe-tool.md templates"
      then: "Valid SKILL.md and skill-meta.md produced from templates"

    - name: "Create meta skill from template"
      given: "User request for meta skill"
      when: "Load x-ipe-meta.md and skill-meta-x-ipe-meta.md templates"
      then: "Valid SKILL.md and skill-meta.md produced from templates"

    - name: "Validate template structure"
      given: "Draft skill created from template"
      when: "Run validation against guideline-v2"
      then: "Section order matches template structure"

  edge_cases:
    - name: "Complex skill requires sub-agents"
      given: "5+ step skill request"
      when: "Execute skill creator"
      then: "DAG workflow applied"

  error_cases:
    - name: "Invalid skill type"
      given: "Unknown skill_type parameter"
      when: "Execute skill creator"
      then: "Error: unsupported skill type"

  blocking:
    - name: "Missing guideline reference"
      given: "SKILL.md without BLOCKING guideline reference"
      when: "Run validation"
      then: "BLOCKED: AC-M07 failed"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All template files exist"
    - "Line count < 500"
    - "Section order validated"
    - "Keyword vs emoji check passed"
    - "DoD covers all step outputs"

  judge_agent:
    - criterion: "Quality of execution procedure clarity"
      rubric: |
        5: Crystal clear, unambiguous steps
        4: Clear with minor ambiguities
        3: Acceptable, some gaps
        2: Confusing, significant issues
        1: Unusable

    - criterion: "Acceptance criteria completeness"
      rubric: |
        5: All behaviors covered with tests
        4: Most behaviors covered
        3: Core behaviors covered
        2: Major gaps
        1: Insufficient

# ─────────────────────────────────────────────────────────────
# PASS CRITERIA
# ─────────────────────────────────────────────────────────────
pass_criteria:
  must_pass_rate: 100%   # All 10 MUST criteria pass
  should_pass_rate: 80%  # At least 4 of 4 SHOULD criteria pass
  could_pass_rate: 0%    # Optional, no minimum
  
  overall_pass:
    condition: "must_pass_rate == 100% AND should_pass_rate >= 80%"
    then: "Merge to production"
    else: "Iterate (max 3 attempts) or escalate"

# ─────────────────────────────────────────────────────────────
# VALIDATION MATRIX
# ─────────────────────────────────────────────────────────────
validation_matrix:
  - { criterion: AC-M01, test_type: file_existence, automated: true, human_review: false }
  - { criterion: AC-M02, test_type: structure_validation, automated: true, human_review: false }
  - { criterion: AC-M03, test_type: line_count, automated: true, human_review: false }
  - { criterion: AC-M04, test_type: content_check, automated: true, human_review: false }
  - { criterion: AC-M05, test_type: pattern_match, automated: true, human_review: false }
  - { criterion: AC-M06, test_type: yaml_parse, automated: true, human_review: false }
  - { criterion: AC-M07, test_type: pattern_match, automated: true, human_review: false }
  - { criterion: AC-M08, test_type: structure_validation, automated: true, human_review: true }
  - { criterion: AC-M09, test_type: content_comparison, automated: true, human_review: false }
  - { criterion: AC-M10, test_type: content_comparison, automated: true, human_review: false }
  - { criterion: AC-S01-S04, test_type: content_analysis, automated: partial, human_review: true }
  - { criterion: AC-C01-C03, test_type: manual_review, automated: false, human_review: true }
```
