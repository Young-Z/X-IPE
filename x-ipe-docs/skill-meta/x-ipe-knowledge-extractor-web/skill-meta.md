# Skill Meta: x-ipe-knowledge-extractor-web

```yaml
# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-extractor-web
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2026-04-16
updated: 2026-04-16

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Extracts knowledge from web sources via Chrome DevTools MCP — scans page structure
  (extract_overview) and extracts specific content sections (extract_details), writing
  results to .working/ staging area.

triggers:
  - "Extract overview of a web page"
  - "Extract detailed content from a web page section"
  - "Scan a web page for headings, sections, and content structure"

not_for:
  - "Orchestration decisions (belong to assistant-knowledge-librarian-DAO)"
  - "Persisting content to memory (use keeper-memory to promote from .working/)"
  - "Searching existing memory (use extractor-memory)"
  - "Non-web content extraction (use extractor-file or extractor-repo)"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform: extract_overview or extract_details"
      validation: "Must be one of: extract_overview, extract_details"

    - name: context
      type: object
      description: "Full context passed by the assistant orchestrator (target URL + params)"
      validation: "Must contain target URL; depth (for overview) or scope (for details)"

  optional:
    - name: context.depth
      type: string
      default: "shallow"
      description: "Scan depth for extract_overview: shallow (headings only) or medium (headings + summaries)"

    - name: context.scope
      type: string
      default: "full"
      description: "Extraction scope for extract_details: full, section, or specific"

    - name: context.format_hints
      type: string
      default: null
      description: "Format guidance for extract_details with scope=specific (e.g., 'extract tables as JSON')"

outputs:
  state:
    - name: status
      value: success | failure

  data:
    - name: operation_output
      type: object
      description: "Structured result with success, operation name, result data, writes_to path, and errors"

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
      expected: name starts with 'x-ipe-knowledge-'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 1 example per operation

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 600 lines
      test: line_count
      expected: < 600

    # CONTENT — Operations structure
    - id: AC-C01
      category: content
      criterion: All required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations, Output Result, Definition of Done, Error Handling,
         Examples]

    - id: AC-C02
      category: content
      criterion: At least 2 operations defined (extract_overview, extract_details) with typed contracts
      test: content_check
      expected: "Both operation blocks with Input, Output, Writes To, Constraints fields"

    - id: AC-C03
      category: content
      criterion: Each operation contains phase backbone (博学之→笃行之)
      test: content_check
      expected: "All 5 phases present inside each operation: 博学之, 审问之, 慎思之, 明辨之, 笃行之"

    - id: AC-C04
      category: content
      criterion: Each operation declares writes_to path (.working/)
      test: content_check
      expected: "writes_to field present in every operation contract pointing to .working/"

    - id: AC-C05
      category: content
      criterion: Stateless service note in Important Notes
      test: content_check
      expected: "Contains 'Operations are stateless services' or equivalent"

    - id: AC-C06
      category: content
      criterion: Error Handling table present
      test: table_parse
      expected: columns [Error, Cause, Resolution]

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Chrome DevTools MCP dependency documented
      test: content_check
      expected: "Important Notes or About mentions Chrome DevTools MCP as runtime dependency"

    - id: AC-B02
      category: behavior
      criterion: extract_overview writes to .working/overview/
      test: content_check
      expected: "extract_overview contract writes_to includes .working/overview/"

    - id: AC-B03
      category: behavior
      criterion: extract_details writes to .working/extracted/
      test: content_check
      expected: "extract_details contract writes_to includes .working/extracted/"

  should:
    - id: AC-C07
      category: content
      criterion: When to Use includes explicit triggers
      test: yaml_parse
      expected: triggers list is not empty

    - id: AC-C08
      category: content
      criterion: Key Concepts section in About
      test: content_check
      expected: "Operation Contract, Stateless Service, writes_to Discipline"

    - id: AC-C09
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C10
      category: content
      criterion: Operation contract types are specific (not generic string/object)
      test: content_check
      expected: Input and Output types use domain-specific type names

  could:
    - id: AC-C11
      category: content
      criterion: Depth parameter documented with shallow/medium semantics
      test: content_check
      expected: Both shallow and medium behaviors described

    - id: AC-C12
      category: content
      criterion: Constraints per operation are actionable
      test: content_check
      expected: Each constraint is testable (not vague guidance)

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-meta-skill-creator
      relationship: creator

    - name: x-ipe-assistant-knowledge-librarian-DAO
      relationship: orchestrator
      description: "Assistant that coordinates and calls this knowledge skill's operations"

  artifacts:
    - path: "Chrome DevTools MCP"
      description: "Runtime dependency — navigate_page, take_snapshot, evaluate_script tools must be available"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "extract_overview success"
      given: "Valid URL (e.g., https://flask.palletsprojects.com/en/3.0.x/)"
      when: "execute extract_overview with depth=shallow"
      then: "success=true, overview written to .working/overview/{url-slug}.md"

    - name: "extract_details success"
      given: "Valid URL + scope=section"
      when: "execute extract_details"
      then: "success=true, content written to .working/extracted/{url-slug}-section.md"

  error_cases:
    - name: "Unreachable URL"
      given: "target='https://nonexistent-domain-xyz.com'"
      when: "execute extract_overview"
      then: "success=false, errors contains URL_UNREACHABLE with diagnostics"

    - name: "Missing target URL"
      given: "context missing target field"
      when: "execute extract_overview"
      then: "success=false, errors contains INPUT_VALIDATION_FAILED"

    - name: "Invalid operation name"
      given: "operation='nonexistent'"
      when: "execute operation"
      then: "success=false, errors contains INVALID_OPERATION"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All operation outputs match contract types"
    - "Results written to declared writes_to paths (.working/ only)"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully with cleanup of partial files"
    - "Chrome DevTools MCP dependency clearly documented"
```
