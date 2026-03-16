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
import html
import json
import os
from pathlib import Path
from flask import Blueprint, jsonify, request, current_app, send_file

from x_ipe.services import IdeasService, SkillsService
from x_ipe.tracing import x_ipe_tracing

# CR-001: Convertible binary formats
CONVERTIBLE_EXTENSIONS = {'.docx', '.msg'}
MAX_CONVERSION_SIZE = 10 * 1024 * 1024  # 10MB

ideas_bp = Blueprint('ideas', __name__)


@ideas_bp.route('/api/ideas/tree', methods=['GET'])
@x_ipe_tracing()
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
@x_ipe_tracing()
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
    
    # CR-004: Get optional kb_references from form data
    kb_references_raw = request.form.get('kb_references')
    kb_references = []
    if kb_references_raw:
        try:
            kb_references = json.loads(kb_references_raw)
            if not isinstance(kb_references, list):
                kb_references = []
        except (json.JSONDecodeError, TypeError):
            kb_references = []
    
    # Convert to (filename, content) tuples
    files = [(f.filename, f.read()) for f in uploaded_files if f.filename]
    
    result = service.upload(files, target_folder=target_folder, kb_references=kb_references)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/kb-references', methods=['GET', 'POST', 'DELETE'])
@x_ipe_tracing()
def manage_kb_references():
    """
    GET /api/ideas/kb-references?folder_path=... — Read .knowledge-reference.yaml
    POST /api/ideas/kb-references — Write .knowledge-reference.yaml immediately
    DELETE /api/ideas/kb-references — Remove .knowledge-reference.yaml
    
    CR-004: Immediate YAML persistence on insert/delete.
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    if request.method == 'GET':
        folder_path = request.args.get('folder_path')
        if not folder_path:
            return jsonify({'success': False, 'error': 'folder_path query parameter is required'}), 400
        result = service.get_kb_references(folder_path)
        if result['success']:
            return jsonify(result)
        return jsonify(result), 400
    
    if not request.is_json:
        return jsonify({'success': False, 'error': 'JSON required'}), 400
    
    data = request.get_json()
    folder_path = data.get('folder_path')
    
    if not folder_path:
        return jsonify({'success': False, 'error': 'folder_path is required'}), 400
    
    if request.method == 'POST':
        kb_references = data.get('kb_references', [])
        if not isinstance(kb_references, list) or not kb_references:
            return jsonify({'success': False, 'error': 'kb_references must be a non-empty list'}), 400
        result = service.save_kb_references(folder_path, kb_references)
    else:  # DELETE
        result = service.delete_kb_references(folder_path)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/create-folder', methods=['POST'])
@x_ipe_tracing()
def create_idea_folder():
    """
    POST /api/ideas/create-folder
    
    Create a new empty folder in ideas directory.
    
    Request body:
        - folder_name: string - Name for the new folder
        - parent_folder: string (optional) - Parent folder path
    
    Response:
        - success: true/false
        - folder_name: string
        - folder_path: string
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'JSON required'
        }), 400
    
    data = request.get_json()
    folder_name = data.get('folder_name')
    parent_folder = data.get('parent_folder')
    
    if not folder_name:
        return jsonify({
            'success': False,
            'error': 'folder_name is required'
        }), 400
    
    result = service.create_folder(folder_name, parent_folder)
    
    if result['success']:
        return jsonify(result)
    return jsonify(result), 400


@ideas_bp.route('/api/ideas/rename', methods=['POST'])
@x_ipe_tracing()
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
@x_ipe_tracing()
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
@x_ipe_tracing()
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
@x_ipe_tracing()
def get_ideas_toolbox():
    """
    GET /api/ideas/toolbox
    
    Get ideation toolbox configuration.
    
    Response:
        - version: string
        - ideation: {x-ipe-tool-infographic-syntax: bool, mermaid: bool}
        - mockup: {frontend-design: bool}
        - sharing: {}
    """
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    service = IdeasService(project_root)
    
    config = service.get_toolbox()
    return jsonify(config)


