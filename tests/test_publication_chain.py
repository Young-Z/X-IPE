"""Reusable real-publisher history tests in disposable projects."""
import json
import shutil

import pytest

from tests.publication_recovery_6749 import publication_chain, resource_inventory
from tests.test_skill_creator_foundation import NAME, api, package, publish


def record(env, task):
    directory = env.candidate.parent
    (directory / f"baseline-TASK-{task}.json").write_text(json.dumps(env.baseline))
    receipt = publish(env, apply=True)
    assert receipt["ok"] and receipt["state"] == "published"
    (directory / f"publication-receipt-TASK-{task}.json").write_text(json.dumps(receipt))
    env.baseline = receipt["files"]
    env.managed = receipt["files"]
    return receipt


def test_two_actual_publications_preserve_prior_receipt(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    first = record(env, 1)
    original = (env.candidate.parent / "publication-receipt-TASK-1.json").read_bytes()
    (env.candidate / "references/keep.txt").write_text("new revision\n")
    (env.candidate / "references/new.txt").write_text("new resource\n")
    second = record(env, 2)
    chain = publication_chain(env.root, env.candidate.parent, NAME)
    assert chain == [first, second]
    assert resource_inventory(env.target) == second["files"]
    assert second["added"] == ["references/new.txt"]
    assert (env.candidate.parent / "publication-receipt-TASK-1.json").read_bytes() == original


def test_unrelated_task_labels_do_not_require_helper_updates(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    first = record(env, 101)
    (env.candidate / "references/keep.txt").write_text("next\n")
    second = record(env, 999)
    assert publication_chain(env.root, env.candidate.parent, NAME) == [first, second]


def test_altered_baseline_or_backup_is_rejected(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    receipt = record(env, 7)
    from pathlib import Path
    backup = Path(receipt["transaction"]) / "backup/references/keep.txt"
    backup.write_text("tampered")
    with pytest.raises(AssertionError):
        publication_chain(env.root, env.candidate.parent, NAME)


def test_broken_chain_is_not_hidden_by_valid_newest_transaction(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    record(env, 1)
    # A real but externally changed baseline cannot silently join the old chain.
    (env.target / "references/keep.txt").write_text("outside publication\n")
    env.baseline = resource_inventory(env.target)
    env.managed = env.baseline
    (env.candidate / "references/keep.txt").write_text("third state\n")
    record(env, 2)
    with pytest.raises(AssertionError, match="Broken or forked"):
        publication_chain(env.root, env.candidate.parent, NAME)


def test_real_evidence_survives_checkout_relocation(tmp_path, api):
    (tmp_path / "original").mkdir()
    env = package(tmp_path / "original", api, existing=True)
    original = record(env, 1)
    relocated = tmp_path / "relocated"
    shutil.copytree(env.root, relocated)
    directory = relocated / env.candidate.parent.relative_to(env.root)
    assert publication_chain(relocated, directory, NAME) == [original]


def test_noncanonical_recorded_transaction_is_rejected(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    receipt = record(env, 1)
    receipt["transaction"] = str(env.root / "outside" / "untrusted")
    (env.candidate.parent / "publication-receipt-TASK-1.json").write_text(json.dumps(receipt))
    with pytest.raises(AssertionError):
        publication_chain(env.root, env.candidate.parent, NAME)
