# Output Schemas — Dynamic Output Reference

> Full field definitions and examples for `task_completion_output` dynamic fields.

---

## input_analysis

```yaml
input_analysis:
  input_type: "source_code_repo | documentation_folder | running_web_app | public_url | single_file"
  format: "mixed | markdown | python | javascript | html | yaml | json | go | rust | java | ruby | restructuredtext | text | unknown"
  app_type: "web | cli | mobile | unknown"
  source_metadata:
    primary_language: "string | null"
    framework: "string | null"
    secondary_app_types: []  # Lower-priority app types (e.g., both web + cli)
    file_count: int
    total_size_bytes: int
    entry_points: ["string"]
    has_docs: bool
```

**Example — Source Code Repo:**
```yaml
input_analysis:
  input_type: "source_code_repo"
  format: "mixed"
  app_type: "web"
  source_metadata:
    primary_language: "TypeScript"
    framework: "Next.js"
    secondary_app_types: ["cli"]
    file_count: 342
    total_size_bytes: 2048000
    entry_points: ["src/index.ts", "package.json"]
    has_docs: true
```

**Example — Public URL:**
```yaml
input_analysis:
  input_type: "public_url"
  format: "html"
  app_type: "web"
  source_metadata:
    primary_language: null
    framework: null
    secondary_app_types: []
    file_count: 0
    total_size_bytes: 0
    entry_points: ["https://docs.example.com"]
    has_docs: true
```

---

## tool_skill_artifacts

```yaml
loaded_tool_skill: "x-ipe-tool-knowledge-extraction-{category} | null"
tool_skill_artifacts:
  playbook_template: "path | null"
  collection_template: "path | null"
  acceptance_criteria: "path | null"
  app_type_mixins:
    web: "path | null"
    cli: "path | null"
    mobile: "path | null"
```

---

## extraction_summary

```yaml
extraction_summary:
  sections_extracted: int    # Sections with content files written
  sections_skipped: int      # Sections skipped (inaccessible source)
  sections_error: int        # Sections that errored during extraction
  total_warnings: int        # Non-fatal warnings
  content_files: ["content/section-{NN}-{slug}.md"]
```

---

## validation_summary

```yaml
validation_summary:
  final_coverage_ratio: float   # 0.0–1.0, criteria_met / criteria_total
  exit_reason: "all_criteria_met | max_iterations_reached | plateau_detected | skipped"
  iterations_completed: int
  coverage_history: [float]     # Per-iteration coverage ratios
  sections_accepted: int
  sections_needs_more_info: int
  sections_error: int
```

---

## error_summary

```yaml
error_summary:
  total_errors: int
  transient_retried: int     # Errors retried successfully
  permanent_halted: int      # Errors that halted extraction for a section
  sections_skipped: int      # Sections skipped due to errors
  resumed_from: "session path | null"  # If resumed from prior session
```

---

## Quality &amp; Output Fields

```yaml
extraction_status: "complete | partial | failed"
quality_score: 0.0       # 0.0–1.0, overall quality (2 decimal places)
quality_label: "high | acceptable | low"   # ≥0.80 high, 0.50–0.79 acceptable, <0.50 low
extraction_id: "{app_name}-{category}"     # e.g., "x-ipe-user-manual", "my-app-workflow-mode-user-manual"
kb_output_path: "x-ipe-docs/knowledge-base/.intake/{extraction_id}/"
```

**Example — Successful Extraction:**
```yaml
extraction_status: "complete"
quality_score: 0.82
quality_label: "high"
extraction_id: "x-ipe-user-manual"
kb_output_path: "x-ipe-docs/knowledge-base/.intake/x-ipe-user-manual/"
```

**Example — Partial Extraction:**
```yaml
extraction_status: "partial"
quality_score: 0.61
quality_label: "acceptable"
extraction_id: "x-ipe-workflow-mode-user-manual"
kb_output_path: "x-ipe-docs/knowledge-base/.intake/x-ipe-workflow-mode-user-manual/"
```
