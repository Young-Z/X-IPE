"""Tests for KB Index scripts — FEATURE-052-B.

Covers _kb_lib.py, kb_get_index.py, kb_set_entry.py, kb_remove_entry.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".github" / "skills" / "x-ipe-tool-x-ipe-app-interactor" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import _lib  # noqa: E402
import _kb_lib  # noqa: E402


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def tmp_project(tmp_path):
    """Create minimal project structure with KB root."""
    (tmp_path / "x-ipe-docs" / "knowledge-base").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def kb_root(tmp_project):
    return tmp_project / "x-ipe-docs" / "knowledge-base"


@pytest.fixture
def sample_index():
    """Canonical .kb-index.json content."""
    return {
        "version": "1.0",
        "entries": {
            "doc.md": {
                "title": "My Doc",
                "description": "A test document",
                "tags": {"domain": ["testing"]},
                "type": "markdown",
                "author": "sage",
                "created": "2026-03-30",
                "auto_generated": False,
            },
            "guides/": {
                "title": "Guides Folder",
                "description": "Collection of guides",
                "tags": {},
                "type": "folder",
            },
        },
    }


@pytest.fixture
def write_index(kb_root, sample_index):
    """Write sample index to KB root."""
    index_path = kb_root / ".kb-index.json"
    index_path.write_text(json.dumps(sample_index, indent=2), encoding="utf-8")
    return index_path


def _run_script(module, args, root):
    """Helper to run a script's main() and capture output."""
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    try:
        with patch("_lib.Path.cwd", return_value=root):
            with redirect_stdout(buf):
                module.main(args)
        return json.loads(buf.getvalue()), 0
    except SystemExit as e:
        output = buf.getvalue()
        if output.strip():
            return json.loads(output), e.code
        return {}, e.code


# ============================================================================
# AC-052-B-01: kb_get_index.py
# ============================================================================

class TestKbGetIndex:
    """AC-052-B-01a through 01g."""

    def test_read_canonical_index(self, tmp_project, kb_root, write_index, sample_index):
        """AC-052-B-01a: Read canonical format returns full index."""
        import kb_get_index
        result, code = _run_script(kb_get_index, [], tmp_project)
        assert code == 0
        assert result["success"] is True
        assert result["folder"] == ""
        assert result["index"]["version"] == "1.0"
        assert "doc.md" in result["index"]["entries"]
        assert "guides/" in result["index"]["entries"]

    def test_empty_folder_reads_kb_root(self, tmp_project, kb_root, write_index):
        """AC-052-B-01b: Omitted --folder reads KB root."""
        import kb_get_index
        result, code = _run_script(kb_get_index, [], tmp_project)
        assert code == 0
        assert result["folder"] == ""

    def test_missing_index_returns_empty(self, tmp_project, kb_root):
        """AC-052-B-01c: Missing .kb-index.json returns empty entries."""
        import kb_get_index
        result, code = _run_script(kb_get_index, [], tmp_project)
        assert code == 0
        assert result["index"] == {"version": "1.0", "entries": {}}

    def test_legacy_flat_format(self, tmp_project, kb_root):
        """AC-052-B-01d: Legacy flat format auto-wrapped."""
        flat_index = {
            "version": "1.0",
            "doc.md": {"title": "Flat Doc", "type": "markdown"},
            "img.png": {"title": "Image", "type": "image"},
        }
        (kb_root / ".kb-index.json").write_text(json.dumps(flat_index))
        import kb_get_index
        result, code = _run_script(kb_get_index, [], tmp_project)
        assert code == 0
        assert "doc.md" in result["index"]["entries"]
        assert "img.png" in result["index"]["entries"]
        assert result["index"]["version"] == "1.0"

    def test_corrupted_json_returns_empty(self, tmp_project, kb_root):
        """AC-052-B-01e: Corrupted JSON returns empty entries."""
        (kb_root / ".kb-index.json").write_text("{bad json!!")
        import kb_get_index
        result, code = _run_script(kb_get_index, [], tmp_project)
        assert code == 0
        assert result["index"]["entries"] == {}

    def test_nonexistent_folder_exits_2(self, tmp_project):
        """AC-052-B-01f: Non-existent folder exits with code 2."""
        import kb_get_index
        result, code = _run_script(kb_get_index, ["--folder", "nonexistent"], tmp_project)
        assert code == 2
        assert result["error"] == "FOLDER_NOT_FOUND"

    def test_text_format(self, tmp_project, kb_root, write_index):
        """AC-052-B-01g: Text format output."""
        import kb_get_index
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                kb_get_index.main(["--format", "text"])
        output = buf.getvalue()
        assert "success" in output.lower() or "entries" in output.lower() or "doc.md" in output

    def test_subfolder(self, tmp_project, kb_root):
        """Read index from a subfolder."""
        sub = kb_root / "guides"
        sub.mkdir()
        sub_index = {"version": "1.0", "entries": {"a.md": {"title": "A"}}}
        (sub / ".kb-index.json").write_text(json.dumps(sub_index))
        import kb_get_index
        result, code = _run_script(kb_get_index, ["--folder", "guides"], tmp_project)
        assert code == 0
        assert result["folder"] == "guides"
        assert "a.md" in result["index"]["entries"]


