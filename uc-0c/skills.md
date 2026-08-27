# skills.md

skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates that all required columns are present, and reports the total null count and the specific rows with null actual_spend values before returning the dataset.
    input: File path (string) pointing to the CSV file (e.g., ../data/budget/ward_budget.csv).
    output: Validated DataFrame plus a null-report list of tuples (period, ward, category, null_reason) for every row where actual_spend is blank.
    error_handling: If the file is not found or required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, raise an error and halt — do not proceed with partial data.

  - name: compute_growth
    description: Takes a ward, category, and growth type (MoM or YoY), then returns a per-period growth table where each row includes the actual_spend, the computed growth percentage, and the exact formula used.
    input: ward (string), category (string), growth_type (string — must be "MoM" or "YoY"), and the validated DataFrame returned by load_dataset.
    output: Tabular result (CSV-compatible) with columns: period, actual_spend, growth_pct, formula — one row per non-null period; null periods are listed separately as flagged/skipped.
    error_handling: If growth_type is not provided or is not "MoM" or "YoY", refuse and return an error asking the caller to specify — never default or guess. If fewer than two non-null data points exist for the selected ward/category, return an error stating growth cannot be computed.
