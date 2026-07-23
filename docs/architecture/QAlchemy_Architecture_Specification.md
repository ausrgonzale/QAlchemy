# QAlchemy Architecture Specification

**Version:** 1.1\
**Status:** Approved Design Specification\
**Authority:** Governing Architecture

**Interim Policy (Current Release):**
Application Services may use Python Standard Library logging directly as a
temporary implementation step until LoggerService rollout is completed.

> This document is the authoritative architectural specification for
> QAlchemy. Implementation SHALL conform to this specification. Any
> architectural change SHALL be approved before implementation is
> modified.

------------------------------------------------------------------------

# Table of Contents

1.  Architecture Philosophy
2.  Guiding Principles
3.  Layered Architecture
4.  Infrastructure Foundation
5.  Application Architecture
6.  Infrastructure Architecture
7.  Component Specifications
8.  Logging Architecture
9.  Exception Architecture
10. Runtime Sequences
11. Responsibilities Matrix
12. Architectural Decisions
13. Future Evolution

------------------------------------------------------------------------

# 1. Architecture Philosophy

QAlchemy is designed around a layered architecture that separates
business logic from technical implementation.

Core principles:

-   Services own business logic.
-   Infrastructure Services provide reusable capabilities.
-   Infrastructure Scripts perform low-level implementation.
-   Configuration controls runtime behavior.
-   Architecture drives implementation.
-   Approved architecture is the governing contract.

------------------------------------------------------------------------

# 2. Guiding Principles

  ID       Principle
  -------- ----------------------------------------------
  AP-001   Services own business logic.
  AP-002   Scripts own technical implementation.
  AP-003   Infrastructure is reusable.
  AP-004   Configuration drives runtime behavior.
  AP-005   Logging is a core infrastructure capability.
  AP-006   Code shall conform to architecture.

------------------------------------------------------------------------

# 3. Layered Architecture

``` mermaid
flowchart TD
CLI[Application Scripts]
APP[Application Services]
INF[Infrastructure Services]
SCR[Infrastructure Scripts]
CFG[AppConfigurationService]
FS[(Filesystem)]

CLI --> APP
APP --> INF
INF --> SCR
SCR --> CFG
SCR --> FS
```

------------------------------------------------------------------------

# 4. Infrastructure Foundation

## Underlying Logging Engine

QAlchemy adopts the Python Standard Library **logging** module as the
underlying logging engine.

QAlchemy does **not** replace Python logging.

Instead, it builds an architectural abstraction that standardizes
application logging while delegating persistence to Python's mature
logging framework.

``` text
Application Service
        │
        ▼
LoggerService
        │
        ▼
Logger
        │
        ▼
Python logging
        │
        ▼
Handlers / Files / Console / Future Providers
```

------------------------------------------------------------------------

# 5. Application Architecture

Business Services include:

-   CodeGenerationService
-   CodeReviewService
-   PromptBuilderService
-   PromptLoaderService

Responsibilities:

-   Execute business workflows
-   Orchestrate application behavior
-   Delegate infrastructure work

Business Services SHALL NOT:

-   Perform file persistence
-   Configure logging
-   Perform infrastructure work directly

------------------------------------------------------------------------

# 6. Infrastructure Architecture

Infrastructure Services:

-   LoggerService
-   ExceptionService (future)

Infrastructure Scripts:

-   Logger
-   LoggerConfig
-   Path utilities

Responsibilities:

-   Logging
-   Diagnostics
-   Technical implementation
-   Runtime configuration

------------------------------------------------------------------------

# 7. Component Specifications

## PromptBuilderService

Purpose:

Compose AI prompts.

Owns:

-   Prompt composition
-   Prompt orchestration

Does NOT Own:

-   File I/O
-   AI communication
-   Persistence

Depends On:

-   PromptLoaderService
-   AppConfigurationService

------------------------------------------------------------------------

## LoggerService

Purpose:

Provide the public logging API.

Owns:

-   LogEntry creation
-   Formatting
-   Logging policy
-   Exception logging

Does NOT Own:

-   File writing
-   Handler configuration

------------------------------------------------------------------------

## Logger

Purpose:

Interface with Python logging.

Owns:

-   Logger initialization
-   Handlers
-   Formatters
-   File persistence

Does NOT Own:

-   Business rules
-   Message formatting policy

------------------------------------------------------------------------

## AppConfigurationService

Purpose:

Provide application configuration.

Owns:

-   Reading YAML
-   Producing strongly typed configuration

------------------------------------------------------------------------

# 8. Logging Architecture

Objectives

-   Consistent logging
-   Configuration-driven behavior
-   Centralized formatting
-   Extensibility

Sequence

``` mermaid
sequenceDiagram
participant Service
participant PythonLogging
participant LoggerService
participant Logger

alt Interim (Current Release)
        Service->>PythonLogging: info()/debug()/exception()
else Target State
        Service->>LoggerService: info()/debug()/error()
        LoggerService->>Logger: write()
        Logger->>PythonLogging: log()
end
```

------------------------------------------------------------------------

# 9. Exception Architecture

Current

``` mermaid
flowchart LR
Application-->LoggerService
LoggerService-->Logger
Logger-->PythonLogging
```

Future

``` mermaid
flowchart LR
ExceptionService-->YAMLExceptionCatalog
ExceptionService-->LoggerService
```

------------------------------------------------------------------------

# 10. Runtime Sequences

Business Service Lifecycle

1.  Log start
2.  Read configuration
3.  Execute business logic
4.  Delegate technical work
5.  Log completion
6.  Log exception
7.  Re-raise exception

------------------------------------------------------------------------

# 11. Responsibilities Matrix

  Component                 Owns                    Never Owns
  ------------------------- ----------------------- ----------------
  Business Services         Business logic          Infrastructure
  LoggerService             Logging behavior        File I/O
  Logger                    Persistence             Business logic
  LoggerConfig              Runtime configuration   YAML parsing
  AppConfigurationService   Configuration           Logging

------------------------------------------------------------------------

# 12. Architectural Decisions

## AD-001

Services SHALL own business logic.

## AD-002

Infrastructure SHALL provide reusable technical capabilities.

## AD-003

Application Services SHALL delegate infrastructure work.

## AD-004

Application Services SHOULD log through LoggerService.

Interim release allowance:
- Application Services MAY log directly with Python Standard Library
        logging until LoggerService integration is complete.
- Services using interim logging SHALL still follow the business service
        lifecycle (start, key operations, completion, exception logging,
        and re-raise behavior).

## AD-005

LoggerService SHALL delegate persistence to Logger.

## AD-006

Logger SHALL use Python Standard Library logging.

## AD-007

Business Services SHALL NOT write directly to log files.

## AD-008

Python Standard Library logging SHALL remain the underlying logging
engine.

## AD-009

Future logging providers SHALL integrate beneath Logger.

## AD-010

Future exception handling SHALL consume LoggerService.

------------------------------------------------------------------------

# 13. Future Evolution

Planned enhancements:

-   YAML Exception Catalog
-   Structured logging
-   JSON logging
-   OpenTelemetry
-   Splunk integration
-   REST diagnostics
-   Cloud logging providers
-   MCP integration

The public contracts of Application Services SHALL remain stable while
the infrastructure layer evolves.
