# QAlchemy Architecture --- Current Implementation (v1.2)

## Purpose and scope

QAlchemy is a configuration-driven Python application for running
AI-assisted engineering workflows. Its central runtime contract is the
immutable `WorkOrder`: a normalized description of a request that
feature services use to produce engineering output.

This document describes the implementation currently present in the
repository. It distinguishes current behavior from intended
architectural direction and planned capabilities so it can serve as a
reliable baseline for future work, including Codex and Copilot-assisted
development.

> **Document status:** Current implementation baseline with identified
> architectural gaps.\
> **Version:** 1.2\
> **Next planned iteration:** 1.3

## Current capabilities

-   CLI-driven requests for `generate_code` and `review_code`.
-   An Ollama client abstraction with configured model, timeout, and
    streaming settings.
-   Runtime construction and persistence of Work Orders.
-   Per-work-order workspaces.
-   Code generation into generated artifact files.
-   Code review of one or more Python source files, rendered as Markdown
    and persisted as a report.
-   YAML application configuration.
-   Standard Python logging and a QAlchemy structured logging subsystem.
-   An exception catalog and exception-handling service.
-   Unit and end-to-end test suites under `tests/`.

## Runtime architecture

``` mermaid
flowchart TD
    CLI["CLI: app/qalchemy.py"]
    REQUEST["RuntimeRequest"]
    BOOTSTRAP["AppBootstrapService"]
    CONFIG["AppConfigurationService\nconfig/app.yaml"]
    EXECUTION["AppExecutionService"]
    ORCH["OrchestrationService"]
    BUILDER["WorkOrderBuilderService"]
    WORKORDER["WorkOrder"]
    WORKSPACE["WorkSpace"]
    GENERATE["GenerateCodeService"]
    REVIEW["ReviewCodeService"]
    CLIENTSERVICE["ClientService"]
    CLIENT["Client\nOllama"]
    REPORT["ReportWriter"]
    OUTPUT["Workspace output / persisted reports"]

    CLI --> REQUEST
    CLI --> BOOTSTRAP
    BOOTSTRAP --> CONFIG
    BOOTSTRAP --> EXECUTION
    EXECUTION --> ORCH
    REQUEST --> ORCH
    ORCH --> BUILDER
    BUILDER --> WORKORDER
    ORCH --> WORKSPACE
    ORCH --> GENERATE
    ORCH --> REVIEW
    WORKORDER --> GENERATE
    WORKORDER --> REVIEW
    GENERATE --> CLIENTSERVICE
    REVIEW --> CLIENTSERVICE
    CLIENTSERVICE --> CLIENT
    REVIEW --> REPORT
    GENERATE --> OUTPUT
    REVIEW --> OUTPUT
```

### Layer responsibilities

  ---------------------------------------------------------------------
  Layer                              Current responsibility
  ---------------------------------- ----------------------------------
  `app/qalchemy.py`                  Parses CLI arguments, creates a
                                     `RuntimeRequest`, bootstraps the
                                     application, and starts
                                     orchestration.

  `AppBootstrapService`              Loads configuration and creates
                                     shared runtime services and
                                     application workflow services.

  `AppExecutionService`              Holds shared runtime services:
                                     configuration, client service,
                                     logger service, and
                                     exception-handling service.

  `OrchestrationService`             Builds Work Orders, assigns IDs,
                                     creates workspaces, persists Work
                                     Orders and source artifacts,
                                     routes workflows, and persists
                                     workflow output where implemented.

  Feature services                   Execute feature-specific work and
                                     create feature results. Current
                                     implementations contain one
                                     identified persistence-boundary
                                     exception described below.

  Core scripts/utilities             Provide focused technical concerns
                                     including contracts,
                                     transformations, file persistence,
                                     provider normalization, reporting,
                                     source resolution, and workspace
                                     support.
  ---------------------------------------------------------------------

## Runtime contracts

### RuntimeRequest

