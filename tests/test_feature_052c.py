"""Tests for FEATURE-052-C: UIUX Reference Script (uiux_save_reference.py).

Covers all 45 acceptance criteria across 9 AC groups.
"""
from __future__ import annotations

import base64
import io
import json
import os
import sys
import textwrap
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import pytest

# ---------------------------------------------------------------------------
# Bootstrap: ensure scripts/ is importable
# ---------------------------------------------------------------------------
SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent
    / ".github" / "skills" / "x-ipe-tool-x-ipe-app-interactor" / "scripts"
)
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import uiux_save_reference as uiux  # noqa: E402
import _lib  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_project(tmp_path):
    """Create a minimal project tree with an idea folder."""
    ideas_dir = tmp_path / "x-ipe-docs" / "ideas" / "036. Test Idea"
    ideas_dir.mkdir(parents=True)
    return tmp_path


def _make_data(**overrides) -> dict:
    """Create minimal valid UIUX reference data."""
    base = {
        "version": "3.0",
        "source_url": "https://example.com",
        "timestamp": "2026-03-30T07:00:00Z",
        "idea_folder": "036. Test Idea",
        "colors": [{"hex": "#1a1a2e", "role": "primary", "source_selector": "body"}],
    }
    base.update(overrides)
    return base


def _make_element(elem_id="area-1", **overrides) -> dict:
    """Create a test element with optional enrichment."""
    elem = {
        "id": elem_id,
        "tag": "section",
        "selector": ".hero",
        "bounding_box": {"x": 0, "y": 0, "width": 800, "height": 600},
        "instruction": "Capture hero area",
    }
    elem.update(overrides)
    return elem


def _run_script(args: list[str], cwd: Path) -> tuple[int, dict | str]:
    """Run the script's main() with patched argv and CWD. Returns (exit_code, parsed_output)."""
    with mock.patch.object(sys, "argv", ["uiux_save_reference.py"] + args):
        with mock.patch.object(_lib.Path, "cwd", return_value=cwd):
            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    uiux.main()
                raw = buf.getvalue().strip()
                try:
                    return 0, json.loads(raw)
                except json.JSONDecodeError:
                    return 0, raw
            except SystemExit as exc:
                raw = buf.getvalue().strip()
                code = exc.code if exc.code is not None else 0
                try:
                    return code, json.loads(raw)
                except (json.JSONDecodeError, ValueError):
                    return code, raw


# ===========================================================================
# AC-052C-01: Input Validation & CLI Interface
# ===========================================================================

class TestInputValidation:
    """AC-052C-01a through 01h."""

    def test_data_file_json(self, tmp_project):
        """AC-052C-01a: --data-file reads JSON from file."""
        data = _make_data()
        data_file = tmp_project / "input.json"
        data_file.write_text(json.dumps(data))
        code, out = _run_script(["--data-file", str(data_file)], tmp_project)
        assert code == 0
        assert out["success"] is True

    def test_inline_data(self, tmp_project):
        """AC-052C-01b: --data parses inline JSON."""
        data = _make_data()
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 0
        assert out["success"] is True

    def test_no_input_exits_1(self, tmp_project):
        """AC-052C-01c: No --data-file or --data → exit 1."""
        code, out = _run_script([], tmp_project)
        assert code == 1

    def test_data_file_takes_precedence(self, tmp_project):
        """AC-052C-01d: --data-file takes precedence over --data."""
        file_data = _make_data(source_url="https://from-file.com")
        inline_data = _make_data(source_url="https://from-inline.com")
        data_file = tmp_project / "input.json"
        data_file.write_text(json.dumps(file_data))
        code, out = _run_script(
            ["--data-file", str(data_file), "--data", json.dumps(inline_data)],
            tmp_project,
        )
        assert code == 0
        # Verify the file data was used
        refs = tmp_project / "x-ipe-docs" / "ideas" / "036. Test Idea" / "uiux-references" / "page-element-references" / "referenced-elements.json"
        ref_data = json.loads(refs.read_text())
        assert ref_data["source_url"] == "https://from-file.com"

    def test_missing_required_field(self, tmp_project):
        """AC-052C-01e: Missing required field → exit 1."""
        data = _make_data()
        del data["source_url"]
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 1
        assert "Missing required field" in out.get("message", "")

    def test_no_data_sections(self, tmp_project):
        """AC-052C-01f: All data sections empty → exit 1."""
        data = _make_data(colors=[], elements=[], design_tokens={})
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 1
        assert "At least one data section" in out.get("message", "")

    def test_missing_data_file(self, tmp_project):
        """AC-052C-01g: Nonexistent --data-file → exit 2."""
        code, out = _run_script(
            ["--data-file", "/nonexistent/file.json"], tmp_project
        )
        assert code == 2

    def test_malformed_json_file(self, tmp_project):
        """AC-052C-01h: Malformed JSON → exit 1."""
        bad_file = tmp_project / "bad.json"
        bad_file.write_text("{invalid json")
        code, out = _run_script(["--data-file", str(bad_file)], tmp_project)
        assert code == 1


