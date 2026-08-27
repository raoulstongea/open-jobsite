# Windows goose verification

This record separates what was actually run from what remains planned.

## Verified on 2026-08-27

- Client: goose CLI 1.46.0 on Windows
- Extension transport: local STDIO launched with `--with-extension`
- Model used by the local goose configuration: `gpt-5.5`
- Input: the synthetic prompt in `berd-prompt.md`
- Data isolation: a new timestamped directory and project ID for the run

The final isolated run persisted exactly:

| Check | Observed value |
|---|---:|
| Evidence records | 2 (`measurement`, `note`) |
| Draft artifacts | 2 (`estimate`, `daily-log`) |
| Estimate subtotal | CAD 344.00 |
| Estimate contingency | CAD 34.40 |
| Estimate total | CAD 378.40 |
| Daily-log labor | 6.00 hours |
| Estimate evidence links | 2 |
| Daily-log evidence links | 1 |
| Human approval required | `true` |
| External action performed | `false` |

The generated project file is intentionally excluded from version control
because runtime data belongs in a user-controlled local folder. Anyone can
reproduce the run with `run_goose_windows.ps1` and compare it with
`expected-result.md`.

## Defects found by the live run

The first live attempt did not complete. It exposed finite choices as plain
strings and nested line items as JSON-encoded strings, so the agent repeatedly
guessed invalid inputs and reached its action limit. The MCP schema now exposes
literal enums and typed nested arrays, and a regression test inspects the
published tool schema.

A later attempt exposed a concurrent read-modify-write race when evidence calls
ran in parallel. The local store now uses an in-process re-entrant lock around
project mutations, with a concurrent-write regression test.

These failures are part of the development record; they are not presented as
successful demos.

## Not yet verified

- No screen recording is included.
- No local Open Jobsite MCP workflow has been completed inside Berd desktop.
- The five-case benchmark is deterministic software coverage, not an agent or
  field-accuracy benchmark.
