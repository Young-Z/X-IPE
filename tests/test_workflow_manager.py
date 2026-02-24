"""
Tests for FEATURE-036-A: Workflow Manager & State Persistence

Covers:
- WorkflowManagerService (unit tests)
- Flask workflow API endpoints (API tests)
- MCP tool integration (integration tests)

TDD: All tests written before implementation — all should FAIL initially.
"""

import json
import os
import tempfile
import shutil
from pathlib import Path

import pytest


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def workflow_dir(temp_project_dir):
    """Return the engineering-workflow directory path (not pre-created)."""
    return os.path.join(temp_project_dir, "x-ipe-docs", "engineering-workflow")


@pytest.fixture
def workflow_service(temp_project_dir):
    """Create a WorkflowManagerService instance."""
    from x_ipe.services.workflow_manager_service import WorkflowManagerService
    return WorkflowManagerService(temp_project_dir)


@pytest.fixture
def app(temp_project_dir):
    """Create Flask test app."""
    from x_ipe.app import create_app
    app = create_app({"TESTING": True, "PROJECT_ROOT": temp_project_dir})
    return app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_workflow(workflow_service):
    """Create a sample workflow and return its name."""
    name = "test-workflow"
    workflow_service.create_workflow(name)
    return name


@pytest.fixture
def workflow_with_features(workflow_service, sample_workflow):
    """Create a workflow with features populated."""
    features = [
        {"id": "FEATURE-040-A", "name": "Login Page", "depends_on": []},
        {"id": "FEATURE-040-B", "name": "Dashboard", "depends_on": ["FEATURE-040-A"]},
        {"id": "FEATURE-040-C", "name": "Settings", "depends_on": []},
    ]
    # Complete ideation and requirement stages first
    workflow_service.update_action_status(sample_workflow, "compose_idea", "done")
    workflow_service.update_action_status(sample_workflow, "refine_idea", "done")
    workflow_service.update_action_status(sample_workflow, "requirement_gathering", "done")
    workflow_service.update_action_status(sample_workflow, "feature_breakdown", "done")
    workflow_service.add_features(sample_workflow, features)
    return sample_workflow


# ==============================================================================
# Unit Tests: WorkflowManagerService — CRUD
# ==============================================================================

