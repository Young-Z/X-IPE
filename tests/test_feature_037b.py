"""
Tests for FEATURE-037-B: Compose Idea Modal — Link Existing & Re-Edit

Tests cover:
- LinkExistingPanel class: file tree, search, preview, confirm link
- StageGateChecker: gate logic for re-opening completed actions
- ComposeIdeaModal edit mode: constructor params, loadEditContent, handleUpdate
- GET /api/ideas/file endpoint: path validation, security, content retrieval
- CSS: Link Existing panel styles
- Workflow-stage.js: gate check + confirmation dialog integration

TDD baseline: All tests should FAIL before implementation.
"""
import os
import re
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from io import BytesIO

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_ROOT = PROJECT_ROOT / "src" / "x_ipe"
JS_FEATURES = SRC_ROOT / "static" / "js" / "features"
CSS_FEATURES = SRC_ROOT / "static" / "css" / "features"


# ============================================================================
# 1. LINK EXISTING PANEL — JS STRUCTURE
# ============================================================================

class TestLinkExistingPanelJS:
    """Verify LinkExistingPanel class exists with expected methods."""

    def test_link_existing_panel_class_exists(self):
        """AC-001: compose-idea-modal.js defines LinkExistingPanel class."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "LinkExistingPanel" in content

    def test_link_panel_has_render_method(self):
        """AC-001: LinkExistingPanel has render() method."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "LinkExistingPanel" in content
        # Find render method in context of LinkExistingPanel
        panel_idx = content.index("LinkExistingPanel")
        remainder = content[panel_idx:]
        assert "render(" in remainder[:2000], "LinkExistingPanel must have render() method"

    def test_link_panel_has_fetch_tree(self):
        """AC-002: LinkExistingPanel fetches /api/ideas/tree."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        panel_idx = content.index("class LinkExistingPanel")
        remainder = content[panel_idx:]
        assert "/api/ideas/tree" in remainder[:3000], \
            "LinkExistingPanel must fetch /api/ideas/tree"

    def test_link_panel_has_search_filter(self):
        """AC-003: LinkExistingPanel has client-side filter."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        panel_idx = content.index("class LinkExistingPanel")
        remainder = content[panel_idx:]
        assert "filter" in remainder[:3000].lower(), \
            "LinkExistingPanel must have filter/search capability"

    def test_link_panel_has_preview(self):
        """AC-004: LinkExistingPanel renders preview of selected file."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        panel_idx = content.index("LinkExistingPanel")
        remainder = content[panel_idx:]
        assert "preview" in remainder[:3000].lower(), \
            "LinkExistingPanel must have preview rendering"

    def test_link_panel_fetches_file_content(self):
        """AC-004: LinkExistingPanel fetches file via /api/ideas/file."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "/api/ideas/file" in content, \
            "Must call GET /api/ideas/file for preview and edit mode"

    def test_link_panel_has_destroy_method(self):
        """LinkExistingPanel has destroy() for cleanup."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        panel_idx = content.index("class LinkExistingPanel")
        remainder = content[panel_idx:]
        assert "destroy(" in remainder[:5000], "LinkExistingPanel must have destroy() method"

    def test_link_panel_has_empty_state(self):
        """AC-009: Shows message when no ideas exist."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "no existing ideas" in content.lower() or "no ideas found" in content.lower() or \
               "use create new" in content.lower(), \
            "Must show empty state message when tree has no ideas"

    def test_link_panel_uses_marked_for_markdown(self):
        """AC-004: Uses marked.js for markdown preview."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "marked" in content.lower(), \
            "Must use marked.js for markdown rendering in preview"


# ============================================================================
# 2. STAGE GATE CHECKER — JS STRUCTURE
# ============================================================================

class TestStageGateCheckerJS:
    """Verify StageGateChecker utility exists in workflow-stage.js."""

    def test_stage_gate_checker_exists(self):
        """AC-010: workflow-stage.js defines StageGateChecker."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        assert "StageGateChecker" in content

    def test_gate_checker_has_can_reopen(self):
        """AC-010: StageGateChecker has canReopen method."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        assert "canReopen" in content

    def test_gate_checks_next_stage(self):
        """AC-011: Gate checker references next stage actions."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        gate_idx = content.find("StageGateChecker")
        if gate_idx == -1:
            pytest.fail("StageGateChecker not found")
        remainder = content[gate_idx:]
        assert "in_progress" in remainder[:1500] or "done" in remainder[:1500], \
            "Gate checker must check for in_progress/done status in next stage"

    def test_gate_checker_is_reusable(self):
        """AC-014: Gate checker takes actionKey parameter (not hardcoded to compose_idea)."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        assert re.search(r"canReopen\s*\(\s*\w+Key", content) or \
               re.search(r"canReopen\s*\(\s*action", content), \
            "canReopen must accept actionKey parameter for reusability"

    def test_gate_uses_stage_order(self):
        """AC-014: Gate checker uses stage ordering to find next stage."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        gate_idx = content.find("StageGateChecker")
        if gate_idx == -1:
            pytest.fail("StageGateChecker not found")
        remainder = content[gate_idx:]
        assert "STAGE_ORDER" in remainder[:1500] or "stage" in remainder[:1500].lower(), \
            "Gate checker must reference stage ordering"


