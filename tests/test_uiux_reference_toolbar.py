"""Tests for FEATURE-030-B: UIUX Reference Agent Skill & Toolbar.

Tests validate the toolbar IIFE (injected JavaScript) structure,
the agent skill definition (SKILL.md), and the toolbar template reference.
"""

import os
import re
import pytest
from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent

TOOLBAR_JS_PATH = PROJECT_ROOT / "src" / "x_ipe" / "static" / "js" / "injected" / "xipe-toolbar.js"
SKILL_PATH = PROJECT_ROOT / ".github" / "skills" / "x-ipe-tool-uiux-reference" / "SKILL.md"
TEMPLATE_PATH = PROJECT_ROOT / ".github" / "skills" / "x-ipe-tool-uiux-reference" / "references" / "toolbar-template.md"


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def toolbar_js():
    """Load toolbar IIFE source code."""
    assert TOOLBAR_JS_PATH.exists(), f"Toolbar JS not found: {TOOLBAR_JS_PATH}"
    return TOOLBAR_JS_PATH.read_text(encoding="utf-8")


@pytest.fixture
def skill_md():
    """Load skill definition."""
    assert SKILL_PATH.exists(), f"Skill SKILL.md not found: {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


@pytest.fixture
def template_md():
    """Load toolbar template reference."""
    assert TEMPLATE_PATH.exists(), f"Template not found: {TEMPLATE_PATH}"
    return TEMPLATE_PATH.read_text(encoding="utf-8")


# ── Toolbar IIFE: File Existence ───────────────────────────────────────────

class TestToolbarFileExists:
    """Verify toolbar JS file exists at expected location."""

    def test_toolbar_js_file_exists(self):
        """AC-6: Toolbar IIFE source file must exist."""
        assert TOOLBAR_JS_PATH.exists()

    def test_toolbar_js_not_empty(self):
        """Toolbar file must have substantial content."""
        assert TOOLBAR_JS_PATH.stat().st_size > 1000


# ── Toolbar IIFE: Guard & Data Store ──────────────────────────────────────

class TestToolbarGuardAndDataStore:
    """Verify IIFE guard clause and global data structures."""

    def test_iife_structure(self, toolbar_js):
        """Toolbar must be wrapped in an IIFE."""
        stripped = toolbar_js.strip()
        assert stripped.startswith("(()") or stripped.startswith("(function"), \
            "Toolbar must start with IIFE: (() => { or (function() {"
        assert stripped.endswith("})();") or stripped.endswith("})()"), \
            "Toolbar must end with IIFE closure: })();"

    def test_double_injection_guard(self, toolbar_js):
        """AC-14/FR-5: Guard prevents double injection."""
        assert "window.__xipeToolbarInjected" in toolbar_js
        assert re.search(r"if\s*\(\s*window\.__xipeToolbarInjected\s*\)\s*return", toolbar_js), \
            "Must have: if (window.__xipeToolbarInjected) return;"

    def test_data_store_initialization(self, toolbar_js):
        """FR-15: window.__xipeRefData must be initialized with colors and elements arrays."""
        assert "window.__xipeRefData" in toolbar_js
        assert re.search(r"__xipeRefData\s*=\s*\{", toolbar_js), \
            "Must initialize __xipeRefData as object"

    def test_ready_flag_initialization(self, toolbar_js):
        """AC-28/FR-21: window.__xipeRefReady must be initialized to false."""
        assert "window.__xipeRefReady" in toolbar_js
        assert re.search(r"__xipeRefReady\s*=\s*false", toolbar_js), \
            "Must initialize __xipeRefReady = false"


# ── Toolbar IIFE: CSS Namespacing ─────────────────────────────────────────

class TestToolbarCSSNamespacing:
    """Verify CSS class prefix to prevent style conflicts."""

    def test_xipe_prefix_in_styles(self, toolbar_js):
        """NFR/AC-14: All toolbar CSS classes must use .xipe- prefix."""
        # Find style content
        assert ".xipe-" in toolbar_js, "CSS must use .xipe- prefix"

    def test_toolbar_class_name(self, toolbar_js):
        """Root element uses xipe-toolbar class."""
        assert "xipe-toolbar" in toolbar_js

    def test_hamburger_class_name(self, toolbar_js):
        """Hamburger uses xipe-hamburger class."""
        assert "xipe-hamburger" in toolbar_js

    def test_panel_class_name(self, toolbar_js):
        """Panel uses xipe-panel class."""
        assert "xipe-panel" in toolbar_js

    def test_z_index_max(self, toolbar_js):
        """AC-10: Toolbar z-index must be 2147483647 (max 32-bit int)."""
        assert "2147483647" in toolbar_js


