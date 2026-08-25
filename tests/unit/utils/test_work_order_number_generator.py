"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_work_order_number_generator.py

Purpose:
    Validates Work Order identifier generation.

Description:
    These tests verify that Work Order identifiers are generated using the
    Work Order prefix, feature identifier, and timestamp.

Responsibilities
----------------
- Verify Work Order identifier format.
- Verify the feature identifier is included.
- Verify the timestamp is included.
- Verify identifiers can be generated without persisted sequence state.

Non-Responsibilities
--------------------
These tests do NOT:

- Create WorkSpaces.
- Persist Work Orders.
- Write Work Order content.
- Execute Work Orders.
- Invoke AI providers.
- Perform orchestration.

===============================================================================
"""

from scripts.utils.work_order_number_generator import (
    WorkOrderNumberGenerator,
)


def test_generates_work_order_number() -> None:
    """Generate a Work Order identifier using the feature and timestamp."""

    generator = WorkOrderNumberGenerator()

    result = generator.generate(
        feature="GCS",
    )

    assert result.startswith("WOGCS")
    assert len(result) == 24


def test_work_order_number_contains_timestamp() -> None:
    """Verify the identifier contains a fourteen-digit timestamp."""

    generator = WorkOrderNumberGenerator()

    result = generator.generate(
        feature="GCS",
    )

    timestamp = result[5:19]

    assert len(timestamp) == 14
    assert timestamp.isdigit()


def test_work_order_number_uses_feature_identifier() -> None:
    """Verify the feature identifier is included in the Work Order number."""

    generator = WorkOrderNumberGenerator()

    result = generator.generate(
        feature="GCS",
    )

    assert result.startswith("WOGCS")


def test_different_features_produce_different_prefixes() -> None:
    """Verify feature identifiers are reflected in generated Work Orders."""

    generator = WorkOrderNumberGenerator()

    generate_code = generator.generate(
        feature="GCS",
    )

    review_code = generator.generate(
        feature="RCS",
    )

    assert generate_code.startswith("WOGCS")
    assert review_code.startswith("WORCS")
