---
name: x-ipe-knowledge-ontology-synthesizer
description: Cross-graph integration engine that discovers related ontology graphs, normalizes vocabulary into canonical terms, and links nodes across domains. Delegates JSONL I/O to scripts/synthesis_ops.py. Triggers on operations like "discover_related", "wash_terms", "link_nodes".
---

# Ontology Synthesizer — Knowledge Skill

## Purpose

AI Agents follow this skill to integrate ontology graphs across domains:
1. Discover related graphs by scanning for overlapping entities and vocabulary
2. Normalize inconsistent terminology into a canonical vocabulary
3. Link nodes across domains at class-level first, then instance-level (hierarchical constraint)

---

## Important Notes

BLOCKING: This is a multi-operation skill with three named operations. The orchestrator calls each operation separately in sequence: `discover_related` → `wash_terms` → `link_nodes`.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.
CRITICAL: Operations are stateless services — the orchestrator passes full context per call. No state is retained between operation invocations.
CRITICAL: Hierarchical linking (BR-1): Class-level relationships MUST exist before instance-level relationships. The `link_nodes` instance tier enforces this constraint — it returns empty results if no class relations exist for the target domains.
CRITICAL: The synthesizer writes to `.ontology/relations/` (new) and updates entities in `.ontology/instances/` (existing). It does NOT modify `.ontology/schema/` or `.ontology/vocabulary/`.

---

## About

This skill serves as the cross-graph integration layer. Given ontology graphs built by `x-ipe-knowledge-ontology-builder` (059-C), it discovers overlap, normalizes vocabulary, and creates typed relationships between entities in different domains.

**Key Concepts:**
- **Cross-Graph Discovery** — Scans entity labels and class IDs across graphs to identify overlapping concepts with confidence scoring (1.0 exact, 0.8 slug-match, 0.6 substring).
- **Vocabulary Normalization** — Groups synonyms via case-insensitive matching, slug normalization, and abbreviation expansion. Selects the most descriptive canonical form. Preserves SKOS broader/narrower hierarchy.
- **Hierarchical Linking** — Two tiers: class-level first creates `related_to` relations between matching classes; instance-level then links instances only within already-linked class domains.
- **Confidence Scoring** — 1.0 for exact label match, 0.8 for slug-match (different casing/separators), 0.6 for substring overlap.
- **Chunk Rotation** — Relations stored in `_relations.NNN.jsonl` with max 5000 records per chunk, using the same rotation pattern as `instance.NNN.jsonl`.
- **JSONL Event Sourcing** — All relation writes and entity updates use the `{op, type, id, ts, props}` envelope, consistent with the builder.
- **writes_to Discipline** — Each operation declares its write targets so the orchestrator can predict side effects.

---

## When to Use

```yaml
triggers:
  - "Discover overlapping concepts across ontology graphs"
  - "Normalize inconsistent vocabulary across domains"
  - "Link nodes across ontology domains"
  - "Create cross-domain relationships"
  - "After ontology-builder completes (auto-trigger)"
```

---

## Input Parameters

```yaml
input:
  operation: discover_related | wash_terms | link_nodes
  context:
    ontology_dir: "path to .ontology/ root"
    # Operation-specific fields — see each operation contract
```

### Input Initialization

