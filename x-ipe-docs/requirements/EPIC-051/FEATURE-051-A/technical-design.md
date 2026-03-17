# Technical Design: User Manual Tool Skill

> Feature ID: FEATURE-051-A | Version: v1.0 | Last Updated: 03-17-2026

---

## Part 1: AC-to-Deliverable Mapping

| AC Group | AC IDs | Deliverable File(s) | Section(s) |
|----------|--------|---------------------|------------|
| AC-051-01: Skill Structure & Discovery | AC-051-01a, AC-051-01b, AC-051-01c, AC-051-01d | `.github/skills/x-ipe-tool-knowledge-extraction-user-manual/SKILL.md` | Frontmatter (categories, artifact paths), folder structure (`references/`, `templates/`) |
| AC-051-02: Playbook Template | AC-051-02a, AC-051-02b, AC-051-02c, AC-051-02d | `templates/playbook-base.md` | All 7 sections with H2 headings + descriptions |
| AC-051-03: Collection Template & Extraction Prompts | AC-051-03a, AC-051-03b, AC-051-03c, AC-051-03d | `templates/collection-template.md` | All 7 sections with HTML comment extraction prompts |
| AC-051-04: Acceptance Criteria File | AC-051-04a, AC-051-04b, AC-051-04c, AC-051-04d | `references/acceptance-criteria.md` | 7 section headings, each with 3-5 pass/fail criteria |
| AC-051-05: App-Type Mixins | AC-051-05a, AC-051-05b, AC-051-05c, AC-051-05d, AC-051-05e | `templates/mixin-web.md`, `templates/mixin-cli.md`, `templates/mixin-mobile.md` | Section-specific augmented prompts for each app type |
| AC-051-06: Operations API | AC-051-06a, AC-051-06b, AC-051-06c, AC-051-06d | `SKILL.md` | Operations section with 5 XML operation blocks: get_artifacts, get_collection_template, validate_section, get_mixin, pack_section |

---

## Part 2: Implementation Plan

### File Structure

```
.github/skills/x-ipe-tool-knowledge-extraction-user-manual/
├── SKILL.md                              # Main skill definition (≤500 lines)
├── references/
│   ├── acceptance-criteria.md            # Per-section validation rules (7 sections × 3-5 criteria)
│   └── examples.md                       # Usage examples for extractor integration
└── templates/
    ├── playbook-base.md                  # 7-section base structure
    ├── collection-template.md            # 7 sections with extraction prompts
    ├── mixin-web.md                      # Web app mixin prompts
    ├── mixin-cli.md                      # CLI app mixin prompts
    └── mixin-mobile.md                   # Mobile app mixin prompts
```

**Total files:** 8 (1 SKILL.md + 2 references + 5 templates)

---

### SKILL.md Structure

Following the X-IPE tool skill template, SKILL.md contains these sections in order:

1. **Frontmatter (YAML)** — Lines 1-10
   ```yaml
   ---
   name: x-ipe-tool-knowledge-extraction-user-manual
   description: Domain expertise for extracting user manual documentation. Provides playbook, prompts, validation rules, and app-type mixins.
   categories:
     - user-manual
   artifact_paths:
     playbook_template: templates/playbook-base.md
     collection_template: templates/collection-template.md
     acceptance_criteria: references/acceptance-criteria.md
     app_type_mixins:
       web: templates/mixin-web.md
       cli: templates/mixin-cli.md
       mobile: templates/mixin-mobile.md
   ---
   ```

2. **Purpose** — Lines 12-20  
   Brief description: tool skill as instructor, source-agnostic, file-based handoff

3. **Important Notes** — Lines 22-30  
   - Read-only, no source file access
   - .checkpoint/ handoff protocol mandatory
   - program_type: skills (no runtime code)

4. **When to Use** — Lines 32-45  
   Triggers: loaded by extractor via glob, not directly invoked by humans

