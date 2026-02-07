# Dev Environment - Tech Stack Details

> Reference from SKILL.md: `See [references/tech-stack-details.md](references/tech-stack-details.md)`

---

## Auto-Detection Hints

| Context Clue | Suggested Stack |
|--------------|-----------------|
| "Python", "Django", "Flask", "FastAPI" | python |
| "Node", "Express", "React", "Next.js" | nodejs |
| "API", "backend", "web service" | python (default) |
| "uv", "pip", "conda" | python |
| "npm", "yarn", "package.json" | nodejs |

---

## Python Setup Details

### Initialization Commands

```
1. Run: uv init
2. Run: uv venv
3. Create src/ folder
4. Create src/__init__.py
5. Create tests/ folder
6. Create tests/__init__.py
```

### Resulting Structure

```
project-root/
├── .venv/
├── src/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
└── README.md
```

### Setup Document Template

Use `templates/setup-python.md` as the base for `x-ipe-docs/environment/setup.md`.

Minimal inline template if templates/ is unavailable:

```markdown
# Environment Setup

## Tech Stack
- Python with uv package manager
- Virtual environment: .venv

## Structure
project-root/
├── .venv/              # Virtual environment
├── src/                # Source code
├── tests/              # Test files
├── pyproject.toml      # Project configuration
└── x-ipe-docs/         # Documentation

## Prerequisites
- Python 3.8+
- uv package manager (install: `pip install uv`)

## Setup Steps
1. `cd /path/to/project`
2. `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)
3. `uv pip install -r requirements.txt`

## Development
- Run application: `python src/main.py`
- Run tests: `pytest tests/`
- Add packages: `uv pip install <package>`
- Freeze dependencies: `uv pip freeze > requirements.txt`
```

---

## Node.js Setup Details

### Initialization Commands

```
1. Ask user: "Would you like to use npm or yarn?" (default: npm)
2. Run: npm init -y  OR  yarn init -y
3. Create src/ folder
4. Create src/index.js
5. Create tests/ folder
6. Create tests/index.test.js
```

### Resulting Structure

```
project-root/
├── node_modules/
├── src/
│   └── index.js
├── tests/
│   └── index.test.js
├── package.json
└── README.md
```

### Setup Document Template

Use `templates/setup-nodejs.md` as the base for `x-ipe-docs/environment/setup.md`.

Minimal inline template if templates/ is unavailable:

```markdown
# Environment Setup

## Tech Stack
- Node.js with {npm|yarn} package manager

## Structure
project-root/
├── node_modules/       # Dependencies
├── src/                # Source code
├── tests/              # Test files
├── package.json        # Project configuration
└── x-ipe-docs/         # Documentation

## Prerequisites
- Node.js 16+
- npm (comes with Node.js) or yarn

## Setup Steps
1. `cd /path/to/project`
2. `npm install` or `yarn install`

## Development
- Run application: `node src/index.js`
- Run tests: `npm test` or `yarn test`
- Add packages: `npm install <package>` or `yarn add <package>`
- Add dev packages: `npm install -D <package>` or `yarn add -D <package>`
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| uv not found | uv not installed | Install: `pip install uv` |
| npm not found | Node.js not installed | Install Node.js from nodejs.org |
| Git not initialized | Step 3 failed | Manually run `git init` |
| Permission denied | Directory permissions | Use `sudo` or change directory owner |

### Validation Commands

**After Python setup:**
```bash
uv --version              # Check uv installed
source .venv/bin/activate # Activate venv
python --version          # Check Python version
git status                # Verify git initialized
```

**After Node.js setup:**
```bash
node --version   # Check Node.js installed
npm --version    # Check npm installed
git status       # Verify git initialized
```
