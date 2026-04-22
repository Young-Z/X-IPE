# Dimension Naming Guidelines

Guidelines for AI agents when discovering and naming dimensions during Operation A (Tag).

## Canonical Naming Rules

1. **Use lowercase with hyphens** for multi-word dimensions: `tech-stack`, `design-pattern`
2. **Prefer singular form**: `technology` not `technologies`
3. **Be specific but not overly narrow**: `security` not `auth-security`
4. **Check the registry first**: Always call `dimension_registry.py resolve` before creating new dimensions

## Standard Dimensions

These are commonly used dimensions across knowledge bases:

| Dimension | Type | Description | Examples |
|-----------|------|-------------|----------|
| `technology` | multi-value | Programming languages, frameworks, tools | Python, React, Docker |
| `domain` | multi-value | Business or technical domains | security, backend, frontend |
| `abstraction` | single-value | Level of abstraction | pattern, implementation, specification |
| `audience` | multi-value | Target audience | developers, architects, beginners |
| `lifecycle` | single-value | Development lifecycle stage | design, implementation, testing |
| `complexity` | single-value | Complexity level | basic, intermediate, advanced |

## Alias Resolution

When the registry returns `{"canonical": null}`, the dimension is new. Before registering:

1. Check if the concept is covered by an existing dimension under a different name
2. Consider whether it should be a value within an existing dimension instead
3. If truly new, register with at least 2 aliases and 3 examples

## Example: Tagging a Source File

Given file `src/auth/jwt_handler.py` with JWT implementation:

```json
{
    "label": "JWT Token Handler",
    "node_type": "entity",
    "description": "Handles JWT token creation, validation, and refresh",
    "dimensions": {
        "technology": ["Python", "JWT", "PyJWT"],
        "domain": ["security", "authentication"],
        "abstraction": "implementation",
        "audience": ["developers"]
    },
    "source_files": ["src/auth/jwt_handler.py"],
    "weight": 7
}
```
