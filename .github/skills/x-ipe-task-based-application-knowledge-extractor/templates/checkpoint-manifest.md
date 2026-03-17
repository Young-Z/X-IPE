# Checkpoint Manifest Template

> Version: v1.0 | Feature: FEATURE-050-A | Last Updated: 03-17-2026

---

## Purpose

This template defines the structure of the session manifest file (`manifest.yaml`) created in `.checkpoint/session-{timestamp}/`. The manifest is the single source of truth for extraction session state.

---

## Template

```yaml
# Schema version for manifest format
schema_version: "1.0"

# Session identification
session_id: "session-{YYYYMMDD-HHMMSS}"  # e.g., session-20260317-143022
created_at: "{ISO 8601 timestamp}"       # e.g., 2026-03-17T14:30:22Z
updated_at: "{ISO 8601 timestamp}"       # Updated on each state change

# Input parameters
target: "{path or URL to source}"        # e.g., /Users/dev/my-app or https://docs.example.com
purpose: "{extraction category}"         # e.g., user-manual

# Input analysis results (from Phase 1, Step 1.1)
input_analysis:
  input_type: "{source_code_repo | documentation_folder | running_web_app | public_url | single_file}"
  format: "{markdown | python | javascript | html | mixed | yaml | json | unknown}"
  app_type: "{web | cli | mobile | unknown}"
  source_metadata:
    primary_language: "{python | javascript | go | rust | java | ruby | null}"
    framework: "{flask | django | express | react | click | null}"
    file_count: 0                        # Total files in source
    total_size_bytes: 0                  # Total size in bytes
    entry_points: []                     # List of detected entry points
    has_docs: true                       # Whether docs/ or README exists
    secondary_app_types: []              # Lower-priority app types detected (optional)

# Category selection (from Phase 1, Step 1.2)
selected_category: "{user-manual | API-reference | architecture | runbook | configuration}"
deferred_categories: []                  # Categories detected but not processed

# Tool skill loading (from Phase 1, Step 1.3)
loaded_tool_skill: "{x-ipe-tool-knowledge-extraction-{category}}"
tool_skill_artifacts:
  playbook_template: "{path to playbook template}"
  collection_template: "{path to collection template}"
  acceptance_criteria: "{path to acceptance criteria}"

# Session status
status: "initialized"
# Status values:
#   - initialized: Foundation complete, ready for extraction
#   - extracting: Actively extracting content (FEATURE-050-B)
#   - validating: Tool skill validating content (FEATURE-050-C)
#   - complete: Extraction finished (FEATURE-050-E)
#   - paused: Session paused, resumable (FEATURE-050-D)
#   - error: Unrecoverable error occurred

# Extraction progress (populated in FEATURE-050-B/C/D/E)
sections: []
# sections array structure (future):
#   - number: 1
#     name: "overview"
#     content_file: "content/section-01-overview.md"
#     status: "extracted | validated | incomplete"
#     feedback_file: "feedback/section-01-feedback.yaml"
#     coverage_score: 0.8
#     validation_score: 0.9

# Coverage and quality (FEATURE-050-C/E)
coverage_score: null                     # 0.0-1.0, null if not calculated
quality_score: null                      # 0.0-1.0, null if not calculated

# Error log (FEATURE-050-D)
error_log: []
# error_log array structure (future):
#   - timestamp: "2026-03-17T14:35:10Z"
#     phase: "extracting"
#     error_type: "FileReadError"
#     message: "Unable to read file /path/to/file.py"
#     retry_count: 2
```

---

## Field Descriptions

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | Yes | Manifest format version (for future compatibility) |
| `session_id` | string | Yes | Unique session identifier (session-{timestamp}) |
| `created_at` | string | Yes | ISO 8601 timestamp of session creation |
| `updated_at` | string | Yes | ISO 8601 timestamp of last update |
| `target` | string | Yes | Path or URL to source being extracted |
| `purpose` | string | Yes | Extraction category requested by user |

