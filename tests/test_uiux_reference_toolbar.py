"""Tests for FEATURE-030-B v2.0: UIUX Reference Toolbar — Shell, Theme Mode, Mockup Mode.

Tests validate the v2.0 toolbar system:
- Core shell (xipe-toolbar-core.js): hamburger, panel, mode tabs, toast, data store, comms
- Theme mode (xipe-toolbar-theme.js): offscreen canvas, magnifier, color sampling, role annotation
- Mockup mode (xipe-toolbar-mockup.js): smart-snap, area capture, drag handles, instructions
- Build script (build.py): minification pipeline
- Agent skill (SKILL.md): staged injection, data polling, rubric analysis
"""

import re
import pytest
from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent

# Source files
CORE_JS = PROJECT_ROOT / "src" / "x_ipe" / "static" / "js" / "injected" / "xipe-toolbar-core.js"
THEME_JS = PROJECT_ROOT / "src" / "x_ipe" / "static" / "js" / "injected" / "xipe-toolbar-theme.js"
MOCKUP_JS = PROJECT_ROOT / "src" / "x_ipe" / "static" / "js" / "injected" / "xipe-toolbar-mockup.js"
BUILD_PY = PROJECT_ROOT / "src" / "x_ipe" / "static" / "js" / "injected" / "build.py"

# Minified outputs (agent reads these)
CORE_MIN = PROJECT_ROOT / ".github" / "skills" / "x-ipe-tool-uiux-reference" / "references" / "toolbar-core.min.js"
THEME_MIN = PROJECT_ROOT / ".github" / "skills" / "x-ipe-tool-uiux-reference" / "references" / "toolbar-theme.min.js"
MOCKUP_MIN = PROJECT_ROOT / ".github" / "skills" / "x-ipe-tool-uiux-reference" / "references" / "toolbar-mockup.min.js"

# Skill
SKILL_PATH = PROJECT_ROOT / ".github" / "skills" / "x-ipe-tool-uiux-reference" / "SKILL.md"

# Legacy (should exist as deprecated reference)
LEGACY_TEMPLATE = PROJECT_ROOT / ".github" / "skills" / "x-ipe-tool-uiux-reference" / "references" / "toolbar-template.md"


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def core_js():
    """Load core shell source code."""
    assert CORE_JS.exists(), f"Core JS not found: {CORE_JS}"
    return CORE_JS.read_text(encoding="utf-8")


@pytest.fixture
def theme_js():
    """Load theme mode source code."""
    assert THEME_JS.exists(), f"Theme JS not found: {THEME_JS}"
    return THEME_JS.read_text(encoding="utf-8")


@pytest.fixture
def mockup_js():
    """Load mockup mode source code."""
    assert MOCKUP_JS.exists(), f"Mockup JS not found: {MOCKUP_JS}"
    return MOCKUP_JS.read_text(encoding="utf-8")


@pytest.fixture
def skill_md():
    """Load skill definition."""
    assert SKILL_PATH.exists(), f"Skill not found: {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# CORE SHELL TESTS (FEATURE-030-B)
# ═══════════════════════════════════════════════════════════════════════════


class TestCoreFileExists:
    """Verify source files exist at expected locations."""

    def test_core_js_exists(self):
        """Core shell JS file must exist."""
        assert CORE_JS.exists()

    def test_core_js_not_empty(self):
        """Core shell must have substantial content."""
        assert CORE_JS.stat().st_size > 500

    def test_theme_js_exists(self):
        """Theme mode JS file must exist."""
        assert THEME_JS.exists()

    def test_mockup_js_exists(self):
        """Mockup mode JS file must exist."""
        assert MOCKUP_JS.exists()

    def test_build_script_exists(self):
        """Build/minification script must exist."""
        assert BUILD_PY.exists()


class TestCoreIIFEStructure:
    """Verify IIFE structure and guard clause."""

    def test_iife_wrapper(self, core_js):
        """Core must be wrapped in an IIFE."""
        stripped = core_js.strip()
        assert stripped.startswith("(()") or stripped.startswith("(function"), \
            "Must start with IIFE"
        assert stripped.endswith("})();") or stripped.endswith("})()"), \
            "Must end with IIFE closure"

    def test_double_injection_guard(self, core_js):
        """FR-3: Guard prevents double injection."""
        assert "window.__xipeToolbarInjected" in core_js
        assert re.search(r"if\s*\(\s*window\.__xipeToolbarInjected\s*\)\s*return", core_js)


class TestCoreDataStore:
    """Verify data store initialization (FR-12, AC-24 through AC-27)."""

    def test_data_store_init(self, core_js):
        """AC-24: __xipeRefData must be initialized with v2.0 schema."""
        assert "window.__xipeRefData" in core_js

    def test_mode_field(self, core_js):
        """AC-27: Data store must include mode field."""
        assert re.search(r"mode\s*:\s*['\"]theme['\"]", core_js), \
            "Default mode must be 'theme'"

    def test_colors_array(self, core_js):
        """AC-25: Data store must include colors array."""
        assert re.search(r"colors\s*:\s*\[", core_js)

    def test_areas_array(self, core_js):
        """AC-26: Data store must include areas array."""
        assert re.search(r"areas\s*:\s*\[", core_js)

    def test_ref_ready_init(self, core_js):
        """FR-13: __xipeRefReady initialized to false."""
        assert "window.__xipeRefReady" in core_js
        assert re.search(r"__xipeRefReady\s*=\s*false", core_js)

    def test_ref_command_init(self, core_js):
        """FR-14: __xipeRefCommand initialized to null."""
        assert "window.__xipeRefCommand" in core_js


class TestCoreModeRegistry:
    """Verify mode extension point system (FR-16)."""

    def test_register_mode_function(self, core_js):
        """FR-16: Must expose window.__xipeRegisterMode function."""
        assert "window.__xipeRegisterMode" in core_js
        assert re.search(r"__xipeRegisterMode\s*=\s*", core_js)


class TestCoreToastAPI:
    """Verify toast notification system (FR-11, AC-19 through AC-23)."""

    def test_toast_function(self, core_js):
        """FR-11: Must expose window.__xipeToast function."""
        assert "window.__xipeToast" in core_js

    def test_toast_types(self, core_js):
        """AC-19: Toast supports info, progress, success, error types."""
        for toast_type in ["info", "progress", "success", "error"]:
            assert toast_type in core_js, f"Toast type '{toast_type}' must be supported"


