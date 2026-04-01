# Application Reverse Engineering — Collection Template

> Per-section extraction prompts guiding what to look for in source code.
> HTML comments contain the actual prompts — the extractor reads these to guide analysis.

---

## 5. Code Structure Analysis

<!-- EXTRACTION PROMPTS:
- Map the root directory tree (first 2-3 levels) with purpose annotations for each directory
- Identify naming conventions: file naming (snake_case, camelCase, PascalCase), class naming, function naming
- Detect module boundary markers: __init__.py, index.ts/js, package.json, go.mod per directory
- Identify layering patterns: controller/service/repository, handler/usecase/entity, routes/middleware/models
- Count files per directory to identify hot spots (most actively developed areas)

SOURCE PRIORITY:
1. Directory tree output (ls -R, tree, or find)
2. README.md / CONTRIBUTING.md for documented structure
3. Build configs (Makefile, package.json scripts, pyproject.toml)
4. Entry points (main.py, index.js, cmd/main.go, App.java)

PHASE CONTEXT:
- Phase: 1-Scan
- Depends on: nothing (first section extracted)
- Output type: inline (Markdown tables)
-->

---

## 7. Technology Stack Identification

<!-- EXTRACTION PROMPTS:
- Parse package manager files for dependency lists: package.json, pyproject.toml, requirements.txt, pom.xml, build.gradle, go.mod, Cargo.toml
- Extract version constraints and lock file versions
- Identify frameworks from imports: Flask/Django/FastAPI, Express/Next.js/Nest, Spring Boot, Gin/Echo
- Detect build tools: webpack, vite, esbuild, tsc, Makefile, Gradle, Maven
- Identify CI/CD: .github/workflows/, Jenkinsfile, .gitlab-ci.yml, Dockerfile
- Detect testing tools: pytest, jest, vitest, JUnit, go test, test frameworks in configs

SOURCE PRIORITY:
1. Package manager files (package.json, pyproject.toml, pom.xml, go.mod)
2. Config files (tsconfig.json, webpack.config.*, .babelrc, setup.cfg)
3. Import statements in source files
4. CI/CD configuration files

PHASE CONTEXT:
- Phase: 1-Scan
- Depends on: nothing (parallel with Section 5)
- Output type: inline (Markdown tables)
-->

---

## 8. Source Code Tests

<!-- EXTRACTION PROMPTS:
- Scan for existing test files: *_test.py, test_*.py, *.test.js, *.spec.ts, *Test.java, *_test.go
- Detect test framework from configs and imports (pytest, jest, vitest, JUnit, testify)
- Catalog existing tests: file path, test count, assertion count, fixture usage
- Copy existing tests to output (copy-first strategy — never modify source)
- Generate missing tests in AAA format (Arrange/Act/Assert) for uncovered modules
- Use project's actual test framework (framework matching rule)
- Execute all tests, record pass/fail per test
- Measure line coverage, identify modules below 80%
- Extract knowledge mapping: what each test reveals about module behavior, integration boundaries, data contracts

SOURCE PRIORITY:
1. Existing test files (highest priority — ground truth)
2. Test configuration files (pytest.ini, jest.config.*, vitest.config.*)
3. README testing section
4. CI/CD test steps

PHASE CONTEXT:
- Phase: 2-Tests
- Depends on: Phase 1 (Section 5 for file structure, Section 7 for test framework)
- Output type: subfolder (executable files + coverage report)

SPECIAL INSTRUCTIONS:
- Ground truth rule: source code is NEVER modified to fix failing tests
- Framework matching: generated tests MUST use the same framework detected in Section 7
- Knowledge extraction: map each test to the module it validates and what behavior it confirms
- Coverage target: ≥80% line coverage; if not achievable, document gaps
-->

---

## 1. Architecture Recovery

<!-- EXTRACTION PROMPTS:
- Analyze module/package structure to identify logical components
- Trace import/dependency chains to understand component relationships
- Identify entry points and request routing (main(), app factory, router registration)
- Classify components by responsibility: handlers, services, repositories, utilities, models
- Build 4-level architecture view:
  Level 1 (Conceptual): Application landscape — what systems/apps exist
  Level 2 (Logical): Module view — how modules relate and their responsibilities
  Level 3 (Physical): Class/file structure — concrete implementations
  Level 4 (Data Flow): Request paths through the system
- Use Architecture DSL for Levels 1-2 (invoke x-ipe-tool-architecture-dsl)
- Use Mermaid class diagrams for Level 3
- Use Mermaid sequence diagrams for Level 4
- Cross-reference with Phase 2 test knowledge: test imports reveal module usage, test mocks reveal boundaries