5. **Operations** — Lines 47-350 (bulk of SKILL.md)  
   5 XML operation blocks, each ~50-60 lines:
   - `<operation name="get_artifacts">`
   - `<operation name="get_collection_template">`
   - `<operation name="validate_section">`
   - `<operation name="get_mixin">`
   - `<operation name="pack_section">`

6. **Definition of Ready** — Lines 352-370  
   Checkpoints: artifact paths exist, .checkpoint/ folder initialized

7. **Definition of Done** — Lines 372-390  
   Checkpoints: all 8 files created, line budget met, operations tested

8. **Examples** — Lines 392-420  
   Brief example pointing to `references/examples.md`

9. **References** — Lines 422-430  
   Table linking to `references/acceptance-criteria.md` and `templates/*`

**Estimated line count:** ~430 lines (well under 500-line limit)

---

### Operation Details (XML Format)

Each operation follows this template:

```xml
<operation name="{operation_name}">
  <purpose>Brief 1-sentence purpose</purpose>
  
  <input>
    <parameter name="param1" type="string" required="true">Description</parameter>
    <parameter name="param2" type="string" required="false">Description</parameter>
  </input>
  
  <action>
    Step-by-step process:
    1. Read input parameters
    2. Load artifact from declared path
    3. Apply logic (if any)
    4. Return output
  </action>
  
  <output>
    <field name="status" type="string">success | error</field>
    <field name="result" type="object">Result structure</field>
  </output>
  
  <error_handling>
    | Error Condition | Response |
    |----------------|----------|
    | Missing artifact file | Return error with file path |
  </error_handling>
</operation>
```

#### Operation 1: get_artifacts

**Purpose:** Return all artifact paths declared in frontmatter

**Input:**
- None (reads from SKILL.md frontmatter)

**Action:**
1. Parse SKILL.md frontmatter
2. Extract `artifact_paths` section
3. Return all paths as structured YAML

**Output:**
```yaml
status: success
result:
  playbook_template: templates/playbook-base.md
  collection_template: templates/collection-template.md
  acceptance_criteria: references/acceptance-criteria.md
  app_type_mixins:
    web: templates/mixin-web.md
    cli: templates/mixin-cli.md
    mobile: templates/mixin-mobile.md
```

#### Operation 2: get_collection_template

**Purpose:** Return collection template path with optional app-type mixin merge

**Input:**
- `app_type` (optional): web | cli | mobile | none

**Action:**
1. Load base collection template from `templates/collection-template.md`
2. IF app_type provided → load corresponding mixin from `templates/mixin-{app_type}.md`
3. IF mixin exists → merge mixin prompts with base prompts (concatenate per section)
4. Write merged template to `.checkpoint/collection-template-merged.md`
5. Return file path

**Output:**
```yaml
status: success
result:
  collection_template_path: .checkpoint/collection-template-merged.md
  app_type_applied: web | cli | mobile | none
```

#### Operation 3: validate_section

**Purpose:** Validate extracted content against acceptance criteria for a specific section

**Input:**
- `section_name`: string (e.g., "Installation & Setup")
- `content_file_path`: string (path to extracted content in .checkpoint/)

**Action:**
1. Load `references/acceptance-criteria.md`
2. Find section matching `section_name`
3. Parse criteria list for that section (3-5 criteria)
4. Read content from `content_file_path`
5. For each criterion:
   - Check if criterion is satisfied (presence check, format check, completeness check)
   - Record pass/fail + feedback message
6. Return validation result

**Output:**
```yaml
status: success
result:
  section_name: "Installation & Setup"
  validation_passed: true | false
  criteria_results:
    - criterion_id: "AC-INSTALL-01"
      criterion: "Must list system prerequisites"
      passed: true
      feedback: null
    - criterion_id: "AC-INSTALL-02"
      criterion: "Must have copy-pasteable commands"
      passed: false
      feedback: "No code blocks found in content"
```

#### Operation 4: get_mixin

**Purpose:** Return app-type mixin template path

**Input:**
- `app_type`: web | cli | mobile

**Action:**
1. Validate app_type is one of: web, cli, mobile
2. IF valid → return path to `templates/mixin-{app_type}.md`
3. IF invalid → return error

