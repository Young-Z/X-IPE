"""
App-Agent Interaction MCP Server (FEATURE-033)

Standalone MCP server (FastMCP, stdio transport) that bridges
CLI agents and the X-IPE Flask backend.

Tools:
    save_uiux_reference — persist UIUX reference data to an idea folder
"""
from fastmcp import FastMCP
import requests
import os

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


if __name__ == "__main__":
    mcp.run()
