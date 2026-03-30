#!/usr/bin/env python3
"""uiux_save_reference.py — FEATURE-052-C

Standalone CLI replacing the save_uiux_reference MCP tool.
Validates UIUX reference data, decodes base64 screenshots, merges
elements into referenced-elements.json, and generates structured
output (HTML/CSS resource files, summarized-uiux-reference.md,
mimic-strategy.md).

Usage:
    python3 uiux_save_reference.py --data-file /tmp/data.json
    python3 uiux_save_reference.py --data '{"version":"3.0",...}'
"""
from __future__ import annotations

import argparse
import base64
import copy
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# --- Bootstrap: add scripts/ to path so _lib can be imported ---
_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import _lib  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
IDEAS_PATH = "x-ipe-docs/ideas"
REQUIRED_FIELDS = ["version", "source_url", "timestamp", "idea_folder"]
DATA_SECTIONS = ["colors", "elements", "design_tokens"]

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_schema(data: dict) -> list[str]:
    """Return list of error messages (empty = valid)."""
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    if not errors:
        has_data = any(
            data.get(s) not in (None, {}, [])
            for s in DATA_SECTIONS
        )
        if not has_data:
            errors.append(
                "At least one data section (colors, elements, design_tokens) "
                "must be non-empty"
            )
    return errors


# ---------------------------------------------------------------------------
# Idea folder
# ---------------------------------------------------------------------------

def resolve_idea_path(project_root: Path, idea_folder: str) -> Path | None:
    """Return Path to idea folder if it exists, else None."""
    idea_path = project_root / IDEAS_PATH / idea_folder
    return idea_path if idea_path.is_dir() else None


# ---------------------------------------------------------------------------
# Screenshot decoding
# ---------------------------------------------------------------------------

def decode_screenshots(data: dict, screenshots_dir: Path) -> tuple[dict, int]:
    """Decode base64:-prefixed screenshots to PNG files.

    Returns (processed_data_copy, count_of_decoded_screenshots).
    """
    result = copy.deepcopy(data)
    count = 0

    for elem in result.get("elements") or []:
        screenshots = elem.get("screenshots")
        if not screenshots:
            continue
        elem_id = elem.get("id", "unknown")
        for key in list(screenshots.keys()):
            val = screenshots[key]
            if val and isinstance(val, str) and val.startswith("base64:"):
                raw_b64 = val[len("base64:"):]
                try:
                    img_data = base64.b64decode(raw_b64)
                    filename = f"{elem_id}-{key}.png"
                    (screenshots_dir / filename).write_bytes(img_data)
                    screenshots[key] = f"screenshots/{filename}"
                    count += 1
                except Exception:
                    screenshots[key] = None

    return result, count


# ---------------------------------------------------------------------------
# Referenced elements persistence
# ---------------------------------------------------------------------------