class TestWorkflowCRUD:
    """Unit tests for workflow create, read, list, delete operations."""

    def test_create_workflow_creates_json_file(self, workflow_service, workflow_dir):
        """AC: create_workflow(name) creates workflow-{name}.json with schema v1.0."""
        result = workflow_service.create_workflow("my-project")
        filepath = os.path.join(workflow_dir, "workflow-my-project.json")
        assert os.path.exists(filepath)

    def test_create_workflow_has_schema_version(self, workflow_service, workflow_dir):
        """AC: Workflow JSON includes schema_version: '2.0'."""
        workflow_service.create_workflow("my-project")
        filepath = os.path.join(workflow_dir, "workflow-my-project.json")
        with open(filepath) as f:
            state = json.load(f)
        assert state["schema_version"] == "2.0"

    def test_create_workflow_ideation_active(self, workflow_service):
        """AC: Ideation stage active, all other stages locked."""
        result = workflow_service.create_workflow("my-project")
        state = workflow_service.get_workflow("my-project")
        assert state["shared"]["ideation"]["status"] == "in_progress"
        assert state["shared"]["requirement"]["status"] == "locked"
        assert state["features"] == []

    def test_create_workflow_duplicate_name_error(self, workflow_service, sample_workflow):
        """AC: create_workflow returns error if name already exists."""
        result = workflow_service.create_workflow(sample_workflow)
        assert result["success"] is False
        assert "already exists" in result.get("message", "").lower()

    def test_create_workflow_auto_creates_directory(self, workflow_service, workflow_dir):
        """AC: Workflow directory auto-created if it does not exist."""
        assert not os.path.exists(workflow_dir)
        workflow_service.create_workflow("first-workflow")
        assert os.path.exists(workflow_dir)

    def test_create_workflow_idea_folder_null(self, workflow_service):
        """AC: idea_folder defaults to null at creation."""
        workflow_service.create_workflow("my-project")
        state = workflow_service.get_workflow("my-project")
        assert state["idea_folder"] is None

    def test_get_workflow_returns_full_state(self, workflow_service, sample_workflow):
        """AC: get_workflow returns full parsed workflow state."""
        state = workflow_service.get_workflow(sample_workflow)
        assert state["name"] == sample_workflow
        assert "shared" in state
        assert "features" in state
        assert "created" in state
        assert "last_activity" in state

    def test_get_workflow_not_found_error(self, workflow_service):
        """AC: get_workflow returns error if not found."""
        result = workflow_service.get_workflow("nonexistent")
        assert result.get("success") is False or "error" in str(result).lower()

    def test_list_workflows_returns_metadata(self, workflow_service, sample_workflow):
        """AC: list_workflows returns metadata for all active workflows."""
        result = workflow_service.list_workflows()
        assert isinstance(result, list)
        assert len(result) >= 1
        entry = result[0]
        assert "name" in entry
        assert "created" in entry
        assert "current_stage" in entry

    def test_list_workflows_empty(self, workflow_service):
        """AC: Empty list returns [], not error."""
        result = workflow_service.list_workflows()
        assert result == []

    def test_delete_workflow_removes_file(self, workflow_service, sample_workflow, workflow_dir):
        """AC: delete_workflow removes the JSON file."""
        filepath = os.path.join(workflow_dir, f"workflow-{sample_workflow}.json")
        assert os.path.exists(filepath)
        workflow_service.delete_workflow(sample_workflow)
        assert not os.path.exists(filepath)

    def test_delete_workflow_not_found_error(self, workflow_service):
        """AC: delete_workflow returns error if not found."""
        result = workflow_service.delete_workflow("nonexistent")
        assert result["success"] is False


# ==============================================================================
# Unit Tests: WorkflowManagerService — Name Validation
# ==============================================================================

class TestWorkflowNameValidation:
    """Tests for workflow name sanitization rules."""

    def test_reject_special_characters(self, workflow_service):
        """AC: Names with special characters rejected."""
        result = workflow_service.create_workflow("bad name!")
        assert result["success"] is False

    def test_reject_spaces(self, workflow_service):
        """AC: Names with spaces rejected."""
        result = workflow_service.create_workflow("has spaces")
        assert result["success"] is False

    def test_reject_over_100_chars(self, workflow_service):
        """AC: Names over 100 chars rejected."""
        result = workflow_service.create_workflow("a" * 101)
        assert result["success"] is False

    def test_accept_alphanumeric_hyphens(self, workflow_service):
        """AC: Alphanumeric + hyphens accepted."""
        result = workflow_service.create_workflow("valid-name-123")
        assert result.get("success") is not False

    def test_accept_max_100_chars(self, workflow_service):
        """AC: Exactly 100 chars accepted."""
        result = workflow_service.create_workflow("a" * 100)
        assert result.get("success") is not False


# ==============================================================================
# Unit Tests: WorkflowManagerService — Stage Gating
# ==============================================================================

