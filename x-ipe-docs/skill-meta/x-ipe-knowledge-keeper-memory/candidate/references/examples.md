# Examples: keeper-memory

## Example 1: Store Semantic Knowledge

**Orchestrator Request:**

```yaml
operation: store
context:
  content: |
    # Flask Jinja2 Templating

    Flask uses Jinja2 as its default templating engine. Jinja2 provides
    template inheritance, autoescaping, and a sandboxed execution environment.

    ## Key Features
    - Template inheritance with `{% extends %}` and `{% block %}`
    - Autoescaping of HTML to prevent XSS
    - Macros for reusable template fragments
    - Filters for transforming values in templates

    ## Usage
    ```python
    from flask import render_template

    @app.route('/hello/<name>')
    def hello(name):
        return render_template('hello.html', name=name)
    ```
  memory_type: semantic
  metadata:
    source: "https://flask.palletsprojects.com"
    extracted_by: "x-ipe-knowledge-extractor-web"
    date: "2026-04-16"
  tags: ["flask", "python", "web-framework", "templating"]
  title: "Flask Jinja2 Templating"
```

**Result:**

```yaml
operation_output:
  success: true
  operation: "store"
  result:
    stored_path: "x-ipe-docs/memory/semantic/flask-jinja2-templating.md"
    memory_entry_id: "sem-20260416-001"
    writes_to: "x-ipe-docs/memory/semantic/"
  errors: []
```

**File content at `x-ipe-docs/memory/semantic/flask-jinja2-templating.md`:**

```markdown
---
memory_entry_id: sem-20260416-001
title: "Flask Jinja2 Templating"
memory_type: semantic
tags: ["flask", "python", "web-framework", "templating"]
metadata:
  source: "https://flask.palletsprojects.com"
  extracted_by: "x-ipe-knowledge-extractor-web"
  date: "2026-04-16"
created: "2026-04-16T10:30:00Z"
updated: "2026-04-16T10:30:00Z"
---

# Flask Jinja2 Templating

Flask uses Jinja2 as its default templating engine...
```

---

## Example 2: Promote Working Draft

**Orchestrator Request:**

```yaml
operation: promote
context:
  working_path: "overview/oauth2-patterns.md"
  memory_type: procedural
  metadata:
    reviewed: true
    promoted_by: "x-ipe-assistant-knowledge-librarian-DAO"
  title: "OAuth2 Token Refresh Workflow"
```

**Result:**

```yaml
operation_output:
  success: true
  operation: "promote"
  result:
    promoted_path: "x-ipe-docs/memory/procedural/oauth2-token-refresh-workflow.md"
    writes_to: "x-ipe-docs/memory/procedural/"
  errors: []
```

The original file at `x-ipe-docs/memory/.working/overview/oauth2-patterns.md` is removed after promotion.

---

## Example 3: Store with Auto-Bootstrap

When memory folders don't exist yet:

```yaml
operation: store
context:
  content: "User prefers dark mode for the application."
  memory_type: episodic
  metadata:
    source: "user-session-2026-04-16"
    date: "2026-04-16"
  tags: ["user-preference", "ui", "dark-mode"]
  title: "User Preference Dark Mode"
```

The skill auto-detects missing folders and runs `init_memory.py` before writing.

**Result:**

```yaml
operation_output:
  success: true
  operation: "store"
  result:
    stored_path: "x-ipe-docs/memory/episodic/user-preference-dark-mode.md"
    memory_entry_id: "epi-20260416-001"
    writes_to: "x-ipe-docs/memory/episodic/"
  errors: []
```

---

## Example 4: Error — Invalid Memory Type

```yaml
operation: store
context:
  content: "Some content"
  memory_type: "tactical"
  title: "Bad Type Example"
```

**Result:**

```yaml
operation_output:
  success: false
  operation: "store"
  result: null
  errors:
    - "INVALID_MEMORY_TYPE: 'tactical' is not valid. Must be one of: episodic, semantic, procedural"
```

---

## Example 5: Error — Missing Content

```yaml
operation: store
context:
  memory_type: semantic
  title: "Missing Content Example"
```

**Result:**

```yaml
operation_output:
  success: false
  operation: "store"
  result: null
  errors:
    - "INPUT_VALIDATION_FAILED: 'content' is required for store operation"
```

---

## Example 6: Error — Working Path Not Found

```yaml
operation: promote
context:
  working_path: "overview/nonexistent-file.md"
  memory_type: semantic
  title: "Ghost File"
```

**Result:**

```yaml
operation_output:
  success: false
  operation: "promote"
  result: null
  errors:
    - "PATH_NOT_FOUND: 'x-ipe-docs/memory/.working/overview/nonexistent-file.md' does not exist"
```