def save_referenced_elements(data: dict, refs_dir: Path) -> None:
    """Merge incoming data into referenced-elements.json (atomic write)."""
    ref_path = refs_dir / "referenced-elements.json"

    existing: dict = {}
    if ref_path.exists():
        try:
            existing = json.loads(ref_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {}

    existing_areas: dict = {}
    for area in existing.get("areas", []):
        aid = area.get("area_id")
        if aid:
            existing_areas[aid] = area

    for elem in data.get("elements") or []:
        eid = elem.get("id", "unknown")
        area_entry: dict = {
            "area_id": eid,
            "selected_area_bounding_box": elem.get("bounding_box", {}),
            "instruction": elem.get("instruction", ""),
        }
        html_css = elem.get("html_css") or {}
        discovered = html_css.get("discovered_elements") or []
        enriched_elements = []
        for de in discovered:
            enriched = {
                "element_name": de.get("element_name", de.get("tag", "unknown")),
                "purpose_of_the_element": de.get("purpose_of_the_element", ""),
                "relationships_to_other_elements": de.get(
                    "relationships_to_other_elements", []
                ),
                "element_details": de.get("element_details", {
                    "tag": de.get("tag", ""),
                    "text_content": de.get("text", ""),
                    "styles": de.get("styles") or de.get("computedStyles", {}),
                    "resources": de.get("resources", []),
                }),
            }
            enriched_elements.append(enriched)
        if enriched_elements:
            area_entry["elements"] = enriched_elements
        existing_areas[eid] = area_entry

    referenced = {
        "version": data.get("version", "3.0"),
        "source_url": data.get("source_url", existing.get("source_url", "")),
        "timestamp": data.get(
            "timestamp", datetime.now(timezone.utc).isoformat()
        ),
        "areas": list(existing_areas.values()),
        "static_resources": data.get(
            "static_resources", existing.get("static_resources", [])
        ),
    }

    colors = data.get("colors") or existing.get("colors")
    if colors:
        referenced["colors"] = colors

    _lib.atomic_write_json(ref_path, referenced)


# ---------------------------------------------------------------------------
# Area resource files (HTML / CSS)
# ---------------------------------------------------------------------------

def save_area_resources(elements: list, resources_dir: Path) -> int:
    """Write per-element HTML structure and CSS files. Returns file count."""
    count = 0
    for elem in elements:
        html_css = elem.get("html_css")
        if not isinstance(html_css, dict):
            continue
        elem_id = elem.get("id", "unknown")

        outer_html = html_css.get("outer_html")
        if outer_html:
            path = resources_dir / f"{elem_id}-structure.html"
            path.write_text(outer_html, encoding="utf-8")
            count += 1

        computed = html_css.get("computed_styles")
        if computed and isinstance(computed, dict) and computed:
            selector = elem.get("selector", f".{elem_id}")
            lines = [f"/* Computed styles for {selector} */", f"{selector} {{"]
            for prop, val in sorted(computed.items()):
                lines.append(f"  {prop}: {val};")
            lines.append("}")
            path = resources_dir / f"{elem_id}-styles.css"
            path.write_text("\n".join(lines), encoding="utf-8")
            count += 1

    return count


# ---------------------------------------------------------------------------
# Summarized reference markdown
# ---------------------------------------------------------------------------

def generate_summarized_reference(data: dict, refs_dir: Path) -> None:
    """Generate summarized-uiux-reference.md from element data."""
    source_url = data.get("source_url", "")
    timestamp = data.get("timestamp", "")
    colors = data.get("colors") or []
    elements = data.get("elements") or []
    static_resources = data.get("static_resources") or []

    lines = [
        "# UIUX Reference Summary",
        "",
        "## Source",
        f"- URL: {source_url}",
        f"- Captured: {timestamp}",
        "",
    ]

    # Colors
    lines.append("## Colors")
    if colors:
        lines.append("")
        lines.append("| Color | Hex | Role | Source |")
        lines.append("|-------|-----|------|--------|")
        for c in colors:
            hex_val = c.get("hex", "")
            role = c.get("role", "")
            src = c.get("source_selector", "")
            lines.append(f"| {hex_val} | `{hex_val}` | {role} | {src} |")
    else:
        lines.append("")
        lines.append("_No colors captured._")
    lines.append("")

    # Per-element sections
    for elem in elements:
        elem_id = elem.get("id", "unknown")
        tag = elem.get("tag", "")
        selector = elem.get("selector", "")
        bb = elem.get("bounding_box") or {}
        w = bb.get("width", 0)
        h = bb.get("height", 0)

        lines.append(f"## Selected Area: {elem_id}")
        lines.append(f"- Tag: `<{tag}>`")
        lines.append(f"- Selector: `{selector}`")
        lines.append(f"- Dimensions: {w} × {h}")
        lines.append("")

        html_css = elem.get("html_css")
        if isinstance(html_css, dict):
            discovered = html_css.get("discovered_elements") or []
            has_enriched = any(
                isinstance(de, dict) and de.get("element_name")
                for de in discovered
            )

            if has_enriched:
                lines.append("### Elements")
                lines.append("")
                for de in discovered:
                    ename = de.get("element_name", "unknown")
                    purpose = de.get("purpose_of_the_element", "")
                    details = de.get("element_details", {})
                    etag = details.get("tag", de.get("tag", ""))
                    text = details.get("text_content", de.get("text", ""))

                    lines.append(f"#### {ename}")
                    lines.append(f"- Tag: `<{etag}>`")
                    if purpose:
                        lines.append(f"- Purpose: {purpose}")
                    if text:
                        truncated = text[:100] + ("..." if len(text) > 100 else "")
                        lines.append(f'- Content: "{truncated}"')

                    styles = details.get("styles", {})
                    if styles:
                        lines.append("- Key styles:")
                        for prop in [
                            "font-family", "fontFamily", "font-size", "fontSize",
                            "font-weight", "fontWeight", "color", "backgroundColor",
                            "display", "width", "height",
                        ]:
                            val = styles.get(prop)
                            if val:
                                lines.append(f"  - {prop}: `{val}`")

                    resources = details.get("resources", [])
                    if resources:
                        lines.append("- Resources:")
                        for r in resources:
                            rtype = r.get("type", "")
                            rsrc = r.get("src", "")
                            rusage = r.get("usage", "")
                            lines.append(f"  - [{rtype}] {rsrc} ({rusage})")

                    lines.append("")

                # Relationships table
                has_rels = any(
                    de.get("relationships_to_other_elements")
                    for de in discovered if isinstance(de, dict)
                )
                if has_rels:
                    lines.append("### Element Relationships")
                    lines.append("")
                    lines.append(
                        "| Element | Related To | Relationship | Mimic Tips |"
                    )
                    lines.append(
                        "|---------|-----------|--------------|------------|"
                    )
                    for de in discovered:
                        ename = de.get("element_name", "unknown")
                        for rel in de.get(
                            "relationships_to_other_elements", []
                        ):
                            related = rel.get("element", "")
                            rtype = rel.get("relationship", "")
                            tips = rel.get("mimic_tips", "")
                            lines.append(
                                f"| {ename} | {related} | {rtype} | {tips} |"
                            )
                    lines.append("")

                # Reconstruction strategy
                lines.append("### Reconstruction Strategy")
                lines.append("")
                lines.append(
                    "Based on element relationships, reconstruct this area by:"
                )
                lines.append("")
                step_num = 1
                containers = [
                    de for de in discovered
                    if isinstance(de, dict) and any(
                        r.get("relationship") in ("parent", "container")
                        for r in de.get("relationships_to_other_elements", [])
                    )
                ]
                if containers:
                    for c in containers:
                        cname = c.get("element_name", "unknown")
                        ctag = c.get("element_details", {}).get("tag", "")
                        lines.append(
                            f"{step_num}. Create `<{ctag}>` container ({cname})"
                        )
                        step_num += 1
                lines.append(
                    f"{step_num}. Place child elements following the "
                    "relationship graph"
                )
                step_num += 1
                lines.append(
                    f"{step_num}. Apply exact styles from element_details.styles"
                )
                step_num += 1
                lines.append(
                    f"{step_num}. Load static resources (fonts, images, SVGs)"
                )
                lines.append("")
            else:
                # Legacy format fallback: computed_styles only
                cs = html_css.get("computed_styles") or {}
                typo_props = [
                    "font-family", "font-size", "font-weight",
                    "line-height", "color",
                ]
                typo_vals = {p: cs.get(p) for p in typo_props if cs.get(p)}
                if typo_vals:
                    lines.append("### Typography")
                    lines.append("")
                    lines.append("| Property | Value |")
                    lines.append("|----------|-------|")
                    for p, v in typo_vals.items():
                        lines.append(f"| {p} | `{v}` |")
                    lines.append("")

        lines.append("")

    # Static resources
    if static_resources:
        lines.append("## Static Resources")
        lines.append("")
        lines.append("| Type | Source URL | Local Path | Usage |")
        lines.append("|------|-----------|------------|-------|")
        for r in static_resources:
            rtype = r.get("type", "")
            src = r.get("src", "")
            local = r.get("local_path", "")
            usage = r.get("usage", "")
            lines.append(f"| {rtype} | {src} | {local} | {usage} |")
        lines.append("")

    md_path = refs_dir / "summarized-uiux-reference.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Mimic strategy markdown
# ---------------------------------------------------------------------------

def generate_mimic_strategy(data: dict, uiux_dir: Path) -> None:
    """Generate mimic-strategy.md with 6-dimension validation rubric."""
    source_url = data.get("source_url", "")
    elements = data.get("elements") or []

    lines = [
        "# Mimic Strategy",
        "",
        "## Target",
        f"- Source: {source_url}",
    ]

    for elem in elements:
        elem_id = elem.get("id", "unknown")
        tag = elem.get("tag", "")
        bb = elem.get("bounding_box") or {}
        w = bb.get("width", 0)
        h = bb.get("height", 0)
        instruction = elem.get("instruction", "")

        lines.append(f"- Component: {elem_id} (`<{tag}>`)")
        lines.append(f"- Dimensions: {w} × {h}")
        if instruction:
            lines.append(f"- Instruction: {instruction}")

    lines.extend([
        "",
        "## 6-Dimension Validation Rubric",
        "",
        "### 1. Layout",
        "- [ ] Display type matches (flex/grid/block/inline)",
        "- [ ] Positioning matches (static/relative/absolute/fixed)",
        "- [ ] Dimensions within 1px (width, height)",
        "- [ ] Flex/grid properties match (direction, wrap, justify, align)",
        "- [ ] Child element count and order match",
        "- [ ] Overflow behavior matches",
        "",
        "### 2. Typography",
        "- [ ] font-family exact match",
        "- [ ] font-size exact match",
        "- [ ] font-weight exact match",
        "- [ ] line-height exact match",
        "- [ ] letter-spacing match",
        "- [ ] text color exact hex match",
        "- [ ] text-align match",
        "",
        "### 3. Color Palette",
        "- [ ] Background color exact hex match",
        "- [ ] Text colors exact hex match",
        "- [ ] Border colors exact hex match",
        "- [ ] Shadow colors exact hex match",
        "- [ ] Gradient values match (if any)",
        "- [ ] Opacity values match",
        "",
        "### 4. Spacing",
        "- [ ] Margin values within 1px",
        "- [ ] Padding values within 1px",
        "- [ ] Gap values within 1px (flex/grid)",
        "- [ ] Element spacing consistent with original",
        "",
        "### 5. Visual Effects",
        "- [ ] box-shadow values match",
        "- [ ] border values match (width, style, color)",
        "- [ ] border-radius values match",
        "- [ ] background-image/gradient match",
        "- [ ] opacity match",
        "- [ ] transform match (if any)",
        "",
        "### 6. Static Resources",
        "- [ ] Font files loaded (same families available)",
        "- [ ] Icons/SVGs use original source or faithful reproduction",
        "- [ ] Images use original source URLs",
        "- [ ] Background images use original source URLs",
        "- [ ] CSS referenced resources available",
        "",
        "## Validation Criteria",
        "- Target accuracy: 99%",
        "- Screenshot comparison: dimensions within 1%",
        "- Property-level: exact match for colors, fonts; "
        "1px tolerance for spacing",
        "- Static resources: original URLs preserved where possible",
        "- Max iterations: 3 refinement rounds before user approval",
    ])

    strategy_path = uiux_dir / "mimic-strategy.md"
    strategy_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Save UIUX reference data to an idea folder."
    )
    parser.add_argument(
        "--data-file", help="Path to JSON file with UIUX reference data"
    )
    parser.add_argument(
        "--data", help="Inline JSON string with UIUX reference data"
    )
    parser.add_argument(
        "--format", choices=["json", "text"], default="json",
        help="Output format (default: json)"
    )
    args = parser.parse_args()

    # --- Load input ---
    if args.data_file:
        data_path = Path(args.data_file)
        if not data_path.exists():
            _lib.exit_with_error(
                _lib.EXIT_FILE_NOT_FOUND, "FILE_NOT_FOUND",
                f"Data file not found: {args.data_file}"
            )
        try:
            data = json.loads(data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            _lib.exit_with_error(
                _lib.EXIT_VALIDATION_ERROR, "INVALID_JSON",
                f"Invalid JSON in {args.data_file}: {exc}"
            )
    elif args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as exc:
            _lib.exit_with_error(
                _lib.EXIT_VALIDATION_ERROR, "INVALID_JSON",
                f"Invalid JSON: {exc}"
            )
    else:
        _lib.exit_with_error(
            _lib.EXIT_VALIDATION_ERROR, "NO_INPUT",
            "No input data provided. Use --data-file or --data."
        )

    # --- Validate ---
    errors = validate_schema(data)
    if errors:
        _lib.exit_with_error(
            _lib.EXIT_VALIDATION_ERROR, "VALIDATION_ERROR",
            "; ".join(errors)
        )

    # --- Resolve idea folder ---
    project_root = _lib.resolve_project_root()
    idea_path = resolve_idea_path(project_root, data["idea_folder"])
    if idea_path is None:
        _lib.exit_with_error(
            _lib.EXIT_FILE_NOT_FOUND, "IDEA_NOT_FOUND",
            f"Idea folder not found: {data['idea_folder']}"
        )

    # --- Create directory tree ---
    uiux_dir = idea_path / "uiux-references"
    screenshots_dir = uiux_dir / "screenshots"
    refs_dir = uiux_dir / "page-element-references"
    resources_dir = refs_dir / "resources"

    screenshots_dir.mkdir(parents=True, exist_ok=True)
    refs_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)

    # --- Decode screenshots ---
    processed_data, screenshots_saved = decode_screenshots(data, screenshots_dir)

    # --- Save referenced-elements.json ---
    save_referenced_elements(processed_data, refs_dir)

    # --- Generate structured output ---
    resource_files_saved = 0
    elements = data.get("elements") or []
    has_html_css = any(
        isinstance(e.get("html_css"), dict)
        and (
            e["html_css"].get("outer_html")
            or e["html_css"].get("discovered_elements")
        )
        for e in elements
    )
    if has_html_css or data.get("static_resources"):
        resource_files_saved = save_area_resources(elements, resources_dir)
        generate_summarized_reference(data, refs_dir)
        generate_mimic_strategy(data, uiux_dir)

    # --- Output ---
    result: dict = {
        "success": True,
        "referenced_elements_file": (
            "page-element-references/referenced-elements.json"
        ),
        "screenshots_saved": screenshots_saved,
    }
    if resource_files_saved > 0:
        result["resource_files_saved"] = resource_files_saved

    _lib.output_result(result, args.format)


if __name__ == "__main__":
    main()
