"""
Tests for FEATURE-036-B: Workflow View Shell & CRUD

Tests cover:
- Template content validation (nav button present, script/css tags)
- Workflow.js module file existence and structure
- API endpoint integration (via Flask test client)

Note: Frontend JS behavior (DOM rendering, modal interactions, panel expand/collapse)
      is validated via acceptance tests (browser-based).
      These tests focus on backend/template aspects.
"""
import os
import pytest
from pathlib import Path


class TestWorkflowNavButton:
    """Verify the workflow button is in the index.html template."""

    def test_index_has_workflow_button(self):
        """AC-001: 'Engineering Workflow' button appears in top-menu."""
        template_path = Path(__file__).parent.parent / "src" / "x_ipe" / "templates" / "index.html"
        content = template_path.read_text(encoding="utf-8")
        assert 'id="btn-workflow"' in content

    def test_workflow_button_has_icon(self):
        """AC-002: Button uses Bootstrap icon bi-diagram-3."""
        template_path = Path(__file__).parent.parent / "src" / "x_ipe" / "templates" / "index.html"
        content = template_path.read_text(encoding="utf-8")
        assert "bi-diagram-3" in content

    def test_workflow_button_has_label(self):
        """AC-002: Button has label text 'Workflow'."""
        template_path = Path(__file__).parent.parent / "src" / "x_ipe" / "templates" / "index.html"
        content = template_path.read_text(encoding="utf-8")
        # Should contain the label text
        assert ">Workflow<" in content


class TestWorkflowModuleFiles:
    """Verify frontend module files exist and have expected structure."""

    def test_workflow_js_exists(self):
        """FR-001: workflow.js exists in static/js/features/."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow.js"
        assert js_path.exists(), "workflow.js must exist"

    def test_workflow_js_has_render_function(self):
        """FR-002: Module exposes a render function."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow.js"
        content = js_path.read_text(encoding="utf-8")
        assert "render(" in content or "render:" in content

    def test_workflow_js_calls_api(self):
        """FR-004: Module makes fetch calls to /api/workflow/."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow.js"
        content = js_path.read_text(encoding="utf-8")
        assert "/api/workflow/" in content

    def test_workflow_css_exists(self):
        """Workflow CSS file exists."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        assert css_path.exists(), "workflow.css must exist"

    def test_workflow_js_size_under_limit(self):
        """NFR-002: JavaScript module under 15KB unminified."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow.js"
        size_kb = js_path.stat().st_size / 1024
        assert size_kb < 15, f"workflow.js is {size_kb:.1f}KB, must be under 15KB"


class TestWorkflowScriptInclusion:
    """Verify script/CSS tags are included in template."""

    def test_index_includes_workflow_js(self):
        """workflow.js is included via script tag."""
        # Check index.html or base.html for the script inclusion
        for fname in ("index.html", "base.html"):
            tpl_path = Path(__file__).parent.parent / "src" / "x_ipe" / "templates" / fname
            if tpl_path.exists():
                content = tpl_path.read_text(encoding="utf-8")
                if "workflow.js" in content:
                    return
        pytest.fail("workflow.js not included in any template")

    def test_index_includes_workflow_css(self):
        """workflow.css is included via link tag."""
        for fname in ("index.html", "base.html"):
            tpl_path = Path(__file__).parent.parent / "src" / "x_ipe" / "templates" / fname
            if tpl_path.exists():
                content = tpl_path.read_text(encoding="utf-8")
                if "workflow.css" in content:
                    return
        pytest.fail("workflow.css not included in any template")


class TestWorkflowInitHandler:
    """Verify init.js has the workflow button click handler."""

    def test_init_has_workflow_handler(self):
        """init.js registers click handler for btn-workflow."""
        init_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "init.js"
        content = init_path.read_text(encoding="utf-8")
        assert "btn-workflow" in content

    def test_init_calls_workflow_render(self):
        """init.js calls workflow.render() on click."""
        init_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "init.js"
        content = init_path.read_text(encoding="utf-8")
        assert "workflow.render" in content


class TestWorkflowAPIIntegration:
    """Test API endpoints return expected shapes via Flask test client."""

    @pytest.fixture
    def app(self, tmp_path):
        from x_ipe.app import create_app
        app = create_app({
            'TESTING': True,
            'PROJECT_ROOT': str(tmp_path),
        })
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_workflow_list_returns_json(self, client):
        """AC-006: GET /api/workflow/list returns JSON list."""
        response = client.get("/api/workflow/list")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    def test_create_and_list_workflow(self, client):
        """AC-015: Created workflow appears in list."""
        client.post("/api/workflow/create", json={"name": "test-wf"})
        response = client.get("/api/workflow/list")
        data = response.get_json()
        names = [w["name"] for w in data["data"]]
        assert "test-wf" in names

    def test_create_workflow_returns_stage(self, client):
        """AC-007: Panel header shows current stage."""
        response = client.post("/api/workflow/create", json={"name": "stage-test"})
        data = response.get_json()
        assert data["data"]["current_stage"] == "ideation"

    def test_delete_workflow_removes_from_list(self, client):
        """AC-021: Deleted workflow removed from list."""
        client.post("/api/workflow/create", json={"name": "del-test"})
        client.delete("/api/workflow/del-test")
        response = client.get("/api/workflow/list")
        names = [w["name"] for w in response.get_json()["data"]]
        assert "del-test" not in names

    def test_create_duplicate_returns_409(self, client):
        """AC-016: Duplicate name returns 409."""
        client.post("/api/workflow/create", json={"name": "dup-test"})
        response = client.post("/api/workflow/create", json={"name": "dup-test"})
        assert response.status_code == 409

    def test_create_invalid_name_returns_400(self, client):
        """AC-017: Invalid name returns 400."""
        response = client.post("/api/workflow/create", json={"name": "bad name!"})
        assert response.status_code == 400