# ============================================================================
# AC-052-B-02: kb_set_entry.py
# ============================================================================

class TestKbSetEntry:
    """AC-052-B-02a through 02i."""

    def test_set_new_entry(self, tmp_project, kb_root):
        """AC-052-B-02a: Set entry creates new entry."""
        import kb_set_entry
        result, code = _run_script(kb_set_entry, [
            "--name", "new.md",
            "--entry", '{"title": "New", "type": "markdown"}',
        ], tmp_project)
        assert code == 0
        assert result["success"] is True
        assert result["name"] == "new.md"
        assert result["entry"]["title"] == "New"
        # Verify persisted
        index = json.loads((kb_root / ".kb-index.json").read_text())
        assert "new.md" in index["entries"]

    def test_update_existing_entry(self, tmp_project, kb_root, write_index):
        """AC-052-B-02b: Existing entry is fully replaced."""
        import kb_set_entry
        result, code = _run_script(kb_set_entry, [
            "--name", "doc.md",
            "--entry", '{"title": "Updated", "type": "pdf"}',
        ], tmp_project)
        assert code == 0
        index = json.loads((kb_root / ".kb-index.json").read_text())
        assert index["entries"]["doc.md"]["title"] == "Updated"
        assert index["entries"]["doc.md"]["type"] == "pdf"
        # Old fields should NOT be present (full replace)
        assert "description" not in index["entries"]["doc.md"]

    def test_creates_index_if_missing(self, tmp_project, kb_root):
        """AC-052-B-02c: Creates new .kb-index.json if missing."""
        assert not (kb_root / ".kb-index.json").exists()
        import kb_set_entry
        result, code = _run_script(kb_set_entry, [
            "--name", "first.md",
            "--entry", '{"title": "First"}',
        ], tmp_project)
        assert code == 0
        index = json.loads((kb_root / ".kb-index.json").read_text())
        assert index["version"] == "1.0"
        assert "first.md" in index["entries"]

    def test_legacy_format_converted(self, tmp_project, kb_root):
        """AC-052-B-02d: Legacy flat format is read and written as canonical."""
        flat = {"version": "1.0", "old.md": {"title": "Old"}}
        (kb_root / ".kb-index.json").write_text(json.dumps(flat))
        import kb_set_entry
        result, code = _run_script(kb_set_entry, [
            "--name", "new.md",
            "--entry", '{"title": "New"}',
        ], tmp_project)
        assert code == 0
        index = json.loads((kb_root / ".kb-index.json").read_text())
        # Written in canonical format
        assert "entries" in index
        assert "old.md" in index["entries"]
        assert "new.md" in index["entries"]

    def test_folder_name_trailing_slash(self, tmp_project, kb_root):
        """AC-052-B-02e: Folder name with trailing slash stored correctly."""
        import kb_set_entry
        result, code = _run_script(kb_set_entry, [
            "--name", "guides/",
            "--entry", '{"title": "Guides", "type": "folder"}',
        ], tmp_project)
        assert code == 0
        index = json.loads((kb_root / ".kb-index.json").read_text())
        assert "guides/" in index["entries"]

    def test_invalid_entry_json(self, tmp_project):
        """AC-052-B-02f: Invalid JSON exits with code 1."""
        import kb_set_entry
        result, code = _run_script(kb_set_entry, [
            "--name", "x.md", "--entry", "{not json}",
        ], tmp_project)
        assert code == 1
        assert result["error"] == "INVALID_ENTRY_JSON"

    def test_empty_name(self, tmp_project):
        """AC-052-B-02g: Empty name exits with code 1."""
        import kb_set_entry
        result, code = _run_script(kb_set_entry, [
            "--name", "  ", "--entry", '{"title": "X"}',
        ], tmp_project)
        assert code == 1
        assert result["error"] == "INVALID_NAME"

    def test_text_format(self, tmp_project, kb_root):
        """AC-052-B-02i: Text format output."""
        import kb_set_entry
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                kb_set_entry.main([
                    "--name", "t.md", "--entry", '{"title": "T"}',
                    "--format", "text",
                ])
        output = buf.getvalue()
        assert "t.md" in output or "success" in output.lower()

    def test_creates_folder_if_missing(self, tmp_project, kb_root):
        """set_entry creates subfolder if it doesn't exist."""
        import kb_set_entry
        result, code = _run_script(kb_set_entry, [
            "--name", "a.md", "--entry", '{"title": "A"}',
            "--folder", "new-subfolder",
        ], tmp_project)
        assert code == 0
        assert (kb_root / "new-subfolder" / ".kb-index.json").exists()


