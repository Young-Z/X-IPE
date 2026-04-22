# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-knowledge-extraction-notes
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
created: 2026-04-13
updated: 2026-04-13

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  General-purpose knowledge extractor that organizes extracted knowledge into structured
  markdown files with hierarchy support, embedded images, and a linked overview table of contents.

triggers:
  - "extract knowledge notes"
  - "create knowledge base"
  - "organize knowledge"
  - "knowledge extraction notes"
  - "take key insights"
  - "create structured notes"

not_for:
  - "x-ipe-tool-knowledge-extraction-user-manual: Use for app user-manual extraction"
  - "x-ipe-tool-knowledge-extraction-application-reverse-engineering: Use for reverse-engineering app architecture"
  - "x-ipe-tool-readme-updator: Use for updating README files"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform"
      validation: "Must be one of: init_knowledge_folder, get_template, extract_section, embed_image, generate_overview, validate_structure"

    - name: knowledge_name
      type: string
      description: "Name of the knowledge base (used as root folder name)"

  optional:
    - name: output_dir
      type: string
      default: "./"
      description: "Parent directory where the knowledge folder will be created"

    - name: source_content
      type: string
      default: null
      description: "Source content to extract knowledge from (text, URL, file path)"

    - name: section_id
      type: string
      default: null
      description: "Section identifier (e.g., '01', '0201') for targeted operations"

    - name: image_path
      type: string
      default: null
      description: "Path to image file to embed"

    - name: template_type
      type: string
      default: "general"
      description: "Template type: general, tutorial, reference, research, meeting-notes"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: knowledge_folder
      type: directory
      path: "{output_dir}/{knowledge_name}/"
      description: "Root folder containing all knowledge files"

    - name: overview_md
      type: file
      path: "{output_dir}/{knowledge_name}/overview.md"
      description: "Content table linking all markdown files"

    - name: images_dir
      type: directory
      path: "{output_dir}/{knowledge_name}/.images/"
      description: "Directory containing all embedded images/screenshots"

  data:
    - name: operation_output
      type: object
      description: "Structure containing result, success status, and errors"

# ─────────────────────────────────────────────────────────────
# FOLDER STRUCTURE
# ─────────────────────────────────────────────────────────────
# The knowledge base follows this structure:
#
#   {knowledge_name}/
#   ├── overview.md                    # Content table linking all sections
#   ├── .images/                       # All embedded images/screenshots
#   │   ├── 01.section-slug.png        # Numbered, descriptive filenames
#   │   ├── 0201.sub-section-slug.png
#   │   └── ...
#   ├── 01.first-topic.md              # Top-level sections (numbered)
#   ├── 02.second-topic.md
#   ├── 03.third-topic/                # Hierarchical: folder for sub-sections
#   │   ├── 0301.sub-topic-a.md
#   │   ├── 0302.sub-topic-b.md
#   │   └── ...
#   └── ...

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
      expected: name starts with 'x-ipe-tool-'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 1 example

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 600 lines
      test: line_count
      expected: < 600

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
      expected: "<operation name=.*>"

    - id: AC-C03
      category: content
      criterion: Error Handling table present
      test: table_parse
      expected: columns [Error, Cause, Resolution]

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: init_knowledge_folder creates correct structure with overview.md, .images/ and numbered sections
      test: execution
      expected: folder structure matches documented pattern

    - id: AC-B02
      category: behavior
      criterion: generate_overview produces linked content table
      test: execution
      expected: overview.md contains markdown links to all section files

    - id: AC-B03
      category: behavior
      criterion: Images are stored in .images/ subfolder with numbered naming convention
      test: path_validation
      expected: "No image files exist outside .images/; names match {NN}.{slug}.{ext}"

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

    - id: AC-B04
      category: behavior
      criterion: Hierarchical sub-sections create numbered sub-folders
      test: execution
      expected: "Sub-folder naming {NN}.{slug}/ with sub-files {NNMM}.{slug}.md"

  could:
    - id: AC-C07
      category: content
      criterion: Templates provided for different knowledge types
      test: file_exists
      expected: templates directory contains at least one template

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-task-based-application-knowledge-extractor
      relationship: caller
      description: "May be invoked by the extractor as a category tool skill"

  artifacts: []

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "init_knowledge_folder success"
      given: "knowledge_name='my-research', output_dir='/tmp/test'"
      when: "execute init_knowledge_folder"
      then: "Folder /tmp/test/my-research/ created with overview.md and .images/"

    - name: "extract_section success"
      given: "source_content provided, section_id='01'"
      when: "execute extract_section"
      then: "01.{slug}.md created with extracted content"

    - name: "generate_overview success"
      given: "knowledge folder with 3 section files"
      when: "execute generate_overview"
      then: "overview.md updated with links to all 3 sections"

    - name: "embed_image success"
      given: "image_path points to valid PNG, section_id='02'"
      when: "execute embed_image"
      then: "Image copied to .images/02.{slug}.png"

    - name: "hierarchical sections"
      given: "source content with sub-topics under section 03"
      when: "execute extract_section with sub-sections"
      then: "03.topic/ folder created with 0301.sub-a.md, 0302.sub-b.md"

  error_cases:
    - name: "Invalid knowledge_name"
      given: "knowledge_name contains special characters"
      when: "execute init_knowledge_folder"
      then: "success=false, error INVALID_NAME"

    - name: "Missing source content for extraction"
      given: "source_content is null"
      when: "execute extract_section"
      then: "success=false, error MISSING_SOURCE"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs match schema"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "Folder structure matches documented pattern"
    - "overview.md links are valid and complete"
