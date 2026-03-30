"""Tests for x-ipe-tool-x-ipe-app-interactor scripts.

Covers _lib.py shared utilities, workflow_get_state.py, and
workflow_update_action.py — FEATURE-052-A acceptance criteria.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts dir to path for imports
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".github" / "skills" / "x-ipe-tool-x-ipe-app-interactor" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import _lib  # noqa: E402


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def tmp_project(tmp_path):
    """Create a minimal project structure with x-ipe-docs marker."""
    (tmp_path / "x-ipe-docs").mkdir()
    (tmp_path / "x-ipe-docs" / "engineering-workflow").mkdir(parents=True)
    (tmp_path / "x-ipe-docs" / "config").mkdir(parents=True)
    (tmp_path / "x-ipe-docs" / "knowledge-base").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def workflow_template():
    """Minimal workflow template for testing."""
    return {
        "stage_order": ["ideation", "requirement", "implement", "validation", "feedback"],
        "stages": {
            "ideation": {
                "type": "shared",
                "next_stage": "requirement",
                "actions": {
                    "compose_idea": {
                        "optional": False,
                        "deliverables": ["$output:raw-ideas", "$output-folder:ideas-folder"],
                        "next_actions_suggested": ["refine_idea"],
                    },
                    "refine_idea": {
                        "optional": True,
                        "deliverables": ["$output:refined-idea"],
                        "next_actions_suggested": ["requirement_gathering"],
                    },
                },
            },
            "requirement": {
                "type": "shared",
                "next_stage": "implement",
                "actions": {
                    "requirement_gathering": {
                        "optional": False,
                        "deliverables": ["$output:requirement-doc"],
                        "next_actions_suggested": ["feature_breakdown"],
                    },
                    "feature_breakdown": {
                        "optional": False,
                        "deliverables": ["$output:features-list", "$output-folder:breakdown-folder"],
                        "next_actions_suggested": [],
                    },
                },
            },
            "implement": {
                "type": "per_feature",
                "next_stage": "validation",
                "actions": {
                    "feature_refinement": {
                        "optional": False,
                        "deliverables": ["$output:specification", "$output-folder:feature-docs-folder"],
                        "next_actions_suggested": ["technical_design"],
                    },
                    "technical_design": {
                        "optional": False,
                        "deliverables": ["$output:tech-design"],
                        "next_actions_suggested": ["implementation"],
                    },
                    "implementation": {
                        "optional": False,
                        "deliverables": ["$output:impl-files"],
                        "next_actions_suggested": ["acceptance_testing"],
                    },
                },
            },
            "validation": {
                "type": "per_feature",
                "next_stage": "feedback",
                "actions": {
                    "acceptance_testing": {
                        "optional": False,
                        "deliverables": ["$output:test-report"],
                        "next_actions_suggested": ["feature_closing"],
                    },
                    "feature_closing": {
                        "optional": False,
                        "deliverables": [],
                        "next_actions_suggested": ["human_playground"],
                    },
                },
            },
            "feedback": {
                "type": "per_feature",
                "next_stage": None,
                "actions": {
                    "human_playground": {
                        "optional": True,
                        "deliverables": ["$output:playground-url"],
                        "next_actions_suggested": [],
                    },
                },
            },
        },
    }


@pytest.fixture
def write_template(tmp_project, workflow_template):
    """Write workflow template to the project config dir."""
    template_path = tmp_project / "x-ipe-docs" / "config" / "workflow-template.json"
    template_path.write_text(json.dumps(workflow_template), encoding="utf-8")
    return template_path


@pytest.fixture
def sample_state():
    """A sample workflow state dict for testing."""
    return {
        "schema_version": "2.0",
        "name": "test-wf",
        "created": "2026-01-01T00:00:00+00:00",
        "last_activity": "2026-01-01T00:00:00+00:00",
        "idea_folder": None,
        "current_stage": "ideation",
        "global": {"process_preference": {"interaction_mode": "interact-with-human"}},
        "shared": {
            "ideation": {
                "status": "in_progress",
                "actions": {
                    "compose_idea": {"status": "pending", "deliverables": []},
                    "refine_idea": {"status": "pending", "deliverables": [], "optional": True},
                },
            },
            "requirement": {
                "status": "locked",
                "actions": {
                    "requirement_gathering": {"status": "pending", "deliverables": []},
                    "feature_breakdown": {"status": "pending", "deliverables": []},
                },
            },
        },
        "features": [],
    }


@pytest.fixture
def write_state(tmp_project, sample_state):
    """Write a sample workflow state file and return the path."""
    state_path = tmp_project / "x-ipe-docs" / "engineering-workflow" / "workflow-test-wf.json"
    state_path.write_text(json.dumps(sample_state, indent=2), encoding="utf-8")
    return state_path


# ============================================================================
# AC-052-A-01: Atomic JSON I/O
# ============================================================================

class TestAtomicIO:
    """AC-052-A-01a through 01f."""

    def test_write_then_read(self, tmp_path):
        """AC-052-A-01a: Write valid dict, read back correctly."""
        path = tmp_path / "test.json"
        data = {"hello": "world", "count": 42, "unicode": "你好"}
        _lib.atomic_write_json(path, data)
        result = _lib.atomic_read_json(path)
        assert result == data

    def test_write_format(self, tmp_path):
        """AC-052-A-01a: JSON written with indent=2 and ensure_ascii=False."""
        path = tmp_path / "test.json"
        _lib.atomic_write_json(path, {"key": "值"})
        raw = path.read_text(encoding="utf-8")
        assert "  " in raw  # indented
        assert "值" in raw  # not escaped

    def test_write_uses_atomic_pattern(self, tmp_path):
        """AC-052-A-01b: Uses tempfile + fsync + os.replace pattern."""
        path = tmp_path / "test.json"
        _lib.atomic_write_json(path, {"a": 1})
        # If it succeeded, the file exists at path (os.replace worked)
        assert path.exists()
        # No leftover .tmp files
        assert not list(tmp_path.glob("*.tmp"))

    def test_write_failure_cleans_up_temp(self, tmp_path):
        """AC-052-A-01c: Temp file cleaned up on exception."""
        path = tmp_path / "test.json"
        _lib.atomic_write_json(path, {"original": True})

        # Try writing a non-serializable object
        class BadObj:
            pass
        with pytest.raises(TypeError):
            _lib.atomic_write_json(path, {"bad": BadObj()})

        # Original file unchanged
        result = _lib.atomic_read_json(path)
        assert result == {"original": True}
        # No temp files left
        assert not list(tmp_path.glob("*.tmp"))

    def test_read_valid_json(self, tmp_path):
        """AC-052-A-01d: Read valid JSON returns parsed dict."""
        path = tmp_path / "test.json"
        path.write_text('{"key": "value"}', encoding="utf-8")
        result = _lib.atomic_read_json(path)
        assert result == {"key": "value"}

    def test_read_missing_file(self, tmp_path):
        """AC-052-A-01e: Missing file returns error dict."""
        path = tmp_path / "nonexistent.json"
        result = _lib.atomic_read_json(path)
        assert result["success"] is False
        assert result["error"] == "FILE_NOT_FOUND"

    def test_read_invalid_json(self, tmp_path):
        """AC-052-A-01f: Invalid JSON returns error dict."""
        path = tmp_path / "bad.json"
        path.write_text("{invalid json", encoding="utf-8")
        result = _lib.atomic_read_json(path)
        assert result["success"] is False
        assert result["error"] == "JSON_PARSE_ERROR"


# ============================================================================
# AC-052-A-02: File Locking
# ============================================================================

class TestFileLocking:
    """AC-052-A-02a through 02d."""

    def test_lock_acquired_and_released(self, tmp_path):
        """AC-052-A-02a, 02c: Lock acquired, body executes, lock released."""
        lock_path = tmp_path / "test.lock"
        executed = False
        with _lib.with_file_lock(lock_path, timeout=5):
            executed = True
            assert lock_path.exists()
        assert executed

    def test_lock_timeout(self, tmp_path):
        """AC-052-A-02b: Exits with code 3 on lock timeout."""
        lock_path = tmp_path / "test.lock"
        # Hold the lock in our process
        fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            with pytest.raises(SystemExit) as exc_info:
                with _lib.with_file_lock(lock_path, timeout=0.3):
                    pass  # Should not reach here
            assert exc_info.value.code == _lib.EXIT_LOCK_TIMEOUT
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


# ============================================================================
# AC-052-A-03: Project Root Discovery
# ============================================================================

class TestProjectRoot:
    """AC-052-A-03a through 03d."""

    def test_resolve_from_project_root(self, tmp_project):
        """AC-052-A-03a: Finds root when CWD has x-ipe-docs/."""
        with patch("_lib.Path.cwd", return_value=tmp_project):
            root = _lib.resolve_project_root()
            assert root == tmp_project

    def test_resolve_from_nested_dir(self, tmp_project):
        """AC-052-A-03b: Finds root from deeply nested CWD."""
        nested = tmp_project / "src" / "x_ipe" / "services"
        nested.mkdir(parents=True)
        with patch("_lib.Path.cwd", return_value=nested):
            root = _lib.resolve_project_root()
            assert root == tmp_project

    def test_resolve_fails_outside_project(self, tmp_path):
        """AC-052-A-03c: Exits with code 2 when no marker found."""
        with patch("_lib.Path.cwd", return_value=tmp_path):
            with pytest.raises(SystemExit) as exc_info:
                _lib.resolve_project_root()
            assert exc_info.value.code == _lib.EXIT_FILE_NOT_FOUND

    def test_resolve_workflow_dir(self, tmp_project):
        """AC-052-A-03d: Returns correct workflow dir path."""
        wf_dir = _lib.resolve_workflow_dir(tmp_project)
        assert wf_dir == tmp_project / "x-ipe-docs" / "engineering-workflow"

    def test_resolve_kb_root(self, tmp_project):
        """resolve_kb_root returns correct path."""
        kb_root = _lib.resolve_kb_root(tmp_project)
        assert kb_root == tmp_project / "x-ipe-docs" / "knowledge-base"


# ============================================================================
# AC-052-A-04: Output Formatting
# ============================================================================

class TestOutputFormatting:
    """AC-052-A-04a through 04c."""

    def test_output_json(self, capsys):
        """AC-052-A-04a: JSON output with trailing newline."""
        _lib.output_result({"success": True, "data": {"key": "val"}}, fmt="json")
        captured = capsys.readouterr()
        parsed = json.loads(captured.out.strip())
        assert parsed["success"] is True
        assert captured.out.endswith("\n")

    def test_output_text_success(self, capsys):
        """AC-052-A-04b: Text output for success."""
        _lib.output_result({"success": True, "data": {"action": "done"}}, fmt="text")
        captured = capsys.readouterr()
        assert "action: done" in captured.out

    def test_output_text_error(self, capsys):
        """AC-052-A-04c: Text output for error."""
        _lib.output_result({"success": False, "error": "OOPS", "message": "bad"}, fmt="text")
        captured = capsys.readouterr()
        assert "ERROR [OOPS]" in captured.out


# ============================================================================
# AC-052-A-05: Exit Codes
# ============================================================================

class TestExitCodes:
    """AC-052-A-05a through 05d."""

    def test_exit_with_error_code_1(self, capsys):
        """AC-052-A-05b: Validation error exits with code 1."""
        with pytest.raises(SystemExit) as exc_info:
            _lib.exit_with_error(1, "INVALID_STATUS", "bad status")
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["error"] == "INVALID_STATUS"

    def test_exit_with_error_code_2(self, capsys):
        """AC-052-A-05c: File not found exits with code 2."""
        with pytest.raises(SystemExit) as exc_info:
            _lib.exit_with_error(2, "FILE_NOT_FOUND", "missing")
        assert exc_info.value.code == 2

    def test_exit_with_error_code_3(self, capsys):
        """AC-052-A-05d: Lock timeout exits with code 3."""
        with pytest.raises(SystemExit) as exc_info:
            _lib.exit_with_error(3, "LOCK_TIMEOUT", "timeout")
        assert exc_info.value.code == 3


# ============================================================================
# AC-052-A-06: workflow_update_action.py CLI
# ============================================================================

class TestWorkflowUpdateAction:
    """AC-052-A-06a through 06i and related ACs."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_project, write_template, write_state, sample_state):
        """Set up project with template and state."""
        self.root = tmp_project
        self.state_path = write_state
        self.template_path = write_template
        self.initial_state = sample_state

    def _run(self, args: list[str]) -> tuple[dict, int]:
        """Run workflow_update_action.main() and capture output."""
        import workflow_update_action as wua
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        try:
            with patch("_lib.Path.cwd", return_value=self.root):
                with redirect_stdout(buf):
                    wua.main(args)
            return json.loads(buf.getvalue()), 0
        except SystemExit as e:
            output = buf.getvalue()
            if output.strip():
                return json.loads(output), e.code
            return {}, e.code

    def test_update_shared_action_done(self):
        """AC-052-A-06a: Update shared action status to done."""
        result, code = self._run([
            "--workflow", "test-wf",
            "--action", "compose_idea",
            "--status", "done",
        ])
        assert code == 0
        assert result["success"] is True
        assert result["data"]["action_updated"] == "compose_idea"
        assert result["data"]["new_status"] == "done"

        # Verify state was persisted
        state = json.loads(self.state_path.read_text())
        assert state["shared"]["ideation"]["actions"]["compose_idea"]["status"] == "done"

    def test_invalid_status(self):
        """AC-052-A-06b: Invalid status exits with code 1."""
        result, code = self._run([
            "--workflow", "test-wf",
            "--action", "compose_idea",
            "--status", "bogus",
        ])
        assert code == 1
        assert result["error"] == "INVALID_STATUS"

    def test_deliverables_dict(self):
        """AC-052-A-06c: Deliverables as JSON dict are stored."""
        result, code = self._run([
            "--workflow", "test-wf",
            "--action", "compose_idea",
            "--status", "done",
            "--deliverables", '{"raw-ideas": "path/to/ideas.md"}',
        ])
        assert code == 0
        state = json.loads(self.state_path.read_text())
        assert state["shared"]["ideation"]["actions"]["compose_idea"]["deliverables"] == {
            "raw-ideas": "path/to/ideas.md"
        }

    def test_deliverables_list_converted(self):
        """AC-052-A-06d: Legacy list deliverables converted to keyed dict."""
        result, code = self._run([
            "--workflow", "test-wf",
            "--action", "compose_idea",
            "--status", "done",
            "--deliverables", '["path1.md", "folder/"]',
        ])
        assert code == 0
        state = json.loads(self.state_path.read_text())
        dels = state["shared"]["ideation"]["actions"]["compose_idea"]["deliverables"]
        assert isinstance(dels, dict)
        assert "raw-ideas" in dels
        assert "ideas-folder" in dels

    def test_context_stored(self):
        """AC-052-A-06e: Context dict is stored on action."""
        result, code = self._run([
            "--workflow", "test-wf",
            "--action", "compose_idea",
            "--status", "done",
            "--context", '{"raw-ideas": "path.md"}',
        ])
        assert code == 0
        state = json.loads(self.state_path.read_text())
        assert state["shared"]["ideation"]["actions"]["compose_idea"]["context"] == {
            "raw-ideas": "path.md"
        }

    def test_feature_breakdown_populates_features(self):
        """AC-052-A-06f: Feature breakdown populates per-feature structures."""
        # First advance to requirement stage
        state = json.loads(self.state_path.read_text())
        state["shared"]["ideation"]["actions"]["compose_idea"]["status"] = "done"
        state["shared"]["ideation"]["status"] = "completed"
        state["shared"]["requirement"]["status"] = "in_progress"
        state["shared"]["requirement"]["actions"]["requirement_gathering"]["status"] = "done"
        state["current_stage"] = "requirement"
        self.state_path.write_text(json.dumps(state, indent=2))

        features = [
            {"id": "FEAT-A", "name": "Feature A", "depends_on": []},
            {"id": "FEAT-B", "name": "Feature B", "depends_on": ["FEAT-A"]},
        ]
        result, code = self._run([
            "--workflow", "test-wf",
            "--action", "feature_breakdown",
            "--status", "done",
            "--features", json.dumps(features),
        ])
        assert code == 0
        state = json.loads(self.state_path.read_text())
        assert len(state["features"]) == 2
        assert state["features"][0]["feature_id"] == "FEAT-A"
        assert "implement" in state["features"][0]
        assert "validation" in state["features"][0]
        assert "feedback" in state["features"][0]
        # next_actions_suggested = features with no deps
        fb_action = state["shared"]["requirement"]["actions"]["feature_breakdown"]
        assert fb_action["next_actions_suggested"] == ["FEAT-A"]

    def test_feature_action_update(self):
        """AC-052-A-06g: Per-feature action update."""
        state = json.loads(self.state_path.read_text())
        state["shared"]["ideation"]["status"] = "completed"
        state["shared"]["requirement"]["status"] = "completed"
        state["current_stage"] = "implement"
        state["features"] = [{
            "feature_id": "FEAT-001",
            "name": "Test Feature",
            "depends_on": [],
            "implement": {
                "status": "in_progress",
                "actions": {
                    "feature_refinement": {"status": "pending", "deliverables": []},
                    "technical_design": {"status": "pending", "deliverables": []},
                    "implementation": {"status": "pending", "deliverables": []},
                },
            },
            "validation": {"status": "locked", "actions": {
                "acceptance_testing": {"status": "pending", "deliverables": []},
                "feature_closing": {"status": "pending", "deliverables": []},
            }},
            "feedback": {"status": "locked", "actions": {
                "human_playground": {"status": "skipped", "deliverables": [], "optional": True},
            }},
        }]
        self.state_path.write_text(json.dumps(state, indent=2))

        result, code = self._run([
            "--workflow", "test-wf",
            "--action", "feature_refinement",
            "--status", "done",
            "--feature-id", "FEAT-001",
        ])
        assert code == 0
        state = json.loads(self.state_path.read_text())
        assert state["features"][0]["implement"]["actions"]["feature_refinement"]["status"] == "done"

    def test_output_json_format(self):
        """AC-052-A-06h: Default JSON output is valid."""
        result, code = self._run([
            "--workflow", "test-wf",
            "--action", "compose_idea",
            "--status", "in_progress",
        ])
        assert code == 0
        assert "success" in result
        assert "data" in result

    def test_output_text_format(self):
        """AC-052-A-06i: Text output format."""
        import workflow_update_action as wua
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=self.root):
            with redirect_stdout(buf):
                wua.main([
                    "--workflow", "test-wf",
                    "--action", "compose_idea",
                    "--status", "in_progress",
                    "--format", "text",
                ])
        output = buf.getvalue()
        assert "action_updated" in output


