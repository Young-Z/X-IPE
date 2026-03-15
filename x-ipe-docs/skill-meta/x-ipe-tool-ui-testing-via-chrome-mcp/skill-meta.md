# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-ui-testing-via-chrome-mcp
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
created: 2026-03-12
updated: 2026-03-12

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Execute sets of frontend-ui acceptance test cases via Chrome DevTools MCP,
  following UI testing best practices (selector strategy, wait patterns,
  screenshot-on-failure, grouped execution with per-TC pass/fail reporting).

triggers:
  - "run UI tests via chrome"
  - "execute frontend-ui acceptance tests"
  - "browser test via chrome devtools"
  - "UI testing via chrome MCP"

not_for:
  - "backend-api tests: use x-ipe-tool-implementation-* skills"
  - "unit tests: use language-specific tool skills"
  - "test case generation: use x-ipe-task-based-feature-acceptance-test (Phase 1-3)"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform"
      validation: "Must be 'execute_ui_tests'"

    - name: test_cases
      type: array
      description: "Array of frontend-ui test case objects from acceptance-test-cases.md"
      validation: "Each TC must have id, title, steps[], expected_results[]"

    - name: target_url
      type: string
      description: "Base URL of the application under test"
      validation: "Must be a valid URL (http:// or https://)"

  optional:
    - name: screenshot_on_failure
      type: boolean
      default: true
      description: "Capture screenshot when a test case fails"

    - name: screenshot_dir
      type: string
      default: "x-ipe-docs/requirements/{feature_id}/screenshots/"
      description: "Directory to save failure screenshots"

    - name: wait_timeout_ms
      type: number
      default: 5000
      description: "Default timeout in ms for wait_for operations"

    - name: viewport
      type: string
      default: null
      description: "Viewport size (e.g., '1280x720'). If null, uses browser default."

outputs:
  state:
    - name: status
      value: success | partial_failure | failure

  artifacts:
    - name: screenshots
      type: directory
      path: "{screenshot_dir}"
      description: "Screenshots of failed test cases"

  data:
    - name: operation_output
      type: object
      description: "Structure containing per-TC results, summary metrics, and errors"

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
      expected: name equals 'x-ipe-tool-ui-testing-via-chrome-mcp'

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

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Tool executes test cases via chrome-devtools MCP tools
      test: execution
      expected: Uses navigate_page, take_snapshot, click, fill, wait_for, take_screenshot

    - id: AC-B02
      category: behavior
      criterion: Tool reports per-TC pass/fail with reasons
      test: execution
      expected: Each TC in results has status (pass/fail/blocked) and notes

    - id: AC-B03
      category: behavior
      criterion: Tool captures screenshots on failure
      test: execution
      expected: screenshot file saved when TC fails and screenshot_on_failure is true

    - id: AC-B04
      category: behavior
      criterion: Tool uses selector priority order
      test: content_check
      expected: Documents priority data-testid > id > aria-label > CSS selector

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
      criterion: Input Initialization subsection present
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-B05
      category: behavior
      criterion: Tool handles navigation failures gracefully
      test: execution
      expected: If page doesn't load, TC marked blocked with reason

  could:
    - id: AC-C07
      category: content
      criterion: Best practices reference document provided
      test: file_exists
      expected: references/ui-test-best-practices.md exists

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-task-based-feature-acceptance-test
      relationship: caller (invokes this tool for frontend-ui test execution)

  artifacts:
    - path: "x-ipe-docs/requirements/{feature_id}/acceptance-test-cases.md"
      description: "Test cases classified as frontend-ui by the AC skill"

  tools:
    - name: chrome-devtools-mcp
      description: "Chrome DevTools MCP server must be available and connected"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Execute 3 UI test cases successfully"
      given: "3 frontend-ui TCs with valid selectors and a running app"
      when: "execute_ui_tests with target_url and test_cases"
      then: "All 3 TCs pass, summary shows 3/3, no screenshots"

    - name: "Mixed pass/fail results"
      given: "2 passing TCs and 1 failing TC"
      when: "execute_ui_tests with screenshot_on_failure=true"
      then: "2 pass, 1 fail, screenshot saved for failed TC"

  error_cases:
    - name: "App not reachable"
      given: "target_url points to unreachable server"
      when: "execute_ui_tests"
      then: "All TCs marked blocked, error UI_APP_UNREACHABLE"

    - name: "Selector not found"
      given: "TC references non-existent selector"
      when: "execute_ui_tests"
      then: "TC marked fail with UI_SELECTOR_NOT_FOUND note"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs match schema"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "Chrome MCP tools used correctly"