### Input Analysis Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input_analysis.input_type` | string | Yes | Source type classification |
| `input_analysis.format` | string | Yes | File format classification |
| `input_analysis.app_type` | string | Yes | Application type classification |
| `input_analysis.source_metadata` | object | Yes | Detailed source metadata |

### Category Selection Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `selected_category` | string | Yes | Extraction category selected for processing |
| `deferred_categories` | array | No | Categories detected but not processed in v1 |

### Tool Skill Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `loaded_tool_skill` | string | Yes | Name of loaded tool skill |
| `tool_skill_artifacts.playbook_template` | string | Yes | Path to playbook template |
| `tool_skill_artifacts.collection_template` | string | Yes | Path to collection template |
| `tool_skill_artifacts.acceptance_criteria` | string | Yes | Path to acceptance criteria |

### Status Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | Yes | Current session status |
| `sections` | array | No | Extraction progress by section (FEATURE-050-B/C) |
| `coverage_score` | number | No | Coverage score 0.0-1.0 (FEATURE-050-C) |
| `quality_score` | number | No | Quality score 0.0-1.0 (FEATURE-050-E) |
| `error_log` | array | No | List of errors encountered (FEATURE-050-D) |

---

## Example: Foundation Phase (FEATURE-050-A)

```yaml
schema_version: "1.0"
session_id: "session-20260317-143022"
created_at: "2026-03-17T14:30:22Z"
updated_at: "2026-03-17T14:30:22Z"
target: "/Users/dev/my-flask-app"
purpose: "user-manual"

input_analysis:
  input_type: "source_code_repo"
  format: "mixed"
  app_type: "web"
  source_metadata:
    primary_language: "python"
    framework: "flask"
    file_count: 45
    total_size_bytes: 512000
    entry_points: ["app.py"]
    has_docs: true
    secondary_app_types: []

selected_category: "user-manual"
deferred_categories: []

loaded_tool_skill: "x-ipe-tool-knowledge-extraction-user-manual"
tool_skill_artifacts:
  playbook_template: ".github/skills/x-ipe-tool-knowledge-extraction-user-manual/templates/playbook-web.md"
  collection_template: ".github/skills/x-ipe-tool-knowledge-extraction-user-manual/templates/collection-template.md"
  acceptance_criteria: ".github/skills/x-ipe-tool-knowledge-extraction-user-manual/references/acceptance-criteria.md"

status: "initialized"
sections: []
coverage_score: null
quality_score: null
error_log: []
```

---

## Example: Extraction Phase (FEATURE-050-B Future)

```yaml
schema_version: "1.0"
session_id: "session-20260317-143022"
created_at: "2026-03-17T14:30:22Z"
updated_at: "2026-03-17T14:45:30Z"
target: "/Users/dev/my-flask-app"
purpose: "user-manual"

input_analysis:
  input_type: "source_code_repo"
  format: "mixed"
  app_type: "web"
  source_metadata:
    primary_language: "python"
    framework: "flask"
    file_count: 45
    total_size_bytes: 512000
    entry_points: ["app.py"]
    has_docs: true

selected_category: "user-manual"
deferred_categories: []

loaded_tool_skill: "x-ipe-tool-knowledge-extraction-user-manual"
tool_skill_artifacts:
  playbook_template: ".github/skills/x-ipe-tool-knowledge-extraction-user-manual/templates/playbook-web.md"
  collection_template: ".github/skills/x-ipe-tool-knowledge-extraction-user-manual/templates/collection-template.md"
  acceptance_criteria: ".github/skills/x-ipe-tool-knowledge-extraction-user-manual/references/acceptance-criteria.md"

status: "extracting"
sections:
  - number: 1
    name: "overview"
    content_file: "content/section-01-overview.md"
    status: "extracted"
    feedback_file: null
    coverage_score: null
    validation_score: null
  - number: 2
    name: "installation"
    content_file: "content/section-02-installation.md"
    status: "extracted"
    feedback_file: null
    coverage_score: null
    validation_score: null

coverage_score: null
quality_score: null
error_log: []
```

