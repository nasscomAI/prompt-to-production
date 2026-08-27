# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates column structure, counts and reports all null actual_spend rows before returning the cleaned dataset.
    input: File path to ward_budget.csv (YYYY-MM, ward, category, budgeted_amount, actual_spend, notes columns).
    output: DataFrame with all rows; dict with null_count (count of nulls), null_rows (list of rows with nulls, including reason from notes column).
    error_handling: Rejects if required columns missing, if period format invalid (not YYYY-MM), or if actual_spend is not float-or-null. Returns error message with column names found.

  - name: compute_growth
    description: Takes ward, category, and growth_type (MoM or YoY), filters the dataset, and returns per-period growth table with formula shown in each row.
    input: DataFrame (from load_dataset), ward (string), category (string), growth_type (string, must be 'MoM' or 'YoY').
    output: Per-period table with columns: period, actual_spend, growth_percentage, formula. Returns null for rows where actual_spend is null, with reason flagged.
    error_handling: Rejects if ward or category not found in dataset. Rejects if growth_type not in ['MoM', 'YoY'] — asks user to specify. Rejects cross-ward or cross-category requests (explains why). Returns error message with reason.
