---
name: change-order
description: Draft an auditable construction change order without issuing or approving it.
---

# Change Order

1. Identify the original scope, discovered condition or requested change, date,
   and supporting evidence.
2. Record the evidence and distinguish observed facts from proposed work.
3. Confirm cost items, currency, schedule impact, assumptions, and exclusions.
4. Call `draft_change_order` with evidence-linked line items.
5. Present the reason, cost change, schedule change, missing contract information,
   and approval warning.
6. Stop for explicit human and contractual review. Never issue, sign, approve,
   invoice, schedule, or start changed work through this workflow.

If safety, structural conditions, hazardous materials, permits, or code issues may
be involved, surface the concern and direct the user to the appropriate qualified
professional rather than making a determination.
