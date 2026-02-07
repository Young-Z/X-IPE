# Technical Design - Design Principles & Rules

> Reference from SKILL.md: `See [references/design-principles.md](references/design-principles.md)`

---

## Design Principles

### KISS (Keep It Simple, Stupid)

- Design simple, maintainable solutions
- Avoid over-engineering
- Choose boring technology when possible
- Complex solutions need strong justification

**Good:** Direct database queries for simple CRUD
**Bad:** Adding message queues for simple data fetching

---

### YAGNI (You Aren't Gonna Need It)

- Design ONLY for current requirements
- No "future-proofing" without clear need
- Defer decisions until last responsible moment
- Avoid speculative generality

**Good:** Simple auth for MVP, expand later if needed
**Bad:** Building OAuth, SSO, MFA when only email/password needed

---

### DRY (Don't Repeat Yourself)

- Identify common patterns across features
- Extract shared logic into reusable components
- Reference existing architecture designs
- But: Don't DRY prematurely (wait for 3+ duplications)

**Good:** Reuse existing error handling patterns
**Bad:** Creating abstractions before seeing actual duplication

---

### Module Size Rule (800-Line Threshold)

> **Rule:** When adding new functionality to an existing file, if the result would exceed **800 lines of code**, extract the new functionality into a **standalone module**.

**Rationale:**
- Files over 800 lines become difficult to navigate and maintain
- Standalone modules enable better separation of concerns
- Easier to test, debug, and refactor isolated modules
- Reduces merge conflicts in collaborative development

**How to Apply:**
1. Before adding code to existing file, check current line count
2. Estimate new functionality size
3. If `current + new > 800`, create new module
4. Keep integration points minimal (exports/imports)

**Good:** Creating `voice-input.js` (400 lines) separate from `terminal-v2.js` (500 lines)
**Bad:** Adding voice input directly to terminal-v2.js making it 900+ lines

---

## Document Location Rules

| Design Scope | Location |
|--------------|----------|
| Feature-specific design | `x-ipe-docs/requirements/FEATURE-XXX/technical-design.md` |
| Cross-feature/Architecture design | `x-ipe-docs/architecture/technical-designs/{component}.md` |

---

## Single File with Version History

**Rule:** Maintain ONE technical design file per feature with version history inside.

- Do NOT create versioned files like `technical-design-v2.md`
- Keep single `technical-design.md` with Version History table at top
- Update content in place, increment version header

---

## Two-Part Document Structure

Technical design documents MUST use this two-part structure. Adapt content based on implementation type (API, CLI, frontend, backend, etc.).

| Part | Purpose | Focus |
|------|---------|-------|
| Part 1: Agent-Facing Summary | Quick reference for AI agents | Key components, dependencies, major flow, usage example |
| Part 2: Implementation Guide | Human-readable details | Workflow diagrams, data models, API specs, implementation steps |

**Format Guidelines:**
- Use tables for component listings with Tags for semantic search
- Include dependency table linking to other feature/foundation designs
- Prioritize Mermaid diagrams for visual comprehension

See [design-templates.md](design-templates.md) for full document template with examples.