class TestStageGating:
    """Tests for stage gating logic."""

    def test_complete_mandatory_ideation_unlocks_requirement(self, workflow_service, sample_workflow):
        """AC: All mandatory ideation actions done → requirement unlocks."""
        workflow_service.update_action_status(sample_workflow, "compose_idea", "done")
        workflow_service.update_action_status(sample_workflow, "refine_idea", "done")
        state = workflow_service.get_workflow(sample_workflow)
        assert state["shared"]["requirement"]["status"] != "locked"

    def test_optional_actions_dont_block(self, workflow_service, sample_workflow):
        """AC: Optional actions (skipped/pending) do not block stage progression."""
        workflow_service.update_action_status(sample_workflow, "compose_idea", "done")
        workflow_service.update_action_status(sample_workflow, "refine_idea", "done")
        # reference_uiux and design_mockup are optional — left as pending
        state = workflow_service.get_workflow(sample_workflow)
        assert state["shared"]["requirement"]["status"] != "locked"

    def test_partial_mandatory_keeps_locked(self, workflow_service, sample_workflow):
        """AC: Not all mandatory done → next stage stays locked."""
        workflow_service.update_action_status(sample_workflow, "compose_idea", "done")
        # refine_idea still pending
        state = workflow_service.get_workflow(sample_workflow)
        assert state["shared"]["requirement"]["status"] == "locked"

    def test_locked_stage_action_rejected(self, workflow_service, sample_workflow):
        """AC: Update action on locked stage rejected."""
        result = workflow_service.update_action_status(
            sample_workflow, "requirement_gathering", "done"
        )
        assert result["success"] is False

    def test_per_feature_gating_independent(self, workflow_service, workflow_with_features):
        """AC: Per-feature stages gate independently per feature lane."""
        name = workflow_with_features
        # Complete feature A's implement actions
        workflow_service.update_action_status(name, "feature_refinement", "done", feature_id="FEATURE-040-A")
        workflow_service.update_action_status(name, "technical_design", "done", feature_id="FEATURE-040-A")
        workflow_service.update_action_status(name, "implementation", "done", feature_id="FEATURE-040-A")
        state = workflow_service.get_workflow(name)
        # Feature A should be in validation, Feature B still in implement
        feat_a = next(f for f in state["features"] if f["feature_id"] == "FEATURE-040-A")
        feat_b = next(f for f in state["features"] if f["feature_id"] == "FEATURE-040-B")
        # Verify independent progression
        assert feat_a["implement"]["actions"]["implementation"]["status"] == "done"
        assert feat_b["implement"]["actions"]["feature_refinement"]["status"] == "pending"


# ==============================================================================
# Unit Tests: WorkflowManagerService — Action Status
# ==============================================================================

class TestActionStatus:
    """Tests for action status updates."""

    def test_update_action_to_done(self, workflow_service, sample_workflow):
        """AC: Update action status to 'done'."""
        result = workflow_service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables=["x-ipe-docs/ideas/my-idea/idea.md"]
        )
        state = workflow_service.get_workflow(sample_workflow)
        assert state["shared"]["ideation"]["actions"]["compose_idea"]["status"] == "done"

    def test_update_action_saves_deliverables(self, workflow_service, sample_workflow):
        """AC: Deliverables list saved in action."""
        deliverables = ["file1.md", "file2.html"]
        workflow_service.update_action_status(
            sample_workflow, "compose_idea", "done", deliverables=deliverables
        )
        state = workflow_service.get_workflow(sample_workflow)
        assert state["shared"]["ideation"]["actions"]["compose_idea"]["deliverables"] == deliverables

    def test_update_action_preserves_deliverables_when_not_provided(self, workflow_service, sample_workflow):
        """AC: Updating action status without deliverables preserves existing ones."""
        original = ["file1.md", "folder/"]
        workflow_service.update_action_status(
            sample_workflow, "compose_idea", "done", deliverables=original
        )
        # Update status again WITHOUT deliverables
        workflow_service.update_action_status(
            sample_workflow, "compose_idea", "pending"
        )
        state = workflow_service.get_workflow(sample_workflow)
        assert state["shared"]["ideation"]["actions"]["compose_idea"]["deliverables"] == original

    def test_update_action_invalid_status_rejected(self, workflow_service, sample_workflow):
        """AC: Invalid status rejected."""
        result = workflow_service.update_action_status(
            sample_workflow, "compose_idea", "invalid_status"
        )
        assert result["success"] is False

    def test_update_last_activity_on_write(self, workflow_service, sample_workflow):
        """AC: last_activity timestamp updated on every write."""
        state_before = workflow_service.get_workflow(sample_workflow)
        workflow_service.update_action_status(sample_workflow, "compose_idea", "done")
        state_after = workflow_service.get_workflow(sample_workflow)
        assert state_after["last_activity"] >= state_before["last_activity"]

    def test_update_feature_action(self, workflow_service, workflow_with_features):
        """AC: When feature_id provided, updates feature-level action."""
        name = workflow_with_features
        result = workflow_service.update_action_status(
            name, "feature_refinement", "done", feature_id="FEATURE-040-A"
        )
        state = workflow_service.get_workflow(name)
        feat = next(f for f in state["features"] if f["feature_id"] == "FEATURE-040-A")
        assert feat["implement"]["actions"]["feature_refinement"]["status"] == "done"

    def test_update_feature_action_nonexistent_feature(self, workflow_service, workflow_with_features):
        """AC: Feature not in workflow → error."""
        result = workflow_service.update_action_status(
            workflow_with_features, "feature_refinement", "done", feature_id="FEATURE-999"
        )
        assert result["success"] is False


