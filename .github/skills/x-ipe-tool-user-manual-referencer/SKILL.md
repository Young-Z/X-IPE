---
name: x-ipe-tool-user-manual-referencer
description: Look up, retrieve, and interpret instructions from user manuals stored in the knowledge base. Use when executor needs manual guidance to perform a step. Triggers on requests like "lookup user manual instruction", "get step-by-step from manual", "troubleshoot from manual", "list documented features".
---

# User Manual Referencer

## Purpose

AI Agents follow this skill to retrieve and interpret user manual instructions from the knowledge base by:
1. Looking up which manual section covers a specific task or feature
2. Extracting structured step-by-step instructions with expected outcomes
3. Troubleshooting unexpected results against documented known issues
4. Listing all documented features and workflows for discovery

---

## Important Notes

BLOCKING: This skill is **read-only** — it retrieves and interprets existing manual content. It MUST NOT create, modify, or delete any knowledge base files.

BLOCKING: Every instruction-returning operation MUST include a `clarity_score` (0.0–1.0). If `clarity_score < clarity_threshold` (default 0.6, configurable via input), set `needs_human_feedback: true` with a reason explaining which steps are unclear.

CRITICAL: Always use project-root-relative paths (e.g., `x-ipe-docs/knowledge-base/{manual-name}/04-core-features/feature01-stage-toolbox.md`) in all output references.

CRITICAL: When multiple manuals exist under `x-ipe-docs/knowledge-base/`, the caller MUST provide `kb_path` pointing to a specific manual folder. Do NOT search across all manuals.

---

## About

The User Manual Referencer is a retrieval tool that reads user manuals previously extracted into the knowledge base by `x-ipe-tool-knowledge-extraction-user-manual`. It is called by `x-ipe-task-based-general-purpose-executor` when the executor encounters a step that requires understanding how an application works — e.g., "click the Create button" or "configure the export settings".

**Key Concepts:**

- **KB Structure** — Each manual lives at `x-ipe-docs/knowledge-base/{manual-name}/` and follows a standard layout: `01-overview.md` through `08-faq-reference.md`, with `04-core-features/` and `05-common-workflows/` containing per-item files
- **Feature/Workflow Files** — Individual files like `feature01-{slug}.md` or `workflow01-{slug}.md` containing description, interaction pattern, step-by-step instructions, screenshots, and tips
- **Interaction Pattern** — Categorization of how a feature is operated: `FORM`, `MODAL`, `CLI_DISPATCH`, `NAVIGATION`, or `TOGGLE`. Used by the executor to understand what kind of UI interaction to expect
- **Clarity Score** — A 0.0–1.0 assessment of how actionable the retrieved instructions are. A step is considered vague if it lacks an action verb, element name, or expected outcome. Each vague step reduces the score by 0.15
- **Index Files** — `_index.md` provides a human-readable listing table; `.kb-index.json` provides machine-readable metadata with tags and descriptions
- **Instruction Format** — Steps follow the pattern: `[Action] Click/Type/Press... [Element] "Label" → [Expected] "You should see..."`

---

## When to Use

```yaml
triggers:
  - "lookup user manual instruction"
  - "get step-by-step from manual"
  - "how do I do X in the application"
  - "troubleshoot from manual"
  - "list documented features"
  - "find manual section for task"
  - "retrieve instructions from knowledge base"

not_for:
  - "Extracting manuals from applications — use x-ipe-tool-knowledge-extraction-user-manual"
  - "Organizing KB intake files — use x-ipe-tool-kb-librarian"
  - "Creating or editing manual content — manual authoring is out of scope"
  - "Searching code documentation — use grep/glob directly"
```

---

## Input Parameters

