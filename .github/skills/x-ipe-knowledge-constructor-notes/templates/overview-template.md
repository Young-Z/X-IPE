# Overview Template

This template is used by the `fill_structure` operation to generate the `overview.md` file for a completed notes knowledge base.

---

## Format

```markdown
# {Knowledge Name (Title Case)}

> {Brief one-line description of this knowledge base}

## Table of Contents

{For each top-level section, ordered by number prefix:}

1. [{Section Title}]({NN}.{slug}.md)
   {IF section is hierarchical (has sub-folder):}
   - {Sub-number}. [{Sub-Section Title}]({NN}.{slug}/{NNMM}.{sub-slug}.md)

## Summary

- **Topic:** {topic from request_context}
- **Depth:** {overview | standard | deep-dive}
- **Sections:** {count}
- **Completeness:** {complete_count}/{total_count} sections filled
- **Last Updated:** {date}

## Quality Assessment

- **Rubric Score:** {rubric_score from fill_structure validation}
- **Incomplete Sections:** {list of sections marked [INCOMPLETE]}

## Images

{IF .images/ contains files:}
This knowledge base includes {image_count} embedded images/screenshots.

## References

{Consolidated, deduplicated list of all source URLs from all sections:}

1. [Source Title](https://example.com/page-1) — Accessed YYYY-MM-DD *(Sections: 1, 3)*
2. [Another Source](https://example.com/page-2) — Accessed YYYY-MM-DD *(Section: 2)*
3. `/path/to/local/file.pdf` — Local file *(Section: 4)*
```

---

## Generation Rules

1. **Title** — Derive from `request_context.topic`, convert to Title Case
2. **Description** — Synthesize from overview and framework purpose
3. **Table of Contents** — Walk framework sections in order, generate relative links
4. **Summary** — Compute from framework metadata and fill_structure results
5. **Quality Assessment** — Include rubric score and list any incomplete sections
6. **References** — Deduplicate across all section files, annotate which sections cite each source

---

## Example Output

```markdown
# React Server Components

> Comprehensive notes on React Server Components architecture, patterns, and best practices.

## Table of Contents

1. [Introduction](01.introduction.md)
2. [Core Concepts](02.core-concepts.md)
3. [Key Insights](03.key-insights/)
   - 3.1 [Streaming SSR](03.key-insights/0301.streaming-ssr.md)
   - 3.2 [Selective Hydration](03.key-insights/0302.selective-hydration.md)
   - 3.3 [Server-Client Boundary](03.key-insights/0303.server-client-boundary.md)
4. [Practical Applications](04.practical-applications.md)
5. [Examples and Patterns](05.examples-and-patterns.md)
6. [References and Sources](06.references-and-sources.md)
7. [Open Questions](07.open-questions.md)

## Summary

- **Topic:** React Server Components
- **Depth:** standard
- **Sections:** 7 (9 files total)
- **Completeness:** 7/7 sections filled
- **Last Updated:** 2025-07-18

## Quality Assessment

- **Rubric Score:** 0.87
- **Incomplete Sections:** None

## Images

This knowledge base includes 3 embedded images/screenshots.

## References

1. [React RFC #188](https://github.com/reactjs/rfcs/pull/188) — Accessed 2025-07-15 *(Sections: 1, 3)*
2. [Next.js Docs](https://nextjs.org/docs/app/building-your-application/rendering) — Accessed 2025-07-15 *(Sections: 2, 4)*
```