@ideas_bp.route('/api/ideas/toolbox', methods=['POST'])
@x_ipe_tracing()
def save_ideas_toolbox():
    """
    POST /api/ideas/toolbox
    
    Save ideation toolbox configuration.
    
    Request body:
        - version: string
        - ideation: {x-ipe-tool-infographic-syntax: bool, mermaid: bool}
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
@x_ipe_tracing()
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
@x_ipe_tracing()
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
@x_ipe_tracing()
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
@x_ipe_tracing()
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
@x_ipe_tracing()
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
@x_ipe_tracing()
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
@x_ipe_tracing()
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
# ==========================================================================
# FILE CONTENT API (FEATURE-037-B)
# ==========================================================================


@x_ipe_tracing(level='DEBUG')
def _convert_docx(file_path):
    """Convert .docx file to HTML via mammoth. Returns HTML string."""
    import mammoth
    with open(file_path, 'rb') as f:
        result = mammoth.convert_to_html(f)
    return result.value


@x_ipe_tracing(level='DEBUG')
def _convert_msg(file_path):
    """Convert .msg file to structured HTML with email metadata and body."""
    import extract_msg
    msg = extract_msg.openMsg(str(file_path))
    try:
        sender = html.escape(str(msg.sender or ''))
        to = html.escape(str(msg.to or ''))
        cc = html.escape(str(msg.cc or ''))
        date = html.escape(str(msg.date or ''))
        subject = html.escape(str(msg.subject or ''))

        if msg.htmlBody:
            body_section = msg.htmlBody if isinstance(msg.htmlBody, str) else msg.htmlBody.decode('utf-8', errors='replace')
        elif msg.body:
            body_section = f'<pre>{html.escape(str(msg.body))}</pre>'
        else:
            body_section = ''

        return (
            f'<div class="msg-preview">'
            f'<table class="msg-headers">'
            f'<tr><td><strong>From:</strong></td><td>{sender}</td></tr>'
            f'<tr><td><strong>To:</strong></td><td>{to}</td></tr>'
            f'<tr><td><strong>CC:</strong></td><td>{cc}</td></tr>'
            f'<tr><td><strong>Date:</strong></td><td>{date}</td></tr>'
            f'<tr><td><strong>Subject:</strong></td><td>{subject}</td></tr>'
            f'</table>'
            f'<hr>'
            f'<div class="msg-body">{body_section}</div>'
            f'</div>'
        )
    finally:
        msg.close()


@x_ipe_tracing(level='DEBUG')
def _sanitize_converted_html(content):
    """Strip dangerous elements from converted HTML using BeautifulSoup."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup.find_all(['script', 'iframe', 'object', 'embed']):
        tag.decompose()
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr.lower().startswith('on'):
                del tag[attr]
    return str(soup)


@ideas_bp.route('/api/ideas/file', methods=['GET'])
@x_ipe_tracing()
def get_idea_file():
    """
    GET /api/ideas/file?path=<relative-path>

    Return raw file content. Path must be within project root.
    Serves text files as plain text and known binary types (images, PDFs) natively.

    Query params:
        - path: string (required) - Relative path from project root

    Response:
        - 200: file content (text or binary with appropriate Content-Type)
        - 400: missing path parameter
        - 403: path outside project root
        - 404: file not found
        - 415: unsupported binary file
    """
    rel_path = request.args.get('path', '')
    if not rel_path:
        return jsonify({'error': 'path parameter required'}), 400

    project_root = Path(current_app.config.get('PROJECT_ROOT', '.')).resolve()
    target = (project_root / rel_path).resolve()

    # Security: path must be within project root
    if not str(target).startswith(str(project_root)):
        return jsonify({'error': 'Access denied'}), 403

    if not target.is_file():
        return jsonify({'error': 'File not found'}), 404

    # Serve known binary types with correct Content-Type
    import mimetypes
    mime_type, _ = mimetypes.guess_type(str(target))
    binary_prefixes = ('image/', 'application/pdf')
    if mime_type and any(mime_type.startswith(p) for p in binary_prefixes):
        return send_file(target, mimetype=mime_type)

    # CR-001: Convert .docx/.msg to HTML for preview
    ext = target.suffix.lower()
    if ext in CONVERTIBLE_EXTENSIONS:
        file_size = target.stat().st_size
        if file_size > MAX_CONVERSION_SIZE:
            return jsonify({'error': 'File too large to preview (max 10MB)'}), 413
        try:
            if ext == '.docx':
                converted_html = _convert_docx(target)
            else:
                converted_html = _convert_msg(target)
            sanitized = _sanitize_converted_html(converted_html)
            return sanitized, 200, {
                'Content-Type': 'text/html; charset=utf-8',
                'X-Converted': 'true'
            }
        except Exception:
            return jsonify({'error': 'Preview unavailable for this file'}), 415

    try:
        content = target.read_text(encoding='utf-8')
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except UnicodeDecodeError:
        return jsonify({'error': 'Binary file — cannot read as text'}), 415


# ==========================================================================
# SKILLS API
# 
# Read-only API for skills defined in .github/skills/
# ==========================================================================

@ideas_bp.route('/api/skills', methods=['GET'])
@x_ipe_tracing()
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
