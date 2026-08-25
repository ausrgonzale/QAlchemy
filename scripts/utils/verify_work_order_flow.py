"""
End-to-end Generate code workflow verification.

Exercises:

    AppBootstrapService
        ↓
    AppExecutionService
        ↓
    OrchestrationService
        ↓
    WorkOrderBuilderService
        ↓
    GenerateCodeService
"""

from pathlib import Path

from scripts.core.runtime_request import RuntimeRequest
from services.app.app_bootstrap_service import AppBootstrapService


def main() -> None:
    """
    Execute the Generate Code engineering workflow.
    """

    runtime_request = RuntimeRequest(
        target="generate_code",
        system_files=[
            Path("resources/system.md"),
        ],
        user_files=[
            Path("resources/user.md"),
        ],
        context_files=[
            Path("resources/context.md"),
        ],
        deliverable_files=[
            Path("resources/deliverable.md"),  # <-- verify spelling in your project
        ],
    )

    application = AppBootstrapService().bootstrap()

    application.run(runtime_request)

    print("Generate Code workflow completed.")


if __name__ == "__main__":
    main()
