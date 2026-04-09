"""
FEATURE-058-E: Ontology Graph Viewer — Flask Routes

Blueprint exposing REST API endpoints under /api/kb/ontology/ for
listing graphs, fetching graph data as Cytoscape.js JSON, and searching nodes.
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
