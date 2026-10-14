"""Tests for FEATURE-047-B: Semantic DAO Logging & Workflow Migration.

Covers:
- DAO logging steps in SKILL.md
- Log template existence and structure
- Call site migration (14 files)
- Old skill deletion
- Legacy log reference removal
"""

import os
import re
from pathlib import Path

import pytest
from tests.test_architecture_draw_skill import frontmatter, linked_resource, section, yaml_contract
from tests.test_workflow_settings import (
    HYBRID, current_candidate_policy, interaction_rows, validate_mode_policy,
)

ROOT = Path(__file__).resolve().parent.parent
DAO_ENTRY = ROOT / '.github/skills/x-ipe-assistant-user-representative-Engineer/SKILL.md'
LOG_TARGET = '.github/skills/x-ipe-assistant-user-representative-Engineer/references/dao-log-format.md'
LIFECYCLE_TARGET = '.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md'
LEGACY_CALLERS = {
    'x-ipe-task-based-dev-environment/SKILL.md',
    'x-ipe-task-based-idea-mockup/SKILL.md',
    'x-ipe-task-based-idea-to-architecture/SKILL.md',
    'x-ipe-task-based-ideation/SKILL.md',
    'x-ipe-task-based-share-idea/SKILL.md',
}


def validate_record_procedure(content):
    phase = re.search(r'<phase_3 name="录 — Record">(.*?)</phase_3>', section(content, 'Execution Procedure'), re.S)
    assert phase and '<name>Write Semantic Log</name>' in phase[1], 'Missing log procedure'
    assert '<constraints>MANDATORY. Append-only. One entry per invocation.</constraints>' in phase[1]
    assert LOG_TARGET in phase[1]


def validate_caller_message_context(content):
    assert 'message_context' in content, 'Missing current DAO message_context'
    assert not re.search(r'type:\s*"routing"', section(content, 'Execution Procedure')), 'Obsolete DAO routing payload'


def validate_log_format(content):
    registry = section(content, 'Registry Table Row')
    header = next(line for line in registry.splitlines() if line.startswith('| Entry ID |'))
    assert [cell.strip() for cell in header.strip('|').split('|')] == [
        'Entry ID', 'Timestamp', 'Task ID', 'Calling Skill', 'Disposition', 'Confidence', 'Summary',
    ]
    detail = section(content, 'Detail Section')
    fields = dict(re.findall(r'^- \*\*([^:]+):\*\* \{([^}]+)\}$', detail, re.M))
    expected = {
        'Timestamp': 'ISO 8601', 'Task ID': 'task_id', 'Feature ID': 'feature_id or N/A',
        'Workflow': 'workflow_name or N/A', 'Calling Skill': 'calling_skill',
        'Source': 'source', 'Disposition': 'disposition', 'Confidence': 'confidence',
    }
    assert fields == expected, 'Missing/incorrect referenced log metadata'
    assert '### Message\n> {original message content}' in detail
    assert '### Guidance Returned\n> {DAO response content}' in detail
    assert '### Rationale\n> {rationale_summary}' in detail
    for field in ('suggested_skills:', 'skill_name:', 'match_strength:', 'reason:', 'execution_steps:', 'phase:', 'step:'):
        assert field in detail, f'Missing log evidence shape: {field}'
    return fields


