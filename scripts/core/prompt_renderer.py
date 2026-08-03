"""
Prompt_renderer.py

PromptRenderer for QAlchemy PromptBuilderService v1.2
"""

from collections.abc import Iterable


class PromptRenderer:
    """Renders an assembled prompt model into Markdown."""

    def render(
        self,
        prompt_model: Iterable[tuple[str, str]],
    ) -> str:
        """Render an assembled prompt model into Markdown."""

        lines: list[str] = []

        for title, content in prompt_model:
            if not content:
                continue

            lines.append(f"## {title}")
            lines.append(str(content).strip())
            lines.append("")

        return "\n".join(lines).rstrip()
