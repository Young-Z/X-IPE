"""TASK-6749 Round 2 scenarios; execution belongs to Round 3.

Only script imports use repository paths. Every validation/publication/recovery
call operates on a resolved pytest temporary project, never a live skill.
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from types import SimpleNamespace

import pytest


PROJECT = Path(__file__).resolve().parents[1]
CANDIDATE = PROJECT / "x-ipe-docs/skill-meta/x-ipe-meta-skill-creator/candidate"
SCRIPTS = CANDIDATE / "scripts"
NAME = "x-ipe-tool-foundation-test"


@pytest.fixture
def api(monkeypatch):
    # Publish imports validate_skill by its documented sibling module name.
    # Register that exact importlib-loaded dependency; isolate it with monkeypatch.
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    modules = []
    for name in ("validate_skill", "publish_skill"):
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        modules.append(module)
    return SimpleNamespace(v=modules[0], p=modules[1])


def skill(name=NAME, skill_type="x-ipe-tool", marker="candidate"):
    operations = skill_type in ("x-ipe-tool", "x-ipe-knowledge")
    action = "## Operations\n<operation name=\"check\">\n<action>Check.</action>\n</operation>" if operations else "## Execution Procedure\n<procedure name=\"check\">\n<step_1><action>Check.</action></step_1>\n</procedure>"
    output = "operation_result:\n  ok: true"
    if skill_type == "x-ipe-task-based":
        output = "task_completion_output:\n  category: standalone\n  next_task_based_skill: null\n  process_preference:\n    interaction_mode: interact-with-human"
    return (
        f"---\nname: {name}\ndescription: Use when testing foundation behavior.\n---\n"
        f"# Foundation\n## Purpose\n{marker}\n## Input Parameters\n"
        "### Input Initialization\n<input_init><field name=\"input\" /></input_init>\n"
        "## Definition of Ready\n<definition_of_ready>\n"
        "<checkpoint><name>Ready</name></checkpoint>\n</definition_of_ready>\n"
        f"{action}\n## Output Result\n```yaml\n{output}\n```\n"
        "## Definition of Done\n<definition_of_done>\n"
        "<checkpoint><name>Done</name></checkpoint>\n</definition_of_done>\n"
    ).encode()


def write_tree(folder, files):
    folder.mkdir(parents=True, exist_ok=True)
    for key, data in files.items():
        path = folder / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def snapshot(root):
    """Include directories/modes/hidden files, not just a publisher manifest."""
    result = {}
    for path in sorted(root.rglob("*")):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            value = ("link", os.readlink(path))
        elif stat.S_ISDIR(mode):
            value = ("directory", stat.S_IMODE(mode))
        elif stat.S_ISREG(mode):
            value = ("file", stat.S_IMODE(mode), path.read_bytes())
        else:
            value = ("special", mode)
        result[path.relative_to(root).as_posix()] = value
    return result


def creator_dependencies(root):
    """Real declared external docs, not placeholders hiding broken dependencies."""
    for relative in (
        ".github/skills/x-ipe-workflow-task-execution/references/lifecycle.md",
        ".github/skills/x-ipe-workflow-task-execution/references/goal-contract.md",
        ".github/skills/x-ipe-meta-lesson-learned/references/lifecycle.md",
    ):
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((PROJECT / relative).read_bytes())


def package(tmp_path, api, existing=False):
    root = tmp_path.resolve() / "project"
    root.mkdir()
    candidate = root / "x-ipe-docs/skill-meta" / NAME / "candidate"
    target = root / ".github/skills" / NAME
    proposed = {"SKILL.md": skill(), "references/keep.txt": b"keep\r\n", ".hidden": b"hidden"}
    write_tree(candidate, proposed)
    if existing:
        write_tree(target, {**proposed, "SKILL.md": skill(marker="baseline")})
    baseline = api.v.manifest(api.v.tree_bytes(target, root))
    return SimpleNamespace(root=root, candidate=candidate, target=target,
                           baseline=baseline, managed=dict(baseline), api=api)


def receipt(env):
    result = env.api.v.validate(env.root, env.candidate, NAME, "x-ipe-tool")
    assert result["ok"], result["errors"]
    return result


def publish(env, **kwargs):
    options = dict(project_root=env.root, candidate=env.candidate, name=NAME,
                   skill_type="x-ipe-tool", baseline=env.baseline,
                   managed=env.managed, expected_candidate_hash=receipt(env)["candidate_hash"])
    options.update(kwargs)
    return env.api.p.publish(**options)


def transaction(env, boundary="installed"):
    """Model an interrupted process from journaled states without a real kill."""
    store = env.root / ".github/.skill-publication"
    txn = store / (NAME + "-interrupted")
    txn.mkdir(parents=True)
    proposed = env.api.v.manifest(env.api.v.tree_bytes(env.candidate, env.root))
    existed = env.target.exists()
    if boundary != "preparing" and existed:
        os.rename(env.target, txn / "backup")
    if boundary == "installed":
        write_tree(env.target, env.api.v.tree_bytes(env.candidate, env.root))
    record = dict(schema=1, name=NAME, target=str(env.target), target_existed=existed,
                  baseline=env.baseline, proposed=proposed,
                  state="preparing" if boundary == "preparing" else "swapping")
    env.api.p.journal_write(txn, record)
    (store / (NAME + ".lock")).write_text(str(txn))
    return txn, record


def test_importlib_interfaces(api):
    pub = inspect.signature(api.p.publish).parameters
    assert list(pub) == ["project_root", "candidate", "name", "skill_type", "baseline",
                         "managed", "expected_candidate_hash", "reviewed_deletions", "apply", "hook"]
    assert pub["apply"].default is False
    assert pub["reviewed_deletions"].default == ()
    assert pub["hook"].default is None
    assert inspect.signature(api.p.recover).parameters["apply"].default is False


@pytest.mark.parametrize("lines,ok", [(999, True), (1000, True), (1001, False)])
@pytest.mark.parametrize("newline", ["\n", "\r\n"])
@pytest.mark.parametrize("trailing", [False, True])
def test_body_boundary(tmp_path, api, lines, ok, newline, trailing):
    env = package(tmp_path, api)
    header, body, original = api.v.parse_skill(skill())
    assert header["name"] == NAME
    # Alternate blank and nonblank padding; end nonblank so newline semantics
    # do not accidentally remove an intended final empty logical line.
    padding = ["" if index % 2 == 0 else "padding" for index in range(lines - original)]
    if padding:
        padding[-1] = "last"
    body_lines = body.split("\n") + padding
    data = newline.join(["---", f"name: {NAME}", "description: test", "# header comment"]
                        + ["# frontmatter padding"] * 20 + ["---"] + body_lines)
    (env.candidate / "SKILL.md").write_bytes((data + (newline if trailing else "")).encode())
    result = api.v.validate(env.root, env.candidate, NAME, "x-ipe-tool")
    assert result["body_lines"] == lines
    assert result["ok"] is ok, result["errors"]
    assert any("maximum is 1000" in error for error in result["errors"]) is (not ok)


@pytest.mark.parametrize("data,error", [
    (b"# no frontmatter", "opening"),
    (b"---\nname: test", "closing"),
    (b"---\n- list\n---\nbody", "mapping"),
    (b"---\nname: [\n---\nbody", ""),
    (skill().replace(f"name: {NAME}\n".encode(), b""), "name"),
    (skill().replace(NAME.encode(), b"x-ipe-tool-other"), "name"),
    (skill().replace(b"description: Use when testing foundation behavior.", b"description: ''"), "description"),
    (skill().replace(b"description: Use when testing foundation behavior.", b"description: [not, text]"), "description"),
    (b"\xff", ""),
])
def test_invalid_frontmatter(tmp_path, api, data, error):
    env = package(tmp_path, api)
    (env.candidate / "SKILL.md").write_bytes(data)
    before = snapshot(env.root)
    result = api.v.validate(env.root, env.candidate, NAME, "x-ipe-tool")
    assert not result["ok"] and result["errors"]
    assert error in " ".join(result["errors"])
    assert snapshot(env.root) == before


@pytest.mark.parametrize("name,kind", [
    ("../escape", "x-ipe-tool"), ("X-ipe-tool-bad", "x-ipe-tool"),
    ("x-ipe-tool-" + "a" * 64, "x-ipe-tool"),
    (NAME, "unknown"), (NAME, "x-ipe-meta"),
])
def test_invalid_identity(tmp_path, api, name, kind):
    env = package(tmp_path, api)
    assert not api.v.validate(env.root, env.candidate, name, kind)["ok"]


@pytest.mark.parametrize("kind,name", [
    ("x-ipe-tool", NAME), ("x-ipe-knowledge", "x-ipe-knowledge-extractor-test"),
    ("x-ipe-task-based", "x-ipe-task-based-test"), ("x-ipe-meta", "x-ipe-meta-test"),
    ("x-ipe-workflow-orchestration", "x-ipe-workflow-test"),
    ("x-ipe-task-category", "x-ipe+all+test"),
    ("x-ipe-assistant", "x-ipe-assistant-test"), ("x-ipe-dao", "x-ipe-dao-test"),
])
def test_applicable_subtype_contract(tmp_path, api, kind, name):
    root = tmp_path.resolve()
    candidate = root / "x-ipe-docs/skill-meta" / name / "candidate"
    write_tree(candidate, {"SKILL.md": skill(name, kind)})
    result = api.v.validate(root, candidate, name, kind)
    assert result["ok"], result["errors"]
    if kind in ("x-ipe-tool", "x-ipe-knowledge"):
        assert b"task_completion_output" not in (candidate / "SKILL.md").read_bytes()


@pytest.mark.parametrize("field", ["task_completion_output", "category", "next_task_based_skill", "interaction_mode"])
def test_task_output_fields_required(tmp_path, api, field):
    root = tmp_path.resolve()
    name = "x-ipe-task-based-test"
    candidate = root / "x-ipe-docs/skill-meta" / name / "candidate"
    data = skill(name, "x-ipe-task-based").replace(f"{field}:".encode(), b"omitted:")
    write_tree(candidate, {"SKILL.md": data})
    result = api.v.validate(root, candidate, name, "x-ipe-task-based")
    assert not result["ok"] and any(f"lacks {field}" in e for e in result["errors"])


@pytest.mark.parametrize("section", ["Purpose", "Input Parameters", "Input Initialization", "Definition of Ready", "Operations", "Output Result", "Definition of Done"])
def test_missing_section(tmp_path, api, section):
    env = package(tmp_path, api)
    path = env.candidate / "SKILL.md"
    path.write_bytes(path.read_bytes().replace(("# " + section).encode(), b"# Absent"))
    result = api.v.validate(env.root, env.candidate, NAME, "x-ipe-tool")
    assert not result["ok"] and f"Missing contract section: {section}" in result["errors"]


@pytest.mark.parametrize("tag", ["input_init", "operation"])
def test_contract_prefix_lookalike_rejected(tmp_path, api, tag):
    env = package(tmp_path, api)
    path = env.candidate / "SKILL.md"
    path.write_bytes(path.read_bytes().replace(("<" + tag).encode(), ("<" + tag + "_fake").encode()))
    result = api.v.validate(env.root, env.candidate, NAME, "x-ipe-tool")
    assert not result["ok"] and f"Missing contract block: <{tag}" in result["errors"]


@pytest.mark.parametrize("tag,limit", [("definition_of_ready", 5), ("definition_of_done", 10)])
@pytest.mark.parametrize("extra,ok", [(0, True), (1, False)])
def test_checkpoint_limits(tmp_path, api, tag, limit, extra, ok):
    env = package(tmp_path, api)
    path = env.candidate / "SKILL.md"
    data = path.read_bytes().replace(f"<{tag}>".encode(),
                                    (f"<{tag}>" + "<checkpoint/>" * (limit - 1 + extra)).encode())
    path.write_bytes(data)
    result = api.v.validate(env.root, env.candidate, NAME, "x-ipe-tool")
    assert result["ok"] is ok, result["errors"]


def test_section_order_and_fenced_heading(tmp_path, api):
    env = package(tmp_path, api)
    path = env.candidate / "SKILL.md"
    path.write_bytes(path.read_bytes() + b"\n```markdown\n## Purpose\n```\n")
    assert receipt(env)["ok"]
    data = path.read_bytes().replace(b"## Purpose", b"## TEMP", 1).replace(
        b"## Output Result", b"## Purpose", 1).replace(b"## TEMP", b"## Output Result", 1)
    path.write_bytes(data)
    result = api.v.validate(env.root, env.candidate, NAME, "x-ipe-tool")
    assert "Required contract sections are out of order" in result["errors"]


@pytest.mark.parametrize("external", [False, True])
def test_missing_self_and_external_resources(tmp_path, api, external):
    env = package(tmp_path, api, existing=True)
    target = "x-ipe-docs/elsewhere.md" if external else f".github/skills/{NAME}/references/only-live.md"
    if not external:
        write_tree(env.target, {"references/only-live.md": b"live must not mask missing candidate resource"})
    write_tree(env.candidate, {"references/links.md": f"[resource]({target})\n".encode()})
    result = api.v.validate(env.root, env.candidate, NAME, "x-ipe-tool")
    assert not result["ok"] and any("Broken resource" in e for e in result["errors"])


def test_self_external_encoded_and_reference_links(tmp_path, api):
    env = package(tmp_path, api)
    write_tree(env.candidate, {"references/my file.md": b"resource", "references/links.md": (
        f"[self](.github/skills/{NAME}/references/my%20file.md#anchor)\n"
        "![image](references/my%20file.md)\n[external][doc]\n"
        "[doc]: x-ipe-docs/external.md \"title\"\n"
        "[web](https://example.invalid/not-fetched)\n[mail](mailto:test@example.invalid)\n"
        "[template](references/{placeholder}.md)\n"
    ).encode()})
    write_tree(env.root, {"x-ipe-docs/external.md": b"external"})
    result = receipt(env)
    assert len(result["warnings"]) == 1 and "template" in result["warnings"][0]


@pytest.mark.parametrize("link", ["../escape.md", "%2e%2e/escape.md", "/absolute.md", "file:///tmp/escape", "//remote/resource"])
def test_unsafe_markdown_targets(tmp_path, api, link):
    env = package(tmp_path, api)
    write_tree(env.candidate, {"references/links.md": f"[bad]({link})".encode()})
    assert not api.v.validate(env.root, env.candidate, NAME, "x-ipe-tool")["ok"]


@pytest.mark.parametrize("key", ["../outside", "/absolute", "a/../b", "a\\b", "a//b", "a/./b", ".", "", "a/"])
def test_manifest_traversal_rejected(api, key):
    with pytest.raises(ValueError):
        api.p.checked_manifest({key: "a" * 64})


@pytest.mark.parametrize("value", [[], {"SKILL.md": "bad"}, {"SKILL.md": "A" * 64}, {"SKILL.md": 123}])
def test_invalid_manifest(api, value):
    with pytest.raises(ValueError):
        api.p.checked_manifest(value)


@pytest.mark.parametrize("location", ["candidate", "candidate-ancestor", "resource", "production", "store", "root"])
def test_symlink_protection(tmp_path, api, location):
    env = package(tmp_path, api, existing=True)
    outside = tmp_path.resolve() / "outside"
    outside.mkdir()
    if location == "resource":
        (outside / "file").write_bytes(b"external")
        (env.candidate / "references/link").symlink_to(outside / "file")
    elif location in ("candidate", "candidate-ancestor", "production"):
        path = {"candidate": env.candidate, "candidate-ancestor": env.candidate.parent,
                "production": env.target}[location]
        moved = path.with_name(path.name + "-real")
        os.rename(path, moved)
        path.symlink_to(moved, target_is_directory=True)
    elif location == "store":
        (env.root / ".github/.skill-publication").symlink_to(outside, target_is_directory=True)
    else:
        alias = tmp_path.resolve() / "alias"
        alias.symlink_to(env.root, target_is_directory=True)
        with pytest.raises(ValueError, match="Symlink"):
            api.p.paths(alias, NAME)
        return
    before = snapshot(env.root)
    with pytest.raises(ValueError):
        api.p.publish(env.root, env.candidate, NAME, "x-ipe-tool",
                      env.baseline, env.managed, "0" * 64, apply=True)
    assert snapshot(env.root) == before
    assert snapshot(outside) == ({"file": ("file", stat.S_IMODE((outside / "file").stat().st_mode), b"external")} if location == "resource" else {})


@pytest.mark.parametrize("node", ["hardlink", "fifo"])
def test_nonprivate_and_special_resources(tmp_path, api, node):
    env = package(tmp_path, api)
    path = env.candidate / "references/node"
    if node == "hardlink":
        os.link(env.candidate / ".hidden", path)
    else:
        os.mkfifo(path)
    result = api.v.validate(env.root, env.candidate, NAME, "x-ipe-tool")
    assert not result["ok"] and any("Non-private" in e or "Special node" in e for e in result["errors"])


@pytest.mark.parametrize("existing", [False, True])
def test_dry_run_no_mutations(tmp_path, api, existing):
    env = package(tmp_path, api, existing)
    before = snapshot(env.root)
    result = publish(env)
    assert result["ok"] and result["state"] == "dry_run"
    assert result["removed"] == [] and result["protected"] == []
    assert result["changed"] == (["SKILL.md"] if existing else [])
    assert result["added"] == ([] if existing else [".hidden", "SKILL.md", "references/keep.txt"])
    assert snapshot(env.root) == before
    assert not (env.root / ".github/.skill-publication").exists()


@pytest.mark.parametrize("existing", [False, True])
def test_successful_new_and_update_publish(tmp_path, api, existing):
    env = package(tmp_path, api, existing)
    source = api.v.tree_bytes(env.candidate, env.root)
    old = api.v.tree_bytes(env.target, env.root)
    (env.candidate / "SKILL.md").chmod(0o640)
    result = publish(env, apply=True)
    assert result["ok"] and result["state"] == "published" and result["byte_parity"]
    assert api.v.tree_bytes(env.target, env.root) == source
    assert api.v.tree_bytes(env.candidate, env.root) == source
    assert stat.S_IMODE((env.target / "SKILL.md").stat().st_mode) == 0o640
    txn = Path(result["transaction"])
    assert txn.parent == env.root / ".github/.skill-publication"
    assert json.loads((txn / "journal.json").read_text())["state"] == "published"
    assert api.v.tree_bytes(txn / "backup", env.root) == old
    assert (txn / "backup").exists() is existing
    assert not (txn.parent / (NAME + ".lock")).exists()


@pytest.mark.parametrize("which", ["baseline", "candidate"])
def test_preflight_fingerprint_concurrency(tmp_path, api, which):
    env = package(tmp_path, api, existing=True)
    reviewed_hash = receipt(env)["candidate_hash"]
    path = (env.target if which == "baseline" else env.candidate) / "references/keep.txt"
    path.write_bytes(b"concurrent edit")
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="baseline|fingerprint"):
        publish(env, expected_candidate_hash=reviewed_hash, apply=True)
    assert snapshot(env.root) == before


@pytest.mark.parametrize("which", ["candidate", "target"])
def test_staged_concurrency_preserves_edits(tmp_path, api, which):
    env = package(tmp_path, api, existing=True)
    old = api.v.tree_bytes(env.target, env.root)
    def hook(event):
        if event == "staged":
            ((env.target if which == "target" else env.candidate) / "references/keep.txt").write_bytes(b"concurrent")
    with pytest.raises(RuntimeError, match="Staging failed|Recovery required"):
        publish(env, apply=True, hook=hook)
    if which == "target":
        assert (env.target / "references/keep.txt").read_bytes() == b"concurrent"
        assert (env.root / ".github/.skill-publication" / (NAME + ".lock")).exists()
    else:
        assert api.v.tree_bytes(env.target, env.root) == old
        assert (env.candidate / "references/keep.txt").read_bytes() == b"concurrent"


@pytest.mark.parametrize("ownership", ["dirty", "unmanaged"])
@pytest.mark.parametrize("action", ["change", "remove"])
def test_protected_files_cannot_change_or_delete(tmp_path, api, ownership, action):
    env = package(tmp_path, api, existing=True)
    key = "references/keep.txt"
    if ownership == "dirty":
        env.managed[key] = api.v.manifest({key: b"trusted old bytes"})[key]
    else:
        del env.managed[key]
    if action == "remove":
        (env.candidate / key).unlink()
    else:
        (env.candidate / key).write_bytes(b"overwrite")
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="dirty or unmanaged"):
        publish(env, reviewed_deletions=(key,) if action == "remove" else (), apply=True)
    assert snapshot(env.root) == before


@pytest.mark.parametrize("ownership", ["dirty", "unmanaged"])
def test_identical_protected_bytes_retained(tmp_path, api, ownership):
    env = package(tmp_path, api, existing=True)
    key = "references/keep.txt"
    if ownership == "dirty":
        env.managed[key] = "a" * 64
    else:
        del env.managed[key]
    result = publish(env, apply=True)
    assert result["protected"] == [key]
    assert (env.target / key).read_bytes() == b"keep\r\n"
    assert env.managed.get(key) != result["files"][key], "Publication must not mutate supplied ownership"


def test_preexisting_deleted_managed_file_not_restored(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    key = "references/keep.txt"
    (env.target / key).unlink()
    env.baseline = api.v.manifest(api.v.tree_bytes(env.target, env.root))
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="preexisting deleted"):
        publish(env, apply=True)
    assert snapshot(env.root) == before


@pytest.mark.parametrize("reviewed", [(), ("references/other.txt",), ("references/keep.txt", "references/keep.txt")])
def test_deletion_review_exactness(tmp_path, api, reviewed):
    env = package(tmp_path, api, existing=True)
    (env.candidate / "references/keep.txt").unlink()
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="exact removal"):
        publish(env, reviewed_deletions=reviewed, apply=True)
    assert snapshot(env.root) == before


def test_explicit_clean_managed_deletion(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    key = "references/keep.txt"
    (env.candidate / key).unlink()
    result = publish(env, reviewed_deletions=(key,), apply=True)
    assert result["removed"] == [key]
    assert not (env.target / key).exists()
    assert (Path(result["transaction"]) / "backup" / key).read_bytes() == b"keep\r\n"
    assert api.v.tree_bytes(env.target, env.root) == api.v.tree_bytes(env.candidate, env.root)


def test_existing_lock_not_stolen(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    lock = env.root / ".github/.skill-publication" / (NAME + ".lock")
    lock.parent.mkdir()
    lock.write_text("another active publisher")
    before = snapshot(env.root)
    with pytest.raises(FileExistsError):
        publish(env, apply=True)
    assert snapshot(env.root) == before


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("boundary", ["staged", "backed_up", "installed"])
def test_fault_rollback(tmp_path, api, existing, boundary):
    env = package(tmp_path, api, existing)
    before = api.v.tree_bytes(env.target, env.root)
    source = api.v.tree_bytes(env.candidate, env.root)
    events = []
    def hook(event):
        events.append(event)
        if event == boundary:
            raise OSError("injected fault")
    with pytest.raises(RuntimeError, match="Staging failed|rolled back"):
        publish(env, apply=True, hook=hook)
    assert events == ["staged", "backed_up", "installed"][:["staged", "backed_up", "installed"].index(boundary) + 1]
    assert api.v.tree_bytes(env.target, env.root) == before
    assert env.target.exists() is existing
    assert api.v.tree_bytes(env.candidate, env.root) == source
    store = env.root / ".github/.skill-publication"
    assert not (store / (NAME + ".lock")).exists()
    journals = list(store.glob("*/journal.json"))
    assert len(journals) == 1
    assert json.loads(journals[0].read_text())["state"] == ("preparing" if boundary == "staged" else "rolled_back")


@pytest.mark.parametrize("changed", ["target", "backup"])
def test_failed_rollback_retains_evidence(tmp_path, api, changed):
    env = package(tmp_path, api, existing=True)
    store = env.root / ".github/.skill-publication"
    def hook(event):
        if event == "installed":
            txn = next(path for path in store.iterdir() if path.is_dir())
            folder = env.target if changed == "target" else txn / "backup"
            (folder / "references/keep.txt").write_bytes(b"unexpected edit")
            raise OSError("force recovery")
    with pytest.raises(RuntimeError, match="Recovery required"):
        publish(env, apply=True, hook=hook)
    txn = next(path for path in store.iterdir() if path.is_dir())
    assert (txn / "backup").exists() and (txn / "journal.json").exists()
    assert (store / (NAME + ".lock")).read_text() == str(txn)
    folder = env.target if changed == "target" else txn / "backup"
    assert (folder / "references/keep.txt").read_bytes() == b"unexpected edit"
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="Concurrent|Backup"):
        api.p.recover(env.root, NAME, txn, apply=True)
    assert snapshot(env.root) == before


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("boundary", ["preparing", "backed_up", "installed"])
def test_interrupted_recovery_and_replay(tmp_path, api, existing, boundary):
    env = package(tmp_path, api, existing)
    original = api.v.tree_bytes(env.target, env.root)
    txn, _ = transaction(env, boundary)
    before = snapshot(env.root)
    dry = api.p.recover(env.root, NAME, txn)
    assert dry["state"] == "dry_run" and not dry["changed"]
    assert snapshot(env.root) == before
    result = api.p.recover(env.root, NAME, txn, apply=True)
    assert result["state"] == "rolled_back"
    assert api.v.tree_bytes(env.target, env.root) == original
    assert env.target.exists() is existing
    after = snapshot(env.root)
    replay = api.p.recover(env.root, NAME, txn, apply=True)
    assert replay["state"] == "rolled_back" and not replay["changed"]
    assert snapshot(env.root) == after


@pytest.mark.parametrize("defect", ["missing", "foreign"])
def test_recovery_requires_matching_lock(tmp_path, api, defect):
    env = package(tmp_path, api, existing=True)
    txn, _ = transaction(env)
    lock = txn.parent / (NAME + ".lock")
    if defect == "missing":
        lock.unlink()
    else:
        lock.write_text("other transaction")
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="matching retained"):
        api.p.recover(env.root, NAME, txn, apply=True)
    assert snapshot(env.root) == before


@pytest.mark.parametrize("defect", ["missing", "corrupt"])
def test_recovery_backup_safety(tmp_path, api, defect):
    env = package(tmp_path, api, existing=True)
    txn, _ = transaction(env)
    if defect == "missing":
        os.rename(txn / "backup", txn / "saved-elsewhere")
    else:
        (txn / "backup/SKILL.md").write_bytes(b"corrupt")
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="backup missing|Backup bytes"):
        api.p.recover(env.root, NAME, txn, apply=True)
    assert snapshot(env.root) == before


@pytest.mark.parametrize("unexpected", ["backup", "baseline"])
def test_new_recovery_rejects_impossible_backup_or_baseline(tmp_path, api, unexpected):
    env = package(tmp_path, api)
    txn, record = transaction(env)
    if unexpected == "backup":
        write_tree(txn / "backup", {"unreviewed.txt": b"do not install"})
    else:
        record["baseline"] = api.v.manifest({"unreviewed.txt": b"not a new skill"})
        api.p.journal_write(txn, record)
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="New-skill recovery"):
        api.p.recover(env.root, NAME, txn, apply=True)
    assert snapshot(env.root) == before


@pytest.mark.parametrize("field,value", [("schema", 2), ("state", "unknown"), ("target_existed", "yes"), ("name", "x-ipe-tool-other"), ("target", "/wrong/root")])
def test_recovery_journal_identity(tmp_path, api, field, value):
    env = package(tmp_path, api, existing=True)
    txn, record = transaction(env)
    record[field] = value
    api.p.journal_write(txn, record)
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="identity|state/schema"):
        api.p.recover(env.root, NAME, txn, apply=True)
    assert snapshot(env.root) == before


def test_recovery_conflicting_failed_tree(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    txn, _ = transaction(env)
    write_tree(txn / "failed", {"unreviewed.txt": b"retain"})
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="failed tree already exists"):
        api.p.recover(env.root, NAME, txn, apply=True)
    assert snapshot(env.root) == before


def test_published_recovery_retained_lock_and_concurrent_edit(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    result = publish(env, apply=True)
    txn = Path(result["transaction"])
    lock = txn.parent / (NAME + ".lock")
    lock.write_text(str(txn))
    target_before = api.v.tree_bytes(env.target, env.root)
    dry_before = snapshot(env.root)
    assert api.p.recover(env.root, NAME, txn)["state"] == "published"
    assert snapshot(env.root) == dry_before
    assert api.p.recover(env.root, NAME, txn, apply=True)["state"] == "published"
    assert not lock.exists() and api.v.tree_bytes(env.target, env.root) == target_before
    (env.target / ".hidden").write_bytes(b"concurrent")
    before = snapshot(env.root)
    with pytest.raises(ValueError, match="Published target changed"):
        api.p.recover(env.root, NAME, txn, apply=True)
    assert snapshot(env.root) == before


def test_durable_published_journal_failure_not_reported_as_rollback(tmp_path, api, monkeypatch):
    env = package(tmp_path, api, existing=True)
    original = api.p.journal_write
    def fail_after_journaling(txn, record):
        original(txn, record)
        if record["state"] == "published":
            raise OSError("injected after durable terminal journal")
    monkeypatch.setattr(api.p, "journal_write", fail_after_journaling)
    result = publish(env, apply=True)
    assert result["state"] == "published" and result["byte_parity"]
    assert api.v.tree_bytes(env.target, env.root) == api.v.tree_bytes(env.candidate, env.root)
    assert json.loads((Path(result["transaction"]) / "journal.json").read_text())["state"] == "published"


def test_staged_byte_parity_failure(tmp_path, api, monkeypatch):
    env = package(tmp_path, api, existing=True)
    original_bytes = api.v.tree_bytes(env.target, env.root)
    original = api.p.tree_bytes
    def corrupt_stage_read(folder, root):
        files = original(folder, root)
        if folder.name == "stage":
            files[".hidden"] = b"not the proposed bytes"
        return files
    monkeypatch.setattr(api.p, "tree_bytes", corrupt_stage_read)
    with pytest.raises(RuntimeError, match="Staged byte parity failed"):
        publish(env, apply=True)
    assert api.v.tree_bytes(env.target, env.root) == original_bytes
    assert not (env.root / ".github/.skill-publication" / (NAME + ".lock")).exists()


def test_install_rename_failure_restores_backup(tmp_path, api, monkeypatch):
    env = package(tmp_path, api, existing=True)
    original_bytes = api.v.tree_bytes(env.target, env.root)
    rename = api.p.os.rename
    def fail_install(source, destination):
        if Path(source).name == "stage":
            raise OSError("injected install rename failure")
        return rename(source, destination)
    monkeypatch.setattr(api.p.os, "rename", fail_install)
    with pytest.raises(RuntimeError, match="rolled back"):
        publish(env, apply=True)
    assert api.v.tree_bytes(env.target, env.root) == original_bytes


def test_rollback_rename_failure_then_explicit_recovery(tmp_path, api, monkeypatch):
    env = package(tmp_path, api, existing=True)
    original_bytes = api.v.tree_bytes(env.target, env.root)
    rename = api.p.os.rename
    def fail_restore(source, destination):
        if Path(source).name == "backup":
            raise OSError("injected backup restoration failure")
        return rename(source, destination)
    monkeypatch.setattr(api.p.os, "rename", fail_restore)
    def hook(event):
        if event == "installed":
            raise OSError("injected publication failure")
    with pytest.raises(RuntimeError, match="Recovery required"):
        publish(env, apply=True, hook=hook)
    store = env.root / ".github/.skill-publication"
    txn = next(path for path in store.iterdir() if path.is_dir())
    assert not env.target.exists()
    assert api.v.tree_bytes(txn / "backup", env.root) == original_bytes
    assert (txn / "failed").exists() and (store / (NAME + ".lock")).exists()
    monkeypatch.setattr(api.p.os, "rename", rename)
    assert api.p.recover(env.root, NAME, txn, apply=True)["state"] == "rolled_back"
    assert api.v.tree_bytes(env.target, env.root) == original_bytes
    assert not (store / (NAME + ".lock")).exists()


@pytest.mark.parametrize("which", ["root", "candidate", "name", "traversal"])
def test_wrong_publication_root_or_identity(tmp_path, api, which):
    env = package(tmp_path, api, existing=True)
    options = {}
    if which == "root":
        wrong = tmp_path.resolve() / "wrong"
        wrong.mkdir()
        options["project_root"] = wrong
    elif which == "candidate":
        options["candidate"] = env.candidate.parent
    elif which == "name":
        options["name"] = "x-ipe-tool-other"
    else:
        options["candidate"] = env.candidate / ".." / "candidate"
    before = snapshot(tmp_path.resolve())
    with pytest.raises(ValueError):
        publish(env, apply=True, **options)
    assert snapshot(tmp_path.resolve()) == before


def test_wrong_recovery_root(tmp_path, api):
    env = package(tmp_path, api, existing=True)
    txn, _ = transaction(env)
    wrong = tmp_path.resolve() / "wrong"
    wrong.mkdir()
    before = snapshot(tmp_path.resolve())
    with pytest.raises(ValueError):
        api.p.recover(wrong, NAME, txn, apply=True)
    assert snapshot(tmp_path.resolve()) == before


@pytest.mark.parametrize("script", ["validate_skill.py", "publish_skill.py"])
@pytest.mark.parametrize("case", ["valid", "missing-arguments", "wrong-root"])
def test_cli_json_exit_and_read_only_default(tmp_path, api, script, case):
    env = package(tmp_path, api)
    args = ["--project-root", str(env.root), "--candidate", str(env.candidate), "--name", NAME,
            "--type", "x-ipe-tool"]
    if script == "publish_skill.py":
        baseline = tmp_path.resolve() / "baseline.json"
        managed = tmp_path.resolve() / "managed.json"
        baseline.write_text("{}")
        managed.write_text("{}")
        args += ["--baseline", str(baseline), "--managed", str(managed), "--candidate-hash", receipt(env)["candidate_hash"]]
    if case == "missing-arguments":
        args = []
    elif case == "wrong-root":
        wrong = tmp_path.resolve() / "wrong"
        wrong.mkdir()
        args[1] = str(wrong)
    before = snapshot(tmp_path.resolve())
    result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *args],
                            cwd=tmp_path.resolve(), capture_output=True, text=True,
                            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=30)
    output = json.loads(result.stdout)
    assert result.returncode == {"valid": 0, "missing-arguments": 2, "wrong-root": 1}[case]
    assert output["ok"] is (case == "valid")
    assert snapshot(tmp_path.resolve()) == before


def test_creator_candidate_contract_resources_and_policy(tmp_path, api):
    # Validate a copied bundle in a temporary project with only the external
    # dependencies it actually declares. Never publish the creator itself.
    root = tmp_path.resolve()
    name = "x-ipe-meta-skill-creator"
    local = root / "x-ipe-docs/skill-meta" / name / "candidate"
    write_tree(local, api.v.tree_bytes(CANDIDATE, PROJECT))
    creator_dependencies(root)
    result = api.v.validate(root, local, name, "x-ipe-meta")
    assert result["ok"], result["errors"]
    text = (local / "SKILL.md").read_text()
    assert result["body_lines"] <= 1000
    assert "TASK-6749" not in text and "OLD four-round procedure" not in text
    assert "Drafting alone does not authorize promotion" in text
    assert "independent review" in text and "references/single-loop-authoring.md" in text
    assert "approximately 120 lines" in text and "up to five" in text
    assert "applied requires actual production fingerprint" in text
    assert "complete compatible publisher JSON receipt" in text
    assert "relevant passing production test receipt" in text
    assert "BLOCKING: Load [general guidelines]" in text
    assert not any(emoji in text for emoji in ("⛔", "⚠️", "🔴", "🟢"))
    examples = (local / "references/examples.md").read_text()
    assert examples.count("## Example") >= 3
    for stem in ("x-ipe-task-based", "x-ipe-tool", "x-ipe-workflow-orchestration", "x-ipe-meta", "x-ipe-dao", "x-ipe-knowledge", "x-ipe-assistant"):
        assert (local / "templates" / f"{stem}.md").is_file()
    for stem in ("x-ipe-task-based", "x-ipe-tool", "x-ipe-task-category", "x-ipe-meta", "x-ipe-dao", "x-ipe-knowledge", "x-ipe-assistant"):
        assert (local / "templates" / f"skill-meta-{stem}.md").is_file()