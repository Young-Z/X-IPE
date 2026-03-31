# 8. FAQ & Reference

## Frequently Asked Questions

### General

**Q: What is the difference between FREE mode and WORKFLOW mode?**
A: FREE mode is a file browser and editor — you can explore project files, view content, and use the terminal. WORKFLOW mode provides a structured engineering lifecycle with 5 stages (Ideation → Requirement → Implement → Validation → Feedback) that guide AI-assisted development.

**Q: Can I switch between FREE and WORKFLOW mode at any time?**
A: Yes. Toggling modes does not lose any data. Workflow state persists on disk, and you can switch freely.

**Q: Do I need an AI CLI tool to use X-IPE?**
A: For WORKFLOW mode, yes — you need one of: GitHub Copilot CLI, Claude Code, or OpenCode. The AI CLI tool executes the skill-based commands that drive workflow actions. FREE mode can be used without an AI CLI for basic file browsing.

**Q: How long do AI actions take?**
A: Typically 1-5 minutes per action, depending on complexity. Implementation actions may take 5-15 minutes for larger features. Watch the terminal for progress.

---

### Workflows

**Q: How many workflows can I have at once?**
A: There is no hardcoded limit. You can create and manage multiple concurrent workflows.

**Q: Can I delete a workflow?**
A: Yes. Click the **⋮** menu on a workflow card and select "Delete". This removes the workflow state file but does not delete generated deliverable files.

**Q: Can I go back to a previous stage?**
A: No. Once a later stage has started, previous actions are locked. If you need to revise earlier work, edit the deliverable files directly in FREE mode.

**Q: What happens if an action fails?**
A: The action status changes to "failed". You can retry by clicking the action again. Check the terminal for error details.

**Q: Can I skip optional actions?**
A: Yes. Optional actions (like Reference UIUX, Design Mockup) don't block stage progression. Only mandatory actions must be completed to advance.

---

### Features & Dependencies

**Q: What do "⇉ Parallel" and "⛓ needs FEATURE-XXX" mean?**
A: "⇉ Parallel" means the feature has no dependencies and can start immediately. "⛓ needs FEATURE-XXX" means the feature is blocked until the specified feature's Implement stage completes.

**Q: Can I work on multiple features simultaneously?**
A: Yes, as long as they are marked "⇉ Parallel" or their dependencies are met. Independent features can progress through their lanes concurrently.

---

### Interaction Modes

**Q: What is DAO?**
A: DAO (Decision-Assisting Oracle) is X-IPE's AI decision-making proxy. It can represent the human developer for routine decisions, reducing the need for manual approval at every step.

**Q: Which interaction mode should I start with?**
A: Start with **"👤 Human Direct"** to understand the workflow. Once comfortable, switch to **"🤖 DAO Represents Human"** for faster execution.

**Q: Can I change the interaction mode during a workflow?**
A: Yes. Click the interaction mode dropdown on any workflow card and select a new mode. The change applies immediately to all future actions.

---

## Glossary

| Term | Definition |
|------|------------|
| **Action** | A single step within a workflow stage (e.g., "Compose Idea", "Feature Breakdown") |
| **CLI_DISPATCH** | Interaction pattern where clicking a button sends a command to the AI CLI terminal |
| **DAO** | Decision-Assisting Oracle — AI proxy that represents human intent in automated decisions |
| **Deliverable** | Any artifact produced by a workflow action (idea docs, specs, code files, test reports) |
| **Epic** | A group of related features, identified by EPIC-NNN numbering |
| **Feature** | An individual unit of work, identified by FEATURE-NNN-X (e.g., FEATURE-050-A) |
| **Feature Lane** | Horizontal progress bar showing a feature's progression through 8 per-feature steps |
| **FREE mode** | X-IPE's file browsing and editing mode |
| **Interaction Mode** | Setting that controls how autonomous the AI is (Human Direct, DAO Represents Human, DAO Inner-Skill Only) |
| **Mandatory action** | An action that must be completed before the stage can advance |
| **Optional action** | An action that can be skipped without blocking stage progression |
| **Skill** | A specialized AI capability (e.g., `x-ipe-task-based-ideation`) dispatched via CLI |
| **Stage** | One of 5 phases in the workflow lifecycle (Ideation, Requirement, Implement, Validation, Feedback) |
| **WebSocket** | Real-time communication protocol used between X-IPE browser and the terminal |
| **WORKFLOW mode** | X-IPE's structured engineering lifecycle mode |
| **Workflow** | A named engineering project that progresses through 5 stages |
| **X-IPE** | AI-Native Integrated Project Environment |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+V` | Toggle microphone for voice input (when enabled) |

---

## API Reference (User-Facing)

**Base URL:** `http://127.0.0.1:5858/api`

### Workflow Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/workflows` | List all workflows |
| `POST` | `/api/workflow/create` | Create a new workflow |
| `GET` | `/api/workflow/{name}` | Get workflow details |
| `DELETE` | `/api/workflow/{name}` | Delete a workflow |
| `PATCH` | `/api/workflow/{name}/settings` | Update workflow settings |
| `POST` | `/api/workflow/{name}/action` | Execute a workflow action |
| `GET` | `/api/workflow/{name}/deliverables` | Get workflow deliverables |
| `GET` | `/api/workflow/{name}/deliverables/tree` | Browse deliverable folder |

### Settings Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/settings` | Get current settings |
| `POST` | `/api/settings` | Save settings |
| `POST` | `/api/settings/language` | Change interface language |

### Other Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tracing/traces` | View application traces |
| `GET` | `/api/file-tree` | Get project file tree |
| `GET` | `/api/file-content` | Get file content |

---

## File Structure Reference

```
project-root/
├── .x-ipe.yaml                                  # Project configuration
├── .github/
│   └── copilot/
│       ├── instructions.md                      # Copilot custom instructions
│       └── mcp-config.json                      # MCP server configuration
├── x-ipe-docs/
│   ├── config/
│   │   ├── .env                                 # Environment variables
│   │   └── workflow-template.json               # Workflow stage definitions
│   ├── engineering-workflow/
│   │   └── workflow-{name}.json                 # Active workflow state files
│   ├── planning/
│   │   └── task-board.md                        # Task tracking board
│   └── knowledge-base/                          # Extracted knowledge articles
├── ideas/
│   └── {workflow-name}/
│       ├── new idea.md                          # Raw idea
│       └── refined-idea/
│           └── idea-summary-v1.md               # AI-refined idea
├── requirements/
│   └── EPIC-{NNN}/
│       └── FEATURE-{NNN}-{X}/
│           ├── specification.md                 # Feature specification
│           ├── technical-design.md              # Technical design
│           └── acceptance-test-report.md        # Test results
└── .github/skills/
    └── x-ipe-task-based-*/                      # AI skill definitions
        └── SKILL.md
```

---

## Version Information

- **Application:** X-IPE (AI-Native Integrated Project Environment)
- **Server:** Flask-based, runs on `127.0.0.1:5858`
- **Communication:** WebSocket (Flask-SocketIO) for real-time terminal interaction
- **Configuration format:** YAML (`.x-ipe.yaml`) and JSON (workflow state files)
