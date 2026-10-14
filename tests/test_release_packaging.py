"""TASK-6749: inspect real Hatch manifests without building release artifacts.

Hatchling is the declared build backend. Install build-system requirements to
run these checks; ordinary application-only environments may skip this module.
Synthetic hostile files exist only in pytest's temporary directory.
"""

import copy
import json
from pathlib import Path
import tomllib

import pytest

pytest.importorskip("hatchling", reason="release checks require the build backend")
from hatchling.builders.sdist import SdistBuilder
from hatchling.builders.wheel import WheelBuilder


ROOT = Path(__file__).resolve().parents[1]
CONFIG = tomllib.loads((ROOT / "pyproject.toml").read_text())
BUILDERS = {"sdist": SdistBuilder, "wheel": WheelBuilder}


def manifest(root, target):
    """Use backend selection and distribution paths, not a simulated glob."""
    builder = BUILDERS[target](str(root), config=copy.deepcopy(CONFIG))
    files = list(builder.recurse_included_files())
    paths = [item.distribution_path.replace("\\", "/") for item in files]
    assert len(paths) == len(set(paths)), "duplicate archive destinations"
    return {path: Path(item.path) for path, item in zip(paths, files)}


@pytest.mark.parametrize("target", BUILDERS)
def test_actual_payload_preserves_runtime_and_offline_dependencies(target):
    files = manifest(ROOT, target)
    package = "src/x_ipe" if target == "sdist" else "x_ipe"
    skills = ".github/skills" if target == "sdist" else "x_ipe/resources/skills"
    config = "x-ipe-docs/config" if target == "sdist" else "x_ipe/resources/config"
    for required in (
        f"{package}/cli/main.py",
        f"{package}/static/js/features/action-execution-modal.js",
        f"{package}/static/3rdparty/js/easymde.min.js",
        f"{skills}/pptx/SKILL.md",
        f"{skills}/pptx/scripts/html2pptx.js",
        f"{skills}/pptx/scripts/package.json",
        f"{skills}/pptx/scripts/package-lock.json",
        f"{skills}/x-ipe-tool-task-board-manager/SKILL.md",
        f"{config}/.env.example",
        f"{config}/workflow-template.json",
        f"{config}/copilot-prompt.json",
    ):
        assert required in files, f"missing intentional content: {required}"
    # Preserve the existing offline payload, including native dependencies.
    # Portability/license approval is a separate release gate, not deletion.
    vendored = ROOT / ".github/skills/pptx/scripts/node_modules"
    for source in vendored.rglob("*"):
        if source.is_file() and source.suffix in {".node", ".dylib"}:
            destination = f"{skills}/pptx/scripts/node_modules/{source.relative_to(vendored).as_posix()}"
            assert destination in files
    for name in ("workflow-template.json", "copilot-prompt.json"):
        assert json.loads(files[f"{config}/{name}"].read_text()) == json.loads(
            (ROOT / "src/x_ipe/resources/config" / name).read_text()
        )
    if target == "sdist":
        for required in ("pyproject.toml", "README.md", "LICENSE", "tests/test_release_packaging.py",
                         "package.json", "package-lock.json", "vitest.config.js"):
            assert required in files
    else:
        assert all(not path.startswith(("tests/", "x-ipe-docs/", ".github/")) for path in files)


@pytest.mark.parametrize("target", BUILDERS)
def test_nested_generated_and_secret_files_are_filtered(tmp_path, target):
    roots = ("src/x_ipe", ".github/skills/example", "x-ipe-docs/config",
             ".github/skills/example/node_modules/dependency")
    forbidden = (
        ".env", ".env.local", ".env.production", ".pypirc", ".npmrc",
        "id_rsa", "id_ed25519", "private.pem", "private.key", "credentials.json",
        ".DS_Store", "Thumbs.db", "__pycache__/leak.pyc", "nested/leak.pyc",
        ".pytest_cache/value", ".ruff_cache/value", ".coverage",
        ".venv/token", ".git/config", ".claude/settings.local.json",
        ".copilot/mcp-config.json", "codex/skills/local/SKILL.md",
        "instance/local.db", "debug.log",
    )
    for base in roots:
        for relative in (*forbidden, ".env.example", "keep.txt"):
            path = tmp_path / base / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic fixture, not a secret")
    for relative in (".github/copilot-instructions.md", "README.md", "LICENSE",
                     "pyproject.toml", "codex/skills/local/SKILL.md",
                     ".claude/settings.local.json", ".copilot/mcp-config.json",
                     "node_modules/development-only/index.js", "unapproved.txt"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic fixture")
    vendored = tmp_path / ".github/skills/example/node_modules/dependency/index.js"
    vendored.parent.mkdir(parents=True, exist_ok=True)
    vendored.write_text("intentional offline dependency")
    files = manifest(tmp_path, target)
    assert len(files) >= 5, "empty manifest cannot prove filtering"
    assert all(source.name in {"keep.txt", ".env.example", "index.js",
                               "copilot-instructions.md", "README.md", "LICENSE",
                               "pyproject.toml"} for source in files.values()), sorted(files)
    assert vendored in files.values(), "do not blanket-exclude offline node_modules"
    assert tmp_path / "unapproved.txt" not in files.values()
    assert tmp_path / "node_modules/development-only/index.js" not in files.values()


def test_sdist_manifest_contains_every_wheel_input():
    """An sdist rebuild must not silently lose the wheel's offline payload."""
    source_files = set(manifest(ROOT, "sdist").values())
    wheel_files = manifest(ROOT, "wheel")
    missing = {destination: str(source.relative_to(ROOT))
               for destination, source in wheel_files.items()
               if source not in source_files}
    assert not missing, missing


@pytest.mark.parametrize("target", BUILDERS)
def test_no_local_mirrors_or_generated_files_in_actual_manifest(target):
    for path in manifest(ROOT, target):
        parts = Path(path).parts
        assert not {"codex", ".claude", ".copilot", "__pycache__", ".venv",
                    ".pytest_cache", ".ruff_cache", ".DS_Store"}.intersection(parts), path
        assert not path.endswith((".pyc", ".pyo")), path
        assert not any(part.startswith(".env") and part != ".env.example" for part in parts), path