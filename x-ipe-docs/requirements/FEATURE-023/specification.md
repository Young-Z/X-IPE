# Feature Specification: Application Action Tracing - Core

> Feature ID: FEATURE-023  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-01-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-01-2026 | Initial specification - Phase 1 Core Tracing |

## Linked Mockups

| Mockup | Type | Path | Description |
|--------|------|------|-------------|
| Tracing Dashboard v4 | HTML | [mockups/tracing-dashboard-v4.html](mockups/tracing-dashboard-v4.html) | Full dashboard with duration toggle, countdown, DAG visualization |

> **Note:** UI implementation is Phase 2. This specification covers Phase 1 (Core Tracing Backend) only. Mockup is linked for API contract reference.

---

## Overview

**Application Action Tracing - Core** is a decorator-based tracing framework for Python and TypeScript that automatically logs function calls, parameters, return values, execution times, and errors. This is Phase 1 of the Application Action Tracing System, focusing on the backend infrastructure.

The system provides `@x_ipe_tracing` (Python) and `@xIpeTracing` (TypeScript) decorators that developers apply to functions to enable automatic tracing. Traces are collected in-memory during request execution and flushed to structured log files upon request completion.

Key capabilities:
- **Automatic parameter/return capture** with configurable sensitive data redaction
- **Execution time tracking** per function call
- **Error capture** with full stack traces
- **UUID-based trace identification** for request correlation
- **Configurable duration-based tracing** (3/15/30 min) via tools.json
- **Automatic cleanup** of old trace files based on retention policy

---

## User Stories

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US-1 | Developer | add a decorator to my functions | their inputs, outputs, and timing are automatically logged |
| US-2 | Developer | have sensitive data redacted automatically | I don't accidentally expose passwords or tokens in logs |
| US-3 | Developer | see full stack traces when errors occur | I can quickly identify the root cause |
| US-4 | Operations | configure tracing duration | I can enable tracing for specific time windows |
| US-5 | Operations | have old logs auto-cleaned | disk space doesn't fill up with stale traces |
| US-6 | QA Engineer | correlate all function calls in a request | I can understand the full execution flow |

---

## Acceptance Criteria

### Python Tracing Decorator

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-1.1 | `@x_ipe_tracing` decorator MUST be importable from `x_ipe.tracing` module | Must |
| AC-1.2 | Decorator MUST accept `level` parameter: "INFO", "DEBUG", "SKIP" | Must |
| AC-1.3 | Decorator MUST accept optional `redact` parameter as list of field names | Must |
| AC-1.4 | Decorator MUST log function entry with: function name, parameters | Must |
| AC-1.5 | Decorator MUST log function exit with: return value, execution time (ms) | Must |
| AC-1.6 | Decorator MUST log exceptions with: type, message, stack trace | Must |
| AC-1.7 | Decorator MUST work with both sync and async functions | Must |
| AC-1.8 | Decorator overhead SHOULD be < 5ms per call | Should |

### TypeScript Tracing Decorator

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-2.1 | `@xIpeTracing` decorator MUST be exportable from `@x-ipe/tracing` package | Must |
| AC-2.2 | Decorator MUST accept `level` option: "INFO", "DEBUG", "SKIP" | Must |
| AC-2.3 | Decorator MUST accept optional `redact` option as string array | Must |
| AC-2.4 | Decorator MUST log function entry with: function name, parameters | Must |
| AC-2.5 | Decorator MUST log function exit with: return value, execution time | Must |
| AC-2.6 | Decorator MUST log exceptions with: error type, message, stack trace | Must |
| AC-2.7 | Decorator MUST work with sync and async methods | Must |
| AC-2.8 | Decorator MUST work with class methods and standalone functions | Must |

### Trace Context Management

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-3.1 | System MUST generate unique UUID trace ID for each root request | Must |
| AC-3.2 | System MUST propagate trace ID to all nested function calls | Must |
| AC-3.3 | System MUST track parent-child relationships between calls | Must |
| AC-3.4 | System MUST maintain call depth/nesting level | Must |
| AC-3.5 | System MUST use in-memory buffer during request execution | Must |
| AC-3.6 | System MUST flush buffer to file on request completion | Must |