class TestDaoLoggingSteps:
    """AC-047-B.1 through AC-047-B.8: DAO skill has logging procedure."""

    SKILL_PATH = ROOT / ".github" / "skills" / "x-ipe-assistant-user-representative-Engineer" / "SKILL.md"

    def _read_skill(self):
        return self.SKILL_PATH.read_text(encoding="utf-8")

    def test_skill_has_logging_step(self):
        """AC-047-B.1: DAO has a logging/record step after the 7-step backbone."""
        content = self._read_skill()
        frontmatter(content, 'x-ipe-assistant-user-representative-Engineer')
        validate_record_procedure(content)

    def test_logging_references_dao_folder(self):
        """AC-047-B.1: Logging step references x-ipe-docs/dao/ folder."""
        content = self._read_skill()
        assert "x-ipe-docs/dao/" in content

    def test_log_entry_metadata_fields(self):
        """AC-047-B.2: Exact linked log contract has metadata + evidence placeholders."""
        validate_log_format(linked_resource(self.SKILL_PATH, LOG_TARGET))

    def test_semantic_task_type_naming(self):
        """AC-047-B.4: Log files follow decisions_made_{semantic_task_type}.md pattern."""
        content = self._read_skill()
        assert "decisions_made_" in content

    def test_merge_or_create_logic(self):
        """AC-047-B.7: DAO describes merge-vs-create logic for log files."""
        content = self._read_skill()
        log = linked_resource(self.SKILL_PATH, LOG_TARGET)
        assert 'Read existing registry table to determine next ID' in section(log, 'Entry ID')
        assert 'Create if missing' in section(content, 'Execution Procedure')
        assert 'Append ONE entry covering ALL units' in section(content, 'Execution Procedure')

    def test_registry_table_mentioned(self):
        """AC-047-B.8: DAO describes a registry table at top of log files."""
        log = linked_resource(self.SKILL_PATH, LOG_TARGET)
        validate_log_format(log)
        assert log.index('## Registry Table Row') < log.index('## Detail Section')

    def test_no_logging_restriction_remains(self):
        """FEATURE-047-B lifts the v1 logging restriction."""
        content = self._read_skill()
        assert "MUST NOT write semantic logs" not in content, \
            "Old v1 logging restriction still present — should be removed"

    def test_skill_under_600_lines(self):
        """NFR: SKILL.md stays under 600 lines after greeting and presentation phases."""
        lines = self._read_skill().splitlines()
        assert len(lines) < 600, f"SKILL.md is {len(lines)} lines, exceeds 600 limit"


