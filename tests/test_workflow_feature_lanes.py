"""
Tests for FEATURE-036-D: Feature Lanes & Dependencies

Tests cover:
- Feature lane module methods existence
- Feature lane CSS classes
- Dependency badge/tag CSS
- SVG overlay CSS
- Feature selector CSS
- Dependencies toggle CSS
- API integration: add features, check dependencies
- Feature lane rendering conditions (has features vs no features)

Note: Frontend JS behavior (DOM rendering, SVG arrows, dropdown interaction)
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

class TestFeatureLaneModuleMethods:
    """Verify workflow-stage.js has feature lane methods."""

    def test_has_feature_lanes_renderer(self):
        """Module has _renderFeatureLanes method."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_renderFeatureLanes" in content

    def test_has_lane_renderer(self):
        """Module has _renderLane method."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_renderLane" in content

    def test_has_dep_arrows(self):
        """Module has _drawDepArrows method."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_drawDepArrows" in content

    def test_has_feature_selector(self):
        """Module has _renderFeatureSelector method."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_renderFeatureSelector" in content

    def test_has_dep_badge_renderer(self):
        """Module has _renderDepBadge method."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_renderDepBadge" in content

    def test_has_feature_check(self):
        """Module has _hasFeatures method to detect features in stages."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_hasFeatures" in content

    def test_has_toggle_deps(self):
        """Module has _toggleDeps method."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_toggleDeps" in content

    def test_has_feature_lane_actions(self):
        """Module defines FEATURE_LANE_ACTIONS constant."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "FEATURE_LANE_ACTIONS" in content


# ─────────────────────────────────────────────
# CSS Tests — Feature Lanes
# ─────────────────────────────────────────────

class TestFeatureLaneCSS:
    """Verify CSS has required classes for feature lanes."""

    def test_css_has_lanes_container(self):
        """CSS defines .lanes-container class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".lanes-container" in content

    def test_css_has_feature_lane(self):
        """CSS defines .feature-lane class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".feature-lane" in content

    def test_css_has_lane_highlighted(self):
        """CSS defines .feature-lane.highlighted class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".feature-lane.highlighted" in content

    def test_css_has_lane_label(self):
        """CSS defines .lane-label class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".lane-label" in content

    def test_css_has_lane_stages(self):
        """CSS defines .lane-stages class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".lane-stages" in content

    def test_css_has_lane_stage_states(self):
        """CSS defines lane stage states (done, active, pending)."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        for state in [".lane-stage.done", ".lane-stage.active", ".lane-stage.pending"]:
            assert state in content, f"CSS class '{state}' must exist"


class TestDependencyCSSClasses:
    """Verify CSS has required classes for dependency visualization."""

    def test_css_has_dep_tag_depends(self):
        """CSS defines .dep-tag.depends class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".dep-tag.depends" in content

    def test_css_has_dep_tag_parallel(self):
        """CSS defines .dep-tag.parallel class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".dep-tag.parallel" in content

    def test_css_has_dep_svg_overlay(self):
        """CSS defines .dep-svg-overlay class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".dep-svg-overlay" in content

    def test_css_has_dep_arrow_line(self):
        """CSS defines .dep-arrow-line class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".dep-arrow-line" in content

    def test_css_has_dep_arrow_head(self):
        """CSS defines .dep-arrow-head class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".dep-arrow-head" in content

    def test_css_has_dep_toggle(self):
        """CSS defines .dep-toggle class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".dep-toggle" in content

    def test_css_has_deps_hidden_rules(self):
        """CSS defines deps-hidden rules that hide SVG and tags."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert "deps-hidden" in content


class TestFeatureSelectorCSS:
    """Verify CSS has required classes for feature selector dropdown."""

    def test_css_has_feature_selector_btn(self):
        """CSS defines .feature-selector-btn class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".feature-selector-btn" in content

    def test_css_has_feature_selector_dropdown(self):
        """CSS defines .feature-selector-dropdown class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".feature-selector-dropdown" in content

    def test_css_has_feature_selector_item(self):
        """CSS defines .feature-selector-item class."""
        css_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "css" / "workflow.css"
        content = css_path.read_text(encoding="utf-8")
        assert ".feature-selector-item" in content


# ─────────────────────────────────────────────
# API Integration Tests — Features & Dependencies
# ─────────────────────────────────────────────

