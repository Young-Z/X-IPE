"""
Engineering Workflow Manager Service (FEATURE-036-A)

Manages the full lifecycle of engineering workflows:
- Workflow CRUD with JSON state persistence
- Stage gating logic (shared and per-feature)
- Feature dependency evaluation
- Next-action suggestion
- Atomic writes for data integrity
- Deliverables resolution (FEATURE-036-E)
- Auto-archive of stale workflows (FEATURE-036-E)
"""

import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

from x_ipe.tracing import x_ipe_tracing

# Valid action statuses
VALID_STATUSES = {"pending", "in_progress", "done", "skipped", "failed"}


def _load_workflow_template(project_root: str = None) -> dict:
    """Load workflow template from x-ipe-docs/config/workflow-template.json."""
    search_paths = []
    if project_root:
        search_paths.append(Path(project_root) / "x-ipe-docs" / "config" / "workflow-template.json")
    # Also try relative to this file's location (src/x_ipe/services/ -> project root)
    service_dir = Path(__file__).resolve().parent
    search_paths.append(service_dir.parent.parent.parent / "x-ipe-docs" / "config" / "workflow-template.json")

    for config_path in search_paths:
        if config_path.exists():
            try:
                return json.loads(config_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                break
    return {}


def _init_config(project_root: str = None):
    """Initialise config from template file, deriving internal structures.

    The template uses a condensed per-action format::

        stages.<stage>.actions.<action> = {
            optional, deliverable_category, next_actions_suggested
        }

    We derive four internal structures the service needs:
      stage_config  – type, mandatory/optional lists, next_stage
      stage_order   – ordered stage names
      deliverable_categories – action → category
      next_actions_map       – action → [suggested next actions]
    """
    tpl = _load_workflow_template(project_root)
    tpl_stages = tpl.get("stages", {})

    if tpl_stages and all("actions" in s for s in tpl_stages.values()):
        # New condensed format – derive internal structures
        stage_order = tpl.get("stage_order",
                              list(tpl_stages.keys()))
        stage_config = {}
        deliverable_categories = {}
        next_actions_map = {}

        for stage_name, stage_def in tpl_stages.items():
            mandatory = []
            optional = []
            for action_name, action_def in stage_def.get("actions", {}).items():
                if action_def.get("optional", False):
                    optional.append(action_name)
                else:
                    mandatory.append(action_name)
                cat = action_def.get("deliverable_category")
                if cat:
                    deliverable_categories[action_name] = cat
                next_actions_map[action_name] = action_def.get(
                    "next_actions_suggested", [])

            stage_config[stage_name] = {
                "type": stage_def.get("type", "shared"),
                "mandatory_actions": mandatory,
                "optional_actions": optional,
                "next_stage": stage_def.get("next_stage"),
            }

        return stage_config, stage_order, deliverable_categories, next_actions_map

    # Fallback – hardcoded defaults
    return _default_config()


def _default_config():
    """Return hardcoded fallback configuration."""
    stage_config = {
        "ideation": {
            "type": "shared",
            "mandatory_actions": ["compose_idea", "refine_idea"],
            "optional_actions": ["reference_uiux", "design_mockup"],
            "next_stage": "requirement",
        },
        "requirement": {
            "type": "shared",
            "mandatory_actions": ["requirement_gathering", "feature_breakdown"],
            "optional_actions": [],
            "next_stage": "implement",
        },
        "implement": {
            "type": "per_feature",
            "mandatory_actions": ["feature_refinement", "technical_design", "implementation"],
            "optional_actions": [],
            "next_stage": "validation",
        },
        "validation": {
            "type": "per_feature",
            "mandatory_actions": ["acceptance_testing"],
            "optional_actions": ["quality_evaluation"],
            "next_stage": "feedback",
        },
        "feedback": {
            "type": "per_feature",
            "mandatory_actions": [],
            "optional_actions": ["change_request"],
            "next_stage": None,
        },
    }
    stage_order = ["ideation", "requirement", "implement", "validation", "feedback"]
    deliverable_categories = {
        "compose_idea": "ideas", "refine_idea": "ideas",
        "reference_uiux": "mockups", "design_mockup": "mockups",
        "requirement_gathering": "requirements", "feature_breakdown": "requirements",
        "feature_refinement": "requirements", "technical_design": "requirements",
        "implementation": "implementations",
        "acceptance_testing": "quality", "quality_evaluation": "quality",
        "change_request": "requirements",
    }
    next_actions_map = {
        "compose_idea": ["refine_idea", "reference_uiux"],
        "refine_idea": ["design_mockup", "requirement_gathering"],
        "reference_uiux": ["design_mockup", "refine_idea"],
        "design_mockup": ["requirement_gathering"],
        "requirement_gathering": ["feature_breakdown"],
        "feature_breakdown": [],
        "feature_refinement": ["technical_design"],
        "technical_design": ["implementation"],
        "implementation": ["acceptance_testing"],
        "acceptance_testing": ["quality_evaluation"],
        "quality_evaluation": ["change_request"],
        "change_request": [],
    }
    return stage_config, stage_order, deliverable_categories, next_actions_map


# Module-level defaults (overridden per-instance when project_root is known)
STAGE_CONFIG, STAGE_ORDER, DELIVERABLE_CATEGORIES, NEXT_ACTIONS_MAP = _init_config()

# Name validation
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9-]+$")
MAX_NAME_LENGTH = 100


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


