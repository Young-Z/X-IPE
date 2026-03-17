# User Manual — Collection Template

> Per-section extraction prompts for the Application Knowledge Extractor.
> Each H2 matches a playbook section. HTML comments contain extraction instructions.
> The extractor reads these prompts to guide source analysis.

---

## 1. Overview

<!-- EXTRACTION PROMPTS:
- What does this application do? (look for README.md, about pages, landing pages, package.json description)
- Who is the target audience? (look for persona references, "designed for" statements, marketing copy)
- What problem does it solve? (look for motivation sections, "why" paragraphs, project proposals)
- What are the key features? (look for feature lists, highlights, badges in README)
- Is there a high-level architecture or workflow diagram? (look for docs/, diagrams/, mermaid blocks)

SOURCE PRIORITY:
1. README.md (root level)
2. docs/index.md or docs/README.md
3. Package metadata (package.json description, pyproject.toml [project] description)
4. Landing page or about page content
-->

---

## 2. Installation & Setup

<!-- EXTRACTION PROMPTS:
- What are the system prerequisites? (look for requirements.txt, package.json engines, Dockerfile FROM, .tool-versions)
- What runtime versions are required? (look for .python-version, .nvmrc, .node-version, rust-toolchain.toml)
- What are the install commands? (look for README install section, Makefile install target, scripts/setup.*, CONTRIBUTING.md)
- Is there a Docker-based setup? (look for Dockerfile, docker-compose.yml, .devcontainer/)
- What initial configuration is needed? (look for .env.example, config.example.*, setup wizards)
- How to verify installation succeeded? (look for health check endpoints, version commands, smoke test scripts)

