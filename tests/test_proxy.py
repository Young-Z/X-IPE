"""
Tests for FEATURE-022-A: Browser Simulator & Proxy

Tests cover:
- ProxyService: validate_url(), fetch_and_rewrite(), _rewrite_html(), _rewrite_url()
- Proxy routes: GET /api/proxy
- URL validation (localhost-only)
- HTML asset path rewriting
- Error handling (connection refused, timeout, invalid URL)
- Edge cases: empty URL, external URLs, various ports

TDD Status: Tests written before implementation - all should FAIL initially.
"""
import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Will be imported after implementation
# from x_ipe.services import ProxyService, ProxyResult
# from x_ipe.app import create_app


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def proxy_service():
    """Create ProxyService instance"""
    from x_ipe.services import ProxyService
    return ProxyService()


@pytest.fixture
def app():
    """Create Flask test app"""
    from x_ipe.app import create_app
    from x_ipe.config import TestingConfig
    app = create_app(TestingConfig)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_html():
    """Sample HTML with various asset references"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/styles/main.css">
    <link rel="stylesheet" href="styles/local.css">
    <script src="/js/app.js"></script>
    <style>
        body { background: url('/images/bg.png'); }
    </style>
</head>
<body>
    <img src="/images/logo.png" alt="Logo">
    <img src="images/icon.png" alt="Icon">
    <a href="/about">About</a>
    <script src="https://cdn.example.com/external.js"></script>
</body>
</html>
'''


@pytest.fixture
def sample_html_with_csp():
    """Sample HTML with CSP meta tag"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
    <title>Test</title>
</head>
<body>
    <p>Content</p>
