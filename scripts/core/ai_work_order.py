"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    ai_work_order.py

Purpose:
    Defines the immutable AIWorkOrder used to submit requests to AI-facing
    services throughout QAlchemy.

Description:
    AIWorkOrder represents a single AI request issued by a host application.

    It provides a strongly typed alternative to passing loosely structured
    dictionaries between services. The work order captures the intent of an
    AI request while remaining independent of implementation details such as
    providers, models, logging, rendering, or framework configuration.

    AIWorkOrder is intentionally immutable once created.

Responsibilities
----------------
- Represent an AI request.
- Provide a stable contract between host applications and framework services.
- Improve type safety.
- Improve IDE completion.
- Eliminate dictionary key lookups.

Non-Responsibilities
--------------------
AIWorkOrder does NOT:

- Generate prompts.
- Perform validation beyond construction.
- Load configuration.
- Invoke AI providers.
- Know anything about logging or exception handling.

Future Evolution
----------------
Future versions may extend AIWorkOrder with additional optional properties
including:

- acceptance criteria
- constraints
- artifacts
- examples
- attachments
- metadata

without changing the public service contracts.

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AIWorkOrder:
    """
    Represents a request submitted to an AI service.

    Attributes
    ----------
    who:
        Identifies the intended AI persona or role.

    what:
        Describes the requested work.

    why:
        Explains the objective or business purpose.

    context:
        Optional supporting context.
    """

    who: str
    what: str
    why: str
    context: str = ""

    @classmethod
    def from_dict(
        cls,
        work_order: dict[str, str],
    ) -> AIWorkOrder:
        """
        Creates an AIWorkOrder from an existing dictionary.

        This helper provides a migration path while older services continue
        to construct dictionary-based work orders.

        Parameters
        ----------
        work_order:
            Dictionary representation of an AI work order.

        Returns
        -------
        AIWorkOrder
            Strongly typed AI work order instance.
        """

        return cls(
            who=work_order.get("who", ""),
            what=work_order.get("what", ""),
            why=work_order.get("why", ""),
            context=work_order.get("context", ""),
        )
