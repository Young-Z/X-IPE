"""
Ideas Routes Blueprint

FEATURE-008: Workplace (Idea Management)
Skills API

Provides:
- Ideas tree
- Ideas upload
- Ideas rename/delete
- Toolbox config
- Skills list
"""
import os
from flask import Blueprint, jsonify, request, current_app

from x_ipe.services import IdeasService, SkillsService

ideas_bp = Blueprint('ideas', __name__)


@ideas_bp.route('/api/ideas/tree', methods=['GET'])
def get_ideas_tree():
    """
    GET /api/ideas/tree
    
    Get tree structure of x-ipe-docs/ideas/ directory.
    
    Response:
        - success: true
        - tree: array of folder/file objects
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    try:
        tree = service.get_tree()
        return jsonify({
            'success': True,
            'tree': tree
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ideas_bp.route('/api/ideas/upload', methods=['POST'])
def upload_ideas():
    """
    POST /api/ideas/upload
    
    Upload files to a new or existing idea folder.
    
    Request: multipart/form-data with 'files' field
    Optional: 'target_folder' field to upload to existing folder (CR-002)
    
    Response:
        - success: true/false
        - folder_name: string
        - folder_path: string
        - files_uploaded: array of filenames
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    if 'files' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No files provided'
        }), 400
    
    uploaded_files = request.files.getlist('files')
    if not uploaded_files or all(f.filename == '' for f in uploaded_files):
        return jsonify({
            'success': False,
            'error': 'No files provided'
        }), 400
    
    # CR-002: Get optional target_folder from form data
    target_folder = request.form.get('target_folder', None)
    
    # Convert to (filename, content) tuples
    files = [(f.filename, f.read()) for f in uploaded_files if f.filename]
    
    result = service.upload(files, target_folder=target_folder)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/rename', methods=['POST'])
def rename_idea_folder():
    """
    POST /api/ideas/rename
    
    Rename an idea folder.
    
    Request body:
        - old_name: string - Current folder name
        - new_name: string - New folder name
    
    Response:
        - success: true/false
        - old_name: string
        - new_name: string
        - new_path: string
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'JSON required'
        }), 400
    
    data = request.get_json()
    old_name = data.get('old_name')
    new_name = data.get('new_name')
    
    if not old_name or not new_name:
        return jsonify({
            'success': False,
            'error': 'old_name and new_name are required'
        }), 400
    
    result = service.rename_folder(old_name, new_name)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/rename-file', methods=['POST'])
def rename_idea_file():
    """
    POST /api/ideas/rename-file
    
    Rename a file within x-ipe-docs/ideas/.
    
    Request body:
        - path: string - Current file path (relative to project root)
        - new_name: string - New file name (with extension)
    
    Response:
        - success: true/false
        - old_path: string
        - new_path: string
        - new_name: string
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'JSON required'
        }), 400
    
    data = request.get_json()
    path = data.get('path')
    new_name = data.get('new_name')
    
    if not path or not new_name:
        return jsonify({
            'success': False,
            'error': 'path and new_name are required'
        }), 400
    
    result = service.rename_file(path, new_name)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/delete', methods=['POST'])
def delete_idea_item():
    """
    POST /api/ideas/delete
    
    Delete an idea file or folder.
    
    Request body:
        - path: string - Relative path to file/folder within x-ipe-docs/ideas/
    
    Response:
        - success: true/false
        - path: string
        - type: 'file' | 'folder'
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'JSON required'
        }), 400
    
    data = request.get_json()
    path = data.get('path')
    
    if not path:
        return jsonify({
            'success': False,
            'error': 'path is required'
        }), 400
    
    result = service.delete_item(path)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/toolbox', methods=['GET'])
def get_ideas_toolbox():
    """
    GET /api/ideas/toolbox
    
    Get ideation toolbox configuration.
    
    Response:
        - version: string
        - ideation: {antv-infographic: bool, mermaid: bool}
        - mockup: {frontend-design: bool}
        - sharing: {}
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    config = service.get_toolbox()
    return jsonify(config)


