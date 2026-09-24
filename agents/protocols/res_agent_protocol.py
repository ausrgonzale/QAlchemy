"""
Requirements Agent Response Protocol

Defines the response contract expected from the Requirements Agent.

This module contains the response protocol only. It does not define typed
result models, implement Agent reasoning, execute tools, or communicate
with external systems.
"""

REQUIREMENTS_AGENT_RESPONSE = """
Requirements Agent Response

Return a single valid JSON object with exactly these top-level fields:

- role
- capability
- status
- summary
- findings
- readiness
- recommended_actions
- confidence
- report

role must contain the role selected for the work.

capability must be one of:
- evaluate
- generate
- refine
- create_acceptance_criteria
- create_test_cases

status must be one of:
- ready
- needs_refinement
- needs_clarification
- invalid

findings must contain:
- strengths
- gaps
- ambiguities
- assumptions

Each findings value must be an array of strings.

readiness must contain:
- implementation
- test_cases
- acceptance_criteria

Each readiness value must be one of:
- ready
- not_ready
- unknown

recommended_actions must be an array of strings.

confidence must be one of:
- HIGH
- MEDIUM
- LOW

report must contain the completed requirements report in Markdown.

Return only valid JSON. Do not return Markdown fences or explanatory text
outside the JSON object.
"""
