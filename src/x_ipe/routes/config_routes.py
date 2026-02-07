"""
Config Routes Blueprint

FEATURE-027-A: CLI Adapter Registry & Service

Provides:
- GET /api/config/cli-adapter — Active CLI adapter info
"""
from flask import Blueprint, jsonify, current_app

from x_ipe.tracing import x_ipe_tracing

config_bp = Blueprint('config', __name__)


def get_cli_adapter_service():
    """Get CLI adapter service from app config."""
    return current_app.config.get('CLI_ADAPTER_SERVICE')


@config_bp.route('/api/config/cli-adapter', methods=['GET'])
@x_ipe_tracing()
def get_cli_adapter():
    """
    GET /api/config/cli-adapter

    Return the active CLI adapter configuration.

    Response (200):
        - success: true
        - adapter_name: string
        - display_name: string
        - command: string
        - prompt_format: string
        - is_installed: bool
    """
    service = get_cli_adapter_service()
    if not service:
        return jsonify({'success': False, 'message': 'CLI adapter service not available'}), 503

    adapter = service.get_active_adapter()
    return jsonify({
        'success': True,
        'adapter_name': adapter.name,
        'display_name': adapter.display_name,
        'command': adapter.command,
        'run_args': adapter.run_args,
        'inline_prompt_flag': adapter.inline_prompt_flag,
        'prompt_format': adapter.prompt_format,
        'is_installed': service.is_installed(adapter.name),
    })
