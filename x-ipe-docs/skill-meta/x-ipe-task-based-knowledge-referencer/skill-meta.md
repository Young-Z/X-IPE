# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based: Knowledge Referencer
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-based-knowledge-referencer
skill_type: x-ipe-task-based
version: "1.0.0"
status: candidate
created: 2026-02-24
updated: 2026-02-24

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Search and reference knowledge from the knowledge base by combining full-text search
  across KB markdown files with ontology tag search (via x-ipe-tool-reference-ontology)
  and optional user manual lookup (via x-ipe-tool-reference-user-manual). Consolidates
  results into a unified, deduplicated, ranked answer.

triggers:
  - "search knowledge base"
  - "find in knowledge base"
  - "reference knowledge"
  - "lookup knowledge"
  - "knowledge search"
  - "what do we know about"

not_for:
  - "Creating/editing KB content — use x-ipe-tool-kb-librarian"
  - "Extracting knowledge from applications — use x-ipe-task-based-application-knowledge-extractor"

# ─────────────────────────────────────────────────────────────
# WORKFLOW POSITION
# ─────────────────────────────────────────────────────────────
workflow:
  category: standalone
  phase: null
  next_task_based_skill: null
  human_review: false

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: query
      type: string
      description: Natural language search query

  optional:
    - name: kb_scope
      type: string
      default: "all"
      description: '"all" to search entire KB, or a specific KB folder path'

    - name: include_user_manual
      type: boolean
      default: true
      description: Whether to also search user manuals when a user manual KB exists

    - name: max_results
      type: integer
      default: 20
      description: Maximum results to return per search step

outputs:
  state:
    - name: category
      value: standalone
    - name: status
      value: completed | blocked
    - name: next_task_based_skill
      value: null

  data:
    - name: consolidated_results
      type: object
      description: |
        Combined search results with the following structure:
        - full_text_matches: [{file_path, matched_lines, context}]
        - ontology_matches: [{entity_id, label, node_type, source_files, dimensions, relevance}]
        - user_manual_matches: [{file_path, title, relevance_score, interaction_pattern}]
        - summary: Synthesized answer from all search results
    - name: total_results
      type: integer
      description: Total number of unique results across all search methods

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name and description fields present

    - id: AC-S02
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-C01
      category: content
      criterion: Execution Flow table uses 5-phase structure with correct phases
      test: table_parse
      expected: Phases 博学之, 审问之(SKIP), 慎思之(SKIP), 明辨之(SKIP), 笃行之, 继续执行

    - id: AC-C02
      category: content
      criterion: x-ipe-tool-reference-ontology is MANDATORY in execution
      test: content_check
      expected: Step 5.2 always invokes x-ipe-tool-reference-ontology

    - id: AC-C03
      category: content
      criterion: x-ipe-tool-reference-user-manual is conditional
      test: content_check
      expected: Step 5.3 conditionally invokes x-ipe-tool-reference-user-manual

    - id: AC-C04
      category: content
      criterion: Consolidation step deduplicates and ranks results
      test: content_check
      expected: Step 5.4 merges, deduplicates, and ranks results

    - id: AC-C05
      category: content
      criterion: DoR ≤ 5 checkpoints and DoD ≤ 10 checkpoints
      test: content_check
      expected: DoR has at most 5, DoD has at most 10

    - id: AC-B01
      category: behavior
      criterion: Full-text search finds matching KB markdown files
      test: execution
      expected: Grep/glob across x-ipe-docs/knowledge-base/ returns matched lines

    - id: AC-B02
      category: behavior
      criterion: Ontology search returns entity matches
      test: execution
      expected: x-ipe-tool-reference-ontology returns entities with labels and dimensions

    - id: AC-B03
      category: behavior
      criterion: User manual lookup is skipped when no manual KB exists
      test: execution
      expected: Step 5.3 skips gracefully when manual KB is absent

  should:
    - id: AC-C06
      category: content
      criterion: Output includes synthesized summary
      test: content_check
      expected: consolidated_results.summary field is populated

    - id: AC-C07
      category: content
      criterion: Scoped search respects kb_scope parameter
      test: content_check
      expected: When kb_scope is a specific path, search is limited to that path

  could:
    - id: AC-C08
      category: content
      criterion: Relevance ranking considers multiple search hit sources
      test: content_check
      expected: Files found by more search methods rank higher

  wont:
    - id: AC-W01
      criterion: Semantic/embedding-based search
      reason: Current approach uses keyword-based search; semantic search is a future enhancement

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: Search with full-text and ontology matches
      given: KB contains documents about "authentication" with ontology tags
      when: Query is "authentication"
      then: Full-text matches + ontology entity matches returned, consolidated summary produced

    - name: Search with user manual included
      given: KB has a user manual folder with 04-core-features/ and related docs
      when: Query is "how to configure export settings" with include_user_manual=true
      then: Full-text + ontology + user manual results returned

  edge_cases:
    - name: No matches found
      given: Query term does not exist in KB
      when: Search is executed
      then: Empty results with summary stating no matches found

    - name: Scoped search to specific folder
      given: KB has multiple application folders
      when: kb_scope is set to a specific app folder path
      then: Only that folder is searched

  error_cases:
    - name: KB path does not exist
      given: x-ipe-docs/knowledge-base/ is missing or empty
      when: Search is attempted
      then: Returns blocked status with clear error message

  blocking:
    - name: Ontology search is always executed
      given: Any valid query
      when: Search is run
      then: x-ipe-tool-reference-ontology is always called regardless of full-text results

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "Execution Flow has 5-phase structure with phases 2-4 skipped"
    - "x-ipe-tool-reference-ontology is MANDATORY in Step 5.2"
    - "x-ipe-tool-reference-user-manual is conditional in Step 5.3"
    - "Step 5.4 consolidates, deduplicates, and ranks results"
    - "DoR ≤ 5 checkpoints, DoD ≤ 10 checkpoints"

  judge_agent:
    - criterion: "Knowledge search is thorough and well-structured"
      rubric: |
        5: Excellent - all search methods used, results well-consolidated, clear summary
        4: Good - minor gaps in consolidation or ranking
        3: Acceptable - basic search works but consolidation incomplete
        2: Poor - missing mandatory ontology search or broken consolidation
        1: Fail - search does not execute or returns no structured output
