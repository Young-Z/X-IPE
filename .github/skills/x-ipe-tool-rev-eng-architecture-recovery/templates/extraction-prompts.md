# Architecture Recovery — Extraction Prompts

> Per-subsection extraction guidance for Section 1 (Architecture Recovery).
> HTML comments contain the actual prompts — the extractor reads these to guide analysis.

---

## 1.1 Conceptual Level — Application Landscape

<!-- EXTRACTION PROMPTS:
- Identify the application's position in the broader system landscape
- List external systems the application communicates with (databases, APIs, message queues, file systems)
- Identify user types / actor roles that interact with the application
- Define application boundaries: what is inside vs outside this codebase
- Use Architecture DSL landscape-view to visualize:
  a. Invoke x-ipe-tool-architecture-dsl with operation generate_landscape_view
  b. Place the target application centrally
  c. Surround with external systems grouped by interaction type

SOURCE PRIORITY:
1. Configuration files (database URLs, API base URLs, queue connections)
2. Environment variables / .env files
3. Docker Compose / Kubernetes manifests (service dependencies)
4. README / architecture documentation (if any)
5. Import statements referencing external SDKs/clients

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (Section 7 tech stack for external tool identification)
- Output type: subfolder (Architecture DSL landscape view)
- Tool: x-ipe-tool-architecture-dsl (generate_landscape_view)
-->

---

## 1.2 Logical Level — Module/Component View

<!-- EXTRACTION PROMPTS:
- Analyze module/package structure from Phase 1 Section 5 directory mapping
- Trace import/dependency chains to understand component relationships
- Classify components by responsibility:
  a. Handlers / Controllers — request entry points
  b. Services / Use Cases — business logic
  c. Repositories / DAOs — data access
  d. Utilities / Helpers — shared functions
  e. Models / Entities — data structures
  f. Middleware — cross-cutting concerns
- Define layers based on detected layering pattern (from Phase 1)
- Use Architecture DSL module-view to visualize:
  a. Invoke x-ipe-tool-architecture-dsl with operation generate_module_view
  b. Define layers (e.g., Presentation, Business, Data)
  c. Place modules in appropriate layers with cols summing to 12
  d. Each module MUST list: responsibility, source directory, key files
- Cross-reference with Phase 2 test knowledge:
  a. Test imports reveal which modules are actively used
  b. Test mocks reveal isolation boundaries between modules

SOURCE PRIORITY:
1. Source code structure (imports, package definitions, module exports)
2. Phase 1 Section 5 directory-to-purpose mapping
3. Phase 2 Section 8 test-to-module mapping
4. DI container / service registration files
5. README / architecture docs

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (Section 5 structure) + Phase 2 (test knowledge)
- Output type: subfolder (Architecture DSL module view)
- Tool: x-ipe-tool-architecture-dsl (generate_module_view)
-->

---

## 1.3 Physical Level — Class/File Structure

<!-- EXTRACTION PROMPTS:
- For key modules identified in Level 2, drill into class/file structure
- Identify class hierarchies: base classes, abstract classes, interfaces, implementations
- Identify composition relationships: which classes contain references to others
- Focus on "hot" areas: most imported files, largest modules, entry points
- Generate Mermaid classDiagram for each key hierarchy:
  ```mermaid
  classDiagram
    class ClassName {
      +publicMethod() ReturnType
      -privateField: FieldType
    }
    ClassName <|-- SubClass : inherits
    ClassName *-- Component : contains
  ```
- Reference source file paths for each class

SOURCE PRIORITY:
1. Source code (class definitions, interface declarations)
2. Type definition files (.d.ts, .pyi, protocol buffers)
3. Phase 1 Section 5 naming conventions (to locate key files)
4. IDE-generated class diagrams (if available in repo)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Level 2 logical view (module identification)
- Output type: subfolder (Mermaid class diagrams)
-->

---

## 1.4 Data Flow Level — Request/Response Paths

<!-- EXTRACTION PROMPTS:
- Trace critical request paths end-to-end through the system:
  a. Entry point (HTTP handler, CLI command, message consumer)
  b. Middleware chain (auth, validation, logging)
  c. Service/business logic invocation
  d. Data access layer calls
  e. Response construction and return
- For each flow step: cite the implementing file:line
- Document data shape at each step (request → validated input → domain object → response)
- Generate Mermaid sequenceDiagram for each critical flow:
  ```mermaid
  sequenceDiagram
    participant Client
    participant Handler
    participant Service
    participant Repository
    Client->>Handler: HTTP POST /resource
    Handler->>Service: createResource(data)
    Service->>Repository: save(entity)
    Repository-->>Service: saved entity
    Service-->>Handler: result
    Handler-->>Client: 201 Created
  ```
- Cross-reference with Phase 2 integration test flows:
  a. Integration tests often trace the exact same paths
  b. Test assertions reveal expected data shapes at each step

SOURCE PRIORITY:
1. Route/endpoint registration (entry points)
2. Middleware chain configuration
3. Service method implementations
4. Phase 2 integration test flows (ground truth for paths)
5. Logging/tracing setup (reveals flow instrumentation)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Level 2 logical view + Phase 2 integration tests
- Output type: subfolder (Mermaid sequence diagrams)
-->
