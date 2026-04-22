# Present to User — Render Operation Examples

## Example 1: Structured Summary (Default)

**Input file** (`knowledge.md`):
```markdown
# Flask Jinja2 Templating

## Overview

Flask uses Jinja2 as its default template engine. Jinja2 provides template inheritance, macros, and filters.

## Setup

Install Flask with pip. [INCOMPLETE: missing prerequisites for virtual environment setup]

## Template Syntax

Use {{ variable }} for expressions and {% block %} for template inheritance.
```

**Command:**
```bash
python3 scripts/render.py render --content-path knowledge.md
```

**Output:**
```json
{
  "success": true,
  "operation": "render",
  "result": {
    "rendered_output": {
      "title": "Flask Jinja2 Templating",
      "summary": "Flask uses Jinja2 as its default template engine. Jinja2 provides template inheritance, macros, and filters.",
      "sections": [
        {"heading": "Overview", "content": "Flask uses Jinja2...", "completeness": 100},
        {"heading": "Setup", "content": "Install Flask with pip. [INCOMPLETE: missing prerequisites...]", "completeness": 42, "warnings": ["INCOMPLETE: missing prerequisites for virtual environment setup"]},
        {"heading": "Template Syntax", "content": "Use {{ variable }}...", "completeness": 100}
      ],
      "metadata": {
        "source_path": "knowledge.md",
        "total_sections": 3,
        "overall_completeness": 81,
        "generated_at": "2026-04-16T04:00:00Z"
      }
    }
  }
}
```

---

## Example 2: Markdown Format

**Command:**
```bash
python3 scripts/render.py render --content-path knowledge.md --format markdown
```

**Output:**
```markdown
# Flask Jinja2 Templating

*Flask uses Jinja2 as its default template engine...*

## Overview

Flask uses Jinja2 as its default template engine...

## Setup

Install Flask with pip. [INCOMPLETE: missing prerequisites...]

> ⚠️ INCOMPLETE: missing prerequisites for virtual environment setup

## Template Syntax

Use {{ variable }} for expressions...

---
*Completeness: 81% | Sections: 3 | Generated: 2026-04-16T04:00:00Z*
```

---

## Example 3: Empty File

**Command:**
```bash
python3 scripts/render.py render --content-path empty.md
```

**Output:**
```json
{
  "success": true,
  "operation": "render",
  "result": {
    "rendered_output": {
      "title": "Empty",
      "summary": "",
      "sections": [],
      "metadata": {"source_path": "empty.md", "total_sections": 0, "overall_completeness": 0, "generated_at": "..."}
    }
  }
}
```

---

## Example 4: Missing File

**Command:**
```bash
python3 scripts/render.py render --content-path nonexistent.md
```

**Output (stderr):**
```json
{"success": false, "error": "CONTENT_NOT_FOUND", "message": "File not found: nonexistent.md"}
```
