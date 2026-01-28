"""
Proxy Service for FEATURE-022-A

Provides localhost URL proxying with asset path rewriting.
"""
import re
import requests
from urllib.parse import urlparse, urljoin, quote
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Tuple

ALLOWED_HOSTS = {'localhost', '127.0.0.1'}
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


@dataclass
class ProxyResult:
    """Result from proxy fetch operation."""
    success: bool
    html: str = ""
    content_type: str = "text/html"
    error: str = ""
    status_code: int = 200


class ProxyService:
    """Service for proxying localhost URLs."""
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate URL is localhost only.
        
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
                return False, "URL must include protocol (http:// or https://)"
            
            if parsed.scheme not in ('http', 'https'):
                return False, "Only http:// and https:// protocols are supported"
            
            if not parsed.hostname:
                return False, "Invalid URL format"
            
            if parsed.hostname not in ALLOWED_HOSTS:
                return False, "Only localhost URLs are supported"
            
            return True, ""
        except Exception as e:
            return False, f"Invalid URL format: {str(e)}"
    
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
        
        # Fetch
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
        
        # Only rewrite HTML
        if 'text/html' in content_type:
            html = self._rewrite_html(response.text, url)
            return ProxyResult(success=True, html=html, content_type=content_type)
        else:
            # Return non-HTML content as-is
            return ProxyResult(
                success=True,
                html=response.text,
                content_type=content_type
            )
    
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
