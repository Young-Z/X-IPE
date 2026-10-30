---
name: x-ipe-tool-implementation-java
description: Java-specific implementation tool skill. Handles Spring Boot, Quarkus, Micronaut, and plain Java projects with built-in best practices (SOLID, clean architecture, JUnit 5). No research step needed — practices are baked in. Called by x-ipe-task-based-code-implementation orchestrator. Triggers on Java tech_stack entries.
---

# Java Implementation Tool Skill

## Purpose

AI Agents follow this skill to implement Java code by:
1. Learning existing code structure and detecting framework/build tool
2. Implementing with built-in Java best practices (SOLID, clean architecture, records, builder)
3. Writing JUnit 5 + Mockito tests mapped to AAA scenario Assert clauses
4. Running tests and linting (Checkstyle + Google Java Format)

---

## Important Notes

BLOCKING: This skill is invoked by the `x-ipe-task-based-code-implementation` orchestrator. Do NOT invoke directly unless testing.

CRITICAL: No research step is needed — Java best practices are built into this skill. Skip identification/research and go straight to learning existing code.

MANDATORY: Follow the standard tool skill I/O contract defined in [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md).

---

## When to Use

```yaml
triggers:
  - "tech_stack contains Java, Spring Boot, Quarkus, Micronaut"
  - "tech_stack contains Java CLI, Java library"
  - "Orchestrator routes Java-related entry to this skill"

not_for:
  - "x-ipe-tool-implementation-python: for Python/Flask/FastAPI/Django"
  - "x-ipe-tool-implementation-html5: for HTML/CSS/JavaScript"
  - "x-ipe-tool-implementation-typescript: for TypeScript/React/Vue/Angular"
  - "x-ipe-tool-implementation-mcp: for MCP servers"
  - "x-ipe-tool-implementation-general: for unknown/rare stacks"
```

---

## Input Parameters

```yaml
input:
  operation: "implement"  # Supported: "implement" | "fix" | "refactor"
  aaa_scenarios:
    - scenario_text: "{tagged AAA scenario text}"
  source_code_path: "{path to source directory}"
  test_code_path: "{path to test directory}"
  feature_context:  # OPTIONAL for "fix"/"refactor"; REQUIRED for "implement"
    feature_id: "{FEATURE-XXX-X}"
    feature_title: "{title}"
    technical_design_link: "{path to technical-design.md}"
    specification_link: "{path to specification.md}"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>AAA scenarios provided</name>
    <verification>aaa_scenarios array is non-empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Source code path valid</name>
    <verification>source_code_path directory exists or can be created</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature context complete</name>
    <verification>feature_id and technical_design_link are provided</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: implement

**When:** Orchestrator routes a Java tech_stack entry to this skill

```xml
<operation name="implement">
  <action>
    1. LEARN existing code:
       a. Read existing files in source_code_path
       b. Detect build tool:
          - Check for pom.xml → Maven (test: mvn test)
          - Check for build.gradle / build.gradle.kts → Gradle (test: ./gradlew test)
          - Neither found → ERROR: BUILD_TOOL_MISSING
       c. Detect framework from build file dependencies:
          - spring-boot-starter → Spring Boot
          - quarkus-bom → Quarkus
          - micronaut-core → Micronaut
          - None matched → Plain Java
       d. Follow existing conventions (naming, packages, error handling)

    2. IMPLEMENT with built-in Java best practices:
       a. Follow technical design Part 2 exactly
       b. SOLID principles:
          - SRP: one responsibility per class
          - OCP: extend via interfaces, not modification
          - LSP: subtypes substitutable for base types
          - ISP: small, focused interfaces
          - DIP: depend on abstractions, inject via constructor
       c. Clean architecture layers:
          - Controller/Resource → handles HTTP/input
          - Service → business logic
          - Repository → data access
       d. Package-by-feature for new modules
       e. Records for DTOs and value objects (Java 16+)
       f. Builder pattern for complex objects with many optional fields
       g. Exception handling:
          - Checked exceptions for recoverable errors
          - Unchecked (RuntimeException) for programming errors
          - Custom exception classes with meaningful messages
       h. Apply framework-specific patterns:
          - Spring Boot: @RestController, @Service, @Repository, @Autowired / constructor injection
          - Quarkus: @Path, @Inject, CDI beans, REST resources
          - Micronaut: @Controller, @Inject, compile-time DI
          - Plain Java: standard SE patterns, main() entry point
       i. Follow KISS/YAGNI — implement only what design specifies

    3. WRITE JUnit 5 tests mapped to AAA scenarios:
       a. FOR EACH AAA scenario group:
          - Create @Nested class with @DisplayName("{scenario group}")
       b. FOR EACH AAA scenario:
          - Create @Test method with @DisplayName("{scenario name}")
          - Arrange → @BeforeEach setup, @Mock stubs (when().thenReturn())
          - Act → method call, MockMvc request, or RestAssured call
          - Assert → one assertion per Assert clause (assertEquals, assertThrows, assertThat)
       c. Use @ExtendWith(MockitoExtension.class) for mock injection
       d. Framework test patterns:
          - Spring Boot: @SpringBootTest, @WebMvcTest, MockMvc
          - Quarkus: @QuarkusTest, RestAssured
          - Micronaut: @MicronautTest, HttpClient
          - Plain Java: plain JUnit 5 + Mockito

    4. RUN tests:
       a. Maven: mvn test -pl {module} (or mvn test if single module)
       b. Gradle: ./gradlew test
       c. Record pass/fail for each Assert clause

    5. RUN linting:
       a. Execute: checkstyle -c google_checks.xml {source_files}
       b. Execute: google-java-format --replace {source_files}
       c. If tools unavailable → log warning, lint_status: "skipped"
       d. Re-run tests after any formatting changes

    6. RETURN standard output
  </action>
  <constraints>
    - CRITICAL: No research step — Java best practices are built into Step 2
    - CRITICAL: Follow existing code conventions found in Step 1
    - MANDATORY: Every AAA Assert clause must map to exactly one test assertion
    - MANDATORY: Use constructor injection (not field injection) for Spring Boot
  </constraints>
  <output>Standard tool skill output (implementation_files, test_files, test_results, lint_status)</output>
