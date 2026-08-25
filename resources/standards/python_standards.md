# Python Standards
**QAlchemy Community Edition**  
**Version:** 1.0

---

# 1. Purpose

This document defines the **Python Reference Standards** used by QAlchemy Community Edition when generating, reviewing, and analyzing Python source code.

These standards represent production-ready engineering practices that emphasize readability, maintainability, consistency, and long-term supportability.

## Reference Standard

QAlchemy includes built-in Python reference standards that are applied by default.

If project-specific Python standards are available, they should be applied in place of the corresponding reference standards.

The objective is to provide high-quality Python implementations out of the box while allowing projects to define their own engineering conventions when necessary.

---

# 2. Python Engineering Philosophy

Generated Python should follow these guiding principles.

| Principle | Description |
|------------|-------------|
| Readability | Code should be easy to understand by humans. |
| Simplicity | Prefer straightforward solutions over clever implementations. |
| Explicitness | Make behavior obvious rather than implied. |
| Maintainability | Optimize for long-term support. |
| Reusability | Reuse existing components before creating new ones. |
| Consistency | Follow established project patterns. |
| Production Ready | Generate code suitable for production environments. |

Whenever multiple valid implementations exist, prefer the implementation that best satisfies these principles.

---

# 3. General Coding Standards

## Naming Conventions

| Element | Convention |
|----------|------------|
| Modules | `snake_case.py` |
| Packages | `snake_case` |
| Functions | `snake_case()` |
| Variables | `snake_case` |
| Classes | `PascalCase` |
| Constants | `UPPER_CASE` |
| Private Members | `_leading_underscore` |

---

## Imports

Prefer:

- Standard library imports first
- Third-party imports second
- Local imports last

Avoid wildcard imports.

Import only what is required.

---

## Type Hints

Public APIs should include type hints whenever practical.

Example:

```python
def load_configuration(path: Path) -> AppConfiguration:
```

---

## Docstrings

Document:

- public modules
- public classes
- public methods
- public functions

Follow PEP 257 conventions.

---

## Comments

Comments should explain **why**, not **what**.

Prefer expressive code over excessive comments.

---

## Formatting

Generated Python should follow PEP 8.

Prefer consistent formatting throughout the project.

---

# 4. Project Architecture

QAlchemy encourages separation of responsibilities.

```text
Scripts
    │
    ▼
Services
    │
    ▼
Clients / Utilities
```

## Scripts

Scripts should:

- orchestrate workflows
- handle command-line interaction
- perform file I/O
- coordinate services

Scripts should avoid business logic.

---

## Services

Services should:

- encapsulate reusable business logic
- expose clear interfaces
- remain independent of CLI interaction
- minimize external side effects

---

## Clients

Clients communicate with external systems.

Examples:

- AI Providers
- REST APIs
- Databases
- Cloud Services

---

## Utilities

Utilities should contain reusable helper functionality that is not business specific.

---

# 5. Dependency Management

Prefer:

- constructor dependency injection
- explicit dependencies
- loosely coupled components

Avoid:

- hidden dependencies
- global mutable state
- circular imports
- tightly coupled implementations

---

# 6. Logging

## Reference Standard

Unless project-specific logging standards are provided, use Python's standard `logging` package.

### Preferred Practices

- Create module loggers using `logging.getLogger(__name__)`
- Configure logging once during application startup
- Use appropriate log levels
- Log meaningful operational events
- Include sufficient context for troubleshooting

### Logging Levels

| Level | Usage |
|--------|------|
| DEBUG | Detailed diagnostic information |
| INFO | Normal application events |
| WARNING | Unexpected but recoverable situations |
| ERROR | Failed operations |
| CRITICAL | Application cannot safely continue |

### Prefer

| Prefer | Avoid |
|----------|-------|
| Module loggers | print() statements |
| Structured log messages | Generic messages |
| Central configuration | Per-module configuration |
| Appropriate log levels | Logging everything as INFO |

### Logging Flow