```yaml
input:
  operation: "lookup_instruction | get_step_by_step | troubleshoot | list_features"
  kb_path: ""           # Path to knowledge base folder (e.g., "x-ipe-docs/knowledge-base/my-app")
  query: ""             # Natural language description of what the caller is looking for
  section_filter: ""    # Optional: "core-features" | "workflows" | "getting-started" | "troubleshooting" | "configuration" | null
  feature_id: ""        # Optional: specific feature file name (e.g., "feature01-stage-toolbox")
  clarity_threshold: 0.6  # Optional: threshold for needs_human_feedback (default 0.6)
    # Caller derives from execution_temperature: strict → 0.8, balanced → 0.6, creative → 0.4
    # When clarity_score < clarity_threshold → needs_human_feedback = true
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies which operation to perform">
    <validation>MUST be one of: lookup_instruction, get_step_by_step, troubleshoot, list_features</validation>
  </field>

  <field name="kb_path" source="Caller provides the knowledge base manual folder path">
    <steps>
      1. IF caller provides explicit path → use it directly
      2. Verify the path exists and contains expected manual structure (at minimum 04-core-features/ or 01-overview.md)
      3. IF path does not exist → fail with KB_NOT_FOUND
    </steps>
  </field>

  <field name="query" source="Caller provides natural language search query">
    <steps>
      1. Required for: lookup_instruction, get_step_by_step (when feature_id is empty), troubleshoot
      2. Not required for: list_features
    </steps>
  </field>

  <field name="section_filter" source="Optional — caller may narrow search scope">
    <steps>
      1. IF provided, map to folder/file:
         - "core-features" → 04-core-features/
         - "workflows" → 05-common-workflows/
         - "getting-started" → 03-getting-started.md
         - "troubleshooting" → 07-troubleshooting.md
         - "configuration" → 06-configuration.md
      2. IF value doesn't match any known section → fail with SECTION_NOT_FOUND
    </steps>
  </field>

  <field name="feature_id" source="Optional — caller may specify exact feature/workflow file">
    <steps>
      1. IF provided, search for matching file in 04-core-features/ and 05-common-workflows/
      2. IF no match found → fail with FEATURE_NOT_FOUND
    </steps>
  </field>

  <field name="clarity_threshold" source="Optional — caller derives from execution_temperature">
    <steps>
      1. IF provided → use as threshold for needs_human_feedback evaluation
      2. IF not provided → default to 0.6
      3. Valid range: 0.0–1.0. Values outside this range → clamp to nearest boundary
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>KB path exists with manual content</name>
    <verification>Directory at kb_path exists and contains at least one recognized manual file (01-overview.md or 04-core-features/)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Valid operation requested</name>
    <verification>operation is one of: lookup_instruction, get_step_by_step, troubleshoot, list_features</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: lookup_instruction

**When:** Executor needs to find which manual section covers a specific task or feature.

```xml
<operation name="lookup_instruction">
  <action>
    1. Read index files from the KB:
       - Read {kb_path}/04-core-features/_index.md for feature listing table
       - Read {kb_path}/05-common-workflows/_index.md for workflow listing table
       - Read .kb-index.json files from both folders for metadata tags

    2. IF section_filter is provided:
       - Narrow search to the mapped folder/file only
       - Skip reading indexes for non-matching sections

    3. Match query against available content:
       - Compare query keywords against feature/workflow titles and descriptions
       - Use .kb-index.json tags for additional matching signals
       - Rank matches by relevance (title match > description match > tag match)

    4. For each match, extract:
       - file_path (project-root-relative)
       - title (from heading or index entry)
       - relevance_score (0.0–1.0)
       - interaction_pattern (FORM, MODAL, CLI_DISPATCH, NAVIGATION, TOGGLE)

    5. Assess clarity_score for the top match:
       - Read the matched file's Instructions section
       - Check if steps contain action verb, element name, and expected outcome
       - Deduct 0.15 per step missing any of these components
       - Minimum clarity_score is 0.0

    6. IF clarity_score < clarity_threshold (default 0.6):
       - Set needs_human_feedback: true
       - Provide feedback_reason listing which aspects are unclear
  </action>
  <constraints>
    - BLOCKING: Must read both _index.md and .kb-index.json for comprehensive matching
    - CRITICAL: Return at most 5 ranked matches
  </constraints>
  <output>
    {
      matches: [{file_path, title, relevance_score, interaction_pattern, clarity_score}],
      best_match: {file_path, title},
      needs_human_feedback: bool,
      feedback_reason: string | null
    }
  </output>
