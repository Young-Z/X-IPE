# Examples — Knowledge Extraction Notes

## Example 1: Create a New Knowledge Base from Research

**Scenario:** Extract knowledge from a research topic into structured notes.

```yaml
# Initialize
operation: init_knowledge_folder
knowledge_name: "react-server-components"
output_dir: "./knowledge-bases"
template_type: "research"

# Result:
# react-server-components/
# ├── overview.md
# └── .images/
```

```yaml
# Extract first section
operation: extract_section
knowledge_name: "react-server-components"
output_dir: "./knowledge-bases"
section_id: "01"
source_content: |
  React Server Components allow rendering on the server...
  Key benefits include reduced bundle size, direct backend access...

# Result:
# react-server-components/
# ├── overview.md
# ├── .images/
# └── 01.introduction-and-benefits.md
```

```yaml
# Extract hierarchical section
operation: extract_section
knowledge_name: "react-server-components"
output_dir: "./knowledge-bases"
section_id: "02"
source_content: |
  Architecture patterns:
  - Streaming SSR: Progressive page rendering...
  - Selective Hydration: Only hydrate interactive parts...
  - Server-Client Boundary: 'use client' directive...

# Result:
# react-server-components/
# ├── overview.md
# ├── .images/
# ├── 01.introduction-and-benefits.md
# └── 02.architecture-patterns/
#     ├── 0201.streaming-ssr.md
#     ├── 0202.selective-hydration.md
#     └── 0203.server-client-boundary.md
```

```yaml
# Generate overview
operation: generate_overview
knowledge_name: "react-server-components"
output_dir: "./knowledge-bases"

# Produces overview.md:
# # React Server Components
#
# ## Table of Contents
#
# 1. [Introduction and Benefits](01.introduction-and-benefits.md)
# 2. [Architecture Patterns](02.architecture-patterns/)
#    - 2.1 [Streaming SSR](02.architecture-patterns/0201.streaming-ssr.md)
#    - 2.2 [Selective Hydration](02.architecture-patterns/0202.selective-hydration.md)
#    - 2.3 [Server-Client Boundary](02.architecture-patterns/0203.server-client-boundary.md)
```

---

## Example 2: Embed Screenshots During Extraction

**Scenario:** Capture and embed UI screenshots while extracting knowledge.

```yaml
# Capture a screenshot and embed it
operation: embed_image
knowledge_name: "react-server-components"
output_dir: "./knowledge-bases"
section_id: "01"
image_path: "/tmp/screenshots/rsc-overview-diagram.png"
image_description: "architecture-overview"

# Result:
# File copied to: .images/01.architecture-overview.png
# Returned markdown: ![architecture-overview](.images/01.architecture-overview.png)
```

The returned markdown reference can then be inserted into section 01:

```markdown
# Introduction and Benefits

React Server Components represent a paradigm shift...

![architecture-overview](.images/01.architecture-overview.png)

Key benefits include...
```

---

## Example 3: Meeting Notes Knowledge Base

**Scenario:** Organize meeting insights into a structured knowledge base.

```yaml
operation: init_knowledge_folder
knowledge_name: "q2-planning-meetings"
output_dir: "./knowledge-bases"
template_type: "meeting-notes"
```

After multiple extraction sessions:

```
q2-planning-meetings/
├── overview.md
├── .images/
│   ├── 01.roadmap-screenshot.png
│   ├── 02.architecture-whiteboard.png
│   └── 0301.budget-chart.png
├── 01.product-roadmap-review.md
├── 02.technical-architecture-decisions.md
├── 03.resource-planning/
│   ├── 0301.budget-allocation.md
│   └── 0302.team-assignments.md
└── 04.action-items-and-followups.md
```

---

## Example 4: Validate and Fix Structure

```yaml
operation: validate_structure
knowledge_name: "react-server-components"
output_dir: "./knowledge-bases"

# Result:
# {
#   "valid": false,
#   "issues": [
#     "Broken image reference in 01.introduction-and-benefits.md: .images/01.missing-diagram.png not found",
#     "overview.md missing link to 02.architecture-patterns/0203.server-client-boundary.md"
#   ],
#   "warnings": [
#     "Section 02.architecture-patterns/ has no images"
#   ]
# }
```

After fixing issues, regenerate overview:

```yaml
operation: generate_overview
knowledge_name: "react-server-components"
output_dir: "./knowledge-bases"
# overview.md is regenerated with all current links
```
