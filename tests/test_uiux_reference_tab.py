"""
Tests for FEATURE-030-A: UIUX Reference Tab & Console Integration

Frontend feature - tests verify config integration, prompt building logic,
and template/static file presence.

TDD: All tests should FAIL before implementation.
"""
import json
import os
import re
import pytest


# ============ FIXTURES ============

@pytest.fixture
def copilot_prompt_config():
    """Load actual copilot-prompt.json."""
    config_path = os.path.join(
        os.path.dirname(__file__), '..', 'x-ipe-docs', 'config', 'copilot-prompt.json'
    )
    with open(config_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def project_root():
    """Project root directory."""
    return os.path.join(os.path.dirname(__file__), '..')


# ============ CONFIG TESTS ============

class TestCopilotPromptConfig:
    """Test copilot-prompt.json has uiux-reference entry."""

    def test_uiux_reference_prompt_exists(self, copilot_prompt_config):
        """copilot-prompt.json must have uiux-reference prompt in ideation.prompts."""
        prompts = copilot_prompt_config.get('ideation', {}).get('prompts', [])
        ids = [p['id'] for p in prompts]
        assert 'uiux-reference' in ids

    def test_uiux_reference_has_en_prompt_details(self, copilot_prompt_config):
        """uiux-reference prompt must have English prompt-details."""
        prompts = copilot_prompt_config['ideation']['prompts']
        uiux_prompt = next(p for p in prompts if p['id'] == 'uiux-reference')
        details = uiux_prompt.get('prompt-details', [])
        en_detail = next((d for d in details if d['language'] == 'en'), None)
        assert en_detail is not None
        assert 'command' in en_detail
        assert '<target-url>' in en_detail['command']

    def test_uiux_reference_has_icon(self, copilot_prompt_config):
        """uiux-reference prompt must have an icon."""
        prompts = copilot_prompt_config['ideation']['prompts']
        uiux_prompt = next(p for p in prompts if p['id'] == 'uiux-reference')
        assert 'icon' in uiux_prompt
        assert uiux_prompt['icon'].startswith('bi-')


# ============ STATIC FILE TESTS ============

class TestStaticFiles:
    """Test that required static files exist."""

    def test_css_file_exists(self, project_root):
        """uiux-reference-tab.css must exist."""
        css_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'css', 'uiux-reference-tab.css')
        assert os.path.exists(css_path), f"CSS file not found: {css_path}"

    def test_js_file_exists(self, project_root):
        """uiux-reference-tab.js must exist."""
        js_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'uiux-reference-tab.js')
        assert os.path.exists(js_path), f"JS file not found: {js_path}"

    def test_css_has_uiux_ref_prefix(self, project_root):
        """CSS must use .uiux-ref- namespace prefix."""
        css_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'css', 'uiux-reference-tab.css')
        with open(css_path, 'r') as f:
            content = f.read()
        assert '.uiux-ref-' in content

    def test_css_has_required_animations(self, project_root):
        """CSS must define fadeSlideIn and pulse-badge animations."""
        css_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'css', 'uiux-reference-tab.css')
        with open(css_path, 'r') as f:
            content = f.read()
        assert 'fadeSlideIn' in content
        assert 'pulse-badge' in content

    def test_css_has_color_variables(self, project_root):
        """CSS must define the editorial light theme color tokens."""
        css_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'css', 'uiux-reference-tab.css')
        with open(css_path, 'r') as f:
            content = f.read()
        assert '#3730a3' in content  # accent (deep indigo)
        assert '#047857' in content  # emerald (success)
        assert '#b91c1c' in content  # danger (error)

    def test_js_has_uiux_reference_tab_class(self, project_root):
        """JS must define UiuxReferenceTab class."""
        js_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'uiux-reference-tab.js')
        with open(js_path, 'r') as f:
            content = f.read()
        assert 'class UiuxReferenceTab' in content

    def test_js_has_validate_form(self, project_root):
        """JS must have validateForm method."""
        js_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'uiux-reference-tab.js')
        with open(js_path, 'r') as f:
            content = f.read()
        assert 'validateForm' in content

    def test_js_has_build_prompt(self, project_root):
        """JS must have buildPrompt method."""
        js_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'uiux-reference-tab.js')
        with open(js_path, 'r') as f:
            content = f.read()
        assert 'buildPrompt' in content

    def test_js_has_state_machine(self, project_root):
        """JS must have setState method with idle/loading/success states."""
        js_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'uiux-reference-tab.js')
        with open(js_path, 'r') as f:
            content = f.read()
        assert 'setState' in content
        assert "'idle'" in content or '"idle"' in content
        assert "'loading'" in content or '"loading"' in content
        assert "'success'" in content or '"success"' in content

    def test_js_has_toggle_auth(self, project_root):
        """JS must have toggleAuth method."""
        js_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'uiux-reference-tab.js')
        with open(js_path, 'r') as f:
            content = f.read()
        assert 'toggleAuth' in content

    def test_js_has_terminal_integration(self, project_root):
        """JS must integrate with terminalPanel and terminalManager."""
        js_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'uiux-reference-tab.js')
        with open(js_path, 'r') as f:
            content = f.read()
        assert 'terminalPanel' in content
        assert 'sendCopilotPromptCommand' in content


