---
name: x-ipe-tool-implementation-typescript
description: TypeScript-specific implementation tool skill. Handles TypeScript, React, Vue, Angular, Next.js, Express, Fastify, and NestJS projects with built-in best practices (strict mode, interface-first, null safety, vitest/jest). No research step needed — practices are baked in. Called by x-ipe-task-based-code-implementation orchestrator. Triggers on TypeScript tech_stack entries.
---

# TypeScript Implementation Tool Skill

## Purpose

AI Agents follow this skill to implement TypeScript code by:
1. Learning existing code structure, tsconfig settings, and detecting framework
2. Implementing with built-in TypeScript best practices (strict mode, interface-first, null safety)
3. Writing vitest/jest tests mapped to AAA scenario Assert clauses
4. Running tests and linting (ESLint + @typescript-eslint + Prettier)

---

## Important Notes

BLOCKING: This skill is invoked by the `x-ipe-task-based-code-implementation` orchestrator. Do NOT invoke directly unless testing.

CRITICAL: No research step is needed — TypeScript best practices are built into this skill. Skip identification/research and go straight to learning existing code.

MANDATORY: Follow the standard tool skill I/O contract defined in [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md).

---

## About

The TypeScript Implementation Tool Skill handles all TypeScript-related tech_stack entries routed by the orchestrator. Unlike the general fallback skill, this skill has **built-in best practices** — no research step is needed, making it faster and more reliable.

**Key Concepts:**
- **Built-In Practices** — strict mode, interface-first design, null safety, proper imports are hardcoded, not discovered
- **AAA Contract** — Receives AAA scenarios and returns standard tool skill output (implementation_files, test_files, test_results, lint_status)
- **Framework Detection** — Identifies React, Vue, Angular, Next.js, Express, Fastify, NestJS, or plain Node.js from project files

---

## When to Use

```yaml
triggers:
  - "tech_stack contains TypeScript, React, Vue, Angular"
  - "tech_stack contains Next.js, Express, Fastify, NestJS"
  - "Orchestrator routes TypeScript-related entry to this skill"

not_for:
  - "x-ipe-tool-implementation-python: for Python/Flask/FastAPI/Django"
  - "x-ipe-tool-implementation-html5: for HTML/CSS/vanilla JavaScript"
  - "x-ipe-tool-implementation-java: for Java/Spring Boot"
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

- AAA scenarios array is non-empty
- source_code_path directory exists or can be created
- feature_id and technical_design_link are provided

---

## Operations

### Operation: implement

**When:** Orchestrator routes a TypeScript tech_stack entry to this skill

```xml
<operation name="implement">
  <action>
    1. LEARN existing code:
       a. Read existing files in source_code_path
       b. Read tsconfig.json — note strict, paths, baseUrl, jsx, moduleResolution
       c. Detect framework:
          - package.json: react/react-dom → React; +next → Next.js
          - package.json: vue → Vue; @angular/core → Angular
          - package.json: express → Express; fastify → Fastify; @nestjs/core → NestJS
          - File patterns: .tsx → React, .vue → Vue, @Component → Angular
          - Default: plain TypeScript / Node.js
       d. Follow existing conventions (naming, barrel files, module structure)

    2. IMPLEMENT with built-in TypeScript best practices:
       a. Follow technical design Part 2 exactly
       b. strict: true — no implicit any, strict null checks, strict property init
       c. Interface-first design:
          - Define interfaces/types BEFORE implementation
          - Named exports preferred (avoid default exports unless framework requires)
          - Barrel files (index.ts) for module re-exports
       d. Null safety:
          - Optional chaining (?.) and nullish coalescing (??)
          - Discriminated unions for complex state
          - No non-null assertions (!) unless justified with comment
       e. Generics where appropriate (utility functions, API responses)
       f. Custom Error classes extending Error for domain errors
       g. Import patterns:
          - Type-only imports: import type { X } from '...'
          - Order: third-party → aliased local → relative (blank line between)
          - Respect tsconfig paths aliases
       h. Framework-specific patterns:
          - React: FC/hooks, Props interface, JSX.Element return types
          - Vue: defineComponent/script setup, typed props/emits, Composition API
          - Angular: typed decorators, injectable services, RxJS observables
          - Express/Fastify: typed Request/Response, middleware interfaces
          - NestJS: decorators, DTOs with class-validator, typed providers
          - Next.js: GetServerSideProps/GetStaticProps types, App Router conventions
       i. Follow KISS/YAGNI — implement only what design specifies

    3. WRITE vitest/jest tests mapped to AAA scenarios:
       a. FOR EACH AAA scenario:
          - Create: test('{scenario_name_kebab_or_descriptive}', () => {})
          - Arrange → typed fixtures, mocks (vi.fn() or jest.fn()), test data
          - Act → typed function call, API request, component render
          - Assert → one typed assertion per Assert clause
       b. Framework test patterns:
          - React: @testing-library/react (render, screen, userEvent)
          - Vue: @vue/test-utils (mount, wrapper)
          - Angular: TestBed, ComponentFixture
          - Express/Fastify: supertest with typed responses
          - NestJS: @nestjs/testing TestingModule
       c. Use describe() blocks to group related scenarios

    4. RUN tests:
       a. Execute: npx vitest run --reporter=verbose (preferred)
       b. Fallback: npx jest --verbose
       c. Record pass/fail for each Assert clause

    5. RUN linting:
       a. Execute: npx eslint {source_code_path} --fix
       b. Execute: npx prettier {source_code_path} --write
       c. If ESLint unavailable: npx tsc --noEmit for type-check only
       d. Re-run tests after any lint-induced changes

    6. RETURN standard output
  </action>
  <constraints>
    - CRITICAL: No research step — TypeScript best practices are built into Step 2
    - CRITICAL: Follow existing code conventions found in Step 1
    - MANDATORY: Every AAA Assert clause must map to exactly one test assertion
    - MANDATORY: Read tsconfig.json before implementing — respect paths, strict, jsx settings
  </constraints>
  <output>Standard tool skill output (implementation_files, test_files, test_results, lint_status)</output>
