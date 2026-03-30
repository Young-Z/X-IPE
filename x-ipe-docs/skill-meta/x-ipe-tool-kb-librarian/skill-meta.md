# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-kb-librarian
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
created: 2026-03-16
updated: 2026-03-30

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Organize knowledge base intake files by analyzing content, assigning lifecycle/domain tags,
  generating YAML frontmatter (markdown only), and moving files from .intake/ to their
  destination folders — all in a single batch operation.

triggers:
  - "organize knowledge base intake files with AI Librarian"
  - "run AI Librarian"
  - "organize intake"

not_for:
  - "Manual file browsing or intake UI interaction — that's the KB Browse Modal frontend"
  - "Knowledge base configuration — use knowledgebase-config.json directly"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform"
      validation: "Must be 'organize_intake'"

  optional:
    - name: kb_root
      type: string
      default: auto-detect
      description: "Knowledge base root folder (auto-detected from project)"

outputs:
  state:
    - name: status
      value: success | partial_success | failure

  artifacts:
    - name: organized_files
      type: list
      description: "Files moved from .intake/ to destination folders"

  data:
    - name: operation_output
      type: object
      description: "files_processed count, destinations list, errors list, summary text"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    # STRUCTURE
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name is 'x-ipe-tool-kb-librarian'

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
      criterion: Operations use XML structure
      test: regex_match
      expected: "<operation name=\"organize_intake\">"

    - id: AC-C03
      category: content
      criterion: Error Handling table present
      test: table_parse
      expected: columns [Error, Cause, Resolution]

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Operation reads KB config for tag taxonomy
      test: content_check
      expected: "GET /api/kb/config or read knowledgebase-config.json"

    - id: AC-B02
      category: behavior
      criterion: Operation gets pending intake files
      test: content_check
      expected: "GET /api/kb/intake"

    - id: AC-B03
      category: behavior
      criterion: Operation sets status to processing before analyzing
      test: content_check
      expected: "status → processing"

    - id: AC-B04
      category: behavior
      criterion: Operation respects pre-assigned destinations
      test: content_check
      expected: "pre-assigned destination" or "UI-assigned"

    - id: AC-B05
      category: behavior
      criterion: Operation generates frontmatter for markdown only
      test: content_check
      expected: "markdown" AND "skip frontmatter" for non-markdown

    - id: AC-B06
      category: behavior
      criterion: Operation moves file to destination folder
      test: content_check
      expected: "move file" AND "destination"

    - id: AC-B07
      category: behavior
      criterion: Operation prints terminal summary
      test: content_check
      expected: "summary" AND "processed"

  should:
    - id: AC-C04
      category: content
      criterion: When to Use includes explicit triggers
      test: yaml_parse
      expected: triggers list is not empty

    - id: AC-C05
      category: content
      criterion: Key Concepts section in About
      test: content_check
      expected: "**Key Concepts:**"

    - id: AC-C06
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

  could:
    - id: AC-C07
      category: content
      criterion: Auto-create destination folders documented
      test: content_check
      expected: "create" AND "folder" AND "not exist"

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills: []

  artifacts:
    - path: "x-ipe-docs/knowledge-base/.intake/"
      description: "Intake folder must exist with files to process"
    - path: "x-ipe-docs/knowledge-base/knowledgebase-config.json"
      description: "KB config with tag taxonomy"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "organize_intake with pending markdown files"
      given: "3 markdown files in .intake/ with status pending"
      when: "execute organize_intake"
      then: "success=true, files_processed=3, all moved to destination folders with frontmatter"

    - name: "organize_intake with pre-assigned destinations"
      given: "2 files in .intake/ with destinations pre-assigned via UI"
      when: "execute organize_intake"
      then: "success=true, files moved to pre-assigned folders (AI folder selection skipped)"

    - name: "organize_intake with mixed file types"
      given: "1 markdown + 1 PDF in .intake/"
      when: "execute organize_intake"
      then: "markdown gets frontmatter, PDF moved without frontmatter, both filed"

  error_cases:
    - name: "No pending files"
      given: "All files in .intake/ already have status 'filed'"
      when: "execute organize_intake"
      then: "success=true, files_processed=0, summary says 'No pending files'"

    - name: "Intake folder not found"
      given: "KB has no .intake/ folder configured"
      when: "execute organize_intake"
      then: "success=false, errors contains INTAKE_FOLDER_NOT_FOUND"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs match schema"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "Frontmatter generation only for markdown files"
    - "Pre-assigned destinations respected"
