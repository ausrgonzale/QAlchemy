"""
===============================================================================
File Descriptor Header
===============================================================================
File: artifact_parser_service.py

Purpose:
    Provides a centralized service for parsing AI-generated artifact responses
    into individual project artifacts.

    This service is responsible for interpreting the structured response
    returned by the AI code generation workflow and converting it into a
    collection of generated artifacts that can be written to disk.

Responsibilities:
    - Parse AI-generated artifact responses.
    - Identify individual generated files.
    - Extract relative file paths.
    - Extract file contents.
    - Return a collection of generated artifacts.

Design Notes:
    ArtifactParserService performs parsing only.

    It does not communicate with AI providers, perform file I/O, or modify
    generated content. Writing generated artifacts to disk is the
    responsibility of FileWriterService.

Dependencies:
    - scripts.generated_artifact.GeneratedArtifact

Author:
    Ron Gonzalez

Created:
    July 2026
===============================================================================
"""

import re

from scripts.core.generate_artifacts import GeneratedArtifact


class ArtifactParserService:
    """
    Parses structured AI responses into generated project artifacts.

    This service converts a structured AI response into a collection of
    GeneratedArtifact objects that can be consumed by downstream services
    responsible for writing artifacts to disk.
    """

    _ARTIFACT_PATTERN = re.compile(
        r"=== FILE:\s*(.*?)\s*===\n(.*?)=== END FILE ===",
        re.DOTALL,
    )

    @staticmethod
    def parse(response: str) -> list[GeneratedArtifact]:
        """
        Parse an AI response into generated project artifacts.

            Args:
                response:
                    Structured response returned by the AI generation workflow.

            Returns:
                A collection of GeneratedArtifact instances representing each generated
                project artifact contained within the response.

            Raises:
                ValueError:
                    Raised when the response does not conform to the expected artifact
                    format.
        """

        if not response or not response.strip():
            raise ValueError("AI response is empty.")

        if "=== FILE:" not in response:
            raise ValueError("AI response does not contain any generated artifacts.")

        artifacts: list[GeneratedArtifact] = []

        for match in ArtifactParserService._ARTIFACT_PATTERN.finditer(response):
            relative_path = match.group(1).strip()
            content = match.group(2).rstrip()

            if not relative_path:
                raise ValueError("Generated artifact is missing a file path.")

            artifacts.append(
                GeneratedArtifact(
                    relative_path=relative_path,
                    content=content,
                )
            )

        if not artifacts:
            raise ValueError("No valid generated artifacts were found.")

        if response.count("=== FILE:") != len(artifacts):
            raise ValueError(
                "One or more generated artifacts are missing an '=== END FILE ===' marker."
            )

        return artifacts
