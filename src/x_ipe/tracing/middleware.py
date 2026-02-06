"""
FEATURE-023: Application Action Tracing - Middleware

Flask middleware for automatic request tracing.

Creates TraceContext for each request when tracing is active,
then writes the trace log file after the request completes.
"""
import time
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, g
from typing import List

from .context import TraceContext
from .writer import TraceLogWriter


# APIs to ignore (to avoid infinite loops and noise)
IGNORED_API_PREFIXES = (
    '/api/tracing/',      # Tracing APIs themselves
    '/static/',           # Static files
    '/socket.io/',        # WebSocket
)


def init_tracing_middleware(app: Flask) -> None:
    """
    Initialize tracing middleware for a Flask app.
    
    Registers before_request and after_request hooks that:
    - Check if tracing is active
    - Start TraceContext before each request
    - End TraceContext and write log file after each request
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def start_trace():
        """Start trace context if tracing is active."""
        # Skip hardcoded ignored paths (system paths)
        if request.path.startswith(IGNORED_API_PREFIXES):
            return
        
        # Check if tracing is active and get config
        project_root = app.config.get('PROJECT_ROOT', '.')
        active, ignored_apis = _get_tracing_config(project_root)
        
        if not active:
            return
        
        # Skip user-configured ignored APIs
        if _is_path_ignored(request.path, ignored_apis):
            return
        
        # Start trace context
        api_name = f"{request.method} {request.path}"
        TraceContext.start_trace(api_name)
        g.trace_start_time = time.perf_counter()
    
    @app.after_request
    def end_trace(response):
        """End trace context and write log file."""
        # Check if we started a trace
        if not hasattr(g, 'trace_start_time'):
            return response
        
        # End the trace
        buffer = TraceContext.end_trace()
        if buffer is None:
            return response
        
        # Determine status from response
        status = "SUCCESS" if response.status_code < 400 else "ERROR"
        
        # Get log path from config
        project_root = app.config.get('PROJECT_ROOT', '.')
        log_path = _get_trace_log_path(project_root)
        
        # Write trace to file
        writer = TraceLogWriter(log_path)
        writer.write(buffer, status)
        
        return response
    
    @app.teardown_request
    def cleanup_trace(exception=None):
        """Clean up trace context on error."""
        if exception is not None:
            buffer = TraceContext.end_trace()
            if buffer is not None:
                project_root = app.config.get('PROJECT_ROOT', '.')
                log_path = _get_trace_log_path(project_root)
                writer = TraceLogWriter(log_path)
                writer.write(buffer, "ERROR")


def _get_tracing_config(project_root: str) -> tuple:
    """
    Get tracing configuration including active status and ignored APIs.
    
    Reads from tools.json to check tracing_enabled, tracing_stop_at,
    and tracing_ignored_apis.
    
    Args:
        project_root: Path to project root
        
    Returns:
        Tuple of (is_active: bool, ignored_apis: List[str])
    """
    import json
    
    tools_path = Path(project_root) / "x-ipe-docs" / "config" / "tools.json"
    if not tools_path.exists():
        return False, []
    
    try:
        with open(tools_path) as f:
            config = json.load(f)
    except (json.JSONDecodeError, IOError):
        return False, []
    
    ignored_apis = config.get("tracing_ignored_apis", [])
    
    # Check if explicitly enabled
    if config.get("tracing_enabled", False):
        return True, ignored_apis
    
    # Check if stop_at is in the future
    stop_at = config.get("tracing_stop_at")
    if stop_at:
        try:
            # Keep timezone-aware for proper comparison
            stop_time = datetime.fromisoformat(
                stop_at.replace("Z", "+00:00")
            )
            if datetime.now(timezone.utc) < stop_time:
                return True, ignored_apis
        except (ValueError, AttributeError):
            pass
    
    return False, ignored_apis


def _is_path_ignored(path: str, ignored_apis: List[str]) -> bool:
    """
    Check if a request path matches any user-configured ignored API patterns.
    
    Supports exact matches and prefix matches (patterns ending with *).
    
    Args:
        path: Request path (e.g., "/api/project/structure")
        ignored_apis: List of API patterns to ignore
        
    Returns:
        True if path should be ignored
    """
    for pattern in ignored_apis:
        if pattern.endswith('*'):
            # Prefix match
            if path.startswith(pattern[:-1]):
                return True
        else:
            # Exact match
            if path == pattern:
                return True
    return False


def _get_trace_log_path(project_root: str) -> str:
    """
    Get the trace log directory path.
    
    Reads from tools.json or uses default.
    
    Args:
        project_root: Path to project root
        
    Returns:
        Absolute path to trace log directory
    """
    import json
    
    tools_path = Path(project_root) / "x-ipe-docs" / "config" / "tools.json"
    log_path = "instance/traces/"
    
    if tools_path.exists():
        try:
            with open(tools_path) as f:
                config = json.load(f)
                log_path = config.get("tracing_log_path", log_path)
        except (json.JSONDecodeError, IOError):
            pass
    
    return str(Path(project_root) / log_path)
