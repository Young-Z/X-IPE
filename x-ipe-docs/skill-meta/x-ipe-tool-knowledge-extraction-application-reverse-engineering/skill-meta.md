# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-knowledge-extraction-application-reverse-engineering
skill_type: x-ipe-tool
version: "2.0.0"
status: candidate
created: 2026-03-31
updated: 2026-04-07

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Provides playbook, collection template, acceptance criteria, and two-dimension mixins
  (repo-type × language-type) for application reverse engineering knowledge extraction.

triggers:
  - "application reverse engineering extraction"
  - "category: application-reverse-engineering"
  - "reverse engineer codebase"

not_for:
  - "x-ipe-tool-knowledge-extraction-user-manual: user manual extraction"
  - "Direct README update: use x-ipe-tool-readme-updator"

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
      default: "application-reverse-engineering"
      description: "Always 'application-reverse-engineering' for this skill"

  optional:
    - name: section_id
      type: string
      default: null
      description: "Section identifier (e.g., '1-architecture-recovery'). Required for validate_section, pack_section, score_quality"

    - name: content_path
      type: string
      default: null
      description: "Path to extracted content file. Required for validate_section, pack_section, score_quality, test_walkthrough"

    - name: mixin_key
      type: string
      default: null
      description: "Mixin identifier (e.g., 'monorepo', 'python'). Required for get_mixin"

    - name: repo_path
      type: string
      default: null
      description: "Path to target repo for test_walkthrough verification"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: playbook_template
      type: file
      path: "templates/playbook-template.md"
      description: "8-section phased playbook"

    - name: collection_template
      type: file
      path: "templates/collection-template.md"
      description: "Per-section extraction prompts"

    - name: acceptance_criteria
      type: file
      path: "templates/acceptance-criteria.md"
      description: "Per-section validation rules"

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
      criterion: SKILL.md exists with valid frontmatter (name, version, categories)
      test: file_exists + yaml_parse
      expected: name is 'x-ipe-tool-knowledge-extraction-application-reverse-engineering', categories includes 'application-reverse-engineering'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists with at least 1 example
      test: file_exists + content_check
      expected: file contains at least 1 example

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: "< 500"

    - id: AC-S04
      category: structure
      criterion: All 12 template files exist in templates/
      test: file_exists
      expected: "playbook-template.md, collection-template.md, acceptance-criteria.md, 4 repo-type mixins, 5 language-type mixins"

    # CONTENT
    - id: AC-C01
      category: content
      criterion: All required sections present in SKILL.md (Purpose, Important Notes, About, When to Use, Input Parameters, Definition of Ready, Operations, Output Result, Definition of Done, Error Handling, Templates, Examples)
      test: section_parse
      expected: all 12+ sections present

    - id: AC-C02
      category: content
      criterion: All 7 operations defined with XML structure
      test: regex_match
      expected: "get_artifacts, get_collection_template, validate_section, get_mixin, pack_section, score_quality, test_walkthrough"

    - id: AC-C03
      category: content
      criterion: Quality scoring weight tables embedded in score_quality operation
      test: content_check
      expected: "3 weight profiles: architecture (1,2,6), tests (8), other (3,4,5,7)"

    - id: AC-C04
      category: content
      criterion: Complexity gate thresholds documented
      test: content_check
      expected: "min_files=10, min_loc=500, min_dirs=3"

    - id: AC-C05
      category: content
      criterion: Playbook template has 8 sections with phase annotations
      test: section_parse
      expected: "Sections 1-8 with Phase 1/2/3 labels"

    - id: AC-C06
      category: content
      criterion: Collection template has extraction prompts in HTML comments for all 8 sections
      test: regex_match
      expected: "8 sections with <!-- EXTRACTION PROMPTS blocks"

    - id: AC-C07
      category: content
      criterion: Acceptance criteria template has [REQ]/[OPT] markers for all 8 sections
      test: regex_match
      expected: "All 8 sections have checklist items with [REQ] or [OPT]"

    - id: AC-C08
      category: content
      criterion: Each mixin has Detection Signals, Additional Sections, and Section Overlay Prompts
      test: section_parse
      expected: "All 9 mixins follow the standard mixin structure"

    - id: AC-C09
      category: content
      criterion: Error Handling table present with all error codes
      test: table_parse
      expected: "columns [Error, Cause, Resolution], at least 7 error codes"

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: get_artifacts returns correct paths for all templates and mixins
      test: execution
      expected: "Returns artifact_paths with playbook, collection, AC, 4 repo-type mixins, 5 language-type mixins"

    - id: AC-B02
      category: behavior
      criterion: get_mixin resolves correct mixin file for all 9 keys
      test: execution
      expected: "Each of 9 mixin keys maps to correct template file"

    - id: AC-B03
      category: behavior
      criterion: validate_section distinguishes FAIL from INCOMPLETE
      test: execution
      expected: "FAIL for wrong content, INCOMPLETE for missing content"

  should:
    - id: AC-C10
      category: content
      criterion: When to Use includes explicit triggers
      test: yaml_parse
      expected: triggers list is not empty

    - id: AC-C11
      category: content
      criterion: Key Concepts section in About
      test: content_check
      expected: "**Key Concepts:**"

    - id: AC-C12
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C13
      category: content
      criterion: Mixin composition rules documented (repo-type primary, language-type additive)
      test: content_check
      expected: "Documents that only one repo-type applied, multiple language-types may be applied"

  could:
    - id: AC-C14
      category: content
      criterion: Templates table lists all 12 template files
      test: table_parse
      expected: "12 rows in Templates table"

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-task-based-application-knowledge-extractor
      relationship: consumer
    - name: x-ipe-tool-knowledge-extraction-user-manual
      relationship: structural-reference

  artifacts:
    - path: ".github/skills/x-ipe-tool-knowledge-extraction-application-reverse-engineering/SKILL.md"
      description: "Skill entry point"
    - path: ".github/skills/x-ipe-tool-knowledge-extraction-application-reverse-engineering/templates/"
      description: "All 12 template files"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "get_artifacts returns all paths"
      given: "Skill is loaded with category 'application-reverse-engineering'"
      when: "execute get_artifacts"
      then: "Returns paths for playbook, collection, AC, 4 repo-type mixins, 5 language-type mixins, config_defaults"

    - name: "get_mixin returns repo-type mixin"
      given: "mixin_key is 'monorepo'"
      when: "execute get_mixin"
      then: "Returns content of templates/mixin-monorepo.md"

    - name: "get_mixin returns language-type mixin"
      given: "mixin_key is 'python'"
      when: "execute get_mixin"
      then: "Returns content of templates/mixin-python.md"

    - name: "validate_section detects passing content"
      given: "section_id is '5-code-structure-analysis' and content meets all [REQ] criteria"
      when: "execute validate_section"
      then: "Returns passed=true with all criteria status='pass'"

    - name: "score_quality applies architecture weights"
      given: "section_id is '1-architecture-recovery'"
      when: "execute score_quality"
      then: "Uses accuracy=0.35 as highest weight"

  error_cases:
    - name: "Invalid mixin_key"
      given: "mixin_key is 'ruby'"
      when: "execute get_mixin"
      then: "Returns INVALID_MIXIN_KEY error with list of valid keys"

    - name: "Missing section_id for validate_section"
      given: "section_id is null"
      when: "execute validate_section"
      then: "Returns MISSING_SECTION_ID error"

    - name: "Content not found"
      given: "content_path points to non-existent file"
      when: "execute validate_section"
      then: "Returns CONTENT_NOT_FOUND error"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All 15 files exist (SKILL.md + 12 templates + examples.md + test-cases.yaml)"
    - "SKILL.md under 500 lines"
    - "All 7 operations have XML structure"
    - "Quality scoring weight tables embed 3 profiles"
    - "Complexity gate thresholds match spec"
    - "All 9 mixins follow standard structure"
    - "Error handling covers all 7+ error codes"
