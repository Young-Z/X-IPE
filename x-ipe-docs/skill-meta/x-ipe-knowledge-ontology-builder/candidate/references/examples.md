# Ontology Builder — Worked Examples

## Example 1: discover_nodes

**Scenario:** Discover domain classes from semantic memory files about web frameworks.

**Input:**
```yaml
operation: discover_nodes
context:
  source_content:
    - "x-ipe-docs/memory/semantic/flask-overview.md"
    - "x-ipe-docs/memory/semantic/react-fundamentals.md"
  depth_limit: 2
```

**Agent performs breadth-first scan and identifies:**
- "WebFramework" (top-level concept)
  - "BackendFramework" (child)
  - "FrontendFramework" (child)

**Script calls:**
```bash
python3 scripts/ontology_ops.py register_class \
  --label "WebFramework" \
  --description "Web application frameworks" \
  --source-files '["x-ipe-docs/memory/semantic/flask-overview.md","x-ipe-docs/memory/semantic/react-fundamentals.md"]' \
  --ontology-dir x-ipe-docs/memory/.ontology

python3 scripts/ontology_ops.py register_class \
  --label "BackendFramework" \
  --description "Server-side web frameworks" \
  --source-files '["x-ipe-docs/memory/semantic/flask-overview.md"]' \
  --parent "web-framework" \
  --ontology-dir x-ipe-docs/memory/.ontology
```

**Output:**
```yaml
operation_output:
  success: true
  operation: "discover_nodes"
  result:
    node_tree:
      - label: "WebFramework"
        description: "Web application frameworks"
        source_files: ["x-ipe-docs/memory/semantic/flask-overview.md", "x-ipe-docs/memory/semantic/react-fundamentals.md"]
        parent: null
        children: ["BackendFramework", "FrontendFramework"]
      - label: "BackendFramework"
        description: "Server-side web frameworks"
        source_files: ["x-ipe-docs/memory/semantic/flask-overview.md"]
        parent: "web-framework"
        children: []
      - label: "FrontendFramework"
        description: "Client-side UI frameworks"
        source_files: ["x-ipe-docs/memory/semantic/react-fundamentals.md"]
        parent: "web-framework"
        children: []
    discovery_report: "Discovered 3 classes from 2 source files. Hierarchy depth: 2."
    writes_to: "x-ipe-docs/memory/.ontology/schema/"
  errors: []
```

**JSONL written to `.ontology/schema/class-registry.jsonl`:**
```jsonl
{"op":"create","type":"KnowledgeNode","id":"web-framework","ts":"2026-04-16T12:00:00Z","props":{"label":"WebFramework","description":"Web application frameworks","source_files":["x-ipe-docs/memory/semantic/flask-overview.md","x-ipe-docs/memory/semantic/react-fundamentals.md"],"weight":5,"parent":null,"properties":[],"lifecycle":"Persistent","synthesize_id":null,"synthesize_message":null}}
{"op":"create","type":"KnowledgeNode","id":"backend-framework","ts":"2026-04-16T12:00:01Z","props":{"label":"BackendFramework","description":"Server-side web frameworks","source_files":["x-ipe-docs/memory/semantic/flask-overview.md"],"weight":5,"parent":"web-framework","properties":[],"lifecycle":"Persistent","synthesize_id":null,"synthesize_message":null}}
```

---

## Example 2: discover_properties

**Scenario:** Enrich the "BackendFramework" class with discovered properties.

**Input:**
```yaml
operation: discover_properties
context:
  class_meta:
    id: "backend-framework"
    label: "BackendFramework"
    description: "Server-side web frameworks"
    source_files: ["x-ipe-docs/memory/semantic/flask-overview.md"]
  source_content: ["x-ipe-docs/memory/semantic/flask-overview.md"]
  web_search_template: "What are common attributes of a BackendFramework?"
```

**Agent performs web search → analyzes source → proposes properties:**

**Script call:**
```bash
python3 scripts/ontology_ops.py add_properties \
  --class-id "backend-framework" \
  --properties '[{"name":"language","kind":"vocabulary","range":"vocabulary:technology","cardinality":"single","vocabulary_scheme":"technology"},{"name":"routing_style","kind":"datatype","range":"string","cardinality":"single"},{"name":"orm_support","kind":"datatype","range":"boolean","cardinality":"single"}]' \
  --ontology-dir x-ipe-docs/memory/.ontology
```

**Output:**
```yaml
operation_output:
  success: true
  operation: "discover_properties"
  result:
    proposed_properties:
      - name: "language"
        kind: "vocabulary"
        range: "vocabulary:technology"
        cardinality: "single"
        vocabulary_scheme: "technology"
      - name: "routing_style"
        kind: "datatype"
        range: "string"
        cardinality: "single"
      - name: "orm_support"
        kind: "datatype"
        range: "boolean"
        cardinality: "single"
    search_results: "Web search found: language, routing, ORM support, templating engine, async support as common attributes."
    writes_to: "x-ipe-docs/memory/.ontology/schema/"
  errors: []
```

---

## Example 3: create_instances

**Scenario:** Create an instance for Flask from persistent memory content.

**Input:**
```yaml
operation: create_instances
context:
  class_registry:
    - id: "backend-framework"
      label: "BackendFramework"
      properties:
        - {name: "language", kind: "vocabulary", range: "vocabulary:technology", cardinality: "single"}
        - {name: "routing_style", kind: "datatype", range: "string", cardinality: "single"}
  source_content: ["x-ipe-docs/memory/semantic/flask-overview.md"]
  property_schema:
    - {name: "language", kind: "vocabulary", range: "vocabulary:technology", cardinality: "single"}
    - {name: "routing_style", kind: "datatype", range: "string", cardinality: "single"}
```

