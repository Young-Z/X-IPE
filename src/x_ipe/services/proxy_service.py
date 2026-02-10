"""
Proxy Service for FEATURE-022-A and FEATURE-022-B

Provides localhost URL proxying with asset path rewriting and inspector script injection.
"""
import mimetypes
import os
import re
import requests
from urllib.parse import urlparse, urljoin, quote, unquote
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Tuple

from x_ipe.tracing import x_ipe_tracing

ALLOWED_HOSTS = {'localhost', '127.0.0.1'}
ALLOWED_SCHEMES = {'http', 'https', 'file'}
PROXY_TIMEOUT = 10  # seconds
REWRITE_ATTRIBUTES = {
    'script': 'src',
    'link': 'href',
    'img': 'src',
    'a': 'href',
    'source': 'src',
    'video': 'src',
    'audio': 'src',
}

# FEATURE-022-B: Inspector script injected into proxied HTML
INSPECTOR_SCRIPT = '''
<script data-x-ipe-inspector="true">
(function() {
    let inspectEnabled = false;
    
    window.addEventListener('message', function(e) {
        if (e.data && e.data.type === 'inspect-mode') {
            inspectEnabled = e.data.enabled;
        }
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!inspectEnabled) return;
        const el = document.elementFromPoint(e.clientX, e.clientY);
        if (!el || el === document.body || el === document.documentElement) {
            window.parent.postMessage({type: 'hover-leave'}, '*');
            return;
        }
        window.parent.postMessage({
            type: 'hover',
            element: {
                tag: el.tagName.toLowerCase(),
                className: (el.className || '').toString().split(' ')[0] || '',
                id: el.id || '',
                selector: generateSelector(el),
                rect: el.getBoundingClientRect()
            }
        }, '*');
    }, true);
    
    document.addEventListener('click', function(e) {
        if (!inspectEnabled) return;
        e.preventDefault();
        e.stopPropagation();
        const el = e.target;
        window.parent.postMessage({
            type: 'select',
            element: {
                tag: el.tagName.toLowerCase(),
                className: (el.className || '').toString().split(' ')[0] || '',
                id: el.id || '',
                selector: generateSelector(el),
                rect: el.getBoundingClientRect()
            },
            multiSelect: e.ctrlKey || e.metaKey
        }, '*');
    }, true);
    
    // FEATURE-022-C: Right-click context menu
    document.addEventListener('contextmenu', function(e) {
        console.log('[X-IPE Inspector] contextmenu event, inspectEnabled:', inspectEnabled);
        if (!inspectEnabled) return;
        e.preventDefault();
        e.stopPropagation();
        console.log('[X-IPE Inspector] sending contextmenu postMessage');
        // Send coordinates to parent for showing context menu
        window.parent.postMessage({
            type: 'contextmenu',
            x: e.screenX,
            y: e.screenY,
            clientX: e.clientX,
            clientY: e.clientY
        }, '*');
    }, true);
    
    function generateSelector(el) {
        if (el.id) return '#' + el.id;
        const tag = el.tagName.toLowerCase();
        const cls = (el.className || '').toString().split(' ')[0];
        if (cls) {
            const siblings = el.parentElement ? el.parentElement.querySelectorAll(tag + '.' + cls) : [];
            if (siblings.length === 1) return tag + '.' + cls;
            const idx = Array.from(siblings).indexOf(el);
            return tag + '.' + cls + ':nth-of-type(' + (idx + 1) + ')';
        }
        const siblings = el.parentElement ? el.parentElement.children : [];
        const idx = Array.from(siblings).indexOf(el);
        return tag + ':nth-child(' + (idx + 1) + ')';
    }
})();
</script>
'''

