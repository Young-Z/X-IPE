# Examples — constructor-notes Operations

Worked examples for each of the 4 operations in `x-ipe-knowledge-constructor-notes`.

---

## Example 1: provide_framework

**Scenario:** Orchestrator requests a standard-depth framework for "React Hooks" notes.

**Input:**
```yaml
operation: provide_framework
context:
  request_context:
    topic: "React Hooks"
    scope: "Patterns, best practices, and common pitfalls"
    depth: "standard"
    source_paths:
      - "https://react.dev/reference/react"
  output_format: "markdown"
```

**Agent Execution (phases):**
1. **博学之** — Reads request_context, loads `templates/general-template.md`, notes "standard" depth.
2. **审问之** — Validates topic ("React Hooks" non-empty), depth ("standard" is valid), source_paths exist.
3. **慎思之** — Generates 7-section hierarchy adapted to React Hooks:
   - 01.introduction.md — What are React Hooks?
   - 02.core-concepts.md — useState, useEffect, rules of hooks
   - 03.key-insights/ — Pattern-specific sub-files
   - 04.practical-applications.md — When to use custom hooks
   - 05.examples-and-patterns.md — Code examples
   - 06.references-and-sources.md
   - 07.open-questions.md
4. **明辨之** — Validates 7 sections, all have stubs, toc_structure matches.
5. **笃行之** — Writes to `x-ipe-docs/memory/.working/framework/react-hooks-framework.md`.

**Output:**
```yaml
operation_output:
  success: true
  operation: "provide_framework"
  result:
    framework_document:
      topic: "React Hooks"
      sections:
        - id: "01"
          title: "Introduction"
          file: "01.introduction.md"
          stub: "What are React Hooks? Why were they introduced?"
        - id: "02"
          title: "Core Concepts"
          file: "02.core-concepts.md"
          stub: "useState, useEffect, useContext, rules of hooks"
        - id: "03"
          title: "Key Insights"
          file: "03.key-insights/"
          stub: "Patterns and deep-dives"
          children:
            - id: "0301"
              title: "State Management Patterns"
              file: "03.key-insights/0301.state-management-patterns.md"
            - id: "0302"
              title: "Effect Lifecycle"
              file: "03.key-insights/0302.effect-lifecycle.md"
        - id: "04"
          title: "Practical Applications"
          file: "04.practical-applications.md"
          stub: "Custom hooks, composability patterns"
        - id: "05"
          title: "Examples and Patterns"
          file: "05.examples-and-patterns.md"
          stub: "Code samples, anti-patterns"
        - id: "06"
          title: "References and Sources"
          file: "06.references-and-sources.md"
          stub: "Links and citations"
        - id: "07"
          title: "Open Questions"
          file: "07.open-questions.md"
          stub: "Unresolved topics"
    toc_structure:
      - { id: "01", title: "Introduction", stubs: "What are React Hooks?", depth: 0 }
      - { id: "02", title: "Core Concepts", stubs: "useState, useEffect, rules", depth: 0 }
      - { id: "03", title: "Key Insights", stubs: "Patterns and deep-dives", depth: 0 }
      - { id: "0301", title: "State Management Patterns", stubs: "", depth: 1 }
      - { id: "0302", title: "Effect Lifecycle", stubs: "", depth: 1 }
      - { id: "04", title: "Practical Applications", stubs: "Custom hooks", depth: 0 }
      - { id: "05", title: "Examples and Patterns", stubs: "Code samples", depth: 0 }
      - { id: "06", title: "References and Sources", stubs: "Links", depth: 0 }
      - { id: "07", title: "Open Questions", stubs: "Unresolved", depth: 0 }
    writes_to: "x-ipe-docs/memory/.working/framework/"
  errors: []
```

---

## Example 2: design_rubric

**Scenario:** Orchestrator requests quality rubric for the React Hooks framework, with user emphasis on practical examples.

**Input:**
```yaml
operation: design_rubric
context:
  framework:
    topic: "React Hooks"
    sections: [{ id: "01", title: "Introduction" }, { id: "02", title: "Core Concepts" }, { id: "03", title: "Key Insights" }, { id: "04", title: "Practical Applications" }, { id: "05", title: "Examples and Patterns" }, { id: "06", title: "References" }, { id: "07", title: "Open Questions" }]
  overview: "Comprehensive notes on React Hooks covering patterns, lifecycle, and custom hooks."
  user_request: "I want lots of practical code examples and pattern comparisons."
```

