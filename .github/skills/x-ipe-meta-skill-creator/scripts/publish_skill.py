"""Manifest-aware publisher. Default is read-only; --apply explicitly writes.

Transactions and backups remain outside production for audited recovery.
The caller, not this script, owns permission and independent-review decisions.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import tempfile
from typing import Callable

from validate_skill import (ReceiptParser, candidate_bytes, fingerprint, manifest, relative_key, safe_path,
                            tree_bytes, validate)


def checked_manifest(value: dict) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError("Manifest must be a path-to-SHA256 mapping")
    for key, digest in value.items():
        relative_key(key)
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"Invalid SHA256 for {key}")
    return value


def journal_write(transaction: Path, record: dict) -> None:
    pending = transaction / "journal.tmp"
    with pending.open("w", encoding="utf-8") as stream:
        json.dump(record, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(pending, transaction / "journal.json")
    descriptor = os.open(transaction, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def paths(project_root: Path, name: str) -> tuple[Path, Path, Path]:
    root = safe_path(project_root, project_root)
    if not re.fullmatch(r"[a-z0-9]+(?:[-+][a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError("Invalid canonical name")
    target = safe_path(root / ".github" / "skills" / name, root)
    store = safe_path(root / ".github" / ".skill-publication", root)
    return root, target, store


def recover(project_root: Path, name: str, transaction: Path,
            apply: bool = False) -> dict:
    """Restore only recorded baseline bytes; preserve unexpected target edits.

    Caller must establish the previous publisher is stopped before --apply.
    A retained lock matching this transaction is required for recovery writes.
    """
    root, target, store = paths(project_root, name)
    transaction = safe_path(transaction, root)
    if transaction.parent != store or not transaction.name.startswith(name + "-"):
        raise ValueError("Recovery transaction is outside canonical staging")
    record = json.loads(safe_path(transaction / "journal.json", root).read_text())
    if not isinstance(record, dict):
        raise ValueError("Recovery journal must be a mapping")
    if record.get("name") != name or record.get("target") != str(target):
        raise ValueError("Recovery identity mismatch")
    if (record.get("schema") != 1
            or record.get("state") not in ("preparing", "swapping", "published", "rolled_back")
            or not isinstance(record.get("target_existed"), bool)):
        raise ValueError("Invalid recovery state/schema")
    baseline = checked_manifest(record["baseline"])
    proposed = checked_manifest(record["proposed"])
    backup = safe_path(transaction / "backup", root)
    current = manifest(tree_bytes(target, root))
    if record["state"] == "published":
        if current != proposed:
            raise ValueError("Published target changed; recovery would discard edits")
        lock = safe_path(store / (name + ".lock"), root)
        if apply and lock.exists():
            if lock.read_text() != str(transaction):
                raise ValueError("Another publisher owns the retained lock")
            lock.unlink()
        return {"ok": True, "operation": "recover", "state": "published", "changed": False}
    if record["state"] == "rolled_back":
        if current != baseline or target.exists() != record["target_existed"]:
            raise ValueError("Rolled-back target changed")
        lock = safe_path(store / (name + ".lock"), root)
        if apply and lock.exists():
            if lock.read_text() != str(transaction):
                raise ValueError("Another publisher owns the retained lock")
            lock.unlink()
        return {"ok": True, "operation": "recover", "state": "rolled_back", "changed": False}
    if current not in (baseline, proposed, {}):
        raise ValueError("Concurrent target edits; retained backup requires manual review")
    if not record["target_existed"] and (baseline or backup.exists()):
        raise ValueError("New-skill recovery cannot contain a baseline or backup")
    if record["target_existed"] and backup.exists():
        if manifest(tree_bytes(backup, root)) != baseline:
            raise ValueError("Backup bytes do not match expected baseline")
    elif record["target_existed"] and current != baseline:
        raise ValueError("Required recovery backup missing")
    result = {"ok": True, "operation": "recover", "state": "dry_run",
              "transaction": str(transaction), "changed": False}
    if not apply:
        return result
    lock = safe_path(store / (name + ".lock"), root)
    if not lock.exists() or lock.read_text() != str(transaction):
        raise ValueError("Recovery requires the matching retained publication lock")
    if manifest(tree_bytes(target, root)) != current:
        raise ValueError("Target changed during recovery")
    if backup.exists():
        if target.exists():
            failed = safe_path(transaction / "failed", root)
            if failed.exists():
                raise ValueError("Recovery conflict: failed tree already exists")
            os.rename(target, failed)
        os.rename(backup, target)
    elif not record["target_existed"] and target.exists():
        os.rename(target, transaction / "failed")
    if (manifest(tree_bytes(target, root)) != baseline
            or target.exists() != record["target_existed"]):
        raise ValueError("Recovery parity failed")
    record["state"] = "rolled_back"
    journal_write(transaction, record)
    lock.unlink()
    result.update(state="rolled_back", changed=True)
    return result


def publish(project_root: Path, candidate: Path, name: str, skill_type: str,
            baseline: dict[str, str], managed: dict[str, str],
            expected_candidate_hash: str, reviewed_deletions: tuple[str, ...] = (),
            apply: bool = False, hook: Callable[[str], None] | None = None) -> dict:
    """Dry-run/apply API. Optional hook injects deterministic transaction faults.

    baseline is the full pre-work target snapshot; managed is a trusted previous
    release manifest. Dirty/unmanaged bytes may be retained identically only.
    """
    root, target, store = paths(project_root, name)
    baseline, managed = checked_manifest(baseline), checked_manifest(managed)
    validation = validate(root, candidate, name, skill_type)
    if not validation["ok"]:
        raise ValueError("Candidate invalid: " + "; ".join(validation["errors"]))
    if validation["candidate_hash"] != expected_candidate_hash:
        raise ValueError("Candidate fingerprint changed since review")
    before_bytes = tree_bytes(target, root)
    before = manifest(before_bytes)
    if before != baseline:
        raise ValueError("Production changed since baseline")
    proposed_bytes = candidate_bytes(candidate, root, name)
    proposed = manifest(proposed_bytes)
    if proposed != validation["files"]:
        raise ValueError("Candidate changed during validation")
    added = sorted(proposed.keys() - before.keys())
    removed = sorted(before.keys() - proposed.keys())
    changed = sorted(key for key in before.keys() & proposed.keys()
                     if before[key] != proposed[key])
    protected = sorted(key for key in before if managed.get(key) != before[key])
    if set(protected) & set(removed + changed):
        raise ValueError("Refusing to change/delete dirty or unmanaged production files")
    if set(added) & (managed.keys() - before.keys()):
        raise ValueError("Refusing to restore preexisting deleted managed files")
    deletions = [relative_key(key) for key in reviewed_deletions]
    if set(deletions) != set(removed) or len(deletions) != len(set(deletions)):
        raise ValueError("Reviewed deletions must match the exact removal manifest")
    result = {"schema": 1, "ok": True, "operation": "publish", "state": "dry_run",
              "name": name, "added": added, "changed": changed, "removed": removed,
              "protected": protected, "baseline_hash": fingerprint(before),
              "candidate_hash": fingerprint(proposed), "files": proposed,
              "excluded_files": validation["excluded_files"]}
    if not apply:
        return result
    target.parent.mkdir(parents=True, exist_ok=True)
    store.mkdir(parents=True, exist_ok=True)
    lock = safe_path(store / (name + ".lock"), root)
    # Exclusive cooperative lock; do not steal stale locks automatically.
    descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    transaction = None
    try:
        transaction = Path(tempfile.mkdtemp(prefix=name + "-", dir=store))
        os.write(descriptor, str(transaction).encode())
        os.fsync(descriptor)
    except BaseException:
        lock.unlink()
        raise
    finally:
        os.close(descriptor)
    stage = transaction / "stage"
    record = {"schema": 1, "name": name, "target": str(target),
              "target_existed": target.exists(), "baseline": before,
              "proposed": proposed, "state": "preparing"}
    try:
        journal_write(transaction, record)
        stage.mkdir()
        for key, data in proposed_bytes.items():
            destination = safe_path(stage / key, root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            source = safe_path(candidate / key, root)
            destination.chmod(source.stat().st_mode & 0o777)
        if tree_bytes(stage, root) != proposed_bytes:
            raise ValueError("Staged byte parity failed")
        if hook:
            hook("staged")
        if tree_bytes(target, root) != before_bytes:
            raise ValueError("Production modified concurrently before swap")
        if candidate_bytes(candidate, root, name) != proposed_bytes:
            raise ValueError("Candidate modified concurrently before swap")
        record["state"] = "swapping"
        journal_write(transaction, record)
        if record["target_existed"]:
            os.rename(target, transaction / "backup")
            if tree_bytes(transaction / "backup", root) != before_bytes:
                raise ValueError("Production modified at swap; preserve backup")
        if hook:
            hook("backed_up")
        os.rename(stage, target)
        if hook:
            hook("installed")
        if tree_bytes(target, root) != proposed_bytes:
            raise ValueError("Post-publication byte parity failed")
        record["state"] = "published"
        journal_write(transaction, record)
        lock.unlink()
        result.update(state="published", transaction=str(transaction), byte_parity=True)
        return result
    except BaseException as exc:
        # Recovery refuses to overwrite newly changed bytes. If it cannot safely
        # roll back, keep lock/journal/backup for an explicit recovery decision.
        if (record["state"] == "preparing"
            and tree_bytes(target, root) == before_bytes):
            lock.unlink()
            raise RuntimeError(f"Staging failed; production untouched at {transaction}: {exc}") from exc
        try:
            recovery = recover(root, name, transaction, apply=True)
        except (OSError, ValueError) as recovery_error:
            raise RuntimeError(f"Recovery required at {transaction}: {recovery_error}") from exc
        if recovery["state"] == "published":
            result.update(state="published", transaction=str(transaction), byte_parity=True)
            return result
        raise RuntimeError(f"Publication failed; rolled back at {transaction}: {exc}") from exc


def main() -> int:
    parser = ReceiptParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--type", dest="skill_type")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--managed", type=Path)
    parser.add_argument("--candidate-hash")
    parser.add_argument("--delete-reviewed", action="append", default=[])
    parser.add_argument("--recover", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        if args.recover:
            result = recover(args.project_root, args.name, args.recover, args.apply)
        else:
            if any(value is None for value in (args.candidate, args.skill_type,
                                               args.baseline, args.managed,
                                               args.candidate_hash)):
                raise ValueError("Publish requires candidate, type, baseline, managed, and candidate-hash")
            result = publish(args.project_root, args.candidate, args.name,
                             args.skill_type, json.loads(args.baseline.read_text()),
                             json.loads(args.managed.read_text()), args.candidate_hash,
                             tuple(args.delete_reviewed), args.apply)
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        result = {"ok": False, "operation": "publish", "errors": [str(exc)]}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())