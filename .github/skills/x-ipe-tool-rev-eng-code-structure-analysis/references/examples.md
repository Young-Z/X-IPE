# Examples — x-ipe-tool-rev-eng-code-structure-analysis

## Example 1: Python Django Project

**Scenario:** Extract code structure from a Django web application.

**Input:**
```yaml
operation: extract
repo_path: /workspace/source/django-shop
output_path: /workspace/kb-output
section_context:
  section_number: 5
  section_name: "Code Structure Analysis"
  phase: "1-Scan"
  repo_type: "single-module"
config:
  tree_depth: 3
  hotspot_threshold: 15
```

**Execution Flow:**
1. `extract` — Produces `05-code-structure-analysis/` with 5 files:
   - `index.md` — TOC linking subsections
   - `5.1-project-layout.md` — Annotated tree showing `shop/`, `orders/`, `products/` Django apps
   - `5.2-directory-structure.md` — Table mapping directories to roles (e.g., `shop/views/` → "View layer for HTTP handling")
   - `5.3-naming-conventions.md` — Django conventions: snake_case files, PascalCase models, `*View` class suffix
   - `5.4-module-boundaries.md` — `__init__.py` markers, Django app structure (models/views/urls/admin pattern)

2. `validate` — Checks all REQ criteria pass:
   ```yaml
   criteria_results:
     - {id: AC-REQ-01, status: pass, detail: "Tree is 3 levels deep with annotations"}
     - {id: AC-REQ-02, status: pass, detail: "Table has 18 rows with Directory/Role/Key Files"}
     - {id: AC-REQ-03, status: pass, detail: "3 naming patterns with Django examples"}
     - {id: AC-REQ-04, status: pass, detail: "Found 12 __init__.py files as boundary markers"}
   quality_score: 0.88
   ```

3. `collect_tests` — Finds `tests/test_imports.py` and `tests/test_app_config.py`
4. `execute_tests` — Runs tests; 4 pass, 0 fail
5. `package` — Finalizes with quality score and test summary in `index.md`

**Output `index.md` (abbreviated):**
```markdown
---
section: 5
title: Code Structure Analysis
quality_score: 0.88
tests: {run: 4, passed: 4, failed: 0, skipped: 0}
---

# 5. Code Structure Analysis

## Table of Contents
1. [5.1 Project Layout](5.1-project-layout.md) — Root directory tree with annotations
2. [5.2 Directory Structure](5.2-directory-structure.md) — Directory-to-purpose mapping
3. [5.3 Naming Conventions](5.3-naming-conventions.md) — File/class/function patterns
4. [5.4 Module Boundaries](5.4-module-boundaries.md) — Django app boundaries

## Summary
Single-module Django project with 3 Django apps (shop, orders, products).
Follows standard Django conventions. Clean app separation via Django app structure.
```

---

## Example 2: TypeScript Monorepo

**Scenario:** Extract code structure from a Turborepo-based monorepo.

**Input:**
```yaml
operation: extract
repo_path: /workspace/source/acme-platform
output_path: /workspace/kb-output
section_context:
  section_number: 5
  section_name: "Code Structure Analysis"
  phase: "1-Scan"
  repo_type: "monorepo"
mixin_overlays: ["mixin-monorepo", "mixin-typescript"]
```

**Key Differences from Example 1:**
- Monorepo mixin triggers per-package tree analysis within `packages/` and `apps/`
- Naming conventions span multiple packages (may differ per package)
- Module boundaries use `package.json` per workspace instead of `__init__.py`
- Directory structure table includes workspace membership column

**Output `5.4-module-boundaries.md` (abbreviated):**
```markdown
# 5.4 Module Boundaries

## Boundary Markers

| Marker | Count | Locations |
|--------|-------|-----------|
| `package.json` | 8 | `root`, `apps/web`, `apps/api`, `packages/ui`, `packages/config`, ... |
| `tsconfig.json` | 8 | Same as package.json |
| `index.ts` | 23 | Barrel exports in each package's `src/` |

## Workspace Structure
- **apps/web** — Next.js frontend (depends on: @acme/ui, @acme/config)
- **apps/api** — Express API server (depends on: @acme/db, @acme/config)
- **packages/ui** — Shared React components (depends on: @acme/config)
- **packages/db** — Prisma database layer (no internal deps)
- **packages/config** — Shared ESLint/TS configs (no internal deps)

## Layering Pattern: Workspace Dependency Graph
```
apps/web ──→ packages/ui ──→ packages/config
apps/api ──→ packages/db
         ──→ packages/config
```
```

**Validation Result:**
```yaml
quality_score: 0.92
criteria_results:
  - {id: AC-REQ-01, status: pass}
  - {id: AC-REQ-02, status: pass}
  - {id: AC-REQ-03, status: pass}
  - {id: AC-REQ-04, status: pass}
  - {id: AC-OPT-01, status: pass, detail: "Hot spots: apps/web/src/ (47 files), packages/ui/src/ (31 files)"}
  - {id: AC-OPT-02, status: pass, detail: "Workspace dependency graph identified"}
```
