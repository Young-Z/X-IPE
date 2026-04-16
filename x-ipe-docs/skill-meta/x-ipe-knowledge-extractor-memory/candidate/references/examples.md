# Examples — x-ipe-knowledge-extractor-memory

## Example 1: extract_overview — Shallow Search

**Scenario:** Find memory entries related to "flask" using file-system search only.

**Input:**
```yaml
operation: extract_overview
context:
  target: "flask"
  depth: shallow
  knowledge_type: null
```

**Execution:**
1. Searches all tiers: `x-ipe-docs/memory/episodic/*.md`, `semantic/*.md`, `procedural/*.md`
2. Runs case-insensitive grep for "flask" across matched files
3. Reads frontmatter from matching files for metadata

**Output:**
```yaml
operation_output:
  success: true
  operation: "extract_overview"
  result:
    overview_content: |
      Found 3 entries matching 'flask' across memory tiers:
      - [semantic] flask-jinja2-templating.md — Flask Jinja2 template rendering patterns
      - [semantic] flask-routing-patterns.md — URL routing and blueprints in Flask
      - [procedural] python-web-framework-setup.md — Steps to set up Flask/Django projects
    source_map:
      - path: "x-ipe-docs/memory/semantic/flask-jinja2-templating.md"
        relevance: 0.9
        memory_tier: "semantic"
        snippet: "Flask uses Jinja2 as its default template engine..."
      - path: "x-ipe-docs/memory/semantic/flask-routing-patterns.md"
        relevance: 0.8
        memory_tier: "semantic"
        snippet: "Flask routing uses the @app.route decorator..."
      - path: "x-ipe-docs/memory/procedural/python-web-framework-setup.md"
        relevance: 0.5
        memory_tier: "procedural"
        snippet: "Step 3: Install Flask via pip install flask..."
    writes_to: null
  errors: []
```

---

## Example 2: extract_overview — Medium Search with Ontology

**Scenario:** Search for "authentication" with ontology graph traversal.

**Input:**
```yaml
operation: extract_overview
context:
  target: "authentication"
  depth: medium
  knowledge_type: semantic
```

**Execution:**
1. Shallow search: glob/grep across `x-ipe-docs/memory/semantic/*.md`
2. Medium addition: runs `python3 scripts/search.py --query "authentication" --memory-dir x-ipe-docs/memory --class-filter semantic`
3. Merges and deduplicates results from both sources
4. Ontology reveals related entities (e.g., "JWT", "OAuth2") via BFS traversal

**Output:**
```yaml
operation_output:
  success: true
  operation: "extract_overview"
  result:
    overview_content: |
      Found 5 entries matching 'authentication' in semantic tier:
      - jwt-token-patterns.md — JSON Web Token authentication flows
      - oauth2-integration.md — OAuth2 provider integration guide
      - session-management.md — Server-side session handling
      (+ 2 ontology-linked entries via entity relationships)
    source_map:
      - path: "x-ipe-docs/memory/semantic/jwt-token-patterns.md"
        relevance: 1.0
        memory_tier: "semantic"
        snippet: "JWT authentication involves signing tokens..."
      - path: "x-ipe-docs/memory/semantic/oauth2-integration.md"
        relevance: 0.8
        memory_tier: "semantic"
        snippet: "OAuth2 provides delegated authentication..."
    writes_to: null
  errors: []
```

---

## Example 3: extract_details — Full Scope

**Scenario:** Retrieve the complete content of a known memory entry.

**Input:**
```yaml
operation: extract_details
context:
  target: "semantic/flask-jinja2-templating.md"
  scope: full
```

**Execution:**
1. Resolves path to `x-ipe-docs/memory/semantic/flask-jinja2-templating.md`
2. Reads entire file content
3. Parses frontmatter for metadata

**Output:**
```yaml
operation_output:
  success: true
  operation: "extract_details"
  result:
    extracted_content: |
      ---
      memory_entry_id: sem-20260315-042
      title: Flask Jinja2 Templating
      tags: [flask, jinja2, templating, python]
      memory_type: semantic
      ---
      # Flask Jinja2 Templating

      Flask uses Jinja2 as its default template engine...
      (full file content)
    metadata:
      file_size: 2048
      last_modified: "2026-03-15T14:30:00Z"
      memory_tier: "semantic"
      title: "Flask Jinja2 Templating"
      tags: ["flask", "jinja2", "templating", "python"]
    writes_to: null
  errors: []
```

---

## Example 4: extract_details — Section Scope

**Scenario:** Extract only a specific section from a memory entry.

**Input:**
```yaml
operation: extract_details
context:
  target: "procedural/python-web-framework-setup.md"
  scope: section
  format_hints: "## Flask Setup"
```

**Execution:**
1. Reads the full file
2. Locates the `## Flask Setup` heading
3. Extracts content from that heading until the next heading of equal or higher level

**Output:**
```yaml
operation_output:
  success: true
  operation: "extract_details"
  result:
    extracted_content: |
      ## Flask Setup

      1. Create virtual environment: `python -m venv .venv`
      2. Activate: `source .venv/bin/activate`
      3. Install: `pip install flask`
      4. Create app.py with minimal route...
    metadata:
      file_size: 4096
      last_modified: "2026-02-20T10:00:00Z"
      memory_tier: "procedural"
      title: "Python Web Framework Setup"
      tags: ["python", "flask", "django", "setup"]
    writes_to: null
  errors: []
```

---

## Example 5: Empty Results (Not an Error)

**Scenario:** Query returns no matching entries.

**Input:**
```yaml
operation: extract_overview
context:
  target: "nonexistent-topic-xyz"
  depth: shallow
```

**Output:**
```yaml
operation_output:
  success: true
  operation: "extract_overview"
  result:
    overview_content: "No entries found for 'nonexistent-topic-xyz'"
    source_map: []
    writes_to: null
  errors: []
```

---

## Example 6: Error — Invalid Operation

**Input:**
```yaml
operation: "summarize"
context:
  target: "flask"
```

**Output:**
```yaml
operation_output:
  success: false
  operation: "summarize"
  result: null
  errors:
    - code: "INVALID_OPERATION"
      message: "Unknown operation 'summarize'. Valid operations: extract_overview, extract_details"
```

---

## Example 7: Error — File Not Found

**Input:**
```yaml
operation: extract_details
context:
  target: "semantic/doesnt-exist.md"
  scope: full
```

**Output:**
```yaml
operation_output:
  success: false
  operation: "extract_details"
  result: null
  errors:
    - code: "PATH_NOT_FOUND"
      message: "File not found: x-ipe-docs/memory/semantic/doesnt-exist.md"
```
