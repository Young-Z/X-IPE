"""
Tests for FEATURE-015: Architecture DSL Skill

Tests cover:
- Skill file structure validation
- SKILL.md content requirements
- Grammar reference completeness
- Example DSL files validity
- Config integration (tools.json)

TDD Approach: All tests written before implementation.
"""
import os
import re
import json
import pytest
from pathlib import Path


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def project_root():
    """Get project root directory"""
    # Navigate from tests/ to project root
    return Path(__file__).parent.parent


@pytest.fixture
def skill_dir(project_root):
    """Get the Architecture DSL skill directory"""
    return project_root / '.github' / 'skills' / 'tool-architecture-dsl'


@pytest.fixture
def config_file(project_root):
    """Get the tools.json config file"""
    return project_root / 'x-ipe-docs' / 'config' / 'tools.json'


# ============================================================================
# SKILL STRUCTURE TESTS (AC-1.x)
# ============================================================================

class TestSkillStructure:
    """Tests for AC-1.x: Skill file structure"""
    
    def test_skill_folder_exists(self, skill_dir):
        """AC-1.1: Skill folder exists at .github/skills/tool-architecture-dsl/"""
        assert skill_dir.exists(), f"Skill folder not found at {skill_dir}"
        assert skill_dir.is_dir(), f"{skill_dir} is not a directory"
    
    def test_skill_md_exists(self, skill_dir):
        """AC-1.2: SKILL.md exists in skill folder"""
        skill_md = skill_dir / 'SKILL.md'
        assert skill_md.exists(), f"SKILL.md not found at {skill_md}"
    
    def test_grammar_reference_exists(self, skill_dir):
        """AC-1.3: Grammar reference exists at references/grammar.md"""
        grammar_md = skill_dir / 'references' / 'grammar.md'
        assert grammar_md.exists(), f"Grammar reference not found at {grammar_md}"
    
    def test_module_view_example_exists(self, skill_dir):
        """AC-1.4: Module View example exists at examples/module-view.dsl"""
        example = skill_dir / 'examples' / 'module-view.dsl'
        assert example.exists(), f"Module View example not found at {example}"
    
    def test_landscape_view_example_exists(self, skill_dir):
        """AC-1.5: Landscape View example exists at examples/landscape-view.dsl"""
        example = skill_dir / 'examples' / 'landscape-view.dsl'
        assert example.exists(), f"Landscape View example not found at {example}"


# ============================================================================
# SKILL.MD CONTENT TESTS (AC-1.2 detailed)
# ============================================================================