---

## Example: Validation Phase (FEATURE-050-C Future)

```yaml
schema_version: "1.0"
session_id: "session-20260317-143022"
created_at: "2026-03-17T14:30:22Z"
updated_at: "2026-03-17T15:00:15Z"
target: "/Users/dev/my-flask-app"
purpose: "user-manual"

# ... (input_analysis, selected_category, loaded_tool_skill omitted for brevity)

status: "validating"
sections:
  - number: 1
    name: "overview"
    content_file: "content/section-01-overview.md"
    status: "validated"
    feedback_file: "feedback/section-01-feedback.yaml"
    coverage_score: 0.9
    validation_score: 0.85
  - number: 2
    name: "installation"
    content_file: "content/section-02-installation.md"
    status: "incomplete"
    feedback_file: "feedback/section-02-feedback.yaml"
    coverage_score: 0.6
    validation_score: 0.5

coverage_score: 0.75
quality_score: null
error_log: []
```

---

## Example: Error State (FEATURE-050-D Future)

```yaml
schema_version: "1.0"
session_id: "session-20260317-143022"
created_at: "2026-03-17T14:30:22Z"
updated_at: "2026-03-17T14:50:45Z"
target: "/Users/dev/my-flask-app"
purpose: "user-manual"

# ... (input_analysis, selected_category, loaded_tool_skill omitted)

status: "error"
sections:
  - number: 1
    name: "overview"
    content_file: "content/section-01-overview.md"
    status: "extracted"
    feedback_file: null
    coverage_score: null
    validation_score: null

coverage_score: null
quality_score: null
error_log:
  - timestamp: "2026-03-17T14:50:45Z"
    phase: "extracting"
    error_type: "FileReadError"
    message: "Unable to read file /Users/dev/my-flask-app/docs/usage.md: Permission denied"
    retry_count: 3
```

---

## Usage in Code

### Python Example

```python
import yaml
from datetime import datetime

def create_manifest(session_id, target, purpose, input_analysis, selected_category, loaded_tool_skill, tool_skill_artifacts):
    manifest = {
        "schema_version": "1.0",
        "session_id": session_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "target": target,
        "purpose": purpose,
        "input_analysis": input_analysis,
        "selected_category": selected_category,
        "deferred_categories": [],
        "loaded_tool_skill": loaded_tool_skill,
        "tool_skill_artifacts": tool_skill_artifacts,
        "status": "initialized",
        "sections": [],
        "coverage_score": None,
        "quality_score": None,
        "error_log": []
    }
    
    manifest_path = f".checkpoint/{session_id}/manifest.yaml"
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
    
    return manifest_path
```

---

## Validation Rules

| Rule | Validation |
|------|------------|
| `schema_version` | Must be "1.0" (exact string match) |
| `session_id` | Must match pattern `session-\d{8}-\d{6}` |
| `created_at`, `updated_at` | Must be valid ISO 8601 timestamp |
| `target` | Must be non-empty string |
| `purpose` | Must be one of: user-manual, API-reference, architecture, runbook, configuration |
| `input_analysis.input_type` | Must be one of: source_code_repo, documentation_folder, running_web_app, public_url, single_file |
| `input_analysis.format` | Must be one of: markdown, python, javascript, html, mixed, yaml, json, unknown |
| `input_analysis.app_type` | Must be one of: web, cli, mobile, unknown |
| `status` | Must be one of: initialized, extracting, validating, complete, paused, error |

---

## References

- **Handoff Protocol:** `.github/skills/x-ipe-task-based-application-knowledge-extractor/references/handoff-protocol.md`
- **Technical Design:** `x-ipe-docs/requirements/EPIC-050/FEATURE-050-A/technical-design.md` (Checkpoint Location & Manifest section)
- **SKILL.md Step 1.4:** `.github/skills/x-ipe-task-based-application-knowledge-extractor/SKILL.md` (Phase 1, Step 1.4)
