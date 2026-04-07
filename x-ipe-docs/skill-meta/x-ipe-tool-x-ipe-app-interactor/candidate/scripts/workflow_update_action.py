#!/usr/bin/env python3
"""Update workflow action status — replaces MCP update_workflow_action tool.

Usage:
    python3 workflow_update_action.py --workflow NAME --action ACTION --status STATUS
        [--feature-id ID] [--deliverables JSON] [--context JSON] [--features JSON]
        [--format json|text] [--lock-timeout SECS]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (
    EXIT_VALIDATION_ERROR,
    atomic_read_json,
    atomic_write_json,
    exit_with_error,
    get_folder_tags,
    get_template_tags,
    load_workflow_template,
    output_result,
    resolve_project_root,
    resolve_workflow_dir,
    with_file_lock,
)

VALID_STATUSES = {"pending", "in_progress", "done", "skipped", "failed"}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update workflow action status, deliverables, and context.",
    )
    parser.add_argument("--workflow", required=True, help="Workflow name")
    parser.add_argument("--action", required=True, help="Action identifier")
    parser.add_argument("--status", required=True, help="New status")
    parser.add_argument("--feature-id", default=None, help="Feature ID for per-feature actions")
    parser.add_argument("--deliverables", default=None, help="Deliverables as JSON string (dict or list)")
    parser.add_argument("--context", default=None, help="Context dict as JSON string")
    parser.add_argument("--features", default=None, help="Feature objects list for feature_breakdown")
    parser.add_argument(
        "--format", choices=["json", "text"], default="json", dest="fmt",
        help="Output format (default: json)",
    )
    parser.add_argument("--lock-timeout", type=int, default=10, help="Lock timeout in seconds (default: 10)")
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Template helpers
# ---------------------------------------------------------------------------

def build_stage_config(template: dict) -> dict:
    """Derive stage config from workflow template.

    Returns dict mapping stage_name -> {type, mandatory_actions, optional_actions, next_stage}.
    """
    config = {}
    for stage_name, stage_def in template.get("stages", {}).items():
        mandatory = []
        optional = []
        for action_name, action_def in stage_def.get("actions", {}).items():
            if action_def.get("optional", False):
                optional.append(action_name)
            else:
                mandatory.append(action_name)
        config[stage_name] = {
            "type": stage_def.get("type", "shared"),
            "mandatory_actions": mandatory,
            "optional_actions": optional,
            "next_stage": stage_def.get("next_stage"),
        }
    return config


def build_next_actions_map(template: dict) -> dict[str, list[str]]:
    """Build action -> next_actions_suggested mapping from template."""
    mapping: dict[str, list[str]] = {}
    for stage_def in template.get("stages", {}).values():
        for action_name, action_def in stage_def.get("actions", {}).items():
            mapping[action_name] = action_def.get("next_actions_suggested", [])
    return mapping


# ---------------------------------------------------------------------------
# Deliverable validation
# ---------------------------------------------------------------------------

def convert_list_to_keyed(template: dict, action: str, deliverables_list: list) -> dict:
    """Convert legacy list format to keyed dict using template tag order."""
    tags = get_template_tags(template, action)
    return {tags[i]: path for i, path in enumerate(deliverables_list) if i < len(tags)}


def validate_deliverables(template: dict, action: str, deliverables: dict) -> None:
    """Validate deliverable tags against template. Exits on error."""
    expected = set(get_template_tags(template, action))
    actual = set(deliverables.keys())

    missing = expected - actual
    if missing:
        # Warning only — operation proceeds
        pass

    unexpected = actual - expected
    if unexpected:
        exit_with_error(
            EXIT_VALIDATION_ERROR,
            "INVALID_DELIVERABLES",
            f"Unexpected deliverable tags for action '{action}': {unexpected}",
        )

    folder_tags = get_folder_tags(template, action)
    for tag, val in deliverables.items():
        if tag in folder_tags and isinstance(val, list):
            exit_with_error(
                EXIT_VALIDATION_ERROR,
                "INVALID_DELIVERABLES",
                f"Folder tag '{tag}' must be a scalar string, not an array",
            )
        if isinstance(val, list):
            for i, elem in enumerate(val):
                if not isinstance(elem, str) or not elem.strip():
                    exit_with_error(
                        EXIT_VALIDATION_ERROR,
                        "INVALID_DELIVERABLES",
                        f"Tag '{tag}' array element [{i}] must be a non-empty string",
                    )


def determine_schema_version(deliverables: dict) -> str | None:
    """Return '4.0' if array values present, '3.0' for keyed dict, None for legacy."""
    if not isinstance(deliverables, dict):
        return None
    if any(isinstance(v, list) for v in deliverables.values()):
        return "4.0"
    return "3.0"


# ---------------------------------------------------------------------------
# State mutation helpers
# ---------------------------------------------------------------------------

def _find_feature(state: dict, feature_id: str) -> dict | None:
    """Find a feature dict in the features array by ID."""
    for feat in state.get("features", []):
        if feat.get("feature_id") == feature_id:
            return feat
    return None


def _apply_update(action_data: dict, status: str, deliverables, context,
                  next_actions_map: dict, action: str, state: dict) -> None:
    """Apply status/deliverables/context update to an action_data dict.

    Shared by both shared and feature action updaters.
    """
    action_data["status"] = status

    if deliverables is not None:
        action_data["deliverables"] = deliverables
        new_ver = determine_schema_version(deliverables)
        if new_ver:
            cur_ver = state.get("schema_version", "2.0")
            if new_ver > cur_ver:
                state["schema_version"] = new_ver
        # Default context to {} for keyed deliverables when no context provided
        if isinstance(deliverables, dict) and context is None:
            if "context" not in action_data:
                action_data["context"] = {}

    if context is not None:
        action_data["context"] = context

    # Set/remove next_actions_suggested based on status
    if status == "done" and action in next_actions_map:
        action_data["next_actions_suggested"] = next_actions_map[action]
    elif status != "done":
        action_data.pop("next_actions_suggested", None)


# ---------------------------------------------------------------------------
# Stage gating
# ---------------------------------------------------------------------------

def _is_shared_stage_ready_to_unlock(state: dict, stage_name: str,
                                     stage_config: dict, stage_order: list[str]) -> bool:
    """Check if a shared stage's predecessor has all mandatory actions done."""
    shared_stages = [s for s in stage_order if stage_config[s]["type"] == "shared"]
    idx = shared_stages.index(stage_name) if stage_name in shared_stages else -1
    if idx <= 0:
        return False
    prev_name = shared_stages[idx - 1]
    prev_stage = state["shared"].get(prev_name, {})
    prev_cfg = stage_config.get(prev_name, {})
    if prev_stage.get("status") not in ("in_progress",):
        return False
    actions = prev_stage.get("actions", {})
    return all(
        actions.get(a, {}).get("status") in ("done", "skipped")
        for a in prev_cfg.get("mandatory_actions", [])
    )


