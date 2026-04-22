---
name: x-ipe-knowledge-extractor-memory
description: Searches and retrieves existing knowledge from persistent memory and ontology. Provides overview scanning (extract_overview) and detailed content retrieval (extract_details). Read-only operations. Triggers on operations like "extract_overview", "extract_details".
---

# Knowledge Extractor — Memory

## Purpose

AI Agents follow this skill to retrieve knowledge from persistent memory:
1. Search across memory tiers (episodic, semantic, procedural) using glob/grep patterns
2. Optionally query the ontology graph for richer entity/relationship search
3. Retrieve detailed content from specific memory entries

---

## Important Notes

BLOCKING: Operations are stateless services — the assistant orchestrator passes full context per call. Do NOT maintain internal state across operations.

CRITICAL: Each operation MUST define typed input/output contracts with a `writes_to` field.

CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.

CRITICAL: This skill is READ-ONLY. It NEVER modifies any file. The `writes_to` field is `null` for all operations.

CRITICAL: For ontology search, this skill absorbs the functionality previously in `x-ipe-tool-ontology`. The old skill is RETIRED.

---

## About

This skill serves as the read gateway to persistent memory. It searches across all memory tiers and the ontology graph to find and retrieve relevant knowledge entries.

**Key Concepts:**
- **Operation Contract** — Each operation declares its input types, output types, writes_to path (null), and constraints.
- **Stateless Service** — Receives all context from orchestrator per call.
- **writes_to Discipline** — All operations declare `writes_to: null` (read-only).
- **Dual Search Strategy** — Shallow depth uses file-system glob/grep; medium depth adds ontology entity/relation search via `scripts/search.py`.
- **Ontology Absorption** — This skill replaces `x-ipe-tool-ontology` for all search operations.

---

## When to Use

```yaml
triggers:
  - "Search memory for knowledge about a topic"
  - "Retrieve detailed content from a memory entry"
  - "Scan knowledge base tiers for relevant entries"
  - "Query ontology for entities and relationships"

not_for:
  - "Writing or modifying memory (use keeper-memory)"
  - "Extracting from web sources (use extractor-web)"
  - "Building ontology (deferred to ontology-builder)"
```

---

## Input Parameters

