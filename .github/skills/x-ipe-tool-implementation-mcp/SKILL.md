---
name: x-ipe-tool-implementation-mcp
description: MCP-specific implementation tool skill. Handles Model Context Protocol server implementations in Python (FastMCP) and TypeScript (MCP SDK) with built-in protocol compliance, tool schema validation, and transport configuration. No research step for protocol practices — they are baked in. Called by x-ipe-task-based-code-implementation orchestrator. Triggers on MCP tech_stack entries.
---

# MCP Implementation Tool Skill

## Purpose

AI Agents follow this skill to implement MCP servers by:
1. Learning existing code structure and detecting language (Python/TypeScript)
2. Implementing with built-in MCP protocol practices (tool schemas, resources, transport)
3. Writing protocol-level tests mapped to AAA scenario Assert clauses
4. Running tests and linting (ruff for Python, eslint/tsc for TypeScript)

---

## Important Notes

BLOCKING: This skill is invoked by the `x-ipe-task-based-code-implementation` orchestrator. Do NOT invoke directly unless testing.

CRITICAL: No research step is needed for MCP protocol practices — they are built into this skill. However, research MAY be needed for the **domain** the MCP server covers (e.g., a GitHub API MCP server needs GitHub API docs).

MANDATORY: Follow the standard tool skill I/O contract defined in [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md).

REFERENCE: For extended MCP domain knowledge (evaluations, inspector, advanced patterns), see [mcp-builder SKILL.md](.github/skills/mcp-builder/SKILL.md).

---

## When to Use

```yaml
triggers:
  - "tech_stack contains MCP, FastMCP, MCP SDK"
  - "tech_stack contains MCP server, MCP tool"
  - "Orchestrator routes MCP-related entry to this skill"

not_for:
  - "x-ipe-tool-implementation-python: for general Python (non-MCP)"
  - "x-ipe-tool-implementation-typescript: for general TypeScript (non-MCP)"
  - "x-ipe-tool-implementation-java: for Java projects"
  - "x-ipe-tool-implementation-general: for unknown/rare stacks"
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

**When:** Orchestrator routes an MCP tech_stack entry to this skill

```xml
<operation name="implement">
  <action>
    1. LEARN existing code:
       a. Read existing files in source_code_path
       b. Detect language/SDK:
          - Check pyproject.toml/requirements.txt for "mcp" or "fastmcp" → Python/FastMCP
          - Check package.json for "@modelcontextprotocol/sdk" → TypeScript/MCP SDK
          - Neither found → default to Python/FastMCP, log warning
       c. Detect transport from existing config or project requirements:
          - Default: stdio (local tools)
          - SSE: if server needs remote HTTP access
       d. Follow existing conventions (naming, structure, error handling)

    2. IMPLEMENT with built-in MCP protocol practices:
       a. Follow technical design Part 2 exactly
       b. Tool definitions must include:
          - name: snake_case, action-oriented (e.g., search_issues, create_file)
          - description: concise summary of tool functionality
          - input_schema: JSON Schema with type, properties, required, descriptions
       c. Resource definitions must include:
          - uri_template: protocol://path/{parameter}
          - name: human-readable resource name
          - description: what data this resource provides
          - mimeType: application/json or text/plain
       d. Annotations on all tools:
          - readOnlyHint, destructiveHint, idempotentHint, openWorldHint
       e. Apply language-specific patterns:
          - Python/FastMCP:
            * from mcp.server.fastmcp import FastMCP
            * @mcp.tool() decorator for tools
            * @mcp.resource() decorator for resources
            * Pydantic models for input validation
            * Async functions for I/O operations
          - TypeScript/MCP SDK:
            * import { McpServer } from "@modelcontextprotocol/sdk/server"
            * server.registerTool(...) with Zod schemas
            * server.registerResource(...) for resources
            * Proper TypeScript types for all inputs/outputs
       f. Transport configuration:
          - stdio: mcp.run(transport="stdio") / StdioServerTransport
          - SSE: mcp.run(transport="sse") / SSEServerTransport
       g. Error handling with MCP error codes (not generic HTTP errors)
       h. Follow KISS/YAGNI — implement only what design specifies

    3. WRITE protocol-level tests mapped to AAA scenarios:
       a. FOR EACH AAA scenario:
          - Create test function/method for scenario
          - Arrange → set up MCP client, prepare test inputs
          - Act → invoke tool/read resource via protocol
          - Assert → validate response structure, content, error codes
       b. Language-specific test patterns:
          - Python/FastMCP:
            * pytest with async test support
            * Test tool invocation: call_tool(name, arguments) → validate result
            * Test schema: verify input_schema matches expected JSON Schema
          - TypeScript/MCP SDK:
            * vitest or jest with MCP test client
            * Test tool invocation: client.callTool({name, arguments}) → validate
            * Test schema: verify Zod schema validation
    4. RUN tests:
       a. Python: python -m pytest {test_code_path} -v
       b. TypeScript: npx vitest run (or npm test)
       c. Record pass/fail for each Assert clause

    5. RUN linting:
       a. Python: ruff check + ruff format (fallback: flake8 + black)
       b. TypeScript: npx eslint + npx tsc --noEmit
       c. If tools unavailable → log warning, lint_status: "skipped"
       d. Re-run tests after any lint-induced changes

    6. RETURN standard output
  </action>
  <constraints>
    - CRITICAL: No research step for MCP protocol — practices are built into Step 2
    - NOTE: Research MAY be needed for the domain API the MCP server wraps
    - CRITICAL: Follow existing code conventions found in Step 1
    - MANDATORY: Every AAA Assert clause must map to exactly one test assertion
    - MANDATORY: All tool definitions must include annotations
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
    stack_identified: "MCP/{language}"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Language detected</name>
    <verification>stack_identified contains "MCP/{language}" in output</verification>
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
    <name>Tool schemas validated</name>
    <verification>All tool definitions include name, description, input_schema, annotations</verification>
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
| `PROTOCOL_VIOLATION` | Tool or resource doesn't conform to MCP spec | Log violation details; fix schema/response and retry |
| `SCHEMA_INVALID` | Tool input_schema is not valid JSON Schema | Return validation errors; fix schema definitions |
| `TRANSPORT_UNSUPPORTED` | Requested transport type not available in SDK | Fall back to stdio; log warning |
| `MCP_SDK_NOT_FOUND` | Neither FastMCP nor MCP SDK detected in dependencies | Default to Python/FastMCP; log warning |
| `TEST_FAILURE` | Protocol-level test fails | Return detailed test_results with error messages |
| `LINT_UNAVAILABLE` | Linting tools not found | Log warning, return lint_status: "skipped", continue |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-implementation-mcp/references/examples.md) for usage examples.