# ── Toolbar IIFE: HTML Structure ──────────────────────────────────────────

class TestToolbarHTMLStructure:
    """Verify required HTML elements in the toolbar."""

    def test_hamburger_button_present(self, toolbar_js):
        """AC-6: Hamburger button with X-IPE label."""
        assert "xipe-hamburger" in toolbar_js
        assert "X-IPE" in toolbar_js

    def test_panel_header(self, toolbar_js):
        """AC-7: Panel has 'X-IPE Reference' title."""
        assert "X-IPE Reference" in toolbar_js

    def test_close_button(self, toolbar_js):
        """AC-8: Panel has close button."""
        assert "xipe-close" in toolbar_js or "xipe-panel-close" in toolbar_js

    def test_color_picker_tool(self, toolbar_js):
        """AC-15: Color Picker tool button present."""
        assert "Color Picker" in toolbar_js
        assert 'data-tool="color"' in toolbar_js or "data-tool='color'" in toolbar_js

    def test_element_highlighter_tool(self, toolbar_js):
        """AC-19: Element Highlighter tool button present."""
        assert "Element Highlighter" in toolbar_js
        assert 'data-tool="highlight"' in toolbar_js or "data-tool='highlight'" in toolbar_js

    def test_phase2_tools_disabled(self, toolbar_js):
        """AC-35/FR-24: Phase 2 tools present but disabled."""
        assert "Element Commenter" in toolbar_js
        assert "Asset Extractor" in toolbar_js
        assert "xipe-disabled" in toolbar_js
        assert "disabled" in toolbar_js

    def test_phase_separators(self, toolbar_js):
        """AC-35: Phase 1 and Phase 2 separators."""
        assert "Phase 1" in toolbar_js
        assert "Phase 2" in toolbar_js

    def test_send_button(self, toolbar_js):
        """AC-25: Send References button present."""
        assert "Send References" in toolbar_js
        assert "xipe-send" in toolbar_js

    def test_collected_references_section(self, toolbar_js):
        """AC-18/AC-23/FR-16: Collected References summary section."""
        assert "Collected References" in toolbar_js
        assert "xipe-collected" in toolbar_js

    def test_badge_count_elements(self, toolbar_js):
        """FR-17: Badge count elements for hamburger and tools."""
        assert "xipe-badge" in toolbar_js
        assert "xipe-color-badge" in toolbar_js
        assert "xipe-elem-badge" in toolbar_js

    def test_drag_hint(self, toolbar_js):
        """AC-13/FR-9: Drag hint element."""
        assert "xipe-drag-hint" in toolbar_js
        assert "Drag to move" in toolbar_js or "drag" in toolbar_js.lower()


# ── Toolbar IIFE: Color Picker Logic ──────────────────────────────────────

class TestToolbarColorPicker:
    """Verify Color Picker tool functionality."""

    def test_color_extraction_uses_computed_style(self, toolbar_js):
        """FR-10: Extracts color via getComputedStyle."""
        assert "getComputedStyle" in toolbar_js

    def test_hex_conversion(self, toolbar_js):
        """AC-15: Converts to hex format."""
        assert "toString(16)" in toolbar_js or "toHex" in toolbar_js

    def test_hsl_conversion(self, toolbar_js):
        """AC-15: Converts to HSL format."""
        assert "hsl" in toolbar_js.lower()

    def test_rgb_parsing(self, toolbar_js):
        """AC-15: Parses RGB values."""
        assert re.search(r"rgba?\s*\(", toolbar_js), \
            "Must parse rgba() color strings"

    def test_color_swatch_feedback(self, toolbar_js):
        """AC-17: Shows swatch pill near picked element."""
        assert "swatch" in toolbar_js.lower()

    def test_color_data_structure(self, toolbar_js):
        """AC-16: Color data has required fields: id, hex, rgb, hsl, source_selector."""
        for field in ["id", "hex", "rgb", "hsl", "source_selector"]:
            assert field in toolbar_js, f"Color data must include '{field}' field"


