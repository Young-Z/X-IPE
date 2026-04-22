#!/usr/bin/env python3
"""Graph connector: push ontology data to X-IPE knowledge graph server.

Resolves port and auth token, reads graph JSON, and sends HTTP POST
to the ontology callback endpoint with retry logic.

JSON to stdout on success; JSON to stderr + exit 1 on error.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


MAX_RETRIES = 2
RETRY_DELAY = 1
REQUEST_TIMEOUT = 10


def _exit_error(error: str, message: str) -> None:
    print(json.dumps({"success": False, "error": error, "message": message}),
          file=sys.stderr)
    sys.exit(1)


def _ok(data: dict) -> None:
    print(json.dumps({"success": True, **data}, ensure_ascii=False))


def _find_git_root() -> Path | None:
    """Walk from CWD upward to find .git directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    if (current / ".git").exists():
        return current
    return None


def _find_x_ipe_yaml() -> Path | None:
    """Search upward from CWD to git root for .x-ipe.yaml."""
    git_root = _find_git_root()
    if not git_root:
        return None
    current = Path.cwd()
    while True:
        candidate = current / ".x-ipe.yaml"
        if candidate.exists():
            return candidate
        if current == git_root:
            break
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _read_port_from_yaml(path: Path) -> int | None:
    """Read server.port from a YAML file. Returns None if not found."""
    try:
        import yaml  # noqa: F811
    except ImportError:
        # Fallback: simple regex parse for server.port
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return None
        import re
        # Look for server:\n  port: NNN pattern
        m = re.search(r"server:\s*\n\s+port:\s*(\d+)", text)
        if m:
            return int(m.group(1))
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            server = data.get("server", {})
            if isinstance(server, dict):
                port_val = server.get("port")
                if isinstance(port_val, int) and 1 <= port_val <= 65535:
                    return port_val
    except Exception:
        pass
    return None


def _resolve_port(cli_port: int | None) -> int:
    """Resolve server port: CLI flag → .x-ipe.yaml → defaults → 5858."""
    if cli_port is not None and cli_port != 0:
        return cli_port

    # 1. Search upward from CWD for .x-ipe.yaml
    project_yaml = _find_x_ipe_yaml()
    if project_yaml:
        port = _read_port_from_yaml(project_yaml)
        if port is not None:
            return port

    # 2. Fallback to defaults file
    git_root = _find_git_root()
    if git_root:
        defaults_path = git_root / "src" / "x_ipe" / "defaults" / ".x-ipe.yaml"
        if defaults_path.exists():
            port = _read_port_from_yaml(defaults_path)
            if port is not None:
                return port

    # 3. Hardcoded default
    return 5858


def _resolve_token(cli_token: str | None) -> str:
    """Resolve auth token: CLI → env var → instance/.internal_token → error."""
    # 1. CLI flag
    if cli_token:
        return cli_token

    # 2. Environment variable
    env_token = os.environ.get("X_IPE_INTERNAL_TOKEN", "").strip()
    if env_token:
        return env_token

    # 3. instance/.internal_token file
    git_root = _find_git_root()
    if git_root:
        token_path = git_root / "instance" / ".internal_token"
        if token_path.exists():
            try:
                token = token_path.read_text(encoding="utf-8").strip()
                if token:
                    return token
            except Exception:
                pass

    _exit_error("AUTH_TOKEN_NOT_FOUND",
                "No auth token found. Checked: --token flag, "
                "$X_IPE_INTERNAL_TOKEN env var, instance/.internal_token file")
    return ""  # unreachable, satisfies type checker


def cmd_connect(args: argparse.Namespace) -> None:
    graph_path = Path(args.graph_json)

    if not graph_path.exists():
        _exit_error("GRAPH_JSON_NOT_FOUND",
                    f"Graph JSON file not found: {graph_path}")

    # Read and validate JSON
    try:
        raw = graph_path.read_text(encoding="utf-8")
        graph_data = json.loads(raw)
    except json.JSONDecodeError as e:
        _exit_error("INVALID_GRAPH_JSON",
                    f"Invalid JSON in {graph_path}: {e}")
    except UnicodeDecodeError:
        _exit_error("INVALID_GRAPH_JSON",
                    f"File is not valid UTF-8: {graph_path}")

    port = _resolve_port(args.port)
    token = _resolve_token(args.token)

    payload = {
        "results": graph_data,
        "subgraph": "ontology",
        "query": args.query or "",
        "scope": args.scope or "",
        "request_id": str(uuid.uuid4()),
    }

    url = f"http://localhost:{port}/api/internal/ontology/callback"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            body = json.dumps(payload).encode("utf-8")
            req = Request(url, data=body, headers=headers, method="POST")
            with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                status_code = resp.status
                resp_body = resp.read().decode("utf-8", errors="replace")

            if 200 <= status_code < 300:
                _ok({
                    "operation": "connector",
                    "result": {
                        "callback_status": "delivered",
                        "server_response": {
                            "status_code": status_code,
                            "body": resp_body,
                        },
                        "port_used": port,
                        "attempts": attempt,
                    },
                })
                return
            else:
                last_error = f"HTTP {status_code}: {resp_body[:200]}"
        except URLError as e:
            last_error = str(e.reason) if hasattr(e, "reason") else str(e)
        except Exception as e:
            last_error = str(e)

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    # All retries exhausted
    _exit_error("CONNECTION_FAILED",
                f"Failed after {MAX_RETRIES} attempts. Last error: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Knowledge graph connector")
    sub = parser.add_subparsers(dest="command")

    p_connect = sub.add_parser("connect", help="Push ontology to graph server")
    p_connect.add_argument("--graph-json", required=True,
                           help="Path to ontology JSON file")
    p_connect.add_argument("--port", type=int, default=None,
                           help="Server port (auto-resolved if not provided)")
    p_connect.add_argument("--token", default=None,
                           help="Auth token (auto-resolved if not provided)")
    p_connect.add_argument("--query", default="",
                           help="Original query string")
    p_connect.add_argument("--scope", default="",
                           help="Scope hint")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "connect":
        cmd_connect(args)


if __name__ == "__main__":
    main()
