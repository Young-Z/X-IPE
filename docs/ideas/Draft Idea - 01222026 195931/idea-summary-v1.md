# Idea Summary

> Idea ID: IDEA-001
> Folder: Draft Idea - 01222026 195931
> Version: v1
> Created: 2026-01-22
> Status: Refined

## Overview

A lightweight web-based project viewer for human users to review, navigate, and edit AI-agent-created projects. Transforms text-based documentation into a user-friendly interface with proper rendering, live updates, and an integrated terminal.

## Problem Statement

AI agents create well-structured projects with text-based documentation (markdown, code, YAML), but native OS file viewers/editors are not optimized for:
- Rendering markdown with diagrams (Mermaid)
- Syntax-highlighted code viewing
- Real-time collaboration with AI agents updating files
- Quick navigation of deep folder structures

Humans need a better interface to efficiently review and interact with AI-generated projects.

## Target Users

**Primary:** Solo developers/users working with AI coding agents on their local machine.

**Use Case:** After AI agent completes a task, human opens the web viewer to:
1. Review generated documentation and code
2. Navigate project structure easily
3. Make small edits/corrections
4. Monitor live file changes during AI work sessions
5. Run terminal commands without leaving the app

## Proposed Solution

A Flask-based web application that runs locally alongside the AI-agent project:

### Architecture
```
┌─────────────────────────────────────────────────┐
│  Web Browser (localhost:5000)                   │
├─────────────┬───────────────────────────────────┤
│  Sidebar    │   Content Area                    │
│  (Tree Nav) │   (Markdown/Code/Diagram Viewer)  │
│             │                                   │
│  ▼ Planning │   ┌───────────────────────────┐   │
│    task-    │   │  # Feature Specification  │   │
│    board.md │   │  ...rendered markdown...  │   │
│  ▼ Require- │   │  ```mermaid              │   │
│    ments    │   │    flowchart TD          │   │
│  ▼ Code     │   │  ```                     │   │
│  ▼ Tests    │   └───────────────────────────┘   │
├─────────────┴───────────────────────────────────┤
│  [▲ Terminal] ───────────────────────────────── │
│  $ python main.py                               │
│  Server running on http://localhost:5000        │
└─────────────────────────────────────────────────┘
```

### Key Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | Python + Flask | File serving, API, WebSocket |
| Frontend | Bootstrap 5 + Vanilla JS | Responsive UI |
| Markdown | marked.js | Markdown rendering |
| Diagrams | Mermaid.js | Diagram rendering |
| Code | highlight.js | Syntax highlighting |
| Terminal | xterm.js + PTY | Interactive shell |
| Database | SQLite | Settings persistence |

## Key Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Project Navigation | Dynamic tree sidebar reflecting folder structure | High |
| Content Viewer | Format-aware rendering (Markdown, Code, Mermaid) | High |
| Content Editor | Edit mode with save/cancel for text files | High |
| Live Refresh | Auto-update content when files change + toast notification | High |
| Interactive Console | Pop-up terminal panel for running commands | High |
| Settings | Configurable project root path, theme preferences | Medium |
| Full Coverage | Support docs/, src/, tests/, playground/, root files | Medium |

## Success Criteria

- [x] User can navigate entire project structure in sidebar
- [x] Markdown files render with proper formatting and Mermaid diagrams
- [x] Code files display with syntax highlighting
- [x] User can edit and save file content
- [x] Content auto-refreshes when AI agent modifies files
- [x] Toast notification appears on file changes
- [x] Terminal panel allows running shell commands
- [x] Works as single-user local deployment

## Constraints & Considerations

| Constraint | Impact |
|------------|--------|
| Single user only | No auth needed, simpler architecture |
| Local deployment | No security hardening for v1 |
| File system access | Limited to configured project root |
| Browser-based | Modern browser required |

### Out of Scope for v1
- Multi-user authentication
- Remote/cloud deployment
- Git integration (viewing commits, branches)
- File creation/deletion from UI
- Search across project

## Brainstorming Notes

**Decisions Made:**
1. **Deployment:** Single user, local only - keeps architecture simple
2. **Coverage:** Full project support (docs, src, tests, playground, root)
3. **Refresh UX:** Toast notifications (non-blocking, auto-dismiss)

**Technical Insights:**
- Flask can serve both API and static files
- WebSocket (Socket.IO) ideal for live updates and terminal
- SQLite sufficient for settings storage
- No build step needed - vanilla JS keeps it simple

## Source Files

- Project Proposal

## Next Steps

- [ ] Proceed to Requirement Gathering
- [ ] Define formal requirements with acceptance criteria
- [ ] Break down into implementable features