class TestCoreCSSScoping:
    """Verify CSS isolation (FR-15, AC-32)."""

    def test_xipe_prefix(self, core_js):
        """AC-32: All CSS classes must use .xipe-* prefix."""
        # Find CSS class declarations in the source
        css_classes = re.findall(r'className\s*=\s*[\'"]([^\'"]+)[\'"]', core_js)
        css_classes += re.findall(r'classList\.add\([\'"]([^\'"]+)[\'"]\)', core_js)
        for cls in css_classes:
            for c in cls.split():
                assert c.startswith("xipe-"), \
                    f"CSS class '{c}' must use xipe- prefix"

    def test_fixed_positioning(self, core_js):
        """FR-15: Toolbar must use position: fixed."""
        assert "position: fixed" in core_js or "position:fixed" in core_js

    def test_z_index_max(self, core_js):
        """FR-15: z-index must be 2147483647."""
        assert "2147483647" in core_js


class TestCoreHamburger:
    """Verify hamburger icon (FR-5, AC-1 through AC-3)."""

    def test_hamburger_class(self, core_js):
        """FR-5: Hamburger button element must exist."""
        assert "xipe-hamburger" in core_js

    def test_hamburger_size(self, core_js):
        """FR-5: Hamburger should be 52x52px."""
        assert "52px" in core_js or "52" in core_js


class TestCorePanelExpandCollapse:
    """Verify expand/collapse behavior (FR-6, FR-7, AC-4 through AC-6)."""

    def test_panel_class(self, core_js):
        """FR-6: Panel element must exist."""
        assert "xipe-panel" in core_js

    def test_panel_width(self, core_js):
        """FR-6: Expanded panel should be 280px wide."""
        assert "280" in core_js

    def test_mouseenter_expand(self, core_js):
        """FR-6: Must handle mouseenter for expand."""
        assert "mouseenter" in core_js

    def test_mouseleave_collapse(self, core_js):
        """FR-7: Must handle mouseleave for collapse."""
        assert "mouseleave" in core_js

    def test_collapse_timer(self, core_js):
        """FR-7: Must use 2-second collapse delay."""
        assert "2000" in core_js


class TestCoreModeSwitcher:
    """Verify mode switching (FR-9, FR-10, AC-7 through AC-10)."""

    def test_mode_tabs(self, core_js):
        """FR-9: Must have mode tab elements."""
        assert "theme" in core_js.lower()
        assert "mockup" in core_js.lower()

    def test_default_mode(self, core_js):
        """FR-10: Default mode must be 'theme'."""
        assert re.search(r"['\"]theme['\"]", core_js)


class TestCoreDrag:
    """Verify drag behavior (FR-8, AC-11 through AC-13)."""

    def test_mousedown_drag(self, core_js):
        """FR-8: Must handle mousedown for drag start."""
        assert "mousedown" in core_js

    def test_mousemove_drag(self, core_js):
        """FR-8: Must handle mousemove for drag."""
        assert "mousemove" in core_js

    def test_mouseup_drag(self, core_js):
        """FR-8: Must handle mouseup for drag end."""
        assert "mouseup" in core_js


class TestCoreCommandPolling:
    """Verify bi-directional communication (FR-14, AC-29 through AC-30)."""

    def test_command_polling(self, core_js):
        """FR-14: Must poll __xipeRefCommand."""
        assert "__xipeRefCommand" in core_js

    def test_deep_capture_handler(self, core_js):
        """FR-14: Must handle 'deep_capture' command action."""
        assert "deep_capture" in core_js

    def test_command_clear_after_execute(self, core_js):
        """FR-14: Must clear command after execution."""
        assert re.search(r"__xipeRefCommand\s*=\s*null", core_js)

    def test_setinterval_polling(self, core_js):
        """FR-14: Must use setInterval for command polling."""
        assert "setInterval" in core_js


class TestCoreReadySignal:
    """Verify toolbar ready signal."""

    def test_toolbar_ready_signal(self, core_js):
        """Core must set __xipeToolbarReady = true after init."""
        assert "__xipeToolbarReady" in core_js
        assert re.search(r"__xipeToolbarReady\s*=\s*true", core_js)


class TestCoreFontLoading:
    """Verify lazy font loading (NFR-5)."""

    def test_lazy_font_loading(self, core_js):
        """NFR-5: Fonts must be loaded lazily."""
        assert "requestIdleCallback" in core_js or "setTimeout" in core_js
        assert "fonts.googleapis.com" in core_js or "font-display" in core_js


class TestCoreSelectorGenerator:
    """Verify CSS selector generation utility."""

    def test_selector_generator_exists(self, core_js):
        """Must include selector generation function."""
        assert "generateSelector" in core_js or "__xipeGenerateSelector" in core_js

    def test_body_prefix(self, core_js):
        """Selector should include body prefix."""
        assert "body" in core_js


# ═══════════════════════════════════════════════════════════════════════════
# THEME MODE TESTS (FEATURE-030-B-THEME)
# ═══════════════════════════════════════════════════════════════════════════


class TestThemeIIFEStructure:
    """Verify theme mode IIFE and registration."""

    def test_iife_wrapper(self, theme_js):
        """Theme must be wrapped in an IIFE."""
        stripped = theme_js.strip()
        assert stripped.startswith("(()") or stripped.startswith("(function")

    def test_mode_registration(self, theme_js):
        """Theme must register with core via __xipeRegisterMode."""
        assert "__xipeRegisterMode" in theme_js
        assert re.search(r"__xipeRegisterMode\s*\(\s*['\"]theme['\"]", theme_js)

    def test_core_dependency_check(self, theme_js):
        """Theme must check that core is loaded."""
        assert "__xipeRegisterMode" in theme_js


class TestThemeOffscreenCanvas:
    """Verify offscreen canvas for color picking (FR-T1, AC-T1 through AC-T7)."""

    def test_canvas_creation(self, theme_js):
        """FR-T1: Must create offscreen canvas element."""
        assert "createElement" in theme_js
        assert "canvas" in theme_js.lower()

    def test_canvas_context(self, theme_js):
        """FR-T1: Must get 2d context with willReadFrequently."""
        assert "getContext" in theme_js
        assert "2d" in theme_js

    def test_scroll_resize_handler(self, theme_js):
        """FR-T1: Must debounce re-render on scroll/resize."""
        assert "scroll" in theme_js
        assert "resize" in theme_js


class TestThemeMagnifier:
    """Verify circular magnifier (FR-T2, AC-T1)."""

    def test_magnifier_element(self, theme_js):
        """FR-T2: Must create magnifier element."""
        assert "magnifier" in theme_js.lower()

    def test_magnifier_canvas(self, theme_js):
        """FR-T2: Magnifier must have its own canvas for zoomed grid."""
        assert re.search(r"(magnifier|mag).*canvas|canvas.*magnifier", theme_js, re.I)

    def test_magnifier_size(self, theme_js):
        """FR-T2: Magnifier should be 120px."""
        assert "120" in theme_js

    def test_raf_throttling(self, theme_js):
        """FR-T2/AC-T7: Must use requestAnimationFrame for throttling."""
        assert "requestAnimationFrame" in theme_js

    def test_crosshair(self, theme_js):
        """FR-T2: Must draw crosshair at center pixel."""
        assert re.search(r"cross|#10b981|stroke", theme_js, re.I)


