# Refactoring Plan - TASK-194

> **Task ID:** TASK-194  
> **Created:** 2026-01-28  
> **Executor:** Nova  
> **Status:** Awaiting Human Approval

---

## 1. Overview

**Goal:** Split `app.py` (1312 lines) into focused modules using Flask Blueprints

**Target:** app.py → ~100 lines (factory only)

**Principles Applied:**
- **SRP** (Single Responsibility) - Each module handles one concern
- **SoC** (Separation of Concerns) - Routes vs Handlers vs Services
- **Modular Design** - Reusable, testable modules

**Constraints:**
- Maintain API compatibility (all endpoints unchanged)
- Preserve WebSocket behavior
- Keep Flask-SocketIO patterns

---

## 2. Target Structure

```
src/x_ipe/
├── app.py                    # Factory only (~100 lines)
├── routes/                   # NEW - Flask Blueprints
│   ├── __init__.py           # Blueprint exports
│   ├── main_routes.py        # FEATURE-001, FEATURE-003
│   ├── settings_routes.py    # FEATURE-006, FEATURE-010
│   ├── project_routes.py     # FEATURE-006 (projects)
│   ├── ideas_routes.py       # FEATURE-008
│   └── tools_routes.py       # FEATURE-011, FEATURE-012
├── handlers/                 # NEW - WebSocket handlers
│   ├── __init__.py           # Handler registration
│   ├── terminal_handlers.py  # FEATURE-005
│   └── voice_handlers.py     # FEATURE-021
└── [existing modules unchanged]
```

---

## 3. Phased Execution Plan

### Phase 1: Create Route Modules (HIGH RISK)

| Step | Change Type | From | To | Principle | Risk |
|------|-------------|------|-----|-----------|------|
| 1.1 | Create | - | `routes/__init__.py` | SoC | Low |
| 1.2 | Extract | `register_routes()` | `routes/main_routes.py` | SRP | Medium |
| 1.3 | Extract | `register_settings_routes()` | `routes/settings_routes.py` | SRP | Medium |
| 1.4 | Extract | `register_project_routes()` | `routes/project_routes.py` | SRP | Medium |
| 1.5 | Extract | `register_ideas_routes()` | `routes/ideas_routes.py` | SRP | Medium |
| 1.6 | Extract | `register_tools_config_routes()` | `routes/tools_routes.py` | SRP | Medium |

**Tests Affected:** `test_navigation.py`, `test_settings.py`, `test_ideas.py`, `test_tools_config.py`, `test_themes.py`

### Phase 2: Create Handler Modules (HIGH RISK)

| Step | Change Type | From | To | Principle | Risk |
|------|-------------|------|-----|-----------|------|
| 2.1 | Create | - | `handlers/__init__.py` | SoC | Low |
| 2.2 | Extract | `register_terminal_handlers()` | `handlers/terminal_handlers.py` | SRP | High |
| 2.3 | Extract | `register_voice_handlers()` | `handlers/voice_handlers.py` | SRP | High |

**Tests Affected:** `test_terminal.py`, `test_voice_input.py`

### Phase 3: Simplify app.py (LOW RISK)

| Step | Change Type | From | To | Principle | Risk |
|------|-------------|------|-----|-----------|------|
| 3.1 | Refactor | `create_app()` | Simplified factory | KISS | Low |
| 3.2 | Update | imports | Use new modules | Modular | Low |

---

## 4. Detailed Changes

### 4.1 routes/main_routes.py

**Features:** FEATURE-001 (Navigation), FEATURE-003 (Editor)

```python
# routes/main_routes.py
from flask import Blueprint, render_template, jsonify, request, send_file
from pathlib import Path
import os

from x_ipe.services import ProjectService, ContentService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve main page with sidebar navigation"""
    return render_template('index.html')

@main_bp.route('/api/project/structure')
def get_project_structure():
    # ... (extracted from app.py lines 147-165)

@main_bp.route('/api/file/content')  
def get_file_content():
    # ... (extracted from app.py lines 167-241)

@main_bp.route('/api/file/save', methods=['POST'])
def save_file():
    # ... (extracted from app.py lines 243-279)
```

**Lines Extracted:** ~140 lines

### 4.2 routes/settings_routes.py

**Features:** FEATURE-006 (Settings), FEATURE-010 (Config)

```python
# routes/settings_routes.py
from flask import Blueprint, render_template, jsonify, request, current_app

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def settings_page():
    # ... (extracted from app.py lines 567-576)

@settings_bp.route('/api/settings', methods=['GET'])
def get_settings():
    # ...

@settings_bp.route('/api/settings', methods=['POST'])
def save_settings():
    # ...

@settings_bp.route('/api/config', methods=['GET'])
def get_config():
    # ...
```

**Lines Extracted:** ~115 lines

### 4.3 routes/project_routes.py

**Features:** FEATURE-006 v2.0 (Multi-Project)

```python
# routes/project_routes.py
from flask import Blueprint, jsonify, request, current_app

project_bp = Blueprint('project', __name__)

@project_bp.route('/api/projects', methods=['GET'])
def get_projects():
    # ...

@project_bp.route('/api/projects', methods=['POST'])
def add_project():
    # ...

# ... switch, update, delete endpoints
```