### Log Format & Storage

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-4.1 | Log file MUST be named: `{timestamp}-{root-api-name}-{trace-id}.log` | Must |
| AC-4.2 | Log path MUST be configurable via `tools.json` → `tracing_log_path` | Must |
| AC-4.3 | Default log path MUST be `instance/traces/` | Must |
| AC-4.4 | Log format MUST include: `[TRACE-START]`, `[TRACE-END]`, `[INFO]`, `[DEBUG]`, `[ERROR]` markers | Must |
| AC-4.5 | Each log entry MUST include: timestamp, trace ID, function name, direction (→/←), data | Must |
| AC-4.6 | Error entries MUST be marked with `[ERROR]` in same file | Must |
| AC-4.7 | Log files older than retention period MUST be deleted on backend startup | Must |
| AC-4.8 | Retention period MUST be configurable via `tracing_retention_hours` (default: 24) | Must |

### Sensitive Data Redaction

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-5.1 | System MUST auto-redact fields containing "password" (case-insensitive) | Must |
| AC-5.2 | System MUST auto-redact fields containing "secret" (case-insensitive) | Must |
| AC-5.3 | System MUST auto-redact fields containing "token" (case-insensitive) | Must |
| AC-5.4 | System MUST auto-redact fields containing "api_key" or "apiKey" | Must |
| AC-5.5 | System MUST redact values matching credit card pattern (16 digits) | Must |
| AC-5.6 | System MUST redact values matching JWT pattern (eyJ...) | Must |
| AC-5.7 | Redacted values MUST be replaced with `[REDACTED]` | Must |
| AC-5.8 | Custom redact fields from decorator MUST be honored | Must |

### Tracing Configuration

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-6.1 | `tools.json` MUST support `tracing_enabled` field (boolean, default: false) | Must |
| AC-6.2 | `tools.json` MUST support `tracing_stop_at` field (ISO timestamp or null) | Must |
| AC-6.3 | `tools.json` MUST support `tracing_log_path` field (default: "instance/traces/") | Must |
| AC-6.4 | `tools.json` MUST support `tracing_retention_hours` field (default: 24) | Must |
| AC-6.5 | `tools.json` SHOULD support `tracing_ignored_apis` field (array of patterns) | Should |
| AC-6.6 | Backend MUST check `tracing_stop_at` on each request | Must |
| AC-6.7 | Backend MUST cleanup old logs on startup | Must |

### API Endpoints

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-7.1 | `GET /api/tracing/status` MUST return tracing state | Must |
| AC-7.2 | `POST /api/tracing/start` MUST accept `duration_minutes` (3, 15, 30) | Must |
| AC-7.3 | `POST /api/tracing/stop` MUST disable tracing immediately | Must |
| AC-7.4 | `GET /api/tracing/logs` SHOULD return list of trace files | Should |
| AC-7.5 | `GET /api/tracing/logs/{trace_id}` SHOULD return parsed trace data | Should |
| AC-7.6 | `DELETE /api/tracing/logs` SHOULD delete all trace logs | Should |

---

## Functional Requirements

### FR-1: Python Tracing Decorator

**Description:** Provide a decorator that automatically logs function execution.

**Input:**
- `level`: "INFO" | "DEBUG" | "SKIP" (default: "INFO")
- `redact`: List[str] - field names to redact (optional)

