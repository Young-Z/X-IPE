---
name: x-ipe-knowledge-extractor-web
description: Extracts knowledge from web sources via Chrome DevTools MCP. Scans page structure (extract_overview) and retrieves specific content sections (extract_details). Writes to .working/ staging only. Triggers on operations like "extract_overview", "extract_details".
---

# Web Knowledge Extractor — Knowledge Skill

## Purpose

AI Agents follow this skill to extract knowledge from web sources:
1. Scan a web page structure to produce an organized overview (headings, sections, content types)
2. Extract specific content sections with format control (tables as JSON, code blocks, prose)
3. Write all extracted content to `.working/` staging area for later promotion

---

## Important Notes

BLOCKING: Operations are stateless services — the assistant orchestrator passes full context per call. Do NOT maintain internal state across operations.

CRITICAL: Each operation MUST define typed input/output contracts with a `writes_to` field.

CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.

CRITICAL: Writes ONLY to `.working/` staging area — NEVER to persistent tiers (episodic/, semantic/, procedural/). Use `x-ipe-knowledge-keeper-memory` to promote.

CRITICAL: Requires Chrome DevTools MCP tools at runtime (navigate_page, take_snapshot, evaluate_script, etc.). If Chrome DevTools MCP is unavailable, return `MCP_UNAVAILABLE` error immediately.

---

## About

This skill interfaces with web browsers via Chrome DevTools MCP to navigate and extract content from web pages. It is the primary ingestion pathway for external web-based knowledge.

**Key Concepts:**
- **Operation Contract** — Each operation declares its input types, output types, writes_to path, and constraints. The orchestrator uses this contract to plan execution.
- **Stateless Service** — The skill receives all needed context from the orchestrator per call. No cross-operation memory.
- **writes_to Discipline** — Every operation declares which path(s) it writes to, enabling the orchestrator to predict side effects and coordinate parallel operations.
- **Staging Only** — This skill extracts to `.working/` staging. Promotion to persistent memory tiers is done by `x-ipe-knowledge-keeper-memory`.

---

## When to Use

```yaml
triggers:
  - "Extract overview structure from a web page"
  - "Extract detailed content from a web page or section"
  - "Scan a web page for headings, sections, and content structure"

not_for:
  - "Persisting extracted content (use keeper-memory)"
  - "Searching existing memory (use extractor-memory)"
  - "Non-web content extraction (use extractor-file or extractor-repo)"
```

---

## Input Parameters

```yaml
input:
  operation: "extract_overview | extract_details"
  context:
    # For extract_overview:
    target: "string"          # URL to extract from
    depth: "shallow | medium" # shallow=headings only, medium=headings+summaries

    # For extract_details:
    target: "string"          # URL to extract from
    scope: "full | section | specific"
    format_hints: "string?"   # e.g., "extract tables as JSON", "code blocks only"
```

### Input Initialization

BLOCKING: All input fields with non-trivial initialization MUST be documented here.