**Agent Execution (phases):**
1. **博学之** — Reads framework (7 sections), overview, user_request. Notes emphasis on "practical code examples."
2. **审问之** — Validates all inputs present and non-empty.
3. **慎思之** — Generates per-section metrics with higher weights for sections 04 and 05:
   - Section 01: weight 0.08 — "Contains scope statement and motivation"
   - Section 02: weight 0.15 — "≥5 terms defined with examples"
   - Section 05: weight 0.25 — "≥4 code examples with explanations" (high: user emphasis)
   - Section 04: weight 0.22 — "≥3 practical use cases with code" (high: user emphasis)
4. **明辨之** — Validates all sections have metrics, weights sum to 1.0, criteria are measurable.
5. **笃行之** — Writes to `x-ipe-docs/memory/.working/rubric/react-hooks-rubric.md`.

**Output:**
```yaml
operation_output:
  success: true
  operation: "design_rubric"
  result:
    rubric_metrics:
      - { section_id: "01", criteria: "Contains scope statement and motivation paragraph", weight: 0.08, threshold: "≥1 paragraph" }
      - { section_id: "02", criteria: "Key terms defined with inline examples", weight: 0.15, threshold: "≥5 terms" }
      - { section_id: "03", criteria: "Each insight has evidence or reasoning", weight: 0.12, threshold: "≥2 insights with citations" }
      - { section_id: "04", criteria: "Practical use cases with runnable code", weight: 0.22, threshold: "≥3 use cases" }
      - { section_id: "05", criteria: "Code examples with explanations and anti-patterns", weight: 0.25, threshold: "≥4 examples" }
      - { section_id: "06", criteria: "All sources cited with URLs and dates", weight: 0.10, threshold: "≥3 references" }
      - { section_id: "07", criteria: "Open questions are specific and actionable", weight: 0.08, threshold: "≥1 question" }
    acceptance_criteria:
      - { section_id: "01", checks: ["Has topic definition", "States scope boundaries"] }
      - { section_id: "02", checks: ["Defines useState", "Defines useEffect", "Lists rules of hooks"] }
      - { section_id: "04", checks: ["Includes custom hook example", "Shows composability pattern"] }
      - { section_id: "05", checks: ["Has before/after comparison", "Includes anti-pattern example"] }
    writes_to: "x-ipe-docs/memory/.working/rubric/"
  errors: []
```

---

## Example 3: request_knowledge

**Scenario:** Orchestrator has a partially filled framework — sections 01 and 06 are filled, others are empty.

**Input:**
```yaml
operation: request_knowledge
context:
  framework:
    topic: "React Hooks"
    sections: [{ id: "01" }, { id: "02" }, { id: "03" }, { id: "04" }, { id: "05" }, { id: "06" }, { id: "07" }]
  current_state:
    filled_sections: ["01", "06"]
    empty_sections: ["02", "03", "04", "05", "07"]
    partial_sections: []
  rubric:
    metrics: [{ section_id: "02", weight: 0.15 }, { section_id: "03", weight: 0.12 }, { section_id: "04", weight: 0.22 }, { section_id: "05", weight: 0.25 }, { section_id: "07", weight: 0.08 }]
```

**Agent Execution (phases):**
1. **博学之** — Lists all sections, categorizes: 01, 06 filled; 02, 03, 04, 05, 07 empty.
2. **审问之** — Validates all inputs. Not all filled → proceed with gap analysis.
3. **慎思之** — Generates requests sorted by rubric weight:
   - Priority 1 (weight 0.25): Section 05 — "Need ≥4 code examples with hooks patterns"
   - Priority 2 (weight 0.22): Section 04 — "Need ≥3 practical use cases for custom hooks"
   - Priority 3 (weight 0.15): Section 02 — "Need definitions for useState, useEffect, useContext, rules"
   - Priority 4 (weight 0.12): Section 03 — "Need insight articles on state management and effect lifecycle"
   - Priority 5 (weight 0.08): Section 07 — "Need open questions about hooks limitations"
