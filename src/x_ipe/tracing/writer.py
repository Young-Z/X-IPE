"""
FEATURE-023: Application Action Tracing - Core

TraceLogWriter for writing trace buffers to log files.

Handles file naming, directory creation, permission setting,
and cleanup of old log files.
"""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .buffer import TraceBuffer


class TraceLogWriter:
    """
    Writer for trace log files.
    
    Writes trace buffers to structured log files with proper naming,
    permissions, and cleanup of old files.
    
    Usage:
        writer = TraceLogWriter("instance/traces/")
        filepath = writer.write(buffer, "SUCCESS")
        deleted = writer.cleanup(retention_hours=24)
    """
    
    def __init__(self, log_path: str = "instance/traces/"):
        """
        Initialize TraceLogWriter.
        
        Args:
            log_path: Directory path for log files
        """
        self.log_path = Path(log_path)
    
    def write(self, buffer: TraceBuffer, status: str = "SUCCESS") -> Optional[str]:
        """
        Write trace buffer to log file.
        
        Creates the log directory if it doesn't exist.
        Sets file permissions to 600 (owner read/write only).
        
        Args:
            buffer: TraceBuffer to write
            status: Final status (SUCCESS, ERROR)
            
        Returns:
            Path to created log file, or None if write failed
        """
        try:
            # Ensure directory exists
            self.log_path.mkdir(parents=True, exist_ok=True)
            
            # Calculate total duration
            total_ms = (datetime.utcnow() - buffer.started_at).total_seconds() * 1000
            content = buffer.to_log_string(status, total_ms)
            
            # Generate filename
            timestamp = buffer.started_at.strftime("%Y%m%d-%H%M%S")
            api_name = self._sanitize_api_name(buffer.root_api)
            filename = f"{timestamp}-{api_name}-{buffer.trace_id}.log"
            filepath = self.log_path / filename
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Set permissions (owner read/write only)
            os.chmod(filepath, 0o600)
            
            return str(filepath)
            
        except Exception as e:
            print(f"[TRACING] Failed to write log: {e}")
            return None
    
    def cleanup(self, retention_hours: int = 24) -> int:
        """
        Delete log files older than retention period.
        
        Args:
            retention_hours: Hours to retain log files
            
        Returns:
            Number of files deleted
        """
        if not self.log_path.exists():
            return 0
        
        deleted = 0
        cutoff = datetime.utcnow().timestamp() - (retention_hours * 3600)
        
        for filepath in self.log_path.glob("*.log"):
            try:
                if filepath.stat().st_mtime < cutoff:
                    filepath.unlink()
                    deleted += 1
            except OSError:
                continue
        
        return deleted
    
    def _sanitize_api_name(self, api: str) -> str:
        """
        Convert API string to safe filename component.
        
        Args:
            api: API string (e.g., "POST /api/orders")
            
        Returns:
            Sanitized string (e.g., "post--api-orders")
        """
        # Replace spaces and slashes with hyphens
        sanitized = api.lower().replace(" ", "-").replace("/", "-")
        # Remove multiple consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Strip leading/trailing hyphens
        return sanitized.strip("-")