# ── Toolbar IIFE: Element Highlighter Logic ───────────────────────────────

class TestToolbarElementHighlighter:
    """Verify Element Highlighter tool functionality."""

    def test_mousemove_handler(self, toolbar_js):
        """AC-19: Listens for mousemove to show hover overlay."""
        assert "mousemove" in toolbar_js

    def test_overlay_element(self, toolbar_js):
        """AC-19: Creates bounding box overlay element."""
        assert "xipe-highlight-overlay" in toolbar_js or "overlay" in toolbar_js.lower()

    def test_selector_label(self, toolbar_js):
        """AC-19: Shows CSS selector label."""
        assert "xipe-selector-label" in toolbar_js or "selector-label" in toolbar_js

    def test_bounding_box_capture(self, toolbar_js):
        """AC-21/FR-13: Uses getBoundingClientRect for element dimensions."""
        assert "getBoundingClientRect" in toolbar_js

    def test_element_data_structure(self, toolbar_js):
        """AC-22: Element data has required fields: id, selector, tag, bounding_box."""
        for field in ["selector", "tag", "bounding_box"]:
            assert field in toolbar_js, f"Element data must include '{field}' field"


# ── Toolbar IIFE: CSS Selector Generator ──────────────────────────────────

class TestToolbarSelectorGenerator:
    """Verify CSS selector generation logic."""

    def test_selector_generator_exists(self, toolbar_js):
        """FR-26: Selector generator function must exist."""
        assert re.search(r"function\s+generateSelector|generateSelector\s*=", toolbar_js), \
            "Must have generateSelector function"

    def test_nth_child_disambiguation(self, toolbar_js):
        """FR-26: Uses nth-child for sibling disambiguation."""
        assert "nth-child" in toolbar_js

    def test_tag_name_usage(self, toolbar_js):
        """FR-26: Uses tagName for selector parts."""
        assert "tagName" in toolbar_js

    def test_class_list_usage(self, toolbar_js):
        """FR-26: Uses classList for meaningful classes."""
        assert "classList" in toolbar_js


# ── Toolbar IIFE: Panel & Drag Interactions ───────────────────────────────

class TestToolbarInteractions:
    """Verify panel toggle and drag functionality."""

    def test_panel_toggle(self, toolbar_js):
        """AC-7/AC-8: Panel toggling via hamburger click and close button."""
        assert "visible" in toolbar_js, "Panel must toggle 'visible' class"

    def test_drag_functionality(self, toolbar_js):
        """AC-11/FR-8: Drag via mousedown/mousemove/mouseup."""
        assert "mousedown" in toolbar_js
        assert "mousemove" in toolbar_js
        assert "mouseup" in toolbar_js

    def test_tool_selection_mutually_exclusive(self, toolbar_js):
        """FR-25: Only one tool active at a time."""
        assert re.search(r"classList\.remove\(\s*['\"]active['\"]\s*\)", toolbar_js), \
            "Must remove 'active' from all tools before activating one"

    def test_capture_phase_event_listeners(self, toolbar_js):
        """Events registered in capture phase to intercept before page handlers."""
        assert re.search(r"addEventListener\([^)]+,\s*true\s*\)", toolbar_js), \
            "Must use capture phase (true) for click/mousemove listeners"

    def test_toolbar_click_exclusion(self, toolbar_js):
        """Clicks on toolbar itself must be excluded from tool handling."""
        assert re.search(r"closest\(\s*['\"]\.xipe-toolbar['\"]\s*\)", toolbar_js), \
            "Must check .closest('.xipe-toolbar') to exclude toolbar clicks"


# ── Toolbar IIFE: Send References & Callback ──────────────────────────────