class TestSkillMdContent:
    """Tests for SKILL.md content requirements"""
    
    @pytest.fixture
    def skill_md_content(self, skill_dir):
        """Read SKILL.md content"""
        skill_md = skill_dir / 'SKILL.md'
        if skill_md.exists():
            return skill_md.read_text()
        return None
    
    def test_skill_md_has_frontmatter(self, skill_md_content):
        """SKILL.md has YAML frontmatter with name and description"""
        assert skill_md_content is not None, "SKILL.md not found"
        assert skill_md_content.startswith('---'), "Missing YAML frontmatter start"
        
        # Check frontmatter has name
        assert 'name: tool-architecture-dsl' in skill_md_content, "Missing skill name in frontmatter"
        
        # Check frontmatter has description
        assert 'description:' in skill_md_content, "Missing description in frontmatter"
    
    def test_skill_md_has_overview_section(self, skill_md_content):
        """SKILL.md has Overview section (or equivalent intro)"""
        assert skill_md_content is not None, "SKILL.md not found"
        # v2: Uses "IPE Markdown Support" as intro section
        assert any(term in skill_md_content for term in [
            '## Overview', '# Overview', '## IPE Markdown Support', '# Architecture DSL Tool'
        ]), "Missing Overview section"
    
    def test_skill_md_has_workflow_section(self, skill_md_content):
        """SKILL.md has Workflow section (or generation steps)"""
        assert skill_md_content is not None, "SKILL.md not found"
        # v2: Uses "Module View Generation" and "Landscape View Generation" as workflow
        assert any(term in skill_md_content for term in [
            '## Workflow', '# Workflow', 'Module View Generation', 'Landscape View Generation'
        ]), "Missing Workflow section"
    
    def test_skill_md_has_when_to_use_section(self, skill_md_content):
        """SKILL.md has When to Use section"""
        assert skill_md_content is not None, "SKILL.md not found"
        assert 'When to Use' in skill_md_content, "Missing 'When to Use' section"
    
    def test_skill_md_has_dsl_syntax_reference(self, skill_md_content):
        """SKILL.md has DSL Syntax Reference section"""
        assert skill_md_content is not None, "SKILL.md not found"
        # Could be various naming conventions
        assert any(term in skill_md_content for term in [
            'DSL Syntax', 'Syntax Reference', 'Quick Reference', 'Grammar'
        ]), "Missing DSL Syntax Reference section"
    
    def test_skill_md_has_capabilities_section(self, skill_md_content):
        """SKILL.md has Capabilities section (or translation patterns)"""
        assert skill_md_content is not None, "SKILL.md not found"
        # v2: Uses "Translation Patterns" instead of explicit "Capabilities"
        assert any(term in skill_md_content.lower() for term in [
            'capabilities', 'translation patterns'
        ]), "Missing Capabilities section"
    
    def test_skill_md_documents_nl_to_dsl(self, skill_md_content):
        """AC-6.1: SKILL.md documents NL to DSL translation capability"""
        assert skill_md_content is not None, "SKILL.md not found"
        # v2: Translation Patterns table documents input -> output patterns
        assert any(term in skill_md_content.lower() for term in [
            'natural language', 'nl →', 'nl->', 'translate', 'translation patterns', 'input'
        ]), "Missing NL to DSL translation documentation"
    
    def test_skill_md_documents_dsl_to_nl(self, skill_md_content):
        """AC-6.2: SKILL.md documents DSL to NL explanation capability"""
        assert skill_md_content is not None, "SKILL.md not found"
        # v2: Translation Patterns shows bidirectional patterns
        assert any(term in skill_md_content.lower() for term in [
            'explain', 'dsl →', 'dsl->', 'natural language', 'output', 'translation'
        ]), "Missing DSL to NL explanation documentation"
    
    def test_skill_md_documents_validation(self, skill_md_content):
        """AC-6.3: SKILL.md documents DSL validation capability"""
        assert skill_md_content is not None, "SKILL.md not found"
        assert 'validat' in skill_md_content.lower(), "Missing validation documentation"
    
    def test_skill_md_documents_refinement(self, skill_md_content):
        """AC-6.4: SKILL.md documents DSL refinement capability"""
        assert skill_md_content is not None, "SKILL.md not found"
        assert any(term in skill_md_content.lower() for term in [
            'refine', 'update', 'modify'
        ]), "Missing refinement documentation"


# ============================================================================
# GRAMMAR REFERENCE TESTS (AC-1.3 detailed, AC-2.x, AC-3.x, AC-4.x, AC-5.x)
# ============================================================================

