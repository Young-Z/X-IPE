"""
App-Agent Interaction MCP Server (FEATURE-033)

Standalone MCP server (FastMCP, stdio transport) that bridges
CLI agents and the X-IPE Flask backend.

Tools:
    save_uiux_reference — persist UIUX reference data to an idea folder
    inject_script — inject JavaScript into browser page via CDP (v1.1)
"""
from fastmcp import FastMCP
from pathlib import Path
import requests
import os

from x_ipe.mcp.cdp_client import CDPClient

mcp = FastMCP(name="x-ipe-app-and-agent-interaction")


def _resolve_base_url() -> str:
    """Resolve backend URL from env var, .x-ipe.yaml config, or default."""
    env_url = os.environ.get("X_IPE_BASE_URL")
    if env_url:
        return env_url
    try:
        from x_ipe.core.config import XIPEConfig
        config = XIPEConfig.load()
        return f"http://{config.server_host}:{config.server_port}"
    except Exception:
        return "http://127.0.0.1:5858"


BASE_URL = _resolve_base_url()

REQUIRED_FIELDS = ["version", "source_url", "timestamp", "idea_folder"]


@mcp.tool
def save_uiux_reference(data: dict) -> dict:
    """Save UIUX reference data (colors, elements, screenshots, design tokens)
    to an idea folder. The data is validated and persisted by the X-IPE backend.

    Args:
        data: Reference data JSON with required fields: version, source_url,
              timestamp, idea_folder. Must include at least one of: colors,
              elements, design_tokens.
    """
    missing = [f for f in REQUIRED_FIELDS if f not in data or not data[f]]
    if missing:
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": f"Missing required fields: {', '.join(missing)}",
        }

    try:
        resp = requests.post(
            f"{BASE_URL}/api/ideas/uiux-reference",
            json=data,
            timeout=30,
        )
        return resp.json()
    except requests.ConnectionError:
        return {
            "success": False,
            "error": "BACKEND_UNREACHABLE",
            "message": f"Cannot connect to X-IPE backend at {BASE_URL}",
        }
    except requests.Timeout:
        return {
            "success": False,
            "error": "BACKEND_TIMEOUT",
            "message": "Request to X-IPE backend timed out (30s)",
        }


@mcp.tool
def inject_script(
    file_path: str | None = None,
    script: str | None = None,
    target_url: str | None = None,
    cdp_port: int = 9222,
) -> dict:
    """Inject JavaScript into the active browser page via Chrome DevTools Protocol.

    Reads a JS file from disk or accepts inline script, then executes it in the
    browser page context via CDP Runtime.evaluate. Requires Chrome to be running
    with --remote-debugging-port.

    Args:
        file_path: Path to a .js file to inject (mutually exclusive with script).
        script: Inline JavaScript code to execute (mutually exclusive with file_path).
        target_url: Optional URL pattern to select a specific browser tab.
        cdp_port: Chrome remote debugging port (default: 9222).
    """
    # Validate: exactly one of file_path or script
    if bool(file_path) == bool(script):
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Provide exactly one of 'file_path' or 'script'",
        }

    # Read file if file_path provided
    if file_path:
        path = Path(file_path).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file():
            return {
                "success": False,
                "error": "FILE_NOT_FOUND",
                "message": f"Script file not found: {path}",
            }
        script = path.read_text(encoding="utf-8")

    # Execute via CDP
    try:
        client = CDPClient(port=cdp_port)
        resp = client.evaluate(script, target_url=target_url)
    except ConnectionError as e:
        return {"success": False, "error": "CDP_CONNECTION_FAILED", "message": str(e)}
    except ValueError as e:
        return {"success": False, "error": "CDP_NO_PAGE", "message": str(e)}

    # Parse CDP response
    result = resp.get("result", {})
    if "exceptionDetails" in result:
        exc = result["exceptionDetails"]
        return {
            "success": False,
            "error": "SCRIPT_EVALUATION_ERROR",
            "message": exc.get("text", "Script evaluation failed"),
            "details": {
                "exception": exc.get("exception", {}).get("description", ""),
            },
        }

    return {
        "success": True,
        "result": result.get("result", {}).get("value"),
        "target_url": target_url,
    }


if __name__ == "__main__":
    mcp.run()
