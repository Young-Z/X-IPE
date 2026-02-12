"""
FEATURE-025-A: KB Core Infrastructure
FEATURE-025-B: KB Landing Zone
FEATURE-025-C: KB Manager Skill
FEATURE-025-D: KB Topics & Summaries

KB Routes: REST API endpoints for Knowledge Base operations.
"""
from flask import Blueprint, jsonify, request, current_app

from x_ipe.services.kb_service import KBService
from x_ipe.services.kb_manager_service import KBManagerService
from x_ipe.services.llm_service import LLMService
from x_ipe.tracing import x_ipe_tracing

kb_bp = Blueprint('kb', __name__, url_prefix='/api/kb')


def _get_kb_service() -> KBService:
    """Get KBService instance using project root from app config."""
    project_root = current_app.config.get('PROJECT_ROOT', '.')
    return KBService(project_root)


@kb_bp.route('/index', methods=['GET'])
@x_ipe_tracing(level="INFO")
def get_index():
    """
    Get current file index.
    
    Returns:
        JSON: File index with version, last_updated, and files list
    """
    service = _get_kb_service()
    index = service.get_index()
    return jsonify(index)


@kb_bp.route('/index/refresh', methods=['POST'])
@x_ipe_tracing(level="INFO")
def refresh_index():
    """
    Rebuild file index from file system.
    
    Returns:
        JSON: Updated file index
    """
    service = _get_kb_service()
    index = service.refresh_index()
    return jsonify(index)


@kb_bp.route('/topics', methods=['GET'])
@x_ipe_tracing(level="INFO")
def get_topics():
    """
    Get list of all topics.
    
    Returns:
        JSON: { "topics": ["topic1", "topic2", ...] }
    """
    service = _get_kb_service()
    topics = service.get_topics()
    return jsonify({"topics": topics})


@kb_bp.route('/topics/<name>', methods=['GET'])
@x_ipe_tracing(level="INFO")
def get_topic_metadata(name: str):
    """
    Get metadata for a specific topic.
    
    Args:
        name: Topic folder name
        
    Returns:
        JSON: Topic metadata or 404 if not found
    """
    service = _get_kb_service()
    metadata = service.get_topic_metadata(name)
    
    if metadata is None:
        return jsonify({"error": f"Topic '{name}' not found"}), 404
    
    return jsonify(metadata)


# ------------------------------------------------------------------
# FEATURE-025-D: Topics & Summaries endpoints
# ------------------------------------------------------------------

@kb_bp.route('/topics/<name>/detail', methods=['GET'])
@x_ipe_tracing(level="INFO")
def get_topic_detail(name: str):
    """Get full topic detail: metadata, summaries, files, related topics."""
    service = _get_kb_service()
    detail = service.get_topic_detail(name)
    if detail is None:
        return jsonify({"error": f"Topic '{name}' not found"}), 404
    return jsonify(detail)


@kb_bp.route('/topics/<name>/summary', methods=['GET'])
@x_ipe_tracing(level="INFO")
def get_topic_summary(name: str):
    """Read summary content by version (default: latest)."""
    service = _get_kb_service()
    version = request.args.get("version", "latest")
    summary = service.get_summary_content(name, version)
    if summary is None:
        return jsonify({"error": f"Summary not found for topic '{name}' version '{version}'"}), 404
    return jsonify(summary)


# ------------------------------------------------------------------
# FEATURE-025-B: Landing Zone endpoints
# ------------------------------------------------------------------

@kb_bp.route('/upload', methods=['POST'])
@x_ipe_tracing(level="INFO")
def upload_files():
    """
    Upload files to the landing directory.
    
    Request: multipart/form-data with 'files' field
    
    Returns:
        JSON: { uploaded: [...], skipped: [...], errors: [...] }
    """
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    uploaded_files = request.files.getlist('files')
    if not uploaded_files or all(f.filename == '' for f in uploaded_files):
        return jsonify({'error': 'No files provided'}), 400
    
    files = []
    for f in uploaded_files:
        if f.filename:
            data = f.read()
            files.append((f.filename, data, len(data)))
    
    service = _get_kb_service()
    result = service.upload_files(files)
    return jsonify(result)


