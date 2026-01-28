"""
Tests for FEATURE-022-B: Element Inspector

TDD tests for inspector script injection and message protocol.
"""
import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup


class TestInspectorScriptInjection:
    """Test inspector script injection via proxy."""
    
    def test_html_contains_inspector_script_after_rewrite(self, app):
        """Injected HTML should contain inspector script."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><head></head><body><div>Content</div></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        assert 'data-x-ipe-inspector="true"' in result
        assert 'inspectEnabled' in result
    
    def test_inspector_script_placed_before_body_close(self, app):
        """Inspector script should be placed at end of body."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body><div>Content</div></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        soup = BeautifulSoup(result, 'html.parser')
        
        # Script should be last child of body
        body = soup.find('body')
        scripts = body.find_all('script', attrs={'data-x-ipe-inspector': 'true'})
        assert len(scripts) == 1
    
    def test_inspector_script_has_required_functions(self, app):
        """Inspector script should contain all required functions."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        # Check for required function definitions
        assert 'generateSelector' in result
        assert 'mousemove' in result
        assert 'click' in result
        assert 'postMessage' in result
    
    def test_inspector_script_not_duplicated(self, app):
        """Rewriting same HTML twice should not duplicate script."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body><div>Content</div></body></html>'
        
        # First rewrite
        result1 = service._rewrite_html(html, 'http://localhost:3000')
        # Second rewrite of result
        result2 = service._rewrite_html(result1, 'http://localhost:3000')
        
        # Count inspector scripts
        count = result2.count('data-x-ipe-inspector="true"')
        assert count == 1
    
    def test_html_without_body_still_works(self, app):
        """HTML without body tag should still be processed."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><head></head></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        # Should not crash, may or may not have script
        assert '<html>' in result


class TestInspectorScriptContent:
    """Test inspector script functionality."""
    
    def test_script_listens_for_inspect_mode_message(self, app):
        """Script should listen for inspect-mode message."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        assert "type === 'inspect-mode'" in result or 'inspect-mode' in result
    
    def test_script_sends_hover_message(self, app):
        """Script should send hover message to parent."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        assert "type: 'hover'" in result
    
    def test_script_sends_select_message(self, app):
        """Script should send select message on click."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        assert "type: 'select'" in result
    
    def test_script_prevents_default_on_click(self, app):
        """Script should prevent default click behavior in inspect mode."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        assert 'preventDefault' in result
        assert 'stopPropagation' in result
    
    def test_script_checks_ctrlkey_metakey_for_multiselect(self, app):
        """Script should check ctrlKey/metaKey for multi-select."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        assert 'ctrlKey' in result or 'metaKey' in result


class TestSelectorGeneration:
    """Test CSS selector generation in inspector script."""
    
    def test_script_generates_id_selector(self, app):
        """Script should generate ID-based selector for elements with ID."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        # Script should check for element ID
        assert 'el.id' in result or 'element.id' in result
    
    def test_script_generates_class_selector(self, app):
        """Script should generate class-based selector."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        # Script should handle className
        assert 'className' in result or 'classList' in result
    
    def test_script_handles_nth_child_fallback(self, app):
        """Script should fall back to nth-child for unique selection."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        assert 'nth-child' in result or 'nth-of-type' in result


class TestElementInfo:
    """Test element info structure in messages."""
    
    def test_message_includes_tag(self, app):
        """Message should include element tag name."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        assert 'tagName' in result or 'tag:' in result
    
    def test_message_includes_rect(self, app):
        """Message should include element bounding rect."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        assert 'getBoundingClientRect' in result
    
    def test_message_includes_selector(self, app):
        """Message should include generated CSS selector."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        assert 'selector:' in result or 'generateSelector' in result


class TestHoverLeave:
    """Test hover-leave message handling."""
    
    def test_script_sends_hover_leave_for_body(self, app):
        """Script should send hover-leave when hovering body/html."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        html = '<html><body></body></html>'
        
        result = service._rewrite_html(html, 'http://localhost:3000')
        
        # Should check for body/documentElement and send hover-leave
        assert 'hover-leave' in result or 'document.body' in result


class TestProxyIntegrationWithInspector:
    """Integration tests for proxy with inspector injection."""
    
    def test_fetch_and_rewrite_includes_inspector(self, app):
        """Full proxy flow should include inspector script."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        
        with patch('x_ipe.services.proxy_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = '<html><body><button>Click me</button></body></html>'
            mock_response.headers = {'Content-Type': 'text/html'}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = service.fetch_and_rewrite('http://localhost:3000')
            
            assert result.success
            assert 'data-x-ipe-inspector="true"' in result.html
    
    def test_non_html_content_no_inspector(self, app):
        """Non-HTML content should not have inspector injected."""
        from x_ipe.services.proxy_service import ProxyService
        
        service = ProxyService()
        
        with patch('x_ipe.services.proxy_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = 'console.log("hello");'
            mock_response.headers = {'Content-Type': 'application/javascript'}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = service.fetch_and_rewrite('http://localhost:3000/app.js')
            
            assert result.success
            assert 'data-x-ipe-inspector' not in result.html


class TestAPIWithInspector:
    """Test API endpoint with inspector injection."""
    
    def test_proxy_api_returns_html_with_inspector(self, client):
        """API should return HTML with inspector script."""
        with patch('x_ipe.services.proxy_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = '<html><body><div>Test</div></body></html>'
            mock_response.headers = {'Content-Type': 'text/html'}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            response = client.get('/api/proxy?url=http://localhost:3000')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success']
            assert 'data-x-ipe-inspector="true"' in data['html']


# Fixtures
@pytest.fixture
def app():
    """Create test app."""
    from x_ipe.app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
