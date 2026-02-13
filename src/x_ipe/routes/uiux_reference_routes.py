"""
UIUX Reference Routes (FEATURE-033)

Flask blueprint for POST /api/ideas/uiux-reference endpoint.
"""
import os

from flask import Blueprint, jsonify, request, current_app

from x_ipe.services.uiux_reference_service import UiuxReferenceService
from x_ipe.tracing import x_ipe_tracing

uiux_reference_bp = Blueprint("uiux_reference", __name__)


@uiux_reference_bp.route("/api/ideas/uiux-reference", methods=["POST"])
@x_ipe_tracing()
def post_uiux_reference():
    """Save UIUX reference data to an idea folder."""
    project_root = current_app.config.get("PROJECT_ROOT", os.getcwd())
    service = UiuxReferenceService(project_root)

    data = request.json
    if not data:
        return jsonify({
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Request body must be JSON",
        }), 400

    result = service.save_reference(data)

    if not result.get("success"):
        status = 404 if result.get("error") == "IDEA_NOT_FOUND" else 400
        return jsonify(result), status

    return jsonify(result), 200
