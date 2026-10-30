import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "publish_reports.py"
SPEC = importlib.util.spec_from_file_location("publish_reports", MODULE_PATH)
publisher = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(publisher)


def metadata(name="Unsafe <script>"):
    return {
        "schema_version": "1.0",
        "record_revision": 1,
        "case": {"id": "CR-2026-001", "name": name, "status": "Evaluating"},
        "inputs": {},
        "reports": {"latest": {}, "history": []},
    }


def model():
    return {
        "schema_version": "1.0",
        "provenance": {"skill_version": "1.0.0", "benchmark_version": "1.0.0", "template_version": "1.0.0", "snapshot_version": 1},
        "case": {"id": "CR-2026-001", "name": "Unsafe <script>", "language": "en", "summary": "Test"},
        "coverage": {"depth": "standard", "status": "complete", "inspected": ["src"], "gaps": []},
        "estimate": {
            "vendor_range": [4, 8], "ai_range": [3, 6], "confidence": 80, "comparison": "aligned",
            "modules": [{"name": "API <script>", "range": [3, 6], "ai_factor": 0}],
            "factors": [], "guidance": "Proceed",
        },
        "design": {"decision": "Adopt", "adoption": ["Reuse service"], "contracts": [], "work_packages": [], "testing": [], "rollout": [], "rollback": [], "risks": [], "traceability": []},
        "diagrams": [],
    }


def case_folder(tmp_path):
    folder = tmp_path / "CR-2026-001"
    folder.mkdir()
    envelope = publisher._envelope(metadata())
    (folder / "CaseRecord.html").write_text(f"<html><body>{envelope}</body></html>", encoding="utf-8")
    return folder


def test_publish_creates_versioned_bundle_and_completed_metadata(tmp_path):
    folder = case_folder(tmp_path)
    model_path = tmp_path / "model.json"
    model_path.write_text(json.dumps(model()), encoding="utf-8")

    receipt = publisher.publish(folder, model_path)

    assert receipt["version"] == 1
    assert (folder / "EffortEstimation_AI_v1.html").is_file()
    assert (folder / "SuggestedTechnicalDesign_AI_v1.html").is_file()
    assert (folder / "reports/report-model-v1.json").is_file()
    updated = publisher._metadata((folder / "CaseRecord.html").read_text(encoding="utf-8"))
    assert updated["case"]["status"] == "Completed"
    assert updated["reports"]["version"] == 1
    assert "&lt;script&gt;" in (folder / "EffortEstimation_AI_v1.html").read_text(encoding="utf-8")


def test_second_publication_preserves_history(tmp_path):
    folder = case_folder(tmp_path)
    model_path = tmp_path / "model.json"
    model_path.write_text(json.dumps(model()), encoding="utf-8")
    publisher.publish(folder, model_path)

    receipt = publisher.publish(folder, model_path)

    updated = publisher._metadata((folder / "CaseRecord.html").read_text(encoding="utf-8"))
    assert receipt["version"] == 2
    assert updated["reports"]["history"][0]["version"] == 1
    assert updated["reports"]["history"][0]["files"]["effort"] == "EffortEstimation_AI_v1.html"


def test_invalid_totals_do_not_replace_latest(tmp_path):
    folder = case_folder(tmp_path)
    model_path = tmp_path / "model.json"
    valid = model()
    model_path.write_text(json.dumps(valid), encoding="utf-8")
    publisher.publish(folder, model_path)
    before = (folder / "CaseRecord.html").read_bytes()
    invalid = model()
    invalid["estimate"]["ai_range"] = [99, 100]
    model_path.write_text(json.dumps(invalid), encoding="utf-8")

    try:
        publisher.publish(folder, model_path)
        assert False, "expected PublishError"
    except publisher.PublishError:
        pass

    assert (folder / "CaseRecord.html").read_bytes() == before
    assert not (folder / "EffortEstimation_AI_v2.html").exists()


def test_ai_factor_requires_evidence(tmp_path):
    folder = case_folder(tmp_path)
    value = model()
    value["estimate"]["modules"][0]["ai_factor"] = -0.15
    model_path = tmp_path / "model.json"
    model_path.write_text(json.dumps(value), encoding="utf-8")

    try:
        publisher.publish(folder, model_path)
        assert False, "expected PublishError"
    except publisher.PublishError as error:
        assert "AI factor" in str(error)


def test_failure_marker_preserves_latest_reports(tmp_path):
    folder = case_folder(tmp_path)
    before = publisher._metadata((folder / "CaseRecord.html").read_text(encoding="utf-8"))["reports"]

    publisher.mark_failed(folder, "Invalid totals at /secret/path")

    updated = publisher._metadata((folder / "CaseRecord.html").read_text(encoding="utf-8"))
    assert updated["case"]["status"] == "Failed"
    assert updated["reports"] == before
    assert "Invalid totals" in updated["assessment_failure"]["reason"]
    assert "/secret/path" not in updated["assessment_failure"]["reason"]
