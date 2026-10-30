#!/usr/bin/env python3
"""Validate and atomically publish CR assessment report bundles."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import html
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

START = "<!-- CR_CASE_METADATA_START -->"
END = "<!-- CR_CASE_METADATA_END -->"
SCRIPT_OPEN = '<script id="cr-case-metadata" type="application/json">'
SCRIPT_CLOSE = "</script>"
ROOT = Path(__file__).resolve().parents[1]


class PublishError(ValueError):
    pass


def _metadata(text: str) -> dict[str, Any]:
    try:
        block = text.split(START, 1)[1].split(END, 1)[0]
        raw = block.split(SCRIPT_OPEN, 1)[1].split(SCRIPT_CLOSE, 1)[0]
        value = json.loads(raw)
    except (IndexError, json.JSONDecodeError) as exc:
        raise PublishError("CaseRecord metadata envelope is invalid") from exc
    if not isinstance(value.get("record_revision"), int) or not value.get("case", {}).get("id"):
        raise PublishError("CaseRecord identity or revision is missing")
    return value


def _validate(model: dict[str, Any], case: dict[str, Any]) -> None:
    schema = json.loads((ROOT / "references" / "report-model-v1.schema.json").read_text(encoding="utf-8"))
    required = set(schema["required"])
    if model.get("schema_version") != "1.0" or not required.issubset(model):
        raise PublishError("Report model does not satisfy schema v1")
    for name, definition in schema["properties"].items():
        if name in model and "required" in definition and not set(definition["required"]).issubset(model[name]):
            raise PublishError(f"Report model {name} fields do not satisfy schema v1")
    if model["case"].get("id") != case["case"]["id"]:
        raise PublishError("Report model case identity does not match CaseRecord")
    modules = model["estimate"].get("modules", [])
    if not modules:
        raise PublishError("At least one effort module is required")
    lows = sum(float(item["range"][0]) for item in modules)
    highs = sum(float(item["range"][1]) for item in modules)
    total = model["estimate"].get("ai_range", [])
    if len(total) != 2 or abs(lows - float(total[0])) > 0.001 or abs(highs - float(total[1])) > 0.001:
        raise PublishError("Module effort ranges do not reconcile with the AI total")
    for item in modules:
        factor = float(item.get("ai_factor", 0))
        if factor and not item.get("ai_factor_evidence"):
            raise PublishError("Every non-zero AI factor requires module evidence")


def _section(title: str, value: Any) -> str:
    if isinstance(value, list):
        body = "".join(f"<li>{html.escape(_display(item))}</li>" for item in value)
        return f"<section><h2>{html.escape(title)}</h2><ul>{body}</ul></section>"
    if isinstance(value, dict):
        rows = "".join(f"<tr><th>{html.escape(str(k))}</th><td>{html.escape(_display(v))}</td></tr>" for k, v in value.items())
        return f"<section><h2>{html.escape(title)}</h2><div class=table-wrap><table>{rows}</table></div></section>"
    return f"<section><h2>{html.escape(title)}</h2><p>{html.escape(_display(value))}</p></section>"


def _display(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _render(template_name: str, title: str, sections: list[tuple[str, Any]], metadata: str = "") -> str:
    template = (ROOT / "templates" / template_name).read_text(encoding="utf-8")
    content = "".join(_section(name, value) for name, value in sections if value not in (None, [], {}))
    return template.replace("{{TITLE}}", html.escape(title)).replace("{{CONTENT}}", content).replace("{{METADATA}}", metadata)


def _envelope(data: dict[str, Any]) -> str:
    raw = json.dumps(data, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    return f"{START}\n{SCRIPT_OPEN}\n{raw}\n{SCRIPT_CLOSE}\n{END}"


def mark_failed(case_folder: Path, reason: str) -> None:
    """Record a safe failure without changing report latest/history fields."""
    record = case_folder.resolve() / "CaseRecord.html"
    text = record.read_text(encoding="utf-8")
    data = _metadata(text)
    data["record_revision"] += 1
    data["case"]["status"] = "Failed"
    data["case"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    safe_reason = re.sub(r"(?:/[\w. -]+){2,}", "[local path]", reason)
    data["assessment_failure"] = {"reason": safe_reason[:500]}
    start = text.index(START)
    end = text.index(END) + len(END)
    updated = text[:start] + _envelope(data) + text[end:]
    fd, temporary = tempfile.mkstemp(prefix=".CaseRecord.html.", dir=record.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(updated)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, record)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def publish(case_folder: Path, model_path: Path, dry_run: bool = False) -> dict[str, Any]:
    folder = case_folder.resolve()
    record = folder / "CaseRecord.html"
    if not folder.is_dir() or not record.is_file():
        raise PublishError("Case folder or CaseRecord.html is missing")
    model = json.loads(model_path.read_text(encoding="utf-8"))
    original = record.read_text(encoding="utf-8")
    current = _metadata(original)
    _validate(model, current)
    lock_path = folder / ".assessment-publish.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        original = record.read_text(encoding="utf-8")
        current = _metadata(original)
        versions = [int(p.stem.rsplit("v", 1)[1]) for p in folder.glob("EffortEstimation_AI_v*.html") if p.stem.rsplit("v", 1)[1].isdigit()]
        version = max(versions, default=0) + 1
        names = {
            "effort": f"EffortEstimation_AI_v{version}.html",
            "design": f"SuggestedTechnicalDesign_AI_v{version}.html",
            "model": f"reports/report-model-v{version}.json",
        }
        now = datetime.now(timezone.utc).isoformat()
        latest = {"case_record": "CaseRecord.html", "effort": names["effort"], "design": names["design"], "model": names["model"]}
        history = list(current.get("reports", {}).get("history", []))
        if current.get("reports", {}).get("latest"):
            prior = current["reports"]["latest"]
            prior_effort = str(prior.get("effort", ""))
            prior_version = int(prior_effort.rsplit("v", 1)[1].split(".", 1)[0]) if "_v" in prior_effort else version - 1
            history.append({"version": prior_version, "files": prior})
        updated = json.loads(json.dumps(current))
        updated["record_revision"] += 1
        updated["case"]["status"] = "Completed"
        updated["case"]["updated_at"] = now
        updated["reports"] = {"latest": latest, "history": history, "version": version, "published_at": now}
        provenance = model["provenance"] | {"report_version": version, "model_sha256": hashlib.sha256(json.dumps(model, sort_keys=True).encode()).hexdigest()}
        updated["assessment"] = {"coverage": model["coverage"], "provenance": provenance}
        effort = _render("effort-estimation-template.html", f"{model['case']['name']} — Effort Estimation", [("Verdict", model["estimate"]), ("Coverage", model["coverage"]), ("Provenance", provenance)])
        design = _render("suggested-technical-design-template.html", f"{model['case']['name']} — Suggested Technical Design", [("Adoption Summary", model["design"].get("adoption")), ("Contracts", model["design"].get("contracts")), ("Work Packages", model["design"].get("work_packages")), ("Testing", model["design"].get("testing")), ("Rollout", model["design"].get("rollout")), ("Rollback", model["design"].get("rollback")), ("Risks and Traceability", {"risks": model["design"].get("risks"), "traceability": model["design"].get("traceability")}), ("Diagrams", model["diagrams"])])
        case_html = _render("case-record-template.html", model["case"]["name"], [("AI Verdict", model["estimate"]), ("Assessment Coverage", model["coverage"]), ("Suggested Solution", model["design"].get("decision")), ("Published Files", latest)], _envelope(updated))
        receipt = {"case_id": model["case"]["id"], "version": version, "case_record": "CaseRecord.html", **names}
        if dry_run:
            return receipt
        stage = Path(tempfile.mkdtemp(prefix=".assessment-stage-", dir=folder))
        try:
            (stage / "reports").mkdir()
            (stage / "assets").mkdir()
            (stage / names["effort"]).write_text(effort, encoding="utf-8")
            (stage / names["design"]).write_text(design, encoding="utf-8")
            (stage / names["model"]).write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
            (stage / "CaseRecord.html").write_text(case_html, encoding="utf-8")
            for asset in (ROOT / "assets").iterdir():
                target = stage / "assets" / asset.name
                if asset.is_dir():
                    shutil.copytree(asset, target)
                else:
                    shutil.copy2(asset, target)
            (folder / "reports").mkdir(exist_ok=True)
            (folder / "assets").mkdir(exist_ok=True)
            os.replace(stage / names["model"], folder / names["model"])
            os.replace(stage / names["effort"], folder / names["effort"])
            os.replace(stage / names["design"], folder / names["design"])
            shutil.copytree(stage / "assets", folder / "assets", dirs_exist_ok=True)
            os.replace(stage / "CaseRecord.html", record)
        finally:
            shutil.rmtree(stage, ignore_errors=True)
        return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-folder", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(publish(args.case_folder, args.model, args.dry_run)))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        try:
            mark_failed(args.case_folder, str(exc))
        except (OSError, ValueError, json.JSONDecodeError):
            pass
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
