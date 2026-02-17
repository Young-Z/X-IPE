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

    When elements include html_css (outer_html, computed_styles), the service
    automatically generates structured output:
    - page-element-references/resources/{id}-structure.html (component HTML)
    - page-element-references/resources/{id}-styles.css (computed CSS)
    - page-element-references/summarized-uiux-reference.md (colors, fonts, resources)
    - mimic-strategy.md (6-dimension validation rubric)

    Args:
        data: Reference data JSON with required fields: version, source_url,
              timestamp, idea_folder. Must include at least one of: colors,
              elements, design_tokens. Optional: static_resources (list of
              {type, src, usage} for fonts/icons/images).
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
def get_workflow_state(workflow_name: str) -> dict:
    """Get the full state of an engineering workflow.

    Returns the current stage, action statuses, feature lanes,
    and dependency information for the named workflow.

    Args:
        workflow_name: Name of the workflow (alphanumeric with hyphens).
    """
    try:
        resp = requests.get(
            f"{BASE_URL}/api/workflow/{workflow_name}",
            timeout=10,
        )
        return resp.json()
    except requests.ConnectionError:
        return {
            "success": False,
            "error": "BACKEND_UNREACHABLE",
            "message": f"Cannot connect to X-IPE backend at {BASE_URL}",
        }


@mcp.tool
def update_workflow_action(workflow_name: str, action: str, status: str,
                           feature_id: str = None,
                           deliverables: list = None) -> dict:
    """Update the status of a workflow action.

    Moves an action (e.g. compose_idea, technical_design) to a new status
    and triggers stage gating re-evaluation.

    Args:
        workflow_name: Name of the workflow.
        action: Action identifier (e.g. compose_idea, feature_refinement).
        status: New status — one of: pending, in_progress, done, skipped, failed.
        feature_id: Required for per-feature actions (implement/validation/feedback stages).
        deliverables: Optional list of deliverable paths produced by the action.
    """
    payload = {"action": action, "status": status}
    if feature_id:
        payload["feature_id"] = feature_id
    if deliverables:
        payload["deliverables"] = deliverables

    try:
        resp = requests.post(
            f"{BASE_URL}/api/workflow/{workflow_name}/action",
            json=payload,
            timeout=10,
        )
        return resp.json()
    except requests.ConnectionError:
        return {
            "success": False,
            "error": "BACKEND_UNREACHABLE",
            "message": f"Cannot connect to X-IPE backend at {BASE_URL}",
        }


if __name__ == "__main__":
    mcp.run()
