---
name: infographic-syntax-creator
description: Generate AntV Infographic syntax outputs. Use when asked to turn user content into the Infographic DSL (template selection, data structuring, theme), or to output `infographic <template>` plain syntax. The output can be embedded in markdown using ```infographic code blocks.
---

# Infographic Syntax Creator

## Overview

Generate AntV Infographic syntax output from user content, following the rules in `references/prompt.md`.

**Note:** When generating markdown documents, infographic DSL can be embedded using fenced code blocks with the `infographic` language identifier:

````markdown
```infographic
infographic list-row-horizontal-icon-arrow
data
  title Example
  lists
    - label Item 1
    - label Item 2
```
````

## Workflow

1. Read `references/prompt.md` for syntax rules, templates, and output constraints.
2. Extract the user's key structure: title, desc, items, hierarchy, metrics; infer missing pieces if needed.
3. Select a template that matches the structure (sequence/list/compare/hierarchy/chart).
4. Compose the syntax using `references/prompt.md` as the formatting baseline.
5. Preserve hard constraints in every output:
   - First line is `infographic <template-name>`.
   - Use two-space indentation; key/value pairs are `key value`; arrays use `-`.
   - Compare templates (`compare-*`) must have exactly two root nodes with children.

## When to Use Infographic vs Mermaid

| Visualization Type | Use Infographic | Use Mermaid |
|-------------------|-----------------|-------------|
| Process flows / Steps | ✅ `sequence-*` | ✅ flowchart |
| Timelines | ✅ `sequence-timeline-*` | ✅ timeline |
| Lists / Features | ✅ `list-*` | ❌ |
| Comparisons (SWOT, Pros/Cons) | ✅ `compare-*` | ❌ |
| Hierarchy / Org charts | ✅ `hierarchy-*` | ✅ flowchart TB |
| Mind maps | ✅ `hierarchy-mindmap-*` | ✅ mindmap |
| Relations / Graphs | ✅ `relation-*` | ✅ flowchart |
| Charts (pie, bar, line) | ✅ `chart-*` | ❌ |
| Class/ER diagrams | ❌ | ✅ classDiagram/erDiagram |
| Sequence diagrams | ❌ | ✅ sequenceDiagram |

**Prefer Infographic when:** You want visually rich, presentation-quality diagrams.
**Prefer Mermaid when:** You need technical diagrams (class, ER, sequence) or simple flowcharts.
