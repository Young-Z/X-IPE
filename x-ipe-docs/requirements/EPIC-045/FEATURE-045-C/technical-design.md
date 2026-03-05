# Technical Design: HTML5 Implementation Tool Skill

> Feature ID: FEATURE-045-C  
> Epic ID: EPIC-045  
> Version: v1.0  
> Status: Designed  
> Last Updated: 03-05-2026  
> program_type: skills  
> tech_stack: ["Markdown/SKILL.md"]

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-05-2026 | Initial design |

---

## Part 1: Agent-Facing Summary

### Key Components

| Component | Path | Purpose |
|-----------|------|---------|
| SKILL.md | `.github/skills/x-ipe-tool-implementation-html5/SKILL.md` | Main skill definition — operations, I/O contract, HTML5-specific steps |
| examples.md | `.github/skills/x-ipe-tool-implementation-html5/references/examples.md` | 3 usage examples (landing page, interactive component, CSS animation) |

### Dependencies

| Dependency | Type | Path |
|------------|------|------|
| Orchestrator | Caller | `.github/skills/x-ipe-task-based-code-implementation/SKILL.md` |
| I/O Contract | Reference | `.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md` |
| General Fallback | Sibling template | `.github/skills/x-ipe-tool-implementation-general/SKILL.md` |

### How the Orchestrator Invokes This Skill

```
Orchestrator Step 4 (Route tool skills):
  FOR EACH tech_stack entry:
    AI semantic match against x-ipe-tool-implementation-* descriptions
    → tech_stack "HTML5/CSS3" matches x-ipe-tool-implementation-html5
    → Orchestrator passes filtered AAA scenarios to this skill
```

### Key Differentiator from General Fallback

| Aspect | General Fallback | HTML5 Skill |
|--------|-----------------|-------------|
| Research step | Required (Step 2) | **Skipped** — practices built-in |
| Best practices | Discovered at runtime | **Hardcoded** (semantic HTML, a11y, responsive) |
| Test framework | Discovered | **Always vitest/jest** |
| Linting tool | Discovered | **Always ESLint + Prettier** |
| Operation steps | 8 steps | **6 steps** (no identify/research) |

---

## Part 2: Implementation Guide

### Skill Structure

```
.github/skills/x-ipe-tool-implementation-html5/
├── SKILL.md                    # Main skill (≤250 lines)
└── references/
    └── examples.md             # 3 examples (landing page, component, animation)
```

### SKILL.md Sections

1. **Frontmatter** — `name: x-ipe-tool-implementation-html5`, description mentions HTML5/CSS3/JavaScript/accessibility/responsive
2. **Purpose** — 6-step process (no research step)
3. **Important Notes** — Same blocking/critical/mandatory notes as general
4. **About** — Key concepts: Built-In Practices, AAA Contract, Framework Detection
5. **When to Use** — Triggers on HTML/CSS/JS tech_stack entries; `not_for` lists other skills
6. **Input Parameters** — Identical to general fallback (standard contract)
7. **Definition of Ready** — Same 3 checkpoints as general
8. **Operations** — 6-step implement operation (see below)
9. **Output Result** — Standard contract + `stack_identified: "HTML5/{framework}"`
10. **Definition of Done** — 5 checkpoints (no "research completed" checkpoint)
11. **Error Handling** — HTML5-specific errors
12. **Examples link** — Points to `references/examples.md`

### Operation Steps (implement)

