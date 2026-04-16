# Application RE — JavaScript Language Mixin

> Apply this mixin when the target codebase contains JavaScript source code.
> Merge these overlays into the base playbook when language: javascript.
> This is an additive overlay — it does NOT replace repo-type mixin content.

---

## Detection Signals

| Signal | File/Pattern | Confidence |
|--------|-------------|------------|
| JavaScript files | `*.js` or `*.jsx` files present | high |
| package.json | `package.json` at root | high |
| Node modules | `node_modules/` directory | medium |
| Webpack config | `webpack.config.*` | medium |
| Vite config | `vite.config.*` | medium |
| Babel config | `.babelrc`, `babel.config.*` | medium |
| ESLint config | `.eslintrc.*`, `eslint.config.*` | medium |

---

## Section Overlay Prompts

### For Section 1 (Architecture Recovery)
<!-- ADDITIONAL PROMPTS:
- Identify module system: CJS (require) vs. ESM (import)
- Check for "type": "module" in package.json
- Detect source directory patterns: src/, lib/, dist/, build/
- Note barrel files (index.js re-exporting from subdirectories)
-->

### For Section 2 (API Contract Extraction)
<!-- ADDITIONAL PROMPTS:
- Extract Express routes: app.get(), app.post(), router.use()
- Extract Fastify routes: fastify.get(), schema definitions
- Extract Koa routes: router.get(), router.post()
- Extract Next.js API routes: pages/api/*.js or app/api/*/route.js
- Check for JSDoc @param and @returns annotations
- Look for Joi/Zod/Yup validation schemas
-->

### For Section 3 (Business Logic Mapping)
<!-- ADDITIONAL PROMPTS:
- Detect module patterns: CommonJS (require/module.exports), ESM (import/export)
- Detect Revealing Module pattern: IIFE with returned public API
- Detect Observer pattern: EventEmitter, addEventListener, custom event buses
- Detect Middleware pattern: Express middleware chains, Koa middleware
- Detect React patterns: Higher-Order Components, Render Props, Custom Hooks, Context
- Detect callback patterns vs. Promise chains vs. async/await
- Detect Proxy/Reflect patterns
- Look for pub/sub implementations (EventEmitter, RxJS Observables)
-->

### For Section 5 (Dependency Analysis)
<!-- ADDITIONAL PROMPTS:
- Parse package.json dependencies and devDependencies
- Detect Node.js version from engines field or .nvmrc or .node-version
- Identify bundler: webpack, vite, esbuild, rollup, parcel
- Identify framework: Express, Fastify, Koa, Next.js, Nuxt, Nest
- Identify frontend framework: React, Vue, Svelte, Angular (if present)
- Detect transpilation: Babel config, SWC
-->

### For Section 7 (Security & Auth Patterns)
<!-- ADDITIONAL PROMPTS:
- Check for passport.js strategies (JWT, OAuth, local)
- Detect helmet.js middleware usage
- Check for express-rate-limit, cors middleware
- Identify cookie/session management (express-session, cookie-parser)
-->

### For Section 8 (Testing Strategy)
<!-- ADDITIONAL PROMPTS:
- Detect Jest: jest.config.*, describe/it/expect
- Detect Vitest: vitest.config.*, describe/it/expect
- Detect Mocha: .mocharc.*, describe/it with chai assertions
- Detect testing-library: @testing-library/*, render/screen/fireEvent
- Check for coverage config: jest --coverage, c8, nyc/istanbul
- Note E2E frameworks: Cypress, Playwright, Puppeteer
-->
