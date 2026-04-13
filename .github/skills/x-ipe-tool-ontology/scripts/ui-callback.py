#!/usr/bin/env python3
"""
UI Callback: Push AI Agent search results to KB Graph Viewer via Socket.IO.

FEATURE-058-F CR-001: Called after search.py completes to POST results to
the internal Flask callback endpoint, which broadcasts via SocketIO.

Usage:
    python3 ui-callback.py --results-json PATH --port PORT --token TOKEN
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import uuid


def _load_results(path: str) -> dict:
    """Load search results JSON from file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _post_callback(payload: dict, port: int, token: str) -> dict:
    """POST payload to internal callback endpoint."""
    url = f"http://localhost:{port}/api/internal/ontology/callback"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _resolve_token(cli_token: str | None) -> str:
    """Resolve auth token: CLI flag > env var > instance file."""
    if cli_token:
        return cli_token
    env_token = os.environ.get('X_IPE_INTERNAL_TOKEN', '')
    if env_token:
        return env_token
    # Auto-read from well-known file written by Flask app on startup
    token_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'instance', '.internal_token')
    try:
        with open(os.path.normpath(token_file), 'r') as f:
            return f.read().strip()
    except OSError:
        return ''


def main():
    parser = argparse.ArgumentParser(description='Push AI Agent search results to KB Graph Viewer UI')
    parser.add_argument('--results-json', required=True, help='Path to search results JSON file')
    parser.add_argument('--port', type=int, default=5858, help='Flask server port (default: 5858)')
    parser.add_argument('--token', default=None, help='Internal auth token (auto-detected if omitted)')
    args = parser.parse_args()

    token = _resolve_token(args.token)
    if not token:
        print(f"ERROR: No auth token found. Set $X_IPE_INTERNAL_TOKEN or pass --token.", file=sys.stderr)
        sys.exit(1)

    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S')

    # Load results file (AC-058F-11b: exit non-zero if missing/invalid)
    try:
        data = _load_results(args.results_json)
    except FileNotFoundError:
        print(f"[{timestamp}] ERROR: Results file not found: {args.results_json}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[{timestamp}] ERROR: Invalid JSON in results file: {e}", file=sys.stderr)
        sys.exit(1)

    # Accept both 'results' (native) and 'matches' (from search.py output)
    results = data.get('results', data.get('matches', []))
    subgraph = data.get('subgraph', {'nodes': [], 'edges': []})
    query = data.get('query', '')
    scope = data.get('scope', '')

    payload = {
        'results': results,
        'subgraph': subgraph,
        'query': query,
        'scope': scope,
        'request_id': str(uuid.uuid4()),
    }

    # POST with one retry (AC-058F-11c)
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        try:
            resp = _post_callback(payload, args.port, token)
            # Log success (AC-058F-11d)
            print(f"[{timestamp}] query=\"{query}\" results={len(results)} status=SUCCESS request_id={resp.get('request_id', '')}")
            sys.exit(0)
        except urllib.error.URLError as e:
            if attempt < max_attempts:
                print(f"[{timestamp}] WARNING: Connection failed (attempt {attempt}/{max_attempts}): {e}", file=sys.stderr)
                time.sleep(1)
            else:
                print(f"[{timestamp}] ERROR: Connection failed after {max_attempts} attempts: {e}", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"[{timestamp}] ERROR: Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
