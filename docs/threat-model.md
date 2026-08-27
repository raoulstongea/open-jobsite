# Threat Model v0.1

## Assets

- Private site notes, photos, measurements, drawings, receipts, and prices
- Estimate and change-order integrity
- Evidence-to-output provenance
- User control over messages, commitments, purchases, and safety decisions

## Threats and current controls

| Threat | Consequence | Current control | Remaining work |
|---|---|---|---|
| Path traversal in a project ID | Read/write outside the data folder | Strict lowercase ID pattern | Add platform-specific tests |
| Partial/corrupt local write | Lost or invalid project state | Temp file, `fsync`, atomic replace | Backups and revision history |
| Invented evidence link | Misleading provenance | Artifact IDs checked against project evidence | Evidence hashing and attachment metadata |
| Bad unit math | Cost/material error | `Decimal`, formulas, intermediate values, tests | Property and unit-conversion tests |
| Silent quote or change approval | Unwanted financial commitment | Draft status, approval flag, no external connectors | Signed approval state machine |
| Private data in public samples | Privacy/client harm | Synthetic-first documentation and publication status | Automated redaction checks |
| Prompt injection in future documents | Unsafe tool calls or data leak | No document parser or network tool in v0.1 | Treat extracted content as untrusted; capability isolation |
| False safety/engineering claim | Injury or code violation | Scope warning; tools limited to quantity math | Domain-specific review policies and expert validation |

## Explicit non-goals for v0.1

The server does not authenticate multiple users, encrypt local data, verify source
authenticity, parse attachments, call suppliers, send communications, or make
regulatory/safety determinations. These absences are visible product boundaries,
not implied guarantees.

## Required review before expanding tools

Any network adapter, document parser, message sender, price lookup, purchase tool,
or approval mechanism must document credentials, data destinations, failure
modes, prompt-injection exposure, least privilege, logging, revocation, and an
explicit human checkpoint.
