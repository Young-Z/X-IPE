---
name: x-ipe-task-based-knowledge-referencer
description: Search and reference knowledge from the knowledge base using full-text search and ontology tag search. Use when needing to find existing knowledge, lookup information, or reference KB content. Triggers on requests like "search knowledge base", "find in knowledge base", "what do we know about", "reference knowledge".
---

# Task-Based Skill: Knowledge Referencer

## Purpose

Search and reference knowledge from the knowledge base by:
1. Full-text search across KB markdown files (grep/glob)
2. Ontology entity/tag search via `x-ipe-tool-reference-ontology` (MANDATORY)
3. Optional user manual lookup via `x-ipe-tool-reference-user-manual` (when manual KB exists and query is about how-to/instructions)
4. Combining, deduplicating, ranking, and consolidating results into a unified answer

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

**Search Strategy:**
- `x-ipe-tool-reference-ontology` is **MANDATORY** — always called regardless of full-text results
- `x-ipe-tool-reference-user-manual` is **OPTIONAL** — only called when a user manual KB exists AND the query is about how-to/instructions
- Results are ranked by cross-method hit count: files found by more search methods rank higher

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-assistant-user-representative-Engineer` to get the answer.

---

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-knowledge-referencer"

  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A"

  category: "standalone"
  next_task_based_skill: "null"
  process_preference:
    interaction_mode: "interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill"

  query: ""                    # Natural language search query (required)
  kb_scope: "all"              # "all" | specific KB folder path
  include_user_manual: true    # Whether to also search user manuals
  max_results: 20              # Maximum results to return per search step
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="query" source="from human input or calling skill" />
  <field name="kb_scope" source="from human input or default 'all'" />
  <field name="include_user_manual" source="from human input or default true" />
  <field name="max_results" source="from human input or default 20" />
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Query provided</name>
    <verification>A non-empty natural language search query exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>KB path exists</name>
    <verification>x-ipe-docs/knowledge-base/ directory exists and is not empty</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>KB scope valid</name>
    <verification>If kb_scope is not "all", the specified folder path exists under knowledge-base/</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 1. 博学之 | 1.1 | Gather Context | Read query, determine KB scope, check if user manual exists | context gathered |
| 2. 审问之 | — | SKIP | Input is fully specified by caller; no ambiguity to resolve | — |
| 3. 慎思之 | — | SKIP | No design decisions; procedural execution | — |
| 4. 明辨之 | — | SKIP | Single valid approach; no alternatives | — |
| 5. 笃行之 | 5.1 | Execute Full-Text Search | Grep/glob across KB markdown files for query terms | results collected |
| | 5.2 | Execute Ontology Search | Load x-ipe-tool-reference-ontology, run search operation | ontology results collected |
| | 5.3 | Execute User Manual Lookup | IF include_user_manual AND manual KB exists: load x-ipe-tool-reference-user-manual | manual results collected (or skipped) |
| | 5.4 | Combine & Consolidate | Merge results, deduplicate, rank by relevance, produce summary | consolidated output |
| | 5.5 | Complete | Verify DoD | DoD validated |
| 6. 继续执行 | 6.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| | 6.2 | Execute Next Action | Load skill, execute | Execution started |

BLOCKING: Step 5.2 (ontology search) is MANDATORY — never skip it.
BLOCKING: Step 5.4 must not run until steps 5.1, 5.2, and 5.3 (if applicable) are complete.

---

## Execution Procedure

```xml
<procedure name="knowledge-referencer">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之（Gather）">
    <step_1_1>
      <name>Gather Context</name>
      <action>
        1. Read the input query — this is the search term(s) for all search methods
        2. Determine KB scope:
           - IF kb_scope == "all": search_path = "x-ipe-docs/knowledge-base/"
           - ELSE: search_path = "x-ipe-docs/knowledge-base/{kb_scope}/"
           - Verify the search_path directory exists; if not, BLOCK with error
        3. Check if a user manual KB exists at search_path:
           - Look for 04-core-features/ directory OR 01-overview.md file
           - Set has_user_manual = true if found, false otherwise
        4. Determine if user manual lookup is applicable:
           - user_manual_applicable = include_user_manual AND has_user_manual
      </action>
      <output>search_path, has_user_manual, user_manual_applicable established</output>
    </step_1_1>
  </phase_1>

  <phase_2 name="审问之（Inquire）">SKIP — Input is fully specified by caller; no ambiguity to resolve.</phase_2>
  <phase_3 name="慎思之（Analyze）">SKIP — No design decisions; procedural execution only.</phase_3>
  <phase_4 name="明辨之（Discern）">SKIP — Single valid approach; no alternatives to evaluate.</phase_4>

  <phase_5 name="笃行之（Execute）">
    <step_5_1>
      <name>Execute Full-Text Search</name>
      <action>
        1. Use grep to search across all .md files under search_path for the query terms
        2. Break query into individual keywords if multi-word; search for each
        3. Collect results up to max_results:
           - file_path: path to the matched file
           - matched_lines: the line(s) containing the match
           - context: 2-3 lines of surrounding context
        4. Sort by number of keyword hits per file (descending)
      </action>
      <output>full_text_matches: [{file_path, matched_lines, context}]</output>
    </step_5_1>

    <step_5_2>
      <name>Execute Ontology Search (MANDATORY)</name>
      <action>
        1. Load x-ipe-tool-reference-ontology skill
        2. Call its search operation with the query
        3. Collect entity matches up to max_results:
           - entity_id: ontology entity identifier
           - label: human-readable entity name
           - node_type: entity type in ontology (concept, feature, component, etc.)
           - source_files: KB files linked to this entity
           - dimensions: ontology dimensions/tags associated
           - relevance: match relevance score
        4. This step is MANDATORY — always execute regardless of Step 5.1 results
      </action>
      <constraints>
        - BLOCKING: This step MUST always execute — do NOT skip
      </constraints>
      <output>ontology_matches: [{entity_id, label, node_type, source_files, dimensions, relevance}]</output>
    </step_5_2>

    <step_5_3>
      <name>Execute User Manual Lookup (OPTIONAL)</name>
      <action>
        1. IF user_manual_applicable == false: SKIP this step, set user_manual_matches = []
        2. IF user_manual_applicable == true:
           a. Load x-ipe-tool-reference-user-manual skill
           b. Call its lookup_instruction operation with the query
           c. Collect matches:
              - file_path: path to the manual document
              - title: section or document title
              - relevance_score: how closely the manual entry matches the query
              - interaction_pattern: the how-to/instruction content
      </action>
      <output>user_manual_matches: [{file_path, title, relevance_score, interaction_pattern}] (or empty)</output>
    </step_5_3>

    <step_5_4>
      <name>Combine & Consolidate</name>
      <action>
        1. Collect all source file paths from all three result sets
        2. Deduplicate by source file path — if the same file appears in multiple search results,
           merge into a single entry noting which methods found it
        3. Rank results by cross-method hit count:
           - File found by 3 methods (full-text + ontology + manual) → highest relevance
           - File found by 2 methods → medium relevance
           - File found by 1 method → standard relevance
           Within same hit count, sort by individual relevance scores
        4. Produce a consolidated summary:
           - List the top matches (up to max_results total) with source file and why they matched
           - Synthesize a brief answer that addresses the original query using the found content
           - Note which search methods contributed to each result
        5. Compute total_results count (unique files across all methods)
      </action>
      <output>consolidated_results object with ranked matches and synthesized summary</output>
    </step_5_4>

    <step_5_5>
      <name>Complete</name>
      <action>
        1. Verify all DoD checkpoints
        2. Produce task_completion_output
      </action>
      <output>Task completed with consolidated knowledge reference output</output>
    </step_5_5>
  </phase_5>

  <phase_6 name="继续执行（Continue Execute）">
    <step_6_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Invoke x-ipe-assistant-user-representative-Engineer with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the context and full output to decide best next action."
          → DAO studies the complete context and decides the best next action
        ELSE (interact-with-human):
          → Present results and next task suggestion to human and wait for instruction
      </action>
      <constraints>
        - BLOCKING (interact-with-human): Human MUST confirm or redirect before proceeding
        - BLOCKING (auto): Proceed after DoD verification; auto-select next task via DAO
      </constraints>
      <output>Next action decided with execution context</output>
    </step_6_1>
    <step_6_2>
      <name>Execute Next Action</name>
      <action>
        Based on the decision from Step 6.1:
        1. Load the target task-based skill's SKILL.md
        2. Generate an execution plan from the skill's Execution Flow table
        3. Start execution from the skill's first phase/step
      </action>
      <constraints>
        - MUST load the skill before executing — do not skip skill loading
        - Execution follows the target skill's procedure, not this skill's
      </constraints>
      <output>Next task execution started</output>
    </step_6_2>
  </phase_6>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill: "null"
  process_preference:
    interaction_mode: "{from input}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links: []
  query: "{from input}"
  total_results: 0
  consolidated_results:
    full_text_matches: [{file_path, matched_lines, context}]
    ontology_matches: [{entity_id, label, node_type, source_files, dimensions, relevance}]
    user_manual_matches: [{file_path, title, relevance_score, interaction_pattern}]
    summary: "Synthesized answer from all search results"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Full-text search executed</name>
    <verification>Grep/glob search was run against KB markdown files under the determined scope</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Ontology search executed</name>
    <verification>x-ipe-tool-reference-ontology was loaded and its search operation was called</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>User manual lookup handled</name>
    <verification>Either user manual lookup was executed (when applicable) or explicitly skipped with reason</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Results deduplicated</name>
    <verification>No duplicate source file paths appear in the final consolidated output</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Results ranked</name>
    <verification>Results are ordered by cross-method hit count and individual relevance</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Summary synthesized</name>
    <verification>A human-readable summary addressing the original query is present in output</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output structure complete</name>
    <verification>task_completion_output contains all required fields including consolidated_results</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Multi-Method Search