# TASK-236: Fetch/XHR interceptor injected into proxied HTML.
# In srcdoc iframes, relative fetch('/api/...') calls resolve to the host origin
# instead of the proxied target. This script intercepts fetch and XMLHttpRequest
# to route them through the proxy endpoint.
FETCH_INTERCEPTOR_TEMPLATE = '''
<script data-x-ipe-fetch-interceptor="true">
(function() {{
    var TARGET_ORIGIN = '{target_origin}';
    var PROXY_PATH = '/api/proxy?url=';

    function buildProxyUrl(input) {{
        var url;
        if (typeof input === 'string') {{
            url = input;
        }} else if (input instanceof Request) {{
            url = input.url;
        }} else if (input instanceof URL) {{
            url = input.href;
        }} else {{
            return null;
        }}
        // Skip already-proxied URLs and absolute external URLs
        if (url.indexOf(PROXY_PATH) !== -1) return null;
        if (url.indexOf('data:') === 0 || url.indexOf('blob:') === 0) return null;
        // Handle relative URLs (starting with /)
        if (url.charAt(0) === '/') {{
            return PROXY_PATH + encodeURIComponent(TARGET_ORIGIN + url);
        }}
        // Handle relative URLs without leading slash
        if (url.indexOf('://') === -1 && url.indexOf('//') !== 0) {{
            return PROXY_PATH + encodeURIComponent(TARGET_ORIGIN + '/' + url);
        }}
        return null;
    }}

    // Intercept fetch
    var originalFetch = window.fetch;
    window.fetch = function(input, init) {{
        var proxied = buildProxyUrl(input);
        if (proxied) {{
            if (typeof input === 'string') {{
                return originalFetch.call(this, proxied, init);
            }} else if (input instanceof Request) {{
                var newReq = new Request(proxied, input);
                return originalFetch.call(this, newReq, init);
            }}
        }}
        return originalFetch.call(this, input, init);
    }};

    // Intercept XMLHttpRequest
    var originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {{
        var proxied = buildProxyUrl(url);
        if (proxied) {{
            arguments[1] = proxied;
        }}
        return originalOpen.apply(this, arguments);
    }};
}})();
</script>
'''


@dataclass
class ProxyResult:
    """Result from proxy fetch operation."""
    success: bool
    html: str = ""
    content_type: str = "text/html"
    error: str = ""
    status_code: int = 200
    binary_content: bytes = None  # TASK-235: For binary files like fonts


# TASK-235: Binary content types that should not be decoded as text
BINARY_CONTENT_TYPES = {
    'font/', 'image/', 'audio/', 'video/',
    'application/octet-stream', 'application/font', 'application/x-font',
}


def _is_binary_content_type(content_type: str) -> bool:
    """Check if content type represents binary data."""
    if not content_type:
        return False
    content_type = content_type.lower()
    for binary_type in BINARY_CONTENT_TYPES:
        if binary_type in content_type:
            return True
    return False