class TestDaoLogTemplate:
    """AC-047-B.3, AC-047-B.8: Log template exists with proper structure."""

    TEMPLATE_PATH = ROOT / ".github" / "skills" / "x-ipe-assistant-user-representative-Engineer" / "templates" / "dao-log-template.md"

    def test_template_exists(self):
        """Log template file exists."""
        assert self.TEMPLATE_PATH.exists(), f"Missing: {self.TEMPLATE_PATH}"

    def test_template_has_registry_table_header(self):
        """AC-047-B.8: Template has a registry table structure."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "Entry" in content and "Timestamp" in content and "Disposition" in content

    def test_template_has_semantic_placeholder(self):
        """Template has placeholder for semantic task type."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "{" in content, "Template should have placeholder for semantic task type"


class TestCallSiteMigration:
    """AC-047-B.10, AC-047-B.11: All call sites migrated to DAO."""

    SKILLS_DIR = ROOT / ".github" / "skills"

    MIGRATED_FILES = [
        "x-ipe-task-based-bug-fix/SKILL.md",
        "x-ipe-task-based-code-implementation/SKILL.md",
        "x-ipe-task-based-code-refactor/SKILL.md",
        "x-ipe-task-based-dev-environment/SKILL.md",
        "x-ipe-task-based-feature-closing/SKILL.md",
        "x-ipe-task-based-idea-mockup/SKILL.md",
        "x-ipe-task-based-idea-to-architecture/SKILL.md",
        "x-ipe-task-based-ideation/SKILL.md",
        "x-ipe-task-based-requirement-gathering/SKILL.md",
        "x-ipe-task-based-share-idea/SKILL.md",
        "x-ipe-workflow-task-execution/SKILL.md",
        "x-ipe-meta-skill-creator/templates/x-ipe-task-based.md",
        "x-ipe-meta-skill-creator/references/skill-general-guidelines-v2.md",
        "x-ipe-tool-web-search/SKILL.md",
    ]

    @pytest.mark.parametrize("rel_path", MIGRATED_FILES)
    def test_no_old_decision_making_reference(self, rel_path):
        """AC-047-B.10: No references to x-ipe-tool-decision-making in migrated files."""
        fpath = self.SKILLS_DIR / rel_path
        assert fpath.is_file(), f'Missing migrated callsite: {rel_path}'
        content = fpath.read_text(encoding="utf-8")
        assert "x-ipe-tool-decision-making" not in content, \
            f"{rel_path} still references x-ipe-tool-decision-making"

    @pytest.mark.parametrize("rel_path", [
        "x-ipe-task-based-bug-fix/SKILL.md",
        "x-ipe-task-based-code-implementation/SKILL.md",
        "x-ipe-task-based-code-refactor/SKILL.md",
        "x-ipe-task-based-dev-environment/SKILL.md",
        "x-ipe-task-based-feature-closing/SKILL.md",
        "x-ipe-task-based-idea-mockup/SKILL.md",
        "x-ipe-task-based-idea-to-architecture/SKILL.md",
        "x-ipe-task-based-ideation/SKILL.md",
        "x-ipe-task-based-requirement-gathering/SKILL.md",
        "x-ipe-task-based-share-idea/SKILL.md",
    ])
    def test_current_message_context_or_exposed_legacy_gap(self, rel_path):
        """Do not claim all name-migrated callsites have migrated payload semantics."""
        fpath = self.SKILLS_DIR / rel_path
        assert fpath.is_file(), f'Missing migrated callsite: {rel_path}'
        content = fpath.read_text(encoding="utf-8")
        lifecycle_link = ".github/skills/x-ipe-workflow-task-execution/references/lifecycle.md"
        if lifecycle_link in content:
            common = linked_resource(fpath, lifecycle_link)
            mode_section = section(common, 'Interaction modes')
            import yaml
            blocks = re.findall(r'```yaml\n(.*?)\n```', mode_section, re.S)
            assert len(blocks) == 1
            context = yaml.safe_load(blocks[0])['input']['message_context']
            assert {'source', 'calling_skill', 'task_id', 'workflow_name', 'messages', 'downstream_context'} <= context.keys()
            assert context['source'] == 'ai' and context['messages'][0]['content']
            assert "instruction_units" in common and "execution_plan" in common
            assert "approval` is guidance, NOT human approval" in common
        else:
            assert rel_path in LEGACY_CALLERS, 'Unexpected unmigrated caller'
            procedure = section(content, 'Execution Procedure')
            assert 'x-ipe-assistant-user-representative-Engineer' in procedure
            assert 'type: "routing"' in procedure and 'completed_skill_output' in procedure
            with pytest.raises(AssertionError, match='Missing current DAO message_context'):
                validate_caller_message_context(content)
        declared = yaml_contract(DAO_ENTRY.read_text(), 'Output Result', 'operation_output')
        result = declared['result']
        assert {'instruction_units', 'execution_plan', 'confidence', 'fallback_required'} <= result.keys()
        unit = result['instruction_units'][0]
        assert {'disposition', 'content', 'rationale_summary', 'depends_on', 'suggested_skills'} <= unit.keys()

    def test_template_uses_dao(self):
        """AC-047-B.19: Task-based template references DAO."""
        fpath = self.SKILLS_DIR / "x-ipe-meta-skill-creator" / "templates" / "x-ipe-task-based.md"
        content = fpath.read_text(encoding="utf-8")
        assert "x-ipe-assistant-user-representative-Engineer" in content

    def test_guidelines_use_dao(self):
        """AC-047-B.20: Guidelines reference DAO."""
        fpath = self.SKILLS_DIR / "x-ipe-meta-skill-creator" / "references" / "skill-general-guidelines-v2.md"
        content = fpath.read_text(encoding="utf-8")
        assert "Preserve all three interaction modes" in content
        assert "use representative only when policy routes an actual decision to it" in content
        assert "no forced DAO call for clear inputs" in content
        template = (self.SKILLS_DIR / "x-ipe-meta-skill-creator/templates/x-ipe-task-based.md").read_text()
        assert "x-ipe-assistant-user-representative-Engineer" in template


class TestOldSkillDeletion:
    """AC-047-B.9: Old decision-making skill folder is deleted."""

    def test_decision_making_folder_deleted(self):
        """AC-047-B.9: x-ipe-tool-decision-making folder does not exist."""
        old_path = ROOT / ".github" / "skills" / "x-ipe-tool-decision-making"
        assert not old_path.exists(), \
            f"Old skill folder still exists: {old_path}"


class TestLegacyLogReferences:
    """AC-047-B.12, AC-047-B.13: Legacy decision_made_by_ai.md refs removed from skills."""

    SKILLS_DIR = ROOT / ".github" / "skills"

    def test_no_decision_made_by_ai_in_active_skills(self):
        """AC-047-B.12: No references to decision_made_by_ai.md in skill files."""
        hits = []
        for md_file in self.SKILLS_DIR.rglob("*.md"):
            # Skip the deleted folder if it somehow still exists
            if "x-ipe-tool-decision-making" in str(md_file):
                continue
            content = md_file.read_text(encoding="utf-8")
            if "decision_made_by_ai" in content:
                hits.append(str(md_file.relative_to(self.SKILLS_DIR)))
        assert not hits, f"Legacy decision_made_by_ai.md still referenced in: {hits}"


class TestThreeModePreservation:
    """AC-047-B.14 through AC-047-B.18: 3-mode behavior preserved."""

    SKILLS_DIR = ROOT / ".github" / "skills"

    @pytest.mark.parametrize("rel_path", [
        "x-ipe-task-based-bug-fix/SKILL.md",
        "x-ipe-task-based-code-implementation/SKILL.md",
        "x-ipe-task-based-code-refactor/SKILL.md",
    ])
    def test_manual_mode_untouched(self, rel_path):
        """AC-047-B.14/B.18: Manual mode still asks human directly."""
        fpath = self.SKILLS_DIR / rel_path
        assert fpath.is_file()
        content = fpath.read_text(encoding="utf-8")
        # Preserve the decision, not the spelling of a pseudocode ELSE branch.
        lifecycle_link = ".github/skills/x-ipe-workflow-task-execution/references/lifecycle.md"
        assert lifecycle_link in content
        common = linked_resource(fpath, lifecycle_link)
        rows = interaction_rows(common)
        assert rows['interact-with-human'] == ('Ask human and wait', 'Human review and route confirmation')
        # Manual mode remains human. Installed hybrid wording is a disclosed
        # unresolved compatibility baseline, not proof of the current app meaning.
        corrected = current_candidate_policy()
        validate_mode_policy(corrected)
        assert rows == corrected
        assert re.search(r"\bhuman\b.{0,50}(ask|go to).{0,20}human", content, re.I | re.S)


@pytest.mark.parametrize('field', ['Timestamp', 'Calling Skill', 'Disposition', 'Confidence'])
def test_missing_referenced_log_metadata_is_detected(field):
    content = linked_resource(DAO_ENTRY, LOG_TARGET)
    corrupt = re.sub(rf'^- \*\*{re.escape(field)}:\*\*.*\n', '', content, flags=re.M)
    # Entry/output tokens elsewhere cannot stand in for metadata in Detail Section.
    corrupt += f'\nMention {field} elsewhere\n'
    with pytest.raises(AssertionError, match='referenced log metadata'):
        validate_log_format(corrupt)


def test_dao_missing_logging_procedure_is_detected():
    content = DAO_ENTRY.read_text()
    corrupt = re.sub(r'<phase_3 name="录 — Record">.*?</phase_3>', '', content, flags=re.S)
    with pytest.raises(AssertionError, match='Missing log procedure'):
        validate_record_procedure(corrupt)


def test_log_resource_cannot_be_replaced_with_unrelated_token_file(tmp_path):
    entry = tmp_path / 'SKILL.md'
    refs = tmp_path / 'references'
    refs.mkdir()
    entry.write_text('[log](references/dao-log-format.md)\n[example](references/example.md)')
    (refs / 'dao-log-format.md').write_text('# Log\nNo metadata contract here\n')
    (refs / 'example.md').write_text(linked_resource(DAO_ENTRY, LOG_TARGET))
    with pytest.raises(AssertionError, match='Missing section'):
        validate_log_format(linked_resource(entry, 'references/dao-log-format.md', tmp_path))


@pytest.mark.parametrize('evidence', ['rationale_summary', 'match_strength:', 'execution_steps:'])
def test_missing_log_evidence_shape_is_detected(evidence):
    content = linked_resource(DAO_ENTRY, LOG_TARGET)
    with pytest.raises(AssertionError):
        validate_log_format(content.replace(evidence, 'unrelated'))
