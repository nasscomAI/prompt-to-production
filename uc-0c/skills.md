skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports the count and location of every null actual_spend row before returning the data.
    input: Path to ward_budget.csv with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      A list of row dicts (period, ward, category, budgeted_amount, actual_spend as
      float or None, notes) plus a null report listing each null row's period, ward,
      category, and notes reason and the total null count.
    error_handling: >
      If the file is missing or a required column is absent, raise a clear error and
      stop. Blank actual_spend becomes None (never 0) and is recorded in the null
      report with its notes reason; malformed numeric values are reported, not
      silently coerced.

  - name: compute_growth
    description: Computes per-period growth for exactly one ward and one category using the explicitly requested growth type, showing the formula per row.
    input: The loaded rows, a ward string, a category string, and a growth_type of MoM or YoY.
    output: >
      A per-period table (period, actual_spend, comparison period + value, growth_pct,
      formula, flag) for the single ward+category. Periods with a null current or
      comparison value are marked NOT COMPUTED with the null reason; the first period
      with no prior comparison is marked N/A.
    error_handling: >
      Refuses if ward or category is missing or set to an aggregate (ALL), if
      growth_type is not MoM or YoY, or if no rows match the ward+category. Never
      aggregates, never interpolates nulls, never guesses the formula.