class ProxyService:
    """Service for proxying localhost URLs."""
    
    @x_ipe_tracing()
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate URL is localhost or local file.
        
        Args:
            url: URL string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url or not url.strip():
            return False, "URL cannot be empty"
        
        try:
            parsed = urlparse(url)
            
            if not parsed.scheme:
                return False, "URL must include protocol (http://, https://, or file://)"
            
            if parsed.scheme not in ALLOWED_SCHEMES:
                return False, "Only http://, https://, and file:// protocols are supported"
            
            # For file:// URLs, validate path exists
            if parsed.scheme == 'file':
                file_path = unquote(parsed.path)
                if not os.path.isfile(file_path):
                    return False, f"File not found: {file_path}"
                return True, ""
            
            # For http/https, validate localhost
            if not parsed.hostname:
                return False, "Invalid URL format"
            
            if parsed.hostname not in ALLOWED_HOSTS:
                return False, "Only localhost URLs are supported"
            
            return True, ""
        except Exception as e:
            return False, f"Invalid URL format: {str(e)}"
    
    @x_ipe_tracing()
    def fetch_and_rewrite(self, url: str) -> ProxyResult:
        """
        Fetch URL and rewrite asset paths for proxy.
        
        Args:
            url: Localhost URL to fetch
            
        Returns:
            ProxyResult with HTML content or error
        """
        # Validate
        valid, error = self.validate_url(url)
        if not valid:
            return ProxyResult(success=False, error=error, status_code=400)
        
        parsed = urlparse(url)
        
        # Handle file:// URLs
        if parsed.scheme == 'file':
            return self._fetch_local_file(url)
        
        # Fetch HTTP/HTTPS
        try:
            response = requests.get(url, timeout=PROXY_TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            return ProxyResult(
                success=False,
                error=f"Cannot connect to {url}. Is your dev server running?",
                status_code=502
            )
        except requests.exceptions.Timeout:
            return ProxyResult(
                success=False,
                error="Request timed out after 10 seconds",
                status_code=504
            )
        except requests.exceptions.HTTPError as e:
            return ProxyResult(
                success=False,
                error=f"HTTP error: {e.response.status_code}",
                status_code=e.response.status_code
            )
        
        content_type = response.headers.get('Content-Type', 'text/html')
        
        # TASK-235: Handle binary content (fonts, images, etc.) without decoding
        if _is_binary_content_type(content_type):
            return ProxyResult(
                success=True,
                binary_content=response.content,
                content_type=content_type
            )
        
        # Only rewrite HTML
        if 'text/html' in content_type:
            html = self._rewrite_html(response.text, url)
            return ProxyResult(success=True, html=html, content_type=content_type)
        # TASK-235: Rewrite CSS url() references for font files
        elif 'text/css' in content_type:
            css = self._rewrite_css_urls(response.text, url)
            return ProxyResult(success=True, html=css, content_type=content_type)
        else:
            # Return text content as-is
            return ProxyResult(
                success=True,
                html=response.text,
                content_type=content_type
            )
    
    def _fetch_local_file(self, url: str) -> ProxyResult:
        """
        Read a local file for file:// URLs.
        
        Args:
            url: file:// URL
            
        Returns:
            ProxyResult with file content
        """
        parsed = urlparse(url)
        file_path = unquote(parsed.path)
        
        try:
            # Determine content type from file extension
            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or 'text/html'
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Only rewrite HTML
            if 'text/html' in content_type or file_path.endswith('.html'):
                html = self._rewrite_html(content, url)
                return ProxyResult(success=True, html=html, content_type='text/html')
            else:
                return ProxyResult(success=True, html=content, content_type=content_type)
                
        except UnicodeDecodeError:
            # Binary file - read as bytes
            try:
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='replace')
                return ProxyResult(success=True, html=content, content_type=content_type)
            except Exception as e:
                return ProxyResult(success=False, error=f"Failed to read file: {str(e)}", status_code=500)
        except Exception as e:
            return ProxyResult(success=False, error=f"Failed to read file: {str(e)}", status_code=500)
    
    def _rewrite_html(self, html: str, base_url: str) -> str:
        """
        Rewrite relative asset paths to proxy URLs.
        
        Args:
            html: Original HTML content
            base_url: Base URL for resolving relative paths
            
        Returns:
            Modified HTML with rewritten asset paths
        """
        if not html:
            return html
            
        soup = BeautifulSoup(html, 'html.parser')
        
        for tag, attr in REWRITE_ATTRIBUTES.items():
            for element in soup.find_all(tag):
                if element.get(attr):
                    element[attr] = self._rewrite_url(element[attr], base_url)
        
        # Handle inline CSS url() references in style tags
        for style in soup.find_all('style'):
            if style.string:
                style.string = self._rewrite_css_urls(style.string, base_url)
        
        # Strip CSP headers via meta tag
        for meta in soup.find_all('meta', attrs={'http-equiv': 'Content-Security-Policy'}):
            meta.decompose()
        
        # FEATURE-022-B: Inject inspector script into body (if not already present)
        body = soup.find('body')
        if body and not soup.find('script', attrs={'data-x-ipe-inspector': 'true'}):
            inspector_soup = BeautifulSoup(INSPECTOR_SCRIPT, 'html.parser')
            body.append(inspector_soup)
        
        # TASK-236: Inject fetch/XHR interceptor to route API calls through proxy
        if body and not soup.find('script', attrs={'data-x-ipe-fetch-interceptor': 'true'}):
            parsed = urlparse(base_url)
            target_origin = f"{parsed.scheme}://{parsed.netloc}"
            interceptor_html = FETCH_INTERCEPTOR_TEMPLATE.format(target_origin=target_origin)
            interceptor_soup = BeautifulSoup(interceptor_html, 'html.parser')
            # Insert before other scripts so fetch is intercepted early
            body.insert(0, interceptor_soup)
        
        return str(soup)
    
    def _rewrite_url(self, url: str, base_url: str) -> str:
        """
        Rewrite a single URL to proxy format.
        
        Args:
            url: URL or path to rewrite
            base_url: Base URL for resolving relative paths
            
        Returns:
            Rewritten URL (proxied if localhost, unchanged otherwise)
        """
        if not url or url.startswith('data:') or url.startswith('#'):
            return url
        
        # Make absolute
        absolute_url = urljoin(base_url, url)
        parsed = urlparse(absolute_url)
        
        # Only proxy localhost URLs
        if parsed.hostname in ALLOWED_HOSTS:
            return f"/api/proxy?url={quote(absolute_url, safe='')}"
        
        return url  # External URLs unchanged
    
    def _rewrite_css_urls(self, css: str, base_url: str) -> str:
        """
        Rewrite url() references in CSS.
        
        Args:
            css: CSS content
            base_url: Base URL for resolving relative paths
            
        Returns:
            CSS with rewritten URL references
        """
        def replace_url(match):
            url = match.group(1).strip('\'"')
            rewritten = self._rewrite_url(url, base_url)
            return f"url('{rewritten}')"
        
        return re.sub(r'url\(([^)]+)\)', replace_url, css)
