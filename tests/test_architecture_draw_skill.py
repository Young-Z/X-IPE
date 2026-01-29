"""
Tests for Architecture Diagram Renderer Skills (Split into two skills)

After refactoring, we now have:
1. tool-draw-layered-architecture - Module View diagrams
2. tool-draw-system-landscape - Landscape View diagrams

This test suite validates both skill structures.
"""

import os
import json
import pytest

# Base paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERED_SKILL_PATH = os.path.join(PROJECT_ROOT, ".github", "skills", "tool-draw-layered-architecture")
LANDSCAPE_SKILL_PATH = os.path.join(PROJECT_ROOT, ".github", "skills", "tool-draw-system-landscape")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "x-ipe-docs", "config", "tools.json")


class TestLayeredArchitectureSkillStructure:
    """Test tool-draw-layered-architecture folder and file structure."""

    def test_skill_folder_exists(self):
        """Skill folder exists at .github/skills/tool-draw-layered-architecture/"""
        assert os.path.isdir(LAYERED_SKILL_PATH), f"Skill folder not found at {LAYERED_SKILL_PATH}"

    def test_skill_md_exists(self):
        """SKILL.md exists"""
        skill_md = os.path.join(LAYERED_SKILL_PATH, "SKILL.md")
        assert os.path.isfile(skill_md), "SKILL.md not found"

    def test_templates_folder_exists(self):
        """templates/ folder exists"""
        templates_path = os.path.join(LAYERED_SKILL_PATH, "templates")
        assert os.path.isdir(templates_path), "templates/ folder not found"

    def test_module_view_template_exists(self):
        """module-view.html template exists"""
        template_path = os.path.join(LAYERED_SKILL_PATH, "templates", "module-view.html")
        assert os.path.isfile(template_path), "module-view.html not found"

    def test_references_folder_exists(self):
        """references/ folder exists"""
        refs_path = os.path.join(LAYERED_SKILL_PATH, "references")
        assert os.path.isdir(refs_path), "references/ folder not found"

    def test_examples_folder_exists(self):
        """examples/ folder exists"""
        examples_path = os.path.join(LAYERED_SKILL_PATH, "examples")
        assert os.path.isdir(examples_path), "examples/ folder not found"


class TestLayeredArchitectureSkillContent:
    """Test tool-draw-layered-architecture SKILL.md content."""

    @pytest.fixture
    def skill_content(self):
        skill_md = os.path.join(LAYERED_SKILL_PATH, "SKILL.md")
        if os.path.isfile(skill_md):
            with open(skill_md, "r") as f:
                return f.read()
        return ""

    def test_skill_md_has_frontmatter(self, skill_content):
        """SKILL.md has YAML frontmatter with name and description"""
        assert "---" in skill_content, "Missing YAML frontmatter"
        assert "name: tool-draw-layered-architecture" in skill_content, "Incorrect name in frontmatter"

    def test_skill_md_has_workflow_section(self, skill_content):
        """SKILL.md has Workflow section"""
        assert "## Execution Workflow" in skill_content or "Workflow" in skill_content

    def test_skill_md_references_module_view(self, skill_content):
        """SKILL.md focuses on module-view"""
        assert "module-view" in skill_content.lower()
        assert "Module View" in skill_content

    def test_skill_md_does_not_have_landscape_template_ref(self, skill_content):
        """SKILL.md should not reference landscape-view template (moved to other skill)"""
        assert "templates/landscape-view.html" not in skill_content

    def test_skill_md_references_landscape_skill(self, skill_content):
        """SKILL.md should reference the landscape skill for landscape diagrams"""
        assert "tool-draw-system-landscape" in skill_content


class TestLandscapeSkillStructure:
    """Test tool-draw-system-landscape folder and file structure."""

    def test_skill_folder_exists(self):
        """Skill folder exists at .github/skills/tool-draw-system-landscape/"""
        assert os.path.isdir(LANDSCAPE_SKILL_PATH), f"Skill folder not found at {LANDSCAPE_SKILL_PATH}"

    def test_skill_md_exists(self):
        """SKILL.md exists"""
        skill_md = os.path.join(LANDSCAPE_SKILL_PATH, "SKILL.md")
        assert os.path.isfile(skill_md), "SKILL.md not found"

    def test_templates_folder_exists(self):
        """templates/ folder exists"""
        templates_path = os.path.join(LANDSCAPE_SKILL_PATH, "templates")
        assert os.path.isdir(templates_path), "templates/ folder not found"

    def test_landscape_view_template_exists(self):
        """landscape-view.html template exists"""
        template_path = os.path.join(LANDSCAPE_SKILL_PATH, "templates", "landscape-view.html")
        assert os.path.isfile(template_path), "landscape-view.html not found"

    def test_references_folder_exists(self):
        """references/ folder exists"""
        refs_path = os.path.join(LANDSCAPE_SKILL_PATH, "references")
        assert os.path.isdir(refs_path), "references/ folder not found"

    def test_examples_folder_exists(self):
        """examples/ folder exists"""
        examples_path = os.path.join(LANDSCAPE_SKILL_PATH, "examples")
        assert os.path.isdir(examples_path), "examples/ folder not found"