```
Step 1: LEARN existing code
  a. Read existing files in source_code_path
  b. Detect framework/approach:
     - package.json → check for alpinejs, htmx, lit, stencil
     - HTML files with x-data attributes → Alpine.js
     - HTML files with hx-* attributes → HTMX
     - JS files with customElements.define() → Web Components
     - Default: vanilla HTML5/CSS3/JS
  c. Detect CSS methodology:
     - BEM naming (block__element--modifier) → BEM
     - Utility classes (flex, mt-4, text-center) → Utility-first
     - CSS custom properties usage → Custom Properties
     - CSS modules (.module.css) → CSS Modules
     - Default: plain CSS3
  d. Follow existing conventions

Step 2: IMPLEMENT with built-in HTML5 best practices
  a. Follow technical design Part 2 exactly
  b. Semantic HTML5: header, nav, main, section, article, aside, footer
  c. Meta tags: charset UTF-8, viewport meta, lang attribute on <html>
  d. Accessibility:
     - ARIA roles and labels on interactive elements
     - Keyboard navigation (tabindex, focus management)
     - Alt text for all images, aria-label for icon buttons
     - Skip-to-content link for page layouts
  e. CSS3:
     - Mobile-first with min-width media queries
     - Relative units (rem, em, %) over fixed px
     - CSS custom properties for theming
     - Flexbox/Grid for layout
  f. ES6+ JavaScript:
     - const/let (no var), arrow functions, template literals
     - addEventListener over inline handlers
     - Modules (import/export) when project supports it
  g. Progressive enhancement: core content works without JS
  h. Follow KISS/YAGNI

Step 3: WRITE tests mapped to AAA scenarios
  a. FOR EACH AAA scenario:
     - Create: test('{scenario_name}', () => {})
     - Arrange → DOM setup (document.createElement or innerHTML)
     - Act → user interaction (click, input, keyboard event)
     - Assert → DOM assertions + accessibility checks
  b. Accessibility test patterns:
     - Check ARIA attributes: expect(el.getAttribute('role')).toBe(...)
     - Check keyboard access: simulate Tab/Enter/Escape events
     - Check focus management: expect(document.activeElement).toBe(...)
  c. Responsive viewport tests:
     - Set viewport width, verify layout changes
  d. Use describe() blocks to group related scenarios

Step 4: RUN tests
  a. Execute: npx vitest run --reporter=verbose (or npx jest --verbose)
  b. Record pass/fail for each Assert clause

Step 5: RUN linting
  a. Execute: npx eslint {source_code_path} --fix
  b. Execute: npx prettier {source_code_path} --write
  c. If ESLint unavailable: log warning, return lint_status: "skipped"
  d. Re-run tests after any lint fixes

Step 6: RETURN standard output
  - Populate implementation_files, test_files, test_results, lint_status
```

### Framework Detection Algorithm

```
FUNCTION detect_framework(source_code_path):
  1. READ package.json (if exists)
  2. SCAN dependencies:
     - "alpinejs" → return "Alpine.js"
     - "htmx.org" → return "HTMX"
     - "lit" → return "Lit"
     - "@stencil/core" → return "Stencil"
  3. SCAN HTML files:
     - x-data attributes → "Alpine.js"
     - hx-get/hx-post attributes → "HTMX"
  4. SCAN JS files:
     - customElements.define() → "Web Components"
     - class extends HTMLElement → "Web Components"
  5. DEFAULT → "Vanilla"
```

### CSS Methodology Detection Algorithm

```
FUNCTION detect_css_methodology(source_code_path):
  1. SCAN CSS files:
     - Pattern /__\w+--\w+/ → "BEM"
     - .module.css extensions → "CSS Modules"
     - Tailwind @apply directives → "Utility-first"
  2. SCAN for CSS custom properties:
     - :root { --var: value } → note "Custom Properties" in use
  3. DEFAULT → "Plain CSS3"
```

### Error Codes

| Error | Cause | Resolution |
|-------|-------|------------|
| `BROWSER_COMPAT_ISSUE` | Code uses API not widely supported | Log warning, suggest polyfill or fallback |
| `ACCESSIBILITY_VIOLATION` | Generated HTML fails accessibility checks | Fix ARIA/keyboard issues before returning |
| `NO_TEST_RUNNER` | Neither vitest nor jest found | Log warning, return test_results: empty, signal orchestrator |
| `LINT_UNAVAILABLE` | Neither ESLint nor Prettier found | Log warning, return lint_status: "skipped" |

### Design Change Log

| Date | Change | Reason |
|------|--------|--------|
| 03-05-2026 | Initial design | FEATURE-045-C creation |
