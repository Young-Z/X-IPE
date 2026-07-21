"""Flask routes for the CR Assessment module."""

from __future__ import annotations

import json
from typing import Any

from flask import Blueprint, current_app, jsonify, render_template, request

from x_ipe.services.case_record_codec import CaseRecordError, RevisionConflictError
from x_ipe.services.cr_assessment_service import CrAssessmentService
from x_ipe.tracing import x_ipe_tracing


cr_assessment_bp = Blueprint("cr_assessment", __name__)


def _service() -> CrAssessmentService:
    return CrAssessmentService(current_app.config.get("PROJECT_ROOT", "."))


def _files() -> dict[str, Any]:
    return {
        "cr_description_file": request.files.get("cr_description_file"),
        "vendor_estimate": request.files.get("vendor_estimate"),
        "supporting_documents": request.files.getlist("supporting_documents"),
    }


def _form() -> dict[str, Any]:
    return {
        "case_name": request.form.get("case_name", ""),
        "cr_description_text": request.form.get("cr_description_text", ""),
        "codebase_path": request.form.get("codebase_path", ""),
        "comments": request.form.get("comments", ""),
        "has_cr_file": bool(request.files.get("cr_description_file")),
    }


def _ok(data: Any, status: int = 200):
    return jsonify({"success": True, "data": data}), status


def _error(code: str, message: str, status: int, details: Any = None):
    payload = {"success": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), status


def _validation(exc: ValueError):
    try:
        details = json.loads(str(exc))
    except json.JSONDecodeError:
        details = None
    return _error("INPUT_INVALID", "Correct the highlighted inputs", 400, details)


@cr_assessment_bp.get("/cr-assessment")
@x_ipe_tracing(level="INFO")
def page():
    return render_template("cr-assessment.html")


@cr_assessment_bp.get("/api/cr-assessments")
@x_ipe_tracing(level="INFO")
def list_cases():
    return _ok({"cases": _service().list_cases(request.args.get("query", ""))})


@cr_assessment_bp.post("/api/cr-assessments")
@x_ipe_tracing(level="INFO")
def create_case():
    try:
        return _ok(_service().create_case(_form(), _files()), 201)
    except ValueError as exc:
        return _validation(exc)
    except OSError:
        return _error("WRITE_FAILED", "The case could not be saved", 500)


@cr_assessment_bp.get("/api/cr-assessments/<case_id>")
@x_ipe_tracing(level="INFO")
def get_case(case_id: str):
    try:
        return _ok(_service().get_case(case_id))
    except FileNotFoundError:
        return _error("CASE_NOT_FOUND", "Case not found", 404)
    except (ValueError, CaseRecordError):
        return _error("CASE_INVALID", "Case record is unavailable", 422)


@cr_assessment_bp.put("/api/cr-assessments/<case_id>")
@x_ipe_tracing(level="INFO")
def update_case(case_id: str):
    try:
        revision = int(request.form["expected_revision"])
        return _ok(_service().update_case(case_id, _form(), _files(), revision))
    except RevisionConflictError:
        return _error("REVISION_CONFLICT", "Case changed since it was loaded", 409)
    except FileNotFoundError:
        return _error("CASE_NOT_FOUND", "Case not found", 404)
    except (ValueError, KeyError) as exc:
        return _validation(exc if isinstance(exc, ValueError) else ValueError("{}"))


@cr_assessment_bp.post("/api/cr-assessments/<case_id>/prepare")
@x_ipe_tracing(level="INFO")
def prepare(case_id: str):
    try:
        revision = int(request.form["expected_revision"])
        depth = request.form.get("depth", "standard")
        return _ok(_service().prepare_assessment(case_id, _form(), depth, _files(), revision))
    except RevisionConflictError:
        return _error("REVISION_CONFLICT", "Case changed since it was loaded", 409)
    except FileNotFoundError:
        return _error("CASE_NOT_FOUND", "Case not found", 404)
    except (ValueError, KeyError) as exc:
        return _validation(exc if isinstance(exc, ValueError) else ValueError("{}"))


@cr_assessment_bp.post("/api/cr-assessments/validate-path")
@x_ipe_tracing(level="INFO")
def validate_path():
    body = request.get_json(silent=True) or {}
    return _ok(_service().validate_codebase(body.get("path", "")))


@cr_assessment_bp.get("/api/cr-assessments/directories")
@x_ipe_tracing(level="INFO")
def directories():
    try:
        return _ok(_service().list_directories(request.args.get("path")))
    except PermissionError:
        return _error("PATH_UNREADABLE", "Directory is not readable", 403)
    except ValueError as exc:
        return _error("PATH_INVALID", str(exc), 400)


@cr_assessment_bp.post("/api/cr-assessments/changes")
@x_ipe_tracing(level="INFO")
def changes():
    body = request.get_json(silent=True) or {}
    markers = body.get("markers", {})
    if not isinstance(markers, dict):
        return _error("INPUT_INVALID", "markers must be an object", 400)
    return _ok(_service().changes(markers))
