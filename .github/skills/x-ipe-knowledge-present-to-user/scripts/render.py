#!/usr/bin/env python3
"""Knowledge rendering: parse Markdown content into structured summaries.

Reads a knowledge file, parses sections, tracks completeness via
[INCOMPLETE: ...] markers, and outputs structured JSON or Markdown.

JSON to stdout on success; JSON to stderr + exit 1 on error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def _exit_error(error: str, message: str) -> None:
    print(json.dumps({"success": False, "error": error, "message": message}),
          file=sys.stderr)
    sys.exit(1)


def _ok(data: dict) -> None:
    print(json.dumps({"success": True, **data}, ensure_ascii=False))


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


INCOMPLETE_PATTERN = re.compile(r"\[INCOMPLETE:\s*([^\]]*)\]")


def _parse_sections(content: str) -> tuple[str, str, list[dict]]:
    """Parse Markdown into title, summary, and sections."""
    lines = content.split("\n")
    title = ""
    summary = ""
    sections: list[dict] = []
    current_heading = ""
    current_lines: list[str] = []

    for line in lines:
        # Check for H1 title
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue

        # Check for H2+ section header
        h2_match = re.match(r"^(#{2,})\s+(.+)$", line)
        if h2_match:
            # Save previous section (skip empty preamble before first H2)
            if current_heading or "\n".join(current_lines).strip():
                sections.append(_build_section(current_heading, current_lines))
            current_heading = h2_match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Save last section (skip empty trailing preamble)
    if current_heading or "\n".join(current_lines).strip():
        sections.append(_build_section(current_heading, current_lines))

    # Extract summary
    if sections:
        first_content = sections[0].get("content", "")
        summary = first_content[:200].strip()
    elif content.strip():
        summary = content[:200].strip()

    # If no title found, use "Untitled"
    if not title:
        title = "Untitled"

    return title, summary, sections


def _build_section(heading: str, lines: list[str]) -> dict:
    """Build a section dict with completeness and warnings."""
    content = "\n".join(lines).strip()
    total_chars = len(content) if content else 0

    # Find incomplete markers
    markers = INCOMPLETE_PATTERN.findall(content)
    incomplete_chars = sum(
        len(m.group())
        for m in INCOMPLETE_PATTERN.finditer(content)
    )

    if total_chars == 0:
        completeness = 0
    else:
        completeness = max(0, min(100,
            round((total_chars - incomplete_chars) / total_chars * 100)))

    section: dict = {
        "heading": heading or "(untitled)",
        "content": content,
        "completeness": completeness,
    }

    if markers:
        section["warnings"] = [f"INCOMPLETE: {reason}" for reason in markers]

    return section


def cmd_render(args: argparse.Namespace) -> None:
    content_path = Path(args.content_path)
    fmt = args.format

    if fmt not in ("structured", "markdown"):
        _exit_error("INPUT_VALIDATION_FAILED",
                    f"Invalid format: {fmt}. Must be 'structured' or 'markdown'")

    if not content_path.exists():
        _exit_error("CONTENT_NOT_FOUND",
                    f"File not found: {content_path}")

    # Try to read as UTF-8
    try:
        content = content_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        _exit_error("INVALID_CONTENT_FORMAT",
                    f"File is not valid UTF-8: {content_path}")

    # Handle empty file
    if not content.strip():
        result = {
            "title": "Empty",
            "summary": "",
            "sections": [],
            "metadata": {
                "source_path": str(content_path),
                "total_sections": 0,
                "overall_completeness": 0,
                "generated_at": _now_iso(),
            },
        }
        if fmt == "markdown":
            print("# Empty\n\n*No content available.*")
        else:
            _ok({"operation": "render", "result": {"rendered_output": result}})
        return

    title, summary, sections = _parse_sections(content)

    overall_completeness = 0
    if sections:
        overall_completeness = round(
            sum(s["completeness"] for s in sections) / len(sections))

    metadata = {
        "source_path": str(content_path),
        "total_sections": len(sections),
        "overall_completeness": overall_completeness,
        "generated_at": _now_iso(),
    }

    if fmt == "markdown":
        md_lines = [f"# {title}", "", f"*{summary}*", ""]
        for section in sections:
            md_lines.append(f"## {section['heading']}")
            md_lines.append("")
            md_lines.append(section["content"])
            if section.get("warnings"):
                md_lines.append("")
                for w in section["warnings"]:
                    md_lines.append(f"> ⚠️ {w}")
            md_lines.append("")
        md_lines.append(f"---\n*Completeness: {overall_completeness}% | "
                        f"Sections: {len(sections)} | "
                        f"Generated: {metadata['generated_at']}*")
        print("\n".join(md_lines))
    else:
        result = {
            "title": title,
            "summary": summary,
            "sections": sections,
            "metadata": metadata,
        }
        _ok({"operation": "render", "result": {"rendered_output": result}})


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Knowledge content renderer")
    sub = parser.add_subparsers(dest="command")

    p_render = sub.add_parser("render", help="Render knowledge content")
    p_render.add_argument("--content-path", required=True,
                          help="Path to knowledge Markdown file")
    p_render.add_argument("--format", default="structured",
                          choices=["structured", "markdown"],
                          help="Output format (default: structured)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "render":
        cmd_render(args)


if __name__ == "__main__":
    main()