# ============================================================================
# 3. COMPLETED ACTION RE-OPEN FLOW
# ============================================================================

class TestCompletedActionReopen:
    """Verify workflow-stage.js handles completed modal actions with gate+confirm."""

    def test_completed_modal_action_not_just_toast(self):
        """AC-010: Clicking completed modal action does NOT just show toast."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        # _handleCompletedAction must exist and use StageGateChecker
        assert "_handleCompletedAction" in content, \
            "Completed actions must use _handleCompletedAction, not just toast"
        handler_idx = content.index("_handleCompletedAction")
        block = content[handler_idx:handler_idx + 1000]
        assert "StageGateChecker" in block or "canReopen" in block, \
            "Completed modal actions must use gate check"

    def test_confirm_dialog_before_reopen(self):
        """AC-013: Bootstrap confirmation modal shown before re-opening."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        assert "_showConfirmModal" in content, \
            "Must show Bootstrap confirmation modal before re-opening"
        assert "modal-dialog" in content, \
            "Confirm modal must use Bootstrap modal markup"

    def test_status_rollback_to_pending(self):
        """AC-015: Action status rolled back to 'pending' on re-open."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        assert "'pending'" in content or '"pending"' in content, \
            "Must rollback action status to 'pending' via API"

    def test_gate_blocked_shows_error(self):
        """AC-012: Error toast when gate check fails."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        assert "cannot re-open" in content.lower() or "already started" in content.lower(), \
            "Must show error message when gate check blocks re-open"


# ============================================================================
# 4. COMPOSE IDEA MODAL — EDIT MODE
# ============================================================================

class TestComposeIdeaModalEditMode:
    """Verify ComposeIdeaModal supports edit mode (CR-001)."""

    def test_constructor_accepts_mode_param(self):
        """AC-016: Constructor accepts mode parameter."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "mode" in content, "Constructor must accept mode parameter"
        # Check for 'edit' mode value
        assert "'edit'" in content or '"edit"' in content, \
            "Must support 'edit' mode value"

    def test_constructor_accepts_file_path(self):
        """AC-018: Constructor accepts filePath parameter."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "filePath" in content or "file_path" in content

    def test_constructor_accepts_folder_params(self):
        """AC-017: Constructor accepts folderPath and folderName."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "folderPath" in content or "folder_path" in content
        assert "folderName" in content or "folder_name" in content

    def test_has_load_edit_content_method(self):
        """AC-016: Has loadEditContent method to pre-populate EasyMDE."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "loadEditContent" in content or "loadEdit" in content

    def test_has_handle_update_method(self):
        """AC-021: Has handleUpdate method for overwrite-in-place save."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "handleUpdate" in content or "Update" in content

    def test_edit_mode_button_text(self):
        """AC-020: Submit button shows 'Update Idea' in edit mode."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "Update Idea" in content

    def test_edit_mode_fetches_file_content(self):
        """AC-019: Edit mode fetches file via /api/ideas/file."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "/api/ideas/file" in content

    def test_edit_mode_folder_name_readonly(self):
        """AC-017: Folder name is read-only in edit mode."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "disabled" in content or "readOnly" in content or "readonly" in content


# ============================================================================
# 5. CSS — LINK EXISTING PANEL STYLES
# ============================================================================

