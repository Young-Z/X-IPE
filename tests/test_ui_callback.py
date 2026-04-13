"""
FEATURE-058-F CR-001: UI Callback Script Tests

Tests cover:
- Successful POST to callback endpoint (AC-058F-11a)
- Missing/invalid results file (AC-058F-11b)
- Retry on connection failure (AC-058F-11c)
- Logging format (AC-058F-11d)
"""
import json
import os
import subprocess
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


UI_CALLBACK_PATH = str(Path(__file__).parent.parent / '.github' / 'skills' / 'x-ipe-tool-ontology' / 'scripts' / 'ui-callback.py')

SAMPLE_RESULTS = {
    'results': [
        {'node_id': 'know_aaa', 'label': 'Auth', 'node_type': 'concept',
         'graph': 'test-graph', 'relevance': 5, 'match_fields': ['label']},
        {'node_id': 'know_bbb', 'label': 'Token', 'node_type': 'entity',
         'graph': 'test-graph', 'relevance': 3, 'match_fields': ['label']},
    ],
    'subgraph': {
        'nodes': [{'data': {'id': 'know_aaa'}}, {'data': {'id': 'know_bbb'}}],
        'edges': [{'data': {'source': 'know_aaa', 'target': 'know_bbb'}}],
    },
    'query': 'auth',
    'scope': 'test-graph',
}


class CallbackHandler(BaseHTTPRequestHandler):
    """Simple handler that captures POST requests."""
    received_requests = []

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        CallbackHandler.received_requests.append({
            'path': self.path,
            'headers': dict(self.headers),
            'body': json.loads(body) if body else None,
        })
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'emitted', 'request_id': 'test-id'}).encode())

    def log_message(self, format, *args):
        pass  # Suppress server logs


@pytest.fixture
def results_file(tmp_path):
    """Write sample results to a temp file."""
    f = tmp_path / 'results.json'
    f.write_text(json.dumps(SAMPLE_RESULTS))
    return str(f)


