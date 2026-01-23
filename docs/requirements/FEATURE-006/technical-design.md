# Technical Design: Settings & Configuration

> Feature ID: FEATURE-006 | Version: v2.0 | Last Updated: 01-20-2026

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v2.0 | 01-20-2026 | Multi-Project Support: ProjectFoldersService, project_folders table, project switcher dropdown, /api/projects endpoints |
| v1.0 | 01-19-2026 | Initial design: SettingsService, SQLite persistence, /api/settings endpoints, settings page |

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating large projects.
> **📌 AI Coders:** Focus on this section for implementation context.

### What's New in v2.0

- **ProjectFoldersService:** Manage list of project folders (CRUD)
- **Project Switcher:** Dropdown in doc viewer header to switch active project
- **New API Endpoints:** `/api/projects`, `/api/projects/<id>`, `/api/projects/switch`
- **Database Migration:** New `project_folders` table, `active_project_id` setting

### Key Components to Implement

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| `ProjectFoldersService` | CRUD for project folders list | Backend service | #sqlite #persistence #service |
| `/api/projects` endpoints | REST API for project folders | API routes | #api #rest #projects |
| `/api/projects/switch` | Switch active project | API endpoint | #api #project-switch |
| Settings page (updated) | Project folders table with add/edit/remove | Frontend HTML | #frontend #ui #settings |
| `ProjectSwitcher` | Dropdown component in doc viewer header | Frontend module | #frontend #javascript #dropdown |

### Scope & Boundaries

**In Scope:**
- `project_folders` table for storing multiple projects (name + path)
- `ProjectFoldersService` with add, update, delete, get_all methods
- REST API endpoints for project folder management
- Project switcher dropdown in doc viewer header
- Auto-refresh sidebar when switching projects
- Active project persistence (`active_project_id` setting)
- Default project "Default Project Folder" → "."
- Validation for project name (unique, non-empty) and path (exists, directory)

**Out of Scope:**
- Drag-and-drop reordering
- Project icons/colors
- Project grouping/categories

### Dependencies

| Dependency | Source | Design Link | Usage Description |
|------------|--------|-------------|-------------------|
| `ProjectService` | FEATURE-001 | [technical-design.md](../FEATURE-001/technical-design.md) | Re-initialize when switching projects |
| `FileWatcher` | FEATURE-001 | [technical-design.md](../FEATURE-001/technical-design.md) | Restart watching new directory |
| `SettingsService` | FEATURE-006 v1.0 | Current file | Store `active_project_id` |
| Flask | External | flask.palletsprojects.com | Web framework |
| SQLite3 | Python stdlib | docs.python.org | Settings persistence |

### Major Flows

**Flow 1: Add Project Folder**
1. User clicks "+ Add" in settings
2. Modal shows with name/path inputs
3. User submits → POST `/api/projects` 
4. Backend validates name (unique) + path (exists, is dir)
5. Success → project added to list, UI updates

**Flow 2: Switch Project**
1. User clicks project dropdown in header
2. User selects different project
3. POST `/api/projects/switch` with `project_id`
4. Backend updates `active_project_id` setting
5. Response includes project path
6. Frontend reloads sidebar with new project structure
7. Content area shows placeholder

### Usage Example

```python
# Backend: ProjectFoldersService
from src.services import ProjectFoldersService

service = ProjectFoldersService('instance/settings.db')

# Get all project folders
projects = service.get_all()
# [{'id': 1, 'name': 'Default Project Folder', 'path': '.'}]

# Add project folder
result = service.add('AI Agent', '/Users/dev/agent')
# {'success': True, 'project': {'id': 2, ...}}

# Update project folder
result = service.update(2, name='AI Agent v2', path='/Users/dev/agent-v2')

# Delete project folder
result = service.delete(2)

# Get/Set active project
active_id = service.get_active_id()
service.set_active(2)
```

```javascript
// Frontend: ProjectSwitcher
class ProjectSwitcher {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.projects = [];
        this.activeProjectId = null;
    }
    
    async load() {
        const response = await fetch('/api/projects');
        const data = await response.json();
        this.projects = data.projects;
        this.activeProjectId = data.active_project_id;
        this.render();
    }
    
    async switchProject(projectId) {
        const response = await fetch('/api/projects/switch', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({project_id: projectId})
        });
        if (response.ok) {
            this.activeProjectId = projectId;
            this.render();
            // Reload sidebar
            window.projectSidebar.load();
            // Clear content
            window.contentRenderer.showPlaceholder();
        }
    }
}
```

### Database Schema

```sql
-- instance/settings.db

-- Existing settings table (add active_project_id)
-- Key: 'active_project_id', Value: '1'

-- New project_folders table
CREATE TABLE IF NOT EXISTS project_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default data (created on first run)
INSERT OR IGNORE INTO project_folders (id, name, path) 
VALUES (1, 'Default Project Folder', '.');

INSERT OR IGNORE INTO settings (key, value) 
VALUES ('active_project_id', '1');
```

