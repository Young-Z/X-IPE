"""
FEATURE-058-E: Ontology Graph Viewer — Backend API & Service Tests

Tests cover:
- OntologyGraphService: list_graphs, get_graph, search
- Flask API endpoints: /api/kb/ontology/graphs, /graph/<name>, /search
- Integration: Blueprint registration, service wiring
"""
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def kb_root_with_ontology(tmp_path):
    """Create a KB root with .ontology/ dir containing test graph data."""
    ontology_dir = tmp_path / ".ontology"
    ontology_dir.mkdir()

    # Create a test JSONL graph file
    graph_data = [
        {"op": "create", "entity": {"id": "know_aaa", "properties": {
            "label": "Authentication", "node_type": "concept", "weight": 5,
            "description": "JWT-based auth system", "dimensions": {"topic": ["security", "auth"]},
            "source_files": ["docs/auth.md"]
        }}, "timestamp": "2026-01-01T00:00:00Z"},
        {"op": "create", "entity": {"id": "know_bbb", "properties": {
            "label": "Token Refresh", "node_type": "entity", "weight": 3,
            "description": "Refresh token mechanism", "dimensions": {"topic": ["security"]},
            "source_files": []
        }}, "timestamp": "2026-01-01T00:00:01Z"},
        {"op": "relate", "from": "know_aaa", "rel": "depends_on", "to": "know_bbb",
         "properties": {}, "timestamp": "2026-01-01T00:00:02Z"},
    ]
    graph_file = ontology_dir / "jwt-authentication.jsonl"
    graph_file.write_text("\n".join(json.dumps(r) for r in graph_data))

    # Create a second graph
    graph2_data = [
        {"op": "create", "entity": {"id": "know_ccc", "properties": {
            "label": "REST API", "node_type": "document", "weight": 7,
            "description": "RESTful API design patterns", "dimensions": {"technology": ["http"]},
            "source_files": ["docs/api.md"]
        }}, "timestamp": "2026-01-02T00:00:00Z"},
    ]
    graph2_file = ontology_dir / "api-design.jsonl"
    graph2_file.write_text("\n".join(json.dumps(r) for r in graph2_data))

    # Create .graph-index.json
    index = {
        "version": "1.0",
        "generated_at": "2026-01-01T00:00:00Z",
        "ontology_dir": str(ontology_dir),
        "graphs": [
            {"name": "jwt-authentication", "file": "jwt-authentication.jsonl",
             "description": "JWT auth graph", "entity_count": 2, "relation_count": 1,
             "dimensions": ["security"], "root_entity_id": "know_aaa", "root_label": "Authentication"},
            {"name": "api-design", "file": "api-design.jsonl",
             "description": "API design graph", "entity_count": 1, "relation_count": 0,
             "dimensions": ["technology"], "root_entity_id": "know_ccc", "root_label": "REST API"},
        ]
    }
    (ontology_dir / ".graph-index.json").write_text(json.dumps(index))

    return tmp_path


@pytest.fixture
def kb_root_empty(tmp_path):
    """Create a KB root WITHOUT .ontology/ dir."""
    return tmp_path


@pytest.fixture
def graph_service(kb_root_with_ontology):
    from x_ipe.services.ontology_graph_service import OntologyGraphService
    return OntologyGraphService(str(kb_root_with_ontology))


@pytest.fixture
def graph_service_empty(kb_root_empty):
    from x_ipe.services.ontology_graph_service import OntologyGraphService
    return OntologyGraphService(str(kb_root_empty))


@pytest.fixture
def app_with_ontology(kb_root_with_ontology):
    from x_ipe.app import create_app
    app = create_app()
    app.config['TESTING'] = True

    from x_ipe.services.ontology_graph_service import OntologyGraphService
    app.config['ONTOLOGY_GRAPH_SERVICE'] = OntologyGraphService(str(kb_root_with_ontology))
    return app


@pytest.fixture
def app_without_ontology(kb_root_empty):
    from x_ipe.app import create_app
    app = create_app()
    app.config['TESTING'] = True

    from x_ipe.services.ontology_graph_service import OntologyGraphService
    app.config['ONTOLOGY_GRAPH_SERVICE'] = OntologyGraphService(str(kb_root_empty))
    return app


@pytest.fixture
def client(app_with_ontology):
    return app_with_ontology.test_client()


@pytest.fixture
def client_no_ontology(app_without_ontology):
    return app_without_ontology.test_client()


# ============================================================================
# SERVICE TESTS
# ============================================================================

class TestOntologyGraphServiceProperties:
    """Test service property accessors."""

    def test_has_ontology_true(self, graph_service):
        assert graph_service.has_ontology is True

    def test_has_ontology_false(self, graph_service_empty):
        assert graph_service_empty.has_ontology is False

    def test_ontology_dir_path(self, graph_service, kb_root_with_ontology):
        expected = kb_root_with_ontology / ".ontology"
        assert graph_service.ontology_dir == expected


