"""
FEATURE-023: Application Action Tracing - Core

TracingService for managing tracing configuration and lifecycle.

Provides high-level API for starting/stopping tracing, reading
configuration from tools.json, and cleaning up old log files.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

from x_ipe.services.tools_config_service import ToolsConfigService
from x_ipe.tracing.writer import TraceLogWriter
from x_ipe.tracing.parser import TraceLogParser
from x_ipe.tracing import x_ipe_tracing


class TracingService:
    """
    Service for managing tracing configuration and lifecycle.
    
    Integrates with tools.json for configuration persistence and
    provides methods for controlling tracing state.
    
    Usage:
        service = TracingService("/path/to/project")
        
        # Check status
        config = service.get_config()
        is_active = service.is_active()
        
        # Control tracing
        service.start(duration_minutes=15)
        service.stop()
        
        # List/cleanup logs
        logs = service.list_logs()
        deleted = service.cleanup_on_startup()
    """
    
    def __init__(self, project_root: str):
        """
        Initialize TracingService.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.tools_config = ToolsConfigService(str(project_root))
    
    @x_ipe_tracing()
    def get_config(self) -> Dict[str, Any]:
        """
        Get current tracing configuration.
        
        Returns:
            Dictionary with tracing settings:
            - enabled: bool
            - stop_at: str or None (ISO timestamp)
            - log_path: str
            - retention_hours: int
            - ignored_apis: list
        """
        config = self.tools_config.load()
        return {
            "enabled": config.get("tracing_enabled", False),
            "stop_at": config.get("tracing_stop_at"),
            "log_path": config.get("tracing_log_path", "instance/traces/"),
            "retention_hours": config.get("tracing_retention_hours", 24),
            "ignored_apis": config.get("tracing_ignored_apis", [])
        }
    
    @x_ipe_tracing()
    def is_active(self) -> bool:
        """
        Check if tracing is currently active.
        
        Tracing is active if:
        - tracing_enabled is True, OR
        - tracing_stop_at is set and in the future
        
        Returns:
            True if tracing should be performed
        """
        config = self.get_config()
        
        if config["enabled"]:
            return True
        
        stop_at = config["stop_at"]
        if stop_at:
            try:
                # Parse ISO timestamp - keep it timezone-aware
                stop_time = datetime.fromisoformat(
                    stop_at.replace("Z", "+00:00")
                )
                return datetime.now(timezone.utc) < stop_time
            except (ValueError, AttributeError):
                return False
        
        return False
    
    @x_ipe_tracing()
    def start(self, duration_minutes: int) -> Dict[str, Any]:
        """
        Start tracing for specified duration.
        
        Args:
            duration_minutes: Duration in minutes (must be 3, 15, or 30)
            
        Returns:
            Dictionary with success status and stop_at timestamp
            
        Raises:
            ValueError: If duration is not 3, 15, or 30
        """
        if duration_minutes not in [3, 15, 30]:
            raise ValueError("Duration must be 3, 15, or 30 minutes")
        
        stop_at = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        # Convert +00:00 to Z for consistent format
        stop_at_str = stop_at.isoformat().replace("+00:00", "Z")
        
        config = self.tools_config.load()
        config["tracing_stop_at"] = stop_at_str
        self.tools_config.save(config)
        
        return {"success": True, "stop_at": stop_at_str}
    
    @x_ipe_tracing()
    def stop(self) -> Dict[str, Any]:
        """
        Stop tracing immediately.
        
        Clears tracing_stop_at and sets tracing_enabled to False.
        
        Returns:
            Dictionary with success status
        """
        config = self.tools_config.load()
        config["tracing_stop_at"] = None
        config["tracing_enabled"] = False
        self.tools_config.save(config)
        
        return {"success": True}
    
    @x_ipe_tracing()
    def update_ignored_apis(self, patterns: List[str]) -> None:
        """
        Update the list of ignored API patterns.
        
        Args:
            patterns: List of API path patterns to ignore
        """
        config = self.tools_config.load()
        config["tracing_ignored_apis"] = patterns
        self.tools_config.save(config)
    
    @x_ipe_tracing()
    def list_logs(self) -> List[Dict[str, Any]]:
        """
        List all trace log files.
        
        Returns:
            List of log file metadata dictionaries:
            - trace_id: str
            - api: str (e.g., "GET /api/project/structure")
            - filename: str
            - size: int (bytes)
            - timestamp: str (ISO format)
        """
        config = self.get_config()
        log_path = self.project_root / config["log_path"]
        
        if not log_path.exists():
            return []
        
        logs = []
        for filepath in sorted(log_path.glob("*.log"), reverse=True):
            try:
                # Parse filename: {timestamp}-{api}-{trace_id}.log
                # Example: 20260202-072505-get-api-project-structure-a649c048-3d73.log
                stem = filepath.stem
                
                # Extract trace_id (last 2 UUID segments: xxxxxxxx-xxxx)
                # Split and find the UUID pattern at the end
                parts = stem.split("-")
                if len(parts) >= 4:
                    # Last 2 parts form the trace_id (e.g., "a649c048-3d73")
                    trace_id = f"{parts[-2]}-{parts[-1]}"
                    # First 2 parts are timestamp (YYYYMMDD-HHMMSS)
                    # Middle parts are the API name
                    api_parts = parts[2:-2]  # Skip timestamp and trace_id
                    api_name = "-".join(api_parts) if api_parts else "unknown"
                    # Convert api_name back to path format (e.g., "get-api-project-structure" -> "GET /api/project/structure")
                    api = self._filename_to_api(api_name)
                else:
                    trace_id = stem
                    api = "/unknown"
                
                stat = filepath.stat()
                logs.append({
                    "trace_id": trace_id,
                    "api": api,
                    "filename": filepath.name,
                    "size": stat.st_size,
                    "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except OSError:
                continue
        
        return logs
    
    def _filename_to_api(self, api_name: str) -> str:
        """
        Convert sanitized API filename component back to API format.
        
        Args:
            api_name: Sanitized name (e.g., "get-api-project-structure")
            
        Returns:
            API string (e.g., "GET /api/project/structure")
        """
        if not api_name or api_name == "unknown":
            return "/unknown"
        
        # Split by first hyphen to get method
        parts = api_name.split("-", 1)
        if len(parts) < 2:
            return f"/{api_name}"
        
        method = parts[0].upper()
        path_part = parts[1]
        
        # Convert hyphens back to slashes for path
        path = "/" + path_part.replace("-", "/")
        
        return f"{method} {path}"
    
    @x_ipe_tracing()
    def cleanup_on_startup(self) -> int:
        """
        Clean up old log files on backend startup.
        
        Uses retention_hours from configuration to determine
        which files to delete.
        
        Returns:
            Number of files deleted
        """
        config = self.get_config()
        log_path = self.project_root / config["log_path"]
        
        writer = TraceLogWriter(str(log_path))
        deleted = writer.cleanup(config["retention_hours"])
        
        if deleted > 0:
            print(f"[TRACING] Cleaned up {deleted} old trace log(s)")
        
        return deleted
    
    @x_ipe_tracing()
    def delete_all_logs(self) -> int:
        """
        Delete all trace log files.
        
        Returns:
            Number of files deleted
        """
        config = self.get_config()
        log_path = self.project_root / config["log_path"]
        
        if not log_path.exists():
            return 0
        
        deleted = 0
        for filepath in log_path.glob("*.log"):
            try:
                filepath.unlink()
                deleted += 1
            except OSError:
                continue
        
        return deleted
    
    @x_ipe_tracing()
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get parsed trace data for visualization.
        
        Searches for a log file matching the trace_id (exact or partial)
        and parses it into visualization-ready structure.
        
        Args:
            trace_id: Full or partial trace ID to search for
            
        Returns:
            Parsed trace data or None if not found:
            {
                "trace_id": str,
                "api": str,
                "timestamp": str,
                "total_time_ms": int,
                "status": str,
                "nodes": [...],
                "edges": [...]
            }
        """
        config = self.get_config()
        log_path = self.project_root / config["log_path"]
        
        if not log_path.exists():
            return None
        
        # Search for matching file
        matching_file = None
        for filepath in log_path.glob("*.log"):
            if trace_id in filepath.stem:
                matching_file = filepath
                break
        
        if not matching_file:
            return None
        
        # Parse the file
        parser = TraceLogParser()
        result = parser.parse(matching_file)
        
        # Add filename for reference
        result["filename"] = matching_file.name
        
        return result
