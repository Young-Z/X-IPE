"""Real cached imports and strict publisher inventories in disposable trees."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tests.publication_recovery_6749 import resource_inventory
from tests.skill_validation_harness_6749 import (
    copy_resources, load_source, validation_project,
)
from tests.test_goal_oriented_skills import validator
from tests.test_skill_creator_foundation import skill

ROOT = Path(__file__).resolve().parents[1]
NAME = "x-ipe-task-based-feature-acceptance-test"


def cached_import(source):
    result = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); __import__(sys.argv[2])",
            str(source.parent), source.stem], capture_output=True, text=True,
           env={key: value for key, value in os.environ.items()
               if key != "PYTHONDONTWRITEBYTECODE"})
    assert result.returncode == 0, result.stdout + result.stderr
    cache = Path(importlib.util.cache_from_source(str(source)))
    assert cache.is_file()
    return cache


def test_generated_cached_import_full_copy_validation_leaves_sources_unchanged(tmp_path):
    tmp_path = tmp_path.resolve()
    v = validator()
    source = ROOT / "x-ipe-docs/skill-meta" / NAME / "candidate"
    original = v.tree_bytes(source, ROOT)
    copy = tmp_path / "imported"
    copy_resources(source, copy)
    baseline = resource_inventory(copy)
    script = copy / "scripts/verify_evidence.py"
    source_bytes = script.read_bytes()
    before = v.tree_bytes(copy, tmp_path)
    load_source(script, "no_cache_evidence_6749")
    assert v.tree_bytes(copy, tmp_path) == before
    cache = cached_import(script)
    assert script.read_bytes() == source_bytes
    assert resource_inventory(copy) == baseline
    # Full canonical package with all real dependencies, not a receipt mock.
    with validation_project(v, ROOT, source, NAME) as (project, candidate):
        generated = candidate / cache.relative_to(copy)
        generated.parent.mkdir(parents=True, exist_ok=True)
        generated.write_bytes(cache.read_bytes())
        physical = v.validate(project, candidate, NAME, "x-ipe-task-based")
        assert physical["ok"], physical["errors"]
        assert cache.relative_to(copy).as_posix() in physical["files"]
        with validation_project(v, project, candidate, NAME) as (clean_root, clean):
            checked = v.validate(clean_root, clean, NAME, "x-ipe-task-based")
            assert checked["ok"], checked["errors"]
            assert checked["files"] == baseline
            assert not (clean / cache.relative_to(copy)).exists()
            # Self references must bind the candidate, not the live package.
            (clean / "scripts/verify_evidence.py").unlink()
            broken = v.validate(clean_root, clean, NAME, "x-ipe-task-based")
            assert not broken["ok"]
            assert any("verify_evidence.py" in error for error in broken["errors"])
        assert generated.read_bytes() == cache.read_bytes()
    assert v.tree_bytes(source, ROOT) == original


@pytest.mark.parametrize("resource", [
    "scripts/__pycache__/unknownfile.pyc", "scripts/unknownfile.pyc",
    "scripts/__pycache__/unmanaged.txt",
    Path(importlib.util.cache_from_source("scripts/verify_evidence.py")).as_posix(),
])
def test_unknownfile_pyc_survives_copy_and_cannot_match_resources(tmp_path, resource):
    v = validator()
    source = ROOT / "x-ipe-docs/skill-meta" / NAME / "candidate"
    with validation_project(v, ROOT, source, NAME) as (project, candidate):
        baseline = resource_inventory(candidate)
        unknown = candidate / resource
        unknown.parent.mkdir(parents=True, exist_ok=True)
        unknown.write_bytes(b"unmanaged tamper")
        with validation_project(v, project, candidate, NAME) as (copied_root, copied):
            checked = v.validate(copied_root, copied, NAME, "x-ipe-task-based")
            assert checked["ok"], checked["errors"]
            key = unknown.relative_to(candidate).as_posix()
            assert key in checked["files"]
            assert (copied / key).read_bytes() == b"unmanaged tamper"
            with pytest.raises(AssertionError):
                assert checked["files"] == baseline


@pytest.mark.parametrize("resource", [
    "scripts/linked.py", "scripts/linked-directory",
    Path(importlib.util.cache_from_source("scripts/verify_evidence.py")).as_posix(),
])
def test_full_copy_preserves_symlink_resources_and_validator_rejects(resource):
    v = validator()
    source = ROOT / "x-ipe-docs/skill-meta" / NAME / "candidate"
    original = v.tree_bytes(source, ROOT)
    with validation_project(v, ROOT, source, NAME) as (project, candidate):
        link = candidate / resource
        link.parent.mkdir(parents=True, exist_ok=True)
        target = candidate / ("references" if resource.endswith("directory") else "SKILL.md")
        link.symlink_to(target, target_is_directory=target.is_dir())
        with validation_project(v, project, candidate, NAME) as (copied_root, copied):
            assert (copied / resource).is_symlink()
            checked = v.validate(copied_root, copied, NAME, "x-ipe-task-based")
            assert not checked["ok"]
            assert any("Symlink prohibited" in error for error in checked["errors"])
            with pytest.raises(AssertionError, match="Symlink resource"):
                resource_inventory(copied)
        assert link.is_symlink()
    assert v.tree_bytes(source, ROOT) == original


def test_tampered_source_full_copy_cannot_match_immutable_resources():
    v = validator()
    source = ROOT / "x-ipe-docs/skill-meta" / NAME / "candidate"
    original = v.tree_bytes(source, ROOT)
    with validation_project(v, ROOT, source, NAME) as (project, candidate):
        baseline = resource_inventory(candidate)
        script = candidate / "scripts/verify_evidence.py"
        cached_import(script)
        script.write_bytes(script.read_bytes() + b"\n# unauthorized source change\n")
        tampered = v.tree_bytes(candidate, project)
        with validation_project(v, project, candidate, NAME) as (copied_root, copied):
            before = v.tree_bytes(copied, copied_root)
            checked = v.validate(copied_root, copied, NAME, "x-ipe-task-based")
            assert checked["ok"], checked["errors"]
            assert checked["files"] == resource_inventory(candidate)
            assert checked["files"]["scripts/verify_evidence.py"] != baseline["scripts/verify_evidence.py"]
            with pytest.raises(AssertionError):
                assert checked["files"] == baseline
            assert v.tree_bytes(copied, copied_root) == before
        assert v.tree_bytes(candidate, project) == tampered
    assert v.tree_bytes(source, ROOT) == original


def test_publisher_preserves_identically_retained_real_cache(tmp_path, monkeypatch):
    tmp_path = tmp_path.resolve()
    v = validator()
    monkeypatch.setitem(sys.modules, "validate_skill", v)
    publisher = load_source(ROOT / ".github/skills/x-ipe-meta-skill-creator/scripts/publish_skill.py",
                            "cache_preserving_publisher_6749")
    name = "x-ipe-tool-cache-test"
    live = tmp_path / ".github/skills" / name
    live.mkdir(parents=True)
    (live / "SKILL.md").write_bytes(skill(name=name, marker="baseline"))
    script = live / "scripts/check.py"
    script.parent.mkdir()
    script.write_text("VALUE = 1\n")
    managed = resource_inventory(live)
    cache = cached_import(script)
    cache_bytes = cache.read_bytes()
    physical = v.manifest(v.tree_bytes(live, tmp_path))
    candidate = tmp_path / "x-ipe-docs/skill-meta" / name / "candidate"
    copy_resources(live, candidate)
    key = cache.relative_to(live).as_posix()
    checked = v.validate(tmp_path, candidate, name, "x-ipe-tool")
    for apply in (False, True):
        with pytest.raises(ValueError, match="dirty or unmanaged"):
            publisher.publish(tmp_path, candidate, name, "x-ipe-tool", physical, managed,
                              checked["candidate_hash"], apply=apply)
        assert v.manifest(v.tree_bytes(live, tmp_path)) == physical
    # Explicitly retaining identical unmanaged bytes is permitted, not ignored.
    retained = candidate / key
    retained.parent.mkdir(parents=True, exist_ok=True)
    retained.write_bytes(cache_bytes)
    (candidate / "SKILL.md").write_bytes(skill(name=name, marker="updated"))
    checked = v.validate(tmp_path, candidate, name, "x-ipe-tool")
    result = publisher.publish(tmp_path, candidate, name, "x-ipe-tool", physical, managed,
                               checked["candidate_hash"], apply=True)
    assert result["state"] == "published" and result["byte_parity"]
    assert key in result["protected"] and key in result["files"]
    assert cache.read_bytes() == cache_bytes
    assert script.read_text() == "VALUE = 1\n"
    assert v.manifest(v.tree_bytes(live, tmp_path)) == checked["files"]