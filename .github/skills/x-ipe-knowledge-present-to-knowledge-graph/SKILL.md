---
name: x-ipe-knowledge-present-to-knowledge-graph
description: Graph connector that pushes ontology data to the X-IPE knowledge graph server via HTTP callback, with automatic port resolution and auth token discovery. Triggers on operations like "connector", "push to graph".
---

# Present to Knowledge Graph — Knowledge Skill

## Purpose

AI Agents follow this skill to push ontology data to the X-IPE knowledge graph server:
1. Resolve the graph server port (CLI → .x-ipe.yaml → defaults → 5858)
2. Resolve the auth token (CLI → env var → instance/.internal_token)
3. Read the graph JSON data
4. POST to the ontology callback endpoint with retry logic

---

## Important Notes

BLOCKING: This is a single-operation skill. The `connector` operation sends ontology data to the graph server.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`).
CRITICAL: Operations are stateless services — the orchestrator passes full context per call.
CRITICAL: Port resolution follows a strict chain: CLI flag → `.x-ipe.yaml` → `src/x_ipe/defaults/.x-ipe.yaml` → hardcoded 5858. Auth token follows: CLI → `$X_IPE_INTERNAL_TOKEN` → `instance/.internal_token`.

---

## About

This skill connects the knowledge pipeline to the X-IPE graph visualization server. It handles port discovery, authentication, and reliable delivery with retry logic. The graph server exposes an internal callback API that accepts ontology payloads for visualization and querying.

**Key Concepts:**
- **Port Resolution** — 4-level chain: CLI `--port` flag → `.x-ipe.yaml` `server.port` (searched upward from CWD to git root) → defaults file → hardcoded 5858.
- **Auth Token Resolution** — 4-level chain: CLI `--token` flag → `$X_IPE_INTERNAL_TOKEN` env var → `instance/.internal_token` file → error.
- **Callback Endpoint** — `POST http://localhost:{port}/api/internal/ontology/callback` with JSON payload.
- **Retry Logic** — Max 2 attempts, 1-second delay between retries, 10-second timeout per request.
- **writes_to Discipline** — This operation writes only to HTTP (the graph server); no local filesystem writes.

---

## When to Use

```yaml
triggers:
  - "Push ontology to knowledge graph server"
  - "Send ontology callback"
  - "Connect ontology to graph visualization"
```

---

## Input Parameters

```yaml
input:
  operation: connector
  context:
    graph_json: "path to ontology JSON file"
    port: null       # optional — auto-resolved if not provided
    token: null      # optional — auto-resolved if not provided
    query: ""        # original query that triggered pipeline
    scope: ""        # scope hint for callback
```

### Input Initialization

