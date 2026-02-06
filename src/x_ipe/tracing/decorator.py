"""
FEATURE-023: Application Action Tracing - Core

@x_ipe_tracing decorator for automatic function tracing.

Provides a decorator that automatically logs function entry, exit,
return values, and exceptions with execution timing.
"""
import functools
import time
import asyncio
import inspect
from datetime import datetime, timezone
from typing import Callable, List, Optional, Any, Dict

from .context import TraceContext
from .buffer import TraceEntry
from .redactor import Redactor


def x_ipe_tracing(
    level: str = "INFO",
    redact: Optional[List[str]] = None
) -> Callable:
    """
    Decorator for automatic function tracing.
    
    Logs function entry with parameters, exit with return value,
    and any exceptions that occur. Automatically redacts sensitive data.
    
    Args:
        level: Log level - "INFO", "DEBUG", or "SKIP"
        redact: List of parameter names to redact (in addition to built-in patterns)
    
    Usage:
        @x_ipe_tracing(level="INFO", redact=["password"])
        def create_user(email: str, password: str) -> dict:
            ...
    
    Returns:
        Decorated function that traces execution
    """
    if level == "SKIP":
        return lambda fn: fn  # No-op decorator
    
    redactor = Redactor(custom_fields=redact)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            ctx = TraceContext.get_current()
            if not ctx:
                return func(*args, **kwargs)  # No active trace
            
            return _trace_call(ctx, func, args, kwargs, level, redactor)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            ctx = TraceContext.get_current()
            if not ctx:
                return await func(*args, **kwargs)  # No active trace
            
            return await _trace_call_async(ctx, func, args, kwargs, level, redactor)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def _extract_params(func: Callable, args: tuple, kwargs: dict) -> Dict[str, Any]:
    """
    Extract function parameters as a dictionary.
    
    Uses function signature to map positional args to parameter names.
    
    Args:
        func: The function being called
        args: Positional arguments
        kwargs: Keyword arguments
        
    Returns:
        Dictionary of parameter names to values
    """
    params = {}
    
    try:
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        
        # Map positional args
        for i, arg in enumerate(args):
            if i < len(param_names):
                # Skip 'self' and 'cls' parameters
                param_name = param_names[i]
                if param_name not in ('self', 'cls'):
                    params[param_name] = arg
            else:
                params[f"arg_{i}"] = arg
        
        # Add keyword args
        params.update(kwargs)
    except (ValueError, TypeError):
        # Fallback if signature introspection fails
        for i, arg in enumerate(args):
            params[f"arg_{i}"] = arg
        params.update(kwargs)
    
    return params


def _safe_serialize(value: Any) -> Any:
    """
    Safely serialize a value for logging.
    
    Handles circular references and non-serializable objects.
    
    Args:
        value: Value to serialize
        
    Returns:
        Serializable representation of the value
    """
    try:
        # Try direct serialization
        import json
        json.dumps(value, default=str)
        return value
    except (TypeError, ValueError, RecursionError):
        # Fallback for complex objects
        return str(value)[:500]


def _trace_call(
    ctx: TraceContext,
    func: Callable,
    args: tuple,
    kwargs: dict,
    level: str,
    redactor: Redactor
) -> Any:
    """
    Trace a synchronous function call.
    
    Logs entry, executes the function, logs exit or exception.
    """
    func_name = func.__name__
    depth = ctx.push_call(func_name)
    
    # Extract and redact parameters
    params = _extract_params(func, args, kwargs)
    redacted_params = redactor.redact(params)
    
    # Log entry
    ctx.buffer.add(TraceEntry(
        timestamp=datetime.now(timezone.utc),
        trace_id=ctx.trace_id,
        level=level,
        direction="→",
        event_type="start_function",
        function_name=func_name,
        data=_safe_serialize(redacted_params),
        depth=depth
    ))
    
    start = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000
        
        # Redact and serialize return value
        redacted_result = redactor.redact({"return": _safe_serialize(result)})
        
        # Log success
        ctx.buffer.add(TraceEntry(
            timestamp=datetime.now(timezone.utc),
            trace_id=ctx.trace_id,
            level=level,
            direction="←",
            event_type="return_function",
            function_name=func_name,
            data=redacted_result,
            duration_ms=duration,
            depth=depth
        ))
        return result
        
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        
        # Log error
        ctx.buffer.add(TraceEntry(
            timestamp=datetime.now(timezone.utc),
            trace_id=ctx.trace_id,
            level="ERROR",
            direction="←",
            event_type="exception",
            function_name=func_name,
            data={
                "error": type(e).__name__,
                "message": str(e)
            },
            duration_ms=duration,
            depth=depth
        ))
        raise
        
    finally:
        ctx.pop_call()


async def _trace_call_async(
    ctx: TraceContext,
    func: Callable,
    args: tuple,
    kwargs: dict,
    level: str,
    redactor: Redactor
) -> Any:
    """
    Trace an asynchronous function call.
    
    Logs entry, awaits the function, logs exit or exception.
    """
    func_name = func.__name__
    depth = ctx.push_call(func_name)
    
    # Extract and redact parameters
    params = _extract_params(func, args, kwargs)
    redacted_params = redactor.redact(params)
    
    # Log entry
    ctx.buffer.add(TraceEntry(
        timestamp=datetime.now(timezone.utc),
        trace_id=ctx.trace_id,
        level=level,
        direction="→",
        event_type="start_function",
        function_name=func_name,
        data=_safe_serialize(redacted_params),
        depth=depth
    ))
    
    start = time.perf_counter()
    try:
        result = await func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000
        
        # Redact and serialize return value
        redacted_result = redactor.redact({"return": _safe_serialize(result)})
        
        # Log success
        ctx.buffer.add(TraceEntry(
            timestamp=datetime.now(timezone.utc),
            trace_id=ctx.trace_id,
            level=level,
            direction="←",
            event_type="return_function",
            function_name=func_name,
            data=redacted_result,
            duration_ms=duration,
            depth=depth
        ))
        return result
        
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        
        # Log error
        ctx.buffer.add(TraceEntry(
            timestamp=datetime.now(timezone.utc),
            trace_id=ctx.trace_id,
            level="ERROR",
            direction="←",
            event_type="exception",
            function_name=func_name,
            data={
                "error": type(e).__name__,
                "message": str(e)
            },
            duration_ms=duration,
            depth=depth
        ))
        raise
        
    finally:
        ctx.pop_call()