**Output:**
```yaml
status: success
result:
  mixin_path: templates/mixin-web.md
  app_type: web
```

#### Operation 5: pack_section

**Purpose:** Format validated content for final output

**Input:**
- `section_name`: string
- `content_file_path`: string (path to validated content)

**Action:**
1. Read content from `content_file_path`
2. Apply formatting rules:
   - Ensure section starts with H2 heading
   - Normalize code block language tags
   - Apply cross-reference format for internal links
   - Wrap long lines at 120 characters
3. Write formatted content to `.checkpoint/{section_name}-packed.md`
4. Return packed file path

**Output:**
```yaml
status: success
result:
  packed_content_path: .checkpoint/Installation & Setup-packed.md
  section_name: "Installation & Setup"
```

---

### Template File Content Outlines

#### templates/playbook-base.md (~120 lines)

```markdown
# User Manual Playbook — Base Template

> This template defines the canonical structure of a user manual.
> Each section below describes what content belongs in that section.

## 1. Overview

**Purpose:** Introduce the application — what it does, who it's for, key value proposition.

**Content:** 2-3 paragraphs covering: purpose, target users, primary use cases, key benefits.

---

## 2. Installation & Setup

**Purpose:** Guide users through installing and configuring the application for first use.

**Content:** System prerequisites, installation steps (by platform if applicable), initial configuration, verification commands.

---

## 3. Getting Started

**Purpose:** Walk users through their first interaction with the application.

**Content:** Quickstart tutorial, "Hello World" example, basic workflow, first successful outcome.

---

## 4. Core Features

**Purpose:** Document the primary features users will interact with regularly.

**Content:** Feature descriptions, usage examples, input/output formats, common workflows.

---

## 5. Configuration

**Purpose:** Explain configuration options and customization.

**Content:** Config file locations, available options, defaults, environment variables, feature flags.

---

## 6. Troubleshooting

**Purpose:** Help users diagnose and resolve common issues.

**Content:** Common errors, diagnostic steps, resolution procedures, log locations, support contacts.

---

## 7. FAQ & Reference

**Purpose:** Answer frequently asked questions and provide quick reference material.

**Content:** FAQs, glossary, command reference, keyboard shortcuts, external resources.
```

#### templates/collection-template.md (~180 lines)

```markdown
# User Manual Collection Template

> Extraction prompts per section.
> HTML comments guide the extractor on WHERE to look and WHAT to extract.

## 1. Overview

<!-- EXTRACTION PROMPTS:
  - Search README.md, index.md, docs/index.md for introductory content
  - Look for: "What is {app_name}", "About", "Introduction" sections
  - Extract: purpose statement, target audience, key features list
  - Scan package.json/pyproject.toml for "description" field
-->

---

## 2. Installation & Setup

<!-- EXTRACTION PROMPTS:
  - Search README.md, INSTALL.md, docs/installation.md, docs/setup.md
  - Look for: "Installation", "Setup", "Getting Started", "Prerequisites"
  - Extract: system requirements, installation commands, config steps
  - Scan: Makefile, setup.py, package.json scripts, Dockerfile for install patterns
  - Check: scripts/install.*, setup.*, requirements.txt, package.json dependencies
-->

---

## 3. Getting Started

<!-- EXTRACTION PROMPTS:
  - Search README.md, docs/quickstart.md, docs/tutorial.md, TUTORIAL.md
  - Look for: "Quick Start", "Tutorial", "First Steps", "Hello World"
  - Extract: minimal working example, step-by-step first use, expected output
  - Scan: examples/, samples/, demos/ folders for starter code
-->

---

## 4. Core Features

<!-- EXTRACTION PROMPTS:
  - Search README.md, docs/features.md, docs/usage.md, USER_GUIDE.md
  - Look for: feature lists, "How to" sections, usage examples
  - Extract: feature descriptions, code examples, screenshots (if available)
  - Scan: CLI help output (--help), API documentation, source comments
-->

---

## 5. Configuration

<!-- EXTRACTION PROMPTS:
  - Search: config/, settings/, .env.example, docs/configuration.md
  - Look for: config file examples, environment variable lists, settings reference
  - Extract: config option names, defaults, descriptions, valid values
  - Scan: source code for config parsers (argparse, click, configparser, dotenv)
-->

---

## 6. Troubleshooting

<!-- EXTRACTION PROMPTS:
  - Search: TROUBLESHOOTING.md, FAQ.md, docs/troubleshooting.md, KNOWN_ISSUES.md
  - Look for: "Common Errors", "Known Issues", "Debugging", error message lists
  - Extract: error descriptions, diagnostic commands, resolution steps
  - Scan: GitHub Issues (if URL provided), changelog for bug mentions
-->

---

## 7. FAQ & Reference

<!-- EXTRACTION PROMPTS:
  - Search: FAQ.md, docs/faq.md, docs/reference.md, GLOSSARY.md
  - Look for: Q&A format, glossary terms, quick reference tables
  - Extract: frequently asked questions, definitions, command summaries
  - Scan: --help output, man pages, wiki pages (if URL provided)
-->
```

