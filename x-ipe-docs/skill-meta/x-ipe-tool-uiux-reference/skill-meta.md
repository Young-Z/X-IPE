# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-uiux-reference
skill_type: x-ipe-tool
version: "2.0.0"
status: production
created: 2026-02-13
updated: 2026-02-15

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Execute the UIUX reference workflow v3.0 — navigate to target URL via Chrome DevTools MCP, inject two-mode toolbar (Catch Design Theme + Copy Design as Mockup) via precompressed 2-call injection from toolbar.compressed.json, collect design data with semantic element naming/purpose/relationships, save as referenced-elements.json via MCP.

triggers:
  - "uiux-reference"
  - "execute uiux-reference"
  - "collect design references"
  - "extract colors from page"
  - "catch design theme"
  - "copy design as mockup"

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
    - name: referenced_elements
      type: file
      path: "uiux-references/page-element-references/referenced-elements.json"
      description: "Single source of truth for all analysis data (replaces session files)"

  data:
    - name: operation_output
      type: object
      description: "Summary with mode, color count, area count, referenced_elements_file path"

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
      criterion: All 12 required sections present in correct order
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

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Compressed injection procedure documented (2 calls not 6+)
      test: content_check
      expected: "toolbar.compressed.json" referenced, 2-call injection described

    - id: AC-B02
      category: behavior
      criterion: referenced-elements.json is single source of truth
      test: content_check
      expected: "referenced-elements.json" appears, no "ref-session" or session file references

    - id: AC-B03
      category: behavior
      criterion: Lesson LL-001 incorporated (ARIA workaround for screenshot)
      test: content_check
      expected: "aria-label" or "ARIA" workaround for elements without UIDs described

  should:
    - id: AC-C04
      category: content
      criterion: When to Use includes trigger phrases for both modes
      test: yaml_parse
      expected: triggers list includes theme and mockup triggers

    - id: AC-C05
      category: content
      criterion: Key Concepts explains compressed injection
      test: content_check
      expected: mentions gzip+base64 or compressed injection

    - id: AC-C06
      category: content
      criterion: Code snippets externalized to references/code-snippets.md
      test: file_exists
      expected: large JS blocks moved out of SKILL.md body

  could:
    - id: AC-C07
      category: content
      criterion: Data schema externalized to references/data-schema.md
      test: file_exists
      expected: referenced-elements.json schema in separate file

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-tool-brand-theme-creator
      relationship: downstream
      description: "Invoked after theme mode completes"

  artifacts:
    - path: ".github/skills/x-ipe-tool-uiux-reference/references/toolbar.compressed.json"
      description: "Precompressed toolbar (gzip+base64, 2 chunks) — primary injection source"

    - path: ".github/skills/x-ipe-tool-uiux-reference/references/toolbar.min.js"
      description: "Uncompressed toolbar (~20KB) — reference only, not injected directly"

    - path: ".github/copilot/mcp-config.json"
      description: "MCP configuration with Chrome DevTools MCP server"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Theme mode — execute reference with URL only"
      given: "url=https://example.com, no auth, user picks colors and clicks Create Theme"
      when: "execute uiux-reference"
      then: "success=true, toolbar injected via 2-call compressed injection, colors saved, brand-theme-creator invoked"

    - name: "Mockup mode — analyze then generate"
      given: "url=https://example.com, user selects areas, clicks Analyze, then Generate"
      when: "execute uiux-reference"
      then: "success=true, referenced-elements.json created, mockup-v1.html generated"

    - name: "Execute reference with auth URL"
      given: "url=https://app.example.com, auth_url=https://login.example.com"
      when: "execute uiux-reference"
      then: "auth page opened first, then target, toolbar injected"

    - name: "Screenshot of element without UID (LL-001)"
      given: "selected element is generic <div> without ARIA role"
      when: "take element screenshot"
      then: "agent adds temporary ARIA attributes, takes snapshot, captures correct element, removes ARIA attributes"

  error_cases:
    - name: "Missing URL parameter"
      given: "no url provided"
      when: "execute uiux-reference"
      then: "error reported: URL is required"

    - name: "Page load failure"
      given: "url=https://nonexistent.example.com"
      when: "execute uiux-reference"
      then: "error reported: Failed to load page"

    - name: "Toolbar init failure"
      given: "page has strict CSP blocking eval"
      when: "inject toolbar"
      then: "error reported: Toolbar failed to initialize, retry once"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All CDP tool references present (navigate_page, evaluate_script, take_screenshot)"
    - "Compressed 2-call injection procedure documented (toolbar.compressed.json)"
    - "referenced-elements.json is single source of truth (no session files)"
    - "LL-001 ARIA workaround for elements without UIDs incorporated"
    - "Authentication flow documented"
    - "Both theme and mockup operations documented"
    - "Error scenarios handled"
