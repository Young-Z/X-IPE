# Technical Design: Java & MCP Implementation Tool Skills

> Feature ID: FEATURE-045-E | Version: v1.0 | Last Updated: 2026-07-14

> Specification: [specification.md](x-ipe-docs/requirements/EPIC-045/FEATURE-045-E/specification.md)

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating the implementation.
> **📌 AI Coders:** Focus on this section for implementation context.

### Key Components Implemented

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| Java Tool Skill | Implement Java code with built-in SOLID/clean architecture, JUnit 5 tests, Checkstyle linting | `.github/skills/x-ipe-tool-implementation-java/SKILL.md` — new file | #java #tool-skill #spring-boot #junit5 |
| Java Examples | Reference examples for Spring Boot REST + Maven CLI | `.github/skills/x-ipe-tool-implementation-java/references/examples.md` — new file | #java #examples |
| MCP Tool Skill | Implement MCP servers with protocol compliance, tool schemas, transport config | `.github/skills/x-ipe-tool-implementation-mcp/SKILL.md` — new file | #mcp #tool-skill #protocol #fastmcp |
| MCP Examples | Reference examples for Python FastMCP + TypeScript SDK | `.github/skills/x-ipe-tool-implementation-mcp/references/examples.md` — new file | #mcp #examples |

### Dependencies

| Dependency | Source | Design Link | Usage Description |
|------------|--------|-------------|-------------------|
| Orchestrator (FEATURE-045-A) | Existing | [SKILL.md](.github/skills/x-ipe-task-based-code-implementation/SKILL.md) | Routes tech_stack entries to these tool skills |
| Tool Skill I/O Contract | Existing | [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md) | Standard input/output format both skills follow |
| Python Tool Skill (FEATURE-045-B) | Existing | [SKILL.md](.github/skills/x-ipe-tool-implementation-python/SKILL.md) | Structural template for both new skills |
| mcp-builder Skill | Existing | [SKILL.md](.github/skills/mcp-builder/SKILL.md) | MCP domain knowledge (protocol, SDKs, patterns) |

### Major Flow

```
Orchestrator Step 5 routes tech_stack entry:
  ├─ "Java/*" → x-ipe-tool-implementation-java
  │   1. Detect build tool (pom.xml / build.gradle)
  │   2. Detect framework (Spring Boot / Quarkus / Micronaut / Plain)
  │   3. Implement with SOLID + clean architecture
  │   4. Map AAA → JUnit 5 + Mockito tests
  │   5. Lint with Checkstyle + Google Java Format
  │
  └─ "MCP/*" → x-ipe-tool-implementation-mcp
      1. Detect language (Python / TypeScript)
      2. Implement tool/resource definitions
      3. Validate schemas against MCP protocol
      4. Map AAA → protocol-level tests
      5. Lint with language-appropriate linter
```

### Design Metadata

```yaml
program_type: "skills"
tech_stack: ["Markdown/SKILL.md"]
```

---

## Part 2: Implementation Details

### 2.1 Java Tool Skill — Detection Logic

#### Build Tool Detection

```
IF pom.xml exists in project root → Maven
  - Test command: mvn test
  - Dependency check: parse <dependencies> in pom.xml
ELSE IF build.gradle OR build.gradle.kts exists → Gradle
  - Test command: ./gradlew test
  - Dependency check: parse dependencies {} block
ELSE → ERROR: BUILD_TOOL_MISSING
```

#### Framework Detection

```
Read build file dependencies:
  IF contains "spring-boot-starter" → Spring Boot
    - Patterns: @RestController, @Service, @Repository, @Autowired
    - Test: @SpringBootTest, @WebMvcTest, MockMvc
  ELSE IF contains "quarkus-bom" → Quarkus
    - Patterns: @Path, @Inject, CDI beans
    - Test: @QuarkusTest, RestAssured
  ELSE IF contains "micronaut-core" → Micronaut
    - Patterns: @Controller, @Inject, compile-time DI
    - Test: @MicronautTest, HttpClient
  ELSE → Plain Java
    - Patterns: standard Java SE, main() entry
    - Test: plain JUnit 5
```

### 2.2 Java Tool Skill — Test Mapping

AAA scenarios map to JUnit 5 as follows:

| AAA Element | JUnit 5 Mapping |
|-------------|----------------|
| Scenario group | @Nested class with @DisplayName |
| Individual scenario | @Test method with @DisplayName |
| Arrange | Test setup: @BeforeEach, mock stubs (when().thenReturn()) |
| Act | Method/endpoint invocation |
| Assert clause | Single assertion: assertEquals / assertThrows / assertThat |
| Shared fixtures | @ExtendWith(MockitoExtension.class), @Mock, @InjectMocks |

