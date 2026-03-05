# Feature Specification: Python Implementation Tool Skill

> Feature ID: FEATURE-045-B  
> Epic ID: EPIC-045  
> Version: v1.0  
> Status: Refined  
> Last Updated: 03-05-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-05-2026 | Initial specification |

## Linked Mockups

N/A — This feature creates an AI skill file (SKILL.md). No UI components.

## Overview

This feature creates `x-ipe-tool-implementation-python`, a language-specific tool skill that the `x-ipe-task-based-code-implementation` orchestrator routes to when `tech_stack` contains Python-related entries (Python, Flask, FastAPI, Django, CLI, library). Unlike the general fallback skill, this skill has **built-in Python best practices** — no research step is needed, which makes it faster and more reliable.

The skill accepts AAA scenarios from the orchestrator, implements Python source code following PEP 8 and type-hinting conventions, writes pytest test functions mapped to AAA Assert clauses, runs tests and linting (ruff), and returns the standard tool skill output contract.

## User Stories

1. **As an AI agent**, I want a Python-specific implementation skill with built-in best practices (PEP 8, type hints, pytest patterns), so that I can implement Python code faster without a research step.

2. **As an AI agent**, I want the skill to detect whether the project uses Flask, FastAPI, Django, or plain Python, so that framework-specific patterns (route decorators, async endpoints, view classes) are applied correctly.

3. **As an AI agent**, I want AAA scenarios automatically mapped to pytest test functions with proper fixtures and parametrize usage, so that test output is idiomatic Python.

## Acceptance Criteria

### AC-1: Standard I/O Contract

- GIVEN the orchestrator routes a Python tech_stack entry to this skill
- WHEN the skill receives `aaa_scenarios`, `source_code_path`, `test_code_path`, and `feature_context`
- THEN it returns `implementation_files`, `test_files`, `test_results`, `lint_status` in the standard format defined in [implementation-guidelines.md](x-ipe-docs/requirements/EPIC-045/FEATURE-045-A/../../../.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md)

### AC-2: Python-Specific Best Practices (Built-In)

- GIVEN this skill is invoked
- WHEN it implements source code
- THEN it applies: PEP 8 style, type hints on all function signatures, docstrings on public functions, proper import ordering (stdlib → third-party → local), snake_case naming

### AC-3: Test Framework Support

- GIVEN AAA scenarios are provided
- WHEN the skill writes tests
- THEN it creates pytest functions: `def test_{scenario_name}():` with Arrange→fixtures/setup, Act→function call or HTTP request, Assert→pytest assertions
- AND uses `@pytest.mark.parametrize` for scenarios with similar structure

### AC-4: Framework Detection

- GIVEN a `source_code_path` with existing Python code
- WHEN the skill reads the project
- THEN it detects the framework (Flask routes, FastAPI endpoints, Django views, CLI argparse, or plain library) and applies framework-specific patterns

### AC-5: Linting Integration

- GIVEN implementation is complete
- WHEN the skill runs linting
- THEN it executes `ruff check` and `ruff format --check` (falling back to `flake8`/`black` if ruff unavailable)
- AND fixes any auto-fixable issues before returning results

### AC-6: Existing Code Convention Following

- GIVEN existing source files in `source_code_path`
- WHEN implementing new code
- THEN the skill follows existing naming patterns, module structure, error handling style, and import conventions already in use

## Functional Requirements

### FR-1: Skill File Structure
The skill SHALL be a SKILL.md file at `.github/skills/x-ipe-tool-implementation-python/SKILL.md` with accompanying `references/examples.md`.

### FR-2: Built-In Practices (No Research Step)
The skill SHALL NOT include a research step. Python best practices (PEP 8, type hints, docstrings, import ordering) are baked into the operation steps.

### FR-3: AAA-to-Pytest Mapping
The skill SHALL map each AAA scenario to a `def test_{scenario_name}()` function. Each Assert clause SHALL become a pytest assertion. Similar scenarios SHALL use `@pytest.mark.parametrize`.

### FR-4: Framework Detection Logic
The skill SHALL detect frameworks by checking: `pyproject.toml`/`requirements.txt` for dependencies, file patterns (`app.py` with Flask, `main.py` with FastAPI, `manage.py` with Django, `cli.py`/`__main__.py` for CLI tools).

### FR-5: Virtual Environment Awareness
The skill SHALL check for active virtual environments and use `python -m pytest` (not bare `pytest`) to avoid path issues.

### FR-6: Linting Pipeline
The skill SHALL run `ruff check --fix` → `ruff format` → re-run tests after lint fixes. If ruff is unavailable, fall back to `flake8` + `black`.

### FR-7: Standard Output Contract
The skill SHALL return output matching the tool skill I/O contract: `implementation_files`, `test_files`, `test_results` (per Assert clause), `lint_status`.

## Non-Functional Requirements

### NFR-1: Skill File Size
The SKILL.md SHALL be under 250 lines to maintain readability and context efficiency.

### NFR-2: No External Dependencies
The skill SHALL not require any tools beyond standard Python development tools (pytest, ruff/flake8, black).

### NFR-3: Orchestrator Compatibility
The skill SHALL be auto-discoverable by the orchestrator's AI semantic routing via its `description` and `When to Use` section.

## Technical Scope

- [x] Skills (SKILL.md + references)
- [ ] Backend
- [ ] Frontend
- [ ] Full Stack

## Dependencies

- FEATURE-045-A (Orchestrator Core + AAA Generator + General Fallback) — **completed**
- [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md) — I/O contract definition