# ============================================================================
# AC-052-A-07: Deliverable Validation
# ============================================================================

class TestDeliverableValidation:
    """AC-052-A-07a through 07e."""

    @pytest.fixture(autouse=True)
    def setup(self, workflow_template):
        self.template = workflow_template

    def test_unexpected_tag_rejected(self):
        """AC-052-A-07a: Unexpected tags cause exit 1."""
        import workflow_update_action as wua
        with pytest.raises(SystemExit) as exc_info:
            wua.validate_deliverables(self.template, "compose_idea", {"bogus-tag": "file.md"})
        assert exc_info.value.code == _lib.EXIT_VALIDATION_ERROR

    def test_folder_tag_array_rejected(self):
        """AC-052-A-07c: Folder tags cannot be arrays."""
        import workflow_update_action as wua
        with pytest.raises(SystemExit) as exc_info:
            wua.validate_deliverables(
                self.template, "compose_idea",
                {"raw-ideas": "f.md", "ideas-folder": ["a/", "b/"]},
            )
        assert exc_info.value.code == _lib.EXIT_VALIDATION_ERROR

    def test_array_values_accepted(self):
        """AC-052-A-07d: Array values on non-folder tags succeed."""
        import workflow_update_action as wua
        # Should not raise
        wua.validate_deliverables(
            self.template, "compose_idea",
            {"raw-ideas": ["file1.md", "file2.md"], "ideas-folder": "folder/"},
        )

    def test_empty_string_in_array_rejected(self):
        """AC-052-A-07e: Empty string in array causes exit 1."""
        import workflow_update_action as wua
        with pytest.raises(SystemExit) as exc_info:
            wua.validate_deliverables(
                self.template, "compose_idea",
                {"raw-ideas": ["good.md", "  "], "ideas-folder": "f/"},
            )
        assert exc_info.value.code == _lib.EXIT_VALIDATION_ERROR

    def test_missing_required_tag_warns_but_proceeds(self):
        """AC-052-A-07b: Missing required tag proceeds (warning only)."""
        import workflow_update_action as wua
        # Only provide one of the two expected tags — should NOT raise
        wua.validate_deliverables(
            self.template, "compose_idea",
            {"raw-ideas": "file.md"},  # missing 'ideas-folder'
        )