# ==============================================================================
# Unit Tests: WorkflowManagerService — Dependency Evaluation
# ==============================================================================

class TestDependencyEvaluation:
    """Tests for feature dependency checking."""

    def test_no_dependencies_not_blocked(self, workflow_service, workflow_with_features):
        """AC: Feature with no deps → {blocked: false, blockers: []}."""
        result = workflow_service.check_dependencies(workflow_with_features, "FEATURE-040-A")
        assert result["blocked"] is False
        assert result["blockers"] == []

    def test_unfinished_dependency_blocked(self, workflow_service, workflow_with_features):
        """AC: Unfinished dependency → {blocked: true, blockers: [...]}."""
        result = workflow_service.check_dependencies(workflow_with_features, "FEATURE-040-B")
        assert result["blocked"] is True
        assert len(result["blockers"]) > 0
        assert result["blockers"][0]["feature_id"] == "FEATURE-040-A"

    def test_finished_dependency_unblocked(self, workflow_service, workflow_with_features):
        """AC: Finished dependency → not blocked."""
        name = workflow_with_features
        # Complete Feature A through implement
        workflow_service.update_action_status(name, "feature_refinement", "done", feature_id="FEATURE-040-A")
        workflow_service.update_action_status(name, "technical_design", "done", feature_id="FEATURE-040-A")
        workflow_service.update_action_status(name, "implementation", "done", feature_id="FEATURE-040-A")
        result = workflow_service.check_dependencies(name, "FEATURE-040-B")
        assert result["blocked"] is False

    def test_independent_features_not_blocked(self, workflow_service, workflow_with_features):
        """AC: Independent features (no deps) → not blocked."""
        result = workflow_service.check_dependencies(workflow_with_features, "FEATURE-040-C")
        assert result["blocked"] is False


# ==============================================================================
# Unit Tests: WorkflowManagerService — Feature Lane Management
# ==============================================================================

