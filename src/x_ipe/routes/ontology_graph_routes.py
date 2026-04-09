"""
FEATURE-058-E/F: Ontology Graph Viewer — Flask Routes

Blueprint exposing REST API endpoints under /api/kb/ontology/ for
listing graphs, fetching graph data as Cytoscape.js JSON, searching nodes,
and BFS graph traversal search.
"""
from flask import Blueprint, jsonify, request, current_app

from x_ipe.tracing import x_ipe_tracing

ontology_graph_bp = Blueprint('ontology_graph', __name__)


def _error(code: str, message: str, status: int):
    return jsonify({'error': code, 'message': message}), status


def _get_service_or_abort():
    """Retrieve OntologyGraphService from app config; abort if missing."""
    svc = current_app.config.get('ONTOLOGY_GRAPH_SERVICE')
    if not svc:
        from flask import abort, make_response
        abort(make_response(
            jsonify({'error': 'INTERNAL_ERROR', 'message': 'Ontology graph service not available'}),
            500,
        ))
    return svc


@ontology_graph_bp.route('/api/kb/ontology/graphs', methods=['GET'])
@x_ipe_tracing()
def get_graphs():
    """GET /api/kb/ontology/graphs — List all available ontology graphs."""
    svc = _get_service_or_abort()
    try:
        if not svc.has_ontology:
            return _error('ONTOLOGY_NOT_FOUND', 'No .ontology/ directory found in knowledge base', 404)
        graphs = svc.list_graphs()
        return jsonify({'graphs': graphs})
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@ontology_graph_bp.route('/api/kb/ontology/graph/<name>', methods=['GET'])
@x_ipe_tracing()
def get_graph(name):
    """GET /api/kb/ontology/graph/<name> — Get Cytoscape.js elements for a graph."""
    svc = _get_service_or_abort()
    try:
        if not svc.has_ontology:
            return _error('ONTOLOGY_NOT_FOUND', 'No .ontology/ directory found in knowledge base', 404)
        result = svc.get_graph(name)
        if result is None:
            return _error('GRAPH_NOT_FOUND', f"Graph '{name}' not found", 404)
        return jsonify(result)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@ontology_graph_bp.route('/api/kb/ontology/search', methods=['GET'])
@x_ipe_tracing()
def search_nodes():
    """GET /api/kb/ontology/search?q=<query>&graphs=<comma-separated>"""
    svc = _get_service_or_abort()
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'results': []})

        graphs_param = request.args.get('graphs', '').strip()
        graph_names = [g.strip() for g in graphs_param.split(',') if g.strip()] if graphs_param else None

        results = svc.search(query, graph_names)
        return jsonify({'results': results})
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)


@ontology_graph_bp.route('/api/kb/ontology/search/bfs', methods=['GET'])
@x_ipe_tracing()
def search_bfs():
    """GET /api/kb/ontology/search/bfs — BFS graph traversal search.

    Query params:
        q: Search query (required)
        scope: Comma-separated graph names or "all" (default: "all")
        depth: BFS traversal depth 1-5 (default: 3)
        page: Page number, 1-based (default: 1)
        page_size: Results per page, max 100 (default: 20)
    """
    svc = _get_service_or_abort()
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return _error('MISSING_QUERY', 'Query parameter "q" is required', 400)

        if not svc.has_ontology:
            return _error('ONTOLOGY_NOT_FOUND', 'No .ontology/ directory found in knowledge base', 404)

        scope_param = request.args.get('scope', 'all').strip()
        graph_names = None
        if scope_param and scope_param != 'all':
            graph_names = [g.strip() for g in scope_param.split(',') if g.strip()]

        depth = max(1, min(5, int(request.args.get('depth', 3))))
        page = max(1, int(request.args.get('page', 1)))
        page_size = max(1, min(100, int(request.args.get('page_size', 20))))

        result = svc.search_bfs(query, graph_names, depth, page, page_size)
        return jsonify(result)
    except ValueError:
        return _error('INVALID_PARAMS', 'Invalid numeric parameter', 400)
    except Exception as exc:
        return _error('INTERNAL_ERROR', str(exc), 500)