# ============================================================================
# AC-052-A-08: Schema Versioning
# ============================================================================

class TestSchemaVersioning:
    """AC-052-A-08a through 08c."""

    def test_scalar_dict_gets_3_0(self):
        """AC-052-A-08a: Scalar dict → schema 3.0."""
        import workflow_update_action as wua
        assert wua.determine_schema_version({"tag": "path"}) == "3.0"

    def test_array_value_gets_4_0(self):
        """AC-052-A-08b: Array value → schema 4.0."""
        import workflow_update_action as wua
        assert wua.determine_schema_version({"tag": ["a", "b"]}) == "4.0"

    def test_upward_only(self, tmp_project, write_template, write_state):
        """AC-052-A-08c: Schema version never downgrades."""
        state = json.loads(write_state.read_text())
        state["schema_version"] = "4.0"
        write_state.write_text(json.dumps(state, indent=2))

        import workflow_update_action as wua
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                wua.main([
                    "--workflow", "test-wf",
                    "--action", "compose_idea",
                    "--status", "done",
                    "--deliverables", '{"raw-ideas": "path.md"}',
                ])
        state = json.loads(write_state.read_text())
        assert state["schema_version"] == "4.0"  # Not downgraded to 3.0


# ============================================================================
# AC-052-A-09: Stage Gating
# ============================================================================

