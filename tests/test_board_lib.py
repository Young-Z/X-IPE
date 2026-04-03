"""Tests for _board_lib.py — Board Shared Library (FEATURE-055-A).

Covers: atomic JSON I/O, file locking, schema validation, path resolution,
structured output, exit codes, and stdlib-only constraint.
"""

from __future__ import annotations

import ast
import fcntl
import json
import os
import sys
import threading
import time
from pathlib import Path
from unittest import mock

import pytest

# ---------------------------------------------------------------------------
# Import _board_lib from skill scripts folder
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = str(
    Path(__file__).resolve().parent.parent
    / ".github" / "skills" / "x-ipe-tool-task-board-manager" / "scripts"
)
sys.path.insert(0, _SCRIPTS_DIR)

import _board_lib  # noqa: E402
from _board_lib import (
    EXIT_FILE_NOT_FOUND,
    EXIT_LOCK_TIMEOUT,
    EXIT_SUCCESS,
    EXIT_VALIDATION_ERROR,
    FEATURE_SCHEMA_V1,
    INDEX_SCHEMA_V1,
    TASK_SCHEMA_V1,
    atomic_read_json,
    atomic_write_json,
    exit_with_error,
    output_result,
    resolve_data_path,
    validate_schema,
    with_file_lock,
)


# ===================================================================
# AC-055A-01: Atomic JSON Read
# ===================================================================

class TestAtomicReadJson:
    """AC-055A-01: atomic_read_json()"""

    def test_read_valid_json(self, tmp_path: Path):
        """AC-055A-01a: Valid JSON file returns parsed dict."""
        data = {"key": "value", "num": 42}
        f = tmp_path / "valid.json"
        f.write_text(json.dumps(data), encoding="utf-8")

        result = atomic_read_json(f)
        assert result["success"] is True
        assert result["data"] == data

    def test_read_valid_list(self, tmp_path: Path):
        """AC-055A-01a: Valid JSON list also works."""
        data = [1, 2, 3]
        f = tmp_path / "list.json"
        f.write_text(json.dumps(data), encoding="utf-8")

        result = atomic_read_json(f)
        assert result["success"] is True
        assert result["data"] == data

    def test_read_missing_file(self, tmp_path: Path):
        """AC-055A-01b: Missing file returns error dict."""
        result = atomic_read_json(tmp_path / "nonexistent.json")
        assert result["success"] is False
        assert result["error"] == "FILE_NOT_FOUND"

    def test_read_invalid_json(self, tmp_path: Path):
        """AC-055A-01c: Invalid JSON returns error dict."""
        f = tmp_path / "bad.json"
        f.write_text("{not valid json!!!", encoding="utf-8")

        result = atomic_read_json(f)
        assert result["success"] is False
        assert result["error"] == "JSON_PARSE_ERROR"

    def test_read_empty_file(self, tmp_path: Path):
        """AC-055A-01d: Empty file returns error dict."""
        f = tmp_path / "empty.json"
        f.write_text("", encoding="utf-8")

        result = atomic_read_json(f)
        assert result["success"] is False
        assert result["error"] == "JSON_PARSE_ERROR"
        assert "empty" in result["message"].lower()

    def test_read_whitespace_only(self, tmp_path: Path):
        """AC-055A-01d: Whitespace-only file treated as empty."""
        f = tmp_path / "ws.json"
        f.write_text("   \n  ", encoding="utf-8")

        result = atomic_read_json(f)
        assert result["success"] is False
        assert result["error"] == "JSON_PARSE_ERROR"

    def test_read_accepts_string_path(self, tmp_path: Path):
        """atomic_read_json accepts str path, not just Path."""
        f = tmp_path / "str.json"
        f.write_text('{"ok": true}', encoding="utf-8")

        result = atomic_read_json(str(f))
        assert result["success"] is True


# ===================================================================
# AC-055A-02: Atomic JSON Write
# ===================================================================

