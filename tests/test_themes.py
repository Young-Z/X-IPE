"""
Tests for FEATURE-012: Design Themes

Tests cover:
- ThemesService: list_themes(), get_theme(), _parse_color_tokens()
- API endpoints: GET /api/themes, GET /api/themes/<name>
- Theme discovery and validation
- Color token parsing from design-system.md
- Config integration (selected-theme in tools.json)

TDD Approach: All tests written before implementation.
"""
import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Will be imported after implementation
# from x_ipe.services import ThemesService
# from src.app import create_app


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_project_with_themes(temp_project_dir):
    """Create temporary project with x-ipe-docs/themes/ folder and sample themes"""
    themes_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'themes'
    
    # Create theme-default
    default_dir = themes_dir / 'theme-default'
    default_dir.mkdir(parents=True, exist_ok=True)
    
    design_system_content = """# Design System: Default

Neutral, clean design system for modern applications.

## Colors

### Primary Palette

| Name | Hex | Usage |
|------|-----|-------|
| Primary | #0f172a | Main text, headings |
| Secondary | #475569 | Secondary text |
| Accent | #10b981 | CTAs, highlights |
| Neutral | #e2e8f0 | Backgrounds, borders |

## Typography

- Heading Font: Inter
- Body Font: System UI
- Code Font: JetBrains Mono
"""
    (default_dir / 'design-system.md').write_text(design_system_content)
    
    visualization_content = """<!DOCTYPE html>
<html><head><title>Default Theme</title></head>
<body>
<script type="application/ld+json">
{"colors": {"primary": "#0f172a", "secondary": "#475569"}}
</script>
</body></html>
"""
    (default_dir / 'component-visualization.html').write_text(visualization_content)
    
    # Create theme-ocean
    ocean_dir = themes_dir / 'theme-ocean'
    ocean_dir.mkdir(parents=True, exist_ok=True)
    
    ocean_design = """# Design System: Ocean

Cool blue tones for professional applications.

## Colors

- Primary: #0284c7
- Secondary: #38bdf8
- Accent: #7dd3fc
- Neutral: #e0f2fe

## Typography

- Heading Font: Poppins
- Body Font: Roboto
"""
    (ocean_dir / 'design-system.md').write_text(ocean_design)
    (ocean_dir / 'component-visualization.html').write_text('<html></html>')
    
    return {
        'root': temp_project_dir,
        'themes_dir': themes_dir,
        'default_dir': default_dir,
        'ocean_dir': ocean_dir
    }


@pytest.fixture
def temp_project_no_themes(temp_project_dir):
    """Create temporary project without x-ipe-docs/themes/ folder"""
    return temp_project_dir


@pytest.fixture
def temp_project_with_invalid_theme(temp_project_dir):
    """Create project with theme missing required design-system.md file"""
    themes_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'themes'
    
    # Theme missing design-system.md (INVALID - required file missing)
    incomplete_dir = themes_dir / 'theme-incomplete'
    incomplete_dir.mkdir(parents=True, exist_ok=True)
    (incomplete_dir / 'component-visualization.html').write_text('<html></html>')
    
    # Another invalid theme with only a readme
    another_invalid = themes_dir / 'theme-only-readme'
    another_invalid.mkdir(parents=True, exist_ok=True)
    (another_invalid / 'README.md').write_text('# No design system')
    
    return {
        'root': temp_project_dir,
        'themes_dir': themes_dir
    }


@pytest.fixture
def sample_design_system_content():
    """Sample design-system.md content with various color formats"""
    return """# Design System

A well-structured design system.

## Colors

Primary: #1a1a2e
Secondary: #4a4a6a
Accent: #10b981
Neutral: #e5e7eb

### Semantic Colors

- Success: #22c55e
- Warning: #f59e0b
- Error: #ef4444
- Info: #3b82f6
"""


@pytest.fixture
def flask_test_client(temp_project_with_themes):
    """Create Flask test client with themes"""
    from src.app import create_app
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['PROJECT_ROOT'] = temp_project_with_themes['root']
    
    with app.test_client() as client:
        yield client


# ============================================================================
# UNIT TESTS: ThemesService
# ============================================================================