`RuntimeRequest` is the transport contract from the CLI to
orchestration. It contains paths and request metadata, not the contents
of referenced files.

  ----------------------------------------------------------------------
  Field                  Type                   Meaning
  ---------------------- ---------------------- ------------------------
  `task`                 `str`                  Engineering task
                                                requested by the user.

  `role`                 `Path`                 Role-definition
                                                document.

  `target`               `str`                  Requested workflow,
                                                currently
                                                `generate_code` or
                                                `review_code`.

  `deliverable`          `Path`                 Deliverable-definition
                                                document.

  `source_code`          `list[Path]`           Optional source files or
                                                directories for review.

  `references`           `list[Path]`           Optional supporting
                                                reference files.
  ----------------------------------------------------------------------

### WorkOrder

`WorkOrder` is an immutable, canonical contract built by
`WorkOrderBuilderService`. The builder reads the role, deliverable, and
reference files identified by the `RuntimeRequest`.

  Field           Type    Meaning
  --------------- ------- ------------------------------------------
  `task`          `str`   Requested engineering task.
  `role`          `str`   Resolved role content.
  `target`        `str`   Feature-routing target.
  `deliverable`   `str`   Resolved deliverable definition.
  `references`    `str`   Concatenated optional reference content.

`WorkOrderTransformer` turns the Work Order into a structured prompt
submitted to the configured AI client.

> `config/work_order.yaml` documents a richer, future-oriented Work
> Order shape. The current runtime builder does not load that YAML file;
> it constructs the current dataclass from the runtime request and
> referenced documents.

## Startup and request flow

1.  `app/qalchemy.py` parses `--task`, `--role`, `--target`,
    `--deliverable`, optional `--source_code`, and optional
    `--reference` arguments.
2.  The entry point creates a `RuntimeRequest`.
3.  `AppBootstrapService.bootstrap()` configures standard Python
    bootstrap logging, loads `config/app.yaml`, and creates shared
    services.
4.  `OrchestrationService.execute()` builds the Work Order, maps its
    target to a feature code, and generates a Work Order ID.
5.  Orchestration creates the work-order workspace and persists the
    rendered Work Order, role content, and deliverable content.
6.  Orchestration dispatches the Work Order to the requested feature
    workflow.
7.  Feature workflows create feature output. Persistence ownership
    follows the current implementation, with the Generate Code exception
    explicitly identified below.

## Feature workflows

### Generate Code

``` mermaid
sequenceDiagram
    participant O as OrchestrationService
    participant G as GenerateCodeService
    participant C as Client
    participant W as WorkSpace

    O->>G: execute(work_order, workspace)
    G->>G: transform WorkOrder
    G->>C: generate(prompt)
    C-->>G: provider response
    G->>G: normalize response
    G->>G: create GeneratedArtifact(s)
    G->>W: write artifact(s) under output/
```

#### Current behavior

-   `GenerateCodeService` uses `ClientService` to create the configured
    client.
-   The service transforms the Work Order and invokes the AI provider.
-   The provider response is normalized.
-   `create_generated_artifacts()` extracts the required artifact path
    from the Work Order deliverable and creates `GeneratedArtifact`
    objects.
-   The current implementation writes generated artifacts directly
    beneath `workspace.output_root`, creating parent directories as
    needed.
-   The configured provider implementation is currently Ollama.

#### Identified architectural deviation

The current implementation of `GenerateCodeService` performs
generated-artifact persistence directly. This is an identified
architectural misalignment.

The intended ownership boundary is:

``` text
GenerateCodeService
    ↓
Create GeneratedArtifact result(s)
    ↓
Return result(s) to OrchestrationService
    ↓
OrchestrationService makes persistence decision
    ↓
ArtifactWriter / FileWriter
    ↓
Filesystem
```

`FileWriter` provides reusable UTF-8 file persistence and creates parent
directories as needed. `ArtifactWriter` resolves generated artifact
paths against a supplied output root and delegates persistence to
`FileWriter`.

This correction is planned for V1.3. The current implementation remains
documented here so the architecture baseline accurately describes
repository behavior rather than presenting intended design as completed
behavior.

### Review Code

``` mermaid
sequenceDiagram
    participant O as OrchestrationService
    participant R as ReviewCodeService
    participant P as SourceCodePreprocessor
    participant C as Client
    participant RW as ReportWriter

    O->>O: resolve source file paths
    O->>R: execute(work_order, workspace, source_files)
    R->>P: preprocess each source file
    R->>R: transform WorkOrder and source content
    R->>C: generate(review prompt)
    C-->>R: review text
    R->>RW: render Markdown report
    RW-->>R: rendered report
    R-->>O: rendered report
    O->>O: persist report
```