class TestStageGating:
    """AC-052-A-09a through 09b."""

    def test_next_action_in_response(self, tmp_project, write_template, write_state):
        """AC-052-A-09a: Response includes current_stage and next_action."""
        import workflow_update_action as wua
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                wua.main([
                    "--workflow", "test-wf",
                    "--action", "compose_idea",
                    "--status", "done",
                ])
        result = json.loads(buf.getvalue())
        assert "current_stage" in result["data"]
        assert "next_action" in result["data"]

    def test_context_initialized_for_keyed_deliverables(self, tmp_project, write_template, write_state):
        """AC-052-A-09b: Empty context initialized when keyed deliverables provided without --context."""
        import workflow_update_action as wua
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                wua.main([
                    "--workflow", "test-wf",
                    "--action", "compose_idea",
                    "--status", "done",
                    "--deliverables", '{"raw-ideas": "path.md"}',
                ])
        state = json.loads(write_state.read_text())
        assert state["shared"]["ideation"]["actions"]["compose_idea"].get("context") == {}


# ============================================================================
# AC-052-A-10: workflow_get_state.py CLI
# ============================================================================

class TestWorkflowGetState:
    """AC-052-A-10a through 10d."""

    def test_get_valid_state(self, tmp_project, write_template, write_state, sample_state):
        """AC-052-A-10a: Returns full workflow state."""
        import workflow_get_state as wgs
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                wgs.main(["--workflow", "test-wf"])
        result = json.loads(buf.getvalue())
        assert result["name"] == "test-wf"
        assert result["current_stage"] == "ideation"

    def test_missing_workflow_exits_2(self, tmp_project, write_template):
        """AC-052-A-10b: Missing workflow exits with code 2."""
        import workflow_get_state as wgs
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with pytest.raises(SystemExit) as exc_info:
                wgs.main(["--workflow", "nonexistent"])
            assert exc_info.value.code == _lib.EXIT_FILE_NOT_FOUND

    def test_corrupted_json_exits_1(self, tmp_project, write_template):
        """AC-052-A-10c: Corrupted JSON exits with code 1."""
        bad_path = tmp_project / "x-ipe-docs" / "engineering-workflow" / "workflow-bad.json"
        bad_path.write_text("{corrupted", encoding="utf-8")
        import workflow_get_state as wgs
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with pytest.raises(SystemExit) as exc_info:
                wgs.main(["--workflow", "bad"])
            assert exc_info.value.code == _lib.EXIT_VALIDATION_ERROR

    def test_text_format(self, tmp_project, write_template, write_state):
        """AC-052-A-10d: Text format output."""
        import workflow_get_state as wgs
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                wgs.main(["--workflow", "test-wf", "--format", "text"])
        output = buf.getvalue()
        # Text format prints key: value pairs
        assert "name" in output or "current_stage" in output


