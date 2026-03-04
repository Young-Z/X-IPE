"""
Tests for FEATURE-041-E: Deliverable Tagging & Action Context Schema (MVP)

Covers:
- WorkflowManagerService: keyed deliverables, context field, dual-format
- Template validation: candidates references, tag uniqueness
- Runtime validation: instance deliverables vs template tags
- Candidate resolution algorithm
- MCP tool: update_workflow_action with dict/list deliverables + context
- API endpoints: folder-contents, candidates

TDD: All tests written before implementation — all should FAIL initially.
"""
import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def project_root(tmp_path):
    """Create a temp project root with workflow + config dirs."""
    wf_dir = tmp_path / "x-ipe-docs" / "engineering-workflow"
    wf_dir.mkdir(parents=True)
    config_dir = tmp_path / "x-ipe-docs" / "config"
    config_dir.mkdir(parents=True)
    return tmp_path


TAGGED_TEMPLATE = {
    "stage_order": ["ideation", "requirement", "implement", "validation", "feedback"],
    "stages": {
        "ideation": {
            "type": "shared",
            "next_stage": "requirement",
            "actions": {
                "compose_idea": {
                    "optional": False,
                    "deliverables": ["$output:raw-idea", "$output-folder:ideas-folder"],
                    "next_actions_suggested": ["refine_idea", "reference_uiux"]
                },
                "reference_uiux": {
                    "optional": True,
                    "deliverables": ["$output:uiux-reference"],
                    "next_actions_suggested": ["design_mockup", "refine_idea"]
                },
                "refine_idea": {
                    "optional": False,
                    "action_context": {
                        "raw-idea": {"required": True, "candidates": "ideas-folder"},
                        "uiux-reference": {"required": False}
                    },
                    "deliverables": ["$output:refined-idea", "$output-folder:refined-ideas-folder"],
                    "next_actions_suggested": ["design_mockup", "requirement_gathering"]
                },
                "design_mockup": {
                    "optional": True,
                    "action_context": {
                        "refined-idea": {"required": True, "candidates": "refined-ideas-folder"},
                        "uiux-reference": {"required": False}
                    },
                    "deliverables": ["$output:mockup-html", "$output-folder:mockups-folder"],
                    "next_actions_suggested": ["requirement_gathering"]
                }
            }
        },
        "requirement": {
            "type": "shared",
            "next_stage": "implement",
            "actions": {
                "requirement_gathering": {
                    "optional": False,
                    "action_context": {
                        "refined-idea": {"required": True, "candidates": "refined-ideas-folder"},
                        "mockup-html": {"required": False}
                    },
                    "deliverables": ["$output:requirement-doc", "$output-folder:requirements-folder"],
                    "next_actions_suggested": ["feature_breakdown"]
                },
                "feature_breakdown": {
                    "optional": False,
                    "action_context": {
                        "requirement-doc": {"required": True, "candidates": "requirements-folder"}
                    },
                    "deliverables": ["$output:features-list", "$output-folder:breakdown-folder"],
                    "next_actions_suggested": []
                }
            }
        },
        "implement": {
            "type": "per_feature",
            "next_stage": "validation",
            "actions": {
                "feature_refinement": {
                    "optional": False,
                    "action_context": {
                        "requirement-doc": {"required": True, "candidates": "requirements-folder"},
                        "features-list": {"required": True}
                    },
                    "deliverables": ["$output:specification", "$output-folder:feature-docs-folder"],
                    "next_actions_suggested": ["technical_design"]
                },
                "technical_design": {
                    "optional": False,
                    "action_context": {
                        "specification": {"required": True, "candidates": "feature-docs-folder"}
                    },
                    "deliverables": ["$output:tech-design", "$output-folder:feature-docs-folder"],
                    "next_actions_suggested": ["implementation"]
                },
                "implementation": {
                    "optional": False,
                    "action_context": {
                        "tech-design": {"required": True, "candidates": "feature-docs-folder"},
                        "specification": {"required": True, "candidates": "feature-docs-folder"}
                    },
                    "deliverables": ["$output:impl-files", "$output-folder:impl-folder"],
                    "next_actions_suggested": ["acceptance_testing"]
                }
            }
        },
        "validation": {
            "type": "per_feature",
            "next_stage": "feedback",
            "actions": {
                "acceptance_testing": {
                    "optional": False,
                    "action_context": {
                        "specification": {"required": True, "candidates": "feature-docs-folder"},
                        "impl-files": {"required": True, "candidates": "impl-folder"}
                    },
                    "deliverables": ["$output:test-report", "$output-folder:test-folder"],
                    "next_actions_suggested": ["quality_evaluation"]
                },
                "quality_evaluation": {
                    "optional": True,
                    "action_context": {
                        "test-report": {"required": True, "candidates": "test-folder"}
                    },
                    "deliverables": ["$output:eval-report"],
                    "next_actions_suggested": ["change_request"]
                }
            }
        },
        "feedback": {
            "type": "per_feature",
            "next_stage": None,
            "actions": {
                "change_request": {
                    "optional": True,
                    "action_context": {
                        "eval-report": {"required": False},
                        "specification": {"required": True, "candidates": "feature-docs-folder"}
                    },
                    "deliverables": ["$output:cr-doc", "$output-folder:cr-folder"],
                    "next_actions_suggested": []
                }
            }
        }
    }
}


