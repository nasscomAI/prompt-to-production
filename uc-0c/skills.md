skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, identifies and reports all null actual_spend rows (with period, ward, category, and reason), then returns the filtered dataset for a specific ward and category.
    input: >
      file_path (str) — path to the CSV file.
      ward (str) — exact ward name to filter on.
      category (str) — exact category name to filter on.
    output: >
      A tuple of:
        (1) filtered_df: pandas DataFrame with columns [period, ward, category,
            budgeted_amount, actual_spend, notes] for the specified ward+category,
            sorted by period ascending.
        (2) null_rows: list of dicts [{period, ward, category, reason}] for all
            null actual_spend rows found in the full dataset BEFORE filtering,
            so the caller is always informed of ALL nulls in the file.
    error_handling: >
      Raise FileNotFoundError if the CSV path is invalid.
      Raise ValueError if any required column is missing from the CSV.
      Raise ValueError if the specified ward or category does not exist in the
      dataset — list available values in the error message.
      Never silently drop or impute null rows.

  - name: compute_growth
    description: Takes a filtered per-ward per-category DataFrame and a growth type, computes per-period growth rates with the formula shown, and returns a results table where null periods are flagged and skipped.
    input: >
      filtered_df (pd.DataFrame) — output of load_dataset skill.
      growth_type (str) — must be exactly "MoM" or "YoY".
        MoM: month-over-month = (current - previous) / previous * 100
        YoY: year-over-year = (current - same month prior year) / same month prior year * 100
      null_rows (list) — null row metadata from load_dataset, used to annotate output.
    output: >
      A pandas DataFrame with columns:
        [period, ward, category, actual_spend, growth_pct, formula_used, null_flag, null_reason]
      growth_pct: float rounded to 2 decimal places, or blank if null_flag is True.
      formula_used: string showing the exact formula applied (e.g., "MoM: (19.7-14.8)/14.8*100").
      null_flag: boolean — True if actual_spend is null.
      null_reason: string from notes column if null_flag is True, else blank.
    error_handling: >
      Raise ValueError if growth_type is not "MoM" or "YoY" — do not default.
      If the first period has no prior period to compare against, emit growth_pct
      as blank and formula_used as "N/A — no prior period".
      If a null row is encountered, skip growth calculation, set null_flag=True,
      and carry forward no value — do not interpolate.
