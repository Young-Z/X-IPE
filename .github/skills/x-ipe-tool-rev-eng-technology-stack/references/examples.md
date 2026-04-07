# Examples — x-ipe-tool-rev-eng-technology-stack

## Example 1: Node.js Express Project

**Scenario:** Extract technology stack from a Node.js REST API project.

**Input:**
```yaml
operation: extract
repo_path: /workspace/source/express-api
output_path: /workspace/kb-output
section_context:
  section_number: 7
  section_name: "Technology Stack Identification"
  phase: "1-Scan"
  repo_type: "single-module"
```

**Execution Flow:**

1. `extract` — Input initialization detects `package.json` + `package-lock.json`. Produces `07-technology-stack/` with 6 files:

   **`7.1-languages.md`:**
   | Language | Version Constraint | Evidence File | Lock Version |
   |----------|-------------------|---------------|--------------|
   | JavaScript (Node.js) | `>=18.0.0` | `package.json` (engines.node) | — |
   | TypeScript | `~5.2.0` | `package.json` (devDependencies) | `5.2.2` (`package-lock.json`) |

   **`7.2-frameworks.md`:**
   | Framework | Version | Evidence File | Config Evidence |
   |-----------|---------|---------------|-----------------|
   | Express | `^4.18.0` | `package.json` | `src/app.ts` (import) |
   | Prisma | `^5.7.0` | `package.json` | `prisma/schema.prisma` |

   **`7.3-build-tools.md`:**
   | Tool | Category | Config File | Purpose |
   |------|----------|-------------|---------|
   | npm | package-manager | `package-lock.json` | Dependency management |
   | TypeScript (tsc) | compiler | `tsconfig.json` | TS compilation |
   | ESLint | linter | `.eslintrc.json` | Code linting |

   **`7.4-runtime-infrastructure.md`:**
   | Tool | Category | Version | Evidence File |
   |------|----------|---------|---------------|
   | Node.js | runtime | `18-alpine` | `Dockerfile` |
   | Docker | container | — | `Dockerfile`, `docker-compose.yml` |
   | GitHub Actions | ci-cd | — | `.github/workflows/ci.yml` |

   **`7.5-testing-frameworks.md`:**
   | Tool | Category | Version | Evidence File |
   |------|----------|---------|---------------|
   | Jest | runner | `^29.7.0` | `package.json` (devDependencies) |
   | Supertest | http-testing | `^6.3.0` | `package.json` (devDependencies) |
   | ts-jest | transform | `^29.1.0` | `jest.config.ts` |

2. `validate` — All REQ criteria pass:
   ```yaml
   criteria_results:
     - {id: AC-REQ-01, status: pass, detail: "2 languages with version constraints"}
     - {id: AC-REQ-02, status: pass, detail: "2 frameworks with config evidence"}
     - {id: AC-REQ-03, status: pass, detail: "3 build tools identified"}
     - {id: AC-REQ-04, status: pass, detail: "All 12 entries have evidence file citations"}
   quality_score: 0.91
   ```

3. `collect_tests` — Finds `tests/setup.test.ts` (verifies dependencies load)
4. `execute_tests` — 2 tests pass, 0 fail
5. `package` — Final index.md with quality score 0.91 and test summary

---

## Example 2: Python Multi-Module Project

**Scenario:** Extract technology stack from a Python project using Poetry with multiple modules.

**Input:**
```yaml
operation: extract
repo_path: /workspace/source/data-pipeline
output_path: /workspace/kb-output
section_context:
  section_number: 7
  section_name: "Technology Stack Identification"
  phase: "1-Scan"
  repo_type: "multi-module"
mixin_overlays: ["mixin-multi-module", "mixin-python"]
```

**Key Differences from Example 1:**
- Multiple `pyproject.toml` files (root + per-module)
- Poetry lock file (`poetry.lock`) instead of `package-lock.json`
- Python-specific framework detection (FastAPI, SQLAlchemy, Alembic)
- Multi-module mixin triggers per-module dependency comparison

**Execution Flow:**

1. `extract` — Input initialization detects `pyproject.toml` + `poetry.lock` at root, plus `modules/etl/pyproject.toml` and `modules/api/pyproject.toml`.

   **`7.1-languages.md` (excerpt):**
   | Language | Version Constraint | Evidence File | Lock Version |
   |----------|-------------------|---------------|--------------|
   | Python | `>=3.11,<3.13` | `pyproject.toml` | `3.11.7` (`.python-version`) |

   **`7.2-frameworks.md` (excerpt):**
   | Framework | Version | Evidence File | Config Evidence |
   |-----------|---------|---------------|-----------------|
   | FastAPI | `>=0.104.0` | `modules/api/pyproject.toml` | `modules/api/main.py` |
   | SQLAlchemy | `>=2.0` | `pyproject.toml` (root) | `modules/etl/models/base.py` |
   | Alembic | `>=1.12` | `pyproject.toml` (root) | `alembic/env.py`, `alembic.ini` |
   | Pydantic | `>=2.5` | `modules/api/pyproject.toml` | `modules/api/schemas/` |

   **`7.3-build-tools.md` (excerpt):**
   | Tool | Category | Config File | Purpose |
   |------|----------|-------------|---------|
   | Poetry | package-manager | `poetry.lock` | Dependency management |
   | Make | build | `Makefile` | Task automation |
   | Ruff | linter | `pyproject.toml [tool.ruff]` | Python linting and formatting |

2. `validate` — All REQ criteria pass with quality_score: 0.89
   - Note: Multi-module mixin flags that `modules/etl/` and `modules/api/` have overlapping dependencies (SQLAlchemy) which could indicate shared library needed

3. `collect_tests` — Finds `tests/test_dependencies.py` (checks all imports resolve)
4. `execute_tests` — 3 pass, 1 skipped (requires database connection)
5. `package` — Final output with per-module dependency breakdown in index.md

**Output `index.md` (abbreviated):**
```markdown
---
section: 7
title: Technology Stack Identification
quality_score: 0.89
tests: {run: 3, passed: 3, failed: 0, skipped: 1}
---

# 7. Technology Stack Identification

## Table of Contents
1. [7.1 Languages](7.1-languages.md) — Python 3.11+
2. [7.2 Frameworks](7.2-frameworks.md) — FastAPI, SQLAlchemy, Alembic, Pydantic
3. [7.3 Build Tools](7.3-build-tools.md) — Poetry, Make, Ruff
4. [7.4 Runtime & Infrastructure](7.4-runtime-infrastructure.md) — Docker, GitHub Actions
5. [7.5 Testing Frameworks](7.5-testing-frameworks.md) — pytest, coverage, factory-boy

## Summary
Python multi-module project with 2 modules (api, etl). Uses Poetry for dependency
management with shared root dependencies. FastAPI for API layer, SQLAlchemy for
data access. Fully containerized with Docker and CI/CD via GitHub Actions.

## Multi-Module Note
Modules `api` and `etl` share SQLAlchemy dependency — consider extracting to
shared library module.
```
