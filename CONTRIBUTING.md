# Contributing

Open Jobsite is early and field feedback is valuable. Please open an issue before
large changes so the problem, safety boundary, and acceptance criteria can be
agreed publicly.

## Development

```bash
uv sync --extra dev
uv run pytest
```

Keep deterministic calculations independent from MCP transport code. New tools
must document their inputs, expose relevant assumptions and evidence, and state
whether they perform local or external side effects. High-impact actions require
an explicit human approval design before implementation.

## Test data and privacy

Use synthetic data by default. Do not submit names, addresses, credentials,
tenant records, unpublished drawings, client photos, invoices, proprietary price
books, or any data you lack permission to publish. Replace identifying details
before opening an issue or pull request.

## Pull requests

1. Describe the field problem and the intended user.
2. Explain new data flows and trust boundaries.
3. Add or update tests and benchmark cases.
4. Confirm that `uv run pytest` passes.
5. Note any output that still needs professional or human review.

By contributing, you agree that your contribution is licensed under Apache-2.0.
