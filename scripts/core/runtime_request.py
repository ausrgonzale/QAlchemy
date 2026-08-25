"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    runtime_request.py

Purpose
-------
Defines the runtime request created by QAlchemy from command-line arguments.

Description
-----------
RuntimeRequest is the transport contract between the QAlchemy application
entry point and the orchestration layer.

It describes the engineering work requested at runtime, including the task,
role, target feature, deliverable location, and optional reference material
locations.

RuntimeRequest contains request metadata and file locations. It does not
contain the engineering content itself.

Architecture
------------
RuntimeRequest is created by the QAlchemy application entry point and
consumed by the OrchestrationService.

The OrchestrationService passes the RuntimeRequest to the
WorkOrderBuilderService, which resolves the referenced files and constructs
the canonical WorkOrder.

Flow:

    CLI
      ↓
    RuntimeRequest
      ↓
    OrchestrationService
      ↓
    WorkOrderBuilderService
      ↓
    WorkOrder

Responsibilities
----------------
- Represent the runtime engineering request.
- Preserve the requested task.
- Preserve the selected engineering role.
- Preserve the target QAlchemy feature.
- Identify the deliverable definition.
- Identify optional reference material.
- Provide a stable transport contract between application layers.

Non-Responsibilities
--------------------
RuntimeRequest does NOT:

- Read files.
- Build WorkOrders.
- Resolve reference material.
- Contain engineering document content.
- Render prompts.
- Invoke AI clients.
- Execute Feature Services.
- Perform logging.
- Perform exception handling.
- Write files.
- Load application configuration.

Design Principles
-----------------
RuntimeRequest is intentionally lightweight.

It represents what was requested at runtime and where supporting artifacts
can be found. Content resolution and WorkOrder construction are handled by
the WorkOrderBuilderService.

Optional reference material is identified by file location and is not
required for a RuntimeRequest to be valid.

===============================================================================
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RuntimeRequest:
    """
    Runtime execution request.

    This object is the transport contract between the application entry
    point and the orchestration layer.
    """

    #
    # Task
    #

    task: str

    #
    # Role
    #

    role: Path

    #
    # Target Feature
    #

    target: str

    #
    # Deliverable
    #

    deliverable: Path

    #
    # Optional Reference Material
    #

    references: list[Path] = field(default_factory=list)
