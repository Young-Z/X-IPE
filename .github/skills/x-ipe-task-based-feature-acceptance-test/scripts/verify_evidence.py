"""Read-only explicit-input acceptance evidence consistency, NOT semantic proof.

PyYAML is the existing project dependency. Caller independently resolves current
sources, all scoped ACs/assertions/types and every relevant input before verify.
This does not execute cases, authorize tools, observe stakeholders or persist state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import yaml


REQUIRED_ROLES = {"source", "specification", "code", "config", "test", "evidence"}
TYPES = {"frontend-ui", "backend-api", "unit", "integration", "structured-review"}
LIMITS = "Hash/coverage consistency only; independent semantic sufficiency, actual execution provenance and current environment review required; no stakeholder observation proof."


def safe_file(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Input path must be a nonempty string")
    relative = Path(value)
    if relative.is_absolute() or any(part in (".", "..") for part in value.split("/")):
        raise ValueError(f"Unsafe relative input: {value}")
    path = root / relative
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError(f"Symlink input: {value}")
    path.resolve(strict=True).relative_to(root)
    if not path.is_file():
        raise ValueError(f"Not a regular file: {value}")
    return path


def strings(value, label: str) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f"{label} must be a nonempty string array")
    if len(value) != len(set(value)):
        raise ValueError(f"Duplicate {label}")
    return value


def verify(project_root: Path, report: Path, expected: dict) -> dict:
    errors = []
    try:
        if project_root.is_symlink():
            raise ValueError("Project root must not be a symlink")
        root = project_root.resolve(strict=True)
        relative_report = report.absolute().relative_to(root).as_posix()
        text = safe_file(root, relative_report).read_text(encoding="utf-8")
        blocks = []
        for body in re.findall(r"```yaml\s*\n(.*?)\n```", text, re.S):
            parsed = yaml.safe_load(body)
            if isinstance(parsed, dict) and "acceptance_evidence" in parsed:
                blocks.append(parsed["acceptance_evidence"])
        if len(blocks) != 1 or not isinstance(blocks[0], dict):
            raise ValueError("Exactly one acceptance_evidence mapping required")
        record = blocks[0]
        if not isinstance(expected, dict) or not isinstance(expected.get("feature_id"), str) or not expected["feature_id"].strip():
            raise ValueError("Explicit current feature/scope identity required")
        if record.get("feature_id") != expected["feature_id"]:
            raise ValueError("Feature/scope mismatch")
        roles = expected.get("inputs")
        if not isinstance(roles, dict) or not REQUIRED_ROLES <= set(roles):
            raise ValueError("Explicit source/specification/code/config/test/evidence inputs required")
        expected_pairs = set()
        for role, paths in roles.items():
            if not isinstance(role, str) or not role.strip():
                raise ValueError("Input role required")
            for path in strings(paths, f"{role} inputs"):
                safe_file(root, path)
                expected_pairs.add((role, path))
        inputs = record.get("inputs")
        if not isinstance(inputs, list):
            raise ValueError("Report inputs must be an array")
        actual_pairs = set()
        for item in inputs:
            if not isinstance(item, dict):
                raise ValueError("Malformed report input")
            role, path = item.get("role"), item.get("path")
            if not isinstance(role, str) or not isinstance(path, str):
                raise ValueError("Report role/path must be strings")
            pair = role, path
            if pair in actual_pairs:
                raise ValueError(f"Duplicate report input: {path}")
            actual_pairs.add(pair)
            if pair not in expected_pairs:
                raise ValueError(f"Unexpected input: {role}/{path}")
            digest = hashlib.sha256(safe_file(root, path).read_bytes()).hexdigest()
            if item.get("sha256") != digest:
                raise ValueError(f"Stale or invalid input hash: {path}")
        if actual_pairs != expected_pairs:
            raise ValueError("Report omits explicit relevant inputs")
        acs = expected.get("acs")
        if not isinstance(acs, dict) or not acs:
            raise ValueError("All relevant AC expectations required")
        for ac, contract in acs.items():
            if not isinstance(ac, str) or not ac.strip() or not isinstance(contract, dict):
                raise ValueError("Malformed AC expectation")
            if not set(strings(contract.get("types"), f"{ac} types")) <= TYPES:
                raise ValueError(f"Unknown expected type: {ac}")
            strings(contract.get("assertions"), f"{ac} assertions")
        cases = record.get("cases")
        if not isinstance(cases, list) or not cases:
            raise ValueError("Actual passing case evidence required")
        ids = set()
        observed = {ac: {kind: set() for kind in contract["types"]}
                    for ac, contract in acs.items()}
        for case in cases:
            if not isinstance(case, dict):
                raise ValueError("Malformed case")
            tc = case.get("tc_id")
            if not isinstance(tc, str) or not tc.strip() or tc in ids:
                raise ValueError("Unique nonempty TC ID required")
            ids.add(tc)
            if case.get("status") != "Pass":
                raise ValueError(f"Case not passing: {tc}")
            for key in ("command_or_review", "result", "environment"):
                if not isinstance(case.get(key), str) or not case[key].strip():
                    raise ValueError(f"Missing {key}: {tc}")
            for path in strings(case.get("evidence_paths"), f"{tc} evidence paths"):
                if ("evidence", path) not in expected_pairs:
                    raise ValueError(f"Unbound case evidence: {path}")
                safe_file(root, path)
            assertions = strings(case.get("assertions"), f"{tc} assertions")
            for ac in strings(case.get("ac_ids"), f"{tc} AC IDs"):
                if ac not in acs or case.get("test_type") not in acs[ac]["types"]:
                    raise ValueError(f"Wrong/orphan AC or type: {tc}")
                observed[ac][case["test_type"]].update(assertions)
        for ac, contract in acs.items():
            for kind in contract["types"]:
                if not set(contract["assertions"]) <= observed[ac][kind]:
                    raise ValueError(f"Incomplete original type/assertion coverage: {ac}/{kind}")
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        errors.append(str(exc))
    return {"reusable": not errors, "errors": errors, "limits": LIMITS}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    args = parser.parse_args()
    try:
        root = args.project_root.resolve(strict=True)
        manifest = args.expected.absolute().relative_to(root).as_posix()
        expected = json.loads(safe_file(root, manifest).read_text(encoding="utf-8"))
        result = verify(args.project_root, args.report, expected)
    except (OSError, ValueError, TypeError) as exc:
        result = {"reusable": False, "errors": [str(exc)], "limits": LIMITS}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["reusable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())