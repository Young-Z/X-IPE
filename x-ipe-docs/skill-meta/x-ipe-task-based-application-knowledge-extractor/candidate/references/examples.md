# Execution Examples

> Version: v1.0 | Feature: FEATURE-050-A | Last Updated: 03-17-2026

---

## Purpose

This document provides detailed execution examples for the Application Knowledge Extractor skill.

---

## Example 1: Local Flask Web App → User Manual Extraction

### Input

```yaml
input:
  task_id: "TASK-123"
  target: "/Users/dev/my-flask-app"
  purpose: "user-manual"
```

### Target Structure

```
/Users/dev/my-flask-app/
├── app.py
├── requirements.txt
├── templates/
├── static/
├── docs/
└── README.md
```

### Execution Flow

**Step 1.1 — Analyze Input:**
```yaml
input_type: "source_code_repo"
format: "mixed"
app_type: "web"
source_metadata:
  primary_language: "python"
  framework: "flask"
  file_count: 45
  entry_points: ["app.py"]
  has_docs: true
```

**Step 1.2 — Select Category:**
```yaml
selected_category: "user-manual"
```

**Step 1.3 — Load Tool Skill:**
```yaml
loaded_tool_skill: "x-ipe-tool-knowledge-extraction-user-manual"
tool_skill_artifacts:
  playbook_template: ".github/skills/x-ipe-tool-knowledge-extraction-user-manual/templates/playbook-web.md"
  collection_template: "..."
  acceptance_criteria: "..."
```

**Step 1.4 — Initialize Handoff:**
```yaml
checkpoint_path: ".x-ipe-checkpoint/session-20260317-143022/"
```

### Output

```yaml
status: "ready_for_extraction"
input_analysis: {...}
selected_category: "user-manual"
loaded_tool_skill: "x-ipe-tool-knowledge-extraction-user-manual"
checkpoint_path: ".x-ipe-checkpoint/session-20260317-143022/"
extraction_status: "foundation_only"
```

---

## Example 2: Public URL Documentation

### Input

```yaml
input:
  target: "https://docs.example.com/getting-started"
  purpose: "user-manual"
```

### Output

```yaml
status: "ready_for_extraction"
input_analysis:
  input_type: "public_url"
  format: "html"
  app_type: "unknown"
checkpoint_path: ".x-ipe-checkpoint/session-20260317-150045/"
```

---

## Example 3: Error — Missing Tool Skill

### Input

```yaml
input:
  target: "/Users/dev/my-app"
  purpose: "user-manual"
```

### Output

```yaml
status: "blocked"
error: "No tool skill found for category 'user-manual'. Install x-ipe-tool-knowledge-extraction-user-manual."
```

---

## Example 4: Error — Empty Directory

### Input

```yaml
input:
  target: "/Users/dev/empty-folder"
  purpose: "user-manual"
```

### Output

```yaml
status: "blocked"
error: "Input directory is empty"
```

---

## Example 5: Error — Unsupported Category

### Input

```yaml
input:
  target: "/Users/dev/my-api"
  purpose: "API-reference"
```

### Output

```yaml
status: "blocked"
error: "Category 'API-reference' not supported in v1. Supported: user-manual"
```

---

## References

- **SKILL.md:** `.github/skills/x-ipe-task-based-application-knowledge-extractor/SKILL.md`
- **Input Detection:** `input-detection-heuristics.md`
- **Handoff Protocol:** `handoff-protocol.md`
