# 1. Overview

## What is X-IPE?

**X-IPE (AI-Native Integrated Project Environment)** is a web-based application that provides an end-to-end, AI-assisted project delivery environment. It orchestrates the entire software engineering lifecycle — from initial idea brainstorming through requirements gathering, implementation, validation, and feedback — using AI agents and structured skill-based workflows.

X-IPE acts as a bridge between human engineers and AI coding assistants (GitHub Copilot CLI, Claude Code, OpenCode), providing a visual workflow management layer that guides AI execution through well-defined engineering phases.

## Target Audience

- **Software engineers and developers** who want AI-assisted project delivery
- **Technical leads and architects** managing feature development workflows
- **Individual developers** building personal projects with AI pair-programming
- **Teams** wanting structured, repeatable engineering processes with AI augmentation

## What Problem Does It Solve?

X-IPE addresses three core challenges:

1. **Unstructured AI usage**: Without X-IPE, developers interact with AI coding assistants ad-hoc. X-IPE provides structured workflows that guide AI through proper engineering phases (ideation → requirements → implementation → validation).

2. **Lack of traceability**: Ad-hoc AI conversations produce no audit trail. X-IPE tracks every deliverable (ideas, specs, designs, code, test reports) across the full project lifecycle.

3. **Missing orchestration**: Complex projects need feature dependencies, stage gating, and parallel work streams. X-IPE provides visual feature lanes with dependency management and automated stage progression.

## Key Features

| Feature | Description |
|---------|-------------|
| **Dual Mode** | FREE mode for general file browsing; WORKFLOW mode for structured engineering |
| **5-Stage Workflow** | Ideation → Requirement → Implement → Validation → Feedback |
| **AI Skill Dispatch** | Actions dispatch to specialized AI skills via the connected CLI terminal |
| **Feature Lanes** | Per-feature progress tracking with dependency management |
| **Deliverables Tracking** | Visual panel showing all artifacts organized by stage and feature |
| **Interaction Modes** | Human Direct, DAO Represents Human, or DAO Inner-Skill Only |
| **Multi-Workflow** | Manage multiple concurrent engineering workflows |
| **Real-Time Console** | Integrated terminal with WebSocket connection for AI command execution |

## High-Level Architecture

```
┌─────────────────────────────────────────────┐
│              Browser (Web UI)                │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  │
│  │ FREE Mode│  │WORKFLOW   │  │ Settings │  │
│  │ (Editor) │  │ Mode      │  │          │  │
│  └──────────┘  └───────────┘  └──────────┘  │
└──────────────┬──────────────────────────────┘
               │ HTTP + WebSocket (SocketIO)
┌──────────────▼──────────────────────────────┐
│           Flask Backend (:5858)              │
│  ┌────────────┐  ┌──────────────────────┐   │
│  │ Workflow    │  │ File/Deliverables    │   │
│  │ Manager    │  │ Service              │   │
│  │ Service    │  │                      │   │
│  └────────────┘  └──────────────────────┘   │
│  ┌────────────┐  ┌──────────────────────┐   │
│  │ CLI Adapter│  │ Settings Service     │   │
│  │ (SocketIO) │  │                      │   │
│  └────────────┘  └──────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │ CLI dispatch
┌──────────────▼──────────────────────────────┐
│    AI CLI (Copilot / Claude / OpenCode)     │
│         Executes skills in terminal         │
└─────────────────────────────────────────────┘
```

The application runs as a local Flask server that serves the web UI and communicates with AI CLI tools through a WebSocket-connected terminal.
