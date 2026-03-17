# Category Taxonomy

> Version: v1.0 | Feature: FEATURE-050-A | Last Updated: 03-17-2026

---

## Purpose

This document defines the fixed taxonomy of extraction categories used by the Application Knowledge Extractor.

---

## Extraction Categories

| ID | Name | Description | Priority | v1 Supported | Tool Skill |
|----|------|-------------|----------|--------------|------------|
| 1 | user-manual | End-user documentation: installation, usage, configuration, troubleshooting | 1 | ✅ Yes | x-ipe-tool-knowledge-extraction-user-manual |
| 2 | API-reference | API endpoints, schemas, authentication, rate limits | 2 | ❌ Future | x-ipe-tool-knowledge-extraction-api-reference |
| 3 | architecture | System design, module structure, data flow, deployment | 3 | ❌ Future | x-ipe-tool-knowledge-extraction-architecture |
| 4 | runbook | Operations: monitoring, alerts, incident response | 4 | ❌ Future | x-ipe-tool-knowledge-extraction-runbook |
| 5 | configuration | Configuration options, environment variables, feature flags | 5 | ❌ Future | x-ipe-tool-knowledge-extraction-configuration |

---

## Category Details

### 1. User Manual (v1 Supported)

**Purpose:** Extract knowledge for end users

**Scope:**
- Installation instructions
- Getting started guides
- Basic usage examples
- Configuration options (user-facing)
- Troubleshooting
- FAQ

**Tool Skill:** `x-ipe-tool-knowledge-extraction-user-manual`

**App-Type Mixins:**
- Web: UI navigation, screenshots, authentication
- CLI: Command-line usage, flags, subcommands
- Mobile: App store, permissions, gestures

---

## Category Selection Logic

### v1 Behavior (Hardcoded Filter)

```python
def select_category_v1(purpose: str) -> str:
    v1_supported = ["user-manual"]
    
    if purpose in v1_supported:
        return purpose
    else:
        raise Error(f"Category '{purpose}' not supported in v1. Supported: {v1_supported}")
```

**No AI inference required** in v1. User explicitly provides category via `purpose` parameter.

---

## Tool Skill Naming Convention

Pattern: `x-ipe-tool-knowledge-extraction-{category-id}`

Discovery: Glob `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md`

---

## References

- **Technical Design:** `x-ipe-docs/requirements/EPIC-050/FEATURE-050-A/technical-design.md`
- **Specification:** `x-ipe-docs/requirements/EPIC-050/FEATURE-050-A/specification.md`
