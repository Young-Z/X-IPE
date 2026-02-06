"""
FEATURE-023: Application Action Tracing - Core

TraceBuffer and TraceEntry for in-memory trace storage.

Traces are collected in-memory during request execution and flushed
to log files upon request completion.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Any
import json


@dataclass
class TraceEntry:
    """
    Single trace log entry representing a function call event.
    
    Attributes:
        timestamp: When the event occurred
        trace_id: Unique identifier for the trace
        level: Log level (INFO, DEBUG, ERROR)
        direction: Arrow direction (→ for entry, ← for exit)
        event_type: Type of event (start_function, return_function, exception)
        function_name: Name of the traced function
        data: Parameters, return value, or error details
        duration_ms: Execution time in milliseconds (only for exit events)
        depth: Nesting level (0 = root)
    """
    timestamp: datetime
    trace_id: str
    level: str
    direction: str
    event_type: str
    function_name: str
    data: dict
    duration_ms: Optional[float] = None
    depth: int = 0


class TraceBuffer:
    """
    In-memory buffer for trace entries during request execution.
    
    Collects trace entries and formats them for log file output.
    Enforces a maximum size limit to prevent memory exhaustion.
    
    Usage:
        buffer = TraceBuffer("abc-123", "POST /api/orders")
        buffer.add(TraceEntry(...))
        log_content = buffer.to_log_string("SUCCESS", 150.0)
    """
    
    MAX_SIZE = 10 * 1024 * 1024  # 10MB limit
    
    def __init__(self, trace_id: str, root_api: str):
        """
        Initialize TraceBuffer.
        
        Args:
            trace_id: Unique identifier for this trace
            root_api: The root API call (e.g., "POST /api/orders")
        """
        self.trace_id = trace_id
        self.root_api = root_api
        self.started_at = datetime.now(timezone.utc)
        self.entries: List[TraceEntry] = []
        self._size = 0
    
    def add(self, entry: TraceEntry) -> None:
        """
        Add a trace entry to the buffer.
        
        Silently drops entries if buffer size limit is exceeded.
        
        Args:
            entry: TraceEntry to add
        """
        try:
            entry_size = len(json.dumps(entry.data, default=str))
        except (TypeError, ValueError):
            entry_size = 100  # Fallback size estimate
        
        if self._size + entry_size > self.MAX_SIZE:
            return  # Silently drop if buffer full
        
        self.entries.append(entry)
        self._size += entry_size
    
    def to_log_string(self, status: str, total_ms: float) -> str:
        """
        Format the buffer as a log file string.
        
        Args:
            status: Final status (SUCCESS, ERROR)
            total_ms: Total execution time in milliseconds
            
        Returns:
            Formatted log string ready for file output
        """
        lines = [
            f"[TRACE-START] {self.trace_id} | {self.root_api} | {self.started_at.isoformat()}Z"
        ]
        
        for entry in self.entries:
            indent = "  " * (entry.depth + 1)
            
            try:
                data_str = json.dumps(entry.data, default=str, ensure_ascii=False)
            except (TypeError, ValueError):
                data_str = str(entry.data)
            
            # Truncate very long data
            if len(data_str) > 1000:
                data_str = data_str[:997] + "..."
            
            if entry.duration_ms is not None:
                line = (
                    f"{indent}[{entry.level}] {entry.direction} {entry.event_type}: "
                    f"{entry.function_name} | {data_str} | {entry.duration_ms:.0f}ms"
                )
            else:
                line = (
                    f"{indent}[{entry.level}] {entry.direction} {entry.event_type}: "
                    f"{entry.function_name} | {data_str}"
                )
            
            lines.append(line)
        
        lines.append(
            f"[TRACE-END] {self.trace_id} | {total_ms:.0f}ms | {status}"
        )
        
        return "\n".join(lines)
