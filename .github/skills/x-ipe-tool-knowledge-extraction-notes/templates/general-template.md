# General Knowledge Template

Use this template structure when extracting general-purpose knowledge.

## Suggested Sections

```
{knowledge_name}/
├── overview.md
├── .images/
├── 01.introduction.md          # What is it? Why does it matter?
├── 02.core-concepts.md         # Key definitions, terminology, mental models
├── 03.key-insights/            # Main findings or takeaways (hierarchical if complex)
│   ├── 0301.insight-one.md
│   ├── 0302.insight-two.md
│   └── ...
├── 04.practical-applications.md  # How to apply this knowledge
├── 05.examples-and-patterns.md   # Concrete examples, code samples, patterns
├── 06.references-and-sources.md  # Links, citations, further reading
└── 07.open-questions.md          # Unresolved items, areas for future exploration
```

## Section Guidelines

### 01. Introduction
- Brief overview of the topic
- Why this knowledge base was created
- Scope and boundaries

### 02. Core Concepts
- Key terminology with definitions
- Foundational principles
- Mental models or frameworks

### 03. Key Insights (Hierarchical)
- Each insight gets its own sub-file if complex
- Include evidence or reasoning for each insight
- Cross-reference related insights

### 04. Practical Applications
- How to apply the knowledge
- Decision frameworks
- Checklists or guidelines

### 05. Examples and Patterns
- Concrete examples with code/diagrams
- Common patterns and anti-patterns
- Before/after comparisons

### 06. References and Sources
- Original source materials
- Further reading links
- Related knowledge bases

### 07. Open Questions
- Unresolved questions
- Areas needing deeper research
- Hypotheses to test

---

## References Footer (Mandatory)

Every markdown file MUST end with this footer:

```markdown
---

## References

1. [Source Title](https://example.com/page) — Accessed YYYY-MM-DD
2. `/path/to/local/file.pdf` — Local file
3. Direct input — User-provided content
```

This applies to ALL section files and overview.md regardless of template_type.
