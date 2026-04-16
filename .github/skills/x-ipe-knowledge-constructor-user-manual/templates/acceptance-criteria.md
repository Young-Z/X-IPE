# User Manual — Acceptance Criteria (Constructor)

> Per-section rubric definitions for the `design_rubric` operation.
> Each H2 matches a playbook section. The constructor loads these criteria
> and adapts weights based on user emphasis.

---

## Rubric Scoring

| Rating | Criteria |
|--------|----------|
| **PASS** | ALL `[REQ]` items satisfied for the section |
| **PARTIAL** | At least 50% of `[REQ]` items satisfied — needs iteration |
| **FAIL** | Fewer than 50% of `[REQ]` items satisfied — request more knowledge |

**Weight scale:** 1 (low) — 2 (normal) — 3 (high, user-emphasized)

---

## Section Rubric Definitions

### 1. Overview

**Default weight:** 2

| ID | Type | Criterion | Threshold |
|----|------|-----------|-----------|
| OV-01 | `[REQ]` | Contains description of what the application does | ≥2 sentences |
| OV-02 | `[REQ]` | Identifies target audience or use case | ≥1 persona or use case |
| OV-03 | `[REQ]` | Lists key features or capabilities | ≥3 features listed |
| OV-04 | `[OPT]` | Includes high-level architecture or workflow summary | Present or explained N/A |
| OV-05 | `[OPT]` | Mentions the technology stack or platform | Present |

### 2. Installation & Setup

**Default weight:** 2

| ID | Type | Criterion | Threshold |
|----|------|-----------|-----------|
| IS-01 | `[REQ]` | Lists system prerequisites with version requirements | ≥1 prerequisite with version |
| IS-02 | `[REQ]` | Provides copy-pasteable install commands | ≥1 command block |
| IS-03 | `[REQ]` | Includes verification step to confirm successful install | ≥1 verification action |
| IS-04 | `[OPT]` | Covers Docker or containerized setup alternative | Present or explained N/A |
| IS-05 | `[OPT]` | Documents initial configuration (API keys, database init) | Present |

### 3. Getting Started

**Default weight:** 3 (commonly emphasized)

| ID | Type | Criterion | Threshold |
|----|------|-----------|-----------|
| GS-01 | `[REQ]` | Provides a quick start path completable in under 5 minutes | ≤5 steps |
| GS-02 | `[REQ]` | Walks through basic happy-path workflow with concrete steps | ≥3 steps with actions |
| GS-03 | `[REQ]` | Includes at least one example command/action with expected output | ≥1 example |
| GS-04 | `[REQ]` | Each step specifies exact UI actions (click X, type Y, press Enter) | All steps have actions |
| GS-05 | `[REQ]` | Each step includes expected outcome ("you should see...") | All steps have outcomes |
| GS-06 | `[REQ]` | CLI dispatch steps explicitly state "press Enter to execute" | All CLI steps covered |
| GS-07 | `[OPT]` | References sample data or seed scripts if available | Present |
| GS-08 | `[OPT]` | Links to more detailed tutorials or guides | Present |

### 4. Core Features

**Default weight:** 3 (main body)

| ID | Type | Criterion | Threshold |
|----|------|-----------|-----------|
| CF-01 | `[REQ]` | Documents distinct features | ≥3 features |
| CF-02 | `[REQ]` | Each feature has a description of what it does | All features described |
| CF-03 | `[REQ]` | Each feature has step-by-step usage instructions | All features have instructions |
| CF-04 | `[REQ]` | Each feature includes concrete example with expected output | ≥1 example per feature |
| CF-05 | `[REQ]` | Features reference screenshots for UI-visible actions | Screenshots or N/A explanation |
| CF-06 | `[REQ]` | Each feature classifies interaction pattern | All features have pattern |
| CF-07 | `[REQ]` | CLI dispatch features document system, Enter requirement, completion indicator | All CLI features covered |
| CF-08 | `[REQ]` | Instructions include exact UI element name/label | All steps have element names |
| CF-09 | `[OPT]` | Features include tips or best practices | Present |
| CF-10 | `[OPT]` | Features document edge cases or error handling | Present |

### 5. Common Workflow Scenarios

**Default weight:** 2

| ID | Type | Criterion | Threshold |
|----|------|-----------|-----------|
| WF-01 | `[REQ]` | Contains end-to-end workflow scenarios | ≥3 scenarios |
| WF-02 | `[REQ]` | Each scenario states a clear goal | All scenarios have goal |
| WF-03 | `[REQ]` | Each scenario has numbered steps referencing Section 4 features | All scenarios have steps |
| WF-04 | `[REQ]` | Each scenario describes the expected result | All scenarios have result |
| WF-05 | `[REQ]` | At least 1 scenario is verifiable end-to-end | ≥1 fully actionable |
| WF-06 | `[REQ]` | Steps don't assume implicit knowledge between steps | Each step self-contained |
| WF-07 | `[REQ]` | Async operation steps specify completion indicator | All async steps covered |
| WF-08 | `[OPT]` | Scenarios include screenshots of key states | Present |
| WF-09 | `[OPT]` | Scenarios include prerequisites | Present |

### 6. Configuration

**Default weight:** 1

| ID | Type | Criterion | Threshold |
|----|------|-----------|-----------|
| CO-01 | `[REQ]` | Identifies configuration file location and format | ≥1 config file documented |
| CO-02 | `[REQ]` | Lists environment variables with descriptions and defaults | ≥1 env var documented |
| CO-03 | `[REQ]` | Documents configurable settings | ≥3 settings |
| CO-04 | `[OPT]` | Explains profile or environment management | Present |
| CO-05 | `[OPT]` | Includes runtime flags or command-line options | Present |

### 7. Troubleshooting

**Default weight:** 1

| ID | Type | Criterion | Threshold |
|----|------|-----------|-----------|
| TS-01 | `[REQ]` | Lists common issues with symptoms and solutions | ≥3 issues |
| TS-02 | `[REQ]` | Explains how to enable debug or verbose mode | ≥1 diagnostic method |
| TS-03 | `[REQ]` | Provides at least one diagnostic step | ≥1 step |
| TS-04 | `[OPT]` | Catalogs error messages with explanations | Present |
| TS-05 | `[OPT]` | Includes links to support channels or issue tracker | Present |

### 8. FAQ & Reference

**Default weight:** 1

| ID | Type | Criterion | Threshold |
|----|------|-----------|-----------|
| FR-01 | `[REQ]` | Contains frequently asked questions with answers | ≥5 FAQs |
| FR-02 | `[REQ]` | Includes glossary of domain-specific terms | ≥3 terms |
| FR-03 | `[OPT]` | Documents keyboard shortcuts if applicable | Present or N/A |
| FR-04 | `[OPT]` | Summarizes version history or links to changelog | Present |
| FR-05 | `[OPT]` | Provides quick-reference tables or cheat sheets | Present |

---

## Weight Adjustment Rules

The constructor adjusts default weights based on `user_request`:

1. **Explicit mention** → Set weight to 3 (e.g., "focus on getting started" → GS weight=3)
2. **User goal alignment** → Boost weight for sections that directly serve user_goal
3. **App-type defaults** → CLI apps boost Section 4 (Core Features as commands); web apps boost Section 5 (Workflows)
4. **Minimum floor** → No section weight below 1 (all sections must be evaluated)