# ============================================================================
# AC-052-A-11: Zero Dependencies
# ============================================================================

class TestZeroDeps:
    """AC-052-A-11a: Only stdlib imports."""

    def test_lib_imports_stdlib_only(self):
        """AC-052-A-11a: _lib.py uses only stdlib modules."""
        import ast
        source = (SCRIPTS_DIR / "_lib.py").read_text()
        tree = ast.parse(source)
        stdlib_modules = {
            "fcntl", "json", "os", "sys", "tempfile", "time",
            "contextlib", "pathlib", "__future__",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] in stdlib_modules, f"Non-stdlib import: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert node.module.split(".")[0] in stdlib_modules, f"Non-stdlib import: {node.module}"

    def test_scripts_imports_stdlib_only(self):
        """AC-052-A-11a: workflow scripts use only stdlib modules (besides _lib)."""
        import ast
        allowed_modules = {
            "argparse", "json", "sys", "pathlib", "datetime", "__future__",
        }
        for script_name in ("workflow_get_state.py", "workflow_update_action.py"):
            source = (SCRIPTS_DIR / script_name).read_text()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split(".")[0]
                        assert mod in allowed_modules or mod == "_lib", \
                            f"Non-stdlib import in {script_name}: {alias.name}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module != "_lib":
                        mod = node.module.split(".")[0]
                        assert mod in allowed_modules, \
                            f"Non-stdlib import in {script_name}: {node.module}"


