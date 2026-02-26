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
                # Support both old deliverable_category and new deliverables array
                cat = action_def.get("deliverable_category")
                if not cat and "deliverables" in action_def:
                    # Derive category from action name for backward compat
                    action_to_category = {
                        "compose_idea": "ideas", "refine_idea": "ideas",
                        "reference_uiux": "mockups", "design_mockup": "mockups",
                        "requirement_gathering": "requirements",
                        "feature_breakdown": "requirements",
                        "feature_refinement": "requirements",
                        "technical_design": "requirements",
                        "implementation": "implementations",
                        "acceptance_testing": "quality",
                        "quality_evaluation": "quality",
                        "change_request": "requirements",
                    }
                    cat = action_to_category.get(action_name, stage_name)
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
                feature_count = len(state.get("features", []))
                if not feature_count and "stages" in state:
                    for sn in ("implement", "validation", "feedback"):
                        feats = state.get("stages", {}).get(sn, {}).get("features", {})
                        if feats:
                            feature_count = len(feats)
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
                             deliverables=None,
                             context: dict = None,
                             features: list = None) -> dict:
        """Update an action's status and re-evaluate gating."""
        if status not in VALID_STATUSES:
            return {"success": False, "error": "INVALID_STATUS",
                    "message": f"Status must be one of: {VALID_STATUSES}"}

        # Dual-format deliverables: convert list to keyed dict using template tags
        if deliverables is not None and isinstance(deliverables, list):
            deliverables = self._convert_list_to_keyed(action, deliverables)

        state = self._read_state(workflow_name)
        if "error" in state and state.get("success") is False:
            return state

        # Find the action in the state
        if feature_id:
            updated, err = self._update_feature_action(state, action, status, feature_id, deliverables, context)
        else:
            updated, err = self._update_shared_action(state, action, status, deliverables, context)

        if err:
            return err

        # If feature_breakdown done with features, populate per-feature structures
        if action == "feature_breakdown" and status == "done" and features:
            self._populate_features(state, features)
            req_actions = state["shared"]["requirement"]["actions"]
            req_actions["feature_breakdown"]["features_created"] = [
                {"id": f["id"], "name": f["name"], "depends_on": f.get("depends_on", [])}
                for f in features
            ]
            no_dep_ids = [f["id"] for f in features if not f.get("depends_on")]
            req_actions["feature_breakdown"]["next_actions_suggested"] = no_dep_ids

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
        feat = self._find_feature(state, feature_id)
        depends_on = feat.get("depends_on", []) if feat else []

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
            stage = state["shared"].get(stage_name, {})
            for action_key, action_data in stage.get("actions", {}).items():
                category = self._deliverable_categories.get(action_key, "implementations")
                raw_deliverables = action_data.get("deliverables", [])
                if isinstance(raw_deliverables, dict):
                    for tag_name, path_str in raw_deliverables.items():
                        full_path = self._project_root / path_str
                        deliverables.append({
                            "name": tag_name,
                            "path": path_str,
                            "category": category,
                            "exists": full_path.exists(),
                        })
                elif isinstance(raw_deliverables, list):
                    for path_str in raw_deliverables:
                        full_path = self._project_root / path_str
                        deliverables.append({
                            "name": os.path.basename(path_str),
                            "path": path_str,
                            "category": category,
                            "exists": full_path.exists(),
                        })

        # Per-feature stages
        for feat in state.get("features", []):
            for stage_name in ("implement", "validation", "feedback"):
                stage_data = feat.get(stage_name, {})
                for action_key, action_data in stage_data.get("actions", {}).items():
                    category = self._deliverable_categories.get(action_key, "implementations")
                    raw_deliverables = action_data.get("deliverables", [])
                    if isinstance(raw_deliverables, dict):
                        for tag_name, path_str in raw_deliverables.items():
                            full_path = self._project_root / path_str
                            deliverables.append({
                                "name": tag_name,
                                "path": path_str,
                                "category": category,
                                "exists": full_path.exists(),
                            })
                    elif isinstance(raw_deliverables, list):
                        for path_str in raw_deliverables:
                            full_path = self._project_root / path_str
                            deliverables.append({
                            "name": os.path.basename(path_str),
                            "path": path_str,
                            "category": category,
                            "exists": full_path.exists(),
                        })

        return {"deliverables": deliverables, "count": len(deliverables)}

    @x_ipe_tracing()
    def validate_template(self) -> bool:
        """Static validation of tagged template at load time."""
        template = _load_workflow_template(str(self._project_root))
        stage_order = template.get("stage_order", [])
        stages = template.get("stages", {})
        all_folder_tags = {}  # {tag_name: (stage_name, action_name)}

        for stage_name in stage_order:
            stage = stages.get(stage_name, {})
            for action_name, action_def in stage.get("actions", {}).items():
                action_tags = set()
                for tag_str in action_def.get("deliverables", []):
                    if ":" not in tag_str:
                        continue
                    prefix, name = tag_str.split(":", 1)
                    if name in action_tags:
                        raise ValueError(
                            f"Duplicate tag '{name}' in action '{action_name}' "
                            f"of stage '{stage_name}'"
                        )
                    action_tags.add(name)
                    if prefix == "$output-folder":
                        all_folder_tags[name] = (stage_name, action_name)

                # Validate action_context candidates references
                for ref_name, ref_def in action_def.get("action_context", {}).items():
                    candidates = ref_def.get("candidates")
                    if candidates and candidates not in all_folder_tags:
                        raise ValueError(
                            f"action_context '{ref_name}' in '{action_name}' references "
                            f"unknown candidates '{candidates}'"
                        )
        return True

    @x_ipe_tracing()
    def validate_action_deliverables(self, action: str, deliverables) -> bool:
        """Runtime validation: check instance keys match template tags."""
        if not isinstance(deliverables, dict):
            return True  # skip validation for legacy list format
        expected_tags = set(self._get_template_tags(action))
        actual_tags = set(deliverables.keys())
        missing = expected_tags - actual_tags
        if missing:
            import logging
            logging.getLogger(__name__).warning(
                f"Action '{action}' missing deliverable tags: {missing}"
            )
        return len(missing) == 0

    @x_ipe_tracing()
    def resolve_candidates(self, workflow_name: str, action: str,
                           candidates_name: str, feature_id: str = None) -> list:
        """Resolve candidates to list of file paths for dropdown population."""
        state = self._read_state(workflow_name)
        if "error" in state and state.get("success") is False:
            return []
        template = _load_workflow_template(str(self._project_root))
        stage_order = template.get("stage_order", [])
        stages = template.get("stages", {})

        # Find current action's stage index
        current_stage_idx = len(stage_order)
        for i, sn in enumerate(stage_order):
            stage_def = stages.get(sn, {})
            if action in stage_def.get("actions", {}):
                current_stage_idx = i
                break

        results = []
        # Walk stages from first to current (inclusive) to find matching tags
        for i in range(current_stage_idx + 1):
            stage_name = stage_order[i]
            stage_def = stages.get(stage_name, {})
            for act_name, act_def in stage_def.get("actions", {}).items():
                # Skip the target action itself
                if i == current_stage_idx and act_name == action:
                    continue
                for tag_str in act_def.get("deliverables", []):
                    if ":" not in tag_str:
                        continue
                    prefix, name = tag_str.split(":", 1)
                    if name == candidates_name:
                        path = self._get_instance_deliverable(
                            state, stage_name, act_name, name, feature_id
                        )
                        if path:
                            rtype = "file" if prefix == "$output" else "folder"
                            results.append({"type": rtype, "path": path})

        # Per-feature scoping: check feature lane for matching tags
        if feature_id:
            feat_results = self._resolve_in_feature(
                state, feature_id, candidates_name, template
            )
            if feat_results:
                results = feat_results + results

        return results

    def _get_instance_deliverable(self, state, stage_name, action_name,
                                  tag_name, feature_id=None):
        """Get a specific deliverable path from instance state."""
        # Check shared stages
        shared = state.get("shared", {}).get(stage_name, {})
        if shared:
            action_data = shared.get("actions", {}).get(action_name, {})
            deliverables = action_data.get("deliverables", {})
            if isinstance(deliverables, dict):
                return deliverables.get(tag_name)
            elif isinstance(deliverables, list):
                # Legacy: try to match by template tag order
                tags = self._get_template_tags(action_name)
                if tag_name in tags:
                    idx = tags.index(tag_name)
                    return deliverables[idx] if idx < len(deliverables) else None
        return None

    def _resolve_in_feature(self, state, feature_id, candidates_name, template):
        """Resolve candidates within a feature lane."""
        feat = self._find_feature(state, feature_id)
        if not feat:
            return []
        results = []
        stages = template.get("stages", {})
        for stage_name in ("implement", "validation", "feedback"):
            stage_def = stages.get(stage_name, {})
            stage_data = feat.get(stage_name, {})
            for act_name, act_def in stage_def.get("actions", {}).items():
                for tag_str in act_def.get("deliverables", []):
                    if ":" not in tag_str:
                        continue
                    prefix, name = tag_str.split(":", 1)
                    if name == candidates_name:
                        action_data = stage_data.get("actions", {}).get(act_name, {})
                        deliverables = action_data.get("deliverables", {})
                        if isinstance(deliverables, dict):
                            path = deliverables.get(name)
                        else:
                            path = None
                        if path:
                            rtype = "file" if prefix == "$output" else "folder"
                            results.append({"type": rtype, "path": path})
        return results

    def _convert_list_to_keyed(self, action: str, deliverables_list: list) -> dict:
        """Convert legacy list format to keyed object using template tags."""
        tags = self._get_template_tags(action)
        result = {}
        for i, path in enumerate(deliverables_list):
            if i < len(tags):
                result[tags[i]] = path
        return result

    def _get_template_tags(self, action: str) -> list:
        """Extract tag names from template deliverables array for an action."""
        template = _load_workflow_template(str(self._project_root))
        for stage in template.get("stages", {}).values():
            if action in stage.get("actions", {}):
                deliverables = stage["actions"][action].get("deliverables", [])
                tags = []
                for tag_str in deliverables:
                    if ":" in tag_str:
                        tags.append(tag_str.split(":", 1)[1])
                return tags
        return []

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

        self._populate_features(state, features)

        state["last_activity"] = _now_iso()
        self._write_state(workflow_name, state)
        return {"success": True, "data": {"features_added": len(features)}}

    def _populate_features(self, state: dict, features: list) -> None:
        """Add feature entries to the features array with partitioned per-feature stages."""
        for feat in features:
            feat_obj = {
                "feature_id": feat["id"],
                "name": feat["name"],
                "depends_on": feat.get("depends_on", []),
            }
            for stage_name in ("implement", "validation", "feedback"):
                config = self._stage_config[stage_name]
                actions = {}
                optional_set = set(config.get("optional_actions", []))
                for action_name in config["mandatory_actions"] + config["optional_actions"]:
                    action_data = {"status": "pending", "deliverables": []}
                    if action_name in optional_set:
                        action_data["optional"] = True
                        action_data["status"] = "skipped"
                    actions[action_name] = action_data
                feat_obj[stage_name] = {"status": "locked", "actions": actions}
            state["features"].append(feat_obj)

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
        shared = {}
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
                shared[stage_name] = {
                    "status": "in_progress" if stage_name == "ideation" else "locked",
                    "actions": actions,
                }
        return {
            "schema_version": "2.0",
            "name": name,
            "created": now,
            "last_activity": now,
            "idea_folder": None,
            "current_stage": "ideation",
            "shared": shared,
            "features": [],
        }

    def _read_state(self, name: str) -> dict:
        path = self._get_workflow_path(name)
        if not path.exists():
            return {"success": False, "error": "NOT_FOUND",
                    "message": f"Workflow '{name}' not found"}
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"success": False, "error": "CORRUPTED_STATE",
                    "message": f"Workflow '{name}' has corrupted state — manual repair required"}
        if state.get("schema_version") != "2.0" and "stages" in state:
            state = self._migrate_v1_to_v2(state)
            self._write_state(name, state)
        return state

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

    def _update_shared_action(self, state, action, status, deliverables, context=None):
        """Update action in a shared stage (ideation/requirement)."""
        for stage_name in ("ideation", "requirement"):
            stage = state["shared"][stage_name]
            if action in stage.get("actions", {}):
                if stage["status"] == "locked":
                    if not self._try_unlock_shared_stage(state, stage_name):
                        return False, {"success": False, "error": "STAGE_LOCKED",
                                       "message": f"Stage '{stage_name}' is locked"}
                stage["actions"][action]["status"] = status
                if deliverables is not None:
                    stage["actions"][action]["deliverables"] = deliverables
                    if isinstance(deliverables, dict):
                        state["schema_version"] = "3.0"
                if context is not None:
                    stage["actions"][action]["context"] = context
                # Add next_actions_suggested when action is done
                if status == "done" and action in self._next_actions_map:
                    stage["actions"][action]["next_actions_suggested"] = self._next_actions_map[action]
                elif status != "done":
                    stage["actions"][action].pop("next_actions_suggested", None)
                return True, None
        return False, {"success": False, "error": "ACTION_NOT_FOUND",
                       "message": f"Action '{action}' not found in shared stages"}

    def _update_feature_action(self, state, action, status, feature_id, deliverables, context=None):
        """Update action in a per-feature stage."""
        feat = self._find_feature(state, feature_id)
        if not feat:
            return False, {"success": False, "error": "FEATURE_NOT_FOUND",
                           "message": f"Feature '{feature_id}' or action '{action}' not found"}
        for stage_name in ("implement", "validation", "feedback"):
            stage_data = feat.get(stage_name, {})
            if action in stage_data.get("actions", {}):
                if stage_data["status"] == "locked":
                    if not self._try_unlock_feature_stage(state, feat, stage_name):
                        return False, {"success": False, "error": "STAGE_LOCKED",
                                       "message": f"Stage '{stage_name}' is locked"}
                stage_data["actions"][action]["status"] = status
                if deliverables is not None:
                    stage_data["actions"][action]["deliverables"] = deliverables
                    if isinstance(deliverables, dict):
                        state["schema_version"] = "3.0"
                if context is not None:
                    stage_data["actions"][action]["context"] = context
                if status == "done" and action in self._next_actions_map:
                    stage_data["actions"][action]["next_actions_suggested"] = self._next_actions_map[action]
                elif status != "done":
                    stage_data["actions"][action].pop("next_actions_suggested", None)
                return True, None
        return False, {"success": False, "error": "FEATURE_NOT_FOUND",
                       "message": f"Feature '{feature_id}' or action '{action}' not found"}

    def _evaluate_stage_gating(self, state):
        """No-op: stage transitions are now on-demand via _try_unlock_stage."""
        pass

    def _find_feature(self, state, feature_id):
        """Find a feature dict in the features array by ID."""
        for feat in state.get("features", []):
            if feat.get("feature_id") == feature_id:
                return feat
        return None

    def _is_shared_stage_ready_to_unlock(self, state, stage_name):
        """Check if a shared stage's predecessor has all mandatory actions done."""
        shared_stages = [s for s in self._stage_order
                         if self._stage_config[s]["type"] == "shared"]
        idx = shared_stages.index(stage_name) if stage_name in shared_stages else -1
        if idx <= 0:
            return False
        prev_name = shared_stages[idx - 1]
        prev_stage = state["shared"].get(prev_name, {})
        prev_config = self._stage_config.get(prev_name, {})
        if prev_stage.get("status") not in ("in_progress",):
            return False
        actions = prev_stage.get("actions", {})
        return all(
            actions.get(a, {}).get("status") == "done"
            for a in prev_config.get("mandatory_actions", [])
        )

    def _is_feature_stage_ready_to_unlock(self, state, feature, stage_name):
        """Check if a feature's per-feature stage predecessor is ready."""
        if stage_name == "implement":
            req_config = self._stage_config.get("requirement", {})
            req_stage = state["shared"].get("requirement", {})
            actions = req_stage.get("actions", {})
            return all(
                actions.get(a, {}).get("status") == "done"
                for a in req_config.get("mandatory_actions", [])
            )
        per_feature_stages = [s for s in self._stage_order
                              if self._stage_config[s]["type"] == "per_feature"]
        idx = per_feature_stages.index(stage_name) if stage_name in per_feature_stages else -1
        if idx <= 0:
            return False
        prev_name = per_feature_stages[idx - 1]
        prev_config = self._stage_config.get(prev_name, {})
        prev_stage = feature.get(prev_name, {})
        if prev_stage.get("status") not in ("in_progress", "done"):
            return False
        actions = prev_stage.get("actions", {})
        return all(
            actions.get(a, {}).get("status") == "done"
            for a in prev_config.get("mandatory_actions", [])
        )

    def _try_unlock_shared_stage(self, state, stage_name):
        """Complete the predecessor shared stage and unlock *stage_name*."""
        if not self._is_shared_stage_ready_to_unlock(state, stage_name):
            return False
        shared_stages = [s for s in self._stage_order
                         if self._stage_config[s]["type"] == "shared"]
        idx = shared_stages.index(stage_name)
        if idx > 0:
            prev_name = shared_stages[idx - 1]
            state["shared"][prev_name]["status"] = "completed"
        state["shared"][stage_name]["status"] = "in_progress"
        state["current_stage"] = stage_name
        return True

    def _try_unlock_feature_stage(self, state, feature, stage_name):
        """Unlock a per-feature stage for a specific feature."""
        if not self._is_feature_stage_ready_to_unlock(state, feature, stage_name):
            return False
        if stage_name == "implement":
            req_stage = state["shared"].get("requirement", {})
            if req_stage.get("status") == "in_progress":
                req_stage["status"] = "completed"
        else:
            per_feature_stages = [s for s in self._stage_order
                                  if self._stage_config[s]["type"] == "per_feature"]
            idx = per_feature_stages.index(stage_name)
            if idx > 0:
                prev_name = per_feature_stages[idx - 1]
                feature[prev_name]["status"] = "done"
        feature[stage_name]["status"] = "in_progress"
        self._update_current_stage(state)
        return True

    def _update_current_stage(self, state):
        """Set current_stage to the highest stage with activity."""
        for stage_name in self._stage_order:
            config = self._stage_config[stage_name]
            if config["type"] == "shared":
                if state["shared"].get(stage_name, {}).get("status") == "in_progress":
                    state["current_stage"] = stage_name
            else:
                for feat in state.get("features", []):
                    if feat.get(stage_name, {}).get("status") in ("in_progress", "done"):
                        state["current_stage"] = stage_name
                        break

    def _is_feature_stage_done(self, state, feature_id, stage_name):
        """Check if a feature has completed all mandatory actions in a stage."""
        config = self._stage_config[stage_name]
        feat = self._find_feature(state, feature_id)
        if not feat:
            return False
        actions = feat.get(stage_name, {}).get("actions", {})
        return all(
            actions.get(a, {}).get("status") == "done"
            for a in config["mandatory_actions"]
        )

    def _compute_next_action(self, state):
        """Determine the recommended next action."""
        for stage_name in self._stage_order:
            config = self._stage_config[stage_name]

            if config["type"] == "shared":
                stage = state["shared"].get(stage_name, {})
                if stage.get("status") == "locked":
                    if self._is_shared_stage_ready_to_unlock(state, stage_name):
                        for action_name in config["mandatory_actions"]:
                            action = stage.get("actions", {}).get(action_name, {})
                            if action.get("status") in ("pending", "failed"):
                                return {"action": action_name, "stage": stage_name,
                                        "feature_id": None,
                                        "reason": "Next stage ready — click to start"}
                    continue
                if stage.get("status") == "in_progress":
                    for action_name in config["mandatory_actions"]:
                        action = stage.get("actions", {}).get(action_name, {})
                        if action.get("status") in ("pending", "failed"):
                            return {"action": action_name, "stage": stage_name,
                                    "feature_id": None,
                                    "reason": "Next pending mandatory action"}

            elif config["type"] == "per_feature":
                for feat in state.get("features", []):
                    feat_stage = feat.get(stage_name, {})
                    if feat_stage.get("status") == "locked":
                        if self._is_feature_stage_ready_to_unlock(state, feat, stage_name):
                            for action_name in config["mandatory_actions"]:
                                action = feat_stage.get("actions", {}).get(action_name, {})
                                if action.get("status") in ("pending", "failed"):
                                    return {"action": action_name, "stage": stage_name,
                                            "feature_id": feat["feature_id"],
                                            "reason": "Next stage ready — click to start"}
                        continue
                    if feat_stage.get("status") == "in_progress":
                        for action_name in config["mandatory_actions"]:
                            action = feat_stage.get("actions", {}).get(action_name, {})
                            if action.get("status") in ("pending", "failed"):
                                return {"action": action_name, "stage": stage_name,
                                        "feature_id": feat["feature_id"],
                                        "reason": "First unblocked feature with pending mandatory action"}

        return {"action": None, "stage": None, "feature_id": None,
                "reason": "All actions complete"}

    def _migrate_v1_to_v2(self, state):
        """Migrate v1.0 (flat stages) to v2.0 (shared + features)."""
        stages = state.get("stages", {})

        shared = {}
        for stage_name in ("ideation", "requirement"):
            if stage_name in stages:
                shared[stage_name] = stages[stage_name]

        feature_ids = list(stages.get("implement", {}).get("features", {}).keys())
        features = []
        for feat_id in feature_ids:
            impl_data = stages.get("implement", {}).get("features", {}).get(feat_id, {})
            feat_obj = {
                "feature_id": feat_id,
                "name": impl_data.get("name", feat_id),
                "depends_on": impl_data.get("depends_on", []),
            }
            for stage_name in ("implement", "validation", "feedback"):
                config = self._stage_config.get(stage_name, {})
                old_feat = stages.get(stage_name, {}).get("features", {}).get(feat_id, {})
                old_actions = old_feat.get("actions", {})
                optional_set = set(config.get("optional_actions", []))
                all_stage_actions = config.get("mandatory_actions", []) + config.get("optional_actions", [])

                stage_status = stages.get(stage_name, {}).get("status", "locked")
                if stage_status == "completed":
                    stage_status = "done"

                new_actions = {}
                for action_name in all_stage_actions:
                    if action_name in old_actions:
                        new_actions[action_name] = old_actions[action_name]
                    else:
                        action_data = {"status": "pending", "deliverables": []}
                        if action_name in optional_set:
                            action_data["optional"] = True
                            action_data["status"] = "skipped"
                        new_actions[action_name] = action_data

                feat_obj[stage_name] = {"status": stage_status, "actions": new_actions}
            features.append(feat_obj)

        return {
            "schema_version": "2.0",
            "name": state.get("name", ""),
            "created": state.get("created", ""),
            "last_activity": state.get("last_activity", ""),
            "idea_folder": state.get("idea_folder"),
            "current_stage": state.get("current_stage", "ideation"),
            "shared": shared,
            "features": features,
        }