</body>
</html>
'''


# ============================================================================
# ProxyService Unit Tests - URL Validation
# ============================================================================

class TestProxyServiceValidation:
    """Unit tests for ProxyService.validate_url()"""
    
    def test_validate_url_localhost_valid(self, proxy_service):
        """Valid localhost URL should pass validation"""
        valid, error = proxy_service.validate_url("http://localhost:3000/")
        assert valid is True
        assert error == ""
    
    def test_validate_url_127_0_0_1_valid(self, proxy_service):
        """Valid 127.0.0.1 URL should pass validation"""
        valid, error = proxy_service.validate_url("http://127.0.0.1:8080/dashboard")
        assert valid is True
        assert error == ""
    
    def test_validate_url_localhost_no_port_valid(self, proxy_service):
        """Localhost URL without port should be valid"""
        valid, error = proxy_service.validate_url("http://localhost/")
        assert valid is True
        assert error == ""
    
    def test_validate_url_localhost_with_path_valid(self, proxy_service):
        """Localhost URL with path should be valid"""
        valid, error = proxy_service.validate_url("http://localhost:3000/app/dashboard")
        assert valid is True
        assert error == ""
    
    def test_validate_url_external_invalid(self, proxy_service):
        """External URL should fail validation"""
        valid, error = proxy_service.validate_url("http://example.com/")
        assert valid is False
        assert "Only localhost URLs are supported" in error
    
    def test_validate_url_internal_network_invalid(self, proxy_service):
        """Internal network IP should fail validation"""
        valid, error = proxy_service.validate_url("http://192.168.1.100:3000/")
        assert valid is False
        assert "Only localhost URLs are supported" in error
    
    def test_validate_url_no_protocol_invalid(self, proxy_service):
        """URL without protocol should fail validation"""
        valid, error = proxy_service.validate_url("localhost:3000/")
        assert valid is False
        assert "protocol" in error or "Invalid URL" in error
    
    def test_validate_url_https_localhost_valid(self, proxy_service):
        """HTTPS localhost URL should be valid"""
        valid, error = proxy_service.validate_url("https://localhost:443/")
        assert valid is True
        assert error == ""
    
    def test_validate_url_empty_invalid(self, proxy_service):
        """Empty URL should fail validation"""
        valid, error = proxy_service.validate_url("")
        assert valid is False
    
    def test_validate_url_malformed_invalid(self, proxy_service):
        """Malformed URL should fail validation"""
        valid, error = proxy_service.validate_url("not a valid url")
        assert valid is False


# ============================================================================
# ProxyService Unit Tests - HTML Rewriting
# ============================================================================

class TestProxyServiceRewriting:
    """Unit tests for ProxyService HTML rewriting"""
    
    def test_rewrite_url_relative_path(self, proxy_service):
        """Relative path should be rewritten to proxy URL"""
        base_url = "http://localhost:3000/"
        result = proxy_service._rewrite_url("/styles/main.css", base_url)
        assert "/api/proxy?url=" in result
        assert "localhost%3A3000" in result or "localhost:3000" in result
    
    def test_rewrite_url_relative_no_slash(self, proxy_service):
        """Relative path without leading slash should be rewritten"""
        base_url = "http://localhost:3000/app/"
        result = proxy_service._rewrite_url("styles/local.css", base_url)
        assert "/api/proxy?url=" in result
    
    def test_rewrite_url_external_unchanged(self, proxy_service):
        """External URL should remain unchanged"""
        base_url = "http://localhost:3000/"
        result = proxy_service._rewrite_url("https://cdn.example.com/lib.js", base_url)
        assert result == "https://cdn.example.com/lib.js"
    
    def test_rewrite_url_data_uri_unchanged(self, proxy_service):
        """Data URI should remain unchanged"""
        base_url = "http://localhost:3000/"
        data_uri = "data:image/png;base64,iVBORw0KGgo="
        result = proxy_service._rewrite_url(data_uri, base_url)
        assert result == data_uri
    
    def test_rewrite_url_hash_unchanged(self, proxy_service):
        """Hash-only link should remain unchanged"""
        base_url = "http://localhost:3000/"
        result = proxy_service._rewrite_url("#section", base_url)
        assert result == "#section"
    
    def test_rewrite_html_script_src(self, proxy_service, sample_html):
        """Script src attributes should be rewritten"""
        result = proxy_service._rewrite_html(sample_html, "http://localhost:3000/")
        assert '/api/proxy?url=' in result
        # External CDN script should remain unchanged
        assert 'https://cdn.example.com/external.js' in result
    
    def test_rewrite_html_link_href(self, proxy_service, sample_html):
        """Link href attributes should be rewritten"""
        result = proxy_service._rewrite_html(sample_html, "http://localhost:3000/")
        assert '/api/proxy?url=' in result
    
    def test_rewrite_html_img_src(self, proxy_service, sample_html):
        """Image src attributes should be rewritten"""
        result = proxy_service._rewrite_html(sample_html, "http://localhost:3000/")
        # Check that localhost images are proxied
        assert result.count('/api/proxy?url=') >= 2  # At least CSS and images
    
    def test_rewrite_html_css_url(self, proxy_service, sample_html):
        """CSS url() references should be rewritten"""
        result = proxy_service._rewrite_html(sample_html, "http://localhost:3000/")
        # The background-url should be rewritten
        assert '/api/proxy?url=' in result
    
    def test_rewrite_html_strips_csp(self, proxy_service, sample_html_with_csp):
        """CSP meta tags should be removed"""
        result = proxy_service._rewrite_html(sample_html_with_csp, "http://localhost:3000/")
        assert 'Content-Security-Policy' not in result


# ============================================================================
# ProxyService Unit Tests - Fetch and Rewrite
# ============================================================================

class TestProxyServiceFetch:
    """Unit tests for ProxyService.fetch_and_rewrite()"""
    
    def test_fetch_and_rewrite_invalid_url_returns_error(self, proxy_service):
        """Invalid URL should return error result"""
        result = proxy_service.fetch_and_rewrite("http://example.com/")
        assert result.success is False
        assert "Only localhost" in result.error
        assert result.status_code == 400
    
    @patch('requests.get')
    def test_fetch_and_rewrite_connection_error(self, mock_get, proxy_service):
        """Connection refused should return appropriate error"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        result = proxy_service.fetch_and_rewrite("http://localhost:3000/")
        assert result.success is False
        assert "Cannot connect" in result.error or "Connection" in result.error
        assert result.status_code == 502
    
    @patch('requests.get')
    def test_fetch_and_rewrite_timeout(self, mock_get, proxy_service):
        """Timeout should return appropriate error"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = proxy_service.fetch_and_rewrite("http://localhost:3000/")
        assert result.success is False
        assert "timed out" in result.error.lower()
        assert result.status_code == 504
    
    @patch('requests.get')
    def test_fetch_and_rewrite_success(self, mock_get, proxy_service, sample_html):
        """Successful fetch should return rewritten HTML"""
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = proxy_service.fetch_and_rewrite("http://localhost:3000/")
        assert result.success is True
        assert result.html != ""
        assert result.content_type == "text/html"
    
    @patch('requests.get')
    def test_fetch_and_rewrite_non_html_unchanged(self, mock_get, proxy_service):
        """Non-HTML content should be returned as-is"""
        mock_response = Mock()
        mock_response.text = '{"key": "value"}'
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = proxy_service.fetch_and_rewrite("http://localhost:3000/api/data")
        assert result.success is True
        assert result.html == '{"key": "value"}'
        assert "json" in result.content_type
    
    @patch('requests.get')
    def test_fetch_and_rewrite_http_error(self, mock_get, proxy_service):
        """HTTP errors should be handled"""
        import requests
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        result = proxy_service.fetch_and_rewrite("http://localhost:3000/notfound")
        assert result.success is False
        assert result.status_code == 404


# ============================================================================
# Proxy Routes API Tests
# ============================================================================

class TestProxyRoutesAPI:
    """API tests for /api/proxy endpoint"""
    
    def test_proxy_missing_url_param(self, client):
        """GET /api/proxy without URL should return 400"""
        response = client.get('/api/proxy')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'URL' in data['error'] or 'url' in data['error'].lower()
    
    def test_proxy_empty_url_param(self, client):
        """GET /api/proxy with empty URL should return 400"""
        response = client.get('/api/proxy?url=')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_proxy_external_url_rejected(self, client):
        """GET /api/proxy with external URL should return 400"""
        response = client.get('/api/proxy?url=http%3A%2F%2Fexample.com%2F')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'localhost' in data['error'].lower()
    
    @patch('x_ipe.services.ProxyService.fetch_and_rewrite')
    def test_proxy_localhost_success(self, mock_fetch, client, sample_html):
        """GET /api/proxy with localhost URL should succeed"""
        from x_ipe.services import ProxyResult
        mock_fetch.return_value = ProxyResult(
            success=True,
            html=sample_html,
            content_type='text/html'
        )
        
        response = client.get('/api/proxy?url=http%3A%2F%2Flocalhost%3A3000%2F')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'html' in data
    
    @patch('x_ipe.services.ProxyService.fetch_and_rewrite')
    def test_proxy_connection_refused(self, mock_fetch, client):
        """GET /api/proxy with unreachable server should return 502"""
        from x_ipe.services import ProxyResult
        mock_fetch.return_value = ProxyResult(
            success=False,
            error="Cannot connect to localhost:3000. Is your dev server running?",
            status_code=502
        )
        
        response = client.get('/api/proxy?url=http%3A%2F%2Flocalhost%3A3000%2F')
        assert response.status_code == 502
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'connect' in data['error'].lower() or 'server' in data['error'].lower()
    
    @patch('x_ipe.services.ProxyService.fetch_and_rewrite')
    def test_proxy_timeout(self, mock_fetch, client):
        """GET /api/proxy timeout should return 504"""
        from x_ipe.services import ProxyResult
        mock_fetch.return_value = ProxyResult(
            success=False,
            error="Request timed out after 10 seconds",
            status_code=504
        )
        
        response = client.get('/api/proxy?url=http%3A%2F%2Flocalhost%3A3000%2F')
        assert response.status_code == 504
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'timed out' in data['error'].lower()
    
    def test_proxy_various_ports(self, client):
        """GET /api/proxy should accept various localhost ports"""
        # These will fail with connection error (expected) but should NOT fail validation
        ports = [80, 443, 3000, 5173, 8080, 9000]
        for port in ports:
            response = client.get(f'/api/proxy?url=http%3A%2F%2Flocalhost%3A{port}%2F')
            data = json.loads(response.data)
            # Should NOT be a validation error (400), may be connection error (502)
            assert response.status_code != 400 or 'localhost' not in data.get('error', '').lower()


# ============================================================================
# Integration Tests - Full Proxy Flow
# ============================================================================

class TestProxyIntegration:
    """Integration tests for complete proxy flow"""
    
    @patch('requests.get')
    def test_full_proxy_flow_html_page(self, mock_get, client, sample_html):
        """Full flow: client request → proxy → fetch → rewrite → response"""
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'Content-Type': 'text/html; charset=utf-8'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = client.get('/api/proxy?url=http%3A%2F%2Flocalhost%3A3000%2F')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify HTML was rewritten
        html = data['html']
        assert '/api/proxy?url=' in html  # Assets should be proxied
        assert 'https://cdn.example.com/external.js' in html  # External unchanged
    
    @patch('requests.get')
    def test_full_proxy_flow_with_subpath(self, mock_get, client):
        """Proxy should handle URLs with subpaths correctly"""
        mock_response = Mock()
        mock_response.text = '<html><body><img src="./image.png"></body></html>'
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = client.get('/api/proxy?url=http%3A%2F%2Flocalhost%3A3000%2Fapp%2Fpage')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # The relative path ./image.png should be resolved relative to /app/page
        assert '/api/proxy?url=' in data['html']


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestProxyEdgeCases:
    """Edge case tests for proxy service"""
    
    def test_proxy_url_with_query_params(self, proxy_service):
        """URL with query parameters should be valid"""
        valid, error = proxy_service.validate_url("http://localhost:3000/api?foo=bar&baz=qux")
        assert valid is True
    
    def test_proxy_url_with_fragment(self, proxy_service):
        """URL with fragment should be valid"""
        valid, error = proxy_service.validate_url("http://localhost:3000/page#section")
        assert valid is True
    
    def test_proxy_url_with_unicode_path(self, proxy_service):
        """URL with unicode in path should be handled"""
        # This may or may not be valid depending on implementation
        valid, error = proxy_service.validate_url("http://localhost:3000/路径")
        # Should at least not crash
        assert isinstance(valid, bool)
    
    def test_rewrite_html_empty_content(self, proxy_service):
        """Empty HTML should not crash"""
        result = proxy_service._rewrite_html("", "http://localhost:3000/")
        assert result == "" or result is not None
    
    def test_rewrite_html_malformed(self, proxy_service):
        """Malformed HTML should be handled gracefully"""
        malformed = "<html><body><p>No closing tags"
        result = proxy_service._rewrite_html(malformed, "http://localhost:3000/")
        assert result is not None  # Should not crash
    
    def test_rewrite_html_no_assets(self, proxy_service):
        """HTML without any assets should pass through"""
        simple = "<html><body><p>Just text</p></body></html>"
        result = proxy_service._rewrite_html(simple, "http://localhost:3000/")
        assert "Just text" in result
    
    @patch('requests.get')
    def test_proxy_large_response(self, mock_get, proxy_service):
        """Large HTML response should be handled"""
        large_html = "<html><body>" + "x" * 1000000 + "</body></html>"
        mock_response = Mock()
        mock_response.text = large_html
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = proxy_service.fetch_and_rewrite("http://localhost:3000/")
        assert result.success is True
        assert len(result.html) > 1000000


# ============================================================================
# Test Coverage Summary
# ============================================================================

"""
Test Coverage Summary for FEATURE-022-A

| Component | Unit Tests | Integration | API Tests | Total |
|-----------|------------|-------------|-----------|-------|
| ProxyService.validate_url | 10 | - | - | 10 |
| ProxyService._rewrite_* | 6 | - | - | 6 |
| ProxyService.fetch_and_rewrite | 6 | - | - | 6 |
| /api/proxy endpoint | - | - | 7 | 7 |
| Full proxy flow | - | 2 | - | 2 |
| Edge cases | 6 | - | - | 6 |
| **TOTAL** | **28** | **2** | **7** | **37** |

TDD Ready State:
- All tests should FAIL because ProxyService and proxy_routes.py don't exist yet
- Tests are ready for Code Implementation phase

Acceptance Criteria Coverage:
- AC-16, AC-17, AC-18: URL validation tests
- AC-19, AC-20, AC-21, AC-22, AC-23: Asset rewriting tests
- AC-24, AC-25, AC-26, AC-27: Error handling tests
"""