class TestToolbarSendReferences:
    """Verify Send References button and callback mechanism."""

    def test_send_button_handler(self, toolbar_js):
        """AC-25: Send button has click handler."""
        assert "xipe-send" in toolbar_js

    def test_ready_flag_set_on_send(self, toolbar_js):
        """AC-28/FR-21: Sets __xipeRefReady = true on send."""
        assert re.search(r"__xipeRefReady\s*=\s*true", toolbar_js)

    def test_empty_data_validation(self, toolbar_js):
        """Edge case: Shows feedback when no data collected."""
        assert re.search(r"(total|length)\s*===?\s*0|No data", toolbar_js), \
            "Must handle case when user sends with 0 items"

    def test_send_button_state_transitions(self, toolbar_js):
        """AC-25/AC-27/FR-20: Three states — idle, sending, success."""
        assert "Sending" in toolbar_js or "sending" in toolbar_js
        assert "Sent to X-IPE" in toolbar_js or "sent" in toolbar_js.lower()
        assert "Send References" in toolbar_js


# ── Toolbar IIFE: Font & Icon Loading ─────────────────────────────────────

class TestToolbarAssetLoading:
    """Verify external font and icon loading."""

    def test_outfit_font_loaded(self, toolbar_js):
        """AC-33: Outfit font for UI text."""
        assert "Outfit" in toolbar_js

    def test_space_mono_font_loaded(self, toolbar_js):
        """AC-33: Space Mono font for selectors/values."""
        assert "Space+Mono" in toolbar_js or "Space Mono" in toolbar_js

    def test_bootstrap_icons_loaded(self, toolbar_js):
        """Icons loaded via Bootstrap Icons CDN."""
        assert "bootstrap-icons" in toolbar_js


# ── Skill SKILL.md: File Existence ────────────────────────────────────────

class TestSkillFileExists:
    """Verify agent skill definition file exists."""

    def test_skill_file_exists(self):
        """Skill SKILL.md must exist at expected location."""
        assert SKILL_PATH.exists()

    def test_skill_file_not_empty(self):
        """Skill file must have substantial content."""
        assert SKILL_PATH.stat().st_size > 500


# ── Skill SKILL.md: Structure ─────────────────────────────────────────────

class TestSkillStructure:
    """Verify skill definition has required sections."""

    def test_skill_frontmatter(self, skill_md):
        """Skill must have YAML frontmatter with name and description."""
        assert skill_md.startswith("---")
        assert "name:" in skill_md
        assert "x-ipe-tool-uiux-reference" in skill_md

    def test_skill_has_purpose(self, skill_md):
        """Skill must describe its purpose."""
        assert "## Purpose" in skill_md or "purpose" in skill_md.lower()

    def test_skill_has_procedure(self, skill_md):
        """Skill must have execution procedure."""
        assert "procedure" in skill_md.lower() or "step" in skill_md.lower()

    def test_skill_references_navigate_page(self, skill_md):
        """AC-1: Skill procedure must reference navigate_page CDP tool."""
        assert "navigate_page" in skill_md

    def test_skill_references_evaluate_script(self, skill_md):
        """AC-6/FR-5: Skill procedure must reference evaluate_script for toolbar injection."""
        assert "evaluate_script" in skill_md

    def test_skill_references_take_screenshot(self, skill_md):
        """AC-21/FR-14: Skill procedure must reference take_screenshot."""
        assert "take_screenshot" in skill_md

    def test_skill_references_save_uiux_reference(self, skill_md):
        """AC-29/FR-23: Skill must call save_uiux_reference MCP tool."""
        assert "save_uiux_reference" in skill_md

    def test_skill_has_auth_flow(self, skill_md):
        """AC-2/FR-3: Skill must describe authentication flow."""
        assert "auth" in skill_md.lower()

    def test_skill_has_polling_mechanism(self, skill_md):
        """AC-28/FR-21: Skill must describe polling for __xipeRefReady."""
        assert "__xipeRefReady" in skill_md or "polling" in skill_md.lower()

    def test_skill_references_toolbar_template(self, skill_md):
        """Skill must reference the toolbar template for injection."""
        assert "toolbar-template" in skill_md or "toolbar" in skill_md.lower()


# ── Toolbar Template: Consistency ─────────────────────────────────────────

