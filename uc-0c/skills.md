skills:
  - name: load_dataset
    description: Reads the ward_budget.csv file, validates required columns, reports null actual_spend rows (count and details), then returns filtered data ready for computation.
    input: file_path (str) — path to ward_budget.csv. ward (str) — the specific ward to filter for. category (str) — the specific category to filter for.
    output: A tuple of (valid_rows, null_rows) where valid_rows is a list of dicts with non-null actual_spend and null_rows is a list of dicts with period, ward, category, notes for each null actual_spend. Prints a null report to stdout before returning.
    error_handling: If file is not found, raise FileNotFoundError. If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, raise ValueError listing missing columns. If the ward or category filter returns zero valid rows after null removal, raise ValueError with a descriptive message.

  - name: compute_growth
    description: Takes a list of valid budget rows for a single ward and category, plus a growth_type (MoM or YoY), and returns a period-by-period growth table with the formula shown for each row.
    input: valid_rows (list of dicts) — output from load_dataset. growth_type (str) — either "MoM" or "YoY". ward (str) and category (str) for labelling output.
    output: A list of dicts, each with: period, ward, category, actual_spend, growth_pct (float or None), formula (str showing exact calculation), note (str — e.g. "First period — no prior value" if growth cannot be computed).
    error_handling: If growth_type is not "MoM" or "YoY", raise ValueError("growth_type must be MoM or YoY. Provide --growth-type explicitly."). If a period's prior value is 0 (division by zero), output growth_pct=None and note="Division by zero — prior period actual_spend is 0". Never silently return a number when the formula cannot be applied.
