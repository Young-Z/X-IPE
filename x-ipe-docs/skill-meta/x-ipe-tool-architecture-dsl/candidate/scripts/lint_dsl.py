#!/usr/bin/env python3
"""
Architecture DSL Linter — validate Architecture DSL files against grammar v2.

Usage:
    python3 lint_dsl.py path/to/file.dsl
    python3 lint_dsl.py path/to/file.dsl --format json
    python3 lint_dsl.py -                              # read from stdin
    echo '@startuml module-view ...' | python3 lint_dsl.py -

Exit codes:
    0  — no errors (warnings may be present)
    1  — one or more errors found

Error codes:
    E001  Missing @startuml header
    E002  Missing @enduml footer
    E003  Invalid view type
    E004  Missing grid declaration (module-view)
    E005  Module cols sum != 12
    E006  Missing rows in layer
    E007  Duplicate alias
    E008  Undefined alias in flow
    E009  Invalid status value
    W001  Empty container
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


# ── Severity ──────────────────────────────────────────────────

class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


# ── Diagnostic ────────────────────────────────────────────────

@dataclass
class Diagnostic:
    code: str
    severity: Severity
    message: str
    line: int | None = None
    fix: str = ""

    def to_dict(self) -> dict:
        d: dict = {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
        }
        if self.line is not None:
            d["line"] = self.line
        if self.fix:
            d["fix"] = self.fix
        return d

    def __str__(self) -> str:
        loc = f":{self.line}" if self.line is not None else ""
        prefix = self.code
        return f"{prefix}{loc}: {self.message}"


# ── Helpers ───────────────────────────────────────────────────

_COMMENT_RE = re.compile(r"^\s*'")
_BLOCK_COMMENT_OPEN = re.compile(r"/'\s*")
_BLOCK_COMMENT_CLOSE = re.compile(r"'\s*/")

VALID_VIEW_TYPES = {"module-view", "landscape-view"}
VALID_STATUSES = {"healthy", "warning", "critical"}
VALID_STEREOTYPES = {"model", "service", "icon", "api", "db", "file", "folder"}

MODULE_VIEW_KEYWORDS = {"layer", "module", "component", "side-column"}
LANDSCAPE_VIEW_KEYWORDS = {"zone", "app", "database"}

_ALIAS_RE = re.compile(r'\bas\s+([a-zA-Z_][a-zA-Z0-9_]*)')
_FLOW_RE = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*-->\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:')
_COLS_RE = re.compile(r'\bcols\s+(\d+)')
_ROWS_RE = re.compile(r'\brows\s+(\d+)')
_GRID_DOC_RE = re.compile(r'^\s*grid\s+(\d+)\s*x\s*(\d+)')
_STATUS_RE = re.compile(r'^\s*status\s*:\s*(\S+)')
_STARTUML_RE = re.compile(r'^\s*@startuml\s+(\S+)')
_ENDUML_RE = re.compile(r'^\s*@enduml\s*$')
_LAYER_RE = re.compile(r'^\s*layer\s+"([^"]*)"')
_MODULE_RE = re.compile(r'^\s*module\s+"([^"]*)"')
_COMPONENT_RE = re.compile(r'^\s*component\s+"([^"]*)"')
_ZONE_RE = re.compile(r'^\s*zone\s+"([^"]*)"')
_APP_RE = re.compile(r'^\s*app\s+"([^"]*)"')
_DATABASE_RE = re.compile(r'^\s*database\s+"([^"]*)"')
_STEREOTYPE_RE = re.compile(r'<<(\w+)>>')


def _strip_comments(lines: list[str]) -> list[tuple[int, str]]:
    """Return (1-based line number, stripped content) pairs, removing comments."""
    result: list[tuple[int, str]] = []
    in_block = False
    for i, raw in enumerate(lines, 1):
        if in_block:
            if _BLOCK_COMMENT_CLOSE.search(raw):
                in_block = False
            continue
        if _BLOCK_COMMENT_OPEN.search(raw):
            in_block = True
            continue
        if _COMMENT_RE.match(raw):
            continue
        # Strip inline comment (single-quote after content)
        content = raw.split("'")[0] if "'" in raw and not raw.strip().startswith("'") else raw
        stripped = content.rstrip()
        if stripped:
            result.append((i, stripped))
    return result


# ── Nesting tracker ───────────────────────────────────────────

@dataclass
class _Container:
    kind: str          # layer | module | zone | app | side-column
    name: str
    line: int
    children: int = 0  # count of meaningful child elements
    cols_sum: int = 0  # for layers: sum of module cols
    has_rows: bool = False
    has_component: bool = False
    module_count: int = 0


# ── Linter ────────────────────────────────────────────────────

@dataclass
class Linter:
    diagnostics: list[Diagnostic] = field(default_factory=list)

    # Collected state
    _view_type: str | None = None
    _has_header: bool = False
    _has_footer: bool = False
    _has_grid: bool = False
    _aliases: dict[str, int] = field(default_factory=dict)  # alias → line
    _flow_refs: list[tuple[str, str, int]] = field(default_factory=list)  # (src, dst, line)
    _stack: list[_Container] = field(default_factory=list)

    def _add(self, code: str, sev: Severity, msg: str, *, line: int | None = None, fix: str = "") -> None:
        self.diagnostics.append(Diagnostic(code, sev, msg, line=line, fix=fix))

    def lint(self, source: str) -> list[Diagnostic]:
        lines = source.splitlines()
        cleaned = _strip_comments(lines)

        if not cleaned:
            self._add("E001", Severity.ERROR, "Empty document — missing @startuml header",
                       fix="Add @startuml module-view or @startuml landscape-view")
            return self.diagnostics

        self._pass_structure(cleaned)
        self._pass_grid_and_nesting(cleaned)
        self._pass_aliases_and_flows(cleaned)

        return self.diagnostics

    # ── Pass 1: document structure ────────────────────────────

    def _pass_structure(self, cleaned: list[tuple[int, str]]) -> None:
        first_lineno, first_line = cleaned[0]
        m = _STARTUML_RE.match(first_line)
        if not m:
            self._add("E001", Severity.ERROR,
                       "Missing @startuml header — document must start with @startuml <view-type>",
                       line=first_lineno,
                       fix="Add @startuml module-view or @startuml landscape-view")
        else:
            self._has_header = True
            vt = m.group(1)
            if vt not in VALID_VIEW_TYPES:
                self._add("E003", Severity.ERROR,
                           f"Invalid view type '{vt}'",
                           line=first_lineno,
                           fix="Use module-view or landscape-view")
            else:
                self._view_type = vt

        last_lineno, last_line = cleaned[-1]
        if not _ENDUML_RE.match(last_line):
            self._add("E002", Severity.ERROR,
                       "Missing @enduml footer",
                       line=last_lineno,
                       fix="Add @enduml at end of document")
        else:
            self._has_footer = True

    # ── Pass 2: grid rules & nesting ──────────────────────────

    def _pass_grid_and_nesting(self, cleaned: list[tuple[int, str]]) -> None:
        for lineno, line in cleaned:

            # Document-level grid
            if _GRID_DOC_RE.match(line) and not self._stack:
                self._has_grid = True

            # Track view-type consistency
            if self._view_type == "landscape-view":
                for kw in MODULE_VIEW_KEYWORDS:
                    if re.match(rf'^\s*{kw}\s', line):
                        self._add("E003", Severity.ERROR,
                                   f"Module-view keyword '{kw}' used in landscape-view",
                                   line=lineno,
                                   fix=f"Remove '{kw}' or change view type to module-view")
            elif self._view_type == "module-view":
                for kw in LANDSCAPE_VIEW_KEYWORDS:
                    if re.match(rf'^\s*{kw}\s', line):
                        self._add("E003", Severity.ERROR,
                                   f"Landscape-view keyword '{kw}' used in module-view",
                                   line=lineno,
                                   fix=f"Remove '{kw}' or change view type to landscape-view")

            # Count braces to detect single-line containers
            open_count = line.count("{")
            close_count = line.count("}")
            is_single_line = open_count > 0 and close_count >= open_count

            # Status validation — check BEFORE container open/close to catch inline status
            for sm in re.finditer(r'status\s*:\s*(\S+)', line):
                status_val = sm.group(1).strip().rstrip(",}")
                if status_val not in VALID_STATUSES:
                    self._add("E009", Severity.ERROR,
                               f"Invalid status '{status_val}'",
                               line=lineno,
                               fix="Use healthy, warning, or critical")

            # Open containers
            if _LAYER_RE.match(line) and "{" in line:
                name = _LAYER_RE.match(line).group(1)
                container = _Container("layer", name, lineno)
                if is_single_line:
                    self._validate_container(container)
                else:
                    self._stack.append(container)

            elif _MODULE_RE.match(line) and "{" in line:
                name = _MODULE_RE.match(line).group(1)
                container = _Container("module", name, lineno)
                for c in reversed(self._stack):
                    if c.kind == "layer":
                        c.module_count += 1
                        break
                if is_single_line:
                    self._validate_container(container)
                else:
                    self._stack.append(container)

            elif _ZONE_RE.match(line) and "{" in line:
                name = _ZONE_RE.match(line).group(1)
                container = _Container("zone", name, lineno)
                if is_single_line:
                    self._validate_container(container)
                else:
                    self._stack.append(container)

            elif _APP_RE.match(line) and "{" in line:
                name = _APP_RE.match(line).group(1)
                if self._stack:
                    for c in reversed(self._stack):
                        if c.kind == "zone":
                            c.children += 1
                            break
                container = _Container("app", name, lineno)
                if is_single_line:
                    pass  # single-line app — no container validation needed
                else:
                    self._stack.append(container)

            elif _APP_RE.match(line) and "{" not in line:
                # app without braces (unlikely but handle)
                if self._stack:
                    for c in reversed(self._stack):
                        if c.kind == "zone":
                            c.children += 1
                            break

            elif _DATABASE_RE.match(line):
                if self._stack:
                    for c in reversed(self._stack):
                        if c.kind == "zone":
                            c.children += 1
                            break

            elif _COMPONENT_RE.match(line):
                if self._stack:
                    for c in reversed(self._stack):
                        if c.kind in ("module", "layer"):
                            c.has_component = True
                            c.children += 1
                            break

            # Track rows in containers (not on container-opening lines)
            if self._stack and _ROWS_RE.match(line.strip()) and not _LAYER_RE.match(line) and not _MODULE_RE.match(line):
                self._stack[-1].has_rows = True

            # Track cols in modules (not component lines)
            if self._stack and self._stack[-1].kind == "module":
                m_cols = _COLS_RE.search(line)
                if m_cols and not _COMPONENT_RE.match(line):
                    self._stack[-1].cols_sum = int(m_cols.group(1))

            # Close containers (standalone closing brace)
            if line.strip() == "}" and self._stack:
                container = self._stack.pop()
                self._validate_container(container)

        # Anything left unclosed?
        for c in self._stack:
            self._add("E002", Severity.ERROR,
                       f"Unclosed {c.kind} '{c.name}' — missing closing brace",
                       line=c.line, fix="Add closing }")

        # Module-view must have grid declaration
        if self._view_type == "module-view" and not self._has_grid:
            self._add("E004", Severity.ERROR,
                       "Missing grid declaration in module-view",
                       fix="Add grid 12 x N at document level")

    def _validate_container(self, c: _Container) -> None:
        if c.kind == "layer":
            if not c.has_rows and self._view_type == "module-view":
                self._add("E006", Severity.ERROR,
                           f"Missing rows declaration in layer '{c.name}'",
                           line=c.line,
                           fix=f"Add rows N to layer '{c.name}'")
            if not c.has_component and self._view_type == "module-view":
                if c.module_count == 0:
                    self._add("W001", Severity.WARNING,
                               f"Empty layer '{c.name}' — no components or modules",
                               line=c.line,
                               fix="Add components or modules to this layer")
            # Check cols sum for layers that contain modules
            if c.module_count > 0:
                total_cols = 0
                # Re-examine — we accumulate cols from closed modules
                # handled below via _layer_cols tracking
                pass

        elif c.kind == "zone":
            if c.children == 0:
                self._add("W001", Severity.WARNING,
                           f"Empty zone '{c.name}' — no apps or databases",
                           line=c.line,
                           fix="Add app or database elements to this zone")

        elif c.kind == "module":
            if c.cols_sum > 0:
                # Record cols for parent layer validation
                for parent in reversed(self._stack):
                    if parent.kind == "layer":
                        parent.cols_sum += c.cols_sum
                        parent.has_component = parent.has_component or c.has_component
                        break
            if not c.has_component:
                self._add("W001", Severity.WARNING,
                           f"Empty module '{c.name}' — no components",
                           line=c.line,
                           fix="Add components to this module")

        # When layer closes, check cols sum
        if c.kind == "layer" and c.module_count > 0 and c.cols_sum != 12:
            self._add("E005", Severity.ERROR,
                       f"Module cols sum to {c.cols_sum}, expected 12 in layer '{c.name}'",
                       line=c.line,
                       fix=f"Adjust module cols to sum to 12")

    # ── Pass 3: aliases & flows ───────────────────────────────

    def _pass_aliases_and_flows(self, cleaned: list[tuple[int, str]]) -> None:
        for lineno, line in cleaned:
            # Collect aliases
            for m in _ALIAS_RE.finditer(line):
                alias = m.group(1)
                if alias in self._aliases:
                    self._add("E007", Severity.ERROR,
                               f"Duplicate alias '{alias}' (first defined at line {self._aliases[alias]})",
                               line=lineno,
                               fix="Use unique alias names")
                else:
                    self._aliases[alias] = lineno

            # Collect flows
            fm = _FLOW_RE.match(line)
            if fm:
                self._flow_refs.append((fm.group(1), fm.group(2), lineno))

        # Validate flow references
        for src, dst, lineno in self._flow_refs:
            if src not in self._aliases:
                self._add("E008", Severity.ERROR,
                           f"Undefined alias '{src}' in flow",
                           line=lineno,
                           fix=f"Define alias with 'as {src}' before using in flow")
            if dst not in self._aliases:
                self._add("E008", Severity.ERROR,
                           f"Undefined alias '{dst}' in flow",
                           line=lineno,
                           fix=f"Define alias with 'as {dst}' before using in flow")


# ── CLI ───────────────────────────────────────────────────────

def _read_input(path_arg: str) -> tuple[str, str]:
    """Return (source_text, display_name)."""
    if path_arg == "-":
        return sys.stdin.read(), "<stdin>"
    p = Path(path_arg)
    if not p.exists():
        print(f"Error: file not found: {path_arg}", file=sys.stderr)
        sys.exit(2)
    return p.read_text(encoding="utf-8"), str(p)


def _format_text(diags: list[Diagnostic], name: str) -> str:
    if not diags:
        return f"✅ {name}: no issues found"
    lines = [f"{'❌' if any(d.severity == Severity.ERROR for d in diags) else '⚠️'}  {name}: {len(diags)} issue(s)"]
    for d in diags:
        icon = "❌" if d.severity == Severity.ERROR else "⚠️"
        loc = f":{d.line}" if d.line is not None else ""
        lines.append(f"  {icon} {d.code}{loc}: {d.message}")
        if d.fix:
            lines.append(f"       Fix: {d.fix}")
    return "\n".join(lines)


def _format_json(diags: list[Diagnostic], name: str) -> str:
    errors = [d.to_dict() for d in diags if d.severity == Severity.ERROR]
    warnings = [d.to_dict() for d in diags if d.severity == Severity.WARNING]
    report = {
        "file": name,
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }
    return json.dumps(report, indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Architecture DSL files against grammar v2.",
        epilog="Exit code 0 = valid (warnings OK), 1 = errors found, 2 = bad arguments.",
    )
    parser.add_argument("file", help="Path to .dsl file, or '-' for stdin")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args(argv)

    source, name = _read_input(args.file)
    linter = Linter()
    diags = linter.lint(source)

    if args.format == "json":
        print(_format_json(diags, name))
    else:
        print(_format_text(diags, name))

    has_errors = any(d.severity == Severity.ERROR for d in diags)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