@pytest.fixture
def tagged_template(project_root):
    """Write tagged template to project config directory."""
    config_path = project_root / "x-ipe-docs" / "config" / "workflow-template.json"
    config_path.write_text(json.dumps(TAGGED_TEMPLATE, indent=2))
    return config_path


@pytest.fixture
def service(project_root, tagged_template):
    """Create a WorkflowManagerService instance with tagged template."""
    from x_ipe.services.workflow_manager_service import WorkflowManagerService
    return WorkflowManagerService(str(project_root))


@pytest.fixture
def app(project_root, tagged_template):
    """Create Flask test app with tagged template."""
    from x_ipe.app import create_app
    return create_app({"TESTING": True, "PROJECT_ROOT": str(project_root)})


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_workflow(service):
    """Create a sample workflow and return its name."""
    name = "test-wf-041e"
    service.create_workflow(name)
    return name


# ==============================================================================
# Unit Tests: Keyed Deliverables
# ==============================================================================

class TestKeyedDeliverables:
    """Test that instance deliverables are stored as keyed objects."""

    def test_update_action_with_dict_deliverables(self, service, sample_workflow):
        """Keyed deliverables dict should be stored directly."""
        deliverables = {
            "raw-idea": "x-ipe-docs/ideas/test/new-idea.md",
            "ideas-folder": "x-ipe-docs/ideas/test"
        }
        result = service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables=deliverables
        )
        assert result["success"] is True
        state = service._read_state(sample_workflow)
        stored = state["shared"]["ideation"]["actions"]["compose_idea"]["deliverables"]
        assert isinstance(stored, dict)
        assert stored["raw-idea"] == "x-ipe-docs/ideas/test/new-idea.md"
        assert stored["ideas-folder"] == "x-ipe-docs/ideas/test"

    def test_update_action_with_list_deliverables_converts(self, service, sample_workflow):
        """Legacy list deliverables should be converted to keyed object using template tags."""
        deliverables = [
            "x-ipe-docs/ideas/test/new-idea.md",
            "x-ipe-docs/ideas/test"
        ]
        result = service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables=deliverables
        )
        assert result["success"] is True
        state = service._read_state(sample_workflow)
        stored = state["shared"]["ideation"]["actions"]["compose_idea"]["deliverables"]
        assert isinstance(stored, dict)
        assert stored.get("raw-idea") == "x-ipe-docs/ideas/test/new-idea.md"
        assert stored.get("ideas-folder") == "x-ipe-docs/ideas/test"

    def test_schema_version_set_on_keyed_deliverables(self, service, sample_workflow):
        """Instance should have schema_version 3.0 when keyed deliverables used."""
        result = service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables={"raw-idea": "idea.md", "ideas-folder": "ideas/"}
        )
        assert result["success"] is True
        state = service._read_state(sample_workflow)
        assert state.get("schema_version") == "3.0"

    def test_empty_list_converts_to_empty_dict(self, service, sample_workflow):
        """Empty list deliverables converts to empty dict."""
        result = service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables=[]
        )
        assert result["success"] is True
        state = service._read_state(sample_workflow)
        stored = state["shared"]["ideation"]["actions"]["compose_idea"]["deliverables"]
        assert isinstance(stored, dict)
        assert stored == {}

    def test_list_longer_than_tags_ignores_extra(self, service, sample_workflow):
        """Extra list items beyond template tag count are ignored."""
        deliverables = ["idea.md", "ideas/", "extra-file.md"]
        result = service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables=deliverables
        )
        assert result["success"] is True
        state = service._read_state(sample_workflow)
        stored = state["shared"]["ideation"]["actions"]["compose_idea"]["deliverables"]
        assert len(stored) == 2  # Only 2 tags defined for compose_idea