#### Current behavior

-   `SourceCodeResolver` accepts files or directories and recursively
    resolves supported `.py` files in deterministic order.
-   `ReviewCodeService` reads and preprocesses each source file.
-   The service constructs the review prompt and invokes the configured
    AI client.
-   `ReportWriter` renders the review into Markdown and conditionally
    includes configured runtime metadata.
-   `ReviewCodeService` returns rendered Markdown.
-   `OrchestrationService` owns persistence of the returned review
    output.

#### Architectural status

`ReviewCodeService` is currently aligned with the intended
feature-service boundary regarding final output persistence: it creates
and returns the feature result and does not write the rendered review to
disk itself.

## Persistence model

Each execution receives a workspace rooted at the configured
`workspace.root`.

``` text
work_space/
└── <work-order-id>/
    ├── <work-order-id>.md
    ├── <role-file-name>
    ├── <deliverable-file-name>
    └── output/
        ├── generated artifacts (generate_code)
        └── <work-order-id>_code_review.md (review_code)
```

When `work_order.runtime.persist_to_disk` is enabled:

-   A canonical Work Order copy is also written to
    `work_order.runtime.directory`.
-   A rendered code-review report is also written to
    `reports.review.output_directory`.

Generated artifact persistence currently occurs inside
`GenerateCodeService`; moving that persistence to orchestration through
the artifact-writing utilities is planned for V1.3.

## Configuration

`config/app.yaml` is loaded by `AppConfigurationService` and exposes
typed configuration sections.

  ---------------------------------------------------------------------
  Section                            Current use
  ---------------------------------- ----------------------------------
  `app`                              Name, version, and edition
                                     metadata.

  `client`                           Provider, default model, request
                                     timeout, streaming, and options.

  `work_order`                       Validation/runtime policy and
                                     persistent Work Order location.

  `workspace`                        Root directory for execution
                                     workspaces.

  `templates`                        Template root and code-review
                                     report template.

  `reports`                          Review-report destination and
                                     optional metadata fields.

  `logging`                          Log file location, level, and
                                     debug-related options.

  `exceptions`                       Exception-catalog location and
                                     intended exception behavior.
  ---------------------------------------------------------------------

## Logging and exception handling

### Logging

QAlchemy currently has two complementary logging mechanisms:

-   Standard Python logging is configured during bootstrap by
    `scripts/app/bootstrap_logging.py` and is used by infrastructure
    components including bootstrap, configuration, client construction,
    and source preprocessing.
-   `LoggerService` creates structured `LogEntry` objects, renders
    application log records, and delegates persistence to the low-level
    `Logger`.
-   The two feature services currently emit normal lifecycle messages
    through `LoggerService`.
-   `OrchestrationService` does not currently emit direct lifecycle
    logs.
-   The application does not yet have a single documented runtime policy
    defining when standard Python logging versus `LoggerService` should
    be used.

### Logging hardening status

The logging subsystem exists and is tested, but application-wide
integration was not completed to the level originally intended.

V1.3 should establish targeted logging at important workflow boundaries,
particularly:

-   `OrchestrationService`
-   `GenerateCodeService`
-   `ReviewCodeService`

The goal is not indiscriminate logging. Key actions, state transitions,
external AI calls, persistence decisions, and unexpected failures should
be observable.

### Exceptions

`ExceptionCatalog`, `QAlchemyException`, and `ExceptionHandlingService`
are initialized during bootstrap. The catalog defines error codes
covering configuration, AI, preprocessing, generation, review, logging,
reporting, filesystem, validation, and internal errors.

Current limitations:

-   Catalogued exception translation is not yet broadly integrated into
    feature or orchestration runtime failures.
-   Native exceptions currently propagate through much of the workflow.
-   The feature services receive the exception-handling service but do
    not yet consistently use it to translate or enrich failures.
-   User-facing error presentation and workflow-level exception policy
    are not yet fully integrated.

This is intentional current-state documentation, not a statement that
exception integration is complete.

### V1.3 logging and exception direction

For critical application workflows:

1.  Log meaningful lifecycle entry and completion points.
2.  Preserve useful failure context.
3.  Delegate unexpected failures to the application's exception-handling
    strategy where appropriate.
