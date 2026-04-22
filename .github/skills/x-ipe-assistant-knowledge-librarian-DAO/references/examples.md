# Examples — Knowledge Librarian

## Example 1: Construction Pipeline (User Manual)

**Input:**
```yaml
request: "Build a user manual for the X-IPE web application"
output_format: "markdown"
```

**Execution Trace:**

```
道 · Knowledge Librarian — ready.

Phase 0: Session librarian-2026-04-20T071834 created

Phase 1 — 格物 (Plan):
  1.1 Discovery: Found 11 skills → 2 extractors, 3 constructors, 1 keeper, 2 presenters, 2 ontology, 1 mimic
  1.2 Classification: type = "construction", constructor = "x-ipe-knowledge-constructor-user-manual"
  1.3 Framework: 8-section user manual layout received
  1.4 Overview: Extracted high-level app overview from source paths
  1.5 Rubric: 8 rubric metrics (one per section) received
  1.6 Plan: 12 knowledge requests generated (4 web, 8 memory)

Phase 2 — 致知 (Execute):
  2.1 Extract: 12/12 requests fulfilled (10 complete, 2 partial)
  2.2 Fill: Draft completed with 1 INCOMPLETE section (Troubleshooting)
  2.3 Critique: Iteration 1 — fail (Troubleshooting gaps)
       Replan: 2 additional requests for Troubleshooting
       Iteration 2 — pass
  2.4 Ontology: 15 entities registered, 3 cross-graph relations created
  2.5 Store: Saved to x-ipe-docs/memory/procedural/x-ipe-web-app-user-manual.md
  2.6 Present: Rendered markdown summary
```

**Output:**
```yaml
pipeline_output:
  pipeline_status: "success"
  pipeline_summary: "User manual constructed in 2 iterations, 15 entities registered, stored to procedural/"
  stored_path: "x-ipe-docs/memory/procedural/x-ipe-web-app-user-manual.md"
  ontology_result: { entities_created: 15, relations_created: 3, terms_normalized: 5 }
  presented_output: { format: "markdown", content: "..." }
```

---

## Example 2: Ontology-Only Pipeline

**Input:**
```yaml
request: "Discover and link ontology graphs for python-frameworks and web-development"
request_type_override: "ontology_only"
```

**Execution Trace:**

```
道 · Knowledge Librarian — ready.

Phase 1 — 格物 (Plan):
  1.1 Discovery: Found 11 skills
  1.2 Classification: type = "ontology_only" (override)
  1.3–1.6: Skipped (not construction)

Phase 2 — 致知 (Execute):
  2.1–2.3: Skipped (not construction/extraction)
  2.4 Ontology: discover_related found 8 overlapping entities
       wash_terms normalized 5 terms
       link_nodes created 3 class-level + 2 instance-level relations
  2.5: Skipped (ontology_only — no content to store)
  2.6 Present: Rendered graph summary
```

**Output:**
```yaml
pipeline_output:
  pipeline_status: "success"
  pipeline_summary: "Ontology integration complete: 3 class relations, 2 instance relations, 5 terms normalized"
  ontology_result: { entities_created: 0, relations_created: 5, terms_normalized: 5 }
```

---

## Example 3: Extraction Pipeline (Direct)

**Input:**
```yaml
request: "Extract knowledge about React hooks from https://react.dev/reference/react"
```

**Execution Trace:**

```
Phase 1 — 格物:
  1.2 Classification: type = "extraction"
  1.3–1.6: Skipped

Phase 2 — 致知:
  2.1 Extract: Invoked extractor-web on https://react.dev/reference/react
  2.2–2.3: Skipped (no construction)
  2.4 Ontology: 8 entities from extracted content
  2.5 Store: Saved to x-ipe-docs/memory/semantic/react-hooks-reference.md
  2.6 Present: Rendered markdown summary
```

---

## Example 4: Partial Failure (Graceful Degradation)

**Input:**
```yaml
request: "Build notes from internal design documents"
```

**Execution Trace (with extractor failure):**

```
Phase 2 — 致知:
  2.1 Extract: 3/5 requests fulfilled, 2 failed (timeout)
       ⚠ Step marked as "failed" — continuing with partial knowledge
  2.2 Fill: Draft completed with 2 INCOMPLETE sections
  2.3 Critique: 3 iterations, final verdict = partial_quality
       ⚠ Max iterations reached — proceeding with partial draft
  2.4 Ontology: 6 entities registered
  2.5 Store: Saved (with partial_quality flag in metadata)
```

**Output:**
```yaml
pipeline_output:
  pipeline_status: "partial"
  pipeline_summary: "Notes constructed with partial quality (2 sections incomplete, extractor timeout)"
  completed_steps:
    - { name: "致知_1_execute", status: "failed" }
    - { name: "致知_3_critique", status: "done", iterations: 3, verdict: "partial_quality" }
```
