# Examples — Knowledge Extraction User Manual Tool

## Example 1: Extractor Loading This Skill for a Web App

**Scenario:** The Application Knowledge Extractor receives a request to extract a user manual from a web application source code repository.

### Step 1 — Extractor discovers and loads the tool skill

```yaml
# Extractor Step 1.3: Load Tool Skill
glob_pattern: ".github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md"
filter: categories contains "user-manual"
match: x-ipe-tool-knowledge-extraction-user-manual
```

### Step 2 — Extractor calls `get_artifacts`

```yaml
# Input
operation: get_artifacts
category: user-manual

# Output
operation_output:
  success: true
  operation: get_artifacts
  result:
    artifact_paths:
      playbook_template: "templates/playbook-template.md"
      collection_template: "templates/collection-template.md"
      acceptance_criteria: "templates/acceptance-criteria.md"
      app_type_mixins:
        web: "templates/mixin-web.md"
        cli: "templates/mixin-cli.md"
        mobile: "templates/mixin-mobile.md"
    config_defaults:
      web_search_enabled: false
      max_files_per_section: 20
```

### Step 3 — Extractor calls `get_mixin` for the web app type

```yaml
# Input
operation: get_mixin
app_type: web

# Output
operation_output:
  success: true
  operation: get_mixin
  result:
    # Returns content of templates/mixin-web.md
    # Includes additional sections: Authentication, Navigation, Browser Requirements, API Endpoints
    # Extractor merges these into the base playbook template
```

### Step 4 — Extractor calls `get_collection_template` for each section

```yaml
# Input (for one section)
operation: get_collection_template
section_id: "2-installation-setup"

# Output
operation_output:
  success: true
  operation: get_collection_template
  result:
    # Returns the Section 2 block from collection-template.md with extraction prompts:
    # - What are the system prerequisites?
    # - What are the install commands?
    # - How to verify installation?
    # Plus web mixin overlay prompts:
    # - What is the application URL?
    # - Is there a self-hosted option?
```

---

## Example 2: Extractor Validating a Section Against Acceptance Criteria

**Scenario:** The extractor has extracted content for Section 2 (Installation & Setup) and needs to validate it before packing.

### Step 1 — Extractor calls `validate_section`

```yaml
# Input
operation: validate_section
section_id: "2-installation-setup"
content_path: ".checkpoint/session-20260317/content/section-02-installation-setup.md"

# Extracted content at that path:
# ## Installation & Setup
# ### Prerequisites
# - Node.js 18+ (LTS recommended)
# - npm 9+ or yarn 1.22+
# ### Installation
# ```bash
# git clone https://github.com/example/app.git
# cd app
# npm install
# ```
# ### Verification
# ```bash
# npm run dev
# # Expected: Server running at http://localhost:3000
# ```
```

### Step 2 — Tool skill evaluates criteria

```yaml
# Output
operation_output:
  success: true
  operation: validate_section
  result:
    validation_result:
      section_id: "2-installation-setup"
      passed: true
      criteria:
        - id: "REQ-1"
          status: "pass"
          feedback: "Prerequisites listed with version requirements (Node.js 18+, npm 9+)"
        - id: "REQ-2"
          status: "pass"
          feedback: "Install commands are copy-pasteable (git clone, cd, npm install)"
        - id: "REQ-3"
          status: "pass"
          feedback: "Verification step included (npm run dev with expected output)"
        - id: "OPT-1"
          status: "fail"
          feedback: "No Docker setup documented — consider adding if Dockerfile exists"
        - id: "OPT-2"
          status: "fail"
          feedback: "No initial configuration section — check for .env.example"
```

### Step 3 — Extractor calls `pack_section` for the validated content

```yaml
# Input
operation: pack_section
section_id: "2-installation-setup"
content_path: ".checkpoint/session-20260317/content/section-02-installation-setup.md"

# Output
operation_output:
  success: true
  operation: pack_section
  result:
    formatted_content: |
      ## 2. Installation & Setup

      ### Prerequisites

      - **Node.js** 18+ (LTS recommended)
      - **npm** 9+ or **yarn** 1.22+

      ### Installation

      ```bash
      git clone https://github.com/example/app.git
      cd app
      npm install
      ```

      ### Verification

      ```bash
      npm run dev
      # Expected: Server running at http://localhost:3000
      ```
```
