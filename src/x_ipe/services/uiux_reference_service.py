"""
UiuxReferenceService (FEATURE-033)

Validates, decodes, and persists UIUX reference data to idea folders.
Handles base64 screenshot decoding, atomic writes,
referenced-elements.json maintenance, and structured output generation
(page-element-references, summarized-uiux-reference.md, mimic-strategy.md).
"""
import base64
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from x_ipe.tracing import x_ipe_tracing


class UiuxReferenceService:
    IDEAS_PATH = "x-ipe-docs/ideas"
    REQUIRED_FIELDS = ["version", "source_url", "timestamp", "idea_folder"]
    DATA_SECTIONS = ["colors", "elements", "design_tokens"]

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.ideas_root = self.project_root / self.IDEAS_PATH

    @x_ipe_tracing()
    def save_reference(self, data: dict) -> dict:
        """Main entry point — validate, decode, save referenced-elements.json, generate structured output."""
        errors = self._validate_schema(data)
        if errors:
            return {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "; ".join(errors),
            }

        idea_folder = data["idea_folder"]
        idea_path = self._resolve_idea_path(idea_folder)
        if idea_path is None:
            return {
                "success": False,
                "error": "IDEA_NOT_FOUND",
                "message": f"Idea folder not found: {idea_folder}",
            }

        uiux_dir = idea_path / "uiux-references"
        screenshots_dir = uiux_dir / "screenshots"
        refs_dir = uiux_dir / "page-element-references"

        screenshots_dir.mkdir(parents=True, exist_ok=True)
        refs_dir.mkdir(parents=True, exist_ok=True)

        processed_data = self._decode_screenshots(data, screenshots_dir)

        screenshots_saved = self._count_decoded_screenshots(data, processed_data)

        # Write referenced-elements.json (single source of truth)
        self._save_referenced_elements(processed_data, refs_dir)

        # Generate structured output if areas have html_css data
        resource_files_saved = self._generate_structured_output(
            data, uiux_dir
        )

        result = {
            "success": True,
            "referenced_elements_file": "page-element-references/referenced-elements.json",
            "screenshots_saved": screenshots_saved,
        }
        if resource_files_saved > 0:
            result["resource_files_saved"] = resource_files_saved
        return result

    def _validate_schema(self, data: dict) -> list:
        """Validate reference data schema. Returns list of error messages."""
        errors = []
        for field in self.REQUIRED_FIELDS:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")

        if not errors:
            has_data = False
            for section in self.DATA_SECTIONS:
                val = data.get(section)
                if val is not None and val != {} and val != []:
                    has_data = True
                    break
            if not has_data:
                errors.append(
                    "At least one data section (colors, elements, design_tokens) "
                    "must be non-empty"
                )

        return errors

    def _resolve_idea_path(self, idea_folder: str):
        """Resolve idea folder path. Returns Path or None if not found."""
        idea_path = self.ideas_root / idea_folder
        if idea_path.is_dir():
            return idea_path
        return None

    def _save_referenced_elements(self, data: dict, refs_dir: Path) -> None:
        """Build and write referenced-elements.json (single source of truth).

        Merges incoming data into any existing referenced-elements.json,
        keyed by element id to support incremental updates.
        """
        ref_path = refs_dir / "referenced-elements.json"

        # Load existing data if present
        existing = {}
        if ref_path.exists():
            try:
                existing = json.loads(ref_path.read_text())
            except (json.JSONDecodeError, OSError):
                existing = {}

        # Build areas dict keyed by element id for merge
        existing_areas = {}
        for area in existing.get("areas", []):
            aid = area.get("area_id")
            if aid:
                existing_areas[aid] = area

        # Convert incoming elements to area format
        for elem in data.get("elements") or []:
            eid = elem.get("id", "unknown")
            area_entry = {
                "area_id": eid,
                "selected_area_bounding_box": elem.get("bounding_box", {}),
                "instruction": elem.get("instruction", ""),
            }
            # If element has enriched data (v3.0 format), preserve it
            html_css = elem.get("html_css") or {}
            discovered = html_css.get("discovered_elements") or []

            # Convert discovered elements to enriched format if present
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

        # Build final structure
        referenced = {
            "version": data.get("version", "3.0"),
            "source_url": data.get("source_url", existing.get("source_url", "")),
            "timestamp": data.get("timestamp",
                                  datetime.now(timezone.utc).isoformat()),
            "areas": list(existing_areas.values()),
            "static_resources": data.get("static_resources",
                                         existing.get("static_resources", [])),
        }

        # Preserve colors if present
        colors = data.get("colors") or existing.get("colors")
        if colors:
            referenced["colors"] = colors

        # Atomic write
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=str(refs_dir), suffix=".tmp"
        )
        try:
            with os.fdopen(tmp_fd, "w") as f:
                json.dump(referenced, f, indent=2)
            os.rename(tmp_path, str(ref_path))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def _decode_screenshots(self, data: dict, screenshots_dir: Path) -> dict:
        """Find base64:-prefixed values in elements, decode to files, replace with paths."""
        import copy
        result = copy.deepcopy(data)

        elements = result.get("elements")
        if not elements:
            return result

        for elem in elements:
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
                        filepath = screenshots_dir / filename
                        filepath.write_bytes(img_data)
                        screenshots[key] = f"screenshots/{filename}"
                    except Exception:
                        screenshots[key] = None

        return result

    def _count_decoded_screenshots(self, original: dict, processed: dict) -> int:
        """Count how many base64 screenshots were decoded."""
        count = 0
        orig_elems = original.get("elements") or []
        for elem in orig_elems:
            screenshots = elem.get("screenshots") or {}
            for val in screenshots.values():
                if val and isinstance(val, str) and val.startswith("base64:"):
                    count += 1
        return count

    # -----------------------------------------------------------------------
    # Structured Output Generation
    # -----------------------------------------------------------------------

    def _generate_structured_output(self, data: dict, uiux_dir: Path) -> int:
        """Generate page-element-references, resource files, summary, and strategy.

        Returns the number of resource files saved.
        """
        elements = data.get("elements") or []
        has_html_css = any(
            isinstance(e.get("html_css"), dict) and (
                e["html_css"].get("outer_html") or
                e["html_css"].get("discovered_elements")
            )
            for e in elements
        )
        if not has_html_css and not data.get("static_resources"):
            return 0

        refs_dir = uiux_dir / "page-element-references"
        resources_dir = refs_dir / "resources"
        refs_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(parents=True, exist_ok=True)

        file_count = self._save_area_resources(elements, resources_dir)
        self._generate_summarized_reference(data, refs_dir)
        self._generate_mimic_strategy(data, uiux_dir)

        return file_count

    def _save_area_resources(self, elements: list, resources_dir: Path) -> int:
        """Save HTML/CSS snippet files per area. Returns count of files saved."""
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

    def _generate_summarized_reference(self, data: dict, refs_dir: Path) -> None:
        """Generate relationship-aware summarized-uiux-reference.md from data."""
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

        # Colors section
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

        # Selected area references with enriched element data
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

            # Enriched elements with relationships
            html_css = elem.get("html_css")
            if isinstance(html_css, dict):
                discovered = html_css.get("discovered_elements") or []

                # Check if elements have enriched format (element_name, purpose, relationships)
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
                            lines.append(
                                f"- Content: \"{text[:100]}{'...' if len(text) > 100 else ''}\""
                            )

                        # Styles
                        styles = details.get("styles", {})
                        if styles:
                            lines.append("- Key styles:")
                            for prop in ["font-family", "fontFamily", "font-size", "fontSize",
                                         "font-weight", "fontWeight", "color", "backgroundColor",
                                         "display", "width", "height"]:
                                val = styles.get(prop)
                                if val:
                                    lines.append(f"  - {prop}: `{val}`")

                        # Resources
                        resources = details.get("resources", [])
                        if resources:
                            lines.append("- Resources:")
                            for r in resources:
                                rtype = r.get("type", "")
                                rsrc = r.get("src", "")
                                rusage = r.get("usage", "")
                                lines.append(f"  - [{rtype}] {rsrc} ({rusage})")

                        lines.append("")

                    # Relationships summary
                    has_rels = any(
                        de.get("relationships_to_other_elements")
                        for de in discovered if isinstance(de, dict)
                    )
                    if has_rels:
                        lines.append("### Element Relationships")
                        lines.append("")
                        lines.append("| Element | Related To | Relationship | Mimic Tips |")
                        lines.append("|---------|-----------|--------------|------------|")
                        for de in discovered:
                            ename = de.get("element_name", "unknown")
                            for rel in de.get("relationships_to_other_elements", []):
                                related = rel.get("element", "")
                                rtype = rel.get("relationship", "")
                                tips = rel.get("mimic_tips", "")
                                lines.append(f"| {ename} | {related} | {rtype} | {tips} |")
                        lines.append("")

                    # Mimic strategy based on relationships
                    lines.append("### Reconstruction Strategy")
                    lines.append("")
                    lines.append("Based on element relationships, reconstruct this area by:")
                    lines.append("")
                    step_num = 1
                    # Group by parent containers first
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
                        f"{step_num}. Place child elements following the relationship graph"
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
                    # Fallback: legacy format with computed_styles
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

    def _generate_mimic_strategy(self, data: dict, uiux_dir: Path) -> None:
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
            "- Property-level: exact match for colors, fonts; 1px tolerance for spacing",
            "- Static resources: original URLs preserved where possible",
            "- Max iterations: 3 refinement rounds before user approval",
        ])

        strategy_path = uiux_dir / "mimic-strategy.md"
        strategy_path.write_text("\n".join(lines), encoding="utf-8")
