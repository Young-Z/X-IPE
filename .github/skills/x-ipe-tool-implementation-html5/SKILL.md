---
name: x-ipe-tool-implementation-html5
description: HTML5/CSS3/JavaScript-specific implementation tool skill. Handles semantic HTML5, CSS3, vanilla JS, web components, Alpine.js, and HTMX projects with built-in best practices (accessibility, responsive design, progressive enhancement). No research step needed — practices are baked in. Called by x-ipe-task-based-code-implementation orchestrator. Triggers on HTML/CSS/JS tech_stack entries.
---

# HTML5 Implementation Tool Skill

## Purpose

AI Agents follow this skill to implement HTML5/CSS3/JS code by:
1. Learning existing code structure and detecting framework/CSS methodology
2. Implementing with built-in web best practices (semantic HTML, accessibility, responsive)
3. Writing vitest/jest tests mapped to AAA scenario Assert clauses
4. Running tests and linting (ESLint + Prettier)

---

## Important Notes

BLOCKING: Invoked by `x-ipe-task-based-code-implementation` orchestrator. Do NOT invoke directly unless testing.
CRITICAL: No research step — HTML5/CSS3/JS best practices are built in. Go straight to learning existing code.
MANDATORY: Follow the standard tool skill I/O contract in [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md).

---

## About

**Key Concepts:**
- **Built-In Practices** — Semantic HTML5, ARIA accessibility, responsive design, progressive enhancement are hardcoded
- **AAA Contract** — Receives AAA scenarios and returns standard output (implementation_files, test_files, test_results, lint_status)
- **Framework Detection** — Identifies vanilla JS, web components, Alpine.js, HTMX, or Lit from project files
- **CSS Methodology Detection** — Identifies BEM, utility-first, CSS modules, or plain CSS from existing stylesheets

---

## When to Use

```yaml
triggers:
  - "tech_stack contains HTML5, CSS3, JavaScript, HTML/CSS/JS"
  - "tech_stack contains web components, Alpine.js, HTMX, Lit"
  - "Orchestrator routes HTML/CSS/JS-related entry to this skill"

not_for:
  - "x-ipe-tool-implementation-python: for Python/Flask/FastAPI/Django"
  - "x-ipe-tool-implementation-typescript: for TypeScript/React/Vue/Angular"
  - "x-ipe-tool-implementation-java: for Java/Spring Boot"
  - "x-ipe-tool-implementation-mcp: for MCP servers"
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
  feature_context:  # OPTIONAL for "fix"/"refactor"; REQUIRED for "implement"
    feature_id: "{FEATURE-XXX-X}"
    feature_title: "{title}"
    technical_design_link: "{path to technical-design.md}"
    specification_link: "{path to specification.md}"
    mockup_link: "{path | N/A}"  # From orchestrator; visual reference for frontend fidelity
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="'implement' | 'fix' | 'refactor' — set by calling orchestrator" />
  <field name="aaa_scenarios" source="Filtered scenarios from orchestrator Step 5" />
  <field name="source_code_path" source="From technical design Part 2" />
  <field name="test_code_path" source="From technical design Part 2 or project convention" />
  <field name="feature_context" source="From orchestrator's Feature Data Model. OPTIONAL for fix/refactor — use synthetic fallback if absent" />
  <field name="feature_context.mockup_link" source="From orchestrator (code-implementation Step 3.1). N/A if no current mockup." />
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

**When:** Orchestrator routes an HTML/CSS/JS tech_stack entry to this skill

```xml
<operation name="implement">
  <action>
    1. LEARN existing code:
       a. Read existing files in source_code_path
       b. Detect framework:
          - Check package.json for alpinejs/htmx.org/lit/@stencil/core
          - Check HTML for x-data attributes (Alpine.js) or hx-* attributes (HTMX)
          - Check JS for customElements.define() or class extends HTMLElement (Web Components)
          - Default: vanilla HTML5/CSS3/JS
       c. Detect CSS methodology:
          - BEM naming (block__element--modifier)
          - Utility-first classes (Tailwind-style)
          - CSS modules (.module.css)
          - Default: plain CSS3 with custom properties
       d. Follow existing conventions (naming, file structure, class naming)

    2. REFERENCE MOCKUP (if available):
       a. IF feature_context.mockup_link != "N/A":
          - READ mockup file at mockup_link
          - EXTRACT visual spec: layout structure, component hierarchy, spacing, colors, states
          - USE as visual fidelity guide for steps below (layout, styling, responsive breakpoints)
       b. ELSE: proceed with technical design only

    3. IMPLEMENT with built-in HTML5/CSS3/JS best practices:
       a. Follow technical design Part 2 exactly; IF mockup available, match its layout/styling
       b. Semantic HTML5: header, nav, main, section, article, aside, footer
       c. Required meta: &lt;meta charset="UTF-8"&gt;, viewport meta, lang attribute on &lt;html&gt;
       d. Accessibility (MANDATORY on all output):
          - ARIA roles and aria-label on interactive elements
          - Keyboard navigation: tabindex, keydown/keyup handlers for Enter/Escape/Arrow keys
          - Focus management: programmatic focus on modal open/close, skip-to-content links
          - Alt text for images, aria-label for icon-only buttons
       e. CSS3 responsive design:
          - Mobile-first with min-width media queries
          - Relative units (rem, em, %) — avoid fixed px for layout
          - CSS custom properties for theming (--color-primary, --spacing-*)
          - Flexbox/Grid for layout — no floats for structural layout
       f. ES6+ JavaScript:
          - const/let (never var), arrow functions, template literals
          - addEventListener (no inline onclick handlers)
          - ES modules (import/export) when project supports it
          - Async/await for fetch calls
       g. Progressive enhancement: core content readable without JavaScript
       h. Follow KISS/YAGNI — implement only what design specifies

    4. WRITE tests mapped to AAA scenarios:
       a. FOR EACH AAA scenario:
          - Create: test('{scenario_name_kebab_or_description}', () => {})
          - Arrange → DOM setup (document.createElement, innerHTML, or JSDOM fixture)
          - Act → user interaction (click, input events, keyboard events, dispatchEvent)
          - Assert → one assertion per Assert clause
       b. Accessibility test patterns:
          - Verify ARIA: expect(el.getAttribute('role')).toBe('dialog')
          - Verify keyboard: simulate Tab/Enter/Escape → check focus/state
          - Verify focus: expect(document.activeElement).toBe(expectedEl)
       c. Responsive test patterns:
          - Mock viewport width → verify CSS class or layout behavior
       d. Use describe() blocks to group related scenarios

    5. RUN tests:
       a. Execute: npx vitest run --reporter=verbose (or npx jest --verbose)
       b. Record pass/fail for each Assert clause

    6. RUN linting:
       a. Execute: npx eslint {source_code_path} --fix
       b. Execute: npx prettier {source_code_path} --write
       c. If ESLint/Prettier unavailable: log warning, return lint_status: "skipped"
       d. Re-run tests after any lint-induced changes

    7. RETURN standard output
  </action>
  <constraints>
    - CRITICAL: No research step — HTML5/CSS3/JS best practices are built into Step 3
    - CRITICAL: Follow existing code conventions found in Step 1
    - CRITICAL: IF mockup_link provided, implementation MUST match mockup layout/styling
    - MANDATORY: Every AAA Assert clause must map to exactly one test assertion
    - MANDATORY: All interactive elements must have ARIA labels and keyboard support
  </constraints>
  <output>Standard tool skill output (implementation_files, test_files, test_results, lint_status)</output>
