---
name: x-ipe-tool-reference-ontology
description: Search and query the knowledge base ontology for entity lookup, graph traversal, and semantic search. Use for finding knowledge entities, exploring relationships, and searching across ontology graphs. Triggers on requests like "search ontology", "query ontology", "find related entities", "knowledge graph search".
---

# KB Ontology Reference (Search-Only)

## Purpose

AI Agents follow this skill to search and query the Knowledge Base Ontology to:
1. Search entities across ontology graphs by keyword and push results to the KB Graph Viewer UI
2. Query and filter entities by type and properties
3. Explore entity relationships and find shortest paths between knowledge nodes
4. Load full graph state for inspection

---

## Important Notes

BLOCKING: The **search** operation has TWO mandatory steps (search.py → ui-callback.py). You MUST execute BOTH steps in sequence. Do NOT skip Step 2.

CRITICAL: This is a **READ-ONLY** skill. For creating, updating, or deleting entities, building graphs, managing dimensions, or retagging — use `x-ipe-tool-ontology`.

CRITICAL: Scripts are NOT copied — they live at `.github/skills/x-ipe-tool-ontology/scripts/`. All commands reference scripts at that original location.

---

## About

This skill provides a read-only interface to the Knowledge Base Ontology system. It exposes search, query, traversal, and inspection operations backed by append-only JSONL event-sourced data.

**Key Concepts:**
- **KnowledgeNode** — Primary entity type representing a knowledge concept, entity, or document
- **Named Graph** — A `.jsonl` file grouping related entities by cluster (e.g., `security.jsonl`)
- **Relation** — Typed directional link between entities (e.g., `depends_on`, `related_to`)
- **Subgraph** — BFS-extracted neighborhood around matched entities returned by search

**Entity Model:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `label` | string | ✅ | Human-readable name |
| `node_type` | string | ✅ | `concept`, `entity`, or `document` |
| `description` | string | ❌ | Brief summary |
| `dimensions` | object | ❌ | Canonical dimension keys → values |
| `source_files` | string[] | ✅ | Project-root-relative paths |
| `weight` | number | ❌ | 1-10 (default: 5) |

**Relation Types:**

| Type | Acyclic | Description |
|------|---------|-------------|
| `related_to` | No | Bidirectional topical overlap |
| `depends_on` | Yes | Understanding dependency |
| `is_type_of` | No | Taxonomy/classification |
| `part_of` | No | Component composition |
| `described_by` | No | Explanatory relation |

**Entity ID Format:** `know_{uuid_hex[:8]}` (e.g., `know_a1b2c3d4`)

**Data Storage:**

| Store | Location |
|-------|----------|
| Master entities | `x-ipe-docs/knowledge-base/.ontology/_entities.jsonl` |
| Named graphs | `x-ipe-docs/knowledge-base/.ontology/{cluster}.jsonl` |
| Graph index | `x-ipe-docs/knowledge-base/.ontology/.graph-index.json` |

---

## When to Use

```yaml
triggers:
  - "search ontology"
  - "query ontology"
  - "find related entities"
  - "ontology search"
  - "knowledge graph search"
  - "find path between entities"
  - "load ontology graph"
  - "list knowledge nodes"

not_for:
  - "Creating/updating/deleting entities → use x-ipe-tool-ontology"
  - "Building or pruning graphs → use x-ipe-tool-ontology"
  - "Dimension registry operations → use x-ipe-tool-ontology"
  - "Retagging filed-untagged files → use x-ipe-tool-ontology"
```

---

## Input Parameters

```yaml
input:
  operation: "search | query | related | find_path | load"
  search_params:
    query: "search text"
    scope: "all | comma-separated .jsonl filenames"
    ontology_dir: "x-ipe-docs/knowledge-base/.ontology/"
    depth: 3
    page_size: 20
    page: 1
  query_params:
    entity_type: "KnowledgeNode"
    where: '{"node_type": "concept"}'
    graph_path: "path/to/graph.jsonl"
  related_params:
    entity_id: "know_a1b2c3d4"
    relation_type: "depends_on"
    direction: "outgoing"
    graph_path: "path/to/graph.jsonl"
  find_path_params:
    from_id: "know_a1b2c3d4"
    to_id: "know_e5f6g7h8"
    graph_path: "path/to/graph.jsonl"
  load_params:
    graph_path: "path/to/graph.jsonl"
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies which read operation to perform" />

  <field name="ontology_dir">
    <steps>
      1. If caller provides ontology_dir, use it
      2. Default: "x-ipe-docs/knowledge-base/.ontology/"
    </steps>
  </field>

  <field name="graph_path">
    <steps>
      1. If caller provides graph_path, use it
      2. If not provided, check .graph-index.json in ontology_dir for available graphs
      3. Prompt caller or select based on context
    </steps>
  </field>

  <field name="scope">
    <steps>
      1. If caller provides scope, use it
      2. Default: "all" (search across all named graphs)
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Ontology directory exists</name>
    <verification>Verify ontology_dir path exists and contains .jsonl graph files</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Operation is valid</name>
    <verification>operation is one of: search, query, related, find_path, load</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Required parameters present</name>
    <verification>Operation-specific required params are set (e.g., query for search, entity_id for related)</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: search

**When:** Caller needs to find entities by keyword across ontology graphs and display results in the KB Graph Viewer UI.

```xml
<operation name="search">
  <action>
    1. Run search.py to find matching entities and extract BFS subgraph:
       ```bash
       python3 .github/skills/x-ipe-tool-ontology/scripts/search.py \
           --query "{query}" \
           --scope {scope} \
           --ontology-dir {ontology_dir} \
           [--depth {depth}] [--page-size {page_size}] [--page {page}] \
           > /tmp/ontology-search-result.json
       ```
    2. Push results to KB Graph Viewer UI via callback API:
       ```bash
       python3 .github/skills/x-ipe-tool-ontology/scripts/ui-callback.py \
           --results-json /tmp/ontology-search-result.json
       ```
  </action>
  <constraints>
    - BLOCKING: Both steps MUST execute in sequence. Step 2 POSTs results to the internal callback API which broadcasts via SocketIO. Without Step 2, results will NOT appear in the UI.
    - Auth token is auto-detected from `instance/.internal_token` — no --token flag needed.
    - Port defaults to 5858 (from .x-ipe.yaml).
  </constraints>
  <output>JSON with matches (scored + paginated), BFS subgraph (nodes + edges), pagination metadata</output>