class TestAtomicWriteJson:
    """AC-055A-02: atomic_write_json()"""

    def test_write_creates_file(self, tmp_path: Path):
        """AC-055A-02a: Basic write creates file with correct content."""
        f = tmp_path / "out.json"
        data = {"hello": "world"}
        atomic_write_json(f, data)

        assert f.exists()
        assert json.loads(f.read_text(encoding="utf-8")) == data

    def test_write_indent_2(self, tmp_path: Path):
        """AC-055A-02d: Output uses indent=2 for git-friendly diffs."""
        f = tmp_path / "indented.json"
        atomic_write_json(f, {"a": 1, "b": [2, 3]})

        text = f.read_text(encoding="utf-8")
        expected = json.dumps({"a": 1, "b": [2, 3]}, indent=2, ensure_ascii=False) + "\n"
        assert text == expected

    def test_write_creates_parent_dirs(self, tmp_path: Path):
        """AC-055A-02b: Creates parent directories if missing."""
        f = tmp_path / "deep" / "nested" / "dir" / "file.json"
        atomic_write_json(f, {"nested": True})

        assert f.exists()
        assert json.loads(f.read_text(encoding="utf-8")) == {"nested": True}

    def test_write_overwrites_existing(self, tmp_path: Path):
        """Overwrite existing file atomically."""
        f = tmp_path / "overwrite.json"
        f.write_text('{"old": true}', encoding="utf-8")

        atomic_write_json(f, {"new": True})
        assert json.loads(f.read_text(encoding="utf-8")) == {"new": True}

    def test_write_temp_cleanup_on_error(self, tmp_path: Path):
        """AC-055A-02c: Temp file cleaned up on write failure."""
        f = tmp_path / "fail.json"
        f.write_text('{"original": true}', encoding="utf-8")

        # Force an error by making data non-serializable
        class BadObj:
            pass

        with pytest.raises(TypeError):
            atomic_write_json(f, {"bad": BadObj()})

        # Original file should be unchanged
        assert json.loads(f.read_text(encoding="utf-8")) == {"original": True}

        # No .tmp files should remain
        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0

    def test_write_accepts_string_path(self, tmp_path: Path):
        """atomic_write_json accepts str path."""
        f = tmp_path / "str_path.json"
        atomic_write_json(str(f), {"str": True})
        assert f.exists()

    def test_write_trailing_newline(self, tmp_path: Path):
        """Output ends with newline for git friendliness."""
        f = tmp_path / "newline.json"
        atomic_write_json(f, {"a": 1})
        assert f.read_text(encoding="utf-8").endswith("\n")


# ===================================================================
# AC-055A-03: File Locking
# ===================================================================

class TestFileLocking:
    """AC-055A-03: with_file_lock()"""

    def test_lock_acquire_and_release(self, tmp_path: Path):
        """AC-055A-03a: Lock acquired, body executes, lock released."""
        lock_file = tmp_path / "test.lock"
        executed = False

        with with_file_lock(lock_file):
            executed = True
            assert lock_file.exists()

        assert executed

    def test_lock_default_timeout(self):
        """AC-055A-03c: Default timeout is 10 seconds."""
        import inspect
        sig = inspect.signature(with_file_lock)
        assert sig.parameters["timeout"].default == 10

    def test_lock_released_on_exception(self, tmp_path: Path):
        """AC-055A-03d: Lock released when body raises exception."""
        lock_file = tmp_path / "exc.lock"

        with pytest.raises(ValueError, match="test error"):
            with with_file_lock(lock_file):
                raise ValueError("test error")

        # Lock should be released — we can acquire it again immediately
        with with_file_lock(lock_file, timeout=1):
            pass  # Should not hang

    def test_lock_file_created(self, tmp_path: Path):
        """AC-055A-03e: Lock file created with O_CREAT if missing."""
        lock_file = tmp_path / "new.lock"
        assert not lock_file.exists()

        with with_file_lock(lock_file):
            assert lock_file.exists()

    def test_lock_timeout_exits(self, tmp_path: Path):
        """AC-055A-03b: Timeout exits with code 3."""
        lock_file = tmp_path / "held.lock"

        # Hold lock in another thread
        barrier = threading.Barrier(2, timeout=5)
        hold = threading.Event()

        def hold_lock():
            fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR)
            fcntl.flock(fd, fcntl.LOCK_EX)
            barrier.wait()
            hold.wait(timeout=5)
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

        t = threading.Thread(target=hold_lock, daemon=True)
        t.start()
        barrier.wait()

        try:
            with pytest.raises(SystemExit) as exc_info:
                with with_file_lock(lock_file, timeout=1):
                    pass  # Should never reach here
            assert exc_info.value.code == EXIT_LOCK_TIMEOUT
        finally:
            hold.set()
            t.join(timeout=3)

    def test_lock_creates_parent_dirs(self, tmp_path: Path):
        """Lock creates parent directories if missing."""
        lock_file = tmp_path / "deep" / "nested" / "test.lock"
        with with_file_lock(lock_file):
            assert lock_file.exists()

    def test_lock_cleanup_removes_file(self, tmp_path: Path):
        """cleanup=True removes lock file after release."""
        lock_file = tmp_path / "cleanup.lock"
        with with_file_lock(lock_file, cleanup=True):
            assert lock_file.exists()
        assert not lock_file.exists()


# ===================================================================
# AC-055A-04: Schema Validation
# ===================================================================