4.  Do not silently suppress unexpected exceptions.
5.  Avoid allowing logging or exception infrastructure to change
    feature-result ownership boundaries.

## Current constraints and deferred work

-   Ollama is the only implemented provider.
-   Generate Code currently derives one required artifact path from the
    deliverable definition.
-   Source-code review currently resolves Python files only.
-   Generate Code currently performs direct artifact persistence; this
    is planned for architectural correction in V1.3.
-   Orchestration-level lifecycle logging remains incomplete.
-   Exception-catalog translation and user-facing error presentation are
    not yet broadly integrated into workflow execution.
-   A unified logging policy remains future hardening work.
-   The repository contains developer utilities for dependency analysis
    and workflow verification; they are not part of the main CLI
    execution path.
-   Agentic workflow and MCP integration are future architecture work
    and are not represented as implemented V1.2 capabilities.

## Repository map

``` text
app/
  qalchemy.py                         CLI entry point
  docs/architecture/                  Current and vision architecture documents

clients/
  client.py                           Ollama-backed provider client

config/
  app.yaml                            Application configuration
  exceptions.yaml                     Exception catalog definitions
  work_order.yaml                     Future-oriented Work Order example/schema

resources/
  role/ and deliverable/              Runtime engineering inputs

scripts/
  app/                                Bootstrap logging
  core/                               Contracts, rendering, logging, reporting, catalog
  feature/                            Source preprocessing
  utils/                              Files, workspace, resolver, artifacts, normalization

services/
  app/                                Bootstrap, configuration, execution, orchestration
  core/                               Client, logger, exception-handling services
  feature/                            Generate Code and Review Code workflows

templates/
  code_review_report_template.md      Review-report template

tests/
  unit/ and e2e/                      Automated test suites
```

## Decision guide for V1.3 and future iterations

When evolving QAlchemy, preserve the following ownership boundaries:

-   The entry point creates `RuntimeRequest` objects; it does not
    execute feature logic.
-   `AppBootstrapService` constructs and wires application dependencies.
-   `AppExecutionService` provides shared runtime services without
    owning feature workflow decisions.
-   `OrchestrationService` owns workflow coordination, IDs, workspace
    setup, routing, and final persistence decisions.
-   Feature services own feature-specific transformation, AI/provider
    invocation, and feature-result creation.
-   Feature services should return results rather than directly owning
    workflow output persistence.
-   Utilities own focused technical concerns such as file access, path
    resolution, preprocessing, output normalization, report rendering,
    and artifact persistence.
-   Cross-cutting concerns such as logging and catalogued exception
    translation should be introduced with targeted tests and without
    changing feature-result ownership.

## Architecture corrections planned for V1.3

The following items are already identified and should be treated as
deliberate backlog work rather than rediscovered implementation issues:

### 1. Generate Code persistence boundary

Move generated-artifact persistence out of `GenerateCodeService`.

Target flow:

``` text
GenerateCodeService
    ↓
GeneratedArtifact result(s)
    ↓
OrchestrationService
    ↓
ArtifactWriter
    ↓
FileWriter
```

### 2. Logging integration

Complete targeted lifecycle logging for the critical workflow path:

``` text
OrchestrationService
        ↓
GenerateCodeService
        ↓
ReviewCodeService
```

### 3. Exception integration

Define and implement consistent handling of important runtime failures
while preserving context and avoiding swallowed exceptions.

### 4. First agentic capability

Introduce the first deliberately designed QAlchemy agent without
redesigning the V1.2 foundation unnecessarily.

The likely direction is a `RequirementEvaluationAgent` capable of:

``` text
Goal
  ↓
Determine required information
  ↓
Select from approved tools / MCP capabilities
  ↓
Gather information
  ↓
Observe results
  ↓
Determine next action
  ↓
Use authorized QAlchemy capabilities where appropriate
  ↓
Deliver a structured engineering result
```

This is future architecture work. It is not part of the V1.2
implementation described above.

## Guidance for AI engineering assistants

When using Codex, Copilot, or another AI engineering assistant with
QAlchemy:

1.  Treat this document as the current architecture baseline.
2.  Distinguish explicitly between **current implementation** and
    **planned architecture**.
