"""
FEATURE-027-C: Skill & Instruction Translation

SkillTranslator: Translate canonical X-IPE skills to CLI-specific formats.
"""
import logging
import shutil
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable

from x_ipe.tracing import x_ipe_tracing

logger = logging.getLogger(__name__)

INSTRUCTIONS_TEMPLATE = 'instructions-template.md'


@dataclass
class TranslationResult:
    """Result of a skill translation operation."""
    translated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


class SkillTranslator:
    """
    Translate canonical X-IPE skills to CLI-specific formats.

    FEATURE-027-C: Skill & Instruction Translation

    Works outside Flask context (CLI commands).
    Follows CLIAdapterService pattern: stateless methods, @x_ipe_tracing.
    """

    @x_ipe_tracing()
    def translate_skills(
        self,
        source: Path,
        target: Path,
        adapter,  # CLIAdapterData
    ) -> TranslationResult:
        """Translate all skills from source to target using adapter strategy."""
        if adapter.name == 'copilot':
            return TranslationResult()  # No-op

        if not source.exists() or not source.is_dir():
            logger.warning(f"Source skills directory not found: {source}")
            return TranslationResult()

        if adapter.name == 'opencode':
            return self._translate_opencode(source, target)
        elif adapter.name == 'claude-code':
            return self._translate_claude_code(source, target)
        else:
            return self._translate_claude_code(source, target)

    @x_ipe_tracing()
    def generate_instructions(
        self,
        adapter,  # CLIAdapterData
        project_root: Path,
        template_path: Optional[Path] = None,
    ) -> Optional[Path]:
        """Generate CLI-specific instruction file from canonical template."""
        if adapter.name == 'copilot':
            return None  # No-op

        if template_path is None:
            template_path = (
                Path(__file__).parent.parent
                / 'resources' / 'templates' / INSTRUCTIONS_TEMPLATE
            )

        if not template_path.exists():
            logger.error(f"Instructions template not found: {template_path}")
            return None

        content = template_path.read_text(encoding='utf-8')
        target_path = project_root / adapter.instructions_file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding='utf-8')
        return target_path

    def _translate_opencode(self, source: Path, target: Path) -> TranslationResult:
        """Translate skills for OpenCode: filter frontmatter to name+description."""
        return self._translate_with_strategy(
            source, target, self.filter_opencode_frontmatter
        )

    def _translate_claude_code(self, source: Path, target: Path) -> TranslationResult:
        """Translate skills for Claude Code: preserve frontmatter as-is."""
        return self._translate_with_strategy(source, target, None)

    def _translate_with_strategy(
        self,
        source: Path,
        target: Path,
        transform_fn: Optional[Callable],
    ) -> TranslationResult:
        """Iterate skills and apply optional frontmatter transformation."""
        result = TranslationResult()

        for skill_dir in sorted(source.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / 'SKILL.md'
            if not skill_md.exists():
                continue

            try:
                self._copy_skill(skill_dir, target, transform_fn)
                result.translated += 1
            except Exception as e:
                msg = f"Failed to translate skill '{skill_dir.name}': {e}"
                logger.warning(msg)
                result.errors.append(msg)

        return result

    def _copy_skill(
        self,
        skill_dir: Path,
        target_base: Path,
        transform_fn: Optional[Callable],
    ) -> None:
        """Copy a single skill directory, optionally transforming frontmatter."""
        skill_name = skill_dir.name
        target_skill = target_base / skill_name
        target_skill.mkdir(parents=True, exist_ok=True)

        # Process SKILL.md
        skill_md = skill_dir / 'SKILL.md'
        content = skill_md.read_text(encoding='utf-8')

        if transform_fn:
            frontmatter, body = self.parse_frontmatter(content)
            transformed = transform_fn(frontmatter, skill_name)
            content = self.serialize_frontmatter(transformed, body)

        (target_skill / 'SKILL.md').write_text(content, encoding='utf-8')

        # Copy subdirectories and non-SKILL.md files
        self._copy_subdirectories(skill_dir, target_skill)

    def _copy_subdirectories(self, source_skill: Path, target_skill: Path) -> None:
        """Copy all files/subdirs except SKILL.md from source to target."""
        for item in source_skill.iterdir():
            if item.name == 'SKILL.md':
                continue
            dest = target_skill / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

    @staticmethod
    def parse_frontmatter(content: str) -> tuple[dict, str]:
        """Parse YAML frontmatter from markdown content."""
        if not content.startswith('---'):
            return {}, content

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content

        try:
            fm = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            fm = {}

        body = parts[2]
        return fm, body

    @staticmethod
    def serialize_frontmatter(frontmatter: dict, body: str) -> str:
        """Serialize frontmatter dict + body back to markdown."""
        if not frontmatter:
            return body.lstrip('\n')

        fm_str = yaml.safe_dump(
            frontmatter, default_flow_style=False, allow_unicode=True
        ).strip()
        return f"---\n{fm_str}\n---{body}"

    @staticmethod
    def filter_opencode_frontmatter(frontmatter: dict, dir_name: str) -> dict:
        """Filter frontmatter to OpenCode-compatible fields (name + description)."""
        result = {}
        result['name'] = frontmatter.get('name', dir_name)
        if 'description' in frontmatter:
            result['description'] = frontmatter['description']
        return result