class TestThemesServiceInit:
    """Tests for ThemesService initialization"""
    
    def test_init_creates_service_with_project_root(self, temp_project_dir):
        """ThemesService initializes with project root path"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_dir)
        
        assert service.project_root == Path(temp_project_dir).resolve()
        assert service.themes_dir == Path(temp_project_dir).resolve() / 'x-ipe-docs' / 'themes'
    
    def test_init_handles_relative_path(self, temp_project_dir):
        """ThemesService handles relative path correctly"""
        from x_ipe.services import ThemesService
        
        # Use relative path
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_project_dir)
            service = ThemesService('.')
            assert service.project_root.is_absolute()
        finally:
            os.chdir(original_cwd)


class TestThemesServiceListThemes:
    """Tests for ThemesService.list_themes()"""
    
    def test_list_themes_returns_all_valid_themes(self, temp_project_with_themes):
        """list_themes returns all valid themes with metadata"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_with_themes['root'])
        themes = service.list_themes()
        
        assert len(themes) == 2
        theme_names = [t['name'] for t in themes]
        assert 'theme-default' in theme_names
        assert 'theme-ocean' in theme_names
    
    def test_list_themes_returns_empty_when_no_themes_dir(self, temp_project_no_themes):
        """list_themes returns empty list when x-ipe-docs/themes/ doesn't exist"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_no_themes)
        themes = service.list_themes()
        
        assert themes == []
    
    def test_list_themes_excludes_invalid_themes(self, temp_project_with_invalid_theme):
        """list_themes excludes themes missing required design-system.md file"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_with_invalid_theme['root'])
        themes = service.list_themes()
        
        # Both themes are invalid (missing design-system.md), so list should be empty
        assert themes == []
    
    def test_list_themes_returns_metadata_structure(self, temp_project_with_themes):
        """list_themes returns proper metadata structure"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_with_themes['root'])
        themes = service.list_themes()
        
        default_theme = next(t for t in themes if t['name'] == 'theme-default')
        
        assert 'name' in default_theme
        assert 'description' in default_theme
        assert 'colors' in default_theme
        assert 'files' in default_theme
        assert 'path' in default_theme
    
    def test_list_themes_extracts_description(self, temp_project_with_themes):
        """list_themes extracts description from first paragraph"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_with_themes['root'])
        themes = service.list_themes()
        
        default_theme = next(t for t in themes if t['name'] == 'theme-default')
        
        assert 'Neutral' in default_theme['description'] or 'clean' in default_theme['description']
    
    def test_list_themes_extracts_color_tokens(self, temp_project_with_themes):
        """list_themes extracts color tokens from design-system.md"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_with_themes['root'])
        themes = service.list_themes()
        
        default_theme = next(t for t in themes if t['name'] == 'theme-default')
        
        assert 'primary' in default_theme['colors']
        assert 'secondary' in default_theme['colors']
        assert 'accent' in default_theme['colors']
        assert 'neutral' in default_theme['colors']
    
    def test_list_themes_lists_files(self, temp_project_with_themes):
        """list_themes includes list of files in theme"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_with_themes['root'])
        themes = service.list_themes()
        
        default_theme = next(t for t in themes if t['name'] == 'theme-default')
        
        assert 'design-system.md' in default_theme['files']
        assert 'component-visualization.html' in default_theme['files']
    
    def test_list_themes_only_scans_theme_prefixed_folders(self, temp_project_with_themes):
        """list_themes only includes folders starting with 'theme-'"""
        from x_ipe.services import ThemesService
        
        # Create a non-theme folder
        other_dir = temp_project_with_themes['themes_dir'] / 'other-folder'
        other_dir.mkdir(parents=True, exist_ok=True)
        (other_dir / 'design-system.md').write_text('# Other')
        (other_dir / 'component-visualization.html').write_text('<html></html>')
        
        service = ThemesService(temp_project_with_themes['root'])
        themes = service.list_themes()
        
        theme_names = [t['name'] for t in themes]
        assert 'other-folder' not in theme_names


