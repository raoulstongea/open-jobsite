# Open Jobsite

Open Jobsite is an open, local-first construction operations server for
[goose](https://github.com/block/goose) and other Model Context Protocol (MCP)
clients. It turns field evidence into reviewable calculations, daily logs,
estimates, and change orders while keeping source references, unit math,
assumptions, exclusions, and human approval boundaries visible.

This repository is a working v0.1 grant-proof MVP. It uses synthetic data, makes
no network calls, and never sends a message, submits a price, places an order, or
approves an artifact.

## Why it exists

Field work starts with rough notes, photos, sketches, measurements, receipts, and
conversations—not clean database rows. General-purpose agents can draft polished
answers while hiding where numbers came from. Open Jobsite takes the opposite
approach:

- **Evidence first:** records retain a user-supplied source reference and privacy
  status.
- **Deterministic math:** quantity tools use decimal arithmetic and expose formulas
  and intermediate values.
- **Draft by default:** every estimate and change order is explicitly unapproved.
- **Local and portable:** JSON files stay in a user-controlled folder and the tool
  surface is standard MCP.
- **Field-shaped workflows:** portable skills cover daily logs, scoped estimates,
  and change orders.

## Working flow

1. Create a local project.
2. Record a note or measurement with a source reference.
3. Run a deterministic quantity calculation.
4. Draft an artifact linked to the evidence ID.
5. Review and edit the draft outside the server before any external action.

## Tools

| Tool | Purpose | External side effect |
|---|---|---|
| `create_project` | Create a local JSON job record | Local file only |
| `record_site_evidence` | Record a sourced note, measurement, or media reference | Local file only |
| `get_project` | Read the complete local record | None |
| `calculate_surface_area` | Area plus stated waste factor | None |
| `calculate_concrete_volume` | Rectangular volume in cubic yards | None |
| `calculate_sheet_count` | Whole sheets plus stated waste | None |
| `calculate_linear_pieces` | Whole stock pieces plus stated waste | None |
| `draft_daily_log` | Draft labor summary linked to evidence | Local file only |
| `draft_estimate` | Draft priced scope with unit math | Local file only |
| `draft_change_order` | Draft scope/cost/schedule change | Local file only |

Financial and job artifacts always return:

```json
{
  "status": "draft",
  "requires_human_approval": true,
  "external_action_performed": false
}
```

## Install and test

Requirements: Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
uv run pytest
uv run open-jobsite --version
```

Run the MCP server over stdio:

```bash
uv run open-jobsite
```

## Synthetic demo

The [`demo/`](demo/) folder contains a synthetic end-to-end workflow, a prompt,
fixed expected results, a Windows goose CLI launcher, and a preflight that
launches the real STDIO server. Run the preflight with:

```bash
uv run python demo/run_demo.py
```

The preflight is also part of GitHub Actions. It verifies the same evidence,
calculation, estimate, daily log, and approval-gate flow intended for a future
screen recording. A recording is not included in v0.1.

Data defaults to `.open-jobsite-data/`. Select another local folder with either
`--data-dir PATH` or the `OPEN_JOBSITE_DATA_DIR` environment variable.

## Connect to goose Desktop

Build and test the repository first. Then add a custom **STDIO** extension in
goose Desktop with:

- Command: the absolute path to `uv` (`where uv` on Windows)
- Arguments: `run --directory C:\absolute\path\to\open-jobsite open-jobsite`
- Environment: optionally set `OPEN_JOBSITE_DATA_DIR` to a private job-data folder

Use only synthetic data in a public demo. The synthetic prompt has been run
through goose CLI 1.46.0 on Windows; see the
[`verification record`](demo/windows-goose-verification.md). A Berd-local MCP
run has not yet been verified.

## Verified v0.1 evidence

As of 2026-08-27:

- 28 automated tests pass on Windows.
- all five synthetic benchmark cases pass, including four exact numeric cases
  and three approval invariants.
- the real STDIO preflight produces 108 square feet, four sheets, a CAD 344.00
  subtotal, a CAD 378.40 total, and 6.00 labor hours.
- an isolated Windows goose CLI run produced two evidence records and two draft
  artifacts with the same expected values.

These are narrow software checks, not claims about field accuracy, estimating
accuracy, code compliance, or user outcomes.

## Example MCP arguments

Complex inputs use typed arrays so goose can see the required fields in the MCP
schema. For `draft_estimate`, a minimal `line_items` value is:

```json
[
  {
    "description": "Synthetic wallboard",
    "quantity": 3,
    "unit": "sheet",
    "unit_cost": 18.5,
    "evidence_ids": ["ev-example"]
  }
]
```

The evidence ID must already exist in the same project.

## Repository map

- `src/open_jobsite/`: deterministic core, local store, artifacts, MCP tools
- `skills/`: portable field-workflow instructions for goose
- `benchmark/`: synthetic, machine-readable evaluation cases
- `demo/`: reproducible preflight, Windows goose launcher, and recording plan
- `examples/`: a synthetic example project record
- `tests/`: core and in-process MCP protocol tests
- `docs/architecture.md`: component and trust-boundary design
- `docs/threat-model.md`: current risks and mitigations

## Safety and limitations

This alpha is not estimating, legal, contract, tax, structural, code, or safety
advice. It does not inspect site conditions, validate plans, optimize cuts,
confirm prices, or replace a qualified professional. A correct calculation can
still be based on a wrong measurement or assumption. Review all output against
current drawings, contracts, codes, manufacturer instructions, and field
conditions.

Do not put tenant names, addresses, credentials, private photos, client records,
or proprietary price data into public examples or bug reports. See
[`SECURITY.md`](SECURITY.md) and [`docs/threat-model.md`](docs/threat-model.md).

## Roadmap

- **Q1:** stable schema, 25 benchmark cases, CI, Windows goose/Berd demo, upstream
  goose contribution
- **Q2:** voice/photo/PDF adapters, bilingual workflows, provenance review MCP App,
  three safely documented pilots
- **Q3:** revision history, change detection, local price-book adapters, security
  hardening, three external pilots
- **Q4:** v1.0, 50+ benchmark tasks, usability study with five field users,
  maintainer documentation

See [`CONTRIBUTING.md`](CONTRIBUTING.md) to participate. Apache-2.0 licensed.
