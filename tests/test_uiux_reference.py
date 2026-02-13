"""
Tests for FEATURE-033: App-Agent Interaction MCP

Tests cover:
- UiuxReferenceService (unit tests)
- POST /api/ideas/uiux-reference endpoint (API tests)
- MCP tool save_uiux_reference (unit tests)

TDD: All tests written before implementation.
"""
import json
import os
import base64
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Test Data Factories
# ---------------------------------------------------------------------------

def make_reference_data(**overrides):
    """Create valid reference data with optional overrides."""
    data = {
        "version": "1.0",
        "source_url": "https://example.com/page",
        "timestamp": "2026-02-13T09:00:00Z",
        "idea_folder": "018. Test Idea",
        "colors": [
            {
                "id": "color-001",
                "hex": "#1A73E8",
                "rgb": "26, 115, 232",
                "hsl": "217, 80%, 51%",
                "source_selector": "header .logo",
                "context": "Brand primary"
            }
        ],
        "elements": [],
        "design_tokens": {
            "colors": {"primary": "#1A73E8"},
            "typography": {"heading_font": "Google Sans"}
        }
    }
    data.update(overrides)
    return data


def make_element_with_screenshot(element_id="elem-001", base64_data=None):
    """Create an element with base64-encoded screenshot."""
    if base64_data is None:
        # 1x1 red PNG
        base64_data = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
            b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
            b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        ).decode('ascii')
    return {
        "id": element_id,
        "selector": "body > main > .cta-button",
        "tag": "button",
        "bounding_box": {"x": 120, "y": 340, "width": 200, "height": 48},
        "screenshots": {
            "full_page": f"base64:{base64_data}",
            "element_crop": f"base64:{base64_data}"
        },
        "comment": "Primary CTA button",
        "extracted_assets": None
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project with idea folder structure."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create idea folder
    idea_dir = project_dir / "x-ipe-docs" / "ideas" / "018. Test Idea"
    idea_dir.mkdir(parents=True)

    return project_dir


@pytest.fixture
def temp_project_with_sessions(temp_project):
    """Create a project with existing reference sessions."""
    uiux_dir = temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea" / "uiux-references"
    sessions_dir = uiux_dir / "sessions"
    sessions_dir.mkdir(parents=True)

    # Create two existing sessions
    session_1 = {
        "version": "1.0",
        "source_url": "https://example.com/page1",
        "timestamp": "2026-02-13T08:00:00Z",
        "colors": [{"id": "color-001", "hex": "#FF0000"}],
        "elements": [],
        "design_tokens": {"colors": {"primary": "#FF0000"}}
    }
    session_2 = {
        "version": "1.0",
        "source_url": "https://example.com/page2",
        "timestamp": "2026-02-13T08:30:00Z",
        "colors": [{"id": "color-002", "hex": "#00FF00"}],
        "elements": [],
        "design_tokens": {"colors": {"primary": "#00FF00"}}
    }

    (sessions_dir / "ref-session-001.json").write_text(json.dumps(session_1, indent=2))
    (sessions_dir / "ref-session-002.json").write_text(json.dumps(session_2, indent=2))

    return temp_project


@pytest.fixture
def uiux_service(temp_project):
    """Create UiuxReferenceService instance."""
    from x_ipe.services.uiux_reference_service import UiuxReferenceService
    return UiuxReferenceService(str(temp_project))


@pytest.fixture
def uiux_service_with_sessions(temp_project_with_sessions):
    """Create UiuxReferenceService with existing sessions."""
    from x_ipe.services.uiux_reference_service import UiuxReferenceService
    return UiuxReferenceService(str(temp_project_with_sessions))


@pytest.fixture
def app(temp_project):
    """Create Flask app with test configuration."""
    from x_ipe.app import create_app

    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': str(temp_project),
    })
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def app_with_sessions(temp_project_with_sessions):
    """Create Flask app with existing sessions."""
    from x_ipe.app import create_app

    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': str(temp_project_with_sessions),
    })
    return app


@pytest.fixture
def client_with_sessions(app_with_sessions):
    """Create test client with existing sessions."""
    return app_with_sessions.test_client()


# ===========================================================================
# UNIT TESTS: UiuxReferenceService
# ===========================================================================