#### templates/mixin-web.md (~80 lines)

```markdown
# Web App Mixin

> Additional extraction prompts for web applications.
> These augment the base collection template.

## 4. Core Features (Web-Specific Augmentation)

<!-- WEB EXTRACTION PROMPTS:
  - Search: docs/ui.md, docs/navigation.md, screenshots/
  - Look for: UI flow diagrams, navigation structure, page descriptions
  - Extract: routes/URLs, UI element descriptions, user flows
  - Authentication: login/logout flows, session management, OAuth providers
  - Scan: frontend source for route definitions (React Router, Vue Router, etc.)
-->

## 5. Configuration (Web-Specific Augmentation)

<!-- WEB EXTRACTION PROMPTS:
  - Look for: port settings, CORS config, SSL/TLS settings, reverse proxy config
  - Extract: environment variables for web server (PORT, HOST, BASE_URL)
  - Scan: nginx.conf, apache.conf, docker-compose.yml for web server config
-->

## 6. Troubleshooting (Web-Specific Augmentation)

<!-- WEB EXTRACTION PROMPTS:
  - Look for: browser console errors, network request failures, CORS issues
  - Extract: HTTP status code meanings, auth failure scenarios
  - Check: browser dev tools usage, network tab guidance
-->
```

#### templates/mixin-cli.md (~80 lines)

```markdown
# CLI App Mixin

> Additional extraction prompts for command-line applications.
> These augment the base collection template.

## 4. Core Features (CLI-Specific Augmentation)

<!-- CLI EXTRACTION PROMPTS:
  - Search: --help output, man pages, docs/commands.md, docs/cli.md
  - Look for: command syntax, subcommand lists, flag descriptions
  - Extract: command examples with flags, argument descriptions, exit codes
  - Scan: argparse, click, commander.js, clap definitions in source code
  - Shell completion: look for completion scripts (bash, zsh, fish)
-->

## 5. Configuration (CLI-Specific Augmentation)

<!-- CLI EXTRACTION PROMPTS:
  - Look for: config file paths (~/.{app}rc, ~/.config/{app}/), CLI flag overrides
  - Extract: config file format (YAML, TOML, JSON), precedence rules
  - Scan: XDG_CONFIG_HOME usage, platform-specific config locations
-->

## 6. Troubleshooting (CLI-Specific Augmentation)

<!-- CLI EXTRACTION PROMPTS:
  - Look for: verbose/debug flags (-v, --debug), log file locations
  - Extract: common exit codes, error message formats
  - Scan: --version output, diagnostic commands
-->
```

#### templates/mixin-mobile.md (~80 lines)

