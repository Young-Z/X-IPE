"""
Tools Routes Blueprint

FEATURE-011: Stage Toolbox
FEATURE-012: Design Themes

Provides:
- Tools configuration API
- Copilot prompt configuration
- Themes list and detail API
"""
import os
import json
from flask import Blueprint, jsonify, request, current_app

from x_ipe.services import ToolsConfigService, ThemesService

tools_bp = Blueprint('tools', __name__)


def _get_tools_service():
    """Get ToolsConfigService instance for current project root."""
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    return ToolsConfigService(project_root)


def _get_themes_service():
    """Get ThemesService instance for current project root."""
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    return ThemesService(project_root)


@tools_bp.route('/api/config/tools', methods=['GET'])
def get_tools_config():
    """
    GET /api/config/tools
    
    Get current tools configuration.
    
    Response:
        - success: true
        - config: tools configuration object
    """
    try:
        service = _get_tools_service()
        config = service.load()
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tools_bp.route('/api/config/tools', methods=['POST'])
def save_tools_config():
    """
    POST /api/config/tools
    
    Save tools configuration.
    
    Request Body: JSON with 'stages' key
    
    Response:
        - success: true/false
        - error: string (on failure)
    """
    try:
        config = request.get_json(force=True, silent=True)
        if config is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON or empty body'
            }), 400
        
        if 'stages' not in config:
            return jsonify({
                'success': False,
                'error': 'Invalid config format: missing stages key'
            }), 400
        
        service = _get_tools_service()
        service.save(config)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tools_bp.route('/api/config/copilot-prompt', methods=['GET'])
def get_copilot_prompt_config():
    """
    GET /api/config/copilot-prompt
    
    Get Copilot prompt configuration for the Copilot button dropdown.
    
    Response:
        - prompts: List of prompt objects with id, label, icon, command
        - placeholder: Dictionary of placeholder descriptions
    """
    try:
        project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
        config_path = os.path.join(project_root, 'x-ipe-docs', 'config', 'copilot-prompt.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return jsonify(config)
        else:
            # Return empty prompts if config doesn't exist
            return jsonify({
                'version': '1.0',
                'prompts': [],
                'placeholder': {}
            })
    except Exception as e:
        return jsonify({
            'prompts': [],
            'error': str(e)
        }), 500


# ============================================================
# FEATURE-012: Design Themes API
# ============================================================

@tools_bp.route('/api/themes', methods=['GET'])
def list_themes():
    """
    GET /api/themes
    
    List all themes with metadata.
    
    Response:
        - themes: List of theme objects with name, description, colors, files, path
        - selected: Currently selected theme name from config (null if none)
    """
    try:
        themes_service = _get_themes_service()
        themes = themes_service.list_themes()
        
        # Get selected theme from tools config (new format)
        tools_service = _get_tools_service()
        config = tools_service.load()
        selected_theme_config = config.get('selected-theme', {})
        selected = selected_theme_config.get('theme-name') if selected_theme_config else None
        
        return jsonify({
            'themes': themes,
            'selected': selected
        })
    except Exception as e:
        return jsonify({
            'themes': [],
            'selected': 'theme-default',
            'error': str(e)
        }), 500


@tools_bp.route('/api/themes/<name>', methods=['GET'])
def get_theme_detail(name):
    """
    GET /api/themes/<name>
    
    Get detailed information about a specific theme.
    
    Args:
        name: Theme folder name (e.g., "theme-default")
        
    Response:
        - Theme detail object with design_system content
        - 404 if theme not found
    """
    try:
        themes_service = _get_themes_service()
        theme = themes_service.get_theme(name)
        
        if theme is None:
            return jsonify({
                'error': f'Theme not found: {name}'
            }), 404
        
        return jsonify(theme)
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
