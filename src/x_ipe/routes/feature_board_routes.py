"""Feature Board API Routes — read-only endpoints for feature queries.

Blueprint: feature_board_bp
Endpoints:
  GET /api/features/list           — filtered, paginated feature list
  GET /api/features/get/<id>       — single feature by ID
  GET /api/features/epic-summary   — per-epic status counts

Location: src/x_ipe/routes/feature_board_routes.py
Feature: FEATURE-056-B
"""

from __future__ import annotations

import logging

from flask import Blueprint, current_app, jsonify, request

from x_ipe.services.feature_board_service import FeatureBoardService
from x_ipe.tracing import x_ipe_tracing

logger = logging.getLogger(__name__)

feature_board_bp = Blueprint("feature_board", __name__)


# ------------------------------------------------------------------
# Error handling
# ------------------------------------------------------------------


@feature_board_bp.errorhandler(Exception)
def handle_error(e: Exception):
    """Return structured JSON for any unhandled exception."""
    logger.exception("Unhandled error in feature board route: %s", e)
    return jsonify({
        "success": False,
        "error": "INTERNAL_ERROR",
        "message": str(e) or "Internal server error",
    }), 500


@feature_board_bp.after_request
def set_no_cache(response):
    """Prevent caching of volatile feature data."""
    response.headers["Cache-Control"] = "no-store"
    return response


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _get_service() -> FeatureBoardService:
    import os
    project_root = current_app.config.get("PROJECT_ROOT", os.getcwd())
    return FeatureBoardService(project_root)


def _parse_int(value: str | None, name: str, default: int) -> tuple[int | None, str | None]:
    """Parse an integer query param. Returns (value, error_message)."""
    if value is None:
        return default, None
    try:
        n = int(value)
    except (ValueError, TypeError):
        return None, f"'{name}' must be an integer, got '{value}'"
    if n < 1:
        return None, f"'{name}' must be >= 1, got {n}"
    return n, None


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------


@feature_board_bp.route("/api/features/list", methods=["GET"])
@x_ipe_tracing()
def list_features():
    """Return filtered, paginated feature list."""
    page, err = _parse_int(request.args.get("page"), "page", 1)
    if err:
        return jsonify({"success": False, "error": "VALIDATION_ERROR", "message": err}), 400

    page_size, err = _parse_int(request.args.get("page_size"), "page_size", 50)
    if err:
        return jsonify({"success": False, "error": "VALIDATION_ERROR", "message": err}), 400

    epic_id = request.args.get("epic_id")
    status = request.args.get("status")
    search = request.args.get("search")

    result = _get_service().list_features(epic_id, status, search, page, page_size)
    return jsonify(result), 200


@feature_board_bp.route("/api/features/get/<feature_id>", methods=["GET"])
@x_ipe_tracing()
def get_feature(feature_id: str):
    """Return a single feature by ID."""
    result = _get_service().get_feature(feature_id)
    if result.get("success"):
        return jsonify(result), 200
    return jsonify(result), 404


@feature_board_bp.route("/api/features/epic-summary", methods=["GET"])
@x_ipe_tracing()
def epic_summary():
    """Return per-epic status count summary."""
    epic_id = request.args.get("epic_id")
    result = _get_service().epic_summary(epic_id)
    return jsonify(result), 200
