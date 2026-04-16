# User Manual — Collection Template (Constructor)

> Per-section knowledge request patterns for the `request_knowledge` operation.
> Each H2 matches a playbook section. The constructor reads these prompts to generate
> specific extraction requests for knowledge gaps.

---

## 1. Overview

**Knowledge request patterns:**
- "Extract application description from README.md, about pages, or landing pages"
- "Identify target audience from persona references, 'designed for' statements, or marketing copy"
- "List key features from feature lists, highlights, or badges in README"
- "Find high-level architecture or workflow diagram from docs/, diagrams/, or mermaid blocks"

**Source priority:** README.md → docs/index.md → package metadata → landing page content

**Suggested extractor:** extractor-web (for live source analysis), extractor-memory (if docs already extracted)

---

## 2. Installation & Setup

**Knowledge request patterns:**
- "Extract system prerequisites from requirements.txt, package.json engines, Dockerfile, .tool-versions"
- "Find install commands from README install section, Makefile targets, CONTRIBUTING.md"
- "Identify initial configuration steps from .env.example, config templates, setup wizards"
- "Find verification steps from health check endpoints, version commands, smoke test scripts"

**Source priority:** README.md setup section → CONTRIBUTING.md → Makefile/taskfile → CI/CD setup steps

**Suggested extractor:** extractor-web (for code/config files), extractor-memory (for existing docs)

---

## 3. Getting Started

**Knowledge request patterns:**
- "Find quickstart guide from QUICKSTART.md, README 'Getting Started' section, tutorials/"
- "Extract minimal happy-path workflow from example scripts, demo/, examples/"
- "Identify first-run experience from onboarding flows, setup wizards, init commands"
- "Find tutorial or walkthrough documents from docs/tutorial*, docs/guide*"

**Source priority:** README.md Getting Started → docs/getting-started.md → examples/ → tutorials

**Suggested extractor:** extractor-web (for live source), extractor-memory (for existing tutorials)

---

## 4. Core Features

**Knowledge request patterns:**
- "List all main features from README feature list, docs/features/, module docstrings"
- "For each feature, extract step-by-step usage instructions (not just description)"
- "Identify feature entry points from route handlers, CLI commands, menu items"
- "Capture interaction patterns per feature: FORM, MODAL, CLI_DISPATCH, NAVIGATION, TOGGLE"
- "For CLI_DISPATCH features: what system receives command, whether Enter needed, expected output"

**Per-feature detail requests:**
- "What does a user click/type to use feature X?"
- "What input goes in, what output comes out for feature X?"
- "What UI elements does the user see for feature X?"
- "What happens with invalid input or edge cases for feature X?"

**Source priority:** README features → docs/ by feature → CLI --help → source docstrings → test files → running app

**Suggested extractor:** extractor-web (for source code, UI screenshots), extractor-memory (for existing docs)

---

## 5. Common Workflow Scenarios

**Knowledge request patterns:**
- "Identify end-to-end user journeys from tutorials, guides, e2e tests, CI pipelines"
- "Extract workflow steps showing how features combine in real usage"
- "Find onboarding workflows from onboarding docs, getting-started-advanced"
- "Discover recurring usage patterns from issues/discussions, 'how do I' questions"

**Per-workflow detail requests:**
- "What is the user trying to accomplish in workflow X?"
- "What prerequisites must be set up before starting workflow X?"
- "What are the numbered steps, and which Section 4 features are used?"
- "What does success look like for workflow X?"

**Source priority:** docs/tutorials/ → examples/ → integration tests → README usage → issue tracker

**Suggested extractor:** extractor-web (for test analysis, live walkthrough), extractor-memory (for existing guides)

---

## 6. Configuration

**Knowledge request patterns:**
- "Find configuration file location and format from config/, settings/, .env"
- "Extract environment variables from .env.example, process.env references, os.environ usage"
- "List defaults from default config objects, fallback values in code"
- "Identify profiles/environments from config/development.*, NODE_ENV usage"

**Source priority:** .env.example → config docs → config schemas → source code env var references

**Suggested extractor:** extractor-web (for config file analysis), extractor-memory (for existing config docs)

---

## 7. Troubleshooting

**Knowledge request patterns:**
- "Find documented common issues from TROUBLESHOOTING.md, FAQ, 'Known Issues' in README"
- "Extract error messages from error constants, error message strings in source"
- "Find debug/verbose mode instructions from DEBUG env var, --verbose flag, log config"
- "Identify log locations from logging setup, log file paths"
- "Find health check or diagnostic commands"

**Source priority:** TROUBLESHOOTING.md → README troubleshooting → GitHub Issues → error handling code

**Suggested extractor:** extractor-web (for error catalog from source), extractor-memory (for existing troubleshooting docs)

---

## 8. FAQ & Reference

**Knowledge request patterns:**
- "Find existing FAQ from FAQ.md, docs/faq.*, 'Frequently Asked Questions' sections"
- "Extract domain-specific terms for glossary from docs, code comments"
- "Find keyboard shortcuts from shortcut definitions, keybinding configs"
- "Extract version history from CHANGELOG.md, HISTORY.md, release notes"

**Source priority:** FAQ.md → CHANGELOG.md → glossary docs → README reference section

**Suggested extractor:** extractor-memory (for existing FAQ/changelog), extractor-web (for source analysis)
