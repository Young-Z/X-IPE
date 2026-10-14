"""Small per-skill lesson queue. Explicit roots; no board writes, Git or database.

JSON CLI input/output; Markdown with YAML records on disk. POSIX cooperative
locking (macOS/Linux); unavailable locking fails closed. PyYAML is installed.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

import yaml

CANONICAL = "x-ipe-meta-lesson-learned.md"
LEGACY = "lesson-learned.md"
STATUSES = {"active", "planned", "applied", "retired"}
PENDING = {"active", "planned"}
UTC = timezone.utc


class QueueLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently discarding protected data."""


def unique_mapping(loader, node):
    pairs = loader.construct_pairs(node, deep=True)
    result = {}
    for key, value in pairs:
        if not isinstance(key, str) or key in result:
            raise ValueError("Non-string or duplicate YAML key protected")
        result[key] = value
    return result


QueueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def timestamp(value):
    """Only explicit UTC instants, never dates or local/naive timestamps."""
    if not isinstance(value, str):
        raise ValueError("UTC timestamp string required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("Explicit UTC required")
    return parsed


def instant(now=None):
    return timestamp(now) if now is not None else datetime.now(UTC)


def stamp(value):
    return value.isoformat().replace("+00:00", "Z")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text(value, field, limit=1000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"Required bounded text: {field}")
    if "\n" in value or "\r" in value:
        raise ValueError(f"Single-line text required: {field}")
    return value.strip()


def safe(root, path):
    root, path = Path(root).absolute(), Path(path).absolute()
    if ".." in root.parts or ".." in path.parts:
        raise ValueError("Traversal prohibited")
    path.relative_to(root)
    for item in (path, *path.parents):
        if item.is_symlink():
            raise ValueError("Symlink prohibited")
        if item.exists():
            mode = item.stat()
            if not (stat.S_ISREG(mode.st_mode) or stat.S_ISDIR(mode.st_mode)):
                raise ValueError("Special node prohibited")
            if item.is_file() and mode.st_nlink != 1:
                raise ValueError("Hard link prohibited")
    return path


def location(root, skill):
    if not isinstance(skill, str) or not re.fullmatch(r"x-ipe[-+][A-Za-z0-9+-]+", skill) or len(skill) > 64:
        raise ValueError("Invalid skill name")
    root = safe(root, root)
    if not safe(root, root / ".github/skills" / skill).is_dir():
        raise ValueError("Target skill does not exist")
    folder = safe(root, root / "x-ipe-docs/skill-meta" / skill)
    canonical, old = safe(root, folder / CANONICAL), safe(root, folder / LEGACY)
    if canonical.exists() and old.exists():
        raise ValueError("Ambiguous canonical and legacy lesson files; review required")
    return old if old.exists() else canonical


def render(document):
    header = {key: document[key] for key in ("schema", "skill_name", "next_id")}
    chunks = ["---\n" + yaml.safe_dump(header, sort_keys=False) + "---\n"]
    for entry in document["records"]:
        chunks.append(f"\n## {entry['id']}\n```yaml\n" +
                      yaml.safe_dump(entry, sort_keys=False, width=10000) + "```\n")
    return "".join(chunks).encode()


def validate_record(entry):
    if not isinstance(entry, dict) or not re.fullmatch(r"LL-\d{3,}", str(entry.get("id", ""))):
        raise ValueError("Invalid lesson identity")
    if entry.get("status") not in STATUSES:
        raise ValueError("Unknown status protected; review required")
    if entry.get("severity") not in {"critical", "major", "minor", "enhancement"}:
        raise ValueError("Invalid severity")
    for field in ("summary", "cause", "corrective_rule", "verification"):
        text(entry.get(field), field)
    admission(entry)
    times = [timestamp(entry.get(field)) for field in ("created_at", "last_validated_at", "expires_at")]
    if not times[0] <= times[1] < times[2]:
        raise ValueError("Invalid lifecycle chronology")
    if times[2] != times[1] + timedelta(days=lifetime(entry)):
        raise ValueError("Expiry must match admission TTL from validation")
    if type(entry.get("occurrences")) is not int or entry["occurrences"] < 1:
        raise ValueError("Invalid occurrence count")
    if len(entry["summary"]) > 240:
        raise ValueError("Summary exceeds 240 characters")
    if entry["severity"] == "critical":
        if timestamp(entry.get("review_due")) != times[1] + timedelta(days=90):
            raise ValueError("Critical review must be 90 days from validation")
    if not isinstance(entry.get("applies_to", []), list):
        raise ValueError("Applicability must be a list")
    for skill in entry.get("applies_to", []):
        if not isinstance(skill, str) or not re.fullmatch(r"x-ipe[-+][A-Za-z0-9+-]+", skill):
            raise ValueError("Invalid applicability")
    if entry["status"] == "planned":
        if not isinstance(entry.get("plan"), dict):
            raise ValueError("Planned ownership mapping required")
        for field in ("task", "candidate", "change", "test"):
            text(entry.get("plan", {}).get(field), field)
        if timestamp(entry.get("planned_at")) < times[0]:
            raise ValueError("Planning cannot precede creation")
    if entry["status"] in {"applied", "retired"}:
        terminal = timestamp(entry.get("terminal_at"))
        if terminal < times[1]:
            raise ValueError("Terminal time cannot precede validation")
        if timestamp(entry.get("purge_after")) != terminal + timedelta(days=30):
            raise ValueError("Terminal retention must be 30 days")
        if entry["status"] == "applied" and not isinstance(entry.get("application"), dict):
            raise ValueError("Application receipt required")
        if entry["status"] == "retired":
            text(entry.get("retirement_reason"), "retirement_reason")


def load(root, skill):
    """Read-only snapshot; legacy/unknown records are reported, never converted."""
    path = location(root, skill)
    raw = path.read_bytes() if path.exists() else b""
    revision = digest(raw)
    empty = {"schema": 1, "skill_name": skill, "next_id": 1, "records": []}
    if not raw:
        return {"path": str(path), "revision": revision, "document": empty, "protected": []}
    content = raw.decode("utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", content, re.S)
    header = yaml.load(match[1], Loader=QueueLoader) if match else None
    if not isinstance(header, dict) or header.get("schema") != 1:
        ids = re.findall(r"(?m)^## (LL-\d+)\b", content)
        return {"path": str(path), "revision": revision, "document": None,
                "protected": [{"id": item, "reason": "legacy dates/status require reviewed migration"}
                              for item in ids] or [{"reason": "unrecognized legacy file"}]}
    if header.get("skill_name") != skill or type(header.get("next_id")) is not int:
        raise ValueError("Invalid file identity or next_id")
    if set(header) != {"schema", "skill_name", "next_id"}:
        raise ValueError("Unknown metadata protected")
    tail, entries = content[match.end():], []
    pattern = re.compile(r"\s*## (LL-\d{3,})\r?\n```yaml\r?\n(.*?)\r?\n```(?:\r?\n|$)", re.S)
    while tail.strip():
        block = pattern.match(tail)
        if not block:
            raise ValueError("Unrecognized prose protected; reviewed migration required")
        entry = yaml.load(block[2], Loader=QueueLoader)
        validate_record(entry)
        if entry["id"] != block[1] or entry["id"] in {e["id"] for e in entries}:
            raise ValueError("Duplicate or mismatched ID")
        entries.append(entry)
        tail = tail[block.end():]
    if header["next_id"] <= max([int(e["id"][3:]) for e in entries], default=0):
        raise ValueError("next_id must exceed every retained ID")
    return {"path": str(path), "revision": revision,
            "document": {**header, "records": entries}, "protected": []}


@contextmanager
def locked(root, skill, expected_revision):
    """Stable lock inode; don't unlink it. Nonblocking writers retry explicitly."""
    import fcntl

    path = location(root, skill)
    if not isinstance(expected_revision, str) or not re.fullmatch(r"[a-f0-9]{64}", expected_revision):
        raise ValueError("Expected SHA256 revision required for writes")
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = safe(root, path.parent / ".lesson-ops.lock")
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        snapshot = load(root, skill)
        if snapshot["revision"] != expected_revision:
            raise ValueError("Revision conflict; reread and review")
        if snapshot["document"] is None:
            raise ValueError("Legacy file protected; migration not authorized")
        yield snapshot
    finally:
        os.close(fd)


def commit(root, snapshot, document):
    """Atomic replacement; recheck snapshot to detect noncooperating edits."""
    path = safe(root, snapshot["path"])
    for entry in document["records"]:
        validate_record(entry)
    data = render(document)
    fd, temporary = tempfile.mkstemp(prefix=".lesson-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        current = path.read_bytes() if path.exists() else b""
        if digest(current) != snapshot["revision"]:
            raise ValueError("Revision conflict during commit")
        safe(root, path)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return digest(data)


def admission(entry):
    details = entry.get("admission")
    if not isinstance(details, dict):
        raise ValueError("Agent admission decision required")
    if set(details) - {"kind", "reason", "reusable_gap", "coverage_check", "ground_truth",
                       "impact", "basis", "basis_evidence", "explicit_request", "purpose", "ttl_days"}:
        raise ValueError("Unknown admission fields; do not store logs")
    for field in ("reason", "reusable_gap", "coverage_check", "ground_truth"):
        text(details.get(field), field)
    evidence = entry.get("evidence")
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 2:
        raise ValueError("One or two distinct evidence links required")
    for link in evidence:
        text(link, "evidence", 500)
    if len(set(evidence)) != len(evidence):
        raise ValueError("Distinct evidence links required")
    kind = details.get("kind")
    if kind == "critical" and entry.get("severity") == "critical":
        text(details.get("impact"), "critical impact")
    elif kind == "high_value" and entry.get("severity") == "major":
        if details.get("basis") not in {"verified_recurrence", "systemic_contract_gap"}:
            raise ValueError("Major severity alone does not qualify")
        text(details.get("basis_evidence"), "high-value basis evidence")
    elif kind == "user_override" and entry.get("severity") in {"critical", "major", "minor", "enhancement"}:
        text(details.get("explicit_request"), "explicit user request")
        text(details.get("purpose"), "override purpose")
        days = details.get("ttl_days")
        if type(days) is not int or not 1 <= days <= 180:
            raise ValueError("Override needs explicit finite TTL (1-180 days)")
    else:
        raise ValueError("Not admitted: critical/high-value evidence or explicit override required")


def lifetime(entry):
    return entry["admission"].get("ttl_days", 180 if entry["severity"] == "critical" else 90) if entry["admission"]["kind"] == "user_override" else (180 if entry["severity"] == "critical" else 90)


def capture(root, skill, proposal, *, expected_revision, now=None, recurrence=False):
    """Admit/merge one agent-evaluated lesson; no speculative scoring."""
    clock = instant(now)
    if proposal.get("retain") is False or proposal.get("covered") is True:
        return {"disposition": "skipped", "reason": "retention declined or safeguard already covers rule"}
    if not isinstance(proposal.get("admission"), dict) or not proposal["admission"].get("ground_truth"):
        return {"disposition": "incident_handoff_required", "reason": "ground truth unknown; use an owned incident task"}
    for field in ("summary", "cause", "corrective_rule", "verification"):
        text(proposal.get(field), field, 240 if field == "summary" else 1000)
    admission(proposal)
    # Persist a bounded schema, not arbitrary caller logs/keys.
    entry = {k: deepcopy(proposal[k]) for k in ("severity", "summary", "cause", "corrective_rule", "verification", "evidence", "admission")}
    if "applies_to" in proposal:
        entry["applies_to"] = deepcopy(proposal["applies_to"])
    with locked(root, skill, expected_revision) as snapshot:
        document = deepcopy(snapshot["document"])
        same = next((e for e in document["records"] if
                     (e["cause"].strip().casefold(), e["corrective_rule"].strip().casefold()) ==
                     (entry["cause"].strip().casefold(), entry["corrective_rule"].strip().casefold())), None)
        if same:
            new = [e for e in entry["evidence"] if e not in same["evidence"]]
            if not recurrence or not new:
                return {"disposition": "duplicate", "id": same["id"], "revision": snapshot["revision"]}
            if same["status"] == "retired":
                return {"disposition": "blocked", "reason": "retired rule needs explicit reviewed re-admission"}
            if same["status"] == "applied" and sum(e["status"] in PENDING for e in document["records"]) >= 8:
                return {"disposition": "blocked", "reason": "eight pending lessons; no silent eviction"}
            if clock < max(timestamp(same[field]) for field in
                           ("last_validated_at", "planned_at", "terminal_at") if field in same):
                raise ValueError("Recurrence cannot move validation backwards")
            if (same["severity"], same["admission"]["kind"]) != (entry["severity"], entry["admission"]["kind"]):
                raise ValueError("Changed admission classification needs explicit review")
            same["admission"] = entry["admission"]
            same.update(evidence=(same["evidence"] + new)[-2:], occurrences=same["occurrences"] + 1,
                        last_validated_at=stamp(clock), expires_at=stamp(clock + timedelta(days=lifetime(same))))
            # A verified regression reopens the retained identity, not a new warning.
            if same["status"] == "applied":
                same["status"] = "active"
                for field in ("application", "terminal_at", "purge_after", "plan", "planned_at"):
                    same.pop(field, None)
            entry = same
            disposition = "merged"
        else:
            if sum(e["status"] in PENDING for e in document["records"]) >= 8:
                return {"disposition": "blocked", "reason": "eight pending lessons; consolidate or approved maintenance"}
            entry.update(id=f"LL-{document['next_id']:03d}", status="active", occurrences=1,
                         created_at=stamp(clock), last_validated_at=stamp(clock),
                         expires_at=stamp(clock + timedelta(days=lifetime(entry))))
            document["next_id"] += 1
            document["records"].append(entry)
            disposition = "captured"
        if entry["severity"] == "critical":
            entry["review_due"] = stamp(clock + timedelta(days=90))
        return {"disposition": disposition, "id": entry["id"],
                "revision": commit(root, snapshot, document)}


def select(root, skills, *, relevant_to=None, now=None):
    """At most five summaries across all supplied primary owners, read-only."""
    clock, eligible, protected, notices = instant(now), [], [], []
    for skill in dict.fromkeys(skills):
        try:
            snapshot = load(root, skill)
        except (ValueError, TypeError, yaml.YAMLError) as exc:
            protected.append({"skill": skill, "reason": str(exc)})
            continue
        protected.extend({"skill": skill, **p} for p in snapshot["protected"])
        for entry in (snapshot["document"] or {}).get("records", []):
            if entry["status"] not in PENDING:
                continue
            if relevant_to is not None and relevant_to not in [skill, *entry.get("applies_to", [])]:
                continue
            if clock >= timestamp(entry["expires_at"]):
                if entry["severity"] == "critical":
                    notices.append({"skill": skill, "id": entry["id"],
                                    "reason": "expired critical; owned handoff/cleanup review required"})
                continue
            eligible.append((skill, entry))
            if entry["severity"] == "critical" and clock >= timestamp(entry.get("review_due", entry["expires_at"])):
                notices.append({"skill": skill, "id": entry["id"], "reason": "critical review due"})
            if entry["status"] == "planned" and clock >= timestamp(entry["planned_at"]) + timedelta(days=14):
                notices.append({"skill": skill, "id": entry["id"], "reason": "owner progress review due; do not steal ownership"})
    eligible.sort(key=lambda pair: (pair[1]["severity"] == "critical", pair[1]["occurrences"],
                                   timestamp(pair[1]["last_validated_at"])), reverse=True)
    summaries = [{"skill": skill, **{key: entry[key] for key in
                 ("id", "severity", "status", "summary", "corrective_rule", "evidence", "expires_at")}}
                 for skill, entry in eligible[:5]]
    overflow = [{"skill": skill, "id": entry["id"]} for skill, entry in eligible[5:] if entry["severity"] == "critical"]
    return {"summaries": summaries, "critical_overflow": overflow, "protected": protected, "notices": notices}


def artifact(root, relative):
    text(relative, "artifact path", 500)
    path = safe(root, Path(root) / relative)
    if Path(relative).is_absolute() or not path.is_file():
        raise ValueError("Existing project-relative artifact required")
    raw = path.read_bytes()
    return json.loads(raw), digest(raw)


def verify_task(root, link, *, lesson_link=None):
    """Verify existing-schema task plus owner and lesson backlink. No board writes."""
    if not isinstance(link, dict):
        raise ValueError("Owned existing task link required, not arbitrary text")
    path = text(link.get("path"), "task path", 500)
    if not re.fullmatch(r"x-ipe-docs/planning/tasks/tasks-\d{4}-\d{2}-\d{2}\.json", path):
        raise ValueError("Canonical existing task file required")
    board, _ = artifact(root, path)
    tasks = [t for t in board.get("tasks", []) if t.get("task_id") == link.get("task_id")]
    if len(tasks) != 1:
        raise ValueError("Existing task identity not found uniquely")
    task = tasks[0]
    for field in ("task_id", "task_type", "description", "role", "status", "created_at", "last_updated"):
        text(task.get(field), field)
    if not isinstance(task.get("output_links"), list) or not isinstance(task.get("next_task"), str):
        raise ValueError("Existing task schema required")
    owner = text(link.get("owner"), "task owner")
    if owner in {"unassigned", "unknown", "none"} or owner != task["role"]:
        raise ValueError("Task must have the supplied actual owner")
    if task["status"] not in {"pending", "in_progress", "blocked", "deferred"}:
        raise ValueError("Task is not open")
    if lesson_link is not None and lesson_link not in task["output_links"]:
        raise ValueError("Critical task needs explicit scoped lesson backlink")
    return task


def application(root, skill, decision, *, verify_production=True):
    revision = text(decision.get("production_revision"), "production revision")
    pub, pub_hash = artifact(root, decision.get("publication_receipt"))
    tests, test_hash = artifact(root, decision.get("test_receipt"))
    if not (pub.get("ok") is True and pub.get("operation") == "publish" and
            pub.get("state") == "published" and pub.get("byte_parity") is True and pub.get("name") == skill):
        raise ValueError("Verified publication receipt required; candidate is not applied")
    files = pub.get("files")
    if not isinstance(files, dict) or "SKILL.md" not in files:
        raise ValueError("Publication manifest required")
    fingerprint = digest(json.dumps(files, sort_keys=True, separators=(",", ":")).encode())
    if pub.get("candidate_hash") != fingerprint or revision != fingerprint:
        raise ValueError("Production revision must match published manifest fingerprint")
    if verify_production:
        production = safe(root, Path(root) / ".github/skills" / skill)
        actual = {}
        for directory, dirs, names in os.walk(production, followlinks=False):
            for name in dirs + names:
                path = safe(root, Path(directory) / name)
                if path.is_file():
                    actual[path.relative_to(production).as_posix()] = digest(path.read_bytes())
        if actual != files:
            raise ValueError("Complete production manifest mismatch")
        for relative, expected in files.items():
            path = safe(root, Path(root) / ".github/skills" / skill / relative)
            if Path(relative).is_absolute() or not path.is_file() or digest(path.read_bytes()) != expected:
                raise ValueError("Published safeguard bytes changed")
    if not (tests.get("ok") is True and tests.get("tests_passed") is True and
            tests.get("skill_name") == skill and tests.get("production_revision") == revision and
            tests.get("candidate_hash") == fingerprint and
            tests.get("verification") == decision.get("planned_test") and
            decision.get("lesson_id") in tests.get("lesson_ids", [])):
        raise ValueError("Relevant passing production test receipt required")
    identity = digest(json.dumps([revision, pub_hash, test_hash], sort_keys=True).encode())
    return {"id": identity, "production_revision": revision,
            "publication_receipt": decision["publication_receipt"], "publication_sha256": pub_hash,
            "test_receipt": decision["test_receipt"], "test_sha256": test_hash}


def settle(root, skill, lesson_id, decision, *, expected_revision, now=None):
    clock = instant(now)
    with locked(root, skill, expected_revision) as snapshot:
        document = deepcopy(snapshot["document"])
        entry = next((e for e in document["records"] if e["id"] == lesson_id), None)
        if entry is None:
            raise ValueError("Scoped lesson not found")
        target = decision.get("status")
        if clock < max(timestamp(entry[field]) for field in
                       ("last_validated_at", "planned_at", "terminal_at") if field in entry):
            raise ValueError("Settlement cannot precede validation")
        if target == "applied":
            if entry["status"] not in {"planned", "applied"} or decision.get("task") != entry.get("plan", {}).get("task"):
                raise ValueError("Application requires matching planned ownership")
            receipt = application(root, skill, {**decision, "lesson_id": lesson_id,
                                               "planned_test": entry.get("plan", {}).get("test")},
                                  verify_production=entry["status"] != "applied")
            if entry["status"] == "applied" and entry["application"] == receipt:
                return {"disposition": "unchanged", "revision": snapshot["revision"]}
            if entry["status"] != "planned":
                raise ValueError("Application requires matching planned ownership")
            if clock >= timestamp(entry["expires_at"]):
                raise ValueError("Expired lesson needs evidence-backed revalidation before application")
            entry["application"] = receipt
        elif target == "planned":
            if entry["status"] not in {"active", "planned"} or clock >= timestamp(entry["expires_at"]):
                raise ValueError("Only valid active lessons can be adopted")
            task = verify_task(root, decision.get("owner"))
            candidate = f"x-ipe-docs/skill-meta/{skill}/candidate"
            if decision.get("candidate") != candidate or not safe(root, Path(root) / candidate).is_dir():
                raise ValueError("Named existing candidate required")
            planned = {"task": task["task_id"], "owner": task["role"], "candidate": candidate,
                       "change": text(decision.get("change"), "lesson-to-change mapping"),
                       "test": text(decision.get("test"), "lesson-to-test mapping")}
            if entry["status"] == "planned":
                if entry["plan"] != planned:
                    raise ValueError("Already planned; release by owning task before replacing mapping")
                return {"disposition": "unchanged", "revision": snapshot["revision"]}
            entry["plan"] = planned
            entry["planned_at"] = stamp(clock)
        elif target == "active":
            if entry["status"] != "planned" or decision.get("task") != entry["plan"]["task"]:
                raise ValueError("Release requires matching planned task")
            if clock >= timestamp(entry["expires_at"]):
                raise ValueError("Cannot release expired content to active")
            text(decision.get("reason"), "release reason")
            entry.pop("plan")
            entry.pop("planned_at")
        elif target == "retired":
            if entry["status"] not in PENDING:
                raise ValueError("Only pending lessons can be retired")
            if entry["status"] == "planned" and decision.get("task") != entry["plan"]["task"]:
                raise ValueError("Retirement requires matching planned task")
            entry["retirement_reason"] = text(decision.get("reason"), "retirement reason")
            if entry["severity"] == "critical":
                link = Path(snapshot["path"]).relative_to(Path(root).absolute()).as_posix() + f"#{lesson_id}"
                verify_task(root, decision.get("handoff"), lesson_link=link)
                entry["handoff"] = deepcopy(decision["handoff"])
        else:
            raise ValueError("Unknown settlement status")
        entry["status"] = target
        if target in {"applied", "retired"}:
            entry.update(terminal_at=stamp(clock), purge_after=stamp(clock + timedelta(days=30)))
        return {"disposition": target, "revision": commit(root, snapshot, document)}


def prune(root, skill, *, now=None, apply=False, expected_revision=None,
          preservation=None, handoffs=None):
    """Preview by default. Explicit, revision-bound user approval permits purge.

    Without Git inspection all files are conservatively untracked/WIP-protected.
    Never infer preservation from a caller's arbitrary 'tracked' boolean.
    """
    clock = instant(now)

    def plan(snapshot):
        if snapshot["document"] is None:
            return None, [], snapshot["protected"]
        document = deepcopy(snapshot["document"])
        actions, blocked = [], []
        approved = (isinstance(preservation, dict) and preservation.get("kind") == "explicit_user_approval"
                    and preservation.get("revision") == snapshot["revision"]
                    and bool(preservation.get("authorized_by")) and bool(preservation.get("reason")))
        for entry in list(document["records"]):
            pending_expired = entry["status"] in PENDING and clock >= timestamp(entry["expires_at"])
            terminal_due = entry["status"] in {"applied", "retired"} and clock >= timestamp(entry["purge_after"])
            if not (pending_expired or terminal_due):
                continue
            if entry["severity"] == "critical" and entry["status"] != "applied":
                handoff = (handoffs or {}).get(entry["id"], entry.get("handoff"))
                try:
                    link = Path(snapshot["path"]).relative_to(Path(root).absolute()).as_posix() + f"#{entry['id']}"
                    verify_task(root, handoff, lesson_link=link)
                except (ValueError, OSError, json.JSONDecodeError) as exc:
                    blocked.append({"id": entry["id"], "reason": f"critical handoff blocked: {exc}"})
                    continue
                entry["handoff"] = deepcopy(handoff)
            if pending_expired:
                entry.update(status="retired", retirement_reason="expired", terminal_at=stamp(clock),
                             purge_after=stamp(clock + timedelta(days=30)))
                actions.append({"id": entry["id"], "action": "retire"})
            elif not approved:
                blocked.append({"id": entry["id"], "reason": "untracked/WIP protected; revision-bound explicit approval required"})
            else:
                document["records"].remove(entry)
                actions.append({"id": entry["id"], "action": "purge"})
        return document, actions, blocked

    if not apply:
        snapshot = load(root, skill)
        _, actions, blocked = plan(snapshot)
        return {"disposition": "dry_run", "revision": snapshot["revision"], "actions": actions, "blocked": blocked}
    with locked(root, skill, expected_revision) as snapshot:
        document, actions, blocked = plan(snapshot)
        revision = commit(root, snapshot, document) if actions else snapshot["revision"]
        return {"disposition": "applied", "revision": revision, "actions": actions, "blocked": blocked}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("capture", "select", "settle", "prune"))
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--skill", action="append", required=True)
    parser.add_argument("--input", help="JSON object; no file writes for CLI output")
    parser.add_argument("--expected-revision")
    parser.add_argument("--now")
    parser.add_argument("--apply", action="store_true", help="prune only; default dry-run")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input or "{}")
        if not isinstance(data, dict) or (args.apply and args.operation != "prune"):
            raise ValueError("JSON object required; --apply only for prune")
        if args.operation == "select":
            result = select(args.project_root, args.skill, relevant_to=data.get("relevant_to"), now=args.now)
        else:
            if len(args.skill) != 1:
                raise ValueError("Writes require exactly one primary skill")
            common = {"expected_revision": args.expected_revision, "now": args.now}
            if args.operation == "capture":
                result = capture(args.project_root, args.skill[0], data.get("proposal", data),
                                 recurrence=data.get("recurrence", False), **common)
            elif args.operation == "settle":
                result = settle(args.project_root, args.skill[0], data.get("id"), data.get("decision", {}), **common)
            else:
                result = prune(args.project_root, args.skill[0], apply=args.apply,
                               preservation=data.get("preservation"), handoffs=data.get("handoffs"), **common)
        print(json.dumps({"ok": True, **result}, sort_keys=True))
        return 0
    except (ValueError, OSError, TypeError, KeyError, yaml.YAMLError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
