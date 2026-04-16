# Examples: x-ipe-knowledge-extractor-web

## Example 1: Extract Overview (Shallow)

**Orchestrator Request:**

```yaml
operation: extract_overview
context:
  target: "https://flask.palletsprojects.com/en/3.0.x/"
  depth: shallow
```

**Agent executes:**
1. `chrome-devtools-navigate_page` → navigates to Flask docs
2. `chrome-devtools-take_snapshot` → captures page DOM
3. Extracts h1–h6 headings from snapshot
4. Builds source_map with section metadata

**Result:**

```yaml
operation_output:
  success: true
  operation: "extract_overview"
  result:
    overview_content: |
      # Flask Documentation
      ## Installation
      ## Quickstart
      ## Tutorial
      ## Templates (Jinja2)
      ## Testing
      ## API Reference
    source_map:
      - { section: "Installation", url_fragment: "#installation", content_type: "prose", estimated_size: "small" }
      - { section: "Quickstart", url_fragment: "#quickstart", content_type: "prose+code", estimated_size: "medium" }
      - { section: "Templates (Jinja2)", url_fragment: "#templates", content_type: "prose+code", estimated_size: "large" }
      - { section: "API Reference", url_fragment: "#api", content_type: "reference", estimated_size: "large" }
    writes_to: "x-ipe-docs/memory/.working/overview/flask-palletsprojects-com-en-3-0-x.md"
  errors: []
```

---

## Example 2: Extract Overview (Medium)

**Orchestrator Request:**

```yaml
operation: extract_overview
context:
  target: "https://docs.python.org/3/library/asyncio.html"
  depth: medium
```

**Agent executes:**
1. Navigates to Python asyncio docs
2. Takes snapshot
3. Extracts headings AND first paragraph per section

**Result:**

```yaml
operation_output:
  success: true
  operation: "extract_overview"
  result:
    overview_content: |
      # asyncio — Asynchronous I/O
      ## High-level APIs
      asyncio provides a set of high-level APIs to run coroutines, create tasks, and manage event loops.
      ## Low-level APIs
      For library and framework developers, asyncio offers low-level APIs for creating transports and protocols.
      ## Guides and Tutorials
      Step-by-step guides for common asyncio patterns.
    source_map:
      - { section: "High-level APIs", url_fragment: "#high-level-apis", content_type: "prose+code", estimated_size: "large" }
      - { section: "Low-level APIs", url_fragment: "#low-level-apis", content_type: "prose+code", estimated_size: "large" }
      - { section: "Guides and Tutorials", url_fragment: "#guides", content_type: "prose", estimated_size: "medium" }
    writes_to: "x-ipe-docs/memory/.working/overview/docs-python-org-3-library-asyncio.md"
  errors: []
```

---

## Example 3: Extract Details (Section)

**Orchestrator Request:**

```yaml
operation: extract_details
context:
  target: "https://flask.palletsprojects.com/en/3.0.x/templating/"
  scope: section
  format_hints: "Focus on Jinja2 template syntax and examples"
```

**Agent executes:**
1. `chrome-devtools-navigate_page` → navigates to Flask templating page
2. `chrome-devtools-take_snapshot` → captures DOM
3. Identifies and extracts the Jinja2 syntax section content

**Result:**

```yaml
operation_output:
  success: true
  operation: "extract_details"
  result:
    extracted_content: |
      # Jinja2 Templates in Flask

      Flask uses Jinja2 as its templating engine. Templates are stored in the
      `templates/` folder by default.

      ## Basic Syntax
      - `{{ variable }}` — output a variable
      - `{% if condition %}...{% endif %}` — control flow
      - `{# comment #}` — template comments

      ## Template Inheritance
      ```html
      {% extends "base.html" %}
      {% block content %}...{% endblock %}
      ```
    metadata:
      title: "Templates — Flask Documentation"
      date: "2026-04-16"
      url: "https://flask.palletsprojects.com/en/3.0.x/templating/"
      structure_context: "Section within Flask docs → Templating chapter"
    writes_to: "x-ipe-docs/memory/.working/extracted/flask-palletsprojects-com-templating-section.md"
  errors: []
```

---

## Example 4: Extract Details (Specific — Tables as JSON)

**Orchestrator Request:**

```yaml
operation: extract_details
context:
  target: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status"
  scope: specific
  format_hints: "Extract the HTTP status codes table as JSON array"
```

**Agent executes:**
1. Navigates to MDN HTTP status codes page
2. Takes snapshot
3. Uses `chrome-devtools-evaluate_script` to extract table data as JSON

**Result:**

```yaml
operation_output:
  success: true
  operation: "extract_details"
  result:
    extracted_content: |
      # HTTP Status Codes

      ```json
      [
        {"code": 200, "phrase": "OK", "description": "The request succeeded."},
        {"code": 301, "phrase": "Moved Permanently", "description": "The URL has been permanently changed."},
        {"code": 404, "phrase": "Not Found", "description": "The server cannot find the requested resource."}
      ]
      ```
    metadata:
      title: "HTTP response status codes - MDN Web Docs"
      url: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status"
      structure_context: "Reference table extracted as JSON"
    writes_to: "x-ipe-docs/memory/.working/extracted/developer-mozilla-org-http-status-specific.md"
  errors: []
```

---

## Example 5: Error — Unreachable URL

**Orchestrator Request:**

```yaml
operation: extract_overview
context:
  target: "https://nonexistent-domain-xyz.com"
  depth: shallow
```

**Result:**

```yaml
operation_output:
  success: false
  operation: "extract_overview"
  result: null
  errors:
    - "URL_UNREACHABLE: Cannot navigate to 'https://nonexistent-domain-xyz.com'. Chrome DevTools returned: net::ERR_NAME_NOT_RESOLVED"
```

Partial files in `.working/overview/` are cleaned up automatically.

---

## Example 6: Error — Missing format_hints for scope=specific

**Orchestrator Request:**

```yaml
operation: extract_details
context:
  target: "https://example.com/docs"
  scope: specific
```

**Result:**

```yaml
operation_output:
  success: false
  operation: "extract_details"
  result: null
  errors:
    - "INPUT_VALIDATION_FAILED: scope='specific' requires 'format_hints' to be provided"
```
