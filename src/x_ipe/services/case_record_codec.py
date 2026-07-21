"""Read and atomically update CR assessment metadata in CaseRecord.html."""

from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from x_ipe.tracing import x_ipe_tracing


class CaseRecordError(ValueError):
    """Raised when a case record cannot be safely read or updated."""


class RevisionConflictError(CaseRecordError):
    """Raised when a caller attempts to update a stale case revision."""


class CaseRecordCodec:
    """Codec for the bounded JSON metadata envelope in ``CaseRecord.html``."""

    START = "<!-- CR_CASE_METADATA_START -->"
    END = "<!-- CR_CASE_METADATA_END -->"
    SCRIPT_OPEN = '<script id="cr-case-metadata" type="application/json">'
    SCRIPT_CLOSE = "</script>"

    @x_ipe_tracing(level="INFO")
    def read(self, path: Path) -> dict[str, Any]:
        """Return validated metadata from a case record."""
        text = path.read_text(encoding="utf-8")
        start = text.find(self.START)
        end = text.find(self.END)
        if start < 0 or end < 0 or end <= start:
            raise CaseRecordError("CaseRecord metadata envelope is missing")
        block = text[start + len(self.START) : end]
        open_at = block.find(self.SCRIPT_OPEN)
        close_at = block.rfind(self.SCRIPT_CLOSE)
        if open_at < 0 or close_at < 0:
            raise CaseRecordError("CaseRecord metadata script is missing")
        raw = block[open_at + len(self.SCRIPT_OPEN) : close_at].strip()
        try:
            metadata = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CaseRecordError("CaseRecord metadata is invalid JSON") from exc
        self._validate(metadata)
        return metadata

    @x_ipe_tracing(level="INFO")
    def create_initial(self, path: Path, metadata: dict[str, Any]) -> None:
        """Create a minimal accessible case record with metadata."""
        self._validate(metadata)
        title = self._escape_text(metadata["case"]["name"])
        document = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title></head>
<body><main><h1>{title}</h1><p>No assessment has been generated.</p></main>
{self._envelope(metadata)}
</body></html>
"""
        self._atomic_write(path, document)

    @x_ipe_tracing(level="INFO")
    def merge(
        self,
        path: Path,
        patch: dict[str, Any],
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        """Deep-merge fields into the latest envelope and write atomically."""
        text = path.read_text(encoding="utf-8")
        current = self.read(path)
        revision = int(current.get("record_revision", 0))
        if expected_revision is not None and expected_revision != revision:
            raise RevisionConflictError("Case record changed since it was loaded")
        merged = copy.deepcopy(current)
        self._deep_merge(merged, patch)
        merged["record_revision"] = revision + 1
        self._validate(merged)
        start = text.index(self.START)
        end = text.index(self.END) + len(self.END)
        updated = text[:start] + self._envelope(merged) + text[end:]
        self._atomic_write(path, updated)
        return merged

    def marker(self, path: Path) -> str:
        """Return a lightweight revision and mtime marker."""
        metadata = self.read(path)
        return f'{metadata["record_revision"]}:{path.stat().st_mtime_ns}'

    def _envelope(self, metadata: dict[str, Any]) -> str:
        raw = json.dumps(metadata, indent=2, ensure_ascii=False).replace("<", "\\u003c")
        return f"{self.START}\n{self.SCRIPT_OPEN}\n{raw}\n{self.SCRIPT_CLOSE}\n{self.END}"

    @staticmethod
    def _deep_merge(target: dict[str, Any], patch: dict[str, Any]) -> None:
        for key, value in patch.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                CaseRecordCodec._deep_merge(target[key], value)
            else:
                target[key] = copy.deepcopy(value)

    @staticmethod
    def _validate(metadata: dict[str, Any]) -> None:
        if not isinstance(metadata, dict):
            raise CaseRecordError("CaseRecord metadata must be an object")
        if not isinstance(metadata.get("record_revision"), int):
            raise CaseRecordError("CaseRecord revision is missing")
        case = metadata.get("case")
        if not isinstance(case, dict) or not case.get("id") or not case.get("name"):
            raise CaseRecordError("CaseRecord case identity is missing")

    @staticmethod
    def _escape_text(value: str) -> str:
        return (
            str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
        )

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
