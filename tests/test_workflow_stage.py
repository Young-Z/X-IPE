"""
Tests for FEATURE-036-C: Stage Ribbon & Action Execution

Tests cover:
- Stage ribbon module file existence and structure
- Action-to-skill mapping completeness
- CSS class presence for stage/action states
- Script inclusion in templates
- API endpoints for full workflow state and next-action
- Stage gating logic in API responses

Note: Frontend JS behavior (DOM rendering, action dispatch, console integration)
      is validated via acceptance tests (browser-based).
      These tests focus on backend/template/structure aspects.
"""
import os
import json
import pytest
from pathlib import Path


# ─────────────────────────────────────────────
# Module File Tests
# ─────────────────────────────────────────────

class TestStageModuleFiles:
    """Verify workflow-stage.js file exists and has expected structure."""

    def test_workflow_stage_js_exists(self):
        """workflow-stage.js exists in static/js/features/."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        assert js_path.exists(), "workflow-stage.js must exist"

    def test_workflow_stage_has_render(self):
        """Module exposes a render function."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "render(" in content or "render:" in content

    def test_workflow_stage_has_action_map(self):
        """Module defines ACTION_MAP with all 12 actions."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "ACTION_MAP" in content

    def test_workflow_stage_has_stage_order(self):
        """Module defines STAGE_ORDER array with 5 stages."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "STAGE_ORDER" in content
        for stage in ["ideation", "requirement", "implement", "validation", "feedback"]:
            assert stage in content, f"Stage '{stage}' must be in module"

    def test_workflow_stage_has_ribbon_renderer(self):
        """Module has _renderRibbon method."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_renderRibbon" in content

    def test_workflow_stage_has_actions_renderer(self):
        """Module has _renderActionsArea method."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_renderActionsArea" in content or "_renderActionGroup" in content

    def test_workflow_stage_has_dispatch_cli(self):
        """Module has CLI action dispatch method."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_dispatchCliAction" in content or "dispatchCli" in content

    def test_workflow_stage_has_dispatch_modal(self):
        """Module has modal action dispatch method."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_dispatchModalAction" in content or "dispatchModal" in content


class TestActionMapping:
    """Verify the action-to-skill mapping covers all 12 required actions (AC-013)."""

    def test_all_skills_referenced(self):
        """All skill names from the mapping table appear in the module."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        required_skills = [
            "x-ipe-tool-uiux-reference",
            "x-ipe-task-based-ideation-v2",
            "x-ipe-task-based-idea-mockup",
            "x-ipe-task-based-requirement-gathering",
            "x-ipe-task-based-feature-breakdown",
            "x-ipe-task-based-feature-refinement",
            "x-ipe-task-based-technical-design",
            "x-ipe-task-based-code-implementation",
            "x-ipe-task-based-feature-acceptance-test",
            "x-ipe-task-based-change-request",
        ]
        for skill in required_skills:
            assert skill in content, f"Skill '{skill}' must be in ACTION_MAP"

    def test_all_action_icons_present(self):
        """All emoji icons from the mapping table appear in the module."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        icons = ["📝", "🎨", "💡", "🖼", "📋", "🔀", "📐", "💻", "🔄"]
        for icon in icons:
            assert icon in content, f"Icon '{icon}' must be in ACTION_MAP"

    def test_compose_idea_is_modal_interaction(self):
        """Compose/Upload Idea action uses 'modal' interaction type."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        # The compose_idea action should have interaction: 'modal'
        assert "compose_idea" in content
        assert "'modal'" in content or '"modal"' in content


# ─────────────────────────────────────────────
# CSS Tests
# ─────────────────────────────────────────────

class TestStageCSSClasses:
    """Verify CSS has required classes for stage ribbon and action buttons."""

    def test_css_has_stage_ribbon(self):
        """CSS defines .stage-ribbon class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".stage-ribbon" in content

    def test_css_has_stage_states(self):
        """CSS defines stage visual states (AC-003)."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        for state in [".stage-item.completed", ".stage-item.active", ".stage-item.pending"]:
            assert state in content, f"CSS class '{state}' must exist"

    def test_css_has_action_button_states(self):
        """CSS defines action button states (AC-010)."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        for state in [".action-btn.done", ".action-btn.suggested", ".action-btn.normal", ".action-btn.locked"]:
            assert state in content, f"CSS class '{state}' must exist"

    def test_css_has_pulse_animation(self):
        """CSS defines pulse-dot animation for active stage (UIR-002)."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert "pulse-dot" in content

    def test_css_has_glow_animation(self):
        """CSS defines gentle-glow animation for suggested action (UIR-003)."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert "gentle-glow" in content

    def test_css_has_actions_area(self):
        """CSS defines .actions-area and .actions-grid classes."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".actions-area" in content
        assert ".actions-grid" in content


# ─────────────────────────────────────────────
# Template Inclusion Tests
# ─────────────────────────────────────────────

class TestStageScriptInclusion:
    """Verify workflow-stage.js is included in templates."""

    def test_template_includes_stage_js(self):
        """workflow-stage.js is included via script tag."""
        for fname in ("index.html", "base.html"):
            tpl_path = Path(__file__).parent.parent / "src" / "x_ipe" / "templates" / fname
            if tpl_path.exists():
                content = tpl_path.read_text(encoding="utf-8")
                if "workflow-stage.js" in content:
                    return
        pytest.fail("workflow-stage.js not included in any template")


# ─────────────────────────────────────────────
# API Integration Tests
# ─────────────────────────────────────────────

class TestWorkflowStateAPI:
    """Test full workflow state API returns stage/action details."""

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

    def test_get_workflow_returns_stages(self, client):
        """AC-004: GET /api/workflow/{name} returns stage details."""
        client.post("/api/workflow/create", json={"name": "state-test"})
        response = client.get("/api/workflow/state-test")
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert "stages" in data
        assert "ideation" in data["stages"]

    def test_workflow_stages_have_status(self, client):
        """AC-004: Each stage has a status field."""
        client.post("/api/workflow/create", json={"name": "status-test"})
        data = client.get("/api/workflow/status-test").get_json()["data"]
        for stage_name, stage_data in data["stages"].items():
            assert "status" in stage_data, f"Stage '{stage_name}' must have status field"

    def test_ideation_stage_active_on_create(self, client):
        """New workflow has ideation stage as in_progress."""
        client.post("/api/workflow/create", json={"name": "active-test"})
        data = client.get("/api/workflow/active-test").get_json()["data"]
        assert data["stages"]["ideation"]["status"] == "in_progress"

    def test_other_stages_locked_on_create(self, client):
        """New workflow has requirement/implement/validation/feedback stages locked."""
        client.post("/api/workflow/create", json={"name": "locked-test"})
        data = client.get("/api/workflow/locked-test").get_json()["data"]
        for stage in ["requirement", "implement", "validation", "feedback"]:
            assert data["stages"][stage]["status"] == "locked", f"Stage '{stage}' should be locked"

    def test_ideation_has_action_statuses(self, client):
        """AC-004: Ideation stage has action statuses."""
        client.post("/api/workflow/create", json={"name": "actions-test"})
        data = client.get("/api/workflow/actions-test").get_json()["data"]
        ideation = data["stages"]["ideation"]
        assert "actions" in ideation
        assert "compose_idea" in ideation["actions"]

    def test_next_action_endpoint(self, client):
        """AC-012: GET /api/workflow/{name}/next-action returns recommendation."""
        client.post("/api/workflow/create", json={"name": "next-test"})
        response = client.get("/api/workflow/next-test/next-action")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data

    def test_action_update_changes_status(self, client):
        """Action status update is reflected in workflow state."""
        client.post("/api/workflow/create", json={"name": "update-test"})
        client.post("/api/workflow/update-test/action", json={
            "action": "compose_idea",
            "status": "done"
        })
        data = client.get("/api/workflow/update-test").get_json()["data"]
        assert data["stages"]["ideation"]["actions"]["compose_idea"]["status"] == "done"


# ─────────────────────────────────────────────
# Workflow.js Integration Tests
# ─────────────────────────────────────────────

class TestWorkflowJSIntegration:
    """Verify workflow.js integrates with workflow-stage.js."""

    def test_workflow_js_fetches_full_state(self):
        """workflow.js fetches full workflow state for expanded panels."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow.js"
        content = js_path.read_text(encoding="utf-8")
        # Should have a call to GET /api/workflow/{name} (not just /list)
        assert "/api/workflow/" in content

    def test_workflow_js_references_stage_module(self):
        """workflow.js calls workflowStage.render or similar."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow.js"
        content = js_path.read_text(encoding="utf-8")
        assert "workflowStage" in content, "workflow.js must reference workflowStage module"
