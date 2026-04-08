# Section 08 — Source Code Tests

## Test Coverage Status

**No automated tests found.** The ontology-1.0.4 skill package does not include a test suite.

## Validation as Implicit Testing

The `validate` command (`ontology.py validate`) serves as a runtime correctness check:

| Validation | What It Checks |
|------------|---------------|
| Required properties | Entities must have all required fields per schema |
| Forbidden properties | Credential entities reject `password`, `secret`, `token`, `key`, `api_key` |
| Enum constraints | Field values must match defined enums (e.g., Task status) |
| Relation type safety | `from`/`to` entity types must match relation schema |
| Cardinality enforcement | `one_to_one`, `one_to_many`, `many_to_one` limits |
| Acyclicity | DFS cycle detection for relations marked `acyclic: true` |
| Event time ordering | `end >= start` for Event entities |

## Testability Assessment

| Aspect | Testable | Notes |
|--------|----------|-------|
| Entity CRUD | ✅ Easy | Pure functions with file I/O; can mock with temp files |
| Relation operations | ✅ Easy | Same pattern as entity CRUD |
| Query/filter | ✅ Easy | Deterministic given a fixed JSONL input |
| Validation engine | ✅ Easy | Returns error list; schema can be constructed in-memory |
| Schema merge | ✅ Easy | Pure dict merge — no side effects beyond file write |
| Path safety | ✅ Easy | `resolve_safe_path()` is a pure function |
| CLI dispatch | ⚠️ Medium | Needs argparse mocking or subprocess call |

## Recommended Test Cases (Not Implemented)

1. Create entity → verify JSONL record written
2. Create + query → verify round-trip
3. Relate + get_related → verify traversal directions
4. Validate with missing required property → expect error
5. Validate with forbidden property on Credential → expect error
6. Validate with cyclic `blocks` relation → expect error
7. Schema merge with overlapping keys → verify deep merge
8. `resolve_safe_path` with `../` traversal → expect SystemExit
