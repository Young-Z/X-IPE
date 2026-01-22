"""
Flask Application for Document Viewer

FEATURE-001: Project Navigation
- Provides API for project structure
- HTTP polling for real-time updates (no WebSocket)
- Serves frontend with sidebar navigation

FEATURE-005: Interactive Console v4.0
- WebSocket handlers for terminal I/O
- Session persistence with automatic reconnection
- xterm.js frontend integration
"""
import os
import sys
from flask import Flask, render_template, jsonify, request, current_app
from flask_socketio import SocketIO, emit

from src.services import ProjectService, ContentService, SettingsService, ProjectFoldersService
from src.services import session_manager
from src.config import config_by_name

# Global settings service instance
settings_service = None

# Global project folders service instance (FEATURE-006 v2.0)
project_folders_service = None

# Socket.IO instance with ping/pong for keep-alive
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,         # Wait 60s for pong response
    ping_interval=25,        # Send ping every 25s
    max_http_buffer_size=1e8,  # 100MB max message size
    always_connect=True,     # Always emit connect even on reconnect
    logger=False,
    engineio_logger=False
)

# Socket SID to Session ID mapping
socket_to_session = {}


def create_app(config=None):
    """
    Application factory for creating Flask app.
    
    Args:
        config: Configuration dict or config class name
    """
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='templates')
    
    # Load configuration
    if config is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    elif isinstance(config, dict):
        app.config.update(config)
    else:
        app.config.from_object(config)
    
    # Initialize settings service
    global settings_service, project_folders_service
    db_path = app.config.get('SETTINGS_DB_PATH', app.config.get('SETTINGS_DB', os.path.join(app.instance_path, 'settings.db')))
    settings_service = SettingsService(db_path)
    project_folders_service = ProjectFoldersService(db_path)
    
    # Apply project_root from settings if not overridden by config
    saved_root = settings_service.get('project_root')
    if saved_root and saved_root != '.' and not app.config.get('TESTING'):
        # Only apply if it's a valid path
        if os.path.exists(saved_root) and os.path.isdir(saved_root):
            app.config['PROJECT_ROOT'] = saved_root
    
    # Register routes
    register_routes(app)
    register_settings_routes(app)
    register_project_routes(app)
    
    # Initialize Socket.IO with the app
    socketio.init_app(app)
    
    # Register WebSocket handlers for terminal
    register_terminal_handlers()
    
    return app


