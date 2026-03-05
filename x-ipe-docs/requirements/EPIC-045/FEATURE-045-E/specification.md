# Feature Specification: Java & MCP Implementation Tool Skills

> Feature ID: FEATURE-045-E
> Epic ID: EPIC-045
> Version: v1.0
> Status: Refined
> Last Updated: 2026-07-14

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 2026-07-14 | Initial specification |

## Linked Mockups

N/A — This feature creates AI skill files (SKILL.md). No UI components.

## Overview

This feature creates two language-specific implementation tool skills: **x-ipe-tool-implementation-java** and **x-ipe-tool-implementation-mcp**. Both follow the standard tool skill I/O contract defined by the FEATURE-045-A orchestrator.

The Java skill handles Java projects (Spring Boot, Quarkus, Micronaut, plain Java) with built-in SOLID principles, clean architecture patterns, JUnit 5 + Mockito test mapping, and Checkstyle/Google Java Format linting.

The MCP skill handles Model Context Protocol server implementations in Python (FastMCP) and TypeScript (MCP SDK) with built-in protocol compliance, tool schema validation, resource definitions, and transport configuration.

## User Stories

1. **As an AI agent**, I want the orchestrator to route Java tech_stack entries to a Java-specific tool skill, so that implementations follow idiomatic Java patterns and conventions.

2. **As an AI agent**, I want the Java skill to detect the build tool (Maven vs Gradle) and framework automatically, so that generated code integrates with the existing project.

3. **As an AI agent**, I want the orchestrator to route MCP tech_stack entries to an MCP-specific tool skill, so that protocol compliance and schema validation are enforced.

4. **As an AI agent**, I want the MCP skill to support both Python (FastMCP) and TypeScript (MCP SDK), so that it covers the two primary MCP implementation languages.

## Acceptance Criteria

### AC-1: Java Tool Skill — Standard I/O Contract

- [ ] AC-1.1: Accepts standard input (operation, aaa_scenarios, source_code_path, test_code_path, feature_context)
- [ ] AC-1.2: Returns standard output (implementation_files, test_files, test_results, lint_status, stack_identified)
- [ ] AC-1.3: stack_identified format is `Java/{framework}` (e.g., `Java/SpringBoot`, `Java/Quarkus`, `Java/Plain`)

### AC-2: Java Tool Skill — Best Practices

- [ ] AC-2.1: SOLID principles are applied (SRP for classes, DIP for dependencies via constructor injection)
- [ ] AC-2.2: Clean architecture layers enforced (controller/service/repository or equivalent)
- [ ] AC-2.3: Package-by-feature structure used for new modules
- [ ] AC-2.4: Records used for DTOs (Java 16+), Builder pattern for complex objects
- [ ] AC-2.5: Proper exception handling (checked for recoverable, unchecked for programming errors)

### AC-3: Java Tool Skill — Test Mapping & Linting

- [ ] AC-3.1: AAA Assert clauses mapped to JUnit 5 @Test methods with @DisplayName
- [ ] AC-3.2: @Nested classes used for grouping related test scenarios
- [ ] AC-3.3: Mockito used for mocking dependencies (@Mock, @InjectMocks, when/verify)
- [ ] AC-3.4: Checkstyle validation + Google Java Format applied as lint step

### AC-4: Java Tool Skill — Framework & Build Tool Detection

- [ ] AC-4.1: Detects Maven (pom.xml) vs Gradle (build.gradle/build.gradle.kts) build tool
- [ ] AC-4.2: Detects Spring Boot (spring-boot-starter), Quarkus (quarkus-bom), Micronaut (micronaut-core)
- [ ] AC-4.3: Falls back to plain Java when no framework detected
- [ ] AC-4.4: Error `BUILD_TOOL_MISSING` raised when neither pom.xml nor build.gradle found

### AC-5: MCP Tool Skill — Standard I/O Contract

- [ ] AC-5.1: Accepts standard input (operation, aaa_scenarios, source_code_path, test_code_path, feature_context)
- [ ] AC-5.2: Returns standard output (implementation_files, test_files, test_results, lint_status, stack_identified)
- [ ] AC-5.3: stack_identified format is `MCP/{language}` (e.g., `MCP/Python`, `MCP/TypeScript`)

### AC-6: MCP Tool Skill — Protocol Compliance

- [ ] AC-6.1: Tool schemas validated (name, description, input_schema with JSON Schema)
- [ ] AC-6.2: Resource definitions include proper URI templates
- [ ] AC-6.3: Transport configuration supports stdio and SSE types
- [ ] AC-6.4: MCP error codes used in error responses (not generic HTTP errors)

### AC-7: MCP Tool Skill — Language Support

- [ ] AC-7.1: Python implementation uses FastMCP with @mcp.tool decorator pattern
- [ ] AC-7.2: TypeScript implementation uses MCP SDK with server.registerTool pattern
- [ ] AC-7.3: Pydantic models (Python) or Zod schemas (TypeScript) for input validation
- [ ] AC-7.4: Tests validate tool invocation → response at protocol level

## Functional Requirements

| ID | Requirement | Priority | AC Ref |
|----|------------|----------|--------|
| FR-1 | Java skill accepts standard tool skill input and returns standard output | Must | AC-1 |
| FR-2 | Java skill detects build tool (Maven/Gradle) from project files | Must | AC-4 |
| FR-3 | Java skill detects framework from dependency declarations | Must | AC-4 |
| FR-4 | Java skill maps AAA Assert clauses to JUnit 5 tests with @DisplayName | Must | AC-3 |
| FR-5 | Java skill runs Checkstyle + Google Java Format as lint step | Must | AC-3 |
| FR-6 | MCP skill accepts standard tool skill input and returns standard output | Must | AC-5 |
| FR-7 | MCP skill validates tool schemas against MCP protocol spec | Must | AC-6 |
| FR-8 | MCP skill supports Python (FastMCP) and TypeScript (MCP SDK) | Must | AC-7 |
| FR-9 | MCP skill generates protocol-level tests (invoke → validate response) | Must | AC-7 |
| FR-10 | MCP skill configures transport (stdio/SSE) based on project requirements | Should | AC-6 |

## Non-Functional Requirements

| ID | Requirement | Metric |
|----|------------|--------|
| NFR-1 | Both skills must follow the standard tool skill I/O contract exactly | 100% contract compliance |
| NFR-2 | Skills must be self-contained (no external research step for built-in practices) | Zero web fetches for core practices |
| NFR-3 | Each SKILL.md must be under 250 lines | ≤250 lines per file |
| NFR-4 | Error handling must use defined error codes, not generic messages | All errors in error table |

## Out of Scope

- Build tool installation (Maven/Gradle must already be available)
- JDK installation or version management
- MCP Inspector integration (handled by mcp-builder skill)
- MCP evaluation creation (handled by mcp-builder skill Phase 4)
- Kotlin, Scala, or other JVM language support
