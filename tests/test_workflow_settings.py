"""
Acceptance tests for EPIC-044: Auto-Proceed Process Preference

Covers:
- FEATURE-044-E: global.process_preference in workflow state & PATCH settings API
- FEATURE-044-F: Settings validation (manual|auto|stop_for_question)
- Integration: initial state includes global section, update persists
"""

import json
import os
import tempfile
import shutil

import pytest


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def temp_project_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def workflow_service(temp_project_dir):
    from x_ipe.services.workflow_manager_service import WorkflowManagerService
    return WorkflowManagerService(temp_project_dir)


@pytest.fixture
def sample_workflow(workflow_service):
    result = workflow_service.create_workflow("test-044")
    assert result["success"]
    return "test-044"


@pytest.fixture
def app(temp_project_dir):
    from x_ipe.app import create_app
    app = create_app({"TESTING": True, "PROJECT_ROOT": temp_project_dir})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# ==============================================================================
# Service-level tests: initial state includes global.process_preference
# ==============================================================================

class TestInitialStateProcessPreference:
    """FEATURE-044-E: New workflows include global.process_preference."""

    def test_initial_state_has_global_section(self, workflow_service, sample_workflow):
        state = workflow_service.get_workflow(sample_workflow)
        assert "global" in state

    def test_initial_state_has_process_preference(self, workflow_service, sample_workflow):
        state = workflow_service.get_workflow(sample_workflow)
        pp = state["global"]["process_preference"]
        assert pp["auto_proceed"] == "manual"

    def test_initial_state_default_is_manual(self, workflow_service, sample_workflow):
        state = workflow_service.get_workflow(sample_workflow)
        assert state["global"]["process_preference"]["auto_proceed"] == "manual"


# ==============================================================================
# Service-level tests: update_settings
# ==============================================================================

class TestUpdateSettings:
    """FEATURE-044-E: update_settings service method."""

    def test_update_to_auto(self, workflow_service, sample_workflow):
        result = workflow_service.update_settings(
            sample_workflow, {"process_preference": {"auto_proceed": "auto"}})
        assert result["success"]
        assert result["data"]["process_preference"]["auto_proceed"] == "auto"

    def test_update_to_stop_for_question(self, workflow_service, sample_workflow):
        result = workflow_service.update_settings(
            sample_workflow, {"process_preference": {"auto_proceed": "stop_for_question"}})
        assert result["success"]
        assert result["data"]["process_preference"]["auto_proceed"] == "stop_for_question"

    def test_update_to_manual(self, workflow_service, sample_workflow):
        # First set to auto, then back to manual
        workflow_service.update_settings(
            sample_workflow, {"process_preference": {"auto_proceed": "auto"}})
        result = workflow_service.update_settings(
            sample_workflow, {"process_preference": {"auto_proceed": "manual"}})
        assert result["success"]
        assert result["data"]["process_preference"]["auto_proceed"] == "manual"

    def test_update_persists_to_disk(self, workflow_service, sample_workflow):
        workflow_service.update_settings(
            sample_workflow, {"process_preference": {"auto_proceed": "auto"}})
        state = workflow_service.get_workflow(sample_workflow)
        assert state["global"]["process_preference"]["auto_proceed"] == "auto"

    def test_invalid_mode_rejected(self, workflow_service, sample_workflow):
        result = workflow_service.update_settings(
            sample_workflow, {"process_preference": {"auto_proceed": "turbo"}})
        assert not result["success"]
        assert result["error"] == "INVALID_VALUE"

    def test_update_nonexistent_workflow(self, workflow_service):
        result = workflow_service.update_settings(
            "nonexistent", {"process_preference": {"auto_proceed": "auto"}})
        assert not result["success"]
        assert result["error"] == "NOT_FOUND"

    def test_update_updates_last_activity(self, workflow_service, sample_workflow):
        state_before = workflow_service.get_workflow(sample_workflow)
        workflow_service.update_settings(
            sample_workflow, {"process_preference": {"auto_proceed": "auto"}})
        state_after = workflow_service.get_workflow(sample_workflow)
        assert state_after["last_activity"] >= state_before["last_activity"]


# ==============================================================================
# API-level tests: PATCH /api/workflow/<name>/settings
# ==============================================================================