def _try_unlock_shared_stage(state: dict, stage_name: str,
                             stage_config: dict, stage_order: list[str]) -> bool:
    """Complete predecessor shared stage and unlock stage_name."""
    if not _is_shared_stage_ready_to_unlock(state, stage_name, stage_config, stage_order):
        return False
    shared_stages = [s for s in stage_order if stage_config[s]["type"] == "shared"]
    idx = shared_stages.index(stage_name)
    if idx > 0:
        prev_name = shared_stages[idx - 1]
        state["shared"][prev_name]["status"] = "completed"
    state["shared"][stage_name]["status"] = "in_progress"
    state["current_stage"] = stage_name
    return True


def _is_feature_stage_ready_to_unlock(state: dict, feature: dict, stage_name: str,
                                      stage_config: dict, stage_order: list[str]) -> bool:
    """Check if a feature's per-feature stage predecessor is ready."""
    if stage_name == "implement":
        req_cfg = stage_config.get("requirement", {})
        req_stage = state["shared"].get("requirement", {})
        actions = req_stage.get("actions", {})
        return all(
            actions.get(a, {}).get("status") in ("done", "skipped")
            for a in req_cfg.get("mandatory_actions", [])
        )
    pf_stages = [s for s in stage_order if stage_config[s]["type"] == "per_feature"]
    idx = pf_stages.index(stage_name) if stage_name in pf_stages else -1
    if idx <= 0:
        return False
    prev_name = pf_stages[idx - 1]
    prev_cfg = stage_config.get(prev_name, {})
    prev_stage = feature.get(prev_name, {})
    if prev_stage.get("status") not in ("in_progress", "done"):
        return False
    actions = prev_stage.get("actions", {})
    return all(
        actions.get(a, {}).get("status") in ("done", "skipped")
        for a in prev_cfg.get("mandatory_actions", [])
    )


def _try_unlock_feature_stage(state: dict, feature: dict, stage_name: str,
                              stage_config: dict, stage_order: list[str]) -> bool:
    """Unlock a per-feature stage for a specific feature."""
    if not _is_feature_stage_ready_to_unlock(state, feature, stage_name, stage_config, stage_order):
        return False
    if stage_name == "implement":
        req_stage = state["shared"].get("requirement", {})
        if req_stage.get("status") == "in_progress":
            req_stage["status"] = "completed"
    else:
        pf_stages = [s for s in stage_order if stage_config[s]["type"] == "per_feature"]
        idx = pf_stages.index(stage_name)
        if idx > 0:
            prev_name = pf_stages[idx - 1]
            feature[prev_name]["status"] = "done"
    feature[stage_name]["status"] = "in_progress"
    _update_current_stage(state, stage_config, stage_order)
    return True