**Process:**
1. On function entry: capture function name, arguments
2. Apply redaction to arguments
3. Log entry with `[{level}] → start_function: {name}`
4. Execute wrapped function
5. On success: log return value with execution time
6. On error: log exception with stack trace
7. Propagate exception (don't swallow)

**Output:** Original function return value (unmodified)

**Example:**
```python
from x_ipe.tracing import x_ipe_tracing

@x_ipe_tracing(level="INFO", redact=["password"])
def create_user(username: str, password: str) -> dict:
    return {"id": 123, "username": username}
```

### FR-2: TypeScript Tracing Decorator

**Description:** Provide a method decorator for TypeScript classes.

**Input:**
- `level`: "INFO" | "DEBUG" | "SKIP" (default: "INFO")
- `redact`: string[] - field names to redact (optional)

**Process:** Same as Python decorator

**Example:**
```typescript
import { xIpeTracing } from '@x-ipe/tracing';

class UserService {
  @xIpeTracing({ level: "INFO", redact: ["password"] })
  async createUser(username: string, password: string): Promise<User> {
    return { id: 123, username };
  }
}
```

### FR-3: Trace Context Manager

**Description:** Manage trace context across nested function calls.

**Process:**
1. On first traced function call in request:
   - Generate UUID trace ID
   - Create in-memory buffer
   - Set as root call (depth = 0)
2. On nested traced function call:
   - Inherit trace ID from context
   - Increment depth
   - Link to parent call
3. On request completion:
   - Flush buffer to log file
   - Clear context

**Thread Safety:** Context must be thread-safe (Python: contextvars, TS: AsyncLocalStorage)

### FR-4: Log File Writer

**Description:** Write trace buffer to structured log file.

**File Naming:** `{YYYYMMDD-HHMMSS}-{api-name}-{trace-id}.log`

**Format:**
```
[TRACE-START] {trace_id} | {method} {path} | {timestamp}
  [{level}] → start_function: {name} | {params_json}
  [{level}] ← return_function: {name} | {return_json} | {duration}ms
  [ERROR] ← exception: {name} | {error_type}: {message} | {duration}ms
    {stack_trace}
[TRACE-END] {trace_id} | {total_duration}ms | {status}
```

### FR-5: Sensitive Data Redactor

**Description:** Automatically redact sensitive data before logging.

**Built-in Patterns:**
| Pattern Type | Detection | Replacement |
|--------------|-----------|-------------|
| Password fields | Key contains "password" | `[REDACTED]` |
| Secret fields | Key contains "secret" | `[REDACTED]` |
| Token fields | Key contains "token" | `[REDACTED]` |
| API keys | Key contains "api_key"/"apiKey" | `[REDACTED]` |
| Credit cards | 16-digit number pattern | `[REDACTED]` |
| JWTs | Value starts with "eyJ" | `[REDACTED]` |

**Custom Redaction:** Fields specified in decorator `redact` parameter are always redacted.

### FR-6: Tracing Configuration API

**Description:** REST API to control tracing.

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/tracing/status` | GET | - | `{ enabled, stop_at, retention_hours }` |
| `/api/tracing/start` | POST | `{ duration_minutes: 3|15|30 }` | `{ stop_at: ISO-timestamp }` |
| `/api/tracing/stop` | POST | - | `{ success: true }` |
| `/api/tracing/logs` | GET | - | `[{ trace_id, api, timestamp, size }]` |
| `/api/tracing/logs/{id}` | GET | - | Parsed trace data |
| `/api/tracing/logs` | DELETE | - | `{ deleted: count }` |

### FR-7: Startup Cleanup

**Description:** Remove stale log files on backend startup.

**Process:**
1. Read `tracing_retention_hours` from tools.json (default: 24)
2. Scan `tracing_log_path` directory
3. Delete files older than retention period
4. Log cleanup summary

---

## Non-Functional Requirements

### NFR-1: Performance

| Metric | Target |
|--------|--------|
| Decorator overhead | < 5ms per call |
| Memory buffer limit | 10MB per request |
| Log write latency | < 50ms |
| Startup cleanup | < 5s for 1000 files |

### NFR-2: Reliability

| Metric | Target |
|--------|--------|
| Log write success rate | 99.9% |
| Context propagation accuracy | 100% |
| Redaction effectiveness | 100% of configured patterns |

### NFR-3: Security

| Requirement | Implementation |
|-------------|----------------|
| Sensitive data redaction | Built-in patterns + custom fields |
| Log file permissions | 600 (owner read/write only) |
| No log injection | Escape special characters in logged data |

---

## Dependencies

### Internal Dependencies

None (Core infrastructure feature)

### External Dependencies

| Dependency | Purpose | Python | TypeScript |
|------------|---------|--------|------------|
| UUID generation | Trace ID creation | `uuid` (stdlib) | `crypto.randomUUID()` |
| Context propagation | Thread-safe context | `contextvars` | `AsyncLocalStorage` |
| JSON serialization | Log formatting | `json` (stdlib) | Native JSON |
| File I/O | Log writing | `aiofiles` | `fs/promises` |

---

## Business Rules

### BR-1: Tracing Activation

**Rule:** Tracing only occurs when:
- `tracing_enabled` is true, OR
- `tracing_stop_at` is set and current time < stop_at

**Example:** If `tracing_stop_at` is "2026-02-01T03:30:00Z" and current time is "2026-02-01T03:25:00Z", tracing is active.

### BR-2: Redaction Priority

**Rule:** Redaction is applied in order:
1. Custom fields from decorator `redact` parameter
2. Built-in patterns (password, secret, token, etc.)
3. Value patterns (credit card, JWT)

**Result:** A field matching multiple patterns is redacted once.

### BR-3: Log File Retention

**Rule:** Log files are only deleted on backend startup, not continuously.

**Rationale:** Prevents race conditions with active tracing and simplifies implementation.

### BR-4: Buffer Size Limit

**Rule:** If trace buffer exceeds 10MB, oldest entries are discarded.

**Rationale:** Prevents memory exhaustion on very long-running requests.

---

## Edge Cases & Constraints

### EC-1: Nested Async Calls

**Scenario:** Async function A calls async function B concurrently with C.
**Expected:** All calls share same trace ID, parent-child relationships preserved.

### EC-2: Exception in Decorator

**Scenario:** Redaction logic throws an error.
**Expected:** Log warning, proceed with unredacted data (safety over completeness).

### EC-3: Circular Object References

**Scenario:** Function returns object with circular reference.
**Expected:** Use safe JSON serialization with max depth, log `[Circular]` placeholder.

### EC-4: Very Large Return Values

**Scenario:** Function returns 1MB+ object.
**Expected:** Truncate logged value with `[Truncated: {size}]` indicator.

### EC-5: Missing tools.json

**Scenario:** tools.json doesn't exist or has invalid format.
**Expected:** Use default values, log warning.

### EC-6: Log Directory Doesn't Exist

**Scenario:** `tracing_log_path` directory doesn't exist.
**Expected:** Create directory automatically, log info message.

### EC-7: Disk Full

**Scenario:** Cannot write log file due to disk space.
**Expected:** Log error to console, don't crash application.

---

## Out of Scope (Phase 1)

- **UI Dashboard** - Tracing visualization UI (Phase 2)
- **Real-time streaming** - WebSocket log streaming
- **Distributed tracing** - Cross-service trace propagation
- **Log aggregation** - Centralized log collection (Elasticsearch, etc.)
- **Skill integration** - Auto-generating tracing code (Phase 3)
- **Metrics/Statistics** - Aggregated tracing metrics

---

## Technical Considerations

### Python Implementation

- Use `contextvars` for async-safe context propagation
- Use `functools.wraps` to preserve function metadata
- Consider `wrapt` library for better decorator handling
- Use `aiofiles` for async file I/O

### TypeScript Implementation

- Use `AsyncLocalStorage` from `async_hooks`
- Decorator factories for parameterized decorators
- Consider reflect-metadata for enhanced introspection
- Use streams for large log file writing

### Log File Format

- Human-readable for debugging
- Machine-parseable for Phase 2 UI
- Indentation shows call hierarchy
- JSON for data payloads

### Configuration Updates

- tools.json is read on each request (not cached)
- Allows runtime tracing control without restart
- Consider caching with file watcher for performance

---

## Open Questions

- [x] Log storage location? → Configurable via tools.json
- [x] Error log separation? → Same file with [ERROR] markers
- [x] Retention policy? → Cleanup on reboot, configurable hours
- [x] Trace ID format? → UUID
- [ ] Should we support custom log formatters? (Defer to v2)
- [ ] Log compression for long-term storage? (Defer to Phase 2)

---
