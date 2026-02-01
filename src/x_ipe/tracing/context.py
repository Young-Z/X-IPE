"""
FEATURE-023: Application Action Tracing - Core

TraceContext for thread-safe context propagation using contextvars.

Manages the active trace context across nested function calls,
ensuring trace ID propagation and proper nesting depth tracking.
"""
from contextvars import ContextVar
from typing import Optional, List
import uuid

from .buffer import TraceBuffer


# Thread-safe context variable for the active trace
_trace_context: ContextVar[Optional['TraceContext']] = ContextVar(
    'trace_context', 
    default=None
)


class TraceContext:
    """
    Thread-safe trace context manager.
    
    Uses Python's contextvars to maintain trace state across async
    function calls. Tracks trace ID, buffer, and call depth.
    
    Usage:
        # Start a new trace
        ctx = TraceContext.start_trace("POST /api/orders")
        
        # Get current context (in nested calls)
        ctx = TraceContext.get_current()
        
        # End trace and get buffer
        buffer = TraceContext.end_trace()
    """
    
    def __init__(self, trace_id: str, root_api: str):
        """
        Initialize TraceContext.
        
        Args:
            trace_id: Unique identifier for this trace
            root_api: The root API call (e.g., "POST /api/orders")
        """
        self.trace_id = trace_id
        self.buffer = TraceBuffer(trace_id, root_api)
        self.depth = 0
        self._call_stack: List[str] = []
    
    @classmethod
    def start_trace(cls, root_api: str) -> 'TraceContext':
        """
        Start a new trace.
        
        Generates a unique trace ID and creates a new context.
        Sets the context as the active trace.
        
        Args:
            root_api: The root API call (e.g., "POST /api/orders")
            
        Returns:
            New TraceContext instance
        """
        # Generate short UUID for readability (first 13 chars)
        trace_id = str(uuid.uuid4())[:13]
        ctx = cls(trace_id, root_api)
        _trace_context.set(ctx)
        return ctx
    
    @classmethod
    def get_current(cls) -> Optional['TraceContext']:
        """
        Get the current active trace context.
        
        Returns:
            Active TraceContext or None if no trace is active
        """
        return _trace_context.get()
    
    @classmethod
    def end_trace(cls) -> Optional[TraceBuffer]:
        """
        End the current trace and return the buffer.
        
        Clears the active context.
        
        Returns:
            TraceBuffer containing all trace entries, or None if no active trace
        """
        ctx = _trace_context.get()
        if ctx:
            _trace_context.set(None)
            return ctx.buffer
        return None
    
    def push_call(self, func_name: str) -> int:
        """
        Push a function call onto the stack.
        
        Increments depth and tracks the function name.
        
        Args:
            func_name: Name of the function being called
            
        Returns:
            Depth level before increment (for logging)
        """
        self._call_stack.append(func_name)
        depth = self.depth
        self.depth += 1
        return depth
    
    def pop_call(self) -> None:
        """
        Pop a function call from the stack.
        
        Decrements depth and removes the function from tracking.
        """
        if self._call_stack:
            self._call_stack.pop()
            self.depth -= 1
