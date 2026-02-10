# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-infographic-syntax
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
created: 2026-02-10
updated: 2026-02-10

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Generate AntV Infographic DSL syntax from user content, selecting appropriate templates and structuring data for visual infographics rendered natively in IPE markdown.

triggers:
  - "create infographic"
  - "infographic diagram"
  - "visualize as infographic"
  - "infographic syntax"
  - "generate infographic"

not_for:
  - "architecture diagrams: use x-ipe-tool-architecture-dsl"
  - "flowcharts or sequence diagrams: use Mermaid"
  - "class/ER diagrams: use Mermaid"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform"
      validation: "Must be one of: generate, refine"

    - name: content
      type: string
      description: "User text content or requirements to convert into infographic syntax"

  optional:
    - name: template_hint
      type: string
      default: null
      description: "Preferred template name or category (list, sequence, compare, hierarchy, chart, relation)"

    - name: theme
      type: string
      default: null
      description: "Theme configuration (dark, custom palette, stylize options)"

    - name: existing_syntax
      type: string
      default: null
      description: "Existing infographic DSL to refine (for refine operation)"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: infographic_syntax
      type: string
      description: "Complete infographic DSL syntax ready for embedding in markdown"

  data:
    - name: operation_output
      type: object
      description: "Structure containing template_used, success status, and errors"

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
      expected: name is 'x-ipe-tool-infographic-syntax'

    - id: AC-S02
      category: structure
      criterion: references/prompt.md exists (DSL specification)
      test: file_exists
      expected: file contains template list and syntax rules

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    # CONTENT
    - id: AC-C01
      category: content
      criterion: All 12 required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Definition of Ready, Operations,
         Output Result, Definition of Done, Error Handling,
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

    - id: AC-C04
      category: content
      criterion: DoD includes validation sub-agent
      test: content_check
      expected: "<validation_sub_agent>" block present with instructions to parse against prompt.md

    - id: AC-C05
      category: content
      criterion: Template-to-data-field mapping documented
      test: content_check
      expected: list->lists, sequence->sequences, compare->compares, hierarchy->root/items, chart->values, relation->nodes+relations

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Tool produces structured output with infographic syntax
      test: execution
      expected: returns operation_output with infographic DSL

    - id: AC-B02
      category: behavior
      criterion: Generated syntax starts with 'infographic <template-name>'
      test: output_validation
      expected: first line matches pattern

    - id: AC-B03
      category: behavior
      criterion: Generated syntax uses correct data field for template type
      test: output_validation
      expected: list-* uses lists, sequence-* uses sequences, etc.

  should:
    - id: AC-C06
      category: content
      criterion: When to Use includes Infographic vs Mermaid comparison
      test: content_check
      expected: table comparing when to use each

    - id: AC-C07
      category: content
      criterion: Key Concepts in About section
      test: content_check
      expected: "**Key Concepts:**"

    - id: AC-C08
      category: content
      criterion: Examples reference file exists
      test: file_exists
      expected: references/examples.md or inline examples

  could:
    - id: AC-C09
      category: content
      criterion: Template selection guide included
      test: content_check
      expected: guidance on which template for which content type

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills: []

  artifacts:
    - path: "references/prompt.md"
      description: "AntV Infographic DSL specification with syntax rules and template list"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Generate list infographic"
      given: "Content with 3-5 feature items"
      when: "execute generate"
      then: "success=true, syntax starts with 'infographic list-*', uses 'lists' data field"

    - name: "Generate sequence infographic"
      given: "Content with ordered steps/process"
      when: "execute generate"
      then: "success=true, syntax starts with 'infographic sequence-*', uses 'sequences' data field"

    - name: "Refine existing syntax"
      given: "Existing infographic DSL with update request"
      when: "execute refine"
      then: "success=true, updated syntax preserves structure"

  error_cases:
    - name: "Invalid template name"
      given: "template_hint with non-existent template"
      when: "execute generate"
      then: "success=false, errors contains template_not_found"

    - name: "Empty content"
      given: "No content provided"
      when: "execute generate"
      then: "success=false, errors contains content_required"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs match schema"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "Sub-agent validates syntax against prompt.md specification"