4. **明辨之** — All requests have required fields, no duplicates, extractors valid.
5. **笃行之** — Writes to `x-ipe-docs/memory/.working/plan/react-hooks-plan.md`.

**Output:**
```yaml
operation_output:
  success: true
  operation: "request_knowledge"
  result:
    knowledge_requests:
      - { target_section: "05", what_needed: "At least 4 code examples demonstrating hooks patterns (useState, useEffect, custom hooks) with explanations and anti-pattern examples", suggested_extractor: "extractor-web", priority: 1 }
      - { target_section: "04", what_needed: "At least 3 practical use cases showing when and how to build custom hooks, with composability patterns", suggested_extractor: "extractor-web", priority: 2 }
      - { target_section: "02", what_needed: "Definitions and explanations for core hooks (useState, useEffect, useContext, useRef) and the rules of hooks", suggested_extractor: "extractor-web", priority: 3 }
      - { target_section: "03", what_needed: "Deep-dive insights on state management patterns with hooks and effect lifecycle behavior", suggested_extractor: "extractor-web", priority: 4 }
      - { target_section: "07", what_needed: "Open questions about hooks limitations, concurrent mode interactions, and future React API directions", suggested_extractor: "extractor-memory", priority: 5 }
    writes_to: "x-ipe-docs/memory/.working/plan/"
  errors: []
```

---

## Example 4: fill_structure

**Scenario:** Orchestrator has gathered knowledge for all sections and needs the draft assembled.

**Input:**
```yaml
operation: fill_structure
context:
  framework:
    topic: "React Hooks"
    sections: [{ id: "01", title: "Introduction", file: "01.introduction.md" }, { id: "02", title: "Core Concepts", file: "02.core-concepts.md" }, ...]
  gathered_knowledge:
    - { section_id: "01", content: "React Hooks were introduced in React 16.8...", source: "https://react.dev/blog/2019/02/06/react-v16.8.0", metadata: { extracted_by: "extractor-web" } }
    - { section_id: "02", content: "**useState** — Returns a stateful value...", source: "https://react.dev/reference/react/useState", metadata: { extracted_by: "extractor-web" } }
    - { section_id: "03", content: "...", source: "...", metadata: {} }
    - { section_id: "04", content: "...", source: "...", metadata: {} }
    - { section_id: "05", content: "...", source: "...", metadata: {} }
    - { section_id: "06", content: "...", source: "...", metadata: {} }
    # Note: section 07 not provided — will be marked incomplete
  rubric:
    metrics: [...]
    acceptance_criteria: [...]
```

**Agent Execution (phases):**
1. **博学之** — Loads framework, gathered_knowledge (6 items), rubric. Loads overview-template.md.
2. **审问之** — Validates inputs. Notes section 07 has no gathered knowledge.
3. **慎思之** — Fills sections:
   - 01–06: maps content to respective files, appends references footer
   - 07: marks `[INCOMPLETE: no knowledge gathered for open questions]`
   - Generates overview.md from overview-template.md with TOC, summary, quality assessment
   - Validates each section against rubric
4. **明辨之** — Draft is non-empty, 6/7 sections pass rubric, 1 incomplete.
5. **笃行之** — Writes to `x-ipe-docs/memory/.working/draft/react-hooks/`.

**Output:**
```yaml
operation_output:
  success: true
  operation: "fill_structure"
  result:
    completed_draft: |
      # React Hooks
      > Comprehensive notes on React Hooks covering patterns, lifecycle, and custom hooks.
      ## Table of Contents
      1. [Introduction](01.introduction.md)
      2. [Core Concepts](02.core-concepts.md)
      ...
    rubric_score: 0.91
    incomplete_count: 1
    writes_to: "x-ipe-docs/memory/.working/draft/"
  errors: []
```

**Notes:**
- Section 07 in the draft contains: `[INCOMPLETE: no knowledge gathered for open questions]`
- The orchestrator may choose to re-run `request_knowledge` + extraction for section 07, or accept the draft with the gap.
- `overview.md` was generated in the draft folder alongside section files.
