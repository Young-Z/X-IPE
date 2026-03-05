# Technical Design: Python Implementation Tool Skill

> Feature ID: FEATURE-045-B  
> Epic ID: EPIC-045  
> Version: v1.0  
> Status: Designed  
> Last Updated: 03-05-2026  
> program_type: skills  
> tech_stack: ["Markdown/SKILL.md"]

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-05-2026 | Initial design |

---

## Part 1: Agent-Facing Summary

### Key Components

| Component | Path | Purpose |
|-----------|------|---------|
| SKILL.md | `.github/skills/x-ipe-tool-implementation-python/SKILL.md` | Main skill definition — operations, I/O contract, Python-specific steps |
| examples.md | `.github/skills/x-ipe-tool-implementation-python/references/examples.md` | 3 usage examples (Flask, FastAPI, CLI) |

### Dependencies

| Dependency | Type | Path |
|------------|------|------|
| Orchestrator | Caller | `.github/skills/x-ipe-task-based-code-implementation/SKILL.md` |
| I/O Contract | Reference | `.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md` |
| General Fallback | Sibling template | `.github/skills/x-ipe-tool-implementation-general/SKILL.md` |

### How the Orchestrator Invokes This Skill

```
Orchestrator Step 4 (Route tool skills):
  FOR EACH tech_stack entry:
    AI semantic match against x-ipe-tool-implementation-* descriptions
    → tech_stack "Python/Flask" matches x-ipe-tool-implementation-python
    → Orchestrator passes filtered AAA scenarios to this skill
```

### Key Differentiator from General Fallback

| Aspect | General Fallback | Python Skill |
|--------|-----------------|--------------|
| Research step | Required (Step 2) | **Skipped** — practices built-in |
| Best practices | Discovered at runtime | **Hardcoded** (PEP 8, type hints, pytest) |
| Test framework | Discovered | **Always pytest** |
| Linting tool | Discovered | **Always ruff** (fallback: flake8+black) |
| Operation steps | 8 steps | **6 steps** (no identify/research) |

---

## Part 2: Implementation Guide

### Skill Structure

Mirror the general fallback structure with Python-specific modifications:

```
.github/skills/x-ipe-tool-implementation-python/
├── SKILL.md                    # Main skill (≤250 lines)
└── references/
    └── examples.md             # 3 examples (Flask, FastAPI, CLI)
```

### SKILL.md Sections

1. **Frontmatter** — `name: x-ipe-tool-implementation-python`, description mentions Python/Flask/FastAPI/Django/pytest
2. **Purpose** — 6-step process (no research step)
3. **Important Notes** — Same blocking/critical/mandatory notes as general
4. **About** — Key concepts: Built-In Practices, AAA Contract, Framework Detection
5. **When to Use** — Triggers on Python tech_stack entries; `not_for` lists other language skills
6. **Input Parameters** — Identical to general fallback (standard contract)
7. **Definition of Ready** — Same 3 checkpoints as general
8. **Operations** — 6-step implement operation (see below)
9. **Output Result** — Standard contract + `stack_identified: "Python/{framework}"`
10. **Definition of Done** — 5 checkpoints (no "research completed" checkpoint)
11. **Error Handling** — Python-specific errors
12. **Examples link** — Points to `references/examples.md`

### Operation Steps (implement)

```
Step 1: LEARN existing code
  a. Read existing files in source_code_path
  b. Identify framework:
     - pyproject.toml/requirements.txt → check for flask/fastapi/django/click/typer
     - File patterns: app.py (Flask), main.py with FastAPI(), manage.py (Django)
     - CLI indicators: argparse, click, typer, __main__.py
     - Default: plain Python library
  c. Follow existing conventions (naming, imports, error handling)

Step 2: IMPLEMENT with built-in Python best practices
  a. Follow technical design Part 2 exactly
  b. Apply PEP 8 style throughout
  c. Type hints on ALL function signatures (params + return)
  d. Docstrings on all public functions (Google style)
  e. Import ordering: stdlib → third-party → local (blank line between groups)
  f. Framework-specific patterns:
     - Flask: @app.route, Blueprint, request/jsonify
     - FastAPI: @router.get, Pydantic models, async def
     - Django: Class-based views, serializers, URL patterns
     - CLI: argparse.ArgumentParser or click.command
  g. Follow KISS/YAGNI — implement only what's in technical design

Step 3: WRITE pytest tests mapped to AAA scenarios
  a. FOR EACH AAA scenario:
     - Create: def test_{scenario_name_snake_case}():
     - Arrange section → fixtures, test data setup, mocks
     - Act section → function call, HTTP test client request, CLI invoke
     - Assert section → assert statements (one per Assert clause)
  b. Use @pytest.mark.parametrize for similar scenarios
  c. Use pytest fixtures for shared setup
  d. Framework test patterns:
     - Flask: app.test_client()
     - FastAPI: TestClient(app) or httpx.AsyncClient
     - Django: django.test.TestCase, self.client
     - CLI: subprocess or click.testing.CliRunner

Step 4: RUN tests
  a. Execute: python -m pytest {test_code_path} -v
  b. Record pass/fail for each Assert clause

Step 5: RUN linting
  a. Execute: ruff check {source_code_path} --fix
  b. Execute: ruff format {source_code_path}
  c. If ruff unavailable: flake8 + black
  d. Re-run tests after any lint fixes

Step 6: RETURN standard output
  - Populate implementation_files, test_files, test_results, lint_status
```

### Framework Detection Algorithm

```
FUNCTION detect_framework(source_code_path):
  1. READ pyproject.toml OR requirements.txt
  2. SCAN dependencies:
     - "flask" → return "Flask"
     - "fastapi" → return "FastAPI"
     - "django" → return "Django"
     - "click" OR "typer" → return "CLI"
     - "argparse" in source files → return "CLI"
  3. CHECK file patterns:
     - manage.py exists → "Django"
     - app.py with "Flask(" → "Flask"
     - main.py with "FastAPI(" → "FastAPI"
     - __main__.py exists → "CLI"
  4. DEFAULT → "Library"
```

### Pytest Mapping Algorithm

```
FUNCTION map_aaa_to_pytest(scenario):
  test_name = snake_case(scenario.name)
  
  FOR EACH arrange_item:
    → Convert to fixture setup or inline variable
  
  FOR act_item:
    IF contains "POST/GET/PUT/DELETE":
      → Generate HTTP test client call
    ELIF contains "invoke" or "run":
      → Generate CLI runner call
    ELSE:
      → Generate direct function call
  
  FOR EACH assert_item:
    → Generate: assert {expected_condition}
    → One assert per Assert clause for traceability
```

### Error Codes

| Error | Cause | Resolution |
|-------|-------|------------|
| `PYTHON_VERSION_CONFLICT` | Code requires Python version not available | Log warning, attempt with available version |
| `DEPENDENCY_MISSING` | Required package not installed | Run `pip install` or `uv add`, then retry |
| `VENV_NOT_FOUND` | No virtual environment detected | Use `python -m pytest` to avoid path issues |
| `TEST_FAILURE` | Assert clause fails | Return detailed results; orchestrator handles retry |

### Design Change Log

| Date | Change | Reason |
|------|--------|--------|
| 03-05-2026 | Initial design | FEATURE-045-B creation |