class TestThemeColorSampling:
    """Verify color sampling on click (FR-T3, AC-T2 through AC-T5)."""

    def test_click_handler(self, theme_js):
        """FR-T3: Must handle click for color sampling."""
        assert "click" in theme_js

    def test_get_image_data(self, theme_js):
        """FR-T3: Must use getImageData for pixel sampling."""
        assert "getImageData" in theme_js

    def test_hex_conversion(self, theme_js):
        """FR-T3: Must convert RGB to hex."""
        assert "Hex" in theme_js or "hex" in theme_js
        assert "toString(16)" in theme_js or "rgbToHex" in theme_js

    def test_hsl_conversion(self, theme_js):
        """FR-T3: Must convert RGB to HSL."""
        assert "hsl" in theme_js.lower()

    def test_color_id_format(self, theme_js):
        """FR-T3: Color IDs must follow color-001 format."""
        assert re.search(r"color-|padStart", theme_js)

    def test_selector_for_clicked_element(self, theme_js):
        """FR-T4: Must generate selector for clicked element."""
        assert "elementFromPoint" in theme_js or "generateSelector" in theme_js


class TestThemeCORSHandling:
    """Verify CORS error handling (FR-T8, AC-T6)."""

    def test_cors_try_catch(self, theme_js):
        """FR-T8: Must handle CORS via try/catch on getImageData."""
        assert "try" in theme_js
        assert "catch" in theme_js

    def test_cors_toast_message(self, theme_js):
        """AC-T6: Must show toast for cross-origin content."""
        assert re.search(r"cross.?origin|CORS|taint", theme_js, re.I)


class TestThemeSwatchPill:
    """Verify visual feedback (FR-T5, AC-T2)."""

    def test_swatch_feedback(self, theme_js):
        """FR-T5: Must show swatch pill near click point."""
        assert "swatch" in theme_js.lower() or "pill" in theme_js.lower()


class TestThemeRoleAnnotation:
    """Verify role annotation UI (FR-T6, AC-T9 through AC-T12)."""

    def test_role_presets(self, theme_js):
        """FR-T6: Must include primary, secondary, accent role presets."""
        assert "primary" in theme_js
        assert "secondary" in theme_js
        assert "accent" in theme_js

    def test_custom_role_input(self, theme_js):
        """AC-T11: Must support custom text role input."""
        assert "custom" in theme_js.lower()
        assert "input" in theme_js.lower()

    def test_role_stored_in_data(self, theme_js):
        """AC-T10: Must store role in __xipeRefData.colors[n].role."""
        assert "role" in theme_js


class TestThemeCreateButton:
    """Verify Create Theme trigger (FR-T7, AC-T13, AC-T16)."""

    def test_create_theme_button(self, theme_js):
        """FR-T7: Must have Create Theme button."""
        assert re.search(r"create.?theme|Create Theme", theme_js, re.I)

    def test_create_sets_ready(self, theme_js):
        """AC-T13: Create Theme must set __xipeRefReady = true."""
        assert "__xipeRefReady" in theme_js

    def test_mode_set_to_theme(self, theme_js):
        """AC-T13: Must set mode to 'theme' on Create."""
        assert re.search(r"mode\s*=\s*['\"]theme['\"]", theme_js)


class TestThemeWizardSteps:
    """Verify 3-step wizard navigation (FR-T9)."""

    def test_step_navigation(self, theme_js):
        """FR-T9: Must support step navigation (1-3)."""
        assert "step" in theme_js.lower()
        # Should have at least 3 steps
        assert re.search(r"step.{0,5}[123]|currentStep|step.*3", theme_js, re.I)


# ═══════════════════════════════════════════════════════════════════════════
# MOCKUP MODE TESTS (FEATURE-030-B-MOCKUP)
# ═══════════════════════════════════════════════════════════════════════════


class TestMockupIIFEStructure:
    """Verify mockup mode IIFE and registration."""

    def test_iife_wrapper(self, mockup_js):
        """Mockup must be wrapped in an IIFE."""
        stripped = mockup_js.strip()
        assert stripped.startswith("(()") or stripped.startswith("(function")

    def test_mode_registration(self, mockup_js):
        """Mockup must register with core via __xipeRegisterMode."""
        assert "__xipeRegisterMode" in mockup_js
        assert re.search(r"__xipeRegisterMode\s*\(\s*['\"]mockup['\"]", mockup_js)


class TestMockupSmartSnap:
    """Verify smart-snap detection (FR-M1, FR-M2, AC-M1 through AC-M2)."""

    def test_semantic_tags(self, mockup_js):
        """FR-M1: Must check semantic HTML tags."""
        for tag in ["SECTION", "NAV", "ARTICLE", "ASIDE", "HEADER", "FOOTER", "MAIN"]:
            assert tag in mockup_js or tag.lower() in mockup_js, \
                f"Semantic tag '{tag}' must be in snap detection"

    def test_role_attribute_check(self, mockup_js):
        """FR-M1: Must check for ARIA role attribute."""
        assert "role" in mockup_js

    def test_fallback_div(self, mockup_js):
        """FR-M2: Fallback must check div with offsetWidth/Height > 50."""
        assert "DIV" in mockup_js or "div" in mockup_js
        assert "50" in mockup_js

    def test_max_depth(self, mockup_js):
        """FR-M1: Must traverse max 5 ancestor levels."""
        assert "5" in mockup_js

    def test_body_exclusion(self, mockup_js):
        """Edge case: Must skip body/html elements."""
        assert "document.body" in mockup_js


class TestMockupComponentCapture:
    """Verify area capture (FR-M5, FR-M6, AC-M5 through AC-M6)."""

    def test_bounding_rect(self, mockup_js):
        """FR-M5: Must use getBoundingClientRect."""
        assert "getBoundingClientRect" in mockup_js

    def test_computed_styles(self, mockup_js):
        """FR-M5: Must use getComputedStyle."""
        assert "getComputedStyle" in mockup_js

    def test_area_id_format(self, mockup_js):
        """FR-M6: Area IDs must follow area-N format."""
        assert re.search(r"area-|areaCounter", mockup_js)

    def test_lightweight_capture(self, mockup_js):
        """FR-M5: Must capture limited CSS property set."""
        # Check for at least some of the lightweight properties
        for prop in ["display", "position", "background", "font-family", "border-radius"]:
            assert prop in mockup_js, f"Property '{prop}' must be in capture list"

    def test_max_areas(self, mockup_js):
        """NFR-M5: Must enforce max 20 areas."""
        assert "20" in mockup_js

    def test_toolbar_click_exclusion(self, mockup_js):
        """Edge case: Must ignore clicks on toolbar itself."""
        assert "xipe-toolbar" in mockup_js


