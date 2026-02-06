"""
FEATURE-022-D: UI/UX Feedback Routes

API routes for submitting UI/UX feedback.
"""
from flask import Blueprint, request, jsonify, current_app
from ..services.uiux_feedback_service import UiuxFeedbackService
from x_ipe.tracing import x_ipe_tracing


uiux_feedback_bp = Blueprint('uiux_feedback', __name__)


@uiux_feedback_bp.route('/api/uiux-feedback', methods=['GET'])
@x_ipe_tracing()
def list_feedback():
    """
    List recent feedback entries.
    
    Query params:
        days: Number of days to look back (default 2)
    
    Returns:
        200: {"entries": [...]}
    """
    project_root = current_app.config.get('PROJECT_ROOT', '.')
    days = request.args.get('days', 2, type=int)
    
    service = UiuxFeedbackService(project_root)
    entries = service.list_feedback(days=days)
    
    return jsonify({'entries': entries}), 200


@uiux_feedback_bp.route('/api/uiux-feedback/<feedback_id>', methods=['DELETE'])
@x_ipe_tracing()
def delete_feedback(feedback_id):
    """
    Delete a feedback entry by ID.
    
    Path params:
        feedback_id: The feedback folder name/ID
    
    Returns:
        200: {"success": true}
        404: {"success": false, "error": "Feedback not found"}
        500: {"success": false, "error": "..."}
    """
    project_root = current_app.config.get('PROJECT_ROOT', '.')
    
    service = UiuxFeedbackService(project_root)
    result = service.delete_feedback(feedback_id)
    
    if result['success']:
        return jsonify(result), 200
    elif 'not found' in result.get('error', '').lower():
        return jsonify(result), 404
    else:
        return jsonify(result), 500


@uiux_feedback_bp.route('/api/uiux-feedback', methods=['POST'])
@x_ipe_tracing()
def submit_feedback():
    """
    Submit UI/UX feedback entry.
    
    Request body:
        {
            "name": "Feedback-20260128-120000",
            "url": "http://localhost:3000/page",
            "elements": ["button.submit", "div.form-group"],
            "screenshot": "data:image/png;base64,...",  # optional
            "description": "User feedback text"  # optional
        }
    
    Returns:
        201: {"success": true, "folder": "x-ipe-docs/uiux-feedback/...", "name": "..."}
        400: {"success": false, "error": "Missing required field: ..."}
        500: {"success": false, "error": "..."}
    """
    try:
        data = request.get_json()
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
    
    # Validate data exists
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # Validate required fields
    required = ['name', 'url', 'elements']
    for field in required:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
    
    # Get project root from config
    project_root = current_app.config.get('PROJECT_ROOT', '.')
    
    # Save feedback
    service = UiuxFeedbackService(project_root)
    result = service.save_feedback(data)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 500