class TestThemesServiceGetTheme:
    """Tests for ThemesService.get_theme()"""
    
    def test_get_theme_returns_theme_details(self, temp_project_with_themes):
        """get_theme returns full theme details including file content"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_with_themes['root'])
        theme = service.get_theme('theme-default')
        
        assert theme is not None
        assert theme['name'] == 'theme-default'
        assert 'design_system' in theme
        assert 'visualization_path' in theme
    
    def test_get_theme_includes_design_system_content(self, temp_project_with_themes):
        """get_theme includes full design-system.md content"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_with_themes['root'])
        theme = service.get_theme('theme-default')
        
        assert '# Design System' in theme['design_system']
        assert 'Primary' in theme['design_system']
    
    def test_get_theme_returns_none_for_missing_theme(self, temp_project_with_themes):
        """get_theme returns None for non-existent theme"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_with_themes['root'])
        theme = service.get_theme('theme-nonexistent')
        
        assert theme is None
    
    def test_get_theme_returns_none_for_invalid_theme(self, temp_project_with_invalid_theme):
        """get_theme returns None for theme missing required files"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_with_invalid_theme['root'])
        theme = service.get_theme('theme-incomplete')
        
        assert theme is None


class TestThemesServiceParseColorTokens:
    """Tests for ThemesService._parse_color_tokens()"""
    
    def test_parse_color_tokens_extracts_hex_colors(self, temp_project_dir):
        """_parse_color_tokens extracts hex colors from content"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_dir)
        content = """
        Primary: #1a1a2e
        Secondary: #4a4a6a
        Accent: #10b981
        Neutral: #e5e7eb
        """
        
        colors = service._parse_color_tokens(content)
        
        assert colors['primary'] == '#1a1a2e'
        assert colors['secondary'] == '#4a4a6a'
        assert colors['accent'] == '#10b981'
        assert colors['neutral'] == '#e5e7eb'
    
    def test_parse_color_tokens_handles_3digit_hex(self, temp_project_dir):
        """_parse_color_tokens handles 3-digit hex colors"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_dir)
        content = "#fff #000 #abc #def"
        
        colors = service._parse_color_tokens(content)
        
        # Should extract first 4 colors found
        assert colors['primary'] == '#fff'
    
    def test_parse_color_tokens_uses_fallback_when_no_colors(self, temp_project_dir):
        """_parse_color_tokens uses fallback colors when none found"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_dir)
        content = "No colors here, just text."
        
        colors = service._parse_color_tokens(content)
        
        # Should return fallback colors
        assert 'primary' in colors
        assert 'secondary' in colors
        assert 'accent' in colors
        assert 'neutral' in colors
    
    def test_parse_color_tokens_handles_less_than_4_colors(self, temp_project_dir):
        """_parse_color_tokens handles content with fewer than 4 colors"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_dir)
        content = "Only one color: #123456"
        
        colors = service._parse_color_tokens(content)
        
        assert colors['primary'] == '#123456'
        # Others should be fallback
        assert 'secondary' in colors


class TestThemesServiceExtractDescription:
    """Tests for ThemesService._extract_description()"""
    
    def test_extract_description_gets_first_paragraph(self, temp_project_dir):
        """_extract_description extracts first non-heading paragraph"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_dir)
        content = """# Title

This is the description paragraph.

## Section