3.  Do not "fix" an architectural deviation without confirming the
    requested iteration or approved backlog item.
4.  Review ownership boundaries before proposing implementation changes.
5.  Do not move business or workflow logic into low-level utilities.
6.  Do not allow feature services to accumulate orchestration or
    persistence responsibilities.
7.  Preserve the immutable `WorkOrder` as the canonical feature-work
    contract unless an approved architecture change says otherwise.
8.  Add logging and exception handling deliberately at meaningful
    workflow boundaries.
9.  Prefer small, focused technical utilities over duplicated low-level
    behavior.
10. Update tests and architecture documentation when approved
    implementation behavior changes.

## Architecture baseline summary

### Solid V1.2 foundation

-   `RuntimeRequest`
-   Immutable `WorkOrder`
-   `WorkOrderBuilderService`
-   Application bootstrap and execution context
-   `OrchestrationService` as the central workflow coordinator
-   Per-work-order workspaces
-   `ReviewCodeService` result/persistence boundary
-   AI client abstraction
-   Logging infrastructure
-   Exception infrastructure
-   File and artifact persistence utilities
-   Automated unit and end-to-end testing

### Known implementation gaps

-   `GenerateCodeService` currently owns generated-artifact persistence.
-   Logging integration is incomplete at orchestration and critical
    failure boundaries.
-   Exception infrastructure is not yet broadly integrated into runtime
    workflows.
-   A unified runtime logging policy is not yet established.

### Next direction

V1.3 should correct the identified architectural gaps while introducing
QAlchemy's first intentionally designed agentic capability.

The objective is to preserve the solid V1.2 foundation, correct known
implementation drift, and expand the application into a more
differentiated AI engineering workflow system without unnecessary
redesign.

## Additional context for future AI-assisted development

This section provides context that is important for Codex, Copilot, or
another AI engineering assistant reviewing QAlchemy. It describes the
direction of the application and the known shortcomings discovered
during the V1.2 work.

### How QAlchemy evolved

QAlchemy began as a focused AI-assisted engineering application with two
primary capabilities:

-   Generate Code
-   Review Code

The V1 and V1.1 work concentrated heavily on establishing reusable
application infrastructure and architectural boundaries. V1.2 continued
that work by introducing a more explicit runtime model built around
`RuntimeRequest`, immutable `WorkOrder` objects, application bootstrap,
execution context, orchestration, workspaces, and feature services.

The V1.2 architecture is therefore more mature than the number of
user-facing capabilities currently suggests.

### Current product limitation

QAlchemy is currently a relatively narrow application. Its primary
workflows are largely predetermined:

``` text
User Request
    ↓
Selected Target
    ↓
Predefined Feature Workflow
    ↓
AI Provider
    ↓
Result
```

The application does not yet independently determine what information it
needs or which approved capabilities it should use to accomplish a
broader engineering objective.

This is an intentional area for future expansion.

### Direction of the application

The next major architectural direction is to introduce controlled
agentic behavior.

The intended future model is:

``` text
Engineering Goal
    ↓
Agent evaluates the objective
    ↓
Agent determines required information
    ↓
Agent selects from approved tools, MCP capabilities, or QAlchemy services
    ↓
Agent performs an action
    ↓
Agent observes the result
    ↓
Agent determines whether additional action is required
    ↓
Agent selects the next authorized capability
    ↓
Structured engineering result
```

The important distinction is that future agents should not merely wrap
an existing service or execute a fixed sequence of steps. A QAlchemy
agent should be capable of making controlled decisions about the next
action needed to accomplish its assigned objective.

### First agent direction

The leading candidate for the first agentic capability is
`RequirementEvaluationAgent`.

The likely objective is to evaluate whether an engineering requirement
is sufficiently complete and ready for downstream engineering work.

A future agent may need to:

-   Retrieve a Jira or similar work-management item.
-   Read acceptance criteria.
-   Inspect comments or linked information.
-   Retrieve referenced design or requirements documents.
-   Determine whether additional information is required.
-   Use authorized QAlchemy capabilities to evaluate quality or
    testability.
-   Identify ambiguity, missing information, risk, or clarification
    needs.
-   Return a structured engineering assessment.

The exact external integrations and MCPs have not yet been selected or
implemented.

### Agent safety and control boundary

