# Project Document Viewer

A lightweight project management web application for reviewing AI agent-created projects.

## Overview

This application provides a user-friendly web interface for humans to view and manage text-based project documentation created by AI agents.

## Features

### ✅ Implemented
- **Project Navigation (FEATURE-001)**: Dynamic sidebar with folder tree navigation
  - Three sections: Project Plan, Requirements, Code
  - Real-time file system monitoring via WebSocket
  - Expandable/collapsible folder tree
  - Auto-refresh on file changes

### 🔜 Planned
- **Content Viewer**: Markdown/code rendering with syntax highlighting
- **Content Editor**: Edit mode for file modifications
- **Live Refresh**: Auto-detect file changes and refresh content
- **Interactive Console**: Terminal for shell commands
- **Settings**: Project root configuration
- **Git Integration**: Version history and diff comparison

## Technology Stack

- **Backend**: Python 3.12+ with Flask, Flask-SocketIO
- **Frontend**: HTML/CSS with Bootstrap 5, JavaScript
- **File Watching**: watchdog library
- **Package Manager**: uv

## How to Run

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Run the application:**
   ```bash
   uv run python -m src.app
   ```

3. **Open in browser:**
   ```
   http://localhost:5000
   ```

4. **Run tests:**
   ```bash
   uv run pytest tests/ -v
   ```

## Project Structure

```
project-root/
├── src/                    # Source code
│   ├── app.py              # Flask application
│   ├── services.py         # ProjectService, FileWatcher
│   ├── config.py           # Configuration
│   └── templates/          # HTML templates
├── static/                 # CSS, JS assets
├── tests/                  # Test files
├── docs/                   # Documentation
│   ├── planning/           # Task board, features
│   ├── requirements/       # Feature specifications
│   └── environment/        # Setup docs
└── pyproject.toml          # Project config
```

## Documentation

- [Task Board](docs/planning/task-board.md)
- [Feature Board](docs/planning/features.md)
- [Requirements](docs/requirements/requirement-summary.md)
- [Environment Setup](docs/environment/setup.md)
