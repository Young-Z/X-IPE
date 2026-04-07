# Extraction Prompts — Section 7: Technology Stack Identification

## 7.1 Languages

**Goal:** Identify all programming languages with version constraints.

**Prompts:**

1. Parse package manager files for language version declarations:
   - Python: `python_requires` in `pyproject.toml`/`setup.py`, `runtime.txt`, `.python-version`
   - Node.js: `engines.node` in `package.json`, `.nvmrc`, `.node-version`
   - Java: `sourceCompatibility`/`targetCompatibility` in `build.gradle`, `maven.compiler.source` in `pom.xml`
   - Go: `go` directive in `go.mod`
   - Rust: `rust-version` in `Cargo.toml`, `rust-toolchain.toml`
2. Count source files by extension to confirm language presence and relative weight
3. Check for polyglot indicators (multiple languages in same repo)

**Source Priority:**
1. Package manager files with explicit version declarations
2. Version control files (`.python-version`, `.nvmrc`, `.tool-versions`)
3. File extension analysis
4. Shebang lines in scripts

**Output Format:**

| Language | Version Constraint | Evidence File | Lock Version | File Count |
|----------|-------------------|---------------|--------------|------------|
| Python | `>=3.10` | `pyproject.toml` | `3.11.5` (from `.python-version`) | 142 |
| TypeScript | `~5.3.0` | `package.json` | `5.3.3` (from `package-lock.json`) | 87 |

---

## 7.2 Frameworks

**Goal:** Identify application frameworks with configuration evidence.

**Prompts:**

1. Identify frameworks from package dependencies (direct dependencies only, not transitive):
   - Python: `django`, `flask`, `fastapi`, `celery`, `sqlalchemy`
   - Node.js: `express`, `next`, `react`, `vue`, `angular`, `nestjs`
   - Java: `spring-boot`, `quarkus`, `micronaut`
   - Go: `gin`, `echo`, `fiber`
2. Confirm framework usage via framework-specific config files:
   - `next.config.js`, `angular.json`, `vue.config.js`, `settings.py` (Django), `application.yml` (Spring)
3. Identify framework version from manifest and lock files
4. Note framework plugins/extensions (e.g., Django REST Framework, Next.js plugins)

**Source Priority:**
1. Package manifest dependencies section
2. Framework configuration files
3. Import statements in entry point files
4. README framework badges/mentions

**Output Format:**

| Framework | Version | Evidence File | Config Evidence |
|-----------|---------|---------------|-----------------|
| Django | `>=4.2,<5.0` | `pyproject.toml` | `shop/settings.py` |
| Django REST Framework | `~=3.14` | `pyproject.toml` | `shop/settings.py` (INSTALLED_APPS) |
| Celery | `>=5.3` | `pyproject.toml` | `shop/celery.py` |

---

## 7.3 Build Tools

**Goal:** Identify build systems, package managers, and task runners.

**Prompts:**

1. Detect build tools from config files:
   - `Makefile`, `CMakeLists.txt`, `webpack.config.*`, `rollup.config.*`, `vite.config.*`
   - `tsconfig.json`, `babel.config.*`, `esbuild.config.*`
2. Identify package managers from lock files:
   - `package-lock.json` (npm), `yarn.lock` (yarn), `pnpm-lock.yaml` (pnpm)
   - `Pipfile.lock` (pipenv), `poetry.lock` (poetry), `uv.lock` (uv)
3. Detect task runners: `Taskfile.yml` (Task), `justfile` (Just), `scripts` in `package.json`
4. Identify release/publish tooling: `.goreleaser.yml`, `semantic-release`, `changesets`

**Source Priority:**
1. Lock files (most reliable package manager indicator)
2. Build tool config files
3. CI/CD pipeline steps referencing build commands
4. `scripts` section in package manifests

**Output Format:**

| Tool | Category | Config File | Purpose |
|------|----------|-------------|---------|
| webpack | bundler | `webpack.config.js` | JavaScript bundling |
| npm | package-manager | `package-lock.json` | Dependency management |
| Make | build | `Makefile` | Build automation and tasks |

---

## 7.4 Runtime & Infrastructure

**Goal:** Identify runtime versions, containers, and CI/CD tools.

**Prompts:**

1. Detect runtime specifications: `Dockerfile` (base images), `.python-version`, `.nvmrc`, `runtime.txt`
2. Detect containerization: `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `Containerfile`
3. Scan CI/CD configuration files:
   - `.github/workflows/*.yml` (GitHub Actions)
   - `.gitlab-ci.yml` (GitLab CI)
   - `Jenkinsfile` (Jenkins)
   - `.circleci/config.yml` (CircleCI)
   - `azure-pipelines.yml` (Azure DevOps)
4. Identify infrastructure-as-code: `terraform/`, `pulumi/`, `cdk/`, `serverless.yml`
5. Detect orchestration tools: `kubernetes/`, `k8s/`, `helm/`, `docker-compose.yml`

**Source Priority:**
1. Container files (Dockerfile, docker-compose.yml)
2. CI/CD configuration files
3. Infrastructure-as-code directories
4. README deployment sections

**Output Format:**

| Tool | Category | Version | Evidence File |
|------|----------|---------|---------------|
| Python | runtime | `3.11-slim` | `Dockerfile` (FROM python:3.11-slim) |
| Docker | container | — | `Dockerfile`, `docker-compose.yml` |
| GitHub Actions | ci-cd | — | `.github/workflows/ci.yml` |
| Terraform | iac | `~>1.5` | `terraform/versions.tf` |

---

## 7.5 Testing Frameworks

**Goal:** Identify test runners, assertion libraries, and coverage tools.

**Prompts:**

1. Detect testing frameworks from:
   - Test dependencies in package manifests (devDependencies, test extras)
   - Test configuration files: `pytest.ini`, `pyproject.toml [tool.pytest]`, `jest.config.*`, `vitest.config.*`, `.mocharc.*`
   - Test directory structure: `tests/`, `__tests__/`, `*_test.go`, `*Test.java`
2. Identify assertion libraries: built-in assert, `chai`, `assertj`, `testify`
3. Detect coverage tools: `coverage`, `istanbul/nyc`, `c8`, `jacoco`, `go tool cover`
4. Detect mocking libraries: `unittest.mock`, `jest` (built-in), `mockito`, `gomock`
5. Detect end-to-end/integration test tools: `playwright`, `cypress`, `selenium`, `testcontainers`

**Source Priority:**
1. Package manifest test/dev dependencies
2. Test configuration files
3. Test file imports (sample 5-10 test files)
4. CI/CD pipeline test steps

**Output Format:**

| Tool | Category | Version | Evidence File |
|------|----------|---------|---------------|
| pytest | runner | `>=7.0` | `pyproject.toml` |
| coverage | coverage | `>=7.0` | `pyproject.toml` |
| factory-boy | fixture | `>=3.3` | `pyproject.toml` |
| playwright | e2e | `>=1.40` | `package.json` (devDependencies) |