</operation>

<operation name="fix">
  <action>
    1. LEARN existing code: scan source_code_path for conventions, TypeScript config, patterns
    2. IF feature_context is absent: generate synthetic context (feature_id: "BUG-{task_id}", technical_design_link: "N/A")
    3. WRITE failing test from AAA scenario:
       a. FOR EACH AAA scenario:
          - Create test: test('fix: {scenario_name}', () => { ... })
          - Arrange → reproduce bug preconditions
          - Act → trigger the buggy action
          - Assert → expected CORRECT behavior (one expect() per Assert clause)
    4. RUN test: npx vitest run {test_file} → MUST FAIL (TDD gate)
       - IF test passes → STOP, report: "TDD gate violation — test already passes, review scenario"
    5. IMPLEMENT minimal fix following TypeScript best practices:
       - Strict types, ESLint compliance, existing conventions
       - Only change what is necessary to make the test pass
    6. RUN test → MUST PASS
    7. RUN all existing tests → no regressions
    8. RUN linting: npx eslint {source_code_path}
    9. RETURN standard output
  </action>
  <constraints>
    - BLOCKING: Test MUST fail before fix (Step 4) — TDD gate
    - CRITICAL: Minimal fix only — do not refactor during a fix
    - CRITICAL: No research step — TypeScript best practices are built into Step 5
    - MANDATORY: Feature_context is OPTIONAL — use synthetic fallback if absent
    - MANDATORY: Support both .ts and .tsx files
  </constraints>
  <output>Standard tool skill output (implementation_files, test_files, test_results, lint_status)</output>
</operation>

<operation name="refactor">
  <action>
    1. LEARN existing code: scan source_code_path for conventions, TypeScript config, patterns
    2. IF feature_context is absent: generate synthetic context (feature_id: "REFACTOR-{task_id}", technical_design_link: "N/A")
    3. RUN existing tests: npx vitest run → establish baseline (all must pass)
       - IF any test fails → STOP, report: "Cannot refactor — baseline tests failing"
    4. RESTRUCTURE code per AAA scenario target state:
       a. FOR EACH AAA scenario:
          - Read target state from Assert clauses
          - Apply structural changes following TypeScript best practices (strict types, ESLint)
          - Preserve external behavior
    5. UPDATE imports and references across affected files
    6. RUN all tests → MUST pass (behavior preserved)
       - IF tests fail → report failed scenarios with details; do NOT auto-revert
    7. RUN linting: npx eslint {source_code_path}
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
    lint_status: "pass | fail"
    lint_details: "{details if fail}"
    stack_identified: "TypeScript/{framework}"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Framework detected</name>
    <verification>stack_identified contains "TypeScript/{framework}" in output</verification>
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
| `TSCONFIG_MISSING` | No tsconfig.json found in project | Log warning, proceed with recommended defaults (strict: true, esModuleInterop: true); suggest creating tsconfig.json |
| `TYPE_ERROR_UNRESOLVABLE` | TypeScript compilation error that cannot be auto-fixed | Return detailed error in test_results; orchestrator handles retry or escalation |
| `FRAMEWORK_DETECTION_AMBIGUOUS` | Multiple frameworks detected (e.g., React + Vue deps) | Use file extension heuristic (.tsx → React, .vue → Vue); log warning with detected candidates |
| `DEPENDENCY_MISSING` | Required package not installed (e.g., vitest, @types/*) | Run `npm install {package}` or suggest adding to devDependencies, then retry |
| `LINT_UNAVAILABLE` | Neither ESLint nor tsc available | Log warning, return lint_status: "skipped", continue |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-implementation-typescript/references/examples.md) for usage examples.