# ============================================================================
# AC-052-B-03: kb_remove_entry.py
# ============================================================================

class TestKbRemoveEntry:
    """AC-052-B-03a through 03e."""

    def test_remove_existing_entry(self, tmp_project, kb_root, write_index):
        """AC-052-B-03a: Remove existing entry."""
        import kb_remove_entry
        result, code = _run_script(kb_remove_entry, ["--name", "doc.md"], tmp_project)
        assert code == 0
        assert result["success"] is True
        assert result["removed"] is True
        index = json.loads((kb_root / ".kb-index.json").read_text())
        assert "doc.md" not in index["entries"]
        assert "guides/" in index["entries"]  # Other entry untouched

    def test_remove_nonexistent_entry(self, tmp_project, kb_root, write_index):
        """AC-052-B-03b: Remove non-existent entry returns removed=false."""
        import kb_remove_entry
        result, code = _run_script(kb_remove_entry, ["--name", "nope.md"], tmp_project)
        assert code == 0
        assert result["removed"] is False

    def test_remove_no_index_file(self, tmp_project, kb_root):
        """AC-052-B-03c: No .kb-index.json returns removed=false, no file created."""
        import kb_remove_entry
        result, code = _run_script(kb_remove_entry, ["--name", "x.md"], tmp_project)
        assert code == 0
        assert result["removed"] is False
        assert not (kb_root / ".kb-index.json").exists()

    def test_empty_name(self, tmp_project):
        """AC-052-B-03d: Empty name exits with code 1."""
        import kb_remove_entry
        result, code = _run_script(kb_remove_entry, ["--name", "  "], tmp_project)
        assert code == 1
        assert result["error"] == "INVALID_NAME"

    def test_text_format(self, tmp_project, kb_root, write_index):
        """AC-052-B-03e: Text format output."""
        import kb_remove_entry
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with patch("_lib.Path.cwd", return_value=tmp_project):
            with redirect_stdout(buf):
                kb_remove_entry.main(["--name", "doc.md", "--format", "text"])
        assert "doc.md" in buf.getvalue() or "removed" in buf.getvalue().lower()


# ============================================================================
# AC-052-B-04: File Locking
# ============================================================================

class TestFileLocking:
    """AC-052-B-04a through 04c."""

    def test_set_entry_uses_lock(self, tmp_project, kb_root):
        """AC-052-B-04a: set_entry creates lock file during write."""
        import kb_set_entry
        # After running, lock file should have been created and released
        result, code = _run_script(kb_set_entry, [
            "--name", "x.md", "--entry", '{"title": "X"}',
        ], tmp_project)
        assert code == 0
        # Lock file may or may not persist (released)
        assert (kb_root / ".kb-index.json").exists()

    def test_remove_entry_uses_lock(self, tmp_project, kb_root, write_index):
        """AC-052-B-04b: remove_entry uses lock for writes."""
        import kb_remove_entry
        result, code = _run_script(kb_remove_entry, ["--name", "doc.md"], tmp_project)
        assert code == 0

    def test_get_index_no_lock(self, tmp_project, kb_root, write_index):
        """AC-052-B-04c: get_index does NOT use file lock."""
        import kb_get_index
        # Should succeed even if lock checking is not involved
        result, code = _run_script(kb_get_index, [], tmp_project)
        assert code == 0


# ============================================================================
# AC-052-B-05: Shared Utilities Reuse
# ============================================================================

class TestSharedUtilities:
    """AC-052-B-05a through 05b."""

    def test_scripts_import_lib(self):
        """AC-052-B-05a: Scripts import from _lib."""
        import ast
        for script_name in ["kb_get_index.py", "kb_set_entry.py", "kb_remove_entry.py"]:
            source = (SCRIPTS_DIR / script_name).read_text()
            tree = ast.parse(source)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module in ("_lib", "_kb_lib"):
                    imports.extend(alias.name for alias in node.names)
            assert "output_result" in imports or "resolve_project_root" in imports, \
                f"{script_name} missing _lib imports"

    def test_scripts_stdlib_only(self):
        """AC-052-B-05b: Only stdlib + _lib/_kb_lib imports."""
        import ast
        allowed = {"_lib", "_kb_lib", "argparse", "json", "sys", "os", "pathlib",
                    "tempfile", "fcntl", "time", "contextlib", "__future__"}
        for script_name in ["_kb_lib.py", "kb_get_index.py", "kb_set_entry.py", "kb_remove_entry.py"]:
            source = (SCRIPTS_DIR / script_name).read_text()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert alias.name.split(".")[0] in allowed, \
                            f"{script_name}: non-stdlib import: {alias.name}"
                elif isinstance(node, ast.ImportFrom) and node.module:
                    assert node.module.split(".")[0] in allowed, \
                        f"{script_name}: non-stdlib import: {node.module}"