# ============ TEMPLATE INTEGRATION TESTS ============

class TestTemplateIntegration:
    """Test that base.html includes the new CSS/JS files."""

    def test_base_html_includes_css(self, project_root):
        """base.html must include uiux-reference-tab.css."""
        base_path = os.path.join(project_root, 'src', 'x_ipe', 'templates', 'base.html')
        with open(base_path, 'r') as f:
            content = f.read()
        assert 'uiux-reference-tab.css' in content

    def test_base_html_includes_js(self, project_root):
        """base.html must include uiux-reference-tab.js."""
        base_path = os.path.join(project_root, 'src', 'x_ipe', 'templates', 'base.html')
        with open(base_path, 'r') as f:
            content = f.read()
        assert 'uiux-reference-tab.js' in content

    def test_base_html_includes_google_fonts(self, project_root):
        """base.html must include Fraunces and Outfit Google Fonts."""
        base_path = os.path.join(project_root, 'src', 'x_ipe', 'templates', 'base.html')
        with open(base_path, 'r') as f:
            content = f.read()
        assert 'Fraunces' in content
        assert 'Outfit' in content


# ============ WORKPLACE JS INTEGRATION ============

class TestWorkplaceIntegration:
    """Test that workplace.js integrates the UIUX Reference tab."""

    def test_workplace_has_uiux_reference_tab(self, project_root):
        """workplace.js must render the UIUX Reference tab button."""
        wp_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'workplace.js')
        with open(wp_path, 'r') as f:
            content = f.read()
        assert 'uiux-reference' in content.lower()

    def test_workplace_has_uiux_reference_pane(self, project_root):
        """workplace.js must render the UIUX Reference tab pane."""
        wp_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'workplace.js')
        with open(wp_path, 'r') as f:
            content = f.read()
        assert 'uiux-reference-pane' in content

    def test_workplace_instantiates_tab_class(self, project_root):
        """workplace.js must instantiate UiuxReferenceTab."""
        wp_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'workplace.js')
        with open(wp_path, 'r') as f:
            content = f.read()
        assert 'UiuxReferenceTab' in content


# ============ PROMPT BUILDING LOGIC ============

# ============ URL NORMALIZATION TESTS ============

class TestUrlNormalization:
    """Test that URLs without protocol prefix get https:// prepended."""

    def test_js_has_normalize_url_method(self, project_root):
        """JS must have normalizeUrl method to auto-prepend https://."""
        js_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'uiux-reference-tab.js')
        with open(js_path, 'r') as f:
            content = f.read()
        assert 'normalizeUrl' in content

    def test_js_normalize_url_prepends_https(self, project_root):
        """normalizeUrl must prepend https:// when no protocol is present."""
        js_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'uiux-reference-tab.js')
        with open(js_path, 'r') as f:
            content = f.read()
        # Verify the method contains logic to check for protocol and prepend https://
        assert "https://" in content
        assert re.search(r'normalizeUrl\s*\(', content)
        # The method should check if URL starts with http:// or https://
        assert re.search(r'https?://', content)

    def test_js_normalize_url_called_in_validate(self, project_root):
        """validateForm must use normalizeUrl before validation."""
        js_path = os.path.join(project_root, 'src', 'x_ipe', 'static', 'js', 'features', 'uiux-reference-tab.js')
        with open(js_path, 'r') as f:
            content = f.read()
        # normalizeUrl should be called within or before validateForm
        assert 'normalizeUrl' in content


class TestPromptBuilding:
    """Test prompt format matches specification FR-13."""

    def test_prompt_has_url_flag(self, copilot_prompt_config):
        """Prompt command must contain --url placeholder."""
        prompts = copilot_prompt_config['ideation']['prompts']
        uiux_prompt = next(p for p in prompts if p['id'] == 'uiux-reference')
        en_detail = next(d for d in uiux_prompt['prompt-details'] if d['language'] == 'en')
        assert '--url' in en_detail['command']

    def test_prompt_has_target_url_placeholder(self, copilot_prompt_config):
        """Prompt command must have <target-url> placeholder for runtime substitution."""
        prompts = copilot_prompt_config['ideation']['prompts']
        uiux_prompt = next(p for p in prompts if p['id'] == 'uiux-reference')
        en_detail = next(d for d in uiux_prompt['prompt-details'] if d['language'] == 'en')
        assert '<target-url>' in en_detail['command']
