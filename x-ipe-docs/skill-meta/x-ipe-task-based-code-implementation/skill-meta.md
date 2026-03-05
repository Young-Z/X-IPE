# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based: Code Implementation (Orchestrator)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-based-code-implementation
skill_type: x-ipe-task-based
version: "2.0.0"
status: candidate
created: 2026-03-01
updated: 2026-03-05

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Orchestrates feature implementation by generating AAA test scenarios from specification,
  routing to language-specific tool skills via semantic matching, and validating all Assert
  clauses pass. Delegates to x-ipe-meta-skill-creator for skill files and mcp-builder for
  MCP servers.

triggers:
  - "implement feature"
  - "write code"
  - "develop feature"
  - "code implementation"

not_for:
  - "x-ipe-task-based-code-refactor: for refactoring existing code"
  - "x-ipe-task-based-bug-fix: for fixing bugs in existing code"
  - "x-ipe-meta-skill-creator: for creating skills directly (but delegated to by this skill)"

# ─────────────────────────────────────────────────────────────
# WORKFLOW POSITION
# ─────────────────────────────────────────────────────────────
workflow:
  category: feature-stage
  phase: "Code Implementation"
  next_task_based_skill: "Feature Acceptance Test"
  human_review: false

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: auto_proceed
      type: boolean
      default: false
      description: Whether to auto-proceed to next task

    - name: feature_id
      type: string
      description: "Feature ID to implement"
      validation: "must match FEATURE-\\d+-[A-Z]"

    - name: program_type
      type: string
      description: "Implementation type from technical design"
      validation: "one of: frontend, backend, fullstack, cli, library, skills, mcp"

    - name: tech_stack
      type: array
      description: "Technologies used, from technical design"

  optional:
    - name: execution_mode
      type: string
      default: "free-mode"
      description: "free-mode or workflow-mode"

    - name: git_strategy
      type: string
      default: "main-branch-only"
      description: "Git branching strategy"

