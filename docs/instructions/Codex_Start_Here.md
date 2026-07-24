# Version >= 1.1
------------------------------------------------------------
DOCUMENT VERSION VALIDATION
------------------------------------------------------------

Before beginning implementation, verify that all required engineering documents contain a VERSION declaration as the first line of the file.

Example:

VERSION >= 1.1

The Engineering Partner shall compare the required document versions against the current project version.

Required documents include, as applicable:

- docs/architecture/QAlchemy_Architecture.md
- docs/design/QAlchemy_Design.md
- Applicable subsystem Design document(s)
- docs/engineering/SESSION.md (if present)

If a required document:

- does not contain a VERSION declaration,
- specifies an older version than the current project version,
- specifies an incompatible version,
- or cannot be validated,

STOP.

Present a **Documentation Version Warning** before proceeding.

The warning shall identify:

- The project version.
- The document name.
- The document version found.
- The expected version.
- The potential impact of continuing.

Do not begin implementation until the user explicitly approves continuing or the documentation has been updated.

Example:

Documentation Version Warning

Project Version:
1.1

Document:
docs/design/QAlchemy_Design.md

Document Version:
1.0

Expected:
VERSION >= 1.1

Status:
The Design document may not reflect the current architecture or engineering standards.

Recommendation:
Update the document before implementation or explicitly approve proceeding with the older version.