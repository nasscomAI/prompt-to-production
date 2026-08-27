skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, and reports null count and which rows are null before returning data.
    input: File path as string, ward as string, category as string.
    output: Filtered dataframe for the given ward and category, plus a printed null report listing period and notes for each null row.
    error_handling: If file not found or required columns missing, raise FileNotFoundError or ValueError with clear message. Never silently continue.

  - name: compute_growth
    description: Takes filtered ward and category data plus growth_type and returns a per-period table with growth percentage and formula shown.
    input: Filtered dataframe, growth_type as string (MoM or YoY).
    output: CSV-ready table with columns period, actual_spend, growth_pct, formula, flag. Null rows get flag=NULL_SKIPPED.
    error_handling: If growth_type is not MoM or YoY, refuse and print error asking user to specify. Never default silently.
