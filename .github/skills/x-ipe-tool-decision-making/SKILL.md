---
name: x-ipe-tool-decision-making
description: Autonomous decision-making for AI agents in auto-proceed mode. Resolves questions, conflicts, and routing decisions using a 6-step process with sub-agent critique. Logs all decisions to decision_made_by_ai.md. Use when process_preference.auto_proceed is "auto" and a decision point is reached. Triggers on "make decision", "resolve conflict", "choose route", "decide autonomously".
---

# Decision Making Tool Skill

## Purpose

AI Agents follow this skill to autonomously resolve decision points by:
1. Classifying and analyzing problems (questions, conflicts, routing choices)
2. Studying project context and optionally searching the web
3. Getting sub-agent critique on proposed answers
4. Recording every decision to a shared audit log

---

## Important Notes

BLOCKING: This skill is ONLY invoked when `process_preference.auto_proceed` is `auto`. In `manual` and `stop_for_question` modes, within-skill questions go to the human instead.

CRITICAL: Every decision MUST be logged to `x-ipe-docs/decision_made_by_ai.md` — no silent decisions.

CRITICAL: Unresolvable problems are logged as UNRESOLVED and execution continues — this skill NEVER blocks indefinitely.

CRITICAL: Web search (Step 3) is ONLY for general knowledge questions. NEVER search for project-internal topics.

---

## About

The Decision Making Tool Skill enables AI agents to operate autonomously during `auto` mode by providing a structured 6-step process for resolving questions, conflicts, and routing decisions that would normally require human input.

**Key Concepts:**

- **Decision Context** — Input structure containing the calling skill, task ID, and an array of problems to resolve
- **Problem Types** — `question` (clarifying questions), `conflict` (requirement/design conflicts), `routing` (choosing among multiple next actions)
- **Decision Log** — Shared audit file at `x-ipe-docs/decision_made_by_ai.md` with registry table and detail sections
- **Decision ID** — Globally unique identifier (D-001, D-002, ...) auto-incremented per project
- **UNRESOLVED** — Status for problems that cannot be confidently resolved; logged with follow-up required flag

---

## When to Use

```yaml
triggers:
  - "make decision"
  - "resolve conflict"
  - "choose route"
  - "decide autonomously"
  - "auto-proceed decision point"
  - "within-skill question in auto mode"

not_for:
  - "Human-answered questions in manual/stop_for_question mode"
  - "Task board management (use x-ipe+all+task-board-management)"
  - "Feature board updates (use x-ipe+feature+feature-board-management)"
```

---

## Input Parameters

```yaml
input:
  operation: "resolve_decisions"
  decision_context:
    calling_skill: "{skill name}"           # Required — e.g. "x-ipe-task-based-ideation-v2"
    task_id: "{TASK-XXX}"                   # Required — current task ID
    feature_id: "{FEATURE-XXX | N/A}"       # Optional — default: N/A
    workflow_name: "{name | N/A}"           # Required — workflow name or N/A for free-mode
    problems:                               # Required — non-empty array
      - problem_id: "P1"                   # Required — unique within this call
        description: "{what needs to be decided}"  # Required
        type: "question | conflict | routing"      # Required — enum
        options: ["option A", "option B"]          # Optional — known alternatives
        related_files: ["path1", "path2"]          # Optional — files for context
```

### Input Initialization

