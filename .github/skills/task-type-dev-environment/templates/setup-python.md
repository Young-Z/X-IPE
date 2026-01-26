# Environment Setup - Python

## Tech Stack
- Python with uv package manager
- Virtual environment: .venv

## Structure
```
project-root/
├── .venv/              # Virtual environment
├── src/                # Source code
│   └── __init__.py
├── tests/              # Test files
│   └── __init__.py
├── pyproject.toml      # Project configuration
├── .gitignore          # Git ignore patterns
├── README.md           # Project documentation
└── x-ipe-docs/               # Documentation
    └── environment/
        └── setup.md    # This file
```

## Prerequisites
- Python 3.8+
- uv package manager (install: `pip install uv`)
- Git

## Setup Steps

### 1. Clone or navigate to project
```bash
cd /path/to/project
```

### 2. Activate virtual environment
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies (when added)
```bash
# From requirements.txt
uv pip install -r requirements.txt

# Individual package
uv pip install <package-name>

# Development dependencies
uv pip install -e ".[dev]"
```

## Development Workflow

### Running the Application
```bash
# Activate environment first
source .venv/bin/activate

# Run main entry point
python src/main.py

# Or use specific module
python -m src.module_name
```

### Running Tests
```bash
# Install pytest if not already installed
uv pip install pytest

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_module.py
```

### Managing Dependencies

#### Add a package
```bash
uv pip install <package-name>

# Update requirements.txt
uv pip freeze > requirements.txt
```

#### Remove a package
```bash
uv pip uninstall <package-name>

# Update requirements.txt
uv pip freeze > requirements.txt
```

#### List installed packages
```bash
uv pip list
```

## Project Structure Guidelines

### Source Code (`src/`)
- Keep all application code here
- Use meaningful module names
- Create `__init__.py` in each package directory

**Example:**
```
src/
├── __init__.py
├── main.py           # Entry point
├── models/
│   ├── __init__.py
│   └── user.py
├── services/
│   ├── __init__.py
│   └── auth.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

### Tests (`tests/`)
- Mirror source structure
- Name test files: `test_<module>.py`
- Use descriptive test function names

**Example:**
```
tests/
├── __init__.py
├── test_main.py
├── models/
│   ├── __init__.py
│   └── test_user.py
└── services/
    ├── __init__.py
    └── test_auth.py
```

## Common Tasks

### Updating Python version
```bash
# Check current version
python --version

# Use specific Python version (if installed)
uv venv --python python3.11
```

### Resetting environment
```bash
# Deactivate current environment
deactivate

# Remove virtual environment
rm -rf .venv

# Recreate
uv venv

# Reactivate
source .venv/bin/activate

# Reinstall dependencies
uv pip install -r requirements.txt
```

### Code Quality Tools
```bash
# Install common tools
uv pip install black flake8 mypy

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Environment Variables

Create a `.env` file for environment-specific configuration:
```bash
# .env (excluded by .gitignore)
DEBUG=True
DATABASE_URL=postgresql://localhost/mydb
SECRET_KEY=your-secret-key
```

Load in Python:
```python
# Install python-dotenv
# uv pip install python-dotenv

from dotenv import load_dotenv
import os

load_dotenv()
debug = os.getenv('DEBUG', 'False') == 'True'
```

## Notes

- **Always activate the virtual environment** before working
- **Keep .venv/ excluded** from git (in .gitignore)
- **Update requirements.txt** after adding/removing packages
- **Use relative imports** within src/ package
- **Run tests frequently** to catch issues early
- **Document dependencies** in requirements.txt or pyproject.toml

## Troubleshooting

### Issue: `uv: command not found`
**Solution:**
```bash
pip install uv
```

### Issue: Virtual environment not activating
**Solution:**
```bash
# Check if .venv exists
ls -la .venv

# Recreate if missing
uv venv
source .venv/bin/activate
```

### Issue: Import errors
**Solution:**
```bash
# Ensure you're in project root
pwd

# Activate environment
source .venv/bin/activate

# Verify Python sees src/
python -c "import sys; print(sys.path)"
```

### Issue: Package conflicts
**Solution:**
```bash
# Create fresh environment
deactivate
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Additional Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [Python Packaging Guide](https://packaging.python.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