class TestToolbarTemplate:
    """Verify toolbar template matches source JS."""

    def test_template_file_exists(self):
        """Template reference file must exist."""
        assert TEMPLATE_PATH.exists()

    def test_template_contains_toolbar_code(self, template_md):
        """Template must contain the toolbar IIFE code."""
        assert "__xipeToolbarInjected" in template_md, \
            "Template must contain the toolbar IIFE guard clause"
        assert "__xipeRefData" in template_md, \
            "Template must contain the data store initialization"

    def test_template_has_code_block(self, template_md):
        """Template must wrap code in a markdown code block."""
        assert "```" in template_md, "Template must contain code block markers"

    def test_template_matches_source(self, toolbar_js, template_md):
        """Template code block content must match toolbar source file."""
        # Extract code from template between ``` markers
        code_blocks = re.findall(r"```(?:javascript|js)?\s*\n(.*?)```", template_md, re.DOTALL)
        assert len(code_blocks) > 0, "Template must have at least one code block"
        # The toolbar source should be contained in the template
        template_code = code_blocks[0].strip()
        source_code = toolbar_js.strip()
        assert template_code == source_code, \
            "Template code block must exactly match xipe-toolbar.js source"


# ── CR-001: Eyedropper Cursor ─────────────────────────────────────────────

class TestToolbarEyedropperCursor:
    """Verify eyedropper/crosshair cursor management (CR-001-A)."""

    def test_eyedropper_cursor_class(self, toolbar_js):
        """AC-36/FR-27: Eyedropper cursor CSS class defined."""
        assert "xipe-cursor-eyedropper" in toolbar_js, \
            "Must define .xipe-cursor-eyedropper class for color picker cursor"

    def test_crosshair_cursor_class(self, toolbar_js):
        """AC-38/FR-28: Crosshair cursor CSS class defined."""
        assert "xipe-cursor-crosshair" in toolbar_js, \
            "Must define .xipe-cursor-crosshair class for element highlighter cursor"

    def test_cursor_applied_to_body(self, toolbar_js):
        """AC-36: Cursor classes are applied to document.body."""
        assert re.search(r"document\.body\.classList\.(add|remove)\(\s*['\"]xipe-cursor", toolbar_js), \
            "Must add/remove cursor classes on document.body"

    def test_cursor_update_function(self, toolbar_js):
        """FR-27/FR-28: updateCursor function exists to manage cursor state."""
        assert re.search(r"function\s+updateCursor|updateCursor\s*=", toolbar_js), \
            "Must have updateCursor function"

    def test_cursor_changes_on_tool_switch(self, toolbar_js):
        """AC-39: Cursor updates when tool selection changes."""
        # updateCursor must be called in the tool selection handler
        assert "updateCursor" in toolbar_js, \
            "Must call updateCursor when tool is selected"

    def test_eyedropper_svg_cursor(self, toolbar_js):
        """AC-36: Custom SVG eyedropper cursor via CSS url() data URI."""
        assert re.search(r"cursor:\s*url\(\s*['\"]?data:image/svg\+xml", toolbar_js), \
            "Must use SVG data URI for eyedropper cursor"


# ── CR-001: Expandable Color List ─────────────────────────────────────────

class TestToolbarColorList:
    """Verify expandable color list in Collected References (CR-001-B)."""

    def test_color_list_container(self, toolbar_js):
        """AC-41/FR-29: Color list container exists in DOM."""
        assert "xipe-color-list" in toolbar_js, \
            "Must have xipe-color-list container element"

    def test_color_entry_class(self, toolbar_js):
        """AC-41/FR-29: Color entries use xipe-color-entry class."""
        assert "xipe-color-entry" in toolbar_js, \
            "Must create elements with xipe-color-entry class"

    def test_color_entry_swatch(self, toolbar_js):
        """AC-41: Each color entry displays a swatch circle."""
        assert "xipe-swatch-dot" in toolbar_js or "swatch-dot" in toolbar_js, \
            "Must include swatch dot in color entry"

    def test_color_entry_hex_value(self, toolbar_js):
        """AC-41: Each color entry displays hex value."""
        assert "xipe-color-hex" in toolbar_js or "color-hex" in toolbar_js, \
            "Must include hex value in color entry"

    def test_color_entry_remove_button(self, toolbar_js):
        """AC-44/FR-33: Each color entry has a remove (×) button."""
        assert "xipe-remove-btn" in toolbar_js, \
            "Must have remove button in entries"

    def test_add_color_entry_function(self, toolbar_js):
        """FR-29: addColorEntry function populates the list."""
        assert re.search(r"function\s+addColorEntry|addColorEntry\s*=", toolbar_js), \
            "Must have addColorEntry function"

    def test_remove_color_updates_data(self, toolbar_js):
        """AC-44/FR-33: Removing color entry removes from __xipeRefData.colors."""
        assert re.search(r"__xipeRefData\.colors\s*=\s*.*filter|colors\.splice", toolbar_js), \
            "Must filter/remove from __xipeRefData.colors on remove"