**When:** Searching for knowledge in the KB
**Then:**
```
1. Run full-text grep across .md files
2. Run ontology entity search (MANDATORY)
3. Optionally run user manual lookup
4. Merge, deduplicate, rank by cross-method hits
5. Synthesize consolidated answer
```

### Pattern: Scoped Search

**When:** User specifies a particular KB area
**Then:**
```
1. Validate kb_scope path exists under knowledge-base/
2. Limit all search methods to that path
3. Report scope in output so user knows search was limited
```

### Pattern: Graceful Skip

**When:** User manual KB does not exist or is not relevant
**Then:**
```
1. Check for 04-core-features/ or 01-overview.md
2. If absent: set user_manual_matches = [], continue
3. Do NOT fail — proceed with full-text + ontology results only
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip ontology search | Misses structured entity/tag matches | Always run ontology search |
| Return raw grep output | Hard to consume, duplicates across methods | Deduplicate and consolidate |
| Skip user manual without checking | May miss relevant how-to content | Check if manual KB exists first |
| Search only by exact query string | Misses partial matches on individual keywords | Break query into keywords |
| Return all results unsorted | User overwhelmed, key results buried | Rank by cross-method hit count |

---

## Examples

See [references/examples.md](x-ipe-docs/skill-meta/x-ipe-task-based-knowledge-referencer/candidate/references/examples.md) for concrete execution examples.