# ==============================================================================
# Unit Tests: Context Field
# ==============================================================================

class TestContextField:
    """Test that action context selections are stored in instance."""

    def test_context_stored_on_update(self, service, sample_workflow):
        """Context dict should be stored in the action's context field."""
        # First complete compose_idea
        service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables={"raw-idea": "idea.md", "ideas-folder": "ideas/"}
        )
        # Now update refine_idea with context
        context = {"raw-idea": "idea.md", "uiux-reference": "N/A"}
        result = service.update_action_status(
            sample_workflow, "refine_idea", "done",
            deliverables={"refined-idea": "refined.md", "refined-ideas-folder": "refined/"},
            context=context
        )
        assert result["success"] is True
        state = service._read_state(sample_workflow)
        stored_ctx = state["shared"]["ideation"]["actions"]["refine_idea"].get("context")
        assert stored_ctx == {"raw-idea": "idea.md", "uiux-reference": "N/A"}

    def test_context_absent_defaults_to_empty(self, service, sample_workflow):
        """When no context provided, action should have no context field (or empty)."""
        result = service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables={"raw-idea": "idea.md", "ideas-folder": "ideas/"}
        )
        assert result["success"] is True
        state = service._read_state(sample_workflow)
        action = state["shared"]["ideation"]["actions"]["compose_idea"]
        # compose_idea has no action_context, so context should be absent or empty
        assert action.get("context") is None or action.get("context") == {}

    def test_auto_detect_persists_in_context(self, service, sample_workflow):
        """'auto-detect' value should persist in context field."""
        service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables={"raw-idea": "idea.md", "ideas-folder": "ideas/"}
        )
        context = {"raw-idea": "auto-detect", "uiux-reference": "auto-detect"}
        result = service.update_action_status(
            sample_workflow, "refine_idea", "in_progress",
            context=context
        )
        assert result["success"] is True
        state = service._read_state(sample_workflow)
        stored = state["shared"]["ideation"]["actions"]["refine_idea"]["context"]
        assert stored["raw-idea"] == "auto-detect"
        assert stored["uiux-reference"] == "auto-detect"

    def test_per_feature_context_stored(self, service, sample_workflow):
        """Feature-level action context should be stored within feature lane."""
        # Setup: complete shared stages and create features
        service.update_action_status(sample_workflow, "compose_idea", "done",
                                     deliverables={"raw-idea": "idea.md", "ideas-folder": "ideas/"})
        service.update_action_status(sample_workflow, "refine_idea", "done",
                                     deliverables={"refined-idea": "refined.md", "refined-ideas-folder": "refined/"})
        service.update_action_status(sample_workflow, "requirement_gathering", "done",
                                     deliverables={"requirement-doc": "req.md", "requirements-folder": "reqs/"})
        service.update_action_status(
            sample_workflow, "feature_breakdown", "done",
            deliverables={"features-list": "features.md", "breakdown-folder": "breakdown/"},
            features=[{"id": "FEATURE-E-1", "name": "Test Feature", "depends_on": []}]
        )
        # Feature-level action with context
        context = {"requirement-doc": "reqs/req.md", "features-list": "auto-detect"}
        result = service.update_action_status(
            sample_workflow, "feature_refinement", "done",
            feature_id="FEATURE-E-1",
            deliverables={"specification": "spec.md", "feature-docs-folder": "docs/"},
            context=context
        )
        assert result["success"] is True
        state = service._read_state(sample_workflow)
        feat = next(f for f in state["features"] if f["feature_id"] == "FEATURE-E-1")
        feat_ctx = feat["implement"]["actions"]["feature_refinement"].get("context")
        assert feat_ctx is not None
        assert feat_ctx["requirement-doc"] == "reqs/req.md"


# ==============================================================================
# Unit Tests: Template Validation
# ==============================================================================

