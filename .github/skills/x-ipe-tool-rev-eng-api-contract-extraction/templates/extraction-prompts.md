# API Contract Extraction — Extraction Prompts

> Per-subsection extraction guidance for Section 3 (API Contract Extraction).
> HTML comments contain the actual prompts — the extractor reads these to guide analysis.

---

## 3.1 Internal APIs — Module-to-Module Interfaces

<!-- EXTRACTION PROMPTS:
- Find public function/method signatures that cross module boundaries:
  a. Functions/classes imported by other modules (trace import chains)
  b. Exported members from package __init__.py, index.ts, or public API files
  c. Interface/protocol definitions that other modules implement
- For each public API:
  a. Function/method name
  b. Parameters with types (infer from usage if not annotated)
  c. Return type (infer from return statements if not annotated)
  d. Module it belongs to
  e. Implementing file:line
- Group by source module
- Identify most-used internal APIs (imported by 3+ other modules)

SOURCE PRIORITY:
1. Source code (function signatures, type annotations, exports)
2. Phase 1 Section 5 module boundaries (which directories are modules)
3. Phase 2 test imports (tests reveal which APIs are exercised)
4. Type definition files (.d.ts, .pyi)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (module boundaries) + Phase 2 (test imports)
- Output type: subfolder (01-internal-apis.md)
-->

---

## 3.2 External HTTP APIs — REST Endpoints

<!-- EXTRACTION PROMPTS:
- Detect HTTP route registration based on framework (from Phase 1 Section 7):
  a. Flask: @app.route("/path"), @blueprint.route("/path")
  b. FastAPI: @app.get("/path"), @router.post("/path")
  c. Express: router.get("/path", handler), app.use("/path", router)
  d. Spring: @RequestMapping, @GetMapping("/path"), @PostMapping("/path")
  e. Gin: r.GET("/path", handler), group.POST("/path", handler)
  f. Django: urlpatterns = [path("path/", view)]
  g. Generic: grep for common HTTP method registration patterns
- For each endpoint:
  a. HTTP method (GET, POST, PUT, DELETE, PATCH)
  b. URL path (including path parameters like :id or {id})
  c. Query parameters with types
  d. Request body schema (from type annotations, validation decorators, or Pydantic models)
  e. Response schema (from return type or response serializer)
  f. Error responses (HTTP status codes + error body)
  g. Middleware applied (auth, validation, rate limiting)
  h. Handler file:line
- Detect API versioning: /v1/, /v2/ prefixes, Accept-Version header, query param
- Check for OpenAPI/Swagger specs (openapi.yaml, swagger.json)

SOURCE PRIORITY:
1. Route registration code (definitive endpoint list)
2. OpenAPI/Swagger specification files (if present)
3. Phase 2 HTTP test calls (tests reveal request/response contracts)
4. Request/response model definitions
5. API documentation files

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 Section 7 (framework detection) + Phase 2 (HTTP test assertions)
- Output type: subfolder (02-external-http-apis.md)
-->

---

## 3.3 CLI Commands

<!-- EXTRACTION PROMPTS:
- Detect CLI framework from Phase 1 Section 7:
  a. Python: argparse, click, typer, fire
  b. Node: commander, yargs, oclif
  c. Go: cobra, urfave/cli, flag package
  d. Java: picocli, JCommander
- For each command:
  a. Command name and aliases
  b. Positional arguments with types and descriptions
  c. Optional flags/options with defaults
  d. Description / help text
  e. Handler function file:line
- Map subcommand hierarchy (if nested commands exist)
- Check for shell completion definitions

SOURCE PRIORITY:
1. CLI framework command definitions
2. Entry point / main function parsing
3. Phase 2 CLI test cases (test assertions reveal expected behavior)
4. README usage examples

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 Section 7 (CLI framework detection)
- Output type: subfolder (03-cli-commands.md)
- Note: If no CLI detected, create file stating "No CLI commands detected"
-->

---

## 3.4 WebSocket/RPC APIs

<!-- EXTRACTION PROMPTS:
- Detect WebSocket handlers:
  a. socket.io event handlers (on("event", handler))
  b. ws/WebSocket message handlers
  c. Django Channels consumers
  d. Go gorilla/websocket handlers
- Detect RPC definitions:
  a. gRPC .proto service definitions
  b. JSON-RPC method handlers
  c. tRPC router definitions
  d. GraphQL resolvers (type Query, type Mutation)
- For each event/method:
  a. Event name or RPC method name
  b. Request message schema
  c. Response message schema
  d. Handler file:line
  e. Bidirectional vs unidirectional
- Document connection lifecycle (connect, authenticate, subscribe, disconnect)

SOURCE PRIORITY:
1. WebSocket/RPC handler registrations
2. Protocol buffer / GraphQL schema definitions
3. Phase 2 WebSocket/RPC test cases
4. Client-side code (reveals expected API shape)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 Section 7 (framework detection)
- Output type: subfolder (04-websocket-rpc-apis.md)
- Note: If no WebSocket/RPC detected, create file stating "None detected"
-->

---

## 3.5 Plugin/Extension APIs

<!-- EXTRACTION PROMPTS:
- Detect plugin/extension systems:
  a. Plugin interfaces / abstract base classes
  b. Hook registration systems (register_hook, add_plugin, use_extension)
  c. Extension points with defined contracts
  d. SDK / client library public APIs
- For each plugin interface:
  a. Interface/protocol name
  b. Required methods and their signatures
  c. Optional hooks / lifecycle callbacks
  d. Expected behavior contract
  e. Definition file:line
- Document plugin lifecycle (load, initialize, activate, deactivate, unload)
- Check for plugin examples in tests or documentation

SOURCE PRIORITY:
1. Interface/abstract class definitions
2. Plugin registration/loading code
3. Existing plugin implementations (reveal expected interface)
4. Phase 2 plugin test cases

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (module structure)
- Output type: subfolder (05-plugin-extension-apis.md)
- Note: If no plugin system detected, create file stating "None detected"
-->

---

## 3.6 Schema Documentation

<!-- EXTRACTION PROMPTS:
- Collect all request/response type definitions:
  a. Pydantic models, dataclasses, TypedDict
  b. TypeScript interfaces, Zod schemas, io-ts codecs
  c. Go structs with JSON tags
  d. Java DTOs, record classes
  e. Protocol buffer messages
- Document validation rules:
  a. Required vs optional fields
  b. Type constraints (string length, number range, enum values)
  c. Custom validators
- Identify shared types used across multiple APIs
- Map type relationships (inheritance, composition, union types)

SOURCE PRIORITY:
1. Type/model definition files
2. Validation decorator/annotation usage
3. OpenAPI/Swagger schema sections
4. Phase 2 test assertions (reveal expected data shapes)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Subsections 3.1-3.5 (API inventory complete)
- Output type: subfolder (06-schema-documentation.md)
-->
