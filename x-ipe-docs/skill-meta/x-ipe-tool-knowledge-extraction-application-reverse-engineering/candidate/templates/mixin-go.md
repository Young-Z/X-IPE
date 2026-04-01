# Application RE — Go Language Mixin

> Apply this mixin when the target codebase contains Go source code.
> Merge these into the base playbook and collection templates when mixin_key: go.
> This is an additive overlay — it does NOT replace repo-type mixin content.

---

## Detection Signals

| Signal | File/Pattern | Confidence |
|--------|-------------|------------|
| Go files | `*.go` files present | high |
| go.mod | `go.mod` at root | high |
| go.sum | `go.sum` at root | high |
| Go directory layout | `cmd/`, `internal/`, `pkg/` directories | medium |
| Go test files | `*_test.go` files | medium |

---

## Section Overlay Prompts

### For Section 2 (Design Pattern Detection)
<!-- ADDITIONAL PROMPTS:
- Detect Go-idiomatic patterns:
  Interface satisfaction: implicit interfaces (no "implements" keyword)
  Functional options: func WithX(val) Option pattern
  Table-driven tests: []struct{name, input, want} test tables
  Middleware: func(http.Handler) http.Handler chaining
  Error wrapping: fmt.Errorf("%w", err) chains
- Detect goroutine patterns: go func(), sync.WaitGroup, errgroup
- Detect channel patterns: producer/consumer, fan-in/fan-out, select{}
- Look for context.Context propagation patterns
- Check for code generation: go:generate directives, generated files
-->

### For Section 3 (API Contracts)
<!-- ADDITIONAL PROMPTS:
- Extract net/http handlers: http.HandleFunc, http.Handle
- Extract Gin handlers: router.GET(), router.POST(), gin.Context
- Extract Echo handlers: e.GET(), e.POST(), echo.Context
- Extract Chi routes: r.Get(), r.Post(), r.Route()
- Document exported function signatures (capitalized = public)
- Parse struct tags for JSON/XML serialization contracts
-->

### For Section 5 (Code Structure)
<!-- ADDITIONAL PROMPTS:
- Identify Go standard project layout:
  cmd/ — application entry points
  internal/ — private packages (not importable externally)
  pkg/ — public library packages
  api/ — API definitions (proto, OpenAPI)
- Document package naming conventions (short, lowercase, no underscores)
- Identify init() functions and their effects
- Note build tags / constraints (//go:build)
-->

### For Section 7 (Technology Stack)
<!-- ADDITIONAL PROMPTS:
- Parse go.mod for module path and Go version
- Parse go.sum for exact dependency versions
- Identify HTTP framework: stdlib net/http, Gin, Echo, Chi, Fiber
- Identify ORM/database: GORM, sqlx, ent, database/sql
- Detect code generation tools: protoc, mockgen, wire, ent
- Identify linting: golangci-lint configuration (.golangci.yml)
-->

### For Section 8 (Source Code Tests)
<!-- ADDITIONAL PROMPTS:
- Go tests are always *_test.go in same package
- Detect testing framework: stdlib testing, testify, gomock, gomega
- Identify table-driven test pattern usage
- Check for test helpers: t.Helper(), testmain
- Identify integration test build tags (//go:build integration)
- Check for coverage: go test -cover output
-->
