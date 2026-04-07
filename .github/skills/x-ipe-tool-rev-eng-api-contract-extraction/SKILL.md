---
name: x-ipe-tool-rev-eng-api-contract-extraction
version: "1.0"
description: Section 3 — API Contract Extraction for application reverse engineering (Phase 3-Deep). Extracts Internal APIs, External HTTP APIs, CLI Commands, WebSocket/RPC APIs, Plugin/Extension APIs, and Schema Documentation. Triggers on "API contract extraction", "endpoint documentation", "API inventory".
section_id: 3
phase: "3-Deep"
categories: ["application-reverse-engineering"]
---

# API Contract Extraction — Section 3

## Purpose

AI Agents follow this skill to extract and document API contracts from a target codebase:
1. Catalog Internal APIs (module-to-module interfaces)
2. Document External HTTP APIs (REST endpoints with schemas)
3. Capture CLI Commands, WebSocket/RPC APIs, and Plugin/Extension APIs
4. Document request/response schemas with parameter types and validation rules

---

## Important Notes

BLOCKING: This is a **tool skill** — it is invoked by `x-ipe-task-based-application-knowledge-extractor` during Phase 3-Deep extraction. Do not invoke standalone.
CRITICAL: Phase 1 scan output (Sections 5 + 7) and Phase 2 test knowledge (Section 8) MUST be available before this skill runs.
CRITICAL: Every API MUST cite the implementing file:line. APIs without citations are rejected.
CRITICAL: Output MUST use subfolder structure with `index.md` linking subsections (LL-001, LL-002).

---

## When to Use

```yaml
triggers:
  - "API contract extraction"
  - "endpoint documentation"
  - "API inventory from source"
  - "section 3 extraction"
  - "REST endpoint scan"

not_for:
  - "Data flow analysis" → Section 6
  - "Dependency analysis" → Section 4
  - "API design (new APIs)" → not reverse engineering
```

---

## Input Parameters