```yaml
input:
  operation: "extract_overview | extract_details"
  context:
    # For extract_overview:
    target: "string"                    # Query string
    depth: "shallow | medium"           # shallow=glob/grep, medium=+ontology
    knowledge_type: "episodic | semantic | procedural | null"  # optional filter

    # For extract_details:
    target: "string"                    # File path or query
    scope: "full | section | specific"
    format_hints: "string?"             # Output format preference
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Assistant orchestrator specifies which operation to perform">
    <validation>Must be one of: extract_overview, extract_details</validation>
  </field>
  <field name="context.target" source="Assistant orchestrator provides search query or file path">
    <validation>Non-empty string</validation>
  </field>
  <field name="context.depth" source="Assistant orchestrator specifies search depth (extract_overview only)">
    <validation>Must be one of: shallow, medium. Default: medium</validation>
  </field>
  <field name="context.knowledge_type" source="Optional filter for specific memory tier">
    <validation>If provided, must be one of: episodic, semantic, procedural</validation>
  </field>
  <field name="context.scope" source="Extraction scope (extract_details only)">
    <validation>Must be one of: full, section, specific. Default: full</validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Operation specified</name>
    <verification>input.operation is "extract_overview" or "extract_details"</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Target provided</name>
    <verification>context.target is a non-empty string</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: extract_overview

> **Contract:**
> - **Input:** target: string, depth: "shallow"|"medium", knowledge_type: string?
> - **Output:** overview_content: string, source_map: object[]
> - **Writes To:** null (read-only)
> - **Constraints:** shallow=glob/grep only; medium=adds ontology search; knowledge_type filters to single tier; empty results return empty set with message

**When:** Orchestrator needs to find relevant knowledge entries across memory.

```xml
<operation name="extract_overview">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: target query, depth, knowledge_type filter
      2. DETERMINE search scope:
         - IF knowledge_type specified → search only that tier folder
         - ELSE → search all tiers: episodic/, semantic/, procedural/
      3. DETERMINE memory base path: x-ipe-docs/memory/
    </action>
    <output>Search scope defined</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE target is non-empty
      2. VALIDATE depth is "shallow" or "medium" (default: medium)
      3. IF knowledge_type specified → VALIDATE it is episodic/semantic/procedural
      4. CHECK memory folder exists (if not → return empty results with message)
    </action>
    <constraints>
      - BLOCKING: Empty target → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. SHALLOW SEARCH (always runs):
         - GLOB x-ipe-docs/memory/{tier}/*.md for each tier in scope
         - GREP target query across matched files (case-insensitive)
         - READ frontmatter of matching files for metadata (title, tags, memory_entry_id)
         - BUILD source_map entries: [{path, relevance, memory_tier, snippet}]
      2. IF depth == "medium":
         - RUN `python3 scripts/search.py --query "{target}" --memory-dir x-ipe-docs/memory [--class-filter TYPE]`
         - MERGE ontology results with file search results
         - DEDUPLICATE by file path
      3. SORT results by relevance score
      4. COMPOSE overview_content summarizing findings
    </action>
    <output>Search results compiled</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. IF no results found → set overview_content to "No entries found for '{target}'" (not error)
      2. VALIDATE source_map entries have required fields
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "extract_overview"
         - result: { overview_content, source_map }
         - writes_to: null
         - errors: []
    </action>
    <output>Results returned to orchestrator (no files written)</output>
  </phase_5>

</operation>
```

### Operation: extract_details

> **Contract:**
> - **Input:** target: string, scope: "full"|"section"|"specific", format_hints: string?
> - **Output:** extracted_content: string, metadata: dict
> - **Writes To:** null (read-only)
> - **Constraints:** Read-only; scope determines extraction granularity

**When:** Orchestrator needs detailed content from a specific memory entry.

```xml
<operation name="extract_details">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: target (file path or query), scope, format_hints
      2. RESOLVE target to a file path:
         - IF target is a file path → use directly
         - IF target is a query → search for best match first
    </action>
    <output>Target file identified</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE target file exists
      2. VALIDATE scope is "full", "section", or "specific"
      3. IF scope == "specific" and no format_hints → default to full
    </action>
    <constraints>
      - BLOCKING: File not found → return error PATH_NOT_FOUND
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. READ target file content
      2. PARSE frontmatter for metadata (memory_entry_id, title, tags, memory_type, timestamps)
      3. IF scope == "full": return entire file content
      4. IF scope == "section": extract matching heading/section from content
      5. IF scope == "specific": apply format_hints to filter content (e.g., code blocks, tables)
      6. BUILD metadata: {file_size, last_modified, memory_tier, title, tags}
    </action>
    <output>Content extracted per scope</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VALIDATE extracted_content is non-empty
      2. VALIDATE metadata contains required fields
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "extract_details"
         - result: { extracted_content, metadata }
         - writes_to: null
         - errors: []
    </action>
    <output>Content returned to orchestrator (no files written)</output>
  </phase_5>

</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "extract_overview | extract_details"
  result:
    overview_content: "..."          # extract_overview
    source_map: [...]                # extract_overview
    extracted_content: "..."         # extract_details
    metadata: {...}                  # extract_details
    writes_to: null                  # always null (read-only)
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed</name>
    <verification>operation_output.success == true (or false with errors)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No files modified</name>
    <verification>writes_to is null; no files created, modified, or deleted</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output matches contract types</name>
    <verification>overview_content or extracted_content is string; source_map is array; metadata is dict</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>search.py functional</name>
    <verification>scripts/search.py executes with --query and --memory-dir parameters</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | Operation not recognized | Return error listing valid operations |
| `INPUT_VALIDATION_FAILED` | Required input missing | Return error with specific field |
| `PATH_NOT_FOUND` | Target file doesn't exist | Return error with path details |
| `ONTOLOGY_UNAVAILABLE` | .ontology/ folder missing or empty | Return grep/glob results only (degraded mode) |
| `SEARCH_ERROR` | search.py failed | Return error with script stderr; fall back to glob/grep |

---

## Examples

See `references/examples.md` for usage examples.
