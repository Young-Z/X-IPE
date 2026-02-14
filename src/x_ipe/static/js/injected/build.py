"""Minify toolbar source files for injection.

Usage: python build.py
Reads from src/x_ipe/static/js/injected/ and writes to
.github/skills/x-ipe-tool-uiux-reference/references/
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
SRC_DIR = PROJECT_ROOT / 'src' / 'x_ipe' / 'static' / 'js' / 'injected'
OUT_DIR = PROJECT_ROOT / '.github' / 'skills' / 'x-ipe-tool-uiux-reference' / 'references'

FILES = {
    'xipe-toolbar-core.js': 'toolbar-core.min.js',
    'xipe-toolbar-theme.js': 'toolbar-theme.min.js',
    'xipe-toolbar-mockup.js': 'toolbar-mockup.min.js',
}


def minify(source: str) -> str:
    """JS minification: strip comments, collapse whitespace, remove unnecessary space."""
    # Remove single-line comments (preserve URLs with //)
    result = re.sub(r'(?<![:\'"\\])//(?!/)[^\n]*', '', source)
    # Remove multi-line comments
    result = re.sub(r'/\*.*?\*/', '', result, flags=re.DOTALL)
    # Collapse runs of whitespace to single space
    result = re.sub(r'[ \t]+', ' ', result)
    # Remove blank lines
    result = re.sub(r'\n\s*\n', '\n', result)
    # Remove leading whitespace per line
    result = re.sub(r'\n\s+', '\n', result)
    # Remove newlines around brackets/operators
    result = re.sub(r'\n([{}();,\[\]:])', r'\1', result)
    result = re.sub(r'([{}();,\[\]:])\n', r'\1', result)
    # Remove space around operators
    result = re.sub(r' ?([\{\}\(\)\[\];,:<>=\+\-\*\/\&\|\!]) ?', r'\1', result)
    # Restore needed spaces (keywords)
    for kw in ['const', 'let', 'var', 'function', 'return', 'if', 'else',
               'new', 'typeof', 'instanceof', 'in', 'of', 'for', 'while',
               'switch', 'case', 'break', 'throw', 'class', 'extends',
               'import', 'export', 'default', 'try', 'catch', 'finally']:
        result = re.sub(rf'({kw})([^\s\({{;,\}}])', rf'\1 \2', result)
    return result.strip()


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for src_name, out_name in FILES.items():
        src = SRC_DIR / src_name
        out = OUT_DIR / out_name
        if not src.exists():
            print(f'SKIP {src_name} (not found)')
            continue
        source = src.read_text(encoding='utf-8')
        minified = minify(source)
        out.write_text(minified, encoding='utf-8')
        ratio = len(minified) / len(source) * 100
        print(f'{src_name} -> {out_name}: {len(source)} -> {len(minified)} bytes ({ratio:.0f}%)')


if __name__ == '__main__':
    build()
