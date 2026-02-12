"""
FEATURE-025-C: KB Manager Skill

KBManagerService: AI-powered KB orchestration — classification, summary
generation, search, and reorganization.
"""
import json
import os
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from x_ipe.services.kb_service import KBService
from x_ipe.services.llm_service import LLMService
from x_ipe.tracing import x_ipe_tracing


class KBManagerService:
    """Orchestrates AI-powered classification, summary, search, reorganization."""

    SESSION_TIMEOUT_MINUTES = 30
    MAX_FILE_BYTES = 1_048_576  # 1 MB
    TEXT_EXTENSIONS = {
        '.md', '.txt', '.py', '.js', '.ts', '.yaml', '.yml', '.json',
        '.csv', '.html', '.css', '.java', '.go', '.rs', '.c', '.cpp',
        '.h', '.jsx', '.tsx', '.sh', '.bash', '.xml', '.toml', '.ini',
        '.cfg', '.sql', '.rb', '.php', '.swift', '.kt', '.scala',
    }

    def __init__(self, kb_service: KBService, llm_service: LLMService):
        self.kb_service = kb_service
        self.llm_service = llm_service
        self._pending_sessions: dict = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @x_ipe_tracing()
    def classify(self, paths: list) -> dict:
        """Classify landing files into topic categories via LLM.

        Args:
            paths: List of relative paths (e.g. ["landing/api-guide.md"])

        Returns:
            dict with session_id and suggestions list

        Raises:
            ValueError: If a processing session is already active
        """
        self._cleanup_expired_sessions()

        active = [s for s in self._pending_sessions.values()
                  if s["status"] == "pending"]
        if active:
            raise ValueError("A processing session is already active")

        if not paths:
            session_id = str(uuid.uuid4())
            self._pending_sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "pending",
                "suggestions": [],
            }
            return {"session_id": session_id, "suggestions": []}

        # Read file contents
        files_data = []
        for path in paths:
            content = self._read_file_content(path)
            files_data.append({
                "path": path,
                "name": os.path.basename(path),
                "content": content,
            })

        # Get existing topics for context
        existing_topics = self.kb_service.get_topics()

        # Call LLM or fallback
        if self.llm_service.is_available():
            prompt = self._build_classify_prompt(files_data, existing_topics)
            system = ("You are a knowledge base organizer. "
                      "Classify files into topics based on their content.")
            response = self.llm_service.complete(prompt, system=system)
            suggestions = self._parse_classification_response(response)
        else:
            suggestions = [
                {"file": f["name"], "topic": "uncategorized", "confidence": 0.0}
                for f in files_data
            ]

        # Map suggestions back to paths
        name_to_path = {f["name"]: f["path"] for f in files_data}
        for s in suggestions:
            s["path"] = name_to_path.get(s["file"], "")
            s.setdefault("suggested_topic", s.get("topic", "uncategorized"))

        session_id = str(uuid.uuid4())
        self._pending_sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
            "suggestions": suggestions,
        }

        return {"session_id": session_id, "suggestions": suggestions}

    @x_ipe_tracing()
    def execute_classification(self, session_id: str, classifications: list) -> dict:
        """Execute confirmed classification — move files and generate summaries.

        Args:
            session_id: Session UUID from classify()
            classifications: List of {path, topic} dicts

        Returns:
            dict with moved, errors, summaries_generated

        Raises:
            KeyError: If session_id not found
        """
        if session_id not in self._pending_sessions:
            raise KeyError(f"Session not found: {session_id}")

        session = self._pending_sessions[session_id]
        session["status"] = "confirmed"

        kb_root = self.kb_service.kb_root
        moved = []
        errors = []
        topics_affected = set()

        for item in classifications:
            src_path = kb_root / item["path"]
            topic = item["topic"]
            topic_dir = kb_root / "topics" / topic / "raw"
            topic_dir.mkdir(parents=True, exist_ok=True)

            dest = topic_dir / src_path.name
            if dest.exists():
                stem = dest.stem
                suffix = dest.suffix
                counter = 1
                while dest.exists():
                    dest = topic_dir / f"{stem}-{counter}{suffix}"
                    counter += 1

            try:
                if not src_path.exists():
                    errors.append({"file": item["path"], "error": "File not found"})
                    continue
                shutil.move(str(src_path), str(dest))
                moved.append({
                    "file": src_path.name,
                    "from": item["path"],
                    "to": str(dest.relative_to(kb_root)),
                })
                topics_affected.add(topic)
            except Exception as e:
                errors.append({"file": item["path"], "error": str(e)})

        # Update metadata for affected topics
        for topic in topics_affected:
            self._update_topic_metadata(topic)

        # Generate summaries
        summaries_generated = []
        for topic in topics_affected:
            try:
                self.generate_summary(topic)
                summaries_generated.append(topic)
            except Exception:
                pass  # Summary failure shouldn't block file moves

        # Refresh index
        self.kb_service.refresh_index()

        del self._pending_sessions[session_id]

        return {
            "moved": moved,
            "errors": errors,
            "summaries_generated": summaries_generated,
        }

    @x_ipe_tracing()
    def cancel_processing(self, session_id: str) -> dict:
        """Cancel a pending classification session.

        Raises:
            KeyError: If session_id not found
        """
        if session_id not in self._pending_sessions:
            raise KeyError(f"Session not found: {session_id}")

        self._pending_sessions[session_id]["status"] = "cancelled"
        del self._pending_sessions[session_id]
        return {"status": "cancelled"}

    @x_ipe_tracing()
    def generate_summary(self, topic: str) -> dict:
        """Generate AI summary for a topic's files.

        Returns:
            dict with topic, version, path of generated summary
        """
        kb_root = self.kb_service.kb_root
        topic_raw = kb_root / "topics" / topic / "raw"

        if not topic_raw.exists():
            return {"topic": topic, "error": "Topic not found"}

        # Read files
        files_data = []
        for fp in sorted(topic_raw.iterdir()):
            if fp.is_file():
                content = self._read_file_content(
                    str(fp.relative_to(kb_root))
                )
                files_data.append({"name": fp.name, "content": content})

        if not files_data:
            return {"topic": topic, "error": "No files in topic"}

        if not self.llm_service.is_available():
            return {"topic": topic, "error": "LLM not available"}

        prompt = self._build_summary_prompt(topic, files_data)
        system = "You are a technical writer creating knowledge base summaries."
        summary_text = self.llm_service.complete(prompt, system=system)

        # Write versioned summary
        processed_dir = kb_root / "processed" / topic
        processed_dir.mkdir(parents=True, exist_ok=True)
        version = self._get_next_summary_version(topic)
        summary_path = processed_dir / f"summary-v{version}.md"

        file_list = "\n".join(f"- {f['name']}" for f in files_data)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        header = (
            f"# Topic: {topic}\n\n"
            f"> Generated: {now}\n"
            f"> Version: v{version}\n"
            f"> Files: {len(files_data)} files\n\n"
            f"## Files in this topic\n\n{file_list}\n\n"
        )
        summary_path.write_text(header + summary_text, encoding="utf-8")

        return {
            "topic": topic,
            "version": version,
            "path": str(summary_path.relative_to(kb_root)),
        }

    @x_ipe_tracing()
    def search(self, query: str) -> list:
        """Search file index for matching entries (case-insensitive).

        Returns:
            List of matching file entries
        """
        if not query:
            return []

        query_lower = query.lower()
        index = self.kb_service.get_index()
        results = []

        for entry in index.get("files", []):
            name = entry.get("name", "").lower()
            path = entry.get("path", "").lower()
            topic = entry.get("topic", "").lower() if "topic" in entry else ""

            if (query_lower in name or query_lower in path or
                    query_lower in topic):
                results.append(entry)

        return results

    @x_ipe_tracing()
    def reorganize(self) -> dict:
        """Analyze topics and suggest merges/renames.

        Returns:
            dict with changes list and summary
        """
        topics = self.kb_service.get_topics()
        if not topics or not self.llm_service.is_available():
            return {"changes": [], "summary": "No reorganization needed"}

        prompt = (
            f"Analyze these knowledge base topics and suggest reorganization:\n"
            f"Topics: {', '.join(topics)}\n\n"
            f"Suggest merges for similar topics. Return JSON:\n"
            f'[{{"action": "merge", "from": "topic1", "to": "topic2"}}]'
        )
        system = "You are a knowledge base organizer."
        response = self.llm_service.complete(prompt, system=system)
        changes = self._parse_classification_response(response)

        return {
            "changes": changes,
            "summary": f"Suggested {len(changes)} reorganization(s)",
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _read_file_content(self, rel_path: str) -> str:
        """Read file content, detecting binary files."""
        kb_root = self.kb_service.kb_root
        full_path = kb_root / rel_path

        if not full_path.exists():
            return ""

        ext = full_path.suffix.lower()
        if ext not in self.TEXT_EXTENSIONS:
            return f"[Binary file - {ext}]"

        # Check for binary content (null bytes in first 8KB)
        try:
            sample = full_path.read_bytes()[:8192]
            if b'\x00' in sample:
                return f"[Binary file - {ext}]"
        except Exception:
            return "[Unreadable file]"

        # Read as text
        try:
            text = full_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = full_path.read_text(encoding="latin-1")
            except Exception:
                return "[Encoding error]"

        # Truncate
        if len(text) > self.MAX_FILE_BYTES:
            text = text[:self.MAX_FILE_BYTES] + "\n... [truncated]"

        return text

    def _build_classify_prompt(self, files: list, existing_topics: list) -> str:
        """Build classification prompt for LLM."""
        file_sections = []
        for i, f in enumerate(files, 1):
            content = f["content"][:500] if len(f["content"]) > 500 else f["content"]
            file_sections.append(f"{i}. {f['name']}: {content}")

        topics_str = ", ".join(existing_topics) if existing_topics else "none yet"

        return (
            "Classify these files into topic categories. Return JSON array.\n\n"
            f"Files:\n" + "\n".join(file_sections) + "\n\n"
            f"Rules:\n"
            f"- Topic names must be kebab-case (lowercase, hyphens)\n"
            f"- Suggest existing topics when possible: {topics_str}\n"
            f"- Each file gets exactly one topic\n"
            f"- Include confidence score 0.0-1.0\n\n"
            f'Response format:\n'
            f'[{{"file": "filename", "topic": "topic-name", "confidence": 0.85}}]'
        )

    def _build_summary_prompt(self, topic: str, files: list) -> str:
        """Build summary generation prompt for LLM."""
        file_sections = []
        for f in files:
            file_sections.append(f"### {f['name']}\n{f['content']}")

        return (
            f'Create a concise summary of these files in the "{topic}" topic.\n\n'
            + "\n\n".join(file_sections) + "\n\n"
            "Requirements:\n"
            "- List key concepts and themes\n"
            "- Note any binary files not analyzed\n"
            "- Keep summary under 500 words\n"
            "- Use markdown formatting"
        )

    def _parse_classification_response(self, response: str) -> list:
        """Extract JSON array from LLM response, handling markdown wrappers."""
        # Try direct parse
        try:
            result = json.loads(response)
            if isinstance(result, list):
                return result
        except (json.JSONDecodeError, TypeError):
            pass

        # Try extracting from markdown code block
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group(1))
                if isinstance(result, list):
                    return result
            except (json.JSONDecodeError, TypeError):
                pass

        # Try finding JSON array
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group(0))
                if isinstance(result, list):
                    return result
            except (json.JSONDecodeError, TypeError):
                pass

        return []

    def _get_next_summary_version(self, topic: str) -> int:
        """Find highest summary version and return next."""
        processed_dir = self.kb_service.kb_root / "processed" / topic
        if not processed_dir.exists():
            return 1

        max_version = 0
        for fp in processed_dir.iterdir():
            match = re.match(r'summary-v(\d+)\.md', fp.name)
            if match:
                max_version = max(max_version, int(match.group(1)))

        return max_version + 1

    def _update_topic_metadata(self, topic: str) -> None:
        """Update topic metadata after file changes."""
        kb_root = self.kb_service.kb_root
        topic_dir = kb_root / "topics" / topic
        raw_dir = topic_dir / "raw"

        if not raw_dir.exists():
            return

        file_count = sum(1 for f in raw_dir.iterdir() if f.is_file())
        metadata = {
            "name": topic,
            "file_count": file_count,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        metadata_path = topic_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def _cleanup_expired_sessions(self) -> None:
        """Remove sessions older than SESSION_TIMEOUT_MINUTES."""
        now = datetime.now(timezone.utc)
        expired = []
        for sid, session in self._pending_sessions.items():
            created = datetime.fromisoformat(session["created_at"])
            if (now - created).total_seconds() > self.SESSION_TIMEOUT_MINUTES * 60:
                expired.append(sid)
        for sid in expired:
            del self._pending_sessions[sid]