---

## Part 2: Implementation Guide

### Component 1: ProjectFoldersService

**File:** `src/services/settings_service.py`

```python
class ProjectFoldersService:
    """
    Service for managing project folders with SQLite persistence.
    
    FEATURE-006 v2.0: Multi-Project Folder Support
    """
    
    def __init__(self, db_path: str = 'instance/settings.db'):
        self.db_path = db_path
        self._ensure_table()
        self._ensure_default_project()
    
    def _ensure_table(self) -> None:
        """Create project_folders table if not exists."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()
    
    def _ensure_default_project(self) -> None:
        """Ensure default project folder exists."""
        if not self.get_all():
            self.add('Default Project Folder', '.')
    
    def get_all(self) -> List[Dict]:
        """Get all project folders."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, path FROM project_folders ORDER BY id')
            return [{'id': r[0], 'name': r[1], 'path': r[2]} for r in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_by_id(self, project_id: int) -> Optional[Dict]:
        """Get project folder by ID."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, path FROM project_folders WHERE id = ?', (project_id,))
            row = cursor.fetchone()
            return {'id': row[0], 'name': row[1], 'path': row[2]} if row else None
        finally:
            conn.close()
    
    def add(self, name: str, path: str) -> Dict:
        """Add a new project folder."""
        # Validate
        errors = self._validate(name, path)
        if errors:
            return {'success': False, 'errors': errors}
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO project_folders (name, path) VALUES (?, ?)',
                (name.strip(), path.strip())
            )
            conn.commit()
            project_id = cursor.lastrowid
            return {
                'success': True,
                'project': {'id': project_id, 'name': name.strip(), 'path': path.strip()}
            }
        except sqlite3.IntegrityError:
            return {'success': False, 'errors': {'name': 'A project with this name already exists'}}
        finally:
            conn.close()
    
    def update(self, project_id: int, name: str = None, path: str = None) -> Dict:
        """Update an existing project folder."""
        existing = self.get_by_id(project_id)
        if not existing:
            return {'success': False, 'error': 'Project not found'}
        
        new_name = name.strip() if name else existing['name']
        new_path = path.strip() if path else existing['path']
        
        # Validate
        errors = self._validate(new_name, new_path, exclude_id=project_id)
        if errors:
            return {'success': False, 'errors': errors}
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE project_folders SET name = ?, path = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (new_name, new_path, project_id)
            )
            conn.commit()
            return {
                'success': True,
                'project': {'id': project_id, 'name': new_name, 'path': new_path}
            }
        except sqlite3.IntegrityError:
            return {'success': False, 'errors': {'name': 'A project with this name already exists'}}
        finally:
            conn.close()
    
    def delete(self, project_id: int, active_project_id: int = None) -> Dict:
        """Delete a project folder."""
        # Check if only one project
        all_projects = self.get_all()
        if len(all_projects) <= 1:
            return {'success': False, 'error': 'Cannot remove the last project folder'}
        
        # Check if trying to delete active project
        if active_project_id and project_id == active_project_id:
            return {'success': False, 'error': 'Switch to another project before deleting this one'}
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM project_folders WHERE id = ?', (project_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return {'success': False, 'error': 'Project not found'}
            return {'success': True}
        finally:
            conn.close()
    
    def _validate(self, name: str, path: str, exclude_id: int = None) -> Dict:
        """Validate project name and path."""
        errors = {}
        
        # Name validation
        if not name or not name.strip():
            errors['name'] = 'Project name is required'
        
        # Path validation
        if not path or not path.strip():
            errors['path'] = 'Project path is required'
        elif not os.path.exists(path):
            errors['path'] = 'The specified path does not exist'
        elif not os.path.isdir(path):
            errors['path'] = 'The specified path is not a directory'
        elif not os.access(path, os.R_OK):
            errors['path'] = 'The application does not have read access to this directory'
        
        return errors
    
    def get_active_id(self) -> int:
        """Get the active project ID from settings."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'active_project_id'")
            row = cursor.fetchone()
            return int(row[0]) if row else 1
        finally:
            conn.close()
    
    def set_active(self, project_id: int) -> Dict:
        """Set the active project ID."""
        # Verify project exists
        project = self.get_by_id(project_id)
        if not project:
            return {'success': False, 'error': 'Project not found'}
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO settings (key, value, updated_at)
                VALUES ('active_project_id', ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP
            ''', (str(project_id), str(project_id)))
            conn.commit()
            return {'success': True, 'active_project_id': project_id, 'project': project}
        finally:
            conn.close()
```

### Component 2: API Endpoints

