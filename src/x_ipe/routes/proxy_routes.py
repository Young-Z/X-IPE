"""
Proxy Routes Blueprint

FEATURE-022-A: Browser Simulator & Proxy

Provides localhost URL proxying endpoint.
"""
from flask import Blueprint, jsonify, request, Response

from x_ipe.services import ProxyService

proxy_bp = Blueprint('proxy', __name__)


@proxy_bp.route('/api/proxy', methods=['GET'])
def proxy_url():
    """
    GET /api/proxy?url=<encoded_url>
    
    Proxy a localhost URL and return content.
    
    For HTML: Returns JSON with rewritten HTML (for iframe srcdoc)
    For non-HTML (JS/CSS/images): Returns raw content with proper Content-Type
    
    Query Parameters:
        url (required): URL-encoded localhost URL
        
    Returns:
        JSON for HTML, raw content for other types
        
    Status Codes:
        200: Success
        400: Invalid URL or missing parameter
        502: Connection refused (server not running)
        504: Request timeout
    """
    url = request.args.get('url')
    
    if not url:
        return jsonify({
            'success': False,
            'error': 'URL parameter is required'
        }), 400
    
    service = ProxyService()
    result = service.fetch_and_rewrite(url)
    
    if result.success:
        # For HTML, return JSON (used by frontend to set iframe.srcdoc)
        if 'text/html' in result.content_type:
            return jsonify({
                'success': True,
                'html': result.html,
                'content_type': result.content_type
            })
        else:
            # For non-HTML (JS, CSS, images, etc.), return raw content
            return Response(
                result.html,  # Contains raw content for non-HTML
                mimetype=result.content_type.split(';')[0].strip()
            )
    else:
        return jsonify({
            'success': False,
            'error': result.error
        }), result.status_code
