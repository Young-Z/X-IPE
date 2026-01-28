"""
Settings Routes Blueprint

FEATURE-006: Settings & Configuration
FEATURE-010: Project Root Configuration

Provides:
- Settings page
- Settings API (GET/POST)
- Config API
"""
import os
from flask import Blueprint, render_template, jsonify, request, current_app

settings_bp = Blueprint('settings', __name__)


def get_settings_service():
    """Get settings service from app config."""
    return current_app.config.get('SETTINGS_SERVICE')


@settings_bp.route('/settings')
def settings_page():
    """
    GET /settings
    
    Render the settings page.
    """
    settings_service = get_settings_service()
    current_settings = settings_service.get_all() if settings_service else {'project_root': '.'}
    return render_template('settings.html', settings=current_settings)


@settings_bp.route('/api/settings', methods=['GET'])
def get_settings():
    """
    GET /api/settings
    
    Get all current settings.
    
    Response:
        - project_root: string - Current project root path
    """
    settings_service = get_settings_service()
    if not settings_service:
        return jsonify({'project_root': current_app.config.get('PROJECT_ROOT', '.')}), 200
    
    return jsonify(settings_service.get_all())


@settings_bp.route('/api/settings', methods=['POST'])
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
    settings_service = get_settings_service()
    
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
        current_app.config['PROJECT_ROOT'] = new_path
    
    return jsonify({'success': True, 'message': 'Settings saved successfully'})


@settings_bp.route('/api/config', methods=['GET'])
def get_config():
    """
    GET /api/config
    
    Get current project configuration from .x-ipe.yaml.
    
    FEATURE-010: Project Root Configuration
    
    Response (config detected):
        - detected: true
        - config_file: string - Path to .x-ipe.yaml
        - version: int
        - project_root: string
        - x_ipe_app: string
        - file_tree_scope: string
        - terminal_cwd: string
    
    Response (no config):
        - detected: false
        - config_file: null
        - using_defaults: true
        - project_root: string - Current project root
        - message: string
    """
    config_data = current_app.config.get('X_IPE_CONFIG')
    
    if config_data:
        return jsonify({
            'detected': True,
            **config_data.to_dict()
        })
    else:
        return jsonify({
            'detected': False,
            'config_file': None,
            'using_defaults': True,
            'project_root': current_app.config.get('PROJECT_ROOT', os.getcwd()),
            'message': 'No .x-ipe.yaml found. Using default paths.'
        })
