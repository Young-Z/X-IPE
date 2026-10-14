"""Current disk verification and disposable tampering; no production writes."""
import json
from pathlib import Path
import shutil

import pytest

from tests import publication_recovery_6749 as recovery

NAMES = ["x-ipe-task-based-" + suffix for suffix in (
    "requirement-gathering", "feature-breakdown", "feature-refinement", "technical-design",
    "code-implementation", "feature-acceptance-test", "feature-closing", "change-request",
    "bug-fix", "code-refactor",
)]


@pytest.mark.parametrize("name", NAMES)
def test_all_ten_actual_publications_and_patch_history(name):
    receipt = recovery.recovered_publication(name)
    assert receipt["native_publisher_receipt"] is False
    assert receipt["version"].endswith(".1")


@pytest.mark.parametrize("defect", [
    "production-byte", "candidate-byte", "baseline-receipt", "review", "r2-record",
    "unknown-cache", "false-native-receipt", "invented-journal", "invented-promotion-time",
])
def test_recovered_evidence_tampering_rejected_without_source_mutation(tmp_path, monkeypatch, defect):
    name = NAMES[4]
    root = recovery.ROOT
    source = recovery.META / name
    target = tmp_path / "x-ipe-docs/skill-meta" / name
    shutil.copytree(source, target)
    production = tmp_path / ".github/skills" / name
    shutil.copytree(root / ".github/skills" / name, production)
    record = tmp_path / recovery.R2.relative_to(root)
    record.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(recovery.R2, record)
    original = {p: p.read_bytes() for p in (source / "candidate").rglob("*") if p.is_file()}
    receipt_path = target / "publication-receipt-TASK-6749-R2.json"
    receipt = json.loads(receipt_path.read_text())
    if defect == "production-byte":
        (production / "SKILL.md").write_text("unexpected edit")
    elif defect == "candidate-byte":
        (target / "candidate/SKILL.md").write_text("unexpected edit")
    elif defect == "baseline-receipt":
        (tmp_path / receipt["baseline_receipt"]).write_text("{}")
    elif defect == "review":
        (target / "independent-review-TASK-6749-R2.md").write_text("invented approval")
    elif defect == "r2-record":
        record.write_text("{}")
    elif defect == "unknown-cache":
        (production / "unexpected.pyc").write_bytes(b"unowned")
    else:
        field, value = {
            "false-native-receipt": ("operation", "publish"),
            "invented-journal": ("atomic_writer_journal", "invented.json"),
            "invented-promotion-time": ("promotion_timestamp", receipt["verified_at"]),
        }[defect]
        receipt[field] = value
        receipt_path.write_text(json.dumps(receipt))
    monkeypatch.setattr(recovery, "ROOT", tmp_path)
    monkeypatch.setattr(recovery, "META", tmp_path / "x-ipe-docs/skill-meta")
    monkeypatch.setattr(recovery, "R2", record)
    with pytest.raises(AssertionError):
        recovery.recovered_publication(name)
    assert all(p.read_bytes() == data for p, data in original.items())