class TestFeatureLanes:
    """Tests for feature lane population."""

    def test_add_features_creates_entries(self, workflow_service, sample_workflow):
        """AC: add_features populates per-feature structures."""
        # Must complete shared stages first
        workflow_service.update_action_status(sample_workflow, "compose_idea", "done")
        workflow_service.update_action_status(sample_workflow, "refine_idea", "done")
        workflow_service.update_action_status(sample_workflow, "requirement_gathering", "done")
        workflow_service.update_action_status(sample_workflow, "feature_breakdown", "done")
        features = [{"id": "FEATURE-040-A", "name": "Test Feature", "depends_on": []}]
        workflow_service.add_features(sample_workflow, features)
        state = workflow_service.get_workflow(sample_workflow)
        feat = next((f for f in state["features"] if f["feature_id"] == "FEATURE-040-A"), None)
        assert feat is not None
        assert "implement" in feat
        assert "validation" in feat
        assert "feedback" in feat

    def test_add_features_with_dependencies(self, workflow_service, sample_workflow):
        """AC: Feature entries include depends_on arrays."""
        workflow_service.update_action_status(sample_workflow, "compose_idea", "done")
        workflow_service.update_action_status(sample_workflow, "refine_idea", "done")
        workflow_service.update_action_status(sample_workflow, "requirement_gathering", "done")
        workflow_service.update_action_status(sample_workflow, "feature_breakdown", "done")
        features = [
            {"id": "FEATURE-040-A", "name": "Base", "depends_on": []},
            {"id": "FEATURE-040-B", "name": "Consumer", "depends_on": ["FEATURE-040-A"]},
        ]
        workflow_service.add_features(sample_workflow, features)
        state = workflow_service.get_workflow(sample_workflow)
        feat_b = next(f for f in state["features"] if f["feature_id"] == "FEATURE-040-B")
        assert feat_b["depends_on"] == ["FEATURE-040-A"]

    def test_add_features_actions_initially_pending(self, workflow_service, sample_workflow):
        """AC: All per-stage actions initially 'pending'."""
        workflow_service.update_action_status(sample_workflow, "compose_idea", "done")
        workflow_service.update_action_status(sample_workflow, "refine_idea", "done")
        workflow_service.update_action_status(sample_workflow, "requirement_gathering", "done")
        workflow_service.update_action_status(sample_workflow, "feature_breakdown", "done")
        features = [{"id": "FEATURE-040-A", "name": "Test", "depends_on": []}]
        workflow_service.add_features(sample_workflow, features)
        state = workflow_service.get_workflow(sample_workflow)
        feat = next(f for f in state["features"] if f["feature_id"] == "FEATURE-040-A")
        for stage_name in ("implement", "validation", "feedback"):
            for action_name, action_data in feat[stage_name]["actions"].items():
                assert action_data["status"] in ("pending", "skipped")


# ==============================================================================
# Unit Tests: WorkflowManagerService — Idea Folder Linking
# ==============================================================================

class TestIdeaFolderLinking:
    """Tests for idea folder linking."""

    def test_link_idea_folder_updates_field(self, workflow_service, sample_workflow, temp_project_dir):
        """AC: link_idea_folder sets idea_folder field."""
        idea_path = os.path.join(temp_project_dir, "x-ipe-docs", "ideas", "test-idea")
        os.makedirs(idea_path, exist_ok=True)
        workflow_service.link_idea_folder(sample_workflow, idea_path)
        state = workflow_service.get_workflow(sample_workflow)
        assert state["idea_folder"] == idea_path

    def test_link_idea_folder_nonexistent_path_error(self, workflow_service, sample_workflow):
        """AC: Non-existent path returns error."""
        result = workflow_service.link_idea_folder(sample_workflow, "/nonexistent/path")
        assert result["success"] is False


# ==============================================================================
# Unit Tests: WorkflowManagerService — State Persistence
# ==============================================================================

class TestStatePersistence:
    """Tests for atomic write and state integrity."""

    def test_atomic_write_produces_valid_json(self, workflow_service, sample_workflow, workflow_dir):
        """AC: State writes produce valid JSON."""
        workflow_service.update_action_status(sample_workflow, "compose_idea", "done")
        filepath = os.path.join(workflow_dir, f"workflow-{sample_workflow}.json")
        with open(filepath) as f:
            state = json.load(f)  # Should not raise
        assert state["schema_version"] == "2.0"

    def test_corrupted_json_returns_error(self, workflow_service, sample_workflow, workflow_dir):
        """AC: Corrupted JSON returns descriptive error."""
        filepath = os.path.join(workflow_dir, f"workflow-{sample_workflow}.json")
        with open(filepath, "w") as f:
            f.write("{invalid json!!!")
        result = workflow_service.get_workflow(sample_workflow)
        assert result.get("success") is False or "error" in str(result).lower()


# ==============================================================================
# Unit Tests: WorkflowManagerService — Next Action
# ==============================================================================