SOURCE PRIORITY:
1. README.md "Installation" or "Setup" section
2. CONTRIBUTING.md or DEVELOPMENT.md
3. Makefile / justfile / taskfile targets
4. CI/CD setup steps (as proxy for what's needed)
-->

---

## 3. Getting Started

<!-- EXTRACTION PROMPTS:
- Is there a quickstart guide? (look for QUICKSTART.md, "Getting Started" in README, tutorials/)
- What is the minimal happy-path workflow? (look for example scripts, demo/, examples/)
- Are there sample data or seed scripts? (look for fixtures/, seeds/, sample-data/)
- What does first-run experience look like? (look for onboarding flows, setup wizards, init commands)
- Are there tutorial or walkthrough documents? (look for docs/tutorial*, docs/guide*, docs/getting-started*)

SOURCE PRIORITY:
1. README.md "Getting Started" or "Quick Start" section
2. docs/getting-started.md or docs/quickstart.md
3. examples/ directory with README
4. Tutorial or walkthrough documents
-->

---

## 4. Core Features

<!-- EXTRACTION PROMPTS:
- What are the main features? (look for feature list in README, docs/features/, module docstrings)
- How is each feature used? (look for usage examples, API docs, CLI help text, UI screenshots)
- Are there feature-specific docs? (look for docs/{feature-name}.md, wiki pages)
- What are the feature entry points? (look for route handlers, CLI commands, menu items)
- Are there best practices or tips per feature? (look for "tips", "best practices", "pro tips" sections)

PER-FEATURE DETAIL (extract for EACH feature individually):
- Step-by-step instructions: What does a user click/type to use this feature?
- Input/output: What goes in, what comes out?
- UI elements: What does the user see? (capture screenshots if web/app via Chrome DevTools)
- Edge cases: What happens with invalid input, empty state, or limits?
- Permissions: Does this feature require specific roles or access?

SCREENSHOT GUIDANCE:
- For each major feature, capture a screenshot showing the feature in action
- Name: 04-core-features-{feature-slug}-{description}.png
- Prioritize: main UI state, key dialogs, result/output views

WHEN CONTENT IS THIN:
- If a feature has only a one-liner description and no usage detail → flag INCOMPLETE
- Request extractor to: read source code for the feature entry point, check test files for behavior, run the app and capture screenshots

SOURCE PRIORITY:
1. README.md feature descriptions
2. docs/ directory organized by feature
3. CLI --help output for each command
4. Source code docstrings and comments on public APIs
5. Test files (describe blocks reveal feature behavior)
6. Running application UI (Chrome DevTools screenshots)
-->

---

## 5. Common Workflow Scenarios

<!-- EXTRACTION PROMPTS:
- What are the most common end-to-end user journeys? (look for tutorials, guides, example scripts, demo workflows)
- How do features combine in real usage? (look for integration tests, e2e tests, CI/CD pipelines)
- What does onboarding a new user look like? (look for onboarding docs, getting-started-advanced, setup wizards)
- Are there documented use cases or stories? (look for use-case docs, user stories, case studies)
- What recurring patterns appear in issues/discussions? (look for "how do I" questions, common support requests)

PER-SCENARIO DETAIL:
- Goal: What is the user trying to accomplish?
- Prerequisites: What must already be set up?
- Steps: Numbered walkthrough showing which features are used and in what order
- Expected result: What does success look like?
- Cross-references: Link back to relevant Section 4 features

SCREENSHOT GUIDANCE:
- Capture key transition points in the workflow (start state, intermediate states, end state)
- Name: 05-workflows-{scenario-slug}-{description}.png

WHEN CONTENT IS THIN:
- If no explicit workflow docs exist → flag INCOMPLETE
- Request extractor to: analyze test suites for multi-step flows, check example/ directories, examine CI pipelines for typical usage patterns

SOURCE PRIORITY:
1. docs/tutorials/ or docs/guides/ directories
2. examples/ directory with multi-step scripts
3. Integration/e2e test files (reveal realistic usage flows)
4. README.md workflow or usage sections
5. Issue tracker "how to" threads
-->

---

## 6. Configuration

<!-- EXTRACTION PROMPTS:
- Where is the configuration file? (look for config/, settings/, .env, *.config.js, *.yaml)
- What environment variables are used? (look for .env.example, process.env references, os.environ usage)
- What are the defaults? (look for default config objects, fallback values in code)
- Are there different profiles/environments? (look for config/development.*, config/production.*, NODE_ENV usage)
- What runtime flags/options exist? (look for argparse definitions, commander/yargs setup, CLI flag parsing)

SOURCE PRIORITY:
1. .env.example or .env.template
2. Configuration documentation in docs/
3. Config file schemas or types (config.schema.json, Settings class)
4. Source code scanning for env var references
-->

---

## 7. Troubleshooting

<!-- EXTRACTION PROMPTS:
- Are there documented common issues? (look for TROUBLESHOOTING.md, FAQ sections, "Known Issues" in README)
- What error messages does the app produce? (look for error constants, error message strings in source)
- How to enable debug/verbose mode? (look for DEBUG env var, --verbose flag, log level settings)
- Where are logs stored? (look for log configuration, logging setup, log file paths)
- Is there a health check or diagnostic command? (look for /health endpoints, doctor/diagnose commands)
- Where to get help? (look for SUPPORT.md, community links, issue templates)

SOURCE PRIORITY:
1. TROUBLESHOOTING.md or FAQ.md
2. README.md troubleshooting section
3. GitHub Issues (common/recurring themes)
4. Error handling code (for error message catalog)
-->

---

## 8. FAQ & Reference

<!-- EXTRACTION PROMPTS:
- Is there an existing FAQ? (look for FAQ.md, docs/faq.*, "Frequently Asked Questions" sections)
- What domain-specific terms are used? (look for glossary files, term definitions in docs)
- Are there keyboard shortcuts? (look for shortcut definitions, keybinding configs)
- What is the version history? (look for CHANGELOG.md, HISTORY.md, release notes)
- Are there reference tables or cheat sheets? (look for docs/reference*, cheatsheet.md)

SOURCE PRIORITY:
1. FAQ.md or docs/faq.md
2. CHANGELOG.md or HISTORY.md
3. Glossary or terminology sections in docs
4. README.md reference section
-->