</operation>
```

### Operation: get_step_by_step

**When:** Executor needs detailed step-by-step instructions for a specific feature or workflow.

```xml
<operation name="get_step_by_step">
  <action>
    1. Resolve the target file:
       - IF feature_id is provided → locate file in 04-core-features/ or 05-common-workflows/
       - ELSE IF query is provided → run lookup_instruction internally, use best_match
       - IF no file resolved → fail with FEATURE_NOT_FOUND

    2. Read the resolved feature/workflow file

    3. Parse the Instructions section:
       - Extract ordered steps from the step-by-step block
       - For each step, parse: action (verb), element (UI label/name), expected_outcome
       - Collect screenshot references (![Alt text](screenshots/filename.png))

    4. Assess instruction quality (clarity_score starts at 1.0):
       - For each step, check presence of: action verb, element name, expected outcome
       - Deduct 0.15 per step missing any component
       - Track unclear_steps with step_number and missing_component

    5. Collect tips from the Tips section (if present)

    6. IF clarity_score < clarity_threshold (default 0.6):
       - Set needs_human_feedback: true
       - Include unclear_steps list identifying which steps need clarification
  </action>
  <constraints>
    - BLOCKING: Must parse every step — do not skip or summarize
    - CRITICAL: Preserve original step ordering
    - CRITICAL: Screenshot references must use project-root-relative paths
  </constraints>
  <output>
    {
      steps: [{step_number, action, element, expected_outcome, screenshot_ref}],
      clarity_score: float,
      needs_human_feedback: bool,
      unclear_steps: [{step_number, missing_component}],
      tips: [string]
    }
  </output>
</operation>
```

### Operation: troubleshoot

**When:** Executor tried following instructions but got an unexpected result.

```xml
<operation name="troubleshoot">
  <action>
    1. Read {kb_path}/07-troubleshooting.md for known issues and resolutions

    2. Search for query matches:
       - Match error messages, symptoms, or behavior descriptions in troubleshooting content
       - Also search 08-faq-reference.md for related Q&A entries

    3. IF section_filter is provided and points to a specific feature:
       - Also check the Tips section of that feature's file for gotchas

    4. IF match found:
       - Extract resolution steps from the matched troubleshooting entry
       - Collect related_sections that may provide additional context

    5. IF no match found:
       - Set needs_human_feedback: true
       - Return available troubleshooting topics for reference
  </action>
  <constraints>
    - CRITICAL: Search troubleshooting first, then FAQ, then feature tips — in that order
  </constraints>
  <output>
    {
      found: bool,
      resolution_steps: [string],
      related_sections: [{file_path, title}],
      needs_human_feedback: bool,
      feedback_reason: string | null
    }
  </output>
</operation>
```

### Operation: list_features

**When:** Caller needs an overview of all documented features and workflows.

```xml
<operation name="list_features">
  <action>
    1. Read {kb_path}/04-core-features/_index.md
       - Parse the listing table to extract feature entries
       - For each entry: extract id (filename), title, interaction_pattern

    2. Read {kb_path}/05-common-workflows/_index.md
       - Parse the listing table to extract workflow entries
       - For each entry: extract id (filename), title, complexity (if documented)

    3. IF _index.md is missing for a section:
       - Fall back to listing files via glob pattern (feature*.md / workflow*.md)
       - Extract titles from file H1 headings
  </action>
  <constraints>
    - CRITICAL: Return ALL documented features and workflows — do not filter or truncate
  </constraints>
  <output>
    {
      features: [{id, title, interaction_pattern}],
      workflows: [{id, title, complexity}]
    }
  </output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "lookup_instruction | get_step_by_step | troubleshoot | list_features"
  result:
    # Operation-specific fields (see each operation's <output> above)
  needs_human_feedback: false
  feedback_reason: null
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed with structured output</name>
    <verification>Output contains all required fields for the requested operation</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Clarity assessment included</name>
    <verification>For lookup_instruction and get_step_by_step, clarity_score is present and computed correctly</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human feedback flag set when needed</name>
    <verification>needs_human_feedback is true when clarity_score &lt; clarity_threshold (default 0.6) or troubleshoot finds no match</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `KB_NOT_FOUND` | kb_path directory does not exist | Halt with message suggesting valid KB paths under `x-ipe-docs/knowledge-base/` |
| `SECTION_NOT_FOUND` | section_filter value doesn't match any known section | Return list of available sections: core-features, workflows, getting-started, troubleshooting, configuration |
| `FEATURE_NOT_FOUND` | feature_id doesn't match any file in core-features or workflows | Return list of available feature/workflow files from the KB |
| `NO_INSTRUCTIONS` | Feature file exists but contains no Instructions section | Set `needs_human_feedback: true` with reason "Feature file lacks Instructions section" |
| `INDEX_MISSING` | _index.md or .kb-index.json not found in expected location | Fall back to file glob and warn that index-based matching is unavailable |

---

## Templates

| File | Purpose |
|------|---------|
| _None_ | This skill retrieves existing content — it produces no template files |

---

## Examples

See [references/examples.md](references/examples.md) for concrete usage scenarios.
