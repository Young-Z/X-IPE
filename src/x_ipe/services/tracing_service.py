"""
FEATURE-023: Application Action Tracing - Core

TracingService for managing tracing configuration and lifecycle.

Provides high-level API for starting/stopping tracing, reading
configuration from tools.json, and cleaning up old log files.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from x_ipe.services.tools_config_service import ToolsConfigService
from x_ipe.tracing.writer import TraceLogWriter


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
                # Parse ISO timestamp
                stop_time = datetime.fromisoformat(
                    stop_at.replace("Z", "+00:00")
                ).replace(tzinfo=None)
                return datetime.utcnow() < stop_time
            except (ValueError, AttributeError):
                return False
        
        return False
    
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
        
        stop_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
        stop_at_str = stop_at.isoformat() + "Z"
        
        config = self.tools_config.load()
        config["tracing_stop_at"] = stop_at_str
        self.tools_config.save(config)
        
        return {"success": True, "stop_at": stop_at_str}
    
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
    
    def list_logs(self) -> List[Dict[str, Any]]:
        """
        List all trace log files.
        
        Returns:
            List of log file metadata dictionaries:
            - trace_id: str
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
                stem = filepath.stem
                parts = stem.rsplit("-", 1)
                trace_id = parts[-1] if len(parts) > 1 else stem
                
                stat = filepath.stat()
                logs.append({
                    "trace_id": trace_id,
                    "filename": filepath.name,
                    "size": stat.st_size,
                    "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except OSError:
                continue
        
        return logs
    
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