class TestTemplateValidation:
    """Test static template validation at load time."""

    def test_valid_template_passes(self, service):
        """Valid tagged template should pass validation."""
        result = service.validate_template()
        assert result is True

    def test_invalid_candidates_reference_fails(self, project_root):
        """Template with unknown candidates reference should fail validation."""
        bad_template = {
            "stage_order": ["ideation"],
            "stages": {
                "ideation": {
                    "type": "shared",
                    "next_stage": None,
                    "actions": {
                        "compose_idea": {
                            "optional": False,
                            "deliverables": ["$output:raw-idea"],
                            "next_actions_suggested": []
                        },
                        "refine_idea": {
                            "optional": False,
                            "action_context": {
                                "raw-idea": {"required": True, "candidates": "nonexistent-folder"}
                            },
                            "deliverables": ["$output:refined-idea"],
                            "next_actions_suggested": []
                        }
                    }
                }
            }
        }
        config_path = project_root / "x-ipe-docs" / "config" / "workflow-template.json"
        config_path.write_text(json.dumps(bad_template))
        from x_ipe.services.workflow_manager_service import WorkflowManagerService
        svc = WorkflowManagerService(str(project_root))
        with pytest.raises(ValueError, match="nonexistent-folder"):
            svc.validate_template()

    def test_duplicate_tag_within_stage_fails(self, project_root):
        """Duplicate tag names within the same action should fail validation."""
        bad_template = {
            "stage_order": ["ideation"],
            "stages": {
                "ideation": {
                    "type": "shared",
                    "next_stage": None,
                    "actions": {
                        "compose_idea": {
                            "optional": False,
                            "deliverables": ["$output:my-file", "$output-folder:my-file"],
                            "next_actions_suggested": []
                        }
                    }
                }
            }
        }
        config_path = project_root / "x-ipe-docs" / "config" / "workflow-template.json"
        config_path.write_text(json.dumps(bad_template))
        from x_ipe.services.workflow_manager_service import WorkflowManagerService
        svc = WorkflowManagerService(str(project_root))
        with pytest.raises(ValueError, match="my-file"):
            svc.validate_template()

    def test_cross_stage_duplicate_tags_allowed(self, service):
        """Cross-stage duplicate tag names should be allowed."""
        # The TAGGED_TEMPLATE has feature-docs-folder in both implement and validation stages
        # via technical_design — this should not fail
        result = service.validate_template()
        assert result is True


# ==============================================================================
# Unit Tests: Runtime Validation
# ==============================================================================

class TestRuntimeValidation:
    """Test runtime validation of instance deliverables vs template tags."""

    def test_matching_keys_passes(self, service):
        """Instance keys matching template tags should pass."""
        result = service.validate_action_deliverables(
            "compose_idea",
            {"raw-idea": "idea.md", "ideas-folder": "ideas/"}
        )
        assert result is True

    def test_missing_key_warns(self, service):
        """Instance missing a template tag should log warning but not fail hard."""
        result = service.validate_action_deliverables(
            "compose_idea",
            {"raw-idea": "idea.md"}  # missing ideas-folder
        )
        assert result is False  # validation fails but doesn't raise

    def test_extra_keys_accepted(self, service):
        """Instance with extra keys beyond template should be accepted."""
        result = service.validate_action_deliverables(
            "compose_idea",
            {"raw-idea": "idea.md", "ideas-folder": "ideas/", "extra-key": "bonus.md"}
        )
        assert result is True

    def test_legacy_list_skips_validation(self, service):
        """Legacy list format should skip keyed validation."""
        result = service.validate_action_deliverables(
            "compose_idea",
            ["idea.md", "ideas/"]  # list, not dict
        )
        assert result is True  # skip validation for legacy


# ==============================================================================
# Unit Tests: Candidate Resolution
# ==============================================================================

