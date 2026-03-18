---
section_id: "6-configuration"
title: "Configuration & Settings"
quality_score: null
provenance:
  source: "X-IPE source code (ideas_service.py, ideas_routes.py, settings) + running application"
  extracted_by: "x-ipe-task-based-application-knowledge-extractor"
  extraction_date: "2026-03-17"
---

# 6. Configuration & Settings

## Instructions

This section covers configurable aspects of the Ideation module, including the toolbox, folder settings, and integration options.

## Content

### 6.1 Ideation Toolbox

The Ideation Toolbox controls which AI-powered tools are available during idea refinement.

**File Location:** `x-ipe-docs/ideas/.ideation-tools.json`

**Configurable Tools:**

| Tool | Key | Description |
|------|-----|-------------|
| Mermaid Diagrams | `mermaid` | Enables flowcharts, sequence diagrams, state diagrams, etc. in idea summaries |
| Infographics | `infographics` | Enables visual summary infographic blocks |
| Architecture DSL | `architecture_dsl` | Enables architecture layer diagrams using X-IPE's DSL format |
| Mockups | `mockups` | Enables UI/UX mockup generation |

**How to Modify:**
1. Navigate to your idea folder in the sidebar
2. Locate `.ideation-tools.json` (or create one if it doesn't exist)
3. Edit the JSON to enable/disable tools:

```json
{
  "mermaid": true,
  "infographics": true,
  "architecture_dsl": true,
  "mockups": true
}
```

**API Endpoint:** `GET/POST /api/ideas/<folder>/toolbox` — Retrieve or update toolbox configuration programmatically.

---

### 6.2 Project Folder Configuration

X-IPE stores ideas within the active project folder's `x-ipe-docs/ideas/` directory.

**Default Location:** `{project_root}/x-ipe-docs/ideas/`

**Changing the Project Folder:**
1. Click the ⚙️ **Settings** gear icon in the top-right header
2. Modify the project folder path
3. Save settings — the Ideation sidebar will refresh to show ideas from the new location

**Multiple Projects:**
- Each project folder has its own `x-ipe-docs/ideas/` directory
- Switching projects switches the visible ideas

---

### 6.3 Knowledge Base References

Configure which Knowledge Base sources are available for linking.

**File Location:** `x-ipe-docs/ideas/{folder}/.knowledge-reference.yaml`

**Format:**
```yaml
references:
  - article_id: "unique-id"
    title: "Article Title"
    path: "x-ipe-docs/knowledge-base/articles/article-name.md"
```

**KB sources are configured per-project and read from:**
- `x-ipe-docs/knowledge-base/` — Project-level knowledge base

---

### 6.4 File Upload Settings

**Built-in Constraints:**

| Setting | Default | Configurable |
|---------|---------|--------------|
| **Max folder name length** | 200 characters | No (hardcoded) |
| **Allowed file types** | Text, Data, Code, Images, Documents | No (hardcoded) |
| **Duplicate handling** | Suffix numbering: `(2)`, `(3)` | No (automatic) |
| **DOCX conversion** | Auto-convert to HTML | No (automatic) |
| **MSG conversion** | Auto-convert to HTML | No (automatic) |

---

### 6.5 Workflow Integration Settings

When running in Workflow Mode, the following settings affect ideation:

**Workflow Template:** `x-ipe-docs/config/workflow-template.json`

This file defines the engineering workflow stages and actions. The ideation-related actions are:
- `compose_idea` — Initial idea creation (Stage: Ideation)
- `idea_mockup` — Generate UI mockups (Stage: Ideation)
- `idea_architecture` — Generate architecture diagrams (Stage: Ideation)

**Auto-Naming:**
Workflow-linked idea folders are automatically named: `wf-{NNN}-{sanitized-name}`
- `NNN` is a zero-padded sequential number
- `sanitized-name` is derived from the workflow name with special characters removed

## Screenshots

No additional screenshots for this section — configuration is primarily file-based.
