"""Disposable validation inputs, without changing production inventory rules."""
from contextlib import contextmanager
import importlib.util
import marshal
from pathlib import Path
import shutil
import tempfile
from types import CodeType
from urllib.parse import unquote, urlsplit


def load_source(path, name):
    """Execute the actual source with normal module metadata, but no cache I/O."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    exec(compile(Path(path).read_bytes(), str(path), "exec"), module.__dict__)
    return module


def source_cache(path, caches):
    """Recognize only compiled caches at exact source-bound interpreter paths."""
    if path not in caches or path.is_symlink() or not path.is_file():
        return False
    data = path.read_bytes()
    if len(data) < 16 or data[:4] != importlib.util.MAGIC_NUMBER:
        return False
    if int.from_bytes(data[4:8], "little") not in (0, 1, 3):
        return False
    try:
        return isinstance(marshal.loads(data[16:]), CodeType)
    except (EOFError, ValueError, TypeError):
        return False


def copy_resources(source, destination):
    """Copy the complete tree except exact current-interpreter source caches.

    No arbitrary .pyc or __pycache__ contents are excluded. Originals are never
    cleaned; the production validator still inventories every copied file.
    """
    source, destination = Path(source), Path(destination)
    caches = {Path(importlib.util.cache_from_source(str(p)))
              for p in source.rglob("*.py") if p.is_file()}

    def ignore(directory, names):
        return [name for name in names if source_cache(Path(directory) / name, caches)]

    shutil.copytree(source, destination, ignore=ignore, symlinks=True)


@contextmanager
def validation_project(validator, root, candidate, name):
    """Full package copies plus real external targets at canonical locations.

    Self-links resolve into the copied candidate, as in the real validator.
    Missing external links remain missing, not stubbed or rewritten. Unknown
    caches remain in the copy and therefore in the validator's receipt.
    """
    root, candidate = Path(root), Path(candidate)
    with tempfile.TemporaryDirectory(prefix="skill-validation-6749-") as directory:
        project = Path(directory).resolve()
        copied = project / candidate.relative_to(root)
        copy_resources(candidate, copied)
        live = root / ".github/skills" / name
        if live.exists():
            copy_resources(live, project / live.relative_to(root))
        for path in candidate.rglob("*.md"):
            for link in validator.markdown_targets(path.read_text()):
                parsed = urlsplit(link)
                resource = unquote(parsed.path)
                if parsed.scheme or parsed.netloc or not resource or "{" in resource:
                    continue
                if resource.startswith("/") or ".." in Path(resource).parts:
                    continue  # Let the real validator reject unsafe links.
                own = f".github/skills/{name}"
                if resource == own or resource.startswith(own + "/"):
                    continue
                external = root / resource
                if not resource.startswith((".github/", "x-ipe-docs/", "src/", "tests/")):
                    if (candidate / path.relative_to(candidate).parent / resource).exists():
                        continue
                target = project / resource
                if external.exists() and not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if external.is_dir():
                        copy_resources(external, target)
                    else:
                        shutil.copy2(external, target, follow_symlinks=False)
        yield project, copied


def validate_resources(validator, root, candidate, name, kind):
    with validation_project(validator, root, candidate, name) as (project, copied):
        return validator.validate(project, copied, name, kind)