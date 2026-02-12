# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-kb-manager
skill_type: x-ipe-tool
version: "1.0.0"
status: released
created: 2026-02-12
updated: 2026-02-12

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Knowledge Base Manager tool providing AI-powered classification, summary generation, search, and topic reorganization operations for the project knowledge base.

triggers:
  - "classify landing items"
  - "classify files"
  - "process knowledge base"
  - "process topic"
  - "search kb"
  - "search knowledge"
  - "reorganize topics"
  - "reorganize knowledge base"

not_for:
  - "x-ipe-task-based-code-implementation: For implementing KB Manager code changes"
  - "kb-landing (FEATURE-025-B): For file upload and landing zone UI"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform: classify | process | search | reorganize | cancel"
      validation: "Must be one of: classify, process, search, reorganize, cancel"

    - name: paths
      type: array
      description: "File paths to classify (required for classify operation)"
      validation: "Non-empty array of strings for classify; not needed for search/reorganize"

  optional:
    - name: query
      type: string
      default: null
      description: "Search query string (required for search operation)"

    - name: session_id
      type: string
      default: null
      description: "Session ID from classify operation (required for process/cancel)"

    - name: classifications
      type: array
      default: null
      description: "Confirmed topic assignments (required for process operation)"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: topic_summaries
      type: file
      path: "instance/kb/{project}/processed/{topic}/summary-vN.md"
      description: "AI-generated topic summaries created after classification"

  data:
    - name: operation_output
      type: object
      description: "JSON response from API endpoint with operation-specific fields"

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
      expected: name equals 'x-ipe-tool-kb-manager'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 2 examples

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
         Input Parameters, Definition of Ready, Operations,
         Output Result, Definition of Done, Error Handling,
         Examples]

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
      criterion: Four operations defined (classify, search, reorganize, cancel)
      test: content_check
      expected: "classify, search, reorganize, cancel operations present"

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Classify operation documents POST /api/kb/process flow
      test: content_check
      expected: "POST /api/kb/process referenced"

    - id: AC-B02
      category: behavior
      criterion: Search operation documents GET /api/kb/search endpoint
      test: content_check
      expected: "GET /api/kb/search referenced"

    - id: AC-B03
      category: behavior
      criterion: Trigger phrases in description frontmatter
      test: yaml_parse
      expected: "description contains classify, search, reorganize triggers"

  should:
    - id: AC-C05
      category: content
      criterion: When to Use includes explicit triggers
      test: yaml_parse
      expected: triggers list is not empty

    - id: AC-C06
      category: content
      criterion: Key Concepts section in About
      test: content_check
      expected: "**Key Concepts:**"

  could:
    - id: AC-C07
      category: content
      criterion: Templates provided for outputs
      test: file_exists
      expected: templates directory exists (optional)

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-workflow-task-execution
      relationship: prerequisite

  artifacts:
    - path: "src/x_ipe/services/kb_manager_service.py"
      description: "KBManagerService must exist (FEATURE-025-C)"
    - path: "src/x_ipe/services/llm_service.py"
      description: "LLMService must exist (FEATURE-025-C)"
    - path: "src/x_ipe/routes/kb_routes.py"
      description: "KB API routes must be registered"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "classify success"
      given: "Files exist in landing zone"
      when: "execute classify with file paths"
      then: "success=true and result contains session_id and suggestions"

    - name: "search success"
      given: "Knowledge base has indexed files"
      when: "execute search with query"
      then: "success=true and result contains query, results, total"

    - name: "reorganize success"
      given: "Topics exist in knowledge base"
      when: "execute reorganize"
      then: "success=true and result contains changes and summary"

    - name: "cancel success"
      given: "Active processing session exists"
      when: "execute cancel with session_id"
      then: "success=true and session is removed"

  error_cases:
    - name: "classify with empty paths"
      given: "Empty paths array"
      when: "execute classify"
      then: "400 error with 'No paths provided'"

    - name: "search without query"
      given: "No query parameter"
      when: "execute search"
      then: "400 error with 'Query parameter q is required'"

    - name: "cancel invalid session"
      given: "Invalid session_id"
      when: "execute cancel"
      then: "404 error with 'Session not found'"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs match schema"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "All 4 operations documented with XML structure"
    - "Trigger phrases match AC-3.6 from specification"
