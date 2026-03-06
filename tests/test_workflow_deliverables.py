"""
Tests for FEATURE-036-E: Deliverables, Polling & Lifecycle

Tests cover:
- Backend: resolve_deliverables() method
- Backend: archive_stale_workflows() method
- API: GET /api/workflow/{name}/deliverables endpoint
- Frontend JS: deliverables rendering methods exist in workflow-stage.js
- Frontend JS: polling methods exist in workflow.js
- Frontend JS: context menu method exists in workflow-stage.js
- CSS: deliverables section classes
- CSS: context menu classes

Note: Frontend JS behavior (DOM rendering, polling timing, context menu UX)
      is validated via acceptance tests (browser-based).
      These tests focus on backend/template/structure aspects.
"""
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

@pytest.fixture
def project_root(tmp_path):
    """Create a temp project root with workflow dir."""
    wf_dir = tmp_path / "x-ipe-docs" / "engineering-workflow"
    wf_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def service(project_root):
    """Create a WorkflowManagerService instance."""
    from x_ipe.services.workflow_manager_service import WorkflowManagerService
    return WorkflowManagerService(str(project_root))


def _create_workflow_with_deliverables(service, project_root, name="test-wf"):
    """Helper to create a workflow with some deliverables."""
    service.create_workflow(name)
    # Update compose_idea with deliverables
    service.update_action_status(
        name, "compose_idea", "done",
        deliverables=["x-ipe-docs/ideas/test/idea-summary-v1.md"]
    )
    # Create the deliverable file so it exists
    idea_path = project_root / "x-ipe-docs" / "ideas" / "test"
    idea_path.mkdir(parents=True, exist_ok=True)
    (idea_path / "idea-summary-v1.md").write_text("# Test Idea")
    return name


# ─────────────────────────────────────────────
# Backend: resolve_deliverables()
# ─────────────────────────────────────────────

