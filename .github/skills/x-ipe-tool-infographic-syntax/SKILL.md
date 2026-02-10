---
name: x-ipe-tool-infographic-syntax
description: Generate AntV Infographic syntax outputs. Use when asked to turn user content into the Infographic DSL (template selection, data structuring, theme), or to output `infographic <template>` plain syntax. The output can be embedded in markdown using ```infographic code blocks. Triggers on requests like "create infographic", "infographic diagram", "visualize as infographic".
version: 1.0
---

# Infographic Syntax Tool

## Purpose

AI Agents follow this skill to generate AntV Infographic DSL syntax to:
1. Convert user content into structured infographic visualizations
2. Select appropriate templates based on content structure
3. Produce valid DSL syntax for native IPE markdown rendering

---

## Important Notes

BLOCKING: Read [references/prompt.md](references/prompt.md) before generating syntax. It contains the complete DSL specification, template list, and data field rules.

CRITICAL: Output MUST be a `plain` code block containing only infographic DSL. No JSON, no Markdown, no explanatory text.

CRITICAL: The first line MUST be `infographic <template-name>` where template-name is from the available templates list in prompt.md.

MANDATORY: Each template category uses a specific data field — do NOT mix fields. See Template-to-Data-Field mapping below.

---

## About

AntV Infographic is a DSL for describing infographic rendering configurations. It uses indentation-based syntax optimized for AI streaming output. IPE natively renders it via `infographic` code blocks in markdown.

**Key Concepts:**
- **Template** — Determines visual layout (e.g., `list-row-horizontal-icon-arrow`, `sequence-timeline-simple`)
- **Data Block** — Contains `title`, `desc`, and the primary data field with items
- **Theme Block** — Optional styling: `palette`, `font`, `stylize` (rough, pattern, gradient)
- **Data Fields** — Template-specific: `lists`, `sequences`, `compares`, `root`, `items`, `values`, `nodes`+`relations`
- **Grid System** — 2-space indentation; key-value pairs use `key space value`; arrays use `-` prefix

**Template-to-Data-Field Mapping:**

| Template Prefix | Data Field | Notes |
|----------------|------------|-------|
| `list-*` | `lists` | Flat items with label/desc/icon |
| `sequence-*` | `sequences` | Ordered steps, optional `order asc\|desc` |
| `compare-*` | `compares` | Supports `children` for grouped comparison |
| `hierarchy-structure` | `items` | Independent tiers, up to 3 levels deep |
| `hierarchy-*` (others) | `root` | Single root with nested `children` |
| `relation-*` | `nodes` + `relations` | Nodes optional for simple graphs |
| `chart-*` | `values` | Numeric data, optional `category` |
| Fallback | `items` | When no specific field matches |

**Compare Rules:**
- `compare-binary-*` / `compare-hierarchy-left-right-*`: Exactly 2 root nodes, all items in `children`
- `compare-quadrant-*`: Exactly 4 items

**Hierarchy Rules:**
- `hierarchy-*` (non-structure): Single `root`, nest via `children` — do NOT repeat `root`

**IPE Markdown Embedding:**

````markdown
```infographic
infographic list-row-horizontal-icon-arrow
data
  title My Title
  lists
    - label Item 1
      icon star
```
````

---

## When to Use

```yaml
triggers:
  - "create infographic"
  - "infographic diagram"
  - "visualize as infographic"
  - "turn into infographic"
  - "infographic syntax"

not_for:
  - "architecture diagrams → x-ipe-tool-architecture-dsl"
  - "flowcharts, sequence diagrams, ER diagrams → Mermaid"
  - "data tables → standard Markdown tables"
```

**Infographic vs Other Tools:**

| Content Type | Tool |
|-------------|------|
| Feature lists, comparisons, processes | **Infographic** |
| Software architecture layers | Architecture DSL |
| Control flow, state machines | Mermaid |
| Raw data tables | Markdown |

---

## Input Parameters

```yaml
input:
  operation: "generate | refine"
  content: "User text content or requirements"
  template_hint: "(optional) Template name or category"
  theme: "(optional) Theme config: dark, palette, stylize"
  existing_syntax: "(optional, refine only) Current DSL to update"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Content Provided</name>
    <verification>User content or requirements available for conversion</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>DSL Spec Loaded</name>
    <verification>references/prompt.md has been read</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Template Hint Available</name>
    <verification>User indicated preferred visualization style or category</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: generate

**When:** User provides content to convert into an infographic

