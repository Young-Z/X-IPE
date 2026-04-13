"""
FEATURE-058-F CR-001: Ontology Callback Endpoint Tests

Tests cover:
- Internal callback endpoint auth validation (AC-058F-09f)
- Payload validation (AC-058F-09c)
- SocketIO emit on valid request (AC-058F-09b)
- Silent drop when no listeners (AC-058F-09d)
"""
import json
import pytest
from unittest.mock import patch, MagicMock


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def app_with_token():
    from x_ipe.app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['INTERNAL_AUTH_TOKEN'] = 'test-secret-token'
    return app


@pytest.fixture
def client(app_with_token):
    return app_with_token.test_client()


VALID_PAYLOAD = {
    'results': [
        {'node_id': 'know_aaa', 'label': 'Auth', 'node_type': 'concept',
         'graph': 'test-graph', 'relevance': 5, 'match_fields': ['label']},
    ],
    'subgraph': {
        'nodes': [{'data': {'id': 'know_aaa', 'label': 'Auth', 'node_type': 'concept'}}],
        'edges': [],
    },
    'query': 'auth',
    'scope': 'test-graph',
    'request_id': 'uuid-001',
}

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer test-secret-token',
}


# ============================================================================
# AUTH TESTS (AC-058F-09f)
# ============================================================================

class TestCallbackAuth:
    """be-02, be-03: Auth rejection."""

    def test_missing_auth_header(self, client):
        resp = client.post('/api/internal/ontology/callback',
                           data=json.dumps(VALID_PAYLOAD),
                           content_type='application/json')
        assert resp.status_code == 401

    def test_invalid_token(self, client):
        resp = client.post('/api/internal/ontology/callback',
                           data=json.dumps(VALID_PAYLOAD),
                           content_type='application/json',
                           headers={'Authorization': 'Bearer wrong-token'})
        assert resp.status_code == 401

    def test_malformed_auth_header(self, client):
        resp = client.post('/api/internal/ontology/callback',
                           data=json.dumps(VALID_PAYLOAD),
                           content_type='application/json',
                           headers={'Authorization': 'Basic wrong-format'})
        assert resp.status_code == 401


# ============================================================================
# PAYLOAD VALIDATION TESTS (AC-058F-09c)
# ============================================================================

class TestCallbackPayload:
    """be-04: Malformed payloads rejected."""

    def test_missing_results_field(self, client):
        payload = {'subgraph': {'nodes': [], 'edges': []}}
        resp = client.post('/api/internal/ontology/callback',
                           data=json.dumps(payload),
                           content_type='application/json',
                           headers=HEADERS)
        assert resp.status_code == 400

    def test_results_not_array(self, client):
        payload = {'results': 'not-array', 'subgraph': {'nodes': [], 'edges': []}}
        resp = client.post('/api/internal/ontology/callback',
                           data=json.dumps(payload),
                           content_type='application/json',
                           headers=HEADERS)
        assert resp.status_code == 400

    def test_missing_subgraph(self, client):
        payload = {'results': []}
        resp = client.post('/api/internal/ontology/callback',
                           data=json.dumps(payload),
                           content_type='application/json',
                           headers=HEADERS)
        assert resp.status_code == 400

    def test_empty_body(self, client):
        resp = client.post('/api/internal/ontology/callback',
                           data='',
                           content_type='application/json',
                           headers=HEADERS)
        assert resp.status_code == 400


# ============================================================================
# SUCCESSFUL EMIT TESTS (AC-058F-09b, AC-058F-09d)
# ============================================================================

class TestCallbackEmit:
    """be-01, be-05, be-07: Valid request triggers SocketIO emit."""

    def test_valid_request_returns_200(self, client):
        resp = client.post('/api/internal/ontology/callback',
                           data=json.dumps(VALID_PAYLOAD),
                           content_type='application/json',
                           headers=HEADERS)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'emitted'
        assert data['request_id'] == 'uuid-001'

    def test_emits_to_ontology_namespace(self, app_with_token):
        """Verify SocketIO.emit is called with correct namespace."""
        mock_socketio = MagicMock()
        app_with_token.extensions['socketio'] = mock_socketio

        with app_with_token.test_client() as client:
            resp = client.post('/api/internal/ontology/callback',
                               data=json.dumps(VALID_PAYLOAD),
                               content_type='application/json',
                               headers=HEADERS)
            assert resp.status_code == 200
            mock_socketio.emit.assert_called_once()
            call_args = mock_socketio.emit.call_args
            assert call_args[0][0] == 'ontology_search_result'
            assert call_args[1]['namespace'] == '/ontology'

    def test_payload_contains_all_fields(self, app_with_token):
        """be-07: Emitted payload matches expected structure."""
        mock_socketio = MagicMock()
        app_with_token.extensions['socketio'] = mock_socketio

        with app_with_token.test_client() as client:
            client.post('/api/internal/ontology/callback',
                        data=json.dumps(VALID_PAYLOAD),
                        content_type='application/json',
                        headers=HEADERS)
            emitted_data = mock_socketio.emit.call_args[0][1]
            assert 'results' in emitted_data
            assert 'subgraph' in emitted_data
            assert 'query' in emitted_data
            assert 'scope' in emitted_data
            assert 'request_id' in emitted_data

    def test_silent_drop_without_socketio(self, app_with_token):
        """be-05: No error when no SocketIO clients are connected."""
        # Remove socketio extension to simulate no-listener scenario
        app_with_token.extensions.pop('socketio', None)

        with app_with_token.test_client() as client:
            resp = client.post('/api/internal/ontology/callback',
                               data=json.dumps(VALID_PAYLOAD),
                               content_type='application/json',
                               headers=HEADERS)
            assert resp.status_code == 200


# ============================================================================
# HANDLER REGISTRATION TESTS (AC-058F-09a)
# ============================================================================

class TestOntologyHandlerRegistration:
    """be-06: Handler registers on /ontology namespace."""

    def test_register_ontology_handlers(self):
        mock_socketio = MagicMock()
        from x_ipe.handlers.ontology_handlers import register_ontology_handlers
        register_ontology_handlers(mock_socketio)
        # Verify @socketio.on decorators were registered
        assert mock_socketio.on.call_count >= 2
        namespaces = [call.kwargs.get('namespace') or call.args[1] if len(call.args) > 1 else call.kwargs.get('namespace')
                      for call in mock_socketio.on.call_args_list]
        assert all(ns == '/ontology' for ns in namespaces)