@ideas_bp.route('/api/ideas/toolbox', methods=['POST'])
def save_ideas_toolbox():
    """
    POST /api/ideas/toolbox
    
    Save ideation toolbox configuration.
    
    Request body:
        - version: string
        - ideation: {antv-infographic: bool, mermaid: bool}
        - mockup: {frontend-design: bool}
        - sharing: {}
    
    Response:
        - success: true/false
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    config = request.get_json()
    result = service.save_toolbox(config)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


# ==========================================================================
# CR-006: Folder Tree UX Enhancement API Endpoints
# ==========================================================================

@ideas_bp.route('/api/ideas/move', methods=['POST'])
def move_idea_item():
    """
    POST /api/ideas/move
    
    Move a file or folder to a new location.
    
    Request body:
        - source_path: string - Path of item to move
        - target_folder: string - Destination folder path
    
    Response:
        - success: true/false
        - new_path: string
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    if not request.is_json:
        return jsonify({'success': False, 'error': 'JSON required'}), 400
    
    data = request.get_json()
    source_path = data.get('source_path')
    target_folder = data.get('target_folder')
    
    if source_path is None:
        return jsonify({'success': False, 'error': 'source_path is required'}), 400
    
    if target_folder is None:
        return jsonify({'success': False, 'error': 'target_folder is required'}), 400
    
    result = service.move_item(source_path, target_folder)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/duplicate', methods=['POST'])
def duplicate_idea_item():
    """
    POST /api/ideas/duplicate
    
    Duplicate a file or folder with -copy suffix.
    
    Request body:
        - path: string - Path of item to duplicate
    
    Response:
        - success: true/false
        - new_path: string
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    if not request.is_json:
        return jsonify({'success': False, 'error': 'JSON required'}), 400
    
    data = request.get_json()
    path = data.get('path')
    
    if not path:
        return jsonify({'success': False, 'error': 'path is required'}), 400
    
    result = service.duplicate_item(path)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/download', methods=['GET'])
def download_idea_file():
    """
    GET /api/ideas/download?path=...
    
    Download a file from ideas folder.
    
    Query params:
        - path: string - Path of file to download
    
    Response:
        File download with appropriate Content-Type
    """
    from flask import send_file
    import io
    
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    path = request.args.get('path')
    
    if not path:
        return jsonify({'success': False, 'error': 'path is required'}), 400
    
    result = service.get_download_info(path)
    
    if not result['success']:
        # Return 404 for file not found
        status_code = 404 if 'not found' in result['error'].lower() else 400
        return jsonify(result), status_code
    
    # Handle both string and bytes content
    content = result['content']
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    return send_file(
        io.BytesIO(content),
        mimetype=result['mime_type'],
        as_attachment=True,
        download_name=result['filename']
    )


@ideas_bp.route('/api/ideas/folder-contents', methods=['GET'])
def get_folder_contents():
    """
    GET /api/ideas/folder-contents?path=...
    
    Get contents of a specific folder.
    
    Query params:
        - path: string - Folder path (optional, defaults to ideas root)
    
    Response:
        - success: true/false
        - items: array of file/folder objects
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    path = request.args.get('path', '')
    
    result = service.get_folder_contents(path)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/search', methods=['GET'])
def search_ideas():
    """
    GET /api/ideas/search?q=...
    
    Search/filter ideas tree by query.
    
    Query params:
        - q: string - Search query
    
    Response:
        - success: true/false
        - tree: filtered tree structure
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    query = request.args.get('q', '')
    
    try:
        tree = service.filter_tree(query)
        return jsonify({'success': True, 'tree': tree})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ideas_bp.route('/api/ideas/delete-info', methods=['GET'])
def get_delete_info():
    """
    GET /api/ideas/delete-info?path=...
    
    Get item info for delete confirmation dialog.
    
    Query params:
        - path: string - Path of item to delete
    
    Response:
        - success: true/false
        - name: string
        - type: 'file' | 'folder'
        - item_count: number (for folders)
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    path = request.args.get('path')
    
    if not path:
        return jsonify({'success': False, 'error': 'path is required'}), 400
    
    result = service.get_delete_info(path)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/validate-drop', methods=['POST'])
def validate_drop_target():
    """
    POST /api/ideas/validate-drop
    
    Validate if drop target is valid for drag source.
    
    Request body:
        - source_path: string - Path being dragged
        - target_folder: string - Drop target folder
    
    Response:
        - valid: true/false
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    if not request.is_json:
        return jsonify({'valid': False}), 400
    
    data = request.get_json()
    source_path = data.get('source_path')
    target_folder = data.get('target_folder', '')
    
    valid = service.is_valid_drop_target(source_path, target_folder)
    return jsonify({'valid': valid})


# ==========================================================================
# SKILLS API
# 
# Read-only API for skills defined in .github/skills/
# ==========================================================================

@ideas_bp.route('/api/skills', methods=['GET'])
def get_skills():
    """
    GET /api/skills
    
    Get list of all skills with name and description.
    
    Response:
        - success: true
        - skills: array of {name, description}
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = SkillsService(project_root)
    
    try:
        skills = service.get_all()
        return jsonify({
            'success': True,
            'skills': skills
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
