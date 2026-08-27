# Security Policy

Open Jobsite handles potentially sensitive job evidence. The v0.1 server is local
only and performs no network requests, but local files still require protection.

## Reporting a vulnerability

Do not open a public issue containing a working exploit or private job data. Until
a dedicated security address is published, open a minimal public issue asking the
maintainer for a private reporting channel, without including sensitive details.

## Current guarantees

- Project IDs are constrained to safe local filenames.
- Project files are written atomically.
- Evidence and draft tools make no network calls.
- Estimates and change orders remain drafts and expose an approval requirement.
- Artifact evidence IDs must exist in the same project.

## Not yet guaranteed

- Encryption at rest or multi-user access control
- Malware scanning for future attachments
- Sandboxed parsing of PDFs, images, or voice files
- Authenticity of source evidence
- Regulatory, contractual, engineering, tax, or safety correctness

Store data on an appropriately protected device and use synthetic examples in
public demonstrations. See `docs/threat-model.md` for the current threat model.
