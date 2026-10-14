"""Run compatibility tests against candidate or --production modules.

Run with configured Python -B from project root. No workspace writes; pytest
cache disabled. New tests use temporary project roots and explicit candidate paths.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
META = Path(__file__).resolve().parent
SCRIPTS = META / "candidate" / "scripts"
NAMES = (
    "_board_lib", "_task_store", "task_create", "task_ensure", "task_update",
    "task_query", "task_archive", "feature_create", "feature_update",
    "feature_query", "migrate",
)
EXISTING = (
    "test_board_lib.py", "test_task_crud.py", "test_feature_crud.py",
    "test_migrate.py", "test_task_board_api.py", "test_feature_board_api.py",
    "test_task_board_page.py", "test_feature_board_page.py",
)


def main() -> int:
    global SCRIPTS
    if sys.argv[1:] == ["--production"]:
        SCRIPTS = ROOT / ".github" / "skills" / "x-ipe-tool-task-board-manager" / "scripts"
    elif sys.argv[1:]:
        raise SystemExit("Usage: verify_candidate.py [--production]")
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(SCRIPTS))
    for name in NAMES:
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    for name in NAMES:
        assert Path(sys.modules[name].__file__).parent == SCRIPTS

    class Origins:
        def pytest_collection_modifyitems(self, items):
            # Existing AST source-path test must also inspect candidate library.
            for item in items:
                if item.module.__name__.endswith("test_board_lib"):
                    item.module._SCRIPTS_DIR = str(SCRIPTS)
                if item.module.__name__.endswith("test_registration"):
                    item.module.SCRIPTS = SCRIPTS
            for name in NAMES:
                assert Path(sys.modules[name].__file__).parent == SCRIPTS

    args = ["-q", "-p", "no:cacheprovider"]
    args += [str(ROOT / "tests" / filename) for filename in EXISTING]
    args += [str(META / "tests" / "test_registration.py")]
    return pytest.main(args, plugins=[Origins()])


if __name__ == "__main__":
    raise SystemExit(main())
