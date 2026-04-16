# Application RE — Python Language Mixin

> Apply this mixin when the target codebase contains Python source code.
> Merge these overlays into the base playbook when language: python.
> This is an additive overlay — it does NOT replace repo-type mixin content.

---

## Detection Signals

| Signal | File/Pattern | Confidence |
|--------|-------------|------------|
| Python files | `*.py` files present | high |
| pyproject.toml | `pyproject.toml` at root | high |
| requirements.txt | `requirements.txt` or `requirements/*.txt` | high |
| setup.py / setup.cfg | `setup.py` or `setup.cfg` | medium |
| Pipfile | `Pipfile` or `Pipfile.lock` | medium |
| __init__.py | `__init__.py` in directories (package markers) | medium |

---

## Section Overlay Prompts

### For Section 1 (Architecture Recovery)
<!-- ADDITIONAL PROMPTS:
- Identify Python package markers (__init__.py) and their exports (__all__)
- Note module-level conventions: constants at top, imports grouped (stdlib/third-party/local)
- Detect virtual environment patterns: venv/, .venv/, poetry.lock
- Identify src layout vs. flat layout
-->

### For Section 2 (API Contract Extraction)
<!-- ADDITIONAL PROMPTS:
- Extract Flask routes: @app.route(), @blueprint.route()
- Extract Django URL patterns: urlpatterns, path(), re_path()
- Extract FastAPI endpoints: @app.get(), @app.post(), @router.{method}()
- Extract type annotations from function signatures (typing module)
- Parse Pydantic models for request/response schemas
- Check for dataclass definitions (@dataclass)
-->

### For Section 3 (Business Logic Mapping)
<!-- ADDITIONAL PROMPTS:
- Detect decorator patterns: @property, @staticmethod, @classmethod, custom decorators
- Detect metaclass usage: __metaclass__, type() calls, ABCMeta
- Detect context manager patterns: __enter__/__exit__, @contextmanager
- Detect generator/iterator patterns: yield, __iter__/__next__
- Detect descriptor patterns: __get__/__set__/__delete__
- Look for Django/Flask patterns: model-view-template, blueprint registration, middleware
- Look for FastAPI patterns: dependency injection via Depends(), Pydantic models
- Python type hints may reveal Strategy pattern (Protocol classes, Union types)
-->

### For Section 5 (Dependency Analysis)
<!-- ADDITIONAL PROMPTS:
- Parse pyproject.toml [project.dependencies] and [project.optional-dependencies]
- Parse requirements.txt with version pinning
- Detect Python version from pyproject.toml [project.requires-python] or .python-version
- Identify package manager: pip, poetry, pdm, uv, pipenv
- Identify linting/formatting: ruff, black, flake8, mypy, pylint
-->

### For Section 7 (Security & Auth Patterns)
<!-- ADDITIONAL PROMPTS:
- Check for Django auth (django.contrib.auth, authentication backends)
- Detect Flask-Login, Flask-JWT-Extended usage
- Check for FastAPI security utilities (OAuth2PasswordBearer, HTTPBearer)
- Identify Python cryptography library usage (cryptography, hashlib, secrets)
-->

### For Section 8 (Testing Strategy)
<!-- ADDITIONAL PROMPTS:
- Detect pytest: conftest.py, pytest.ini, [tool.pytest.ini_options]
- Detect unittest: classes inheriting unittest.TestCase
- Look for pytest fixtures: @pytest.fixture, conftest.py fixtures
- Identify test parametrization: @pytest.mark.parametrize
- Check for coverage config: .coveragerc, [tool.coverage] in pyproject.toml
-->