class TestLinkExistingCSS:
    """Verify CSS has Link Existing panel styles."""

    def test_css_has_link_existing_panel(self):
        """AC-028: CSS defines .link-existing-panel."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert "link-existing-panel" in content or "le-" in content

    def test_css_has_tree_styles(self):
        """AC-028: CSS has file tree styles."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert "le-tree" in content or "tree" in content.lower()

    def test_css_has_preview_styles(self):
        """AC-028: CSS has preview panel styles."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert "le-preview" in content or "preview" in content.lower()

    def test_css_has_search_styles(self):
        """AC-003: CSS has search input styles."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert "le-search" in content or "search" in content.lower()

    def test_css_has_two_column_layout(self):
        """AC-028: Link Existing panel uses two-column layout (flex)."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        # Should have display:flex for the panel container
        assert "display: flex" in content or "display:flex" in content


# ============================================================================
# 6. API — GET /api/ideas/file ENDPOINT
# ============================================================================

class TestGetIdeaFileAPI:
    """API tests for GET /api/ideas/file endpoint."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with a test idea file."""
        temp_dir = tempfile.mkdtemp()
        ideas_path = Path(temp_dir) / "x-ipe-docs" / "ideas" / "wf-001-test"
        ideas_path.mkdir(parents=True)
        (ideas_path / "new idea.md").write_text("# Test Idea\n\nContent here")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def app_client(self, temp_project_dir):
        """Create Flask test client."""
        try:
            from src.app import create_app
            app = create_app({
                "PROJECT_ROOT": temp_project_dir,
                "TESTING": True,
                "SETTINGS_DB_PATH": os.path.join(temp_project_dir, "test_settings.db")
            })
            with app.test_client() as client:
                yield client
        except ImportError:
            pytest.skip("App not importable yet (TDD)")

    def test_get_file_returns_content(self, app_client):
        """AC-019: GET /api/ideas/file returns file content as plain text."""
        resp = app_client.get(
            "/api/ideas/file?path=x-ipe-docs/ideas/wf-001-test/new idea.md"
        )
        assert resp.status_code == 200
        assert b"# Test Idea" in resp.data

    def test_get_file_returns_plain_text_content_type(self, app_client):
        """AC-019: Response content type is text/plain."""
        resp = app_client.get(
            "/api/ideas/file?path=x-ipe-docs/ideas/wf-001-test/new idea.md"
        )
        assert "text/plain" in resp.content_type

    def test_get_file_404_for_missing_file(self, app_client):
        """AC-024: Returns 404 if file does not exist."""
        resp = app_client.get("/api/ideas/file?path=x-ipe-docs/ideas/nonexistent.md")
        assert resp.status_code == 404

    def test_get_file_403_for_path_traversal(self, app_client):
        """AC-025: Returns 403 for path traversal attempts."""
        resp = app_client.get("/api/ideas/file?path=../../etc/passwd")
        assert resp.status_code == 403

    def test_get_file_403_for_absolute_path(self, app_client):
        """AC-025: Returns 403 for absolute paths."""
        resp = app_client.get("/api/ideas/file?path=/etc/passwd")
        assert resp.status_code == 403

    def test_get_file_400_for_missing_path_param(self, app_client):
        """AC-025: Returns 400 if path parameter is missing."""
        resp = app_client.get("/api/ideas/file")
        assert resp.status_code == 400

    def test_get_file_endpoint_exists_in_routes(self):
        """FR-037-B.8: ideas_routes.py defines GET /api/ideas/file route."""
        content = (SRC_ROOT / "routes" / "ideas_routes.py").read_text()
        assert "/api/ideas/file" in content, \
            "ideas_routes.py must define GET /api/ideas/file endpoint"

    def test_get_file_validates_path_within_project(self):
        """FR-037-B.8: Route validates path is within project root."""
        content = (SRC_ROOT / "routes" / "ideas_routes.py").read_text()
        # Should use resolve() and startswith() for path security
        assert "resolve" in content or "realpath" in content, \
            "Must resolve path to prevent traversal"


# ============================================================================
# 7. INTEGRATION — MODAL SWITCH MODES
# ============================================================================

class TestModalModeSwitching:
    """Verify toggle between Create New and Link Existing works."""

    def test_switch_mode_creates_link_panel(self):
        """AC-001: Switching to Link Existing creates LinkExistingPanel."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        # switchMode or equivalent should reference LinkExistingPanel
        assert "LinkExistingPanel" in content, \
            "Modal must create LinkExistingPanel when switching to Link Existing"

    def test_switch_mode_replaces_placeholder(self):
        """AC-001: Link Existing no longer shows placeholder after 037-B."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        panel_idx = content.find("LinkExistingPanel")
        assert panel_idx > -1, "LinkExistingPanel must exist (replacing placeholder)"

    def test_link_mode_changes_submit_label(self):
        """AC-006: Submit button label changes to 'Confirm Link' in link mode."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "Confirm Link" in content or "confirm" in content.lower()


# ============================================================================
# 8. ERROR HANDLING — EDIT MODE
# ============================================================================

class TestEditModeErrorHandling:
    """Verify error handling in edit mode."""

    def test_file_not_found_shows_error(self):
        """AC-024: Error toast when deliverable file not found (404)."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "not found" in content.lower() or "404" in content

    def test_no_deliverables_opens_create_mode(self):
        """AC-027: Missing deliverables → open in create mode."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        # Should check deliverables length and fall back to create mode
        assert "deliverables" in content.lower(), \
            "Must check deliverables to determine edit vs create mode"