class TestResolveDeliverables:
    """Test the resolve_deliverables service method."""

    def test_resolve_returns_deliverables_list(self, service, project_root):
        """resolve_deliverables returns a dict with deliverables array and count."""
        name = _create_workflow_with_deliverables(service, project_root)
        result = service.resolve_deliverables(name)
        assert "deliverables" in result
        assert "count" in result
        assert isinstance(result["deliverables"], list)
        assert result["count"] >= 1

    def test_resolve_includes_category(self, service, project_root):
        """Each deliverable has a category field."""
        name = _create_workflow_with_deliverables(service, project_root)
        result = service.resolve_deliverables(name)
        for d in result["deliverables"]:
            assert "category" in d
            assert d["category"] in ("ideas", "mockups", "requirements", "implementations", "quality")

    def test_resolve_compose_idea_is_ideas_category(self, service, project_root):
        """compose_idea deliverables are categorized as 'ideas'."""
        name = _create_workflow_with_deliverables(service, project_root)
        result = service.resolve_deliverables(name)
        ideas = [d for d in result["deliverables"] if d["category"] == "ideas"]
        assert len(ideas) >= 1

    def test_resolve_checks_file_existence(self, service, project_root):
        """Deliverables include exists=True for real files."""
        name = _create_workflow_with_deliverables(service, project_root)
        result = service.resolve_deliverables(name)
        existing = [d for d in result["deliverables"] if d["exists"]]
        assert len(existing) >= 1

    def test_resolve_missing_file_marked_not_exists(self, service, project_root):
        """Deliverables with missing files have exists=False."""
        name = "missing-test"
        service.create_workflow(name)
        service.update_action_status(
            name, "compose_idea", "done",
            deliverables=["nonexistent/path/file.md"]
        )
        result = service.resolve_deliverables(name)
        missing = [d for d in result["deliverables"] if not d["exists"]]
        assert len(missing) >= 1

    def test_resolve_includes_name_and_path(self, service, project_root):
        """Each deliverable has name and path fields."""
        name = _create_workflow_with_deliverables(service, project_root)
        result = service.resolve_deliverables(name)
        for d in result["deliverables"]:
            assert "name" in d
            assert "path" in d
            assert len(d["name"]) > 0
            assert len(d["path"]) > 0

    def test_resolve_no_deliverables(self, service, project_root):
        """Empty deliverables list when workflow has none."""
        service.create_workflow("empty-wf")
        result = service.resolve_deliverables("empty-wf")
        assert result["deliverables"] == []
        assert result["count"] == 0

    def test_resolve_includes_stage_field(self, service, project_root):
        """Each deliverable includes a 'stage' field indicating which stage it belongs to."""
        name = _create_workflow_with_deliverables(service, project_root)
        result = service.resolve_deliverables(name)
        for d in result["deliverables"]:
            assert "stage" in d
            assert d["stage"] in ("ideation", "requirement", "implement", "validation", "feedback")

    def test_resolve_compose_idea_stage_is_ideation(self, service, project_root):
        """compose_idea deliverables have stage='ideation'."""
        name = _create_workflow_with_deliverables(service, project_root)
        result = service.resolve_deliverables(name)
        ideas = [d for d in result["deliverables"] if d["category"] == "ideas"]
        assert all(d["stage"] == "ideation" for d in ideas)

    def test_resolve_per_feature_deliverable_has_stage_and_feature(self, service, project_root):
        """Per-feature deliverables include correct stage, feature_id, and feature_name."""
        name = "feat-stage"
        service.create_workflow(name)
        service.update_action_status(name, "compose_idea", "done")
        service.update_action_status(name, "refine_idea", "done")
        service.update_action_status(name, "requirement_gathering", "done")
        service.update_action_status(name, "feature_breakdown", "done")
        service.add_features(name, [{"id": "FEATURE-200", "name": "Stage Test", "depends_on": []}])
        service.update_action_status(
            name, "feature_refinement", "done",
            feature_id="FEATURE-200",
            deliverables=["x-ipe-docs/requirements/FEATURE-200/specification.md"]
        )
        result = service.resolve_deliverables(name)
        reqs = [d for d in result["deliverables"] if d["category"] == "requirements"]
        assert len(reqs) >= 1
        assert all(d["stage"] == "implement" for d in reqs)
        assert all(d["feature_id"] == "FEATURE-200" for d in reqs)
        assert all(d["feature_name"] == "Stage Test" for d in reqs)

    def test_resolve_workflow_not_found(self, service):
        """Returns error for nonexistent workflow."""
        result = service.resolve_deliverables("nope")
        assert result.get("success") is False or result.get("error") == "NOT_FOUND"

    def test_resolve_per_feature_deliverables(self, service, project_root):
        """Deliverables from per-feature actions are included."""
        name = "feat-deliv"
        service.create_workflow(name)
        # Progress to implement stage
        service.update_action_status(name, "compose_idea", "done")
        service.update_action_status(name, "refine_idea", "done")
        service.update_action_status(name, "requirement_gathering", "done")
        service.update_action_status(name, "feature_breakdown", "done")
        # Add a feature
        service.add_features(name, [{"id": "FEATURE-100", "name": "Test Feature", "depends_on": []}])
        # Add deliverable to feature action
        service.update_action_status(
            name, "feature_refinement", "done",
            feature_id="FEATURE-100",
            deliverables=["x-ipe-docs/requirements/FEATURE-100/specification.md"]
        )
        result = service.resolve_deliverables(name)
        reqs = [d for d in result["deliverables"] if d["category"] == "requirements"]
        assert len(reqs) >= 1

    def test_resolve_multiple_categories(self, service, project_root):
        """Deliverables from different actions get different categories."""
        name = "multi-cat"
        service.create_workflow(name)
        service.update_action_status(
            name, "compose_idea", "done",
            deliverables=["ideas/file.md"]
        )
        service.update_action_status(
            name, "design_mockup", "done",
            deliverables=["mockups/page.html"]
        )
        result = service.resolve_deliverables(name)
        categories = {d["category"] for d in result["deliverables"]}
        assert "ideas" in categories
        assert "mockups" in categories


# ─────────────────────────────────────────────
# Backend: archive_stale_workflows()
# ─────────────────────────────────────────────

