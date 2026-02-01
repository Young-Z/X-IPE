"""
FEATURE-024: Project Quality Evaluation UI

API routes for quality evaluation file management.

Provides REST endpoints for:
- GET /api/quality-evaluation/status - Get folder status and versions
- GET /api/quality-evaluation/content - Get markdown content for a version
"""
from flask import Blueprint, request, jsonify, current_app
from pathlib import Path
import re
from datetime import datetime

from x_ipe.tracing import x_ipe_tracing


quality_evaluation_bp = Blueprint('quality_evaluation', __name__, url_prefix='/api/quality-evaluation')


QUALITY_EVAL_FOLDER = 'x-ipe-docs/quality-evaluation'
EVAL_FILE_PREFIX = 'project-quality-evaluation'


def get_project_root() -> Path:
    """Get project root from app config."""
    return Path(current_app.config.get('PROJECT_ROOT', '.'))


@x_ipe_tracing(level="INFO")
def get_evaluation_folder() -> Path:
    """Get the quality evaluation folder path."""
    return get_project_root() / QUALITY_EVAL_FOLDER


@x_ipe_tracing(level="INFO")
def parse_version_from_filename(filename: str) -> str:
    """Extract version number from filename.
    
    Examples:
        project-quality-evaluation.md -> v5 (current)
        project-quality-evaluation-v4.md -> v4
    """
    if filename == f'{EVAL_FILE_PREFIX}.md':
        return 'current'
    match = re.match(rf'{EVAL_FILE_PREFIX}-v(\d+)\.md', filename)
    if match:
        return f'v{match.group(1)}'
    return None


@x_ipe_tracing(level="INFO")
def get_file_date(file_path: Path) -> str:
    """Get formatted modification date for a file."""
    try:
        mtime = file_path.stat().st_mtime
        dt = datetime.fromtimestamp(mtime)
        return dt.strftime('%b %d')
    except Exception:
        return ''


@x_ipe_tracing(level="INFO")
def scan_versions(folder: Path) -> list:
    """Scan folder for evaluation versions.
    
    Returns list of version dicts sorted by version number (newest first).
    Latest (current) file is always first.
    """
    if not folder.exists():
        return []
    
    versions = []
    current_file = folder / f'{EVAL_FILE_PREFIX}.md'
    
    # Check for current (latest) file first
    if current_file.exists():
        # Count existing versioned files to determine current version number
        versioned_files = list(folder.glob(f'{EVAL_FILE_PREFIX}-v*.md'))
        max_version = 0
        for vf in versioned_files:
            match = re.match(rf'{EVAL_FILE_PREFIX}-v(\d+)\.md', vf.name)
            if match:
                max_version = max(max_version, int(match.group(1)))
        
        current_version = max_version + 1
        versions.append({
            'version': f'v{current_version}',
            'filename': current_file.name,
            'date': get_file_date(current_file),
            'is_current': True
        })
    
    # Scan for versioned files
    versioned_files = sorted(
        folder.glob(f'{EVAL_FILE_PREFIX}-v*.md'),
        key=lambda f: int(re.search(r'-v(\d+)\.md', f.name).group(1)),
        reverse=True
    )
    
    for vf in versioned_files:
        match = re.match(rf'{EVAL_FILE_PREFIX}-v(\d+)\.md', vf.name)
        if match:
            versions.append({
                'version': f'v{match.group(1)}',
                'filename': vf.name,
                'date': get_file_date(vf),
                'is_current': False
            })
    
    # Limit to 5 most recent versions
    return versions[:5]


@quality_evaluation_bp.route('/status', methods=['GET'])
@x_ipe_tracing(level="INFO")
def get_status():
    """
    GET /api/quality-evaluation/status
    
    Get folder status and available versions.
    
    Response:
        {
            "exists": true,
            "folder_path": "x-ipe-docs/quality-evaluation",
            "versions": [
                {"version": "v5", "filename": "project-quality-evaluation.md", "date": "Feb 1", "is_current": true},
                {"version": "v4", "filename": "project-quality-evaluation-v4.md", "date": "Jan 31", "is_current": false}
            ]
        }
    """
    folder = get_evaluation_folder()
    versions = scan_versions(folder)
    
    return jsonify({
        'exists': len(versions) > 0,
        'folder_path': QUALITY_EVAL_FOLDER,
        'versions': versions
    })


@quality_evaluation_bp.route('/content', methods=['GET'])
@x_ipe_tracing(level="INFO")
def get_content():
    """
    GET /api/quality-evaluation/content
    
    Get markdown content for a specific version.
    
    Query Parameters:
        version (optional): Version to retrieve (e.g., "v4"). Default: latest.
    
    Response:
        {
            "content": "# Project Quality Evaluation...",
            "version": "v5",
            "filename": "project-quality-evaluation.md",
            "path": "x-ipe-docs/quality-evaluation/project-quality-evaluation.md"
        }
    """
    folder = get_evaluation_folder()
    requested_version = request.args.get('version')
    
    versions = scan_versions(folder)
    if not versions:
        return jsonify({'error': 'No evaluation file found'}), 404
    
    # Find the requested version or use latest
    target_version = None
    if requested_version:
        for v in versions:
            if v['version'] == requested_version:
                target_version = v
                break
        if not target_version:
            return jsonify({'error': f'Version {requested_version} not found'}), 404
    else:
        target_version = versions[0]  # Latest
    
    # Read the file content
    file_path = folder / target_version['filename']
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return jsonify({'error': f'Failed to read file: {str(e)}'}), 500
    
    return jsonify({
        'content': content,
        'version': target_version['version'],
        'filename': target_version['filename'],
        'path': f"{QUALITY_EVAL_FOLDER}/{target_version['filename']}"
    })