def _update_current_stage(state: dict, stage_config: dict, stage_order: list[str]) -> None:
    """Set current_stage to the highest stage with activity."""
    for stage_name in stage_order:
        cfg = stage_config[stage_name]
        if cfg["type"] == "shared":
            if state["shared"].get(stage_name, {}).get("status") == "in_progress":
                state["current_stage"] = stage_name
        else:
            for feat in state.get("features", []):
                if feat.get(stage_name, {}).get("status") in ("in_progress", "done"):
                    state["current_stage"] = stage_name
                    break


# ---------------------------------------------------------------------------
# Core update logic
# ---------------------------------------------------------------------------

def update_shared_action(state: dict, action: str, status: str,
                         deliverables, context, next_actions_map: dict,
                         stage_config: dict, stage_order: list[str]):
    """Update action in a shared stage (ideation/requirement).

    Returns (True, None) on success, (False, error_dict) on failure.
    """
    for stage_name in ("ideation", "requirement"):
        stage = state["shared"].get(stage_name, {})
        if action in stage.get("actions", {}):
            if stage.get("status") == "locked":
                if not _try_unlock_shared_stage(state, stage_name, stage_config, stage_order):
                    return False, {
                        "success": False, "error": "STAGE_LOCKED",
                        "message": f"Stage '{stage_name}' is locked",
                    }
            _apply_update(
                stage["actions"][action], status, deliverables, context,
                next_actions_map, action, state,
            )
            return True, None
    return False, {
        "success": False, "error": "ACTION_NOT_FOUND",
        "message": f"Action '{action}' not found in shared stages",
    }


def update_feature_action(state: dict, action: str, status: str,
                          feature_id: str, deliverables, context,
                          next_actions_map: dict,
                          stage_config: dict, stage_order: list[str]):
    """Update action in a per-feature stage.

    Returns (True, None) on success, (False, error_dict) on failure.
    """
    feat = _find_feature(state, feature_id)
    if not feat:
        return False, {
            "success": False, "error": "FEATURE_NOT_FOUND",
            "message": f"Feature '{feature_id}' not found",
        }
    for stage_name in ("implement", "validation", "feedback"):
        stage_data = feat.get(stage_name, {})
        if action in stage_data.get("actions", {}):
            if stage_data.get("status") == "locked":
                if not _try_unlock_feature_stage(state, feat, stage_name, stage_config, stage_order):
                    return False, {
                        "success": False, "error": "STAGE_LOCKED",
                        "message": f"Stage '{stage_name}' is locked for feature '{feature_id}'",
                    }
            _apply_update(
                stage_data["actions"][action], status, deliverables, context,
                next_actions_map, action, state,
            )
            return True, None
    return False, {
        "success": False, "error": "FEATURE_NOT_FOUND",
        "message": f"Action '{action}' not found for feature '{feature_id}'",
    }


def populate_features(state: dict, stage_config: dict, features: list) -> None:
    """Add feature entries to the features array with per-feature stages."""
    for feat in features:
        feat_obj = {
            "feature_id": feat["id"],
            "name": feat["name"],
            "depends_on": feat.get("depends_on", []),
        }
        for stage_name in ("implement", "validation", "feedback"):
            cfg = stage_config[stage_name]
            actions = {}
            optional_set = set(cfg.get("optional_actions", []))
            for action_name in cfg["mandatory_actions"] + cfg["optional_actions"]:
                action_data = {"status": "pending", "deliverables": []}
                if action_name in optional_set:
                    action_data["optional"] = True
                    action_data["status"] = "skipped"
                actions[action_name] = action_data
            feat_obj[stage_name] = {"status": "locked", "actions": actions}
        state["features"].append(feat_obj)