```xml
<input_init>
  <field name="context.ontology_dir" source="Orchestrator or project default" default="x-ipe-docs/memory/.ontology">
    <validation>Must be a valid directory path containing schema/, instances/, vocabulary/</validation>
  </field>
  <field name="context.source_graph" source="Orchestrator" default="none">
    <validation>Required for discover_related. Must be a JSONL file path relative to instances/ or schema/</validation>
  </field>
  <field name="context.search_scope" source="Orchestrator or default" default="all">
    <validation>Must be "all" or comma-separated list of graph file paths</validation>
  </field>
  <field name="context.tier" source="Orchestrator" default="class">
    <validation>Required for link_nodes. Must be "class" or "instance"</validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Ontology directory accessible</name>
    <verification>context.ontology_dir exists with schema/, instances/, vocabulary/ subdirectories</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>At least two graphs exist</name>
    <verification>At least two instance chunk files or class-registry entries exist for cross-graph operations</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Relations folder initialized</name>
    <verification>.ontology/relations/ exists (run init_relations if not)</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: discover_related

> **Contract:**
> - **Input:** source_graph: string (JSONL file path), search_scope: "all" | string[] (graph paths)
> - **Output:** related_graphs: string[], overlap_candidates: overlap_candidate[]
> - **Writes To:** stdout (JSON result) — no filesystem writes
> - **Delegates To:** `scripts/synthesis_ops.py discover`
> - **Constraints:** Stateless; re-analyzes from scratch every invocation (no cache)

**When:** Orchestrator needs to find which graphs have overlapping concepts with a source graph.

```xml
<operation name="discover_related">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. LOAD source graph entities from ontology_dir:
         - Read class-registry.jsonl for class labels and IDs
         - Read instance chunk files for instance labels and class assignments
      2. IDENTIFY search targets:
         - IF search_scope == "all" → list all instance chunk files and class-registry
         - ELSE → use specified graph file paths
      3. BUILD source entity index: {id → label, slug, class}
    </action>
    <output>Source entity index loaded, target graphs identified</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE source_graph exists and is non-empty
      2. VALIDATE search_scope targets exist
      3. FOR EACH target graph (excluding source):
         a. Load target entities (same approach as source)
         b. Compare source labels/slugs against target labels/slugs
         c. For each overlap: create overlap_candidate:
            - exact label match → confidence 1.0
            - slug match (same slugified form, different original) → confidence 0.8
            - substring overlap (one label contains the other) → confidence 0.6
      4. COLLECT related_graphs[] (graphs with ≥1 overlap candidate)
    </action>
    <constraints>
      - BLOCKING: Missing source_graph → return error SOURCE_NOT_FOUND
      - Minimum confidence threshold: 0.6 (below is noise)
    </constraints>
    <output>overlap_candidates[] and related_graphs[] computed</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. DEDUPLICATE overlap candidates (same source_id + target_id pair)
      2. SORT by confidence_score descending
      3. LOG summary: "{N} overlap candidates across {M} related graphs"
    </action>
    <output>Deduplicated, sorted overlap candidates</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY each overlap_candidate has required fields: source_id, target_id, graph_source, graph_target, confidence_score
      2. VERIFY related_graphs[] contains only graphs with actual overlap (not empty matches)
    </action>
    <output>Validated output ready</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. EXECUTE:
         ```
         python3 scripts/synthesis_ops.py discover \
           --ontology-dir {ontology_dir} \
           --source-graph {source_graph} \
           --search-scope {search_scope}
         ```
      2. RETURN operation_output with related_graphs[] and overlap_candidates[]
    </action>
    <output>discover_related complete</output>
  </phase_5>

