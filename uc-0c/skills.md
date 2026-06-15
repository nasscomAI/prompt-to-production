skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates required columns are present, prints a null report listing every row with missing actual_spend, and returns the parsed DataFrame.
    input: file_path (string) — absolute or relative path to ward_budget.csv
    output: pandas DataFrame with validated columns; prints to stdout before returning — total rows loaded, null count, and for each null row its period, ward, category, and notes reason
    error_handling: Raises FileNotFoundError if file path does not exist; raises ValueError if any required column (period, ward, category, budgeted_amount, actual_spend, notes) is missing; raises ValueError if the DataFrame is empty after loading.

  - name: compute_growth
    description: Filters dataset to the specified ward and category, computes per-period growth using the specified growth_type, and returns a table with formula shown for every row including null-flagged rows.
    input: df (DataFrame), ward (string — exact match), category (string — exact match), growth_type (string — must be exactly "MoM" or "YoY")
    output: list of dicts with keys — period, actual_spend, prior_spend, formula, growth_pct, is_null, null_reason; null rows have formula=NULL_FLAGGED and growth_pct empty; rows with null prior have formula=PRIOR_NULL_FLAGGED
    error_handling: Raises ValueError if ward not found in dataset; raises ValueError if category not found in dataset; raises ValueError if growth_type is not "MoM" or "YoY"; never treats null actual_spend as zero or skips null rows silently.