class TestUiuxReferenceServiceValidation:
    """Unit tests for schema validation."""

    def test_validate_valid_data_returns_no_errors(self, uiux_service):
        """Valid reference data passes validation."""
        data = make_reference_data()
        errors = uiux_service._validate_schema(data)
        assert errors == []

    def test_validate_missing_version_returns_error(self, uiux_service):
        """Missing 'version' field returns validation error."""
        data = make_reference_data()
        del data["version"]
        errors = uiux_service._validate_schema(data)
        assert any("version" in e for e in errors)

    def test_validate_missing_source_url_returns_error(self, uiux_service):
        """Missing 'source_url' field returns validation error."""
        data = make_reference_data()
        del data["source_url"]
        errors = uiux_service._validate_schema(data)
        assert any("source_url" in e for e in errors)

    def test_validate_missing_timestamp_returns_error(self, uiux_service):
        """Missing 'timestamp' field returns validation error."""
        data = make_reference_data()
        del data["timestamp"]
        errors = uiux_service._validate_schema(data)
        assert any("timestamp" in e for e in errors)

    def test_validate_missing_idea_folder_returns_error(self, uiux_service):
        """Missing 'idea_folder' field returns validation error."""
        data = make_reference_data()
        del data["idea_folder"]
        errors = uiux_service._validate_schema(data)
        assert any("idea_folder" in e for e in errors)

    def test_validate_empty_data_sections_returns_error(self, uiux_service):
        """All data sections empty returns validation error."""
        data = make_reference_data(colors=[], elements=[], design_tokens={})
        errors = uiux_service._validate_schema(data)
        assert any("at least one" in e.lower() for e in errors)

    def test_validate_missing_all_data_sections_returns_error(self, uiux_service):
        """No data sections present returns validation error."""
        data = {
            "version": "1.0",
            "source_url": "https://example.com",
            "timestamp": "2026-02-13T09:00:00Z",
            "idea_folder": "018. Test Idea"
        }
        errors = uiux_service._validate_schema(data)
        assert any("at least one" in e.lower() for e in errors)

    def test_validate_with_only_colors_passes(self, uiux_service):
        """Data with only colors section (no elements/tokens) passes."""
        data = make_reference_data(elements=None, design_tokens=None)
        # Remove the keys entirely
        data.pop("elements", None)
        data.pop("design_tokens", None)
        errors = uiux_service._validate_schema(data)
        assert errors == []


class TestUiuxReferenceServiceSessionNumbering:
    """Unit tests for session auto-increment numbering."""

    def test_first_session_gets_number_001(self, uiux_service, temp_project):
        """First session in empty folder gets number 1."""
        sessions_dir = temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea" / "uiux-references" / "sessions"
        sessions_dir.mkdir(parents=True)
        number = uiux_service._get_next_session_number(sessions_dir)
        assert number == 1

    def test_next_session_after_two_gets_003(self, uiux_service_with_sessions, temp_project_with_sessions):
        """After sessions 001 and 002, next is 003."""
        sessions_dir = temp_project_with_sessions / "x-ipe-docs" / "ideas" / "018. Test Idea" / "uiux-references" / "sessions"
        number = uiux_service_with_sessions._get_next_session_number(sessions_dir)
        assert number == 3

    def test_session_numbering_with_gaps(self, uiux_service, temp_project):
        """Gaps in numbering (001, 003) → next is 004."""
        sessions_dir = temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea" / "uiux-references" / "sessions"
        sessions_dir.mkdir(parents=True)
        (sessions_dir / "ref-session-001.json").write_text("{}")
        (sessions_dir / "ref-session-003.json").write_text("{}")
        number = uiux_service._get_next_session_number(sessions_dir)
        assert number == 4


