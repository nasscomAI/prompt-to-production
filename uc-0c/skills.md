# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates the expected columns are present, and reports the null count and which specific rows are null before returning any data.
    input: file path (str) to ward_budget.csv.
    output: >
      list of dicts (one per CSV row: period, ward, category,
      budgeted_amount, actual_spend or None, notes). Also prints a null
      report to stdout: count of null actual_spend rows and their
      period/ward/category/notes before any computation happens.
    error_handling: >
      If a required column is missing from the header, raises a clear
      error naming the missing column rather than silently proceeding
      with partial data. Malformed numeric fields are treated as null
      (flagged), not coerced to 0.

  - name: compute_growth
    description: Takes a loaded dataset plus ward, category, and growth_type, and returns a per-period table with the formula shown for each row — refusing if any required argument is missing or the ward/category scope isn't exactly one pair.
    input: dataset (from load_dataset), ward (str, exact match), category (str, exact match), growth_type ("MoM" or "YoY").
    output: >
      list of dicts, one per period for the requested ward+category:
      {period, actual_spend, growth_pct, formula, flag}. flag is one of
      "" (computed normally), "NULL_ACTUAL" (this period's spend is null),
      or "NULL_COMPARISON" (the baseline period needed for growth is null
      or missing).
    error_handling: >
      Raises/refuses (does not return a partial table) if ward, category,
      or growth_type is missing, "all", or not an exact match found in the
      dataset — per agents.md, this skill never silently aggregates or
      guesses a formula.
