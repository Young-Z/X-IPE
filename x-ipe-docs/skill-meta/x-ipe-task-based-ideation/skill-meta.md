# ═══════════════════════════════════════════════════════════
# SKILL META - Task Type
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-based-ideation
skill_type: x-ipe-task-based
version: "1.0.0"
status: candidate
created: 2026-02-06
updated: 2026-02-06

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Learns and refines user ideas through collaborative brainstorming, producing a structured idea summary with config-driven visualizations and sub-agent critique.

triggers:
  - "ideate"
  - "brainstorm"
  - "refine idea"
  - "analyze my idea"

not_for:
  - "task-type-idea-mockup: Use when creating UI/UX mockups after ideation"
  - "task-type-idea-to-architecture: Use when creating system architecture diagrams after ideation"
  - "task-type-requirement-gathering: Use when gathering formal requirements (post-ideation)"

# ─────────────────────────────────────────────────────────────
# WORKFLOW POSITION
# ─────────────────────────────────────────────────────────────
workflow:
  category: ideation-stage
  phase: ideation
  next_task_type: "Idea Mockup | Idea to Architecture"
  human_review: true

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: auto_proceed
      type: boolean
      default: false
      description: Whether to auto-proceed to next task

    - name: idea_folder_path
      type: string
      default: null
      description: "Path to idea folder under x-ipe-docs/ideas/{folder}"
      validation: "Must be valid directory path"

  optional:
    - name: toolbox_meta_path
      type: string
      default: "x-ipe-docs/config/tools.json"
      description: "Path to ideation toolbox configuration"

    - name: extra_instructions
      type: string
      default: null
      description: "Additional context or requirements from human or config"

