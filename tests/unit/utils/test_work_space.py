"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_work_space.py

Purpose:
    Validates WorkSpace creation and filesystem structure.

Description:
    These tests verify that WorkSpace creates the directory structure required
    for a Work Order and exposes the paths required by downstream services.

Responsibilities
----------------
- Verify the WorkSpace directory is created.
- Verify the output directory is created.
- Verify the Work Order identifier is exposed.
- Verify the WorkSpace root is exposed.
- Verify the role path is exposed.
- Verify the deliverable path is exposed.
- Verify the output root is exposed.

Non-Responsibilities
--------------------
These tests do NOT:

- Generate Work Order numbers.
- Write role or deliverable content.
- Write generated artifacts.
- Persist Work Orders.
- Parse Deliverables.
- Normalize provider responses.
- Invoke AI providers.
- Test ArtifactWriter.
- Perform orchestration.

===============================================================================
"""

from pathlib import Path

from scripts.utils.work_space import WorkSpace


def test_creates_work_order_output_structure(
    tmp_path: Path,
) -> None:
    """Create the WorkSpace and its output directory."""

    workspace_root = tmp_path / "work_space"

    workspace = WorkSpace(
        root=workspace_root,
        work_order_id="WO001",
    )

    workspace.create()

    expected_root = workspace_root / "WO001"
    expected_output = expected_root / "output"
    expected_role = expected_root / "role.md"
    expected_deliverable = expected_root / "deliverable.md"

    assert expected_root.is_dir()
    assert expected_output.is_dir()

    assert workspace.root == workspace_root
    assert workspace.work_order_id == "WO001"
    assert workspace.workspace_root == expected_root
    assert workspace.role_path == expected_role
    assert workspace.deliverable_path == expected_deliverable
    assert workspace.output_root == expected_output