class TestUiuxReferenceServiceScreenshots:
    """Unit tests for base64 screenshot decoding."""

    def test_decode_base64_screenshot_creates_file(self, uiux_service, temp_project):
        """Base64-prefixed screenshot is decoded and saved as file."""
        screenshots_dir = temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea" / "uiux-references" / "screenshots"
        screenshots_dir.mkdir(parents=True)

        element = make_element_with_screenshot()
        data = make_reference_data(elements=[element])

        result = uiux_service._decode_screenshots(data, screenshots_dir)

        # Verify files were created
        assert any(screenshots_dir.iterdir())

    def test_decode_replaces_base64_with_path(self, uiux_service, temp_project):
        """After decoding, base64 data is replaced with file path in JSON."""
        screenshots_dir = temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea" / "uiux-references" / "screenshots"
        screenshots_dir.mkdir(parents=True)

        element = make_element_with_screenshot()
        data = make_reference_data(elements=[element])

        result = uiux_service._decode_screenshots(data, screenshots_dir)

        for elem in result.get("elements", []):
            screenshots = elem.get("screenshots", {})
            for key, val in screenshots.items():
                if val:
                    assert not val.startswith("base64:"), f"base64 not replaced for {key}"

    def test_non_base64_screenshot_left_unchanged(self, uiux_service, temp_project):
        """Screenshot with file path (not base64:) is left as-is."""
        screenshots_dir = temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea" / "uiux-references" / "screenshots"
        screenshots_dir.mkdir(parents=True)

        element = {
            "id": "elem-001",
            "selector": ".btn",
            "screenshots": {
                "full_page": "screenshots/existing.png",
                "element_crop": None
            }
        }
        data = make_reference_data(elements=[element])

        result = uiux_service._decode_screenshots(data, screenshots_dir)

        assert result["elements"][0]["screenshots"]["full_page"] == "screenshots/existing.png"

    def test_no_elements_returns_data_unchanged(self, uiux_service, temp_project):
        """Data without elements is returned unchanged."""
        screenshots_dir = temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea" / "uiux-references" / "screenshots"
        screenshots_dir.mkdir(parents=True)

        data = make_reference_data(elements=[])
        result = uiux_service._decode_screenshots(data, screenshots_dir)
        assert result["elements"] == []


class TestUiuxReferenceServiceSaveReference:
    """Unit tests for the main save_reference method."""

    def test_save_valid_reference_returns_success(self, uiux_service):
        """AC-033.1: Valid reference data is saved successfully."""
        data = make_reference_data()
        result = uiux_service.save_reference(data)

        assert result["success"] is True
        assert "session_file" in result
        assert result["session_file"] == "ref-session-001.json"
        assert result["session_number"] == 1

    def test_save_creates_session_json_file(self, uiux_service, temp_project):
        """Session JSON file is created on disk."""
        data = make_reference_data()
        uiux_service.save_reference(data)

        session_path = (temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea"
                       / "uiux-references" / "sessions" / "ref-session-001.json")
        assert session_path.exists()

        content = json.loads(session_path.read_text())
        assert content["source_url"] == "https://example.com/page"

    def test_save_creates_directories_automatically(self, uiux_service, temp_project):
        """AC-033.8: uiux-references/, sessions/, screenshots/ are auto-created."""
        data = make_reference_data()
        uiux_service.save_reference(data)

        uiux_dir = temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea" / "uiux-references"
        assert uiux_dir.exists()
        assert (uiux_dir / "sessions").exists()
        assert (uiux_dir / "screenshots").exists()

    def test_save_with_screenshots_decodes_and_saves(self, uiux_service, temp_project):
        """AC-033.2: Base64 screenshots are decoded and saved."""
        element = make_element_with_screenshot()
        data = make_reference_data(elements=[element])
        result = uiux_service.save_reference(data)

        assert result["success"] is True
        screenshots_dir = (temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea"
                          / "uiux-references" / "screenshots")
        screenshot_files = list(screenshots_dir.glob("*.png"))
        assert len(screenshot_files) > 0

    def test_save_invalid_schema_returns_error(self, uiux_service):
        """AC-033.3: Invalid schema returns validation error."""
        data = {"version": "1.0"}  # missing required fields
        result = uiux_service.save_reference(data)

        assert result["success"] is False
        assert result["error"] == "VALIDATION_ERROR"
        assert "message" in result

    def test_save_nonexistent_idea_folder_returns_not_found(self, uiux_service):
        """AC-033.6: Nonexistent idea folder returns IDEA_NOT_FOUND."""
        data = make_reference_data(idea_folder="999. Does Not Exist")
        result = uiux_service.save_reference(data)

        assert result["success"] is False
        assert result["error"] == "IDEA_NOT_FOUND"
        assert "999. Does Not Exist" in result["message"]

    def test_save_increments_session_number(self, uiux_service_with_sessions):
        """AC-033.5: Session number auto-increments past existing sessions."""
        data = make_reference_data()
        result = uiux_service_with_sessions.save_reference(data)

        assert result["success"] is True
        assert result["session_number"] == 3
        assert result["session_file"] == "ref-session-003.json"

    def test_save_updates_merged_reference_data(self, uiux_service, temp_project):
        """AC-033.4: reference-data.json is created after save."""
        data = make_reference_data()
        uiux_service.save_reference(data)

        merged_path = (temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea"
                      / "uiux-references" / "reference-data.json")
        assert merged_path.exists()

        merged = json.loads(merged_path.read_text())
        assert "colors" in merged
        assert "last_updated" in merged

    def test_save_merged_contains_all_sessions(self, uiux_service_with_sessions, temp_project_with_sessions):
        """AC-033.4: Merged reference-data.json contains all sessions' data."""
        data = make_reference_data(
            colors=[{"id": "color-003", "hex": "#0000FF"}]
        )
        uiux_service_with_sessions.save_reference(data)

        merged_path = (temp_project_with_sessions / "x-ipe-docs" / "ideas" / "018. Test Idea"
                      / "uiux-references" / "reference-data.json")
        merged = json.loads(merged_path.read_text())

        # Should contain colors from all 3 sessions
        color_ids = [c["id"] for c in merged.get("colors", [])]
        assert "color-001" in color_ids
        assert "color-002" in color_ids
        assert "color-003" in color_ids


