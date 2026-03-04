# Feature Specification: Existing File Migration

> Feature ID: FEATURE-043-D
> Epic ID: EPIC-043
> Version: v1.0
> Status: Refined
> Last Updated: 03-04-2026

## Overview

Migrate all existing markdown files in `x-ipe-docs/` and `.github/skills/` from relative or partial internal paths to full project-root-relative paths. This ensures the File Link Preview feature can resolve all links.

## Acceptance Criteria

- **AC-043-D.1:** All `.md` files in `x-ipe-docs/` and `.github/skills/` use full root-relative internal paths.
- **AC-043-D.2:** Paths inside fenced code blocks and inline code are NOT rewritten.
- **AC-043-D.3:** Unresolvable paths (target file doesn't exist) flagged for manual review, not auto-rewritten.
- **AC-043-D.4:** Migration performed via automated script with verification.

## Technical Scope

- **Type:** Documentation-only migration
- **No frontend, backend, or test changes**
- **Implementation:** Python migration script
