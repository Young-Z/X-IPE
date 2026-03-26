# User Manual — Acceptance Criteria

> Per-section validation rules for the Application Knowledge Extractor.
> Each H2 matches a playbook section. Checklist items are evaluated by the `validate_section` operation.
> A section passes validation only when ALL required items (marked `[REQ]`) are satisfied.

---

## Section Validation Rules

### 1. Overview

- [ ] `[REQ]` Contains description of what the application does (at least 2 sentences)
- [ ] `[REQ]` Identifies target audience or use case
- [ ] `[REQ]` Lists at least 3 key features or capabilities
- [ ] `[OPT]` Includes high-level architecture or workflow summary
- [ ] `[OPT]` Mentions the technology stack or platform

### 2. Installation & Setup

- [ ] `[REQ]` Lists system prerequisites with version requirements
- [ ] `[REQ]` Provides copy-pasteable install commands
- [ ] `[REQ]` Includes verification step to confirm successful install
- [ ] `[OPT]` Covers Docker or containerized setup alternative
- [ ] `[OPT]` Documents initial configuration (API keys, database init)

### 3. Getting Started

- [ ] `[REQ]` Provides a quick start path completable in under 5 minutes
- [ ] `[REQ]` Walks through the basic happy-path workflow with concrete steps
- [ ] `[REQ]` Includes at least one example command or action with expected output
- [ ] `[REQ]` Quick start must specify exact UI actions (click X, type Y, press Enter)
- [ ] `[REQ]` Each step must include expected outcome ("you should see...")
- [ ] `[REQ]` If actions dispatch commands to terminal/CLI, must explicitly state "press Enter to execute"
- [ ] `[OPT]` References sample data or seed scripts if available
- [ ] `[OPT]` Links to more detailed tutorials or guides

### 4. Core Features

- [ ] `[REQ]` Documents at least 3 distinct features
- [ ] `[REQ]` Each feature has a description of what it does
- [ ] `[REQ]` Each feature has step-by-step usage instructions (not just a description)
- [ ] `[REQ]` Each feature includes at least one concrete example with expected output
- [ ] `[REQ]` Features reference screenshots for UI-visible actions (or explain why N/A)
- [ ] `[REQ]` Each feature must classify its interaction pattern (form/modal/CLI dispatch/navigation/toggle)
- [ ] `[REQ]` CLI dispatch features must document: what system receives command, whether Enter is needed, how to know when complete
- [ ] `[REQ]` Each step-by-step instruction must include the exact UI element name/label to interact with
- [ ] `[OPT]` Features include tips or best practices
- [ ] `[OPT]` Features document edge cases or error handling
- [ ] `[OPT]` Features note required permissions or roles

### 5. Common Workflow Scenarios

- [ ] `[REQ]` Contains at least 3 end-to-end workflow scenarios
- [ ] `[REQ]` Each scenario states a clear goal
- [ ] `[REQ]` Each scenario has numbered steps referencing features from Section 4
- [ ] `[REQ]` Each scenario describes the expected result
- [ ] `[REQ]` At least 1 scenario must be verifiable end-to-end (every step has exact action + expected outcome)
- [ ] `[REQ]` Scenario steps must not assume implicit knowledge between consecutive steps
- [ ] `[REQ]` Steps involving async operations (AI processing, builds) must specify how to know when complete
- [ ] `[OPT]` Scenarios include screenshots of key workflow states
- [ ] `[OPT]` Scenarios include prerequisites
- [ ] `[OPT]` Scenarios provide tips or variations

### 6. Configuration

- [ ] `[REQ]` Identifies configuration file location and format
- [ ] `[REQ]` Lists environment variables with descriptions and defaults
- [ ] `[REQ]` Documents at least 3 configurable settings
- [ ] `[OPT]` Explains profile or environment management (dev/staging/prod)
- [ ] `[OPT]` Includes runtime flags or command-line options

### 7. Troubleshooting

- [ ] `[REQ]` Lists at least 3 common issues with symptoms and solutions
- [ ] `[REQ]` Explains how to enable debug or verbose mode
- [ ] `[REQ]` Provides at least one diagnostic step (checking logs, health endpoint)
- [ ] `[OPT]` Catalogs error messages with explanations
- [ ] `[OPT]` Includes links to support channels or issue tracker

### 8. FAQ & Reference

- [ ] `[REQ]` Contains at least 5 frequently asked questions with answers
- [ ] `[REQ]` Includes glossary of domain-specific terms (at least 3 terms)
- [ ] `[OPT]` Documents keyboard shortcuts if applicable
- [ ] `[OPT]` Summarizes version history or links to changelog
- [ ] `[OPT]` Provides quick-reference tables or cheat sheets

---

## Validation Scoring

| Rating | Criteria |
|--------|----------|
| **PASS** | ALL `[REQ]` items satisfied for the section |
| **PARTIAL** | At least 50% of `[REQ]` items satisfied — needs iteration |
| **FAIL** | Fewer than 50% of `[REQ]` items satisfied — re-extract |