outputs:
  state:
    - name: category
      value: feature-stage
    - name: status
      value: completed | blocked
    - name: next_task_based_skill
      value: "Feature Acceptance Test"
    - name: require_human_review
      value: false
    - name: auto_proceed
      value: "${inputs.auto_proceed}"

  artifacts:
    - name: implementation_files
      type: directory
      path: "src/"
      description: "Implemented source code files"
    - name: test_files
      type: directory
      path: "tests/"
      description: "Generated test files"

  data:
    - name: aaa_scenarios
      type: object
      description: "Generated AAA scenarios with coverage summary"
    - name: validation_report
      type: object
      description: "Aggregated pass/fail report from tool skill outputs"

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
      expected: name and description fields present, description mentions orchestrator

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 4 examples

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
      expected: Purpose, Important Notes, Input Parameters, DoR, Execution Flow, Execution Procedure, Output Result, DoD, Patterns, Examples

    - id: AC-C02
      category: content
      criterion: Step 4 generates AAA scenarios (not test-generation)
      test: content_check
      expected: Step 4 mentions "AAA", "Arrange", "Act", "Assert" and does NOT say "INVOKE x-ipe-tool-test-generation" as primary action

    - id: AC-C03
      category: content
      criterion: Step 5 has semantic routing to tool skills
      test: content_check
      expected: Step 5 mentions "x-ipe-tool-implementation-*", "semantic", "route"

    - id: AC-C04
      category: content
      criterion: Step 5 has special-case delegations preserved
      test: content_check
      expected: Step 5 mentions "x-ipe-meta-skill-creator" for skills and "mcp-builder" for MCP

    - id: AC-C05
      category: content
      criterion: Step 6 validates Assert clauses
      test: content_check
      expected: Step 6 mentions "Assert clauses", "pass/fail", "integration"

    - id: AC-C06
      category: content
      criterion: Phase 1 coexistence with test-generation documented
      test: content_check
      expected: Important Notes mentions fallback to x-ipe-tool-test-generation

    - id: AC-C07
      category: content
      criterion: Tool skill I/O contract in references
      test: content_check
      expected: implementation-guidelines.md has "tool_skill_input" and "tool_skill_output" YAML blocks

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Standard feature generates AAA scenarios and routes to tool skills
      test: execution
      expected: Step 4 produces tagged scenarios, Step 5 routes to matching skills

    - id: AC-B02
      category: behavior
      criterion: Skills-type feature delegates to skill-creator
      test: execution
      expected: program_type "skills" triggers delegation in Step 5, skips Steps 4 and 6

    - id: AC-B03
      category: behavior
      criterion: Output YAML has correct structure
      test: yaml_validate
      expected: category is first field, all required fields present

  should:
    - id: AC-C08
      category: content
      criterion: Input Initialization subsection present
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C09
      category: content
      criterion: Failure handling documented
      test: content_check
      expected: implementation-guidelines.md has retry and fallback procedures

    - id: AC-C10
      category: content
      criterion: Context budget strategy for large features
      test: content_check
      expected: implementation-guidelines.md mentions per-layer batching for >20 components

  could:
    - id: AC-C11
      category: content
      criterion: Mermaid diagrams in examples
      test: content_check
      expected: examples.md includes visual flow

  wont:
    - id: AC-W01
      criterion: Board status updates
      reason: Handled by category skill, not task-based skill

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-workflow-task-execution
      relationship: prerequisite
      description: Must be learned before executing this skill

    - name: x-ipe+feature+feature-board-management
      relationship: integration
      description: Called for feature data model query

    - name: x-ipe-tool-test-generation
      relationship: fallback
      description: Phase 1 fallback when AAA generation fails

    - name: x-ipe-meta-skill-creator
      relationship: delegation
      description: Delegation target for program_type "skills"

    - name: mcp-builder
      relationship: delegation
      description: Delegation target for MCP server features

    - name: x-ipe-tool-implementation-general
      relationship: dependency
      description: Fallback tool skill for unmapped tech stacks

  artifacts:
    - path: "x-ipe-docs/requirements/FEATURE-XXX/technical-design.md"
      description: "Technical design must exist before implementation"
    - path: "x-ipe-docs/requirements/FEATURE-XXX/specification.md"
      description: "Feature specification for AAA scenario generation"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Standard fullstack feature with AAA"
      given: "Feature with tech_stack [Python/Flask, HTML/CSS] and specification with 3 ACs"
      when: "Execute code-implementation skill"
      then: "AAA scenarios generated, routed to python + html5 tool skills, all Asserts pass"

    - name: "Skills-type feature delegation"
      given: "Feature with program_type 'skills' and tech_stack [Markdown/SKILL.md]"
      when: "Execute code-implementation skill"
      then: "Delegates to x-ipe-meta-skill-creator, skips AAA generation and validation"

  edge_cases:
    - name: "AAA generation fallback"
      given: "Specification has vague acceptance criteria"
      when: "AAA generation fails"
      then: "Falls back to x-ipe-tool-test-generation (Phase 1)"

    - name: "No matching tool skill"
      given: "tech_stack entry 'Rust/Actix' with no matching tool skill"
      when: "Semantic routing runs"
      then: "Assigns x-ipe-tool-implementation-general as fallback"

    - name: "Large feature (>20 components)"
      given: "Technical design with 25 components"
      when: "AAA generation runs"
      then: "Per-layer batching: backend first, then frontend"

  error_cases:
    - name: "Tool skill fails on retry"
      given: "Backend tool skill fails twice"
      when: "Retry attempted"
      then: "Preserves passing results from other skills, escalates to human"

    - name: "Integration failure"
      given: "Unit-level tool skills pass but @integration fails"
      when: "Validation gate runs @integration scenarios"
      then: "Reports cross-layer contract mismatch to human"

  blocking:
    - name: "Feature not designed"
      given: "Feature status is 'Refined' (not 'Designed')"
      when: "DoR check runs"
      then: "BLOCKED with 'Feature status must be Designed'"

    - name: "Technical design missing"
      given: "No technical-design.md file"
      when: "DoR check runs"
      then: "BLOCKED with 'Technical design document not found'"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs.artifacts exist"
    - "Output YAML validates against schema"
    - "DoD checkpoints all verified"
    - "AAA scenarios have coverage for all ACs"
    - "Tool skill I/O contract followed"

  judge_agent:
    - criterion: "Orchestrator flow quality"
      rubric: |
        5: All AAA scenarios correct, routing accurate, validation thorough
        4: Minor gaps in coverage or routing
        3: Acceptable but missing edge case scenarios
        2: Significant routing or validation issues
        1: Fails to generate AAA or route correctly
