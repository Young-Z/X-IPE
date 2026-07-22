"""AAA-driven backend and route tests for FEATURE-060-A."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from x_ipe.app import create_app
from x_ipe.services.case_record_codec import CaseRecordCodec, RevisionConflictError
from x_ipe.services.cr_assessment_service import CrAssessmentService


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    (tmp_path / "repo").mkdir()
    config = tmp_path / "x-ipe-docs" / "config"
    config.mkdir(parents=True)
    config.joinpath("copilot-prompt.json").write_text(
        json.dumps({
            "cr-assessment": {"prompts": [{"id": "evaluate-cr-effort", "prompt-details": [{
                "language": "en", "label": "AI Estimation",
                "command": "assess <case-folder> --analysis-depth <analysis-depth>",
            }]}]}
        })
    )
    return tmp_path


@pytest.fixture()
def service(project: Path) -> CrAssessmentService:
    return CrAssessmentService(project)


def valid_form(project: Path) -> dict[str, str]:
    return {
        "case_name": "Portal SSO",
        "cr_description_text": "Add enterprise SSO",
        "codebase_path": str(project / "repo"),
        "comments": "Check migration",
    }


def vendor_file(name: str = "vendor.xlsx"):
    from werkzeug.datastructures import FileStorage
    return FileStorage(stream=io.BytesIO(b"estimate"), filename=name)


def test_codec_creates_reads_and_preserves_unknown_fields(tmp_path: Path):
    codec = CaseRecordCodec()
    path = tmp_path / "CaseRecord.html"
    metadata = {"schema_version": "1.0", "record_revision": 1, "case": {"id": "CR-2026-001", "name": "A"}, "future": {"value": 1}}
    codec.create_initial(path, metadata)
    merged = codec.merge(path, {"case": {"name": "B"}}, 1)
    assert merged["case"]["name"] == "B"
    assert merged["future"] == {"value": 1}
    assert merged["record_revision"] == 2


def test_codec_rejects_stale_revision(tmp_path: Path):
    codec = CaseRecordCodec()
    path = tmp_path / "CaseRecord.html"
    codec.create_initial(path, {"record_revision": 1, "case": {"id": "CR-2026-001", "name": "A"}})
    with pytest.raises(RevisionConflictError):
        codec.merge(path, {"case": {"name": "B"}}, 0)


def test_codec_escapes_script_like_metadata(tmp_path: Path):
    codec = CaseRecordCodec()
    path = tmp_path / "CaseRecord.html"
    codec.create_initial(path, {"record_revision": 1, "case": {"id": "CR-2026-001", "name": "</script>"}})
    text = path.read_text()
    assert "\\u003c/script>" in text
    assert text.count("</script>") == 1


def test_create_assigns_immutable_generated_id(service: CrAssessmentService, project: Path):
    first = service.create_case(valid_form(project))
    second = service.create_case({**valid_form(project), "case_name": "Portal SSO"})
    assert first["case"]["id"].endswith("-001")
    assert second["case"]["id"].endswith("-002")
    assert first["case"]["name"] == second["case"]["name"]


def test_update_name_does_not_rename_folder(service: CrAssessmentService, project: Path):
    case = service.create_case(valid_form(project))
    case_id = case["case"]["id"]
    updated = service.update_case(case_id, {**valid_form(project), "case_name": "Renamed"}, expected_revision=1)
    assert updated["case"]["name"] == "Renamed"
    assert (project / "x-ipe-docs" / "cr-cases" / case_id).is_dir()


def test_stale_update_does_not_store_new_artifacts(service: CrAssessmentService, project: Path):
    case = service.create_case(valid_form(project))
    case_id = case["case"]["id"]
    with pytest.raises(RevisionConflictError):
        service.update_case(
            case_id,
            valid_form(project),
            {"vendor_estimate": vendor_file("stale.xlsx")},
            expected_revision=0,
        )
    assert not (project / "x-ipe-docs" / "cr-cases" / case_id / "inputs" / "vendor-estimate").exists()


@pytest.mark.parametrize("path", ["https://example.com/repo.git", "git@github.com:a/b.git", "/missing/path"])
def test_invalid_codebase_paths_are_rejected(service: CrAssessmentService, path: str):
    assert service.validate_codebase(path)["valid"] is False


def test_valid_codebase_and_directory_listing(service: CrAssessmentService, project: Path):
    (project / "repo" / "child").mkdir()
    assert service.validate_codebase(str(project / "repo"))["valid"] is True
    listing = service.list_directories(str(project / "repo"))
    assert listing["directories"] == [{"name": "child", "path": str(project / "repo" / "child")}]


def test_prepare_requires_vendor_estimate(service: CrAssessmentService, project: Path):
    case = service.create_case(valid_form(project))
    with pytest.raises(ValueError, match="vendor_estimate"):
        service.prepare_assessment(case["case"]["id"], valid_form(project), "standard", expected_revision=1)


@pytest.mark.parametrize("depth", ["quick", "standard", "deep"])
def test_prepare_snapshots_and_marks_evaluating(service: CrAssessmentService, project: Path, depth: str):
    case = service.create_case(valid_form(project), {"vendor_estimate": vendor_file()})
    result = service.prepare_assessment(case["case"]["id"], valid_form(project), depth, expected_revision=1)
    stored = service.get_case(case["case"]["id"])
    assert result["status"] == "Evaluating"
    assert result["command"].endswith(f"--analysis-depth {depth}")
    assert (project / result["snapshot_path"]).is_file()
    assert stored["case"]["status"] == "Evaluating"


def test_uploaded_names_are_safe_and_original_preserved(service: CrAssessmentService, project: Path):
    case = service.create_case(valid_form(project), {"vendor_estimate": vendor_file("../../vendor estimate.xlsx")})
    vendor = case["inputs"]["vendor_estimate"]
    assert vendor["original_name"] == "../../vendor estimate.xlsx"
    assert ".." not in vendor["path"]
    assert (project / "x-ipe-docs" / "cr-cases" / case["case"]["id"] / vendor["path"]).is_file()


def test_changes_returns_only_changed_and_removed(service: CrAssessmentService, project: Path):
    case = service.create_case(valid_form(project))
    first = service.changes({})
    marker = first["markers"][case["case"]["id"]]
    assert len(first["changed"]) == 1
    assert service.changes({case["case"]["id"]: marker})["changed"] == []
    assert service.changes({"CR-2026-999": "1:1"})["removed"] == ["CR-2026-999"]


@pytest.fixture()
def client(project: Path):
    app = create_app({"TESTING": True, "PROJECT_ROOT": str(project)})
    return app.test_client()


def test_empty_list_route(client):
    response = client.get("/api/cr-assessments")
    assert response.status_code == 200
    assert response.json["data"]["cases"] == []


def test_create_get_search_and_update_routes(client, project: Path):
    created = client.post("/api/cr-assessments", data=valid_form(project))
    assert created.status_code == 201
    case = created.json["data"]
    case_id = case["case"]["id"]
    assert client.get(f"/api/cr-assessments/{case_id}").status_code == 200
    assert len(client.get("/api/cr-assessments?query=sso").json["data"]["cases"]) == 1
    updated = client.put(f"/api/cr-assessments/{case_id}", data={**valid_form(project), "case_name": "Renamed", "expected_revision": "1"})
    assert updated.status_code == 200
    assert updated.json["data"]["case"]["name"] == "Renamed"


def test_route_revision_conflict(client, project: Path):
    case_id = client.post("/api/cr-assessments", data=valid_form(project)).json["data"]["case"]["id"]
    response = client.put(f"/api/cr-assessments/{case_id}", data={**valid_form(project), "expected_revision": "0"})
    assert response.status_code == 409
    assert response.json["error"]["code"] == "REVISION_CONFLICT"


def test_route_validation_and_directory_contracts(client, project: Path):
    validation = client.post("/api/cr-assessments/validate-path", json={"path": str(project / "repo")})
    assert validation.json["data"]["valid"] is True
    directories = client.get("/api/cr-assessments/directories", query_string={"path": str(project)})
    assert directories.status_code == 200
    assert any(item["name"] == "repo" for item in directories.json["data"]["directories"])


def test_prepare_route_returns_command_without_executing(client, project: Path):
    data = {**valid_form(project), "vendor_estimate": (io.BytesIO(b"estimate"), "vendor.xlsx")}
    case = client.post("/api/cr-assessments", data=data, content_type="multipart/form-data").json["data"]
    response = client.post(
        f'/api/cr-assessments/{case["case"]["id"]}/prepare',
        data={**valid_form(project), "expected_revision": "1", "depth": "standard"},
    )
    assert response.status_code == 200
    assert response.json["data"]["command"].startswith("assess x-ipe-docs/cr-cases/")


def test_changes_route_rejects_non_object_markers(client):
    response = client.post("/api/cr-assessments/changes", json={"markers": []})
    assert response.status_code == 400
