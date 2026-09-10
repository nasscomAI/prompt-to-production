# agents.md — UC-0C Budget Growth (RICE)

role: >
  Scoped budget-growth calculator. It computes month-on-month (or year-on-year)
  growth for exactly ONE ward and ONE category over the 12 months of 2024.
  Its operational boundary is one slice at a time: it never aggregates across
  wards or categories, never fills in missing actuals, and never chooses a
  formula the user did not ask for.

intent: >
  A correct output is verifiable row by row: (1) every output row carries the
  requested ward and category only — never a blended all-ward number;
  (2) every null `actual_spend` row is present with blank growth, its reason
  copied from the `notes` column, and a NULL flag — never silently skipped or
  zero-filled; (3) every computed row shows the exact formula with its input
  numbers next to the result, matching `(curr-prev)/prev*100` for MoM;
  (4) reference rows reproduce exactly: Ward 1 Kasba Roads 2024-07 +33.1%,
  2024-10 −34.8%, and the Ward 2 / Ward 4 null rows are flagged, not computed.
  Any aggregation, silent null, hidden formula, or guessed growth-type is a
  failure.

context: >
  The agent may use ONLY the rows of `ward_budget.csv` matching the requested
  `--ward` and `--category`, plus the requested `--growth-type`. It must NOT
  use: rows from other wards/categories (no cross-slice pooling), invented
  baselines for YoY (2023 data does not exist), or zero/imputed values for
  null actuals. Exclusions are explicit — a null stays null, an unasked
  formula stays uncomputed, an all-ward request stays refused.

enforcement:
  - "E1-single-slice-scope: output rows MUST all carry the requested ward AND category; the calculator MUST refuse (exit non-zero with a reason) any request whose ward/category is missing, unknown, or multi-scope (e.g. 'all', '*', comma lists). Test: every output row's ward/category equals the request; all-ward input is refused, never averaged."
  - "E2-null-flag-first: before computing, the loader MUST report null count + periods; in the output every null-actual row MUST keep blank growth with flag starting NULL_ and the reason copied verbatim from `notes`, and any growth whose baseline period is null MUST be blank with flag NULL_BASELINE. Test: the 5 documented nulls are flagged with their notes reasons; no null row carries a number."
  - "E3-formula-visible: every output row MUST include a `formula` cell showing the computation with input numbers (MoM: `(curr-prev)/prev*100`, e.g. `(19.7-14.8)/14.8*100`) or the explicit reason no computation applies (first period / null / no baseline). Test: each computed row's growth_pct re-derives from its formula; no row has a bare number without a formula."
  - "E4-no-guess-refusal: if `--growth-type` is absent the program MUST refuse with 'specify --growth-type' and compute nothing; YoY MUST NOT invent 2023 baselines — every YoY row is flagged NO_BASELINE. Never default to MoM silently. Test: no-growth-type invocation exits non-zero with zero rows written."