class TestNextAction:
    """Tests for next-action suggestion."""

    def test_next_action_initial_state(self, workflow_service, sample_workflow):
        """AC: Initial state suggests first mandatory ideation action."""
        result = workflow_service.get_next_action(sample_workflow)
        assert result["action"] in ("compose_idea", "refine_idea")
        assert result["stage"] == "ideation"

    def test_next_action_after_ideation_complete(self, workflow_service, sample_workflow):
        """AC: After ideation complete, suggests first requirement action."""
        workflow_service.update_action_status(sample_workflow, "compose_idea", "done")
        workflow_service.update_action_status(sample_workflow, "refine_idea", "done")
        result = workflow_service.get_next_action(sample_workflow)
        assert result["stage"] == "requirement"


# ==============================================================================
# API Tests: Flask Workflow Endpoints
# ==============================================================================

class TestWorkflowAPI:
    """API tests for workflow Flask endpoints."""

    def test_create_workflow_endpoint(self, client):
        """POST /api/workflow/create returns 201."""
        response = client.post("/api/workflow/create", json={"name": "api-test"})
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True

    def test_create_workflow_duplicate_409(self, client):
        """POST /api/workflow/create with duplicate returns 409."""
        client.post("/api/workflow/create", json={"name": "dup-test"})
        response = client.post("/api/workflow/create", json={"name": "dup-test"})
        assert response.status_code == 409

    def test_create_workflow_invalid_name_400(self, client):
        """POST /api/workflow/create with invalid name returns 400."""
        response = client.post("/api/workflow/create", json={"name": "bad name!"})
        assert response.status_code == 400

    def test_list_workflows_endpoint(self, client):
        """GET /api/workflow/list returns 200."""
        response = client.get("/api/workflow/list")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data["data"], list)

    def test_get_workflow_endpoint(self, client):
        """GET /api/workflow/{name} returns 200."""
        client.post("/api/workflow/create", json={"name": "get-test"})
        response = client.get("/api/workflow/get-test")
        assert response.status_code == 200

    def test_get_workflow_not_found_404(self, client):
        """GET /api/workflow/{name} returns 404 if not found."""
        response = client.get("/api/workflow/nonexistent")
        assert response.status_code == 404

    def test_delete_workflow_endpoint(self, client):
        """DELETE /api/workflow/{name} returns 200."""
        client.post("/api/workflow/create", json={"name": "del-test"})
        response = client.delete("/api/workflow/del-test")
        assert response.status_code == 200

    def test_update_action_endpoint(self, client):
        """POST /api/workflow/{name}/action returns 200."""
        client.post("/api/workflow/create", json={"name": "action-test"})
        response = client.post("/api/workflow/action-test/action", json={
            "action": "compose_idea",
            "status": "done",
            "deliverables": []
        })
        assert response.status_code == 200

    def test_add_features_endpoint(self, client):
        """POST /api/workflow/{name}/features returns 200."""
        client.post("/api/workflow/create", json={"name": "feat-test"})
        # Complete shared stages first
        client.post("/api/workflow/feat-test/action", json={"action": "compose_idea", "status": "done"})
        client.post("/api/workflow/feat-test/action", json={"action": "refine_idea", "status": "done"})
        client.post("/api/workflow/feat-test/action", json={"action": "requirement_gathering", "status": "done"})
        client.post("/api/workflow/feat-test/action", json={"action": "feature_breakdown", "status": "done"})
        response = client.post("/api/workflow/feat-test/features", json={
            "features": [{"id": "FEATURE-040-A", "name": "Test", "depends_on": []}]
        })
        assert response.status_code == 200

    def test_link_idea_endpoint(self, client, temp_project_dir):
        """POST /api/workflow/{name}/link-idea returns 200."""
        client.post("/api/workflow/create", json={"name": "link-test"})
        idea_path = os.path.join(temp_project_dir, "x-ipe-docs", "ideas", "test-idea")
        os.makedirs(idea_path, exist_ok=True)
        response = client.post("/api/workflow/link-test/link-idea", json={
            "idea_folder": idea_path
        })
        assert response.status_code == 200

    def test_get_dependencies_endpoint(self, client):
        """GET /api/workflow/{name}/dependencies/{feature_id} returns 200."""
        client.post("/api/workflow/create", json={"name": "dep-test"})
        client.post("/api/workflow/dep-test/action", json={"action": "compose_idea", "status": "done"})
        client.post("/api/workflow/dep-test/action", json={"action": "refine_idea", "status": "done"})
        client.post("/api/workflow/dep-test/action", json={"action": "requirement_gathering", "status": "done"})
        client.post("/api/workflow/dep-test/action", json={"action": "feature_breakdown", "status": "done"})
        client.post("/api/workflow/dep-test/features", json={
            "features": [
                {"id": "FEATURE-040-A", "name": "Base", "depends_on": []},
                {"id": "FEATURE-040-B", "name": "Consumer", "depends_on": ["FEATURE-040-A"]}
            ]
        })
        response = client.get("/api/workflow/dep-test/dependencies/FEATURE-040-B")
        assert response.status_code == 200

    def test_next_action_endpoint(self, client):
        """GET /api/workflow/{name}/next-action returns 200."""
        client.post("/api/workflow/create", json={"name": "next-test"})
        response = client.get("/api/workflow/next-test/next-action")
        assert response.status_code == 200

    def test_create_workflow_server_error_returns_json(self, client, monkeypatch):
        """POST /api/workflow/create returns JSON 500 even when service throws."""
        from x_ipe.services import workflow_manager_service as wms
        orig_create = wms.WorkflowManagerService.create_workflow
        def boom(self, name):
            raise RuntimeError("disk full")
        monkeypatch.setattr(wms.WorkflowManagerService, "create_workflow", boom)
        response = client.post("/api/workflow/create", json={"name": "err-test"})
        assert response.status_code == 500
        data = response.get_json()
        assert data is not None, "Response must be JSON, not HTML"
        assert data["success"] is False
        assert "error" in data

    def test_list_workflows_server_error_returns_json(self, client, monkeypatch):
        """GET /api/workflow/list returns JSON 500 even when service throws."""
        from x_ipe.services import workflow_manager_service as wms
        def boom(self):
            raise RuntimeError("oops")
        monkeypatch.setattr(wms.WorkflowManagerService, "list_workflows", boom)
        response = client.get("/api/workflow/list")
        assert response.status_code == 500
        data = response.get_json()
        assert data is not None
        assert data["success"] is False

    def test_delete_workflow_server_error_returns_json(self, client, monkeypatch):
        """DELETE /api/workflow/{name} returns JSON 500 even when service throws."""
        from x_ipe.services import workflow_manager_service as wms
        def boom(self, name):
            raise RuntimeError("oops")
        monkeypatch.setattr(wms.WorkflowManagerService, "delete_workflow", boom)
        response = client.delete("/api/workflow/err-test")
        assert response.status_code == 500
        data = response.get_json()
        assert data is not None
        assert data["success"] is False


# ==============================================================================
# Tracing Tests
# ==============================================================================

class TestWorkflowTracing:
    """Verify tracing decorators are applied to public methods."""

    def test_service_methods_have_tracing(self):
        """All public methods of WorkflowManagerService should have @x_ipe_tracing."""
        from x_ipe.services.workflow_manager_service import WorkflowManagerService
        public_methods = [m for m in dir(WorkflowManagerService) if not m.startswith("_") and callable(getattr(WorkflowManagerService, m))]
        for method_name in public_methods:
            method = getattr(WorkflowManagerService, method_name)
            # Check if method has tracing wrapper (has __wrapped__ attribute or tracing metadata)
            assert hasattr(method, "__wrapped__") or hasattr(method, "_x_ipe_traced"), \
                f"Method {method_name} missing @x_ipe_tracing decorator"
