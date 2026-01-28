"""
Project Routes Blueprint

FEATURE-006 v2.0: Multi-Project Folder Support

Provides:
- List projects
- Add project
- Update project
- Delete project
- Switch active project
"""
import os
from flask import Blueprint, jsonify, request, current_app

project_bp = Blueprint('project', __name__)


def get_project_folders_service():
    """Get project folders service from app config."""
    return current_app.config.get('PROJECT_FOLDERS_SERVICE')


@project_bp.route('/api/projects', methods=['GET'])
def get_projects():
    """
    GET /api/projects
    
    Get all project folders and active project ID.
    
    Response:
        - projects: array of {id, name, path}
        - active_project_id: number
    """
    project_folders_service = get_project_folders_service()
    if not project_folders_service:
        return jsonify({'projects': [], 'active_project_id': 1}), 200
    
    return jsonify({
        'projects': project_folders_service.get_all(),
        'active_project_id': project_folders_service.get_active_id()
    })


@project_bp.route('/api/projects', methods=['POST'])
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
    project_folders_service = get_project_folders_service()
    
    if not request.is_json:
        return jsonify({'success': False, 'error': 'JSON required'}), 400
    
    data = request.get_json()
    name = data.get('name', '').strip()
    path = data.get('path', '').strip()
    
    result = project_folders_service.add(name, path)
    
    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 400


@project_bp.route('/api/projects/<int:project_id>', methods=['PUT'])
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
    project_folders_service = get_project_folders_service()
    
    if not request.is_json:
        return jsonify({'success': False, 'error': 'JSON required'}), 400
    
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')
    
    result = project_folders_service.update(project_id, name=name, path=path)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@project_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
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
    project_folders_service = get_project_folders_service()
    
    active_id = project_folders_service.get_active_id()
    result = project_folders_service.delete(project_id, active_project_id=active_id)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@project_bp.route('/api/projects/switch', methods=['POST'])
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
    project_folders_service = get_project_folders_service()
    
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
        project_path = project['path']
        
        # If config is detected, project folders are relative to config's project_root
        config_data = current_app.config.get('X_IPE_CONFIG')
        if config_data:
            # Config always takes precedence - use its project_root
            current_app.config['PROJECT_ROOT'] = config_data.project_root
        elif project_path == '.':
            # No config, default project folder - use cwd where x-ipe was run
            current_app.config['PROJECT_ROOT'] = os.environ.get('X_IPE_PROJECT_ROOT', os.getcwd())
        else:
            # Absolute path from project folder
            current_app.config['PROJECT_ROOT'] = project_path
        
        return jsonify(result)
    return jsonify(result), 400
