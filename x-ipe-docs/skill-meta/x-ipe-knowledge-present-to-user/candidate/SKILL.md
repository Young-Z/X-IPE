---
name: x-ipe-knowledge-present-to-user
description: Knowledge output formatter that renders constructed knowledge as a structured summary for human consumption. Delegates rendering to scripts/render.py. Triggers on operations like "render", "present to user".
---

# Present to User — Knowledge Skill

## Purpose

AI Agents follow this skill to render knowledge content into human-consumable formats:
1. Read knowledge content from a source file
2. Parse into sections with completeness tracking
3. Flag incomplete sections with warnings
4. Output as structured JSON or Markdown

---

## Important Notes

BLOCKING: This is a single-operation skill. The `render` operation reads a content file and produces formatted output.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`).
CRITICAL: Operations are stateless services — the orchestrator passes full context per call.
CRITICAL: The default output format is structured JSON (BR-5). Markdown and other formats are only used when explicitly requested by the caller.

---

## About

This skill formats knowledge content for human consumption. It parses Markdown-based knowledge files, tracks section completeness (detecting `[INCOMPLETE: ...]` markers left by the constructor's fill_structure operation), and produces either a structured JSON summary or a Markdown-formatted output.

**Key Concepts:**
- **Structured Summary** — Default output: JSON with `title`, `summary`, `sections[]`, and `metadata`. Each section includes `heading`, `content`, `completeness` percentage, and optional `warnings[]`.
- **Completeness Tracking** — Measures the ratio of filled content to `[INCOMPLETE: ...]` markers per section, producing a percentage (0–100).
- **Incomplete Warnings** — Sections with `[INCOMPLETE: reason]` markers generate warnings in the output, helping users identify gaps.
- **writes_to Discipline** — This operation writes to stdout only (no filesystem writes).

---

## When to Use

```yaml
triggers:
  - "Render knowledge for human consumption"
  - "Present knowledge summary to user"
  - "Format knowledge as structured JSON or Markdown"
```

---

## Input Parameters

```yaml
input:
  operation: render
  context:
    content_path: "path to knowledge Markdown file"
    format: "structured" | "markdown"   # default: "structured"
```

### Input Initialization

```xml
<input_init>
  <field name="context.content_path" source="Orchestrator" default="none">
    <validation>Must be a valid file path. File must exist and be UTF-8 encoded.</validation>
  </field>
  <field name="context.format" source="Orchestrator or default" default="structured">
    <validation>Must be "structured" or "markdown"</validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Content file exists</name>
    <verification>context.content_path points to an existing, readable file</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Format is valid</name>
    <verification>context.format is "structured" or "markdown"</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: render

> **Contract:**
> - **Input:** content_path: string (file path), format: "structured" | "markdown" (default: "structured")
> - **Output:** rendered_output: structured_summary | markdown_text
> - **Writes To:** stdout (JSON or Markdown) — no filesystem writes
> - **Delegates To:** `scripts/render.py render`
> - **Constraints:** Default format is structured JSON (BR-5); empty files produce minimal valid output

**When:** Orchestrator needs to present knowledge content to the user.

```xml
<operation name="render">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ file at content_path
      2. IF file does not exist → return error CONTENT_NOT_FOUND
      3. IF file is empty → prepare empty output: {title: "Empty", summary: "", sections: [], metadata: {overall_completeness: 0}}
      4. IF file is not valid UTF-8 → return error INVALID_CONTENT_FORMAT
    </action>
    <output>Content loaded or error returned</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. PARSE content into sections by Markdown headers (## heading)
      2. IF no headers found → treat entire content as single untitled section
      3. Extract title from first H1 header (# title) or filename
      4. Extract summary from first 200 characters or first paragraph
    </action>
    <constraints>
      - BLOCKING: Invalid format value → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Sections parsed with headings and content</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. FOR EACH section:
         a. Count total characters in content
         b. Find all [INCOMPLETE: reason] markers
         c. Compute completeness: (total_chars - incomplete_marker_chars) / total_chars * 100
         d. IF incomplete markers found → add warnings[] with marker reasons
      2. COMPUTE overall_completeness: average of all section completeness values
    </action>
    <output>Sections enriched with completeness and warnings</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. BUILD metadata: source_path, total_sections, overall_completeness, generated_at (ISO-8601)
      2. VERIFY all sections have heading, content, completeness fields
      3. VERIFY completeness is 0-100 range
    </action>
    <output>Validated output ready for formatting</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. EXECUTE:
         ```
         python3 scripts/render.py render \
           --content-path {content_path} \
           --format {format}
         ```
      2. IF format == "structured" → output JSON
      3. IF format == "markdown" → output Markdown text
      4. RETURN operation_output
    </action>
    <output>render complete</output>
  </phase_5>

</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "render"
  result:
    rendered_output:
      title: "string"
      summary: "string (first 200 chars or first paragraph)"
      sections:
        - heading: "string"
          content: "string"
          completeness: "int (0-100)"
          warnings: ["string"]         # only if incomplete markers found
      metadata:
        source_path: "string"
        total_sections: "int"
        overall_completeness: "int (0-100)"
        generated_at: "string (ISO-8601)"
  errors: []
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
    <name>Structured output has required fields</name>
    <verification>Output contains title, summary, sections[], metadata with all required sub-fields</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Completeness tracking works</name>
    <verification>Sections with [INCOMPLETE: ...] markers have reduced completeness and warnings[]</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Both formats supported</name>
    <verification>format=structured produces JSON; format=markdown produces Markdown text</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Error cases handled</name>
    <verification>Missing file → CONTENT_NOT_FOUND; empty file → valid empty output</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `CONTENT_NOT_FOUND` | content_path does not exist | Return error with path details |
| `INVALID_CONTENT_FORMAT` | File is not valid UTF-8 | Return error with encoding details |
| `INPUT_VALIDATION_FAILED` | Invalid format value | Return error listing valid formats |

---

## Patterns & Anti-Patterns

| Pattern | When | Key Actions |
|---------|------|-------------|
| Structured summary | Default presentation | Use format=structured for JSON output |
| Markdown export | User requests text | Use format=markdown |
| Completeness check | Before sharing knowledge | Check overall_completeness in metadata |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Default to markdown | Breaks BR-5 contract | Default is structured JSON |
| Ignore incomplete markers | User sees unfinished content | Always flag with warnings |

---

## Examples

See `references/examples.md` for worked examples of the render operation.