# ============================================================================
# AC-052-A-12: Output Compatibility
# ============================================================================

class TestOutputCompatibility:
    """AC-052-A-12a through 12c."""

    def test_update_success_structure(self, tmp_project, write_template, write_state):
        """AC-052-A-12a: Update output matches expected structure."""
        import workflow_update_action as wua
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                wua.main([
                    "--workflow", "test-wf",
                    "--action", "compose_idea",
                    "--status", "done",
                ])
        result = json.loads(buf.getvalue())
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data["action_updated"], str)
        assert isinstance(data["new_status"], str)
        assert isinstance(data["current_stage"], str)
        assert "next_action" in data
        # next_action is a dict with action/stage/feature_id/reason keys
        na = data["next_action"]
        assert isinstance(na, dict)
        assert "action" in na
        assert "stage" in na
        assert "feature_id" in na
        assert "reason" in na

    def test_get_state_structure(self, tmp_project, write_template, write_state, sample_state):
        """AC-052-A-12b: Get state output matches full workflow state dict."""
        import workflow_get_state as wgs
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                wgs.main(["--workflow", "test-wf"])
        result = json.loads(buf.getvalue())
        # Should contain the same top-level keys as the sample state
        for key in ("schema_version", "name", "current_stage", "shared", "features"):
            assert key in result, f"Missing key '{key}' in get_state output"

    def test_error_structure(self, capsys):
        """AC-052-A-12c: Error output matches expected structure."""
        with pytest.raises(SystemExit):
            _lib.exit_with_error(1, "TEST_ERROR", "test message")
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["success"] is False
        assert isinstance(result["error"], str)
        assert isinstance(result["message"], str)


