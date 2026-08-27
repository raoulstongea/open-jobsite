---
name: daily-log
description: Turn sourced field updates into a reviewable Open Jobsite daily log.
---

# Daily Log

Use this workflow only after the user identifies the project and work date.

1. Separate observed facts from interpretations. Ask for missing work date,
   worker identifiers/roles/hours, and the source of each material fact.
2. Create the project if it does not exist.
3. Record each source with `record_site_evidence`. Default publication status to
   `private`; use `synthetic` only when the user confirms it is synthetic.
4. Call `draft_daily_log` with ISO date, factual summary, worker array, and the
   evidence IDs. Put unresolved claims in assumptions or exclusions.
5. Present the draft, total labor hours, evidence links, assumptions, and gaps.
6. Stop for human review. Do not send the log, alter a timesheet, or claim approval.

Prefer role-based synthetic worker identifiers in demos; do not expose tenant or
employee personal information.
