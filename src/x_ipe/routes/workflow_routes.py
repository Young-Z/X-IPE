"""
Workflow Routes Blueprint

EPIC-036 / FEATURE-036-A: Workflow Manager & State Persistence

Provides:
- Workflow CRUD (create, list, get, delete)
- Action status updates
- Feature management
- Idea folder linking
- Dependency checking
- Next-action suggestion
"""
import os
from flask import Blueprint, jsonify, request, current_app

from x_ipe.services.workflow_manager_service import WorkflowManagerService
from x_ipe.tracing import x_ipe_tracing

workflow_bp = Blueprint('workflow', __name__)


def _get_service():
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    return WorkflowManagerService(project_root)


@workflow_bp.route('/api/workflow/create', methods=['POST'])
@x_ipe_tracing()
def create_workflow():
    data = request.get_json(force=True)
    name = data.get('name', '')
    result = _get_service().create_workflow(name)
    if result.get('success'):
        return jsonify(result), 201
    error = result.get('error', '')
    status_code = 409 if error == 'ALREADY_EXISTS' else 400
    return jsonify(result), status_code


@workflow_bp.route('/api/workflow/list', methods=['GET'])
@x_ipe_tracing()
def list_workflows():
    workflows = _get_service().list_workflows()
    return jsonify({'success': True, 'data': workflows})


@workflow_bp.route('/api/workflow/<name>', methods=['GET'])
@x_ipe_tracing()
def get_workflow(name):
    result = _get_service().get_workflow(name)
    if 'error' in result and result.get('success') is False:
        return jsonify(result), 404
    return jsonify({'success': True, 'data': result})


@workflow_bp.route('/api/workflow/<name>', methods=['DELETE'])
@x_ipe_tracing()
def delete_workflow(name):
    result = _get_service().delete_workflow(name)
    if result.get('success'):
        return jsonify(result)
    return jsonify(result), 404


@workflow_bp.route('/api/workflow/<name>/action', methods=['POST'])
@x_ipe_tracing()
def update_action(name):
    data = request.get_json(force=True)
    action = data.get('action', '')
    status = data.get('status', '')
    feature_id = data.get('feature_id')
    deliverables = data.get('deliverables', [])
    result = _get_service().update_action_status(
        name, action, status, feature_id=feature_id, deliverables=deliverables)
    if result.get('success'):
        return jsonify(result)
    error = result.get('error', '')
    if error == 'NOT_FOUND':
        return jsonify(result), 404
    return jsonify(result), 400


@workflow_bp.route('/api/workflow/<name>/features', methods=['POST'])
@x_ipe_tracing()
def add_features(name):
    data = request.get_json(force=True)
    features = data.get('features', [])
    result = _get_service().add_features(name, features)
    if result.get('success'):
        return jsonify(result)
    return jsonify(result), 404


@workflow_bp.route('/api/workflow/<name>/link-idea', methods=['POST'])
@x_ipe_tracing()
def link_idea(name):
    data = request.get_json(force=True)
    idea_folder_path = data.get('idea_folder_path') or data.get('idea_folder', '')
    result = _get_service().link_idea_folder(name, idea_folder_path)
    if result.get('success'):
        return jsonify(result)
    error = result.get('error', '')
    if error == 'NOT_FOUND':
        return jsonify(result), 404
    return jsonify(result), 400


@workflow_bp.route('/api/workflow/<name>/dependencies/<feature_id>', methods=['GET'])
@x_ipe_tracing()
def check_dependencies(name, feature_id):
    result = _get_service().check_dependencies(name, feature_id)
    if 'error' in result and result.get('success') is False:
        return jsonify(result), 404
    return jsonify({'success': True, 'data': result})


@workflow_bp.route('/api/workflow/<name>/next-action', methods=['GET'])
@x_ipe_tracing()
def get_next_action(name):
    result = _get_service().get_next_action(name)
    if 'error' in result and result.get('success') is False:
        return jsonify(result), 404
    return jsonify({'success': True, 'data': result})


@workflow_bp.route('/api/workflow/<name>/deliverables', methods=['GET'])
@x_ipe_tracing()
def get_deliverables(name):
    result = _get_service().resolve_deliverables(name)
    if 'error' in result and result.get('success') is False:
        return jsonify(result), 404
    return jsonify({'success': True, 'data': result})


def get_project_root():
    return current_app.config.get('PROJECT_ROOT', os.getcwd())


@workflow_bp.route('/api/workflow/<name>/deliverables/tree', methods=['GET'])
def get_deliverable_tree(name):
    """List folder contents for deliverable viewer (FEATURE-038-C)."""
    folder_path = request.args.get('path')
    if not folder_path:
        return jsonify({'error': 'Missing path parameter'}), 400

    root = get_project_root()
    abs_path = os.path.normpath(os.path.join(root, folder_path))

    # Security: prevent path traversal
    if not abs_path.startswith(os.path.normpath(root)):
        return jsonify({'error': 'Path traversal not allowed'}), 403

    if not os.path.isdir(abs_path):
        return jsonify({'error': 'Folder not found'}), 404

    entries = []
    try:
        for entry_name in sorted(os.listdir(abs_path))[:50]:
            entry_path = os.path.join(abs_path, entry_name)
            rel = os.path.relpath(entry_path, root)
            entry_type = 'dir' if os.path.isdir(entry_path) else 'file'
            entries.append({
                'name': entry_name,
                'type': entry_type,
                'path': rel + ('/' if entry_type == 'dir' else '')
            })
    except OSError:
        return jsonify({'error': 'Cannot read folder'}), 500

    return jsonify(entries)
