---
name: x-ipe-tool-rev-eng-data-flow-analysis
version: "1.0"
description: Section 6 — Data Flow / Protocol Analysis for application reverse engineering (Phase 3-Deep). Traces end-to-end request flows, event propagation, data transformation chains, communication protocols, and async/sync boundaries. Triggers on "data flow analysis", "request tracing", "protocol analysis".
section_id: 6
phase: "3-Deep"
categories: ["application-reverse-engineering"]
---

# Data Flow / Protocol Analysis — Section 6

## Purpose

AI Agents follow this skill to extract data flow knowledge from a target codebase:
1. Trace end-to-end request processing paths with file:line at each step
2. Document event-driven communication patterns (emitters, queues, pub/sub)
3. Map data transformation chains (how data changes shape between layers)
4. Identify communication protocols (HTTP, gRPC, WebSocket, MQ)
5. Mark async/sync boundaries where execution model changes

---

## Important Notes

BLOCKING: This is a **tool skill** — it is invoked by `x-ipe-task-based-application-knowledge-extractor` during Phase 3-Deep extraction. Do not invoke standalone.
CRITICAL: Phase 1 scan output (Sections 5 + 7) and Phase 2 test knowledge (Section 8) MUST be available before this skill runs.
CRITICAL: Every flow step MUST cite file:line. Flows without step-level citations are rejected.
CRITICAL: Output MUST use subfolder structure with `index.md` linking subsections (LL-001, LL-002).

---

## When to Use

```yaml
triggers:
  - "data flow analysis"
  - "request tracing"
  - "protocol analysis"
  - "section 6 extraction"
  - "event propagation mapping"

not_for:
  - "Dependency graph (import-level)" → Section 4
  - "Architecture recovery" → Section 1
  - "API contract documentation" → Section 3
```

---

## Input Parameters

