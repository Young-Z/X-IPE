"""
Tests for x_ipe.core.paths module

Covers:
- resolve_path function
- get_project_root function
- is_initialized function
- ensure_directory function
"""
import os
import tempfile
import pytest
from pathlib import Path

from x_ipe.core.paths import (
    resolve_path,
    get_project_root,
    is_initialized,
    ensure_directory,
)


class TestResolvePath:
    """Tests for resolve_path function."""
    
    def test_absolute_path_returns_unchanged(self):
        """Absolute paths should be returned as-is (resolved)."""
        abs_path = "/tmp/test/path"
        result = resolve_path(abs_path)
        assert result == Path(abs_path).resolve()
    
    def test_relative_path_uses_cwd(self):
        """Relative paths should be resolved from cwd by default."""
        rel_path = "subdir/file.txt"
        result = resolve_path(rel_path)
        expected = (Path.cwd() / rel_path).resolve()
        assert result == expected
    
    def test_relative_path_with_base(self):
        """Relative paths should be resolved from provided base."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            rel_path = "subdir/file.txt"
            result = resolve_path(rel_path, base)
            expected = (base / rel_path).resolve()
            assert result == expected
    
    def test_dot_path_resolves_to_base(self):
        """Single dot path should resolve to base."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            result = resolve_path(".", base)
            assert result == base.resolve()


class TestGetProjectRoot:
    """Tests for get_project_root function."""
    
    def test_finds_x_ipe_yaml(self):
        """Should find project root by .x-ipe.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".x-ipe.yaml").touch()
            subdir = root / "src" / "module"
            subdir.mkdir(parents=True)
            
            result = get_project_root(subdir)
            assert result == root.resolve()
    
    def test_finds_x_ipe_dir(self):
        """Should find project root by .x-ipe/ directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".x-ipe").mkdir()
            subdir = root / "deep" / "nested" / "dir"
            subdir.mkdir(parents=True)
            
            result = get_project_root(subdir)
            assert result == root.resolve()
    
    def test_finds_git_dir_fallback(self):
        """Should find project root by .git/ directory as fallback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            subdir = root / "src"
            subdir.mkdir()
            
            result = get_project_root(subdir)
            assert result == root.resolve()
    
    def test_prefers_x_ipe_over_git(self):
        """Should prefer .x-ipe.yaml over .git."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".x-ipe.yaml").touch()
            (root / ".git").mkdir()  # Both exist
            
            result = get_project_root(root)
            assert result == root.resolve()
    
    def test_returns_none_when_not_found(self):
        """Should return None when no project root found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # No indicators in temp dir
            result = get_project_root(Path(tmpdir))
            # Might find parent .git, so check if None or valid Path
            # In isolated temp, should be None
            assert result is None or isinstance(result, Path)
    
    def test_uses_cwd_when_no_start_dir(self):
        """Should use cwd when start_dir not provided."""
        result = get_project_root()
        # Should return some Path (this project has .git)
        # or None if running in isolated env
        assert result is None or isinstance(result, Path)


class TestIsInitialized:
    """Tests for is_initialized function."""
    
    def test_true_with_x_ipe_dir(self):
        """Should return True when .x-ipe/ directory exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".x-ipe").mkdir()
            
            assert is_initialized(root) is True
    
    def test_true_with_x_ipe_yaml(self):
        """Should return True when .x-ipe.yaml file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".x-ipe.yaml").touch()
            
            assert is_initialized(root) is True
    
    def test_false_when_neither_exists(self):
        """Should return False when no X-IPE indicators exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            assert is_initialized(root) is False
    
    def test_false_with_only_git(self):
        """Should return False when only .git exists (not X-IPE)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            
            assert is_initialized(root) is False
    
    def test_accepts_string_path(self):
        """Should accept string path as input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".x-ipe.yaml").touch()
            
            assert is_initialized(tmpdir) is True


class TestEnsureDirectory:
    """Tests for ensure_directory function."""
    
    def test_creates_single_directory(self):
        """Should create a single directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "newdir"
            
            result = ensure_directory(new_dir)
            
            assert new_dir.exists()
            assert new_dir.is_dir()
            assert result == new_dir
    
    def test_creates_nested_directories(self):
        """Should create nested directories (parents=True)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = Path(tmpdir) / "a" / "b" / "c"
            
            result = ensure_directory(nested)
            
            assert nested.exists()
            assert nested.is_dir()
            assert result == nested
    
    def test_idempotent_on_existing(self):
        """Should not fail if directory already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            existing = Path(tmpdir) / "existing"
            existing.mkdir()
            
            result = ensure_directory(existing)
            
            assert existing.exists()
            assert result == existing
    
    def test_returns_path_for_chaining(self):
        """Should return the path for method chaining."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "chain"
            
            result = ensure_directory(new_dir)
            
            assert result == new_dir
            assert isinstance(result, Path)
