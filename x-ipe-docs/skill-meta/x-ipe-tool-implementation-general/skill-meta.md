# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill: General Implementation
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-implementation-general
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
created: 2026-03-05
updated: 2026-03-05

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  General-purpose fallback implementation tool skill that handles any tech stack
  not covered by language-specific tool skills, using research-driven implementation.

triggers:
  - "No matching language-specific tool skill"
  - "Orchestrator fallback for unmapped tech stack"
  - "General implementation needed"

not_for:
  - "x-ipe-tool-implementation-python: for Python stacks"
  - "x-ipe-tool-implementation-html5: for HTML/CSS/JS stacks"
  - "x-ipe-tool-implementation-typescript: for TypeScript stacks"
  - "x-ipe-tool-implementation-java: for Java stacks"
  - "x-ipe-tool-implementation-mcp: for MCP servers"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Always 'implement'"
      validation: "Must be 'implement'"

    - name: aaa_scenarios
      type: array
      description: "Tagged AAA scenarios from orchestrator"

    - name: source_code_path
      type: string
      description: "Path to source directory"

    - name: feature_context
      type: object
      description: "Feature metadata (id, title, design link, spec link)"

  optional:
    - name: test_code_path
      type: string
      default: "tests/"
      description: "Path to test directory"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: implementation_files
      type: file
      path: "{source_code_path}/*"
      description: "Created source files"
    - name: test_files
      type: file
      path: "{test_code_path}/*"
      description: "Created test files"

  data:
    - name: operation_output
      type: object
      description: "Standard tool skill output: implementation_files, test_files, test_results, lint_status"

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
      expected: file contains at least 2 examples

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    # CONTENT
    - id: AC-C01
      category: content
      criterion: Operations section has "implement" operation
      test: content_check
      expected: '<operation name="implement">' present

    - id: AC-C02
      category: content
      criterion: Research-first approach enforced
      test: content_check
      expected: BLOCKING constraint requires research before implementation

    - id: AC-C03
      category: content
      criterion: Standard tool skill I/O contract followed
      test: content_check
      expected: Input has aaa_scenarios, source_code_path, feature_context; Output has implementation_files, test_files, test_results, lint_status

    - id: AC-C04
      category: content
      criterion: Error handling table present
      test: table_parse
      expected: columns [Error, Cause, Resolution] with at least 3 entries

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Identifies language from source path
      test: execution
      expected: stack_identified field populated in output

    - id: AC-B02
      category: behavior
      criterion: Maps AAA Assert clauses to test assertions
      test: execution
      expected: test_results count matches Assert clause count

  should:
    - id: AC-C05
      category: content
      criterion: Input Initialization present
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C06
      category: content
      criterion: Key Concepts section in About
      test: content_check
      expected: "**Key Concepts:**"

  could:
    - id: AC-C07
      category: content
      criterion: Handles stack identification failure gracefully
      test: content_check
      expected: STACK_UNIDENTIFIABLE error documented

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-task-based-code-implementation
      relationship: caller
      description: Orchestrator that invokes this tool skill

  artifacts:
    - path: ".github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md"
      description: "Tool skill I/O contract specification"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Go/Gin API implementation"
      given: "source_code_path with go.mod, 3 @backend scenarios"
      when: "execute implement operation"
      then: "Identifies Go/Gin, implements handlers, 3/3 tests pass"

    - name: "Rust/Actix implementation"
      given: "source_code_path with Cargo.toml, 2 @backend scenarios"
      when: "execute implement operation"
      then: "Identifies Rust/Actix, implements handlers, 2/2 tests pass"

  error_cases:
    - name: "Stack unidentifiable"
      given: "Empty source_code_path, generic scenarios"
      when: "execute implement operation"
      then: "Returns STACK_UNIDENTIFIABLE error, signals orchestrator"

    - name: "No test framework available"
      given: "Rare language with no standard test framework"
      when: "execute implement operation"
      then: "Returns NO_TEST_FRAMEWORK error"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs match standard tool skill contract"
    - "DoD checkpoints all verified"
    - "Research completed before implementation"
    - "Every AAA Assert maps to a test assertion"

  judge_agent:
    - criterion: "Implementation quality for unknown stack"
      rubric: |
        5: Excellent - follows discovered best practices, all tests pass
        4: Good - minor style issues but functional
        3: Acceptable - works but doesn't follow stack conventions
        2: Poor - significant issues, some tests fail
        1: Fail - cannot implement for the stack