</operation>
```

### Operation: wash_terms

> **Contract:**
> - **Input:** graphs: string[] (graph paths), overlap_candidates: overlap_candidate[] (from discover_related)
> - **Output:** canonical_vocabulary: canonical_entry[], normalization_map: normalization_entry[]
> - **Writes To:** stdout (JSON result) — no filesystem writes
> - **Delegates To:** `scripts/synthesis_ops.py wash`
> - **Constraints:** Stateless; preserves SKOS broader/narrower hierarchy from vocabulary files

**When:** Orchestrator has overlap candidates and needs to normalize vocabulary before linking.

```xml
<operation name="wash_terms">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. LOAD overlap candidates (from discover_related output or file)
      2. LOAD all entity labels from involved graphs
      3. LOAD existing vocabulary files from .ontology/vocabulary/ for SKOS hierarchy data
    </action>
    <output>All labels and vocabulary hierarchy loaded</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE overlap_candidates is non-empty (warn if empty — proceed with no-op)
      2. GROUP synonyms using three strategies:
         a. Case-insensitive match ("flask" = "Flask" = "FLASK")
         b. Slug normalization ("web-framework" = "WebFramework" = "web_framework")
         c. Abbreviation expansion ("JS" ↔ "JavaScript") — built-in abbreviation table
      3. For each synonym group, SELECT canonical form:
         - Prefer most descriptive (longest non-abbreviation)
         - If tied, prefer title case
    </action>
    <constraints>
      - BLOCKING: Invalid candidates format → return error INPUT_VALIDATION_FAILED
      - Preserve SKOS broader/narrower from vocabulary files — do not flatten hierarchy
    </constraints>
    <output>Synonym groups with canonical forms selected</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. BUILD canonical_vocabulary[]: list of {canonical, aliases[]}
      2. BUILD normalization_map[]: list of {original_term, canonical_term, source_graph, confidence}
      3. VERIFY no canonical term collisions (two different canonical forms for same slug)
    </action>
    <output>canonical_vocabulary and normalization_map built</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY each normalization_map entry has required fields
      2. VERIFY SKOS hierarchy is preserved for any vocabulary terms
    </action>
    <output>Validated normalization output</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. SAVE overlap_candidates to temp file if passing via file
      2. EXECUTE:
         ```
         python3 scripts/synthesis_ops.py wash \
           --ontology-dir {ontology_dir} \
           --candidates-json {candidates_path_or_stdin}
         ```
      3. RETURN operation_output with canonical_vocabulary and normalization_map
    </action>
    <output>wash_terms complete</output>
  </phase_5>

</operation>
```

### Operation: link_nodes

> **Contract:**
> - **Input:** graphs: string[], normalization_map: normalization_entry[], canonical_vocabulary: canonical_entry[], tier: "class" | "instance"
> - **Output:** cross_references: cross_reference[], linked_graph: dict (summary)
> - **Writes To:** `.ontology/relations/_relations.NNN.jsonl` (new relations), `.ontology/instances/` (entity synthesis updates)
> - **Delegates To:** `scripts/synthesis_ops.py link`
> - **Constraints:** BR-1 — class-level relations MUST exist before instance-level; vocabulary translation applied at instance tier

**When:** Orchestrator has normalized vocabulary and needs to create cross-domain relationships.

```xml
<operation name="link_nodes">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. LOAD normalization_map and canonical_vocabulary (from wash_terms output or files)
      2. LOAD entity data from specified graphs
      3. IF tier == "instance": LOAD existing class-level relations from _relations.NNN.jsonl
      4. READ _synthesis_meta.json for current synthesis_version
    </action>
    <output>All input data and existing state loaded</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE graphs[], normalization_map, canonical_vocabulary are non-empty
      2. VALIDATE tier is "class" or "instance"
      3. IF tier == "instance" AND no class-level relations exist:
         → LOG "No class-level relationships found — instance linking skipped"
         → RETURN empty cross_references[]
      4. PROPOSE relations:
         - **Class tier:** Match normalized class labels across graphs → create `related_to`
         - **Instance tier:** For each class-level relation, find instances of both linked classes, apply normalization_map to instance labels, match by normalized label
    </action>
    <constraints>
      - BLOCKING: tier=="instance" without class relations → return empty (BR-1)
      - BLOCKING: Missing normalization_map → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Proposed relations ready for dedup check</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. CHECK existing relations for duplicates (same from_id + to_id + relation_type)
      2. SKIP duplicates, log skip reason
      3. ASSIGN relation IDs: sequential rel-NNN (scan existing chunks for max ID)
      4. IF --dry-run → return proposed relations without writing
    </action>
    <output>Deduplicated relations with IDs assigned</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY each cross_reference has: from_id, to_id, relation_type, source_graph, target_graph, synthesis_version
      2. VERIFY relation JSONL records use event-sourcing envelope: {op, type, id, ts, props}
      3. IF tier == "instance": VERIFY entity update records have synthesize_id and synthesize_message
    </action>
    <output>All records validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. SAVE normalization_map and canonical_vocabulary to temp files
      2. EXECUTE:
         ```
         python3 scripts/synthesis_ops.py link \
           --ontology-dir {ontology_dir} \
           --tier {tier} \
           --normalization-map-json {map_path} \
           --canonical-vocab-json {vocab_path} \
           --graphs {graph1},{graph2}[,...]
         ```
      3. VERIFY writes: check _relations.NNN.jsonl updated, _synthesis_meta.json bumped
      4. IF tier == "instance": VERIFY entity updates written to instance chunk files
      5. RETURN operation_output with cross_references[] and linked_graph summary
    </action>
    <output>link_nodes complete</output>
  </phase_5>

