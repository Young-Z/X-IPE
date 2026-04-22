# Ontology Synthesizer — Cross-Graph Linking Examples

## Example 1: discover_related — Two Overlapping Web Framework Graphs

**Scenario:** Two separate knowledge ingestion sessions produced ontology graphs about web frameworks in different languages. Graph 1 covers Python (Flask, Django) and Graph 2 covers JavaScript (Express, React). Both mention the concept "WebFramework" and share the vocabulary term "REST API".

**Command:**
```bash
python3 scripts/synthesis_ops.py discover \
  --ontology-dir x-ipe-docs/memory/.ontology \
  --source-graph instance.001.jsonl \
  --search-scope all
```

**Output:**
```json
{
  "success": true,
  "related_graphs": ["instance.002.jsonl"],
  "overlap_candidates": [
    {
      "source_id": "web-framework",
      "target_id": "web-framework",
      "graph_source": "instance.001.jsonl",
      "graph_target": "instance.002.jsonl",
      "confidence_score": 1.0
    },
    {
      "source_id": "rest-api",
      "target_id": "rest-api",
      "graph_source": "instance.001.jsonl",
      "graph_target": "instance.002.jsonl",
      "confidence_score": 1.0
    }
  ]
}
```

---

## Example 2: discover_related — No Overlap

**Scenario:** Graph 1 covers "Database Engines" and Graph 2 covers "UI Design Patterns". No shared concepts.

**Output:**
```json
{
  "success": true,
  "related_graphs": [],
  "overlap_candidates": []
}
```

---

## Example 3: wash_terms — Normalizing Synonyms

**Scenario:** Overlap candidates reveal inconsistent labels: "JS" (graph 1), "JavaScript" (graph 2), "javascript" (graph 3). Also "WebFramework" (graph 1) vs "web-framework" (graph 2).

**Command:**
```bash
python3 scripts/synthesis_ops.py wash \
  --ontology-dir x-ipe-docs/memory/.ontology \
  --candidates-json /tmp/overlap_candidates.json
```

**Output:**
```json
{
  "success": true,
  "canonical_vocabulary": [
    {"canonical": "JavaScript", "aliases": ["JS", "javascript", "Javascript"]},
    {"canonical": "web-framework", "aliases": ["WebFramework", "Web Framework"]}
  ],
  "normalization_map": [
    {"original_term": "JS", "canonical_term": "JavaScript", "source_graph": "instance.001.jsonl", "confidence": 0.8},
    {"original_term": "javascript", "canonical_term": "JavaScript", "source_graph": "instance.003.jsonl", "confidence": 1.0},
    {"original_term": "WebFramework", "canonical_term": "web-framework", "source_graph": "instance.001.jsonl", "confidence": 0.8}
  ]
}
```

---

## Example 4: link_nodes — Class-Level Linking

**Scenario:** After washing terms, we know "web-framework" is a canonical class shared across two graphs. We create a class-level `related_to` relation.

**Command:**
```bash
python3 scripts/synthesis_ops.py link \
  --ontology-dir x-ipe-docs/memory/.ontology \
  --tier class \
  --normalization-map-json /tmp/normalization_map.json \
  --canonical-vocab-json /tmp/canonical_vocabulary.json \
  --graphs instance.001.jsonl,instance.002.jsonl
```

**Output:**
```json
{
  "success": true,
  "cross_references": [
    {
      "from_id": "web-framework",
      "to_id": "web-framework",
      "relation_type": "related_to",
      "source_graph": "instance.001.jsonl",
      "target_graph": "instance.002.jsonl",
      "synthesis_version": 1
    }
  ],
  "relations_written": 1,
  "duplicates_skipped": 0,
  "writes_to": "x-ipe-docs/memory/.ontology/relations/_relations.001.jsonl"
}
```

**Written to `_relations.001.jsonl`:**
```jsonl
{"op":"create","type":"Relation","id":"rel-001","ts":"2026-04-16T04:00:00Z","props":{"from_id":"web-framework","to_id":"web-framework","relation_type":"related_to","source_graph":"instance.001.jsonl","target_graph":"instance.002.jsonl","synthesis_version":1,"synthesized_with":["instance.001.jsonl","instance.002.jsonl"]}}
```

---

## Example 5: link_nodes — Instance-Level Linking

**Scenario:** Class-level `related_to` exists between "web-framework" in both graphs. Now we link instances: "Flask" (graph 1) is class "web-framework", and "Express" (graph 2) is also class "web-framework". The instance labels don't match, so they are linked via their shared class relationship.

**Command:**
```bash
python3 scripts/synthesis_ops.py link \
  --ontology-dir x-ipe-docs/memory/.ontology \
  --tier instance \
  --normalization-map-json /tmp/normalization_map.json \
  --canonical-vocab-json /tmp/canonical_vocabulary.json \
  --graphs instance.001.jsonl,instance.002.jsonl
```

**Output:**
```json
{
  "success": true,
  "cross_references": [
    {
      "from_id": "inst-001",
      "to_id": "inst-005",
      "relation_type": "related_to",
      "source_graph": "instance.001.jsonl",
      "target_graph": "instance.002.jsonl",
      "synthesis_version": 2
    }
  ],
  "entities_updated": 2,
  "relations_written": 1,
  "duplicates_skipped": 0,
  "writes_to": "x-ipe-docs/memory/.ontology/relations/_relations.001.jsonl"
}
```

**Entity synthesis update (appended to instance.001.jsonl):**
```jsonl
{"op":"update","type":"KnowledgeNode","id":"inst-001","ts":"2026-04-16T04:00:00Z","props":{"synthesize_id":"2026-04-16T04:00:00Z","synthesize_message":"Cross-domain linking: Flask ↔ Express (web-framework)"}}
```

---

## Example 6: Instance Linking Blocked by Missing Class Relations

**Scenario:** Attempting instance-level linking between graphs that have no class-level relations.

**Command:**
```bash
python3 scripts/synthesis_ops.py link \
  --ontology-dir x-ipe-docs/memory/.ontology \
  --tier instance \
  --normalization-map-json /tmp/normalization_map.json \
  --canonical-vocab-json /tmp/canonical_vocabulary.json \
  --graphs instance.001.jsonl,instance.003.jsonl
```

**Output:**
```json
{
  "success": true,
  "cross_references": [],
  "entities_updated": 0,
  "relations_written": 0,
  "duplicates_skipped": 0,
  "message": "No class-level relationships found — instance linking skipped",
  "writes_to": null
}
```

---

## Example 7: init_relations — Bootstrap

**Command:**
```bash
python3 scripts/synthesis_ops.py init_relations \
  --ontology-dir x-ipe-docs/memory/.ontology
```

**Output (first run):**
```json
{"success": true, "message": "Relations initialized", "writes_to": "x-ipe-docs/memory/.ontology/relations/_relations.001.jsonl"}
```

**Output (subsequent run):**
```json
{"success": true, "message": "Relations already initialized"}
```