class TestLandscapeSkillContent:
    """Test tool-draw-system-landscape SKILL.md content."""

    @pytest.fixture
    def skill_content(self):
        skill_md = os.path.join(LANDSCAPE_SKILL_PATH, "SKILL.md")
        if os.path.isfile(skill_md):
            with open(skill_md, "r") as f:
                return f.read()
        return ""

    def test_skill_md_has_frontmatter(self, skill_content):
        """SKILL.md has YAML frontmatter with name and description"""
        assert "---" in skill_content, "Missing YAML frontmatter"
        assert "name: tool-draw-system-landscape" in skill_content, "Incorrect name in frontmatter"

    def test_skill_md_has_workflow_section(self, skill_content):
        """SKILL.md has Workflow section"""
        assert "## Execution Workflow" in skill_content or "Workflow" in skill_content

    def test_skill_md_references_landscape_view(self, skill_content):
        """SKILL.md focuses on landscape-view"""
        assert "landscape-view" in skill_content.lower()
        assert "Landscape View" in skill_content

    def test_skill_md_documents_zones(self, skill_content):
        """SKILL.md documents zone elements"""
        assert "zone" in skill_content.lower() or "Zone" in skill_content

    def test_skill_md_documents_apps(self, skill_content):
        """SKILL.md documents app elements"""
        assert "app" in skill_content.lower() or "App" in skill_content

    def test_skill_md_documents_flows(self, skill_content):
        """SKILL.md documents flow elements"""
        assert "flow" in skill_content.lower() or "Flow" in skill_content

    def test_skill_md_references_layered_skill(self, skill_content):
        """SKILL.md should reference the layered skill for module diagrams"""
        assert "tool-draw-layered-architecture" in skill_content


class TestConfigIntegration:
    """Test tools.json configuration for both skills."""

    @pytest.fixture
    def config_content(self):
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        return {}

    def test_layered_skill_registered_in_architecture(self, config_content):
        """tool-draw-layered-architecture registered in ideation.architecture"""
        assert config_content.get("stages", {}).get("ideation", {}).get("architecture", {}).get("tool-draw-layered-architecture") == True

    def test_landscape_skill_registered_in_architecture(self, config_content):
        """tool-draw-system-landscape registered in ideation.architecture"""
        assert config_content.get("stages", {}).get("ideation", {}).get("architecture", {}).get("tool-draw-system-landscape") == True

    def test_layered_skill_disabled_in_ideation(self, config_content):
        """tool-draw-layered-architecture disabled in ideation.ideation (by default)"""
        assert config_content.get("stages", {}).get("ideation", {}).get("ideation", {}).get("tool-draw-layered-architecture") == False

    def test_landscape_skill_disabled_in_ideation(self, config_content):
        """tool-draw-system-landscape disabled in ideation.ideation (by default)"""
        assert config_content.get("stages", {}).get("ideation", {}).get("ideation", {}).get("tool-draw-system-landscape") == False


class TestModuleViewTemplate:
    """Test module-view.html template structure."""

    @pytest.fixture
    def template_content(self):
        template_path = os.path.join(LAYERED_SKILL_PATH, "templates", "module-view.html")
        if os.path.isfile(template_path):
            with open(template_path, "r") as f:
                return f.read()
        return ""

    def test_template_has_layer_structure(self, template_content):
        """Template has layer container"""
        assert ".layer" in template_content or "layer" in template_content.lower()

    def test_template_has_module_structure(self, template_content):
        """Template has module container"""
        assert ".module" in template_content or "module" in template_content.lower()

    def test_template_has_component_structure(self, template_content):
        """Template has component element"""
        assert ".component" in template_content or "component" in template_content.lower()

    def test_template_has_grid_system(self, template_content):
        """Template uses 12-column grid system"""
        assert "12" in template_content and "grid" in template_content.lower()


class TestLandscapeViewTemplate:
    """Test landscape-view.html template structure."""

    @pytest.fixture
    def template_content(self):
        template_path = os.path.join(LANDSCAPE_SKILL_PATH, "templates", "landscape-view.html")
        if os.path.isfile(template_path):
            with open(template_path, "r") as f:
                return f.read()
        return ""

    def test_template_has_zone_structure(self, template_content):
        """Template has zone container"""
        assert ".zone" in template_content or "zone" in template_content.lower()

    def test_template_has_app_structure(self, template_content):
        """Template has app container"""
        assert ".app" in template_content or "app" in template_content.lower()

    def test_template_has_database_structure(self, template_content):
        """Template has database element"""
        assert ".database" in template_content or "database" in template_content.lower()

    def test_template_has_flow_structure(self, template_content):
        """Template has flow element"""
        assert ".flow" in template_content or "flow" in template_content.lower()

    def test_template_has_status_indicators(self, template_content):
        """Template has status indicators (healthy, warning, critical)"""
        assert "healthy" in template_content and "warning" in template_content and "critical" in template_content
