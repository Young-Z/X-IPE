"""
Main Routes Blueprint

FEATURE-001: Project Navigation
FEATURE-003: Content Editor

Provides:
- Index page
- Project structure API
- File content API
- File save API
"""
import os
from pathlib import Path
from flask import Blueprint, render_template, jsonify, request, current_app, send_file

from x_ipe.services import ProjectService, ContentService

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Serve main page with sidebar navigation"""
    return render_template('index.html')


@main_bp.route('/uiux-feedbacks')
def uiux_feedbacks():
    """
    GET /uiux-feedbacks
    
    FEATURE-022: UIUX Feedbacks placeholder page (CR-004)
    """
    return render_template('uiux-feedbacks.html')


@main_bp.route('/workplace')
def workplace():
    """
    GET /workplace
    
    FEATURE-008: Workplace/Ideation page
    CR-004: Route preserved for backward compatibility, page renamed to Ideation.
    """
    return render_template('workplace.html')


@main_bp.route('/api/project/structure')
def get_project_structure():
    """
    GET /api/project/structure
    
    Returns the project folder structure for sidebar navigation.
    """
    project_root = current_app.config.get('PROJECT_ROOT')
    
    if not project_root or not os.path.exists(project_root):
        return jsonify({
            'error': 'Project root not configured or does not exist',
            'project_root': project_root
        }), 400
    
    service = ProjectService(project_root)
    structure = service.get_structure()
    
    return jsonify(structure)


@main_bp.route('/api/file/content')
def get_file_content():
    """
    GET /api/file/content?path=<relative_path>&raw=<true/false>
    
    Returns the content of a file with metadata for rendering.
    If raw=true or file is binary (images, etc.), serves the raw file content.
    """
    file_path = request.args.get('path')
    raw = request.args.get('raw', 'false').lower() == 'true'
    
    if not file_path:
        return jsonify({'error': 'Path parameter required'}), 400
    
    project_root = current_app.config.get('PROJECT_ROOT')
    
    # Binary file extensions that should always be served raw
    binary_extensions = {
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.rar', '.tar', '.gz', '.7z',
        '.mp3', '.mp4', '.wav', '.avi', '.mov',
        '.exe', '.dll', '.so', '.dylib',
    }
    
    try:
        # Resolve path
        full_path = (Path(project_root) / file_path).resolve()
        
        # Security check: ensure path is within project root
        if not str(full_path).startswith(str(Path(project_root).resolve())):
            return jsonify({'error': 'Access denied'}), 403
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        ext = full_path.suffix.lower()
        
        # Auto-detect binary files or use raw parameter
        if raw or ext in binary_extensions:
            # Determine MIME type
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.ico': 'image/x-icon',
                '.svg': 'image/svg+xml',
                '.webp': 'image/webp',
                '.html': 'text/html',
                '.htm': 'text/html',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.json': 'application/json',
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.xls': 'application/vnd.ms-excel',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.ppt': 'application/vnd.ms-powerpoint',
                '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                '.zip': 'application/zip',
                '.rar': 'application/vnd.rar',
            }
            mime_type = mime_types.get(ext, 'application/octet-stream')
            
            return send_file(full_path, mimetype=mime_type)
        
        service = ContentService(project_root)
        result = service.get_content(file_path)
        return jsonify(result)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except PermissionError:
        return jsonify({'error': 'Access denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/file/save', methods=['POST'])
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
    
    project_root = current_app.config.get('PROJECT_ROOT')
    
    if not project_root or not os.path.exists(project_root):
        return jsonify({'success': False, 'error': 'Project root not configured'}), 400
    
    service = ContentService(project_root)
    result = service.save_content(data['path'], data['content'])
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400
