"""
Proxy Routes Blueprint

FEATURE-022-A: Browser Simulator & Proxy

Provides localhost URL proxying endpoint.
"""
from flask import Blueprint, jsonify, request

from x_ipe.services import ProxyService

proxy_bp = Blueprint('proxy', __name__)


@proxy_bp.route('/api/proxy', methods=['GET'])
def proxy_url():
    """
    GET /api/proxy?url=<encoded_url>
    
    Proxy a localhost URL and return modified HTML.
    
    Query Parameters:
        url (required): URL-encoded localhost URL
        
    Returns:
        JSON with success status and HTML content or error message
        
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
        return jsonify({
            'success': True,
            'html': result.html,
            'content_type': result.content_type
        })
    else:
        return jsonify({
            'success': False,
            'error': result.error
        }), result.status_code
