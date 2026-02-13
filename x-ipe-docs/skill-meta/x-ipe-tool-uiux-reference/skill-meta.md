# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-uiux-reference
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
created: 2026-02-13
updated: 2026-02-13

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Execute the UIUX reference workflow — navigate to target URL via Chrome DevTools MCP, inject interactive toolbar, collect colors and elements, take screenshots, and save reference data via save_uiux_reference MCP tool.

triggers:
  - "uiux-reference"
  - "execute uiux-reference"
  - "collect design references"
  - "extract colors from page"

not_for:
  - "x-ipe-task-based-code-implementation: Building the toolbar code itself"
  - "mcp-builder: Creating MCP servers"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: url
      type: string
      description: "Target URL to extract design references from"
      validation: "Must be a valid HTTP/HTTPS URL"

  optional:
    - name: auth_url
      type: string
      default: null
      description: "Authentication prerequisite URL — agent navigates here first for login"

    - name: extra
      type: string
      default: null
      description: "Additional instructions for the agent (e.g., 'Focus on pricing card colors')"

    - name: idea_folder
      type: string
      default: null
      description: "Idea folder name to save references to (derived from context if not provided)"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: reference_session
      type: file
      path: "uiux-references/sessions/ref-session-{NNN}.json"
      description: "Session JSON with all collected reference data"

  data:
    - name: operation_output
      type: object
      description: "Summary with color count, element count, session file path"

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
      expected: name is 'x-ipe-tool-uiux-reference'

    - id: AC-S02
      category: structure
      criterion: references/toolbar-template.md exists
      test: file_exists
      expected: file contains toolbar IIFE code block

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    # CONTENT
    - id: AC-C01
      category: content
      criterion: Purpose section describes workflow
      test: section_parse
      expected: mentions navigate, inject, collect, save

    - id: AC-C02
      category: content
      criterion: Operations section covers execute_reference operation
      test: regex_match
      expected: "<operation name=\"execute_reference\">"

    - id: AC-C03
      category: content
      criterion: References navigate_page CDP tool
      test: content_check
      expected: "navigate_page" appears in operations

    - id: AC-C04
      category: content
      criterion: References evaluate_script for injection
      test: content_check
      expected: "evaluate_script" appears in operations

    - id: AC-C05
      category: content
      criterion: References take_screenshot for captures
      test: content_check
      expected: "take_screenshot" appears in operations

    - id: AC-C06
      category: content
      criterion: References save_uiux_reference MCP tool
      test: content_check
      expected: "save_uiux_reference" appears in operations

    - id: AC-C07
      category: content
      criterion: Describes authentication flow
      test: content_check
      expected: "auth" keyword in operations

    - id: AC-C08
      category: content
      criterion: Describes polling for __xipeRefReady
      test: content_check
      expected: "__xipeRefReady" or "polling" in operations

    - id: AC-C09
      category: content
      criterion: References toolbar-template for injection payload
      test: content_check
      expected: "toolbar-template" referenced in operations

    - id: AC-C10
      category: content
      criterion: Error Handling table present
      test: table_parse
      expected: columns [Error, Cause, Resolution]

  should:
    - id: AC-C11
      category: content
      criterion: When to Use includes trigger phrases
      test: yaml_parse
      expected: triggers list is not empty

    - id: AC-C12
      category: content
      criterion: Key Concepts explains toolbar injection
      test: content_check
      expected: mentions IIFE or injection

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills: []

  artifacts:
    - path: "src/x_ipe/static/js/injected/xipe-toolbar.js"
      description: "Toolbar IIFE source code"

    - path: ".github/copilot/mcp-config.json"
      description: "MCP configuration with Chrome DevTools MCP server"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Execute reference with URL only"
      given: "url=https://example.com, no auth"
      when: "execute uiux-reference"
      then: "success=true, toolbar injected, data collected and saved"

    - name: "Execute reference with auth URL"
      given: "url=https://app.example.com, auth_url=https://login.example.com"
      when: "execute uiux-reference"
      then: "auth page opened first, then target, toolbar injected"

  error_cases:
    - name: "Missing URL parameter"
      given: "no url provided"
      when: "execute uiux-reference"
      then: "error reported: URL is required"

    - name: "Page load failure"
      given: "url=https://nonexistent.example.com"
      when: "execute uiux-reference"
      then: "error reported: Failed to load page"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All CDP tool references present (navigate_page, evaluate_script, take_screenshot)"
    - "Authentication flow documented"
    - "Polling mechanism described"
    - "Error scenarios handled"
    - "toolbar-template.md referenced for injection payload"
