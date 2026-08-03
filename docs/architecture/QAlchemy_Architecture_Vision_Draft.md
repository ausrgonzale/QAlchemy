# QAlchemy Architecture Documentation Vision

**Status:** Draft for Review\
**Purpose:** Define the philosophy, structure, and content of the
production Architecture.md for QAlchemy Version 1.

------------------------------------------------------------------------

# Mission

The Architecture document is the engineering blueprint for QAlchemy.

It defines the intended platform architecture---not the current
implementation. Every design decision, service design document,
implementation, and test should trace back to this document.

------------------------------------------------------------------------

# Documentation Philosophy

## Less is More

Every page must reduce uncertainty.

Prefer:

-   Diagrams
-   Relationship maps
-   Dependency matrices
-   Tables

Avoid lengthy narrative whenever a visual communicates the same
information.

------------------------------------------------------------------------

# Architecture Objectives

The document should answer:

1.  What is QAlchemy?
2.  What capabilities does it provide?
3.  How are responsibilities divided?
4.  How do services collaborate?
5.  Where are integration boundaries?
6.  Where can failures occur?
7.  How does work flow through the platform?
8.  What is implemented versus planned?

If these questions cannot be answered quickly, the architecture should
be improved.

------------------------------------------------------------------------

# Proposed Architecture.md Structure

1.  Vision
2.  Architectural Principles
3.  Layered Architecture
4.  Capability Map
5.  Core Services
6.  Engineering Services
7.  Service Relationship Diagram (ERD Style)
8.  Processing Workflow
9.  Integration Boundaries
10. Failure Propagation
11. Feature ↔ Core Service Dependency Matrix
12. External Integration Matrix
13. Service Status Matrix
14. Repository Structure
15. Roadmap

------------------------------------------------------------------------

# Core Service Dependency Matrix

  -------------------------------------------------------------------------------------------------------------------------------
  Feature Service        Bootstrap   Config   Prompt     AI     Artifact    File    Logger   Exception   Reporting  Dependency
                                                       Client              Writer                                   Summary
  --------------------- ----------- -------- -------- -------- ---------- -------- -------- ----------- ----------- -------------
  ReqEvalService             ✓         ✓        ✓        ✓         ✓         ✓        ✓          ✓           ○      Produces
                                                                                                                    engineering
                                                                                                                    artifacts.

  CodeGenService             ✓         ✓        ✓        ✓         ✓         ✓        ✓          ✓           ✓      Generates
                                                                                                                    production
                                                                                                                    code.

  CodeRevService             ✓         ✓        ✓        ✓         ✓         ✓        ✓          ✓           ✓      Produces
                                                                                                                    review
                                                                                                                    reports.

  TestGenService             ✓         ✓        ✓        ✓         ✓         ✓        ✓          ✓           ✓      Planned.

  DocGenService              ✓         ✓        ✓        ✓         ✓         ✓        ✓          ✓           ✓      Planned.

  DefectTriageService        ○         ○        ○        ○         ○         ○        ○          ○           ○      Planned for
                                                                                                                    V1.x.
  -------------------------------------------------------------------------------------------------------------------------------

Legend:

-   [x] Required
-   ○ Planned
-   --- Not Applicable

------------------------------------------------------------------------

# Integration Philosophy

Every external integration shall identify:

-   Integration owner
-   Boundary
-   Inputs
-   Outputs
-   Failure points
-   Recovery owner

Integration arrows alone are insufficient.

------------------------------------------------------------------------

# Failure Architecture

Each workflow documents:

-   Detection point
-   Logging point
-   Exception owner
-   Recovery strategy
-   User-visible outcome

Failure behavior is considered part of the architecture.

------------------------------------------------------------------------

# Architectural Relationships

Represent service collaboration using ERD-style diagrams rather than
only component diagrams.

The emphasis is ownership, collaboration, and dependency---not
implementation files.

------------------------------------------------------------------------

# Visual-First Standard

Every major section begins with a visual artifact:

-   Capability Diagram
-   Component Diagram
-   ERD Relationship Diagram
-   Sequence Diagram
-   Dependency Matrix
-   Integration Matrix
-   Failure Flow

Text explains the visuals instead of replacing them.

------------------------------------------------------------------------

# Validation Checklist

Before Architecture.md is considered complete:

-   Every Core Service is represented.
-   Every Engineering Service is represented.
-   Planned services are visible.
-   Integration boundaries are identified.
-   Failure paths are documented.
-   Dependency matrices are complete.
-   Repository structure matches implementation.
-   Architecture aligns with current service designs and workflows.

------------------------------------------------------------------------

# Review Against Current Project

Review of the current project archive indicates:

-   Strong separation between Core and Feature services.
-   Dedicated LoggerService and ExceptionService designs.
-   Requirements Evaluation design establishing downstream
    orchestration.
-   AI generation workflow emphasizing architecture-first
    implementation.
-   Existing architecture already defines layered architecture but can
    be expanded with richer relationship, dependency, and failure views.

These observations support evolving the Architecture.md into a visual
engineering blueprint rather than a descriptive reference.