</operation>
```

---

## Output Result

```yaml
# discover_related output:
operation_output:
  success: true | false
  operation: "discover_related"
  result:
    related_graphs: ["string (graph file paths)"]
    overlap_candidates:
      - source_id: "string"
        target_id: "string"
        graph_source: "string"
        graph_target: "string"
        confidence_score: "float (0.6–1.0)"
  errors: []

# wash_terms output:
operation_output:
  success: true | false
  operation: "wash_terms"
  result:
    canonical_vocabulary:
      - canonical: "string"
        aliases: ["string"]
    normalization_map:
      - original_term: "string"
        canonical_term: "string"
        source_graph: "string"
        confidence: "float"
  errors: []

# link_nodes output:
operation_output:
  success: true | false
  operation: "link_nodes"
  result:
    cross_references:
      - from_id: "string"
        to_id: "string"
        relation_type: "related_to"
        source_graph: "string"
        target_graph: "string"
        synthesis_version: "int"
    relations_written: "int"
    duplicates_skipped: "int"
    entities_updated: "int"           # instance tier only
    writes_to: "string (.ontology/relations/)"
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
    <name>discover_related returns valid overlap data</name>
    <verification>overlap_candidates[] entries have all required fields (source_id, target_id, graph_source, graph_target, confidence_score)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>wash_terms produces canonical vocabulary</name>
    <verification>normalization_map entries have all required fields (original_term, canonical_term, source_graph, confidence)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>link_nodes writes relations with event-sourcing envelope</name>
    <verification>_relations.NNN.jsonl records have {op, type, id, ts, props} format</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Hierarchical linking enforced</name>
    <verification>Instance-tier linking returns empty when no class-level relations exist (BR-1)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Entity synthesis fields updated</name>
    <verification>After instance-tier linking, processed entities have synthesize_id (ISO-8601) and synthesize_message set</verification>
  </checkpoint>
  <checkpoint required="if_applicable">
    <name>Chunk rotation works</name>
    <verification>New chunk created when _relations.NNN.jsonl exceeds 5000 records</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INPUT_VALIDATION_FAILED` | Missing/invalid operation parameters | Return error with field details |
| `SOURCE_NOT_FOUND` | source_graph path does not exist | Return error with path details |
| `ONTOLOGY_DIR_ERROR` | Cannot access .ontology/ directory | Return error with path details |
| `NO_GRAPHS_FOUND` | No instance/class files found in ontology_dir | Return error — builder must run first |
| `RELATION_WRITE_FAILED` | Cannot write to _relations.NNN.jsonl | Return error with I/O details |
| `CORRUPT_JSONL` | Invalid JSON lines in chunk files | Skip corrupted lines, log warning, continue |
| `DUPLICATE_RELATION` | Same from/to/type relation already exists | Skip (not an error), log and continue |

---

## Patterns & Anti-Patterns

| Pattern | When | Key Actions |
|---------|------|-------------|
| Full pipeline | New domain integration | discover → wash → link(class) → link(instance) |
| Class-only linking | Quick structural overview | discover → wash → link(class) — skip instance tier |
| Auto-trigger | After builder completes | Orchestrator calls discover_related automatically |
| Re-synthesis | Vocabulary updated | Re-run wash → link to update relations |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip wash_terms | Inconsistent vocabulary causes false negatives | Always wash before linking |
| Instance before class | Violates BR-1, structurally unsound | Class-tier first, instance-tier second |
| Cache discover results | Stale overlap data | Re-discover from scratch each run |
| Manual relation ID | ID collision risk | Let synthesis_ops.py generate sequential IDs |

---

## Examples

See `references/examples.md` for worked examples of all three operations.
