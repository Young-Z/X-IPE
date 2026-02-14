"""
Tests for FEATURE-033 v1.1 (CR-001): inject_script MCP tool and CDPClient

Tests cover:
- CDPClient (unit tests: page discovery, page filtering, WS evaluate)
- MCP tool inject_script (unit tests: validation, file read, error mapping)

TDD: All tests written before implementation.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock


# ---------------------------------------------------------------------------
# CDPClient Unit Tests
# ---------------------------------------------------------------------------

class TestCDPClientDiscoverPages:
    """Unit tests for CDPClient.discover_pages()."""

    def _make_client(self, port=9222):
        from x_ipe.mcp.cdp_client import CDPClient
        return CDPClient(port=port)

    @patch('x_ipe.mcp.cdp_client.urllib.request.urlopen')
    def test_discover_pages_returns_page_list(self, mock_urlopen):
        """AC-033.11: CDP discovers available pages via GET /json."""
        pages = [
            {"type": "page", "url": "https://example.com", "webSocketDebuggerUrl": "ws://localhost:9222/devtools/page/1"},
            {"type": "page", "url": "https://other.com", "webSocketDebuggerUrl": "ws://localhost:9222/devtools/page/2"},
        ]
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(pages).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        client = self._make_client()
        result = client.discover_pages()

        assert len(result) == 2
        assert result[0]["url"] == "https://example.com"

    @patch('x_ipe.mcp.cdp_client.urllib.request.urlopen')
    def test_discover_pages_uses_correct_port(self, mock_urlopen):
        """CDP client uses configured port for discovery."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[]'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        client = self._make_client(port=9333)
        client.discover_pages()

        call_url = mock_urlopen.call_args[0][0]
        assert "9333" in call_url

    @patch('x_ipe.mcp.cdp_client.urllib.request.urlopen')
    def test_discover_pages_connection_error_raises(self, mock_urlopen):
        """AC-033.12: Connection failure raises ConnectionError."""
        mock_urlopen.side_effect = Exception("Connection refused")

        client = self._make_client()
        with pytest.raises(ConnectionError, match="Cannot connect to Chrome DevTools"):
            client.discover_pages()


class TestCDPClientFindTargetPage:
    """Unit tests for CDPClient._find_target_page()."""

    def _make_client(self):
        from x_ipe.mcp.cdp_client import CDPClient
        return CDPClient()

    def _make_pages(self):
        return [
            {"type": "page", "url": "https://example.com/landing", "webSocketDebuggerUrl": "ws://1"},
            {"type": "page", "url": "https://other.com", "webSocketDebuggerUrl": "ws://2"},
            {"type": "page", "url": "chrome-extension://abc/popup.html", "webSocketDebuggerUrl": "ws://3"},
            {"type": "background_page", "url": "chrome-extension://xyz", "webSocketDebuggerUrl": "ws://4"},
            {"type": "page", "url": "devtools://devtools/inspector.html", "webSocketDebuggerUrl": "ws://5"},
        ]

    def test_find_first_suitable_page_without_target_url(self):
        """AC-033.11: Selects first non-extension, non-devtools page."""
        client = self._make_client()
        pages = self._make_pages()

        result = client._find_target_page(pages, target_url=None)

        assert result["url"] == "https://example.com/landing"

    def test_find_page_matching_target_url(self):
        """AC-033.11: Matches page by target_url pattern."""
        client = self._make_client()
        pages = self._make_pages()

        result = client._find_target_page(pages, target_url="other.com")

        assert result["url"] == "https://other.com"

    def test_excludes_chrome_extensions(self):
        """Chrome extension pages are excluded from selection."""
        client = self._make_client()
        pages = [
            {"type": "page", "url": "chrome-extension://abc/popup.html", "webSocketDebuggerUrl": "ws://1"},
        ]

        with pytest.raises(ValueError, match="No suitable browser page"):
            client._find_target_page(pages, target_url=None)

    def test_excludes_devtools_pages(self):
        """DevTools pages are excluded from selection."""
        client = self._make_client()
        pages = [
            {"type": "page", "url": "devtools://devtools/inspector.html", "webSocketDebuggerUrl": "ws://1"},
        ]

        with pytest.raises(ValueError, match="No suitable browser page"):
            client._find_target_page(pages, target_url=None)

    def test_excludes_non_page_types(self):
        """Non-page types (background_page, service_worker) are excluded."""
        client = self._make_client()
        pages = [
            {"type": "background_page", "url": "chrome-extension://xyz", "webSocketDebuggerUrl": "ws://1"},
        ]

        with pytest.raises(ValueError, match="No suitable browser page"):
            client._find_target_page(pages, target_url=None)

    def test_target_url_no_match_raises(self):
        """No page matching target_url raises ValueError."""
        client = self._make_client()
        pages = [
            {"type": "page", "url": "https://example.com", "webSocketDebuggerUrl": "ws://1"},
        ]

        with pytest.raises(ValueError, match="No page matching URL pattern"):
            client._find_target_page(pages, target_url="nonexistent.com")

    def test_empty_pages_raises(self):
        """Empty page list raises ValueError."""
        client = self._make_client()

        with pytest.raises(ValueError, match="No suitable browser page"):
            client._find_target_page([], target_url=None)


