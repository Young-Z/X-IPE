# Python Implementation Tool Skill - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Flask REST API Implementation

**Context:**
- tech_stack entry: "Python/Flask"
- source_code_path: `src/my_app/`
- 2 @backend AAA scenarios received from orchestrator

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @backend
      Test Scenario: Create project via API
        Arrange:
          - Flask app is configured with test database
          - User is authenticated with valid JWT token
        Act:
          - Send POST /api/projects with body { "name": "Test Project" }
        Assert:
          - Response status is 201
          - Response body contains "id" field
  - scenario_text: |
      @backend
      Test Scenario: Reject duplicate project name
        Arrange:
          - Project "Existing" already exists in database
        Act:
          - Send POST /api/projects with body { "name": "Existing" }
        Assert:
          - Response status is 409
          - Response body contains error message "Project name already exists"
```

### Execution Flow

```
1. LEARN existing code:
   - Found: pyproject.toml with flask dependency
   - Detected: Flask framework
   - Existing pattern: Blueprint-based routes, jsonify responses

2. IMPLEMENT (built-in practices, no research):
   - Created: src/my_app/projects/routes.py
   - Applied: type hints, Google-style docstrings, Blueprint pattern

3. WRITE pytest tests:
   - Created: tests/test_projects_routes.py
```

### Implementation Output (snippet)

```python
# src/my_app/projects/routes.py
from flask import Blueprint, jsonify, request

from my_app.projects.service import ProjectService

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")


@projects_bp.route("", methods=["POST"])
def create_project() -> tuple:
    """Create a new project.

    Returns:
        Tuple of JSON response and status code.

    Raises:
        409: If project name already exists.
    """
    data: dict = request.get_json()
    project = ProjectService.create(name=data["name"])
    return jsonify({"id": project.id, "name": project.name}), 201
```

### Test Output (snippet)

```python
# tests/test_projects_routes.py
import pytest
from my_app import create_app


@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client


def test_create_project_via_api(client):
    """@backend: Create project via API."""
    # Arrange
    headers = {"Authorization": "Bearer test-token"}
    payload = {"name": "Test Project"}

    # Act
    response = client.post("/api/projects", json=payload, headers=headers)

    # Assert
    assert response.status_code == 201
    assert "id" in response.get_json()


def test_reject_duplicate_project_name(client):
    """@backend: Reject duplicate project name."""
    # Arrange — create existing project
    client.post("/api/projects", json={"name": "Existing"})

    # Act
    response = client.post("/api/projects", json={"name": "Existing"})

    # Assert
    assert response.status_code == 409
    assert "already exists" in response.get_json()["error"]
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/my_app/projects/routes.py"
      - "src/my_app/projects/service.py"
    test_files:
      - "tests/test_projects_routes.py"
    test_results:
      - scenario: "Create project via API"
        assert_clause: "Response status is 201"
        status: "pass"
      - scenario: "Create project via API"
        assert_clause: "Response body contains id field"
        status: "pass"
      - scenario: "Reject duplicate project name"
        assert_clause: "Response status is 409"
        status: "pass"
      - scenario: "Reject duplicate project name"
        assert_clause: "Response body contains error message"
        status: "pass"
    lint_status: "pass"
    stack_identified: "Python/Flask"
  errors: []
```

---

## Example 2: FastAPI + Async Endpoint

**Context:**
- tech_stack entry: "Python/FastAPI"
- source_code_path: `src/api/`
- 1 @backend AAA scenario

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @backend
      Test Scenario: Fetch user profile async
        Arrange:
          - User with id "user-123" exists in database
        Act:
          - Send GET /api/users/user-123
        Assert:
          - Response status is 200
          - Response body contains "email" field
          - Response time is under 100ms
```

### Execution Flow

```
1. LEARN: Found fastapi in pyproject.toml, async patterns in existing code
2. IMPLEMENT: Created async endpoint with Pydantic response model
3. WRITE: TestClient-based pytest function
4. RUN tests: 3/3 assertions pass
5. RUN lint: ruff check + ruff format → pass
```

### Implementation Output (snippet)

```python
# src/api/routers/users.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/users", tags=["users"])


class UserProfile(BaseModel):
    """User profile response model."""
    id: str
    email: str
    display_name: str


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str) -> UserProfile:
    """Fetch user profile by ID.

    Args:
        user_id: The unique user identifier.

    Returns:
        UserProfile with email and display name.

    Raises:
        HTTPException: 404 if user not found.
    """
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(id=user.id, email=user.email, display_name=user.name)
```

### Test Output (snippet)

```python
# tests/test_users_router.py
from fastapi.testclient import TestClient
from src.api.main import app


client = TestClient(app)


def test_fetch_user_profile_async():
    """@backend: Fetch user profile async."""
    # Arrange — seed test user
    # (handled by test fixture or factory)

    # Act
    response = client.get("/api/users/user-123")

    # Assert
    assert response.status_code == 200
    assert "email" in response.json()
```

---

## Example 3: CLI Tool with argparse

**Context:**
- tech_stack entry: "Python/CLI"
- source_code_path: `src/cli/`
- 2 @backend AAA scenarios

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @backend
      Test Scenario: Export data to CSV
        Arrange:
          - Database contains 10 records
        Act:
          - Run CLI command: export --format csv --output data.csv
        Assert:
          - Exit code is 0
          - File data.csv is created
          - File contains 10 rows plus header
  - scenario_text: |
      @backend
      Test Scenario: Invalid format argument
        Arrange:
          - No preconditions
        Act:
          - Run CLI command: export --format xml
        Assert:
          - Exit code is non-zero
          - Error message contains "unsupported format"
```

### Implementation Output (snippet)

```python
# src/cli/export_cmd.py
import argparse
import csv
import sys
from pathlib import Path


def create_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser.

    Returns:
        Configured ArgumentParser for the export command.
    """
    parser = argparse.ArgumentParser(description="Export data")
    parser.add_argument("--format", choices=["csv", "json"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(args: list[str] | None = None) -> int:
    """Run the export command.

    Args:
        args: CLI arguments (defaults to sys.argv).

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = create_parser()
    parsed = parser.parse_args(args)
    # ... export logic
    return 0
```

### Test Output (snippet)

```python
# tests/test_export_cmd.py
import pytest
from src.cli.export_cmd import main


def test_export_data_to_csv(tmp_path):
    """@backend: Export data to CSV."""
    # Arrange
    output_file = tmp_path / "data.csv"

    # Act
    exit_code = main(["--format", "csv", "--output", str(output_file)])

    # Assert
    assert exit_code == 0
    assert output_file.exists()
    lines = output_file.read_text().strip().split("\n")
    assert len(lines) == 11  # 10 rows + header


def test_invalid_format_argument():
    """@backend: Invalid format argument."""
    # Act
    with pytest.raises(SystemExit) as exc_info:
        main(["--format", "xml", "--output", "out.csv"])

    # Assert
    assert exc_info.value.code != 0
```
