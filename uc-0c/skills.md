skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates all required columns exist,
      and reports every null actual_spend row (with its reason from the notes column)
      before returning the DataFrame — nulls are never silently passed through.
    input: filepath (string) — absolute or relative path to a CSV file with columns
      period, ward, category, budgeted_amount, actual_spend, notes.
    output: pandas DataFrame with period parsed as datetime, all 300 rows intact
      including null rows. Prints a null-row report to stdout before returning.
    error_handling: Exits with a clear error message if the file is not found,
      if any required column is missing, or if the period column cannot be parsed
      as YYYY-MM format.

  - name: compute_growth
    description: Filters the dataset to a single ward + category combination,
      then computes MoM or YoY growth per period — returning a table with the
      actual_spend, growth percentage, formula string, and a flag for any
      row that could not be computed due to a null value.
    input: df (pandas DataFrame from load_dataset), ward (string — exact match),
      category (string — exact match), growth_type (string — "MoM" or "YoY").
    output: pandas DataFrame with columns — period, actual_spend, growth_%,
      formula, flag. One row per period. Null rows appear with growth_%=None
      and a non-empty flag explaining why computation was skipped.
    error_handling: Exits with an error if ward or category is not found in the
      dataset. Refuses YoY if the dataset contains fewer than 2 distinct years.
      Never fills, interpolates, or skips null rows silently.