def compute_next_action(state: dict, stage_config: dict, stage_order: list[str]) -> dict:
    """Determine the recommended next action."""
    for stage_name in stage_order:
        cfg = stage_config[stage_name]
        if cfg["type"] == "shared":
            stage = state["shared"].get(stage_name, {})
            if stage.get("status") == "locked":
                if _is_shared_stage_ready_to_unlock(state, stage_name, stage_config, stage_order):
                    for action_name in cfg["mandatory_actions"]:
                        action = stage.get("actions", {}).get(action_name, {})
                        if action.get("status") in ("pending", "failed"):
                            return {"action": action_name, "stage": stage_name,
                                    "feature_id": None,
                                    "reason": "Next stage ready"}
                continue
            if stage.get("status") == "in_progress":
                for action_name in cfg["mandatory_actions"]:
                    action = stage.get("actions", {}).get(action_name, {})
                    if action.get("status") in ("pending", "failed"):
                        return {"action": action_name, "stage": stage_name,
                                "feature_id": None,
                                "reason": "Next pending mandatory action"}
        elif cfg["type"] == "per_feature":
            for feat in state.get("features", []):
                feat_stage = feat.get(stage_name, {})
                if feat_stage.get("status") == "locked":
                    if _is_feature_stage_ready_to_unlock(state, feat, stage_name, stage_config, stage_order):
                        for action_name in cfg["mandatory_actions"]:
                            action = feat_stage.get("actions", {}).get(action_name, {})
                            if action.get("status") in ("pending", "failed"):
                                return {"action": action_name, "stage": stage_name,
                                        "feature_id": feat["feature_id"],
                                        "reason": "Next stage ready"}
                    continue
                if feat_stage.get("status") == "in_progress":
                    for action_name in cfg["mandatory_actions"]:
                        action = feat_stage.get("actions", {}).get(action_name, {})
                        if action.get("status") in ("pending", "failed"):
                            return {"action": action_name, "stage": stage_name,
                                    "feature_id": feat["feature_id"],
                                    "reason": "Next pending mandatory action"}
    return {"action": None, "stage": None, "feature_id": None, "reason": "All actions complete"}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # Validate status early (before lock)
    if args.status not in VALID_STATUSES:
        exit_with_error(
            EXIT_VALIDATION_ERROR,
            "INVALID_STATUS",
            f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}",
        )

    root = resolve_project_root()
    template = load_workflow_template(root)
    stage_config = build_stage_config(template)
    stage_order = template.get("stage_order", list(template.get("stages", {}).keys()))
    next_actions_map = build_next_actions_map(template)
    wf_dir = resolve_workflow_dir(root)
    state_path = wf_dir / f"workflow-{args.workflow}.json"
    lock_path = state_path.with_suffix(".lock")

    # Parse JSON arguments
    deliverables = json.loads(args.deliverables) if args.deliverables else None
    context = json.loads(args.context) if args.context else None
    features = json.loads(args.features) if args.features else None

    # feature_breakdown done requires --features
    if args.action == "feature_breakdown" and args.status == "done" and not features:
        exit_with_error(
            EXIT_VALIDATION_ERROR,
            "MISSING_FEATURES",
            "The feature_breakdown action requires a --features argument when status is 'done'.",
        )

    # Convert legacy list deliverables to keyed dict
    if isinstance(deliverables, list):
        deliverables = convert_list_to_keyed(template, args.action, deliverables)

    # Validate deliverables against template
    if isinstance(deliverables, dict) and deliverables:
        validate_deliverables(template, args.action, deliverables)

    with with_file_lock(lock_path, timeout=args.lock_timeout):
        state = atomic_read_json(state_path)
        if state.get("success") is False:
            exit_with_error(
                EXIT_VALIDATION_ERROR if state["error"] == "JSON_PARSE_ERROR" else 2,
                state["error"],
                state["message"],
            )

        # Dispatch to shared or feature action
        if args.feature_id:
            ok, err = update_feature_action(
                state, args.action, args.status, args.feature_id,
                deliverables, context, next_actions_map, stage_config, stage_order,
            )
        else:
            ok, err = update_shared_action(
                state, args.action, args.status,
                deliverables, context, next_actions_map, stage_config, stage_order,
            )

        if not ok:
            exit_with_error(EXIT_VALIDATION_ERROR, err["error"], err["message"])

        # Feature breakdown special case
        if args.action == "feature_breakdown" and args.status == "done" and features:
            populate_features(state, stage_config, features)
            req_actions = state["shared"]["requirement"]["actions"]
            req_actions["feature_breakdown"]["features_created"] = [
                {"id": f["id"], "name": f["name"], "depends_on": f.get("depends_on", [])}
                for f in features
            ]
            no_dep_ids = [f["id"] for f in features if not f.get("depends_on")]
            req_actions["feature_breakdown"]["next_actions_suggested"] = no_dep_ids

        state["last_activity"] = datetime.now(timezone.utc).isoformat()
        atomic_write_json(state_path, state)

        next_action = compute_next_action(state, stage_config, stage_order)

    output_result({
        "success": True,
        "data": {
            "action_updated": args.action,
            "new_status": args.status,
            "current_stage": state.get("current_stage", "unknown"),
            "next_action": next_action,
        },
    }, fmt=args.fmt)


if __name__ == "__main__":
    main()
