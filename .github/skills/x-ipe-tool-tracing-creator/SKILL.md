---
name: x-ipe-tool-tracing-creator
description: Creates tracing utility infrastructure for a target project/language. Generates decorator templates, log writers, and configuration. Use when setting up tracing for a new project or adding tracing support to existing project. Triggers on "create tracing utility", "set up tracing for", "add tracing infrastructure".
---

# Tool: Tracing Creator

## Purpose

AI Agents follow this skill to create tracing utility infrastructure for a project by:
1. Detecting target language (Python/TypeScript)
2. Generating tracing decorator/wrapper code
3. Creating log writer, buffer, and context modules
4. Setting up configuration files
5. Adding sensitive data redaction

---

## Important Notes

BLOCKING: Language must be detected or explicitly specified before generating any files.
CRITICAL: All generated code must include sensitive data redaction - never trace raw passwords, tokens, or keys.

---

## About

This tool scaffolds a complete tracing infrastructure for a project, producing decorator/wrapper code that instruments functions with automatic entry/exit logging, timing, and error capture.

**Key Concepts:**
- **Tracing Decorator** - Function wrapper (`@x_ipe_tracing` / `@xIpeTracing`) that captures call metadata
- **TraceContext** - Thread-local/async-local storage for correlating traces within a request
- **Redactor** - Pattern-based filter that masks sensitive fields (passwords, tokens, keys, auth, financial)
- **TraceBuffer** - In-memory accumulator that batches trace entries before writing

---

## When to Use

```yaml
triggers:
  - "create tracing utility for {project}"
  - "set up tracing for {language} project"
  - "add tracing infrastructure to {path}"
  - "generate tracing decorators for {project}"
  - "initialize tracing system"

not_for:
  - "instrument existing routes with tracing (use x-ipe-tool-tracing-instrumentation)"
  - "view or query trace logs (use tracing dashboard)"
```

---

## Input Parameters

```yaml
input:
  target_path: "string (required) - Project root or source directory"
  language: "string (default: auto) - python | typescript | auto"
  log_path: "string (default: instance/traces/) - Directory for trace log files"
  retention_hours: "int (default: 24) - Hours to retain log files"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Target path exists</name>
    <verification>Confirm target_path is a valid directory</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Language determinable</name>
    <verification>Language is specified, or project contains pyproject.toml/setup.py/requirements.txt (Python) or package.json/tsconfig.json (TypeScript)</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Detect Language

**When:** `language="auto"` (default)

```xml
<operation name="detect_language">
  <action>
    1. Check for pyproject.toml, setup.py, requirements.txt in target_path -> Python
    2. Check for package.json, tsconfig.json in target_path -> TypeScript
    3. If both detected, ask human to specify
    4. If neither detected, report error
  </action>
  <constraints>
    - BLOCKING: Must resolve to exactly one language before proceeding
  </constraints>
  <output>language: "python" | "typescript"</output>
</operation>
```

### Operation: Create Directory Structure

**When:** Language is determined

```xml
<operation name="create_directory_structure">
  <action>
    1. Create {target_path}/tracing/ directory
    2. For Python: create __init__.py, decorator.py, context.py, buffer.py, writer.py, redactor.py
    3. For TypeScript: create index.ts, decorator.ts, context.ts, buffer.ts, writer.ts, redactor.ts
  </action>
  <constraints>
    - BLOCKING: Do not overwrite existing tracing directory without confirmation
  </constraints>
  <output>List of created file paths</output>
</operation>
```

### Operation: Generate Core Files

**When:** Directory structure is created

```xml
<operation name="generate_core_files">
  <action>
    1. Generate decorator file with sync/async support and redaction integration
    2. Generate context file with thread-local (Python) or AsyncLocalStorage (TypeScript)
    3. Generate buffer file for in-memory trace accumulation
    4. Generate writer file for log output to log_path
    5. Generate redactor file with default sensitive patterns (see Sensitive Data Patterns below)
    6. Generate exports file (__init__.py or index.ts) exposing public API
  </action>
  <constraints>
    - CRITICAL: Use X-IPE reference implementation as basis (src/x_ipe/tracing/)
    - CRITICAL: Redactor must cover: passwords, secrets, tokens, keys, auth, financial data
  </constraints>
  <output>Generated source files with decorator, context, buffer, writer, redactor, and exports</output>
</operation>
```

### Operation: Create Configuration

**When:** Core files are generated

```xml
<operation name="create_configuration">
  <action>
    1. For Python: add [tool.tracing] section to pyproject.toml with enabled, log_path, retention_hours
    2. For TypeScript: add "tracing" section to package.json with enabled, logPath, retentionHours
    3. Apply provided log_path and retention_hours values (or defaults)
  </action>
  <output>Updated configuration file path</output>
</operation>
```

### Operation: Report Results

**When:** All files are generated and configuration is set

```xml
<operation name="report_results">
  <action>
    1. List all generated files with their purpose
    2. Show configuration summary (log path, retention, sensitive patterns)
    3. Provide usage example with decorator applied to a sample function
    4. Suggest next steps: instrument routes, configure retention, view dashboard
  </action>
  <output>Formatted summary report for human</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    language: "python | typescript"
    files_created:
      - "{target_path}/tracing/decorator.py"
      - "{target_path}/tracing/context.py"
      - "{target_path}/tracing/buffer.py"
      - "{target_path}/tracing/writer.py"
      - "{target_path}/tracing/redactor.py"
      - "{target_path}/tracing/__init__.py"
    config_file: "pyproject.toml | package.json"
    log_path: "instance/traces/"
    retention_hours: 24
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Language resolved</name>
    <verification>Language is detected or explicitly specified</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Directory structure created</name>
    <verification>tracing/ directory exists with all required files</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Decorator generated</name>
    <verification>decorator.py/ts exists with sync and async support</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Support modules generated</name>
    <verification>context, buffer, writer, redactor files all exist</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Configuration added</name>
    <verification>Project config contains tracing settings</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Usage instructions provided</name>
    <verification>Report includes usage example and next steps</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `LANGUAGE_NOT_DETECTED` | No language markers found in target_path | Ask human to specify `language` parameter |
| `AMBIGUOUS_LANGUAGE` | Both Python and TypeScript markers found | Ask human to choose one |
| `TARGET_PATH_NOT_FOUND` | target_path does not exist | Verify path and retry |
| `TRACING_DIR_EXISTS` | tracing/ directory already exists | Ask human to confirm overwrite |

---

## Templates

### Sensitive Data Patterns

The generated redactor includes these default patterns:

| Category | Patterns |
|----------|----------|
| Passwords | password, pwd, passwd, pass |
| Secrets | secret, secret_key, secretkey |
| Tokens | token, auth_token, api_token, access_token |
| Keys | key, api_key, apikey, private_key |
| Auth | auth, authorization, credential |
| Financial | card_number, cvv, ssn |

### Reference Implementation

Adapt from X-IPE's own tracing modules:
- `src/x_ipe/tracing/decorator.py`
- `src/x_ipe/tracing/context.py`
- `src/x_ipe/tracing/buffer.py`
- `src/x_ipe/tracing/writer.py`
- `src/x_ipe/tracing/redactor.py`

---

## Examples

See [references/examples.md](references/examples.md) for detailed examples.