```xml
<operation name="generate">
  <action>
    1. Load DSL specification from references/prompt.md
    2. Analyze content structure: identify items, hierarchy, sequences, comparisons
    3. Select template:
       - IF template_hint provided → validate against available templates list
       - IF no hint → match content structure to template category (see About section mapping)
    4. Map content to data fields:
       - Extract title and description
       - Map items to the correct data field for the selected template
       - Add icon keywords where appropriate
    5. Apply theme if specified:
       - palette colors, font-family, stylize options (rough, pattern, gradient)
    6. Output complete DSL in a plain code block
  </action>
  <constraints>
    - BLOCKING: First line must be `infographic <template-name>` from available list
    - BLOCKING: Use correct data field for template prefix (see mapping table)
    - CRITICAL: 2-space indentation for block nesting
    - CRITICAL: No JSON, Markdown, or explanatory text in output
  </constraints>
  <output>infographic_syntax (plain code block)</output>
</operation>
```

### Operation: refine

**When:** User wants to update or improve existing infographic DSL

```xml
<operation name="refine">
  <action>
    1. Load DSL specification from references/prompt.md
    2. Parse existing_syntax to identify current template, data, and theme
    3. Apply requested changes (content updates, template switch, theme changes)
    4. Validate refined syntax against DSL rules
    5. Output updated DSL in a plain code block
  </action>
  <constraints>
    - BLOCKING: Preserve existing structure unless explicitly asked to change
    - CRITICAL: Re-validate data field matches template after any template change
  </constraints>
  <output>infographic_syntax (plain code block)</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    template_used: "{template-name}"
    infographic_syntax: "{complete DSL}"
    data_field_used: "{lists|sequences|compares|root|items|values|nodes}"
  errors: []
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Entry Line Valid</name>
    <verification>First line matches `infographic &lt;template-name&gt;` where template-name is in available templates list</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Block Structure Valid</name>
    <verification>Uses `data` and optional `theme` blocks with 2-space indentation</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Data Field Correct</name>
    <verification>Data field matches template prefix (list→lists, sequence→sequences, compare→compares, hierarchy→root/items, chart→values, relation→nodes+relations)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Mixed Fields Avoided</name>
    <verification>Only ONE primary data field used (no mixing lists+items, sequences+items, etc.)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Compare Rules Met</name>
    <verification>Binary compare has exactly 2 root nodes; quadrant has exactly 4 items</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Hierarchy Rules Met</name>
    <verification>hierarchy-* (non-structure) uses single `root` with `children` nesting, no repeated root</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Indentation Correct</name>
    <verification>Consistent 2-space indentation throughout, key-value pairs use `key space value`</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No Forbidden Output</name>
    <verification>Output contains no JSON, Markdown formatting, or explanatory text — only DSL syntax</verification>
  </checkpoint>

  <validation_sub_agent>
    <instructions>
      After generating infographic syntax, launch a sub-agent (model hint: haiku) to independently validate:
      1. Parse the output and verify first line matches `infographic {template}` where {template} is in the available templates list from references/prompt.md
      2. Verify only one primary data field is used and it matches the template prefix
      3. For compare-binary-*/compare-hierarchy-left-right-*: verify exactly 2 root compares nodes
      4. For hierarchy-* (non-structure): verify single root, no duplicate root
      5. Verify 2-space indentation is consistent
      6. Verify output contains no JSON, no markdown, no explanatory text
      Report: PASS/FAIL per checkpoint with specific violations if any.
    </instructions>
  </validation_sub_agent>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `template_not_found` | Template name not in available list | Check references/prompt.md for valid template names |
| `content_required` | No content provided for generate | Request content from user |
| `data_field_mismatch` | Wrong data field for template type | Consult Template-to-Data-Field mapping |
| `invalid_indentation` | Inconsistent indentation in output | Use strict 2-space indentation |
| `mixed_data_fields` | Multiple primary data fields used | Use only one field per template category |

---

## Templates

| File | Purpose |
|------|---------|
| `references/prompt.md` | Complete AntV Infographic DSL specification with syntax rules, template list, and examples |

---

## Examples

**List Infographic:**

```plain
infographic list-grid-badge-card
data
  title Feature List
  lists
    - label Fast
      icon flash fast
    - label Secure
      icon secure shield check
```

**Sequence Infographic:**

```plain
infographic sequence-timeline-simple
data
  title Project Phases
  sequences
    - label Planning
      desc Define scope and goals
    - label Development
      desc Build core features
    - label Launch
      desc Release to production
```

**Compare Infographic (SWOT):**

```plain
infographic compare-swot
data
  compares
    - label Strengths
      children
        - label Strong brand
        - label Loyal users
    - label Weaknesses
      children
        - label High cost
        - label Slow release
```

See [references/prompt.md](references/prompt.md) for the complete template list and additional examples.
