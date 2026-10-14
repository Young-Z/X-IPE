"""
Tests for Architecture Diagram Renderer Skills (Split into two skills)

After refactoring, we now have:
1. x-ipe-tool-draw-layered-architecture - Module View diagrams
2. x-ipe-tool-draw-system-landscape - Landscape View diagrams

This test suite validates both skill structures.
"""

import os
import json
import pytest
import re
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree as ET

import yaml


def section(content, heading):
    """Read one named Markdown section, not an unrelated token elsewhere."""
    lines = content.splitlines(keepends=True)
    start = None
    fence = None
    for index, line in enumerate(lines):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            delimiter = marker[1]
            if fence is None:
                fence = delimiter
            elif delimiter[0] == fence[0] and len(delimiter) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        if start is None and line.rstrip() == f'## {heading}':
            start = index + 1
        elif start is not None and line.startswith('## '):
            return ''.join(lines[start:index])
    assert start is not None, f"Missing section: {heading}"
    return ''.join(lines[start:])


def frontmatter(content, name):
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", content, re.S)
    assert match, "Missing YAML frontmatter"
    data = yaml.safe_load(match[1])
    assert isinstance(data, dict) and data.get("name") == name, "Missing canonical name"
    assert isinstance(data.get("description"), str) and data["description"].strip()
    return data


def yaml_contract(content, heading, key):
    blocks = re.findall(r"^```yaml\n(.*?)\n```", section(content, heading), re.M | re.S)
    assert len(blocks) == 1, f"Expected one YAML contract in {heading}"
    parsed = yaml.safe_load(blocks[0])
    assert isinstance(parsed, dict) and isinstance(parsed.get(key), dict)
    return parsed[key]


def linked_resource(entry, target, root=None):
    """Load only a named entry-linked resource; reject missing/escaping paths.

    Entries use project-root Markdown links or explicit backtick resource paths.
    Anchors are checked against headings. No recursive content concatenation.
    """
    root = Path(root or PROJECT_ROOT).resolve()
    entry = Path(entry).resolve()
    assert entry.is_relative_to(root), "Entry escapes root"
    content = entry.read_text(encoding="utf-8")
    references = re.findall(r"\]\(([^)]+)\)", content)
    references += re.findall(r"`((?:references|templates|scripts)/[^`\s]+)`", content)
    matches = [ref for ref in references if ref.split("#", 1)[0] == target]
    assert matches, f"Missing explicit resource reference: {target}"
    base = root if target.startswith((".github/", "src/", "x-ipe-docs/")) else entry.parent
    path = (base / unquote(target)).resolve()
    assert path.is_relative_to(root), "Resource escapes root"
    assert path.is_file(), f"Missing resource: {target}"
    text = path.read_text(encoding="utf-8")
    assert text.strip(), f"Empty resource: {target}"
    for ref in matches:
        if "#" in ref:
            anchor = ref.split("#", 1)[1]
            headings = re.findall(r"^#+ (.+)$", text, re.M)
            slugs = {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}
            assert anchor in slugs, f"Missing resource anchor: {anchor}"
    return text


def operation_contract(content, names):
    operations = section(content, "Operations")
    blocks = re.findall(r"```xml\n(.*?)\n```", operations, re.S)
    nodes = [ET.fromstring(block) for block in blocks]
    assert {node.get("name") for node in nodes} == set(names), "Missing operation"
    for node in nodes:
        assert node.tag == "operation"
        assert node.findtext("action", "").strip(), "Missing operation procedure"
        assert node.findtext("output", "").strip(), "Missing operation output"
        assert node.findtext("constraints", "").strip(), "Missing operation constraints"
    return {node.get("name"): node for node in nodes}


def tool_flags(config, stage, phase):
    """Validate actual Stage Toolbox keys; metadata is not an enabled tool."""
    from x_ipe.services.tools_config_service import DEFAULT_CONFIG

    assert stage in DEFAULT_CONFIG["stages"], "Unknown toolbox stage"
    assert phase in DEFAULT_CONFIG["stages"][stage], "Unknown toolbox phase"
    flags = config["stages"][stage][phase]
    assert isinstance(flags, dict)
    for name, enabled in flags.items():
        if not name.startswith("_"):
            assert type(enabled) is bool, f"Invalid enabled flag: {name}"
    return {name: enabled for name, enabled in flags.items() if not name.startswith("_")}

# Base paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERED_SKILL_PATH = os.path.join(PROJECT_ROOT, ".github", "skills", "x-ipe-tool-draw-layered-architecture")
LANDSCAPE_SKILL_PATH = os.path.join(PROJECT_ROOT, ".github", "skills", "x-ipe-tool-draw-system-landscape")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "x-ipe-docs", "config", "tools.json")