class TestArchiveStaleWorkflows:
    """Test the archive_stale_workflows service method."""

    def test_archive_creates_archive_dir(self, service, project_root):
        """archive_stale_workflows creates archive/ dir if needed."""
        service.archive_stale_workflows()
        archive_dir = project_root / "x-ipe-docs" / "engineering-workflow" / "archive"
        assert archive_dir.exists()

    def test_archive_moves_stale_workflow(self, service, project_root):
        """Workflows inactive for >30 days are moved to archive/."""
        service.create_workflow("old-wf")
        # Manually backdate last_activity
        wf_path = project_root / "x-ipe-docs" / "engineering-workflow" / "workflow-old-wf.json"
        state = json.loads(wf_path.read_text())
        old_time = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
        state["last_activity"] = old_time
        wf_path.write_text(json.dumps(state))

        result = service.archive_stale_workflows()
        assert result["archived_count"] >= 1
        assert not wf_path.exists()
        archive_path = project_root / "x-ipe-docs" / "engineering-workflow" / "archive" / "workflow-old-wf.json"
        assert archive_path.exists()

    def test_archive_keeps_active_workflow(self, service, project_root):
        """Workflows with recent activity are NOT archived."""
        service.create_workflow("active-wf")
        service.archive_stale_workflows()
        wf_path = project_root / "x-ipe-docs" / "engineering-workflow" / "workflow-active-wf.json"
        assert wf_path.exists()

    def test_archive_not_in_list(self, service, project_root):
        """Archived workflows do not appear in list_workflows()."""
        service.create_workflow("to-archive")
        wf_path = project_root / "x-ipe-docs" / "engineering-workflow" / "workflow-to-archive.json"
        state = json.loads(wf_path.read_text())
        old_time = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
        state["last_activity"] = old_time
        wf_path.write_text(json.dumps(state))

        service.archive_stale_workflows()
        workflows = service.list_workflows()
        names = [w["name"] for w in workflows]
        assert "to-archive" not in names


# ─────────────────────────────────────────────
# API: GET /api/workflow/{name}/deliverables
# ─────────────────────────────────────────────

class TestDeliverablesAPIEndpoint:
    """Test the deliverables API route."""

    @pytest.fixture
    def app_client(self, tmp_path):
        """Create a Flask test client with the workflow blueprint."""
        from flask import Flask
        from x_ipe.routes.workflow_routes import workflow_bp
        app = Flask(__name__)
        app.config['PROJECT_ROOT'] = str(tmp_path)
        app.config['TESTING'] = True
        app.register_blueprint(workflow_bp)
        wf_dir = tmp_path / "x-ipe-docs" / "engineering-workflow"
        wf_dir.mkdir(parents=True)
        return app.test_client()

    def test_deliverables_endpoint_exists(self, app_client, tmp_path):
        """GET /api/workflow/{name}/deliverables returns 200 or 404."""
        # Create workflow first
        app_client.post('/api/workflow/create', json={'name': 'api-test'})
        resp = app_client.get('/api/workflow/api-test/deliverables')
        assert resp.status_code == 200

    def test_deliverables_endpoint_returns_json(self, app_client, tmp_path):
        """Response is JSON with success and data fields."""
        app_client.post('/api/workflow/create', json={'name': 'json-test'})
        resp = app_client.get('/api/workflow/json-test/deliverables')
        data = resp.get_json()
        assert data.get('success') is True
        assert 'data' in data
        assert 'deliverables' in data['data']
        assert 'count' in data['data']

    def test_deliverables_endpoint_404_missing(self, app_client):
        """Returns 404 for nonexistent workflow."""
        resp = app_client.get('/api/workflow/nonexistent/deliverables')
        assert resp.status_code == 404


# ─────────────────────────────────────────────
# Frontend JS: workflow-stage.js methods
# ─────────────────────────────────────────────