class TestCDPClientEvaluate:
    """Unit tests for CDPClient.evaluate() — end-to-end with mocked WS."""

    def _make_client(self):
        from x_ipe.mcp.cdp_client import CDPClient
        return CDPClient()

    @patch.object(
        __import__('builtins'), '__import__', side_effect=ImportError
    )
    def test_evaluate_calls_discover_and_ws(self):
        """evaluate() discovers pages, finds target, connects via WS."""
        # This test verifies the integration between discover + ws_evaluate
        # We mock both discover_pages and _ws_evaluate
        client = self._make_client()

        pages = [{"type": "page", "url": "https://example.com", "webSocketDebuggerUrl": "ws://test"}]
        ws_result = {"id": 1, "result": {"result": {"type": "string", "value": "hello"}}}

        with patch.object(client, 'discover_pages', return_value=pages), \
             patch.object(client, '_ws_evaluate', return_value=ws_result) as mock_ws:
            import asyncio
            mock_ws.return_value = ws_result
            # Make _ws_evaluate a coroutine that returns ws_result
            async def mock_coro(ws_url, expression):
                return ws_result
            with patch.object(client, '_ws_evaluate', side_effect=mock_coro):
                result = client.evaluate("1+1", target_url=None)

        assert result["id"] == 1

    def test_evaluate_propagates_connection_error(self):
        """evaluate() propagates ConnectionError from discover_pages."""
        client = self._make_client()

        with patch.object(client, 'discover_pages', side_effect=ConnectionError("fail")):
            with pytest.raises(ConnectionError):
                client.evaluate("1+1")

    def test_evaluate_propagates_value_error(self):
        """evaluate() propagates ValueError from _find_target_page."""
        client = self._make_client()

        with patch.object(client, 'discover_pages', return_value=[]):
            with pytest.raises(ValueError):
                client.evaluate("1+1")


# ---------------------------------------------------------------------------
# MCP Tool inject_script Unit Tests
# ---------------------------------------------------------------------------

