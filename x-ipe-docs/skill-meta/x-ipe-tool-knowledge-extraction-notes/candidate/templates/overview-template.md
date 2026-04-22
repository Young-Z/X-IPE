# Overview Template

Use this template to generate the overview.md file for a knowledge base.

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

- **Sections:** {count}
- **Last Updated:** {date}

## Images

{IF .images/ contains files:}
This knowledge base includes {image_count} embedded images/screenshots.

## References

{Consolidated, deduplicated list of all source URLs and data sources from all sections:}

1. [Source Title](https://example.com/page-1) — Accessed YYYY-MM-DD *(Sections: 1, 3)*
2. [Another Source](https://example.com/page-2) — Accessed YYYY-MM-DD *(Section: 2)*
3. `/path/to/local/file.pdf` — Local file *(Section: 4)*
```

---

## Example Output

```markdown
# React Server Components

> Comprehensive notes on React Server Components architecture, patterns, and best practices.

## Table of Contents

1. [Introduction and Benefits](01.introduction-and-benefits.md)
2. [Architecture Patterns](02.architecture-patterns/)
   - 2.1 [Streaming SSR](02.architecture-patterns/0201.streaming-ssr.md)
   - 2.2 [Selective Hydration](02.architecture-patterns/0202.selective-hydration.md)
   - 2.3 [Server-Client Boundary](02.architecture-patterns/0203.server-client-boundary.md)
3. [Migration Guide](03.migration-guide.md)
4. [Performance Considerations](04.performance-considerations.md)

## Summary

- **Sections:** 4 (6 files total)
- **Last Updated:** 2026-04-13

## Images

This knowledge base includes 3 embedded images/screenshots.
```