class TestDeliverablesFrontendMethods:
    """Verify workflow-stage.js has deliverables and context menu methods."""

    def _js_content(self):
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        return js_path.read_text(encoding="utf-8")

    def test_has_render_deliverables(self):
        """Module has _renderDeliverables method."""
        assert "_renderDeliverables" in self._js_content()

    def test_has_render_deliverable_card(self):
        """Module has _renderDeliverableCard method."""
        assert "_renderDeliverableCard" in self._js_content()

    def test_has_render_context_menu(self):
        """Module has _renderContextMenu method."""
        assert "_renderContextMenu" in self._js_content()

    def test_has_deliverable_icons_constant(self):
        """Module defines DELIVERABLE_ICONS constant."""
        assert "DELIVERABLE_ICONS" in self._js_content()


# ─────────────────────────────────────────────
# Frontend JS: workflow.js polling methods
# ─────────────────────────────────────────────

class TestPollingFrontendMethods:
    """Verify workflow.js has polling methods."""

    def _js_content(self):
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow.js"
        return js_path.read_text(encoding="utf-8")

    def test_has_start_polling(self):
        """Module has _startPolling method."""
        assert "_startPolling" in self._js_content()

    def test_has_stop_polling(self):
        """Module has _stopPolling method."""
        assert "_stopPolling" in self._js_content()

    def test_has_polling_intervals_storage(self):
        """Module has _pollingIntervals storage object."""
        assert "_pollingIntervals" in self._js_content()


# ─────────────────────────────────────────────
# CSS: Deliverables section classes
# ─────────────────────────────────────────────

class TestDeliverablesCSSClasses:
    """Verify workflow.css has deliverables CSS classes."""

    def _css_content(self):
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        return css_path.read_text(encoding="utf-8")

    def test_deliverables_area(self):
        assert ".deliverables-area" in self._css_content()

    def test_deliverables_header(self):
        assert ".deliverables-header" in self._css_content()

    def test_deliverables_grid(self):
        assert ".deliverables-grid" in self._css_content()

    def test_deliverable_card(self):
        assert ".deliverable-card" in self._css_content()

    def test_deliverable_icon(self):
        assert ".deliverable-icon" in self._css_content()

    def test_deliverable_icon_ideas(self):
        assert ".deliverable-icon.ideas" in self._css_content()

    def test_deliverable_icon_mockups(self):
        assert ".deliverable-icon.mockups" in self._css_content()

    def test_deliverable_icon_requirements(self):
        assert ".deliverable-icon.requirements" in self._css_content()

    def test_deliverable_icon_implementations(self):
        assert ".deliverable-icon.implementations" in self._css_content()

    def test_deliverable_icon_quality(self):
        assert ".deliverable-icon.quality" in self._css_content()

    def test_deliverable_missing(self):
        assert ".deliverable-card.missing" in self._css_content()

    def test_deliverables_count(self):
        assert ".deliverables-count" in self._css_content()

    def test_deliverables_toggle(self):
        assert ".deliverables-toggle" in self._css_content()

    def test_deliverables_empty(self):
        assert ".deliverables-empty" in self._css_content()


class TestDeliverablesStageSectionCSS:
    """TASK-680 + CR-001: Verify workflow.css has deliverables feature section CSS classes."""

    def _css_content(self):
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        return css_path.read_text(encoding="utf-8")

    def test_deliverables_feature_section(self):
        assert ".deliverables-feature-section" in self._css_content()

    def test_deliverables_feature_section_title(self):
        assert ".deliverables-feature-section-title" in self._css_content()

    def test_deliverables_row(self):
        assert ".deliverables-row" in self._css_content()

    def test_deliverables_feature_section_last_child(self):
        assert ".deliverables-feature-section:last-child" in self._css_content()

    def test_no_old_stage_classes(self):
        css = self._css_content()
        assert ".deliverables-stage-section" not in css
        assert ".deliverables-stage-title" not in css
        assert ".deliverables-feature-group" not in css
        assert ".deliverables-feature-label" not in css


# ─────────────────────────────────────────────
# CSS: Context menu classes
# ─────────────────────────────────────────────

class TestContextMenuCSSClasses:
    """Verify workflow.css has context menu CSS classes."""

    def _css_content(self):
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        return css_path.read_text(encoding="utf-8")

    def test_context_menu(self):
        assert ".wf-context-menu" in self._css_content()

    def test_context_menu_item(self):
        assert ".wf-context-menu-item" in self._css_content()