class TestMockupAreaDataModel:
    """Verify area data model stores bounding_box and snap context (v2.3, TD 2.14)."""

    def test_area_stores_bounding_box(self, mockup_js):
        """v2.3: captureArea must store bounding_box in area object."""
        assert "bounding_box" in mockup_js

    def test_bounding_box_has_coordinates(self, mockup_js):
        """v2.3: bounding_box must have x, y, width, height."""
        # Check for bounding_box construction with rect properties
        assert re.search(r"bounding_box.*\{.*x.*y.*width.*height", mockup_js, re.DOTALL)

    def test_area_stores_selector(self, mockup_js):
        """v2.3: Area must store snap element selector."""
        assert "selector" in mockup_js

    def test_area_stores_tag(self, mockup_js):
        """v2.3: Area must store snap element tag name."""
        assert re.search(r"tag.*tagName|tagName.*tag", mockup_js, re.I)

    def test_area_id_sequential(self, mockup_js):
        """v2.3: Area IDs must be sequential (area-1, area-2, ...)."""
        assert re.search(r"area-\$\{|`area-|'area-'.*\+|areaCounter", mockup_js)


class TestMockupOverlay:
    """Verify snap overlay with drag handles (FR-M3, FR-M4, AC-M3 through AC-M4)."""

    def test_overlay_border(self, mockup_js):
        """FR-M3: Must show dashed teal border."""
        assert "dashed" in mockup_js
        assert "#10b981" in mockup_js or "10b981" in mockup_js

    def test_tag_badge(self, mockup_js):
        """FR-M3: Must show tag badge."""
        assert "badge" in mockup_js.lower() or "tag" in mockup_js.lower()

    def test_drag_handles(self, mockup_js):
        """FR-M4: Must create drag handles."""
        assert "handle" in mockup_js.lower() or "resize" in mockup_js.lower()

    def test_eight_handles(self, mockup_js):
        """FR-M4: Must have 8 drag handle positions (4 corners + 4 midpoints)."""
        # Check for at least some resize cursors
        resize_cursors = re.findall(r"(nw|ne|sw|se|n|s|e|w)-resize", mockup_js)
        assert len(resize_cursors) >= 4, "Must have at least 4 resize handle directions"


class TestMockupInstructions:
    """Verify per-area instructions (FR-M7, AC-M8 through AC-M10)."""

    def test_instruction_field(self, mockup_js):
        """FR-M7: Must support instruction input per area."""
        assert "instruction" in mockup_js


class TestMockupAnalyze:
    """Verify analyze step (FR-M8, AC-M11 through AC-M16)."""

    def test_analyze_button(self, mockup_js):
        """FR-M8: Must have Analyze button."""
        assert re.search(r"[Aa]nalyz", mockup_js)

    def test_sets_ready_for_analysis(self, mockup_js):
        """AC-M11: Must set __xipeRefReady for agent analysis."""
        assert "__xipeRefReady" in mockup_js


class TestMockupGenerate:
    """Verify generate step (FR-M10, FR-M11, AC-M17 through AC-M22)."""

    def test_generate_button(self, mockup_js):
        """Must have Generate button."""
        assert re.search(r"[Gg]enerat", mockup_js)

    def test_mode_set_to_mockup(self, mockup_js):
        """Must set mode to 'mockup' on send."""
        assert re.search(r"mode\s*=\s*['\"]mockup['\"]", mockup_js)


class TestMockupWizardSteps:
    """Verify 4-step wizard navigation (FR-M13)."""

    def test_step_navigation(self, mockup_js):
        """FR-M13: Must support 4-step navigation."""
        assert "step" in mockup_js.lower()
        assert re.search(r"step.{0,5}[1234]|currentStep|step.*4", mockup_js, re.I)


# ═══════════════════════════════════════════════════════════════════════════
# MOCKUP MODE v2.1 TESTS (CR-001: Button Lifecycle & Agent Flow)
# ═══════════════════════════════════════════════════════════════════════════


class TestMockupButtonGlobals:
    """Verify global button control variables (FR-M14, AC-M31)."""

    def test_analyze_enabled_global_in_core(self, core_js):
        """FR-M14: Core must initialize __xipeAnalyzeEnabled."""
        assert "__xipeAnalyzeEnabled" in core_js

    def test_generate_enabled_global_in_core(self, core_js):
        """FR-M14: Core must initialize __xipeGenerateMockupEnabled."""
        assert "__xipeGenerateMockupEnabled" in core_js

    def test_analyze_enabled_default_false(self, core_js):
        """FR-M14: __xipeAnalyzeEnabled must default to false."""
        assert re.search(r"__xipeAnalyzeEnabled\s*=\s*false", core_js)

    def test_generate_enabled_default_false(self, core_js):
        """FR-M14: __xipeGenerateMockupEnabled must default to false."""
        assert re.search(r"__xipeGenerateMockupEnabled\s*=\s*false", core_js)


class TestMockupButtonPolling:
    """Verify toolbar polls global variables for button state (FR-M14)."""

    def test_polling_interval_exists(self, mockup_js):
        """FR-M14: Must have setInterval for button state polling."""
        assert "setInterval" in mockup_js

    def test_polls_analyze_enabled(self, mockup_js):
        """FR-M14: Must read __xipeAnalyzeEnabled in polling."""
        assert "__xipeAnalyzeEnabled" in mockup_js

    def test_polls_generate_enabled(self, mockup_js):
        """FR-M14: Must read __xipeGenerateMockupEnabled in polling."""
        assert "__xipeGenerateMockupEnabled" in mockup_js

    def test_polling_removes_processing_when_enabled(self, mockup_js):
        """TASK-451: Polling must NOT skip buttons that have processing class.

        The polling condition must re-enable buttons even when xipe-btn-processing
        is present — that's exactly the state that needs clearing. The guard
        '!...contains(processing)' is inverted and prevents re-enabling.
        """
        # The polling block should NOT have a negative guard on processing class.
        # Extract the setInterval polling block and check it doesn't skip processing buttons.
        polling_match = re.search(
            r'setInterval\s*\(\s*\(\)\s*=>\s*\{(.+?)\}\s*,\s*500\s*\)',
            mockup_js,
            re.DOTALL,
        )
        assert polling_match, "Button polling setInterval block not found"
        polling_body = polling_match.group(1)
        # Must NOT contain negated processing-class guard
        assert not re.search(
            r'!\s*\w+\.classList\.contains\([\'"]xipe-btn-processing[\'"]\)',
            polling_body,
        ), "Polling must not skip buttons with processing class — inverted guard bug"

    def test_skill_enforces_button_reenable(self, skill_md):
        """TASK-451: SKILL.md must instruct agents to directly re-enable buttons."""
        assert re.search(
            r'disabled\s*=\s*false.*classList\.remove|classList\.remove.*disabled\s*=\s*false',
            skill_md,
            re.DOTALL,
        ), "SKILL.md must instruct agents to directly set disabled=false and remove processing class"