```text
Operation
     │
     ▼
Should this event be logged?
     │
 Yes─┴─No
 │
 ▼
Select Appropriate Log Level
 │
 ▼
Write Structured Log Entry
```

If project-specific logging standards exist, they supersede these reference standards.

---

# 7. Exception Handling

## Reference Standard

Unless project-specific exception handling standards are supplied, use Python's built-in exception hierarchy.

### Preferred Practices

- Raise the most specific exception available.
- Preserve exception context.
- Handle exceptions only when meaningful recovery is possible.
- Allow unrecoverable exceptions to propagate to the application boundary.

### Exception Reference

| Situation | Preferred Exception |
|-----------|--------------------|
| Invalid argument | ValueError |
| Missing file | FileNotFoundError |
| Missing dictionary key | KeyError |
| Unsupported feature | NotImplementedError |
| Business-specific condition | Custom Exception (when appropriate) |

### Avoid

- swallowing exceptions
- broad `except Exception`
- silent failures
- using exceptions for normal program flow

### Exception Flow

```text
Failure
   │
   ▼
Can caller recover?
   │
Yes────No
 │       │
 ▼       ▼
Raise    Allow Exception
Specific to Propagate
Exception
```

If project-specific exception handling standards exist, they supersede these reference standards.

---

# 8. Unit Testing

## Reference Standard

Unless project-specific testing standards are supplied, use **pytest**.

### Testing Philosophy

Generated code should be testable.

Unit tests should:

- validate one unit of behavior
- execute independently
- be deterministic
- execute quickly
- avoid external dependencies whenever practical

### Arrange–Act–Assert

```text
Arrange
    │
    ▼
Act
    │
    ▼
Assert
```

### Preferred Practices

| Prefer | Avoid |
|----------|-------|
| pytest | Multiple testing frameworks |
| Fixtures | Duplicate setup |
| Mock external systems | Mock business logic |
| Deterministic tests | Timing-based tests |
| Independent execution | Test ordering dependencies |

### Test Coverage

Unit tests should validate:

- normal behavior
- input validation
- expected exceptions
- edge cases
- boundary conditions

Whenever practical, generated features should include corresponding unit tests.

If project-specific testing standards exist, they supersede these reference standards.

---

# 9. Documentation

Document public interfaces.

Prefer:

- meaningful module docstrings
- class documentation
- public API documentation
- self-documenting code

Avoid excessive comments that duplicate the code.

---

# 10. Performance

Correctness should always precede optimization.

Prefer:

- readable implementations
- maintainable algorithms
- measured optimization

Avoid premature optimization.

---

# 11. Security

Generated Python should follow secure coding practices.

Prefer:

- validating external input
- protecting sensitive information
- avoiding hardcoded secrets
- sanitizing file paths
- using safe library APIs

If project-specific security standards exist, they supersede these reference standards.

---

# 12. AI Generation Guidance

When generating Python, the AI should:

- produce production-ready code
- reuse existing services whenever possible
- follow the established project architecture
- minimize duplication
- apply logging appropriately
- use meaningful exception handling
- generate maintainable implementations
- generate unit tests when appropriate

The AI should avoid:

- inventing new architectural patterns without justification
- duplicating existing functionality
- introducing unnecessary complexity
- violating project-specific standards

---

# 13. Summary

| Area | Community Reference Standard |
|------|-------------------------------|
| Formatting | PEP 8 |
| Docstrings | PEP 257 |
| Logging | Python `logging` |
| Exception Handling | Built-in exception hierarchy |
| Unit Testing | pytest |
| Dependency Management | Constructor Injection |
| Architecture | Scripts → Services → Clients / Utilities |
| Type Hints | Recommended for public APIs |
| Security | Secure coding practices |
| Performance | Correctness before optimization |

---

# Final Note

This document defines the Python reference standards used by QAlchemy Community Edition.

These standards provide a consistent engineering baseline for Python development. When project-specific standards are available, they should be applied in preference to the corresponding reference standards described here.