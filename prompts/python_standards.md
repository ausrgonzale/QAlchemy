# Python Standards

**Edition:** Community  
**Version:** 1.0

---

# Purpose

These standards define the Python development practices used when generating, reviewing, or refactoring Python code.

The objective is to produce code that is readable, maintainable, testable, and consistent with modern Python best practices.

---

# Python Philosophy

Write Python that embraces the Zen of Python.

Code should be:

- Explicit rather than implicit.
- Simple rather than complex.
- Easy to understand.
- Easy to maintain.
- Consistent throughout the project.

Favor clarity over cleverness.

---

# Python Version

Generate code compatible with the project's configured Python version.

Use modern language features when they improve readability without sacrificing compatibility.

---

# Project Organization

- Organize modules by responsibility.
- Keep files focused on a single purpose.
- Group related functionality together.
- Avoid unnecessarily large modules.

---

# Naming

Use descriptive names.

| Element | Convention |
|----------|------------|
| Variables | `snake_case` |
| Functions | `snake_case` |
| Methods | `snake_case` |
| Classes | `PascalCase` |
| Constants | `UPPER_CASE` |
| Private members | `_leading_underscore` |

Avoid abbreviations unless they are widely understood.

---

# Imports

- Group imports logically.
- Order imports:
  1. Standard library
  2. Third-party packages
  3. Local project imports
- Prefer explicit imports.
- Remove unused imports.
- Avoid wildcard imports.

---

# Type Hints

Use type hints whenever practical.

Include:

- Parameters
- Return values
- Public attributes
- Collections
- Optional values

Avoid `Any` unless there is no practical alternative.

---

# Documentation

Document public modules, classes, and functions.

Documentation should describe:

- Purpose
- Parameters
- Return values
- Raised exceptions (when appropriate)

Explain behavior rather than implementation.

---

# Functions

Functions should:

- Have a single responsibility.
- Be concise and readable.
- Avoid hidden side effects.
- Return predictable results.

---

# Classes

Classes should represent a single concept.

Prefer composition over inheritance when appropriate.

Avoid unnecessary complexity.

---

# Error Handling

- Raise meaningful exceptions.
- Catch exceptions only when recovery is possible.
- Do not silently ignore failures.
- Provide useful exception messages.

---

# Logging

Use structured logging for application code.

Log:

- Significant events
- Warnings
- Recoverable failures
- Unexpected exceptions

Do not log sensitive information.

---

# File Handling

- Prefer `pathlib.Path`.
- Use context managers.
- Specify text encodings.
- Validate file paths when appropriate.

---

# Configuration

Keep configuration outside source code.

Avoid hardcoded:

- File paths
- Secrets
- API keys
- Environment-specific values

---

# Dependencies

- Prefer the standard library when appropriate.
- Minimize unnecessary dependencies.
- Introduce third-party libraries only when they provide clear value.

---

# Testing

Write code that supports automated testing.

Prefer:

- Fast tests
- Deterministic behavior
- Independent test execution

Mock external dependencies when appropriate.

---

# Review Checklist

Before completing code generation or review, verify that the code:

- Uses descriptive names.
- Includes appropriate type hints.
- Includes useful documentation.
- Uses `pathlib` where appropriate.
- Uses context managers.
- Handles errors consistently.
- Avoids duplicated code.
- Follows the Single Responsibility Principle.
- Is easy to test and maintain.

---

# Summary

Write Python that another experienced developer would immediately recognize as clean, maintainable, and production-ready.

Favor clarity, consistency, and simplicity over clever implementations.