```markdown
# Mobile App Mixin

> Additional extraction prompts for mobile applications.
> These augment the base collection template.

## 2. Installation & Setup (Mobile-Specific Augmentation)

<!-- MOBILE EXTRACTION PROMPTS:
  - Look for: App Store/Play Store links, minimum OS version, device requirements
  - Extract: permissions required (camera, location, notifications), download size
  - Scan: Info.plist (iOS), AndroidManifest.xml (Android) for permissions
-->

## 4. Core Features (Mobile-Specific Augmentation)

<!-- MOBILE EXTRACTION PROMPTS:
  - Look for: gesture controls (swipe, pinch, long-press), touch interactions
  - Extract: screen-specific features (home screen, detail view, settings)
  - Scan: screenshots for UI elements, navigation patterns
  - Platform differences: iOS vs Android feature parity, platform-specific features
-->

## 6. Troubleshooting (Mobile-Specific Augmentation)

<!-- MOBILE EXTRACTION PROMPTS:
  - Look for: crash logs, memory issues, background task failures
  - Extract: permission troubleshooting, offline mode issues
  - Platform-specific: App Store rejection reasons, Play Store review guidelines
-->
```

#### references/acceptance-criteria.md (~150 lines)

```markdown
# Acceptance Criteria — User Manual Sections

> Per-section validation rules for the extract-validate loop.
> Each criterion is binary: pass or fail.

## 1. Overview

| Criterion ID | Criterion | Validation Logic |
|--------------|-----------|------------------|
| AC-OVERVIEW-01 | Must include a purpose statement (what the app does) | Check for non-empty paragraph after heading |
| AC-OVERVIEW-02 | Must identify target users or use cases | Check for "users", "for", "use case" keywords |
| AC-OVERVIEW-03 | Must list 2-3 key features or benefits | Check for list or enumeration with ≥2 items |

## 2. Installation & Setup

| Criterion ID | Criterion | Validation Logic |
|--------------|-----------|------------------|
| AC-INSTALL-01 | Must list system prerequisites with version requirements | Check for "prerequisites", "requires", version numbers |
| AC-INSTALL-02 | Must have copy-pasteable installation commands | Check for code blocks with shell/bash language tag |
| AC-INSTALL-03 | Must include a verification step (how to confirm install worked) | Check for "verify", "test install", or command with expected output |
| AC-INSTALL-04 | Must specify supported platforms (if applicable) | Check for OS mentions: Linux, macOS, Windows, or "all platforms" |

## 3. Getting Started

| Criterion ID | Criterion | Validation Logic |
|--------------|-----------|------------------|
| AC-START-01 | Must provide a minimal working example | Check for code block or step-by-step procedure |
| AC-START-02 | Must show expected output or success indicator | Check for "output", "result", "you should see" |
| AC-START-03 | Must be completable in <5 minutes | Heuristic: ≤10 steps, ≤50 lines of code |

## 4. Core Features

| Criterion ID | Criterion | Validation Logic |
|--------------|-----------|------------------|
| AC-FEATURE-01 | Must document at least 3 core features | Check for ≥3 subsections or feature descriptions |
| AC-FEATURE-02 | Each feature must have a usage example | Check for code block or command per feature |
| AC-FEATURE-03 | Must specify inputs and outputs for each feature | Check for "input", "output", "parameters" keywords |

## 5. Configuration

| Criterion ID | Criterion | Validation Logic |
|--------------|-----------|------------------|
| AC-CONFIG-01 | Must specify config file location or environment variables | Check for file paths or VAR=value patterns |
| AC-CONFIG-02 | Must list available config options with defaults | Check for table or list with option names + default values |
| AC-CONFIG-03 | Must explain how to reload/apply config changes | Check for restart command, reload signal, or dynamic reload mention |

## 6. Troubleshooting

| Criterion ID | Criterion | Validation Logic |
|--------------|-----------|------------------|
| AC-TROUBLE-01 | Must document at least 3 common errors or issues | Check for ≥3 error scenarios or FAQ entries |
| AC-TROUBLE-02 | Each issue must have a resolution or workaround | Check for "solution", "fix", "workaround" per issue |
| AC-TROUBLE-03 | Must specify where to find logs or diagnostic output | Check for log file paths or diagnostic commands |

## 7. FAQ & Reference

| Criterion ID | Criterion | Validation Logic |
|--------------|-----------|------------------|
| AC-FAQ-01 | Must have at least 5 frequently asked questions | Check for ≥5 Q&A pairs or FAQ entries |
| AC-FAQ-02 | Must include links to external resources or support channels | Check for URLs, email addresses, or community links |
| AC-FAQ-03 | Must provide a glossary or command reference (if applicable) | Check for definition list or reference table |
```

