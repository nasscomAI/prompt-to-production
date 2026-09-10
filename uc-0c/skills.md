# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates that required columns exist, and reports null actual_spend values with their reasons before returning the data.
    input: File path to ward_budget.csv.
    output: A list of row dicts with all columns preserved, plus a printed null report listing each null row's period, ward, category, and reason from the notes column.
    error_handling: If required columns (period, ward, category, budgeted_amount, actual_spend) are missing, returns an error and halts. If null actual_spend values are found, reports them but does not halt — the data is still returned for non-null computation.

  - name: compute_growth
    description: Takes filtered data for one ward and one category, computes month-over-month or year-over-year growth, and returns a per-period table with the formula shown.
    input: Filtered row list (one ward, one category), growth type (MoM or YoY).
    output: A list of dicts with columns period, ward, category, actual_spend, previous_spend, growth_pct, formula, flag. Growth percentage is rounded to 1 decimal place.
    error_handling: If either the current or previous period has null actual_spend, outputs growth_pct as "NULL" and flag as the reason from the notes column. If growth type is not specified, refuses and asks the user. If no data matches the ward+category filter, returns an error.