class TestGrammarReference:
    """Tests for grammar.md content completeness"""
    
    @pytest.fixture
    def grammar_content(self, skill_dir):
        """Read grammar.md content"""
        grammar_md = skill_dir / 'references' / 'grammar.md'
        if grammar_md.exists():
            return grammar_md.read_text()
        return None
    
    # --- Core Elements (AC-2.x) ---
    
    def test_grammar_documents_startuml_enduml(self, grammar_content):
        """AC-2.1: Grammar documents @startuml/@enduml delimiters"""
        assert grammar_content is not None, "grammar.md not found"
        assert '@startuml' in grammar_content, "Missing @startuml documentation"
        assert '@enduml' in grammar_content, "Missing @enduml documentation"
    
    def test_grammar_documents_title(self, grammar_content):
        """AC-2.2: Grammar documents title property"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'title' in grammar_content.lower(), "Missing title property documentation"
    
    def test_grammar_documents_direction(self, grammar_content):
        """AC-2.3: Grammar documents direction property"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'direction' in grammar_content.lower(), "Missing direction property documentation"
        assert any(term in grammar_content for term in [
            'top-to-bottom', 'left-to-right'
        ]), "Missing direction values documentation"
    
    def test_grammar_documents_comments(self, grammar_content):
        """AC-2.4, AC-2.5: Grammar documents comment syntax"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'comment' in grammar_content.lower(), "Missing comment documentation"
        assert "'" in grammar_content, "Missing single-line comment documentation"
    
    # --- Module View Elements (AC-3.x) ---
    
    def test_grammar_documents_layer(self, grammar_content):
        """AC-3.1: Grammar documents layer syntax"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'layer' in grammar_content.lower(), "Missing layer documentation"
    
    def test_grammar_documents_module(self, grammar_content):
        """AC-3.2: Grammar documents module syntax"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'module' in grammar_content.lower(), "Missing module documentation"
    
    def test_grammar_documents_component(self, grammar_content):
        """AC-3.3: Grammar documents component syntax"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'component' in grammar_content.lower(), "Missing component documentation"
    
    def test_grammar_documents_stereotype(self, grammar_content):
        """AC-3.4: Grammar documents stereotype syntax (<<...>>)"""
        assert grammar_content is not None, "grammar.md not found"
        assert '<<' in grammar_content and '>>' in grammar_content, \
            "Missing stereotype documentation"
    
    # --- Landscape View Elements (AC-4.x) ---
    
    def test_grammar_documents_zone(self, grammar_content):
        """AC-4.1: Grammar documents zone syntax"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'zone' in grammar_content.lower(), "Missing zone documentation"
    
    def test_grammar_documents_app(self, grammar_content):
        """AC-4.2: Grammar documents app syntax with metadata"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'app' in grammar_content.lower(), "Missing app documentation"
        # Check for metadata properties
        assert 'tech' in grammar_content.lower(), "Missing tech property documentation"
    
    def test_grammar_documents_database(self, grammar_content):
        """AC-4.3: Grammar documents database syntax"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'database' in grammar_content.lower(), "Missing database documentation"
    
    def test_grammar_documents_flow(self, grammar_content):
        """AC-4.4: Grammar documents flow/connection syntax"""
        assert grammar_content is not None, "grammar.md not found"
        assert '-->' in grammar_content, "Missing flow arrow documentation"
    
    def test_grammar_documents_status_values(self, grammar_content):
        """AC-4.5: Grammar documents status values"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'status' in grammar_content.lower(), "Missing status documentation"
        assert any(val in grammar_content.lower() for val in [
            'healthy', 'warning', 'critical'
        ]), "Missing status values documentation"
    
    # --- Layout Control (AC-5.x) ---
    
    def test_grammar_documents_style(self, grammar_content):
        """AC-5.1: Grammar documents layout control (v2: align, gap)"""
        assert grammar_content is not None, "grammar.md not found"
        # v2 uses 'align' and 'gap' for layout control
        assert 'align' in grammar_content.lower(), "Missing align property documentation"
    
    def test_grammar_documents_cols_property(self, grammar_content):
        """AC-5.2: Grammar documents cols property (v2 grid system)"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'cols' in grammar_content, "Missing cols documentation"
    
    def test_grammar_documents_rows_property(self, grammar_content):
        """AC-5.3: Grammar documents rows property (v2 grid system)"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'rows' in grammar_content, "Missing rows documentation"
    
    def test_grammar_documents_grid_property(self, grammar_content):
        """AC-5.4: Grammar documents grid property (v2 grid system)"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'grid' in grammar_content, "Missing grid documentation"
    
    def test_grammar_documents_gap(self, grammar_content):
        """AC-5.5: Grammar documents row-gap and column-gap"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'gap' in grammar_content.lower(), "Missing gap documentation"
    
    def test_grammar_documents_text_align(self, grammar_content):
        """AC-5.6, AC-5.7, AC-5.8: Grammar documents text-align"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'text-align' in grammar_content, "Missing text-align documentation"
    
    def test_grammar_documents_canvas(self, grammar_content):
        """AC-5.9: Grammar documents canvas (explicit dimensions)"""
        assert grammar_content is not None, "grammar.md not found"
        assert 'canvas' in grammar_content, "Missing canvas documentation"


# ============================================================================
# EXAMPLE FILE TESTS (AC-1.4, AC-1.5)
# ============================================================================

class TestExampleFiles:
    """Tests for example DSL files validity"""
    
    @pytest.fixture
    def module_view_content(self, skill_dir):
        """Read module-view.dsl content"""
        example = skill_dir / 'examples' / 'module-view.dsl'
        if example.exists():
            return example.read_text()
        return None
    
    @pytest.fixture
    def landscape_view_content(self, skill_dir):
        """Read landscape-view.dsl content"""
        example = skill_dir / 'examples' / 'landscape-view.dsl'
        if example.exists():
            return example.read_text()
        return None
    
    # --- Module View Example ---
    
    def test_module_view_has_startuml(self, module_view_content):
        """Module View example starts with @startuml module-view"""
        assert module_view_content is not None, "module-view.dsl not found"
        assert '@startuml module-view' in module_view_content, \
            "Missing @startuml module-view header"
    
    def test_module_view_has_enduml(self, module_view_content):
        """Module View example ends with @enduml"""
        assert module_view_content is not None, "module-view.dsl not found"
        assert '@enduml' in module_view_content, "Missing @enduml footer"
    
    def test_module_view_has_layers(self, module_view_content):
        """Module View example contains layer definitions"""
        assert module_view_content is not None, "module-view.dsl not found"
        assert 'layer ' in module_view_content, "Missing layer definitions"
    
    def test_module_view_has_modules(self, module_view_content):
        """Module View example contains module definitions"""
        assert module_view_content is not None, "module-view.dsl not found"
        assert 'module ' in module_view_content, "Missing module definitions"
    
    def test_module_view_has_components(self, module_view_content):
        """Module View example contains component definitions"""
        assert module_view_content is not None, "module-view.dsl not found"
        assert 'component ' in module_view_content, "Missing component definitions"
    
    def test_module_view_demonstrates_style(self, module_view_content):
        """Module View example demonstrates style property"""
        assert module_view_content is not None, "module-view.dsl not found"
        assert 'style ' in module_view_content, "Missing style demonstration"
    
    def test_module_view_demonstrates_virtual_box(self, module_view_content):
        """Module View example demonstrates virtual-box"""
        assert module_view_content is not None, "module-view.dsl not found"
        assert 'virtual-box' in module_view_content, "Missing virtual-box demonstration"
    
    # --- Landscape View Example ---
    
    def test_landscape_view_has_startuml(self, landscape_view_content):
        """Landscape View example starts with @startuml landscape-view"""
        assert landscape_view_content is not None, "landscape-view.dsl not found"
        assert '@startuml landscape-view' in landscape_view_content, \
            "Missing @startuml landscape-view header"
    
    def test_landscape_view_has_enduml(self, landscape_view_content):
        """Landscape View example ends with @enduml"""
        assert landscape_view_content is not None, "landscape-view.dsl not found"
        assert '@enduml' in landscape_view_content, "Missing @enduml footer"
    
    def test_landscape_view_has_zones(self, landscape_view_content):
        """Landscape View example contains zone definitions"""
        assert landscape_view_content is not None, "landscape-view.dsl not found"
        assert 'zone ' in landscape_view_content, "Missing zone definitions"
    
    def test_landscape_view_has_apps(self, landscape_view_content):
        """Landscape View example contains app definitions"""
        assert landscape_view_content is not None, "landscape-view.dsl not found"
        assert 'app ' in landscape_view_content, "Missing app definitions"
    
    def test_landscape_view_has_databases(self, landscape_view_content):
        """Landscape View example contains database definitions"""
        assert landscape_view_content is not None, "landscape-view.dsl not found"
        assert 'database ' in landscape_view_content, "Missing database definitions"
    
    def test_landscape_view_has_flows(self, landscape_view_content):
        """Landscape View example contains action flows"""
        assert landscape_view_content is not None, "landscape-view.dsl not found"
        assert '-->' in landscape_view_content, "Missing action flow arrows"
    
    def test_landscape_view_demonstrates_status(self, landscape_view_content):
        """Landscape View example demonstrates status property"""
        assert landscape_view_content is not None, "landscape-view.dsl not found"
        assert 'status:' in landscape_view_content, "Missing status demonstration"


# ============================================================================
# CONFIG INTEGRATION TESTS (AC-7.x)
# ============================================================================

class TestConfigIntegration:
    """Tests for x-ipe-docs/config/tools.json integration"""
    
    @pytest.fixture
    def config_content(self, config_file):
        """Read and parse tools.json"""
        if config_file.exists():
            return json.loads(config_file.read_text())
        return None
    
    def test_tools_json_exists(self, config_file):
        """x-ipe-docs/config/tools.json exists"""
        assert config_file.exists(), f"tools.json not found at {config_file}"
    
    def test_architecture_dsl_registered(self, config_content):
        """AC-7.1: tool-architecture-dsl registered in tools.json"""
        assert config_content is not None, "tools.json not found"
        
        # Navigate to stages.ideation.ideation.tool-architecture-dsl
        stages = config_content.get('stages', {})
        ideation = stages.get('ideation', {})
        ideation_phase = ideation.get('ideation', {})
        
        assert 'tool-architecture-dsl' in ideation_phase, \
            "tool-architecture-dsl not registered in stages.ideation.ideation"
    
    def test_architecture_dsl_is_boolean(self, config_content):
        """tool-architecture-dsl value is boolean (can be enabled/disabled)"""
        assert config_content is not None, "tools.json not found"
        
        stages = config_content.get('stages', {})
        ideation = stages.get('ideation', {})
        ideation_phase = ideation.get('ideation', {})
        
        value = ideation_phase.get('tool-architecture-dsl')
        assert isinstance(value, bool), \
            f"tool-architecture-dsl should be boolean, got {type(value)}"


# ============================================================================
# TEST SUMMARY
# ============================================================================
# 
# Total: 46 tests
# 
# Skill Structure (5 tests):
#   - test_skill_folder_exists
#   - test_skill_md_exists
#   - test_grammar_reference_exists
#   - test_module_view_example_exists
#   - test_landscape_view_example_exists
#
# SKILL.md Content (12 tests):
#   - test_skill_md_has_frontmatter
#   - test_skill_md_has_overview_section
#   - test_skill_md_has_workflow_section
#   - test_skill_md_has_when_to_use_section
#   - test_skill_md_has_dsl_syntax_reference
#   - test_skill_md_has_capabilities_section
#   - test_skill_md_documents_nl_to_dsl
#   - test_skill_md_documents_dsl_to_nl
#   - test_skill_md_documents_validation
#   - test_skill_md_documents_refinement
#
# Grammar Reference (18 tests):
#   - Core elements (4): startuml/enduml, title, direction, comments
#   - Module View (4): layer, module, component, stereotype
#   - Landscape View (5): zone, app, database, flow, status
#   - Layout Control (5): style, justify-content, align-items, flex-direction, 
#                         gap, text-align, virtual-box
#
# Example Files (14 tests):
#   - Module View (7): header, footer, layers, modules, components, style, virtual-box
#   - Landscape View (7): header, footer, zones, apps, databases, flows, status
#
# Config Integration (3 tests):
#   - test_tools_json_exists
#   - test_architecture_dsl_registered
#   - test_architecture_dsl_is_boolean
# ============================================================================
