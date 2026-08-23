# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that every required column is
      present, and reports the null count and exactly which rows are null
      before returning anything to the caller.
    input: >
      path (str) — path to ward_budget.csv with columns period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      A dict: {"rows": [row dicts in file order], "wards": [sorted unique],
      "categories": [sorted unique], "periods": [sorted unique],
      "nulls": [{period, ward, category, notes}], "row_count": int}.
      The nulls list is printed by the caller before any arithmetic runs.
    error_handling: >
      Missing file → FileNotFoundError naming the attempted path.
      Missing required columns → ValueError naming which are missing and which
      were found; nothing is returned so no downstream code can assume defaults.
      A non-numeric actual_spend or budgeted_amount is recorded as a parse
      failure on that row and surfaced in the nulls list with the reason
      "unparseable value: <raw>" — it is never coerced to 0.0.
      A blank actual_spend is preserved as None. It is never filled from
      budgeted_amount, never interpolated, never treated as zero.

  - name: compute_growth
    description: >
      Takes a ward, a category and a growth type and returns a per-period table
      for that single scope, with the formula written out for every row and a
      status explaining every row where growth was not computed.
    input: >
      dataset (dict from load_dataset), ward (str, exact value from the file),
      category (str, exact value from the file), growth_type (str, "MoM" or
      "YoY" — no default is supplied anywhere in the code).
    output: >
      A list of row dicts with keys ward, category, period, budgeted_amount,
      actual_spend, prior_period, prior_actual, growth_type, formula,
      growth_pct, status, note. One row per period present in the scope, in
      period order. status is one of COMPUTED, NULL_ACTUAL, PRIOR_NULL,
      NO_PRIOR_PERIOD.
    error_handling: >
      growth_type not supplied → the caller refuses before this skill is
      reached; this skill raises ValueError rather than defaulting.
      ward or category not present in the dataset → ValueError listing the
      exact valid values, so an empty table can never be mistaken for zero
      growth.
      Prior period missing from the data (gap in the series) or blank →
      status PRIOR_NULL / NO_PRIOR_PERIOD with an empty growth_pct and a
      formula string of "not computed — <reason>"; the row is still emitted.
      Prior actual of exactly 0.0 → status PRIOR_NULL with reason "prior
      actual is 0.0, percentage growth is undefined" rather than a division
      error or an infinity.
      Aggregation is structurally impossible here: the skill accepts exactly
      one ward and one category and has no code path that sums across either.
