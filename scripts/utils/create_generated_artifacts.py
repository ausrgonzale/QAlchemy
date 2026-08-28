"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    create_generated_artifacts.py

Purpose:
    Creates GeneratedArtifact objects from normalized AI provider responses.

Description:
    This utility transforms normalized provider output into the QAlchemy
    GeneratedArtifact representation required by downstream persistence.

Responsibilities
----------------
- Define the GeneratedArtifact data structure.
- Extract required artifact paths from the WorkOrder deliverable.
- Create GeneratedArtifact objects containing relative paths and generated
  content.

Non-Responsibilities
--------------------
This utility does NOT:

- Invoke AI providers.
- Normalize provider responses.
- Write files.
- Create directories.
- Manage WorkSpaces.
- Modify WorkOrders.
- Perform logging.
- Perform orchestration.

===============================================================================
"""

from dataclasses import dataclass

from scripts.core.work_order import WorkOrder


@dataclass(frozen=True)
class GeneratedArtifact:
    """
    Represents a generated project artifact.
    """

    relative_path: str
    content: str


def create_generated_artifacts(
    work_order: WorkOrder,
    response: str,
) -> tuple[GeneratedArtifact, ...]:
    """
    Create GeneratedArtifact objects from a WorkOrder and normalized response.

    The artifact path is extracted from the Required Artifact section of the
    Deliverable contained in the WorkOrder.
    """

    lines = work_order.deliverable.splitlines()

    for index, line in enumerate(lines):
        if line.strip() != "## Required Artifact":
            continue

        for candidate in lines[index + 1 :]:
            candidate = candidate.strip()

            if not candidate:
                continue

            if candidate.startswith("```"):
                continue

            if candidate.lower().startswith("generate exactly one file"):
                continue

            if candidate.startswith("#"):
                continue

            return (
                GeneratedArtifact(
                    relative_path=candidate,
                    content=response,
                ),
            )

        break

    raise ValueError("WorkOrder deliverable does not define a required artifact.")