</operation>

<operation name="fix">
  <action>
    1. LEARN existing code: scan source_code_path for HTML structure, CSS patterns, JS conventions
    2. IF feature_context is absent: generate synthetic context (feature_id: "BUG-{task_id}", technical_design_link: "N/A")
    3. WRITE failing test from AAA scenario:
       a. FOR EACH AAA scenario:
          - Create DOM assertion test for the bug
          - Arrange → set up DOM state reproducing the bug
          - Act → trigger the buggy interaction
          - Assert → expected CORRECT DOM/CSS/JS behavior
    4. RUN test → MUST FAIL (TDD gate)
       - IF test passes → STOP, report: "TDD gate violation — test already passes, review scenario"
    5. IMPLEMENT minimal fix following HTML5/CSS/JS best practices:
       - Semantic HTML, accessible markup, valid CSS
       - Only change what is necessary to make the test pass
    6. RUN test → MUST PASS
    7. RUN all existing tests → no regressions
    8. RUN validation: HTML validation, CSS validation
    9. RETURN standard output
  </action>
  <constraints>
    - BLOCKING: Test MUST fail before fix (Step 4) — TDD gate
    - CRITICAL: Minimal fix only — do not refactor during a fix
    - MANDATORY: Feature_context is OPTIONAL — use synthetic fallback if absent
    - MANDATORY: Validate HTML5 semantics and accessibility
  </constraints>
  <output>Standard tool skill output (implementation_files, test_files, test_results, lint_status)</output>
</operation>

<operation name="refactor">
  <action>
    1. LEARN existing code: scan source_code_path for HTML structure, CSS patterns, JS conventions
    2. IF feature_context is absent: generate synthetic context (feature_id: "REFACTOR-{task_id}", technical_design_link: "N/A")
    3. RUN existing tests → establish baseline (all must pass)
       - IF any test fails → STOP, report: "Cannot refactor — baseline tests failing"
    4. RESTRUCTURE code per AAA scenario target state:
       a. FOR EACH AAA scenario:
          - Read target state from Assert clauses
          - Apply structural changes (semantic HTML, CSS reorganization, JS patterns)
          - Preserve external behavior and visual appearance
    5. UPDATE references across affected HTML/CSS/JS files
    6. RUN all tests → MUST pass (behavior preserved)
       - IF tests fail → report failed scenarios with details; do NOT auto-revert
    7. RUN validation: HTML validation, CSS validation
    8. RETURN standard output
  </action>
  <constraints>
    - BLOCKING: Baseline tests must pass before refactoring (Step 3)
    - CRITICAL: Preserve behavior and visual appearance — no functional changes
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
    stack_identified: "HTML5/{framework}"
  errors: []
```

---

## Definition of Done

- ✅ **Framework detected** — stack_identified contains "HTML5/{framework}"
- ✅ **Implementation files created** — implementation_files array is non-empty
- ✅ **Test files created** — test_files array is non-empty
- ✅ **All AAA Assert clauses mapped** — test_results count equals total Assert clauses
- ✅ **Lint passes** — lint_status == "pass" or "skipped"

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `BROWSER_COMPAT_ISSUE` | API not widely supported | Log warning, suggest polyfill, continue |
| `ACCESSIBILITY_VIOLATION` | Missing ARIA/keyboard support | Fix before returning; re-run checks |
| `NO_TEST_RUNNER` | Neither vitest nor jest found | Log warning, empty test_results; signal orchestrator |
| `LINT_UNAVAILABLE` | ESLint/Prettier not found | Log warning, lint_status: "skipped" |
| `CSS_METHODOLOGY_CONFLICT` | Mixed CSS methodologies | Follow dominant methodology; log warning |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-tool-implementation-html5/references/examples.md) for usage examples.