SOURCE PRIORITY:
1. Source code structure (imports, class definitions, function signatures)
2. Dependency/import graphs
3. Configuration files (routing, DI containers, middleware registration)
4. Phase 2 test-derived knowledge (test imports, mock setups)
5. README / architecture docs (if any)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (structure + tech stack) + Phase 2 (test knowledge)
- Output type: subfolder (Architecture DSL + Mermaid diagrams)
-->

---

## 2. Design Pattern Detection

<!-- EXTRACTION PROMPTS:
- Scan for creational patterns: Factory (create_*, build_*), Singleton (instance caching, module-level state), Builder (fluent chaining)
- Scan for structural patterns: Adapter (wrapping external APIs), Decorator (function decorators, middleware chains), Facade (simplified interfaces)
- Scan for behavioral patterns: Observer (event emitters, pub/sub), Strategy (pluggable algorithms, interface implementations), Command (handler dispatch)
- For each detected pattern:
  a. Cite evidence with file:line references
  b. Assign confidence: 🟢 (clear canonical implementation), 🟡 (partial/informal match), 🔴 (possible but ambiguous)
  c. Describe the pattern's role in the system
- Look for test mocks/stubs — they reveal integration boundaries which indicate pattern usage
- Check for pattern composition (e.g., Factory + Strategy, Observer + Mediator)

SOURCE PRIORITY:
1. Source code structure (class hierarchies, interfaces, abstract classes)
2. Factory functions and constructors
3. Phase 2 test knowledge (mocks reveal isolation boundaries → pattern indicators)
4. Configuration/DI setup files

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (structure) + Phase 2 (test mocks reveal patterns)
- Output type: subfolder (pattern inventory + per-pattern evidence)
-->

---

## 3. API Contract Extraction

<!-- EXTRACTION PROMPTS:
- Internal APIs: find public function/method signatures across module boundaries
- External APIs: detect HTTP route registration (Flask routes, Express router, Spring @RequestMapping, Gin handlers)
- For each API endpoint/function:
  a. Document parameters with types
  b. Document return type / response schema
  c. Document error responses / exceptions
  d. Cite the implementing file:line
- Group APIs by module or service boundary
- Detect API versioning patterns (URL prefix, header, query param)
- Check for API documentation (OpenAPI/Swagger, JSDoc, docstrings)

SOURCE PRIORITY:
1. Source code (route definitions, function signatures, type annotations)
2. API schema files (openapi.yaml, swagger.json)
3. Phase 2 test knowledge (test assertions reveal API contracts)
4. Documentation/README

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (structure) + Phase 2 (test assertions reveal contracts)
- Output type: subfolder (per-API-group files)
-->

---

## 4. Dependency Analysis

<!-- EXTRACTION PROMPTS:
- Inter-module dependencies: trace import/require/include statements between internal modules
- External library dependencies: parse package manager lock files for exact versions
- For each dependency:
  a. Source module/file
  b. Target module/library
  c. Type: import, runtime, dev, optional
  d. Purpose: what functionality it provides
- Build dependency graph (who depends on whom)
- Identify circular dependencies
- Identify heavy/critical dependencies (used by many modules)
- Use Architecture DSL for dependency landscape visualization

SOURCE PRIORITY:
1. Import statements in source files
2. Package manager files (exact versions from lock files)
3. Build configuration (dependency declarations)
4. Phase 2 test knowledge (test fixtures reveal data flow direction)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (structure + tech stack) + Phase 2 (test knowledge)
- Output type: subfolder (per-module dependency files + graphs)
-->

---

## 6. Data Flow / Protocol Analysis

<!-- EXTRACTION PROMPTS:
- Trace end-to-end request flows: entry point → middleware → handler → service → repository → response
- Identify event-driven flows: event emitters, message queues, pub/sub patterns
- Document data transformation chains: how data changes shape between layers
- Identify communication protocols: HTTP REST, gRPC, WebSocket, message queues (RabbitMQ, Kafka, Redis)
- For each flow:
  a. Name the flow (e.g., "User Login Flow", "Order Processing Pipeline")
  b. List each step with file:line citation
  c. Document data shape at each step
  d. Note async/sync boundaries
- Create Mermaid sequence diagrams for critical flows

SOURCE PRIORITY:
1. Source code (middleware chains, handler implementations, service calls)
2. Route/endpoint registration
3. Event handler registrations
4. Phase 2 test knowledge (integration tests reveal data flow paths)

PHASE CONTEXT:
- Phase: 3-Deep
- Depends on: Phase 1 (structure) + Phase 2 (integration test knowledge)
- Output type: subfolder (per-flow trace files + sequence diagrams)
-->