More content here.
"""
        
        description = service._extract_description(content)
        
        assert 'description paragraph' in description
    
    def test_extract_description_handles_empty_content(self, temp_project_dir):
        """_extract_description handles empty content gracefully"""
        from x_ipe.services import ThemesService
        
        service = ThemesService(temp_project_dir)
        description = service._extract_description('')
        
        assert description == '' or description is not None


# ============================================================================
# API TESTS: /api/themes
# ============================================================================

class TestThemesAPIListEndpoint:
    """Tests for GET /api/themes endpoint"""
    
    def test_get_themes_returns_200(self, flask_test_client):
        """GET /api/themes returns 200 OK"""
        response = flask_test_client.get('/api/themes')
        
        assert response.status_code == 200
    
    def test_get_themes_returns_json(self, flask_test_client):
        """GET /api/themes returns JSON response"""
        response = flask_test_client.get('/api/themes')
        
        assert response.content_type == 'application/json'
    
    def test_get_themes_returns_themes_list(self, flask_test_client):
        """GET /api/themes returns themes array"""
        response = flask_test_client.get('/api/themes')
        data = response.get_json()
        
        assert 'themes' in data
        assert isinstance(data['themes'], list)
    
    def test_get_themes_includes_selected_theme(self, flask_test_client):
        """GET /api/themes includes currently selected theme"""
        response = flask_test_client.get('/api/themes')
        data = response.get_json()
        
        assert 'selected' in data
    
    def test_get_themes_returns_empty_list_when_no_themes(self, temp_project_no_themes):
        """GET /api/themes returns empty list when no themes exist"""
        from src.app import create_app
        
        app = create_app()
        app.config['TESTING'] = True
        app.config['PROJECT_ROOT'] = temp_project_no_themes
        
        with app.test_client() as client:
            response = client.get('/api/themes')
            data = response.get_json()
            
            assert data['themes'] == []


class TestThemesAPIDetailEndpoint:
    """Tests for GET /api/themes/<name> endpoint"""
    
    def test_get_theme_detail_returns_200(self, flask_test_client):
        """GET /api/themes/<name> returns 200 for existing theme"""
        response = flask_test_client.get('/api/themes/theme-default')
        
        assert response.status_code == 200
    
    def test_get_theme_detail_returns_404_for_missing(self, flask_test_client):
        """GET /api/themes/<name> returns 404 for non-existent theme"""
        response = flask_test_client.get('/api/themes/theme-nonexistent')
        
        assert response.status_code == 404
    
    def test_get_theme_detail_returns_design_system_content(self, flask_test_client):
        """GET /api/themes/<name> returns design-system.md content"""
        response = flask_test_client.get('/api/themes/theme-default')
        data = response.get_json()
        
        assert 'design_system' in data
        assert len(data['design_system']) > 0
    
    def test_get_theme_detail_returns_visualization_path(self, flask_test_client):
        """GET /api/themes/<name> returns path to component-visualization.html"""
        response = flask_test_client.get('/api/themes/theme-default')
        data = response.get_json()
        
        assert 'visualization_path' in data
        assert 'component-visualization.html' in data['visualization_path']


# ============================================================================
# INTEGRATION TESTS: Theme Selection
# ============================================================================

class TestThemeSelectionIntegration:
    """Integration tests for theme selection with ToolsConfigService"""
    
    def test_theme_selection_persisted_in_config(self, temp_project_with_themes):
        """Theme selection is saved to x-ipe-docs/config/tools.json"""
        from x_ipe.services import ThemesService, ToolsConfigService
        
        root = temp_project_with_themes['root']
        tools_service = ToolsConfigService(root)
        
        # Load config and set theme with new format
        config = tools_service.load()
        config['selected-theme'] = {
            'theme-name': 'theme-ocean',
            'theme-folder-path': 'x-ipe-docs/themes/theme-ocean'
        }
        tools_service.save(config)
        
        # Reload and verify
        config = tools_service.load()
        
        assert config['selected-theme']['theme-name'] == 'theme-ocean'
        assert config['selected-theme']['theme-folder-path'] == 'x-ipe-docs/themes/theme-ocean'
    
    def test_default_theme_selected_when_none_specified(self, temp_project_with_themes):
        """No theme is selected when none specified in config"""
        from x_ipe.services import ToolsConfigService
        
        root = temp_project_with_themes['root']
        tools_service = ToolsConfigService(root)
        config = tools_service.load()
        
        # Config should not have selected-theme by default
        selected_theme = config.get('selected-theme')
        
        assert selected_theme is None
    
    def test_fallback_to_default_when_selected_missing(self, temp_project_with_themes):
        """Themes still list when selected theme doesn't exist"""
        from x_ipe.services import ThemesService, ToolsConfigService
        
        root = temp_project_with_themes['root']
        tools_service = ToolsConfigService(root)
        themes_service = ThemesService(root)
        
        # Set a theme that will be "deleted"
        config = tools_service.load()
        config['selected-theme'] = {
            'theme-name': 'theme-nonexistent',
            'theme-folder-path': 'x-ipe-docs/themes/theme-nonexistent'
        }
        tools_service.save(config)
        
        # list_themes should still work
        themes = themes_service.list_themes()
        
        assert len(themes) > 0


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestThemesEdgeCases:
    """Edge case tests for themes functionality"""
    
    def test_theme_with_special_characters_in_name(self, temp_project_dir):
        """Themes with unusual names are handled correctly"""
        from x_ipe.services import ThemesService
        
        themes_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'themes'
        special_dir = themes_dir / 'theme-my-brand-2024'
        special_dir.mkdir(parents=True, exist_ok=True)
        (special_dir / 'design-system.md').write_text('# Special\n\nDescription.\n\n#123456 #234567 #345678 #456789')
        (special_dir / 'component-visualization.html').write_text('<html></html>')
        
        service = ThemesService(temp_project_dir)
        themes = service.list_themes()
        
        assert any(t['name'] == 'theme-my-brand-2024' for t in themes)
    
    def test_large_design_system_file(self, temp_project_dir):
        """Large design-system.md files are handled"""
        from x_ipe.services import ThemesService
        
        themes_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'themes'
        large_dir = themes_dir / 'theme-large'
        large_dir.mkdir(parents=True, exist_ok=True)
        
        # Create large file (~50KB)
        large_content = '# Large Theme\n\nDescription.\n\n' + '#abcdef ' * 5000
        (large_dir / 'design-system.md').write_text(large_content)
        (large_dir / 'component-visualization.html').write_text('<html></html>')
        
        service = ThemesService(temp_project_dir)
        theme = service.get_theme('theme-large')
        
        assert theme is not None
        assert len(theme['design_system']) > 40000
    
    def test_many_themes_performance(self, temp_project_dir):
        """Service handles many themes without performance issues"""
        from x_ipe.services import ThemesService
        import time
        
        themes_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'themes'
        
        # Create 20 themes
        for i in range(20):
            theme_dir = themes_dir / f'theme-test{i:02d}'
            theme_dir.mkdir(parents=True, exist_ok=True)
            (theme_dir / 'design-system.md').write_text(f'# Theme {i}\n\nTheme number {i}.\n\n#aabbcc #ddeeff #112233 #445566')
            (theme_dir / 'component-visualization.html').write_text('<html></html>')
        
        service = ThemesService(temp_project_dir)
        
        start = time.time()
        themes = service.list_themes()
        elapsed = time.time() - start
        
        assert len(themes) == 20
        assert elapsed < 0.5  # Should complete in under 500ms
    
    def test_utf8_content_in_design_system(self, temp_project_dir):
        """UTF-8 content in design-system.md is handled correctly"""
        from x_ipe.services import ThemesService
        
        themes_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'themes'
        utf8_dir = themes_dir / 'theme-utf8'
        utf8_dir.mkdir(parents=True, exist_ok=True)
        
        utf8_content = """# Design System 设计系统

Описание на русском. 日本語テスト.

## Colors 颜色

- Primary: #123456
- 主色: #234567
"""
        (utf8_dir / 'design-system.md').write_text(utf8_content, encoding='utf-8')
        (utf8_dir / 'component-visualization.html').write_text('<html></html>')
        
        service = ThemesService(temp_project_dir)
        theme = service.get_theme('theme-utf8')
        
        assert theme is not None
        assert '设计系统' in theme['design_system']


# ============================================================================
# TEST SUMMARY
# ============================================================================
"""
Test Coverage Summary for FEATURE-012: Design Themes

| Component | Unit Tests | Integration | API Tests | Edge Cases |
|-----------|------------|-------------|-----------|------------|
| ThemesService.__init__ | 2 | - | - | - |
| ThemesService.list_themes | 8 | - | - | - |
| ThemesService.get_theme | 4 | - | - | - |
| ThemesService._parse_color_tokens | 4 | - | - | - |
| ThemesService._extract_description | 2 | - | - | - |
| GET /api/themes | - | - | 5 | - |
| GET /api/themes/<name> | - | - | 4 | - |
| Theme Selection | - | 3 | - | - |
| Edge Cases | - | - | - | 4 |
| **TOTAL** | **20** | **3** | **9** | **4** |

Total: 36 tests

TDD Baseline: All 36 tests should FAIL before implementation.
"""
