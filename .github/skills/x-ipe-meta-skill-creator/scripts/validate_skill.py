"""Read-only skill validation and manifests. CLI emits one JSON receipt.

PyYAML is the sole non-stdlib dependency (already used by X-IPE).
No repository/global state is inferred; APIs accept temporary project roots.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import unquote, urlsplit

import yaml


TYPES = {
    "x-ipe-task-based": "x-ipe-task-based-",
    "x-ipe-tool": "x-ipe-tool-",
    "x-ipe-meta": "x-ipe-meta-",
    "x-ipe-workflow-orchestration": "x-ipe-workflow-",
    "x-ipe-task-category": "x-ipe+",
    "x-ipe-knowledge": "x-ipe-knowledge-",
    "x-ipe-assistant": "x-ipe-assistant-",
    "x-ipe-dao": "x-ipe-dao-",
}
CONTRACTS = {
    "x-ipe-tool": ("Operations", "<operation"),
    "x-ipe-knowledge": ("Operations", "<operation"),
}
# One established category has a reporting-operations contract, not child-task
# completion orchestration. Identity remains category-only; never change TYPES
# or infer an exemption from the candidate's headings or a matching prefix.
LEGACY_CATEGORY_CONTRACTS = {
    "x-ipe+feature+quality-board-management": ("Operations", "<operation"),
}
# Existing distributed identity only; new assistants still use lowercase names.
LEGACY_NAMES = {
    "x-ipe-assistant-user-representative-Engineer": "x-ipe-assistant",
}
# Explicit cleanup exception for this creator migration only. Not an ignore
# pattern: unknown files under the excluded root fail, and all nodes are checked.
EXCLUDED_ROOTS = {
    "x-ipe-meta-skill-creator": {
        "metadata": frozenset({"metadata/review-findings.md", "metadata/test-cases.yaml"}),
    },
}


class ReceiptParser(argparse.ArgumentParser):
    """Keep argument errors machine-readable too (exit status 2)."""

    def error(self, message: str) -> None:
        print(json.dumps({"ok": False, "errors": [message]}))
        raise SystemExit(2)


def safe_path(path: Path, root: Path) -> Path:
    """Reject traversal, links (including ancestor links), and special nodes."""
    path, root = Path(path).absolute(), Path(root).absolute()
    if ".." in path.parts or ".." in root.parts:
        raise ValueError("Parent traversal is prohibited")
    path.relative_to(root)
    for item in (path, *path.parents):
        if item.is_symlink():
            raise ValueError(f"Symlink prohibited: {item}")
        if item.exists() and not (item.is_file() or item.is_dir()):
            raise ValueError(f"Special node prohibited: {item}")
    return path


def relative_key(key: str) -> str:
    if not isinstance(key, str):
        raise ValueError("Manifest paths must be strings")
    path = PurePosixPath(key)
    if (not key or path.is_absolute() or ".." in path.parts
            or "\\" in key or path.as_posix() != key or key == "."):
        raise ValueError(f"Unsafe manifest path: {key!r}")
    return key


def tree_bytes(folder: Path, root: Path) -> dict[str, bytes]:
    """Inventory every file, including hidden files; no implicit exclusions."""
    folder = safe_path(folder, root)
    if not folder.exists():
        return {}
    if not folder.is_dir():
        raise ValueError("Package root must be a directory")
    result = {}
    for directory, dirs, files in os.walk(folder, followlinks=False):
        for name in sorted(dirs + files):
            item = safe_path(Path(directory) / name, root)
            if item.is_file():
                before = item.stat()
                data = item.read_bytes()
                after = item.stat()
                if (before.st_ino, before.st_mtime_ns, before.st_size) != (
                        after.st_ino, after.st_mtime_ns, after.st_size):
                    raise ValueError(f"File changed during inventory: {item}")
                # Reject hard-linked files to avoid modifying shared resources.
                if after.st_nlink != 1 or not stat.S_ISREG(after.st_mode):
                    raise ValueError(f"Non-private regular file: {item}")
                result[item.relative_to(folder).as_posix()] = data
    return dict(sorted(result.items()))


def candidate_bytes(folder: Path, root: Path, name: str) -> dict[str, bytes]:
    """Publishable candidate bytes; inspect every node before narrow exclusion."""
    files = tree_bytes(folder, root)
    for excluded_root, allowed in EXCLUDED_ROOTS.get(name, {}).items():
        for key in tuple(files):
            if key == excluded_root or key.startswith(excluded_root + "/"):
                if key not in allowed:
                    raise ValueError(f"Unexpected resource under excluded metadata root: {key}")
                del files[key]
    return files


def manifest(files: dict[str, bytes]) -> dict[str, str]:
    return {key: hashlib.sha256(value).hexdigest() for key, value in files.items()}


def fingerprint(files: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(files, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def parse_skill(data: bytes) -> tuple[dict, str, int]:
    """Count logical LF/CRLF lines, not newline bytes; include body blanks."""
    text = data.decode("utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("Missing opening YAML frontmatter delimiter")
    end = next((index for index in range(1, len(lines))
                if lines[index] == "---"), None)
    if end is None:
        raise ValueError("Missing closing YAML frontmatter delimiter")
    metadata = yaml.safe_load("\n".join(lines[1:end]))
    if not isinstance(metadata, dict):
        raise ValueError("Frontmatter must be a mapping")
    body_lines = lines[end + 1:]
    return metadata, "\n".join(body_lines), len(body_lines)


def headings(text: str) -> list[str]:
    """Ignore fenced examples when checking the entry file's contract."""
    clean = re.sub(r"(?ms)^(```|~~~).*?^\1[^\n]*$", "", text)
    return re.findall(r"(?m)^#{2,3} (.+?)\s*$", clean)


