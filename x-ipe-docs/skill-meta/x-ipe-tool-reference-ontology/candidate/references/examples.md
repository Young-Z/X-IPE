# x-ipe-tool-reference-ontology — Examples

## Example 1: Search Ontology for "authentication"

**Scenario:** Find all knowledge entities related to authentication across all ontology graphs.

**Operation:** `search`

**Step 1 — Run search:**
```bash
python3 .github/skills/x-ipe-tool-ontology/scripts/search.py \
    --query "authentication" \
    --scope all \
    --ontology-dir x-ipe-docs/knowledge-base/.ontology/ \
    --depth 3 \
    --page-size 20 \
    --page 1 \
    > /tmp/ontology-search-result.json
```

**Step 2 — Push to UI (BLOCKING — must execute):**
```bash
python3 .github/skills/x-ipe-tool-ontology/scripts/ui-callback.py \
    --results-json /tmp/ontology-search-result.json
```

**Expected output (from search.py):**
```json
{
  "query": "authentication",
  "scope": "all",
  "matches": [
    {
      "entity": {
        "id": "know_a1b2c3d4",
        "type": "KnowledgeNode",
        "properties": {
          "label": "JWT Authentication",
          "node_type": "concept",
          "description": "Token-based authentication using JSON Web Tokens",
          "dimensions": { "domain": ["security", "authentication"], "technology": ["JWT"] },
          "source_files": ["src/auth/jwt_handler.py"],
          "weight": 7
        }
      },
      "score": 1.0,
      "provenance": "security.jsonl",
      "match_fields": ["label"]
    }
  ],
  "subgraph": {
    "nodes": ["know_a1b2c3d4", "know_e5f6a7b8"],
    "edges": [
      { "from": "know_a1b2c3d4", "rel": "depends_on", "to": "know_e5f6a7b8" }
    ]
  },
  "total_count": 1,
  "page": 1,
  "page_size": 20
}
```

---

## Example 2: Query All Concept-Type Entities

**Scenario:** List all KnowledgeNode entities where `node_type` is `concept` in a specific graph.

**Operation:** `query`

```bash
python3 .github/skills/x-ipe-tool-ontology/scripts/ontology.py query \
    --type KnowledgeNode \
    --where '{"node_type": "concept"}' \
    --graph x-ipe-docs/knowledge-base/.ontology/security.jsonl
```

**Expected output:**
```json
[
  {
    "id": "know_a1b2c3d4",
    "type": "KnowledgeNode",
    "properties": {
      "label": "JWT Authentication",
      "node_type": "concept",
      "description": "Token-based authentication using JSON Web Tokens",
      "dimensions": { "domain": ["security", "authentication"] },
      "source_files": ["src/auth/jwt_handler.py"],
      "weight": 7
    }
  },
  {
    "id": "know_c9d0e1f2",
    "type": "KnowledgeNode",
    "properties": {
      "label": "OAuth2 Flow",
      "node_type": "concept",
      "description": "Authorization framework using OAuth 2.0 protocol",
      "dimensions": { "domain": ["security", "authorization"] },
      "source_files": ["src/auth/oauth2.py"],
      "weight": 6
    }
  }
]
```

---

## Example 3: Find Related Entities for a Specific Node

**Scenario:** Discover all entities related to `know_a1b2c3d4` via outgoing `depends_on` relations.

**Operation:** `related`

```bash
python3 .github/skills/x-ipe-tool-ontology/scripts/ontology.py related \
    --id know_a1b2c3d4 \
    --rel depends_on \
    --dir outgoing \
    --graph x-ipe-docs/knowledge-base/.ontology/security.jsonl
```

**Expected output:**
```json
[
  {
    "entity": {
      "id": "know_e5f6a7b8",
      "type": "KnowledgeNode",
      "properties": {
        "label": "Cryptographic Key Management",
        "node_type": "concept",
        "source_files": ["src/crypto/keys.py"]
      }
    },
    "relation": {
      "from": "know_a1b2c3d4",
      "rel": "depends_on",
      "to": "know_e5f6a7b8"
    }
  }
]
```

**Without filters (all relations, all directions):**
```bash
python3 .github/skills/x-ipe-tool-ontology/scripts/ontology.py related \
    --id know_a1b2c3d4 \
    --graph x-ipe-docs/knowledge-base/.ontology/security.jsonl
```

---

## Example 4: Find Path Between Two Entities

**Scenario:** Find the shortest path between "JWT Authentication" (`know_a1b2c3d4`) and "API Gateway" (`know_f3g4h5i6`).

**Operation:** `find_path`

```bash
python3 .github/skills/x-ipe-tool-ontology/scripts/ontology.py find-path \
    --from know_a1b2c3d4 \
    --to know_f3g4h5i6 \
    --graph x-ipe-docs/knowledge-base/.ontology/security.jsonl
```

**Expected output:**
```json
{
  "path": ["know_a1b2c3d4", "know_e5f6a7b8", "know_f3g4h5i6"],
  "edges": [
    { "from": "know_a1b2c3d4", "rel": "depends_on", "to": "know_e5f6a7b8" },
    { "from": "know_e5f6a7b8", "rel": "related_to", "to": "know_f3g4h5i6" }
  ],
  "length": 2
}
```

**When no path exists:**
```json
{
  "path": [],
  "edges": [],
  "length": -1
}
```

---

## Example 5: Load Full Graph State

**Scenario:** Inspect all entities and relations in a named graph.

**Operation:** `load`

```bash
python3 .github/skills/x-ipe-tool-ontology/scripts/ontology.py load \
    --graph x-ipe-docs/knowledge-base/.ontology/security.jsonl
```

**Expected output:**
```json
{
  "entities": {
    "know_a1b2c3d4": {
      "id": "know_a1b2c3d4",
      "type": "KnowledgeNode",
      "properties": {
        "label": "JWT Authentication",
        "node_type": "concept"
      }
    },
    "know_e5f6a7b8": {
      "id": "know_e5f6a7b8",
      "type": "KnowledgeNode",
      "properties": {
        "label": "Cryptographic Key Management",
        "node_type": "concept"
      }
    }
  },
  "relations": [
    { "from": "know_a1b2c3d4", "rel": "depends_on", "to": "know_e5f6a7b8" }
  ]
}
```