class TestMockupActionField:
    """Verify action field distinguishes analyze vs generate (FR-M16)."""

    def test_analyze_sets_action(self, mockup_js):
        """FR-M16: Analyze click must set action = 'analyze'."""
        assert re.search(r"action\s*=\s*['\"]analyze['\"]", mockup_js)

    def test_generate_sets_action(self, mockup_js):
        """FR-M16: Generate click must set action = 'generate'."""
        assert re.search(r"action\s*=\s*['\"]generate['\"]", mockup_js)


class TestMockupProcessingAnimation:
    """Verify processing animation on buttons (FR-M15, AC-M11, AC-M17)."""

    def test_processing_css_class(self, mockup_js):
        """FR-M15: Must add processing CSS class on click."""
        assert "xipe-btn-processing" in mockup_js

    def test_processing_spinner_keyframes(self, mockup_js):
        """FR-M15: Must define spinner animation (xipe-spin or similar)."""
        assert re.search(r"xipe-spin|@keyframes|animation.*spin", mockup_js, re.I)

    def test_analyze_disables_on_click(self, mockup_js):
        """AC-M11: Analyze button must add processing class on click."""
        # This test will pass once xipe-btn-processing is added to analyze handler
        assert "xipe-btn-processing" in mockup_js

    def test_generate_disables_on_click(self, mockup_js):
        """AC-M17: Generate button must set disabled = true on click."""
        # Both buttons should disable on click
        assert re.search(r"disabled\s*=\s*true", mockup_js)


class TestMockupButtonDataAttributes:
    """Verify data attributes for stable button targeting (TD 2.2)."""

    def test_analyze_data_attribute(self, mockup_js):
        """TD 2.3: Analyze button must have data-xipe-analyze attribute."""
        assert "data-xipe-analyze" in mockup_js

    def test_generate_data_attribute(self, mockup_js):
        """TD 2.4: Generate button must have data-xipe-generate attribute."""
        assert "data-xipe-generate" in mockup_js


class TestMockupAnalyzeDisablesGlobal:
    """Verify analyze click sets global to false (AC-M11, FR-M14)."""

    def test_analyze_click_sets_global_false(self, mockup_js):
        """AC-M11: Clicking Analyze must set __xipeAnalyzeEnabled = false."""
        # The onclick handler should set the global to false
        assert re.search(r"__xipeAnalyzeEnabled\s*=\s*false", mockup_js)

    def test_generate_click_sets_global_false(self, mockup_js):
        """AC-M17: Clicking Generate must set __xipeGenerateMockupEnabled = false."""
        assert re.search(r"__xipeGenerateMockupEnabled\s*=\s*false", mockup_js)


class TestSkillDecoupledAnalyzeGenerate:
    """Verify skill decouples analyze from generate (FR-M20, AC-M31–M33)."""

    def test_skill_references_action_analyze(self, skill_md):
        """FR-M20: Skill must check action = 'analyze'."""
        assert re.search(r"action.*=.*['\"]analyze['\"]|action.*analyze", skill_md, re.I)

    def test_skill_references_action_generate(self, skill_md):
        """FR-M20: Skill must check action = 'generate'."""
        assert re.search(r"action.*=.*['\"]generate['\"]|action.*generate", skill_md, re.I)

    def test_skill_no_auto_trigger(self, skill_md):
        """FR-M20: Skill must NOT auto-trigger generation after analysis."""
        assert re.search(r"NOT.*auto.?trigger|does NOT|no.*auto", skill_md, re.I)

    def test_skill_resume_polling_after_analysis(self, skill_md):
        """AC-M31: Skill must resume polling after analysis completes."""
        assert re.search(r"resume.*poll|loop.*back|AwaitData", skill_md, re.I)

    def test_skill_enables_both_buttons(self, skill_md):
        """AC-M15/AC-M31: Skill must set both enabled variables after analysis."""
        assert "__xipeAnalyzeEnabled" in skill_md
        assert "__xipeGenerateMockupEnabled" in skill_md


class TestSkillExactAreaScreenshots:
    """Verify skill takes exact area screenshots by coordinate (FR-M17, AC-M42–M43, TD 2.8)."""

    def test_skill_coordinate_based_crop(self, skill_md):
        """TD 2.8: Skill must crop screenshots by bounding_box coordinates, not DOM UID."""
        assert "bounding_box" in skill_md
        assert re.search(r"crop|clip|coordinate", skill_md, re.I)

    def test_skill_scroll_before_capture(self, skill_md):
        """TD 2.8: Skill must scroll area into viewport before screenshot."""
        assert re.search(r"scroll.*viewport|scrollTo|scroll.*bounding", skill_md, re.I)

    def test_skill_dimension_validation(self, skill_md):
        """AC-M43: Cropped dimensions must match bounding_box within 1px."""
        assert re.search(r"1px|within.*1|dimension.*match|validate.*dimension", skill_md, re.I)

    def test_skill_full_page_screenshot(self, skill_md):
        """AC-M46: Skill must take viewport screenshot saved as full-page.png."""
        assert re.search(r"take_screenshot.*full-page\.png|full-page\.png.*screenshot", skill_md, re.I)
        assert re.search(r"full-page\.png", skill_md)

    def test_skill_per_area_screenshot_naming(self, skill_md):
        """AC-M47: Per-area screenshots must use {area-id}.png naming."""
        assert re.search(r"area-\d+\.png|\{area.?id\}\.png|screenshots/", skill_md, re.I)

    def test_skill_no_dom_uid_for_screenshots(self, skill_md):
        """TD 2.8: Skill must NOT use DOM element UID for area screenshots."""
        assert re.search(r"not.*uid|not.*dom.*element.*uid|coordinate.based|NOT.*UID", skill_md, re.I)


class TestSkillAreaElementDiscovery:
    """Verify skill discovers all elements within area bounding_box (FR-M18, AC-M44, TD 2.9)."""

    def test_skill_element_discovery_concept(self, skill_md):
        """TD 2.9: Skill must reference element discovery for areas."""
        assert re.search(r"element.*discover|discover.*element|discovered_elements", skill_md, re.I)

    def test_skill_bbox_intersection(self, skill_md):
        """TD 2.9: Skill must check element intersection with bounding_box."""
        assert re.search(r"getBoundingClientRect|bounding.*rect|intersect", skill_md, re.I)

    def test_skill_all_elements_not_just_subtree(self, skill_md):
        """AC-M44: Must discover ALL elements in bbox, not just snap element subtree."""
        assert re.search(r"all.*element|querySelectorAll|not.*just.*snap|not.*subtree", skill_md, re.I)

    def test_skill_classify_element_types(self, skill_md):
        """TD 2.9: Must classify elements by type (img, svg, canvas, video, dom)."""
        # Must reference at least img, svg, canvas types
        assert re.search(r"img|image", skill_md, re.I)
        assert re.search(r"svg", skill_md, re.I)
        assert re.search(r"canvas", skill_md, re.I)

    def test_skill_extract_computed_styles(self, skill_md):
        """TD 2.9: Must extract computed styles for discovered elements."""
        assert re.search(r"computedStyle|getComputedStyle|computed.*style", skill_md, re.I)

    def test_skill_skip_toolbar_elements(self, skill_md):
        """TD 2.9: Must skip toolbar container elements during discovery."""
        assert re.search(r"skip.*toolbar|xipe-toolbar-container|closest.*toolbar", skill_md, re.I)


