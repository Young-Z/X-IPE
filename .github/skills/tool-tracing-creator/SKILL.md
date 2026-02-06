---
name: tool-tracing-creator
description: Creates tracing utility infrastructure for a target project/language. Generates decorator templates, log writers, and configuration. Use when setting up tracing for a new project or adding tracing support to existing project. Triggers on "create tracing utility", "set up tracing for", "add tracing infrastructure".
---

# Tool: Tracing Creator

## Purpose

Create tracing utility infrastructure for a project by:
1. Detecting target language (Python/TypeScript)
2. Generating tracing decorator/wrapper code
3. Creating log writer and buffer modules
4. Setting up configuration files
5. Adding sensitive data redaction

---

## Trigger Patterns

Use this skill when human asks to:
- "create tracing utility for {project}"
- "set up tracing for {language} project"
- "add tracing infrastructure to {path}"
- "generate tracing decorators for {project}"
- "initialize tracing system"

---

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| target_path | string | Required | Project root or source directory |
| language | string | "auto" | Target language: "python", "typescript", or "auto" |
| log_path | string | "instance/traces/" | Directory for trace log files |
| retention_hours | int | 24 | Hours to retain log files |

---

## Execution Procedure

### Step 1: Detect Language

If `language="auto"`:
1. Check for `pyproject.toml`, `setup.py`, `requirements.txt` → Python
2. Check for `package.json`, `tsconfig.json` → TypeScript
3. If both exist, ask human to specify

### Step 2: Create Directory Structure

**For Python:**
```
{target_path}/
├── tracing/
│   ├── __init__.py       # Exports decorator and utilities
│   ├── decorator.py      # @x_ipe_tracing decorator
│   ├── context.py        # TraceContext for request tracking
│   ├── buffer.py         # In-memory trace buffer
│   ├── writer.py         # Log file writer
│   └── redactor.py       # Sensitive data redaction
```

**For TypeScript:**
```
{target_path}/
├── tracing/
│   ├── index.ts          # Exports decorator and utilities
│   ├── decorator.ts      # @xIpeTracing decorator
│   ├── context.ts        # TraceContext for request tracking
│   ├── buffer.ts         # In-memory trace buffer
│   ├── writer.ts         # Log file writer
│   └── redactor.ts       # Sensitive data redaction
```

### Step 3: Generate Core Files

#### 3.1 Decorator (Python)

```python
# tracing/decorator.py
"""
Tracing decorator for automatic function instrumentation.
"""
import functools
import time
import asyncio
from typing import Callable, List, Optional

from .context import TraceContext
from .redactor import Redactor


def x_ipe_tracing(
    level: str = "INFO",
    redact: Optional[List[str]] = None
) -> Callable:
    """
    Decorator for automatic function tracing.
    
    Args:
        level: Log level - "INFO", "DEBUG", or "SKIP"
        redact: List of parameter names to redact
    
    Usage:
        @x_ipe_tracing(level="INFO", redact=["password"])
        def login(email: str, password: str) -> dict:
            ...
    """
    if level == "SKIP":
        return lambda fn: fn
    
    redactor = Redactor(custom_fields=redact)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            ctx = TraceContext.get_current()
            if not ctx:
                return func(*args, **kwargs)
            return _trace_call(ctx, func, args, kwargs, level, redactor)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            ctx = TraceContext.get_current()
            if not ctx:
                return await func(*args, **kwargs)
            return await _trace_async(ctx, func, args, kwargs, level, redactor)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
```

#### 3.2 Decorator (TypeScript)

```typescript
// tracing/decorator.ts
import { TraceContext } from './context';
import { Redactor } from './redactor';

interface TracingOptions {
  level?: 'INFO' | 'DEBUG' | 'SKIP';
  redact?: string[];
}

export function xIpeTracing(options: TracingOptions = {}) {
  const { level = 'INFO', redact = [] } = options;
  
  if (level === 'SKIP') {
    return (target: any, key: string, descriptor: PropertyDescriptor) => descriptor;
  }
  
  const redactor = new Redactor(redact);
  
  return function (target: any, key: string, descriptor: PropertyDescriptor) {
    const original = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      const ctx = TraceContext.getCurrent();
      if (!ctx) {
        return original.apply(this, args);
      }
      return traceCall(ctx, original, this, args, key, level, redactor);
    };
    
    return descriptor;
  };
}
```

### Step 4: Generate Support Files

Create these additional modules:
- **context.py/ts**: TraceContext with thread-local/async-local storage
- **buffer.py/ts**: TraceBuffer for in-memory log accumulation
- **writer.py/ts**: TraceLogWriter for file output
- **redactor.py/ts**: Redactor with sensitive pattern matching

### Step 5: Create Configuration

Add to project configuration:

**Python (pyproject.toml or .env):**
```toml
[tool.tracing]
enabled = true
log_path = "instance/traces/"
retention_hours = 24
```

**TypeScript (package.json or .env):**
```json
{
  "tracing": {
    "enabled": true,
    "logPath": "traces/",
    "retentionHours": 24
  }
}
```

### Step 6: Create __init__.py / index.ts

Export public API:

```python
# tracing/__init__.py
from .decorator import x_ipe_tracing
from .context import TraceContext
from .writer import TraceLogWriter

__all__ = ['x_ipe_tracing', 'TraceContext', 'TraceLogWriter']
```

```typescript
// tracing/index.ts
export { xIpeTracing } from './decorator';
export { TraceContext } from './context';
export { TraceLogWriter } from './writer';
```

### Step 7: Report Results

```markdown
## Tracing Utility Created ✅

### Files Generated

| File | Purpose |
|------|---------|
| `tracing/__init__.py` | Public exports |
| `tracing/decorator.py` | @x_ipe_tracing decorator |
| `tracing/context.py` | Request context tracking |
| `tracing/buffer.py` | In-memory trace buffer |
| `tracing/writer.py` | Log file writer |
| `tracing/redactor.py` | Sensitive data redaction |

### Configuration

- Log path: `instance/traces/`
- Retention: 24 hours
- Sensitive patterns: password, token, secret, key, auth

### Usage

```python
from tracing import x_ipe_tracing

@x_ipe_tracing(level="INFO")
def my_function():
    pass
```

### Next Steps

1. Add tracing to API routes using `tool-tracing-instrumentation` skill
2. Configure retention in project settings
3. View traces in Tracing Dashboard
```

---

## Sensitive Data Patterns

The generated redactor includes these patterns:

| Category | Patterns |
|----------|----------|
| Passwords | password, pwd, passwd, pass |
| Secrets | secret, secret_key, secretkey |
| Tokens | token, auth_token, api_token, access_token |
| Keys | key, api_key, apikey, private_key |
| Auth | auth, authorization, credential |
| Financial | card_number, cvv, ssn |

---

## Reference Implementation

The skill uses X-IPE's own tracing implementation as reference:
- `src/x_ipe/tracing/decorator.py`
- `src/x_ipe/tracing/context.py`
- `src/x_ipe/tracing/buffer.py`
- `src/x_ipe/tracing/writer.py`
- `src/x_ipe/tracing/redactor.py`

When creating tracing for a new project, adapt these patterns to the target language.

---

## Definition of Done

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Language detected or specified | Yes |
| 2 | Directory structure created | Yes |
| 3 | Decorator file generated | Yes |
| 4 | Context file generated | Yes |
| 5 | Buffer file generated | Yes |
| 6 | Writer file generated | Yes |
| 7 | Redactor file generated | Yes |
| 8 | Configuration added | Yes |
| 9 | Usage instructions provided | Yes |

---

## Examples

See [references/examples.md](references/examples.md) for detailed examples.
