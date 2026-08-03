"""
prototype/prompt_debug_writer.py

Prototype PromptDebugWriter for QAlchemy PromptBuilderService v1.2
"""

from datetime import UTC, datetime
from pathlib import Path


class PromptDebugWriter:
    """Writes prompt debug artifacts when enabled."""

    def write(
        self,
        prompt_model: list,
        rendered_prompt: str,
        output_directory: str = "reports/debug",
    ) -> Path:
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        file_path = output_path / f"prompt_{timestamp}.md"

        with file_path.open("w", encoding="utf-8") as file:
            file.write("# Prompt Debug Output\n\n")

            file.write("## Prompt Model\n")
            for title, content in prompt_model:
                file.write(f"- {title}: {content}\n")

            file.write("\n---\n\n")

            file.write("## Rendered Prompt\n\n")
            file.write(rendered_prompt)

        return file_path