class TestOntologyGraphServiceListGraphs:
    """AC-058E-15a, 15e: List graphs from index."""

    def test_list_graphs_returns_all(self, graph_service):
        graphs = graph_service.list_graphs()
        assert len(graphs) == 2
        names = [g['name'] for g in graphs]
        assert 'jwt-authentication' in names
        assert 'api-design' in names

    def test_list_graphs_has_required_fields(self, graph_service):
        graphs = graph_service.list_graphs()
        for g in graphs:
            assert 'name' in g
            assert 'file_path' in g
            assert 'node_count' in g
            assert 'edge_count' in g
            assert 'dominant_type' in g

    def test_list_graphs_counts(self, graph_service):
        graphs = graph_service.list_graphs()
        jwt = next(g for g in graphs if g['name'] == 'jwt-authentication')
        assert jwt['node_count'] == 2
        assert jwt['edge_count'] == 1

    def test_list_graphs_empty_when_no_ontology(self, graph_service_empty):
        assert graph_service_empty.list_graphs() == []

    def test_list_graphs_reads_from_index(self, graph_service):
        """AC-058E-15e: Uses .graph-index.json for fast listing."""
        graphs = graph_service.list_graphs()
        assert len(graphs) > 0


class TestOntologyGraphServiceGetGraph:
    """AC-058E-15b, 15c: Get Cytoscape.js elements for a graph."""

    def test_get_graph_returns_elements(self, graph_service):
        result = graph_service.get_graph('jwt-authentication')
        assert result is not None
        assert 'elements' in result

    def test_get_graph_nodes_have_cytoscape_format(self, graph_service):
        result = graph_service.get_graph('jwt-authentication')
        nodes = result['elements']['nodes']
        assert len(nodes) == 2

        node_a = next(n for n in nodes if n['data']['id'] == 'know_aaa')
        assert node_a['data']['label'] == 'Authentication'
        assert node_a['data']['node_type'] == 'concept'
        assert node_a['data']['weight'] == 5
        assert node_a['data']['description'] == 'JWT-based auth system'
        assert 'dimensions' in node_a['data']
        assert 'source_files' in node_a['data']

    def test_get_graph_edges_have_cytoscape_format(self, graph_service):
        result = graph_service.get_graph('jwt-authentication')
        edges = result['elements']['edges']
        assert len(edges) == 1

        edge = edges[0]
        assert edge['data']['source'] == 'know_aaa'
        assert edge['data']['target'] == 'know_bbb'
        assert 'label' in edge['data']

    def test_get_graph_not_found_returns_none(self, graph_service):
        """AC-058E-15c: Invalid graph name → None."""
        result = graph_service.get_graph('nonexistent-graph')
        assert result is None

    def test_get_graph_no_ontology_returns_none(self, graph_service_empty):
        result = graph_service_empty.get_graph('jwt-authentication')
        assert result is None


class TestOntologyGraphServiceSearch:
    """AC-058E-15d, 09e: Search across graphs."""

    def test_search_by_label(self, graph_service):
        results = graph_service.search('Authentication', None)
        assert len(results) > 0
        assert any(r['node_id'] == 'know_aaa' for r in results)

    def test_search_by_description(self, graph_service):
        results = graph_service.search('JWT', None)
        assert len(results) > 0

    def test_search_scoped_to_graph(self, graph_service):
        results = graph_service.search('Authentication', ['api-design'])
        assert not any(r['node_id'] == 'know_aaa' for r in results)

    def test_search_no_results(self, graph_service):
        results = graph_service.search('zzznonexistent', None)
        assert results == []

    def test_search_results_have_required_fields(self, graph_service):
        results = graph_service.search('Authentication', None)
        for r in results:
            assert 'node_id' in r
            assert 'label' in r
            assert 'graph' in r
            assert 'relevance' in r

    def test_search_sorted_by_relevance_desc(self, graph_service):
        results = graph_service.search('auth', None)
        if len(results) > 1:
            relevances = [r['relevance'] for r in results]
            assert relevances == sorted(relevances, reverse=True)

    def test_search_empty_query(self, graph_service):
        results = graph_service.search('', None)
        assert results == []


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestGraphsEndpoint:
    """AC-058E-15a, 15e: GET /api/kb/ontology/graphs"""

    def test_get_graphs_success(self, client):
        resp = client.get('/api/kb/ontology/graphs')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'graphs' in data
        assert len(data['graphs']) == 2

    def test_get_graphs_response_shape(self, client):
        resp = client.get('/api/kb/ontology/graphs')
        data = resp.get_json()
        for g in data['graphs']:
            assert 'name' in g
            assert 'node_count' in g
            assert 'edge_count' in g

    def test_get_graphs_no_ontology_returns_404(self, client_no_ontology):
        resp = client_no_ontology.get('/api/kb/ontology/graphs')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['error'] == 'ONTOLOGY_NOT_FOUND'