# ===========================================================================
# AC-052C-02: Idea Folder Resolution
# ===========================================================================

class TestIdeaFolder:
    """AC-052C-02a through 02c."""

    def test_resolves_existing_folder(self, tmp_project):
        """AC-052C-02a: Valid idea_folder resolves correctly."""
        data = _make_data()
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 0
        idea_dir = tmp_project / "x-ipe-docs" / "ideas" / "036. Test Idea"
        assert idea_dir.is_dir()

    def test_nonexistent_folder_exits_2(self, tmp_project):
        """AC-052C-02b: Nonexistent idea folder → exit 2."""
        data = _make_data(idea_folder="999. NonExistent")
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 2
        assert "Idea folder not found" in out.get("message", "")

    def test_creates_subdirectories(self, tmp_project):
        """AC-052C-02c: Creates uiux-references subdirectories."""
        data = _make_data()
        _run_script(["--data", json.dumps(data)], tmp_project)
        base = tmp_project / "x-ipe-docs" / "ideas" / "036. Test Idea" / "uiux-references"
        assert (base / "screenshots").is_dir()
        assert (base / "page-element-references").is_dir()
        assert (base / "page-element-references" / "resources").is_dir()


# ===========================================================================
# AC-052C-03: Screenshot Decoding
# ===========================================================================

