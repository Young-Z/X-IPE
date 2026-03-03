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
    """Verify the workflow mode toggle is in the index.html template."""

    def test_index_has_workflow_toggle(self):
        """AC-001: Mode toggle switch appears in top-menu."""
        template_path = Path(__file__).parent.parent / "src" / "x_ipe" / "templates" / "index.html"
        content = template_path.read_text(encoding="utf-8")
        assert 'id="mode-toggle"' in content

    def test_workflow_toggle_has_switch(self):
        """AC-002: Toggle uses role=switch button."""
        template_path = Path(__file__).parent.parent / "src" / "x_ipe" / "templates" / "index.html"
        content = template_path.read_text(encoding="utf-8")
        assert 'id="mode-toggle-btn"' in content

    def test_workflow_button_has_label(self):
        """AC-002: Button has label text 'Workflow'."""
        template_path = Path(__file__).parent.parent / "src" / "x_ipe" / "templates" / "index.html"
        content = template_path.read_text(encoding="utf-8")
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
        """NFR-002: JavaScript module under 20KB unminified."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow.js"
        size_kb = js_path.stat().st_size / 1024
        assert size_kb < 20, f"workflow.js is {size_kb:.1f}KB, must be under 20KB"


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
    """Verify init.js has the workflow mode toggle handler."""

    def test_init_has_workflow_handler(self):
        """init.js registers click handler for mode-toggle-btn."""
        init_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "init.js"
        content = init_path.read_text(encoding="utf-8")
        assert "mode-toggle-btn" in content

    def test_init_calls_workflow_render(self):
        """init.js calls workflow.render() on click."""
        init_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "init.js"
        content = init_path.read_text(encoding="utf-8")
        assert "workflow.render" in content


class TestModeSwitchContentBodyClass:
    """TASK-541: Verify init.js preserves content-body class when switching back from workflow."""

    def test_free_mode_restores_content_body_class(self):
        """Switching to free mode must reset className to 'content-body', not empty string."""
        init_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "init.js"
        content = init_path.read_text(encoding="utf-8")
        # The free-mode branch must NOT clear className to '' — it must restore 'content-body'
        # Find lines that set container.className in the free-mode branch
        import re
        # Match container.className = '' (with optional spaces)
        bad_pattern = re.compile(r"container\.className\s*=\s*['\"]'?['\"]")
        matches = bad_pattern.findall(content)
        assert len(matches) == 0, (
            f"init.js sets container.className to empty string ({len(matches)} occurrences). "
            "This strips the 'content-body' CSS class, breaking flex layout and scrollbars. "
            "Must use container.className = 'content-body' instead."
        )


class TestWorkflowPanelsSpacing:
    """TASK-543: Verify workflow panels have CSS gap for visual spacing."""

    def test_workflow_panels_has_css_rule(self):
        """workflow.css must define .workflow-panels with gap for spacing between panels."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".workflow-panels" in content, \
            "workflow.css must have a .workflow-panels rule (JS uses this class but CSS is missing)"


class TestComposeFolderPreviewPath:
    """TASK-543: Verify folder preview shows full relative path."""

    def test_folder_preview_shows_full_path(self):
        """Folder preview must show x-ipe-docs/ideas/ prefix, not bare wf-???-name."""
        content = (Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "compose-idea-modal.js").read_text()
        assert "x-ipe-docs/ideas/wf-" in content, \
            "Folder preview must show full path like 'x-ipe-docs/ideas/wf-???-name'"


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