```yaml
input:
  operation: "extract | validate | package"
  section_id: "6-data-flow-analysis"
  content_path: "string | null"
  repo_path: "string"
  phase1_output: "string"       # Path to Phase 1 results (Sections 5, 7)
  phase2_output: "string"       # Path to Phase 2 results (Section 8)
  output_path: "string"         # Target output directory
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies which operation to perform" />
  <field name="repo_path" source="Caller provides path to target repository">
    <steps>
      1. Must be a valid directory containing source code
      2. Required for extract operation
    </steps>
  </field>
  <field name="phase1_output" source="Phase 1 scan output directory">
    <steps>
      1. Must contain Section 5 (code structure) for entry point identification
      2. Must contain Section 7 (tech stack) for framework-specific routing patterns
      3. Read entry points (main files, route handlers, event listeners)
      4. Read detected frameworks for middleware/handler chain patterns
    </steps>
  </field>
  <field name="phase2_output" source="Phase 2 test knowledge directory">
    <steps>
      1. Must contain Section 8 (test knowledge extraction)
      2. Read integration test flows — they trace real request paths
      3. Read test fixtures — they reveal data shapes at boundaries
    </steps>
  </field>
  <field name="content_path" source="Path to extracted content">
    <steps>
      1. Required for validate, package operations
      2. Must be UTF-8 markdown
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Phase 1 output available</name>
    <verification>phase1_output directory exists with Section 5 and Section 7 content</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Phase 2 output available</name>
    <verification>phase2_output directory exists with Section 8 test knowledge</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Repository accessible</name>
    <verification>repo_path is a valid directory with source code</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Valid operation requested</name>
    <verification>operation is one of: extract, validate, package</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: extract

**When:** Orchestrator requests data flow extraction for Section 6.

```xml
<operation name="extract">
  <action>
    1. Read Phase 1 output:
       a. From Section 5: entry points, module boundaries, directory structure
       b. From Section 7: web framework (Express, Flask, FastAPI, Spring, Gin, etc.),
          message queue (RabbitMQ, Kafka, Redis pub/sub), WebSocket library
    2. Read Phase 2 output:
       a. From Section 8: integration test flows revealing real request paths
       b. Test fixtures revealing data shapes at layer boundaries
    3. Extract request flows (subsection 6.1):
       a. Identify entry points: HTTP route handlers, CLI commands, scheduled jobs
       b. For each critical entry point, trace the complete processing path:
          Entry → Middleware → Validation → Handler → Service → Repository → Response
       c. At each step record:
          - Step name and role (e.g., "auth middleware")
          - File:line where processing occurs
          - Data shape entering this step (TypeScript interface, Python dataclass, etc.)
          - Data shape leaving this step
          - Sync or async execution
       d. Create Mermaid sequenceDiagram for each traced flow
       e. Output: 01-request-flows.md
    4. Extract event propagation (subsection 6.2):
       a. Find event emitters: EventEmitter, signals, message queue publish
       b. Find event listeners/subscribers: on(), subscribe(), @listener
       c. For each event:
          - Event name/topic
          - Publisher: file:line
          - Subscriber(s): file:line
          - Payload shape
          - Delivery guarantee (at-most-once, at-least-once, exactly-once)
       d. Output: 02-event-propagation.md
    5. Extract data transformation chains (subsection 6.3):
       a. Trace how data shape changes as it moves through layers:
          DTO → Entity → Domain Model → DTO (or similar)
       b. For each transformation:
          - Input shape (with field names and types)
          - Output shape (with field names and types)
          - Transformation location: file:line
          - Fields added, removed, renamed, or type-converted
       c. Output: 03-data-transformations.md
    6. Document protocol details (subsection 6.4):
       a. Identify communication protocols in use:
          - HTTP/HTTPS: REST, GraphQL
          - gRPC: proto file locations, service definitions
          - WebSocket: connection handlers, message types
          - Message Queues: broker type, queue/topic names, serialization format
          - IPC: shared memory, pipes, sockets
       b. For each protocol: technology, configuration location, serialization format
       c. Output: 04-protocol-details.md
    7. Map async/sync boundaries (subsection 6.5):
       a. Identify where code transitions between sync and async:
          - async/await boundaries
          - Callback-to-promise transitions
          - Thread pool submissions
          - Queue publish (fire-and-forget)
          - Event loop integration points
       b. For each boundary: location file:line, upstream model, downstream model
       c. Document error propagation across boundaries
       d. Output: 05-async-sync-boundaries.md
    8. Create index.md with data flow overview:
       | Metric | Count |
       | Request flows traced | N |
       | Event-driven flows | N |
       | Data transformations | N |
       | Protocols identified | N |
       | Async/sync boundaries | N |
  </action>
  <constraints>
    - CRITICAL: Every flow step MUST cite file:line
    - CRITICAL: Data shape MUST be documented at each transformation step
    - CRITICAL: At least 1 end-to-end request flow with Mermaid sequence diagram
    - CRITICAL: Each subsection goes in its own file (LL-002)
    - CRITICAL: index.md must link all subsections with summary metrics (LL-001)
  </constraints>
  <output>
    extracted_content: path to output directory with index.md + 5 subsection files
  </output>
</operation>
```

### Operation: validate

**When:** After extraction, validate content against acceptance criteria.

```xml
<operation name="validate">
  <action>
    1. Load acceptance criteria from templates/acceptance-criteria.md
    2. Read extracted content at content_path
    3. Evaluate each criterion:
       a. [REQ] At least 1 end-to-end request flow → check 01-request-flows.md
          contains a complete entry-to-response flow
       b. [REQ] Each flow step cites file:line → scan all steps for path:line format
       c. [REQ] Data shape at each transformation → check 03-data-transformations.md
          or inline shapes in 01-request-flows.md
       d. [REQ] Mermaid sequence diagram for critical flows → check for
          sequenceDiagram blocks in 01-request-flows.md
       e. [OPT] Event-driven flows documented → check 02-event-propagation.md
       f. [OPT] Communication protocols identified → check 04-protocol-details.md
    4. Mark each as PASS, FAIL, or INCOMPLETE
    5. Distinguish FAIL (wrong content) from INCOMPLETE (missing content)
  </action>
  <output>
    validation_result: { section_id, passed, criteria: [{id, status, feedback}], missing_info[] }
  </output>
