# Extraction Prompts — Section 6: Data Flow / Protocol Analysis

> These prompts guide AI agents during the `extract` operation.
> Each subsection has targeted prompts for systematic extraction.

---

## 6.1 Request Flows

### Primary Prompt

```
Trace end-to-end request processing paths in {repo_path}.
Start from HTTP route handlers, CLI entry points, or scheduled job triggers
identified in Phase 1 Section 5.

For each critical flow (start with the most-used or most-complex):

1. Name the flow (e.g., "User Registration", "Order Checkout")
2. List every processing step in order:
   | Step # | Name | Role | File:Line | Data In | Data Out | Sync/Async |
3. Processing roles to look for:
   - Entry point (route handler, CLI parser)
   - Middleware (auth, logging, rate limiting, CORS)
   - Validation (schema validation, input sanitization)
   - Handler/Controller (request orchestration)
   - Service (business logic)
   - Repository/DAO (data access)
   - External call (HTTP client, queue publish, cache)
   - Response serialization
4. Create a Mermaid sequenceDiagram:
   - Participants = modules/services involved
   - Messages = method calls with data shape annotation
   - Note async boundaries with "activate/deactivate" blocks
```

### Follow-up Prompt

```
For each traced flow, verify the path by checking:
- Do integration tests in Phase 2 exercise this exact path?
- Does the middleware chain match the framework's registration order?
- Are there branching paths (error handling, validation failures)?
Document the happy path first, then note error/alternate branches.
```

---

## 6.2 Event Propagation

### Primary Prompt

```
Identify event-driven communication patterns in {repo_path}:

1. Event Emitters / Publishers:
   - Node.js: EventEmitter.emit(), process.emit()
   - Python: signal.send(), emit(), publish()
   - Java: ApplicationEventPublisher, @EventListener
   - Generic: message queue publish calls (RabbitMQ, Kafka, Redis)

2. Event Listeners / Subscribers:
   - Node.js: .on(), .once(), .addEventListener()
   - Python: @receiver, signal.connect(), subscribe()
   - Java: @EventListener, implements ApplicationListener
   - Generic: message queue consumer/subscriber registrations

3. For each event/topic:
   | Field | Value |
   |-------|-------|
   | Event name / topic | string |
   | Publisher | file:line |
   | Subscriber(s) | file:line (list) |
   | Payload shape | { field: type, ... } |
   | Delivery guarantee | at-most-once / at-least-once / exactly-once |
   | Ordering | guaranteed / best-effort |

4. If no event-driven patterns found, explicitly state:
   "No event-driven communication patterns detected in this codebase."
```

---

## 6.3 Data Transformation Chains

### Primary Prompt

```
Trace how data changes shape as it moves through layers in {repo_path}:

1. Identify common transformation patterns:
   - HTTP request body → DTO → Domain Entity → Database row
   - Database row → Domain Entity → DTO → HTTP response body
   - External API response → Internal model → Cache entry
   - Queue message → Event payload → Handler input

2. For each transformation step:
   | Input Shape | Output Shape | Transform Location | Fields Changed |
   |-------------|--------------|-------------------|----------------|
   | { name: str, email: str } | User(id, name, email, created_at) | services/user.py:42 | +id, +created_at |

3. Document:
   - Which fields are added (e.g., generated IDs, timestamps)
   - Which fields are removed (e.g., passwords stripped from response)
   - Which fields are renamed (e.g., snake_case → camelCase)
   - Which fields change type (e.g., string date → Date object)

4. Source priority: Type definitions > runtime assertions > test fixtures
```

---

## 6.4 Protocol Details

### Primary Prompt

```
Identify all communication protocols used in {repo_path}:

1. HTTP/HTTPS:
   - REST API: base URL, content type (JSON, XML, form-data)
   - GraphQL: schema location, resolver patterns
   - Configuration: CORS, rate limiting, timeouts

2. gRPC:
   - Proto file locations
   - Service definitions and RPC methods
   - Serialization: protobuf version

3. WebSocket:
   - Connection handler locations
   - Message types (text, binary, custom protocol)
   - Heartbeat/ping-pong configuration

4. Message Queues:
   - Broker type: RabbitMQ, Kafka, Redis Streams, SQS, etc.
   - Queue/topic names and their purpose
   - Serialization: JSON, protobuf, Avro, msgpack
   - Configuration file location

5. For each protocol:
   | Protocol | Technology | Config Location | Serialization | Purpose |
```

---

## 6.5 Async/Sync Boundaries

### Primary Prompt

```
Map where async and sync code meet in {repo_path}:

1. Identify boundary types:
   - async/await entry points (first async call in a sync context)
   - Promise/Future creation from sync code
   - Callback-to-promise wrappers (util.promisify, new Promise())
   - Thread pool submissions (executor.submit, ThreadPoolExecutor)
   - Queue publish points (sync code firing async work)
   - Event loop integration (asyncio.run, loop.run_until_complete)

2. For each boundary:
   | Location | Upstream Model | Downstream Model | Mechanism | Error Propagation |
   |----------|----------------|-------------------|-----------|-------------------|
   | handlers/user.py:28 | sync (Flask route) | async (aiohttp call) | asyncio.run() | Exception wrapping |

3. Document error propagation across boundaries:
   - How do async errors surface in sync callers?
   - Are there unhandled promise rejections / uncaught exceptions?
   - Is there a global error handler for async boundaries?

4. If the codebase is uniformly sync or uniformly async, state that explicitly
   rather than leaving the section empty.
```

---

## Cross-Cutting Guidance

- **Source priority:** Integration tests > route handlers > service methods > repository calls
- **Always cite file:line** for every flow step, event, and boundary
- **Phase 1 reference:** Use Section 5 entry points and Section 7 framework info as starting points
- **Phase 2 reference:** Use Section 8 integration test flows to validate and discover paths
- **Mermaid diagrams:** Required for request flows; recommended for event propagation
- **Empty subsections:** If a pattern is not present, create the file with explicit "None detected" statement