@kb_bp.route('/landing/delete', methods=['POST'])
@x_ipe_tracing(level="INFO")
def delete_landing_files():
    """
    Delete files from the landing directory.
    
    Request: JSON { paths: ["landing/file1.pdf", ...] }
    
    Returns:
        JSON: { deleted: [...], errors: [...] }
    """
    if not request.is_json:
        return jsonify({'error': 'JSON required'}), 400
    
    data = request.get_json()
    paths = data.get('paths', [])
    
    service = _get_kb_service()
    result = service.delete_files(paths)
    return jsonify(result)


@kb_bp.route('/landing', methods=['GET'])
@x_ipe_tracing(level="INFO")
def get_landing_files():
    """
    Get files in the landing directory.
    
    Returns:
        JSON: { files: [...] }
    """
    service = _get_kb_service()
    files = service.get_landing_files()
    return jsonify({'files': files})


# ------------------------------------------------------------------
# FEATURE-025-C: KB Manager endpoints
# ------------------------------------------------------------------

def _get_manager() -> KBManagerService:
    """Get or create KBManagerService singleton on app context."""
    if not hasattr(current_app, '_kb_manager'):
        kb_service = _get_kb_service()
        llm_service = LLMService()
        current_app._kb_manager = KBManagerService(
            kb_service=kb_service, llm_service=llm_service
        )
    return current_app._kb_manager


@kb_bp.route('/process', methods=['POST'])
@x_ipe_tracing(level="INFO")
def process_files():
    """
    Classify landing files into topics via LLM.

    Request: JSON { paths: ["landing/file1.md", ...] }
    Response: { session_id, suggestions: [...] }
    """
    if not request.is_json:
        return jsonify({'error': 'JSON required'}), 400

    data = request.get_json()
    paths = data.get('paths')
    if not paths:
        return jsonify({'error': 'No paths provided'}), 400

    manager = _get_manager()
    try:
        result = manager.classify(paths)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 409


@kb_bp.route('/process/confirm', methods=['POST'])
@x_ipe_tracing(level="INFO")
def process_confirm():
    """
    Confirm classification — move files and generate summaries.

    Request: JSON { session_id, classifications: [{path, topic}, ...] }
    """
    if not request.is_json:
        return jsonify({'error': 'JSON required'}), 400

    data = request.get_json()
    session_id = data.get('session_id')
    classifications = data.get('classifications', [])

    manager = _get_manager()
    try:
        result = manager.execute_classification(session_id, classifications)
        return jsonify(result)
    except KeyError:
        return jsonify({'error': 'Session not found'}), 404


@kb_bp.route('/process/cancel', methods=['POST'])
@x_ipe_tracing(level="INFO")
def process_cancel():
    """
    Cancel a pending classification session.

    Request: JSON { session_id }
    """
    if not request.is_json:
        return jsonify({'error': 'JSON required'}), 400

    data = request.get_json()
    session_id = data.get('session_id')

    manager = _get_manager()
    try:
        result = manager.cancel_processing(session_id)
        return jsonify(result)
    except KeyError:
        return jsonify({'error': 'Session not found'}), 404


@kb_bp.route('/search', methods=['GET'])
@x_ipe_tracing(level="INFO")
def search_kb():
    """
    Search knowledge base file index.

    Query params: q=search_query
    Response: { query, results: [...], total }
    """
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400

    manager = _get_manager()
    results = manager.search(query)
    return jsonify({'query': query, 'results': results, 'total': len(results)})


@kb_bp.route('/reorganize', methods=['POST'])
@x_ipe_tracing(level="INFO")
def reorganize_kb():
    """
    Analyze and reorganize KB topics.

    Response: { changes: [...], summary }
    """
    manager = _get_manager()
    result = manager.reorganize()
    return jsonify(result)