</operation>
```



### Operation: package

**When:** Format validated content into final subfolder output.

```xml
<operation name="package">
  <action>
    1. Read validated content at content_path
    2. Create output subfolder structure:
       section-06-data-flow/
       ├── index.md                      # Data flow overview with counts
       ├── 01-request-flows.md           # End-to-end request paths
       ├── 02-event-propagation.md       # Event-driven patterns
       ├── 03-data-transformations.md    # Data shape changes
       ├── 04-protocol-details.md        # Communication protocols
       ├── 05-async-sync-boundaries.md   # Async/sync boundaries
       ├── screenshots/
    3. Ensure index.md has summary metrics table and links to each subsection
    4. Verify all flow steps cite file:line
    5. Verify Mermaid sequenceDiagram blocks have correct syntax
    6. Verify data shapes are documented at transformation points
  </action>
  <constraints>
    - CRITICAL: index.md MUST link all subsections with summary metrics (LL-001)
    - CRITICAL: Each subsection in its own file (LL-002)
  </constraints>
  <output>
    package_path: path to section-06-data-flow/ directory
  </output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "extract | validate | package"
  result:
    extracted_content:   # extract — path to output directory
    validation_result:   # validate — { section_id, passed, criteria[], missing_info[] }
    package_path:        # package — path to final subfolder
  errors: []
```

---

## Quality Scoring

**Profile:** Architecture Sections

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Completeness | 0.20 | Ratio of [REQ] criteria satisfied, flow coverage |
| Structure | 0.10 | Proper heading hierarchy, diagrams, subfolder layout |
| Clarity | 0.15 | Clear step descriptions, readable sequence diagrams |
| **Accuracy** | **0.35** | Evidence-backed claims, verified file:line citations |
| Freshness | 0.10 | References current code state |
| Coverage | 0.10 | Breadth across flow types and protocols |

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed successfully</name>
    <verification>operation_output.success is true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Subfolder structure correct</name>
    <verification>Output has index.md + subsection files + screenshots/</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All REQ criteria pass</name>
    <verification>validate operation returns passed: true for all [REQ] items</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>End-to-end flow present</name>
    <verification>01-request-flows.md contains at least 1 complete entry-to-response flow</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>File:line citations at every step</name>
    <verification>Every flow step cites source file:line</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Data shapes documented</name>
    <verification>Data shape recorded at each transformation step</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Mermaid sequence diagrams present</name>
    <verification>At least 1 Mermaid sequenceDiagram block for critical flows</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `PHASE1_NOT_AVAILABLE` | Phase 1 output missing or incomplete | Run Phase 1 scan first |
| `PHASE2_NOT_AVAILABLE` | Phase 2 test knowledge missing | Run Phase 2 test extraction first |
| `INVALID_OPERATION` | Operation not one of the 3 defined | Use: extract, validate, package |
| `CONTENT_NOT_FOUND` | content_path file does not exist | Verify extraction completed |
| `NO_ENTRY_POINTS` | No route handlers or entry points found | Review Phase 1 output; may be a library without request handling |
| `NO_FLOWS_TRACED` | Could not trace any complete flows | Start from integration tests in Phase 2 for flow hints |
| `FRAMEWORK_NOT_RECOGNIZED` | Unknown web framework routing | Fall back to manual call-chain tracing |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/acceptance-criteria.md` | Validation rules with [REQ]/[OPT] markers |
| `templates/extraction-prompts.md` | Per-subsection extraction guidance |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
