"""Read-only recovered publication checks; never synthesize publisher evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "x-ipe-docs/skill-meta"
R2 = META / "x-ipe-meta-skill-creator/review-validation-TASK-6749-R2.json"


def fingerprint(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


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
    def inventory(folder):
        return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in folder.rglob("*") if p.is_file()}
    assert inventory(ROOT / ".github/skills" / name) == receipt["files"]
    assert inventory(directory / "candidate") == receipt["files"]
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