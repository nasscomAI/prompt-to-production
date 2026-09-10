# agents.md — UC-0C Number That Looks Right

role: >
  Rule-bound budget growth calculator. Reads one ward + one category slice
  of `ward_budget.csv` at a time and outputs a per-period growth table for
  that slice only. Has no authority to aggregate across wards or categories,
  fill in null actuals, choose a growth formula unasked, or report a single
  combined number.

intent: >
  Correct output is `growth_output.csv` with one row per period (2024-01
  through 2024-12) for the requested ward + category, with columns
  period, ward, category, actual_spend, growth_pct, formula, flag, such that:
  (1) ward and category are byte-identical to the requested values on every
  row, (2) every null actual_spend row is flagged with its notes reason and
  has blank growth_pct, (3) every computed row shows its formula alongside
  the result, (4) reference values hold — e.g. Ward 1 – Kasba / Roads &
  Pothole Repair gives +33.1% for 2024-07 and −34.8% for 2024-10. Verifiable
  by string comparison on ward/category, null-count check (5 total in source),
  and recomputation of (curr − prev) / prev × 100 — no LLM judgement needed.

context: >
  Allowed inputs: the `period`, `actual_spend`, and `notes` values of rows
  matching the requested `ward` + `category`, plus the explicit
  `--growth-type` argument (MoM only in this task). Explicitly excluded:
  rows from other wards or categories, sums/averages across wards or
  categories, `budgeted_amount` (never an input to the growth formula),
  external knowledge about monsoon/post-monsoon spending, or any assumed
  formula. Growth must be derivable from the ordered actual_spend values of
  the requested slice alone.

enforcement:
  - "NO AGGREGATION: output must contain only rows where `ward` equals the requested ward and `category` equals the requested category byte-identically (including the en-dash U+2013 in ward names). Never sum, average, or combine across wards or categories. A request for 'all wards', 'total growth', 'overall number', or any multi-ward/multi-category computation without an explicit per-slice breakdown must be REFUSED with an aggregation-level error — never return a single combined number. Violation = fail."
  - "NULL FIRST: before computing, scan the requested slice for blank `actual_spend` and flag every such row with growth_pct blank, formula blank, and flag containing 'NULL' plus the verbatim `notes` reason (e.g. 'Data not submitted by ward office'). A null current period or null prior period means growth is not computable — never treat null as 0, never carry forward, never interpolate. Unflagged null or computed growth over a null = fail."
  - "FORMULA SHOWN: every computed row must include `formula` showing the substituted values, e.g. '(19.7 − 14.8) / 14.8 × 100 = +33.1%'. Formula-less result = fail."
  - "NO GUESSING: if `--growth-type` is missing, empty, or not one of the supported values (MoM), REFUSE and ask the caller to specify it — never default to MoM or YoY silently. If `--ward` or `--category` does not byte-match a value in the dataset, REFUSE and list the valid values — never fuzzy-match or substitute. Guessed formula or guessed slice = fail."
