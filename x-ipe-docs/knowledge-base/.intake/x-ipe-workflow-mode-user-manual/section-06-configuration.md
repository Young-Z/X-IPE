# 6. Configuration & Settings

## Settings Page

**URL:** `http://127.0.0.1:5858/settings` or click **"⚙ Settings"** in the header bar.

![Settings Page](screenshots/06-configuration-settings-page.png)

The Settings page provides the following configuration options:

---

## Language

**Location:** Settings → Language section

| Setting | Description |
|---------|-------------|
| **Interface Language** | Controls copilot instructions and prompt display language |
| **Options** | English, 中文 (Chinese) |
| **Default** | English |

**How to change:**
1. Open Settings
2. Find the **"Interface Language"** dropdown
3. Select your preferred language (English or 中文)
4. The change takes effect immediately

**Note:** "Instructions will be regenerated. Custom edits outside X-IPE sections are preserved." — Changing the language regenerates the `.github/copilot/instructions.md` file while preserving any custom sections you've added.

---

## DAO Message Interception

**Location:** Settings → DAO Message Interception section

| Setting | Description |
|---------|-------------|
| **Enable DAO as message interceptor** | Toggle switch (On/Off) |
| **Default** | Off |

**What it does:**
- **When ON:** Every user message is processed through the DAO human representative skill before the agent acts. The DAO acts as an intermediary for all interactions.
- **When OFF:** The agent classifies requests directly into skills without DAO intermediation.
- **Note:** DAO within-skill interaction (controlled by the per-workflow Interaction Mode setting) is unaffected by this toggle.

**When to enable:**
- When you want consistent DAO mediation across all interactions
- When working in teams where consistent decision-making is important

**Warning:** "Toggling this will regenerate the copilot instructions file for the active project."

---

## Project Folders

**Location:** Settings → Project Folders section

This section manages which project directories X-IPE monitors.

| Column | Description |
|--------|-------------|
| **Name** | Display name for the project (e.g., "Default Project Folder") |
| **Path** | Filesystem path (e.g., `.` for current directory) |
| **Actions** | Edit button (✏️) to modify project settings |
| **Active** | Badge indicating the currently active project |

**How to add a project:**
1. Click **"➕ Add Project"**
2. Enter the project name and filesystem path
3. Save

**How to edit a project:**
1. Click the **✏️** edit button next to the project
2. Modify the name or path
3. Save

---

## Project Configuration (Read-Only)

**Location:** Settings → Project Configuration section

Displays detected configuration for the active project:

| Field | Description | Example |
|-------|-------------|---------|
| **Config file** | Source of configuration | `package-defaults` |
| **Version** | Config version | `1` |
| **Project Root** | Absolute path to project | `/Users/yzhang/Documents/projects/X-IPE` |
| **X-IPE App** | Path to X-IPE application | `/Users/yzhang/Documents/projects/X-IPE` |
| **File Tree Scope** | Which directory the file browser shows | `project_root` |
| **Terminal CWD** | Working directory for terminal commands | `project_root` |

---

## Configuration File: `.x-ipe.yaml`

The primary configuration file lives at the project root:

```yaml
version: 1
paths:
  project_root: "."          # Root directory for project files
  x_ipe_app: "./x-ipe"       # X-IPE application directory
defaults:
  file_tree_scope: "project_root"  # File browser scope
  terminal_cwd: "project_root"     # Terminal working directory
server:
  host: "127.0.0.1"          # Server bind address
  port: 5858                  # Server port
  debug: true                 # Debug mode (verbose logging)
```

**Scope options:**
- `project_root` — Shows/operates from the project root directory
- `x_ipe_app` — Shows/operates from the X-IPE application directory only

---

## Environment Variables (`.env`)

Located at `x-ipe-docs/config/.env`:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ALIBABA_SPEECH_API_KEY` | API key for voice recognition | No | (none) |
| `VOICE_TRANSLATION` | Enable voice input translation | No | `false` |
| `VOICE_TRANSLATION_TARGET` | Target language for translation | No | (none) |
| `PROJECT_ROOT` | Override project root path | No | Current directory |
| `SECRET_KEY` | Flask secret key | No | `dev-secret-key-change-in-production` |

---

## Workflow Template Configuration

Located at `x-ipe-docs/config/workflow-template.json` or bundled in `src/x_ipe/resources/config/workflow-template.json`:

This file defines the structure of workflow stages, available actions per stage, which actions are mandatory vs optional, and deliverable tag templates. It is used when creating new workflows to establish the initial state.

---

## API Endpoints for Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/settings` | Retrieve current settings |
| `POST` | `/api/settings` | Save settings (project root, preferences) |
| `POST` | `/api/settings/language` | Change interface language |
| `PATCH` | `/api/workflow/{name}/settings` | Update per-workflow settings (interaction mode) |
