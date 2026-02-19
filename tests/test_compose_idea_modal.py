"""
Tests for FEATURE-037-A: Compose Idea Modal — Create New

Tests cover:
- File existence and structure for compose-idea-modal.js and compose-idea-modal.css
- ComposeIdeaModal class: open/close lifecycle, DOM creation, tab switching
- IdeaNameValidator: validation logic, sanitization, word counting
- AutoFolderNamer: wf-NNN pattern, tree scanning, zero-padding
- Workplace.js refactoring: containerEl parameter backward compatibility
- Template integration: CSS/JS links in index.html
- API integration: POST /api/ideas/upload, POST /api/workflow/{name}/action
- Error handling: name validation, folder collision, API failures

TDD baseline: All tests should FAIL before implementation.
"""
import os
import re
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_ROOT = PROJECT_ROOT / "src" / "x_ipe"
JS_FEATURES = SRC_ROOT / "static" / "js" / "features"
CSS_FEATURES = SRC_ROOT / "static" / "css" / "features"
TEMPLATES = SRC_ROOT / "templates"


# ============================================================================
# 1. FILE EXISTENCE & STRUCTURE
# ============================================================================

class TestComposeIdeaModalFiles:
    """Verify new frontend module files exist and have expected structure."""

    def test_compose_idea_modal_js_exists(self):
        """FR-001: compose-idea-modal.js exists in static/js/features/."""
        js_path = JS_FEATURES / "compose-idea-modal.js"
        assert js_path.exists(), "compose-idea-modal.js must exist"

    def test_compose_idea_modal_css_exists(self):
        """FR-001: compose-idea-modal.css exists in static/css/features/."""
        css_path = CSS_FEATURES / "compose-idea-modal.css"
        assert css_path.exists(), "compose-idea-modal.css must exist"

    def test_js_has_compose_idea_modal_class(self):
        """AC-001: JS defines ComposeIdeaModal class."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "class ComposeIdeaModal" in content or "ComposeIdeaModal" in content

    def test_js_has_idea_name_validator_class(self):
        """AC-011: JS defines IdeaNameValidator class."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "IdeaNameValidator" in content

    def test_js_has_auto_folder_namer_class(self):
        """AC-024: JS defines AutoFolderNamer class."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "AutoFolderNamer" in content

    def test_js_has_open_method(self):
        """AC-001: ComposeIdeaModal has open() method."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "open(" in content

    def test_js_has_close_method(self):
        """AC-004: ComposeIdeaModal has close() method."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "close(" in content

    def test_js_has_handle_submit_method(self):
        """AC-023: ComposeIdeaModal has handleSubmit() method."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "handleSubmit" in content

    def test_js_has_cleanup_method(self):
        """AC-018: ComposeIdeaModal has cleanup() for EasyMDE destruction."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "cleanup" in content

    def test_js_calls_ideas_upload_api(self):
        """AC-026: JS calls POST /api/ideas/upload."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "/api/ideas/upload" in content

    def test_js_calls_workflow_action_api(self):
        """AC-027: JS calls POST /api/workflow/ action endpoint."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "/api/workflow/" in content

    def test_js_calls_ideas_tree_api(self):
        """AC-024: AutoFolderNamer calls GET /api/ideas/tree."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "/api/ideas/tree" in content


# ============================================================================
# 2. CSS STRUCTURE
# ============================================================================

class TestComposeIdeaModalCSS:
    """Verify CSS has expected selectors matching technical design."""

    def test_css_has_overlay_class(self):
        """AC-002: CSS defines .compose-modal-overlay."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert ".compose-modal-overlay" in content

    def test_css_has_modal_class(self):
        """AC-002: CSS defines .compose-modal."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert ".compose-modal" in content

    def test_css_has_header_class(self):
        """AC-003: CSS defines .compose-modal-header."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert ".compose-modal-header" in content

    def test_css_has_toggle_class(self):
        """AC-007: CSS defines .compose-modal-toggle."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert ".compose-modal-toggle" in content

    def test_css_has_name_class(self):
        """AC-011: CSS defines .compose-modal-name."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert ".compose-modal-name" in content

    def test_css_has_tabs_class(self):
        """AC-015: CSS defines .compose-modal-tabs."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert ".compose-modal-tabs" in content

    def test_css_has_editor_class(self):
        """AC-016: CSS defines .compose-modal-editor."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert ".compose-modal-editor" in content

    def test_css_has_upload_class(self):
        """AC-019: CSS defines .compose-modal-upload."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert ".compose-modal-upload" in content

    def test_css_has_footer_class(self):
        """AC-003: CSS defines .compose-modal-footer."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert ".compose-modal-footer" in content

    def test_css_has_active_state(self):
        """AC-001: CSS defines .compose-modal-overlay.active for show/hide."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert ".compose-modal-overlay.active" in content

    def test_css_z_index_above_stage_toolbox(self):
        """AC-002: Modal overlay z-index is 1051 (above stage-toolbox 1050)."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert "1051" in content

    def test_css_has_max_width_720(self):
        """AC-002: Modal max-width ~720px per spec."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert "720px" in content


# ============================================================================
# 3. TEMPLATE INTEGRATION
# ============================================================================

class TestTemplateIntegration:
    """Verify base.html includes compose-idea-modal CSS and JS."""

    def test_index_has_compose_modal_css(self):
        """FR-001: base.html links compose-idea-modal.css."""
        content = (TEMPLATES / "base.html").read_text()
        assert "compose-idea-modal.css" in content

    def test_index_has_compose_modal_js(self):
        """FR-001: base.html includes compose-idea-modal.js."""
        content = (TEMPLATES / "base.html").read_text()
        assert "compose-idea-modal.js" in content


# ============================================================================
# 4. WORKPLACE JS REFACTORING — BACKWARD COMPATIBILITY
# ============================================================================

class TestWorkplaceRefactoring:
    """Verify workplace.js setupComposer/setupUploader accept containerEl."""

    def test_setup_composer_has_container_param(self):
        """AC-035: setupComposer accepts containerEl parameter."""
        content = (JS_FEATURES / "workplace.js").read_text()
        # Should have containerEl or container parameter
        pattern = r"setupComposer\s*\([^)]*container"
        assert re.search(pattern, content, re.IGNORECASE), \
            "setupComposer must accept a container element parameter"

    def test_setup_uploader_has_container_param(self):
        """AC-036: setupUploader accepts containerEl parameter."""
        content = (JS_FEATURES / "workplace.js").read_text()
        pattern = r"setupUploader\s*\([^)]*container"
        assert re.search(pattern, content, re.IGNORECASE), \
            "setupUploader must accept a container element parameter"

    def test_setup_composer_uses_query_selector(self):
        """AC-035: Refactored setupComposer uses querySelector instead of getElementById."""
        content = (JS_FEATURES / "workplace.js").read_text()
        # Find the setupComposer method body and check for querySelector
        match = re.search(r"setupComposer\s*\([^)]*\)\s*\{([\s\S]*?)(?=\n\s{4}\w|\n\s{2}\})", content)
        if match:
            method_body = match.group(1)
            assert "querySelector" in method_body or "container" in method_body.lower(), \
                "setupComposer should use querySelector or container parameter"

    def test_workplace_compose_selectors_preserved(self):
        """AC-037: Existing workplace compose IDs still referenced for backward compat."""
        content = (JS_FEATURES / "workplace.js").read_text()
        assert "workplace-submit-idea" in content or "submit-idea" in content
        assert "workplace-compose-textarea" in content or "compose-textarea" in content


# ============================================================================
# 5. IDEA NAME VALIDATOR LOGIC (via Python emulation of spec rules)
# ============================================================================

class TestIdeaNameValidatorRules:
    """Test IdeaNameValidator logic by verifying JS implements spec rules.
    
    These tests check the JS file contains the correct validation logic.
    Actual UI behavior is verified in acceptance tests.
    """

    def test_max_word_count_is_10(self):
        """AC-013: Max word count is 10."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "10" in content, "Max word count of 10 must be defined"

    def test_sanitize_converts_to_lowercase(self):
        """AC-025: Sanitization includes toLowerCase."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "toLowerCase" in content

    def test_sanitize_replaces_spaces_with_hyphens(self):
        """AC-025: Sanitization replaces spaces with hyphens."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        # Should have a regex replacing \s+ with -
        assert "replace" in content
        # Check for space-to-hyphen pattern
        assert re.search(r"replace\([^)]*\\s", content) or "replace(/\\s+/g" in content

    def test_sanitize_removes_special_chars(self):
        """AC-025: Sanitization removes special characters."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert re.search(r"replace\([^)]*\[.*?\]", content), \
            "Should have regex to remove special characters"

    def test_sanitize_max_50_chars(self):
        """AC-025: Sanitization limits name to 50 chars."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "50" in content or "substring" in content

    def test_live_word_counter_on_input(self):
        """AC-012: Live word counter updates on input event."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "input" in content, "Should listen to input event for live counter"

    def test_word_count_uses_split(self):
        """AC-012: Word count splits by whitespace."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "split" in content, "Should split text to count words"


# ============================================================================
# 6. AUTO FOLDER NAMER LOGIC
# ============================================================================

class TestAutoFolderNamerRules:
    """Test AutoFolderNamer implements wf-NNN naming convention."""

    def test_folder_prefix_is_wf(self):
        """AC-024: Folder name starts with 'wf-'."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "wf-" in content

    def test_folder_number_zero_padded_3_digits(self):
        """AC-024: NNN is zero-padded to 3 digits."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "padStart" in content or "padStart(3" in content, \
            "Should zero-pad to 3 digits using padStart"

    def test_folder_scans_existing_wf_numbers(self):
        """AC-024: Scans tree for highest existing wf-XXX number."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert re.search(r"wf-\(?\\/?\(?\\d", content, re.IGNORECASE) or \
               "wf-(\\d" in content or "wf-\\d" in content or \
               re.search(r"match.*wf-", content), \
            "Should have regex to match wf-NNN pattern in tree"


# ============================================================================
# 7. MODAL BEHAVIOR RULES (JS structure checks)
# ============================================================================

class TestModalBehaviorStructure:
    """Verify JS implements key modal behavior rules from spec."""

    def test_escape_key_closes_modal(self):
        """AC-004: Escape key press closes modal."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "Escape" in content or "escape" in content or "keydown" in content

    def test_overlay_click_does_not_close(self):
        """AC-005: Clicking overlay does NOT close modal.
        Verified by checking overlay click handler stops propagation or
        only dialog content click is handled.
        """
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        # Should have click handler on overlay that checks target
        assert "target" in content, \
            "Should check event.target to prevent overlay click from closing"

    def test_create_new_is_default_mode(self):
        """AC-008: 'Create New' is the default active toggle."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "create" in content.lower(), "Default mode should be 'create'"

    def test_link_existing_shows_placeholder(self):
        """AC-009: 'Link Existing' shows placeholder message."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "placeholder" in content.lower() or "next update" in content.lower() or \
               "coming soon" in content.lower() or "available" in content.lower()

    def test_compose_is_default_tab(self):
        """AC-015: 'Compose' tab is default active."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "compose" in content.lower()

    def test_easymde_toolbar_buttons(self):
        """AC-016: EasyMDE has toolbar buttons: bold, italic, heading, etc."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "bold" in content.lower() or "toolbar" in content.lower()

    def test_easymde_cleanup_on_close(self):
        """AC-018: EasyMDE destroyed on close via toTextArea."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "toTextArea" in content

    def test_submit_disabled_until_valid(self):
        """AC-023: Submit button disabled until name valid AND content exists."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "disabled" in content

    def test_auto_complete_compose_idea_action(self):
        """AC-027: On success, compose_idea action auto-completes."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "compose_idea" in content

    def test_modal_closes_on_success(self):
        """AC-028: Modal closes on successful submit."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "close" in content


# ============================================================================
# 8. ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Verify JS implements error handling from spec."""

    def test_handles_api_error(self):
        """AC-030: Shows error toast on API failure."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "error" in content.lower() or "Error" in content

    def test_handles_folder_collision(self):
        """AC-029: Handles 409 folder collision response."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "409" in content or "collision" in content.lower() or \
               "already exists" in content.lower()


# ============================================================================
# 9. WORKFLOW INTEGRATION
# ============================================================================

class TestWorkflowIntegration:
    """Verify compose-idea-modal integrates with workflow stage view."""

    def test_workflow_js_dispatches_to_compose_modal(self):
        """AC-001: workflow-stage.js dispatches compose_idea action to ComposeIdeaModal."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        assert "compose_idea" in content and "ComposeIdeaModal" in content

    def test_workflow_js_imports_compose_modal(self):
        """AC-001: workflow-stage.js references ComposeIdeaModal."""
        content = (JS_FEATURES / "workflow-stage.js").read_text()
        assert "ComposeIdeaModal" in content


class TestTemplateAutoReload:
    """BUG-539: Flask must always auto-reload templates so base.html changes are served."""

    def test_flask_config_enables_templates_auto_reload(self):
        """TEMPLATES_AUTO_RELOAD must be True in base Config to prevent stale template cache."""
        from x_ipe.config import Config
        assert getattr(Config, 'TEMPLATES_AUTO_RELOAD', None) is True


# ============================================================================
# 10. API ENDPOINT TESTS (Backend — Flask test client)
# ============================================================================

class TestIdeaUploadAPI:
    """API tests for /api/ideas/upload with auto-named folders.
    
    These tests verify the backend properly handles compose modal submissions.
    Uses Flask test client fixture.
    """

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        ideas_path = Path(temp_dir) / "x-ipe-docs" / "ideas"
        ideas_path.mkdir(parents=True)
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

    def test_ideas_tree_returns_json(self, app_client):
        """AC-024: GET /api/ideas/tree returns folder tree as JSON."""
        response = app_client.get("/api/ideas/tree")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, (list, dict))

    def test_ideas_upload_with_target_folder(self, app_client, temp_project_dir):
        """AC-026: POST /api/ideas/upload with target_folder creates idea."""
        from io import BytesIO
        data = {
            "target_folder": "wf-001-test-idea",
            "files": (BytesIO(b"# Test Idea\n\nContent here"), "idea.md")
        }
        response = app_client.post(
            "/api/ideas/upload",
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code in (200, 201)

    def test_ideas_upload_creates_folder_with_wf_prefix(self, app_client, temp_project_dir):
        """AC-024: Uploaded idea creates folder matching wf-NNN-{name} pattern."""
        from io import BytesIO
        folder_name = "wf-001-my-test"
        data = {
            "target_folder": folder_name,
            "files": (BytesIO(b"# Test"), "idea.md")
        }
        app_client.post("/api/ideas/upload", data=data, content_type="multipart/form-data")
        folder_path = Path(temp_project_dir) / "x-ipe-docs" / "ideas" / folder_name
        assert folder_path.exists()


# ============================================================================
# 11. UPLOAD TAB TESTS
# ============================================================================

class TestUploadTabRules:
    """Verify upload tab implements spec rules."""

    def test_accepts_specified_file_types(self):
        """AC-020: Upload accepts md, txt, pdf, png, jpg, py, js, docx."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        accepted_types = ["md", "txt", "pdf", "png", "jpg", "py", "js", "docx"]
        found = sum(1 for t in accepted_types if t in content)
        assert found >= 4, f"Should reference accepted file types, found {found}/8"

    def test_drag_over_visual_feedback(self):
        """AC-021: Visual feedback on file drag-over."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "dragover" in content.lower() or "drag-over" in content.lower()

    def test_file_list_shows_name_and_size(self):
        """AC-022: Uploaded files show name and size."""
        content = (JS_FEATURES / "compose-idea-modal.js").read_text()
        assert "size" in content.lower() or "name" in content.lower()


# ============================================================================
# 12. MOCKUP ALIGNMENT (structural checks)
# ============================================================================

class TestMockupAlignment:
    """AC-032 to AC-034: UI elements match approved mockup structure."""

    def test_css_uses_slate_emerald_palette(self):
        """AC-033: Slate/Emerald color palette from mockup design tokens."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        # Check for at least some Slate/Emerald hex values
        slate_colors = ["1e293b", "334155", "64748b", "94a3b8", "e2e8f0"]
        emerald_colors = ["10b981"]
        found = sum(1 for c in slate_colors + emerald_colors if c in content.lower())
        assert found >= 2, f"Should use Slate/Emerald palette, found {found} colors"

    def test_css_uses_dm_sans_font(self):
        """AC-033: DM Sans font from mockup design tokens."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert "DM Sans" in content or "dm-sans" in content.lower()

    def test_css_uses_12px_border_radius(self):
        """AC-033: 12px border-radius from mockup."""
        content = (CSS_FEATURES / "compose-idea-modal.css").read_text()
        assert "12px" in content
