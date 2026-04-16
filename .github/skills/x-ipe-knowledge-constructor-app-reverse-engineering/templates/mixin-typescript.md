# Application RE — TypeScript Language Mixin

> Apply this mixin when the target codebase contains TypeScript source code.
> Merge these overlays into the base playbook when language: typescript.
> This is an additive overlay — it does NOT replace repo-type mixin content.

---

## Detection Signals

| Signal | File/Pattern | Confidence |
|--------|-------------|------------|
| TypeScript files | `*.ts` or `*.tsx` files present | high |
| tsconfig.json | `tsconfig.json` at root or in directories | high |
| TypeScript dependency | `"typescript"` in package.json devDependencies | high |
| Declaration files | `*.d.ts` files | medium |
| Path aliases | `"paths"` in tsconfig.json | medium |

---

## Section Overlay Prompts

### For Section 1 (Architecture Recovery)
<!-- ADDITIONAL PROMPTS:
- Analyze tsconfig.json path aliases for module organization
- Check for project references (composite tsconfig)
- Identify declaration files (.d.ts) for type-only modules
- Note strict mode settings and their implications
- Identify barrel exports (index.ts re-exports)
-->

### For Section 2 (API Contract Extraction)
<!-- ADDITIONAL PROMPTS:
- Extract type exports: exported interfaces, types, and type aliases
- Document generic type parameters and constraints
- Extract Nest.js endpoints: @Get(), @Post(), @Body(), @Param()
- Check for tRPC router definitions
- Parse Zod schemas used for runtime validation
- Extract branded/nominal types used as API contracts
-->

### For Section 3 (Business Logic Mapping)
<!-- ADDITIONAL PROMPTS:
- Detect type-level patterns:
  Discriminated Unions: type Action = { type: "A" } | { type: "B" }
  Generic constraints: <T extends Base>
  Mapped types: { [K in keyof T]: ... }
  Conditional types: T extends U ? X : Y
- Detect decorator patterns: @Injectable, @Controller (if experimentalDecorators)
- Detect interface-driven design: interfaces as contracts between modules
- Detect type guard patterns: function isX(val): val is X
- Look for Nest.js patterns: @Module, @Injectable, @Controller, Providers
- Check reflect-metadata usage for runtime type information
-->

### For Section 5 (Dependency Analysis)
<!-- ADDITIONAL PROMPTS:
- Parse tsconfig.json target and module settings
- Detect TypeScript version from package.json
- Identify strict mode configuration
- Check for tsx/ts-node for development runtime
- Detect type checking tools: tsc, @typescript-eslint
-->

### For Section 7 (Security & Auth Patterns)
<!-- ADDITIONAL PROMPTS:
- Check for Nest.js guards and interceptors (@UseGuards, AuthGuard)
- Detect type-safe auth middleware patterns
- Look for branded types used for auth tokens
- Check for class-validator decorators on auth DTOs
-->

### For Section 8 (Testing Strategy)
<!-- ADDITIONAL PROMPTS:
- Check for TypeScript test configuration: ts-jest, vitest with TypeScript
- Note type-level testing: expect-type, tsd
- Identify test utility types (test helpers with generic signatures)
- Check tsconfig for test-specific overrides (tsconfig.test.json)
-->