**Lines Extracted:** ~170 lines

### 4.4 routes/ideas_routes.py

**Features:** FEATURE-008 (Workplace), Skills API

```python
# routes/ideas_routes.py
from flask import Blueprint, jsonify, request, current_app

from x_ipe.services import IdeasService, SkillsService

ideas_bp = Blueprint('ideas', __name__)

@ideas_bp.route('/api/ideas/tree', methods=['GET'])
def get_ideas_tree():
    # ...

# ... upload, rename, delete, toolbox endpoints
# ... skills API endpoints
```

**Lines Extracted:** ~245 lines

### 4.5 routes/tools_routes.py

**Features:** FEATURE-011 (Tools Config), FEATURE-012 (Themes)

```python
# routes/tools_routes.py
from flask import Blueprint, jsonify, request, current_app

from x_ipe.services import ToolsConfigService, ThemesService

tools_bp = Blueprint('tools', __name__)

@tools_bp.route('/api/config/tools', methods=['GET'])
def get_tools_config():
    # ...

@tools_bp.route('/api/themes', methods=['GET'])
def list_themes():
    # ...
```

**Lines Extracted:** ~175 lines

### 4.6 handlers/terminal_handlers.py

**Features:** FEATURE-005 (Interactive Console)

```python
# handlers/terminal_handlers.py
from flask import request
from flask_socketio import emit

from x_ipe.services import session_manager

# Socket SID to Session ID mapping
socket_to_session = {}

def register_terminal_handlers(socketio):
    """Register WebSocket event handlers for terminal."""
    
    @socketio.on('connect')
    def handle_connect():
        # ...
    
    @socketio.on('attach')
    def handle_attach(data):
        # ...
    
    # ... input, resize, disconnect handlers
```

**Lines Extracted:** ~105 lines

### 4.7 handlers/voice_handlers.py

**Features:** FEATURE-021 (Voice Input)

```python
# handlers/voice_handlers.py
from flask import request
from flask_socketio import emit
import os

from x_ipe.services.voice_input_service_v2 import VoiceInputService, is_voice_command

# Global voice service instance
voice_service = None
socket_to_voice_session = {}

def register_voice_handlers(socketio):
    """Register WebSocket event handlers for voice input."""
    # ...
```

**Lines Extracted:** ~160 lines

### 4.8 app.py (Simplified)

After refactoring:

```python
# app.py - Factory Only (~100 lines)
"""Flask Application Factory for X-IPE"""
import os
from pathlib import Path
from flask import Flask
from flask_socketio import SocketIO

from x_ipe.services import SettingsService, ProjectFoldersService, ConfigService
from x_ipe.config import config_by_name

# Load .env from config folder
def load_env_file():
    # ... (keep existing ~15 lines)

load_env_file()

# Global service instances
settings_service = None
project_folders_service = None
config_service = None

# Socket.IO instance
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',
    # ... (keep existing config)
)

def create_app(config=None):
    """Application factory for creating Flask app."""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    # ... (keep existing config loading)
    
    # Initialize services
    global settings_service, project_folders_service, config_service
    # ... (keep existing service init)
    
    # Register Blueprints
    from x_ipe.routes import main_bp, settings_bp, project_bp, ideas_bp, tools_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(ideas_bp)
    app.register_blueprint(tools_bp)
    
    # Initialize Socket.IO
    socketio.init_app(app)
    
    # Register WebSocket handlers
    from x_ipe.handlers import register_terminal_handlers, register_voice_handlers
    register_terminal_handlers(socketio)
    register_voice_handlers(socketio)
    
    return app

if __name__ == '__main__':
    app = create_app()
    from x_ipe.services import session_manager
    session_manager.start_cleanup_task()
```

**Target Size:** ~100 lines (from 1312)

---

## 5. Execution Order

```
1. Create routes/__init__.py (empty initially)
2. Create routes/main_routes.py ← Extract from app.py
3. RUN TESTS
4. Create routes/settings_routes.py ← Extract from app.py  
5. RUN TESTS
6. Create routes/project_routes.py ← Extract from app.py
7. RUN TESTS
8. Create routes/ideas_routes.py ← Extract from app.py
9. RUN TESTS
10. Create routes/tools_routes.py ← Extract from app.py
11. RUN TESTS
12. Create handlers/__init__.py
13. Create handlers/terminal_handlers.py ← Extract from app.py
14. RUN TESTS
15. Create handlers/voice_handlers.py ← Extract from app.py
16. RUN TESTS
17. Simplify app.py to factory only
18. RUN TESTS
19. Final validation
```

---

## 6. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Import cycles | Use current_app for service access |
| Global state issues | Pass services via app.config |
| WebSocket breakage | Test terminal/voice after each handler extraction |
| Test failures | Git checkpoint before each phase |

---

## 7. Summary

| Metric | Before | After |
|--------|--------|-------|
| app.py lines | 1312 | ~100 |
| Route files | 0 | 5 |
| Handler files | 0 | 2 |
| SRP violations | 6+ | 0 |
| Module cohesion | Low | High |

**Principles Applied:**
- SRP: 7 extractions
- SoC: Routes separated from handlers
- Modular Design: Reusable blueprints

**Approve this plan to proceed with execution?**