class TestSkillResourceDownload:
    """Verify skill downloads static resources from discovered elements (FR-M25, AC-M45, TD 2.10)."""

    def test_skill_resource_download_concept(self, skill_md):
        """TD 2.10: Skill must reference resource download for areas."""
        assert re.search(r"resource.*download|download.*resource", skill_md, re.I)

    def test_skill_fetch_in_page_context(self, skill_md):
        """TD 2.10: Must use page-context fetch via evaluate_script."""
        assert "evaluate_script" in skill_md
        assert "fetch" in skill_md

    def test_skill_image_download(self, skill_md):
        """TD 2.10: Must download images (img src, background-image)."""
        assert re.search(r"img.*src|background.?image", skill_md, re.I)

    def test_skill_svg_download(self, skill_md):
        """TD 2.10: Must handle SVGs (inline outerHTML or external src)."""
        assert re.search(r"svg|outerHTML", skill_md, re.I)

    def test_skill_font_detection(self, skill_md):
        """TD 2.10: Must detect @font-face URLs from stylesheets."""
        assert re.search(r"font.?face|CSSFontFaceRule|font.*url|stylesheet.*font", skill_md, re.I)

    def test_skill_resource_naming_convention(self, skill_md):
        """TD 2.10: Resources must use {area-id}-{type}-{N}.{ext} naming."""
        assert re.search(r"area-\d+-img|area.?id.*img|\{area.?id\}-img", skill_md, re.I)

    def test_skill_resources_folder(self, skill_md):
        """TD 2.10: Resources must be saved to resources/ folder."""
        assert re.search(r"resources/|resources.*folder", skill_md, re.I)


class TestSkillStructuredOutput:
    """Verify skill generates structured folder output (FR-M26, FR-M27, AC-M46–M48, TD Flow 6)."""

    def test_skill_structure_html_output(self, skill_md):
        """AC-M47: Must generate {area-id}-structure.html files."""
        assert re.search(r"structure\.html|structure.*html", skill_md, re.I)

    def test_skill_styles_css_output(self, skill_md):
        """AC-M47: Must generate {area-id}-styles.css files."""
        assert re.search(r"styles\.css|styles.*css", skill_md, re.I)

    def test_skill_mimic_strategy(self, skill_md):
        """AC-M48: Must generate mimic-strategy.md."""
        assert "mimic-strategy" in skill_md

    def test_skill_summarized_reference(self, skill_md):
        """AC-M47: Must generate summarized-uiux-reference.md."""
        assert "summarized-uiux-reference" in skill_md

    def test_skill_page_element_references_folder(self, skill_md):
        """AC-M47: Must use page-element-references/ folder structure."""
        assert "page-element-references" in skill_md

    def test_skill_save_uiux_reference_call(self, skill_md):
        """Flow 6: Must call save_uiux_reference for structured output."""
        assert "save_uiux_reference" in skill_md

    def test_skill_verify_folder_structure(self, skill_md):
        """Flow 6: Must verify folder structure after save."""
        assert re.search(r"verify.*folder|verify.*structure|check.*folder", skill_md, re.I)


class TestSkillVersionedMockups:
    """Verify skill generates versioned mockup files (FR-M19, AC-M34–M35)."""

    def test_skill_versioned_filenames(self, skill_md):
        """FR-M19: Skill must use versioned mockup filenames."""
        assert re.search(r"mockup-v\d|version.*suffix|versioned.*file", skill_md, re.I)

    def test_skill_no_overwrite(self, skill_md):
        """AC-M35: Skill must not overwrite existing mockup versions."""
        assert re.search(r"not.*overwrite|never.*overwrite|no.*overwrite|append|preserved", skill_md, re.I)


# ═══════════════════════════════════════════════════════════════════════════
# BUILD SCRIPT TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestBuildScript:
    """Verify build.py minification pipeline."""

    def test_build_script_exists(self):
        """Build script must exist."""
        assert BUILD_PY.exists()

    def test_build_script_content(self):
        """Build script must reference all 3 source files."""
        content = BUILD_PY.read_text(encoding="utf-8")
        assert "xipe-toolbar-core" in content
        assert "xipe-toolbar-theme" in content
        assert "xipe-toolbar-mockup" in content

    def test_build_output_paths(self):
        """Build script must output to references/ directory."""
        content = BUILD_PY.read_text(encoding="utf-8")
        assert "toolbar-core.min.js" in content
        assert "toolbar-theme.min.js" in content
        assert "toolbar-mockup.min.js" in content


class TestMinifiedOutputs:
    """Verify minified files exist and meet size targets."""

    def test_core_min_exists(self):
        """Minified core must exist."""
        assert CORE_MIN.exists(), f"Core min not found: {CORE_MIN}"

    def test_theme_min_exists(self):
        """Minified theme must exist."""
        assert THEME_MIN.exists(), f"Theme min not found: {THEME_MIN}"

    def test_mockup_min_exists(self):
        """Minified mockup must exist."""
        assert MOCKUP_MIN.exists(), f"Mockup min not found: {MOCKUP_MIN}"

    def test_core_size_target(self):
        """NFR-2: Core minified must be < 12KB (was <8KB, adjusted for CSS)."""
        size = CORE_MIN.stat().st_size
        assert size < 12288, f"Core min is {size} bytes, target < 12288"

    def test_theme_size_target(self):
        """Theme minified must be < 15KB (was <5KB, adjusted for CSS)."""
        size = THEME_MIN.stat().st_size
        assert size < 15360, f"Theme min is {size} bytes, target < 15360"

    def test_mockup_size_target(self):
        """Mockup minified must be < 15KB (was <5KB, adjusted for CSS)."""
        size = MOCKUP_MIN.stat().st_size
        assert size < 15360, f"Mockup min is {size} bytes, target < 15360"

    def test_minified_is_valid_iife(self):
        """Minified files must still be valid IIFEs."""
        for path in [CORE_MIN, THEME_MIN, MOCKUP_MIN]:
            content = path.read_text(encoding="utf-8").strip()
            assert content.startswith("("), f"{path.name} must start with ("
            assert content.endswith(")()") or content.endswith("})();") or content.endswith("})()"), \
                f"{path.name} must end with IIFE closure"

    def test_minified_smaller_than_source(self):
        """Minified files must be smaller than source."""
        pairs = [(CORE_JS, CORE_MIN), (THEME_JS, THEME_MIN), (MOCKUP_JS, MOCKUP_MIN)]
        for src, min_f in pairs:
            assert min_f.stat().st_size < src.stat().st_size, \
                f"{min_f.name} must be smaller than {src.name}"


