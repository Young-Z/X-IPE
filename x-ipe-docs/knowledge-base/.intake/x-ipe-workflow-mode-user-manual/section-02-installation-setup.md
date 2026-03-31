# 2. Installation & Setup

## System Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python** | 3.12 or higher |
| **Package Manager** | `uv` (recommended) or `pip` |
| **AI CLI Tool** | One of: GitHub Copilot CLI, Claude Code (`claude`), or OpenCode (`opencode`) |
| **AI Model** | Claude Sonnet 4.5+ or Gemini 2.5 Flash+ (must support tools/skills) |
| **Operating System** | macOS, Linux, or Windows (with WSL) |
| **Browser** | Modern browser with JavaScript and WebSocket support (Chrome, Firefox, Safari, Edge) |

### Browser Requirements

- JavaScript enabled
- WebSocket support (for real-time terminal communication)
- Cookies enabled (for session management)
- Recommended: Chrome or Firefox (latest version)

## Installation Methods

### Option 1: PyPI Install (Recommended)

```bash
# Using uv (fastest)
uv tool install x-ipe

# Or using pip
pip install x-ipe
```

### Option 2: From Source

```bash
# Clone the repository
git clone https://github.com/user/X-IPE.git
cd X-IPE

# Install with development dependencies
uv sync
# Or
pip install -e ".[dev]"
```

## Initial Configuration

### Step 1: Initialize Project Structure

Run the init command to create the required directory structure:

```bash
x-ipe init [--project /path/to/your/project]
```

This creates:
```
your-project/
├── x-ipe-docs/
│   ├── config/              # Settings and environment
│   │   └── .env             # API keys (optional)
│   └── engineering-workflow/ # Workflow state files
├── .x-ipe.yaml              # Project configuration (optional)
└── .github/
    └── copilot/
        └── instructions.md  # Copilot custom instructions
```

### Step 2: Configure Project (Optional)

Create or edit `.x-ipe.yaml` in your project root:

```yaml
version: 1
paths:
  project_root: "."
  x_ipe_app: "./x-ipe"
defaults:
  file_tree_scope: "project_root"
  terminal_cwd: "project_root"
server:
  host: "127.0.0.1"
  port: 5858
  debug: true
```

### Step 3: Configure Environment Variables (Optional)

Copy and edit the environment file for optional features like voice recognition:

```bash
cp x-ipe-docs/config/.env.example x-ipe-docs/config/.env
```

Available environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ALIBABA_SPEECH_API_KEY` | Voice recognition API key | (none) |
| `VOICE_TRANSLATION` | Enable voice translation | `false` |
| `VOICE_TRANSLATION_TARGET` | Translation target language | (none) |
| `PROJECT_ROOT` | Default project path | Current directory |

## Starting the Application

```bash
# Start the X-IPE server
x-ipe serve

# With options
x-ipe serve --host 127.0.0.1 --port 5858 --debug --open
```

**Command-line flags:**

| Flag | Description | Default |
|------|-------------|---------|
| `--host` | Server host address | `127.0.0.1` |
| `--port` | Server port | `5858` |
| `--debug` | Enable debug mode with verbose logging | `false` |
| `--open` | Auto-open browser after start | `false` |

**Alternative start methods:**

```bash
# Direct Python module execution
python -m x_ipe

# From source
python src/x_ipe/app.py
```

## Verifying Installation

1. **Start the server**: Run `x-ipe serve`
2. **Open browser**: Navigate to `http://127.0.0.1:5858`
3. **Check console**: The bottom status bar should show "Console: Connected" (green)
4. **Verify mode toggle**: You should see the "FREE / WORKFLOW" toggle in the header bar

If the console shows "Disconnected", ensure your AI CLI tool is running in a compatible terminal.

## Application URL

- **Default**: `http://127.0.0.1:5858`
- **Custom**: Set via `--port` flag or `.x-ipe.yaml` server configuration
