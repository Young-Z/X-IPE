---
name: x-ipe-tool-implementation-general
description: General-purpose fallback implementation tool skill. Handles any tech stack not covered by language-specific tool skills. Researches best practices before implementing. Called by x-ipe-task-based-code-implementation orchestrator when no specific tool skill matches. Triggers on requests like "implement unknown stack", "general implementation", "fallback implementation".
---

# General Implementation Tool Skill

## Purpose

AI Agents follow this skill to implement code for any tech stack by:
1. Identifying language/framework from source code and AAA scenarios
2. Researching best practices for the identified stack
3. Implementing code following discovered practices
4. Writing tests mapped to AAA scenario Assert clauses
5. Running tests and linting

---

## Important Notes

BLOCKING: This skill is invoked by the `x-ipe-task-based-code-implementation` orchestrator. Do NOT invoke directly unless testing.

CRITICAL: Always research before implementing. This skill handles unfamiliar tech stacks — blind implementation without research leads to anti-pattern code.

MANDATORY: Follow the standard tool skill I/O contract defined in [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md).

---

## About

The General Implementation Tool Skill is a fallback for when no language-specific tool skill (e.g., `x-ipe-tool-implementation-python`, `x-ipe-tool-implementation-typescript`) matches the `tech_stack` entry routed by the orchestrator.

**Key Concepts:**
- **Research-First** — Unlike language-specific skills that have built-in best practices, this skill MUST research before coding
- **AAA Contract** — Receives AAA scenarios and must return standard tool skill output (implementation_files, test_files, test_results, lint_status)
- **Stack Discovery** — Identifies the language and framework from source code structure, file extensions, and AAA scenario content

---

## When to Use

```yaml
triggers:
  - "No language-specific tool skill matches tech_stack entry"
  - "Orchestrator routes to general fallback"
  - "Unknown or rare tech stack implementation"

not_for:
  - "x-ipe-tool-implementation-python: for Python/Flask/FastAPI/Django"
  - "x-ipe-tool-implementation-html5: for HTML/CSS/JavaScript"
  - "x-ipe-tool-implementation-typescript: for TypeScript/React/Vue/Angular"
  - "x-ipe-tool-implementation-java: for Java/Spring Boot"
  - "x-ipe-tool-implementation-mcp: for MCP servers"
```

---

## Input Parameters

```yaml
input:
  operation: "implement"
  aaa_scenarios:
    - scenario_text: "{tagged AAA scenario text}"
  source_code_path: "{path to source directory}"
  test_code_path: "{path to test directory}"
  feature_context:
    feature_id: "{FEATURE-XXX-X}"
    feature_title: "{title}"
    technical_design_link: "{path to technical-design.md}"
    specification_link: "{path to specification.md}"
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Always 'implement' when called by orchestrator" />
  <field name="aaa_scenarios" source="Filtered scenarios from orchestrator Step 5" />
  <field name="source_code_path" source="From technical design Part 2" />
  <field name="test_code_path" source="From technical design Part 2 or project convention" />
  <field name="feature_context" source="From orchestrator's Feature Data Model" />
</input_init>
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

**When:** Orchestrator routes an unmapped tech_stack entry to this skill

```xml
<operation name="implement">
  <action>
    1. IDENTIFY language and framework:
       a. Check file extensions in source_code_path
       b. Check package files (Cargo.toml, go.mod, build.gradle, etc.)
       c. Parse AAA scenario content for technology hints
       d. Read technical design for explicit tech references
    2. RESEARCH best practices:
       a. Search for official documentation of identified language/framework
       b. Look for testing frameworks appropriate for the stack
       c. Check linting tools available
       d. Identify project structure conventions
    3. LEARN existing code structure:
       a. Read existing files in source_code_path
       b. Identify coding patterns already in use
       c. Follow existing conventions (naming, imports, structure)
    4. IMPLEMENT code:
       a. Follow technical design Part 2 exactly
       b. Create source files in source_code_path
       c. Apply discovered best practices
       d. Follow KISS/YAGNI principles
    5. WRITE tests mapped to AAA scenarios:
       a. FOR EACH AAA scenario:
          - Create test function named after scenario
          - Arrange section → test setup
          - Act section → test action
          - Assert section → test assertions
       b. Use discovered testing framework
       c. Place test files in test_code_path
    6. RUN tests:
       a. Execute all test files
       b. Record pass/fail for each Assert clause
    7. RUN linting:
       a. Use discovered linting tool
       b. Fix any linting errors
       c. Re-run tests after fixes
    8. RETURN standard output
  </action>
  <constraints>
    - BLOCKING: Steps 1-2 (identify + research) MUST complete before Step 4 (implement)
    - CRITICAL: Follow existing code conventions in source_code_path
    - MANDATORY: Every AAA Assert clause must map to a test assertion
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
      - "{path to created source file 2}"
    test_files:
      - "{path to created test file 1}"
    test_results:
      - scenario: "{scenario name}"
        assert_clause: "{assert text}"
        status: "pass | fail"
        error: "{error message if fail}"
    lint_status: "pass | fail"
    lint_details: "{details if fail}"
    stack_identified: "{language/framework identified}"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Language/framework identified</name>
    <verification>stack_identified field is populated in output</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Research completed before implementation</name>
    <verification>Agent researched best practices before writing code</verification>
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
    <name>Lint passes</name>
    <verification>lint_status == "pass"</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `STACK_UNIDENTIFIABLE` | Cannot determine language from source path or scenarios | Ask orchestrator for explicit tech_stack hint; if unavailable, signal human |
| `NO_TEST_FRAMEWORK` | Cannot find appropriate testing framework | Research language's standard testing tools; install if needed |
| `LINT_UNAVAILABLE` | No linting tool found for identified stack | Log warning, return lint_status: "skipped", continue |
| `TEST_FAILURE` | One or more Assert clauses fail | Return detailed test_results with error messages; orchestrator handles retry |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-implementation-general/references/examples.md) for usage examples.