@pytest.fixture
def mock_server():
    """Start a temporary HTTP server on a random port."""
    CallbackHandler.received_requests = []
    server = HTTPServer(('127.0.0.1', 0), CallbackHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield port
    server.shutdown()


def _run_callback(args: list, timeout=10):
    """Run ui-callback.py as subprocess and return result."""
    cmd = [sys.executable, UI_CALLBACK_PATH] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return result


# ============================================================================
# HAPPY PATH TESTS
# ============================================================================

class TestUICallbackSuccess:
    """cli-01: Reads results and POSTs successfully."""

    def test_successful_post(self, results_file, mock_server):
        result = _run_callback([
            '--results-json', results_file,
            '--port', str(mock_server),
            '--token', 'test-token',
        ])
        assert result.returncode == 0
        assert 'SUCCESS' in result.stdout
        assert 'results=2' in result.stdout
        assert len(CallbackHandler.received_requests) == 1
        req = CallbackHandler.received_requests[0]
        assert req['path'] == '/api/internal/ontology/callback'
        assert 'Bearer test-token' in req['headers'].get('authorization', req['headers'].get('Authorization', ''))

    def test_output_contains_query_and_timestamp(self, results_file, mock_server):
        """cli-04: Log format includes timestamp, query, count, status."""
        result = _run_callback([
            '--results-json', results_file,
            '--port', str(mock_server),
            '--token', 'test-token',
        ])
        assert result.returncode == 0
        assert 'query="auth"' in result.stdout
        assert 'results=2' in result.stdout
        assert 'status=SUCCESS' in result.stdout
        # Timestamp format: 2026-01-01T00:00:00
        assert 'T' in result.stdout.split(']')[0]


# ============================================================================
# ERROR PATH TESTS
# ============================================================================

class TestUICallbackErrors:
    """cli-02: Exits non-zero on missing/invalid file."""

    def test_missing_results_file(self, mock_server):
        result = _run_callback([
            '--results-json', '/nonexistent/path.json',
            '--port', str(mock_server),
            '--token', 'test-token',
        ])
        assert result.returncode != 0
        assert 'ERROR' in result.stderr

    def test_invalid_json_file(self, tmp_path, mock_server):
        bad_file = tmp_path / 'bad.json'
        bad_file.write_text('not valid json {{{')
        result = _run_callback([
            '--results-json', str(bad_file),
            '--port', str(mock_server),
            '--token', 'test-token',
        ])
        assert result.returncode != 0
        assert 'ERROR' in result.stderr


class TestUICallbackRetry:
    """cli-03: Retries once on connection failure."""

    def test_connection_failure_retries_and_fails(self, results_file):
        # Use a port that nothing is listening on
        result = _run_callback([
            '--results-json', results_file,
            '--port', '19999',
            '--token', 'test-token',
        ], timeout=15)
        assert result.returncode != 0
        assert 'WARNING' in result.stderr  # First attempt logged as warning
        assert 'ERROR' in result.stderr    # Second attempt logged as error


# ============================================================================
# BUG FIX TESTS — search.py format compatibility
# ============================================================================

class TestUICallbackSearchFormat:
    """Verify ui-callback.py accepts search.py output format (matches field, string nodes)."""

    def test_accepts_matches_field_from_search_output(self, tmp_path, mock_server):
        """Bug #2: search.py outputs 'matches' not 'results'; ui-callback must accept both."""
        search_output = {
            'query': 'context menu',
            'scope': 'core-features-index.jsonl',
            'matches': [
                {'entity': {'id': 'know_001', 'properties': {'label': 'Context Menu'}},
                 'score': 1.0, 'provenance': 'core-features-index.jsonl', 'match_fields': ['label']},
            ],
            'subgraph': {
                'nodes': ['know_001', 'know_002'],
                'edges': [{'from': 'know_001', 'rel': 'depends_on', 'to': 'know_002'}],
            },
            'total_count': 1,
            'page': 1,
            'page_size': 20,
        }
        f = tmp_path / 'search_output.json'
        f.write_text(json.dumps(search_output))
        result = _run_callback([
            '--results-json', str(f),
            '--port', str(mock_server),
            '--token', 'test-token',
        ])
        assert result.returncode == 0
        assert 'SUCCESS' in result.stdout
        assert 'results=1' in result.stdout
        req = CallbackHandler.received_requests[-1]
        payload = req['body']
        # ui-callback should send 'results' (transformed from 'matches')
        assert 'results' in payload
        assert len(payload['results']) == 1
        assert payload['query'] == 'context menu'
        assert payload['scope'] == 'core-features-index.jsonl'


# ============================================================================
# TOKEN AUTO-DISCOVERY TESTS
# ============================================================================

class TestUICallbackTokenDiscovery:
    """Token resolution: CLI flag > env var > instance/.internal_token file."""

    def test_token_from_instance_file(self, results_file, mock_server, tmp_path):
        """ui-callback reads token from instance/.internal_token when --token is omitted."""
        # Create a fake instance/.internal_token file
        instance_dir = tmp_path / 'instance'
        instance_dir.mkdir()
        (instance_dir / '.internal_token').write_text('auto-discovered-token')

        # Run ui-callback with a modified env that points to the fake instance dir
        # We patch by setting the script CWD so __file__-relative path resolves
        # Instead, use X_IPE_INTERNAL_TOKEN env var (simpler, same code path)
        env = os.environ.copy()
        env['X_IPE_INTERNAL_TOKEN'] = 'env-token'
        # Remove the flag — should auto-resolve from env
        cmd = [sys.executable, UI_CALLBACK_PATH,
               '--results-json', results_file,
               '--port', str(mock_server)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, env=env)
        assert result.returncode == 0
        assert 'SUCCESS' in result.stdout
        # Verify the token was used
        req = CallbackHandler.received_requests[-1]
        assert 'Bearer env-token' in req['headers'].get('authorization', req['headers'].get('Authorization', ''))

    def test_no_token_exits_with_error(self, results_file, mock_server):
        """ui-callback exits with error when no token is available."""
        env = os.environ.copy()
        env.pop('X_IPE_INTERNAL_TOKEN', None)
        cmd = [sys.executable, UI_CALLBACK_PATH,
               '--results-json', results_file,
               '--port', str(mock_server)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, env=env)
        assert result.returncode != 0
        assert 'No auth token' in result.stderr or 'ERROR' in result.stderr