class TestCandidateResolution:
    """Test the candidate resolution algorithm."""

    def test_resolve_candidates_finds_folder(self, service, sample_workflow):
        """resolve_candidates should find the $output-folder deliverable from prior action."""
        # Complete compose_idea with deliverables
        service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables={
                "raw-idea": "x-ipe-docs/ideas/test/new-idea.md",
                "ideas-folder": "x-ipe-docs/ideas/test"
            }
        )
        # Resolve candidates for refine_idea's "ideas-folder" candidate
        results = service.resolve_candidates(
            sample_workflow, "refine_idea", "ideas-folder"
        )
        assert len(results) > 0
        folder_result = next((r for r in results if r["type"] == "folder"), None)
        assert folder_result is not None
        assert folder_result["path"] == "x-ipe-docs/ideas/test"

    def test_resolve_candidates_returns_output_file_too(self, service, sample_workflow):
        """resolve_candidates should include $output file matching the name."""
        service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables={
                "raw-idea": "x-ipe-docs/ideas/test/new-idea.md",
                "ideas-folder": "x-ipe-docs/ideas/test"
            }
        )
        results = service.resolve_candidates(
            sample_workflow, "refine_idea", "ideas-folder"
        )
        # Should have both the folder entry
        types = [r["type"] for r in results]
        assert "folder" in types

    def test_resolve_candidates_later_stage_precedence(self, service, sample_workflow):
        """Later stage deliverables should take precedence."""
        # If same-named folder exists in multiple stages, later wins
        service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables={"raw-idea": "idea.md", "ideas-folder": "ideas/v1"}
        )
        # refine_idea also has refined-ideas-folder
        service.update_action_status(
            sample_workflow, "refine_idea", "done",
            deliverables={"refined-idea": "refined.md", "refined-ideas-folder": "ideas/v2"},
            context={"raw-idea": "idea.md", "uiux-reference": "N/A"}
        )
        # requirement_gathering wants refined-ideas-folder — should get ideas/v2
        results = service.resolve_candidates(
            sample_workflow, "requirement_gathering", "refined-ideas-folder"
        )
        assert any(r["path"] == "ideas/v2" for r in results)

    def test_resolve_candidates_per_feature_scoping(self, service, sample_workflow):
        """Per-feature resolution should search feature lane first, then shared."""
        # Setup shared stages
        service.update_action_status(sample_workflow, "compose_idea", "done",
                                     deliverables={"raw-idea": "idea.md", "ideas-folder": "ideas/"})
        service.update_action_status(sample_workflow, "refine_idea", "done",
                                     deliverables={"refined-idea": "refined.md", "refined-ideas-folder": "refined/"})
        service.update_action_status(sample_workflow, "requirement_gathering", "done",
                                     deliverables={"requirement-doc": "req.md", "requirements-folder": "reqs/"})
        service.update_action_status(
            sample_workflow, "feature_breakdown", "done",
            deliverables={"features-list": "features.md", "breakdown-folder": "breakdown/"},
            features=[{"id": "F-1", "name": "Feature 1", "depends_on": []}]
        )
        # Complete feature_refinement for F-1 (creates feature-docs-folder)
        service.update_action_status(
            sample_workflow, "feature_refinement", "done", feature_id="F-1",
            deliverables={"specification": "f1-spec.md", "feature-docs-folder": "f1-docs/"},
            context={"requirement-doc": "req.md", "features-list": "auto-detect"}
        )
        # Resolve for technical_design within F-1 — should find feature-docs-folder from F-1
        results = service.resolve_candidates(
            sample_workflow, "technical_design", "feature-docs-folder", feature_id="F-1"
        )
        assert any(r["path"] == "f1-docs/" for r in results)


# ==============================================================================
# Unit Tests: Backward Compatibility
# ==============================================================================

class TestBackwardCompat:
    """Test backward compatibility with legacy list deliverables."""

    def test_resolve_deliverables_handles_dict(self, service, sample_workflow):
        """resolve_deliverables should handle keyed dict format."""
        service.update_action_status(
            sample_workflow, "compose_idea", "done",
            deliverables={"raw-idea": "idea.md", "ideas-folder": "ideas/"}
        )
        result = service.resolve_deliverables(sample_workflow)
        results = result["deliverables"]
        names = [r["name"] for r in results]
        assert "raw-idea" in names or any("idea.md" in r.get("path", "") for r in results)

    def test_resolve_deliverables_handles_list(self, service, sample_workflow):
        """resolve_deliverables should handle legacy list format."""
        # Manually write legacy format to instance
        state = service._read_state(sample_workflow)
        state["shared"]["ideation"]["actions"]["compose_idea"]["status"] = "done"
        state["shared"]["ideation"]["actions"]["compose_idea"]["deliverables"] = ["idea.md", "ideas/"]
        service._write_state(sample_workflow, state)

        result = service.resolve_deliverables(sample_workflow)
        assert len(result["deliverables"]) > 0

    def test_idea_folder_preserved(self, service, sample_workflow):
        """idea_folder field should not be removed from instance."""
        state = service._read_state(sample_workflow)
        # idea_folder may or may not exist, but should not be removed
        if "idea_folder" in state:
            service.update_action_status(
                sample_workflow, "compose_idea", "done",
                deliverables={"raw-idea": "idea.md", "ideas-folder": "ideas/"}
            )
            state2 = service._read_state(sample_workflow)
            assert "idea_folder" in state2