class TestSchemaValidation:
    """AC-055A-04: validate_schema()"""

    SIMPLE_SCHEMA = {
        "_version": "1.0",
        "name":  {"type": str,  "required": True},
        "age":   {"type": int,  "required": True},
        "email": {"type": str,  "required": False},
    }

    def test_valid_data(self):
        """AC-055A-04a: Conforming data returns success."""
        data = {"name": "Alice", "age": 30, "email": "a@b.com"}
        result = validate_schema(data, self.SIMPLE_SCHEMA)
        assert result["success"] is True

    def test_valid_data_optional_missing(self):
        """AC-055A-04a: Optional field can be omitted."""
        data = {"name": "Bob", "age": 25}
        result = validate_schema(data, self.SIMPLE_SCHEMA)
        assert result["success"] is True

    def test_missing_required_field(self):
        """AC-055A-04b: Missing required field returns error."""
        data = {"name": "Charlie"}
        result = validate_schema(data, self.SIMPLE_SCHEMA)
        assert result["success"] is False
        assert "Missing required field: age" in result["error"]

    def test_wrong_type(self):
        """AC-055A-04c: Wrong type returns error."""
        data = {"name": "Dave", "age": "not a number"}
        result = validate_schema(data, self.SIMPLE_SCHEMA)
        assert result["success"] is False
        assert "age" in result["error"]
        assert "int" in result["error"]
        assert "str" in result["error"]

    def test_unknown_field_rejected(self):
        """AC-055A-04d: Extra field rejected in strict mode."""
        data = {"name": "Eve", "age": 28, "extra": "bad"}
        result = validate_schema(data, self.SIMPLE_SCHEMA)
        assert result["success"] is False
        assert "Unknown field: extra" in result["error"]

    def test_non_dict_input(self):
        """AC-055A-04e: Non-dict input returns error."""
        result = validate_schema([1, 2, 3], self.SIMPLE_SCHEMA)
        assert result["success"] is False
        assert "dict" in result["error"].lower()

        result2 = validate_schema("string", self.SIMPLE_SCHEMA)
        assert result2["success"] is False

    def test_metadata_keys_ignored(self):
        """Keys starting with _ are metadata, not fields."""
        data = {"name": "Frank", "age": 40}
        result = validate_schema(data, self.SIMPLE_SCHEMA)
        assert result["success"] is True
        # _version is in schema but not required in data


# ===================================================================
# AC-055A-05: Schema Definitions
# ===================================================================

class TestSchemaDefinitions:
    """AC-055A-05: Schema constants"""

    def test_task_schema_fields(self):
        """AC-055A-05a: TASK_SCHEMA_V1 has all required fields."""
        expected_fields = {
            "task_id", "task_type", "description", "role", "status",
            "created_at", "last_updated", "output_links", "next_task",
        }
        actual_fields = {k for k in TASK_SCHEMA_V1 if not k.startswith("_")}
        assert actual_fields == expected_fields

    def test_task_schema_types(self):
        """AC-055A-05a: Field types are correct."""
        assert TASK_SCHEMA_V1["task_id"]["type"] is str
        assert TASK_SCHEMA_V1["output_links"]["type"] is list

    def test_feature_schema_fields(self):
        """AC-055A-05b: FEATURE_SCHEMA_V1 has all required fields."""
        expected_fields = {
            "feature_id", "epic_id", "title", "version", "status",
            "description", "dependencies", "specification_link",
            "created_at", "last_updated",
        }
        actual_fields = {k for k in FEATURE_SCHEMA_V1 if not k.startswith("_")}
        assert actual_fields == expected_fields

    def test_feature_schema_types(self):
        """AC-055A-05b: Feature schema types correct."""
        assert FEATURE_SCHEMA_V1["dependencies"]["type"] is list
        assert FEATURE_SCHEMA_V1["description"]["required"] is False

    def test_schema_version_key(self):
        """AC-055A-05c: All schemas have _version key."""
        assert TASK_SCHEMA_V1["_version"] == "1.0"
        assert FEATURE_SCHEMA_V1["_version"] == "1.0"
        assert INDEX_SCHEMA_V1["_version"] == "1.0"

    def test_index_schema_fields(self):
        """AC-055A-05d: INDEX_SCHEMA_V1 has version and entries."""
        assert "version" in INDEX_SCHEMA_V1
        assert "entries" in INDEX_SCHEMA_V1
        assert INDEX_SCHEMA_V1["entries"]["type"] is dict

    def test_task_schema_validates_sample(self):
        """AC-055A-05a: Sample task data passes validation."""
        sample = {
            "task_id": "TASK-1000",
            "task_type": "Ideation",
            "description": "Test task",
            "role": "Drift",
            "status": "in_progress",
            "created_at": "2026-04-03T10:00:00Z",
            "last_updated": "2026-04-03T10:30:00Z",
            "output_links": [],
            "next_task": "x-ipe-task-based-requirement-gathering",
        }
        assert validate_schema(sample, TASK_SCHEMA_V1)["success"] is True


