# Input Analysis Output Template

> Version: v1.0 | Feature: FEATURE-050-A | Last Updated: 03-17-2026

---

## Purpose

This template defines the structure of the `InputAnalysis` object produced in Phase 1, Step 1.1 of the Application Knowledge Extractor skill. The InputAnalysis object captures all classification and metadata about the input source.

---

## Template

```yaml
# Input type classification
input_type: "{source_code_repo | documentation_folder | running_web_app | public_url | single_file}"

# File format classification
format: "{markdown | python | javascript | html | mixed | yaml | json | go | rust | java | ruby | restructuredtext | text | unknown}"

# Application type classification
app_type: "{web | cli | mobile | unknown}"

# Source metadata
source_metadata:
  # Primary programming language (if applicable)
  primary_language: "{python | javascript | go | rust | java | ruby | null}"
  
  # Detected framework (if applicable)
  framework: "{flask | django | express | rails | next | react | click | commander | clap | react-native | flutter | null}"
  
  # File count in source
  file_count: 0  # Integer
  
  # Total size of all files in bytes
  total_size_bytes: 0  # Integer
  
  # Detected entry points (main files)
  entry_points: []  # List of strings
  
  # Whether documentation exists (docs/ or README)
  has_docs: true  # Boolean
  
  # Secondary app types detected (lower priority)
  secondary_app_types: []  # List of strings: ["cli", "web", "mobile"]
```

---

## Field Descriptions

### Core Classification Fields

| Field | Type | Required | Description | Possible Values |
|-------|------|----------|-------------|-----------------|
| `input_type` | string | Yes | Broad category of the source | `source_code_repo`, `documentation_folder`, `running_web_app`, `public_url`, `single_file` |
| `format` | string | Yes | Primary file format(s) | `markdown`, `python`, `javascript`, `html`, `mixed`, `yaml`, `json`, `go`, `rust`, `java`, `ruby`, `restructuredtext`, `text`, `unknown` |
| `app_type` | string | Yes | Application type classification | `web`, `cli`, `mobile`, `unknown` |

### Source Metadata Fields

| Field | Type | Required | Description | Possible Values |
|-------|------|----------|-------------|-----------------|
| `primary_language` | string | No | Primary programming language | `python`, `javascript`, `go`, `rust`, `java`, `ruby`, `null` |
| `framework` | string | No | Detected framework | `flask`, `django`, `express`, `rails`, `next`, `react`, `click`, `commander`, `clap`, `react-native`, `flutter`, `null` |
| `file_count` | integer | Yes | Total files in source | Any non-negative integer |
| `total_size_bytes` | integer | Yes | Total size in bytes | Any non-negative integer |
| `entry_points` | array | Yes | Detected entry points | List of file paths (e.g., `["app.py", "main.py"]`) |
| `has_docs` | boolean | Yes | Whether docs exist | `true` or `false` |
| `secondary_app_types` | array | No | Lower-priority app types | List of app types (e.g., `["cli"]`) |

---

## Examples

### Example 1: Flask Web App (Source Code Repo)

```yaml
input_type: "source_code_repo"
format: "mixed"
app_type: "web"
source_metadata:
  primary_language: "python"
  framework: "flask"
  file_count: 45
  total_size_bytes: 512000
  entry_points: ["app.py"]
  has_docs: true
  secondary_app_types: []
```

### Example 2: React Web App (Source Code Repo)

```yaml
input_type: "source_code_repo"
format: "mixed"
app_type: "web"
source_metadata:
  primary_language: "javascript"
  framework: "react"
  file_count: 128
  total_size_bytes: 2048576
  entry_points: ["index.js", "src/App.jsx"]
  has_docs: true
  secondary_app_types: []
```

### Example 3: Python CLI Tool (Source Code Repo)

```yaml
input_type: "source_code_repo"
format: "python"
app_type: "cli"
source_metadata:
  primary_language: "python"
  framework: "click"
  file_count: 12
  total_size_bytes: 102400
  entry_points: ["cli.py", "main.py"]
  has_docs: false
  secondary_app_types: []
```

### Example 4: Markdown Documentation Folder

```yaml
input_type: "documentation_folder"
format: "markdown"
app_type: "unknown"
source_metadata:
  primary_language: null
  framework: null
  file_count: 8
  total_size_bytes: 51200
  entry_points: []
  has_docs: true
  secondary_app_types: []
```

### Example 5: Public URL (Documentation Site)

```yaml
input_type: "public_url"
format: "html"
app_type: "unknown"
source_metadata:
  primary_language: null
  framework: null
  file_count: 0
  total_size_bytes: 0
  entry_points: []
  has_docs: true
  secondary_app_types: []
```

### Example 6: Running Web App (localhost)

```yaml
input_type: "running_web_app"
format: "html"
app_type: "web"
source_metadata:
  primary_language: null
  framework: null
  file_count: 0
  total_size_bytes: 0
  entry_points: []
  has_docs: false
  secondary_app_types: []
```

### Example 7: Single Markdown File

```yaml
input_type: "single_file"
format: "markdown"
app_type: "unknown"
source_metadata:
  primary_language: null
  framework: null
  file_count: 1
  total_size_bytes: 8192
  entry_points: []
  has_docs: true
  secondary_app_types: []
```

