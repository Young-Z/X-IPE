# User Manual — Playbook Template (Constructor)

> Structural template for the `provide_framework` operation.
> Defines the 8 standard user manual sections. The constructor loads this template,
> applies the appropriate app-type mixin, and returns a framework_document with section stubs.

---

## Table of Contents

<!-- TOC_MODE: inline | split -->
<!-- The constructor sets TOC_MODE based on output_format parameter -->

| # | Section | Stub Description |
|---|---------|-----------------|
| 1 | Overview | Application description, audience, key features |
| 2 | Installation & Setup | Prerequisites, install steps, verification |
| 3 | Getting Started | Quick start, basic workflow, first action |
| 4 | Core Features | Feature-by-feature usage guide |
| 5 | Common Workflow Scenarios | End-to-end workflow walkthroughs |
| 6 | Configuration | Settings, env vars, runtime options |
| 7 | Troubleshooting | Common issues, error messages, diagnostics |
| 8 | FAQ & Reference | FAQ, glossary, shortcuts, version history |

---

## 1. Overview

**Framework stub — the constructor fills this with guidance for knowledge gathering.**

**Subsections to generate:**
- **What is {app_name}?** — One-paragraph description of the application
- **Who is it for?** — Target audience, personas, or use cases
- **Key Features** — Bulleted list of 3–7 headline capabilities
- **How it works** — High-level workflow or architecture summary (1–2 paragraphs)

**Constructor notes:** Populate {app_name} from request_context. If source_paths include a README, hint that Overview content is likely there.

---

## 2. Installation & Setup

**Framework stub — prerequisites and installation steps.**

**Subsections to generate:**
- **Prerequisites** — System requirements, runtime versions, OS compatibility
- **Installation** — Step-by-step install commands (copy-pasteable)
- **Initial Configuration** — First-time setup steps (API keys, database init, etc.)
- **Verification** — Command or action to confirm successful installation

**Constructor notes:** Adapt based on app_type. Web apps may need browser requirements (see mixin-web). CLI apps may need PATH setup (see mixin-cli). Mobile apps may need store links (see mixin-mobile).

---

## 3. Getting Started

**Framework stub — guided first-run experience.**

**Subsections to generate:**
- **Quick Start** — Minimal steps to see the app in action (under 5 minutes)
- **Basic Workflow** — The core happy-path workflow explained step by step
- **Your First {Action}** — Concrete tutorial creating or doing something meaningful

**Constructor notes:** The {Action} placeholder adapts to user_goal from request_context.

---

## 4. Core Features

**Framework stub — feature-by-feature usage guide. This is the main body.**

**Output structure:** Subfolder with one file per feature:
```
04-core-features/
  feature01-{feature-slug}.md
  feature02-{feature-slug}.md
  _index.md
```

**Each feature file must include:**
- Feature name and interaction pattern (FORM | MODAL | CLI_DISPATCH | NAVIGATION | TOGGLE)
- Description — What it does and why
- Step-by-step instructions: [Action] → [Element] → [Expected]
- Example with expected output
- Screenshot references

**Constructor notes:** The number of features is unknown at framework time. Generate the structure template and index format. Actual features populated during fill_structure.

---

## 5. Common Workflow Scenarios

**Framework stub — end-to-end workflow walkthroughs.**

**Output structure:** Subfolder with one file per workflow:
```
05-common-workflows/
  workflow01-{scenario-slug}.md
  workflow02-{scenario-slug}.md
  _index.md
```

**Each workflow file must include:**
- Goal — What the user wants to accomplish
- Prerequisites — What must be set up before starting
- Steps — Numbered walkthrough referencing features from Section 4
- Expected Result — What success looks like

**Constructor notes:** Minimum 3 scenarios covering the most common user journeys. Actual workflows populated during fill_structure.

---

## 6. Configuration

**Framework stub — all user-facing settings and options.**

**Subsections to generate:**
- **Configuration File** — Location, format, and structure of config files
- **Environment Variables** — Table of env vars with name, description, default, required flag
- **Runtime Options** — Command-line flags or UI settings that modify behavior
- **Profiles / Environments** — How to manage different configurations (dev, staging, prod)

---

## 7. Troubleshooting

**Framework stub — common problems and solutions.**

**Subsections to generate:**
- **Common Issues** — Table or list of frequent problems with symptoms and fixes
- **Error Messages** — Reference of error codes/messages with explanations
- **Diagnostic Steps** — How to gather logs, enable debug mode, check connectivity
- **Getting Help** — Where to report bugs, ask questions, find community support

---

## 8. FAQ & Reference

**Framework stub — reference material.**

**Subsections to generate:**
- **FAQ** — Question-and-answer format for the most common user questions
- **Glossary** — Definitions of domain-specific or application-specific terms
- **Keyboard Shortcuts** — If applicable, table of shortcuts
- **Version History** — Summary of major version changes relevant to users

---

## Content Splitting Guidelines

**Threshold:** If the assembled manual exceeds **800 lines**, use split mode.

**File naming convention:**
- Sub-markdown files: `{nn}-{section-slug}.md` (e.g., `01-overview.md`)
- Screenshot images: `screenshots/{nn}-{section-slug}-{description}.png`
- Sections 4 and 5 ALWAYS use subfolders regardless of total length

**Constructor behavior:**
- If output_format is "split" → generate file references in TOC
- If output_format is "markdown" → generate anchor links in TOC
- The constructor reports which mode it selected in the toc_structure output