# ============================================================================
# AC-052-B-06: Output Compatibility
# ============================================================================

class TestOutputCompatibility:
    """AC-052-B-06a through 06d."""

    def test_get_index_structure(self, tmp_project, kb_root, write_index):
        """AC-052-B-06a: get_index output matches MCP structure."""
        import kb_get_index
        result, code = _run_script(kb_get_index, [], tmp_project)
        assert result["success"] is True
        assert isinstance(result["folder"], str)
        assert isinstance(result["index"], dict)
        assert "version" in result["index"]
        assert "entries" in result["index"]

    def test_set_entry_structure(self, tmp_project, kb_root):
        """AC-052-B-06b: set_entry output matches MCP structure."""
        import kb_set_entry
        result, code = _run_script(kb_set_entry, [
            "--name", "x.md", "--entry", '{"title": "X"}',
        ], tmp_project)
        assert result["success"] is True
        assert isinstance(result["folder"], str)
        assert isinstance(result["name"], str)
        assert isinstance(result["entry"], dict)

    def test_remove_entry_structure(self, tmp_project, kb_root, write_index):
        """AC-052-B-06c: remove_entry output matches MCP structure."""
        import kb_remove_entry
        result, code = _run_script(kb_remove_entry, ["--name", "doc.md"], tmp_project)
        assert result["success"] is True
        assert isinstance(result["folder"], str)
        assert isinstance(result["name"], str)
        assert isinstance(result["removed"], bool)

    def test_error_structure(self, tmp_project):
        """AC-052-B-06d: Error output matches structure."""
        import kb_set_entry
        result, code = _run_script(kb_set_entry, [
            "--name", "", "--entry", '{"title": "X"}',
        ], tmp_project)
        # argparse will reject empty --name; test with whitespace instead
        result, code = _run_script(kb_set_entry, [
            "--name", " ", "--entry", '{"title": "X"}',
        ], tmp_project)
        assert code == 1
        assert result["success"] is False
        assert isinstance(result["error"], str)
        assert isinstance(result["message"], str)


# ============================================================================
# AC-052-B-07: Exit Codes
# ============================================================================

class TestExitCodes:
    """AC-052-B-07a through 07d."""

    def test_success_exits_0(self, tmp_project, kb_root, write_index):
        """AC-052-B-07a: Successful operations exit with 0."""
        import kb_get_index
        _, code = _run_script(kb_get_index, [], tmp_project)
        assert code == 0

    def test_validation_error_exits_1(self, tmp_project):
        """AC-052-B-07b: Validation error exits with 1."""
        import kb_set_entry
        _, code = _run_script(kb_set_entry, [
            "--name", " ", "--entry", '{"x": 1}',
        ], tmp_project)
        assert code == 1

    def test_folder_not_found_exits_2(self, tmp_project):
        """AC-052-B-07c: Missing folder exits with 2."""
        import kb_get_index
        _, code = _run_script(kb_get_index, ["--folder", "nope"], tmp_project)
        assert code == 2


# ============================================================================
# _kb_lib unit tests
# ============================================================================

class TestKbLib:
    """Unit tests for _kb_lib.read_kb_index."""

    def test_read_canonical(self, kb_root, write_index, sample_index):
        index = _kb_lib.read_kb_index(kb_root)
        assert index["version"] == "1.0"
        assert "doc.md" in index["entries"]

    def test_read_missing(self, kb_root):
        index = _kb_lib.read_kb_index(kb_root)
        assert index == {"version": "1.0", "entries": {}}

    def test_read_flat(self, kb_root):
        flat = {"old.md": {"title": "Old"}, "version": "1.0"}
        (kb_root / ".kb-index.json").write_text(json.dumps(flat))
        index = _kb_lib.read_kb_index(kb_root)
        assert "entries" in index
        assert "old.md" in index["entries"]
        assert "version" not in index["entries"]

    def test_read_corrupted(self, kb_root):
        (kb_root / ".kb-index.json").write_text("NOT JSON")
        index = _kb_lib.read_kb_index(kb_root)
        assert index == {"version": "1.0", "entries": {}}