outputs:
  state:
    - name: category
      value: ideation-stage
    - name: status
      value: completed | blocked
    - name: next_task_type
      value: "Idea Mockup | Idea to Architecture"
    - name: require_human_review
      value: true
    - name: auto_proceed
      value: "${inputs.auto_proceed}"

  artifacts:
    - name: idea_summary
      type: file
      path: "x-ipe-docs/ideas/{folder}/idea-summary-vN.md"
      description: "Versioned idea summary document"

    - name: mockup
      type: file
      path: "x-ipe-docs/ideas/{folder}/mockups/mockup-vN.html"
      description: "HTML mockup (if frontend-design tool enabled)"

  data:
    - name: idea_id
      type: string
      description: "Unique idea identifier (IDEA-XXX)"
    - name: idea_status
      type: string
      description: "Refined"
    - name: idea_version
      type: string
      description: "Version number (vN)"
    - name: folder_renamed
      type: boolean
      description: "Whether folder was renamed from draft pattern"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    # STRUCTURE
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter (name + description with triggers)
      test: file_exists + yaml_parse
      expected: name and description fields present, description contains "Use when" and "Trigger"

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists with at least 3 examples
      test: file_exists + content_check
      expected: file contains >= 3 example sections

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    # CONTENT
    - id: AC-C01
      category: content
      criterion: All 10 required sections present in v3 order
      test: section_parse
      expected: |
        [Purpose, Important Notes, Input Parameters, Definition of Ready,
         Execution Flow, Execution Procedure, Output Result,
         Definition of Done, Patterns & Anti-Patterns, Examples]

    - id: AC-C02
      category: content
      criterion: Execution procedure uses XML step-based format
      test: content_check
      expected: contains <procedure>, <step_N>, <action>, <output> tags

    - id: AC-C03
      category: content
      criterion: DoR uses XML checkpoint format
      test: content_check
      expected: contains <definition_of_ready> with <checkpoint> elements

    - id: AC-C04
      category: content
      criterion: DoD uses XML checkpoint format with step_output references
      test: content_check
      expected: contains <definition_of_done> with <checkpoint> and <step_output> elements

    - id: AC-C05
      category: content
      criterion: Importance signals use keywords not emoji
      test: content_check
      expected: uses BLOCKING/CRITICAL/MANDATORY, no emoji signals

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Skill produces idea-summary-vN.md after execution
      test: execution
      expected: file created at x-ipe-docs/ideas/{folder}/idea-summary-vN.md

    - id: AC-B02
      category: behavior
      criterion: Output YAML has correct structure (category first)
      test: yaml_validate
      expected: category is first field, all required fields present

  should:
    - id: AC-S04
      category: structure
      criterion: references/ contains tool-usage-guide.md, visualization-guide.md, folder-naming-guide.md
      test: file_exists
      expected: all 4 reference files exist

    - id: AC-C06
      category: content
      criterion: Sub-agent defined for critique step
      test: content_check
      expected: sub_agent block with role=idea-critic

    - id: AC-C07
      category: content
      criterion: Patterns cover >= 3 common scenarios
      test: section_parse
      expected: >= 3 patterns with When/Then structure

    - id: AC-C08
      category: content
      criterion: Anti-patterns table has >= 4 entries
      test: table_parse
      expected: >= 4 anti-pattern rows

    - id: AC-B03
      category: behavior
      criterion: Blocking rules prevent skip of brainstorming and human review
      test: execution
      expected: skill blocks when brainstorming incomplete or human not approved

  could:
    - id: AC-C09
      category: content
      criterion: Config-driven tool loading documented with branching logic
      test: content_check
      expected: IF/THEN/ELSE for tool config scenarios

  wont:
    - id: AC-W01
      criterion: Board status updates
      reason: Handled by ideation-stage+ideation-board-management, not task-type skill

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: task-execution-guideline
      relationship: prerequisite
      description: Must be learned before executing this skill

    - name: infographic-syntax-creator
      relationship: integration
      description: Used for visual infographics when antv-infographic enabled

    - name: ideation-stage+ideation-board-management
      relationship: integration
      description: Called for board updates

  artifacts:
    - path: "x-ipe-docs/ideas/{folder}/files/"
      description: "Idea files must exist before skill can run"

    - path: "x-ipe-docs/config/tools.json"
      description: "Toolbox configuration (created if missing)"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Full ideation with tools enabled"
      given: "Idea files uploaded, tools.json has antv-infographic and mermaid enabled"
      when: "Agent executes ideation skill"
      then: "idea-summary-vN.md created with infographic/mermaid visualizations"

    - name: "Ideation without tools"
      given: "Idea files uploaded, all tools disabled in config"
      when: "Agent executes ideation skill"
      then: "idea-summary-vN.md created with standard markdown"

    - name: "Draft folder rename"
      given: "Folder named 'Draft Idea - 01232026 131611'"
      when: "Ideation completes with clear idea identity"
      then: "Folder renamed to '{Idea Name} - 01232026 131611'"

  edge_cases:
    - name: "Missing config file"
      given: "x-ipe-docs/config/tools.json does not exist"
      when: "Agent starts ideation"
      then: "Default config created with all tools disabled, user informed"

    - name: "Multiple existing versions"
      given: "idea-summary-v1.md and v2 already exist"
      when: "Agent creates new summary"
      then: "Creates idea-summary-v3.md (auto-increment)"

  error_cases:
    - name: "Empty idea folder"
      given: "No files in x-ipe-docs/ideas/{folder}/files/"
      when: "Agent attempts to analyze files"
      then: "BLOCKED with message about missing files"

  blocking:
    - name: "Brainstorming not complete"
      given: "Idea has significant ambiguities unresolved"
      when: "Agent attempts to create summary"
      then: "BLOCKED until brainstorming is well-defined"

    - name: "Human review required"
      given: "Idea summary created"
      when: "Agent attempts to proceed to next task"
      then: "BLOCKED until human approves"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "idea-summary-vN.md exists at correct path"
    - "Output YAML validates against schema"
    - "DoD checkpoints all verified"
    - "Visualization matches config (infographic/mermaid if enabled)"

  judge_agent:
    - criterion: "Idea summary quality"
      rubric: |
        5: Excellent - comprehensive, well-structured, visualizations effective
        4: Good - covers all sections, minor gaps
        3: Acceptable - main sections present, some gaps
        2: Poor - missing key sections or unclear
        1: Fail - does not meet minimum requirements