```yaml
input:
  operation: "extract | validate | package"
  section_id: "3-api-contract-extraction"
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
      1. Must contain Section 5 (code structure) for module boundary identification
      2. Must contain Section 7 (tech stack) for framework-specific route detection
      3. Read detected frameworks to know route registration patterns
    </steps>
  </field>
  <field name="phase2_output" source="Phase 2 test knowledge directory">
    <steps>
      1. Must contain Section 8 (test knowledge extraction)
      2. Read test assertions — they reveal API contracts and expected responses
      3. Read integration test HTTP calls for endpoint discovery
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

**When:** Orchestrator requests API contract extraction for Section 3.

```xml
<operation name="extract">
  <action>
    1. Read Phase 1 output:
       a. From Section 5: module boundaries, public vs internal directories
       b. From Section 7: detected frameworks for route pattern matching
          - Flask: @app.route, @blueprint.route
          - Express: router.get/post/put/delete, app.use
          - FastAPI: @app.get/post, @router.get/post
          - Spring: @RequestMapping, @GetMapping, @PostMapping
          - Gin: r.GET, r.POST, group.Use
    2. Read Phase 2 output:
       a. From Section 8: test assertions revealing API contracts
       b. HTTP client calls in tests revealing endpoints
    3. Extract Internal APIs (module-to-module):
       a. Find public function/method signatures crossing module boundaries
       b. Document: function name, parameters with types, return type, module
       c. Output: 01-internal-apis.md
    4. Extract External HTTP APIs:
       a. Detect HTTP route registrations using framework patterns
       b. For each endpoint: method, path, parameters, request body schema,
          response schema, error responses, middleware, implementing file:line
       c. Detect API versioning patterns (URL prefix, header, query param)
       d. Output: 02-external-http-apis.md
    5. Extract CLI Commands:
       a. Detect CLI frameworks: argparse, click, cobra, urfave/cli, commander
       b. For each command: name, arguments, flags, description, handler file:line
       c. Output: 03-cli-commands.md
    6. Extract WebSocket/RPC APIs:
       a. Detect WebSocket handlers, gRPC service definitions, message handlers
       b. For each: event/method name, request schema, response schema, file:line
       c. Output: 04-websocket-rpc-apis.md
    7. Extract Plugin/Extension APIs:
       a. Detect plugin interfaces, hook systems, extension points
       b. For each: interface name, methods, expected behavior, file:line
       c. Output: 05-plugin-extension-apis.md
    8. Document Schemas:
       a. Collect request/response type definitions
       b. Document validation rules (required fields, constraints)
       c. Output: 06-schema-documentation.md
    9. Create index.md with API inventory table:
       | API Group | Type | Endpoint Count | Module | Reference |
  </action>
  <constraints>
    - CRITICAL: Every API MUST cite implementing file:line
    - CRITICAL: Parameters MUST include types (inferred if not annotated)
    - CRITICAL: APIs MUST be grouped by module or service boundary
    - CRITICAL: Each subsection in its own file (LL-002)
    - BLOCKING: Skip subsections with no APIs (create file noting "None detected")
  </constraints>
  <output>
    extracted_content: path to output directory with index.md + 6 subsection files
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
       a. [REQ] API inventory table present → check index.md
       b. [REQ] Parameters with types documented → check subsection files
       c. [REQ] Return type / response schema → check each API entry
       d. [REQ] Grouped by module or service → check section organization
       e. [REQ] File:line citations → verify path:line format present
       f. [OPT] Error responses documented → check for error sections
       g. [OPT] API versioning patterns → check for versioning notes
    4. Mark each as PASS, FAIL, or INCOMPLETE
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
       section-03-api-contracts/
       ├── index.md                     # API overview with endpoint counts
       ├── 01-internal-apis.md
       ├── 02-external-http-apis.md
       ├── 03-cli-commands.md
       ├── 04-websocket-rpc-apis.md
       ├── 05-plugin-extension-apis.md
       ├── 06-schema-documentation.md
       ├── screenshots/
    3. Ensure index.md has API inventory table with endpoint counts
    4. Verify all file:line citations are present
    5. Verify parameter types are documented for every API
  </action>
  <constraints>
    - CRITICAL: index.md MUST contain API inventory table (LL-001)
    - CRITICAL: Each API group in its own file (LL-002)
  </constraints>
  <output>
    package_path: path to section-03-api-contracts/ directory
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

**Profile:** Other Sections

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Completeness** | **0.30** | Ratio of [REQ] criteria satisfied, API coverage |
| Structure | 0.20 | Proper grouping, inventory table, subsection layout |
| Clarity | 0.20 | Clear parameter documentation, readable schemas |
| Accuracy | 0.15 | Correct signatures, valid file:line citations |
| Freshness | 0.10 | References current code state and versions |
| Coverage | 0.05 | Breadth across API types and modules |

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
    <name>API inventory table present</name>
    <verification>index.md contains table with API Group, Type, Endpoint Count columns</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Parameter types documented</name>
    <verification>Every API entry documents parameters with types and return type</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `PHASE1_NOT_AVAILABLE` | Phase 1 output missing | Run Phase 1 scan first |
| `PHASE2_NOT_AVAILABLE` | Phase 2 test knowledge missing | Run Phase 2 test extraction first |
| `INVALID_OPERATION` | Operation not one of the 3 defined | Use: extract, validate, package |
| `CONTENT_NOT_FOUND` | content_path file does not exist | Verify extraction completed |
| `NO_APIS_DETECTED` | No APIs found in codebase | Document "no APIs detected"; may be a library |
| `FRAMEWORK_NOT_RECOGNIZED` | Unknown web framework | Fall back to generic route pattern scanning |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/acceptance-criteria.md` | Validation rules with [REQ]/[OPT] markers |
| `templates/extraction-prompts.md` | Per-subsection extraction guidance |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
