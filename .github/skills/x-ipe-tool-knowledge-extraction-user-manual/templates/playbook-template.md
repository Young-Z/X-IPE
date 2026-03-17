# User Manual — Playbook Template

> Base layout for user manual knowledge extraction. Each H2 section defines a standard chapter.
> The extractor uses this template to structure the final output.

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

**What belongs here:** Feature-by-feature usage guide covering all primary capabilities.

**Subsections:**
- One H3 per feature (e.g., `### User Management`, `### Data Export`)
- Each feature subsection includes:
  - What it does
  - How to use it (steps or commands)
  - Example usage
  - Tips or best practices

---

## 5. Configuration

**What belongs here:** All user-facing settings, options, and customization points.

**Subsections:**
- **Configuration File** — Location, format, and structure of config files
- **Environment Variables** — Table of env vars with name, description, default, required flag
- **Runtime Options** — Command-line flags or UI settings that modify behavior
- **Profiles / Environments** — How to manage different configurations (dev, staging, prod)

---

## 6. Troubleshooting

**What belongs here:** Common problems users encounter and how to resolve them.

**Subsections:**
- **Common Issues** — Table or list of frequent problems with symptoms and fixes
- **Error Messages** — Reference of error codes/messages with explanations
- **Diagnostic Steps** — How to gather logs, enable debug mode, check connectivity
- **Getting Help** — Where to report bugs, ask questions, find community support

---

## 7. FAQ & Reference

**What belongs here:** Frequently asked questions and reference material.

**Subsections:**
- **FAQ** — Question-and-answer format for the most common user questions
- **Glossary** — Definitions of domain-specific or application-specific terms
- **Keyboard Shortcuts** — If applicable, table of shortcuts
- **Version History** — Summary of major version changes relevant to users