# ===================================================================
# AC-055A-06: Path Resolution
# ===================================================================

class TestPathResolution:
    """AC-055A-06: resolve_data_path()"""

    def test_tasks_path(self):
        """AC-055A-06a: 'tasks' resolves to planning/tasks/."""
        result = resolve_data_path("tasks")
        assert result.name == "tasks"
        assert "x-ipe-docs/planning/tasks" in str(result)

    def test_features_path(self):
        """AC-055A-06b: 'features' resolves to planning/features/."""
        result = resolve_data_path("features")
        assert result.name == "features"
        assert "x-ipe-docs/planning/features" in str(result)

    def test_unknown_type_raises(self):
        """AC-055A-06c: Unknown data_type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown data_type"):
            resolve_data_path("unknown")

    def test_returns_absolute_path(self):
        """AC-055A-06d: Returns absolute path using project root detection."""
        result = resolve_data_path("tasks")
        assert result.is_absolute()

    def test_project_root_contains_marker(self):
        """AC-055A-06d: Project root contains x-ipe-docs/ marker."""
        result = resolve_data_path("tasks")
        project_root = result.parent.parent.parent
        assert (project_root / "x-ipe-docs").is_dir()


# ===================================================================
# AC-055A-07: Structured Output & Exit Codes
# ===================================================================

class TestStructuredOutput:
    """AC-055A-07: output_result(), exit_with_error(), exit codes"""

    def test_output_result_stdout(self, capsys: pytest.CaptureFixture):
        """AC-055A-07a: output_result prints JSON to stdout."""
        output_result({"success": True, "data": {"task_id": "TASK-1"}})
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["success"] is True
        assert parsed["data"]["task_id"] == "TASK-1"

    def test_output_result_valid_json(self, capsys: pytest.CaptureFixture):
        """AC-055A-07d: Output is valid JSON."""
        output_result({"success": True, "data": {"emoji": "🚀"}})
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["data"]["emoji"] == "🚀"

    def test_exit_with_error_stderr(self):
        """AC-055A-07b: exit_with_error prints to stderr and exits."""
        with pytest.raises(SystemExit) as exc_info:
            exit_with_error(EXIT_VALIDATION_ERROR, "TEST_ERROR", "test msg")
        assert exc_info.value.code == EXIT_VALIDATION_ERROR

    def test_exit_with_error_json_output(self, capsys: pytest.CaptureFixture):
        """AC-055A-07b: Error output is valid JSON on stderr."""
        with pytest.raises(SystemExit):
            exit_with_error(EXIT_FILE_NOT_FOUND, "NOT_FOUND", "missing")
        captured = capsys.readouterr()
        parsed = json.loads(captured.err)
        assert parsed["success"] is False
        assert parsed["error"] == "NOT_FOUND"
        assert parsed["message"] == "missing"

    def test_exit_code_constants(self):
        """AC-055A-07c: Exit code constants have correct values."""
        assert EXIT_SUCCESS == 0
        assert EXIT_VALIDATION_ERROR == 1
        assert EXIT_FILE_NOT_FOUND == 2
        assert EXIT_LOCK_TIMEOUT == 3


# ===================================================================
# AC-055A-08: Stdlib-Only Constraint
# ===================================================================

class TestStdlibConstraint:
    """AC-055A-08: No third-party imports"""

    STDLIB_MODULES = {
        "json", "os", "sys", "time", "fcntl", "tempfile", "pathlib",
        "contextlib", "typing", "__future__",
    }

    def test_only_stdlib_imports(self):
        """AC-055A-08a: All imports are from stdlib."""
        source_path = Path(_SCRIPTS_DIR) / "_board_lib.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_modules.add(node.module.split(".")[0])

        non_stdlib = imported_modules - self.STDLIB_MODULES
        assert non_stdlib == set(), f"Non-stdlib imports found: {non_stdlib}"

    def test_module_loads_without_third_party(self):
        """AC-055A-08b: Module imports successfully (integration)."""
        # If we got here, the import at the top of this file succeeded
        assert hasattr(_board_lib, "atomic_read_json")
        assert hasattr(_board_lib, "atomic_write_json")
        assert hasattr(_board_lib, "with_file_lock")
        assert hasattr(_board_lib, "validate_schema")
        assert hasattr(_board_lib, "resolve_data_path")
        assert hasattr(_board_lib, "output_result")
        assert hasattr(_board_lib, "exit_with_error")
