"""
Flask Application Factory for X-IPE

This module provides the application factory pattern for creating Flask apps.
Route handling is delegated to Blueprint modules in x_ipe.routes.
WebSocket handling is delegated to handler modules in x_ipe.handlers.

Features:
- FEATURE-001: Project Navigation (via routes/main_routes.py)
- FEATURE-003: Content Editor (via routes/main_routes.py)
- FEATURE-005: Interactive Console (via handlers/terminal_handlers.py)
- FEATURE-006: Settings & Projects (via routes/settings_routes.py, project_routes.py)
- FEATURE-008: Workplace (via routes/ideas_routes.py)
- FEATURE-010: Project Config (via routes/settings_routes.py)
- FEATURE-011: Stage Toolbox (via routes/tools_routes.py)
- FEATURE-012: Design Themes (via routes/tools_routes.py)
- FEATURE-021: Voice Input (via handlers/voice_handlers.py)
"""
import os
from pathlib import Path
from flask import Flask
from flask_socketio import SocketIO

from x_ipe.services import SettingsService, ProjectFoldersService, ConfigService
from x_ipe.services import session_manager
from x_ipe.config import config_by_name


def load_env_file():
    """Load environment variables from x-ipe-docs/config/.env file."""
    env_path = Path(__file__).parent.parent.parent / 'x-ipe-docs' / 'config' / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if value and key not in os.environ:
                        os.environ[key] = value


# Load environment variables on module import
load_env_file()

# Socket.IO instance with ping/pong for keep-alive
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=300,
    ping_interval=60,
    max_http_buffer_size=1e8,
    always_connect=True,
    logger=False,
    engineio_logger=False,
    http_compression=True,
    manage_session=True,
)


def create_app(config=None):
    """
    Application factory for creating Flask app.
    
    Args:
        config: Configuration dict or config class name
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    if config is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    elif isinstance(config, dict):
        app.config.update(config)
    else:
        app.config.from_object(config)
    
    # Initialize services
    _init_services(app)
    
    # Register Blueprints
    _register_blueprints(app)
    
    # Initialize Socket.IO
    socketio.init_app(app)
    
    # Register WebSocket handlers
    _register_handlers()
    
    return app


def _init_services(app):
    """Initialize application services and store in app.config."""
    db_path = app.config.get(
        'SETTINGS_DB_PATH', 
        app.config.get('SETTINGS_DB', os.path.join(app.instance_path, 'settings.db'))
    )
    
    # Create service instances
    settings_service = SettingsService(db_path)
    project_folders_service = ProjectFoldersService(db_path)
    
    # Store services in app.config for Blueprint access
    app.config['SETTINGS_SERVICE'] = settings_service
    app.config['PROJECT_FOLDERS_SERVICE'] = project_folders_service
    
    # Initialize config service and load .x-ipe.yaml (FEATURE-010)
    if not app.config.get('TESTING'):
        config_service = ConfigService()
        config_data = config_service.load()
        if config_data:
            app.config['X_IPE_CONFIG'] = config_data
            app.config['PROJECT_ROOT'] = config_data.get_file_tree_path()
    
    # Apply project_root from settings only if no .x-ipe.yaml detected
    if not app.config.get('X_IPE_CONFIG'):
        saved_root = settings_service.get('project_root')
        if saved_root and saved_root != '.' and not app.config.get('TESTING'):
            if os.path.exists(saved_root) and os.path.isdir(saved_root):
                app.config['PROJECT_ROOT'] = saved_root


def _register_blueprints(app):
    """Register all Flask Blueprints."""
    from x_ipe.routes import main_bp, settings_bp, project_bp, ideas_bp, tools_bp, proxy_bp
    from x_ipe.routes.uiux_feedback_routes import uiux_feedback_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(ideas_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(proxy_bp)
    app.register_blueprint(uiux_feedback_bp)


def _register_handlers():
    """Register all WebSocket handlers."""
    from x_ipe.handlers import register_terminal_handlers, register_voice_handlers
    
    register_terminal_handlers(socketio)
    register_voice_handlers(socketio)


# Entry point for running directly
if __name__ == '__main__':
    app = create_app()
    session_manager.start_cleanup_task()
    socketio.run(app, debug=True, host='0.0.0.0', port=5858)
