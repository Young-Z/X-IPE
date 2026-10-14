"""Read-only recovered publication checks; never synthesize publisher evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path

from tests.skill_validation_harness_6749 import source_cache

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "x-ipe-docs/skill-meta"
R2 = META / "x-ipe-meta-skill-creator/review-validation-TASK-6749-R2.json"


def fingerprint(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def resource_inventory(folder):
    """Ignore only this interpreter's cache for an existing Python source.

    Unknown bytecode, arbitrary files inside __pycache__, and source changes
    remain visible. Publisher safety uses its own complete physical inventory.
    """
    folder = Path(folder)
    nodes = list(folder.rglob("*"))
    assert not folder.is_symlink(), f"Symlink resource: {folder}"
    assert not any(p.is_symlink() for p in nodes), "Symlink resource in inventory"
    sources = [p for p in nodes if p.suffix == ".py" and p.is_file()]
    caches = {Path(importlib.util.cache_from_source(str(p))) for p in sources}
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in nodes if p.is_file() and not source_cache(p, caches)}


def recovered_publication(name, live=None):
    """Check current bytes, immutable historical baseline and trusted R2 review."""
    directory = META / name
    receipt = json.loads((directory / "publication-receipt-TASK-6749-R2.json").read_text())
    assert receipt["operation"] == "recovered_editor_publication_verification"
    assert receipt["publication_state"] == "published" and receipt["byte_parity"] is True
    assert receipt["production_writes_replayed"] is False
    assert receipt["promotion_timestamp"] is None
    assert receipt["atomic_writer_journal"] is None
    assert receipt["preserved_unmanaged"] == {}
    assert hashlib.sha256(R2.read_bytes()).hexdigest() == receipt["r2_record_sha256"]
    recorded = next(item for item in json.loads(R2.read_text())["validation_summaries"] if item["name"] == name)
    assert receipt["candidate_hash"] == recorded["candidate_hash"]
    assert receipt["baseline_hash"] == recorded["production_hash"]
    prior = ROOT / receipt["baseline_receipt"]
    assert hashlib.sha256(prior.read_bytes()).hexdigest() == receipt["baseline_receipt_sha256"]
    historical = json.loads(prior.read_text())
    baseline = historical.get("files", historical.get("published_files"))
    assert fingerprint(baseline) == receipt["baseline_hash"]
    assert set(baseline) == set(receipt["files"])
    assert receipt["added"] == receipt["removed"] == []
    assert receipt["changed"] == sorted(p for p in baseline if baseline[p] != receipt["files"][p])
    review = directory / "independent-review-TASK-6749-R2.md"
    assert hashlib.sha256(review.read_bytes()).hexdigest() == receipt["review_sha256"]
    assert receipt["candidate_hash"] in review.read_text()
    assert fingerprint(receipt["files"]) == receipt["candidate_hash"] == receipt["production_hash"]
    assert resource_inventory(ROOT / ".github/skills" / name) == receipt["files"]
    assert resource_inventory(directory / "candidate") == receipt["files"]
    if live is not None:
        assert live == receipt["files"]
    history = (directory / "skill-meta.md").read_text().split("## R2 recovered publication history", 1)[1]
    assert receipt["version"] in history and receipt["candidate_hash"] in history
    return receipt


def historical_publication(name):
    directory = META / name
    path = directory / "publication-receipt-goal-TASK-6749.json"
    if not path.exists():
        path = directory / "promotion-receipt-goal-TASK-6749.json"
    return json.loads(path.read_text())