class TestSettingsEndpoint:
    """FEATURE-044-F: PATCH endpoint for workflow settings."""

    def test_patch_settings_200(self, client):
        client.post("/api/workflow/create", json={"name": "api-test-044"})
        resp = client.patch("/api/workflow/api-test-044/settings",
                            json={"process_preference": {"auto_proceed": "auto"}})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"]
        assert data["data"]["process_preference"]["auto_proceed"] == "auto"

    def test_patch_settings_not_found_404(self, client):
        resp = client.patch("/api/workflow/nonexistent/settings",
                            json={"process_preference": {"auto_proceed": "auto"}})
        assert resp.status_code == 404

    def test_patch_settings_invalid_mode_400(self, client):
        client.post("/api/workflow/create", json={"name": "api-test-044b"})
        resp = client.patch("/api/workflow/api-test-044b/settings",
                            json={"process_preference": {"auto_proceed": "invalid"}})
        assert resp.status_code == 400

    def test_get_workflow_includes_global(self, client):
        client.post("/api/workflow/create", json={"name": "api-test-044c"})
        resp = client.get("/api/workflow/api-test-044c")
        data = resp.get_json()
        # GET wraps state in {"success": true, "data": {...}} or returns state directly
        state = data.get("data", data) if isinstance(data, dict) and "data" in data else data
        assert "global" in state
        assert state["global"]["process_preference"]["auto_proceed"] == "manual"

    def test_roundtrip_toggle(self, client):
        """Simulate UI toggle: create → read default → change to auto → read back."""
        client.post("/api/workflow/create", json={"name": "toggle-test"})

        # Read default
        resp = client.get("/api/workflow/toggle-test")
        state = resp.get_json()
        if "data" in state:
            state = state["data"]
        assert state["global"]["process_preference"]["auto_proceed"] == "manual"

        # Toggle to auto
        resp = client.patch("/api/workflow/toggle-test/settings",
                            json={"process_preference": {"auto_proceed": "auto"}})
        assert resp.status_code == 200

        # Read back
        resp = client.get("/api/workflow/toggle-test")
        state = resp.get_json()
        if "data" in state:
            state = state["data"]
        assert state["global"]["process_preference"]["auto_proceed"] == "auto"

        # Toggle to stop_for_question
        resp = client.patch("/api/workflow/toggle-test/settings",
                            json={"process_preference": {"auto_proceed": "stop_for_question"}})
        assert resp.status_code == 200

        # Read back
        resp = client.get("/api/workflow/toggle-test")
        state = resp.get_json()
        if "data" in state:
            state = state["data"]
        assert state["global"]["process_preference"]["auto_proceed"] == "stop_for_question"


# ==============================================================================
# Template tests: workflow-template.json includes global.process_preference
# ==============================================================================

class TestWorkflowTemplate:
    """FEATURE-044-E: workflow-template.json has global section."""

    def test_docs_template_has_global(self):
        path = os.path.join(os.path.dirname(__file__), "..",
                            "x-ipe-docs", "config", "workflow-template.json")
        with open(path) as f:
            tpl = json.load(f)
        assert "global" in tpl
        assert tpl["global"]["process_preference"]["auto_proceed"] == "manual"

    def test_src_template_has_global(self):
        path = os.path.join(os.path.dirname(__file__), "..",
                            "src", "x_ipe", "resources", "config", "workflow-template.json")
        with open(path) as f:
            tpl = json.load(f)
        assert "global" in tpl
        assert tpl["global"]["process_preference"]["auto_proceed"] == "manual"


# ==============================================================================
# Skill template tests: process_preference replaces old booleans
# ==============================================================================

class TestSkillTemplateUpdate:
    """FEATURE-044-B/C: All task-based skills use process_preference."""

    def _get_skill_files(self):
        skills_dir = os.path.join(os.path.dirname(__file__), "..", ".github", "skills")
        import glob
        return glob.glob(os.path.join(skills_dir, "x-ipe-task-based-*", "SKILL.md"))

    def test_no_skill_has_require_human_review(self):
        for path in self._get_skill_files():
            content = open(path).read()
            assert "require_human_review" not in content, \
                f"{os.path.basename(os.path.dirname(path))} still has require_human_review"

    def test_no_skill_has_auto_proceed_false(self):
        for path in self._get_skill_files():
            content = open(path).read()
            assert "auto_proceed: false" not in content, \
                f"{os.path.basename(os.path.dirname(path))} still has auto_proceed: false"

    def test_all_skills_have_process_preference(self):
        for path in self._get_skill_files():
            content = open(path).read()
            assert "process_preference" in content, \
                f"{os.path.basename(os.path.dirname(path))} missing process_preference"

    def test_skill_count_is_22(self):
        assert len(self._get_skill_files()) == 22


# ==============================================================================
# Orchestrator tests: workflow-task-execution uses 3-mode routing
# ==============================================================================

class TestOrchestratorUpdate:
    """FEATURE-044-D: Workflow orchestrator uses process_preference."""

    def _read_orchestrator(self):
        path = os.path.join(os.path.dirname(__file__), "..", ".github", "skills",
                            "x-ipe-workflow-task-execution", "SKILL.md")
        return open(path).read()

    def test_no_require_human_review(self):
        content = self._read_orchestrator()
        assert "require_human_review" not in content

    def test_has_process_preference(self):
        content = self._read_orchestrator()
        assert "process_preference" in content

    def test_has_3_mode_routing(self):
        content = self._read_orchestrator()
        assert "manual" in content
        assert "auto" in content
        assert "stop_for_question" in content

    def test_references_decision_making_skill(self):
        content = self._read_orchestrator()
        assert "x-ipe-tool-decision-making" in content
