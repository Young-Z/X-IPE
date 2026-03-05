# Feature Specification: HTML5 Implementation Tool Skill

> Feature ID: FEATURE-045-C  
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

This feature creates `x-ipe-tool-implementation-html5`, a language-specific tool skill that the `x-ipe-task-based-code-implementation` orchestrator routes to when `tech_stack` contains HTML/CSS/JavaScript entries. Unlike the general fallback skill, this skill has **built-in web best practices** — no research step is needed.

The skill accepts AAA scenarios from the orchestrator, implements semantic HTML5/CSS3/ES6+ code with accessibility and responsive design built in, writes vitest/jest test functions mapped to AAA Assert clauses, runs tests and linting (ESLint + Prettier), and returns the standard tool skill output contract.

## User Stories

1. **As an AI agent**, I want an HTML5-specific implementation skill with built-in best practices (semantic HTML, accessibility, responsive design), so that I can implement web code faster without a research step.

2. **As an AI agent**, I want the skill to detect whether the project uses vanilla JS, web components, Alpine.js, HTMX, or other lightweight frameworks, so that framework-specific patterns are applied correctly.

3. **As an AI agent**, I want AAA scenarios automatically mapped to vitest/jest test functions with accessibility audits and viewport tests, so that test output is idiomatic web code.

## Acceptance Criteria

### AC-1: Standard I/O Contract

- GIVEN the orchestrator routes an HTML/CSS/JS tech_stack entry to this skill
- WHEN the skill receives `aaa_scenarios`, `source_code_path`, `test_code_path`, and `feature_context`
- THEN it returns `implementation_files`, `test_files`, `test_results`, `lint_status` in the standard format defined in [implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md)

### AC-2: HTML5/CSS3/JS Best Practices (Built-In)

- GIVEN this skill is invoked
- WHEN it implements source code
- THEN it applies: semantic HTML5 elements, CSS3 with BEM or utility-class awareness, ES6+ JavaScript, proper meta tags, charset/viewport declarations

### AC-3: Accessibility Compliance

- GIVEN any HTML output is generated
- WHEN the skill implements UI components
- THEN it includes: ARIA roles/labels where appropriate, keyboard navigation support, focus management, sufficient color contrast guidance, alt text for images

### AC-4: Responsive Design

- GIVEN any layout is implemented
- WHEN the skill writes CSS
- THEN it follows mobile-first approach with media queries, fluid grids, relative units (rem/em/%), and viewport-aware breakpoints

### AC-5: Test Mapping

- GIVEN AAA scenarios are provided
- WHEN the skill writes tests
- THEN it creates vitest/jest functions: `test('{scenario name}', () => {})` with Arrange→DOM setup, Act→user interaction or render, Assert→DOM assertions and accessibility checks

### AC-6: Linting Integration

- GIVEN implementation is complete
- WHEN the skill runs linting
- THEN it executes ESLint and Prettier (falling back to available linters if not installed)
- AND fixes any auto-fixable issues before returning results

### AC-7: Framework Detection

- GIVEN a `source_code_path` with existing web code
- WHEN the skill reads the project
- THEN it detects the framework (vanilla JS, web components, Alpine.js, HTMX, or static HTML) and applies framework-specific patterns

## Functional Requirements

### FR-1: Skill File Structure
The skill SHALL be a SKILL.md file at `.github/skills/x-ipe-tool-implementation-html5/SKILL.md` with accompanying `references/examples.md`.

### FR-2: Built-In Practices (No Research Step)
The skill SHALL NOT include a research step. Web best practices (semantic HTML5, CSS3, ES6+, accessibility, responsive design) are baked into the operation steps.

### FR-3: AAA-to-Test Mapping
The skill SHALL map each AAA scenario to a `test('{scenario_name}', () => {})` function. Each Assert clause SHALL become a test assertion. Accessibility Assert clauses SHALL use DOM role/label queries.

### FR-4: Framework Detection Logic
The skill SHALL detect frameworks by checking: `package.json` for dependencies, file patterns (`.html` with `x-data` for Alpine.js, `hx-` attributes for HTMX, `customElements.define` for web components).

### FR-5: CSS Methodology Detection
The skill SHALL detect CSS methodology by scanning existing stylesheets for BEM naming (`block__element--modifier`), utility classes (Tailwind-style), CSS custom properties, or CSS modules.

### FR-6: Linting Pipeline
The skill SHALL run ESLint → Prettier → re-run tests after lint fixes. If ESLint is unavailable, log warning and return `lint_status: "skipped"`.

### FR-7: Standard Output Contract
The skill SHALL return output matching the tool skill I/O contract: `implementation_files`, `test_files`, `test_results` (per Assert clause), `lint_status`.

## Non-Functional Requirements

### NFR-1: Skill File Size
The SKILL.md SHALL be under 250 lines to maintain readability and context efficiency.

### NFR-2: No External Dependencies
The skill SHALL not require any tools beyond standard web development tools (vitest/jest, ESLint, Prettier).

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
