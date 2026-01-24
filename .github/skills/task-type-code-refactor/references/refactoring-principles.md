# Refactoring Principles by Application Type

> Reference from SKILL.md: `See [references/refactoring-principles.md](references/refactoring-principles.md)`

---

## Web Application (Frontend)

```
1. Component Isolation - Each component in its own file
2. State Management Separation - Logic separated from UI
3. Style Colocation - CSS/styles with components OR in dedicated files
4. Utility Extraction - Shared helpers in utils/
5. API Layer Abstraction - All API calls in services/
6. Type Safety - Interfaces/types in dedicated files
```

### Example Structure
```
src/
├── components/
│   ├── Header/
│   │   ├── Header.tsx
│   │   ├── Header.css
│   │   └── index.ts
│   └── UserCard/
│       ├── UserCard.tsx
│       └── UserCard.css
├── services/
│   ├── api.ts
│   └── userService.ts
├── utils/
│   ├── formatters.ts
│   └── validators.ts
└── types/
    └── index.ts
```

---

## Web Application (Backend)

```
1. Route/Controller Separation - Routes in routes/, handlers in controllers/
2. Service Layer - Business logic in services/
3. Repository Pattern - Data access abstracted
4. Middleware Extraction - Cross-cutting concerns isolated
5. Config Centralization - All config in config/
6. Error Handling Standardization - Consistent error types
```

### Example Structure (Python Flask)
```
src/
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py
│   └── user_routes.py
├── controllers/
│   ├── auth_controller.py
│   └── user_controller.py
├── services/
│   ├── auth_service.py
│   └── user_service.py
├── repositories/
│   └── user_repository.py
├── middleware/
│   ├── auth_middleware.py
│   └── error_handler.py
└── config/
    └── settings.py
```

### Example Structure (Node.js Express)
```
src/
├── routes/
│   ├── index.js
│   ├── authRoutes.js
│   └── userRoutes.js
├── controllers/
│   ├── authController.js
│   └── userController.js
├── services/
│   ├── authService.js
│   └── userService.js
├── repositories/
│   └── userRepository.js
├── middleware/
│   ├── authMiddleware.js
│   └── errorHandler.js
└── config/
    └── settings.js
```

---

## CLI Application

```
1. Command Pattern - Each command in separate file
2. Input/Output Abstraction - IO operations isolated
3. Config Management - Settings separated from logic
4. Plugin Architecture - Extensible command system
5. Help/Documentation - Self-documenting commands
```

### Example Structure
```
src/
├── commands/
│   ├── __init__.py
│   ├── init.py
│   ├── build.py
│   └── deploy.py
├── io/
│   ├── console.py
│   └── file_io.py
├── config/
│   ├── settings.py
│   └── defaults.py
└── plugins/
    └── plugin_loader.py
```

---

## Library/Package

```
1. Public API Surface - Clear exports in index
2. Internal Modules - Private implementation hidden
3. Type Definitions - Full TypeScript/type hints
4. Documentation - JSDoc/docstrings on public API
5. Backward Compatibility - Version-safe changes
```

### Example Structure
```
src/
├── __init__.py          # Public API exports
├── public_api.py        # Main public interface
├── _internal/           # Private implementation (underscore prefix)
│   ├── __init__.py
│   ├── _parser.py
│   └── _transformer.py
├── types/
│   └── __init__.py      # Type definitions
└── py.typed             # PEP 561 marker
```

---

## Monolith to Modules

```
1. Domain Boundaries - Split by business domain
2. Dependency Direction - Core modules have no external deps
3. Interface Segregation - Small, focused interfaces
4. Shared Kernel - Common code in shared/
5. Anti-Corruption Layer - Adapters for external systems
```

### Example Structure
```
src/
├── core/                    # No external dependencies
│   ├── entities/
│   └── interfaces/
├── domains/
│   ├── users/
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── models.py
│   ├── products/
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── models.py
│   └── orders/
│       ├── service.py
│       └── models.py
├── shared/                  # Common utilities
│   ├── utils.py
│   └── exceptions.py
└── adapters/                # Anti-corruption layer
    ├── payment_gateway.py
    └── shipping_provider.py
```

---

## Principle Selection Guide

| Application Type | Start With | Add As Needed |
|------------------|------------|---------------|
| Frontend | Component Isolation, State Separation | Type Safety, API Layer |
| Backend | Service Layer, Route Separation | Repository Pattern, Config |
| CLI | Command Pattern, Config Management | Plugin Architecture |
| Library | Public API Surface, Type Definitions | Backward Compatibility |
| Monolith | Domain Boundaries, Shared Kernel | Anti-Corruption Layer |
