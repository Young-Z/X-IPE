# Extraction Prompts — Section 5: Code Structure Analysis

## 5.1 Project Layout

**Goal:** Capture the root-level directory tree with purpose annotations.

**Prompts:**

1. Map the root directory tree (first 2-3 levels) with purpose annotations for each directory
2. For each top-level directory, describe its role in one sentence (e.g., "Contains REST API endpoint handlers")
3. Identify entry points: main files, app bootstrapping files, CLI entry points
4. Note any unconventional directory names and their purpose

**Source Priority:**
1. `tree -L 3 -d` output from repository root
2. README.md project structure sections
3. CONTRIBUTING.md directory descriptions

**Output Format:**
```
project-root/
├── src/                    # Application source code
│   ├── controllers/        # HTTP request handlers
│   ├── services/           # Business logic layer
│   └── models/             # Data models and schemas
├── tests/                  # Test suite
├── docs/                   # Documentation
└── scripts/                # Build and deployment scripts
```

---

## 5.2 Directory Structure

**Goal:** Build a comprehensive directory-to-purpose mapping table.

**Prompts:**

1. For each directory (2-3 levels deep), determine: role, key files it contains, and file count
2. Count files per directory to identify hot spots (directories with most files)
3. Identify directories that serve as package/module roots
4. Note any empty directories or directories with only generated content

**Source Priority:**
1. `find` output with file counts per directory
2. Package manifests listing submodules
3. Build configs referencing source directories

**Output Format:**

| Directory | Role | Key Files | File Count |
|-----------|------|-----------|------------|
| `src/controllers/` | HTTP handlers | `user_controller.py`, `auth_controller.py` | 12 |
| `src/services/` | Business logic | `user_service.py`, `auth_service.py` | 8 |

---

## 5.3 Naming Conventions

**Goal:** Document file, class, and function naming patterns with examples.

**Prompts:**

1. Identify naming conventions for files: snake_case, camelCase, PascalCase, kebab-case
2. Identify naming conventions for classes: patterns, prefixes, suffixes (e.g., `*Controller`, `*Service`)
3. Identify naming conventions for functions/methods: verb prefixes, naming style
4. Check for naming convention documentation in linter configs (`.eslintrc`, `pyproject.toml [tool.pylint]`)
5. Note any inconsistencies or mixed conventions

**Source Priority:**
1. File listing samples (50-100 files)
2. Class/function definitions in representative files (10-20 files)
3. Linter configuration files
4. CONTRIBUTING.md naming guidelines

**Output Format:**

| Category | Convention | Pattern | Example |
|----------|-----------|---------|---------|
| Files | snake_case | `{noun}_{type}.py` | `user_service.py` |
| Classes | PascalCase | `{Noun}{Type}` | `UserService` |
| Functions | snake_case | `{verb}_{noun}` | `get_user_by_id()` |

---

## 5.4 Module Boundaries

**Goal:** Identify how the project separates concerns at the module level.

**Prompts:**

1. Detect module boundary markers: `__init__.py`, `index.ts/js`, `package.json` (sub-packages), `go.mod`, `Cargo.toml`
2. Identify layering patterns by directory names:
   - MVC: controller/model/view
   - Clean Architecture: handler/usecase/entity/repository
   - Go standard: cmd/internal/pkg
   - Domain-Driven: domain/application/infrastructure
3. Count boundary marker files and map their locations
4. Analyze import/dependency patterns between modules (which modules import from which)

**Source Priority:**
1. Boundary marker files (`__init__.py`, `index.ts`, etc.)
2. Import statements across module boundaries
3. Build config module declarations
4. README.md architecture sections

**Output Format:**

| Boundary Marker | Count | Locations |
|----------------|-------|-----------|
| `__init__.py` | 15 | `src/`, `src/controllers/`, `src/services/`, ... |
| `setup.py` | 1 | `root` |

**Layering Pattern:** Clean Architecture
| Layer | Directory | Depends On |
|-------|-----------|------------|
| Handlers | `src/handlers/` | Use Cases |
| Use Cases | `src/usecases/` | Entities, Repositories |
| Entities | `src/entities/` | (none) |
| Repositories | `src/repositories/` | Entities |
