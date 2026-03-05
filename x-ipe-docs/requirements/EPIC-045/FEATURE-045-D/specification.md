# Feature Specification: TypeScript Implementation Tool Skill

> Feature ID: FEATURE-045-D  
> Epic ID: EPIC-045  
> Version: v1.0  
> Status: Refined  
> Last Updated: 03-05-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-05-2026 | Initial specification |

## Linked Mockups

N/A — This feature creates an AI skill file (SKILL.md). No UI components.

## Overview

This feature creates `x-ipe-tool-implementation-typescript`, a language-specific tool skill that the `x-ipe-task-based-code-implementation` orchestrator routes to when `tech_stack` contains TypeScript entries. Unlike the general fallback skill, this skill has **built-in TypeScript best practices** — no research step is needed.

The skill accepts AAA scenarios from the orchestrator, implements TypeScript code with strict mode, interface-first design, and proper type safety built in, writes vitest/jest test functions mapped to AAA Assert clauses, runs tests and linting (ESLint + typescript-eslint + Prettier), and returns the standard tool skill output contract.

## User Stories

1. **As an AI agent**, I want a TypeScript-specific implementation skill with built-in best practices (strict mode, interface-first design, null safety), so that I can implement TS code faster without a research step.

2. **As an AI agent**, I want the skill to detect whether the project uses React, Vue, Angular, Next.js, Express, Fastify, or NestJS, so that framework-specific patterns are applied correctly.

3. **As an AI agent**, I want AAA scenarios automatically mapped to vitest/jest test functions with proper type-safe assertions, so that test output is idiomatic TypeScript.

## Acceptance Criteria

### AC-1: Standard I/O Contract

- GIVEN the orchestrator routes a TypeScript tech_stack entry to this skill
- WHEN the skill receives `aaa_scenarios`, `source_code_path`, `test_code_path`, and `feature_context`
- THEN it returns `implementation_files`, `test_files`, `test_results`, `lint_status` in the standard format defined in [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md)

### AC-2: TypeScript Strict Mode

- GIVEN this skill is invoked
- WHEN it implements source code
- THEN it applies: `strict: true` in tsconfig.json, no implicit `any`, strict null checks enabled, strict property initialization

### AC-3: Interface-First Design

- GIVEN any new module is implemented
- WHEN the skill writes TypeScript code
- THEN it defines interfaces/types before implementation, uses named exports, and avoids `any` unless explicitly justified with a comment

### AC-4: Test Mapping (vitest/jest)

- GIVEN AAA scenarios are provided
- WHEN the skill writes tests
- THEN it creates vitest (preferred) or jest functions: `test('{scenario name}', () => {})` or `it('{scenario name}', () => {})` with Arrange→setup/mocks, Act→function call, Assert→typed assertions

### AC-5: Linting Integration (ESLint + typescript-eslint + Prettier)

- GIVEN implementation is complete
- WHEN the skill runs linting
- THEN it executes ESLint with @typescript-eslint plugin and Prettier
- AND fixes any auto-fixable issues before returning results

### AC-6: Framework Detection

- GIVEN a `source_code_path` with existing TypeScript code
- WHEN the skill reads the project
- THEN it detects the framework (React, Vue, Angular, Next.js, Express, Fastify, NestJS, or plain Node.js) and applies framework-specific patterns

### AC-7: Null Safety and Generics

- GIVEN any implementation
- WHEN the skill writes TypeScript code
- THEN it uses proper null handling (optional chaining, nullish coalescing, discriminated unions), generics where appropriate, and custom Error classes for domain errors

## Functional Requirements

### FR-1: Skill File Structure
The skill SHALL be a SKILL.md file at `.github/skills/x-ipe-tool-implementation-typescript/SKILL.md` with accompanying `references/examples.md`.

### FR-2: Built-In Practices (No Research Step)
The skill SHALL NOT include a research step. TypeScript best practices (strict mode, interface-first, null safety, proper imports/exports) are baked into the operation steps.

### FR-3: AAA-to-Test Mapping
The skill SHALL map each AAA scenario to a `test('{scenario_name}', () => {})` or `it('{scenario_name}', () => {})` function. Each Assert clause SHALL become a typed test assertion.

### FR-4: Framework Detection Logic
The skill SHALL detect frameworks by checking: `package.json` for dependencies, tsconfig.json for compiler options (jsx, decorators), file patterns (`.tsx` for React, `.vue` for Vue SFCs, Angular decorators).

### FR-5: tsconfig Awareness
The skill SHALL read existing `tsconfig.json` and respect its settings (paths, module resolution, baseUrl). If no tsconfig exists, the skill SHALL recommend `strict: true` configuration.

### FR-6: Linting Pipeline
The skill SHALL run ESLint (with @typescript-eslint) → Prettier → re-run tests after lint fixes. If ESLint is unavailable, log warning and return `lint_status: "skipped"`.

### FR-7: Standard Output Contract
The skill SHALL return output matching the tool skill I/O contract: `implementation_files`, `test_files`, `test_results` (per Assert clause), `lint_status`.

## Non-Functional Requirements

### NFR-1: Skill File Size
The SKILL.md SHALL be under 250 lines to maintain readability and context efficiency.

### NFR-2: No External Dependencies
The skill SHALL not require any tools beyond standard TypeScript development tools (tsc, vitest/jest, ESLint, Prettier).

### NFR-3: Orchestrator Compatibility
The skill SHALL be auto-discoverable by the orchestrator's AI semantic routing via its `description` and `When to Use` section.

## Technical Scope

- [x] Skills (SKILL.md + references)
- [ ] Backend
- [ ] Frontend
- [ ] Full Stack

## Dependencies

- FEATURE-045-A (Orchestrator Core + AAA Generator + General Fallback) — **completed**
- [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md) — I/O contract definition