class TestScreenshotDecoding:
    """AC-052C-03a through 03e."""

    def _b64_png(self) -> str:
        """Return a minimal base64-encoded PNG."""
        # Minimal 1x1 transparent PNG
        raw = base64.b64encode(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
            b"\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        ).decode()
        return f"base64:{raw}"

    def test_decode_base64_screenshot(self, tmp_project):
        """AC-052C-03a: base64: screenshots decoded to PNG files."""
        elem = _make_element(screenshots={"full_page": self._b64_png()})
        data = _make_data(elements=[elem], colors=[])
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 0
        assert out["screenshots_saved"] == 1
        ss_dir = tmp_project / "x-ipe-docs" / "ideas" / "036. Test Idea" / "uiux-references" / "screenshots"
        assert (ss_dir / "area-1-full_page.png").exists()

    def test_multiple_screenshot_keys(self, tmp_project):
        """AC-052C-03b: Multiple screenshot keys each decoded."""
        elem = _make_element(screenshots={
            "full_page": self._b64_png(),
            "element_crop": self._b64_png(),
        })
        data = _make_data(elements=[elem], colors=[])
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 0
        assert out["screenshots_saved"] == 2

    def test_non_base64_unchanged(self, tmp_project):
        """AC-052C-03c: Non-base64 values left unchanged."""
        elem = _make_element(screenshots={"full_page": "screenshots/existing.png"})
        data = _make_data(elements=[elem], colors=[])
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 0
        assert out["screenshots_saved"] == 0

    def test_invalid_base64_sets_none(self, tmp_project):
        """AC-052C-03d: Invalid base64 → value set to None, no crash."""
        elem = _make_element(screenshots={"full_page": "base64:!!!invalid!!!"})
        data = _make_data(elements=[elem], colors=[])
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 0

    def test_no_screenshots(self, tmp_project):
        """AC-052C-03e: No elements/screenshots → no files created."""
        data = _make_data()
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 0
        assert out["screenshots_saved"] == 0


# ===========================================================================
# AC-052C-04: Referenced Elements Persistence
# ===========================================================================

class TestReferencedElements:
    """AC-052C-04a through 04h."""

    def _ref_path(self, tmp_project):
        return (
            tmp_project / "x-ipe-docs" / "ideas" / "036. Test Idea"
            / "uiux-references" / "page-element-references"
            / "referenced-elements.json"
        )

    def test_new_file_created(self, tmp_project):
        """AC-052C-04a: New referenced-elements.json with correct fields."""
        elem = _make_element()
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        ref = json.loads(self._ref_path(tmp_project).read_text())
        assert "version" in ref
        assert "source_url" in ref
        assert "timestamp" in ref
        assert "areas" in ref
        assert len(ref["areas"]) == 1

    def test_incremental_merge(self, tmp_project):
        """AC-052C-04b: New area merged with existing."""
        elem1 = _make_element(elem_id="area-1")
        data1 = _make_data(elements=[elem1])
        _run_script(["--data", json.dumps(data1)], tmp_project)

        elem2 = _make_element(elem_id="area-2")
        data2 = _make_data(elements=[elem2])
        _run_script(["--data", json.dumps(data2)], tmp_project)

        ref = json.loads(self._ref_path(tmp_project).read_text())
        area_ids = {a["area_id"] for a in ref["areas"]}
        assert area_ids == {"area-1", "area-2"}

    def test_same_area_overwrites(self, tmp_project):
        """AC-052C-04c: Same area_id overwrites existing data."""
        elem1 = _make_element(instruction="First capture")
        data1 = _make_data(elements=[elem1])
        _run_script(["--data", json.dumps(data1)], tmp_project)

        elem2 = _make_element(instruction="Second capture")
        data2 = _make_data(elements=[elem2])
        _run_script(["--data", json.dumps(data2)], tmp_project)

        ref = json.loads(self._ref_path(tmp_project).read_text())
        assert ref["areas"][0]["instruction"] == "Second capture"

    def test_enriched_elements_format(self, tmp_project):
        """AC-052C-04d: discovered_elements converted to enriched format."""
        elem = _make_element(html_css={
            "discovered_elements": [{
                "element_name": "heading",
                "purpose_of_the_element": "Main title",
                "tag": "h1",
                "text": "Hello",
                "relationships_to_other_elements": [],
            }]
        })
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)

        ref = json.loads(self._ref_path(tmp_project).read_text())
        area = ref["areas"][0]
        assert "elements" in area
        assert area["elements"][0]["element_name"] == "heading"
        assert area["elements"][0]["purpose_of_the_element"] == "Main title"

    def test_new_colors_replace_existing(self, tmp_project):
        """AC-052C-04e: New colors replace existing."""
        data1 = _make_data(colors=[{"hex": "#000"}], elements=[_make_element()])
        _run_script(["--data", json.dumps(data1)], tmp_project)

        data2 = _make_data(colors=[{"hex": "#fff"}], elements=[_make_element()])
        _run_script(["--data", json.dumps(data2)], tmp_project)

        ref = json.loads(self._ref_path(tmp_project).read_text())
        assert ref["colors"] == [{"hex": "#fff"}]

    def test_absent_colors_preserved(self, tmp_project):
        """AC-052C-04f: Missing new colors → existing preserved."""
        data1 = _make_data(colors=[{"hex": "#000"}], elements=[_make_element()])
        _run_script(["--data", json.dumps(data1)], tmp_project)

        data2 = _make_data(elements=[_make_element(elem_id="area-2")])
        del data2["colors"]
        _run_script(["--data", json.dumps(data2)], tmp_project)

        ref = json.loads(self._ref_path(tmp_project).read_text())
        assert ref["colors"] == [{"hex": "#000"}]

    def test_static_resources_included(self, tmp_project):
        """AC-052C-04g: static_resources persisted."""
        data = _make_data(
            elements=[_make_element()],
            static_resources=[{"type": "font", "src": "https://fonts.com/inter.woff2", "usage": "primary"}],
        )
        _run_script(["--data", json.dumps(data)], tmp_project)

        ref = json.loads(self._ref_path(tmp_project).read_text())
        assert len(ref["static_resources"]) == 1
        assert ref["static_resources"][0]["type"] == "font"

    def test_atomic_write(self, tmp_project):
        """AC-052C-04h: Write is atomic (uses _lib.atomic_write_json)."""
        # Verify by checking the function is called (patching)
        elem = _make_element()
        data = _make_data(elements=[elem])
        with mock.patch.object(_lib, "atomic_write_json", wraps=_lib.atomic_write_json) as m:
            with mock.patch.object(_lib.Path, "cwd", return_value=tmp_project):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    with mock.patch.object(sys, "argv", [
                        "uiux_save_reference.py", "--data", json.dumps(data)
                    ]):
                        uiux.main()
                assert m.called


