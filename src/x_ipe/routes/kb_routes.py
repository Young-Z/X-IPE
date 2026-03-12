"""
FEATURE-049-A: KB Backend & Storage Foundation — Routes

Flask Blueprint exposing REST API endpoints under /api/kb/ for Knowledge Base
file/folder CRUD, config, tree, and search operations.
"""
from flask import Blueprint, jsonify, request, current_app

from x_ipe.tracing import x_ipe_tracing

kb_bp = Blueprint('kb', __name__)


def _error(code: str, message: str, status: int):
    return jsonify({'error': code, 'message': message}), status


def _get_kb_service_or_abort():
    """Retrieve KBService from app config; abort with JSON 500 if missing."""
    svc = current_app.config.get('KB_SERVICE')
    if not svc:
        from flask import abort, make_response
        abort(make_response(
            jsonify({'error': 'INTERNAL_ERROR', 'message': 'KB service not available'}),
            500,
        ))
    return svc


# ---------------------------------------------------------------------------
# Tree
# ---------------------------------------------------------------------------


@kb_bp.route('/api/kb/tree', methods=['GET'])
@x_ipe_tracing()
def get_tree():
    """
    GET /api/kb/tree

    FEATURE-049-A: Return full KB folder/file tree (excludes .intake/).
    """
    svc = _get_kb_service_or_abort()
    try:
        tree = svc.get_tree()
        return jsonify({'tree': [n.to_dict() for n in tree]})
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


# ---------------------------------------------------------------------------
# File listing
# ---------------------------------------------------------------------------


