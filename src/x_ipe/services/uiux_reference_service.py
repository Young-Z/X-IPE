"""
UiuxReferenceService (FEATURE-033)

Validates, decodes, and persists UIUX reference data to idea folders.
Handles session numbering, base64 screenshot decoding, atomic writes,
and merged reference-data.json maintenance.
"""
import base64
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from x_ipe.tracing import x_ipe_tracing


class UiuxReferenceService:
    IDEAS_PATH = "x-ipe-docs/ideas"
    REQUIRED_FIELDS = ["version", "source_url", "timestamp", "idea_folder"]
    DATA_SECTIONS = ["colors", "elements", "design_tokens"]

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.ideas_root = self.project_root / self.IDEAS_PATH

    @x_ipe_tracing()
    def save_reference(self, data: dict) -> dict:
        """Main entry point — validate, decode, save session, update merge."""
        errors = self._validate_schema(data)
        if errors:
            return {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "; ".join(errors),
            }

        idea_folder = data["idea_folder"]
        idea_path = self._resolve_idea_path(idea_folder)
        if idea_path is None:
            return {
                "success": False,
                "error": "IDEA_NOT_FOUND",
                "message": f"Idea folder not found: {idea_folder}",
            }

        uiux_dir = idea_path / "uiux-references"
        sessions_dir = uiux_dir / "sessions"
        screenshots_dir = uiux_dir / "screenshots"

        sessions_dir.mkdir(parents=True, exist_ok=True)
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        session_number = self._get_next_session_number(sessions_dir)
        session_filename = f"ref-session-{session_number:03d}.json"
        session_path = sessions_dir / session_filename

        processed_data = self._decode_screenshots(data, screenshots_dir)

        screenshots_saved = self._count_decoded_screenshots(data, processed_data)

        save_data = {k: v for k, v in processed_data.items() if k != "idea_folder"}
        self._save_session_file(save_data, session_path)

        self._update_merged_reference(uiux_dir)

        return {
            "success": True,
            "session_file": session_filename,
            "session_number": session_number,
            "screenshots_saved": screenshots_saved,
            "merged_reference_updated": True,
        }

    def _validate_schema(self, data: dict) -> list:
        """Validate reference data schema. Returns list of error messages."""
        errors = []
        for field in self.REQUIRED_FIELDS:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")

        if not errors:
            has_data = False
            for section in self.DATA_SECTIONS:
                val = data.get(section)
                if val is not None and val != {} and val != []:
                    has_data = True
                    break
            if not has_data:
                errors.append(
                    "At least one data section (colors, elements, design_tokens) "
                    "must be non-empty"
                )

        return errors

    def _resolve_idea_path(self, idea_folder: str):
        """Resolve idea folder path. Returns Path or None if not found."""
        idea_path = self.ideas_root / idea_folder
        if idea_path.is_dir():
            return idea_path
        return None

    def _get_next_session_number(self, sessions_dir: Path) -> int:
        """Scan existing session files and return max+1."""
        pattern = re.compile(r"^ref-session-(\d{3})\.json$")
        max_num = 0
        for f in sessions_dir.iterdir():
            m = pattern.match(f.name)
            if m:
                max_num = max(max_num, int(m.group(1)))
        return max_num + 1

    def _decode_screenshots(self, data: dict, screenshots_dir: Path) -> dict:
        """Find base64:-prefixed values in elements, decode to files, replace with paths."""
        import copy
        result = copy.deepcopy(data)

        elements = result.get("elements")
        if not elements:
            return result

        for elem in elements:
            screenshots = elem.get("screenshots")
            if not screenshots:
                continue
            elem_id = elem.get("id", "unknown")
            for key in list(screenshots.keys()):
                val = screenshots[key]
                if val and isinstance(val, str) and val.startswith("base64:"):
                    raw_b64 = val[len("base64:"):]
                    try:
                        img_data = base64.b64decode(raw_b64)
                        filename = f"{elem_id}-{key}.png"
                        filepath = screenshots_dir / filename
                        filepath.write_bytes(img_data)
                        screenshots[key] = f"screenshots/{filename}"
                    except Exception:
                        screenshots[key] = None

        return result

    def _count_decoded_screenshots(self, original: dict, processed: dict) -> int:
        """Count how many base64 screenshots were decoded."""
        count = 0
        orig_elems = original.get("elements") or []
        for elem in orig_elems:
            screenshots = elem.get("screenshots") or {}
            for val in screenshots.values():
                if val and isinstance(val, str) and val.startswith("base64:"):
                    count += 1
        return count

    def _save_session_file(self, data: dict, session_path: Path) -> None:
        """Atomic write: tmp file + rename."""
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=str(session_path.parent), suffix=".tmp"
        )
        try:
            with os.fdopen(tmp_fd, "w") as f:
                json.dump(data, f, indent=2)
            os.rename(tmp_path, str(session_path))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def _update_merged_reference(self, uiux_dir: Path) -> None:
        """Read all session files, merge, and write reference-data.json."""
        sessions_dir = uiux_dir / "sessions"
        pattern = re.compile(r"^ref-session-(\d{3})\.json$")

        session_files = sorted(
            [f for f in sessions_dir.iterdir() if pattern.match(f.name)],
            key=lambda f: int(pattern.match(f.name).group(1)),
        )

        merged_colors = {}
        merged_elements = {}
        source_urls = []
        latest_design_tokens = {}

        for sf in session_files:
            session = json.loads(sf.read_text())

            for color in session.get("colors") or []:
                cid = color.get("id")
                if cid:
                    merged_colors[cid] = color

            for elem in session.get("elements") or []:
                eid = elem.get("id")
                if eid:
                    merged_elements[eid] = elem

            tokens = session.get("design_tokens")
            if tokens and tokens != {}:
                latest_design_tokens = tokens

            url = session.get("source_url")
            if url and url not in source_urls:
                source_urls.append(url)

        merged = {
            "colors": list(merged_colors.values()),
            "elements": list(merged_elements.values()),
            "design_tokens": latest_design_tokens,
            "source_urls": source_urls,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        merged_path = uiux_dir / "reference-data.json"
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=str(uiux_dir), suffix=".tmp"
        )
        try:
            with os.fdopen(tmp_fd, "w") as f:
                json.dump(merged, f, indent=2)
            os.rename(tmp_path, str(merged_path))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
