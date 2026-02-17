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

# Data-driven stage configuration
STAGE_CONFIG = {
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

STAGE_ORDER = ["ideation", "requirement", "implement", "validation", "feedback"]

# Map actions to deliverable categories (FEATURE-036-E)
DELIVERABLE_CATEGORIES = {
    "compose_idea": "ideas",
    "refine_idea": "ideas",
    "reference_uiux": "mockups",
    "design_mockup": "mockups",
    "requirement_gathering": "requirements",
    "feature_breakdown": "requirements",
    "feature_refinement": "requirements",
    "technical_design": "requirements",
    "implementation": "implementations",
    "acceptance_testing": "quality",
    "quality_evaluation": "quality",
    "change_request": "requirements",
}

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
                category = DELIVERABLE_CATEGORIES.get(action_key, "implementations")
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
                    category = DELIVERABLE_CATEGORIES.get(action_key, "implementations")
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
                    "quality_evaluation": {"status": "skipped", "deliverables": []},
                    "change_request": {"status": "pending", "deliverables": []},
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
        return {
            "schema_version": "1.0",
            "name": name,
            "created": now,
            "last_activity": now,
            "idea_folder": None,
            "current_stage": "ideation",
            "stages": {
                "ideation": {
                    "status": "in_progress",
                    "actions": {
                        "compose_idea": {"status": "pending", "deliverables": []},
                        "reference_uiux": {"status": "pending", "deliverables": []},
                        "refine_idea": {"status": "pending", "deliverables": []},
                        "design_mockup": {"status": "pending", "deliverables": []},
                    },
                },
                "requirement": {
                    "status": "locked",
                    "actions": {
                        "requirement_gathering": {"status": "pending", "deliverables": []},
                        "feature_breakdown": {"status": "pending", "deliverables": [],
                                              "features_created": []},
                    },
                },
                "implement": {"status": "locked", "features": {}},
                "validation": {"status": "locked", "features": {}},
                "feedback": {"status": "locked", "features": {}},
            },
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
                    return False, {"success": False, "error": "STAGE_LOCKED",
                                   "message": f"Stage '{stage_name}' is locked"}
                stage["actions"][action]["status"] = status
                stage["actions"][action]["deliverables"] = deliverables
                return True, None
        return False, {"success": False, "error": "ACTION_NOT_FOUND",
                       "message": f"Action '{action}' not found in shared stages"}

    def _update_feature_action(self, state, action, status, feature_id, deliverables):
        """Update action in a per-feature stage."""
        for stage_name in ("implement", "validation", "feedback"):
            features = state["stages"][stage_name].get("features", {})
            if feature_id in features and action in features[feature_id].get("actions", {}):
                if state["stages"][stage_name]["status"] == "locked":
                    return False, {"success": False, "error": "STAGE_LOCKED",
                                   "message": f"Stage '{stage_name}' is locked"}
                features[feature_id]["actions"][action]["status"] = status
                features[feature_id]["actions"][action]["deliverables"] = deliverables
                return True, None
        return False, {"success": False, "error": "FEATURE_NOT_FOUND",
                       "message": f"Feature '{feature_id}' or action '{action}' not found"}

    def _evaluate_stage_gating(self, state):
        """Re-evaluate which stages should be unlocked."""
        for i, stage_name in enumerate(STAGE_ORDER):
            config = STAGE_CONFIG[stage_name]
            stage = state["stages"][stage_name]

            if config["type"] == "shared":
                actions = stage.get("actions", {})
                mandatory_done = all(
                    actions.get(a, {}).get("status") == "done"
                    for a in config["mandatory_actions"]
                )
                if mandatory_done and stage["status"] == "in_progress":
                    stage["status"] = "completed"
                    # Unlock next stage
                    next_stage = config["next_stage"]
                    if next_stage and state["stages"][next_stage]["status"] == "locked":
                        state["stages"][next_stage]["status"] = "in_progress"
                        state["current_stage"] = next_stage

            elif config["type"] == "per_feature":
                # Per-feature stages unlock when previous shared/per-feature stage completes
                if i > 0:
                    prev_stage = STAGE_ORDER[i - 1]
                    prev_status = state["stages"][prev_stage]["status"]
                    if prev_status in ("completed", "in_progress") and stage["status"] == "locked":
                        if prev_status == "completed":
                            stage["status"] = "in_progress"
                            state["current_stage"] = stage_name

    def _is_feature_stage_done(self, state, feature_id, stage_name):
        """Check if a feature has completed all mandatory actions in a stage."""
        config = STAGE_CONFIG[stage_name]
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
        for stage_name in STAGE_ORDER:
            config = STAGE_CONFIG[stage_name]
            stage = state["stages"][stage_name]

            if stage["status"] == "locked":
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