</operation>
```

### Operation: query

**When:** Caller needs to filter entities by type and property values within a specific graph.

```xml
<operation name="query">
  <action>
    1. Run ontology.py query to filter entities:
       ```bash
       python3 .github/skills/x-ipe-tool-ontology/scripts/ontology.py query \
           --type {entity_type} \
           --where '{where_json}' \
           --graph {graph_path}
       ```
  </action>
  <constraints>
    - where must be valid JSON string
    - entity_type defaults to KnowledgeNode
  </constraints>
  <output>JSON array of entities matching the filter criteria</output>
</operation>
```

### Operation: related

**When:** Caller needs to discover entities connected to a specific entity via relations.

```xml
<operation name="related">
  <action>
    1. Run ontology.py related to get connected entities:
       ```bash
       python3 .github/skills/x-ipe-tool-ontology/scripts/ontology.py related \
           --id {entity_id} \
           [--rel {relation_type}] \
           [--dir {direction}] \
           --graph {graph_path}
       ```
  </action>
  <constraints>
    - entity_id is required
    - relation_type and direction are optional filters
    - direction: "outgoing" or "incoming"
  </constraints>
  <output>JSON array of related entities with relation metadata</output>
</operation>
```

### Operation: find_path

**When:** Caller needs to find the shortest path between two entities in the ontology graph.

```xml
<operation name="find_path">
  <action>
    1. Run ontology.py find-path for BFS shortest path:
       ```bash
       python3 .github/skills/x-ipe-tool-ontology/scripts/ontology.py find-path \
           --from {from_id} \
           --to {to_id} \
           --graph {graph_path}
       ```
  </action>
  <constraints>
    - Both from_id and to_id are required
    - Returns empty path if entities are not connected
  </constraints>
  <output>JSON with ordered path of entity IDs and traversed relations</output>
</operation>
```

### Operation: load

**When:** Caller needs to inspect the full state of a named graph (all entities and relations).

```xml
<operation name="load">
  <action>
    1. Run ontology.py load to get full graph state:
       ```bash
       python3 .github/skills/x-ipe-tool-ontology/scripts/ontology.py load \
           --graph {graph_path}
       ```
  </action>
  <constraints>
    - graph_path is required
    - Returns the full materialized state (all entities + relations)
  </constraints>
  <output>JSON with entities dict and relations array for the entire graph</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "search | query | related | find_path | load"
  result:
    # search: { query, scope, matches[], subgraph{nodes[], edges[]}, total_count, page, page_size }
    # query: [ {entity}... ]
    # related: [ {entity, relation}... ]
    # find_path: { path: [id...], edges: [{from, rel, to}...] }
    # load: { entities: {id: entity...}, relations: [{from, rel, to}...] }
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed successfully</name>
    <verification>Script exited with code 0 and returned valid JSON to stdout</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Search UI callback executed</name>
    <verification>For search operation: ui-callback.py executed after search.py (both exit 0)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No mutation occurred</name>
    <verification>No entities were created, updated, or deleted — data files unchanged</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `ONTOLOGY_DIR_NOT_FOUND` | ontology_dir path does not exist | Verify path; check if ontology has been initialized |
| `GRAPH_NOT_FOUND` | Specified graph .jsonl file does not exist | List available graphs in ontology_dir or check .graph-index.json |
| `ENTITY_NOT_FOUND` | entity_id does not exist in graph | Verify ID format (`know_{hex8}`); search for entity first |
| `INVALID_WHERE_JSON` | where parameter is not valid JSON | Fix JSON syntax in the where filter |
| `UI_CALLBACK_FAILED` | ui-callback.py could not reach Flask server | Verify server is running on expected port; check instance/.internal_token exists |
| `SCRIPT_ERROR` | Python script returned exit code 1 | Check stderr output; JSON `{"error": "message"}` from script |

---

## Templates

| File | Purpose |
|------|---------|
| _None_ | This skill produces JSON output only — no document templates required |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
