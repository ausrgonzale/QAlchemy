"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    work_order.py

Purpose:
    Defines the canonical WorkOrder consumed by QAlchemy Feature Services.

Description:
    AIWorkOrder is the immutable engineering contract exchanged between the
    WorkOrderBuilderService and Feature Services.

    The work order represents everything required for an AI Feature Service to
    execute an engineering task. It intentionally contains only business data
    and is independent of infrastructure concerns such as persistence, logging,
    AI providers, prompt rendering, or application configuration.

Architecture
------------
WorkOrder is the canonical contract within the QAlchemy application.

Responsibilities
----------------
- Represent a complete engineering work order.
- Provide a stable contract between application services.
- Improve type safety.
- Improve IDE completion.
- Eliminate dictionary-based work orders.

Non-Responsibilities
--------------------
WorkOrder does NOT:

- Build work orders.
- Read files.
- Write files.
- Load configuration.
- Render prompts.
- Invoke clients.
- Perform logging.
- Perform exception handling.
- Know anything about persistence.

Design Principles
-----------------
The WorkOrder is intentionally simple and stable.

Future capabilities should be introduced by enhancing the services that
produce or consume the work order rather than modifying the work order
itself whenever possible.

When WorkOrder schema changes are necessary, they should be deliberate
and validated across all producers and consumers.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkOrder:
    """
    Canonical engineering contract consumed by QAlchemy Feature Services.
    """

    #
    # Task
    #

    task: str

    #
    # Role
    #

    role: str

    #
    # Target Feature
    #

    target: str

    #
    # Deliverable Definition
    #

    deliverable: str

    #
    # Optional Reference Material
    #

    references: str = ""
