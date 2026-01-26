# Environment Setup

## Tech Stack
- Python 3.12+ with uv package manager
- Flask web framework
- Virtual environment: .venv

## Project Structure
```
project-root/
├── .venv/              # Virtual environment
├── src/                # Source code (Flask app)
├── tests/              # Test files
├── x-ipe-docs/               # Documentation
├── pyproject.toml      # Project configuration
└── README.md           # Project overview
```

## Prerequisites
- Python 3.12+
- uv package manager (install: `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Setup Steps

1. **Clone or navigate to project:**
   ```bash
   cd /path/to/project
   ```

2. **Create virtual environment (if not exists):**
   ```bash
   uv venv
   ```

3. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\activate    # Windows
   ```

4. **Install dependencies:**
   ```bash
   uv sync
   ```

## Development

- **Run application:** `uv run python -m src.app`
- **Run tests:** `uv run pytest tests/`
- **Add packages:** `uv add <package>`
- **Add dev packages:** `uv add --dev <package>`

## Installed Packages

| Package | Purpose |
|---------|---------|
| Flask | Web framework |

## Notes
- Keep all source code in `src/`
- Keep all tests in `tests/`
- Use .gitignore to exclude .venv/ and other generated files