```xml
<input_init>
  <field name="decision_context.calling_skill" source="Calling skill provides its own name">
    <validation>MUST be non-empty string. FAIL FAST if missing.</validation>
  </field>
  <field name="decision_context.task_id" source="Calling skill provides current task ID">
    <validation>MUST be non-empty string matching TASK-{NNN} format. FAIL FAST if missing.</validation>
  </field>
  <field name="decision_context.feature_id" source="Calling skill provides or defaults to N/A">
    <validation>Default: "N/A". Accept any string.</validation>
  </field>
  <field name="decision_context.workflow_name" source="Calling skill provides workflow name or N/A">
    <validation>MUST be non-empty string. FAIL FAST if missing.</validation>
  </field>
  <field name="decision_context.problems" source="Calling skill provides problems array">
    <validation>
      MUST be non-empty array.
      Each problem MUST have: problem_id (unique), description (non-empty), type (question|conflict|routing).
      FAIL FAST if any validation fails.
    </validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Decision context provided</name>
    <verification>decision_context has calling_skill, task_id, workflow_name, and non-empty problems array</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All problems have required fields</name>
    <verification>Each problem has problem_id, description, and type (question|conflict|routing)</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: resolve_decisions

**When:** AI agent in `auto` mode reaches a decision point (question, conflict, or routing choice)

```xml
<operation name="resolve_decisions">

  <step_1>
    <name>Identify & Classify</name>
    <action>
      1. Read all problems from decision_context.problems
      2. Validate each problem has required fields (problem_id, description, type)
      3. Classify each by type:
         - question: clarifying question that would normally go to human
         - conflict: contradictory requirements, designs, or patterns
         - routing: multiple next-step options to choose from
      4. Identify quick-resolve candidates:
         - Routing with single option → auto-select that option
         - Questions with answer directly stated in related_files → fast-path
      5. Order problems: quick-resolve first, then complex
    </action>
    <constraints>
      - FAIL FAST if problems array is empty or any problem missing required fields
    </constraints>
    <output>Classified problem list with resolution strategy per problem</output>
  </step_1>

  <step_2>
    <name>Study Project Context</name>
    <action>
      FOR EACH problem:
      1. Read all files listed in problem.related_files
         - Skip non-existent files with warning (do not fail)
         - Skip binary files (images, PDFs)
      2. Read the calling skill's SKILL.md:
         - Locate at .github/skills/{calling_skill}/SKILL.md
         - Understand the decision point's context within the skill procedure
      3. IF feature_id != "N/A":
         - Derive epic number from feature_id (FEATURE-044-A → EPIC-044)
         - Read specification: x-ipe-docs/requirements/EPIC-{nnn}/FEATURE-{nnn}-{X}/specification.md
         - Read technical design: x-ipe-docs/requirements/EPIC-{nnn}/FEATURE-{nnn}-{X}/technical-design.md (if exists)
      4. Scan x-ipe-docs/requirements/requirement-details-part-*.md for the relevant EPIC section
      5. Formulate initial proposed answer/solution for each problem
    </action>
    <constraints>
      - Read at most 10 files per problem to bound context window usage
      - Skip binary files — only read text-based files
    </constraints>
    <output>Project context gathered, initial proposed answers formulated</output>
  </step_2>

  <step_3>
    <name>Web Search (Optional)</name>
    <action>
      FOR EACH problem WHERE type == "question":
      1. Evaluate whether this is a general knowledge question or project-specific:
         - General: industry standards, best practices, compliance rules, library/API usage
         - Project-specific: references internal code, features, configs, or project files → SKIP
      2. IF general:
         - Formulate 1-2 focused search queries
         - Execute web search (use web_fetch or equivalent)
         - Extract relevant findings (best practices, standards, recommendations)
         - Limit: max 3 searches per problem
      3. IF project-specific:
         - Skip web search
         - Log: "Skipped web search — project-specific question"
    </action>
    <constraints>
      - NEVER search for project-internal topics
      - Max 3 searches per problem, max 6 total across all problems in this call
      - If web search fails or returns no useful results: proceed without, log warning
    </constraints>
    <output>Web research findings (or "N/A — project-specific") per problem</output>
  </step_3>

  <step_4>
    <name>Sub-Agent Critique</name>
    <action>
      FOR EACH problem (batch related problems if same context):
      1. Invoke a sub-agent (explore or general-purpose) with:
         - Problem description
         - Proposed answer/solution from Steps 1-3
         - Key context findings from project docs and web research
         - Instruction: "Critique this proposed decision. Identify weaknesses,
           blind spots, and missing considerations. Suggest improvements."
      2. Receive critique feedback
      3. IF sub-agent is unavailable:
         - Log warning: "Sub-agent unavailable, proceeding without critique"
         - Continue to Step 5 with original proposed answer
    </action>
    <constraints>
      - Sub-agent prompt context must be concise (< 500 words of context)
      - If critique raises valid concerns, they MUST be addressed in Step 5
    </constraints>
    <output>Critique feedback per problem (or "N/A — sub-agent unavailable")</output>
  </step_4>

  <step_5>
    <name>Refine Answers</name>
    <action>
      FOR EACH problem:
      1. Review critique feedback from Step 4
      2. IF critique identified valid concerns:
         - Adjust proposed answer to address each concern
         - Document how each concern was addressed in the rationale
      3. IF critique found no issues:
         - Confirm original proposed answer
      4. Determine final status:
         - "resolved": confident answer found, well-supported by context
         - "unresolved": no good answer despite full 6-step process
      5. FOR "unresolved" problems:
         - Write best-effort analysis in decision field (what was found, what's unclear)
         - Explain in rationale why resolution failed (insufficient context, conflicting constraints, etc.)
         - Mark: Follow-up Required = Yes
    </action>
    <output>Final decisions array with status, decision, and rationale per problem</output>
  </step_5>

  <step_6>
    <name>Record Decisions</name>
    <action>
      1. Check if x-ipe-docs/decision_made_by_ai.md exists
         IF NOT:
           Copy template from .github/skills/x-ipe-tool-decision-making/templates/decision-log-template.md
           Place at x-ipe-docs/decision_made_by_ai.md
      2. Read existing Decision Registry table to find highest D-{NNN} ID
         IF file is new/empty: start at D-001
      3. FOR EACH decision in the final decisions array:
         a. Assign next Decision ID: D-{max+1}, D-{max+2}, ...
         b. Append row to Decision Registry table:
            | D-{NNN} | {date} | {task_id} | {feature_id} | {calling_skill} | {workflow_name} | {type} | {status emoji} | [D-{NNN}](#d-{nnn}-short-title) |
         c. Append detail section at end of file:
            ### D-{NNN}: {Short Title}
            (Full detail format — see templates/decision-log-template.md)
      4. Return complete decisions array to calling skill
    </action>
    <constraints>
      - BLOCKING: Every decision MUST be logged — no silent decisions
      - Append-only: NEVER modify or delete existing entries
      - If concurrent write detected (ID collision on read): re-read registry, use next available ID
    </constraints>
    <output>All decisions recorded in decision_made_by_ai.md, decisions array returned</output>
  </step_6>

</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  decisions:
    - problem_id: "P1"
      decision_id: "D-001"               # Assigned during Step 6
      status: "resolved | unresolved"
      decision: "{chosen answer/solution}"
      rationale: "{why this decision was made}"
    - problem_id: "P2"
      decision_id: "D-002"
      status: "resolved"
      decision: "{answer}"
      rationale: "{reasoning}"
  errors: []  # Non-fatal warnings: missing files, search failures, sub-agent unavailable
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>All problems processed</name>
    <verification>Every problem in the input has a corresponding entry in the output decisions array</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All decisions logged</name>
    <verification>Each decision has an entry in x-ipe-docs/decision_made_by_ai.md (registry row + detail section)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Decision IDs unique</name>
    <verification>No duplicate D-{NNN} IDs in the registry table</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Unresolved marked correctly</name>
    <verification>Any unresolved decision has status "unresolved" and "Follow-up Required: Yes"</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Empty problems array | Caller passed no problems | Return `success: false, errors: ["problems array is empty"]` |
| Missing required field | problem_id, description, or type missing | Return `success: false, errors: ["Problem {id} missing required field: {field}"]` |
| Invalid problem type | type not in [question, conflict, routing] | Return `success: false, errors: ["Problem {id} has invalid type: {value}"]` |
| Related file not found | Path in related_files does not exist | Skip with warning in errors array, continue processing |
| Sub-agent unavailable | Cannot invoke sub-agent for critique | Proceed without critique (Step 4 skipped), add warning to errors |
| Web search failure | Network error or no results | Proceed without web context, add warning to errors |
| Decision log file missing | First-time invocation | Create from template, then append |
| Decision ID collision | Concurrent agent wrote between read and write | Re-read registry, assign next available ID, retry |

---

## Templates

See [templates/decision-log-template.md](.github/skills/x-ipe-tool-decision-making/templates/decision-log-template.md) for the decision log file template.

## References

See [references/decision-quality-guidelines.md](.github/skills/x-ipe-tool-decision-making/references/decision-quality-guidelines.md) for quality criteria and heuristics.