#### references/examples.md (~80 lines)

```markdown
# Examples — Tool Skill Usage

## Example 1: Extractor Discovers and Loads Skill

```yaml
# Extractor globs .github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md
# Finds: x-ipe-tool-knowledge-extraction-user-manual

# Extractor loads SKILL.md frontmatter
categories: ["user-manual"]
artifact_paths:
  playbook_template: templates/playbook-base.md
  collection_template: templates/collection-template.md
  acceptance_criteria: references/acceptance-criteria.md
  app_type_mixins:
    web: templates/mixin-web.md
    cli: templates/mixin-cli.md
    mobile: templates/mixin-mobile.md

# Extractor calls: get_artifacts()
# Returns: all artifact paths
```

## Example 2: Extractor Requests Collection Template with Web Mixin

```yaml
# Extractor detected app_type: web (Flask application)

# Extractor calls: get_collection_template(app_type="web")
# Action:
#   1. Load templates/collection-template.md
#   2. Load templates/mixin-web.md
#   3. Merge: base prompts + web-specific prompts per section
#   4. Write merged template to .checkpoint/collection-template-merged.md

# Returns:
status: success
result:
  collection_template_path: .checkpoint/collection-template-merged.md
  app_type_applied: web
```

## Example 3: Extractor Validates Extracted Content

```yaml
# Extractor extracted content for "Installation & Setup" section
# Content written to .checkpoint/section-installation-extracted.md

# Extractor calls: validate_section(
#   section_name="Installation & Setup",
#   content_file_path=".checkpoint/section-installation-extracted.md"
# )

# Action:
#   1. Load references/acceptance-criteria.md
#   2. Find "Installation & Setup" section (4 criteria)
#   3. Read content from .checkpoint/section-installation-extracted.md
#   4. Check each criterion:
#      - AC-INSTALL-01: system prerequisites → PASS
#      - AC-INSTALL-02: copy-pasteable commands → FAIL (no code blocks)
#      - AC-INSTALL-03: verification step → PASS
#      - AC-INSTALL-04: supported platforms → PASS

# Returns:
status: success
result:
  section_name: "Installation & Setup"
  validation_passed: false
  criteria_results:
    - criterion_id: "AC-INSTALL-01"
      criterion: "Must list system prerequisites"
      passed: true
      feedback: null
    - criterion_id: "AC-INSTALL-02"
      criterion: "Must have copy-pasteable commands"
      passed: false
      feedback: "No code blocks found. Add shell commands in fenced code blocks."
    - criterion_id: "AC-INSTALL-03"
      criterion: "Must include verification step"
      passed: true
      feedback: null
    - criterion_id: "AC-INSTALL-04"
      criterion: "Must specify supported platforms"
      passed: true
      feedback: null

# Extractor sees validation_passed: false
# → Extractor enters Phase 3 loop: re-extract Installation section focusing on code examples
# → Extractor calls validate_section again
# → Loop continues until validation_passed: true
```

---

## Example 4: Full Workflow Integration

```
1. Extractor (EPIC-050) starts with target="/path/to/flask-app", purpose="user-manual"
2. Extractor globs and discovers x-ipe-tool-knowledge-extraction-user-manual
3. Extractor calls: get_artifacts() → receives all artifact paths
4. Extractor calls: get_collection_template(app_type="web") → receives merged template
5. Extractor reads merged template, sees 7 sections with extraction prompts
6. FOR EACH section (1-7):
   a. Extractor reads source files based on prompts (README, docs/, source code)
   b. Extractor writes extracted content to .checkpoint/section-{name}-extracted.md
   c. Extractor calls: validate_section(section_name, content_file_path)
   d. IF validation fails → extractor loops back to step 6a with feedback
   e. IF validation passes → extractor calls: pack_section(section_name, content_file_path)
