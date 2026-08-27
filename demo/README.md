# Goose CLI demo and Berd recording plan

The deterministic flow in this folder has been verified through the real Open
Jobsite STDIO server and goose CLI on Windows. A visible Berd-local MCP run and
screen recording have not yet been completed. The prompt and shot list are
ready for that proof step.

All inputs are synthetic. Nothing here contacts a client, sends a quote, orders
material, or approves work.

## What the reviewer should see

In one short goose or Berd conversation, the reviewer should see:

1. Create a local training project.
2. Save two source notes as evidence.
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
tools an MCP client calls, checks the expected values, and prints a short JSON
summary. This is also run by GitHub Actions.

If Windows has the goose-bundled `uv.exe` but it is not on `PATH`, set its exact
path for the preflight:

```powershell
$env:OPEN_JOBSITE_UV = "$env:LOCALAPPDATA\Goose\bin\uv.exe"
& $env:OPEN_JOBSITE_UV run python demo\run_demo.py
```

To run the same prompt through the installed goose CLI with a fresh synthetic
data folder, use:

```powershell
.\demo\run_goose_windows.ps1
```

The observed Windows run and exact persisted checks are documented in
[`windows-goose-verification.md`](windows-goose-verification.md).

## Berd status

On 2026-08-27 the installed Berd desktop app launched and exposed Home, Agents,
Skills, Projects, Chats, Settings, and a hosted “Chat with Goose” composer. A
working local MCP connection for Open Jobsite was not verified in that build.
Do not describe the demo as a Berd run until Open Jobsite's ten tools are visible
in Berd and the complete prompt succeeds there.

If a future Berd build exposes local STDIO MCP configuration, use the same
command, arguments, and isolated data directory documented for goose. The
equivalent goose configuration fragment is in
[`goose-extension.example.yaml`](goose-extension.example.yaml).

## Recording checklist

Keep the recording at or under two minutes. The exact shot list and narration
are in [`recording-script.md`](recording-script.md).

1. Show the enabled Open Jobsite connection and identify the client accurately.
2. Paste the prepared prompt into a fresh chat in the identified client.
3. Let the tool calls run without editing their results.
4. Expand one calculation and the estimate so the evidence and unit math are
   visible.
5. End on the summary showing CAD 378.40, six labor hours,
   `requires_human_approval: true`, and `external_action_performed: false`.

Use a clean desktop and synthetic data only. Hide notifications, account details,
private paths, API keys, and real building information before recording.
