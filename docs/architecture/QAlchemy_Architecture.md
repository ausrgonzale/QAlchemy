# Version >= 1.1

# QAlchemy Architecture

---

# Purpose

Provide a high-level architectural view of the QAlchemy application.

This document describes the application's organization, runtime architecture, startup lifecycle, and major architectural components.

Implementation details and architectural rationale are documented in **Architecture_Design.md**.

---

# Overall Architecture

```mermaid
flowchart TD

    Host["Host Applications<br/>Scripts • Tests • CLI • REST • MCP"]

    Bootstrap["ApplicationBootstrapService<br/><i>Composition Root</i>"]

    Feature["Feature Services"]

    Core["Core Services"]

    Infrastructure["Infrastructure"]

    Host --> Bootstrap
    Bootstrap --> Feature
    Feature --> Core
    Core --> Infrastructure
```

---

# Package Organization

```mermaid
flowchart TB

    Root["QAlchemy"]

    Root --> Services
    Root --> Scripts
    Root --> Config
    Root --> Prompts
    Root --> Templates
    Root --> Reports
    Root --> Tests
    Root --> Docs

    Services --> Application
    Services --> Core
    Services --> Feature

    Application --> Bootstrap["ApplicationBootstrapService"]

    Core --> Configuration["AppConfigurationService"]
    Core --> PromptLoader["PromptLoaderService"]
    Core --> PromptBuilder["PromptBuilderService"]
    Core --> Logger["LoggerService"]
    Core --> Exception["ExceptionService"]
    Core --> AIBuilder["AIClientBuilderService"]
    Core --> Preprocessor["SourceCodePreprocessingService"]

    Feature --> Generator["CodeGenerationService"]
    Feature --> Reviewer["CodeReviewService"]
```

---

# Layered Architecture

```mermaid
flowchart TD

    Host["Host Layer"]

    Application["Application Layer"]

    Feature["Feature Layer"]

    Core["Core Layer"]

    Infrastructure["Infrastructure Layer"]

    Host --> Application
    Application --> Feature
    Feature --> Core
    Core --> Infrastructure
```

---

# Application Startup Lifecycle

```mermaid
sequenceDiagram

    participant Host
    participant Bootstrap
    participant Generation
    participant Review

    Host->>Bootstrap: bootstrap()

    Bootstrap->>Bootstrap: Validate Startup

    Bootstrap->>Bootstrap: Instantiate Feature Services

    Bootstrap-->>Host: Initialized ApplicationBootstrapService

    Host->>Generation: generate()

    Host->>Review: review()
```

---

# Application Bootstrap

```mermaid
flowchart LR

    Start([Application Start])

    Config["Load Configuration"]

    Validation["Validate Configuration"]

    Services["Instantiate Feature Services"]

    Ready([Application Ready])

    Start --> Config
    Config --> Validation
    Validation --> Services
    Services --> Ready
```

---

# Runtime Architecture

```mermaid
flowchart LR

    Bootstrap["ApplicationBootstrapService"]

    Generation["CodeGenerationService"]

    Review["CodeReviewService"]

    Core["Core Services"]

    Bootstrap --> Generation
    Bootstrap --> Review

    Generation --> Core
    Review --> Core
```

---

# Core Services

```mermaid
flowchart TB

    Core["Core Services"]

    Core --> Configuration["AppConfigurationService"]

    Core --> PromptLoader["PromptLoaderService"]

    Core --> PromptBuilder["PromptBuilderService"]

    Core --> AIBuilder["AIClientBuilderService"]

    Core --> Logger["LoggerService"]

    Core --> Exception["ExceptionService"]

    Core --> Preprocessor["SourceCodePreprocessingService"]
```

---

# Feature Services

```mermaid
flowchart TB

    Features["Feature Services"]

    Features --> Generation["CodeGenerationService"]

    Features --> Review["CodeReviewService"]
```

---

# Dependency Direction

```mermaid
flowchart TD

    Host

    Application

    Feature

    Core

    Infrastructure

    Host --> Application

    Application --> Feature

    Feature --> Core

    Core --> Infrastructure
```

---

# Dependency Rules

| Allowed               | Not Allowed              |
| --------------------- | ------------------------ |
| Host → Application    | Feature → Application    |
| Application → Feature | Core → Application       |
| Feature → Core        | Core → Feature           |
| Core → Infrastructure | Infrastructure → Feature |

---

# Current Application Host

```mermaid
flowchart LR

    Test["test_e2e_qalchemy.py"]

    Bootstrap["ApplicationBootstrapService"]

    Generation["CodeGenerationService"]

    Review["CodeReviewService"]

    Test --> Bootstrap

    Bootstrap --> Generation

    Bootstrap --> Review
```

---

# Future Host Applications

```mermaid
flowchart TB

    Bootstrap["ApplicationBootstrapService"]

    Bootstrap --> E2E["test_e2e_qalchemy.py"]

    Bootstrap --> Generate["generate_code.py"]

    Bootstrap --> Review["review_source_code.py"]

    Bootstrap --> Demo["demo.py"]

    Bootstrap --> CLI["CLI Host"]

    Bootstrap --> REST["REST Host"]

    Bootstrap --> MCP["MCP Host"]
```

---

# Architecture Evolution

```mermaid
flowchart LR

    V11["v1.1<br/>Bootstrap Service<br/>Used by E2E"]

    V12["v1.2<br/>Helper Scripts<br/>Use Bootstrap"]

    Future["Future<br/>CLI • REST • MCP • Plugins"]

    V11 --> V12

    V12 --> Future
```

---

# Architectural Principles

```mermaid
mindmap
  root((QAlchemy))
    Layered Architecture
    Service-Oriented Design
    Composition Root
    Separation of Concerns
    Configuration Driven
    Low Coupling
    High Cohesion
    Thin Host Applications
    Reusable Core Services
```

---

# Related Documents

* Architecture_Design.md
* ApplicationBootstrapService Blueprint
* Service Blueprints
* Design Specifications
* README.md
