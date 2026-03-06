# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-web-search
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
created: 2026-03-06
updated: 2026-03-06

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Delegate focused web research to the current coding agent's web capability, then return structured findings, principles, and citations for downstream skills.

triggers:
  - "web search"
  - "research topic"
  - "find best practices"
  - "search the web"
  - "research common principles"

not_for:
  - "project-internal codebase analysis: use repo search/explore tools instead"
  - "task routing decisions: use x-ipe-tool-decision-making"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform"
      validation: "Must be one of: research_topic"

    - name: research_request
      type: object
      description: "Structured research request including topic, goal, and questions"
      validation: "Must include topic and goal"

  optional:
    - name: existing_knowledge
      type: string
      default: null
      description: "What the caller already knows or assumptions to validate"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: research_summary
      type: markdown
      path: "templates/research-summary.md"
      description: "Optional summary structure callers can follow when embedding findings"

  data:
    - name: operation_output
      type: object
      description: "Structured result with findings, citations, and recommended principles"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name is 'x-ipe-tool-web-search'

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

    - id: AC-C01
      category: content
      criterion: All required tool-skill sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations, Output Result, Definition of Done, Error Handling,
         Templates, Examples]

    - id: AC-C02
      category: content
      criterion: Operation documents capability delegation and bounded research
      test: content_check
      expected: native web capability preferred, limits documented

    - id: AC-B01
      category: behavior
      criterion: Tool returns structured findings with citations
      test: execution
      expected: operation_output contains key_findings, recommended_principles, and sources

  should:
    - id: AC-C03
      category: content
      criterion: Error handling covers unavailable capability and project-specific topics
      test: table_parse
      expected: includes WEB_SEARCH_NOT_APPROPRIATE and WEB_CAPABILITY_UNAVAILABLE

    - id: AC-C04
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-B02
      category: behavior
      criterion: Research request supports caller-provided questions and seed URLs
      test: execution
      expected: operation handles both seeded and capability-driven search flows

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills: []

  artifacts:
    - path: "templates/research-summary.md"
      description: "Reusable summary structure for embedding findings"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Research authentication best practices"
      given: "general topic with 3 focused questions"
      when: "execute research_topic"
      then: "success=true with cited sources and recommended principles"

    - name: "Research from seed URLs"
      given: "goal plus 2 official docs URLs"
      when: "execute research_topic"
      then: "seed URLs fetched first, findings synthesized"

  error_cases:
    - name: "Project-specific request"
      given: "request is about internal project files or code"
      when: "execute research_topic"
      then: "success=false with WEB_SEARCH_NOT_APPROPRIATE"

    - name: "Web capability unavailable"
      given: "agent has no internet or fetch capability"
      when: "execute research_topic"
      then: "success=false with WEB_CAPABILITY_UNAVAILABLE"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "Research flow distinguishes general knowledge from project-specific questions"
    - "Native CLI or agent web capability is preferred over manual browsing"
    - "Returned findings always include citations or a clear failure reason"
