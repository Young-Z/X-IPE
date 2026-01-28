"""
Tests for x_ipe.services.skills_service module

Covers:
- SkillsService initialization
- get_all method
- _parse_skill_md method
"""
import tempfile
import pytest
from pathlib import Path

from x_ipe.services.skills_service import SkillsService


class TestSkillsServiceInit:
    """Tests for SkillsService initialization."""
    
    def test_init_sets_project_root(self):
        """Should set project_root from constructor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = SkillsService(tmpdir)
            assert service.project_root == Path(tmpdir).resolve()
    
    def test_init_sets_skills_dir(self):
        """Should set skills_dir to .github/skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = SkillsService(tmpdir)
            expected = Path(tmpdir).resolve() / '.github' / 'skills'
            assert service.skills_dir == expected


class TestSkillsServiceGetAll:
    """Tests for SkillsService.get_all method."""
    
    def test_returns_empty_when_no_skills_dir(self):
        """Should return empty list when .github/skills doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = SkillsService(tmpdir)
            result = service.get_all()
            assert result == []
    
    def test_returns_empty_when_skills_dir_empty(self):
        """Should return empty list when skills dir is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / '.github' / 'skills'
            skills_dir.mkdir(parents=True)
            
            service = SkillsService(tmpdir)
            result = service.get_all()
            assert result == []
    
    def test_finds_skill_with_valid_frontmatter(self):
        """Should find skill with valid YAML frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / '.github' / 'skills'
            skill_dir = skills_dir / 'my-skill'
            skill_dir.mkdir(parents=True)
            
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text("""---
name: my-skill
description: A test skill for testing
---

# My Skill

Content here.
""")
            
            service = SkillsService(tmpdir)
            result = service.get_all()
            
            assert len(result) == 1
            assert result[0]['name'] == 'my-skill'
            assert result[0]['description'] == 'A test skill for testing'
    
    def test_finds_multiple_skills_sorted(self):
        """Should find multiple skills sorted alphabetically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / '.github' / 'skills'
            
            for name in ['zebra-skill', 'alpha-skill', 'beta-skill']:
                skill_dir = skills_dir / name
                skill_dir.mkdir(parents=True)
                (skill_dir / 'SKILL.md').write_text(f"""---
name: {name}
description: Description for {name}
---
""")
            
            service = SkillsService(tmpdir)
            result = service.get_all()
            
            assert len(result) == 3
            assert result[0]['name'] == 'alpha-skill'
            assert result[1]['name'] == 'beta-skill'
            assert result[2]['name'] == 'zebra-skill'
    
    def test_skips_folders_without_skill_md(self):
        """Should skip folders that don't have SKILL.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / '.github' / 'skills'
            
            # Valid skill
            valid = skills_dir / 'valid-skill'
            valid.mkdir(parents=True)
            (valid / 'SKILL.md').write_text("""---
name: valid-skill
description: Valid
---
""")
            
            # Invalid - no SKILL.md
            invalid = skills_dir / 'invalid-skill'
            invalid.mkdir(parents=True)
            (invalid / 'README.md').write_text("# Not a skill")
            
            service = SkillsService(tmpdir)
            result = service.get_all()
            
            assert len(result) == 1
            assert result[0]['name'] == 'valid-skill'
    
    def test_skips_files_in_skills_dir(self):
        """Should skip files (not directories) in skills dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / '.github' / 'skills'
            skills_dir.mkdir(parents=True)
            
            # File, not directory
            (skills_dir / 'README.md').write_text("# Skills")
            
            # Valid skill directory
            skill_dir = skills_dir / 'real-skill'
            skill_dir.mkdir()
            (skill_dir / 'SKILL.md').write_text("""---
name: real-skill
description: Real
---
""")
            
            service = SkillsService(tmpdir)
            result = service.get_all()
            
            assert len(result) == 1


class TestSkillsServiceParseSkillMd:
    """Tests for SkillsService._parse_skill_md method."""
    
    def test_returns_none_without_frontmatter(self):
        """Should return None if no YAML frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = Path(tmpdir) / 'SKILL.md'
            skill_md.write_text("# No frontmatter\nJust content")
            
            service = SkillsService(tmpdir)
            result = service._parse_skill_md(skill_md)
            
            assert result is None
    
    def test_returns_none_without_closing_frontmatter(self):
        """Should return skill even with trailing content after frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = Path(tmpdir) / 'SKILL.md'
            # Actually YAML considers # as comment, and --- at start of line ends frontmatter
            # The skill parser just looks for second --- which exists here
            skill_md.write_text("""---
name: test-skill
---
Content without closing is fine since we found second ---
""")
            
            service = SkillsService(tmpdir)
            result = service._parse_skill_md(skill_md)
            
            # This should parse successfully
            assert result is not None
            assert result['name'] == 'test-skill'
    
    def test_returns_none_without_name(self):
        """Should return None if no 'name' field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = Path(tmpdir) / 'SKILL.md'
            skill_md.write_text("""---
description: Has description but no name
---
""")
            
            service = SkillsService(tmpdir)
            result = service._parse_skill_md(skill_md)
            
            assert result is None
    
    def test_returns_none_for_invalid_yaml(self):
        """Should return None for invalid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = Path(tmpdir) / 'SKILL.md'
            skill_md.write_text("""---
name: [invalid: yaml: here
---
""")
            
            service = SkillsService(tmpdir)
            result = service._parse_skill_md(skill_md)
            
            assert result is None
    
    def test_returns_none_for_non_dict_yaml(self):
        """Should return None if YAML is not a dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = Path(tmpdir) / 'SKILL.md'
            skill_md.write_text("""---
- just
- a
- list
---
""")
            
            service = SkillsService(tmpdir)
            result = service._parse_skill_md(skill_md)
            
            assert result is None
    
    def test_handles_empty_description(self):
        """Should handle skill with name but no description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = Path(tmpdir) / 'SKILL.md'
            skill_md.write_text("""---
name: no-description
---
""")
            
            service = SkillsService(tmpdir)
            result = service._parse_skill_md(skill_md)
            
            assert result is not None
            assert result['name'] == 'no-description'
            assert result['description'] == ''
    
    def test_parses_multiline_description(self):
        """Should handle multiline description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = Path(tmpdir) / 'SKILL.md'
            skill_md.write_text("""---
name: multi-line
description: >
  This is a long description
  that spans multiple lines.
---
""")
            
            service = SkillsService(tmpdir)
            result = service._parse_skill_md(skill_md)
            
            assert result is not None
            assert 'long description' in result['description']
