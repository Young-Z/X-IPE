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
    """Resolve backend URL from env var, .x-ipe.yaml config, or default.

    Falls back to port 5858 if the configured port is unreachable.
    """
    env_url = os.environ.get("X_IPE_BASE_URL")
    if env_url:
        return env_url
    try:
        from x_ipe.core.config import XIPEConfig
        config = XIPEConfig.load()
        primary = f"http://{config.server_host}:{config.server_port}"
        # Quick connectivity check on the configured port
        try:
            requests.head(primary, timeout=2)
            return primary
        except requests.ConnectionError:
            pass
        # Fallback to 5858 if different from configured port
        if config.server_port != 5858:
            fallback = f"http://{config.server_host}:5858"
            try:
                requests.head(fallback, timeout=2)
                return fallback
            except requests.ConnectionError:
                pass
        return primary
    except Exception:
        return "http://127.0.0.1:5858"



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
        base = _resolve_base_url()
        resp = requests.post(
            f"{base}/api/ideas/uiux-reference",
            json=data,
            timeout=30,
        )
        return resp.json()
    except requests.ConnectionError:
        return {
            "success": False,
            "error": "BACKEND_UNREACHABLE",
            "message": f"Cannot connect to X-IPE backend at {base}",
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
    base = _resolve_base_url()
    try:
        resp = requests.get(
            f"{base}/api/workflow/{workflow_name}",
            timeout=10,
        )
        return resp.json()
    except requests.ConnectionError:
        return {
            "success": False,
            "error": "BACKEND_UNREACHABLE",
            "message": f"Cannot connect to X-IPE backend at {base}",
        }


@mcp.tool
def update_workflow_action(workflow_name: str, action: str, status: str,
                           feature_id: str = None,
                           deliverables=None,
                           context: dict = None,
                           features: list = None) -> dict:
    """Update the status of a workflow action.

    Moves an action to a new status and triggers stage gating re-evaluation.
    Supports all workflow actions across the engineering lifecycle including
    ideation (compose_idea, idea_mockup, idea_architecture), requirements
    (requirement_gathering, feature_breakdown, feature_refinement),
    design (technical_design), implementation
    (code_implementation, acceptance_test), and delivery
    (human_playground, feature_closing).

    Args:
        workflow_name: Name of the workflow.
        action: Action identifier (e.g. compose_idea, idea_mockup, requirement_gathering,
                feature_breakdown, feature_refinement, technical_design,
                code_implementation, acceptance_test, human_playground, feature_closing).
        status: New status — one of: pending, in_progress, done, skipped, failed.
        feature_id: Required for per-feature actions (implement/validation/feedback stages).
        deliverables: Optional deliverable paths — either a keyed dict (new format:
            {"tag-name": "path/to/file"}) or a list of paths (legacy format, auto-converted
            to keyed dict using template tag order). CR-003: Tag values may be arrays
            for multi-file outputs, e.g. {"raw-ideas": ["idea.md", "sketch.png"]}.
            Array values trigger schema_version "4.0". $output-folder tags do NOT
            support arrays.
        context: Optional dict of action context selections (e.g.
            {"raw-ideas": "path/to/idea.md", "uiux-reference": "N/A"}).
        features: Optional list of feature objects for feature_breakdown action.
            Each feature: {"id": "FEATURE-XXX", "name": "...", "depends_on": [...]}.
            When provided with action=feature_breakdown and status=done, automatically
            populates per-feature structures and sets next_actions_suggested to
            features with no dependencies.
    """
    payload = {"action": action, "status": status}
    if feature_id:
        payload["feature_id"] = feature_id
    if deliverables:
        payload["deliverables"] = deliverables
    if context:
        payload["context"] = context
    if features:
        payload["features"] = features

    base = _resolve_base_url()
    try:
        resp = requests.post(
            f"{base}/api/workflow/{workflow_name}/action",
            json=payload,
            timeout=10,
        )
        return resp.json()
    except requests.ConnectionError:
        return {
            "success": False,
            "error": "BACKEND_UNREACHABLE",
            "message": f"Cannot connect to X-IPE backend at {base}",
        }


def main():
    """Entry point for x-ipe-mcp console script (stdio transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
