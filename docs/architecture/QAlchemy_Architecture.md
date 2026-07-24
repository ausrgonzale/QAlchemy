# Version >= 1.1

# QAlchemy Architecture

**Status:** Active  
**Audience:** Architects, Engineers, Contributors  
**Last Updated:** July 2026

---

# 1. Purpose

This document describes the overall architecture of the QAlchemy application.

It defines the major architectural components, their responsibilities, and how they interact. It intentionally avoids implementation details, algorithms, and coding standards. Those are documented in the Design Specifications.

This document answers the question:

> **What is QAlchemy and how is it organized?**

---

# 2. Architectural Principles

QAlchemy is designed around a small set of engineering principles.

## Separation of Concerns

Each component has a single well-defined responsibility.

Business logic, AI interaction, configuration, logging, reporting, and exception handling remain independent services.

---

## Service-Oriented Architecture

Application functionality is implemented through reusable services.

Services communicate through well-defined interfaces and remain loosely coupled.

---

## Configuration Driven

Application behavior is controlled through configuration rather than hard-coded values.

No component should depend on implementation-specific paths, filenames, models, or providers.

---

## AI Provider Independence

AI functionality is accessed through a common abstraction.

Application features never communicate directly with a specific AI provider.

---

## Testability

Every service is designed to support automated unit testing and feature validation.

---

## Extensibility

New AI providers, services, prompts, and engineering capabilities can be added with minimal impact to existing components.

---

# 3. Architectural Overview

```
                    +----------------------+
                    |      CLI Scripts     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |  Feature Services    |
                    +----------+-----------+
                               |
             +-----------------+------------------+
             |                 |                  |
             v                 v                  v
     Configuration       Prompt Builder     Reporting
             |                 |                  |
             +-----------------+------------------+
                               |
                               v
                     AI Client Builder
                               |
                               v
                       AI Provider Layer
```

Cross-cutting services:

```
Logging Service
Exception Handling Service
```

These services are available throughout the application.

---

# 4. High-Level Components

## CLI Scripts

Scripts provide the user-facing entry points into QAlchemy.

Examples include:

- Code Generation
- Code Review
- Validation
- Demonstrations

Scripts contain minimal business logic and delegate work to services.

---

## Feature Services

Feature Services implement the primary capabilities of the application.

Current services include:

- CodeGenerationService
- CodeReviewService

Future services may include:

- RequirementsService
- DocumentationService
- WorkflowService

---

## Core Services

Core services provide reusable infrastructure shared across the application.

Current core services include:

- AppConfigurationService
- PromptBuilderService
- PromptLoaderService
- AIClientBuilderService
- LoggerService
- ExceptionHandlingService
- ReportWriter

---

## AI Provider Layer

The AI Provider Layer isolates the application from specific AI vendors.

Current implementations include:

- Ollama

Future providers may include:

- OpenAI
- Azure OpenAI
- Anthropic
- Google Gemini
- Local LLMs
- MCP-enabled providers

---

# 5. Cross-Cutting Services

Certain services are available to every subsystem.

---

## Configuration

Provides centralized application configuration.

Responsibilities include:

- Reading configuration
- Validation
- Strongly typed configuration objects
- Runtime configuration access

---

## Logging

Provides centralized logging throughout the application.

Responsibilities include:

- Structured logging
- Configurable output
- Standard formatting
- Future observability integration

---

## Exception Handling

Provides consistent application error handling.

Responsibilities include:

- Standard exception catalog
- Error message formatting
- Logging integration
- Standardized exception codes

---

## Reporting

Responsible for producing user-facing reports.

Examples include:

- Code Review Reports
- Validation Reports
- Future Analysis Reports

---

# 6. Runtime Flow

A typical execution follows this sequence.

```
User

  |

CLI Script

  |

Feature Service

  |

Prompt Builder

  |

AI Client Builder

  |

AI Provider

  |

Response

  |

Report Writer

  |

Output
```

During execution:

- Configuration is available globally.
- Logging records application activity.
- Exception Handling manages failures.

---

# 7. Layered Architecture

```
+------------------------------------+
|          User Interface            |
|         (CLI / Validation)         |
+------------------------------------+

+------------------------------------+
|         Feature Services           |
+------------------------------------+

+------------------------------------+
|          Core Services             |
+------------------------------------+

+------------------------------------+
|        AI Provider Layer           |
+------------------------------------+

+------------------------------------+
|      External AI Providers         |
+------------------------------------+
```

Dependencies always flow downward.

Lower layers never depend upon higher layers.

---

# 8. Current Feature Set

Version 1.1 provides the following user-facing capabilities.

### Code Generation

Generate source code using configurable AI providers.

---

### Code Review

Perform automated source code reviews.

---

### Validation

Execute feature validation scripts.

---

### Reporting

Generate Markdown reports.

---

# 9. Planned Evolution

The architecture is intentionally designed to support future capabilities without requiring structural redesign.

Planned additions include:

- Requirements Management
- Documentation Generation
- REST API
- MCP Integration
- Multi-Agent Workflows
- IDE Integration
- SaaS Deployment

These capabilities will extend the existing architecture rather than replace it.

---

# 10. Architectural Boundaries

The architecture document intentionally excludes implementation details.

The following topics are documented separately:

- Engineering standards
- Coding standards
- Design specifications
- Prompt and instruction assets
- Testing standards
- Feature validation

---

# 11. Related Documentation

| Document | Purpose |
|----------|---------|
| QAlchemy_Design.md | Application engineering design and subsystem overview |
| QAlchemy_Exception_Handling_Design.md | Detailed exception handling design |
| Engineering Standards | Engineering policies and development practices |
| Testing Standards | Unit and feature validation requirements |

---

# 12. Summary

QAlchemy is a modular, service-oriented AI engineering application designed to produce maintainable, testable, and extensible AI-powered software solutions.

Its architecture separates application features from infrastructure concerns while maintaining clear boundaries between configuration, AI interaction, logging, exception handling, reporting, and future expansion.

The architecture is intentionally stable so that future capabilities can be introduced by extending existing services rather than redesigning the application.