class TestLayeredArchitectureSkillStructure:
    """Test x-ipe-tool-draw-layered-architecture folder and file structure."""

    def test_skill_folder_exists(self):
        """Skill folder exists at .github/skills/x-ipe-tool-draw-layered-architecture/"""
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
    """Test x-ipe-tool-draw-layered-architecture SKILL.md content."""

    @pytest.fixture
    def skill_content(self):
        skill_md = os.path.join(LAYERED_SKILL_PATH, "SKILL.md")
        if os.path.isfile(skill_md):
            with open(skill_md, "r") as f:
                return f.read()
        return ""

    def test_skill_md_has_frontmatter(self, skill_content):
        """SKILL.md has YAML frontmatter with name and description"""
        frontmatter(skill_content, "x-ipe-tool-draw-layered-architecture")

    def test_skill_md_has_workflow_section(self, skill_content):
        """Renderer declares an operation procedure, not a Python renderer API."""
        node = operation_contract(skill_content, {"render_diagram"})["render_diagram"]
        assert "module-view-corporate.html" in node.findtext("action")
        assert "Module cols values must sum to 12" in node.findtext("constraints")

    def test_skill_md_references_module_view(self, skill_content):
        """SKILL.md focuses on module-view"""
        assert "module-view" in skill_content.lower()
        assert "Module View" in skill_content

    def test_skill_md_does_not_have_landscape_template_ref(self, skill_content):
        """SKILL.md should not reference landscape-view template (moved to other skill)"""
        assert "templates/landscape-view.html" not in skill_content

    def test_skill_md_references_landscape_skill(self, skill_content):
        """SKILL.md should reference the landscape skill for landscape diagrams"""
        assert "x-ipe-tool-draw-system-landscape" in skill_content


class TestLandscapeSkillStructure:
    """Test x-ipe-tool-draw-system-landscape folder and file structure."""

    def test_skill_folder_exists(self):
        """Skill folder exists at .github/skills/x-ipe-tool-draw-system-landscape/"""
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
    """Test x-ipe-tool-draw-system-landscape SKILL.md content."""

    @pytest.fixture
    def skill_content(self):
        skill_md = os.path.join(LANDSCAPE_SKILL_PATH, "SKILL.md")
        if os.path.isfile(skill_md):
            with open(skill_md, "r") as f:
                return f.read()
        return ""

    def test_skill_md_has_frontmatter(self, skill_content):
        """SKILL.md has YAML frontmatter with name and description"""
        frontmatter(skill_content, "x-ipe-tool-draw-system-landscape")

    def test_skill_md_has_workflow_section(self, skill_content):
        """Landscape procedure requires aliases and valid flow endpoints."""
        node = operation_contract(skill_content, {"render_landscape"})["render_landscape"]
        constraints = node.findtext("constraints")
        assert "aliases are unique" in constraints
        assert "flow source/target references exist" in constraints
        assert "must belong to a zone" in constraints

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
        assert "x-ipe-tool-draw-layered-architecture" in skill_content


class TestConfigIntegration:
    """Test tools.json configuration for both skills."""

    @pytest.fixture
    def config_content(self):
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        return {}

    def test_layered_skill_registered_in_architecture(self, config_content):
        """x-ipe-tool-draw-layered-architecture registered in ideation.architecture"""
        assert tool_flags(config_content, "ideation", "architecture")["x-ipe-tool-draw-layered-architecture"] is True

    def test_landscape_skill_registered_in_architecture(self, config_content):
        """x-ipe-tool-draw-system-landscape registered in ideation.architecture"""
        assert tool_flags(config_content, "ideation", "architecture")["x-ipe-tool-draw-system-landscape"] is True

    def test_layered_skill_not_selected_in_ideation(self, config_content):
        """Absent entry is not explicit false: this renderer is not selected here."""
        assert "x-ipe-tool-draw-layered-architecture" not in tool_flags(config_content, "ideation", "ideation")

    def test_landscape_skill_not_selected_in_ideation(self, config_content):
        assert "x-ipe-tool-draw-system-landscape" not in tool_flags(config_content, "ideation", "ideation")


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


@pytest.mark.parametrize("skill_dir,reference,expected", [
    (LAYERED_SKILL_PATH, "dsl-to-css.md", ("grid-column: span N", "grid-row: span N", "grid-template-columns", "IGNORED in corporate style")),
    (LANDSCAPE_SKILL_PATH, "landscape-mapping.md", ("flow-source", "flow-target", "healthy", "warning", "critical")),
])
def test_required_renderer_mapping_is_linked_and_loaded(skill_dir, reference, expected):
    entry = Path(skill_dir) / "SKILL.md"
    target = f".github/skills/{entry.parent.name}/references/{reference}"
    mapping = linked_resource(entry, target)
    for item in expected:
        assert item in mapping, f"Mapping missing {item}"
    content = entry.read_text()
    result = yaml_contract(content, "Output Result", "operation_output")
    assert set(result) == {"success", "result", "errors"}
    assert "file_path" in result["result"] and result["errors"] == []
    # Templates are explicit table entries, not Markdown links in these skills.
    templates = section(content, "Templates")
    for template in re.findall(r"`(templates/[^`]+\.html)`", templates):
        assert (entry.parent / template).resolve().is_relative_to(Path(PROJECT_ROOT))
        assert (entry.parent / template).is_file()