def markdown_targets(text: str) -> list[str]:
    inline = re.findall(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", text)
    defined = re.findall(r"(?m)^\s*\[[^\]\n]+\]:\s*(.+)$", text)
    targets = []
    for value in inline + defined:
        value = re.sub(r'\s+["\'][^"\']*["\']\s*$', "", value).strip()
        targets.append(value.strip("<>"))
    return targets


def validate(project_root: Path, candidate: Path, name: str,
             skill_type: str) -> dict:
    """Return errors/warnings plus complete file hashes; never write files."""
    errors, warnings = [], []
    receipt = {"schema": 1, "operation": "validate", "name": name,
               "skill_type": skill_type, "ok": False,
               "errors": errors, "warnings": warnings}
    try:
        root = safe_path(Path(project_root), Path(project_root))
        expected = root / "x-ipe-docs" / "skill-meta" / name / "candidate"
        if ((not re.fullmatch(r"[a-z0-9]+(?:[-+][a-z0-9]+)*", name)
             and LEGACY_NAMES.get(name) != skill_type)
                or len(name) > 64 or skill_type not in TYPES
                or not name.startswith(TYPES[skill_type])):
            raise ValueError("Invalid name or subtype identity")
        candidate = safe_path(Path(candidate), root)
        if candidate != expected:
            raise ValueError("Candidate must be the same-named canonical candidate root")
        physical = tree_bytes(candidate, root)
        files = candidate_bytes(candidate, root, name)
        receipt["excluded_files"] = manifest({key: data for key, data in physical.items()
                              if key not in files})
        if "SKILL.md" not in files:
            raise ValueError("Candidate lacks SKILL.md")
        metadata, body, count = parse_skill(files["SKILL.md"])
        receipt["body_lines"] = count
        if metadata.get("name") != name:
            errors.append("Frontmatter name does not match folder identity")
        description = metadata.get("description")
        if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
            errors.append("Frontmatter description must contain 1-1024 characters")
        if count > 1000:
            errors.append(f"SKILL.md body has {count} lines; maximum is 1000")
        sections = headings(body)
        action_section, action_tag = CONTRACTS.get(
            skill_type, ("Execution Procedure", "<procedure"))
        if skill_type == "x-ipe-task-category" and name in LEGACY_CATEGORY_CONTRACTS:
            action_section, action_tag = LEGACY_CATEGORY_CONTRACTS[name]
        required = ["Purpose", "Input Parameters", "Input Initialization",
                    "Definition of Ready", action_section, "Output Result",
                    "Definition of Done"]
        positions = []
        for section in required:
            if section not in sections:
                errors.append(f"Missing contract section: {section}")
            else:
                positions.append(sections.index(section))
        if positions != sorted(positions):
            errors.append("Required contract sections are out of order")
        for tag in ("<input_init", "<definition_of_ready", action_tag,
                    "<definition_of_done"):
            if not re.search(re.escape(tag) + r"(?=[\s/>])", body):
                errors.append(f"Missing contract block: {tag}")
        for tag, limit in (("definition_of_ready", 5), ("definition_of_done", 10)):
            blocks = re.findall(fr"<{tag}\b[^>]*>(.*?)</{tag}>", body, re.S)
            if len(blocks) != 1:
                errors.append(f"Expected exactly one closed {tag} block")
            elif len(re.findall(r"<checkpoint\b", blocks[0])) > limit:
                errors.append(f"{tag} exceeds {limit} checkpoints")
        if skill_type == "x-ipe-task-based":
            output = body.split("## Output Result", 1)[-1].split("\n## ", 1)[0]
            for field in ("task_completion_output", "category", "process_preference",
                          "next_task_based_skill", "interaction_mode"):
                if not re.search(fr"(?m)^\s*{field}:", output):
                    errors.append(f"Task-based output lacks {field}")
            if not re.search(r"(?m)^([ \t]+)process_preference:[ \t]*\n\1[ \t]+interaction_mode:", output):
                errors.append("Task-based output requires nested process_preference.interaction_mode")
        # Tools/knowledge use operation results, never forced task routing fields.
        for key, data in files.items():
            if not key.endswith(".md"):
                continue
            for link in markdown_targets(data.decode("utf-8")):
                if "{" in link or "}" in link:
                    warnings.append(f"Uninstantiated template link: {key}: {link}")
                    continue
                parsed = urlsplit(link)
                if parsed.scheme in ("http", "https", "mailto") or link.startswith("#"):
                    continue
                if parsed.scheme or parsed.netloc:
                    errors.append(f"Unsupported resource URI: {key}: {link}")
                    continue
                resource = unquote(parsed.path)
                if not resource:
                    continue
                if resource.startswith("/") or ".." in PurePosixPath(resource).parts:
                    errors.append(f"Unsafe resource path: {key}: {link}")
                    continue
                own = f".github/skills/{name}"
                if resource == own or resource.startswith(own + "/"):
                    target = candidate / resource[len(own):].lstrip("/")
                elif resource.startswith((".github/", "x-ipe-docs/", "src/", "tests/")):
                    target = root / resource
                elif resource.startswith(("references/", "scripts/", "templates/")):
                    target = candidate / resource
                else:
                    # Existing file-relative links remain valid; canonical root
                    # files (e.g. README.md) use root fallback only if present.
                    target = candidate / Path(key).parent / resource
                    if not target.exists() and (root / resource).exists():
                        target = root / resource
                try:
                    target = safe_path(target, root)
                    if not target.exists():
                        raise ValueError("Resource does not exist")
                except ValueError as exc:
                    errors.append(f"Broken resource: {key}: {link}: {exc}")
        receipt["files"] = manifest(files)
        receipt["candidate_hash"] = fingerprint(receipt["files"])
    except (ValueError, OSError, UnicodeError, yaml.YAMLError) as exc:
        errors.append(str(exc))
    receipt["ok"] = not errors
    return receipt


def main() -> int:
    parser = ReceiptParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--type", dest="skill_type", choices=TYPES, required=True)
    args = parser.parse_args()
    result = validate(args.project_root, args.candidate, args.name, args.skill_type)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())