Future agents should select only from capabilities that have been
explicitly registered, authorized, and made available to them.

The current architectural direction is not to allow an agent to
arbitrarily discover, install, or trust external tools.

The intended model is:

``` text
Agent
    ↓
Approved Capability Registry
    ├── Approved MCP tools
    ├── Approved external integrations
    └── Approved QAlchemy services
```

This preserves control, observability, security, and testability while
still allowing meaningful agentic decision-making.

### Known shortcomings discovered during V1.2

The following issues are known and should be treated as deliberate
backlog items rather than assumptions that the architecture is fully
implemented.

#### Logging

The logging infrastructure was implemented, but integration across
important application workflows was not completed as originally
intended.

The application currently has:

-   Standard Python logging.
-   `LogEntry`.
-   `Logger`.
-   `LoggerConfig`.
-   `LoggerService`.

However, the critical workflow path does not yet have complete and
consistent lifecycle observability, particularly at orchestration
boundaries.

Future work should focus on meaningful logging at important actions
rather than adding logging indiscriminately.

#### Exception handling

The exception infrastructure exists but is only partially integrated
into runtime workflows.

The application currently has:

-   `ExceptionCatalog`.
-   `QAlchemyException`.
-   `ExceptionHandlingService`.

However, important runtime failures are not yet consistently translated,
enriched, logged, or presented through a unified application policy.

Future work should integrate exception handling without suppressing
useful native error context.

#### Generate Code service boundary

`GenerateCodeService` currently performs generated-artifact persistence
directly.

This conflicts with the intended architecture in which:

-   Feature services create feature results.
-   `OrchestrationService` coordinates the workflow and owns persistence
    decisions.
-   File-writing utilities perform focused persistence operations.

This is a known implementation deviation, not an approved future service
responsibility.

#### Review Code service

`ReviewCodeService` is closer to the intended architecture. It performs
feature work, renders the review result, and returns the result for
orchestration to persist.

Future changes should preserve this separation of feature execution and
final persistence ownership.

### Important architectural principle

QAlchemy is intended to evolve toward an application in which services
have focused responsibilities.

In particular:

``` text
Orchestration
    Owns workflow coordination and decisions.

Feature Services
    Own feature-specific processing and result creation.

Agents
    Own controlled goal evaluation and next-action decisions.

Utilities
    Own focused technical operations.

MCPs / External Tools
    Provide authorized capabilities and information.
```

Feature services should not gradually become orchestration engines,
filesystem managers, or general-purpose agent controllers.

Likewise, future agents should not absorb every technical responsibility
themselves. An agent should decide what needs to happen and invoke
approved capabilities to perform the work.

### Guidance when reviewing the repository

An AI engineering assistant should actively distinguish among:

1.  **Implemented and working behavior.**
2.  **Implemented but architecturally incomplete behavior.**
3.  **Intended future architecture.**
4.  **Unapproved ideas that have not yet become architecture.**

Do not assume that because a component exists, its integration is
complete.

Do not assume that a documented future design has already been
implemented.

When a proposed change crosses a service boundary, changes ownership of
persistence, introduces a new dependency, adds an MCP, or changes the
role of orchestration, the change should be treated as an architectural
decision and reviewed before implementation.

### V1.3 working philosophy

V1.3 should not be treated as a wholesale redesign.

The intended approach is:

``` text
Preserve the stable V1.2 foundation
        ↓
Correct known architectural drift
        ↓
Complete critical cross-cutting integration
        ↓
Introduce one controlled agentic capability
        ↓
Learn from the implementation
        ↓
Use those lessons to guide later expansion
```

The objective is to build one real, demonstrable agentic capability
carefully enough that the architecture remains understandable, testable,
observable, and extensible.

### Practical success criteria for the first agent

The first agent should eventually be demonstrable end-to-end.

A demonstration should make it possible to show:

1.  The engineering goal provided to the agent.
2.  The information and capabilities available to the agent.
3.  The action or tool selected by the agent.
4.  The result or observation returned.
5.  The agent's subsequent decision.
6.  The final structured engineering result.
7.  Relevant logs and failure behavior.
8.  Automated tests covering deterministic boundaries.

The purpose is not merely to add the word "agent" to QAlchemy. The
implementation should provide a concrete, observable example of
controlled agentic decision-making.