### 2.3 Java Tool Skill — Lint Pipeline

```
1. Run: checkstyle -c google_checks.xml {source_files}
   - If checkstyle unavailable → log warning, skip
2. Run: google-java-format --replace {source_files}
   - If unavailable → log warning, skip
3. Re-run tests if any formatting changes applied
4. Return lint_status: pass | fail | skipped
```

### 2.4 MCP Tool Skill — Language Detection

```
IF pyproject.toml OR requirements.txt contains "mcp" or "fastmcp" → Python/FastMCP
  - Pattern: from mcp.server.fastmcp import FastMCP
  - Decorator: @mcp.tool()
  - Input validation: Pydantic models
  - Test: pytest with mcp client test utilities
ELSE IF package.json contains "@modelcontextprotocol/sdk" → TypeScript/MCP SDK
  - Pattern: import { McpServer } from "@modelcontextprotocol/sdk/server"
  - Registration: server.registerTool(...)
  - Input validation: Zod schemas
  - Test: vitest/jest with SDK test client
ELSE → ERROR: MCP_SDK_NOT_FOUND (attempt Python FastMCP as default)
```

### 2.5 MCP Tool Skill — Protocol Validation

Tool schemas must satisfy:

```yaml
tool_schema_requirements:
  name: "snake_case, descriptive, action-oriented"
  description: "Concise summary of tool functionality"
  input_schema:
    type: "object"
    properties: "JSON Schema with descriptions per field"
    required: "list of required fields"
  annotations:
    readOnlyHint: "boolean"
    destructiveHint: "boolean"
```

Resource definitions must satisfy:

```yaml
resource_requirements:
  uri_template: "protocol://path/{parameter}"
  name: "Human-readable resource name"
  description: "What data this resource provides"
  mimeType: "application/json or text/plain"
```

### 2.6 MCP Tool Skill — Transport Configuration

```
IF project specifies "stdio" transport:
  - Python: mcp.run(transport="stdio")
  - TypeScript: StdioServerTransport
IF project specifies "SSE" transport:
  - Python: mcp.run(transport="sse", host="...", port=...)
  - TypeScript: SSEServerTransport with Express/Fastify
DEFAULT: stdio (simpler, recommended for local tools)
```

### 2.7 MCP Tool Skill — Test Strategy

Protocol-level tests validate the full request→response cycle:

| Test Type | What It Validates |
|-----------|-------------------|
| Tool invocation | Call tool with valid input → correct structured response |
| Schema validation | Call tool with invalid input → proper MCP error code |
| Resource read | Read resource by URI → correct content and mimeType |
| Error handling | Trigger error condition → actionable error message |

### 2.8 Files to Create

| File | Lines | Purpose |
|------|-------|---------|
| `.github/skills/x-ipe-tool-implementation-java/SKILL.md` | ≤250 | Java tool skill definition |
| `.github/skills/x-ipe-tool-implementation-java/references/examples.md` | ~150 | Java usage examples |
| `.github/skills/x-ipe-tool-implementation-mcp/SKILL.md` | ≤250 | MCP tool skill definition |
| `.github/skills/x-ipe-tool-implementation-mcp/references/examples.md` | ~150 | MCP usage examples |

### 2.9 Error Handling Summary

| Skill | Error Code | Trigger | Resolution |
|-------|-----------|---------|------------|
| Java | BUILD_TOOL_MISSING | No pom.xml or build.gradle | Signal orchestrator; cannot proceed |
| Java | JAVA_VERSION_INCOMPATIBLE | Code requires Java version not available | Log warning; attempt with available JDK |
| Java | DEPENDENCY_CONFLICT | Conflicting versions in build file | Log details; orchestrator handles retry |
| Java | TEST_FAILURE | JUnit test fails | Return detailed test_results |
| Java | LINT_UNAVAILABLE | Checkstyle/formatter not found | Return lint_status: "skipped" |
| MCP | PROTOCOL_VIOLATION | Tool/resource doesn't conform to MCP spec | Log violation details; fix and retry |
| MCP | SCHEMA_INVALID | Tool input_schema is not valid JSON Schema | Return validation errors; fix schema |
| MCP | TRANSPORT_UNSUPPORTED | Requested transport not available | Fall back to stdio; log warning |
| MCP | MCP_SDK_NOT_FOUND | Neither FastMCP nor MCP SDK detected | Default to Python FastMCP; log warning |
| MCP | TEST_FAILURE | Protocol-level test fails | Return detailed test_results |
