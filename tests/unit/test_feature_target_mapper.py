"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_feature_target_mapper.py

Purpose:
    Validates mapping of Work Order feature targets to feature codes.

Description:
    These tests verify that canonical Work Order target values are translated
    into the short feature codes used by Work Order identifiers.

Responsibilities
----------------
- Verify Generate Code maps to GCS.
- Verify Review Code maps to RCS.
- Verify Requirement Evaluation maps to RRE.
- Verify unsupported targets are rejected.

Non-Responsibilities
--------------------
These tests do NOT:

- Generate Work Order identifiers.
- Create WorkSpaces.
- Write Work Orders.
- Execute Feature Services.
- Perform orchestration.

===============================================================================
"""

import pytest

from scripts.utils.feature_target_mapper import (
    map_feature_code,
    map_requirements_capability,
)

pytestmark = pytest.mark.mapping


def test_maps_generate_code_target_to_gcs() -> None:
    """Map the Generate Code target to GCS."""

    assert map_feature_code("generate_code") == "GCS"


def test_maps_review_code_target_to_rcs() -> None:
    """Map the Review Code target to RCS."""

    assert map_feature_code("review_code") == "RCS"


def test_maps_requirement_evaluation_target_to_res() -> None:
    """Map the Requirement Evaluation target to RES."""

    assert map_feature_code("requirements") == "RES"


def test_rejects_unsupported_target() -> None:
    """Reject an unsupported Work Order target."""

    with pytest.raises(
        ValueError,
        match="Unsupported Work Order target",
    ):
        map_feature_code("unsupported_target")


def test_maps_requirements_evaluate_capability_to_feature() -> None:
    """Map the Requirements Agent evaluate capability to its feature target."""

    assert map_requirements_capability("evaluate") == "evaluate_requirement"


def test_rejects_unsupported_requirements_capability() -> None:
    """Reject an unsupported Requirements Agent capability."""

    with pytest.raises(ValueError, match="Unsupported Requirements Agent capability"):
        map_requirements_capability("unsupported")
