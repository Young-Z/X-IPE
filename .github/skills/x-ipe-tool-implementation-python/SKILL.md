---
name: x-ipe-tool-implementation-python
description: Python-specific implementation tool skill. Handles Python, Flask, FastAPI, Django, CLI, and library projects with built-in best practices (PEP 8, type hints, pytest). No research step needed — practices are baked in. Called by x-ipe-task-based-code-implementation orchestrator. Triggers on Python tech_stack entries.
---

# Python Implementation Tool Skill

## Purpose

AI Agents follow this skill to implement Python code by:
1. Learning existing code structure and detecting framework
2. Implementing with built-in Python best practices (PEP 8, type hints, docstrings)
3. Writing pytest tests mapped to AAA scenario Assert clauses
4. Running tests and linting (ruff)

---

## Important Notes

BLOCKING: This skill is invoked by the `x-ipe-task-based-code-implementation` orchestrator. Do NOT invoke directly unless testing.

CRITICAL: No research step is needed — Python best practices are built into this skill. Skip identification/research and go straight to learning existing code.

MANDATORY: Follow the standard tool skill I/O contract defined in [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md).

---

## About

The Python Implementation Tool Skill handles all Python-related tech_stack entries routed by the orchestrator. Unlike the general fallback skill, this skill has **built-in best practices** — no research step is needed, making it faster and more reliable.

**Key Concepts:**
- **Built-In Practices** — PEP 8, type hints, docstrings, import ordering are hardcoded, not discovered
- **AAA Contract** — Receives AAA scenarios and returns standard tool skill output (implementation_files, test_files, test_results, lint_status)
- **Framework Detection** — Identifies Flask, FastAPI, Django, CLI, or plain library from project files

---

## When to Use

```yaml
triggers:
  - "tech_stack contains Python, Flask, FastAPI, Django"
  - "tech_stack contains python CLI, python library"
  - "Orchestrator routes Python-related entry to this skill"

not_for:
  - "x-ipe-tool-implementation-html5: for HTML/CSS/JavaScript"
  - "x-ipe-tool-implementation-typescript: for TypeScript/React/Vue/Angular"
  - "x-ipe-tool-implementation-java: for Java/Spring Boot"
  - "x-ipe-tool-implementation-mcp: for MCP servers"
  - "x-ipe-tool-implementation-general: for unknown/rare stacks"
```

---

## Input Parameters

```yaml
input:
  operation: "implement"
  aaa_scenarios:
    - scenario_text: "{tagged AAA scenario text}"
  source_code_path: "{path to source directory}"
  test_code_path: "{path to test directory}"
  feature_context:
    feature_id: "{FEATURE-XXX-X}"
    feature_title: "{title}"
    technical_design_link: "{path to technical-design.md}"
    specification_link: "{path to specification.md}"
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Always 'implement' when called by orchestrator" />
  <field name="aaa_scenarios" source="Filtered scenarios from orchestrator Step 5" />
  <field name="source_code_path" source="From technical design Part 2" />
  <field name="test_code_path" source="From technical design Part 2 or project convention" />
  <field name="feature_context" source="From orchestrator's Feature Data Model" />
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>AAA scenarios provided</name>
    <verification>aaa_scenarios array is non-empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Source code path valid</name>
    <verification>source_code_path directory exists or can be created</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature context complete</name>
    <verification>feature_id and technical_design_link are provided</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: implement

**When:** Orchestrator routes a Python tech_stack entry to this skill

```xml
<operation name="implement">
  <action>
    1. LEARN existing code:
       a. Read existing files in source_code_path
       b. Detect framework:
          - Check pyproject.toml/requirements.txt for flask/fastapi/django/click/typer
          - Check file patterns: app.py (Flask), main.py with FastAPI(), manage.py (Django)
          - Check for __main__.py or argparse usage (CLI)
          - Default: plain Python library
       c. Follow existing conventions (naming, imports, error handling, module structure)

    2. IMPLEMENT with built-in Python best practices:
       a. Follow technical design Part 2 exactly
       b. PEP 8 style throughout
       c. Type hints on ALL function signatures (parameters + return type)
       d. Docstrings on all public functions (Google-style: Args, Returns, Raises)
       e. Import ordering: stdlib → third-party → local (blank line between groups)
       f. Apply framework-specific patterns:
          - Flask: @app.route / Blueprint, request/jsonify, error handlers
          - FastAPI: @router.get/post, Pydantic models, async def, Depends()
          - Django: Class-based views, serializers, URL conf
          - CLI: argparse.ArgumentParser or click.command / typer.Typer
       g. Follow KISS/YAGNI — implement only what design specifies

    3. WRITE pytest tests mapped to AAA scenarios:
       a. FOR EACH AAA scenario:
          - Create: def test_{scenario_name_snake_case}():
          - Arrange → fixtures, test data, mocks (pytest fixtures for shared setup)
          - Act → function call, test client request, or CLI runner invoke
          - Assert → one assert statement per Assert clause
       b. Use @pytest.mark.parametrize for scenarios with similar structure
       c. Framework test patterns:
          - Flask: app.test_client(), pytest fixture for app
          - FastAPI: from fastapi.testclient import TestClient
          - Django: django.test.TestCase, self.client
          - CLI: subprocess.run or click.testing.CliRunner

    4. RUN tests:
       a. Execute: python -m pytest {test_code_path} -v
       b. Record pass/fail for each Assert clause

    5. RUN linting:
       a. Execute: ruff check {source_code_path} --fix
       b. Execute: ruff format {source_code_path}
       c. If ruff unavailable: flake8 {source_code_path} + black {source_code_path}
       d. Re-run tests after any lint-induced changes

    6. RETURN standard output
  </action>
  <constraints>
    - CRITICAL: No research step — Python best practices are built into Step 2
    - CRITICAL: Follow existing code conventions found in Step 1
    - MANDATORY: Every AAA Assert clause must map to exactly one test assertion
    - MANDATORY: Use python -m pytest (not bare pytest) for virtual environment safety
  </constraints>
  <output>Standard tool skill output (implementation_files, test_files, test_results, lint_status)</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    implementation_files:
      - "{path to created source file 1}"
    test_files:
      - "{path to created test file 1}"
    test_results:
      - scenario: "{scenario name}"
        assert_clause: "{assert text}"
        status: "pass | fail"
        error: "{error message if fail}"
    lint_status: "pass | fail"
    lint_details: "{details if fail}"
    stack_identified: "Python/{framework}"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Framework detected</name>
    <verification>stack_identified contains "Python/{framework}" in output</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Implementation files created</name>
    <verification>implementation_files array is non-empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test files created</name>
    <verification>test_files array is non-empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All AAA Assert clauses mapped to tests</name>
    <verification>test_results count equals total Assert clauses across all scenarios</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Lint passes</name>
    <verification>lint_status == "pass"</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `PYTHON_VERSION_CONFLICT` | Code requires Python version not available | Log warning, attempt with available Python; if incompatible, signal orchestrator |
| `DEPENDENCY_MISSING` | Required package not installed (e.g., flask, pytest) | Run `pip install {package}` or `uv add {package}`, then retry implementation |
| `VENV_NOT_FOUND` | No virtual environment detected | Use `python -m pytest` to avoid path issues; log warning |
| `TEST_FAILURE` | One or more Assert clauses fail | Return detailed test_results with error messages; orchestrator handles retry |
| `LINT_UNAVAILABLE` | Neither ruff nor flake8 found | Log warning, return lint_status: "skipped", continue |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-implementation-python/references/examples.md) for usage examples.
