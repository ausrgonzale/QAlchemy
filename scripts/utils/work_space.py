"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    work_space.py

Purpose:
    Provides the WorkSpace used to create and expose the filesystem structure
    for a Work Order.

Description:
    WorkSpace owns the physical directory structure associated with a Work
    Order. It creates the Work Order workspace, including the locations for
    the role, deliverable, and execution output, while remaining independent
    of artifact generation and file persistence.

Responsibilities
----------------
- Define the configured WorkSpace root.
- Define the current Work Order workspace.
- Expose the Work Order identifier.
- Create the Work Order workspace structure.
- Expose the role path.
- Expose the deliverable path.
- Expose the output root for downstream writers.

Non-Responsibilities
--------------------
This utility does NOT:

- Generate Work Order identifiers.
- Write role or deliverable content.
- Write generated artifacts.
- Persist Work Orders.
- Parse Deliverables.
- Normalize provider responses.
- Invoke AI providers.
- Perform orchestration.
- Manage artifact contents.

===============================================================================
"""

from pathlib import Path


class WorkSpace:
    """
    Represents the filesystem workspace for a Work Order.
    """

    def __init__(
        self,
        root: Path,
        work_order_id: str,
    ) -> None:
        """
        Initialize the WorkSpace.
        """

        self._root = root
        self._work_order_id = work_order_id

    @property
    def root(self) -> Path:
        """Return the configured WorkSpace root."""

        return self._root

    @property
    def work_order_id(self) -> str:
        """Return the Work Order identifier."""

        return self._work_order_id

    @property
    def workspace_root(self) -> Path:
        """Return the filesystem root for this Work Order."""

        return self._root / self._work_order_id

    @property
    def role_path(self) -> Path:
        """Return the path for the Work Order role."""

        return self.workspace_root / "role.md"

    @property
    def deliverable_path(self) -> Path:
        """Return the path for the Work Order deliverable."""

        return self.workspace_root / "deliverable.md"

    @property
    def output_root(self) -> Path:
        """Return the output directory for generated artifacts."""

        return self.workspace_root / "output"

    def create(self) -> None:
        """
        Create the Work Order workspace structure.
        """

        self.role_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.output_root.mkdir(
            parents=True,
            exist_ok=True,
        )
