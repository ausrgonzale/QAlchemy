"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    work_order_number_generator.py

Purpose:
    Generates unique Work Order identifiers for QAlchemy workflows.

Description:
    WorkOrderNumberGenerator creates a Work Order identifier using the
    Work Order prefix, feature identifier, current timestamp, and a random
    four-digit suffix.

Responsibilities
----------------
- Generate Work Order identifiers.
- Include the feature identifier.
- Include the current timestamp.
- Include a random four-digit suffix.

Non-Responsibilities
--------------------
This utility does NOT:

- Persist Work Orders.
- Create WorkSpaces.
- Write files.
- Maintain sequence state.
- Perform orchestration.
- Execute Feature Services.

===============================================================================
"""

from datetime import datetime
from random import randint
from zoneinfo import ZoneInfo


class WorkOrderNumberGenerator:
    """
    Generates Work Order identifiers.
    """

    def generate(
        self,
        feature: str,
    ) -> str:
        """
        Generate a Work Order identifier.
        """

        timestamp = datetime.now(
            tz=ZoneInfo("America/Chicago"),
        ).strftime(
            "%Y%m%d%H%M%S",
        )

        random_suffix = randint(
            1000,
            9999,
        )

        return f"WO{feature}" f"{timestamp}" f"-{random_suffix}"