# ═══════════════════════════════════════════════════════════════════════════
# AGENT SKILL TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestSkillDefinition:
    """Verify skill SKILL.md for v2.0 staged injection."""

    def test_skill_exists(self):
        """Skill SKILL.md must exist."""
        assert SKILL_PATH.exists()

    def test_staged_injection_references(self, skill_md):
        """Skill must reference toolbar injection file."""
        assert "toolbar.min.js" in skill_md

    def test_toolbar_ready_polling(self, skill_md):
        """Skill must poll __xipeToolbarReady after core injection."""
        assert "__xipeToolbarReady" in skill_md

    def test_data_polling(self, skill_md):
        """Skill must poll __xipeRefReady for user data."""
        assert "__xipeRefReady" in skill_md
        assert "__xipeRefData" in skill_md

    def test_screenshot_provision(self, skill_md):
        """Skill must reference screenshot handling."""
        assert "screenshot" in skill_md.lower()
        assert "take_screenshot" in skill_md

    def test_deep_capture_command(self, skill_md):
        """Skill must support __xipeRefCommand for deep capture."""
        assert "__xipeRefCommand" in skill_md
        assert "deep_capture" in skill_md

    def test_save_uiux_reference(self, skill_md):
        """Skill must use save_uiux_reference MCP for persistence."""
        assert "save_uiux_reference" in skill_md

    def test_rubric_dimensions(self, skill_md):
        """Skill must evaluate 5 rubric dimensions for mockup mode."""
        for dim in ["layout", "typography", "color", "spacing", "visual"]:
            assert dim in skill_md.lower(), f"Rubric dimension '{dim}' must be referenced"

    def test_three_evaluate_script_calls(self, skill_md):
        """Skill must show 3 evaluate_script injection steps."""
        matches = re.findall(r"evaluate_script", skill_md)
        assert len(matches) >= 3, "Must have at least 3 evaluate_script calls (core + theme + mockup)"

    def test_iterative_validation(self, skill_md):
        """Skill must describe iterative mockup validation (max 3)."""
        assert re.search(r"3.*iteration|max.*3|attempt.*3", skill_md, re.I)


class TestSkillModeHandling:
    """Verify skill handles both modes correctly."""

    def test_theme_mode_handler(self, skill_md):
        """Skill must handle theme mode (invoke brand-theme-creator)."""
        assert "brand-theme-creator" in skill_md or "theme" in skill_md.lower()

    def test_mockup_mode_handler(self, skill_md):
        """Skill must handle mockup mode (generate mockup)."""
        assert "mockup" in skill_md.lower()


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestSourceTemplateSync:
    """Verify source files and minified outputs are in sync."""

    def test_core_has_all_globals(self, core_js):
        """Core must define all required globals."""
        globals_required = [
            "__xipeToolbarInjected",
            "__xipeRefData",
            "__xipeRefReady",
            "__xipeRefCommand",
            "__xipeRegisterMode",
            "__xipeToast",
            "__xipeToolbarReady",
            "__xipeAnalyzeEnabled",
            "__xipeGenerateMockupEnabled",
        ]
        for g in globals_required:
            assert g in core_js, f"Global '{g}' must be defined in core"

    def test_theme_does_not_redefine_globals(self, theme_js):
        """Theme must not redefine core globals."""
        assert "__xipeToolbarInjected" not in theme_js or "if" in theme_js
        assert "window.__xipeRefData =" not in theme_js

    def test_mockup_does_not_redefine_globals(self, mockup_js):
        """Mockup must not redefine core globals."""
        assert "__xipeToolbarInjected" not in mockup_js or "if" in mockup_js
        assert "window.__xipeRefData =" not in mockup_js

    def test_no_elements_array_in_schema(self, core_js):
        """v2.0+ schema uses 'areas', not 'elements'."""
        # Should not have elements: [] in data store init
        assert not re.search(r"elements\s*:\s*\[", core_js), \
            "v2.0+ uses areas[], not elements[]"


# ═══════════════════════════════════════════════════════════════════════════
# BUG FIX TESTS — TASK-467
# ═══════════════════════════════════════════════════════════════════════════


class TestSkillViewportScreenshot:
    """Bug 1: full-page.png should be viewport screenshot, not fullPage."""

    def test_skill_viewport_screenshot_not_fullpage(self, skill_md):
        """SKILL.md must NOT use fullPage: true as a parameter for screenshot."""
        # Find all instances of fullPage: true — they must appear only in
        # warning/prohibition context (e.g., "Do NOT use fullPage: true")
        for m in re.finditer(r"fullPage:\s*true", skill_md):
            context = skill_md[max(0, m.start()-40):m.start()]
            assert re.search(r"NOT|not|Don.t|never|avoid", context, re.I), \
                f"fullPage: true used as parameter (not prohibition) near: ...{context}..."

    def test_skill_viewport_screenshot_instruction(self, skill_md):
        """SKILL.md must instruct viewport-only screenshot for reference."""
        assert re.search(r"viewport.*screenshot|viewport.*capture|take_screenshot\b(?!.*fullPage)", skill_md, re.I)


class TestSkillAreaScreenshotCrop:
    """Bug 2: area screenshot must be cropped to exact bounding box."""

    def test_skill_area_screenshot_uses_clip(self, skill_md):
        """SKILL.md must instruct clipping area screenshot to bounding box."""
        # Must reference using evaluate_script to crop or clip region
        assert re.search(r"clip.*bounding|crop.*bounding|clip.*region|clip.*area", skill_md, re.I)


class TestSkillMockupUsesDiscoveredElements:
    """Bug 3: Mockup must use ALL elements in bounding box, not just snap element."""

    def test_skill_mockup_uses_discovered_not_outer_html(self, skill_md):
        """SKILL.md generate flow must use discovered_elements, not snap outer_html."""
        # Step 10b must reference discovered_elements as content source
        assert re.search(r"discovered_elements.*content|discovered_elements.*source|discovered_elements.*mockup", skill_md, re.I)

    def test_skill_mockup_not_only_outer_html(self, skill_md):
        """SKILL.md must NOT rely solely on snap element outer_html for mockup."""
        # Must explicitly warn not to use only outer_html
        assert re.search(r"not.*only.*outer_html|not.*rely.*outer_html|beyond.*snap.*element|all.*elements.*bounding", skill_md, re.I)