```xml
<input_init>
  <field name="operation" source="Assistant orchestrator specifies which operation to perform">
    <validation>Must be one of: extract_overview, extract_details</validation>
  </field>

  <field name="context.target" source="Assistant orchestrator provides target URL">
    <validation>Must be a valid URL string (http:// or https://)</validation>
  </field>

  <field name="context.depth" source="Assistant orchestrator specifies scan depth (extract_overview only)">
    <validation>Must be one of: shallow, medium. Default: shallow</validation>
  </field>

  <field name="context.scope" source="Assistant orchestrator specifies extraction scope (extract_details only)">
    <validation>Must be one of: full, section, specific. Default: full</validation>
  </field>

  <field name="context.format_hints" source="Assistant orchestrator provides format guidance (extract_details, scope=specific only)">
    <validation>Optional string. Required when scope=specific</validation>
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
    <name>Target URL provided</name>
    <verification>context.target is a non-empty URL string starting with http:// or https://</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Chrome DevTools MCP available</name>
    <verification>Chrome DevTools MCP tools are accessible (navigate_page, take_snapshot)</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: extract_overview

> **Contract:**
> - **Input:** target: string (URL), depth: "shallow" | "medium"
> - **Output:** overview_content: string, source_map: object[]
> - **Writes To:** x-ipe-docs/memory/.working/overview/
> - **Constraints:** Uses Chrome DevTools MCP; on error, returns diagnostics and cleans up partial files

**When:** Orchestrator needs to understand the structure of a web page before detailed extraction.

```xml
<operation name="extract_overview">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: target URL, depth parameter
      2. DETERMINE output path: x-ipe-docs/memory/.working/overview/{url-slug}.md
         - url-slug: domain + path segments joined with hyphens, lowercase, max 80 chars
      3. ENSURE .working/overview/ directory exists (create if needed via bash mkdir -p)
    </action>
    <output>Input context understood, output path determined</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE target is a valid URL (starts with http:// or https://)
      2. VALIDATE depth is "shallow" or "medium" (default: shallow if omitted)
      3. CHECK Chrome DevTools MCP tools are available (navigate_page, take_snapshot)
      4. IF target invalid → RETURN error URL_INVALID with details
      5. IF Chrome DevTools MCP unavailable → RETURN error MCP_UNAVAILABLE
    </action>
    <constraints>
      - BLOCKING: Invalid URL → return error URL_INVALID immediately
      - BLOCKING: Chrome DevTools MCP unavailable → return error MCP_UNAVAILABLE
    </constraints>
    <output>Input validated, ready for extraction</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. NAVIGATE to target URL via chrome-devtools-navigate_page
      2. WAIT for page load (chrome-devtools-wait_for with page title or timeout)
      3. IF navigation fails → RETURN error URL_UNREACHABLE with diagnostics
      4. TAKE page snapshot via chrome-devtools-take_snapshot
      5. IF depth == "shallow":
         - EXTRACT headings (h1–h6) and page title from snapshot
         - BUILD source_map: [{section, url_fragment, content_type, estimated_size}]
      6. IF depth == "medium":
         - EXTRACT headings + first paragraph or summary per section
         - USE chrome-devtools-evaluate_script if needed for dynamic headings
         - BUILD richer source_map with summaries included
      7. COMPOSE overview_content as structured markdown with heading hierarchy
    </action>
    <output>Overview extracted from page DOM</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VALIDATE overview_content is non-empty string
      2. VALIDATE source_map has at least one entry
      3. IF extraction returned empty → set warning (some pages are minimal) but not error
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE overview_content to x-ipe-docs/memory/.working/overview/{url-slug}.md
      2. RETURN operation_output:
         - success: true
         - operation: "extract_overview"
         - result: { overview_content, source_map }
         - writes_to: "x-ipe-docs/memory/.working/overview/"
         - errors: []
    </action>
    <output>Overview written to staging, result returned to orchestrator</output>
  </phase_5>

</operation>
```

### Operation: extract_details

> **Contract:**
> - **Input:** target: string (URL), scope: "full" | "section" | "specific", format_hints: string?
> - **Output:** extracted_content: string, metadata: object
> - **Writes To:** x-ipe-docs/memory/.working/extracted/
> - **Constraints:** scope=full extracts entire page; section extracts by heading; specific uses format_hints

**When:** Orchestrator needs detailed content from a specific part of a web page.

```xml
<operation name="extract_details">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: target URL, scope, format_hints
      2. DETERMINE output path: x-ipe-docs/memory/.working/extracted/{url-slug}-{scope}.md
      3. ENSURE .working/extracted/ directory exists (create if needed via bash mkdir -p)
    </action>
    <output>Input context understood, output path determined</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE target is a valid URL (starts with http:// or https://)
      2. VALIDATE scope is one of: full, section, specific (default: full)
      3. IF scope == "specific": VALIDATE format_hints is provided and non-empty
      4. CHECK Chrome DevTools MCP tools are available
      5. IF scope=specific without format_hints → RETURN error INPUT_VALIDATION_FAILED
    </action>
    <constraints>
      - BLOCKING: scope=specific without format_hints → return error INPUT_VALIDATION_FAILED
      - BLOCKING: Invalid URL → return error URL_INVALID
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. NAVIGATE to target URL via chrome-devtools-navigate_page
      2. IF navigation fails → RETURN error URL_UNREACHABLE with diagnostics; clean up partial files
      3. TAKE page snapshot via chrome-devtools-take_snapshot
      4. IF scope == "full":
         - EXTRACT entire page content from snapshot as structured markdown
         - Preserve heading hierarchy, lists, tables, code blocks
      5. IF scope == "section":
         - IDENTIFY target section from URL fragment or context clues
         - EXTRACT only that section's content (heading to next same-level heading)
      6. IF scope == "specific":
         - APPLY format_hints to guide extraction (e.g., "tables as JSON", "code blocks only")
         - USE chrome-devtools-evaluate_script for dynamic content if needed
      7. BUILD metadata: { title, date, author (if available), url, structure_context }
    </action>
    <output>Detailed content extracted per scope</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VALIDATE extracted_content is non-empty string
      2. VALIDATE metadata contains required fields: title, url
      3. IF extraction empty → RETURN error EXTRACTION_EMPTY with page context
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE extracted_content to x-ipe-docs/memory/.working/extracted/{url-slug}-{scope}.md
      2. RETURN operation_output:
         - success: true
         - operation: "extract_details"
         - result: { extracted_content, metadata }
         - writes_to: "x-ipe-docs/memory/.working/extracted/"
         - errors: []
    </action>
    <output>Content written to staging, result returned to orchestrator</output>
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
    # extract_overview fields:
    overview_content: "string"   # Structured markdown with heading hierarchy
    source_map: "object[]"       # [{section, url_fragment, content_type, estimated_size}]
    # extract_details fields:
    extracted_content: "string"  # Extracted page content as markdown
    metadata: "object"           # {title, date, author, url, structure_context}
    # Common:
    writes_to: "string"          # Path where output was written
  errors: "string[]"             # Empty on success; error codes with messages on failure
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed successfully</name>
    <verification>operation_output.success == true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output written to .working/ staging</name>
    <verification>File exists at writes_to path with non-empty content</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output matches contract types</name>
    <verification>overview_content or extracted_content is non-empty string; source_map is array; metadata has title and url</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | Operation name not recognized | Return error listing valid operations: extract_overview, extract_details |
| `URL_INVALID` | Target is not a valid URL | Return error with target value and expected format |
| `URL_UNREACHABLE` | Cannot navigate to URL (DNS, timeout, etc.) | Return error with Chrome DevTools diagnostics; clean up partial .working/ files |
| `MCP_UNAVAILABLE` | Chrome DevTools MCP tools not accessible | Return error; orchestrator may retry later or use alternate extraction |
| `INPUT_VALIDATION_FAILED` | Required input missing (e.g., scope=specific without format_hints) | Return error with specific missing field name |
| `EXTRACTION_EMPTY` | Page loaded but content could not be extracted | Return error with page title/URL context for orchestrator diagnosis |

---

## Examples

See `references/examples.md` for usage examples.