class TestFeatureAPIIntegration:
    """Test feature management and dependency checking API endpoints."""

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

    @pytest.fixture
    def workflow_with_features(self, client):
        """Create a workflow and advance to implement stage with features."""
        client.post("/api/workflow/create", json={"name": "feat-test"})
        # Complete ideation mandatory actions
        client.post("/api/workflow/feat-test/action", json={"action": "compose_idea", "status": "done"})
        client.post("/api/workflow/feat-test/action", json={"action": "refine_idea", "status": "done"})
        # Complete requirement mandatory actions
        client.post("/api/workflow/feat-test/action", json={"action": "requirement_gathering", "status": "done"})
        client.post("/api/workflow/feat-test/action", json={"action": "feature_breakdown", "status": "done"})
        # Add features
        client.post("/api/workflow/feat-test/features", json={
            "features": [
                {"id": "FEATURE-040", "name": "Login Page", "depends_on": []},
                {"id": "FEATURE-041", "name": "Dashboard", "depends_on": ["FEATURE-040"]},
                {"id": "FEATURE-042", "name": "Settings", "depends_on": []},
            ]
        })
        return "feat-test"

    def test_add_features_success(self, client):
        """POST /api/workflow/{name}/features adds features to workflow."""
        client.post("/api/workflow/create", json={"name": "add-feat"})
        # Advance to implement stage
        client.post("/api/workflow/add-feat/action", json={"action": "compose_idea", "status": "done"})
        client.post("/api/workflow/add-feat/action", json={"action": "refine_idea", "status": "done"})
        client.post("/api/workflow/add-feat/action", json={"action": "requirement_gathering", "status": "done"})
        client.post("/api/workflow/add-feat/action", json={"action": "feature_breakdown", "status": "done"})
        resp = client.post("/api/workflow/add-feat/features", json={
            "features": [
                {"id": "FEATURE-100", "name": "Test Feature", "depends_on": []}
            ]
        })
        assert resp.status_code == 200

    def test_features_appear_in_state(self, client, workflow_with_features):
        """Features added via API appear in workflow state."""
        resp = client.get("/api/workflow/feat-test")
        data = resp.get_json()["data"]
        implement = data["stages"].get("implement", {})
        features = implement.get("features", {})
        assert "FEATURE-040" in features
        assert features["FEATURE-040"]["name"] == "Login Page"

    def test_feature_has_depends_on(self, client, workflow_with_features):
        """Feature dependency data is preserved in state."""
        resp = client.get("/api/workflow/feat-test")
        data = resp.get_json()["data"]
        features = data["stages"]["implement"]["features"]
        assert features["FEATURE-041"]["depends_on"] == ["FEATURE-040"]
        assert features["FEATURE-040"]["depends_on"] == []

    def test_dependency_check_blocked(self, client, workflow_with_features):
        """GET /api/workflow/{name}/dependencies/{id} returns blocked status for dependent feature."""
        resp = client.get("/api/workflow/feat-test/dependencies/FEATURE-041")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["blocked"] is True
        assert len(data["blockers"]) > 0

    def test_dependency_check_not_blocked(self, client, workflow_with_features):
        """GET /api/workflow/{name}/dependencies/{id} returns not blocked for independent feature."""
        resp = client.get("/api/workflow/feat-test/dependencies/FEATURE-040")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["blocked"] is False

    def test_feature_action_update(self, client, workflow_with_features):
        """POST /api/workflow/{name}/action with feature_id updates per-feature action."""
        resp = client.post("/api/workflow/feat-test/action", json={
            "action": "feature_refinement",
            "status": "done",
            "feature_id": "FEATURE-040"
        })
        assert resp.status_code == 200
        # Verify in state
        state = client.get("/api/workflow/feat-test").get_json()["data"]
        feat = state["stages"]["implement"]["features"]["FEATURE-040"]
        assert feat["actions"]["feature_refinement"]["status"] == "done"

    def test_multiple_independent_features(self, client, workflow_with_features):
        """Independent features can be updated independently."""
        client.post("/api/workflow/feat-test/action", json={
            "action": "feature_refinement", "status": "done", "feature_id": "FEATURE-040"
        })
        client.post("/api/workflow/feat-test/action", json={
            "action": "feature_refinement", "status": "done", "feature_id": "FEATURE-042"
        })
        state = client.get("/api/workflow/feat-test").get_json()["data"]
        feat040 = state["stages"]["implement"]["features"]["FEATURE-040"]
        feat042 = state["stages"]["implement"]["features"]["FEATURE-042"]
        assert feat040["actions"]["feature_refinement"]["status"] == "done"
        assert feat042["actions"]["feature_refinement"]["status"] == "done"

    def test_feature_breakdown_with_inline_features(self, client):
        """feature_breakdown action with features param creates per-feature structures."""
        client.post("/api/workflow/create", json={"name": "inline-feat"})
        client.post("/api/workflow/inline-feat/action", json={"action": "compose_idea", "status": "done"})
        client.post("/api/workflow/inline-feat/action", json={"action": "refine_idea", "status": "done"})
        client.post("/api/workflow/inline-feat/action", json={"action": "requirement_gathering", "status": "done"})
        # Pass features inline with feature_breakdown action
        resp = client.post("/api/workflow/inline-feat/action", json={
            "action": "feature_breakdown",
            "status": "done",
            "deliverables": ["x-ipe-docs/requirements/requirement-details.md"],
            "features": [
                {"id": "FEAT-A", "name": "Auth Module", "depends_on": []},
                {"id": "FEAT-B", "name": "Dashboard", "depends_on": ["FEAT-A"]},
                {"id": "FEAT-C", "name": "Settings", "depends_on": []},
            ]
        })
        assert resp.status_code == 200
        state = client.get("/api/workflow/inline-feat").get_json()["data"]
        # Features should be populated in implement stage
        impl_features = state["stages"]["implement"]["features"]
        assert "FEAT-A" in impl_features
        assert "FEAT-B" in impl_features
        assert "FEAT-C" in impl_features
        assert impl_features["FEAT-B"]["depends_on"] == ["FEAT-A"]

    def test_feature_breakdown_inline_sets_features_created(self, client):
        """feature_breakdown with features param populates features_created field."""
        client.post("/api/workflow/create", json={"name": "fc-test"})
        client.post("/api/workflow/fc-test/action", json={"action": "compose_idea", "status": "done"})
        client.post("/api/workflow/fc-test/action", json={"action": "refine_idea", "status": "done"})
        client.post("/api/workflow/fc-test/action", json={"action": "requirement_gathering", "status": "done"})
        client.post("/api/workflow/fc-test/action", json={
            "action": "feature_breakdown", "status": "done",
            "features": [
                {"id": "FEAT-X", "name": "Feature X", "depends_on": []},
                {"id": "FEAT-Y", "name": "Feature Y", "depends_on": ["FEAT-X"]},
            ]
        })
        state = client.get("/api/workflow/fc-test").get_json()["data"]
        fb = state["stages"]["requirement"]["actions"]["feature_breakdown"]
        assert len(fb["features_created"]) == 2
        assert fb["features_created"][0]["id"] == "FEAT-X"

    def test_feature_breakdown_inline_next_actions_no_deps(self, client):
        """next_actions_suggested contains only feature IDs with no dependencies."""
        client.post("/api/workflow/create", json={"name": "na-test"})
        client.post("/api/workflow/na-test/action", json={"action": "compose_idea", "status": "done"})
        client.post("/api/workflow/na-test/action", json={"action": "refine_idea", "status": "done"})
        client.post("/api/workflow/na-test/action", json={"action": "requirement_gathering", "status": "done"})
        client.post("/api/workflow/na-test/action", json={
            "action": "feature_breakdown", "status": "done",
            "features": [
                {"id": "FEAT-1", "name": "Base", "depends_on": []},
                {"id": "FEAT-2", "name": "Dependent", "depends_on": ["FEAT-1"]},
                {"id": "FEAT-3", "name": "Independent", "depends_on": []},
            ]
        })
        state = client.get("/api/workflow/na-test").get_json()["data"]
        fb = state["stages"]["requirement"]["actions"]["feature_breakdown"]
        suggested = fb["next_actions_suggested"]
        assert "FEAT-1" in suggested
        assert "FEAT-3" in suggested
        assert "FEAT-2" not in suggested


# ─────────────────────────────────────────────
# JS Integration — Feature Lanes Branching
# ─────────────────────────────────────────────

class TestFeatureLaneBranching:
    """Verify workflow-stage.js branches between global actions and feature lanes."""

    def test_render_has_feature_check_branching(self):
        """render() method checks for features before deciding rendering path."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "_hasFeatures" in content
        assert "_renderFeatureLanes" in content
        assert "_renderActionsArea" in content

    def test_dependency_check_api_call(self):
        """Module calls dependency check API before dispatching feature actions."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "/dependencies/" in content

    def test_uses_custom_modal_not_native(self):
        """Module uses custom modal for dependency confirmation, not native confirm()."""
        js_path = Path(__file__).parent.parent / "src" / "x_ipe" / "static" / "js" / "features" / "workflow-stage.js"
        content = js_path.read_text(encoding="utf-8")
        assert "workflow-modal" in content
        # Must NOT use native confirm()
        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue
            if 'confirm(' in stripped and 'Confirm' not in stripped and '_showConfirm' not in stripped:
                # Allow references to showConfirmModal but not native confirm()
                if 'window.confirm' in stripped or stripped.startswith('confirm('):
                    pytest.fail("Must not use native confirm() — use custom modal instead")
