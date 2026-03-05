# Technical Design: TypeScript Implementation Tool Skill

> Feature ID: FEATURE-045-D  
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
| SKILL.md | `.github/skills/x-ipe-tool-implementation-typescript/SKILL.md` | Main skill definition — operations, I/O contract, TypeScript-specific steps |
| examples.md | `.github/skills/x-ipe-tool-implementation-typescript/references/examples.md` | 3 usage examples (React component, Express API, Vue SFC) |

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
    → tech_stack "TypeScript/React" matches x-ipe-tool-implementation-typescript
    → Orchestrator passes filtered AAA scenarios to this skill
```

### Key Differentiator from General Fallback

| Aspect | General Fallback | TypeScript Skill |
|--------|-----------------|------------------|
| Research step | Required (Step 2) | **Skipped** — practices built-in |
| Best practices | Discovered at runtime | **Hardcoded** (strict mode, interfaces, null safety) |
| Test framework | Discovered | **Always vitest (preferred) or jest** |
| Linting tool | Discovered | **Always ESLint + @typescript-eslint + Prettier** |
| Operation steps | 8 steps | **6 steps** (no identify/research) |
| Type system | N/A | **Interface-first, generics, no `any`** |

---

## Part 2: Implementation Guide

### Skill Structure

```
.github/skills/x-ipe-tool-implementation-typescript/
├── SKILL.md                    # Main skill (≤250 lines)
└── references/
    └── examples.md             # 3 examples (React, Express, Vue)
```

### SKILL.md Sections

1. **Frontmatter** — `name: x-ipe-tool-implementation-typescript`, description mentions TypeScript/React/Vue/Angular/Node.js
2. **Purpose** — 6-step process (no research step)
3. **Important Notes** — Same blocking/critical/mandatory notes as general
4. **About** — Key concepts: Built-In Practices, AAA Contract, Framework Detection
5. **When to Use** — Triggers on TypeScript tech_stack entries; `not_for` lists other skills
6. **Input Parameters** — Identical to general fallback (standard contract)
7. **Definition of Ready** — Same 3 checkpoints as general
8. **Operations** — 6-step implement operation (see below)
9. **Output Result** — Standard contract + `stack_identified: "TypeScript/{framework}"`
10. **Definition of Done** — 5 checkpoints (no "research completed" checkpoint)
11. **Error Handling** — TypeScript-specific errors
12. **Examples link** — Points to `references/examples.md`

### Operation Steps (implement)

```
Step 1: LEARN existing code
  a. Read existing files in source_code_path
  b. Read tsconfig.json — note strict settings, paths, module resolution, jsx config
  c. Detect framework:
     - package.json → check for react, vue, @angular/core, next, express, fastify, @nestjs/core
     - .tsx files → React or Next.js
     - .vue files → Vue
     - Angular decorators (@Component, @Injectable) → Angular
     - Express/Fastify/NestJS patterns in src/ → Node.js backend
     - Default: plain TypeScript / Node.js
  d. Follow existing conventions (naming, module structure, barrel files)

Step 2: IMPLEMENT with built-in TypeScript best practices
  a. Follow technical design Part 2 exactly
  b. strict: true enforcement — no implicit any, strict null checks
  c. Interface-first design:
     - Define interfaces/types BEFORE implementation
     - Use named exports (avoid default exports unless framework requires it)
     - Barrel files (index.ts) for module re-exports
  d. Null safety:
     - Optional chaining (?.) and nullish coalescing (??)
     - Discriminated unions for complex state
     - No non-null assertions (!) unless justified with comment
  e. Generics where appropriate (utility functions, data structures, API responses)
  f. Custom Error classes extending Error for domain errors
  g. Proper import/export patterns:
     - Named exports preferred
     - Type-only imports: import type { X } from '...'
     - Avoid circular dependencies
  h. Apply framework-specific patterns:
     - React: FC/hooks, Props interfaces, JSX.Element returns
     - Vue: defineComponent/script setup, typed props/emits, Composition API
     - Angular: typed decorators, injectable services, RxJS observables
     - Express/Fastify: typed Request/Response, middleware interfaces
     - NestJS: decorators, DTOs with class-validator, typed providers
     - Next.js: GetServerSideProps/GetStaticProps types, App Router conventions
  i. Follow KISS/YAGNI

Step 3: WRITE tests mapped to AAA scenarios
  a. FOR EACH AAA scenario:
     - Create: test('{scenario_name}', () => {}) or it('{scenario_name}', () => {})
     - Arrange → typed fixtures, mocks (vi.fn() or jest.fn()), test data
     - Act → typed function call, API request, component render
     - Assert → one typed assertion per Assert clause
  b. Framework test patterns:
     - React: @testing-library/react (render, screen, userEvent)
     - Vue: @vue/test-utils (mount, wrapper.find)
     - Angular: TestBed, ComponentFixture
     - Express/Fastify: supertest with typed responses
     - NestJS: @nestjs/testing TestingModule
  c. Use describe() blocks to group scenarios

Step 4: RUN tests
  a. Execute: npx vitest run --reporter=verbose (preferred)
  b. Fallback: npx jest --verbose
  c. Record pass/fail for each Assert clause

Step 5: RUN linting
  a. Execute: npx eslint {source_code_path} --fix
  b. Execute: npx prettier {source_code_path} --write
  c. If ESLint unavailable: run npx tsc --noEmit for type checking only
  d. Re-run tests after any lint fixes

Step 6: RETURN standard output
```

### Framework Detection Algorithm

```
FUNCTION detect_framework(source_code_path):
  1. READ tsconfig.json — note jsx, experimentalDecorators, paths
  2. READ package.json dependencies:
     - "react" or "react-dom" → if "next" also present → "Next.js" else "React"
     - "vue" → "Vue"
     - "@angular/core" → "Angular"
     - "express" → "Express"
     - "fastify" → "Fastify"
     - "@nestjs/core" → "NestJS"
  3. SCAN file patterns:
     - *.tsx → React (confirm with imports)
     - *.vue → Vue
     - @Component decorator → Angular
  4. DEFAULT → "Node.js"
```

### tsconfig Awareness

```
FUNCTION read_tsconfig(source_code_path):
  1. FIND tsconfig.json (check source_code_path, then project root)
  2. NOTE key settings:
     - strict → if false, warn but proceed; recommend enabling
     - paths → use for module resolution in imports
     - baseUrl → use for non-relative imports
     - jsx → "react-jsx" or "react" confirms React
     - experimentalDecorators → Angular or NestJS
     - moduleResolution → "node" or "bundler"
  3. IF tsconfig.json missing:
     - Log TSCONFIG_MISSING warning
     - Proceed with recommended defaults (strict: true, esModuleInterop: true)
```

### Module Resolution

```
FUNCTION resolve_imports(source_code_path, tsconfig):
  1. IF tsconfig.paths defined → use path aliases (@/components → src/components)
  2. IF barrel files exist (index.ts) → import from directory, not individual files
  3. USE type-only imports for interfaces: import type { User } from './types'
  4. ORDER: third-party → aliased local → relative local (blank line between groups)
```
