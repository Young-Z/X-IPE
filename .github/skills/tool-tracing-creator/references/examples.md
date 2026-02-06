# Tracing Creator Skill Examples

## Example 1: Python Project with Flask

**User Request:**
```
Create tracing infrastructure for my Python Flask API project
```

**Agent Execution:**

1. **Check existing structure:**
   ```
   src/
   ├── app.py
   ├── routes/
   └── services/
   ```

2. **Create tracing module:**
   ```
   src/tracing/
   ├── __init__.py
   ├── decorator.py
   ├── context.py
   ├── buffer.py
   ├── writer.py
   └── redactor.py
   ```

3. **Generated code:**

   **decorator.py:**
   ```python
   import functools
   import time
   from .context import get_trace_id
   from .buffer import TraceBuffer
   from .redactor import Redactor
   
   def x_ipe_tracing(level="INFO", redact=None):
       """Decorator for tracing function calls."""
       def decorator(func):
           @functools.wraps(func)
           def wrapper(*args, **kwargs):
               trace_id = get_trace_id()
               func_name = func.__name__
               
               # Redact sensitive params
               safe_kwargs = Redactor.redact_dict(kwargs, redact or [])
               
               TraceBuffer.log(
                   trace_id=trace_id,
                   level=level,
                   event="start",
                   function=func_name,
                   input=safe_kwargs
               )
               
               start = time.perf_counter()
               try:
                   result = func(*args, **kwargs)
                   duration = time.perf_counter() - start
                   
                   TraceBuffer.log(
                       trace_id=trace_id,
                       level=level,
                       event="return",
                       function=func_name,
                       output=result,
                       duration_ms=duration * 1000
                   )
                   return result
               except Exception as e:
                   duration = time.perf_counter() - start
                   TraceBuffer.log(
                       trace_id=trace_id,
                       level="ERROR",
                       event="exception",
                       function=func_name,
                       error=str(e),
                       duration_ms=duration * 1000
                   )
                   raise
           return wrapper
       return decorator
   ```

4. **Update requirements:**
   - No additional dependencies needed

5. **Report:**
   ```
   ## Tracing Infrastructure Created
   
   Created 5 files in src/tracing/:
   - decorator.py (x_ipe_tracing decorator)
   - context.py (trace ID management)
   - buffer.py (log buffering)
   - writer.py (file/stdout output)
   - redactor.py (sensitive data protection)
   
   Import: `from tracing import x_ipe_tracing`
   ```

---

## Example 2: TypeScript/Node.js Project

**User Request:**
```
Create tracing for my Node.js Express API
```

**Agent Execution:**

1. **Create tracing module:**
   ```
   src/tracing/
   ├── index.ts
   ├── decorator.ts
   ├── context.ts
   ├── buffer.ts
   ├── writer.ts
   └── redactor.ts
   ```

2. **Generated decorator.ts:**
   ```typescript
   import { getTraceId } from './context';
   import { TraceBuffer } from './buffer';
   import { Redactor } from './redactor';
   
   export function xIpeTracing(options: {
     level?: 'INFO' | 'DEBUG';
     redact?: string[];
   } = {}) {
     const { level = 'INFO', redact = [] } = options;
     
     return function(
       target: any,
       propertyKey: string,
       descriptor: PropertyDescriptor
     ) {
       const originalMethod = descriptor.value;
       
       descriptor.value = async function(...args: any[]) {
         const traceId = getTraceId();
         const funcName = propertyKey;
         
         TraceBuffer.log({
           traceId,
           level,
           event: 'start',
           function: funcName,
           input: Redactor.redact(args, redact)
         });
         
         const start = performance.now();
         try {
           const result = await originalMethod.apply(this, args);
           const duration = performance.now() - start;
           
           TraceBuffer.log({
             traceId,
             level,
             event: 'return',
             function: funcName,
             output: result,
             durationMs: duration
           });
           
           return result;
         } catch (error) {
           const duration = performance.now() - start;
           TraceBuffer.log({
             traceId,
             level: 'ERROR',
             event: 'exception',
             function: funcName,
             error: String(error),
             durationMs: duration
           });
           throw error;
         }
       };
       
       return descriptor;
     };
   }
   ```

3. **Report:**
   ```
   ## Tracing Infrastructure Created
   
   Created 6 files in src/tracing/:
   - index.ts (exports)
   - decorator.ts (xIpeTracing decorator)
   - context.ts (trace ID via AsyncLocalStorage)
   - buffer.ts (log buffering)
   - writer.ts (file/console output)
   - redactor.ts (sensitive data protection)
   
   Import: `import { xIpeTracing } from './tracing';`
   ```

---

## Example 3: Existing Project with Partial Tracing

**User Request:**
```
My project has some tracing but it's incomplete. Set up proper infrastructure.
```

**Agent Execution:**

1. **Analyze existing tracing:**
   ```
   Found: src/utils/logger.py (basic logging only)
   Missing: Proper tracing with context, buffering, redaction
   ```

2. **Create parallel structure:**
   ```
   src/tracing/        # NEW - full tracing
   ├── __init__.py
   ├── decorator.py
   ...
   
   src/utils/logger.py # KEEP - for general logging
   ```

3. **Migration guide:**
   ```markdown
   ## Migration Steps
   
   1. Replace `@log_function` with `@x_ipe_tracing`
   2. Add redact=[] for sensitive params
   3. Update imports: `from tracing import x_ipe_tracing`
   ```

---

## Example 4: Project Without Package Structure

**User Request:**
```
Add tracing to my simple Python script project
```

**Agent Execution:**

1. **Check structure:**
   ```
   app.py
   utils.py
   config.py
   ```

2. **Create minimal structure:**
   ```
   tracing.py  # Single file with all tracing code
   ```

3. **Single-file tracing.py:**
   ```python
   """Minimal tracing decorator for simple projects."""
   import functools
   import time
   import json
   from datetime import datetime
   from contextvars import ContextVar
   
   _trace_id: ContextVar[str] = ContextVar('trace_id', default=None)
   
   def set_trace_id(trace_id: str):
       _trace_id.set(trace_id)
   
   def get_trace_id() -> str:
       return _trace_id.get()
   
   def x_ipe_tracing(level="INFO", redact=None):
       def decorator(func):
           @functools.wraps(func)
           def wrapper(*args, **kwargs):
               trace_id = get_trace_id() or "no-trace"
               
               # Simple redaction
               safe_kwargs = {
                   k: "[REDACTED]" if k in (redact or []) else v
                   for k, v in kwargs.items()
               }
               
               print(f"[{datetime.now().isoformat()}] [{level}] → {func.__name__}: {safe_kwargs}")
               
               start = time.perf_counter()
               try:
                   result = func(*args, **kwargs)
                   duration = (time.perf_counter() - start) * 1000
                   print(f"[{datetime.now().isoformat()}] [{level}] ← {func.__name__}: {duration:.1f}ms")
                   return result
               except Exception as e:
                   duration = (time.perf_counter() - start) * 1000
                   print(f"[{datetime.now().isoformat()}] [ERROR] ✗ {func.__name__}: {e} ({duration:.1f}ms)")
                   raise
           return wrapper
       return decorator
   ```

4. **Report:**
   ```
   ## Minimal Tracing Created
   
   Created single file: tracing.py
   
   Usage:
   from tracing import x_ipe_tracing, set_trace_id
   
   @x_ipe_tracing(level="INFO")
   def my_function():
       pass
   ```