**File:** `src/app.py`

```python
def register_project_routes(app):
    """Register project folder API routes."""
    
    @app.route('/api/projects', methods=['GET'])
    def get_projects():
        """Get all project folders and active project."""
        db_path = app.config.get('SETTINGS_DB', 'instance/settings.db')
        service = ProjectFoldersService(db_path)
        
        return jsonify({
            'projects': service.get_all(),
            'active_project_id': service.get_active_id()
        })
    
    @app.route('/api/projects', methods=['POST'])
    def add_project():
        """Add a new project folder."""
        if not request.is_json:
            return jsonify({'success': False, 'error': 'JSON required'}), 400
        
        data = request.get_json()
        name = data.get('name', '').strip()
        path = data.get('path', '').strip()
        
        db_path = app.config.get('SETTINGS_DB', 'instance/settings.db')
        service = ProjectFoldersService(db_path)
        result = service.add(name, path)
        
        if result['success']:
            return jsonify(result), 201
        return jsonify(result), 400
    
    @app.route('/api/projects/<int:project_id>', methods=['PUT'])
    def update_project(project_id):
        """Update an existing project folder."""
        if not request.is_json:
            return jsonify({'success': False, 'error': 'JSON required'}), 400
        
        data = request.get_json()
        name = data.get('name')
        path = data.get('path')
        
        db_path = app.config.get('SETTINGS_DB', 'instance/settings.db')
        service = ProjectFoldersService(db_path)
        result = service.update(project_id, name=name, path=path)
        
        if result['success']:
            return jsonify(result)
        return jsonify(result), 400
    
    @app.route('/api/projects/<int:project_id>', methods=['DELETE'])
    def delete_project(project_id):
        """Delete a project folder."""
        db_path = app.config.get('SETTINGS_DB', 'instance/settings.db')
        service = ProjectFoldersService(db_path)
        active_id = service.get_active_id()
        result = service.delete(project_id, active_project_id=active_id)
        
        if result['success']:
            return jsonify(result)
        return jsonify(result), 400
    
    @app.route('/api/projects/switch', methods=['POST'])
    def switch_project():
        """Switch the active project."""
        if not request.is_json:
            return jsonify({'success': False, 'error': 'JSON required'}), 400
        
        data = request.get_json()
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({'success': False, 'error': 'project_id required'}), 400
        
        db_path = app.config.get('SETTINGS_DB', 'instance/settings.db')
        service = ProjectFoldersService(db_path)
        result = service.set_active(project_id)
        
        if result['success']:
            # Update app config with new project root
            project = result['project']
            app.config['PROJECT_ROOT'] = project['path']
            return jsonify(result)
        return jsonify(result), 400
```

### Component 3: Project Switcher (Frontend)

**File:** `src/templates/index.html` (add to header)

```html
<!-- Project Switcher Dropdown -->
<div class="project-switcher dropdown me-2" id="project-switcher">
    <button class="btn btn-outline-secondary dropdown-toggle" 
            type="button" id="projectDropdown" 
            data-bs-toggle="dropdown" aria-expanded="false">
        <i class="bi bi-folder"></i>
        <span class="project-name">Loading...</span>
    </button>
    <ul class="dropdown-menu" aria-labelledby="projectDropdown">
        <!-- Populated by JavaScript -->
    </ul>
</div>
```

```javascript
class ProjectSwitcher {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.button = this.container.querySelector('.dropdown-toggle');
        this.menu = this.container.querySelector('.dropdown-menu');
        this.projectNameSpan = this.button.querySelector('.project-name');
        this.projects = [];
        this.activeProjectId = null;
        
        this.load();
    }
    
    async load() {
        try {
            const response = await fetch('/api/projects');
            const data = await response.json();
            this.projects = data.projects;
            this.activeProjectId = data.active_project_id;
            this.render();
        } catch (error) {
            console.error('Failed to load projects:', error);
        }
    }
    
    render() {
        // Update button text
        const activeProject = this.projects.find(p => p.id === this.activeProjectId);
        this.projectNameSpan.textContent = activeProject ? activeProject.name : 'Select Project';
        
        // Render dropdown items
        this.menu.innerHTML = this.projects.map(project => `
            <li>
                <a class="dropdown-item ${project.id === this.activeProjectId ? 'active' : ''}" 
                   href="#" data-project-id="${project.id}">
                    ${project.id === this.activeProjectId ? '<i class="bi bi-check me-2"></i>' : ''}
                    ${this.escapeHtml(project.name)}
                </a>
            </li>
        `).join('');
        
        // Add event listeners
        this.menu.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const projectId = parseInt(item.dataset.projectId);
                if (projectId !== this.activeProjectId) {
                    this.switchProject(projectId);
                }
            });
        });
    }
    
    async switchProject(projectId) {
        try {
            const response = await fetch('/api/projects/switch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({project_id: projectId})
            });
            
            if (response.ok) {
                const data = await response.json();
                this.activeProjectId = data.active_project_id;
                this.render();
                
                // Refresh sidebar
                if (window.projectSidebar) {
                    window.projectSidebar.load();
                }
                
                // Clear content area
                if (window.contentRenderer) {
                    window.contentRenderer.showPlaceholder();
                }
                
                // Show toast
                this.showToast(`Switched to ${data.project.name}`);
            }
        } catch (error) {
            console.error('Failed to switch project:', error);
            this.showToast('Failed to switch project', 'error');
        }
    }
    
    showToast(message, type = 'success') {
        // Use existing toast mechanism
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `<i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}`;
        container.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
```