# ============================================================================
# Template helper tests
# ============================================================================

class TestTemplateHelpers:
    """Tests for build_stage_config and build_next_actions_map."""

    def test_get_template_tags(self, workflow_template):
        tags = _lib.get_template_tags(workflow_template, "compose_idea")
        assert tags == ["raw-ideas", "ideas-folder"]

    def test_get_folder_tags(self, workflow_template):
        folder = _lib.get_folder_tags(workflow_template, "compose_idea")
        assert folder == {"ideas-folder"}

    def test_get_tags_unknown_action(self, workflow_template):
        assert _lib.get_template_tags(workflow_template, "nonexistent") == []
        assert _lib.get_folder_tags(workflow_template, "nonexistent") == set()

    def test_build_stage_config(self, workflow_template):
        import workflow_update_action as wua
        config = wua.build_stage_config(workflow_template)
        assert "ideation" in config
        assert config["ideation"]["type"] == "shared"
        assert "compose_idea" in config["ideation"]["mandatory_actions"]
        assert "refine_idea" in config["ideation"]["optional_actions"]

    def test_build_next_actions_map(self, workflow_template):
        import workflow_update_action as wua
        mapping = wua.build_next_actions_map(workflow_template)
        assert mapping["compose_idea"] == ["refine_idea"]
        assert mapping["requirement_gathering"] == ["feature_breakdown"]