def register_routes(app):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        """Serve main page with sidebar navigation"""
        return render_template('index.html')
    
    @app.route('/api/project/structure')
    def get_project_structure():
        """
        GET /api/project/structure
        
        Returns the project folder structure for sidebar navigation.
        """
        project_root = app.config.get('PROJECT_ROOT')
        
        if not project_root or not os.path.exists(project_root):
            return jsonify({
                'error': 'Project root not configured or does not exist',
                'project_root': project_root
            }), 400
        
        service = ProjectService(project_root)
        structure = service.get_structure()
        
        return jsonify(structure)
    
    @app.route('/api/file/content')
    def get_file_content():
        """
        GET /api/file/content?path=<relative_path>
        
        Returns the content of a file with metadata for rendering.
        """
        file_path = request.args.get('path')
        
        if not file_path:
            return jsonify({'error': 'Path parameter required'}), 400
        
        project_root = app.config.get('PROJECT_ROOT')
        
        try:
            service = ContentService(project_root)
            result = service.get_content(file_path)
            return jsonify(result)
        except FileNotFoundError:
            return jsonify({'error': 'File not found'}), 404
        except PermissionError:
            return jsonify({'error': 'Access denied'}), 403
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/file/save', methods=['POST'])
    def save_file():
        """
        POST /api/file/save
        
        Save content to a file. Request body: {path: string, content: string}
        
        FEATURE-003: Content Editor
        """
        # Check for JSON body
        if not request.is_json:
            return jsonify({'success': False, 'error': 'JSON body required'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400
        
        if 'path' not in data:
            return jsonify({'success': False, 'error': 'Path is required'}), 400
        
        if 'content' not in data:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        project_root = app.config.get('PROJECT_ROOT')
        
        if not project_root or not os.path.exists(project_root):
            return jsonify({'success': False, 'error': 'Project root not configured'}), 400
        
        service = ContentService(project_root)
        result = service.save_content(data['path'], data['content'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400


# =============================================================================
# FEATURE-005: Interactive Console v4.0 - WebSocket Handlers
# =============================================================================

def register_terminal_handlers():
    """Register WebSocket event handlers for terminal."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle new WebSocket connection."""
        sid = request.sid
        print(f"[Terminal] Client connected: {sid}")
    
    @socketio.on('attach')
    def handle_attach(data):
        """
        Handle session attachment.
        Creates new session or reconnects to existing one.
        """
        sid = request.sid
        requested_session_id = data.get('session_id') if data else None
        # Ensure rows/cols are valid integers with defaults
        rows = data.get('rows') if data else None
        cols = data.get('cols') if data else None
        rows = int(rows) if rows is not None else 24
        cols = int(cols) if cols is not None else 80
        
        def emit_output(output_data):
            socketio.emit('output', output_data, room=sid)
        
        # Try to reconnect to existing session
        if requested_session_id and session_manager.has_session(requested_session_id):
            session = session_manager.get_session(requested_session_id)
            
            if session.is_expired():
                session_manager.remove_session(requested_session_id)
            else:
                # Reconnect to existing session
                session.attach(sid, emit_output)
                socket_to_session[sid] = requested_session_id
                
                # Replay buffered output
                buffer = session.get_buffer()
                if buffer:
                    socketio.emit('output', buffer, room=sid)
                
                socketio.emit('reconnected', {'session_id': requested_session_id}, room=sid)
                return
        
        # Create new session
        session_id = session_manager.create_session(emit_output, rows, cols)
        session = session_manager.get_session(session_id)
        session.attach(sid, emit_output)
        socket_to_session[sid] = session_id
        
        socketio.emit('session_id', session_id, room=sid)
        socketio.emit('new_session', {'session_id': session_id}, room=sid)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle WebSocket disconnection - keep session alive."""
        sid = request.sid
        session_id = socket_to_session.pop(sid, None)
        
        if session_id:
            session = session_manager.get_session(session_id)
            if session:
                session.detach()  # Keep PTY alive for reconnection
        
        print(f"[Terminal] Client disconnected: {sid}")
    
    @socketio.on('input')
    def handle_input(data):
        """Forward input to PTY."""
        sid = request.sid
        session_id = socket_to_session.get(sid)
        
        if session_id:
            session = session_manager.get_session(session_id)
            if session:
                session.write(data)
    
    @socketio.on('resize')
    def handle_resize(data):
        """Handle terminal resize."""
        sid = request.sid
        session_id = socket_to_session.get(sid)
        
        if session_id:
            session = session_manager.get_session(session_id)
            if session:
                rows = data.get('rows', 24)
                cols = data.get('cols', 80)
                session.resize(rows, cols)


# =============================================================================
# FEATURE-006: Settings & Configuration - Routes
# =============================================================================

def register_settings_routes(app):
    """Register settings API and page routes."""
    
    @app.route('/settings')
    def settings_page():
        """
        GET /settings
        
        Render the settings page.
        """
        global settings_service
        current_settings = settings_service.get_all() if settings_service else {'project_root': '.'}
        return render_template('settings.html', settings=current_settings)
    
    @app.route('/api/settings', methods=['GET'])
    def get_settings():
        """
        GET /api/settings
        
        Get all current settings.
        
        Response:
            - project_root: string - Current project root path
        """
        global settings_service
        if not settings_service:
            return jsonify({'project_root': app.config.get('PROJECT_ROOT', '.')}), 200
        
        return jsonify(settings_service.get_all())
    
    @app.route('/api/settings', methods=['POST'])
    def save_settings():
        """
        POST /api/settings
        
        Save settings.
        
        Request body:
            - project_root: string (optional) - New project root path
        
        Response (success):
            - success: true
            - message: string
        
        Response (error):
            - success: false
            - errors: object with field-specific error messages
        """
        global settings_service, file_watcher
        
        data = request.get_json() or {}
        errors = {}
        
        # Validate project_root if provided
        if 'project_root' in data:
            path = data['project_root']
            path_errors = settings_service.validate_project_root(path)
            errors.update(path_errors)
        
        # Return errors if any
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Save settings
        for key, value in data.items():
            if key in ['project_root']:  # Allowed settings
                settings_service.set(key, value)
        
        # Apply project_root change
        if 'project_root' in data:
            new_path = data['project_root']
            app.config['PROJECT_ROOT'] = new_path
        
        return jsonify({'success': True, 'message': 'Settings saved successfully'})


def register_project_routes(app):
    """
    Register project folder management routes.
    
    FEATURE-006 v2.0: Multi-Project Folder Support
    """
    
    @app.route('/api/projects', methods=['GET'])
    def get_projects():
        """
        GET /api/projects
        
        Get all project folders and active project ID.
        
        Response:
            - projects: array of {id, name, path}
            - active_project_id: number
        """
        global project_folders_service
        if not project_folders_service:
            return jsonify({'projects': [], 'active_project_id': 1}), 200
        
        return jsonify({
            'projects': project_folders_service.get_all(),
            'active_project_id': project_folders_service.get_active_id()
        })
    
    @app.route('/api/projects', methods=['POST'])
    def add_project():
        """
        POST /api/projects
        
        Add a new project folder.
        
        Request body:
            - name: string - Project name
            - path: string - Project path
        
        Response (success):
            - success: true
            - project: {id, name, path}
        
        Response (error):
            - success: false
            - errors: object with field-specific error messages
        """
        global project_folders_service
        
        if not request.is_json:
            return jsonify({'success': False, 'error': 'JSON required'}), 400
        
        data = request.get_json()
        name = data.get('name', '').strip()
        path = data.get('path', '').strip()
        
        result = project_folders_service.add(name, path)
        
        if result['success']:
            return jsonify(result), 201
        return jsonify(result), 400
    
    @app.route('/api/projects/<int:project_id>', methods=['PUT'])
    def update_project(project_id):
        """
        PUT /api/projects/<id>
        
        Update an existing project folder.
        
        Request body:
            - name: string (optional) - New project name
            - path: string (optional) - New project path
        
        Response (success):
            - success: true
            - project: {id, name, path}
        
        Response (error):
            - success: false
            - errors: object with field-specific error messages
        """
        global project_folders_service
        
        if not request.is_json:
            return jsonify({'success': False, 'error': 'JSON required'}), 400
        
        data = request.get_json()
        name = data.get('name')
        path = data.get('path')
        
        result = project_folders_service.update(project_id, name=name, path=path)
        
        if result['success']:
            return jsonify(result)
        return jsonify(result), 400
    
    @app.route('/api/projects/<int:project_id>', methods=['DELETE'])
    def delete_project(project_id):
        """
        DELETE /api/projects/<id>
        
        Delete a project folder.
        
        Response (success):
            - success: true
        
        Response (error):
            - success: false
            - error: string error message
        """
        global project_folders_service
        
        active_id = project_folders_service.get_active_id()
        result = project_folders_service.delete(project_id, active_project_id=active_id)
        
        if result['success']:
            return jsonify(result)
        return jsonify(result), 400
    
    @app.route('/api/projects/switch', methods=['POST'])
    def switch_project():
        """
        POST /api/projects/switch
        
        Switch the active project.
        
        Request body:
            - project_id: number - Project ID to switch to
        
        Response (success):
            - success: true
            - active_project_id: number
            - project: {id, name, path}
        
        Response (error):
            - success: false
            - error: string error message
        """
        global project_folders_service
        
        if not request.is_json:
            return jsonify({'success': False, 'error': 'JSON required'}), 400
        
        data = request.get_json()
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({'success': False, 'error': 'project_id required'}), 400
        
        result = project_folders_service.set_active(project_id)
        
        if result['success']:
            # Update app config with new project root
            project = result['project']
            app.config['PROJECT_ROOT'] = project['path']
            
            return jsonify(result)
        return jsonify(result), 400


# Entry point for running with `python -m src.app`
if __name__ == '__main__':
    app = create_app()
    # Start session cleanup task
    session_manager.start_cleanup_task()
    # Use socketio.run for WebSocket support
    socketio.run(app, debug=True, host='0.0.0.0', port=5858)