### Component 4: Settings Page Update

**File:** `src/templates/settings.html` (replace project root section)

```html
<!-- Project Folders Section -->
<div class="card mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><i class="bi bi-folder me-2"></i>Project Folders</h5>
        <button class="btn btn-primary btn-sm" id="btn-add-project">
            <i class="bi bi-plus"></i> Add Project
        </button>
    </div>
    <div class="card-body">
        <table class="table table-hover" id="projects-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Path</th>
                    <th style="width: 120px;">Actions</th>
                </tr>
            </thead>
            <tbody id="projects-list">
                <!-- Populated by JavaScript -->
            </tbody>
        </table>
    </div>
</div>

<!-- Add/Edit Project Modal -->
<div class="modal fade" id="projectModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="projectModalTitle">Add Project Folder</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="project-form">
                    <input type="hidden" id="project-id">
                    <div class="mb-3">
                        <label class="form-label">Project Name</label>
                        <input type="text" class="form-control" id="project-name" required>
                        <div class="invalid-feedback" id="name-error"></div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Project Path</label>
                        <input type="text" class="form-control" id="project-path" required>
                        <div class="form-text">Absolute path to the project directory</div>
                        <div class="invalid-feedback" id="path-error"></div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="btn-save-project">Save</button>
            </div>
        </div>
    </div>
</div>
```

---

## Part 3: API Reference

### GET /api/projects

**Response (200):**
```json
{
    "projects": [
        {"id": 1, "name": "Default Project Folder", "path": "."},
        {"id": 2, "name": "AI Agent", "path": "/Users/dev/agent"}
    ],
    "active_project_id": 1
}
```

### POST /api/projects

**Request:**
```json
{"name": "New Project", "path": "/path/to/project"}
```

**Response (201):**
```json
{
    "success": true,
    "project": {"id": 3, "name": "New Project", "path": "/path/to/project"}
}
```

**Response (400):**
```json
{
    "success": false,
    "errors": {"path": "The specified path does not exist"}
}
```

### PUT /api/projects/:id

**Request:**
```json
{"name": "Updated Name", "path": "/new/path"}
```

**Response (200):**
```json
{
    "success": true,
    "project": {"id": 2, "name": "Updated Name", "path": "/new/path"}
}
```

### DELETE /api/projects/:id

**Response (200):**
```json
{"success": true}
```

**Response (400):**
```json
{"success": false, "error": "Cannot remove the last project folder"}
```

### POST /api/projects/switch

**Request:**
```json
{"project_id": 2}
```

**Response (200):**
```json
{
    "success": true,
    "active_project_id": 2,
    "project": {"id": 2, "name": "AI Agent", "path": "/Users/dev/agent"}
}
```

---

## Part 4: Testing Checklist

### Unit Tests (ProjectFoldersService)
- [ ] `test_get_all_returns_projects_list`
- [ ] `test_get_all_creates_default_on_empty`
- [ ] `test_add_project_success`
- [ ] `test_add_project_duplicate_name_fails`
- [ ] `test_add_project_invalid_path_fails`
- [ ] `test_add_project_empty_name_fails`
- [ ] `test_update_project_success`
- [ ] `test_update_project_not_found`
- [ ] `test_delete_project_success`
- [ ] `test_delete_last_project_fails`
- [ ] `test_delete_active_project_fails`
- [ ] `test_get_active_id_default`
- [ ] `test_set_active_success`
- [ ] `test_set_active_invalid_id_fails`

### API Tests
- [ ] `test_get_projects_returns_list`
- [ ] `test_post_projects_creates_project`
- [ ] `test_post_projects_validation_errors`
- [ ] `test_put_project_updates`
- [ ] `test_delete_project_removes`
- [ ] `test_switch_project_updates_active`
- [ ] `test_switch_invalid_project_fails`

### Integration Tests
- [ ] `test_switch_project_updates_sidebar`
- [ ] `test_add_project_appears_in_dropdown`
- [ ] `test_active_project_persists_across_refresh`
