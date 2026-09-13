# agents.md

role: >
  UC-0C "Number That Looks Right" agent. Computes period-over-period growth from
  ../data/budget/ward_budget.csv. Operational boundary: exactly one ward and one
  category per run; never a rolled-up number. Uses only stdlib; no third-party
  dependencies. CLI surface is fixed: --input, --ward, --category,
  --growth-type, --output.

intent: >
  A correct run writes uc-0c/growth_output.csv as a per-period table (one row per
  month) for the single requested ward + category, with every row showing the
  formula used alongside the result. Growth = (current − prior) / prior × 100.
  Reference row 2024-07 Ward 1 – Kasba Roads & Pothole Repair must read
  actual 19.7, MoM +33.1%; 2024-10 reads actual 13.1, MoM −34.8%. Every null
  actual_spend row is flagged before any growth is computed. Verifiable by
  re-running the README command and diffing the output.

context: >
  Allowed: the six columns in ward_budget.csv (period, ward, category,
  budgeted_amount, actual_spend, notes). Excluded: any cross-ward or
  cross-category arithmetic, any silent assumption of MoM vs YoY, and any
  inference about a null row's reason beyond the notes column.

enforcement:
  - "Never aggregate across wards or categories. Only one --ward and one
     --category are accepted; a wildcard/aggregation request (e.g. 'all',
     'every', 'total') or a value not exactly present in the dataset is refused
     with an error and the list of valid choices."
  - "Flag every null actual_spend row before computing growth, reporting the
     count and each row (period, ward, category) with its reason from the notes
     column."
  - "Never compute growth for a row whose actual_spend is null (or whose prior
     month's actual_spend is null) — output that row with growth blank and a
     FLAGGED / N/A formula explaining why."
  - "Show the formula used in every output row alongside the result, e.g.
     (19.7 - 14.8) / 14.8 * 100 = +33.1%."
  - "Refusal condition: if --growth-type is not specified (or is not exactly
     MoM or YoY), refuse and ask for it — never guess between MoM and YoY.
     Also refuse if --ward or --category look like an all-ward / cross-category
     aggregate."