**Script call:**
```bash
python3 scripts/ontology_ops.py create_instance \
  --class-id "backend-framework" \
  --label "Flask" \
  --source-files '["x-ipe-docs/memory/semantic/flask-overview.md"]' \
  --properties '{"language":"Python","routing_style":"decorator-based","orm_support":null}' \
  --ontology-dir x-ipe-docs/memory/.ontology
```

**Output:**
```yaml
operation_output:
  success: true
  operation: "create_instances"
  result:
    instances:
      - id: "inst-001"
        class: "backend-framework"
        label: "Flask"
        props:
          language: "Python"
          routing_style: "decorator-based"
          orm_support: null
        lifecycle: "Persistent"
    writes_to: "x-ipe-docs/memory/.ontology/instances/"
  errors: []
```

**JSONL written to `.ontology/instances/instance.001.jsonl`:**
```jsonl
{"op":"create","type":"KnowledgeNode","id":"inst-001","ts":"2026-04-16T12:05:00Z","props":{"label":"Flask","class":"backend-framework","source_files":["x-ipe-docs/memory/semantic/flask-overview.md"],"lifecycle":"Persistent","synthesize_id":null,"synthesize_message":null,"language":"Python","routing_style":"decorator-based","orm_support":null}}
```

**Ephemeral lifecycle example** (source in `.working/`):
```bash
python3 scripts/ontology_ops.py create_instance \
  --class-id "backend-framework" \
  --label "Express Draft" \
  --source-files '["x-ipe-docs/memory/.working/express-notes.md"]' \
  --properties '{"language":"JavaScript"}' \
  --ontology-dir x-ipe-docs/memory/.ontology
```
→ `lifecycle: "Ephemeral"` because source_files contains `.working/`.

---

## Example 4: critique_validate

**Scenario:** Validate ontology entries against vocabulary.

**Input:**
```yaml
operation: critique_validate
context:
  class_registry:
    - id: "backend-framework"
      label: "BackendFramework"
      properties: [{name: "language", kind: "vocabulary", range: "vocabulary:technology"}]
  instances:
    - id: "inst-001"
      class: "backend-framework"
      label: "Flask"
      props: {language: "Python", routing_style: "decorator-based"}
    - id: "inst-002"
      class: "backend-framework"
      label: "Express Draft"
      props: {language: "NodeJS"}
  vocabulary_index:
    technology: ["Python", "JavaScript", "Flask", "React"]
```

**Script call (term validation):**
```bash
python3 scripts/ontology_ops.py validate_terms \
  --terms '[{"label":"Python","scheme":"technology"},{"label":"NodeJS","scheme":"technology"}]' \
  --ontology-dir x-ipe-docs/memory/.ontology
```

**Output:**
```yaml
operation_output:
  success: true
  operation: "critique_validate"
  result:
    critique_report:
      accuracy_score: 85
      completeness_score: 70
      suggestions:
        - "Instance 'Express Draft' uses 'NodeJS' — vocabulary uses 'JavaScript'. Consider normalizing."
        - "Property 'orm_support' missing from inst-002 — set to null explicitly."
    term_issues:
      - term: "NodeJS"
        issue: "Not in vocabulary scheme 'technology'"
        suggestion: "Register 'NodeJS' or use existing term 'JavaScript'"
    writes_to: "x-ipe-docs/memory/.ontology/"
  errors: []
```

---

## Example 5: register_vocabulary

**Scenario:** Add new technology terms to the vocabulary.

**Input:**
```yaml
operation: register_vocabulary
context:
  new_terms:
    - label: "FastAPI"
      broader: "Python"
      scheme: "technology"
    - label: "Starlette"
      broader: "Python"
      scheme: "technology"
  target_scheme: "technology"
```

**Script calls:**
```bash
python3 scripts/ontology_ops.py add_vocabulary \
  --scheme "technology" \
  --label "FastAPI" \
  --broader "Python" \
  --ontology-dir x-ipe-docs/memory/.ontology

python3 scripts/ontology_ops.py add_vocabulary \
  --scheme "technology" \
  --label "Starlette" \
  --broader "Python" \
  --ontology-dir x-ipe-docs/memory/.ontology
```

**Output:**
```yaml
operation_output:
  success: true
  operation: "register_vocabulary"
  result:
    updated_vocabulary:
      scheme: "technology"
      concepts:
        Python:
          label: "Python"
          narrower: ["Flask", "FastAPI", "Starlette"]
        FastAPI:
          label: "FastAPI"
          broader: "Python"
        Starlette:
          label: "Starlette"
          broader: "Python"
    added_terms: ["FastAPI", "Starlette"]
    writes_to: "x-ipe-docs/memory/.ontology/vocabulary/"
  errors: []
```

**Scheme file** (`.ontology/vocabulary/technology.json`):
```json
{
  "scheme": "technology",
  "version": "1.0",
  "description": "",
  "concepts": {
    "Python": {
      "label": "Python",
      "narrower": ["Flask", "FastAPI", "Starlette"]
    },
    "Flask": {
      "label": "Flask",
      "broader": "Python"
    },
    "FastAPI": {
      "label": "FastAPI",
      "broader": "Python"
    },
    "Starlette": {
      "label": "Starlette",
      "broader": "Python"
    }
  }
}
```
