---
skill: x-ipe-tool-knowledge-extraction-user-manual
created: 2026-03-17
last_updated: 2026-03-17
---

# Lessons Learned — x-ipe-tool-knowledge-extraction-user-manual

---

## LL-001

| Field | Value |
|-------|-------|
| **ID** | LL-001 |
| **Date** | 2026-03-17 |
| **Severity** | major |
| **Source** | human_feedback |
| **Status** | raw |
| **Task** | TASK-949 |
| **Scenario** | User ran knowledge extraction for a user manual and found screenshots dumped directly into the user manual output root folder |

### Observed Behavior

Screenshots captured during extraction and used by the user manual tool skill (e.g., for Section 4 Core Features and Section 5 Common Workflow Scenarios) were placed directly in the user manual output root folder alongside the playbook markdown, making the output messy and hard to navigate.

### Expected Behavior

The user manual output should have a `references/` subfolder for all images/screenshots. The playbook markdown should reference images via relative paths pointing into this subfolder.

### Ground Truth

```
User manual output structure:
  .intake/{extraction_id}/
    ├── user-manual-playbook.md         # main playbook
    ├── extraction_report.md            # extraction metadata
    └── references/                     # NEW: all images go here
        ├── 4-1-feature-overview.png
        ├── 4-2-feature-detail.png
        ├── 5-1-scenario-workflow.png
        └── ...

Image references in playbook:
  ![Feature Overview](references/4-1-feature-overview.png)

Naming convention for images:
  {section_number}-{subsection_number}-{descriptive-slug}.png
  Examples:
    4-1-dashboard-overview.png
    4-2-create-new-item.png
    5-1-onboarding-workflow.png
    5-2-data-export-steps.png
```

### Proposed Improvements

**Improvement 1: Reference subfolder for images**
- **Type:** update_instruction
- **Target:** `SKILL.md` — `pack_section` operation output path; `templates/playbook-template.md` — image reference format; `templates/collection-template.md` — screenshot storage instructions
- **Description:** Update `pack_section` to place screenshots into a `references/` subfolder within the output directory instead of the root. Update playbook template screenshot placeholders to use `references/` relative paths. Update collection template to instruct screenshot storage into `references/`.
- **Proposed AC:**
  - id: AC-NEW-1
  - description: "All screenshots are stored in a references/ subfolder within the user manual output"
  - test_method: path_validation
  - expected: "No image files exist directly in the user manual root folder; all are under references/"

**Improvement 2: Image naming convention**
- **Type:** add_example
- **Target:** `references/examples.md` — add example showing correct image naming; `templates/playbook-template.md` — document naming convention
- **Description:** Document and enforce the naming convention `{section_number}-{subsection_number}-{descriptive-slug}.png` for all screenshot files.
- **Proposed AC:**
  - id: AC-NEW-2
  - description: "Screenshots follow the naming convention {section}-{subsection}-{slug}.png"
  - test_method: naming_validation
  - expected: "All image filenames match pattern [0-9]+-[0-9]+-[a-z0-9-]+\\.png"