# ── CR-001: Expandable Element List ───────────────────────────────────────

class TestToolbarElementList:
    """Verify expandable element list in Collected References (CR-001-C)."""

    def test_element_list_container(self, toolbar_js):
        """AC-46/FR-31: Element list container exists in DOM."""
        assert "xipe-elem-list" in toolbar_js, \
            "Must have xipe-elem-list container element"

    def test_element_entry_class(self, toolbar_js):
        """AC-46/FR-31: Element entries use xipe-elem-entry class."""
        assert "xipe-elem-entry" in toolbar_js, \
            "Must create elements with xipe-elem-entry class"

    def test_element_entry_tag_pill(self, toolbar_js):
        """AC-46: Each element entry displays tag name pill."""
        assert "xipe-tag-pill" in toolbar_js or "tag-pill" in toolbar_js, \
            "Must include tag pill in element entry"

    def test_add_element_entry_function(self, toolbar_js):
        """FR-31: addElementEntry function populates the list."""
        assert re.search(r"function\s+addElementEntry|addElementEntry\s*=", toolbar_js), \
            "Must have addElementEntry function"

    def test_remove_element_updates_data(self, toolbar_js):
        """AC-49/FR-33: Removing element entry removes from __xipeRefData.elements."""
        assert re.search(r"__xipeRefData\.elements\s*=\s*.*filter|elements\.splice", toolbar_js), \
            "Must filter/remove from __xipeRefData.elements on remove"


# ── CR-001: Hover-to-Highlight ────────────────────────────────────────────

class TestToolbarHoverHighlight:
    """Verify hover-to-highlight for color/element list entries (CR-001-B/C)."""

    def test_highlight_rose_class(self, toolbar_js):
        """AC-42/FR-30: Rose highlight class for color entry hover."""
        assert "xipe-hover-highlight-rose" in toolbar_js, \
            "Must define xipe-hover-highlight-rose CSS class"

    def test_highlight_accent_class(self, toolbar_js):
        """AC-47/FR-32: Accent highlight class for element entry hover."""
        assert "xipe-hover-highlight-accent" in toolbar_js, \
            "Must define xipe-hover-highlight-accent CSS class"

    def test_highlight_function(self, toolbar_js):
        """FR-30/FR-32: highlightPageElement function exists."""
        assert re.search(r"function\s+highlightPageElement|highlightPageElement\s*=", toolbar_js), \
            "Must have highlightPageElement function"

    def test_remove_highlight_function(self, toolbar_js):
        """AC-43/AC-48: removePageHighlight function exists."""
        assert re.search(r"function\s+removePageHighlight|removePageHighlight\s*=", toolbar_js), \
            "Must have removePageHighlight function"

    def test_mouseenter_event(self, toolbar_js):
        """AC-42/AC-47: Highlight applied on mouseenter."""
        assert "mouseenter" in toolbar_js, \
            "Must listen for mouseenter on list entries"

    def test_mouseleave_event(self, toolbar_js):
        """AC-43/AC-48: Highlight removed on mouseleave."""
        assert "mouseleave" in toolbar_js, \
            "Must listen for mouseleave on list entries"

    def test_highlight_uses_box_shadow(self, toolbar_js):
        """AC-42/AC-47: Highlight applied via box-shadow."""
        assert "box-shadow" in toolbar_js, \
            "Must use box-shadow for hover highlight effect"


# ── CR-001: Collapsible Collected References ──────────────────────────────