class TestGraphDetailEndpoint:
    """AC-058E-15b, 15c: GET /api/kb/ontology/graph/<name>"""

    def test_get_graph_success(self, client):
        resp = client.get('/api/kb/ontology/graph/jwt-authentication')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'elements' in data

    def test_get_graph_has_nodes_and_edges(self, client):
        resp = client.get('/api/kb/ontology/graph/jwt-authentication')
        data = resp.get_json()
        nodes = data['elements']['nodes']
        edges = data['elements']['edges']
        assert len(nodes) == 2
        assert len(edges) == 1

    def test_get_graph_not_found(self, client):
        """AC-058E-15c: Invalid name → 404."""
        resp = client.get('/api/kb/ontology/graph/nonexistent')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['error'] == 'GRAPH_NOT_FOUND'

    def test_get_graph_no_ontology(self, client_no_ontology):
        resp = client_no_ontology.get('/api/kb/ontology/graph/jwt-authentication')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['error'] == 'ONTOLOGY_NOT_FOUND'


class TestSearchEndpoint:
    """AC-058E-15d: GET /api/kb/ontology/search"""

    def test_search_with_results(self, client):
        resp = client.get('/api/kb/ontology/search?q=Authentication')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'results' in data
        assert len(data['results']) > 0

    def test_search_empty_query(self, client):
        resp = client.get('/api/kb/ontology/search?q=')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['results'] == []

    def test_search_no_query_param(self, client):
        resp = client.get('/api/kb/ontology/search')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['results'] == []

    def test_search_with_graph_scope(self, client):
        resp = client.get('/api/kb/ontology/search?q=REST&graphs=api-design')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['results']) > 0

    def test_search_no_results(self, client):
        resp = client.get('/api/kb/ontology/search?q=zzzznonexistent')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['results'] == []


class TestBlueprintRegistration:
    """AC-058E-15f: Integration — blueprint registered at startup."""

    def test_ontology_routes_registered(self):
        from x_ipe.app import create_app
        app = create_app()
        rules = [r.rule for r in app.url_map.iter_rules()]
        assert '/api/kb/ontology/graphs' in rules
        assert '/api/kb/ontology/graph/<name>' in rules
        assert '/api/kb/ontology/search' in rules

    def test_service_stored_in_config(self):
        from x_ipe.app import create_app
        app = create_app()
        from x_ipe.services.ontology_graph_service import OntologyGraphService
        svc = app.config.get('ONTOLOGY_GRAPH_SERVICE')
        assert isinstance(svc, OntologyGraphService)


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Edge cases: malformed data, empty files, special characters."""

    def test_malformed_jsonl_skipped(self, tmp_path):
        """Malformed lines in JSONL should be skipped, not crash."""
        ontology_dir = tmp_path / ".ontology"
        ontology_dir.mkdir()
        graph_file = ontology_dir / "broken.jsonl"
        graph_file.write_text('{"op":"create","entity":{"id":"know_x","properties":{"label":"Good","node_type":"concept","weight":1,"description":"ok","dimensions":{},"source_files":[]}},"timestamp":"2026-01-01T00:00:00Z"}\nNOT VALID JSON\n')
        index = {"version": "1.0", "generated_at": "now", "ontology_dir": str(ontology_dir),
                 "graphs": [{"name": "broken", "file": "broken.jsonl", "description": "",
                             "entity_count": 1, "relation_count": 0, "dimensions": [],
                             "root_entity_id": "know_x", "root_label": "Good"}]}
        (ontology_dir / ".graph-index.json").write_text(json.dumps(index))

        from x_ipe.services.ontology_graph_service import OntologyGraphService
        svc = OntologyGraphService(str(tmp_path))
        result = svc.get_graph('broken')
        assert result is not None
        nodes = result['elements']['nodes']
        assert len(nodes) == 1

    def test_empty_jsonl_file(self, tmp_path):
        """Empty JSONL file returns empty elements."""
        ontology_dir = tmp_path / ".ontology"
        ontology_dir.mkdir()
        (ontology_dir / "empty.jsonl").write_text("")
        index = {"version": "1.0", "generated_at": "now", "ontology_dir": str(ontology_dir),
                 "graphs": [{"name": "empty", "file": "empty.jsonl", "description": "",
                             "entity_count": 0, "relation_count": 0, "dimensions": [],
                             "root_entity_id": "", "root_label": ""}]}
        (ontology_dir / ".graph-index.json").write_text(json.dumps(index))

        from x_ipe.services.ontology_graph_service import OntologyGraphService
        svc = OntologyGraphService(str(tmp_path))
        result = svc.get_graph('empty')
        assert result is not None
        assert result['elements']['nodes'] == []
        assert result['elements']['edges'] == []

    def test_special_characters_in_graph_name(self, client):
        """Graph names with special chars should return 404 gracefully."""
        resp = client.get('/api/kb/ontology/graph/../../etc/passwd')
        assert resp.status_code == 404