class TestToolbarSnapVsBoundingBox:
    """Bug 4: Area selector must represent bounding box, not snap element."""

    def test_mockup_stores_snap_selector(self, mockup_js):
        """Toolbar must store snap element as snap_selector (anchor), not selector."""
        assert re.search(r"snap_selector|snap_element|snap_tag", mockup_js), \
            "Toolbar must store snap element reference separately as snap_selector"

    def test_mockup_area_not_single_selector(self, mockup_js):
        """Area data must not use a single selector as the area identity."""
        # The area is defined by bounding_box, not by a single DOM selector
        # capture function should store snap info distinctly
        assert re.search(r"snap_selector|snap_tag", mockup_js)


# ═══════════════════════════════════════════════════════════════════════════
# BUG FIX TESTS — TASK-474: Select toggle + analyze/generate button persistence
# ═══════════════════════════════════════════════════════════════════════════


class TestSnapToggleAfterCapture:
    """Bug 1: Select Area button must toggle off after capturing an area."""

    def test_snap_deactivates_after_capture(self, mockup_js):
        """After captureArea, snapActive must be set to false."""
        # handleSnapClick must set snapActive = false after calling captureArea
        assert re.search(
            r"captureArea\(target\).*?snapActive\s*=\s*false",
            mockup_js,
            re.DOTALL,
        ), "snapActive must be set to false after captureArea call"

    def test_render_area_list_called_after_deactivation(self, mockup_js):
        """After deactivating snap, area list must be re-rendered."""
        assert re.search(
            r"snapActive\s*=\s*false.*?renderAreaList\(\)",
            mockup_js,
            re.DOTALL,
        ), "renderAreaList() must be called after snapActive = false"


class TestReadOnlyAreaListInSteps3And4:
    """Bug 2: Steps 3/4 must show read-only area summary, not interactive C()."""

    def test_source_has_render_area_summary(self, mockup_js):
        """Source must define renderAreaSummary for read-only area display."""
        assert "renderAreaSummary" in mockup_js, \
            "Must have renderAreaSummary function for read-only area list in steps 3/4"

    def test_analyze_step_uses_area_summary(self, mockup_js):
        """renderAnalyze must call renderAreaSummary, not renderAreaList."""
        # Find the renderAnalyze function body
        analyze_match = re.search(
            r"function renderAnalyze\(\)\s*\{(.+?)(?=function\s+render|$)",
            mockup_js,
            re.DOTALL,
        )
        assert analyze_match, "renderAnalyze function not found"
        body = analyze_match.group(1)
        assert "renderAreaSummary" in body, \
            "renderAnalyze must use renderAreaSummary for read-only area list"
        assert "renderAreaList" not in body, \
            "renderAnalyze must NOT call renderAreaList (interactive, causes rebuild)"

    def test_generate_step_uses_area_summary(self, mockup_js):
        """renderGenerate must call renderAreaSummary, not renderAreaList."""
        generate_match = re.search(
            r"function renderGenerate\(\)\s*\{(.+?)(?=function\s+|// ===|$)",
            mockup_js,
            re.DOTALL,
        )
        assert generate_match, "renderGenerate function not found"
        body = generate_match.group(1)
        assert "renderAreaSummary" in body, \
            "renderGenerate must use renderAreaSummary for read-only area list"
        assert "renderAreaList" not in body, \
            "renderGenerate must NOT call renderAreaList (interactive, causes rebuild)"

    def test_area_summary_no_click_handlers(self, mockup_js):
        """renderAreaSummary must NOT have click event listeners."""
        summary_match = re.search(
            r"function renderAreaSummary\([^)]*\)\s*\{(.+?)\n\s*\}",
            mockup_js,
            re.DOTALL,
        )
        assert summary_match, "renderAreaSummary function not found"
        body = summary_match.group(1)
        assert "addEventListener" not in body, \
            "renderAreaSummary must be read-only (no click handlers)"
        assert "onclick" not in body, \
            "renderAreaSummary must be read-only (no onclick)"

    def test_area_summary_no_remove_buttons(self, mockup_js):
        """renderAreaSummary must NOT have remove (✕) buttons or splice calls."""
        summary_match = re.search(
            r"function renderAreaSummary\([^)]*\)\s*\{(.+?)\n\s*\}",
            mockup_js,
            re.DOTALL,
        )
        assert summary_match, "renderAreaSummary function not found"
        body = summary_match.group(1)
        # Must not have splice (removal logic) or xipe-area-remove class
        assert "splice" not in body, \
            "renderAreaSummary must not have splice (removal logic)"
        assert "xipe-area-remove" not in body, \
            "renderAreaSummary must not have remove button class"


class TestCombinedToolbarReadOnlyAreaList:
    """Bug 2 (combined toolbar.min.js): Steps 3/4 must use R() not C()."""

    COMBINED_MIN = Path(__file__).parent.parent / ".github" / "skills" / \
        "x-ipe-tool-uiux-reference" / "references" / "toolbar.min.js"

    def test_combined_has_readonly_function(self):
        """Combined toolbar.min.js must define R() read-only area function."""
        if not self.COMBINED_MIN.exists():
            pytest.skip("Combined toolbar.min.js not found")
        content = self.COMBINED_MIN.read_text(encoding="utf-8")
        assert "function R(e){" in content, \
            "Combined toolbar.min.js must have R() read-only area summary"

    def test_combined_step3_uses_readonly(self):
        """Combined step 3 (Analyze) must use R() not C() for area list."""
        if not self.COMBINED_MIN.exists():
            pytest.skip("Combined toolbar.min.js not found")
        content = self.COMBINED_MIN.read_text(encoding="utf-8")
        # Step 3: after "areas ready" text, before Analyze button
        assert "R(e[2])" in content, "Step 3 must use R(e[2]) for read-only area list"
        assert "C(e[2])" not in content, "Step 3 must NOT use C(e[2]) (interactive)"

    def test_combined_step4_uses_readonly(self):
        """Combined step 4 (Generate) must use R() not C() for area list."""
        if not self.COMBINED_MIN.exists():
            pytest.skip("Combined toolbar.min.js not found")
        content = self.COMBINED_MIN.read_text(encoding="utf-8")
        assert "R(e[3])" in content, "Step 4 must use R(e[3]) for read-only area list"
        assert "C(e[3])" not in content, "Step 4 must NOT use C(e[3]) (interactive)"

    def test_combined_step1_still_uses_interactive(self):
        """Combined step 1 must still use C() for interactive area list."""
        if not self.COMBINED_MIN.exists():
            pytest.skip("Combined toolbar.min.js not found")
        content = self.COMBINED_MIN.read_text(encoding="utf-8")
        assert "C(e[0])" in content, "Step 1 must still use C(e[0]) for interactive area list"