</operation>

<operation name="fix">
  <action>
    1. LEARN existing code: scan source_code_path for conventions, build system (Maven/Gradle), patterns
    2. IF feature_context is absent: generate synthetic context (feature_id: "BUG-{task_id}", technical_design_link: "N/A")
    3. WRITE failing test from AAA scenario:
       a. FOR EACH AAA scenario:
          - Create test: @Test void testFix_{scenarioName}() { ... }
          - Arrange → reproduce bug preconditions
          - Act → trigger the buggy action
          - Assert → expected CORRECT behavior (JUnit assertions)
    4. RUN test → MUST FAIL (TDD gate)
       - IF test passes → STOP, report: "TDD gate violation — test already passes, review scenario"
    5. IMPLEMENT minimal fix following Java best practices:
       - Code style, proper exception handling, existing conventions
       - Only change what is necessary to make the test pass
    6. RUN test → MUST PASS
    7. RUN all existing tests → no regressions
    8. RUN linting: checkstyle or spotless (if configured)
    9. RETURN standard output
  </action>
  <constraints>
    - BLOCKING: Test MUST fail before fix (Step 4) — TDD gate
    - CRITICAL: Minimal fix only — do not refactor during a fix
    - MANDATORY: Feature_context is OPTIONAL — use synthetic fallback if absent
    - MANDATORY: Detect Maven vs Gradle for test runner
  </constraints>
  <output>Standard tool skill output (implementation_files, test_files, test_results, lint_status)</output>
</operation>

<operation name="refactor">
  <action>
    1. LEARN existing code: scan source_code_path for conventions, build system, patterns
    2. IF feature_context is absent: generate synthetic context (feature_id: "REFACTOR-{task_id}", technical_design_link: "N/A")
    3. RUN existing tests → establish baseline (all must pass)
       - IF any test fails → STOP, report: "Cannot refactor — baseline tests failing"
    4. RESTRUCTURE code per AAA scenario target state:
       a. FOR EACH AAA scenario:
          - Read target state from Assert clauses
          - Apply structural changes following Java best practices
          - Preserve external behavior
    5. UPDATE imports and references across affected files
    6. RUN all tests → MUST pass (behavior preserved)
       - IF tests fail → report failed scenarios with details; do NOT auto-revert
    7. RUN linting: checkstyle or spotless (if configured)
    8. RETURN standard output
  </action>
  <constraints>
    - BLOCKING: Baseline tests must pass before refactoring (Step 3)
    - CRITICAL: Preserve behavior — no functional changes
    - CRITICAL: Do NOT manage git commits — orchestrator handles checkpointing
    - MANDATORY: Feature_context is OPTIONAL — use synthetic fallback if absent
  </constraints>
  <output>Standard tool skill output (implementation_files, test_files, test_results, lint_status)</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    implementation_files:
      - "{path to created source file 1}"
    test_files:
      - "{path to created test file 1}"
    test_results:
      - scenario: "{scenario name}"
        assert_clause: "{assert text}"
        status: "pass | fail"
        error: "{error message if fail}"
    lint_status: "pass | fail | skipped"
    lint_details: "{details if fail}"
    stack_identified: "Java/{framework}"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Build tool and framework detected</name>
    <verification>stack_identified contains "Java/{framework}" in output</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Implementation files created</name>
    <verification>implementation_files array is non-empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test files created</name>
    <verification>test_files array is non-empty</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All AAA Assert clauses mapped to tests</name>
    <verification>test_results count equals total Assert clauses across all scenarios</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Lint passes or skipped</name>
    <verification>lint_status == "pass" or lint_status == "skipped"</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `BUILD_TOOL_MISSING` | No pom.xml or build.gradle found in project | Signal orchestrator; cannot proceed without build tool |
| `JAVA_VERSION_INCOMPATIBLE` | Code requires Java version not available | Log warning; attempt with available JDK; signal if incompatible |
| `DEPENDENCY_CONFLICT` | Conflicting dependency versions in build file | Log conflict details; orchestrator handles retry |
| `TEST_FAILURE` | One or more JUnit assertions fail | Return detailed test_results with error messages |
| `LINT_UNAVAILABLE` | Checkstyle or google-java-format not found | Log warning, return lint_status: "skipped", continue |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-implementation-java/references/examples.md) for usage examples.
