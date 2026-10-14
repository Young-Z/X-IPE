"""Full promoted-goal package census, read-only API/CLI and receipt parity.

This verifies distributable contracts and publication bytes, not agent decisions.
"""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tests.publication_recovery_6749 import recovered_publication, resource_inventory
from tests.skill_validation_harness_6749 import load_source, validation_project

ROOT = Path(__file__).resolve().parents[1]
NAMES = ["x-ipe-workflow-task-execution"] + [
    "x-ipe-task-based-" + suffix for suffix in (
        "requirement-gathering", "feature-breakdown", "feature-refinement", "technical-design",
        "code-implementation", "feature-acceptance-test", "feature-closing", "change-request",
        "bug-fix", "code-refactor",
    )
] + ["x-ipe-tool-refactoring-analysis", "x-ipe-tool-code-quality-sync",
     "x-ipe+feature+quality-board-management"]


@pytest.mark.parametrize("name", NAMES)
def test_each_promoted_goal_package_current_receipt_cli_and_canonical_dependencies(name):
    script = ROOT / ".github/skills/x-ipe-meta-skill-creator/scripts/validate_skill.py"
    validator = load_source(script, "inventory_validator_6749")
    meta = ROOT / "x-ipe-docs/skill-meta" / name
    candidate = meta / "candidate"
    kind = ("x-ipe-workflow-orchestration" if name.startswith("x-ipe-workflow-") else
            "x-ipe-task-category" if "+" in name else
            "x-ipe-tool" if name.startswith("x-ipe-tool-") else "x-ipe-task-based")
    installed = ROOT / ".github/skills" / name
    before = (validator.tree_bytes(candidate, ROOT), validator.tree_bytes(installed, ROOT))
    with validation_project(validator, ROOT, candidate, name) as (project, copied):
        checked = validator.validate(project, copied, name, kind)
        assert checked["ok"], checked["errors"]
        copied_before = validator.tree_bytes(copied, project)
        process = subprocess.run([sys.executable, str(script), "--project-root", str(project),
                                  "--candidate", str(copied), "--name", name, "--type", kind],
                                 capture_output=True, text=True, timeout=30)
        assert process.returncode == 0, process.stdout + process.stderr
        assert json.loads(process.stdout) == checked
        assert validator.tree_bytes(copied, project) == copied_before
    assert (validator.tree_bytes(candidate, ROOT), validator.tree_bytes(installed, ROOT)) == before
    installed_files = resource_inventory(installed)
    assert resource_inventory(candidate) == checked["files"]
    receipt_path = meta / "publication-receipt-goal-TASK-6749.json"
    if name == "x-ipe-workflow-task-execution":
        receipt_path = meta / "publication-receipt-mode-TASK-6749-R2.json"
    if not receipt_path.exists():
        receipt_path = meta / "promotion-receipt-goal-TASK-6749.json"
    published = json.loads(receipt_path.read_text())
    if name.startswith("x-ipe-task-based-"):
        # Prior goal receipt stays immutable; R2 verifies actual installed bytes.
        historical = published
        published = recovered_publication(name, installed_files)
        assert published["baseline_hash"] == validator.fingerprint(historical["files"])
    manifest = published.get("files", published.get("published_files"))
    assert manifest == installed_files  # Publication receipt binds installed bytes.
    if name == "x-ipe+feature+quality-board-management":
        assert published["operation"] == "authorized_patch_promotion" and published["state"] == "published"
        fingerprint = published["post_promotion"]["candidate_hash"]
        assert published["post_promotion"]["production_hash"] == fingerprint
        assert published["post_promotion"]["byte_parity"] is True
    else:
        fingerprint = published["candidate_hash"]
        assert published["byte_parity"] is True
        if name == "x-ipe-workflow-task-execution":
            assert published["operation"] == "publish" and published["state"] == "published"
        else:
            assert published["publication_state"] == "published"
    assert fingerprint == validator.fingerprint(manifest)
    if name == "x-ipe-workflow-task-execution":
        # Real R2 native publication; historical correction receipts stay unchanged.
        assert checked["files"] == installed_files and checked["candidate_hash"] == fingerprint
        transaction = Path(published["transaction"])
        journal = json.loads((transaction / "journal.json").read_text())
        assert journal["state"] == "published" and journal["proposed"] == installed_files
        old = json.loads((meta / "promotion-receipt-goal-TASK-6749.json").read_text())
        assert validator.manifest(validator.tree_bytes(transaction / "backup", ROOT)) == old["files"]
        assert published["baseline_hash"] == old["candidate_hash"]
    else:
        assert installed_files == checked["files"]
        assert fingerprint == checked["candidate_hash"]
    # Every concrete Markdown dependency is checked by the installed validator.
    # Additionally forbid accidentally distributing links to a staged goal policy.
    for path in installed.rglob("*.md"):
        for link in validator.markdown_targets(path.read_text()):
            if "goal-contract.md" in link:
                assert link == ".github/skills/x-ipe-workflow-task-execution/references/goal-contract.md"
    if name == "x-ipe-tool-refactoring-analysis":
        entry = (installed / "SKILL.md").read_text()
        for clause in ("goal/subgoal/source/parent", "all-required", "selected alternatives", "stakeholder observation"):
            assert clause in entry  # Own operation contract, not a task/lifecycle schema.