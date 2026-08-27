---
name: scoped-estimate
description: Build an evidence-linked draft estimate with explicit unit math and exclusions.
---

# Scoped Estimate

1. Confirm the project, currency, scope, measurements, source references, and
   whether prices include tax.
2. Record the relevant measurement, note, drawing, or price source using
   `record_site_evidence`.
3. Use a deterministic calculation tool for each applicable quantity. Never hide
   waste factors, dimensions, conversions, or rounding.
4. Build line items with description, quantity, unit, unit cost, and evidence IDs.
5. List assumptions and exclusions explicitly; do not invent missing prices or
   represent uncertain scope as final.
6. Call `draft_estimate`, then show its unit math and totals.
7. Stop for review. Do not send, accept, sign, or treat the draft as a quotation.

Remind the user that correct arithmetic does not validate field measurements,
contract scope, taxes, code compliance, price availability, or professional work.
