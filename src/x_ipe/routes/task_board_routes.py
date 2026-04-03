"""Task Board API Routes — read-only endpoints for task queries.

Blueprint: task_board_bp
Endpoints:
  GET /api/tasks/list   — filtered, paginated task list
  GET /api/tasks/get/<task_id> — single task by ID

Location: src/x_ipe/routes/task_board_routes.py
Feature: FEATURE-055-C
"""

from __future__ import annotations

import logging

from flask import Blueprint, current_app, jsonify, request

from x_ipe.services.task_board_service import TaskBoardService
from x_ipe.tracing import x_ipe_tracing

logger = logging.getLogger(__name__)

task_board_bp = Blueprint("task_board", __name__)

_VALID_RANGES = frozenset({"1w", "1m", "all"})


# ------------------------------------------------------------------
# Error handling
# ------------------------------------------------------------------


@task_board_bp.errorhandler(Exception)
def handle_error(e: Exception):
    """Return structured JSON for any unhandled exception."""
    logger.exception("Unhandled error in task board route: %s", e)
    return jsonify({
        "success": False,
        "error": "INTERNAL_ERROR",
        "message": str(e) or "Internal server error",
    }), 500


@task_board_bp.after_request
def set_no_cache(response):
    """Prevent caching of volatile task data."""
    response.headers["Cache-Control"] = "no-store"
    return response


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _get_service() -> TaskBoardService:
    import os
    project_root = current_app.config.get("PROJECT_ROOT", os.getcwd())
    return TaskBoardService(project_root)


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


@task_board_bp.route("/api/tasks/list", methods=["GET"])
@x_ipe_tracing()
def list_tasks():
    """Return filtered, paginated task list."""
    range_str = request.args.get("range", "1w")
    if range_str not in _VALID_RANGES:
        return jsonify({
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": f"'range' must be one of {sorted(_VALID_RANGES)}, got '{range_str}'",
        }), 400

    page, err = _parse_int(request.args.get("page"), "page", 1)
    if err:
        return jsonify({"success": False, "error": "VALIDATION_ERROR", "message": err}), 400

    page_size, err = _parse_int(request.args.get("page_size"), "page_size", 50)
    if err:
        return jsonify({"success": False, "error": "VALIDATION_ERROR", "message": err}), 400

    status = request.args.get("status")
    search = request.args.get("search")

    result = _get_service().list_tasks(range_str, status, search, page, page_size)
    return jsonify(result), 200


@task_board_bp.route("/api/tasks/get/<task_id>", methods=["GET"])
@x_ipe_tracing()
def get_task(task_id: str):
    """Return a single task by ID."""
    result = _get_service().get_task(task_id)
    if result.get("success"):
        return jsonify(result), 200
    return jsonify(result), 404
