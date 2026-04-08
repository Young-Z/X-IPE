# Section 07 — Technology Stack

## Runtime Dependencies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | ≥ 3.10 | Runtime (uses `X | Y` union type syntax) |
| PyYAML | (imported lazily) | Schema loading/writing (YAML format) |

## Standard Library Usage

| Module | Purpose |
|--------|---------|
| `argparse` | CLI argument parsing (9 subcommands) |
| `json` | JSONL graph file I/O, property serialization |
| `uuid` | Entity ID generation (`uuid4().hex[:8]`) |
| `datetime` | Timestamps (UTC ISO 8601) |
| `pathlib` | File path resolution & safe path traversal |

## Storage Format

| Component | Format | Path |
|-----------|--------|------|
| Graph data | JSONL (append-only) | `memory/ontology/graph.jsonl` |
| Schema | YAML | `memory/ontology/schema.yaml` |

## Language Features Used

- Python 3.10+ union type syntax: `dict | None`, `str | None`
- f-strings for all string interpolation
- `dataclasses`-style patterns (manual dict construction)
- Generator expressions, list comprehensions
- Nested function definitions (DFS cycle detection)

## Build & Package

- No build step required — pure Python script
- No `setup.py` / `pyproject.toml` for the skill itself
- Distributed as a skill package (slug: `ontology`, version: `1.0.4`)
- Published timestamp: `1773249559725` (from `_meta.json`)

## Security

- `resolve_safe_path()` prevents path traversal attacks (rejects paths outside workspace root)
- `Credential` type enforces `forbidden_properties` — never stores raw secrets
- No network I/O — purely local file operations