class TestContractCorruptionControls:
    """In-memory/tmp fixtures reject corruption; production stays immutable."""

    @pytest.mark.parametrize("replacement", ["skill_name", "other_name"])
    def test_frontmatter_requires_real_name(self, replacement):
        content = (Path(LAYERED_SKILL_PATH) / "SKILL.md").read_text()
        with pytest.raises(AssertionError, match="canonical name"):
            frontmatter(content.replace("name:", replacement + ":", 1), "x-ipe-tool-draw-layered-architecture")

    def test_missing_operation_procedure_is_detected(self):
        content = (Path(LAYERED_SKILL_PATH) / "SKILL.md").read_text()
        corrupt = re.sub(r"<action>.*?</action>", "<action/>", content, count=1, flags=re.S)
        with pytest.raises(AssertionError, match="procedure"):
            operation_contract(corrupt, {"render_diagram"})

    @pytest.mark.parametrize("value", ["true", 1, None, {}, []])
    def test_invalid_enabled_flags_are_detected(self, value):
        config = {"stages": {"ideation": {"architecture": {"renderer": value}}}}
        with pytest.raises(AssertionError, match="enabled flag"):
            tool_flags(config, "ideation", "architecture")

    @pytest.mark.parametrize("stage,phase", [("feature", "implementation"), ("implement", "implementation")])
    def test_stale_stage_keys_are_detected(self, stage, phase):
        with pytest.raises(AssertionError, match="Unknown toolbox"):
            tool_flags({}, stage, phase)

    def test_resource_missing_link_file_and_anchor(self, tmp_path):
        entry = tmp_path / "SKILL.md"
        resource = tmp_path / "references" / "mapping.md"
        resource.parent.mkdir()
        resource.write_text("## Required mapping\ncols → grid-column\n")
        entry.write_text("Mention mapping.md without a resource link")
        with pytest.raises(AssertionError, match="explicit resource"):
            linked_resource(entry, "references/mapping.md", tmp_path)
        entry.write_text("[mapping](references/mapping.md#absent)")
        with pytest.raises(AssertionError, match="anchor"):
            linked_resource(entry, "references/mapping.md", tmp_path)
        entry.write_text("[mapping](references/mapping.md)")
        resource.unlink()
        with pytest.raises(AssertionError, match="Missing resource"):
            linked_resource(entry, "references/mapping.md", tmp_path)

    def test_resource_escape_and_symlink_are_detected(self, tmp_path):
        root = tmp_path / "project"
        root.mkdir()
        outside = tmp_path / "outside.md"
        outside.write_text("## External\n")
        entry = root / "SKILL.md"
        entry.write_text("[outside](../outside.md)")
        with pytest.raises(AssertionError, match="escapes root"):
            linked_resource(entry, "../outside.md", root)
        (root / "references").mkdir()
        (root / "references" / "mapping.md").symlink_to(outside)
        entry.write_text("[mapping](references/mapping.md)")
        with pytest.raises(AssertionError, match="escapes root"):
            linked_resource(entry, "references/mapping.md", root)


def test_toolbox_stage_keys_agree_with_actual_service_and_ui():
    from x_ipe.services.tools_config_service import DEFAULT_CONFIG

    ui = (Path(PROJECT_ROOT) / 'src/x_ipe/static/js/features/stage-toolbox.js').read_text()
    stage_array = re.search(r'this\.stageOrder\s*=\s*\[([^\]]+)\]', ui)
    assert stage_array
    ui_stages = re.findall(r"'([^']+)'", stage_array[1])
    assert ui_stages == list(DEFAULT_CONFIG['stages'])
    label_block = re.search(r'this\.phaseLabels\s*=\s*\{(.*?)\n\s*\};', ui, re.S)
    assert label_block
    ui_phases = set(re.findall(r"^\s*(\w+):\s*'", label_block[1], re.M))
    config = json.loads(Path(CONFIG_PATH).read_text())
    assert set(config['stages']) == set(ui_stages)
    for stage, phases in config['stages'].items():
        assert set(phases) == set(DEFAULT_CONFIG['stages'][stage])
        for phase in phases:
            assert phase in ui_phases
            tool_flags(config, stage, phase)


def test_fenced_example_headings_cannot_end_a_named_resource_section():
    text = '## Detail Section\n```\n## {Entry ID}\nmetadata\n```\n## Other\nnot detail\n'
    assert section(text, 'Detail Section') == '```\n## {Entry ID}\nmetadata\n```\n'
