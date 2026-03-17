# File-Based Handoff Protocol

> Version: v1.0 | Feature: FEATURE-050-A | Last Updated: 03-17-2026

---

## Purpose

This document defines the file-based handoff protocol used by the Application Knowledge Extractor to exchange knowledge with tool skills. All communication occurs via files in `.x-ipe-checkpoint/` folder.

---

## Protocol Overview

### Key Principles

1. **File-Based Only:** All data exchange uses files in `.x-ipe-checkpoint/`, never inline YAML
2. **Session Isolation:** Each extraction session has its own timestamped folder
3. **Structured Manifest:** Session state tracked in `manifest.yaml`
4. **Location Rule:** `.x-ipe-checkpoint/` created in CWD (project root), NEVER inside target directory

---

## Folder Structure

```
.x-ipe-checkpoint/
└── session-{timestamp}/
    ├── manifest.yaml              # Session manifest
    ├── content/                   # Extracted content chunks (FEATURE-050-B)
    ├── feedback/                  # Tool skill feedback (FEATURE-050-C)
    └── screenshots/               # Screenshots captured during extraction
```

---

## Session Manifest

### Manifest File: `manifest.yaml`

```yaml
schema_version: "1.0"
session_id: "session-{timestamp}"
created_at: "{ISO 8601}"
updated_at: "{ISO 8601}"
target: "{path or URL}"
purpose: "{category}"

input_analysis:
  input_type: "{type}"
  format: "{format}"
  app_type: "{type}"
  source_metadata: {}

selected_category: "{category}"
loaded_tool_skill: "{skill name}"
tool_skill_artifacts:
  playbook_template: "{path}"
  collection_template: "{path}"
  acceptance_criteria: "{path}"

status: "initialized"  # initialized | extracting | validating | complete | paused | error
sections: []
coverage_score: null
quality_score: null
error_log: []
```

---

## Content Files

Content files written by extractor during extraction (FEATURE-050-B):

```
.x-ipe-checkpoint/session-{timestamp}/content/
├── section-01-{slug}.md
├── section-02-{slug}.md
└── ...
```

---

## Feedback Files

Feedback files written by tool skills during validation (FEATURE-050-C):

```
.x-ipe-checkpoint/session-{timestamp}/feedback/
├── section-01-feedback.yaml
├── section-02-feedback.yaml
└── ...
```

---

## Screenshots

Screenshots captured during extraction (e.g., via Chrome DevTools) are stored inside the session folder:

```
.x-ipe-checkpoint/session-{timestamp}/screenshots/
├── 04-core-features-{feature-slug}-{description}.png
├── 05-workflows-{scenario-slug}-{description}.png
└── ...
```

**Session Isolation:** Each extraction session stores screenshots in its own session folder. This prevents collisions between concurrent extractions and enables clean session-level cleanup.

**Naming Convention:** Screenshots follow the tool skill's naming convention: `{nn}-{section-slug}-{description}.png`

---

## Message Passing Protocol

### Extractor → Tool Skill

1. Extractor writes content to `.x-ipe-checkpoint/session-{timestamp}/content/section-{N}-{slug}.md`
2. Extractor updates manifest
3. Extractor invokes tool skill with file path (not inline content)

### Tool Skill → Extractor

1. Tool skill reads content file
2. Tool skill writes feedback to `.x-ipe-checkpoint/session-{timestamp}/feedback/section-{N}-feedback.yaml`
3. Tool skill returns feedback file path
4. Extractor reads feedback and processes

---

## References

- **Technical Design:** `x-ipe-docs/requirements/EPIC-050/FEATURE-050-A/technical-design.md`
- **Checkpoint Manifest Template:** `.github/skills/x-ipe-task-based-application-knowledge-extractor/templates/checkpoint-manifest.md`
