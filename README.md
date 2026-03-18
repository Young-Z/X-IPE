# X-IPE

> **The world first AI-native Integrated Project Environment (IPE) for end-to-end business value delivery.**

```
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║   ██╗  ██╗      ██╗██████╗ ███████╗                               ║
    ║   ╚██╗██╔╝      ██║██╔══██╗██╔════╝                               ║
    ║    ╚███╔╝ █████╗██║██████╔╝█████╗                                 ║
    ║    ██╔██╗ ╚════╝██║██╔═══╝ ██╔══╝                                 ║
    ║   ██╔╝ ██╗      ██║██║     ███████╗                               ║
    ║   ╚═╝  ╚═╝      ╚═╝╚═╝     ╚══════╝                               ║
    ║                                                                   ║
    ║          From Idea to Delivery, Powered by AI Agents              ║
    ╚═══════════════════════════════════════════════════════════════════╝
```

---

## 📑 Contents

- [💡 What is X-IPE?](#-what-is-x-ipe)
- [🚀 Getting Started](#-getting-started)
- [🎯 The Vision](#-the-vision)
- [📚 Part of a Larger Journey](#-part-of-a-larger-journey)
- [🔄 How I Build This Application, How We Build Others](#-how-i-build-this-application-how-we-build-others)
- [✨ Features](#-features)
- [🛠️ Technology Stack](#️-technology-stack)
- [📁 Project Structure](#-project-structure)
- [📖 Documentation](#-documentation)
- [📋 Version Changelog](#-version-changelog)
- [📄 License](#-license)

---

## 💡 What is X-IPE?

<img src="resources/X-IPE%20home.png" alt="X-IPE Home" width="600">

**X-IPE (Integrated Project Environment)** is a demonstration of this mindset shift—from code-centric to value-centric software delivery in AI age.

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         X - I P E                                                 │
│                          Integrated Project Environment                                           │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                   │
│   ┌─────────────────────────────────────────────────────────────────────────────────────────┐     │
│   │                        👤 HUMAN-FACING LAYER (What You See)                             │     │
│   ├─────────────────────────────────────────────────────────────────────────────────────────┤     │
│   │                                                                                         │     │
│   │    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │     │
│   │    │  💡 Ideas   │    │  📋 Review   │    │  ✅ Approve │    │  🎮 Test &  │             │     │
│   │    │   Capture   │ ─▶ │  & Feedback │ ─▶ │  & Confirm  │ ─▶ │  Validate   │             │     │
│   │    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘             │     │
│   │                                                                                         │     │
│   │    Human Focus: Creative thinking │ Strategic decisions │ Quality gates │ Feedback      │     │
│   └─────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                           │                                                       │
│                                           │ 🔄 Feedback Loop                                      │
│                                           │ (Transparency)                                        │
│                                           ▼                                                       │
│   ┌─────────────────────────────────────────────────────────────────────────────────────────┐     │
│   │                     🤖 AI LAYER (Behind the Scenes)                                     │     │
│   ├─────────────────────────────────────────────────────────────────────────────────────────┤     │
│   │                                                                                         │     │
│   │  ┌────────────────────────────────────────────────────────────────────────────────┐     │     │
│   │  │                         🎯 MAIN AGENT (Orchestrator)                           │     │     │
│   │  │     Understands intent │ Plans tasks │ Coordinates workflow │ Reports status   │     │     │
│   │  └────────────────────────────────────────────────────────────────────────────────┘     │     │
│   │                                           │                                             │     │
│   │              ┌────────────────────────────┼────────────────────────────┐                │     │
│   │              │                            │                            │                │     │
│   │              ▼                            ▼                            ▼                │     │
│   │  ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐             │     │
│   │  │  📝 Requirement  │       │  🏗️ Design &      │       │  💻 Code &       │             │     │
│   │  │     Sub-Agent    │       │  Test Sub-Agent  │       │  Docs Sub-Agent  │             │     │
│   │  ├──────────────────┤       ├──────────────────┤       ├──────────────────┤             │     │
│   │  │ • Breakdown      │       │ • Tech Design    │       │ • Implementation │             │     │
│   │  │ • Refinement     │       │ • Test Gen       │       │ • Documentation  │             │     │
│   │  │ • Specification  │       │ • Architecture   │       │ • PR Creation    │             │     │
│   │  └──────────────────┘       └──────────────────┘       └──────────────────┘             │     │
│   │                                                                                         │     │
│   │  ═══════════════════════════════════════════════════════════════════════════════════    │     │
│   │  📚 SKILLS LIBRARY: x-ipe-workflow-task-execution │ feature-board-management │ etc.     │     │
│   │  ═══════════════════════════════════════════════════════════════════════════════════    │     │
│   └─────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                           │                                                       │
│                                           ▼                                                       │
│   ┌─────────────────────────────────────────────────────────────────────────────────────────┐     │
│   │                          📦 ARTIFACTS (Transparent & Traceable)                         │     │
│   ├─────────────────────────────────────────────────────────────────────────────────────────┤     │
│   │                                                                                         │     │
│   │    ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │     │
│   │    │  📋 Task   │  │  🎯 Feature │  │  📄 Specs  │  │  🏗️ Tech   │  │  💻 Code    │       │     │
│   │    │   Board    │  │   Board    │  │  & Docs    │  │  Designs   │  │  & Tests   │       │     │
│   │    └────────────┘  └────────────┘  └────────────┘  └────────────┘  └────────────┘       │     │
│   │                                                                                         │     │
│   │    All artifacts visible │ Version controlled │ Human can review any time               │     │
│   └─────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Principles (Inspired by DevOps and Agile)

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                   │
│   🔄 TRANSPARENCY              🔁 FEEDBACK LOOPS           👥 COLLABORATION                        │
│   ─────────────────            ──────────────────          ─────────────────                      │
│                                                                                                   │
│   • All AI work is visible     • Human reviews at each     • Human: Strategy &                    │
│   • Task board shows progress    stage gate                  Decisions                            │
│   • Feature board tracks       • Approve before moving     • AI: Execution &                      │
│     lifecycle                    to next phase               Documentation                        │
│   • Artifacts are traceable    • Feedback shapes next      • Clear handoff points                 │
│                                  iteration                                                        │
│                                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Transparency** — All AI-generated work is visible and auditable (task board, feature board, specs, designs)
2. **Feedback Loops** — Human review gates at each stage; approve before advancing
3. **Value-Centric** — Focus on business outcomes, not just code output
4. **AI-Human Collaboration** — Humans guide strategy; AI agents execute implementation
5. **End-to-End Orchestration** — Manage the complete journey from idea to delivery

* I will share more details in the upcoming blog series on mindset shifts, process changes, and tool evolution needed to thrive in the AI age of software delivery.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- A supported AI coding CLI (at least one):
  - [GitHub Copilot CLI](https://docs.github.com/en/copilot) (`copilot`)
  - [OpenCode](https://opencode.ai) (`opencode`)
  - [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (`claude`)
- AI model with skills/tools capability (Claude Sonnet 4.5+, Gemini 2.5 Flash+, etc.)

### Installation

#### Option 1: Install from PyPI (Recommended)

```bash
# Install X-IPE using uv
uv tool install x-ipe

# Or using pip
pip install x-ipe
```

#### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/pinkpixel-dev/X-IPE.git
cd X-IPE

# Install with uv
uv sync
```

### Quick Start

```bash
# Initialize X-IPE in your project
cd your-project
x-ipe init

# Check project status
x-ipe status

# Start the web server
x-ipe serve

# Start server and open browser
x-ipe serve -o
```

### CLI Commands

```bash
x-ipe --help          # Show all available commands
x-ipe --version       # Show version
x-ipe init            # Initialize X-IPE (auto-detects CLI, prompts for selection)
x-ipe init --cli copilot  # Initialize with a specific CLI
x-ipe init --dry-run  # Preview what would be created
x-ipe status          # Show project initialization status
x-ipe info            # Show X-IPE package information
x-ipe serve           # Start the web server
x-ipe serve -o        # Start server and open browser
x-ipe upgrade         # Upgrade skills (prompts for CLI selection)
x-ipe upgrade --cli opencode  # Switch to a different CLI (backs up old, deploys new)
```

### Multi-CLI Support

X-IPE supports multiple AI coding CLIs. During `init` and `upgrade`, you'll be prompted to select your CLI:

```bash
# Initialize — auto-detects installed CLIs, prompts for selection
x-ipe init
# > Detected CLI(s): copilot, opencode
# > Select CLI (copilot, opencode, claude-code) [copilot]:

# Switch CLI — backs up old artifacts, deploys for new CLI
x-ipe upgrade --cli opencode
# > Migrating from 'copilot' to 'opencode'
# > Backed up 2 artifact(s) to .x-ipe/backup/copilot-20260207-153300/
# > Updated .x-ipe.yaml: cli → opencode
# > ✓ Migration complete: copilot → opencode
```

Each CLI gets its own:
- **Skills folder** — `.github/skills/` (Copilot), `.opencode/skills/` (OpenCode), `.claude/skills/` (Claude Code)
- **Instructions file** — `copilot-instructions.md`, `.opencode/instructions.md`, `.claude/instructions.md`
- **MCP config** — `~/.copilot/mcp-config.json` (global), `opencode.json` (project), `.mcp.json` (project)

### Running from Source

```bash
# Run the application
uv run python -m x_ipe.app

# Open in browser
# http://localhost:5858

# Run tests
uv run pytest tests/ -v
```

### Running as a Subfolder in Your Project

X-IPE can run as a subfolder within a larger project, allowing you to view your entire project structure while keeping X-IPE isolated. This is useful when X-IPE is a tool within a bigger codebase.

**Setup:**

1. Place X-IPE in a subfolder of your project:
   ```
   my-project/
   ├── .x-ipe.yaml          # Config file at project root
   ├── src/                  # Your project source
   ├── x-ipe-docs/                 # Your project docs
   └── x-ipe/                # X-IPE application folder
       ├── src/
       ├── x-ipe-docs/
       └── ...
   ```

2. Create `.x-ipe.yaml` at your project root:
   ```yaml
   # .x-ipe.yaml
   version: 1
   paths:
     project_root: "."       # Relative to this config file
     x_ipe_app: "./x-ipe"    # Path to X-IPE folder
   defaults:
     file_tree_scope: "project_root"   # Show entire project in file tree
     terminal_cwd: "project_root"      # Terminal starts at project root
   ```

3. Run X-IPE from **anywhere** in your project:
   ```bash
   # From project root
   cd my-project
   uv run --directory x-ipe python -m x_ipe.app

   # Or from X-IPE folder
   cd my-project/x-ipe
   uv run python -m x_ipe.app
   ```

X-IPE will automatically discover `.x-ipe.yaml` by searching the current directory and up to 20 parent directories.

**Config Options:**

| Field | Description | Required |
|-------|-------------|----------|
| `version` | Config version (always `1`) | Yes |
| `paths.project_root` | Path to your project root (relative to config) | Yes |
| `paths.x_ipe_app` | Path to X-IPE folder (relative to config) | Yes |
| `defaults.file_tree_scope` | `"project_root"` or `"x_ipe_app"` (default: `"project_root"`) | No |
| `defaults.terminal_cwd` | `"project_root"` or `"x_ipe_app"` (default: `"project_root"`) | No |

**Without `.x-ipe.yaml`:** X-IPE works exactly as before—file tree shows the X-IPE folder, terminal starts in the X-IPE directory.

---

### Application Action Tracing

X-IPE includes a built-in tracing system to monitor function calls, parameters, return values, and execution times.

**Using the Decorator:**

```python
from x_ipe.tracing import x_ipe_tracing

@x_ipe_tracing(name="process_order", level="info")
def process_order(order_id: str, items: list):
    # Your function logic
    return {"status": "completed", "order_id": order_id}

# Async functions are also supported
@x_ipe_tracing(name="fetch_data", redact=["api_key"])
async def fetch_data(api_key: str, endpoint: str):
    # Sensitive fields are automatically redacted
    pass
```

**Tracing API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tracing/status` | GET | Get current tracing configuration |
| `/api/tracing/start` | POST | Start tracing for 3, 15, or 30 minutes |
| `/api/tracing/stop` | POST | Stop tracing immediately |
| `/api/tracing/logs` | GET | List all trace log files |
| `/api/tracing/logs` | DELETE | Delete all trace logs |

**Starting Tracing via API:**

```bash
# Start 15-minute tracing session
curl -X POST http://localhost:5858/api/tracing/start \
  -H "Content-Type: application/json" \
  -d '{"duration_minutes": 15}'

# Check status
curl http://localhost:5858/api/tracing/status
```

**Features:**
- Automatic sensitive data redaction (passwords, tokens, credit cards, JWTs)
- Async-safe context propagation
- Duration-based tracing (3/15/30 minutes)
- JSON log files with automatic 24-hour cleanup

**Tracing Dashboard UI:**

The Tracing Dashboard provides a visual interface for managing tracing sessions directly from the X-IPE Workplace:

1. **Access:** Click the 📊 graph icon in the Workplace sidebar to open the Tracing Dashboard
2. **Start Tracing:** Click duration buttons (3 min, 15 min, or 30 min) to start a tracing session
3. **Monitor:** Watch the live countdown timer (green = active, yellow = <1 min remaining)
4. **Stop:** Click "Stop" button to end tracing early, or let it auto-stop when timer reaches 0
5. **Browse Traces:** View captured traces in the sidebar list (green = success, red = error)
6. **Configure:** Use ⚙️ Config button to set retention hours and log path
7. **Ignore APIs:** Use 🚫 Ignored APIs button to exclude noisy endpoints (e.g., `/api/health/*`)

**DAG Visualization (FEATURE-023-C):**

Click on any trace in the list to view its execution flow as an interactive DAG (Directed Acyclic Graph):

- **Node Types:** API calls (blue), INFO-level functions (green badges), DEBUG-level functions (purple badges)
- **Error Highlighting:** Failed functions show red borders and ⚠ warning icons
- **Timing Info:** Each node displays its execution duration
- **Node Details:** Click any node to open a modal with:
  - Input/output JSON data (pretty-printed)
  - Error details with stack trace (for failed functions)
  - Execution timing and level
- **Navigation:** Pan (drag canvas), zoom (scroll/buttons), fit-to-view (fullscreen button)

**Tracing Instrumentation Skill (FEATURE-023-D):**

Ask the AI agent to automatically add tracing decorators to your code:

```
"Add tracing to src/x_ipe/services/ideas_service.py"
```

The skill will:
1. Analyze the file for traceable functions
2. Assign levels (INFO for public, DEBUG for private)
3. Detect sensitive parameters for redaction (password, token, etc.)
4. Show you a proposal for review
5. Apply decorators after your approval

---

## 🎯 The Vision

### Rethinking Software Engineering in the AI Age

In the rapidly evolving AI landscape, LLM giants are racing to build more powerful models, and an ecosystem of tools has emerged to boost developer productivity—code generation agents, AI-powered IDEs, and intelligent assistants.

**But here's the deeper question:**

> *If AI can write code, does coding remain a value-adding activity for software engineers? Or should we shift our focus to higher-level activities—requirement analysis, system design, and architecture planning?*

### The Core Insight

Drawing from the principles of **DevOps** and **Lean**, the fundamental goal of software delivery has always been:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Deliver business value continuously with high quality         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Traditionally, coding has been the critical bottleneck—a human-intensive activity essential for translating ideas into working software. But with the power of AI agents, **coding can now be delegated**, transforming it from a value-adding activity to an automated process.

### The Mindset Shift: A Value Stream Perspective

From a **Lean** perspective, every activity in software delivery either adds value or creates waste. Let's examine how the value stream has evolved across three development stages:

```
═════════════════════════════════════════════════════════════════════════════════════════════════════
                           VALUE STREAM EVOLUTION BY DEVELOPMENT STAGE
═════════════════════════════════════════════════════════════════════════════════════════════════════

┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                   │
│     STAGE 1                    STAGE 2                       STAGE 3                              │
│     IDEATION                   REQUIREMENT                   FEATURE DELIVERY                     │
│     ─────────                  ───────────                   ────────────────                     │
│                                                                                                   │
│     ┌───────────┐              ┌─────────────┐               ┌──────────────────────────────────┐ │
│     │  Ideation │      ──▶     │ Requirement │       ──▶     │ Refinement ──▶ Design ──▶ Test   │ │
│     │           │              │  Gathering  │               │ ──▶ Code ──▶ Playground ──▶ Close│ │
│     └───────────┘              └─────────────┘               └──────────────────────────────────┘ │
│                                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

#### 📍 STAGE 1: IDEATION

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│  IDEATION STAGE - "What should we build?"                                                         │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                   │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│    │   Capture   │      │   Refine    │      │  Document   │      │    Share    │                 │
│    │    Idea     │  ──▶ │    Idea     │  ──▶ │    Idea     │  ──▶ │    Idea     │                 │
│    └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘                 │
│                                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  🔴 TRADITIONAL: All manual, scattered across emails, meetings, whiteboards                       │
│                                                                                                   │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│    │   Capture   │      │   Refine    │      │  Document   │      │    Share    │                 │
│    │    [H]      │  ──▶ │    [H]      │  ──▶ │    [H]      │  ──▶ │    [H]      │                 │
│    └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘                 │
│                                                                                                   │
│    ╔═════════════════════════════════════════════════════════════════════════════════════════╗    │
│    ║  NON-VALUE-ADDING ACTIVITIES:                                                           ║    │
│    ║  • Manually organizing scattered idea notes from multiple sources                       ║    │
│    ║  • Transcribing whiteboard sessions into documents                                      ║    │
│    ║  • Reformatting ideas for different audiences                                           ║    │
│    ║  • Searching through email threads to find idea context                                 ║    │
│    ║  • Creating presentation slides for idea sharing                                        ║    │
│    ║  • Scheduling and coordinating brainstorming meetings                                   ║    │
│    ╚═════════════════════════════════════════════════════════════════════════════════════════╝    │
│                                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  🟡 DEVOPS + AGILE: Better tools, but still mostly manual ideation work                           │
│                                                                                                   │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│    │   Capture   │      │   Refine    │      │  Document   │      │    Share    │                 │
│    │    [H]      │  ──▶ │    [H]      │  ──▶ │    [H]      │  ──▶ │   [H+T]     │                 │
│    └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘                 │
│                                                                                                   │
│    ╔═════════════════════════════════════════════════════════════════════════════════════════╗    │
│    ║  IMPROVEMENTS:                                                                          ║    │
│    ║  ✓ Collaboration tools (Miro, Confluence, Notion)                                       ║    │
│    ║  ✓ Shared digital whiteboards                                                           ║    │
│    ║  ✓ Version-controlled documentation                                                     ║    │
│    ║                                                                                         ║    │
│    ║  STILL MANUAL:                                                                          ║    │
│    ║  • Writing and organizing ideas                                                         ║    │
│    ║  • Creating summaries and proposals                                                     ║    │
│    ║  • Formatting for stakeholder presentations                                             ║    │
│    ╚═════════════════════════════════════════════════════════════════════════════════════════╝    │
│                                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  🟢 AI-NATIVE: Human focuses on creative thinking, AI handles organization                        │
│                                                                                                   │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│    │   Capture   │      │   Refine    │      │  Document   │      │    Share    │                 │
│    │    Idea     │  ──▶ │    Idea     │  ──▶ │    Idea     │  ──▶ │    Idea     │                 │
│    │    [H]      │      │   [H+AI]    │      │    [AI]     │      │    [AI]     │                 │
│    └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘                 │
│                                                                                                   │
│    ✅ Human: Creative vision, problem identification, initial brainstorming                       │
│    🤖 AI: Organize notes, structure ideas, generate summaries, create shareable docs              │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

#### 📍 STAGE 2: REQUIREMENT

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│  REQUIREMENT STAGE - "What problem are we solving?"                                               │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                   │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│    │   Gather    │      │  Clarify &  │      │   Document  │      │  Breakdown  │                 │
│    │   Needs     │  ──▶ │   Analyze   │  ──▶ │ Requirements│  ──▶ │  Features   │                 │
│    └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘                 │
│                                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  🔴 TRADITIONAL: Heavy documentation overhead, lots of back-and-forth                             │
│                                                                                                   │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│    │   Gather    │      │  Clarify &  │      │   Document  │      │  Breakdown  │                 │
│    │    [H]      │  ──▶ │    [H]      │  ──▶ │    [H]      │  ──▶ │    [H]      │                 │
│    └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘                 │
│                                                                                                   │
│    ╔═════════════════════════════════════════════════════════════════════════════════════════╗    │
│    ║  NON-VALUE-ADDING ACTIVITIES:                                                           ║    │
│    ║  • Writing lengthy requirement documents in specific formats                            ║    │
│    ║  • Creating user story cards and acceptance criteria templates                          ║    │
│    ║  • Maintaining traceability matrices between requirements                               ║    │
│    ║  • Formatting and reformatting specifications for reviews                               ║    │
│    ║  • Generating requirement reports for stakeholders                                      ║    │
│    ║  • Cross-referencing dependencies between requirement documents                         ║    │
│    ║  • Updating requirement status across multiple tracking systems                         ║    │
│    ║  • Creating feature breakdown structures manually                                       ║    │
│    ╚═════════════════════════════════════════════════════════════════════════════════════════╝    │
│                                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  🟡 DEVOPS + AGILE: Better tracking, but documentation still manual                               │
│                                                                                                   │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│    │   Gather    │      │  Clarify &  │      │   Document  │      │  Breakdown  │                 │
│    │    [H]      │  ──▶ │    [H]      │  ──▶ │   [H+T]     │  ──▶ │   [H+T]     │                 │
│    └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘                 │
│                                                                                                   │
│    ╔═════════════════════════════════════════════════════════════════════════════════════════╗    │
│    ║  IMPROVEMENTS:                                                                          ║    │
│    ║  ✓ Jira, Azure DevOps, Linear for tracking                                              ║    │
│    ║  ✓ User story templates and workflows                                                   ║    │
│    ║  ✓ Automated status updates and notifications                                           ║    │
│    ║  ✓ Backlog management and sprint planning tools                                         ║    │
│    ║                                                                                         ║    │
│    ║  STILL MANUAL:                                                                          ║    │
│    ║  • Writing user stories and acceptance criteria                                         ║    │
│    ║  • Creating detailed specifications                                                     ║    │
│    ║  • Breaking down epics into features                                                    ║    │
│    ║  • Maintaining requirement documentation                                                ║    │
│    ╚═════════════════════════════════════════════════════════════════════════════════════════╝    │
│                                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  🟢 AI-NATIVE: Human focuses on understanding needs, AI handles documentation                     │
│                                                                                                   │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│    │   Gather    │      │  Clarify &  │      │   Document  │      │  Breakdown  │                 │
│    │   Needs     │  ──▶ │   Analyze   │  ──▶ │ Requirements│  ──▶ │  Features   │                 │
│    │    [H]      │      │   [H+AI]    │      │    [AI]     │      │    [AI]     │                 │
│    └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘                 │
│                                                                                                   │
│    ✅ Human: Stakeholder conversations, clarifying questions, prioritization decisions            │
│    🤖 AI: Document requirements, generate acceptance criteria, create feature breakdown           │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

#### 📍 STAGE 3: FEATURE DELIVERY

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│  FEATURE DELIVERY STAGE - "Build, Test, Ship"                                                     │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                   │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│    │ Refine-  │    │ Technical│    │   Test   │    │   Code   │    │   Play-  │    │ Feature  │   │
│    │   ment   │ ─▶ │  Design  │ ─▶ │   Gen    │ ─▶ │   Impl   │ ─▶ │  ground  │ ─▶ │ Closing  │   │
│    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│                                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  🔴 TRADITIONAL: Heavy manual effort across all phases                                            │
│                                                                                                   │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│    │   [H]    │ ─▶ │   [H]    │ ─▶ │   [H]    │ ─▶ │   [H]    │ ─▶ │   [H]    │ ─▶ │   [H]    │   │
│    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│                                                                                                   │
│    ╔═════════════════════════════════════════════════════════════════════════════════════════╗    │
│    ║  NON-VALUE-ADDING ACTIVITIES:                                                           ║    │
│    ║                                                                                         ║    │
│    ║  📋 REFINEMENT:                                                                         ║    │
│    ║  • Writing detailed specification documents                                             ║    │
│    ║  • Creating wireframes and mockup documentation                                         ║    │
│    ║  • Maintaining version history of specifications                                        ║    │
│    ║                                                                                         ║    │
│    ║  🏗️  DESIGN:                                                                            ║    │
│    ║  • Writing technical design documents from scratch                                      ║    │
│    ║  • Creating architecture diagrams manually                                              ║    │
│    ║  • Documenting API contracts and interfaces                                             ║    │
│    ║  • Research for best practices and patterns                                             ║    │
│    ║                                                                                         ║    │
│    ║  🧪 TESTING:                                                                            ║    │
│    ║  • Writing unit tests, integration tests, API tests                                     ║    │
│    ║  • Creating test data and fixtures                                                      ║    │
│    ║  • Maintaining test documentation                                                       ║    │
│    ║  • Manual regression testing                                                            ║    │
│    ║                                                                                         ║    │
│    ║  💻 CODING:                                                                             ║    │
│    ║  • Implementing boilerplate code                                                        ║    │
│    ║  • Writing CRUD operations                                                              ║    │
│    ║  • Implementing standard patterns                                                       ║    │
│    ║  • Writing code documentation and comments                                              ║    │
│    ║                                                                                         ║    │
│    ║  🎮 PLAYGROUND:                                                                         ║    │
│    ║  • Setting up demo environments                                                         ║    │
│    ║  • Creating sample data for testing                                                     ║    │
│    ║  • Writing usage documentation                                                          ║    │
│    ║                                                                                         ║    │
│    ║  📦 CLOSING:                                                                            ║    │
│    ║  • Creating pull request descriptions                                                   ║    │
│    ║  • Writing release notes and changelogs                                                 ║    │
│    ║  • Updating project documentation                                                       ║    │
│    ╚═════════════════════════════════════════════════════════════════════════════════════════╝    │
│                                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  🟡 DEVOPS + AGILE: CI/CD automates deployment, but coding still manual                           │
│                                                                                                   │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│    │   [H]    │ ─▶ │   [H]    │ ─▶ │  [H+T]   │ ─▶ │   [H]    │ ─▶ │  [H+T]   │ ─▶ │   [T]    │   │
│    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│                                                                                                   │
│    ╔═════════════════════════════════════════════════════════════════════════════════════════╗    │
│    ║  IMPROVEMENTS:                                                                          ║    │
│    ║  ✓ CI/CD pipelines automate build, test, deploy                                         ║    │
│    ║  ✓ Automated testing frameworks (Jest, Pytest, etc.)                                    ║    │
│    ║  ✓ Infrastructure as Code (Terraform, CloudFormation)                                   ║    │
│    ║  ✓ Containerization (Docker, Kubernetes)                                                ║    │
│    ║  ✓ Feature flags and gradual rollouts                                                   ║    │
│    ║                                                                                         ║    │
│    ║  STILL MANUAL:                                                                          ║    │
│    ║  • Writing specifications and technical designs                                         ║    │
│    ║  • Writing all the code (still 100% human)                                              ║    │
│    ║  • Writing tests (unit, integration, e2e)                                               ║    │
│    ║  • Code reviews and documentation                                                       ║    │
│    ║  • PR descriptions and release notes                                                    ║    │
│    ╚═════════════════════════════════════════════════════════════════════════════════════════╝    │
│                                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  🟢 AI-NATIVE: Human focuses on review & approval, AI handles execution                           │
│                                                                                                   │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│    │ Refine-  │    │ Technical│    │   Test   │    │   Code   │    │   Play-  │    │ Feature  │   │
│    │   ment   │ ─▶ │  Design  │ ─▶ │   Gen    │ ─▶ │   Impl   │ ─▶ │  ground  │ ─▶ │ Closing  │   │
│    │  [H+AI]  │    │  [H+AI]  │    │   [AI]   │    │   [AI]   │    │  [H+AI]  │    │   [AI]   │   │
│    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│                                                                                                   │
│    ✅ Human: Review specs, approve designs, validate in playground, final approval                │
│    🤖 AI: Generate specs, create designs, write tests, implement code, create PRs                 │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

#### 📊 The Complete Transformation

```
═══════════════════════════════════════════════════════════════════════════════════════════
                         SUMMARY: WHERE HUMANS ADD VALUE
═══════════════════════════════════════════════════════════════════════════════════════════

  STAGE          TRADITIONAL                 DEVOPS/AGILE              AI-NATIVE
  ─────          ───────────                 ────────────              ─────────
                                                                       
  IDEATION       [H] Everything              [H] Everything            [H] Creative Vision
                 Manual docs                 Better tools              [AI] Organization
                                                                       
  REQUIREMENT    [H] Everything              [H] Everything            [H] Understanding
                 Heavy paperwork             Agile boards              [AI] Documentation
                                                                       
  FEATURE        [H] Everything              [H] Code + Test           [H] Review + Approve
  DELIVERY       Manual deploy               [T] CI/CD                 [AI] Code + Test
                                                                       [T] CI/CD

═══════════════════════════════════════════════════════════════════════════════════════════

  HUMAN ACTIVITIES IN AI-NATIVE ERA:
  
  ┌──────────────────────────────────────────────────────────────────────────────────────┐
  │                                                                                      │
  │   🎯 IDEATION        │  💡 Creative thinking, vision, problem discovery               │
  │   📋 REQUIREMENT     │  🤝 Stakeholder engagement, clarification, prioritization      │
  │   🏗️  DESIGN         │  ✅ Architecture decisions, design review & approval           │
  │   💻 IMPLEMENTATION  │  👀 Code review, quality gates                                 │
  │   🎮 VALIDATION      │  🧪 User acceptance, business validation                       │
  │   📦 DELIVERY        │  ✅ Final approval, release decision                           │
  │                                                                                      │
  └──────────────────────────────────────────────────────────────────────────────────────┘
  
  🚀 RESULT: Humans focus on THINKING & DECIDING, AI handles EXECUTING & DOCUMENTING

═══════════════════════════════════════════════════════════════════════════════════════════
```

**The key realization:** To answer "What should humans do in the AI age?", we need more than just better AI tools. We need an **operation model**—a way to orchestrate the end-to-end process from idea to delivery that fits your organizational context.

Just as DevOps isn't merely a toolchain but a delivery model that orchestrates **people, process, and tools**, the AI age demands a new paradigm for value delivery.

---

## 📚 Part of a Larger Journey

This project is part of a **software engineering blog series** exploring the impact of AI on delivery practices. Topics include:

- What remains unchanged in software engineering?
- What can be optimized with AI?
- Mindset shifts, process improvements, and tool evolution

**Stay tuned for more insights!**

---

## 🔄 How I Build This Application, How We Build Others

The X-IPE development workflow follows a continuous improvement loop:

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                   │
│                              THE X-IPE DEVELOPMENT LOOP                                           │
│                                                                                                   │
│   ┌─────────────────────┐                                       ┌─────────────────────┐           │
│   │  1️⃣ DEFINE SKILLS    │ ──────────────────────────────────▶  │  2️⃣ INSTRUCT AGENTS │            │ 
│   │  (Agent Playbook)   │                                       │  (Execute Tasks)    │           │
│   └─────────────────────┘                                       └─────────────────────┘           │
│            ▲                                                              │                       │
│            │                                                              ▼                       │
│   ┌─────────────────────┐                                       ┌─────────────────────┐           │
│   │  4️⃣ IMPROVE SKILLS  │ ◀──────────────────────────────────   │  3️⃣ MONITOR & GIVE  │            │
│   │  & IPE PLATFORM     │                                       │     FEEDBACK        │           │
│   └─────────────────────┘                                       └─────────────────────┘           │
│                                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1️⃣ Define Skills for Agents (GitHub Copilot CLI)

> **The foundation: Create predefined skills that guide agent behavior**

```
┌─────────────────────────────────────────────────────────┐
│   👤 Human: Draft initial skill version                 │
│      ↓                                                  │
│   🤖 AI: Revise and enhance the skill                   │
│      ↓                                                  │
│   👤 Human: Review, provide feedback                    │
│      ↓                                                  │
│   🔄 Loop until skill is production-ready               │
└─────────────────────────────────────────────────────────┘
```

Skills live in `.github/skills/` and define:
- Task execution procedures
- Definition of Ready (DoR) & Done (DoD)
- Output artifacts and templates
- Integration with other skills

---

### 2️⃣ Instruct Agents to Execute Tasks

> **The execution: Agents follow skill rules to plan and complete work**

```
┌─────────────────────────────────────────────────────────┐
│   📋 Agent loads skill for current task type            │
│      ↓                                                  │
│   ✅ Follows rules in skill to plan work                │
│      ↓                                                  │
│   🚀 Executes task, generates artifacts                 │
│      ↓                                                  │
│   ➡️ Auto-proceeds to next task (with approval gates)   │
│      ↓                                                  │
│   🔄 Loop through all tasks in the workflow             │
└─────────────────────────────────────────────────────────┘
```

Key behaviors:
- Task board as single source of truth
- Human approval required at stage gates
- Artifacts are version-controlled and traceable

---

### 3️⃣ Monitor Deliveries and Provide Feedback

> **The oversight: Track progress and guide direction**

```
┌─────────────────────────────────────────────────────────┐
│   📊 Overview project status:                           │
│      • Feature completeness (feature board)             │
│      • Task status (task board)                         │
│      • Overall quality (tests, code review)             │
│      ↓                                                  │
│   💬 Provide feedback on deliverables                   │
│      ↓                                                  │
│   📝 Plan next assignments                              │
│      ↓                                                  │
│   🔄 Loop: continuous monitoring                        │
└─────────────────────────────────────────────────────────┘
```

Monitoring through:
- Task board for agent work tracking
- Feature board for delivery lifecycle
- IPE interface for real-time visibility

---

### 4️⃣ Continuous Skill & IPE Improvement

> **The evolution: Learn from practice, improve the system**

```
┌─────────────────────────────────────────────────────────┐
│   📈 Gather feedback from practice                      │
│      ↓                                                  │
│   🔧 Update operation model (skills) based on learnings │
│      ↓                                                  │
│   🖥️ Optimize IPE for transparency & accessibility      │
│      ↓                                                  │
│   ↩️ Back to Step 1: Refine skills for next cycle       │
└─────────────────────────────────────────────────────────┘
```

Improvements include:
- Better skill definitions from real-world usage
- New skills for emerging patterns
- IPE features for better human-AI collaboration

---

**🔄 The Big Loop:** This cycle repeats continuously—each iteration improves both the **operation model** (skills) and the **platform** (IPE), creating a virtuous cycle of AI-assisted development.

---

## ✨ Features

### ✅ Implemented

| Feature | Description | Status |
|---------|-------------|--------|
| **Project Navigation** | Dynamic sidebar with folder tree, real-time file monitoring | ✅ Completed |
| **Content Viewer** | Markdown rendering with syntax highlighting | ✅ Completed |
| **Content Editor** | Edit mode for file modifications with save to filesystem | ✅ Completed |
| **Live Refresh** | Auto-detect file changes and refresh content via WebSocket | ✅ Completed |
| **Settings & Configuration** | Project root configuration and app preferences | ✅ Completed |
| **Multi-Project Support** | Manage and switch between multiple projects | ✅ Completed |
| **Workplace (Ideas)** | Upload, organize, and refine ideas with tree view and inline editing | ✅ Completed |
| **File Change Indicator** | Visual indicator showing unsaved changes in navigation | ✅ Completed |
| **Interactive Console v2** | Full xterm.js terminal with session persistence, auto-reconnection, split-pane support | ✅ Completed |
| **Application Action Tracing** | Python function tracing with @x_ipe_tracing decorator, sensitive data redaction, duration-based control, dashboard UI | ✅ Completed |
| **File Link Preview** | Click internal links (`x-ipe-docs/`, `.github/skills/`) in rendered markdown to preview files in-place via modal overlay | ✅ Completed |

### 🔜 Planned

| Feature | Description | Status |
|---------|-------------|--------|
| **Git Integration** | Version history and side-by-side diff comparison | Planned |

---

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|--------------|
| **AI Agent** | GitHub Copilot CLI |
| **Agent Models** | Claude Sonnet 4.5+, Gemini 2.5 Flash+ (models with skills/tools capability) |
| **Skills System** | Custom skill definitions in `.github/skills/` (Anthropic-style skills protocol) |
| **Backend** | Python 3.12+, Flask, Flask-SocketIO, eventlet |
| **Frontend** | HTML/CSS, Bootstrap 5, JavaScript, xterm.js |
| **Real-time** | WebSocket (Socket.IO), watchfiles (file monitoring) |
| **Testing** | pytest, pytest-flask |
| **Package Manager** | uv |

---

## 📁 Project Structure

```
X-IPE/
├── src/                        # Source code
│   ├── app.py                  # Flask application entry point
│   ├── services.py             # Business logic services
│   ├── config.py               # Configuration management
│   ├── templates/              # Jinja2 HTML templates
│   └── instance/               # Instance-specific data
├── static/                     # Frontend assets
│   ├── css/                    # Stylesheets
│   └── js/                     # JavaScript modules
├── tests/                      # Test suite
├── playground/                 # Feature playground & experiments
│   └── tests/                  # Playground-specific tests
├── x-ipe-docs/                       # Documentation
│   ├── planning/               # Task board, feature board
│   ├── requirements/           # Feature specifications & designs
│   │   └── FEATURE-XXX/        # Per-feature specs & tech designs
│   ├── ideas/                  # Captured ideas
│   ├── environment/            # Setup documentation
│   └── reference/              # Lessons learned & references
├── resources/                  # Screenshots & media assets
├── .github/
│   ├── copilot-instructions.md # AI agent instructions
│   └── skills/                 # AI agent skill definitions
│       ├── x-ipe-workflow-task-execution/
│       ├── x-ipe+all+task-board-management/
│       ├── x-ipe-task-based-*/        # Task-specific skills
│       └── *-stage+*-management/ # Stage board management
└── pyproject.toml              # Project configuration (uv)
```

---

## 📋 Version Changelog

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-01-23 | Initial release of X-IPE with complete AI-native project lifecycle management, featuring ideation, requirement gathering, feature breakdown, technical design, code implementation, and human playground capabilities. |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  <strong>X-IPE</strong> — Reimagining Software Delivery for the AI Age
</p>