# ===========================================================================
# AC-052C-05: Area Resource Generation
# ===========================================================================

class TestAreaResources:
    """AC-052C-05a through 05e."""

    def _resources_dir(self, tmp_project):
        return (
            tmp_project / "x-ipe-docs" / "ideas" / "036. Test Idea"
            / "uiux-references" / "page-element-references" / "resources"
        )

    def test_html_structure_file(self, tmp_project):
        """AC-052C-05a: outer_html → {id}-structure.html."""
        elem = _make_element(html_css={
            "outer_html": "<section>Hello</section>",
            "computed_styles": {},
        })
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        html_file = self._resources_dir(tmp_project) / "area-1-structure.html"
        assert html_file.exists()
        assert "<section>Hello</section>" in html_file.read_text()

    def test_css_styles_file(self, tmp_project):
        """AC-052C-05b: computed_styles → {id}-styles.css with sorted props."""
        elem = _make_element(html_css={
            "outer_html": "<div/>",
            "computed_styles": {"color": "red", "display": "flex", "background": "blue"},
        })
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        css_file = self._resources_dir(tmp_project) / "area-1-styles.css"
        assert css_file.exists()
        css = css_file.read_text()
        assert "background: blue;" in css
        assert "color: red;" in css
        assert "display: flex;" in css

    def test_css_uses_element_selector(self, tmp_project):
        """AC-052C-05c: CSS uses element's selector field."""
        elem = _make_element(
            selector=".hero-section",
            html_css={
                "outer_html": "<div/>",
                "computed_styles": {"color": "red"},
            },
        )
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        css_file = self._resources_dir(tmp_project) / "area-1-styles.css"
        css = css_file.read_text()
        assert ".hero-section {" in css

    def test_no_html_css_no_resources(self, tmp_project):
        """AC-052C-05d: No html_css → no resource files."""
        elem = _make_element()  # No html_css
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        res_dir = self._resources_dir(tmp_project)
        resource_files = list(res_dir.glob("*")) if res_dir.exists() else []
        assert len(resource_files) == 0

    def test_resource_files_counted(self, tmp_project):
        """AC-052C-05e: resource_files_saved count in output."""
        elem = _make_element(html_css={
            "outer_html": "<div/>",
            "computed_styles": {"color": "red"},
        })
        data = _make_data(elements=[elem])
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 0
        assert out["resource_files_saved"] == 2  # 1 HTML + 1 CSS


# ===========================================================================
# AC-052C-06: Summarized Reference Markdown
# ===========================================================================