7. Extractor assembles all packed sections into final user manual
8. Extractor writes final output to x-ipe-docs/knowledge-base/.intake/user-manual-{app_name}.md
```

---

### Implementation Sequence

**Order of file creation (recommended):**

1. **Create folder structure:** `.github/skills/x-ipe-tool-knowledge-extraction-user-manual/` with `references/` and `templates/` subfolders

2. **Write templates first** (easiest to validate independently):
   - `templates/playbook-base.md` — 7 sections with headings + descriptions
   - `templates/collection-template.md` — 7 sections with HTML comment prompts
   - `templates/mixin-web.md` — web-specific prompts
   - `templates/mixin-cli.md` — CLI-specific prompts
   - `templates/mixin-mobile.md` — mobile-specific prompts

3. **Write references:**
   - `references/acceptance-criteria.md` — 7 sections with 3-5 criteria each
   - `references/examples.md` — 3-4 usage examples

4. **Write SKILL.md last** (references all other files):
   - Frontmatter with categories + artifact paths
   - Purpose, Important Notes, When to Use
   - 5 operations in XML format
   - DoR/DoD
   - References table

5. **Validate:**
   - Check SKILL.md line count ≤ 500
   - Verify all artifact paths resolve correctly
   - Confirm 7-section structure is consistent across playbook, collection template, and acceptance criteria
   - Test mixin merge logic (base + mixin should concatenate cleanly)

---

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| 7 sections canonical for v1 | Balances completeness with simplicity; covers essential user manual content |
| HTML comments for prompts | Keeps prompts close to section content; doesn't interfere with rendering |
| 3-5 criteria per section | Enough to ensure quality, not so many as to make validation slow |
| File-based handoff mandatory | Prevents context overflow on large codebases; enforces clean interfaces |
| App-type mixins augment (not replace) | Preserves base template as fallback; allows graceful degradation for unknown types |
| Operations in XML format | Consistent with X-IPE tool skill template; machine-parseable; human-readable |
| program_type: skills | No runtime code needed; pure template/reference system |
| Delivered via skill-creator | Enforces validation, changelog, candidate workflow for production merge |

---

### Line Budget Enforcement

**Target:** SKILL.md ≤ 500 lines

**Strategy:**
- Frontmatter: ~15 lines
- Purpose/Notes/When to Use: ~30 lines
- 5 operations × 50 lines each: ~250 lines
- DoR/DoD: ~40 lines
- Examples (brief, point to references/examples.md): ~20 lines
- References table: ~10 lines
- **Total:** ~365 lines (leaves 135-line buffer)

**Enforcement:** If SKILL.md exceeds 500 lines during implementation, move content to:
- Detailed operation logic → `references/operation-details.md`
- Extended examples → `references/examples.md`
- Keep only operation signatures and brief descriptions in SKILL.md

---

### Edge Case Handling Summary

| Edge Case | Design Response |
|-----------|----------------|
| Extractor requests unsupported mixin | Return error: "Unsupported app_type. Supported: web, cli, mobile" |
| Section name typo in validate_section call | Return error: "Section '{name}' not found in acceptance criteria" |
| .checkpoint/ folder missing | Return error: "Handoff protocol requires .checkpoint/ folder" |
| Content file path does not exist | Return error: "Content file not found: {path}" |
| Playbook/collection template section mismatch | Fail DoR check during skill creation |
| Multiple tool skills for same category | Extractor takes first alphabetical match (defined in EPIC-050 design) |

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 03-17-2026 | Initial Design | Initial technical design for user manual tool skill. Defines 8-file structure (SKILL.md + 2 references + 5 templates), 5 operations (get_artifacts, get_collection_template, validate_section, get_mixin, pack_section), 7-section canonical structure, app-type mixins, acceptance criteria per section, file-based handoff protocol. Line budget: SKILL.md ≤ 500 lines. Delivery via x-ipe-meta-skill-creator candidate workflow. |
