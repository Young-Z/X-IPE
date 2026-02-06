"""
FEATURE-023: Application Action Tracing - Core

Tracing module for X-IPE applications.

Provides automatic function tracing with sensitive data redaction,
execution timing, and structured log output.

Usage:
    from x_ipe.tracing import x_ipe_tracing, TraceContext

    @x_ipe_tracing(level="INFO", redact=["password"])
    def my_function(email: str, password: str):
        ...

    # Start/end traces manually (usually done by middleware)
    TraceContext.start_trace("POST /api/endpoint")
    # ... execute traced functions ...
    buffer = TraceContext.end_trace()
"""

from .decorator import x_ipe_tracing
from .context import TraceContext
from .buffer import TraceBuffer, TraceEntry
from .writer import TraceLogWriter
from .redactor import Redactor
from .middleware import init_tracing_middleware

__all__ = [
    'x_ipe_tracing',
    'TraceContext',
    'TraceBuffer',
    'TraceEntry',
    'TraceLogWriter',
    'Redactor',
    'init_tracing_middleware',
]