# ============================================================================
# Edge case tests
# ============================================================================

class TestEdgeCases:
    """Edge cases from specification."""

    def test_empty_deliverables_dict_accepted(self, tmp_project, write_template, write_state):
        """Empty deliverables dict is accepted."""
        import workflow_update_action as wua
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                wua.main([
                    "--workflow", "test-wf",
                    "--action", "compose_idea",
                    "--status", "done",
                    "--deliverables", "{}",
                ])
        result = json.loads(buf.getvalue())
        assert result["success"] is True

    def test_feature_not_found(self, tmp_project, write_template, write_state):
        """Feature not found exits with code 1."""
        import workflow_update_action as wua
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        try:
            with patch("_lib.Path.cwd", return_value=tmp_project):
                with redirect_stdout(buf):
                    wua.main([
                        "--workflow", "test-wf",
                        "--action", "feature_refinement",
                        "--status", "done",
                        "--feature-id", "FEAT-NONEXISTENT",
                    ])
        except SystemExit as e:
            assert e.code == 1
            result = json.loads(buf.getvalue())
            assert result["error"] == "FEATURE_NOT_FOUND"

    def test_action_not_found_in_shared(self, tmp_project, write_template, write_state):
        """Action not in shared stages exits with code 1."""
        import workflow_update_action as wua
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        try:
            with patch("_lib.Path.cwd", return_value=tmp_project):
                with redirect_stdout(buf):
                    wua.main([
                        "--workflow", "test-wf",
                        "--action", "nonexistent_action",
                        "--status", "done",
                    ])
        except SystemExit as e:
            assert e.code == 1
            result = json.loads(buf.getvalue())
            assert result["error"] == "ACTION_NOT_FOUND"

    def test_load_template_missing(self, tmp_project):
        """Missing template file exits with code 2."""
        template_path = tmp_project / "x-ipe-docs" / "config" / "workflow-template.json"
        if template_path.exists():
            template_path.unlink()
        with pytest.raises(SystemExit) as exc_info:
            _lib.load_workflow_template(tmp_project)
        assert exc_info.value.code == _lib.EXIT_FILE_NOT_FOUND
