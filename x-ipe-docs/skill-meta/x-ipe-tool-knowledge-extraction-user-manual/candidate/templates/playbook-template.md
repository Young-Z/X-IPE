# User Manual — Playbook Template

> Base layout for user manual knowledge extraction. Each H2 section defines a standard chapter.
> The extractor uses this template to structure the final output.

---

## Table of Contents

<!-- TOC_MODE: inline | split -->
<!-- When TOC_MODE is "split", each entry links to a sub-markdown file -->
<!-- When TOC_MODE is "inline", each entry links to an anchor in this document -->

| # | Section | Link |
|---|---------|------|
| 1 | Overview | [Overview](#1-overview) |
| 2 | Installation & Setup | [Installation & Setup](#2-installation--setup) |
| 3 | Getting Started | [Getting Started](#3-getting-started) |
| 4 | Core Features | [Core Features](#4-core-features) |
| 5 | Common Workflow Scenarios | [Common Workflow Scenarios](#5-common-workflow-scenarios) |
| 6 | Configuration | [Configuration](#6-configuration) |
| 7 | Troubleshooting | [Troubleshooting](#7-troubleshooting) |
| 8 | FAQ & Reference | [FAQ & Reference](#8-faq--reference) |

<!-- SPLIT MODE EXAMPLE:
| 1 | Overview | [Overview](01-overview.md) |
| 2 | Installation & Setup | [Installation & Setup](02-installation-setup.md) |
| 3 | Getting Started | [Getting Started](03-getting-started.md) |
| 4 | Core Features | [Core Features](04-core-features/_index.md) |
| 5 | Common Workflow Scenarios | [Common Workflow Scenarios](05-common-workflows/_index.md) |
| 6 | Configuration | [Configuration](06-configuration.md) |
| 7 | Troubleshooting | [Troubleshooting](07-troubleshooting.md) |
| 8 | FAQ & Reference | [FAQ & Reference](08-faq-reference.md) |
-->

---

## 1. Overview

**What belongs here:** A concise description of what the application does, who it's for, and the key value it provides.

**Subsections:**
- **What is {App Name}?** — One-paragraph description of the application
- **Who is it for?** — Target audience, personas, or use cases
- **Key Features** — Bulleted list of 3–7 headline capabilities
- **How it works** — High-level workflow or architecture summary (1–2 paragraphs)

---

## 2. Installation & Setup

**What belongs here:** Everything a new user needs to go from zero to a working installation.

**Subsections:**
- **Prerequisites** — System requirements, runtime versions, OS compatibility
- **Installation** — Step-by-step install commands (copy-pasteable)
- **Initial Configuration** — First-time setup steps (API keys, database init, etc.)
- **Verification** — Command or action to confirm successful installation

---

## 3. Getting Started

**What belongs here:** A guided first-run experience that takes the user from installation to their first successful interaction.

**Subsections:**
- **Quick Start** — Minimal steps to see the app in action (under 5 minutes)
- **Basic Workflow** — The core happy-path workflow explained step by step
- **Your First {Action}** — Concrete tutorial creating or doing something meaningful

---

## 4. Core Features

**What belongs here:** Feature-by-feature usage guide covering all primary capabilities. This is the main body of the user manual — each feature should be detailed enough for a user to understand and use it independently.

**Output structure:** Subfolder with one file per feature:
```
04-core-features/
  feature01-{feature-slug}.md
  feature02-{feature-slug}.md
  ...
```

**File naming convention:** `feature{nn}-{feature-slug}.md` (e.g., `feature01-workflow-mode.md`, `feature02-free-mode.md`)

**Each feature file MUST include:**
- **H1 heading:** `# Feature {nn}: {Feature Name}`
- **Interaction Pattern** — One of: FORM | MODAL | CLI_DISPATCH | NAVIGATION | TOGGLE
- **Description** — What it does and why a user would use it
- **Instructions** — Step-by-step usage guide using the format:
  1. [Action] Click/Type/Press... [Element] "Button Label" → [Expected] "You should see..."
- **Example** — Concrete usage example with expected output
- **Screenshots** — Reference screenshots: `![{Alt text}](screenshots/feature{nn}-{feature-slug}-{description}.png)`
- **Tips** — Best practices, common pitfalls, or power-user shortcuts (optional but recommended)

**Screenshot convention:** `screenshots/feature{nn}-{feature-slug}-{description}.png`
(e.g., `screenshots/feature01-workflow-mode-stage-panel.png`)

**Index file:** The subfolder MUST contain a `_index.md` with a table listing all features:
```markdown
# Core Features

| # | Feature | File | Interaction |
|---|---------|------|-------------|
| 1 | Workflow Mode | [feature01-workflow-mode.md](feature01-workflow-mode.md) | NAVIGATION |
| 2 | Free Mode | [feature02-free-mode.md](feature02-free-mode.md) | NAVIGATION |
```

**When content is insufficient:** If extracted content lacks detail for any feature (e.g., missing instructions or only has a one-liner description), flag it as INCOMPLETE and request the extractor to gather more source material for that specific feature.

---

## 5. Common Workflow Scenarios

**What belongs here:** End-to-end workflow walkthroughs showing how multiple features work together to accomplish real-world tasks. Unlike Section 4 (which documents individual features), this section demonstrates feature combinations in context.

**Output structure:** Subfolder with one file per workflow:
```
05-common-workflows/
  workflow01-{scenario-slug}.md
  workflow02-{scenario-slug}.md
  ...
```

**File naming convention:** `workflow{nn}-{scenario-slug}.md` (e.g., `workflow01-create-new-project.md`, `workflow02-implement-feature.md`)

**Each workflow file MUST include:**
- **H1 heading:** `# Workflow {nn}: {Scenario Name}`
- **Goal** — What the user wants to accomplish (1 sentence)
- **Prerequisites** — What must be set up before starting
- **Steps** — Numbered walkthrough referencing features from Section 4 (with cross-links to feature files), using the format:
  1. [Action] ... [Element] ... → [Expected] ...
     ⚠️ If this dispatches a CLI command: Press **Enter** to execute. Wait for completion (1-5 min).
- **Expected Result** — What success looks like
- **Screenshots** — Key UI states: `![{Alt text}](screenshots/workflow{nn}-{scenario-slug}-{description}.png)`
- **Tips** — Variations, shortcuts, or "what if" guidance (optional)

**Screenshot convention:** `screenshots/workflow{nn}-{scenario-slug}-{description}.png`
(e.g., `screenshots/workflow01-create-project-setup-wizard.png`)

**Index file:** The subfolder MUST contain a `_index.md` with a table listing all workflows:
```markdown
# Common Workflow Scenarios

| # | Workflow | File | Complexity |
|---|----------|------|-----------|
| 1 | Create a New Project | [workflow01-create-new-project.md](workflow01-create-new-project.md) | Basic |
| 2 | Implement a Feature | [workflow02-implement-feature.md](workflow02-implement-feature.md) | Intermediate |
```

**Minimum:** At least 3 scenarios covering the most common user journeys.

**When content is insufficient:** If source material doesn't reveal common workflows clearly, flag as INCOMPLETE and request the extractor to analyze usage patterns, test files, or example scripts for workflow evidence.

---

## 6. Configuration

**What belongs here:** All user-facing settings, options, and customization points.

**Subsections:**
- **Configuration File** — Location, format, and structure of config files
- **Environment Variables** — Table of env vars with name, description, default, required flag
- **Runtime Options** — Command-line flags or UI settings that modify behavior
- **Profiles / Environments** — How to manage different configurations (dev, staging, prod)

---

## 7. Troubleshooting

**What belongs here:** Common problems users encounter and how to resolve them.

**Subsections:**
- **Common Issues** — Table or list of frequent problems with symptoms and fixes
- **Error Messages** — Reference of error codes/messages with explanations
- **Diagnostic Steps** — How to gather logs, enable debug mode, check connectivity
- **Getting Help** — Where to report bugs, ask questions, find community support

---

## 8. FAQ & Reference

**What belongs here:** Frequently asked questions and reference material.

**Subsections:**
- **FAQ** — Question-and-answer format for the most common user questions
- **Glossary** — Definitions of domain-specific or application-specific terms
- **Keyboard Shortcuts** — If applicable, table of shortcuts
- **Version History** — Summary of major version changes relevant to users

---

## Content Splitting Guidelines

**Threshold:** If the assembled playbook exceeds **800 lines**, split into sub-files.

**File naming convention:**
- Sub-markdown files: `{nn}-{section-slug}.md` (e.g., `01-overview.md`, `06-configuration.md`)
- Screenshot images: `screenshots/{nn}-{section-slug}-{description}.png` (e.g., `screenshots/04-core-features-dashboard-view.png`)
- Sub-markdown files stored alongside the main playbook; all images stored in `screenshots/` subfolder

**Subfolder convention for Sections 4 and 5:**
Sections 4 (Core Features) and 5 (Common Workflows) ALWAYS use subfolders with per-item files, regardless of content length:
- `04-core-features/feature{nn}-{slug}.md` — one file per feature
- `04-core-features/_index.md` — feature listing table
- `04-core-features/screenshots/` — feature screenshots
- `05-common-workflows/workflow{nn}-{slug}.md` — one file per workflow
- `05-common-workflows/_index.md` — workflow listing table
- `05-common-workflows/screenshots/` — workflow screenshots

**Sub-file structure:**
Each sub-markdown file follows this structure:
```
# {Section Number}. {Section Title}

## Instructions

{Brief explanation of what this section covers and how to use it}

## Content

{Extracted and validated content for this section}

## Screenshots

<!-- Optional — include when documenting UI features -->
![{Alt text}](references/{nn}-{section-slug}-{description}.png)
```

**When to split:**
1. Estimate total lines after all sections are assembled
2. IF total > 800 lines → create sub-files + update ToC to split mode
3. IF total ≤ 800 lines → keep inline + use inline ToC mode