class TestUiuxReferenceServiceEdgeCases:
    """Edge case tests."""

    def test_special_chars_in_folder_name(self, uiux_service, temp_project):
        """Idea folder with special chars (dots, spaces) works."""
        # Folder already exists as "018. Test Idea"
        data = make_reference_data(idea_folder="018. Test Idea")
        result = uiux_service.save_reference(data)
        assert result["success"] is True

    def test_empty_colors_with_valid_elements(self, uiux_service):
        """Empty colors but valid elements passes validation."""
        element = {"id": "elem-001", "selector": ".btn"}
        data = make_reference_data(colors=[], elements=[element], design_tokens={})
        result = uiux_service.save_reference(data)
        assert result["success"] is True

    def test_optional_auth_url_accepted(self, uiux_service):
        """auth_url field is optional and accepted when provided."""
        data = make_reference_data(auth_url="https://example.com/login")
        result = uiux_service.save_reference(data)
        assert result["success"] is True


# ===========================================================================
# API TESTS: POST /api/ideas/uiux-reference
# ===========================================================================

class TestUiuxReferenceEndpoint:
    """API tests for POST /api/ideas/uiux-reference endpoint."""

    def test_post_valid_data_returns_200(self, client):
        """AC-033.1: Valid reference data returns 200."""
        data = make_reference_data()
        response = client.post(
            '/api/ideas/uiux-reference',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["success"] is True
        assert "session_file" in result

    def test_post_valid_data_creates_session_file(self, client, temp_project):
        """Session JSON file is created after POST."""
        data = make_reference_data()
        client.post('/api/ideas/uiux-reference', json=data, content_type='application/json')

        session_path = (temp_project / "x-ipe-docs" / "ideas" / "018. Test Idea"
                       / "uiux-references" / "sessions" / "ref-session-001.json")
        assert session_path.exists()

    def test_post_missing_fields_returns_400(self, client):
        """AC-033.3: Missing required fields returns 400."""
        data = {"version": "1.0"}
        response = client.post(
            '/api/ideas/uiux-reference',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 400
        result = json.loads(response.data)
        assert result["success"] is False
        assert result["error"] == "VALIDATION_ERROR"

    def test_post_empty_body_returns_400(self, client):
        """Empty request body returns 400."""
        response = client.post(
            '/api/ideas/uiux-reference',
            data='',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_post_nonexistent_idea_returns_404(self, client):
        """AC-033.6: Nonexistent idea folder returns 404."""
        data = make_reference_data(idea_folder="999. Does Not Exist")
        response = client.post(
            '/api/ideas/uiux-reference',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 404
        result = json.loads(response.data)
        assert result["error"] == "IDEA_NOT_FOUND"

    def test_post_with_screenshots_returns_200(self, client):
        """AC-033.2: Data with base64 screenshots is accepted."""
        element = make_element_with_screenshot()
        data = make_reference_data(elements=[element])
        response = client.post(
            '/api/ideas/uiux-reference',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["success"] is True

    def test_post_increments_session_number(self, client_with_sessions):
        """AC-033.5: Session number auto-increments."""
        data = make_reference_data()
        response = client_with_sessions.post(
            '/api/ideas/uiux-reference',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["session_number"] == 3

    def test_post_error_response_has_descriptive_message(self, client):
        """AC-033.3: Error response includes descriptive message."""
        data = make_reference_data()
        del data["idea_folder"]
        del data["source_url"]
        response = client.post(
            '/api/ideas/uiux-reference',
            json=data,
            content_type='application/json'
        )
        result = json.loads(response.data)
        assert "message" in result
        assert len(result["message"]) > 0


# ===========================================================================
# UNIT TESTS: MCP Tool (save_uiux_reference)
# ===========================================================================

class TestMCPToolSaveUiuxReference:
    """Unit tests for the MCP tool function."""

    def _call_tool(self, data):
        """Call the underlying function of the MCP tool."""
        from x_ipe.mcp.app_agent_interaction import save_uiux_reference
        # FastMCP wraps functions in FunctionTool; access .fn for the raw function
        fn = save_uiux_reference.fn if hasattr(save_uiux_reference, 'fn') else save_uiux_reference
        return fn(data)

    @patch('x_ipe.mcp.app_agent_interaction.requests.post')
    def test_tool_valid_data_calls_backend(self, mock_post):
        """MCP tool POSTs valid data to Flask backend."""
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"success": True, "session_file": "ref-session-001.json", "session_number": 1}
        )

        data = make_reference_data()
        result = self._call_tool(data)

        assert result["success"] is True
        mock_post.assert_called_once()

    @patch('x_ipe.mcp.app_agent_interaction.requests.post')
    def test_tool_passes_data_to_correct_endpoint(self, mock_post):
        """MCP tool calls /api/ideas/uiux-reference endpoint."""
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"success": True}
        )

        data = make_reference_data()
        self._call_tool(data)

        call_args = mock_post.call_args
        assert "/api/ideas/uiux-reference" in call_args[0][0]

    def test_tool_missing_fields_returns_error_locally(self):
        """MCP tool validates required fields before HTTP call."""
        data = {"version": "1.0"}  # missing source_url, timestamp, idea_folder
        result = self._call_tool(data)

        assert result["success"] is False
        assert result["error"] == "VALIDATION_ERROR"

    @patch('x_ipe.mcp.app_agent_interaction.requests.post')
    def test_tool_backend_unreachable_returns_error(self, mock_post):
        """AC-033.7: Backend unreachable returns clear error."""
        import requests as req_lib

        mock_post.side_effect = req_lib.ConnectionError("Connection refused")

        data = make_reference_data()
        result = self._call_tool(data)

        assert result["success"] is False
        assert result["error"] == "BACKEND_UNREACHABLE"

    @patch('x_ipe.mcp.app_agent_interaction.requests.post')
    def test_tool_backend_timeout_returns_error(self, mock_post):
        """Backend timeout returns descriptive error."""
        import requests as req_lib

        mock_post.side_effect = req_lib.Timeout("Request timed out")

        data = make_reference_data()
        result = self._call_tool(data)

        assert result["success"] is False
        assert "timed out" in result["message"].lower()

    @patch('x_ipe.mcp.app_agent_interaction.requests.post')
    def test_tool_returns_backend_error_response(self, mock_post):
        """MCP tool returns backend error response to agent."""
        mock_post.return_value = MagicMock(
            status_code=404,
            json=lambda: {"success": False, "error": "IDEA_NOT_FOUND", "message": "Idea folder not found"}
        )

        data = make_reference_data()
        result = self._call_tool(data)

        assert result["success"] is False
        assert result["error"] == "IDEA_NOT_FOUND"


# ===========================================================================
# TRACING TESTS
# ===========================================================================

class TestUiuxReferenceTracing:
    """Verify tracing decorators are present."""

    def test_service_methods_have_tracing(self):
        """Service public methods have @x_ipe_tracing decorators."""
        import inspect
        from x_ipe.services.uiux_reference_service import UiuxReferenceService

        source = inspect.getsource(UiuxReferenceService.save_reference)
        assert "@x_ipe_tracing" in source, "save_reference missing @x_ipe_tracing"

    def test_route_has_tracing(self):
        """Flask route has @x_ipe_tracing decorator."""
        import inspect
        from x_ipe.routes.uiux_reference_routes import post_uiux_reference

        source = inspect.getsource(post_uiux_reference)
        assert "@x_ipe_tracing" in source, "post_uiux_reference missing @x_ipe_tracing"