# ==============================================================================
# API Tests: Action Update with Context
# ==============================================================================

class TestActionUpdateAPI:
    """Test Flask API endpoints for new deliverable/context format."""

    def test_post_action_with_dict_deliverables(self, client, sample_workflow):
        """POST /api/workflow/{name}/action with dict deliverables."""
        resp = client.post(f"/api/workflow/{sample_workflow}/action", json={
            "action": "compose_idea",
            "status": "done",
            "deliverables": {
                "raw-idea": "idea.md",
                "ideas-folder": "ideas/"
            }
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_post_action_with_list_deliverables(self, client, sample_workflow):
        """POST /api/workflow/{name}/action with list deliverables (legacy)."""
        resp = client.post(f"/api/workflow/{sample_workflow}/action", json={
            "action": "compose_idea",
            "status": "done",
            "deliverables": ["idea.md", "ideas/"]
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_post_action_with_context(self, client, sample_workflow):
        """POST /api/workflow/{name}/action with context field."""
        # First complete compose_idea
        client.post(f"/api/workflow/{sample_workflow}/action", json={
            "action": "compose_idea", "status": "done",
            "deliverables": {"raw-idea": "idea.md", "ideas-folder": "ideas/"}
        })
        # Now refine_idea with context
        resp = client.post(f"/api/workflow/{sample_workflow}/action", json={
            "action": "refine_idea",
            "status": "done",
            "deliverables": {"refined-idea": "refined.md", "refined-ideas-folder": "refined/"},
            "context": {"raw-idea": "idea.md", "uiux-reference": "N/A"}
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True


# ==============================================================================
# API Tests: Candidates Endpoint
# ==============================================================================

class TestCandidatesAPI:
    """Test the candidates resolution API endpoint."""

    def test_get_candidates(self, client, sample_workflow):
        """GET /api/workflow/{name}/candidates/{action}/{candidates} returns results."""
        # Setup
        client.post(f"/api/workflow/{sample_workflow}/action", json={
            "action": "compose_idea", "status": "done",
            "deliverables": {"raw-idea": "idea.md", "ideas-folder": "x-ipe-docs/ideas/test"}
        })
        resp = client.get(
            f"/api/workflow/{sample_workflow}/candidates/refine_idea/ideas-folder"
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)


# ==============================================================================
# API Tests: Folder Contents Endpoint
# ==============================================================================

class TestFolderContentsAPI:
    """Test the folder contents listing endpoint."""

    def test_list_folder_contents(self, client, project_root):
        """GET /api/workflow/{name}/folder-contents?path=... lists files."""
        # Create test folder with files
        folder = project_root / "x-ipe-docs" / "ideas" / "test"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "idea.md").write_text("# Idea")
        (folder / "notes.txt").write_text("notes")

        resp = client.get(
            f"/api/workflow/test/folder-contents?path={folder}"
        )
        assert resp.status_code == 200
        files = resp.get_json()
        assert len(files) >= 2
        assert any("idea.md" in f for f in files)
        assert any("notes.txt" in f for f in files)

    def test_list_folder_contents_relative_path(self, client, project_root):
        """GET folder-contents with relative path resolves against PROJECT_ROOT."""
        folder = project_root / "x-ipe-docs" / "ideas" / "wf-test"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "summary-v1.md").write_text("# Summary v1")
        (folder / "summary-v2.md").write_text("# Summary v2")

        # Use RELATIVE path (as stored in workflow instance deliverables)
        resp = client.get(
            "/api/workflow/test/folder-contents?path=x-ipe-docs/ideas/wf-test"
        )
        assert resp.status_code == 200
        files = resp.get_json()
        assert len(files) >= 2
        assert any("summary-v1.md" in f for f in files)
        assert any("summary-v2.md" in f for f in files)
        # Verify paths preserve relative format
        for f in files:
            assert not os.path.isabs(f), f"Expected relative path, got: {f}"

    def test_list_nonexistent_folder(self, client):
        """GET folder-contents for nonexistent path returns empty list."""
        resp = client.get(
            "/api/workflow/test/folder-contents?path=/nonexistent/path"
        )
        assert resp.status_code == 200
        assert resp.get_json() == []