```xml
<input_init>
  <field name="context.graph_json" source="Orchestrator" default="none">
    <validation>Must be a valid file path pointing to a JSON file.</validation>
  </field>
  <field name="context.port" source="CLI flag or auto-resolved" default="auto">
    <validation>If provided, must be a valid port number (1-65535). If 0 or null, triggers auto-resolution.</validation>
  </field>
  <field name="context.token" source="CLI flag, env var, or file" default="auto">
    <validation>Non-empty string. Auto-resolved if not provided.</validation>
  </field>
  <field name="context.query" source="Orchestrator" default="">
    <validation>String (may be empty)</validation>
  </field>
  <field name="context.scope" source="Orchestrator" default="">
    <validation>String (may be empty)</validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Graph JSON file exists</name>
    <verification>context.graph_json points to an existing, valid JSON file</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Auth token resolvable</name>
    <verification>Token available via CLI, env var, or instance/.internal_token file</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: connector

> **Contract:**
> - **Input:** graph_json: string (file path), port: int | null, token: string | null, query: string, scope: string
> - **Output:** callback_status: "delivered" | "failed", server_response: object
> - **Writes To:** HTTP POST to graph server — no local filesystem writes
> - **Delegates To:** `scripts/graph_connector.py connect`
> - **Constraints:** Max 2 retry attempts; 10-second timeout per request

**When:** Orchestrator wants to push ontology data to the graph visualization server.

```xml
<operation name="connector">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ graph JSON at graph_json path
      2. IF file does not exist → return error GRAPH_JSON_NOT_FOUND
      3. IF file is not valid JSON → return error INVALID_GRAPH_JSON
      4. PARSE JSON content into payload
    </action>
    <output>Graph payload loaded or error returned</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. RESOLVE port via chain:
         a. CLI --port flag (if non-zero)
         b. .x-ipe.yaml server.port (search upward from CWD to git root)
         c. src/x_ipe/defaults/.x-ipe.yaml server.port
         d. Hardcoded 5858
      2. RESOLVE auth token via chain:
         a. CLI --token flag
         b. $X_IPE_INTERNAL_TOKEN environment variable
         c. instance/.internal_token file (relative to project root)
         d. IF none found → return error AUTH_TOKEN_NOT_FOUND
    </action>
    <output>Port and token resolved</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. BUILD request payload:
         ```json
         {
           "results": {graph_json_content},
           "subgraph": "ontology",
           "query": "{query}",
           "scope": "{scope}",
           "request_id": "{uuid4}"
         }
         ```
      2. SET URL: http://localhost:{port}/api/internal/ontology/callback
      3. SET headers: Content-Type: application/json, Authorization: Bearer {token}
    </action>
    <output>Request prepared</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY port is in valid range (1-65535)
      2. VERIFY token is non-empty
      3. VERIFY payload is valid JSON
    </action>
    <output>Request validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. EXECUTE:
         ```
         python3 scripts/graph_connector.py connect \
           --graph-json {graph_json} \
           [--port {port}] \
           [--token {token}] \
           [--query {query}] \
           [--scope {scope}]
         ```
      2. Script sends HTTP POST with retry logic (max 2 attempts, 1s delay, 10s timeout)
      3. ON success → callback_status: "delivered"
      4. ON failure → callback_status: "failed" (error details in errors[])
      5. RETURN operation_output
    </action>
    <output>connector complete</output>
  </phase_5>

</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "connector"
  result:
    callback_status: "delivered" | "failed"
    server_response:
      status_code: "int"
      body: "string"
    port_used: "int"
    attempts: "int"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed</name>
    <verification>operation_output returned with callback_status</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Port resolution works</name>
    <verification>Port resolved correctly via 4-level chain</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Auth token resolved</name>
    <verification>Token resolved via 4-level chain or error returned</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Retry logic implemented</name>
    <verification>Max 2 attempts, 1-second delay, 10-second timeout</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Error cases handled</name>
    <verification>GRAPH_JSON_NOT_FOUND, AUTH_TOKEN_NOT_FOUND, CONNECTION_FAILED all produce structured errors</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `GRAPH_JSON_NOT_FOUND` | graph_json path does not exist | Return error with path details |
| `INVALID_GRAPH_JSON` | File is not valid JSON | Return error with parse details |
| `AUTH_TOKEN_NOT_FOUND` | No token available via any resolution path | Return error listing checked paths |
| `CONNECTION_FAILED` | Server unreachable after retries | Return error with last exception details |
| `SERVER_ERROR` | Server returned non-2xx status | Return error with status code and body |

---

## Patterns & Anti-Patterns

| Pattern | When | Key Actions |
|---------|------|-------------|
| Auto-resolve port | Default behavior | Let the 4-level chain find the port |
| Explicit port | Testing or non-default server | Pass --port flag |
| Retry on failure | Transient network errors | Script retries up to 2 times automatically |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Hardcode port | Breaks different environments | Use port resolution chain |
| Skip auth | Security violation | Always resolve and send token |
| No retry | Transient errors cause false failures | Let retry logic handle |

---

## Examples

See `references/examples.md` for worked examples of the connector operation.
