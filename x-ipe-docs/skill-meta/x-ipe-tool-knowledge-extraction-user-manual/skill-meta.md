# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-knowledge-extraction-user-manual
skill_type: x-ipe-tool
version: "1.1.0"
status: candidate
created: 2026-03-17
updated: 2026-07-25

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Provides playbook template, collection template, acceptance criteria, and app-type mixins
  for user manual knowledge extraction. Loaded by x-ipe-task-based-application-knowledge-extractor
  when processing category "user-manual".

triggers:
  - "user-manual extraction"
  - "category: user-manual"
  - "extract user manual knowledge"

not_for:
  - "x-ipe-tool-knowledge-extraction-api-reference: API reference extraction"
  - "x-ipe-tool-readme-updator: Direct README update"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform"
      validation: "Must be one of: get_artifacts, get_collection_template, validate_section, get_mixin, pack_section, score_quality, test_walkthrough"

    - name: category
      type: string
      default: "user-manual"
      description: "Knowledge extraction category — always 'user-manual' for this skill"

  optional:
    - name: section_id
      type: string
      default: null
      description: "Section identifier (e.g., '1-overview'). Required for validate_section, pack_section"

    - name: content_path
      type: string
      default: null
      description: "Path to extracted content file. Required for validate_section, pack_section"

    - name: app_type
      type: string
      default: null
      description: "Target platform: web, cli, or mobile. Required for get_mixin"

    - name: config
      type: object
      default: "{ web_search_enabled: false, max_files_per_section: 20, max_iterations: 3 }"
      description: "Configuration overrides for extraction behavior"

    - name: instruction_temperature
      type: string
      default: "balanced"
      description: "Controls instructional content style: strict (verbatim, no drift), balanced (accuracy + flow), creative (exploratory, inventive examples)"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: playbook_template
      type: file
      path: "templates/playbook-template.md"
      description: "Base user manual section layout (8 sections)"

    - name: collection_template
      type: file
      path: "templates/collection-template.md"
      description: "Per-section extraction prompts"

    - name: acceptance_criteria
      type: file
      path: "templates/acceptance-criteria.md"
      description: "Per-section validation rules"

    - name: mixin_web
      type: file
      path: "templates/mixin-web.md"
      description: "Web app-specific sections and prompts"

    - name: mixin_cli
      type: file
      path: "templates/mixin-cli.md"
      description: "CLI app-specific sections and prompts"

    - name: mixin_mobile
      type: file
      path: "templates/mixin-mobile.md"
      description: "Mobile app-specific sections and prompts"

  data:
    - name: operation_output
      type: object
      description: "Structure containing result, success status, and errors"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    # STRUCTURE
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter including categories
      test: file_exists + yaml_parse
      expected: "name starts with 'x-ipe-tool-', categories includes 'user-manual'"

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists with at least 2 examples
      test: file_exists + content_check
      expected: "file contains 'Example 1' and 'Example 2'"

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 600 lines
      test: line_count
      expected: "< 600"

    - id: AC-S04
      category: structure
      criterion: All 6 template files exist
      test: file_exists
      expected: "playbook-template.md, collection-template.md, acceptance-criteria.md, mixin-web.md, mixin-cli.md, mixin-mobile.md"

    # CONTENT
    - id: AC-C01
      category: content
      criterion: All required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations, Output Result, Definition of Done, Error Handling,
         Templates, Examples]

    - id: AC-C02
      category: content
      criterion: 7 operations defined with XML structure
      test: regex_match
      expected: "7 instances of <operation name=.*>"

    - id: AC-C03
      category: content
      criterion: Error Handling table present
      test: table_parse
      expected: "columns [Error, Cause, Resolution]"

    - id: AC-C04
      category: content
      criterion: Playbook template has 7 sections
      test: content_check
      expected: "H2 headings for Overview, Installation, Getting Started, Core Features, Configuration, Troubleshooting, FAQ"

    - id: AC-C05
      category: content
      criterion: Collection template has extraction prompts for all 7 sections
      test: content_check
      expected: "HTML comments with EXTRACTION PROMPTS in each section"

    - id: AC-C06
      category: content
      criterion: Acceptance criteria has validation rules for all 7 sections
      test: content_check
      expected: "Checkbox items with [REQ] markers for each section"

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: get_artifacts returns all artifact paths
      test: execution
      expected: "Returns playbook_template, collection_template, acceptance_criteria, app_type_mixins"

    - id: AC-B02
      category: behavior
      criterion: validate_section evaluates all criteria
      test: execution
      expected: "Returns per-criterion pass/fail with feedback"

  should:
    - id: AC-C07
      category: content
      criterion: Key Concepts section in About
      test: content_check
      expected: "**Key Concepts:**"

    - id: AC-C08
      category: content
      criterion: Input Initialization uses XML structure
      test: regex_match
      expected: "<input_init>"

    - id: AC-C09
      category: content
      criterion: Mixins include section overlay prompts
      test: content_check
      expected: "Each mixin has 'Section Overlay Prompts' heading"

  could:
    - id: AC-C10
      category: content
      criterion: Examples show both happy path and validation flow
      test: content_check
      expected: "Example 1 covers loading, Example 2 covers validation"

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-task-based-application-knowledge-extractor
      relationship: "loaded-by (extractor discovers and loads this tool skill)"

  artifacts:
    - path: "templates/playbook-template.md"
      description: "Must exist for get_artifacts and pack_section operations"
    - path: "templates/collection-template.md"
      description: "Must exist for get_artifacts and get_collection_template operations"
    - path: "templates/acceptance-criteria.md"
      description: "Must exist for get_artifacts and validate_section operations"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "get_artifacts returns all paths"
      given: "Skill installed with all template files"
      when: "execute get_artifacts"
      then: "success=true, all 6 artifact paths returned, config defaults included"

    - name: "get_collection_template returns full template"
      given: "No section_id specified, instruction_temperature=balanced"
      when: "execute get_collection_template"
      then: "success=true, all 8 sections with extraction prompts returned, balanced temperature guidance appended"

    - name: "get_collection_template respects strict temperature"
      given: "instruction_temperature=strict"
      when: "execute get_collection_template"
      then: "success=true, strict temperature guidance appended (verbatim labels, no paraphrasing)"

    - name: "validate_section passes valid content"
      given: "Section content satisfying all REQ criteria"
      when: "execute validate_section with section_id and content_path"
      then: "success=true, passed=true, all criteria evaluated"

    - name: "get_mixin returns web mixin"
      given: "app_type=web"
      when: "execute get_mixin"
      then: "success=true, web mixin content with additional sections returned"

    - name: "pack_section formats content with temperature"
      given: "Validated section content, instruction_temperature=balanced"
      when: "execute pack_section with section_id and content_path"
      then: "success=true, formatted_content with proper headings returned, instructional tone matches balanced"

  error_cases:
    - name: "Invalid operation"
      given: "operation='invalid_op'"
      when: "execute operation"
      then: "success=false, errors contains INVALID_OPERATION"

    - name: "Missing section_id for validate_section"
      given: "operation='validate_section', section_id=null"
      when: "execute validate_section"
      then: "success=false, errors contains MISSING_SECTION_ID"

    - name: "Invalid app_type for get_mixin"
      given: "operation='get_mixin', app_type='desktop'"
      when: "execute get_mixin"
      then: "success=false, errors contains INVALID_APP_TYPE"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All 7 operations produce structured output matching schema"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully with descriptive messages"
    - "Template files unmodified after all operations"