class TestSummarizedReference:
    """AC-052C-06a through 06f."""

    def _md_path(self, tmp_project):
        return (
            tmp_project / "x-ipe-docs" / "ideas" / "036. Test Idea"
            / "uiux-references" / "page-element-references"
            / "summarized-uiux-reference.md"
        )

    def test_colors_table(self, tmp_project):
        """AC-052C-06a: Colors table with Hex/Role/Source columns."""
        elem = _make_element(html_css={"outer_html": "<div/>"})
        data = _make_data(
            elements=[elem],
            colors=[{"hex": "#1a1a2e", "role": "primary", "source_selector": "body"}],
        )
        _run_script(["--data", json.dumps(data)], tmp_project)
        md = self._md_path(tmp_project).read_text()
        assert "| Color | Hex | Role | Source |" in md
        assert "#1a1a2e" in md
        assert "primary" in md

    def test_no_colors_message(self, tmp_project):
        """AC-052C-06b: No colors → shows fallback message."""
        elem = _make_element(html_css={"outer_html": "<div/>"})
        data = _make_data(elements=[elem], colors=[])
        _run_script(["--data", json.dumps(data)], tmp_project)
        md = self._md_path(tmp_project).read_text()
        assert "_No colors captured._" in md

    def test_enriched_elements_sections(self, tmp_project):
        """AC-052C-06c: Enriched elements produce detailed sections."""
        elem = _make_element(html_css={
            "outer_html": "<section/>",
            "discovered_elements": [{
                "element_name": "hero-heading",
                "purpose_of_the_element": "Main brand heading",
                "element_details": {
                    "tag": "h1",
                    "text_content": "Welcome",
                    "styles": {"font-family": "Inter", "color": "#000"},
                    "resources": [],
                },
                "relationships_to_other_elements": [],
            }],
        })
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        md = self._md_path(tmp_project).read_text()
        assert "#### hero-heading" in md
        assert "Main brand heading" in md
        assert "Inter" in md

    def test_relationships_and_reconstruction(self, tmp_project):
        """AC-052C-06d: Relationships table + reconstruction strategy generated."""
        elem = _make_element(html_css={
            "outer_html": "<section/>",
            "discovered_elements": [{
                "element_name": "container",
                "purpose_of_the_element": "Wrapper",
                "element_details": {"tag": "div"},
                "relationships_to_other_elements": [
                    {"element": "heading", "relationship": "parent", "mimic_tips": "flex container"}
                ],
            }],
        })
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        md = self._md_path(tmp_project).read_text()
        assert "### Element Relationships" in md
        assert "### Reconstruction Strategy" in md
        assert "container" in md

    def test_legacy_typography_fallback(self, tmp_project):
        """AC-052C-06e: Legacy format → Typography table."""
        elem = _make_element(html_css={
            "outer_html": "<div/>",
            "computed_styles": {
                "font-family": "Arial",
                "font-size": "16px",
                "color": "#333",
            },
        })
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        md = self._md_path(tmp_project).read_text()
        assert "### Typography" in md
        assert "Arial" in md

    def test_static_resources_table(self, tmp_project):
        """AC-052C-06f: Static resources table appended."""
        elem = _make_element(html_css={"outer_html": "<div/>"})
        data = _make_data(
            elements=[elem],
            static_resources=[{
                "type": "font",
                "src": "https://fonts.com/inter.woff2",
                "local_path": "resources/inter.woff2",
                "usage": "Primary font",
            }],
        )
        _run_script(["--data", json.dumps(data)], tmp_project)
        md = self._md_path(tmp_project).read_text()
        assert "## Static Resources" in md
        assert "inter.woff2" in md


# ===========================================================================
# AC-052C-07: Mimic Strategy Generation
# ===========================================================================