class WorkflowManagerService:
    """Backend service for engineering workflow management."""

    def __init__(self, project_root: str):
        self._project_root = Path(project_root)
        self._workflow_dir = self._project_root / "x-ipe-docs" / "engineering-workflow"
        # Reload config from project-level template if available
        cfg = _init_config(project_root)
        self._stage_config = cfg[0]
        self._stage_order = cfg[1]
        self._deliverable_categories = cfg[2]
        self._next_actions_map = cfg[3]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @x_ipe_tracing()
    def create_workflow(self, name: str) -> dict:
        """Create a new workflow with initial state."""
        err = self._validate_workflow_name(name)
        if err:
            return err

        path = self._get_workflow_path(name)
        if path.exists():
            return {"success": False, "error": "ALREADY_EXISTS",
                    "message": f"Workflow '{name}' already exists"}

        state = self._build_initial_state(name)
        self._write_state(name, state)
        return {"success": True, "data": {
            "name": name, "created": state["created"],
            "current_stage": state["current_stage"]}}

    @x_ipe_tracing()
    def get_workflow(self, name: str) -> dict:
        """Return full workflow state."""
        return self._read_state(name)

    @x_ipe_tracing()
    def list_workflows(self) -> list:
        """Return metadata for all active workflows."""
        if not self._workflow_dir.exists():
            return []

        results = []
        for f in sorted(self._workflow_dir.glob("workflow-*.json")):
            try:
                state = json.loads(f.read_text(encoding="utf-8"))
                feature_count = 0
                for stage_name in ("implement", "validation", "feedback"):
                    features = state.get("stages", {}).get(stage_name, {}).get("features", {})
                    if features:
                        feature_count = len(features)
                        break
                results.append({
                    "name": state.get("name", f.stem),
                    "created": state.get("created"),
                    "last_activity": state.get("last_activity"),
                    "current_stage": state.get("current_stage"),
                    "feature_count": feature_count,
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return results

    @x_ipe_tracing()
    def delete_workflow(self, name: str) -> dict:
        """Delete a workflow JSON file."""
        path = self._get_workflow_path(name)
        if not path.exists():
            return {"success": False, "error": "NOT_FOUND",
                    "message": f"Workflow '{name}' not found"}
        path.unlink()
        return {"success": True, "message": f"Workflow '{name}' deleted"}

    @x_ipe_tracing()
    def update_action_status(self, workflow_name: str, action: str,
                             status: str, feature_id: str = None,
                             deliverables: list = None) -> dict:
        """Update an action's status and re-evaluate gating."""
        if status not in VALID_STATUSES:
            return {"success": False, "error": "INVALID_STATUS",
                    "message": f"Status must be one of: {VALID_STATUSES}"}

        state = self._read_state(workflow_name)
        if "error" in state and state.get("success") is False:
            return state

        if deliverables is None:
            deliverables = []

        # Find the action in the state
        if feature_id:
            updated, err = self._update_feature_action(state, action, status, feature_id, deliverables)
        else:
            updated, err = self._update_shared_action(state, action, status, deliverables)

        if err:
            return err

        # Re-evaluate stage gating
        self._evaluate_stage_gating(state)
        state["last_activity"] = _now_iso()
        self._write_state(workflow_name, state)

        next_action = self._compute_next_action(state)
        return {"success": True, "data": {
            "action_updated": action, "new_status": status,
            "current_stage": state["current_stage"],
            "next_action": next_action}}

    @x_ipe_tracing()
    def check_dependencies(self, workflow_name: str, feature_id: str) -> dict:
        """Check if a feature's dependencies are satisfied."""
        state = self._read_state(workflow_name)
        if "error" in state and state.get("success") is False:
            return state

        # Find feature's depends_on list
        depends_on = []
        for stage_name in ("implement", "validation", "feedback"):
            features = state["stages"].get(stage_name, {}).get("features", {})
            if feature_id in features:
                depends_on = features[feature_id].get("depends_on", [])
                break

        if not depends_on:
            return {"blocked": False, "blockers": []}

        blockers = []
        for dep_id in depends_on:
            dep_done = self._is_feature_stage_done(state, dep_id, "implement")
            if not dep_done:
                blockers.append({
                    "feature_id": dep_id,
                    "current_stage": "implement",
                    "required_stage": "implement",
                })

        return {"blocked": len(blockers) > 0, "blockers": blockers}

    @x_ipe_tracing()
    def get_next_action(self, workflow_name: str) -> dict:
        """Return the recommended next action."""
        state = self._read_state(workflow_name)
        if "error" in state and state.get("success") is False:
            return state
        return self._compute_next_action(state)

    @x_ipe_tracing()
    def resolve_deliverables(self, workflow_name: str) -> dict:
        """Collect all deliverables from all actions, check file existence."""
        state = self._read_state(workflow_name)
        if "error" in state and state.get("success") is False:
            return state

        deliverables = []

        # Shared stages (ideation, requirement)
        for stage_name in ("ideation", "requirement"):
            stage = state["stages"].get(stage_name, {})
            for action_key, action_data in stage.get("actions", {}).items():
                category = self._deliverable_categories.get(action_key, "implementations")
                for path_str in action_data.get("deliverables", []):
                    full_path = self._project_root / path_str
                    deliverables.append({
                        "name": os.path.basename(path_str),
                        "path": path_str,
                        "category": category,
                        "exists": full_path.exists(),
                    })

        # Per-feature stages (implement, validation, feedback)
        for stage_name in ("implement", "validation", "feedback"):
            features = state["stages"].get(stage_name, {}).get("features", {})
            for feat_id, feat_data in features.items():
                for action_key, action_data in feat_data.get("actions", {}).items():
                    category = self._deliverable_categories.get(action_key, "implementations")
                    for path_str in action_data.get("deliverables", []):
                        full_path = self._project_root / path_str
                        deliverables.append({
                            "name": os.path.basename(path_str),
                            "path": path_str,
                            "category": category,
                            "exists": full_path.exists(),
                        })

        return {"deliverables": deliverables, "count": len(deliverables)}

    @x_ipe_tracing()
    def archive_stale_workflows(self, days: int = 30) -> dict:
        """Move workflows inactive for >days to archive/."""
        archive_dir = self._workflow_dir / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        archived = 0
        if not self._workflow_dir.exists():
            return {"archived_count": 0}

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        for f in list(self._workflow_dir.glob("workflow-*.json")):
            try:
                state = json.loads(f.read_text(encoding="utf-8"))
                last_activity = state.get("last_activity", "")
                if last_activity:
                    la_dt = datetime.fromisoformat(last_activity)
                    if la_dt < cutoff:
                        shutil.move(str(f), str(archive_dir / f.name))
                        archived += 1
            except (json.JSONDecodeError, ValueError, KeyError):
                continue

        return {"archived_count": archived}

    @x_ipe_tracing()
    def add_features(self, workflow_name: str, features: list) -> dict:
        """Populate per-feature structures after Feature Breakdown."""
        state = self._read_state(workflow_name)
        if "error" in state and state.get("success") is False:
            return state

        for feat in features:
            feat_id = feat["id"]
            entry = {
                "name": feat["name"],
                "depends_on": feat.get("depends_on", []),
                "actions": {
                    "feature_refinement": {"status": "pending", "deliverables": []},
                    "technical_design": {"status": "pending", "deliverables": []},
                    "implementation": {"status": "pending", "deliverables": []},
                    "acceptance_testing": {"status": "pending", "deliverables": []},
                    "quality_evaluation": {"status": "skipped", "deliverables": [], "optional": True},
                    "change_request": {"status": "pending", "deliverables": [], "optional": True},
                },
            }
            for stage_name in ("implement", "validation", "feedback"):
                state["stages"][stage_name]["features"][feat_id] = entry.copy()
                # Deep-copy actions for each stage
                state["stages"][stage_name]["features"][feat_id]["actions"] = {
                    k: dict(v) for k, v in entry["actions"].items()
                }

        state["last_activity"] = _now_iso()
        self._write_state(workflow_name, state)
        return {"success": True, "data": {"features_added": len(features)}}

    @x_ipe_tracing()
    def link_idea_folder(self, workflow_name: str, idea_folder_path: str) -> dict:
        """Associate an idea folder with a workflow."""
        if not os.path.exists(idea_folder_path):
            return {"success": False, "error": "PATH_NOT_FOUND",
                    "message": f"Idea folder path does not exist: {idea_folder_path}"}

        state = self._read_state(workflow_name)
        if "error" in state and state.get("success") is False:
            return state

        state["idea_folder"] = idea_folder_path
        state["last_activity"] = _now_iso()
        self._write_state(workflow_name, state)
        return {"success": True, "data": {"idea_folder": idea_folder_path}}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_workflow_name(self, name: str):
        if not name or not NAME_PATTERN.match(name):
            return {"success": False, "error": "INVALID_NAME",
                    "message": "Workflow name must be alphanumeric with hyphens only"}
        if len(name) > MAX_NAME_LENGTH:
            return {"success": False, "error": "INVALID_NAME",
                    "message": f"Workflow name must not exceed {MAX_NAME_LENGTH} characters"}
        return None

    def _get_workflow_path(self, name: str) -> Path:
        return self._workflow_dir / f"workflow-{name}.json"

    def _build_initial_state(self, name: str) -> dict:
        now = _now_iso()
        stages = {}
        for stage_name, config in self._stage_config.items():
            if config["type"] == "shared":
                actions = {}
                all_optional = set(config.get("optional_actions", []))
                for action_name in config["mandatory_actions"] + config["optional_actions"]:
                    action_data = {"status": "pending", "deliverables": []}
                    if action_name in all_optional:
                        action_data["optional"] = True
                    if action_name == "feature_breakdown":
                        action_data["features_created"] = []
                    actions[action_name] = action_data
                stages[stage_name] = {
                    "status": "in_progress" if stage_name == "ideation" else "locked",
                    "actions": actions,
                }
            else:
                stages[stage_name] = {"status": "locked", "features": {}}
        return {
            "schema_version": "1.0",
            "name": name,
            "created": now,
            "last_activity": now,
            "idea_folder": None,
            "current_stage": "ideation",
            "stages": stages,
        }

    def _read_state(self, name: str) -> dict:
        path = self._get_workflow_path(name)
        if not path.exists():
            return {"success": False, "error": "NOT_FOUND",
                    "message": f"Workflow '{name}' not found"}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"success": False, "error": "CORRUPTED_STATE",
                    "message": f"Workflow '{name}' has corrupted state — manual repair required"}

    def _write_state(self, name: str, state: dict):
        self._workflow_dir.mkdir(parents=True, exist_ok=True)
        target = self._get_workflow_path(name)
        fd, tmp_path = tempfile.mkstemp(dir=str(self._workflow_dir), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, str(target))
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def _update_shared_action(self, state, action, status, deliverables):
        """Update action in a shared stage (ideation/requirement)."""
        for stage_name in ("ideation", "requirement"):
            stage = state["stages"][stage_name]
            if action in stage.get("actions", {}):
                if stage["status"] == "locked":
                    if not self._try_unlock_stage(state, stage_name):
                        return False, {"success": False, "error": "STAGE_LOCKED",
                                       "message": f"Stage '{stage_name}' is locked"}
                stage["actions"][action]["status"] = status
                stage["actions"][action]["deliverables"] = deliverables
                # Add next_actions_suggested when action is done
                if status == "done" and action in self._next_actions_map:
                    stage["actions"][action]["next_actions_suggested"] = self._next_actions_map[action]
                elif status != "done":
                    stage["actions"][action].pop("next_actions_suggested", None)
                return True, None
        return False, {"success": False, "error": "ACTION_NOT_FOUND",
                       "message": f"Action '{action}' not found in shared stages"}

    def _update_feature_action(self, state, action, status, feature_id, deliverables):
        """Update action in a per-feature stage."""
        for stage_name in ("implement", "validation", "feedback"):
            features = state["stages"][stage_name].get("features", {})
            if feature_id in features and action in features[feature_id].get("actions", {}):
                if state["stages"][stage_name]["status"] == "locked":
                    if not self._try_unlock_stage(state, stage_name):
                        return False, {"success": False, "error": "STAGE_LOCKED",
                                       "message": f"Stage '{stage_name}' is locked"}
                features[feature_id]["actions"][action]["status"] = status
                features[feature_id]["actions"][action]["deliverables"] = deliverables
                # Add next_actions_suggested when action is done
                if status == "done" and action in self._next_actions_map:
                    features[feature_id]["actions"][action]["next_actions_suggested"] = self._next_actions_map[action]
                elif status != "done":
                    features[feature_id]["actions"][action].pop("next_actions_suggested", None)
                return True, None
        return False, {"success": False, "error": "FEATURE_NOT_FOUND",
                       "message": f"Feature '{feature_id}' or action '{action}' not found"}

    def _evaluate_stage_gating(self, state):
        """No-op: stage transitions are now on-demand via _try_unlock_stage."""
        pass

    def _is_stage_ready_to_unlock(self, state, stage_name):
        """Check if a locked stage's predecessor has all mandatory actions done."""
        idx = self._stage_order.index(stage_name) if stage_name in self._stage_order else -1
        if idx <= 0:
            return False

        prev_name = self._stage_order[idx - 1]
        prev_stage = state["stages"].get(prev_name, {})
        prev_config = self._stage_config.get(prev_name, {})

        if prev_stage.get("status") not in ("in_progress",):
            return False

        if prev_config.get("type") == "shared":
            actions = prev_stage.get("actions", {})
            return all(
                actions.get(a, {}).get("status") == "done"
                for a in prev_config.get("mandatory_actions", [])
            )
        elif prev_config.get("type") == "per_feature":
            features = prev_stage.get("features", {})
            if not features:
                return False
            return all(
                all(
                    feat_data.get("actions", {}).get(a, {}).get("status") == "done"
                    for a in prev_config.get("mandatory_actions", [])
                )
                for feat_data in features.values()
            )
        return False

    def _try_unlock_stage(self, state, stage_name):
        """Complete the predecessor and unlock *stage_name* on demand."""
        if not self._is_stage_ready_to_unlock(state, stage_name):
            return False

        idx = self._stage_order.index(stage_name)
        prev_name = self._stage_order[idx - 1]
        state["stages"][prev_name]["status"] = "completed"
        state["stages"][stage_name]["status"] = "in_progress"
        state["current_stage"] = stage_name
        return True

    def _is_feature_stage_done(self, state, feature_id, stage_name):
        """Check if a feature has completed all mandatory actions in a stage."""
        config = self._stage_config[stage_name]
        features = state["stages"].get(stage_name, {}).get("features", {})
        if feature_id not in features:
            return False
        actions = features[feature_id].get("actions", {})
        return all(
            actions.get(a, {}).get("status") == "done"
            for a in config["mandatory_actions"]
        )

    def _compute_next_action(self, state):
        """Determine the recommended next action."""
        for stage_name in self._stage_order:
            config = self._stage_config[stage_name]
            stage = state["stages"][stage_name]

            if stage["status"] == "locked":
                # Check if this locked stage is ready to unlock
                if self._is_stage_ready_to_unlock(state, stage_name):
                    if config["type"] == "shared":
                        for action_name in config["mandatory_actions"]:
                            action = stage.get("actions", {}).get(action_name, {})
                            if action.get("status") in ("pending", "failed"):
                                return {"action": action_name, "stage": stage_name,
                                        "feature_id": None,
                                        "reason": "Next stage ready — click to start"}
                    elif config["type"] == "per_feature":
                        features = stage.get("features", {})
                        for feat_id, feat_data in features.items():
                            for action_name in config["mandatory_actions"]:
                                action = feat_data.get("actions", {}).get(action_name, {})
                                if action.get("status") in ("pending", "failed"):
                                    return {"action": action_name, "stage": stage_name,
                                            "feature_id": feat_id,
                                            "reason": "Next stage ready — click to start"}
                continue

            if config["type"] == "shared":
                for action_name in config["mandatory_actions"]:
                    action = stage.get("actions", {}).get(action_name, {})
                    if action.get("status") in ("pending", "failed"):
                        return {"action": action_name, "stage": stage_name,
                                "feature_id": None,
                                "reason": "Next pending mandatory action"}

            elif config["type"] == "per_feature":
                features = stage.get("features", {})
                for feat_id, feat_data in features.items():
                    for action_name in config["mandatory_actions"]:
                        action = feat_data.get("actions", {}).get(action_name, {})
                        if action.get("status") in ("pending", "failed"):
                            return {"action": action_name, "stage": stage_name,
                                    "feature_id": feat_id,
                                    "reason": "First unblocked feature with pending mandatory action"}

        return {"action": None, "stage": None, "feature_id": None,
                "reason": "All actions complete"}
