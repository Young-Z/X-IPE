"""
FEATURE-023: Application Action Tracing - Core

Tracing API routes for controlling tracing and viewing logs.

Provides REST endpoints for:
- GET /api/tracing/status - Get tracing configuration
- POST /api/tracing/start - Start tracing for duration
- POST /api/tracing/stop - Stop tracing immediately
- GET /api/tracing/logs - List trace log files
- DELETE /api/tracing/logs - Delete all trace logs
"""
from flask import Blueprint, request, jsonify, current_app
from pathlib import Path

from x_ipe.services.tracing_service import TracingService
from x_ipe.tracing import x_ipe_tracing


tracing_bp = Blueprint('tracing', __name__, url_prefix='/api/tracing')


def get_service() -> TracingService:
    """Get TracingService instance for current app."""
    project_root = current_app.config.get('PROJECT_ROOT', '.')
    return TracingService(project_root)


@tracing_bp.route('/status', methods=['GET'])
@x_ipe_tracing()
def get_status():
    """
    GET /api/tracing/status
    
    Get current tracing configuration and status.
    
    Response:
        {
            "enabled": false,
            "stop_at": "2026-02-01T03:30:00Z",
            "log_path": "instance/traces/",
            "retention_hours": 24,
            "ignored_apis": [],
            "active": true
        }
    """
    service = get_service()
    config = service.get_config()
    config["active"] = service.is_active()
    return jsonify(config)


@tracing_bp.route('/start', methods=['POST'])
@x_ipe_tracing()
def start_tracing():
    """
    POST /api/tracing/start
    
    Start tracing for specified duration.
    
    Request:
        {
            "duration_minutes": 3 | 15 | 30
        }
    
    Response:
        {
            "success": true,
            "stop_at": "2026-02-01T03:33:00Z"
        }
    
    Errors:
        400 - Invalid duration (must be 3, 15, or 30)
    """
    data = request.get_json() or {}
    duration = data.get('duration_minutes', 3)
    
    try:
        service = get_service()
        result = service.start(duration)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@tracing_bp.route('/stop', methods=['POST'])
@x_ipe_tracing()
def stop_tracing():
    """
    POST /api/tracing/stop
    
    Stop tracing immediately.
    
    Response:
        {
            "success": true
        }
    """
    service = get_service()
    result = service.stop()
    return jsonify(result)


@tracing_bp.route('/logs', methods=['GET'])
@x_ipe_tracing()
def list_logs():
    """
    GET /api/tracing/logs
    
    List all trace log files.
    
    Response:
        [
            {
                "trace_id": "abc-123",
                "filename": "20260201-033000-post-api-orders-abc-123.log",
                "size": 1234,
                "timestamp": "2026-02-01T03:30:00"
            }
        ]
    """
    service = get_service()
    logs = service.list_logs()
    return jsonify(logs)


@tracing_bp.route('/logs', methods=['DELETE'])
@x_ipe_tracing()
def delete_logs():
    """
    DELETE /api/tracing/logs
    
    Delete all trace log files.
    
    Response:
        {
            "deleted": 5
        }
    """
    service = get_service()
    deleted = service.delete_all_logs()
    return jsonify({"deleted": deleted})


@tracing_bp.route('/logs/<trace_id>', methods=['GET'])
@x_ipe_tracing()
def get_trace(trace_id):
    """
    GET /api/tracing/logs/<trace_id>
    
    Get parsed trace data for DAG visualization.
    
    Response:
        {
            "trace_id": "abc-123",
            "api": "POST /api/orders",
            "timestamp": "2026-02-01T03:30:00",
            "total_time_ms": 245,
            "status": "success",
            "nodes": [
                {
                    "id": "node-0",
                    "label": "POST /api/orders",
                    "timing": "245ms",
                    "status": "success",
                    "level": "API",
                    "input": "{}",
                    "output": "{}",
                    "error": null
                }
            ],
            "edges": [
                {"source": "node-0", "target": "node-1"}
            ],
            "filename": "20260201-post-api-orders-abc123.log"
        }
        
    Errors:
        404 - Trace not found
    """
    service = get_service()
    result = service.get_trace(trace_id)
    
    if result is None:
        return jsonify({"error": f"Trace not found: {trace_id}"}), 404
    
    return jsonify(result)


@tracing_bp.route('/ignored', methods=['GET'])
@x_ipe_tracing()
def get_ignored_apis():
    """
    GET /api/tracing/ignored
    
    Get list of ignored API patterns.
    
    Response:
        {
            "patterns": ["/api/health/*", "/api/status"]
        }
    """
    service = get_service()
    config = service.get_config()
    return jsonify({"patterns": config.get("ignored_apis", [])})


@tracing_bp.route('/ignored', methods=['POST'])
@x_ipe_tracing()
def update_ignored_apis():
    """
    POST /api/tracing/ignored
    
    Update list of ignored API patterns.
    
    Request:
        {
            "patterns": ["/api/health/*", "/api/status"]
        }
    
    Response:
        {
            "success": true
        }
    """
    data = request.get_json() or {}
    patterns = data.get('patterns', [])
    
    service = get_service()
    service.update_ignored_apis(patterns)
    
    return jsonify({"success": True})