class TestMCPToolInjectScript:
    """Unit tests for the inject_script MCP tool function."""

    def _call_tool(self, **kwargs):
        """Call the underlying function of the inject_script MCP tool."""
        from x_ipe.mcp.app_agent_interaction import inject_script
        fn = inject_script.fn if hasattr(inject_script, 'fn') else inject_script
        return fn(**kwargs)

    # --- Validation Tests ---

    def test_tool_requires_exactly_one_of_file_path_or_script(self):
        """BR-033.7: Providing both file_path and script is a validation error."""
        result = self._call_tool(file_path="/some/file.js", script="alert(1)")

        assert result["success"] is False
        assert result["error"] == "VALIDATION_ERROR"
        assert "exactly one" in result["message"].lower()

    def test_tool_requires_at_least_one_of_file_path_or_script(self):
        """BR-033.7: Providing neither file_path nor script is a validation error."""
        result = self._call_tool()

        assert result["success"] is False
        assert result["error"] == "VALIDATION_ERROR"

    # --- File Path Tests ---

    def test_tool_file_not_found_returns_error(self, tmp_path):
        """AC-033.9: Non-existent file returns FILE_NOT_FOUND."""
        result = self._call_tool(file_path=str(tmp_path / "nonexistent.js"))

        assert result["success"] is False
        assert result["error"] == "FILE_NOT_FOUND"

    @patch('x_ipe.mcp.app_agent_interaction.CDPClient')
    def test_tool_reads_file_and_injects(self, mock_cdp_class, tmp_path):
        """AC-033.9: Reads JS file content and passes to CDP evaluate."""
        js_file = tmp_path / "test.js"
        js_file.write_text("console.log('hello');", encoding="utf-8")

        mock_client = MagicMock()
        mock_client.evaluate.return_value = {
            "id": 1,
            "result": {"result": {"type": "undefined"}}
        }
        mock_cdp_class.return_value = mock_client

        result = self._call_tool(file_path=str(js_file))

        assert result["success"] is True
        mock_client.evaluate.assert_called_once()
        call_args = mock_client.evaluate.call_args
        assert "console.log('hello');" in call_args[0][0]

    # --- Inline Script Tests ---

    @patch('x_ipe.mcp.app_agent_interaction.CDPClient')
    def test_tool_inline_script_injects(self, mock_cdp_class):
        """AC-033.10: Inline script is executed via CDP."""
        mock_client = MagicMock()
        mock_client.evaluate.return_value = {
            "id": 1,
            "result": {"result": {"type": "string", "value": "hello"}}
        }
        mock_cdp_class.return_value = mock_client

        result = self._call_tool(script="document.title")

        assert result["success"] is True
        assert result["result"] == "hello"

    @patch('x_ipe.mcp.app_agent_interaction.CDPClient')
    def test_tool_returns_script_evaluation_value(self, mock_cdp_class):
        """AC-033.10: Return value from script is included in response."""
        mock_client = MagicMock()
        mock_client.evaluate.return_value = {
            "id": 1,
            "result": {"result": {"type": "number", "value": 42}}
        }
        mock_cdp_class.return_value = mock_client

        result = self._call_tool(script="21 * 2")

        assert result["success"] is True
        assert result["result"] == 42

    # --- CDP Connection Error Tests ---

    @patch('x_ipe.mcp.app_agent_interaction.CDPClient')
    def test_tool_cdp_connection_failed_returns_error(self, mock_cdp_class):
        """AC-033.12: No browser returns CDP_CONNECTION_FAILED."""
        mock_client = MagicMock()
        mock_client.evaluate.side_effect = ConnectionError(
            "Cannot connect to Chrome DevTools at localhost:9222"
        )
        mock_cdp_class.return_value = mock_client

        result = self._call_tool(script="1+1")

        assert result["success"] is False
        assert result["error"] == "CDP_CONNECTION_FAILED"
        assert "Chrome DevTools" in result["message"]

    @patch('x_ipe.mcp.app_agent_interaction.CDPClient')
    def test_tool_cdp_no_page_returns_error(self, mock_cdp_class):
        """AC-033.11: No suitable page returns CDP_NO_PAGE."""
        mock_client = MagicMock()
        mock_client.evaluate.side_effect = ValueError("No suitable browser page found")
        mock_cdp_class.return_value = mock_client

        result = self._call_tool(script="1+1")

        assert result["success"] is False
        assert result["error"] == "CDP_NO_PAGE"

    # --- Script Evaluation Error Tests ---

    @patch('x_ipe.mcp.app_agent_interaction.CDPClient')
    def test_tool_script_error_returns_details(self, mock_cdp_class):
        """AC-033.13: Script runtime error returns exception details."""
        mock_client = MagicMock()
        mock_client.evaluate.return_value = {
            "id": 1,
            "result": {
                "exceptionDetails": {
                    "text": "Uncaught ReferenceError",
                    "exception": {
                        "description": "ReferenceError: foo is not defined\n    at <anonymous>:1:1"
                    }
                }
            }
        }
        mock_cdp_class.return_value = mock_client

        result = self._call_tool(script="foo.bar()")

        assert result["success"] is False
        assert result["error"] == "SCRIPT_EVALUATION_ERROR"
        assert "details" in result

    # --- Target URL and Port Tests ---

    @patch('x_ipe.mcp.app_agent_interaction.CDPClient')
    def test_tool_passes_target_url_to_cdp(self, mock_cdp_class):
        """AC-033.11: target_url is forwarded to CDPClient.evaluate."""
        mock_client = MagicMock()
        mock_client.evaluate.return_value = {
            "id": 1,
            "result": {"result": {"type": "undefined"}}
        }
        mock_cdp_class.return_value = mock_client

        self._call_tool(script="1+1", target_url="https://example.com")

        mock_client.evaluate.assert_called_once_with(
            "1+1", target_url="https://example.com"
        )

    @patch('x_ipe.mcp.app_agent_interaction.CDPClient')
    def test_tool_uses_custom_cdp_port(self, mock_cdp_class):
        """Custom CDP port is passed to CDPClient constructor."""
        mock_client = MagicMock()
        mock_client.evaluate.return_value = {
            "id": 1,
            "result": {"result": {"type": "undefined"}}
        }
        mock_cdp_class.return_value = mock_client

        self._call_tool(script="1+1", cdp_port=9333)

        mock_cdp_class.assert_called_once_with(port=9333)

    @patch('x_ipe.mcp.app_agent_interaction.CDPClient')
    def test_tool_default_cdp_port_is_9222(self, mock_cdp_class):
        """Default CDP port is 9222."""
        mock_client = MagicMock()
        mock_client.evaluate.return_value = {
            "id": 1,
            "result": {"result": {"type": "undefined"}}
        }
        mock_cdp_class.return_value = mock_client

        self._call_tool(script="1+1")

        mock_cdp_class.assert_called_once_with(port=9222)
