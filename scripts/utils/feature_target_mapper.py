"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    feature_target_mapper.py

Purpose:
    Maps canonical Work Order feature targets to QAlchemy feature codes.

Description:
    The Feature Target Mapper translates the target value carried by a
    WorkOrder into the short feature code used when generating Work Order
    identifiers.

Responsibilities
----------------
- Map canonical feature targets to feature codes.
- Reject unsupported feature targets.

Non-Responsibilities
--------------------
This utility does NOT:

- Generate Work Order identifiers.
- Create WorkSpaces.
- Write Work Orders.
- Execute Feature Services.
- Perform orchestration.
- Modify WorkOrders.

Design Principles
-----------------
The mapper is deterministic and stateless.

Given the same feature target, the mapper always returns the same feature
code.

===============================================================================
"""

_FEATURE_CODES = {
    "generate_code": "GCS",
    "review_code": "RCS",
    "requirement_evaluation": "RRE",
}


def map_feature_code(
    target: str,
) -> str:
    """
    Map a canonical Work Order target to its feature code.

    Args:
        target:
            Canonical Work Order feature target.

    Returns:
        The feature code associated with the target.

    Raises:
        ValueError:
            If the target is not supported.
    """

    try:
        return _FEATURE_CODES[target]
    except KeyError as exc:
        raise ValueError(f"Unsupported Work Order target: {target}") from exc