### Example 8: Multi-Framework Repo (Flask + CLI)

```yaml
input_type: "source_code_repo"
format: "mixed"
app_type: "web"  # Highest priority (web > cli)
source_metadata:
  primary_language: "python"
  framework: "flask"
  file_count: 56
  total_size_bytes: 716800
  entry_points: ["app.py", "cli.py"]
  has_docs: true
  secondary_app_types: ["cli"]  # Secondary type detected
```

---

## Field Value Reference

### Input Type Values

| Value | Description | Detection Signal |
|-------|-------------|------------------|
| `source_code_repo` | Directory with source code | Has package.json, pyproject.toml, Cargo.toml, etc. |
| `documentation_folder` | Directory with only docs | Contains only .md, .rst, .txt files |
| `running_web_app` | Localhost web app | URL matches localhost:*, 127.0.0.1:*, 0.0.0.0:* |
| `public_url` | Public web resource | URL matches https?:// (not localhost) |
| `single_file` | Single file path | Path points to individual file |

### Format Values

| Value | Description | File Extensions |
|-------|-------------|-----------------|
| `markdown` | Markdown docs | .md, .markdown |
| `python` | Python source | .py |
| `javascript` | JavaScript/TypeScript | .js, .jsx, .ts, .tsx |
| `html` | HTML documents | .html, .htm |
| `yaml` | YAML config | .yaml, .yml |
| `json` | JSON data | .json |
| `go` | Go source | .go |
| `rust` | Rust source | .rs |
| `java` | Java source | .java |
| `ruby` | Ruby source | .rb |
| `restructuredtext` | ReStructuredText | .rst |
| `text` | Plain text | .txt, .text |
| `mixed` | Multiple formats | Multiple file types in directory |
| `unknown` | Unrecognized format | No recognized extensions |

### App Type Values

| Value | Description | Detection Signal |
|-------|-------------|------------------|
| `web` | Web application | Flask, Django, Express, React, Rails, Next.js |
| `cli` | Command-line tool | argparse, click, commander, clap |
| `mobile` | Mobile application | React Native, Flutter, Swift, Kotlin |
| `unknown` | Cannot determine | No framework markers |

### Primary Language Values

| Value | Description |
|-------|-------------|
| `python` | Python code |
| `javascript` | JavaScript/TypeScript code |
| `go` | Go code |
| `rust` | Rust code |
| `java` | Java code |
| `ruby` | Ruby code |
| `null` | No code language detected |

### Framework Values

| Value | Language | Type |
|-------|----------|------|
| `flask` | Python | Web |
| `django` | Python | Web |
| `express` | JavaScript | Web |
| `rails` | Ruby | Web |
| `next` | JavaScript | Web |
| `react` | JavaScript | Web |
| `click` | Python | CLI |
| `commander` | JavaScript | CLI |
| `clap` | Rust | CLI |
| `react-native` | JavaScript | Mobile |
| `flutter` | Dart | Mobile |
| `null` | N/A | N/A |

---

## Usage in Code

### Python Example

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class SourceMetadata:
    primary_language: Optional[str]
    framework: Optional[str]
    file_count: int
    total_size_bytes: int
    entry_points: List[str]
    has_docs: bool
    secondary_app_types: List[str]

@dataclass
class InputAnalysis:
    input_type: str
    format: str
    app_type: str
    source_metadata: SourceMetadata

# Example usage
def create_input_analysis(target: str) -> InputAnalysis:
    # ... detection logic ...
    
    metadata = SourceMetadata(
        primary_language="python",
        framework="flask",
        file_count=45,
        total_size_bytes=512000,
        entry_points=["app.py"],
        has_docs=True,
        secondary_app_types=[]
    )
    
    return InputAnalysis(
        input_type="source_code_repo",
        format="mixed",
        app_type="web",
        source_metadata=metadata
    )
```

---

## Validation Rules

| Field | Validation Rule |
|-------|-----------------|
| `input_type` | Must be one of the defined input type values |
| `format` | Must be one of the defined format values |
| `app_type` | Must be one of the defined app type values |
| `source_metadata.primary_language` | Must be one of the defined language values or null |
| `source_metadata.framework` | Must be one of the defined framework values or null |
| `source_metadata.file_count` | Must be non-negative integer |
| `source_metadata.total_size_bytes` | Must be non-negative integer |
| `source_metadata.entry_points` | Must be array of strings (may be empty) |
| `source_metadata.has_docs` | Must be boolean |
| `source_metadata.secondary_app_types` | Must be array of app type values (may be empty) |

---

## References

- **Input Detection Heuristics:** `x-ipe-docs/skill-meta/x-ipe-task-based-application-knowledge-extractor/candidate/references/input-detection-heuristics.md`
- **Technical Design:** `x-ipe-docs/requirements/EPIC-050/FEATURE-050-A/technical-design.md` (InputAnalysis data model)
- **SKILL.md Step 1.1:** `x-ipe-docs/skill-meta/x-ipe-task-based-application-knowledge-extractor/candidate/SKILL.md` (Phase 1, Step 1.1)