class TestMimicStrategy:
    """AC-052C-07a through 07c."""

    def _strategy_path(self, tmp_project):
        return (
            tmp_project / "x-ipe-docs" / "ideas" / "036. Test Idea"
            / "uiux-references" / "mimic-strategy.md"
        )

    def test_target_section(self, tmp_project):
        """AC-052C-07a: Target section with component/dimensions/instruction."""
        elem = _make_element(
            html_css={"outer_html": "<div/>"},
            instruction="Capture hero area",
        )
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        md = self._strategy_path(tmp_project).read_text()
        assert "## Target" in md
        assert "area-1" in md
        assert "800" in md
        assert "Capture hero area" in md

    def test_six_dimension_rubric(self, tmp_project):
        """AC-052C-07b: 6-dimension validation rubric present."""
        elem = _make_element(html_css={"outer_html": "<div/>"})
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        md = self._strategy_path(tmp_project).read_text()
        for dim in [
            "### 1. Layout",
            "### 2. Typography",
            "### 3. Color Palette",
            "### 4. Spacing",
            "### 5. Visual Effects",
            "### 6. Static Resources",
        ]:
            assert dim in md, f"Missing dimension: {dim}"

    def test_validation_criteria(self, tmp_project):
        """AC-052C-07c: Validation criteria section present."""
        elem = _make_element(html_css={"outer_html": "<div/>"})
        data = _make_data(elements=[elem])
        _run_script(["--data", json.dumps(data)], tmp_project)
        md = self._strategy_path(tmp_project).read_text()
        assert "## Validation Criteria" in md
        assert "99%" in md
        assert "1px tolerance" in md


# ===========================================================================
# AC-052C-08: Output Compatibility
# ===========================================================================

class TestOutputCompatibility:
    """AC-052C-08a through 08d."""

    def test_success_output_structure(self, tmp_project):
        """AC-052C-08a: Success JSON has required fields."""
        data = _make_data()
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 0
        assert out["success"] is True
        assert "referenced_elements_file" in out
        assert "screenshots_saved" in out

    def test_resource_files_count(self, tmp_project):
        """AC-052C-08b: resource_files_saved included when > 0."""
        elem = _make_element(html_css={
            "outer_html": "<div/>",
            "computed_styles": {"color": "red"},
        })
        data = _make_data(elements=[elem])
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert "resource_files_saved" in out
        assert out["resource_files_saved"] > 0

    def test_text_format(self, tmp_project):
        """AC-052C-08c: --format text gives key=value output."""
        data = _make_data()
        code, out = _run_script(
            ["--data", json.dumps(data), "--format", "text"], tmp_project
        )
        assert code == 0
        assert isinstance(out, str)
        assert "success" in out

    def test_error_output_structure(self, tmp_project):
        """AC-052C-08d: Error JSON has success/error/message."""
        data = _make_data(idea_folder="999. NonExistent")
        code, out = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 2
        assert out["success"] is False
        assert "error" in out
        assert "message" in out


# ===========================================================================
# AC-052C-09: Exit Codes & Shared Utilities
# ===========================================================================

class TestExitCodes:
    """AC-052C-09a through 09e."""

    def test_success_exit_0(self, tmp_project):
        """AC-052C-09a: Successful execution exits 0."""
        data = _make_data()
        code, _ = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 0

    def test_validation_error_exit_1(self, tmp_project):
        """AC-052C-09b: Validation error exits 1."""
        data = _make_data()
        del data["version"]
        code, _ = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 1

    def test_not_found_exit_2(self, tmp_project):
        """AC-052C-09c: Missing idea folder exits 2."""
        data = _make_data(idea_folder="999. NonExistent")
        code, _ = _run_script(["--data", json.dumps(data)], tmp_project)
        assert code == 2

    def test_imports_from_lib(self):
        """AC-052C-09d: Script imports from _lib."""
        assert hasattr(uiux, '_lib') or 'import _lib' in open(
            str(SCRIPTS_DIR / "uiux_save_reference.py")
        ).read()

    def test_stdlib_only(self):
        """AC-052C-09e: Only stdlib + _lib dependencies."""
        source = (SCRIPTS_DIR / "uiux_save_reference.py").read_text()
        # Check no third-party imports (only stdlib + _lib)
        import_lines = [
            line.strip() for line in source.split("\n")
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]
        allowed_modules = {
            "__future__", "argparse", "base64", "copy", "json", "os", "sys",
            "tempfile", "pathlib", "datetime", "_lib",
        }
        for line in import_lines:
            # Extract module name
            if line.startswith("from "):
                mod = line.split()[1].split(".")[0]
            else:
                mod = line.split()[1].split(".")[0]
            assert mod in allowed_modules, f"Unexpected import: {line}"
