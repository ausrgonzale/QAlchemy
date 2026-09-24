# Requirements Review Definition of Done

## Purpose

This standard defines the conditions that must be satisfied for a
requirements review to be considered complete.

The review determines whether a requirement is sufficiently defined to
support Development, QE, business validation, estimation, and delivery.

This standard is used by the Requirements Evaluation Agent when
assessing a requirement.

------------------------------------------------------------------------

## Definition of Done

A requirements review is complete when all applicable areas below have
been evaluated and the results are supported by evidence or clearly
identified as unknown.

### 1. Requirement Understanding

-   The requirement has been read and understood in its entirety.
-   The intended user, business, or product outcome is identified.
-   The primary behavior or capability being requested is understood.
-   Relevant background and business context have been considered.
-   Any ambiguity in the stated intent has been identified.

### 2. Problem and Goal

-   The problem or user need is clearly stated.
-   The business or product goal is understood.
-   The expected outcome is observable or measurable where appropriate.
-   The relationship between the requested behavior and the intended
    outcome is understandable.

### 3. Scope

-   In-scope behavior is identifiable.
-   Important out-of-scope boundaries are identified where necessary.
-   The requirement does not contain unrelated or conflicting
    objectives.
-   The size and scope of the requirement are reasonable for
    implementation and estimation, or the need for decomposition is
    identified.

### 4. Acceptance Criteria

-   Acceptance criteria exist when they are required.
-   Each applicable criterion is clear and understandable.
-   Each criterion describes an observable outcome.
-   Each criterion can be objectively evaluated as satisfied or not
    satisfied.
-   Criteria are independently verifiable where practical.
-   Criteria align with the stated requirement and intended outcome.
-   Happy-path behavior is addressed where applicable.
-   Relevant edge cases are addressed or identified as missing.
-   Relevant error and failure conditions are addressed or identified as
    missing.
-   Relevant non-functional requirements are addressed or identified
    when applicable.
-   Acceptance criteria do not prescribe unnecessary implementation
    details.

### 5. Development Readiness

-   The requirement contains sufficient information for Development to
    understand the expected behavior.
-   Required business rules and constraints are identified.
-   Required inputs and expected outcomes are understood.
-   Relevant dependencies are identified.
-   Important technical or architectural unknowns are identified.
-   No unresolved requirement issue prevents Development from
    understanding what must be built.

### 6. QE Readiness

-   The expected behavior can be translated into testable scenarios.
-   Expected results can be determined objectively.
-   Acceptance criteria provide sufficient basis for test-case design.
-   Important positive, negative, boundary, and error scenarios are
    identified where applicable.
-   Required test data, environments, integrations, or external systems
    are identified when relevant.
-   No unresolved requirement issue prevents QE from determining how the
    requirement should be validated.

### 7. Dependencies and Constraints

-   Dependencies on teams, systems, services, APIs, data, environments,
    or external resources are identified when applicable.
-   Required access or environmental conditions are identified.
-   Known constraints are documented or identified as missing.
-   Potential blockers are identified.
-   External dependencies that could affect validation or
    reproducibility are identified.

### 8. Design and UX

When applicable:

-   Required designs, wireframes, workflows, or other UX artifacts are
    identified.
-   Required content or copy is available or identified as missing.
-   Important design decisions are resolved.
-   Any unresolved design dependency is identified.

If this area does not apply, the review explicitly records it as not
applicable.

### 9. Estimation Readiness

-   The team has enough information to understand the work sufficiently
    for estimation.
-   Significant unknowns are identified.
-   Work that requires discovery, research, or a technical spike is
    identified.
-   The requirement is not considered estimable merely because it has a
    description; meaningful uncertainty must be surfaced.

### 10. Open Questions and Gaps

-   All material unanswered questions discovered during the review are
    identified.
-   Gaps are specific and actionable.
-   Assumptions made during the evaluation are identified.
-   Conflicting information is identified.
-   Missing information that could affect implementation, testing,
    validation, or estimation is identified.
-   Where an owner or responsible party can be determined from the
    available information, the required action is associated with that
    owner.

### 11. Evidence and Traceability

-   Findings can be traced to the requirement, acceptance criteria, or
    supporting evidence.
-   External or internal evidence used to reach a finding is identified.
-   Evidence is distinguished from assumptions or interpretation.
-   The Agent does not invent missing information.
-   When additional research was necessary, the relevant research
    findings are included as supporting evidence.

### 12. Final Readiness Determination

The review produces one of the following determinations:

-   **Ready** --- no blocking gaps were identified.
-   **Ready with Conditions** --- remaining gaps are minor and do not
    prevent work from proceeding with the stated conditions understood.
-   **Not Ready** --- one or more blocking gaps must be resolved before
    the requirement should proceed.

The determination must be supported by the findings from the applicable
review areas.

------------------------------------------------------------------------

## Review Completion Criteria

The Requirements Review is considered **Done** only when:

1.  The requirement and acceptance criteria have been evaluated.
2.  All applicable Definition of Done areas have been assessed.
3.  Material gaps, ambiguities, assumptions, dependencies, and blockers
    have been identified.
4.  Development readiness has been assessed.
5.  QE readiness has been assessed.
6.  Estimation readiness has been assessed.
7.  Open questions and required actions have been identified.
8.  Supporting evidence and rationale have been captured.
9.  A final readiness determination has been made.
10. The completed findings have been delivered through the requirements
    review report.

------------------------------------------------------------------------

## Important Evaluation Rules

### Evaluate --- Do Not Implement

The Requirements Evaluation Agent evaluates the supplied requirement. It
does not implement, execute, or fulfill the work described by the
requirement unless the assigned task explicitly requires that activity.

### Do Not Silently Resolve Ambiguity

If the requirement is unclear, the review should identify the ambiguity
rather than choosing an interpretation and treating it as fact.

### Do Not Invent Requirements

Missing acceptance criteria, business rules, constraints, dependencies,
or other information must be identified as gaps when they are necessary
for readiness. They must not be fabricated to make the requirement
appear ready.

### Applicability

Not every criterion applies to every requirement. When a criterion is
not applicable, the review should identify it as **Not Applicable**
rather than treating it as a failure.

### Evidence-Based Findings

Findings should be supported by the supplied requirement, applicable
standards, or evidence gathered during the review.

------------------------------------------------------------------------

## Relationship to Other Agent Resources

This standard defines **what must be true for a requirements review to
be considered complete**.

It does not replace:

-   **Agent Core Behavior** --- defines how the Agent operates.
-   **Business Analyst Role** --- defines the professional perspective
    used to evaluate requirements.
-   **Definition of Ready** --- defines the detailed readiness criteria.
-   **Report Template** --- defines how the completed assessment is
    presented.

The Requirements Evaluation Agent uses these resources together to
produce the final requirements review.
