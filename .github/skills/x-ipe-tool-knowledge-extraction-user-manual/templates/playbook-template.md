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
| 4 | Core Features | [Core Features](04-core-features.md) |
| 5 | Common Workflow Scenarios | [Common Workflow Scenarios](05-common-workflow-scenarios.md) |
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

**Subsections:**
- One H3 per feature (e.g., `### User Management`, `### Data Export`)
- Each feature subsection MUST include:
  - **Description** — What it does and why a user would use it
  - **Instructions** — Step-by-step usage guide (numbered steps with concrete commands or UI paths)
  - **Example** — Concrete usage example with expected output
  - **Screenshots** — Reference screenshots for UI features: `![{Alt text}]({nn}-core-features-{feature-slug}.png)`
  - **Tips** — Best practices, common pitfalls, or power-user shortcuts (optional but recommended)

**Screenshot convention:** `04-core-features-{feature-slug}-{description}.png`
(e.g., `04-core-features-user-mgmt-create-dialog.png`)

**When content is insufficient:** If extracted content lacks detail for any feature subsection (e.g., missing instructions or only has a one-liner description), flag it as INCOMPLETE and request the extractor to gather more source material for that specific feature.

---

## 5. Common Workflow Scenarios

**What belongs here:** End-to-end workflow walkthroughs showing how multiple features work together to accomplish real-world tasks. Unlike Section 4 (which documents individual features), this section demonstrates feature combinations in context.

**Subsections:**
- One H3 per scenario (e.g., `### Onboarding a New Team Member`, `### Deploying to Production`)
- Each scenario MUST include:
  - **Goal** — What the user wants to accomplish (1 sentence)
  - **Prerequisites** — What must be set up before starting
  - **Steps** — Numbered walkthrough referencing features from Section 4 (with cross-links)
  - **Expected Result** — What success looks like
  - **Screenshots** — Key UI states during the workflow: `![{Alt text}]({nn}-workflows-{scenario-slug}.png)`
  - **Tips** — Variations, shortcuts, or "what if" guidance (optional)

**Screenshot convention:** `05-workflows-{scenario-slug}-{description}.png`
(e.g., `05-workflows-deploy-prod-pipeline-view.png`)

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
- Sub-markdown files: `{nn}-{section-slug}.md` (e.g., `01-overview.md`, `04-core-features.md`)
- Screenshot images: `{nn}-{section-slug}-{description}.png` (e.g., `04-core-features-dashboard-view.png`)
- All files stored in the same output directory alongside the main playbook

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
![{Alt text}]({nn}-{section-slug}-{description}.png)
```

**When to split:**
1. Estimate total lines after all sections are assembled
2. IF total > 800 lines → create sub-files + update ToC to split mode
3. IF total ≤ 800 lines → keep inline + use inline ToC mode
