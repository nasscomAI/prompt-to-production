skills:
  - name: load_dataset
    description: >
      Reads the budget CSV, validates its required columns, and reports the null
      actual_spend count and the exact rows involved before returning the data.
    input: >
      A file path (str) to a CSV such as ../data/budget/ward_budget.csv, encoded
      UTF-8, with header columns period, ward, category, budgeted_amount,
      actual_spend, notes. period is YYYY-MM; actual_spend is a float or blank
      (deliberately null).
    output: >
      A list of row dicts with keys period, ward, category, budgeted_amount,
      actual_spend (float or None), notes, plus a report of how many rows have a
      null actual_spend and a list identifying each null row by period, ward,
      category and its verbatim notes reason. Faithfully preserves the exact ward
      and category strings, including any en-dash, as present in the file.
    error_handling: >
      If the file does not exist, cannot be read, is empty, or is missing any of
      the required columns (period, ward, category, budgeted_amount,
      actual_spend, notes), raise a clear error naming the path and the failing
      check. Do not proceed, silently drop rows, or fabricate data.

  - name: compute_growth
    description: >
      Given an explicitly requested ward, category, and growth type, returns a
      per-period growth table for that single (ward, category) series with the
      formula shown on every row, flagging null rows instead of computing them.
    input: >
      The loaded row list from load_dataset, exactly one ward as --ward (str),
      exactly one category as --category (str), and one growth type as
      --growth-type (str, e.g. MoM). Only the rows matching that exact ward and
      category, ordered by period, are used; nothing else is aggregated.
    output: >
      One row per period for the requested (ward, category) slice with fields:
      ward, category, period, budgeted_amount, actual_spend, previous_actual_spend,
      growth_percent, formula, status, notes. Non-null rows carry the numeric
      growth_percent, a human-readable formula string such as
      "(19.7 - 14.8)/14.8 x 100 = +33.1%", and status OK. Null rows carry status
      NULL / NOT COMPUTED, growth_percent and formula left blank, and the verbatim
      notes reason. The table is never a single aggregated number.
    error_handling: >
      If growth_type is not provided, refuse with a message asking for an
      explicit choice (MoM or YoY) — never guess or default. If the requested
      ward or category is not present in the data, refuse and report the missing
      value. If a request would combine multiple wards or categories (e.g. no
      ward or no category given), refuse rather than aggregate. Null rows are
      flagged and never imputed or silently skipped.
