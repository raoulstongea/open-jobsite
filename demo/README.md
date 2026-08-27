# Berd demo

This demo shows Open Jobsite working as a local MCP connection inside Berd. It
uses synthetic data and does not contact a client, send a quote, order material,
or approve any work.

## What the reviewer should see

In one short conversation, Berd should:

1. Create a local training project.
2. save two source notes as evidence.
3. calculate 108 square feet and four 4 by 8 sheets with 10 percent waste.
4. draft a CAD 378.40 estimate and a six-hour daily log.
5. show that both artifacts still require human approval and that no external
   action was performed.

The fixed expected values are listed in [`expected-result.md`](expected-result.md).

## Preflight the real STDIO connection

From the repository root, run:

```bash
uv sync --extra dev
uv run python demo/run_demo.py
```

The preflight starts `open-jobsite` as a separate STDIO process, calls the same
tools Berd will call, checks the expected values, and prints a short JSON
summary. This is also run by GitHub Actions.

## Add the connection in Berd

Open **Connections** in Berd and add a local MCP for Goose with these values:

- Name: `Open Jobsite`
- Type: `STDIO`
- Command: the full path returned by `where uv`
- Arguments: `run`, `--directory`, the absolute repository path, `open-jobsite`
- Environment variable: `OPEN_JOBSITE_DATA_DIR` set to a new private demo folder
- Timeout: `300`

If the connection screen accepts one command line instead of separate arguments,
use:

```text
C:\absolute\path\to\uv.exe run --directory C:\absolute\path\to\open-jobsite open-jobsite
```

The equivalent Goose configuration fragment is in
[`goose-extension.example.yaml`](goose-extension.example.yaml). Merge the entry
into an existing config. Do not replace the rest of a user's config file.

Start a fresh chat after enabling the connection. Ask Berd which Open Jobsite
tools are available. It should list ten tools. Then paste the complete contents
of [`berd-prompt.md`](berd-prompt.md).

## Recording checklist

Keep the recording between 60 and 90 seconds:

1. Show the enabled Open Jobsite connection.
2. Paste the prepared prompt into a fresh Berd chat.
3. Let the tool calls run without editing their results.
4. Expand one calculation and the estimate so the evidence and unit math are
   visible.
5. End on the summary showing CAD 378.40, six labor hours,
   `requires_human_approval: true`, and `external_action_performed: false`.

Use a clean desktop and synthetic data only. Hide notifications, account details,
private paths, API keys, and real building information before recording.
