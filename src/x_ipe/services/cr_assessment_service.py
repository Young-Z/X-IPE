"""Filesystem case service for FEATURE-060-A."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from x_ipe.services.case_record_codec import (
    CaseRecordCodec,
    CaseRecordError,
    RevisionConflictError,
)
from x_ipe.tracing import x_ipe_tracing


CASE_ID_RE = re.compile(r"^CR-\d{4}-\d{3,}$")
REMOTE_RE = re.compile(r"^(?:https?|ssh|git)://|^[\w.-]+@[\w.-]+:", re.I)


class CrAssessmentService:
    """Manage CR assessment cases without performing AI assessment."""

    ROOT = Path("x-ipe-docs/cr-cases")

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root).resolve()
        self.case_root = self.project_root / self.ROOT
        self.codec = CaseRecordCodec()

    @x_ipe_tracing(level="INFO")
    def list_cases(self, query: str = "") -> list[dict[str, Any]]:
        """Return newest-first case summaries, optionally filtered."""
        self.case_root.mkdir(parents=True, exist_ok=True)
        needle = query.casefold().strip()
        summaries = []
        for folder in self.case_root.iterdir():
            if not folder.is_dir() or not CASE_ID_RE.fullmatch(folder.name):
                continue
            record = folder / "CaseRecord.html"
            try:
                metadata = self.codec.read(record)
                summary = self._summary(metadata, record)
            except (OSError, CaseRecordError):
                continue
            if needle and needle not in summary["id"].casefold() and needle not in summary["name"].casefold():
                continue
            summaries.append(summary)
        return sorted(summaries, key=lambda item: item["updated_at"], reverse=True)

    @x_ipe_tracing(level="INFO")
    def get_case(self, case_id: str) -> dict[str, Any]:
        """Return complete case metadata plus readiness and marker."""
        record = self._case_dir(case_id) / "CaseRecord.html"
        if not record.is_file():
            raise FileNotFoundError(case_id)
        metadata = self.codec.read(record)
        return {
            **metadata,
            "marker": self.codec.marker(record),
            "readiness": self._readiness(metadata),
        }

    @x_ipe_tracing(level="INFO")
    def create_case(
        self,
        form: dict[str, Any],
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a case with an immutable generated identifier."""
        errors = self._validate_form(form, for_assessment=False)
        if errors:
            raise ValueError(json.dumps(errors))
        case_id, folder = self._allocate_case_dir()
        now = self._now()
        try:
            file_meta = self._store_files(folder, files or {})
            metadata = {
                "schema_version": "1.0",
                "record_revision": 1,
                "case": {
                    "id": case_id,
                    "name": form["case_name"].strip(),
                    "status": "Created",
                    "review_state": "Not Reviewed",
                    "created_at": now,
                    "updated_at": now,
                },
                "inputs": self._input_metadata(form, file_meta),
                "invocation": {},
                "reports": {"latest": {}, "history": []},
            }
            self.codec.create_initial(folder / "CaseRecord.html", metadata)
            return self.get_case(case_id)
        except Exception:
            self._remove_empty_or_partial(folder)
            raise

    @x_ipe_tracing(level="INFO")
    def update_case(
        self,
        case_id: str,
        form: dict[str, Any],
        files: dict[str, Any] | None = None,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        """Update service-owned case fields while preserving skill metadata."""
        folder = self._case_dir(case_id)
        current = self.codec.read(folder / "CaseRecord.html")
        validation_form = dict(form)
        validation_form["has_cr_file"] = bool(
            form.get("has_cr_file")
            or current.get("inputs", {}).get("cr_description", {}).get("path")
        )
        errors = self._validate_form(validation_form, for_assessment=False)
        if errors:
            raise ValueError(json.dumps(errors))
        file_meta = self._store_files(folder, files or {})
        inputs = self._input_metadata(form, file_meta, current.get("inputs", {}))
        patch = {
            "case": {"name": form["case_name"].strip(), "updated_at": self._now()},
            "inputs": inputs,
        }
        self.codec.merge(folder / "CaseRecord.html", patch, expected_revision)
        return self.get_case(case_id)

    @x_ipe_tracing(level="INFO")
    def prepare_assessment(
        self,
        case_id: str,
        form: dict[str, Any],
        depth: str,
        files: dict[str, Any] | None = None,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        """Save, snapshot, mark Evaluating, and return an unexecuted command."""
        depth = depth.lower()
        if depth not in {"quick", "standard", "deep"}:
            raise ValueError(json.dumps({"analysis_depth": "Choose Quick, Standard, or Deep"}))
        updated = self.update_case(case_id, form, files, expected_revision)
        errors = self._validate_metadata_for_assessment(updated)
        if errors:
            raise ValueError(json.dumps(errors))
        folder = self._case_dir(case_id)
        snapshot_dir = folder / "snapshots"
        snapshot_dir.mkdir(exist_ok=True)
        version = self._next_version(snapshot_dir, "invocation-v", ".json")
        relative = f"snapshots/invocation-v{version}.json"
        snapshot = {
            "schema_version": "1.0",
            "snapshot_id": f"{case_id}/invocation-v{version}",
            "created_at": self._now(),
            "case_id": case_id,
            "case_record_revision": updated["record_revision"],
            "analysis_depth": depth,
            "codebase_path": updated["inputs"]["codebase_path"],
            "inputs": updated["inputs"],
        }
        self._atomic_json(snapshot_dir / f"invocation-v{version}.json", snapshot)
        now = self._now()
        merged = self.codec.merge(
            folder / "CaseRecord.html",
            {
                "case": {"status": "Evaluating", "updated_at": now},
                "invocation": {
                    "latest_snapshot": relative,
                    "analysis_depth": depth,
                    "prompt_populated_at": now,
                },
            },
            updated["record_revision"],
        )
        case_folder = str((self.ROOT / case_id).as_posix())
        return {
            "case_id": case_id,
            "status": "Evaluating",
            "record_revision": merged["record_revision"],
            "snapshot_path": str((self.ROOT / case_id / relative).as_posix()),
            "command": self._resolve_command(case_folder, depth),
        }

    @x_ipe_tracing(level="INFO")
    def validate_codebase(self, raw_path: str) -> dict[str, Any]:
        """Validate a readable local directory without enumerating content."""
        if not raw_path or REMOTE_RE.search(raw_path.strip()):
            return {"valid": False, "reason": "Only readable local directories are supported"}
        path = Path(raw_path).expanduser()
        if not path.exists():
            return {"valid": False, "reason": "Path does not exist"}
        if not path.is_dir():
            return {"valid": False, "reason": "Path is not a directory"}
        if not os.access(path, os.R_OK | os.X_OK):
            return {"valid": False, "reason": "Directory is not readable"}
        return {"valid": True, "reason": "", "normalized_display_path": str(path.resolve())}

    @x_ipe_tracing(level="INFO")
    def list_directories(self, raw_path: str | None = None) -> dict[str, Any]:
        """List readable child directories for the local directory picker."""
        path = Path(raw_path).expanduser() if raw_path else self.project_root
        validation = self.validate_codebase(str(path))
        if not validation["valid"]:
            raise ValueError(validation["reason"])
        path = path.resolve()
        children = []
        try:
            for child in sorted(path.iterdir(), key=lambda item: item.name.casefold()):
                if child.name.startswith(".") or not child.is_dir():
                    continue
                if os.access(child, os.R_OK | os.X_OK):
                    children.append({"name": child.name, "path": str(child)})
        except PermissionError as exc:
            raise PermissionError("Directory is not readable") from exc
        parent = str(path.parent) if path.parent != path else None
        return {"path": str(path), "parent": parent, "directories": children}

    @x_ipe_tracing(level="INFO")
    def changes(self, known: dict[str, str]) -> dict[str, Any]:
        """Return created, changed, and removed summaries by marker."""
        current = {item["id"]: item for item in self.list_cases()}
        changed = [item for cid, item in current.items() if known.get(cid) != item["marker"]]
        removed = sorted(set(known) - set(current))
        return {"changed": changed, "removed": removed, "markers": {cid: item["marker"] for cid, item in current.items()}}

    def _allocate_case_dir(self) -> tuple[str, Path]:
        self.case_root.mkdir(parents=True, exist_ok=True)
        year = datetime.now(timezone.utc).year
        numbers = []
        for path in self.case_root.glob(f"CR-{year}-*"):
            try:
                numbers.append(int(path.name.rsplit("-", 1)[1]))
            except ValueError:
                continue
        number = max(numbers, default=0) + 1
        while True:
            case_id = f"CR-{year}-{number:03d}"
            folder = self.case_root / case_id
            try:
                folder.mkdir()
                return case_id, folder
            except FileExistsError:
                number += 1

    def _case_dir(self, case_id: str) -> Path:
        if not CASE_ID_RE.fullmatch(case_id):
            raise ValueError("Invalid case ID")
        folder = (self.case_root / case_id).resolve()
        if self.case_root.resolve() not in folder.parents:
            raise ValueError("Invalid case path")
        return folder

    def _validate_form(self, form: dict[str, Any], for_assessment: bool) -> dict[str, str]:
        errors = {}
        if not str(form.get("case_name", "")).strip():
            errors["case_name"] = "Case Name is required"
        if not str(form.get("cr_description_text", "")).strip() and not form.get("has_cr_file"):
            errors["cr_description"] = "CR Description is required"
        if for_assessment:
            result = self.validate_codebase(str(form.get("codebase_path", "")))
            if not result["valid"]:
                errors["codebase_path"] = result["reason"]
        return errors

    def _validate_metadata_for_assessment(self, metadata: dict[str, Any]) -> dict[str, str]:
        inputs = metadata.get("inputs", {})
        errors = self._validate_form(
            {
                "case_name": metadata["case"]["name"],
                "cr_description_text": inputs.get("cr_description", {}).get("text", ""),
                "has_cr_file": bool(inputs.get("cr_description", {}).get("path")),
                "codebase_path": inputs.get("codebase_path", ""),
            },
            for_assessment=True,
        )
        if not inputs.get("vendor_estimate", {}).get("path"):
            errors["vendor_estimate"] = "Vendor Effort Estimation is required"
        return errors

    def _input_metadata(self, form: dict[str, Any], new_files: dict[str, Any], existing: dict[str, Any] | None = None) -> dict[str, Any]:
        previous = existing or {}
        description = new_files.get("cr_description") or previous.get("cr_description") or {
            "kind": "text",
            "text": str(form.get("cr_description_text", "")),
        }
        if description.get("kind") == "text":
            description["text"] = str(form.get("cr_description_text", description.get("text", "")))
        return {
            "cr_description": description,
            "codebase_path": str(form.get("codebase_path", "")).strip(),
            "supporting_documents": previous.get("supporting_documents", []) + new_files.get("supporting_documents", []),
            "vendor_estimate": new_files.get("vendor_estimate") or previous.get("vendor_estimate") or {},
            "comments": str(form.get("comments", "")),
        }

    def _store_files(self, folder: Path, files: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {"supporting_documents": []}
        mapping = {
            "cr_description_file": ("cr-description", "cr_description"),
            "vendor_estimate": ("vendor-estimate", "vendor_estimate"),
        }
        for field, (subfolder, key) in mapping.items():
            upload = files.get(field)
            if upload and getattr(upload, "filename", ""):
                result[key] = self._save_upload(folder, subfolder, upload)
                if key == "cr_description":
                    result[key]["kind"] = "file"
        for upload in files.get("supporting_documents", []) or []:
            if getattr(upload, "filename", ""):
                result["supporting_documents"].append(self._save_upload(folder, "supporting", upload))
        return result

    def _save_upload(self, folder: Path, subfolder: str, upload: FileStorage) -> dict[str, Any]:
        original = upload.filename or "upload"
        safe = secure_filename(original) or "upload"
        target_dir = folder / "inputs" / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / safe
        stem, suffix = target.stem, target.suffix
        index = 2
        while target.exists():
            target = target_dir / f"{stem}-{index}{suffix}"
            index += 1
        digest = hashlib.sha256()
        with target.open("wb") as handle:
            while chunk := upload.stream.read(64 * 1024):
                digest.update(chunk)
                handle.write(chunk)
        return {"path": str(target.relative_to(folder).as_posix()), "original_name": original, "sha256": digest.hexdigest()}

    def _summary(self, metadata: dict[str, Any], record: Path) -> dict[str, Any]:
        case = metadata["case"]
        return {
            "id": case["id"], "name": case["name"], "status": case.get("status", "Created"),
            "updated_at": case.get("updated_at", case.get("created_at", "")),
            "review_state": case.get("review_state", "Not Reviewed"),
            "record_revision": metadata["record_revision"], "marker": self.codec.marker(record),
        }

    def _readiness(self, metadata: dict[str, Any]) -> dict[str, bool]:
        inputs = metadata.get("inputs", {})
        description = inputs.get("cr_description", {})
        return {
            "cr_brief": bool(description.get("text") or description.get("path")),
            "codebase": self.validate_codebase(inputs.get("codebase_path", ""))["valid"],
            "vendor_estimate": bool(inputs.get("vendor_estimate", {}).get("path")),
        }

    def _resolve_command(self, case_folder: str, depth: str) -> str:
        command = "evaluate change request effort for <case-folder> with evaluate-change-request-efforts skill --analysis-depth <analysis-depth>"
        for config_path in (
            self.project_root / "x-ipe-docs/config/copilot-prompt.json",
            Path(__file__).parents[1] / "resources/config/copilot-prompt.json",
        ):
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
                prompt = next(item for item in config.get("cr-assessment", {}).get("prompts", []) if item.get("id") == "evaluate-cr-effort")
                command = prompt["prompt-details"][0]["command"]
                break
            except (OSError, ValueError, KeyError, StopIteration):
                continue
        return command.replace("<case-folder>", case_folder).replace("<analysis-depth>", depth)

    @staticmethod
    def _next_version(folder: Path, prefix: str, suffix: str) -> int:
        versions = []
        for path in folder.glob(f"{prefix}*{suffix}"):
            try:
                versions.append(int(path.stem.removeprefix(prefix)))
            except ValueError:
                continue
        return max(versions, default=0) + 1

    @staticmethod
    def _atomic_json(path: Path, data: dict[str, Any]) -> None:
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temp, path)

    @staticmethod
    def _remove_empty_or_partial(folder: Path) -> None:
        import shutil
        shutil.rmtree(folder, ignore_errors=True)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