class TestToolbarCollapsibleReferences:
    """Verify collapsible Collected References section (CR-001-B/C)."""

    def test_collected_header_toggle(self, toolbar_js):
        """AC-45/FR-34: Collected References header has toggle."""
        assert "xipe-collected-toggle" in toolbar_js or "collected-toggle" in toolbar_js, \
            "Must have toggle element in collected section header"

    def test_chevron_icon(self, toolbar_js):
        """AC-45/FR-34: Chevron icon for collapse/expand state."""
        assert "xipe-chevron" in toolbar_js or "chevron" in toolbar_js, \
            "Must have chevron element for toggle state"

    def test_collapse_toggle_logic(self, toolbar_js):
        """FR-34: Toggle shows/hides color and element lists."""
        assert re.search(r"(display\s*=\s*['\"]none['\"]|style\.display)", toolbar_js), \
            "Must toggle display of lists"


# ── CR-001: Post-Send Reset ──────────────────────────────────────────────

class TestToolbarPostSendReset:
    """Verify post-send reset of all collected data (CR-001-E)."""

    def test_colors_reset_after_send(self, toolbar_js):
        """AC-53/FR-36: Colors array cleared after send."""
        assert re.search(r"__xipeRefData\.colors\s*=\s*\[\s*\]", toolbar_js), \
            "Must reset colors to empty array after send"

    def test_elements_reset_after_send(self, toolbar_js):
        """AC-53/FR-36: Elements array cleared after send."""
        assert re.search(r"__xipeRefData\.elements\s*=\s*\[\s*\]", toolbar_js), \
            "Must reset elements to empty array after send"

    def test_ready_flag_reset(self, toolbar_js):
        """AC-53/FR-36: __xipeRefReady reset to false after send."""
        # There should be both a true and false assignment for __xipeRefReady
        true_matches = re.findall(r"__xipeRefReady\s*=\s*true", toolbar_js)
        false_matches = re.findall(r"__xipeRefReady\s*=\s*false", toolbar_js)
        assert len(true_matches) >= 1, "Must set __xipeRefReady = true on send"
        assert len(false_matches) >= 2, \
            "Must reset __xipeRefReady = false (initial + post-send)"

    def test_dom_lists_cleared(self, toolbar_js):
        """AC-54/FR-36: Color and element list DOM containers cleared after send."""
        assert re.search(r"(innerHTML\s*=\s*['\"]['\"]|textContent\s*=\s*['\"]['\"])", toolbar_js), \
            "Must clear list container innerHTML after send"

    def test_badges_reset_after_send(self, toolbar_js):
        """AC-54/FR-36: Badge counts reset after send."""
        # updateBadges must be called after the reset
        # Check that updateBadges is called in the send success handler
        send_section = toolbar_js[toolbar_js.find("Sent to X-IPE"):]
        assert "updateBadges" in send_section, \
            "Must call updateBadges after resetting data in send handler"


# ── CR-001: Panel Scrollability ──────────────────────────────────────────

class TestToolbarPanelScrollability:
    """Verify panel scrollability for large lists (CR-001-B/C)."""

    def test_panel_max_height(self, toolbar_js):
        """FR-37: Panel has max-height constraint."""
        assert "max-height" in toolbar_js, \
            "Must set max-height on panel for scrollability"

    def test_panel_overflow_scroll(self, toolbar_js):
        """FR-37: Panel has overflow-y scroll."""
        assert re.search(r"overflow-y\s*:\s*(auto|scroll)", toolbar_js), \
            "Must set overflow-y: auto/scroll on panel"

    def test_panel_width_288(self, toolbar_js):
        """FR-7 (updated): Panel width is 288px."""
        assert "288px" in toolbar_js or "288" in toolbar_js, \
            "Panel width must be 288px (updated from 272px)"


# ── CR-001: Screenshot Accuracy (Skill) ──────────────────────────────────

class TestSkillScreenshotAccuracy:
    """Verify bounding-box UID matching strategy in skill (CR-001-D)."""

    def test_skill_mentions_bounding_box(self, skill_md):
        """AC-50/FR-35: Skill describes bounding box matching."""
        assert "bounding" in skill_md.lower() or "bounding_box" in skill_md, \
            "Skill must describe bounding box matching for screenshot accuracy"

    def test_skill_mentions_take_snapshot(self, skill_md):
        """AC-50/FR-35: Skill uses take_snapshot for a11y tree."""
        assert "take_snapshot" in skill_md, \
            "Skill must reference take_snapshot for UID matching"
