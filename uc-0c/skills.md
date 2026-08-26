# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning
    input: Path to CSV file
    output: Tuple of (DataFrame, null_count, null_rows) where null_rows lists ward/category/period for each null actual_spend
    error_handling: Raise ValueError if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing; report null count and row details

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown
    input: ward (string), category (string), growth_type (string: "MoM" or "YoY")
    output: DataFrame with columns [period, actual_spend, growth_value, formula_shown] per ward/category combo
    error_handling: Refuse if growth_type is not "MoM" or "YoY"; flag null rows before computing; refuse if ward/category combination has no data