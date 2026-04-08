# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-user-manual-referencer
skill_type: x-ipe-tool
version: "1.1.0"
status: candidate
created: 2026-04-07
updated: 2026-04-07

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Looks up, retrieves, and interprets instructions from user manuals stored in the knowledge base.
  Returns structured step-by-step instructions with clarity scoring. Flags unclear instructions
  for human feedback.

triggers:
  - "look up user manual"
  - "find instructions in manual"
  - "user manual reference"
  - "manual lookup"

not_for:
  - "x-ipe-tool-knowledge-extraction-user-manual: Creating/extracting user manuals (not looking up)"
  - "x-ipe-task-based-application-knowledge-extractor: Full knowledge extraction workflow"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform"
      validation: "Must be one of: lookup_instruction, get_step_by_step, troubleshoot, list_features"

    - name: kb_path
      type: string
      description: "Path to knowledge base folder containing user manual"

  optional:
    - name: query
      type: string
      default: null
      description: "Natural language query for what caller is looking for"

    - name: section_filter
      type: string
      default: null
      description: "Filter to specific section: core-features, workflows, getting-started, troubleshooting, configuration"

    - name: feature_id
      type: string
      default: null
      description: "Specific feature file name (e.g., feature01-stage-toolbox)"

    - name: clarity_threshold
      type: float
      default: 0.6
      description: "Threshold for needs_human_feedback. Caller derives from execution_temperature: strict→0.8, balanced→0.6, creative→0.4"

outputs:
  state:
    - name: status
      value: success | failure

  data:
    - name: operation_output
      type: object
      description: "Structured result with matches, steps, clarity_score, and needs_human_feedback flag"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: "name starts with 'x-ipe-tool-'"

    - id: AC-S02
      category: structure
      criterion: SKILL.md body < 600 lines
      test: line_count
      expected: "< 600"

    - id: AC-B01
      category: behavior
      criterion: lookup_instruction returns ranked matches with clarity_score
      test: execution
      expected: "matches array with relevance_score and clarity_score per match"

    - id: AC-B02
      category: behavior
      criterion: get_step_by_step parses instructions into structured steps
      test: execution
      expected: "steps array with action, element, expected_outcome per step"

    - id: AC-B03
      category: behavior
      criterion: needs_human_feedback set when clarity_score < 0.6
      test: execution
      expected: "needs_human_feedback=true with feedback_reason"

    - id: AC-B04
      category: behavior
      criterion: troubleshoot searches 07-troubleshooting.md
      test: execution
      expected: "Searches troubleshooting section and returns resolution or needs_human_feedback"

  should:
    - id: AC-B05
      category: behavior
      criterion: list_features returns structured feature and workflow listings
      test: execution
      expected: "features and workflows arrays with interaction patterns"

    - id: AC-B06
      category: behavior
      criterion: Screenshot references included in step-by-step output
      test: execution
      expected: "screenshot_ref field populated when screenshots exist"

  could:
    - id: AC-B07
      category: behavior
      criterion: Uses .kb-index.json metadata for enhanced search
      test: execution
      expected: "Tags and descriptions from index used for relevance scoring"

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-task-based-general-purpose-executor
      relationship: "called-by (executor invokes this tool skill)"

  artifacts:
    - path: "x-ipe-docs/knowledge-base/"
      description: "Knowledge base containing user manual files"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "lookup_instruction finds matching feature"
      given: "KB with user manual, query='create workflow'"
      when: "execute lookup_instruction"
      then: "Returns match for workflow01-create-new-workflow.md with high relevance"

    - name: "get_step_by_step returns structured steps"
      given: "Feature file with step-by-step instructions"
      when: "execute get_step_by_step with feature_id"
      then: "Returns steps array with action, element, expected_outcome, screenshots"

    - name: "troubleshoot finds resolution"
      given: "07-troubleshooting.md has entry matching query"
      when: "execute troubleshoot"
      then: "Returns resolution_steps"

  error_cases:
    - name: "KB path not found"
      given: "kb_path doesn't exist"
      when: "Any operation"
      then: "KB_NOT_FOUND error"

    - name: "Unclear instructions flagged"
      given: "Feature file with vague instructions"
      when: "get_step_by_step"
      then: "clarity_score < 0.6, needs_human_feedback=true"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All 4 operations produce structured output"
    - "Clarity scoring applied consistently"
    - "needs_human_feedback flag correctly set"
    - "Error scenarios handled with descriptive messages"