@kb_bp.route('/api/kb/files', methods=['GET'])
@x_ipe_tracing()
def list_files():
    """
    GET /api/kb/files?folder={path}&sort={field}&recursive={true|false}

    FEATURE-049-A: List files in folder with frontmatter metadata.
    """
    svc = _get_kb_service_or_abort()

    folder = request.args.get('folder', '')
    sort = request.args.get('sort', 'modified')
    recursive = request.args.get('recursive', 'false').lower() == 'true'

    try:
        files = svc.list_files(folder=folder, sort=sort, recursive=recursive)
        return jsonify({
            'files': [f.to_dict() for f in files],
            'folder': folder,
        })
    except FileNotFoundError as exc:
        return _error('NOT_FOUND', str(exc), 404)
    except ValueError as exc:
        return _error('BAD_REQUEST', str(exc), 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


# ---------------------------------------------------------------------------
# File CRUD
# ---------------------------------------------------------------------------


@kb_bp.route('/api/kb/files/<path:file_path>', methods=['GET'])
@x_ipe_tracing()
def get_file(file_path):
    """
    GET /api/kb/files/{path}

    FEATURE-049-A: Read single file content + frontmatter.
    """
    svc = _get_kb_service_or_abort()
    try:
        result = svc.get_file(file_path)
        return jsonify(result)
    except FileNotFoundError as exc:
        return _error('NOT_FOUND', str(exc), 404)
    except ValueError as exc:
        return _error('BAD_REQUEST', str(exc), 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@kb_bp.route('/api/kb/files', methods=['POST'])
@x_ipe_tracing()
def create_file():
    """
    POST /api/kb/files

    FEATURE-049-A: Create a new file with content and optional frontmatter.
    """
    svc = _get_kb_service_or_abort()

    if not request.is_json:
        return _error('BAD_REQUEST', 'JSON body required', 400)

    data = request.get_json()
    path = data.get('path', '').strip()
    content = data.get('content', '')
    frontmatter = data.get('frontmatter')

    if not path:
        return _error('BAD_REQUEST', 'path is required', 400)

    try:
        result = svc.create_file(path, content, frontmatter)
        return jsonify(result), 201
    except FileExistsError as exc:
        return _error('CONFLICT', str(exc), 409)
    except FileNotFoundError as exc:
        return _error('NOT_FOUND', str(exc), 404)
    except ValueError as exc:
        msg = str(exc)
        if 'Unsupported file type' in msg:
            return _error('UNSUPPORTED_MEDIA_TYPE', msg, 415)
        if 'exceeds maximum size' in msg:
            return _error('PAYLOAD_TOO_LARGE', msg, 413)
        return _error('BAD_REQUEST', msg, 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@kb_bp.route('/api/kb/files/<path:file_path>', methods=['PUT'])
@x_ipe_tracing()
def update_file(file_path):
    """
    PUT /api/kb/files/{path}

    FEATURE-049-A: Update file content and/or frontmatter.
    """
    svc = _get_kb_service_or_abort()

    if not request.is_json:
        return _error('BAD_REQUEST', 'JSON body required', 400)

    data = request.get_json()
    content = data.get('content')
    frontmatter = data.get('frontmatter')

    try:
        result = svc.update_file(file_path, content, frontmatter)
        return jsonify(result)
    except FileNotFoundError as exc:
        return _error('NOT_FOUND', str(exc), 404)
    except ValueError as exc:
        msg = str(exc)
        if 'exceeds maximum size' in msg:
            return _error('PAYLOAD_TOO_LARGE', msg, 413)
        return _error('BAD_REQUEST', msg, 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@kb_bp.route('/api/kb/files/<path:file_path>', methods=['DELETE'])
@x_ipe_tracing()
def delete_file(file_path):
    """
    DELETE /api/kb/files/{path}

    FEATURE-049-A: Delete a file.
    """
    svc = _get_kb_service_or_abort()
    try:
        svc.delete_file(file_path)
        return jsonify({'success': True, 'deleted': file_path})
    except FileNotFoundError as exc:
        return _error('NOT_FOUND', str(exc), 404)
    except ValueError as exc:
        return _error('BAD_REQUEST', str(exc), 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@kb_bp.route('/api/kb/files/move', methods=['PUT'])
@x_ipe_tracing()
def move_file():
    """
    PUT /api/kb/files/move

    FEATURE-049-A: Move a file to a new path.
    """
    svc = _get_kb_service_or_abort()

    if not request.is_json:
        return _error('BAD_REQUEST', 'JSON body required', 400)

    data = request.get_json()
    source = data.get('source', '').strip()
    destination = data.get('destination', '').strip()

    if not source or not destination:
        return _error('BAD_REQUEST', 'source and destination are required', 400)

    try:
        result = svc.move_file(source, destination)
        return jsonify({'success': True, **result})
    except FileNotFoundError as exc:
        return _error('NOT_FOUND', str(exc), 404)
    except FileExistsError as exc:
        return _error('CONFLICT', str(exc), 409)
    except ValueError as exc:
        return _error('BAD_REQUEST', str(exc), 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


# ---------------------------------------------------------------------------
# Folder CRUD
# ---------------------------------------------------------------------------


@kb_bp.route('/api/kb/folders', methods=['POST'])
@x_ipe_tracing()
def create_folder():
    """
    POST /api/kb/folders

    FEATURE-049-A: Create a new folder at specified path.
    """
    svc = _get_kb_service_or_abort()

    if not request.is_json:
        return _error('BAD_REQUEST', 'JSON body required', 400)

    data = request.get_json()
    path = data.get('path', '').strip()

    if not path:
        return _error('BAD_REQUEST', 'path is required', 400)

    try:
        result = svc.create_folder(path)
        return jsonify(result), 201
    except FileExistsError as exc:
        return _error('CONFLICT', str(exc), 409)
    except ValueError as exc:
        return _error('BAD_REQUEST', str(exc), 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@kb_bp.route('/api/kb/folders', methods=['PATCH'])
@x_ipe_tracing()
def rename_folder():
    """
    PATCH /api/kb/folders

    FEATURE-049-A: Rename a folder.
    """
    svc = _get_kb_service_or_abort()

    if not request.is_json:
        return _error('BAD_REQUEST', 'JSON body required', 400)

    data = request.get_json()
    path = data.get('path', '').strip()
    new_name = data.get('new_name', '').strip()

    if not path or not new_name:
        return _error('BAD_REQUEST', 'path and new_name are required', 400)

    try:
        result = svc.rename_folder(path, new_name)
        return jsonify(result)
    except FileNotFoundError as exc:
        return _error('NOT_FOUND', str(exc), 404)
    except FileExistsError as exc:
        return _error('CONFLICT', str(exc), 409)
    except ValueError as exc:
        return _error('BAD_REQUEST', str(exc), 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@kb_bp.route('/api/kb/folders/move', methods=['PUT'])
@x_ipe_tracing()
def move_folder():
    """
    PUT /api/kb/folders/move

    FEATURE-049-A: Move a folder to a new parent.
    """
    svc = _get_kb_service_or_abort()

    if not request.is_json:
        return _error('BAD_REQUEST', 'JSON body required', 400)

    data = request.get_json()
    source = data.get('source', '').strip()
    destination = data.get('destination', '').strip()

    if not source or not destination:
        return _error('BAD_REQUEST', 'source and destination are required', 400)

    try:
        result = svc.move_folder(source, destination)
        return jsonify({'success': True, **result})
    except FileNotFoundError as exc:
        return _error('NOT_FOUND', str(exc), 404)
    except FileExistsError as exc:
        return _error('CONFLICT', str(exc), 409)
    except ValueError as exc:
        return _error('BAD_REQUEST', str(exc), 400)
    except PermissionError as exc:
        return _error('FORBIDDEN', str(exc), 403)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@kb_bp.route('/api/kb/folders', methods=['DELETE'])
@x_ipe_tracing()
def delete_folder():
    """
    DELETE /api/kb/folders

    FEATURE-049-A: Delete a folder and its contents.
    """
    svc = _get_kb_service_or_abort()

    if not request.is_json:
        return _error('BAD_REQUEST', 'JSON body required', 400)

    data = request.get_json()
    path = data.get('path', '').strip()

    if not path:
        return _error('BAD_REQUEST', 'path is required', 400)

    try:
        result = svc.delete_folder(path)
        return jsonify({'success': True, **result})
    except PermissionError as exc:
        return _error('FORBIDDEN', str(exc), 403)
    except FileNotFoundError as exc:
        return _error('NOT_FOUND', str(exc), 404)
    except ValueError as exc:
        return _error('BAD_REQUEST', str(exc), 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@kb_bp.route('/api/kb/config', methods=['GET'])
@x_ipe_tracing()
def get_config():
    """
    GET /api/kb/config

    FEATURE-049-A: Return kb-config.json (tag taxonomy + AI Librarian config).
    """
    svc = _get_kb_service_or_abort()
    try:
        config = svc.get_config()
        return jsonify(config)
    except RuntimeError as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@kb_bp.route('/api/kb/search', methods=['GET'])
@x_ipe_tracing()
def search_files():
    """
    GET /api/kb/search?q={query}&tag={tag}&tag_type={lifecycle|domain}

    FEATURE-049-A: Search KB files by filename, frontmatter fields, and/or tag.
    """
    svc = _get_kb_service_or_abort()

    q = request.args.get('q', '')
    tag = request.args.get('tag', '')
    tag_type = request.args.get('tag_type', '')

    try:
        results = svc.search(query=q, tag=tag, tag_type=tag_type)
        return jsonify({'results': [r.to_dict() for r in results]})
    except ValueError as exc:
        return _error('BAD_REQUEST', str(exc), 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@kb_bp.route('/api/kb/upload', methods=['POST'])
@x_ipe_tracing()
def upload_files():
    """
    POST /api/kb/upload

    FEATURE-049-E: Upload files to KB. Accepts multipart/form-data.
    - files: one or more files
    - folder: destination folder path (default: root)
    Automatically extracts .zip archives preserving internal structure.
    """
    svc = _get_kb_service_or_abort()

    folder = request.form.get('folder', '').strip()
    uploaded_files = request.files.getlist('files')

    if not uploaded_files:
        return _error('BAD_REQUEST', 'No files provided', 400)

    results = []
    errors = []

    for f in uploaded_files:
        if not f.filename:
            continue

        try:
            content = f.read()

            # Archive extraction for .zip
            if f.filename.lower().endswith('.zip'):
                extracted = svc.extract_zip(content, folder)
                results.extend(extracted)
            elif f.filename.lower().endswith('.7z'):
                extracted = svc.extract_7z(content, folder)
                results.extend(extracted)
            else:
                dest_path = f'{folder}/{f.filename}' if folder else f.filename
                result = svc.create_file(dest_path, content.decode('utf-8', errors='replace'))
                results.append(result)
        except (FileExistsError, ValueError) as exc:
            errors.append({'file': f.filename, 'error': str(exc)})
        except Exception as exc:
            errors.append({'file': f.filename, 'error': str(exc)})

    return jsonify({
        'uploaded': results,
        'errors': errors,
        'total': len(results),
        'failed': len(errors)
    }), 201 if results else 400
